"""
Maintains multi-turn chat history and keeps every request inside a token
budget by replacing older turns with a compact memory (pinned user facts
plus a short summary), always preserving the original system message.

Inputs:
    Backend settings from environment variables or the ".env" file next
    to this script: CHAT_BASE_URL, CHAT_API_KEY, CHAT_MODEL (read by
    chat_client.py), plus CHAT_TOKEN_BUDGET (total tokens one request may
    use, prompt plus reply) and CHAT_REPLY_RESERVE_TOKENS (the part of
    that budget held back for the reply). The demonstration uses a fixed
    list of user messages defined in this file.

Outputs:
    Printed to stdout for every turn: the untrimmed history's token
    count (tracked but never sent) against the budget, the managed
    history's token count before and after trimming, what was done to
    fit (nothing, summarized, or dropped), the prompt size the backend
    itself reported, and the reply. At the end: a per-turn table, a
    check against the backend's own token counts, a check that the
    original system message was never altered, a check that the last
    answer still recalls facts from the first turn, and the final
    memory (pinned facts and summary parts). Requests and responses are logged by chat_client.py
    to chat_exchange.log.

Token counts use tiktoken's cl100k_base encoding plus the usual
per-message overhead. The backend model uses its own tokenizer, so its
reported prompt size differs somewhat; both are printed. No paid API key
is used or required.
"""

import logging
import os
import sys

import tiktoken

from chat_client import ChatError, get_chat_config, send_chat_completion, setup_logger
from embed_store import load_dotenv_file

ENV_FILE_NAME = ".env"
LOG_FILE_NAME = "chat_exchange.log"
ENCODING_NAME = "cl100k_base"

# Rough per-message cost of the chat format (role markers and separators)
# plus the tokens that prime the reply, following OpenAI's published
# guidance for cl100k-based chat models.
TOKENS_PER_MESSAGE = 4
TOKENS_REPLY_PRIMING = 3

# Messages kept word-for-word at the end of the history when trimming:
# the latest user/assistant exchange. The new user message is always kept
# on top of these.
KEEP_RECENT_MESSAGES = 2

# The backend model's tokenizer counted about 5% more tokens than
# tiktoken's cl100k_base on this conversation, so the prompt limit is
# shrunk by 10% to keep the real request inside the budget.
TOKENIZER_SAFETY_FACTOR = 1.10
SUMMARY_MAX_TOKENS = 120
FACTS_MAX_TOKENS = 120

# Trimmed turns become two kinds of memory. Facts the user stated (names,
# numbers, settings) are extracted once and pinned word for word. The
# rest becomes append-only summary parts that are never re-summarized:
# with this 1.5B model, re-summarizing a summary was observed dropping
# the project name and settings. When the parts exceed this cap, the
# oldest are dropped rather than compressed.
SUMMARY_TOKEN_CAP = 110

# Facts stated in the first user message that the last question asks
# about; the demo checks the final reply still contains all of them.
RECALL_FACTS = ["Lambda Search", "300", "60"]
FACTS_PREFIX = "Facts the user stated earlier in this conversation:"
SUMMARY_PREFIX = "Summary of the earlier conversation: "
REQUEST_OPTIONS = {"temperature": 0, "seed": 7}

SYSTEM_MESSAGE = (
    "You are a technical advisor helping a developer build a document "
    "retrieval (RAG) pipeline in Python. Answer in at most 3 short "
    "sentences. Use facts the user told you earlier in the conversation "
    "when they are relevant."
)

DEMO_USER_MESSAGES = [
    "My project is called Lambda Search. It indexes internal runbooks, and "
    "I chunk them at 300 tokens with 60 tokens of overlap. Is that overlap "
    "reasonable?",
    "I embed chunks with nomic-embed-text through Ollama. What vector "
    "length should I expect?",
    "I store vectors in chromadb with cosine distance. Is cosine a good "
    "choice for these embeddings?",
    "Some runbooks have repeated page footers. How should I remove them "
    "before chunking?",
    "Retrieval sometimes returns a chunk that starts with 'Its weakness "
    "is...'. Why might that happen?",
    "How many chunks should I retrieve per question for a small model?",
    "Should I re-embed everything when a single runbook changes?",
    "Remind me: what is my project called, and what chunk size and overlap "
    "did I say I use?",
]


