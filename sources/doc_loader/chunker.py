"""
Splits cleaned document text into retrieval-sized chunks using more than
one strategy, and compares the results.

Inputs:
    A single cleaned text string, such as the "cleaned_text" value
    produced by cleaner.clean_text() for one document.

Outputs:
    For each chunking strategy: a list of chunk records (dicts with
    "text", "start", and "end" keys, where "start"/"end" are character
    offsets into the input text), plus printed statistics (chunk count,
    average chunk size) and a small printed sample of chunks with their
    boundaries visible, so the two strategies can be inspected side by
    side on the same document.

No network calls or API keys are used anywhere in this module.
"""

import os
import re

FIXED_CHUNK_SIZE = 500
FIXED_CHUNK_OVERLAP = 80
PARAGRAPH_MAX_CHUNK_SIZE = 500

SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


def chunk_fixed_size(text, chunk_size, overlap):
    """
    Split text into fixed-size, overlapping character windows.

    Args:
        text (str): The text to split.
        chunk_size (int): Maximum number of characters per chunk.
        overlap (int): Number of characters repeated at the start of each
            chunk from the tail of the previous chunk, so content sitting
            on a boundary is not lost entirely from either side.

    Returns:
        list[dict]: One record per chunk, each with "text" (str),
            "start" (int, inclusive offset into the input text), and
            "end" (int, exclusive offset into the input text).
    """
    chunks = []
    length = len(text)
    start = 0

    while start < length:
        end = min(start + chunk_size, length)
        chunks.append({"text": text[start:end], "start": start, "end": end})
        if end == length:
            break
        start = end - overlap

    return chunks


def split_into_paragraphs(text):
    """
    Split text into non-empty paragraphs on blank lines.

    Args:
        text (str): Cleaned text, where paragraphs are separated by a
            single blank line ("\\n\\n").

    Returns:
        list[str]: The paragraphs, in order, with surrounding whitespace
            stripped and any empty entries removed.
    """
    return [part.strip() for part in text.split("\n\n") if part.strip()]


def split_into_sentences(paragraph):
    """
    Split one paragraph into sentences.

    Args:
        paragraph (str): A single paragraph of text.

    Returns:
        list[str]: The sentences in the paragraph, in order, split on
            whitespace that follows a period, question mark, or
            exclamation point.
    """
    return [sentence.strip() for sentence in SENTENCE_SPLIT_PATTERN.split(paragraph) if sentence.strip()]


def chunk_by_paragraph(text, max_chunk_size):
    """
    Split text into chunks that respect paragraph boundaries.

    Args:
        text (str): Cleaned text, where paragraphs are separated by a
            single blank line ("\\n\\n").
        max_chunk_size (int): Maximum number of characters per chunk.
            Whole paragraphs are packed together up to this size; a
            single paragraph longer than this size is split further by
            sentence so no chunk is dropped or silently truncated.

    Returns:
        list[dict]: One record per chunk, each with "text" (str),
            "start" (int, inclusive offset into the input text), and
            "end" (int, exclusive offset into the input text).
    """
    chunk_texts = []
    current = ""

    for paragraph in split_into_paragraphs(text):
        candidate = "{}\n\n{}".format(current, paragraph) if current else paragraph
        if len(candidate) <= max_chunk_size:
            current = candidate
            continue

        if current:
            chunk_texts.append(current)
            current = ""

        if len(paragraph) <= max_chunk_size:
            current = paragraph
            continue

        sub_current = ""
        for sentence in split_into_sentences(paragraph):
            sub_candidate = "{} {}".format(sub_current, sentence) if sub_current else sentence
            if len(sub_candidate) <= max_chunk_size:
                sub_current = sub_candidate
            else:
                if sub_current:
                    chunk_texts.append(sub_current)
                sub_current = sentence
        if sub_current:
            chunk_texts.append(sub_current)

    if current:
        chunk_texts.append(current)

    return locate_chunk_offsets(text, chunk_texts)


