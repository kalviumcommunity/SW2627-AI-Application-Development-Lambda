"""
Shows the effect of well-constructed system and user messages on a chat
completion call by sending the same underlying questions with a vague
prompt and with a clear, constrained prompt, then comparing the replies.

Inputs:
    Backend settings from environment variables or the ".env" file next
    to this script (CHAT_BASE_URL, CHAT_API_KEY, CHAT_MODEL), read by
    chat_client.py. The default configuration uses a local Ollama server;
    Groq's free tier works by changing those three values. Two prompt
    variations and two questions are defined in this file: one question
    the assistant can answer, and one it cannot (it asks for live data),
    which tests what each prompt makes the model say when it cannot
    answer.

Outputs:
    Printed to stdout: for each question, the exact system and user
    messages of both variations, their replies side by side, and
    measured checks for each reply (word count, bullet count, whether it
    used the required "cannot answer" sentence). Then a written note
    naming the better prompt and explaining what made it clearer, more
    reliable, and better formatted. Requests and responses are also
    logged by chat_client.py to chat_exchange.log.

No paid API key is used or required.
"""

import logging
import os
import re
import sys
import textwrap

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger

ENV_FILE_NAME = ".env"
LOG_FILE_NAME = "chat_exchange.log"
COLUMN_WIDTH = 56
REQUEST_OPTIONS = {"temperature": 0, "seed": 7}

FALLBACK_SENTENCE = "I can't answer that from what I know about building retrieval pipelines."
MAX_WORDS = 60
REQUIRED_BULLETS = 3

VAGUE_SYSTEM = "You are a helpful assistant."

CLEAR_SYSTEM = (
    "You are a technical advisor for a team building a document retrieval "
    "(RAG) pipeline in Python.\n"
    "\n"
    "Step 1 - scope check. You only answer questions about loading, "
    "cleaning, chunking, embedding, or retrieving documents. You have no "
    "internet access and no live data.\n"
    "If the question is about anything else (for example stock prices, "
    "weather, news, sports), reply with exactly this sentence and nothing "
    "else:\n"
    "{fallback}\n"
    "\n"
    "Step 2 - answer format, only for in-scope questions:\n"
    "- Exactly {bullets} bullet points, each starting with \"- \".\n"
    "- Each bullet is one sentence of at most 20 words.\n"
    "- No bold text, headings, introduction, or closing sentence.\n"
    "- Plain, neutral tone. Do not write code unless asked."
).format(bullets=REQUIRED_BULLETS, fallback=FALLBACK_SENTENCE)

# Worked examples sent as real prior turns: one out-of-scope question
# answered with the fallback sentence, one in-scope question answered in
# the required format. Small models copy demonstrated behavior far more
# reliably than they follow the same rule stated only in prose.
CLEAR_EXAMPLE_TURNS = [
    {"role": "user", "content": "What is the weather in Paris today?"},
    {"role": "assistant", "content": FALLBACK_SENTENCE},
    {"role": "user", "content": "How should I clean PDF text before embedding it?"},
    {"role": "assistant", "content": (
        "- Normalize Unicode and unify line endings before anything else.\n"
        "- Remove repeated headers, footers, and page numbers.\n"
        "- Collapse extra whitespace but keep headings and numbers intact."
    )},
]

QUESTIONS = [
    {
        "label": "answerable question",
        "answerable": True,
        "vague_user": "chunk size?",
        "clear_user": (
            "What should I weigh when choosing a chunk size, measured in "
            "tokens, for embedding long prose reports for retrieval?"
        ),
    },
    {
        "label": "question it cannot answer (needs live data)",
        "answerable": False,
        "vague_user": "what's the apple stock price today",
        "clear_user": "What is Apple's stock price right now?",
    },
]


def build_variations(question):
    """
    Build the vague and clear message lists for one question.

    Args:
        question (dict): A question with "vague_user" and "clear_user"
            (str) keys.

    Returns:
        list[dict]: Two variations, each with "name" (str) and
            "messages" (list[dict]). The vague variation is a system and
            a user message; the clear one is a system message, the
            worked example turns, then the user message.
    """
    return [
        {"name": "vague", "messages": [
            {"role": "system", "content": VAGUE_SYSTEM},
            {"role": "user", "content": question["vague_user"]},
        ]},
        {"name": "clear", "messages": (
            [{"role": "system", "content": CLEAR_SYSTEM}]
            + CLEAR_EXAMPLE_TURNS
            + [{"role": "user", "content": question["clear_user"]}]
        )},
    ]


