"""
Gets a chat model to return structured JSON reliably and handles its
replies safely: parse, validate, recover, or reject cleanly.

Inputs:
    Backend settings from environment variables or the ".env" file next
    to this script (CHAT_BASE_URL, CHAT_API_KEY, CHAT_MODEL), read by
    chat_client.py. A few real chunks from the sample corpus (run
    through the existing load/clean/chunk pipeline) serve as context,
    and a fixed set of demonstration cases is defined in this file:
    normal questions, real malformed replies produced by the model
    itself, and deliberately injected malformed replies.

Outputs:
    For every case, printed to stdout: each step taken (model call,
    parse, local repair, validation, model repair), the raw text at each
    step, and the final result: "ok" with the parsed dict, "recovered"
    with the parsed dict and how it was recovered, or "rejected" with
    the reasons. A summary table follows. Nothing raises past the
    handling code; a rejected reply is reported, never used.

The requested structure is:
    {"answer": str, "source": str, "found": bool}
where "source" must be the id of one of the supplied context chunks, or
"none" when "found" is false. The backend's JSON-schema response mode is
used when available, falling back to its plain JSON mode. No paid API
key is used or required.
"""

import json
import logging
import os
import re
import sys
import textwrap

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger

ENV_FILE_NAME = ".env"
LOG_FILE_NAME = "chat_exchange.log"
WRAP_WIDTH = 100
CONTEXT_CHUNK_IDS = ["long_report.txt#1", "long_report.txt#2", "readme.md#0"]
NO_SOURCE = "none"
BASE_OPTIONS = {"temperature": 0}

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "source": {"type": "string"},
        "found": {"type": "boolean"},
    },
    "required": ["answer", "source", "found"],
    "additionalProperties": False,
}
REQUIRED_FIELDS = {"answer": str, "source": str, "found": bool}

SYSTEM_TEMPLATE = (
    "You answer questions using only the context chunks provided. Each chunk is labelled with its id.\n"
    "Reply with a single JSON object and nothing else, exactly this shape:\n"
    "{{\"answer\": string, \"source\": string, \"found\": boolean}}\n"
    "- \"answer\": one or two sentences answering the question from the context.\n"
    "- \"source\": the id of the chunk the answer comes from, one of: {ids}.\n"
    "- \"found\": true if the context answers the question.\n"
    "If the context does not answer the question, reply with "
    "{{\"answer\": \"The provided context does not say.\", \"source\": \"none\", \"found\": false}}."
)


def response_format_for(mode):
    """
    Build the response_format request field for a JSON mode.

    Args:
        mode (str or None): "json_schema", "json_object", or None for no
            JSON mode.

    Returns:
        dict or None: The response_format value to send, or None.
    """
    if mode == "json_schema":
        return {"type": "json_schema", "json_schema": {"name": "grounded_answer", "schema": ANSWER_SCHEMA, "strict": True}}
    if mode == "json_object":
        return {"type": "json_object"}
    return None


def build_messages(question, chunks):
    """
    Build the system and user messages for one question.

    Args:
        question (str): The question to answer.
        chunks (list[dict]): Context chunks with "chunk_id" and "text".

    Returns:
        list[dict]: A system message describing the JSON structure and a
            user message holding the context and question.
    """
    ids = ", ".join(chunk["chunk_id"] for chunk in chunks)
    context = "\n\n".join("[{}]\n{}".format(chunk["chunk_id"], chunk["text"]) for chunk in chunks)
    return [
        {"role": "system", "content": SYSTEM_TEMPLATE.format(ids=ids)},
        {"role": "user", "content": "Context:\n{}\n\nQuestion: {}".format(context, question)},
    ]


