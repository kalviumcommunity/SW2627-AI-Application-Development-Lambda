"""
Attaches consistent metadata to every chunk produced from a corpus, so
each chunk can be traced back to its exact source document and position.

Inputs:
    A folder of documents, loaded with loader.load_corpus and cleaned
    with cleaner.clean_text, then split into chunks with
    chunker.chunk_by_paragraph.

Outputs:
    A flat list of chunk records, one per chunk across the whole corpus,
    every record sharing the exact same set of fields:
        "source":       str, the originating file path
        "chunk_id":      str, a unique id combining the source filename
                         and the chunk's position ("<filename>#<index>")
        "chunk_index":   int, 0-based position of the chunk within its
                         source document
        "total_chunks":  int, how many chunks that source document
                         produced in total
        "section":       str or None, the nearest heading/title line
                         that precedes the chunk in its source document
        "start_char":    int, inclusive character offset into the
                         document's cleaned text
        "end_char":      int, exclusive character offset into the
                         document's cleaned text
        "text":          str, the chunk's text
    A page-number field is deliberately not included: the loader
    flattens every PDF into one string per document without recording
    page boundaries, so a page number would not be genuine metadata for
    any chunk in this corpus.

No network calls or API keys are used anywhere in this module.
"""

import os
import re

from chunker import PARAGRAPH_MAX_CHUNK_SIZE, chunk_by_paragraph

HEADING_MAX_CHARS = 70
MARKDOWN_HEADING_PATTERN = re.compile(r"^#{1,6}\s+\S")
SENTENCE_END_CHARS = (".", "!", "?", ",")


def is_heading_line(line):
    """
    Decide whether a single line of text reads as a heading or title.

    Args:
        line (str): One line of text (no surrounding newline).

    Returns:
        bool: True if the line looks like a Markdown heading or a short
            title-like line that does not end in sentence punctuation,
            False otherwise.
    """
    stripped = line.strip()
    if not stripped:
        return False
    if MARKDOWN_HEADING_PATTERN.match(stripped):
        return True
    if len(stripped) <= HEADING_MAX_CHARS and not stripped.endswith(SENTENCE_END_CHARS):
        return stripped[0].isupper() or stripped[0] == "#"
    return False


def extract_headings(text):
    """
    Find every heading-like line in a document and its character offset.

    Args:
        text (str): The document's cleaned text.

    Returns:
        list[dict]: One entry per detected heading, in document order,
            each with "offset" (int, the character index where the
            heading line starts in text) and "heading" (str, the
            heading text with any leading "#" markers stripped).
    """
    headings = []
    cursor = 0
    for line in text.split("\n"):
        if is_heading_line(line):
            heading_text = line.strip().lstrip("#").strip()
            headings.append({"offset": cursor, "heading": heading_text})
        cursor += len(line) + 1
    return headings


def find_section_for_offset(headings, offset):
    """
    Find the section a character offset falls under.

    Args:
        headings (list[dict]): Heading entries as returned by
            extract_headings, each with "offset" (int) and "heading"
            (str).
        offset (int): A character offset into the same document text
            the headings were extracted from.

    Returns:
        str or None: The heading text of the nearest heading whose
            offset is less than or equal to the given offset, or None
            if no such heading exists (the offset comes before every
            heading, or the document has none).
    """
    current_section = None
    for heading in headings:
        if heading["offset"] <= offset:
            current_section = heading["heading"]
        else:
            break
    return current_section


def build_chunk_records(source, cleaned_text):
    """
    Chunk one document's cleaned text and attach metadata to every chunk.

    Args:
        source (str): The originating file path for this document, used
            as the source identifier on every resulting chunk.
        cleaned_text (str): The document's cleaned text, as produced by
            cleaner.clean_text.

    Returns:
        list[dict]: One record per chunk, each with the fields
            "source", "chunk_id", "chunk_index", "total_chunks",
            "section", "start_char", "end_char", and "text", as
            described in this module's docstring.
    """
    headings = extract_headings(cleaned_text)
    chunks = chunk_by_paragraph(cleaned_text, PARAGRAPH_MAX_CHUNK_SIZE)
    total_chunks = len(chunks)
    filename = os.path.basename(source)

    records = []
    for index, chunk in enumerate(chunks):
        records.append({
            "source": source,
            "chunk_id": "{}#{}".format(filename, index),
            "chunk_index": index,
            "total_chunks": total_chunks,
            "section": find_section_for_offset(headings, chunk["start"]),
            "start_char": chunk["start"],
            "end_char": chunk["end"],
            "text": chunk["text"],
        })
    return records


