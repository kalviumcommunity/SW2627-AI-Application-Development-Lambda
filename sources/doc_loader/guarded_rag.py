"""
Adds a safety guardrail to the RAG answer pipeline: before any answer is
generated, a named relevance gate checks the retrieved context, and the
pipeline returns a clearly labelled refusal instead of an answer when
that context is missing or weak.

Inputs:
    Questions defined in this file: a calibration set of questions the
    corpus does and does not support, and the two questions compared
    side by side. Chat settings (CHAT_BASE_URL, CHAT_API_KEY, CHAT_MODEL)
    and retrieval settings (the EMBEDDING_* and VECTOR_DB_* variables)
    come from environment variables or the ".env" file next to this
    script. Retrieval uses the chromadb collection built by
    index_corpus.py; answers use prompts/templates/grounded_answer.txt.

Outputs:
    Printed to stdout:
        - The relevance gate's thresholds.
        - A calibration table: for each calibration question, its top
          similarity, how many chunks reached the support threshold, and
          the gate's decision (no chat model call is made here).
        - The two main questions side by side: status, answer, sources,
          the gate's signals, and whether the chat model was called.
        - A near-miss question that passes the gate, showing what the
          post-generation backstop does with it.

Similarity is 1 minus the cosine distance chromadb reports. No paid API
key is used or required.
"""

import logging
import os
import re
import sys
import textwrap

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger
from prompts import TemplateError, format_context, render_prompt
from retriever import Retriever

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WRAP_WIDTH = 104
TOP_K = 5
ANSWER_MAX_SENTENCES = 3
ANSWER_OPTIONS = {"temperature": 0, "max_tokens": 200}

# The relevance gate. It runs after retrieval and before generation, and
# only a question whose context passes every check reaches the chat model.
# Values come from calibrating on this corpus (see CALIBRATION_QUESTIONS):
# questions the corpus answers had a top similarity of 0.64 to 0.85 and
# at least 2 chunks at 0.55 or above; off-topic questions topped out at
# 0.37 to 0.52. The minimum sits in that gap, 0.04 below the lowest
# answerable score and 0.08 above the highest off-topic one.
# "Near miss" questions (on-topic, but asking for a detail the corpus does
# not contain) are the gate's known weak spot: similarity measures topic
# closeness, not whether the answer is present, so some of them pass. A
# yes/no "does the context answer this?" check with the 1.5B model was
# tried as a second gate and rejected: it answered "yes" to on-topic
# context regardless of whether the detail was there.
RELEVANCE_GATE = {
    "min_top_similarity": 0.60,
    "support_similarity": 0.55,
    "min_supporting_chunks": 2,
}

REFUSAL_MESSAGE = "I don't have enough reliable context to answer that."
MODEL_NO_ANSWER_PREFIX = "The provided context does not say"

CALIBRATION_QUESTIONS = [
    ("supported", "What file formats does the loading stage read?"),
    ("supported", "How are repeated page headers and footers removed?"),
    ("supported", "Why is paragraph-based chunking the better default?"),
    ("supported", "When is fixed-size chunking still worth using?"),
    ("supported", "What does the cleaning stage do to line endings?"),
    ("supported", "Which files are in the sample corpus?"),
    ("unsupported", "Which company funds this project?"),
    ("unsupported", "What is the monthly budget for the embedding server?"),
    ("unsupported", "Who is the CEO of the company?"),
    ("unsupported", "What is the capital of France?"),
    ("unsupported", "How do I reset my VPN password?"),
    ("unsupported", "What was the revenue last quarter?"),
    ("near miss", "How does the pipeline handle scanned images with OCR?"),
    ("near miss", "How does the loader handle password-protected PDFs?"),
    ("near miss", "How long does indexing the whole corpus take?"),
    ("near miss", "Which embedding model does the design report recommend?"),
    ("near miss", "How does the chunking stage handle tables?"),
]

ANSWERABLE_QUESTION = "What file formats does the loading stage read?"
UNSUPPORTED_QUESTION = "Which company funds this project?"
NEAR_MISS_QUESTION = "How does the pipeline handle scanned images with OCR?"