def get_budget_settings(env_path):
    """
    Read the token budget and reply reserve from the environment.

    Args:
        env_path (str): Path to a .env file used for any variable not
            set in the process environment.

    Returns:
        dict: "budget" (int, total tokens per request), "reply_reserve"
            (int, tokens held back for the reply), and "history_limit"
            (int, the most the prompt may use as counted by tiktoken:
            budget minus reply_reserve, divided by
            TOKENIZER_SAFETY_FACTOR).

    Raises:
        ValueError: If either value is missing, not a positive integer,
            or the reserve leaves no room for the prompt.
    """
    dotenv_values = load_dotenv_file(env_path)
    values = {}
    for name in ("CHAT_TOKEN_BUDGET", "CHAT_REPLY_RESERVE_TOKENS"):
        raw = os.environ.get(name) or dotenv_values.get(name)
        if not raw or not raw.isdigit() or int(raw) <= 0:
            raise ValueError("{} must be set to a positive integer (in {} or the environment)".format(name, env_path))
        values[name] = int(raw)

    budget = values["CHAT_TOKEN_BUDGET"]
    reserve = values["CHAT_REPLY_RESERVE_TOKENS"]
    if reserve >= budget:
        raise ValueError("CHAT_REPLY_RESERVE_TOKENS must be smaller than CHAT_TOKEN_BUDGET")
    return {
        "budget": budget,
        "reply_reserve": reserve,
        "history_limit": int((budget - reserve) / TOKENIZER_SAFETY_FACTOR),
    }


def count_message_tokens(messages, encoding):
    """
    Count the tokens a list of chat messages occupies in a request.

    Args:
        messages (list[dict]): Chat messages with "role" and "content".
        encoding (tiktoken.Encoding): Tokenizer used for the count.

    Returns:
        int: Content tokens plus per-message overhead plus reply
            priming.
    """
    total = TOKENS_REPLY_PRIMING
    for message in messages:
        total += TOKENS_PER_MESSAGE + len(encoding.encode(message["content"]))
    return total


