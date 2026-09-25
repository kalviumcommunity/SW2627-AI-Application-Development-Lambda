"""
Demonstrates how generation parameters change a chat completion's output:
temperature, max_tokens, stop, and top_p.

Inputs:
    Backend settings from environment variables or the ".env" file next
    to this script (CHAT_BASE_URL, CHAT_API_KEY, CHAT_MODEL), read by
    chat_client.py. The default configuration uses a local Ollama server;
    Groq's free tier works by changing those three values. The prompts
    and parameter values compared are defined in this file.

Outputs:
    Printed to stdout, all in one run:
        - Temperature: the same prompt sampled several times at each of
          several temperatures, every reply shown, plus how many replies
          were distinct and how different their wording was.
        - max_tokens: one prompt with no limit and with a small limit,
          showing reply length, token count, and finish reason.
        - stop: a numbered-list prompt with and without a stop sequence.
        - top_p: the same prompt at a high temperature with top_p 1.0
          and with a small top_p, sampled several times.
        - A summary table of every comparison, and a note on recommended
          settings for grounded, factual answers.
    Requests and responses are also logged by chat_client.py to
    chat_exchange.log.

No paid API key is used or required.
"""

import logging
import os
import sys
import textwrap

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger

ENV_FILE_NAME = ".env"
LOG_FILE_NAME = "chat_exchange.log"
SAMPLES_PER_SETTING = 3
WRAP_WIDTH = 100

SYSTEM_MESSAGE = "You are a helpful assistant for a team building a document retrieval pipeline."

TEMPERATURE_PROMPT = "In one sentence, describe what a vector database is used for."
TEMPERATURES = [0.0, 0.7, 1.5]

MAX_TOKENS_PROMPT = "Explain why documents are split into chunks before they are embedded."
MAX_TOKENS_LIMIT = 25

STOP_PROMPT = "List the 5 main stages of a document retrieval pipeline as a numbered list, one line each."
STOP_SEQUENCE = "\n4."

TOP_P_PROMPT = TEMPERATURE_PROMPT
TOP_P_TEMPERATURE = 1.5
TOP_P_VALUES = [1.0, 0.1]

NOTE = [
    "Recommended settings for grounded, factual answers (for example, answering from retrieved chunks):",
    "- temperature 0 to 0.2. Low temperature makes the model pick its most likely wording, so the same "
    "question gets the same answer and the model is less likely to wander from the source text. The "
    "temperature runs above show this: at 0 every sample is the same reply; as temperature rises the "
    "samples diverge in wording and, at the highest setting, in content.",
    "- max_tokens sized to the answer you expect plus headroom (roughly 150-300 for a short grounded "
    "answer). It bounds cost and latency, but it cuts the reply off rather than making it shorter, as "
    "the max_tokens example shows. Ask for brevity in the prompt, and treat finish_reason \"length\" "
    "as a truncated answer to handle, not a normal one.",
    "- stop sequences are optional. They are useful when the output has a known end marker, such as a "
    "delimiter you asked for, or to stop the model from continuing into an invented next "
    "\"Question:\" turn. The reply ends at the stop point with no sentence clean-up, and the stop "
    "example shows finish_reason is \"stop\" either way, so it cannot tell a natural ending from a "
    "stop-sequence cut.",
    "- top_p can stay at 1.0. A small top_p restricts sampling to the few most likely tokens, so it "
    "also stabilizes output: the top_p 0.1 samples above behave like temperature 0 even at "
    "temperature 1.5. But once temperature is near 0 there is little left for top_p to change, and "
    "tuning both at once makes the effect of each harder to reason about, so set one and leave the "
    "other at its default.",
]


def generate(prompt, config, logger, options):
    """
    Send one prompt with the given generation parameters.

    Args:
        prompt (str): The user message.
        config (dict): Backend settings from chat_client.get_chat_config.
        logger (logging.Logger): Logger passed to send_chat_completion.
        options (dict): Generation parameters merged into the request,
            such as "temperature", "max_tokens", "stop", or "top_p".

    Returns:
        dict: "reply" (str), "completion_tokens" (int or None), and
            "finish_reason" (str or None).
    """
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": prompt},
    ]
    result = send_chat_completion(messages, config, logger, options=options)
    usage = result["usage"] or {}
    return {
        "reply": result["reply"].strip(),
        "completion_tokens": usage.get("completion_tokens"),
        "finish_reason": result["finish_reason"],
    }


