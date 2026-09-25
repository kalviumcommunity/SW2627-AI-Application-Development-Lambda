"""
Batch/CLI path: answers every question in a file, non-interactively,
using the shared "grounded_answer" prompt template.

Inputs:
    A text file of questions, one per line; blank lines and lines
    starting with "#" are skipped (default: batch_questions.txt next to
    this script). Chat and retrieval settings come from environment
    variables or the ".env" file next to this script.
    Flags: --questions PATH, --output PATH, --show-prompts (print every
    rendered prompt), --top-k N.

Outputs:
    A JSON Lines file (default: batch_answers.jsonl next to this script)
    with one record per question: the question, the answer, the chunk
    ids used, and the template name and fingerprint that produced it.
    Printed to stdout: the rendered prompt for each question (with
    --show-prompts), each answer, and a one-line summary. A question
    that fails is recorded with its error and the batch continues.

Contains no prompt wording: the text sent to the model comes entirely
from prompts/templates/grounded_answer.txt. No paid API key is used or
required.
"""

import argparse
import json
import logging
import os
import sys

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger
from prompts import TemplateError, format_context, load_template, preview_messages, render_prompt
from retriever import Retriever

TEMPLATE_NAME = "grounded_answer"
BATCH_MAX_SENTENCES = 2
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def read_questions(path):
    """
    Read questions from a text file.

    Args:
        path (str): Path to the questions file.

    Returns:
        list[str]: Non-blank lines that do not start with "#".
    """
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip() and not line.strip().startswith("#")]


def answer_one(question, retriever, config, logger, top_k):
    """
    Retrieve context, render the shared template, and ask the model.

    Args:
        question (str): The question.
        retriever (Retriever): Opened retriever.
        config (dict): Chat backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.
        top_k (int): Number of chunks to retrieve.

    Returns:
        tuple[list[dict], list[dict], str]: (rendered messages, retrieved
            chunks, answer).
    """
    chunks = retriever.retrieve(question, top_k)
    messages = render_prompt(
        TEMPLATE_NAME,
        context=format_context(chunks),
        question=question,
        source_ids=", ".join(chunk["chunk_id"] for chunk in chunks),
        max_sentences=BATCH_MAX_SENTENCES,
    )
    reply = send_chat_completion(messages, config, logger, options={"temperature": 0, "max_tokens": 200})
    return messages, chunks, reply["reply"].strip()


def main(argv):
    """
    Answer every question in the input file and write the results.

    Args:
        argv (list[str]): Command-line arguments excluding the program
            name.

    Returns:
        int: Process exit status: 0 if every question was answered, 1 if
            setup failed or any question failed.
    """
    parser = argparse.ArgumentParser(description="Answer a file of questions about the corpus.")
    parser.add_argument("--questions", default=os.path.join(SCRIPT_DIR, "batch_questions.txt"))
    parser.add_argument("--output", default=os.path.join(SCRIPT_DIR, "batch_answers.jsonl"))
    parser.add_argument("--show-prompts", action="store_true", help="print every rendered prompt")
    parser.add_argument("--top-k", type=int, default=3, help="chunks retrieved per question")
    arguments = parser.parse_args(argv)

    logger = setup_logger(os.path.join(SCRIPT_DIR, "chat_exchange.log"))
    logger.handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
    try:
        config = get_chat_config(os.path.join(SCRIPT_DIR, ".env"))
        retriever = Retriever()
        questions = read_questions(arguments.questions)
        fingerprint = load_template(TEMPLATE_NAME)["fingerprint"]
    except (ChatError, RuntimeError, OSError, TemplateError) as error:
        print("Error: {}".format(error))
        return 1

    print("Batch path: {} question(s) from {} (model {})".format(len(questions), arguments.questions, config["model_name"]))
    failures = 0
    with open(arguments.output, "w", encoding="utf-8") as output:
        for number, question in enumerate(questions, start=1):
            print()
            print("[{}/{}] {}".format(number, len(questions), question))
            record = {"question": question, "template": TEMPLATE_NAME, "template_fingerprint": fingerprint}
            try:
                messages, chunks, answer = answer_one(question, retriever, config, logger, arguments.top_k)
            except (ChatError, TemplateError) as error:
                failures += 1
                record.update({"answer": None, "chunk_ids": [], "error": str(error)})
                print("  error: {}".format(error))
            else:
                if arguments.show_prompts:
                    print("  rendered prompt (template {} @ {}):".format(TEMPLATE_NAME, fingerprint))
                    print(preview_messages(messages, indent="    | "))
                record.update({"answer": answer, "chunk_ids": [chunk["chunk_id"] for chunk in chunks], "error": None})
                print("  answer: {}".format(answer))
            output.write(json.dumps(record, ensure_ascii=False) + "\n")

    print()
    print("Answered {} of {}; results written to {}".format(len(questions) - failures, len(questions), arguments.output))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
