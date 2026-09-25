"""
Multi-turn conversational retrieval: tracks chat history, rewrites each
follow-up question into a standalone query using that history, retrieves
context with the rewritten query, and answers from it.

Inputs:
    A scripted dialogue defined in this file (a first question, two
    follow-ups that only make sense given earlier turns, and a question
    on a new topic). Chat settings (CHAT_BASE_URL, CHAT_API_KEY,
    CHAT_MODEL) and retrieval settings (the EMBEDDING_* and VECTOR_DB_*
    variables) come from environment variables or the ".env" file next
    to this script. Retrieval uses the chromadb collection built by
    index_corpus.py. Prompt wording comes from
    prompts/templates/rewrite_query.txt and grounded_answer.txt.

Outputs:
    Printed to stdout for every turn: the raw question, the rewritten
    standalone query (for follow-ups), the retrieved chunks with their
    distances and a preview of their text, and the final answer. For
    each follow-up, a comparison against retrieving with the raw
    follow-up text instead: which chunks that returns, whether the
    chunk known to answer the question was among them, and the answer
    it leads to. A summary table closes the run.

No paid API key is used or required.
"""

import logging
import os
import sys
import textwrap

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger
from prompts import TemplateError, format_context, render_prompt
from retriever import Retriever

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WRAP_WIDTH = 100
TOP_K = 3
HISTORY_TURNS = 3
ANSWER_MAX_SENTENCES = 3
REWRITE_OPTIONS = {"temperature": 0, "max_tokens": 60}
ANSWER_OPTIONS = {"temperature": 0, "max_tokens": 200}

# The scripted dialogue. "expected_chunk" is the chunk already known to
# answer the question, used to check retrieval; "follow_up" marks turns
# that depend on earlier ones. For follow-ups, "must_mention" is the
# term the rewrite has to resolve to, and "must_not_mention" the wrong
# referent: a chunk can be retrieved for the wrong reason (both chunking
# strategies appear in several chunks), so retrieval alone does not
# prove the follow-up was understood.
DIALOGUE = [
    {"question": "What two chunking strategies does the design report compare?",
     "follow_up": False, "expected_chunk": "long_report.txt#4"},
    {"question": "Why is the second one the better default?",
     "follow_up": True, "expected_chunk": "long_report.txt#10",
     "must_mention": "paragraph", "must_not_mention": "fixed"},
    {"question": "And when is the first one still worth using?",
     "follow_up": True, "expected_chunk": "long_report.txt#11",
     "must_mention": "fixed", "must_not_mention": "paragraph"},
    {"question": "What does the cleaning stage do to line endings?",
     "follow_up": False, "expected_chunk": "long_report.txt#2"},
]


def rewrite_resolved(step, standalone):
    """
    Check whether a follow-up's rewrite names the right referent.

    Args:
        step (dict): A DIALOGUE entry.
        standalone (str): The rewritten query.

    Returns:
        bool or None: True if the rewrite contains the step's
            "must_mention" term and not its "must_not_mention" term,
            False otherwise, or None for turns that are not follow-ups.
    """
    if not step["follow_up"]:
        return None
    text = standalone.lower()
    return step["must_mention"] in text and step["must_not_mention"] not in text


class Conversation:
    """
    Conversation history: each turn's raw question, the standalone
    question it was resolved to, the chunks used, and the answer.
    """

    def __init__(self, history_turns):
        """
        Start an empty conversation.

        Args:
            history_turns (int): How many recent turns are shown to the
                rewrite step.

        Returns:
            None
        """
        self.history_turns = history_turns
        self.turns = []

    def add_turn(self, raw_question, standalone_question, chunks, answer):
        """
        Record one completed turn.

        Args:
            raw_question (str): The question as the user asked it.
            standalone_question (str): The question after rewriting.
            chunks (list[dict]): Chunks used to answer it.
            answer (str): The assistant's answer.

        Returns:
            None
        """
        self.turns.append({
            "raw_question": raw_question,
            "standalone_question": standalone_question,
            "chunk_ids": [chunk["chunk_id"] for chunk in chunks],
            "answer": answer,
        })

    def history_text(self):
        """
        Format recent turns for the rewrite prompt.

        Args:
            None

        Returns:
            str: The last history_turns turns as alternating "user:" and
                "assistant:" lines. The user line shows the standalone
                version of each question, so a chain of follow-ups stays
                resolvable.
        """
        lines = []
        for turn in self.turns[-self.history_turns:]:
            lines.append("user: {}".format(turn["standalone_question"]))
            lines.append("assistant: {}".format(turn["answer"]))
        return "\n".join(lines)