def word_set(text):
    """
    Reduce a reply to its set of lowercase words.

    Args:
        text (str): The reply.

    Returns:
        set[str]: Words with surrounding punctuation removed.
    """
    return {word.strip(".,;:!?\"'()").lower() for word in text.split()} - {""}


def mean_pairwise_difference(replies):
    """
    Measure how different a set of replies are from each other.

    Args:
        replies (list[str]): Two or more replies.

    Returns:
        float: The average, over every pair, of 1 minus the Jaccard
            similarity of the two replies' word sets. 0.0 means every
            reply uses the same words; 1.0 means no words are shared.
    """
    sets = [word_set(reply) for reply in replies]
    distances = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            union = sets[i] | sets[j]
            distances.append(1 - len(sets[i] & sets[j]) / len(union) if union else 0.0)
    return sum(distances) / len(distances) if distances else 0.0


def sample_setting(prompt, config, logger, options, samples):
    """
    Sample one prompt several times with the same parameters.

    Args:
        prompt (str): The user message.
        config (dict): Backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.
        options (dict): Generation parameters. No seed is set, so
            sampling is free to vary between calls.
        samples (int): Number of calls to make.

    Returns:
        dict: "options" (dict), "replies" (list[str]), "distinct" (int,
            number of different replies), and "difference" (float, as
            returned by mean_pairwise_difference).
    """
    replies = [generate(prompt, config, logger, options)["reply"] for _ in range(samples)]
    return {
        "options": options,
        "replies": replies,
        "distinct": len(set(replies)),
        "difference": mean_pairwise_difference(replies),
    }


def print_wrapped(label, text, indent=4):
    """
    Print a labelled, wrapped block of text.

    Args:
        label (str): Label printed before the text.
        text (str): The text; its own line breaks are kept.
        indent (int): Spaces before continuation lines.

    Returns:
        None
    """
    prefix = " " * indent
    lines = text.splitlines() or [""]
    first = True
    for line in lines:
        wrapped = textwrap.wrap(line, WRAP_WIDTH - indent) or [""]
        for piece in wrapped:
            print("{}{}".format(prefix + label + " " if first else prefix + " " * (len(label) + 1), piece))
            first = False


def print_header(title):
    """
    Print a section header.

    Args:
        title (str): The section title.

    Returns:
        None
    """
    print()
    print("=" * WRAP_WIDTH)
    print(title)
    print("=" * WRAP_WIDTH)


def run_temperature(config, logger):
    """
    Compare the same prompt across several temperatures.

    Args:
        config (dict): Backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        list[dict]: One sample_setting result per temperature.
    """
    print_header("1. temperature  (same prompt, {} samples each, no seed)".format(SAMPLES_PER_SETTING))
    print("  prompt: {}".format(TEMPERATURE_PROMPT))
    results = []
    for temperature in TEMPERATURES:
        result = sample_setting(TEMPERATURE_PROMPT, config, logger, {"temperature": temperature}, SAMPLES_PER_SETTING)
        results.append(result)
        print()
        print("  temperature {}: {} distinct of {}, wording difference {:.2f}".format(
            temperature, result["distinct"], SAMPLES_PER_SETTING, result["difference"]
        ))
        for number, reply in enumerate(result["replies"], start=1):
            print_wrapped("[{}]".format(number), reply)
    return results


def run_max_tokens(config, logger):
    """
    Compare one prompt with no length limit and with a small max_tokens.

    Args:
        config (dict): Backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        dict: "unlimited" and "limited", each a generate result.
    """
    print_header("2. max_tokens  (temperature 0, so only the limit differs)")
    print("  prompt: {}".format(MAX_TOKENS_PROMPT))
    unlimited = generate(MAX_TOKENS_PROMPT, config, logger, {"temperature": 0})
    limited = generate(MAX_TOKENS_PROMPT, config, logger, {"temperature": 0, "max_tokens": MAX_TOKENS_LIMIT})
    for label, result in (("no max_tokens", unlimited), ("max_tokens={}".format(MAX_TOKENS_LIMIT), limited)):
        print()
        print("  {}: {} completion tokens, {} words, finish_reason={}".format(
            label, result["completion_tokens"], len(result["reply"].split()), result["finish_reason"]
        ))
        print_wrapped(">", result["reply"])
    return {"unlimited": unlimited, "limited": limited}