def measure_reply(reply, answerable):
    """
    Check a reply against the constraints the clear prompt sets.

    Args:
        reply (str): The model's reply.
        answerable (bool): Whether the question can be answered. For
            answerable questions the reply should be three short
            bullets; otherwise it should be exactly the fallback
            sentence.

    Returns:
        dict: "words" (int), "bullets" (int, lines starting with "- ",
            "* ", or "1. "-style numbering), "meets_constraints" (bool),
            and "summary" (str, a one-line human-readable result).
    """
    words = len(reply.split())
    bullets = sum(1 for line in reply.splitlines() if re.match(r"\s*([-*•]|\d+[.)])\s+", line))

    if answerable:
        meets = bullets == REQUIRED_BULLETS and words <= MAX_WORDS
        summary = "{} words, {} bullets -> {}".format(
            words, bullets, "meets format" if meets else "does not meet 3 bullets / <{} words".format(MAX_WORDS)
        )
    else:
        meets = reply.strip() == FALLBACK_SENTENCE
        summary = "{} words -> {}".format(
            words, "used the exact fallback sentence" if meets else "did not use the fallback sentence"
        )
    return {"words": words, "bullets": bullets, "meets_constraints": meets, "summary": summary}


def wrap_block(text, width):
    """
    Wrap multi-line text to a fixed width, keeping its line breaks.

    Args:
        text (str): The text to wrap.
        width (int): Maximum characters per line.

    Returns:
        list[str]: The wrapped lines, with blank lines preserved.
    """
    lines = []
    for paragraph in text.splitlines() or [""]:
        lines.extend(textwrap.wrap(paragraph, width) or [""])
    return lines


def print_side_by_side(left_title, left_text, right_title, right_text, width):
    """
    Print two blocks of text as adjacent columns.

    Args:
        left_title (str): Heading for the left column.
        left_text (str): Body of the left column.
        right_title (str): Heading for the right column.
        right_text (str): Body of the right column.
        width (int): Width of each column in characters.

    Returns:
        None
    """
    left = [left_title, "-" * width] + wrap_block(left_text, width)
    right = [right_title, "-" * width] + wrap_block(right_text, width)
    for row in range(max(len(left), len(right))):
        left_cell = left[row] if row < len(left) else ""
        right_cell = right[row] if row < len(right) else ""
        print("  {:<{w}} | {}".format(left_cell, right_cell, w=width))


def run_comparison(config, logger):
    """
    Send every question with both prompt variations.

    Args:
        config (dict): Backend settings, as returned by
            chat_client.get_chat_config.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        list[dict]: One entry per question, each with "question" (dict)
            and "results" (dict mapping "vague"/"clear" to a dict with
            "messages", "reply", "usage", and "checks").
    """
    comparisons = []
    for question in QUESTIONS:
        results = {}
        for variation in build_variations(question):
            response = send_chat_completion(variation["messages"], config, logger, options=REQUEST_OPTIONS)
            results[variation["name"]] = {
                "messages": variation["messages"],
                "reply": response["reply"].strip(),
                "usage": response["usage"],
                "checks": measure_reply(response["reply"], question["answerable"]),
            }
        comparisons.append({"question": question, "results": results})
    return comparisons


def print_comparisons(comparisons, config):
    """
    Print the inputs, side-by-side outputs, and checks for every question.

    Args:
        comparisons (list[dict]): Results as returned by run_comparison.
        config (dict): Backend settings, used to name the model.

    Returns:
        None
    """
    print()
    print("Model: {} at {} (temperature {}, seed {})".format(
        config["model_name"], config["base_url"], REQUEST_OPTIONS["temperature"], REQUEST_OPTIONS["seed"]
    ))
    print()
    print("Clear system message (used for every 'clear' request):")
    for line in CLEAR_SYSTEM.splitlines():
        print("  | {}".format(line))
    print()
    print("Worked example turns (sent after the clear system message, before the question):")
    for turn in CLEAR_EXAMPLE_TURNS:
        for index, line in enumerate(turn["content"].splitlines()):
            print("  | {:<10} {}".format("[{}]".format(turn["role"]) if index == 0 else "", line))
    print()
    print("Vague system message (used for every 'vague' request):")
    print("  | {}".format(VAGUE_SYSTEM))

    for number, comparison in enumerate(comparisons, start=1):
        question = comparison["question"]
        vague = comparison["results"]["vague"]
        clear = comparison["results"]["clear"]
        print()
        print("=" * (COLUMN_WIDTH * 2 + 5))
        print("Question {}: {}".format(number, question["label"]))
        print("=" * (COLUMN_WIDTH * 2 + 5))
        print_side_by_side(
            "VAGUE user message", question["vague_user"],
            "CLEAR user message", question["clear_user"], COLUMN_WIDTH,
        )
        print()
        print_side_by_side(
            "VAGUE reply", vague["reply"],
            "CLEAR reply", clear["reply"], COLUMN_WIDTH,
        )
        print()
        print_side_by_side(
            "VAGUE checks", vague["checks"]["summary"],
            "CLEAR checks", clear["checks"]["summary"], COLUMN_WIDTH,
        )