def clean_rewrite(reply, raw_question):
    """
    Turn the model's rewrite reply into a usable query.

    Args:
        reply (str): The model's reply to the rewrite prompt.
        raw_question (str): The original question, used as a fallback.

    Returns:
        tuple[str, str or None]: (query, note). The query is the first
            non-empty line of the reply with any "Rewritten:" label and
            surrounding quotes removed. If that is empty or implausibly
            long (a sign the model answered instead of rewriting), the
            raw question is returned with a note saying so.
    """
    lines = [line.strip() for line in reply.splitlines() if line.strip()]
    query = lines[0] if lines else ""
    if query.lower().startswith("rewritten:"):
        query = query[len("rewritten:"):].strip()
    query = query.strip("\"'`").strip()
    if not query:
        return raw_question, "rewrite was empty; used the raw question"
    if len(query) > 3 * len(raw_question) + 100:
        return raw_question, "rewrite was implausibly long; used the raw question"
    return query, None


def rewrite_question(question, conversation, config, logger):
    """
    Rewrite a question into a standalone query using the history.

    Args:
        question (str): The raw question.
        conversation (Conversation): The conversation so far.
        config (dict): Chat backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        tuple[str, str or None]: (standalone query, note). On the first
            turn there is no history, so the question is returned as is.
    """
    if not conversation.turns:
        return question, "first turn: no history to resolve against"
    messages = render_prompt("rewrite_query", history=conversation.history_text(), question=question)
    reply = send_chat_completion(messages, config, logger, options=REWRITE_OPTIONS)["reply"]
    return clean_rewrite(reply, question)


def answer_from_chunks(question, chunks, config, logger):
    """
    Answer a question from retrieved chunks with the shared template.

    Args:
        question (str): The question to answer.
        chunks (list[dict]): Retrieved chunks.
        config (dict): Chat backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        str: The model's answer.
    """
    messages = render_prompt(
        "grounded_answer",
        context=format_context(chunks),
        question=question,
        source_ids=", ".join(chunk["chunk_id"] for chunk in chunks),
        max_sentences=ANSWER_MAX_SENTENCES,
    )
    return send_chat_completion(messages, config, logger, options=ANSWER_OPTIONS)["reply"].strip()


def print_wrapped(prefix, text):
    """
    Print text wrapped to the page width with a hanging indent.

    Args:
        prefix (str): Text printed before the first line.
        text (str): The text to print.

    Returns:
        None
    """
    lines = textwrap.wrap(" ".join(text.split()), WRAP_WIDTH - len(prefix)) or [""]
    print(prefix + lines[0])
    for line in lines[1:]:
        print(" " * len(prefix) + line)


def print_chunks(label, chunks, expected_chunk):
    """
    Print retrieved chunks with distances and a short text preview.

    Args:
        label (str): Heading for this list.
        chunks (list[dict]): Retrieved chunks.
        expected_chunk (str): Chunk id known to answer the question;
            marked when present.

    Returns:
        bool: True if expected_chunk was among the chunks.
    """
    found = any(chunk["chunk_id"] == expected_chunk for chunk in chunks)
    print("  {} (known answer {}: {})".format(label, expected_chunk, "RETRIEVED" if found else "NOT retrieved"))
    for chunk in chunks:
        preview = " ".join(chunk["text"].split())
        print("    {:<2} {:<20} distance {:.3f}  {}".format(
            "*" if chunk["chunk_id"] == expected_chunk else "", chunk["chunk_id"], chunk["distance"],
            preview[:52] + ("..." if len(preview) > 52 else ""),
        ))
    return found