def build_corpus_chunk_records(cleaned_records):
    """
    Build metadata-tagged chunks for every document in a corpus.

    Args:
        cleaned_records (list[dict]): One entry per document, each with
            "source" (str) and "cleaned_text" (str) keys.

    Returns:
        list[dict]: The concatenation of build_chunk_records's output
            for every document, in corpus order, so every chunk in the
            whole corpus shares the same metadata field structure.
    """
    all_records = []
    for record in cleaned_records:
        all_records.extend(build_chunk_records(record["source"], record["cleaned_text"]))
    return all_records


def verify_consistent_fields(chunk_records):
    """
    Confirm every chunk record in a corpus shares the same field names.

    Args:
        chunk_records (list[dict]): Chunk records as returned by
            build_corpus_chunk_records.

    Returns:
        bool: True if every record's set of keys matches the first
            record's set of keys.

    Raises:
        AssertionError: If chunk_records is empty, or if any record's
            keys differ from the first record's keys.
    """
    assert chunk_records, "no chunk records to verify"
    expected_fields = set(chunk_records[0].keys())
    for record in chunk_records:
        actual_fields = set(record.keys())
        assert actual_fields == expected_fields, (
            "inconsistent metadata fields: expected {}, found {} on chunk_id={}".format(
                sorted(expected_fields), sorted(actual_fields), record.get("chunk_id")
            )
        )
    return True


def trace_chunk_to_source(chunk_record, cleaned_lookup):
    """
    Recover a chunk's exact original text using only its stored metadata.

    Args:
        chunk_record (dict): A single chunk record, with at least
            "source", "start_char", and "end_char" keys.
        cleaned_lookup (dict): Mapping of source file path (str) to that
            document's full cleaned text (str).

    Returns:
        str: The substring of the source document's cleaned text lying
            between "start_char" and "end_char", recovered independently
            of the chunk's stored "text" field.
    """
    document_text = cleaned_lookup[chunk_record["source"]]
    return document_text[chunk_record["start_char"]:chunk_record["end_char"]]


def demonstrate_traceability(chunk_records, cleaned_lookup):
    """
    Show that a chunk's metadata alone is enough to recover its source.

    Args:
        chunk_records (list[dict]): Chunk records as returned by
            build_corpus_chunk_records.
        cleaned_lookup (dict): Mapping of source file path (str) to that
            document's full cleaned text (str), as used by
            trace_chunk_to_source.

    Returns:
        bool: True if the recovered text matches the chunk's stored
            text exactly, False otherwise. Also prints the chunk's
            metadata, the recovered text, and the pass/fail result.
    """
    sample_chunk = chunk_records[len(chunk_records) // 2]
    recovered_text = trace_chunk_to_source(sample_chunk, cleaned_lookup)
    matches = recovered_text == sample_chunk["text"]

    print("Traceability check:")
    print("  chunk_id:     {}".format(sample_chunk["chunk_id"]))
    print("  source:       {}".format(sample_chunk["source"]))
    print("  section:      {}".format(sample_chunk["section"]))
    print("  chunk_index:  {} of {}".format(sample_chunk["chunk_index"], sample_chunk["total_chunks"]))
    print("  char range:   [{}:{}]".format(sample_chunk["start_char"], sample_chunk["end_char"]))
    print("  recovered text from source using only stored offsets:")
    print("    {}".format(" ".join(recovered_text.split())[:140]))
    print("  matches stored chunk text: {}".format(matches))

    return matches


def print_sample_chunks(chunk_records, sample_count):
    """
    Print chunk text alongside its full metadata block for a few chunks.

    Args:
        chunk_records (list[dict]): Chunk records as returned by
            build_corpus_chunk_records.
        sample_count (int): Maximum number of chunks to print.

    Returns:
        None
    """
    for record in chunk_records[:sample_count]:
        preview = " ".join(record["text"].split())
        if len(preview) > 140:
            preview = preview[:140] + "..."
        print("chunk_id: {}".format(record["chunk_id"]))
        print("  text: {}".format(preview))
        print("  metadata:")
        for key in ("source", "chunk_index", "total_chunks", "section", "start_char", "end_char"):
            print("    {}: {}".format(key, record[key]))
        print()


if __name__ == "__main__":
    from loader import load_corpus
    from cleaner import clean_text

    corpus_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")
    loaded_records = load_corpus(corpus_folder)

    cleaned_records = [
        {"source": record["source"], "cleaned_text": clean_text(record["text"])}
        for record in loaded_records
    ]
    cleaned_lookup = {record["source"]: record["cleaned_text"] for record in cleaned_records}

    all_chunks = build_corpus_chunk_records(cleaned_records)

    print()
    print("Built {} chunk(s) across {} document(s).".format(len(all_chunks), len(cleaned_records)))
    verify_consistent_fields(all_chunks)
    print("Verified: every chunk shares the same metadata fields: {}".format(sorted(all_chunks[0].keys())))
    print()

    demonstrate_traceability(all_chunks, cleaned_lookup)
    print()

    print("Sample chunks with metadata:")
    print_sample_chunks(all_chunks, 5)