def score(comparisons, name):
    """
    Count how many replies of one variation met the constraints.

    Args:
        comparisons (list[dict]): Results as returned by run_comparison.
        name (str): "vague" or "clear".

    Returns:
        int: Number of questions whose reply for that variation met the
            constraints.
    """
    return sum(1 for comparison in comparisons if comparison["results"][name]["checks"]["meets_constraints"])


def print_note(comparisons):
    """
    Print the note naming the better prompt and explaining why.

    Args:
        comparisons (list[dict]): Results as returned by run_comparison.

    Returns:
        None
    """
    vague_score = score(comparisons, "vague")
    clear_score = score(comparisons, "clear")
    total = len(comparisons)

    print()
    print("=" * (COLUMN_WIDTH * 2 + 5))
    print("Note")
    print("=" * (COLUMN_WIDTH * 2 + 5))
    print("Replies meeting the format / fallback rules: clear {}/{}, vague {}/{}.".format(
        clear_score, total, vague_score, total
    ))
    print()
    for paragraph in NOTE_PARAGRAPHS:
        for line in textwrap.wrap(paragraph, COLUMN_WIDTH * 2 + 3):
            print("  {}".format(line))
        print()
    if clear_score <= vague_score:
        print("  CAVEAT: on this run the clear prompt did not measurably beat the vague one;")
        print("  the explanation above describes the intended effect, not this run's result.")


NOTE_PARAGRAPHS = [
    "Better prompt: the clear one. With only \"chunk size?\" and a generic "
    "system message, the model has to guess what \"chunk size\" means, so it "
    "answers about generic data processing (file I/O, memory, network "
    "packets) rather than retrieval, runs to 200+ words, and adds material "
    "nobody asked for. The clear user message names the domain (embedding "
    "prose reports for retrieval) and the unit (tokens), and the system "
    "message sets the role, so the reply stays on topic.",

    "Formatting became reliable because the limits are concrete and easy to "
    "check: exactly 3 bullets, each one sentence of at most 20 words, no "
    "bold or headings. An earlier draft asked for \"under 80 words\" for the "
    "whole reply; this model produced 133. Per-bullet limits are easier for "
    "a small model to follow than a total word count.",

    "The biggest reliability gain is on the question it cannot answer. The "
    "vague prompt invents a stock price. Stating the fallback rule in the "
    "system message was not enough: in earlier drafts this 1.5B model still "
    "made up a price. What worked was (1) putting the scope check first, "
    "before any formatting rules, and (2) adding two short worked examples "
    "as real prior turns: one off-topic question answered with the exact "
    "fallback sentence, and one on-topic question answered in the required "
    "format. The model copies demonstrated behavior much more reliably than "
    "it follows a rule described in prose.",

    "Limit: the clear prompt fixes scope, format, and refusals, but not "
    "depth. The three bullets are still generic, which reflects the small "
    "model more than the prompt; a larger model with the same prompt "
    "should give more specific advice.",
]


def main():
    """
    Run the comparison and print the results and note.

    Args:
        None

    Returns:
        int: Process exit status: 0 on success, 1 on a reported failure.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logger = setup_logger(os.path.join(script_dir, LOG_FILE_NAME))
    logger.handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
    try:
        config = get_chat_config(os.path.join(script_dir, ENV_FILE_NAME))
        comparisons = run_comparison(config, logger)
    except ChatError as error:
        print("Error: {}".format(error))
        return 1

    print_comparisons(comparisons, config)
    print_note(comparisons)
    return 0


if __name__ == "__main__":
    sys.exit(main())