class ConversationHistory:
    """
    Running chat history: the original system message, a memory of
    trimmed turns (pinned user facts plus a droppable summary), and the
    turns still kept word for word.
    """

    def __init__(self, system_message, encoding, history_limit):
        """
        Start an empty conversation.

        Args:
            system_message (str): The system message, kept unchanged for
                the whole conversation.
            encoding (tiktoken.Encoding): Tokenizer used for counts.
            history_limit (int): Maximum prompt tokens per request.

        Returns:
            None
        """
        self.system_message = {"role": "system", "content": system_message}
        self.encoding = encoding
        self.history_limit = history_limit
        self.facts = []
        self.summary_parts = []
        self.turns = []

    @property
    def summary(self):
        """
        The combined summary of trimmed turns still kept.

        Args:
            None

        Returns:
            str or None: The summary parts joined in order, or None if
                there are none.
        """
        return " ".join(self.summary_parts) if self.summary_parts else None

    def memory_text(self):
        """
        Build the memory message content from facts and summary.

        Args:
            None

        Returns:
            str or None: The pinned facts section and the summary
                section, or None if both are empty.
        """
        sections = []
        if self.facts:
            sections.append(FACTS_PREFIX + "\n" + "\n".join("- " + fact for fact in self.facts))
        if self.summary:
            sections.append(SUMMARY_PREFIX + self.summary)
        return "\n\n".join(sections) if sections else None

    def add_facts(self, new_facts):
        """
        Pin new facts, skipping any already pinned.

        Args:
            new_facts (list[str]): Fact lines without the "- " prefix.

        Returns:
            int: Number of facts actually added.
        """
        known = {fact.lower() for fact in self.facts}
        added = 0
        for fact in new_facts:
            if fact.lower() not in known:
                self.facts.append(fact)
                known.add(fact.lower())
                added += 1
        return added

    def section_tokens(self, text):
        """
        Count the tokens of one piece of text.

        Args:
            text (str or None): The text to count.

        Returns:
            int: Its token count, or 0 for None.
        """
        return len(self.encoding.encode(text)) if text else 0

    def add(self, role, content):
        """
        Append one user or assistant message.

        Args:
            role (str): "user" or "assistant".
            content (str): The message text.

        Returns:
            None
        """
        self.turns.append({"role": role, "content": content})

    def messages(self):
        """
        Build the message list that would be sent right now.

        Args:
            None

        Returns:
            list[dict]: The original system message, then one memory
                message if any turns have been trimmed, then the kept
                turns.
        """
        result = [self.system_message]
        memory = self.memory_text()
        if memory:
            result.append({"role": "system", "content": memory})
        return result + self.turns

    def token_count(self):
        """
        Count the tokens of the current message list.

        Args:
            None

        Returns:
            int: Token count of messages().
        """
        return count_message_tokens(self.messages(), self.encoding)

    def fit_to_budget(self, summarize_fn, extract_facts_fn):
        """
        Trim the history, if needed, so the next request fits the limit.

        Older turns are removed from the verbatim history. Facts the
        user stated in them are extracted and pinned word for word, and
        the turns are summarized into a new summary part. Summary parts
        are never re-summarized; when they exceed SUMMARY_TOKEN_CAP the
        oldest parts are dropped instead. If the history is still too
        long, the oldest kept turns, then summary parts, then the oldest
        facts are dropped. The original system message and the newest
        user message are never removed.

        Args:
            summarize_fn (callable): Function taking a list of messages
                (list[dict]) and returning a short summary (str); may
                raise ChatError.
            extract_facts_fn (callable): Function taking a list of user
                messages (list[dict]) and returning fact lines
                (list[str]); may raise ChatError.

        Returns:
            dict: "before" (int), "after" (int), "action" (str describing
                what was done), and "within_limit" (bool).

        Raises:
            ValueError: If even the system message plus the newest user
                message exceed the limit.
        """
        before = self.token_count()
        if before <= self.history_limit:
            return {"before": before, "after": before, "action": "none needed", "within_limit": True}

        actions = []
        keep = KEEP_RECENT_MESSAGES + 1
        older, recent = self.turns[:-keep], self.turns[-keep:]
        if older:
            self.turns = recent
            try:
                added = self.add_facts(extract_facts_fn([m for m in older if m["role"] == "user"]))
                actions.append("pinned {} new fact(s)".format(added))
            except ChatError as error:
                actions.append("fact extraction failed ({})".format(error))
            try:
                part = summarize_fn(older)
                self.summary_parts.append(part)
                actions.append("summarized {} older message(s) into a {}-token part".format(
                    len(older), self.section_tokens(part)
                ))
            except ChatError as error:
                actions.append("summary failed ({})".format(error))

        while self.section_tokens(self.summary) > SUMMARY_TOKEN_CAP and len(self.summary_parts) > 1:
            self.summary_parts.pop(0)
            actions.append("dropped the oldest summary part (summary over {} tokens)".format(SUMMARY_TOKEN_CAP))

        dropped = 0
        while self.token_count() > self.history_limit and len(self.turns) > 1:
            self.turns.pop(0)
            dropped += 1
        if dropped:
            actions.append("dropped {} oldest message(s)".format(dropped))
        while self.token_count() > self.history_limit and self.summary_parts:
            self.summary_parts.pop(0)
            actions.append("dropped the oldest summary part")
        while self.token_count() > self.history_limit and self.facts:
            self.facts.pop(0)
            actions.append("dropped the oldest fact")

        after = self.token_count()
        if after > self.history_limit:
            raise ValueError("the system message and newest user message alone exceed the token limit")
        return {"before": before, "after": after, "action": "; ".join(actions), "within_limit": True}


def make_summarizer(config, logger):
    """
    Build a summarize_fn that asks the chat backend for a summary.

    Args:
        config (dict): Backend settings from chat_client.get_chat_config.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        callable: A function (messages) -> str that returns a short
            summary of the given messages, capped at SUMMARY_MAX_TOKENS
            reply tokens.
    """
    def summarize(messages):
        """
        Summarize conversation messages into a few sentences.

        Args:
            messages (list[dict]): Turns to summarize.

        Returns:
            str: The summary.
        """
        transcript = "\n".join("{}: {}".format(message["role"], message["content"]) for message in messages)
        request = [
            {"role": "system", "content": (
                "You compress chat transcripts. Write at most 3 short sentences "
                "covering what was asked and what was advised. Drop pleasantries."
            )},
            {"role": "user", "content": "Summarize this conversation:\n" + transcript},
        ]
        options = dict(REQUEST_OPTIONS, max_tokens=SUMMARY_MAX_TOKENS)
        return send_chat_completion(request, config, logger, options=options)["reply"].strip()

    return summarize


