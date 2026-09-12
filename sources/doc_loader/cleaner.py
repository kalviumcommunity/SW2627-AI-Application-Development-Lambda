"""
Cleans raw text produced by the document loader so it is consistent and
retrieval-ready.

Inputs:
    Records as produced by loader.load_corpus(): a list of dicts, each
    with a "source" key (the originating file path) and a "text" key
    (the raw extracted string).

Outputs:
    A new list of records, one per input record, each with:
        "source":        unchanged from the input
        "original_text": the raw text before cleaning
        "cleaned_text":  the same text after cleaning
    The exact same cleaning function is applied to every record with no
    per-file special casing, so the whole corpus is normalized the same
    way.

No network calls or API keys are used anywhere in this module.
"""

import os
import re
import unicodedata
from collections import Counter

# Common sequences produced when UTF-8 bytes are mis-decoded as
# Windows-1252/Latin-1 (mojibake). Mapped back to the intended character.
MOJIBAKE_REPLACEMENTS = {
    "â€™": "’",  # â€™ -> '
    "â€œ": "“",  # â€œ -> "
    "â€": "”",  # â€ -> "
    "â€“": "–",  # â€" -> -
    "â€”": "—",  # â€" -> --
    "Ã©": "é",        # Ã© -> e-acute
}

# Lines that are boilerplate on sight regardless of how often they repeat.
BOILERPLATE_LINE_PATTERNS = [
    re.compile(r"^\s*page\s+\d+\s+of\s+\d+\s*$", re.IGNORECASE),
]

# A non-blank line at most this long that repeats at least this many times
# in one document is treated as a running header/footer and dropped.
REPEATED_LINE_MAX_CHARS = 80
REPEATED_LINE_MIN_COUNT = 3


def clean_text(text):
    """
    Normalize a single block of raw text for retrieval.

    Args:
        text (str): Raw text as extracted by the document loader.

    Returns:
        str: The cleaned text, with Unicode normalized to NFKC, line
            endings unified to "\\n", repeated headers/footers and
            page-number boilerplate removed, and runaway whitespace or
            blank lines collapsed. Ordinary punctuation, headings, and
            numbers are left intact.
    """
    de_mojibaked = text
    for garbled, fixed in MOJIBAKE_REPLACEMENTS.items():
        de_mojibaked = de_mojibaked.replace(garbled, fixed)

    normalized = unicodedata.normalize("NFKC", de_mojibaked)

    unified = normalized.replace("\r\n", "\n").replace("\r", "\n")

    lines = unified.split("\n")
    stripped_lines = [line.strip() for line in lines]

    line_counts = Counter(
        line for line in stripped_lines
        if line and len(line) <= REPEATED_LINE_MAX_CHARS
    )
    repeated_boilerplate = {
        line for line, count in line_counts.items()
        if count >= REPEATED_LINE_MIN_COUNT
    }

    kept_lines = []
    for line in stripped_lines:
        if any(pattern.match(line) for pattern in BOILERPLATE_LINE_PATTERNS):
            continue
        if line in repeated_boilerplate:
            continue
        kept_lines.append(line)

    rejoined = "\n".join(kept_lines)

    horizontal_collapsed = re.sub(r"[ \t]+", " ", rejoined)
    blank_lines_collapsed = re.sub(r"\n{3,}", "\n\n", horizontal_collapsed)

    return blank_lines_collapsed.strip()


def clean_corpus(records):
    """
    Apply clean_text, unchanged, to every record in a corpus.

    Args:
        records (list[dict]): Records as returned by loader.load_corpus,
            each with "source" (str) and "text" (str) keys.

    Returns:
        list[dict]: One record per input record, each with "source"
            (str, unchanged), "original_text" (str, the input text), and
            "cleaned_text" (str, the result of clean_text on that same
            input). The same function is called for every record with no
            per-document branching.
    """
    cleaned_records = []
    for record in records:
        original_text = record["text"]
        cleaned_records.append({
            "source": record["source"],
            "original_text": original_text,
            "cleaned_text": clean_text(original_text),
        })
    return cleaned_records


def print_before_after(cleaned_records):
    """
    Print a short before/after sample and the character-count change.

    Args:
        cleaned_records (list[dict]): Records as returned by
            clean_corpus, each with "source", "original_text", and
            "cleaned_text" keys.

    Returns:
        None
    """
    sample_length = 120
    for record in cleaned_records:
        source = record["source"]
        original_text = record["original_text"]
        cleaned_text = record["cleaned_text"]

        before_sample = " ".join(original_text.split())[:sample_length]
        after_sample = " ".join(cleaned_text.split())[:sample_length]
        change = len(cleaned_text) - len(original_text)

        print(source)
        print("  before ({} chars): {}".format(len(original_text), before_sample))
        print("  after  ({} chars): {}".format(len(cleaned_text), after_sample))
        print("  change: {:+d} chars".format(change))


if __name__ == "__main__":
    from loader import load_corpus

    corpus_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")
    loaded_records = load_corpus(corpus_folder)
    cleaned = clean_corpus(loaded_records)
    print()
    print("Cleaned {} document(s):".format(len(cleaned)))
    print_before_after(cleaned)
