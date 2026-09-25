"""
Connects to a free, OpenAI-compatible chat completion backend and makes
a first working call.

Inputs:
    Backend settings read from environment variables, falling back to
    the ".env" file next to this script: CHAT_BASE_URL, CHAT_API_KEY, and
    CHAT_MODEL. None of the three is hard-coded here. The default
    configuration points at a local Ollama server
    (http://localhost:11434/v1); Groq's free tier works the same way by
    setting CHAT_BASE_URL=https://api.groq.com/openai/v1, CHAT_API_KEY to
    a free Groq key, and CHAT_MODEL to a Groq model name.
    Optional flag: --check-errors, which first exercises the failure
    handling before making the normal call.

Outputs:
    Printed to stdout: the model's reply and, at the end of the run, the
    full exchange (system message, user message, reply, token usage).
    Logged to stderr and to chat_exchange.log next to this script: the
    outgoing messages and the incoming response, including token usage
    when the backend reports it. Failures such as missing or invalid
    credentials, rate limiting, an unreachable backend, or an unknown
    model are reported as a one-line human-readable message instead of a
    stack trace, and the script exits with status 1.

No paid API key is used or required.
"""

import argparse
import json
import logging
import os
import sys

import requests

from embed_store import load_dotenv_file

ENV_FILE_NAME = ".env"
LOG_FILE_NAME = "chat_exchange.log"
REQUIRED_CHAT_VARS = ("CHAT_BASE_URL", "CHAT_API_KEY", "CHAT_MODEL")
REQUEST_TIMEOUT_SECONDS = 120

SYSTEM_MESSAGE = (
    "You are a concise assistant for a document retrieval project. "
    "Answer in two sentences or fewer."
)
USER_MESSAGE = "In plain terms, why does a retrieval pipeline split documents into chunks before embedding them?"


class ChatError(Exception):
    """
    A chat request failure with a short, human-readable explanation.

    The "kind" attribute names the failure category: "missing_config",
    "invalid_credentials", "rate_limited", "unreachable",
    "model_not_found", "backend_error", or "bad_response".
    """

    def __init__(self, kind, message):
        """
        Create the error.

        Args:
            kind (str): The failure category.
            message (str): A short explanation suitable for printing.

        Returns:
            None
        """
        super().__init__(message)
        self.kind = kind


def get_chat_config(env_path):
    """
    Resolve the chat backend's base URL, API key, and model name.

    Args:
        env_path (str): Path to a .env file to fall back on for any
            variable not set in the process environment.

    Returns:
        dict[str, str]: "base_url", "api_key", and "model_name".

    Raises:
        ChatError: With kind "missing_config" if any of CHAT_BASE_URL,
            CHAT_API_KEY, or CHAT_MODEL is not set anywhere.
    """
    dotenv_values = load_dotenv_file(env_path)
    resolved = {name: os.environ.get(name) or dotenv_values.get(name) for name in REQUIRED_CHAT_VARS}
    missing = [name for name, value in resolved.items() if not value]
    if missing:
        raise ChatError(
            "missing_config",
            "Missing credentials/configuration: {} {} not set (add to {} or the environment).".format(
                ", ".join(missing), "is" if len(missing) == 1 else "are", env_path
            ),
        )
    return {
        "base_url": resolved["CHAT_BASE_URL"],
        "api_key": resolved["CHAT_API_KEY"],
        "model_name": resolved["CHAT_MODEL"],
    }