def check_context(chunks, gate):
    """
    Decide whether retrieved context is strong enough to answer from.

    Args:
        chunks (list[dict]): Retrieved chunks, closest first, each with a
            "distance" (float, cosine distance).
        gate (dict): Thresholds with "min_top_similarity" (float),
            "support_similarity" (float), and "min_supporting_chunks"
            (int).

    Returns:
        dict: "allowed" (bool), "reasons" (list[str], every failed check;
            empty when allowed), "top_similarity" (float or None),
            "supporting_chunks" (list[dict], chunks at or above
            support_similarity), and "signals" (dict of each check's
            result: "has_results", "top_ok", "support_ok").
    """
    similarities = [1 - chunk["distance"] for chunk in chunks]
    top_similarity = similarities[0] if similarities else None
    supporting = [chunk for chunk, sim in zip(chunks, similarities) if sim >= gate["support_similarity"]]

    signals = {
        "has_results": bool(chunks),
        "top_ok": top_similarity is not None and top_similarity >= gate["min_top_similarity"],
        "support_ok": len(supporting) >= gate["min_supporting_chunks"],
    }
    reasons = []
    if not signals["has_results"]:
        reasons.append("retrieval returned no chunks")
    else:
        if not signals["top_ok"]:
            reasons.append("top similarity {:.3f} < {:.2f}".format(top_similarity, gate["min_top_similarity"]))
        if not signals["support_ok"]:
            reasons.append("{} chunk(s) >= {:.2f}, need {}".format(
                len(supporting), gate["support_similarity"], gate["min_supporting_chunks"]
            ))
    return {
        "allowed": not reasons,
        "reasons": reasons,
        "top_similarity": top_similarity,
        "supporting_chunks": supporting,
        "signals": signals,
    }


def cited_sources(answer, allowed_ids):
    """
    Find the chunk ids an answer cites in square brackets.

    Args:
        answer (str): The generated answer.
        allowed_ids (list[str]): Ids of the chunks the model was given.

    Returns:
        list[str]: Cited ids that were actually supplied, in order,
            without duplicates.
    """
    cited = []
    for match in re.findall(r"\[([^\[\]]+)\]", answer):
        if match in allowed_ids and match not in cited:
            cited.append(match)
    return cited


def guarded_answer(question, retriever, config, logger, gate=RELEVANCE_GATE):
    """
    Answer a question only if the retrieved context passes the gate.

    Args:
        question (str): The question.
        retriever (Retriever): Opened retriever.
        config (dict): Chat backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.
        gate (dict): Relevance thresholds; see check_context.

    Returns:
        dict: "question" (str), "status" ("ANSWERED",
            "REFUSED - weak retrieval", or "REFUSED - context does not
            answer it"), "answer" (str; REFUSAL_MESSAGE when refused),
            "sources" (list[str], cited chunk ids for an answer; empty for
            a refusal), "context_ids" (list[str], chunks given to the
            model), "check" (dict from check_context), and "model_called"
            (bool). When the gate fails, the chat model is not called.
    """
    chunks = retriever.retrieve(question, TOP_K)
    check = check_context(chunks, gate)
    result = {"question": question, "check": check, "context_ids": [], "sources": [], "model_called": False}

    if not check["allowed"]:
        result.update({"status": "REFUSED - weak retrieval", "answer": REFUSAL_MESSAGE})
        return result

    supporting = check["supporting_chunks"]
    ids = [chunk["chunk_id"] for chunk in supporting]
    messages = render_prompt(
        "grounded_answer",
        context=format_context(supporting),
        question=question,
        source_ids=", ".join(ids),
        max_sentences=ANSWER_MAX_SENTENCES,
    )
    answer = send_chat_completion(messages, config, logger, options=ANSWER_OPTIONS)["reply"].strip()
    result.update({"context_ids": ids, "model_called": True})

    if answer.startswith(MODEL_NO_ANSWER_PREFIX):
        result.update({"status": "REFUSED - context does not answer it", "answer": REFUSAL_MESSAGE})
        return result

    result.update({"status": "ANSWERED", "answer": answer, "sources": cited_sources(answer, ids) or ids})
    return result


def print_calibration(retriever, gate):
    """
    Show how the gate classifies the calibration questions.

    Args:
        retriever (Retriever): Opened retriever.
        gate (dict): Relevance thresholds.

    Returns:
        dict: Kind of question ("supported", "unsupported", "near miss")
            mapped to (number the gate classified as expected, total).
            Supported questions should be allowed; the others refused.
    """
    print()
    print("Calibration (retrieval and gate only; no chat model calls)")
    print("  {:<11} | {:>7} | {:>10} | {:<6} | {}".format("kind", "top sim", "supporting", "gate", "question"))
    tally = {}
    for kind, question in CALIBRATION_QUESTIONS:
        check = check_context(retriever.retrieve(question, TOP_K), gate)
        ok = check["allowed"] == (kind == "supported")
        hits, total = tally.get(kind, (0, 0))
        tally[kind] = (hits + ok, total + 1)
        print("  {:<11} | {:>7.3f} | {:>10} | {:<6} | {}{}".format(
            kind, check["top_similarity"], len(check["supporting_chunks"]),
            "answer" if check["allowed"] else "refuse", question,
            "" if ok else "   <-- passes the gate although the corpus does not answer it",
        ))
    for kind, (hits, total) in tally.items():
        print("  {:<11}: gate {} {} of {}".format(kind, "allowed" if kind == "supported" else "refused", hits, total))
    return tally