def parse_fact_lines(reply):
    """
    Turn a fact-extraction reply into a list of fact strings.

    Args:
        reply (str): The model's reply, expected as "- " lines or NONE.

    Returns:
        list[str]: Each "- " line with the prefix removed, skipping
            blank lines and any NONE marker (the model sometimes writes
            "- NONE").
    """
    facts = []
    for line in reply.splitlines():
        text = line.strip().lstrip("-*").strip()
        if text and text.upper().rstrip(".") != "NONE":
            facts.append(text)
    return facts


def make_fact_extractor(config, logger):
    """
    Build an extract_facts_fn that asks the backend for user-stated facts.

    Args:
        config (dict): Backend settings from chat_client.get_chat_config.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        callable: A function (user_messages) -> list[str] returning the
            concrete facts the user stated in those messages.
    """
    def extract_facts(user_messages):
        """
        Extract facts the user stated about their own project.

        Args:
            user_messages (list[dict]): User messages to read.

        Returns:
            list[str]: Fact lines, possibly empty.
        """
        if not user_messages:
            return []
        text = "\n".join("user: " + message["content"] for message in user_messages)
        request = [
            {"role": "system", "content": (
                "You extract facts. From the user's messages below, list every concrete "
                "fact the user states about their own project: its name, what it indexes, "
                "numbers, tools, and settings. One fact per line, each line starting with "
                "\"- \" and written as \"label: value\", for example \"- chunk size: 300 tokens\". "
                "Copy names and numbers exactly. Do not include questions, advice, or anything "
                "the user did not state. If there are no such facts, reply exactly: NONE"
            )},
            {"role": "user", "content": text},
        ]
        options = dict(REQUEST_OPTIONS, max_tokens=FACTS_MAX_TOKENS)
        return parse_fact_lines(send_chat_completion(request, config, logger, options=options)["reply"])

    return extract_facts


def run_demo(config, settings, logger):
    """
    Run the scripted conversation, keeping every request within budget.

    Args:
        config (dict): Backend settings from chat_client.get_chat_config.
        settings (dict): Budget settings from get_budget_settings.
        logger (logging.Logger): Logger passed to send_chat_completion.

    Returns:
        tuple[list[dict], ConversationHistory]: One record per turn
            ("turn", "naive_tokens", "before", "after", "action",
            "backend_prompt_tokens", "reply_tokens", "reply"), and the
            final history.
    """
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    history = ConversationHistory(SYSTEM_MESSAGE, encoding, settings["history_limit"])
    naive_messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
    summarize = make_summarizer(config, logger)
    extract_facts = make_fact_extractor(config, logger)
    reply_options = dict(REQUEST_OPTIONS, max_tokens=settings["reply_reserve"])
    records = []

    for turn, user_message in enumerate(DEMO_USER_MESSAGES, start=1):
        history.add("user", user_message)
        naive_messages.append({"role": "user", "content": user_message})
        naive_tokens = count_message_tokens(naive_messages, encoding)

        fit = history.fit_to_budget(summarize, extract_facts)
        assert history.messages()[0]["content"] == SYSTEM_MESSAGE
        assert fit["after"] <= settings["history_limit"]

        print()
        print("Turn {}".format(turn))
        print("  user: {}".format(user_message))
        print("  untrimmed history: {} tokens{}".format(
            naive_tokens, "  <-- OVER the {}-token limit; would not be sent".format(settings["history_limit"])
            if naive_tokens > settings["history_limit"] else ""
        ))
        print("  managed history:   {} tokens before -> {} tokens after (limit {})".format(
            fit["before"], fit["after"], settings["history_limit"]
        ))
        print("  action: {}".format(fit["action"]))

        result = send_chat_completion(history.messages(), config, logger, options=reply_options)
        reply = result["reply"].strip()
        history.add("assistant", reply)
        naive_messages.append({"role": "assistant", "content": reply})

        usage = result["usage"] or {}
        print("  request sent: {} tokens (tiktoken) + up to {} reply tokens = within the {} budget".format(
            fit["after"], settings["reply_reserve"], settings["budget"]
        ))
        print("  backend reported: {} prompt + {} reply tokens (model's own tokenizer)".format(
            usage.get("prompt_tokens", "?"), usage.get("completion_tokens", "?")
        ))
        print("  assistant: {}".format(reply))

        records.append({
            "turn": turn,
            "naive_tokens": naive_tokens,
            "before": fit["before"],
            "after": fit["after"],
            "action": fit["action"],
            "backend_prompt_tokens": usage.get("prompt_tokens"),
            "reply_tokens": usage.get("completion_tokens"),
            "reply": reply,
        })

    return records, history