def run_stop(config, logger):
    """
    Compare a numbered-list prompt with and without a stop sequence.

    Args:
        config (dict): Backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        dict: "without" and "with", each a generate result.
    """
    print_header("3a. stop  (temperature 0, stop sequence {!r})".format(STOP_SEQUENCE))
    print("  prompt: {}".format(STOP_PROMPT))
    without = generate(STOP_PROMPT, config, logger, {"temperature": 0})
    with_stop = generate(STOP_PROMPT, config, logger, {"temperature": 0, "stop": [STOP_SEQUENCE]})
    for label, result in (("no stop", without), ("stop={!r}".format(STOP_SEQUENCE), with_stop)):
        print()
        print("  {}: {} completion tokens, finish_reason={}".format(
            label, result["completion_tokens"], result["finish_reason"]
        ))
        print_wrapped(">", result["reply"])
    return {"without": without, "with": with_stop}


def run_top_p(config, logger):
    """
    Compare top_p values at a high temperature.

    Args:
        config (dict): Backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        list[dict]: One sample_setting result per top_p value.
    """
    print_header("3b. top_p  (temperature {}, {} samples each, no seed)".format(TOP_P_TEMPERATURE, SAMPLES_PER_SETTING))
    print("  prompt: {}".format(TOP_P_PROMPT))
    results = []
    for top_p in TOP_P_VALUES:
        options = {"temperature": TOP_P_TEMPERATURE, "top_p": top_p}
        result = sample_setting(TOP_P_PROMPT, config, logger, options, SAMPLES_PER_SETTING)
        results.append(result)
        print()
        print("  top_p {}: {} distinct of {}, wording difference {:.2f}".format(
            top_p, result["distinct"], SAMPLES_PER_SETTING, result["difference"]
        ))
        for number, reply in enumerate(result["replies"], start=1):
            print_wrapped("[{}]".format(number), reply)
    return results


def print_summary(temperature_results, max_tokens_result, stop_result, top_p_results):
    """
    Print one table summarizing every comparison.

    Args:
        temperature_results (list[dict]): From run_temperature.
        max_tokens_result (dict): From run_max_tokens.
        stop_result (dict): From run_stop.
        top_p_results (list[dict]): From run_top_p.

    Returns:
        None
    """
    print_header("Summary of every comparison")
    print("  {:<34} | {}".format("setting", "effect measured"))
    print("  {}-+-{}".format("-" * 34, "-" * 60))
    for result in temperature_results:
        print("  {:<34} | {} distinct of {}, wording difference {:.2f}".format(
            "temperature {}".format(result["options"]["temperature"]),
            result["distinct"], SAMPLES_PER_SETTING, result["difference"],
        ))
    for label, key in (("no max_tokens", "unlimited"), ("max_tokens={}".format(MAX_TOKENS_LIMIT), "limited")):
        result = max_tokens_result[key]
        print("  {:<34} | {} tokens, {} words, finish_reason={}".format(
            label, result["completion_tokens"], len(result["reply"].split()), result["finish_reason"]
        ))
    for label, key in (("no stop", "without"), ("stop={!r}".format(STOP_SEQUENCE), "with")):
        result = stop_result[key]
        numbered = sum(1 for line in result["reply"].splitlines() if line.strip()[:2].rstrip(".").isdigit())
        print("  {:<34} | {} numbered lines, {} tokens, finish_reason={}".format(
            label, numbered, result["completion_tokens"], result["finish_reason"]
        ))
    for result in top_p_results:
        print("  {:<34} | {} distinct of {}, wording difference {:.2f}".format(
            "temperature {}, top_p {}".format(TOP_P_TEMPERATURE, result["options"]["top_p"]),
            result["distinct"], SAMPLES_PER_SETTING, result["difference"],
        ))


def print_note():
    """
    Print the recommended settings for grounded, factual answers.

    Args:
        None

    Returns:
        None
    """
    print_header("Note")
    for paragraph in NOTE:
        for index, line in enumerate(textwrap.wrap(paragraph, WRAP_WIDTH - 4)):
            print("  {}{}".format("" if index == 0 or not paragraph.startswith("-") else "  ", line))
        print()


def main():
    """
    Run every parameter comparison and print the results and note.

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
        print("Model: {} at {}".format(config["model_name"], config["base_url"]))
        temperature_results = run_temperature(config, logger)
        max_tokens_result = run_max_tokens(config, logger)
        stop_result = run_stop(config, logger)
        top_p_results = run_top_p(config, logger)
    except ChatError as error:
        print("Error: {}".format(error))
        return 1

    print_summary(temperature_results, max_tokens_result, stop_result, top_p_results)
    print_note()
    return 0


if __name__ == "__main__":
    sys.exit(main())
