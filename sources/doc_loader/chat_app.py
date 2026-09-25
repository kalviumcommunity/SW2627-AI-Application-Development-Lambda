"""
Interactive chat path: answers questions typed at a prompt, one at a
time, using the shared "grounded_answer" prompt template.

Inputs:
    Questions read from standard input, one per line, until "exit" or
    end of input (so questions can also be piped in). Chat settings
    (CHAT_BASE_URL, CHAT_API_KEY, CHAT_MODEL) and retrieval settings come
    from environment variables or the ".env" file next to this script.
    Flags: --show-prompt prints the fully rendered prompt before each
    answer; --top-k sets how many chunks are retrieved.

Outputs:
    For each question, printed to stdout: the rendered prompt (with
    --show-prompt), the template name and fingerprint, the retrieved
    chunk ids, and the model's answer. Errors are reported in one line
    and the session continues.

Contains no prompt wording: the text sent to the model comes entirely
from prompts/templates/grounded_answer.txt. No paid API key is used or
required.
"""

import argparse
import logging
import os
import sys

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger
from prompts import TemplateError, format_context, load_template, preview_messages, render_prompt
from retriever import Retriever

TEMPLATE_NAME = "grounded_answer"
CHAT_MAX_SENTENCES = 3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def answer_question(question, retriever, config, logger, top_k, show_prompt):
    """
    Retrieve context, render the shared template, and ask the model.

    Args:
        question (str): The user's question.
        retriever (Retriever): Opened retriever.
        config (dict): Chat backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.
        top_k (int): Number of chunks to retrieve.
        show_prompt (bool): Whether to print the rendered prompt.

    Returns:
        str: The model's answer.
    """
    chunks = retriever.retrieve(question, top_k)
    messages = render_prompt(
        TEMPLATE_NAME,
        context=format_context(chunks),
        question=question,
        source_ids=", ".join(chunk["chunk_id"] for chunk in chunks),
        max_sentences=CHAT_MAX_SENTENCES,
    )
    if show_prompt:
        print("rendered prompt (template {} @ {}):".format(TEMPLATE_NAME, load_template(TEMPLATE_NAME)["fingerprint"]))
        print(preview_messages(messages))
    print("retrieved: {}".format(", ".join("{} ({:.3f})".format(c["chunk_id"], c["distance"]) for c in chunks)))
    reply = send_chat_completion(messages, config, logger, options={"temperature": 0, "max_tokens": 200})
    return reply["reply"].strip()


def main(argv):
    """
    Run the interactive question-and-answer loop.

    Args:
        argv (list[str]): Command-line arguments excluding the program
            name.

    Returns:
        int: Process exit status: 0 on a normal exit, 1 if setup failed.
    """
    parser = argparse.ArgumentParser(description="Ask questions about the corpus interactively.")
    parser.add_argument("--show-prompt", action="store_true", help="print the rendered prompt before each answer")
    parser.add_argument("--top-k", type=int, default=2, help="chunks retrieved per question")
    arguments = parser.parse_args(argv)

    logger = setup_logger(os.path.join(SCRIPT_DIR, "chat_exchange.log"))
    logger.handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
    try:
        config = get_chat_config(os.path.join(SCRIPT_DIR, ".env"))
        retriever = Retriever()
    except (ChatError, RuntimeError) as error:
        print("Error: {}".format(error))
        return 1

    interactive = sys.stdin.isatty()
    print("Chat path ready (model {}). Type a question, or 'exit' to quit.".format(config["model_name"]))
    while True:
        if interactive:
            print()
        try:
            line = input("you> " if interactive else "")
        except EOFError:
            break
        question = line.strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break
        if not interactive:
            print()
            print("you> {}".format(question))
        try:
            answer = answer_question(question, retriever, config, logger, arguments.top_k, arguments.show_prompt)
        except (ChatError, TemplateError) as error:
            print("Error: {}".format(error))
            continue
        print("assistant> {}".format(answer))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