def run_dialogue(config, retriever, logger):
    """
    Run the scripted dialogue end to end and print every turn.

    Args:
        config (dict): Chat backend settings.
        retriever (Retriever): Opened retriever.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        list[dict]: One row per turn with "turn", "follow_up",
            "rewritten" (bool, whether the query changed), "resolved"
            (bool or None, from rewrite_resolved), "rewritten_found"
            (bool) and, for follow-ups, "raw_found" (bool): whether the
            known answer chunk was retrieved.
    """
    conversation = Conversation(HISTORY_TURNS)
    rows = []
    for number, step in enumerate(DIALOGUE, start=1):
        raw = step["question"]
        print()
        print("=" * WRAP_WIDTH)
        print("Turn {}{}".format(number, "  (follow-up)" if step["follow_up"] else ""))
        print("=" * WRAP_WIDTH)
        print_wrapped("  raw question:       ", raw)

        standalone, note = rewrite_question(raw, conversation, config, logger)
        if note:
            print("  rewritten query:    (not rewritten: {})".format(note))
        else:
            print_wrapped("  rewritten query:    ", standalone + ("   [unchanged]" if standalone == raw else ""))
        resolved = rewrite_resolved(step, standalone)
        if resolved is not None:
            print("  rewrite resolved to the right referent (\"{}\"): {}".format(
                step["must_mention"], "yes" if resolved else "NO"
            ))

        chunks = retriever.retrieve(standalone, TOP_K)
        rewritten_found = print_chunks("context retrieved with the rewritten query", chunks, step["expected_chunk"])
        answer = answer_from_chunks(standalone, chunks, config, logger)
        print_wrapped("  answer:             ", answer)

        row = {"turn": number, "follow_up": step["follow_up"], "rewritten": standalone != raw,
               "resolved": resolved, "rewritten_found": rewritten_found, "raw_found": None}
        if step["follow_up"]:
            print()
            print("  --- without the rewrite: retrieve and answer with the raw follow-up text ---")
            raw_chunks = retriever.retrieve(raw, TOP_K)
            row["raw_found"] = print_chunks("context retrieved with the raw text", raw_chunks, step["expected_chunk"])
            print_wrapped("  answer:             ", answer_from_chunks(raw, raw_chunks, config, logger))

        conversation.add_turn(raw, standalone, chunks, answer)
        rows.append(row)
    return rows


def print_summary(rows):
    """
    Print a per-turn summary of rewriting and retrieval.

    Args:
        rows (list[dict]): As returned by run_dialogue.

    Returns:
        None
    """
    print()
    print("=" * WRAP_WIDTH)
    print("Summary: did the rewrite resolve the follow-up, and was the answering chunk retrieved?")
    print("=" * WRAP_WIDTH)
    print("  turn | kind       | query changed | right referent | chunk found (rewritten) | chunk found (raw text)")
    for row in rows:
        print("  {:>4} | {:<10} | {:<13} | {:<14} | {:<23} | {}".format(
            row["turn"], "follow-up" if row["follow_up"] else "standalone",
            "yes" if row["rewritten"] else "no",
            "n/a" if row["resolved"] is None else ("yes" if row["resolved"] else "NO"),
            "yes" if row["rewritten_found"] else "NO",
            "n/a" if row["raw_found"] is None else ("yes" if row["raw_found"] else "NO"),
        ))


def main():
    """
    Run the multi-turn conversational retrieval demonstration.

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
        print("Model: {} at {}; retrieving top {} chunks per query".format(config["model_name"], config["base_url"], TOP_K))
        rows = run_dialogue(config, retriever, logger)
    except (ChatError, TemplateError, RuntimeError) as error:
        print("Error: {}".format(error))
        return 1
    print_summary(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