def result_lines(result, width):
    """
    Format one result as labelled lines for side-by-side display.

    Args:
        result (dict): As returned by guarded_answer.
        width (int): Column width in characters.

    Returns:
        list[str]: Wrapped lines covering question, status, answer,
            sources, gate signals, and whether the model was called.
    """
    check = result["check"]
    fields = [
        ("question", result["question"]),
        ("status", result["status"]),
        ("answer", result["answer"]),
        ("sources", ", ".join(result["sources"]) or "(none: refused)"),
        ("top similarity", "{:.3f} (min {:.2f})".format(check["top_similarity"], RELEVANCE_GATE["min_top_similarity"])
         if check["top_similarity"] is not None else "n/a (no results)"),
        ("supporting chunks", "{} >= {:.2f} (need {})".format(
            len(check["supporting_chunks"]), RELEVANCE_GATE["support_similarity"], RELEVANCE_GATE["min_supporting_chunks"])),
        ("gate", "PASSED" if check["allowed"] else "FAILED: " + "; ".join(check["reasons"])),
        ("chat model called", "yes" if result["model_called"] else "no (refused before generation)"),
    ]
    lines = []
    for label, value in fields:
        wrapped = textwrap.wrap(value, width - 19) or [""]
        lines.append("{:<18} {}".format(label + ":", wrapped[0]))
        lines.extend(" " * 19 + piece for piece in wrapped[1:])
        lines.append("")
    return lines


def print_side_by_side(left, right):
    """
    Print two results as adjacent columns.

    Args:
        left (dict): Result for the left column.
        right (dict): Result for the right column.

    Returns:
        None
    """
    width = (WRAP_WIDTH - 3) // 2
    left_lines = result_lines(left, width)
    right_lines = result_lines(right, width)
    print("  {:<{w}} | {}".format("SUPPORTED QUESTION", "UNSUPPORTED QUESTION", w=width))
    print("  {} | {}".format("-" * width, "-" * width))
    for row in range(max(len(left_lines), len(right_lines))):
        print("  {:<{w}} | {}".format(
            left_lines[row] if row < len(left_lines) else "",
            right_lines[row] if row < len(right_lines) else "", w=width,
        ))


def main():
    """
    Run the calibration, the side-by-side comparison, and the near miss.

    Args:
        None

    Returns:
        int: Process exit status: 0 on success, 1 on a reported failure.
    """
    logger = setup_logger(os.path.join(SCRIPT_DIR, "chat_exchange.log"))
    logger.handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
    try:
        config = get_chat_config(os.path.join(SCRIPT_DIR, ".env"))
        retriever = Retriever()
        print("Model: {} at {}; top {} chunks retrieved per question".format(config["model_name"], config["base_url"], TOP_K))
        print("Relevance gate (checked before generation): top similarity >= {:.2f}, and at least {} chunk(s) "
              "with similarity >= {:.2f}".format(RELEVANCE_GATE["min_top_similarity"],
                                                 RELEVANCE_GATE["min_supporting_chunks"],
                                                 RELEVANCE_GATE["support_similarity"]))
        print_calibration(retriever, RELEVANCE_GATE)

        answered = guarded_answer(ANSWERABLE_QUESTION, retriever, config, logger)
        refused = guarded_answer(UNSUPPORTED_QUESTION, retriever, config, logger)
        print()
        print("=" * WRAP_WIDTH)
        print("Supported vs unsupported question")
        print("=" * WRAP_WIDTH)
        print_side_by_side(answered, refused)

        near_miss = guarded_answer(NEAR_MISS_QUESTION, retriever, config, logger)
    except (ChatError, TemplateError, RuntimeError) as error:
        print("Error: {}".format(error))
        return 1

    print("=" * WRAP_WIDTH)
    print("Near miss: on-topic, but the corpus does not say how scanned images are handled")
    print("=" * WRAP_WIDTH)
    for line in result_lines(near_miss, WRAP_WIDTH - 2):
        print("  " + line)
    if near_miss["status"] == "ANSWERED":
        print("  LIMITATION: this question passed the relevance gate and the model produced an answer the")
        print("  corpus does not support. The gate stops off-topic questions and some near misses before")
        print("  generation; catching the rest needs a stronger answerability check than this model provides.")
    else:
        print("  Caught: status {}.".format(near_miss["status"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