def print_final_report(records, history, settings):
    """
    Print the per-turn token table and final checks.

    Args:
        records (list[dict]): Per-turn records from run_demo.
        history (ConversationHistory): The final history.
        settings (dict): Budget settings from get_budget_settings.

    Returns:
        None
    """
    limit = settings["history_limit"]
    print()
    print("Token counts per turn (prompt limit {} = (budget {} - reply reserve {}) / {} tokenizer margin)".format(
        limit, settings["budget"], settings["reply_reserve"], TOKENIZER_SAFETY_FACTOR
    ))
    print("  turn | untrimmed | before | after | backend prompt | trimmed?")
    for record in records:
        print("  {:>4} | {:>9} | {:>6} | {:>5} | {:>14} | {}".format(
            record["turn"],
            "{}{}".format(record["naive_tokens"], "*" if record["naive_tokens"] > limit else " "),
            record["before"], record["after"],
            record["backend_prompt_tokens"] if record["backend_prompt_tokens"] is not None else "?",
            "yes" if record["action"] != "none needed" else "no",
        ))
    print("  * untrimmed history over the limit")

    over = sum(1 for record in records if record["naive_tokens"] > limit)
    print()
    print("Untrimmed history exceeded the limit on {} of {} turns (peak {} tokens).".format(
        over, len(records), max(record["naive_tokens"] for record in records)
    ))
    print("Managed history stayed within the limit on {} of {} turns (peak {} tokens).".format(
        sum(1 for record in records if record["after"] <= limit), len(records),
        max(record["after"] for record in records)
    ))
    backend_totals = [
        record["backend_prompt_tokens"] + settings["reply_reserve"]
        for record in records if record["backend_prompt_tokens"] is not None
    ]
    print("Backend's own count, prompt + full reply reserve, within the {} budget on {} of {} turns (peak {}).".format(
        settings["budget"], sum(1 for total in backend_totals if total <= settings["budget"]),
        len(backend_totals), max(backend_totals) if backend_totals else "?"
    ))
    print("Original system message unchanged at position 0: {}".format(
        history.messages()[0] == {"role": "system", "content": SYSTEM_MESSAGE}
    ))
    final_reply = records[-1]["reply"]
    missing = [fact for fact in RECALL_FACTS if fact not in final_reply]
    print("Final answer recalls facts from turn 1 ({}): {}".format(
        ", ".join(RECALL_FACTS), "yes" if not missing else "NO, missing {}".format(missing)
    ))
    print()
    print("Final memory carried in the history ({} tokens):".format(history.section_tokens(history.memory_text())))
    print("  pinned facts:")
    for fact in history.facts or ["(none)"]:
        print("    - {}".format(fact))
    print("  summary parts:")
    for part in history.summary_parts or ["(none)"]:
        print("    - {}".format(part))


def main():
    """
    Run the long-conversation demonstration.

    Args:
        None

    Returns:
        int: Process exit status: 0 on success, 1 on a reported failure.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ENV_FILE_NAME)
    logger = setup_logger(os.path.join(script_dir, LOG_FILE_NAME))
    logger.handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]

    try:
        config = get_chat_config(env_path)
        settings = get_budget_settings(env_path)
        print("Model: {} at {}".format(config["model_name"], config["base_url"]))
        print("Budget: {} tokens per request; {} reserved for the reply; prompt limit {} tiktoken tokens "
              "(includes a {:.0%} margin for the model's own tokenizer)".format(
                  settings["budget"], settings["reply_reserve"], settings["history_limit"],
                  TOKENIZER_SAFETY_FACTOR - 1
              ))
        records, history = run_demo(config, settings, logger)
    except (ChatError, ValueError) as error:
        print("Error: {}".format(error))
        return 1

    print_final_report(records, history, settings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