def setup_logger(log_path):
    """
    Create a logger that writes exchanges to stderr and a log file.

    Args:
        log_path (str): File the log is appended to.

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger("chat_client")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("[log] %(message)s"))
    logger.addHandler(console_handler)

    return logger


def mask_key(api_key):
    """
    Hide most of an API key so it can be logged safely.

    Args:
        api_key (str): The key to mask.

    Returns:
        str: The key's last four characters prefixed with asterisks.
    """
    return "****" + api_key[-4:] if len(api_key) > 4 else "****"


def extract_error_detail(response):
    """
    Pull the backend's own error message out of a failed response.

    Args:
        response (requests.Response): The failed HTTP response.

    Returns:
        str: The backend's error message if the body is OpenAI-style
            JSON, otherwise the first 200 characters of the raw body.
    """
    try:
        return response.json()["error"]["message"]
    except (ValueError, KeyError, TypeError):
        return response.text[:200]


def raise_for_failure(response, config):
    """
    Convert a non-200 response into a human-readable ChatError.

    Args:
        response (requests.Response): The HTTP response to inspect.
        config (dict): Backend settings, used to name the model and URL
            in the message.

    Returns:
        None: Returns only when the response status is 200.

    Raises:
        ChatError: For any non-200 status, with a kind of
            "invalid_credentials" (401/403), "rate_limited" (429),
            "model_not_found" (404), or "backend_error" (anything else).
    """
    status = response.status_code
    if status == 200:
        return

    detail = extract_error_detail(response)
    if status in (401, 403):
        raise ChatError(
            "invalid_credentials",
            "Invalid or missing API key: the backend at {} rejected CHAT_API_KEY (HTTP {}). "
            "Check the key in .env.".format(config["base_url"], status),
        )
    if status == 429:
        retry_after = response.headers.get("Retry-After")
        wait_hint = " Retry after {} seconds.".format(retry_after) if retry_after else " Wait a moment and try again."
        raise ChatError("rate_limited", "Rate limited by the backend (HTTP 429).{}".format(wait_hint))
    if status == 404:
        raise ChatError(
            "model_not_found",
            "Model '{}' was not found on the backend ({}). Check CHAT_MODEL.".format(config["model_name"], detail),
        )
    raise ChatError("backend_error", "Backend returned HTTP {}: {}".format(status, detail))


def send_chat_completion(messages, config, logger, post_fn=requests.post, options=None):
    """
    Send one chat completion request and return the model's reply.

    Args:
        messages (list[dict]): Chat messages, each with "role" and
            "content" keys.
        config (dict): Backend settings with "base_url", "api_key", and
            "model_name".
        logger (logging.Logger): Logger that records the outgoing
            request and the incoming response.
        post_fn (callable): Function used to send the HTTP POST, with
            the same signature as requests.post; replaceable for
            testing.
        options (dict or None): Extra request fields merged into the
            payload, such as "temperature" or "seed".

    Returns:
        dict: "reply" (str), "model" (str, as reported by the backend),
            "usage" (dict or None, token usage if reported), and
            "finish_reason" (str or None).

    Raises:
        ChatError: If the backend is unreachable, rejects the request,
            or returns a body without a reply.
    """
    url = "{}/chat/completions".format(config["base_url"].rstrip("/"))
    payload = dict(options or {}, model=config["model_name"], messages=messages)

    logger.info("OUTGOING POST %s (model=%s, key=%s, options=%s)", url, config["model_name"],
                mask_key(config["api_key"]), options or {})
    for message in messages:
        logger.info("  %s: %s", message["role"], message["content"])

    try:
        response = post_fn(
            url,
            headers={"Authorization": "Bearer {}".format(config["api_key"]), "Content-Type": "application/json"},
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.Timeout:
        raise ChatError("unreachable", "The backend at {} did not respond within {} seconds.".format(
            config["base_url"], REQUEST_TIMEOUT_SECONDS
        ))
    except requests.ConnectionError:
        raise ChatError("unreachable", "Could not connect to the backend at {}. Is the server running?".format(
            config["base_url"]
        ))

    logger.info("INCOMING HTTP %s", response.status_code)
    raise_for_failure(response, config)

    try:
        body = response.json()
        choice = body["choices"][0]
        reply = choice["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise ChatError("bad_response", "The backend returned a response without a chat reply.")

    usage = body.get("usage")
    logger.info("  assistant: %s", reply)
    logger.info("  usage: %s", json.dumps(usage) if usage else "not reported by backend")
    logger.debug("  raw response: %s", json.dumps(body))

    return {
        "reply": reply,
        "model": body.get("model", config["model_name"]),
        "usage": usage,
        "finish_reason": choice.get("finish_reason"),
    }


def build_messages(system_message, user_message):
    """
    Build the message list for one chat request.

    Args:
        system_message (str): Instructions for the model.
        user_message (str): The user's question.

    Returns:
        list[dict]: A system message followed by a user message.
    """
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]


class SimulatedResponse:
    """
    A minimal stand-in for requests.Response, used to exercise failure
    handling that a local Ollama server never produces on its own (it
    does not check API keys and does not rate-limit).
    """

    def __init__(self, status_code, body, headers=None):
        """
        Create the stand-in response.

        Args:
            status_code (int): HTTP status to report.
            body (dict): JSON body to return from json().
            headers (dict or None): Response headers.

        Returns:
            None
        """
        self.status_code = status_code
        self.body = body
        self.text = json.dumps(body)
        self.headers = headers or {}

    def json(self):
        """
        Return the response body.

        Args:
            None

        Returns:
            dict: The JSON body given at construction.
        """
        return self.body


def make_simulated_post(status_code, message, headers=None):
    """
    Build a post function that always returns one simulated failure.

    Args:
        status_code (int): HTTP status the simulated response reports.
        message (str): Error message placed in an OpenAI-style body.
        headers (dict or None): Response headers, e.g. Retry-After.

    Returns:
        callable: A function accepting the same arguments as
            requests.post and returning a SimulatedResponse.
    """
    def simulated_post(*args, **kwargs):
        """
        Ignore the request and return the simulated failure.

        Args:
            *args: Positional arguments of requests.post (ignored).
            **kwargs: Keyword arguments of requests.post (ignored).

        Returns:
            SimulatedResponse: The configured failure response.
        """
        return SimulatedResponse(status_code, {"error": {"message": message}}, headers)

    return simulated_post


def run_error_checks(config, env_path, logger):
    """
    Trigger each handled failure and print how it is reported.

    Args:
        config (dict): Working backend settings.
        env_path (str): Path of the real .env file, used to derive a
            path that does not exist for the missing-config case.
        logger (logging.Logger): Logger passed through to requests.

    Returns:
        bool: True if every case produced the expected ChatError kind.
    """
    messages = build_messages("Reply with one word.", "Hello?")
    missing_env = env_path + ".does-not-exist"
    saved = {name: os.environ.pop(name, None) for name in REQUIRED_CHAT_VARS}

    cases = [
        ("missing credentials/config (real)", "missing_config",
         lambda: get_chat_config(missing_env)),
        ("backend unreachable (real, closed port)", "unreachable",
         lambda: send_chat_completion(messages, dict(config, base_url="http://localhost:9/v1"), logger)),
        ("unknown model (real)", "model_not_found",
         lambda: send_chat_completion(messages, dict(config, model_name="no-such-model"), logger)),
        ("invalid API key (simulated HTTP 401)", "invalid_credentials",
         lambda: send_chat_completion(messages, config, logger,
                                      make_simulated_post(401, "Invalid API Key"))),
        ("rate limited (simulated HTTP 429)", "rate_limited",
         lambda: send_chat_completion(messages, config, logger,
                                      make_simulated_post(429, "Rate limit reached", {"Retry-After": "7"}))),
    ]

    all_ok = True
    print("Failure handling checks")
    try:
        for label, expected_kind, action in cases:
            try:
                action()
                outcome, ok = "no error raised", False
            except ChatError as error:
                outcome, ok = "{} -> {}".format(error.kind, error), error.kind == expected_kind
            all_ok = all_ok and ok
            print("  [{}] {}".format("OK" if ok else "UNEXPECTED", label))
            print("       {}".format(outcome))
    finally:
        for name, value in saved.items():
            if value is not None:
                os.environ[name] = value
    print()
    return all_ok


def print_exchange(messages, result, config):
    """
    Print a full chat exchange.

    Args:
        messages (list[dict]): The messages that were sent.
        result (dict): The result returned by send_chat_completion.
        config (dict): Backend settings, used to show where the request
            went.

    Returns:
        None
    """
    print("Sample exchange")
    print("  backend: {}".format(config["base_url"]))
    print("  model:   {}".format(result["model"]))
    for message in messages:
        print("  [{}] {}".format(message["role"], message["content"]))
    print("  [assistant] {}".format(result["reply"]))
    usage = result["usage"]
    if usage:
        print("  token usage: {} prompt + {} completion = {} total".format(
            usage.get("prompt_tokens"), usage.get("completion_tokens"), usage.get("total_tokens")
        ))
    else:
        print("  token usage: not reported by backend")
    print("  finish reason: {}".format(result["finish_reason"]))


def main(argv):
    """
    Run the optional failure checks, then one real chat exchange.

    Args:
        argv (list[str]): Command-line arguments excluding the program
            name.

    Returns:
        int: Process exit status: 0 on success, 1 on a reported failure.
    """
    parser = argparse.ArgumentParser(description="Make a chat completion call to a free backend.")
    parser.add_argument("--check-errors", action="store_true", help="exercise failure handling before the real call")
    arguments = parser.parse_args(argv)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ENV_FILE_NAME)
    logger = setup_logger(os.path.join(script_dir, LOG_FILE_NAME))

    try:
        config = get_chat_config(env_path)
        if arguments.check_errors and not run_error_checks(config, env_path, logger):
            print("Error: failure handling did not behave as expected.")
            return 1

        messages = build_messages(SYSTEM_MESSAGE, USER_MESSAGE)
        result = send_chat_completion(messages, config, logger)
    except ChatError as error:
        print("Error: {}".format(error))
        return 1

    print("Reply: {}".format(result["reply"]))
    print()
    print_exchange(messages, result, config)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