def call_model(messages, config, logger, mode, extra_options=None):
    """
    Request a reply in the given JSON mode, falling back if unsupported.

    Args:
        messages (list[dict]): The messages to send.
        config (dict): Backend settings from chat_client.get_chat_config.
        logger (logging.Logger): Logger passed to send_chat_completion.
        mode (str or None): Preferred JSON mode; see response_format_for.
        extra_options (dict or None): Additional request fields such as
            "max_tokens".

    Returns:
        tuple[str, str or None]: (raw reply text, JSON mode actually
            used). If the backend rejects "json_schema" (HTTP 400 or
            similar), the request is retried once with "json_object".

    Raises:
        ChatError: If the backend fails for any other reason.
    """
    options = dict(BASE_OPTIONS, **(extra_options or {}))
    response_format = response_format_for(mode)
    if response_format:
        options["response_format"] = response_format
    try:
        return send_chat_completion(messages, config, logger, options=options)["reply"], mode
    except ChatError as error:
        if mode != "json_schema" or error.kind != "backend_error":
            raise
        logger.info("json_schema mode rejected (%s); retrying with json_object", error)
        options["response_format"] = response_format_for("json_object")
        return send_chat_completion(messages, config, logger, options=options)["reply"], "json_object"


def parse_json_text(raw):
    """
    Parse text as a JSON object without raising.

    Args:
        raw (str): The text to parse.

    Returns:
        tuple[dict or None, str or None]: (parsed object, None) on
            success, or (None, a one-line error description) if the text
            is not valid JSON or is JSON but not an object.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        return None, "invalid JSON: {} (line {}, column {})".format(error.msg, error.lineno, error.colno)
    except TypeError:
        return None, "invalid JSON: reply was not text"
    if not isinstance(data, dict):
        return None, "valid JSON but a {}, not an object".format(type(data).__name__)
    return data, None


def local_repair(raw):
    """
    Try cheap text fixes that often make a near-JSON reply parseable.

    Args:
        raw (str): The reply that failed to parse.

    Returns:
        tuple[str or None, str or None]: (candidate text, description of
            the fix) if a fix changed the text, otherwise (None, None).
            Fixes tried: removing a Markdown code fence, then taking the
            text from the first "{" to the last "}".
    """
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL)
    if fenced and fenced.group(1) != raw:
        return fenced.group(1), "stripped a Markdown code fence"
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end > start and raw[start:end + 1] != raw:
        return raw[start:end + 1], "extracted the outermost {...} block"
    return None, None


def validate_answer(data, allowed_sources):
    """
    Check a parsed reply against the required structure.

    Args:
        data (dict): The parsed JSON object.
        allowed_sources (list[str]): Chunk ids the answer may cite.

    Returns:
        list[str]: Problems found; empty when the reply is usable.
            Checks: every required field present with the right type,
            a non-empty answer, a source that is one of the allowed ids
            or "none", and "found" consistent with "source".
    """
    problems = []
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in data:
            problems.append("missing required field \"{}\"".format(field))
        elif not isinstance(data[field], expected_type):
            problems.append("field \"{}\" should be {}, got {}".format(
                field, expected_type.__name__, type(data[field]).__name__
            ))
    if problems:
        return problems

    if not data["answer"].strip():
        problems.append("field \"answer\" is empty")
    if data["source"] not in allowed_sources + [NO_SOURCE]:
        problems.append("field \"source\" is \"{}\", which was not supplied; it must be one of {}".format(
            data["source"], ", ".join("\"{}\"".format(source) for source in allowed_sources + [NO_SOURCE])
        ))
    elif data["found"] and data["source"] == NO_SOURCE:
        problems.append("\"found\" is true but \"source\" is \"none\"")
    elif not data["found"] and data["source"] != NO_SOURCE:
        problems.append("\"found\" is false but \"source\" names a chunk")
    return problems


def check_candidate(raw, allowed_sources):
    """
    Parse and validate one candidate reply, trying a local repair once.

    Args:
        raw (str): The candidate reply text.
        allowed_sources (list[str]): Chunk ids the answer may cite.

    Returns:
        tuple[dict or None, list[str], list[dict]]: (usable data or None,
            outstanding problems, steps taken). Each step has "step"
            (str), "detail" (str), and optionally "raw" (str).
    """
    steps = []
    data, error = parse_json_text(raw)
    if error:
        steps.append({"step": "parse", "detail": "FAILED - " + error})
        repaired, fix = local_repair(raw)
        if repaired is None:
            steps.append({"step": "local repair", "detail": "no applicable fix"})
            return None, [error], steps
        data, repair_error = parse_json_text(repaired)
        steps.append({"step": "local repair", "detail": fix + (" -> still " + repair_error if repair_error else " -> parsed"),
                      "raw": repaired})
        if repair_error:
            return None, [repair_error], steps
    else:
        steps.append({"step": "parse", "detail": "ok"})

    problems = validate_answer(data, allowed_sources)
    steps.append({"step": "validate", "detail": "ok" if not problems else "FAILED - " + "; ".join(problems)})
    return (data if not problems else None), problems, steps


def build_repair_messages(original_messages, bad_raw, problems):
    """
    Build a follow-up request asking the model to correct its reply.

    Args:
        original_messages (list[dict]): The messages of the first request.
        bad_raw (str): The reply that could not be used.
        problems (list[str]): What was wrong with it.

    Returns:
        list[dict]: The original messages, the bad reply as an assistant
            turn, and a user turn listing the problems and asking for a
            corrected JSON object only.
    """
    return original_messages + [
        {"role": "assistant", "content": bad_raw},
        {"role": "user", "content": (
            "Your reply could not be used: " + "; ".join(problems) + ". "
            "Fix only those problems. Keep any answer text that the context supports, and take "
            "\"source\" from the chunk that answer came from. "
            "Reply again with only the corrected JSON object in the required shape."
        )},
    ]


def get_structured_answer(question, chunks, config, logger, mode="json_schema", first_raw=None,
                          first_options=None, max_model_repairs=1):
    """
    Get a validated structured answer, recovering or rejecting as needed.

    Args:
        question (str): The question to answer.
        chunks (list[dict]): Context chunks with "chunk_id" and "text".
        config (dict): Backend settings.
        logger (logging.Logger): Logger passed to send_chat_completion.
        mode (str or None): JSON mode for model calls; see
            response_format_for.
        first_raw (str or None): If given, used as the first reply
            instead of calling the model (to inject a malformed reply).
        first_options (dict or None): Extra request fields for the first
            model call only, e.g. a tiny "max_tokens".
        max_model_repairs (int): How many times the model may be asked
            to correct an unusable reply.

    Returns:
        dict: "status" ("ok", "recovered", or "rejected"), "data" (dict
            or None; only set when the reply passed validation),
            "problems" (list[str], empty unless rejected), "mode" (str or
            None, the JSON mode used), and "steps" (list[dict]).
    """
    allowed_sources = [chunk["chunk_id"] for chunk in chunks]
    messages = build_messages(question, chunks)
    steps = []

    try:
        if first_raw is not None:
            raw, used_mode = first_raw, mode
            steps.append({"step": "first reply", "detail": "INJECTED (no model call)", "raw": raw})
        else:
            raw, used_mode = call_model(messages, config, logger, mode, first_options)
            steps.append({"step": "first reply", "detail": "model call, JSON mode: {}{}".format(
                used_mode or "off", ", options {}".format(first_options) if first_options else ""
            ), "raw": raw})

        data, problems, check_steps = check_candidate(raw, allowed_sources)
        steps.extend(check_steps)
        repaired = any(step["step"] == "local repair" for step in check_steps) and data is not None

        repairs_left = max_model_repairs
        while data is None and repairs_left > 0:
            repairs_left -= 1
            raw, used_mode = call_model(build_repair_messages(messages, raw, problems), config, logger, used_mode or "json_object")
            steps.append({"step": "model repair", "detail": "asked the model to fix: " + "; ".join(problems), "raw": raw})
            data, problems, check_steps = check_candidate(raw, allowed_sources)
            steps.extend(check_steps)
            repaired = data is not None
    except ChatError as error:
        steps.append({"step": "backend", "detail": "FAILED - " + str(error)})
        return {"status": "rejected", "data": None, "problems": [str(error)], "mode": mode, "steps": steps}

    if data is None:
        if max_model_repairs == 0:
            steps.append({"step": "model repair", "detail": "not allowed for this case"})
        return {"status": "rejected", "data": None, "problems": problems, "mode": used_mode, "steps": steps}
    return {"status": "recovered" if repaired else "ok", "data": data, "problems": [], "mode": used_mode, "steps": steps}


def load_context_chunks(script_dir):
    """
    Load the context chunks used by every demonstration case.

    Args:
        script_dir (str): Directory holding the sample corpus.

    Returns:
        list[dict]: The chunks named in CONTEXT_CHUNK_IDS, in that order.

    Raises:
        KeyError: If a named chunk is not produced by the pipeline.
    """
    from index_corpus import build_corpus_chunks

    by_id = {chunk["chunk_id"]: chunk for chunk in build_corpus_chunks(os.path.join(script_dir, "sample_corpus"))}
    return [by_id[chunk_id] for chunk_id in CONTEXT_CHUNK_IDS]


def print_case(number, case, result):
    """
    Print one demonstration case: its steps and final result.

    Args:
        number (int): Case number.
        case (dict): The case definition, with "label" and "question".
        result (dict): As returned by get_structured_answer.

    Returns:
        None
    """
    print()
    print("=" * WRAP_WIDTH)
    print("Case {}: {}".format(number, case["label"]))
    print("=" * WRAP_WIDTH)
    print("  question: {}".format(case["question"]))
    for step in result["steps"]:
        print("  - {}: {}".format(step["step"], step["detail"]))
        if step.get("raw") is not None:
            for line in textwrap.wrap(repr(step["raw"]), WRAP_WIDTH - 8):
                print("        {}".format(line))
    print("  RESULT: {}".format(result["status"].upper()))
    if result["data"] is not None:
        print("  parsed dict: {}".format(result["data"]))
    else:
        print("  not used; reasons: {}".format("; ".join(result["problems"])))


DEMO_CASES = [
    {"label": "normal question, JSON-schema mode",
     "question": "What file formats does the loading stage read?"},
    {"label": "question the context cannot answer, JSON-schema mode",
     "question": "Which company funds this project?"},
    {"label": "REAL malformed reply: JSON mode off, model wraps JSON in a code fence",
     "question": "What does the cleaning stage remove?", "mode": None},
    {"label": "REAL malformed reply: max_tokens=12 truncates the JSON mid-object",
     "question": "What file formats does the loading stage read?", "first_options": {"max_tokens": 12}},
    {"label": "INJECTED reply missing required fields",
     "question": "What file formats does the loading stage read?",
     "first_raw": "{\"answer\": \"It reads PDF, plain text, Markdown, and HTML files.\"}"},
    {"label": "INJECTED reply citing a chunk that was never supplied",
     "question": "What file formats does the loading stage read?",
     "first_raw": "{\"answer\": \"PDF and HTML.\", \"source\": \"secret_notes.txt#4\", \"found\": true}"},
    {"label": "INJECTED prose instead of JSON, repairs disabled -> clean rejection",
     "question": "What file formats does the loading stage read?",
     "first_raw": "Sure! The loader reads PDFs and HTML. Let me know if you need anything else.",
     "max_model_repairs": 0},
]


def main():
    """
    Run every demonstration case and print the results.

    Args:
        None

    Returns:
        int: Process exit status: 0 when every case ended in a handled
            outcome (ok, recovered, or rejected), 1 if the backend
            configuration could not be loaded.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logger = setup_logger(os.path.join(script_dir, LOG_FILE_NAME))
    logger.handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]

    try:
        config = get_chat_config(os.path.join(script_dir, ENV_FILE_NAME))
    except ChatError as error:
        print("Error: {}".format(error))
        return 1

    chunks = load_context_chunks(script_dir)
    print()
    print("Model: {} at {}".format(config["model_name"], config["base_url"]))
    print("Required structure: {{\"answer\": str, \"source\": one of {} or \"none\", \"found\": bool}}".format(
        [chunk["chunk_id"] for chunk in chunks]
    ))

    outcomes = []
    for number, case in enumerate(DEMO_CASES, start=1):
        result = get_structured_answer(
            case["question"], chunks, config, logger,
            mode=case.get("mode", "json_schema"),
            first_raw=case.get("first_raw"),
            first_options=case.get("first_options"),
            max_model_repairs=case.get("max_model_repairs", 1),
        )
        print_case(number, case, result)
        outcomes.append((number, case["label"], result))

    print()
    print("=" * WRAP_WIDTH)
    print("Summary")
    print("=" * WRAP_WIDTH)
    for number, label, result in outcomes:
        print("  {}. {:<10} {}".format(number, result["status"].upper(), label))
    return 0


if __name__ == "__main__":
    sys.exit(main())