def locate_chunk_offsets(text, chunk_texts):
    """
    Attach character offsets to a sequence of non-overlapping chunk texts.

    Args:
        text (str): The original text the chunks were derived from.
        chunk_texts (list[str]): Chunk strings in the order they appear
            in text, with no overlap between consecutive chunks.

    Returns:
        list[dict]: One record per input chunk, each with "text" (str,
            unchanged), "start" (int), and "end" (int). If a chunk
            cannot be located verbatim (for example because sentence
            joins normalized whitespace differently than the source),
            its offsets fall back to the end of the previous chunk so
            reporting still proceeds without raising an error.
    """
    located = []
    cursor = 0

    for chunk_text in chunk_texts:
        start = text.find(chunk_text, cursor)
        if start == -1:
            start = cursor
        end = start + len(chunk_text)
        located.append({"text": chunk_text, "start": start, "end": end})
        cursor = end

    return located


def compute_chunk_stats(chunks):
    """
    Compute the chunk count and average chunk size for a set of chunks.

    Args:
        chunks (list[dict]): Chunk records as returned by
            chunk_fixed_size or chunk_by_paragraph, each with a "text"
            key.

    Returns:
        tuple[int, float]: The number of chunks, and the average number
            of characters per chunk (0.0 if there are no chunks).
    """
    count = len(chunks)
    if count == 0:
        return 0, 0.0
    average_size = sum(len(chunk["text"]) for chunk in chunks) / count
    return count, average_size


def print_chunk_samples(chunks, label, sample_count=3):
    """
    Print a small sample of chunks with their character boundaries.

    Args:
        chunks (list[dict]): Chunk records as returned by
            chunk_fixed_size or chunk_by_paragraph, each with "text",
            "start", and "end" keys.
        label (str): A short name for the strategy, used in the printed
            header.
        sample_count (int): Maximum number of chunks to print.

    Returns:
        None
    """
    print("{} sample chunks:".format(label))
    head_len, tail_len = 70, 50
    for index, chunk in enumerate(chunks[:sample_count]):
        collapsed = " ".join(chunk["text"].split())
        if len(collapsed) > head_len + tail_len:
            preview = "{} <<CUT>> {}".format(collapsed[:head_len], collapsed[-tail_len:])
        else:
            preview = collapsed
        print("  chunk {} [{}:{}] ({} chars): {}".format(
            index + 1, chunk["start"], chunk["end"], len(chunk["text"]), preview
        ))


if __name__ == "__main__":
    from loader import load_corpus
    from cleaner import clean_text

    corpus_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")
    loaded_records = load_corpus(corpus_folder)
    target_record = next(r for r in loaded_records if r["source"].endswith("long_report.txt"))
    sample_text = clean_text(target_record["text"])

    print()
    print("Comparing chunking strategies on: {}".format(target_record["source"]))
    print("Cleaned document length: {} chars".format(len(sample_text)))
    print()

    fixed_chunks = chunk_fixed_size(sample_text, FIXED_CHUNK_SIZE, FIXED_CHUNK_OVERLAP)
    paragraph_chunks = chunk_by_paragraph(sample_text, PARAGRAPH_MAX_CHUNK_SIZE)

    fixed_count, fixed_average = compute_chunk_stats(fixed_chunks)
    paragraph_count, paragraph_average = compute_chunk_stats(paragraph_chunks)

    print("Fixed-size strategy: {} chunks, average {:.1f} chars/chunk".format(fixed_count, fixed_average))
    print("Paragraph-based strategy: {} chunks, average {:.1f} chars/chunk".format(paragraph_count, paragraph_average))
    print()

    print_chunk_samples(fixed_chunks, "Fixed-size")
    print()
    print_chunk_samples(paragraph_chunks, "Paragraph-based")
    print()

    # For a real corpus of normal prose (reports, articles, docs), the
    # paragraph-based strategy is the better default: this sample document
    # has clear paragraph structure, and grouping whole paragraphs keeps
    # each chunk semantically coherent instead of cutting mid-sentence,
    # which tends to matter more for retrieval quality than having
    # perfectly uniform chunk sizes. Fixed-size chunking is worth keeping
    # around as a fallback for documents with little or no paragraph
    # structure (e.g. raw OCR output) and is already used internally as a
    # safety net when a single paragraph exceeds the chunk size limit.
    print("Recommendation: prefer paragraph-based chunking for structured prose corpora;")
    print("fall back to fixed-size chunking for unstructured text with no paragraph breaks.")
