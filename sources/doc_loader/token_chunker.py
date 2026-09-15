"""
Splits text into retrieval-sized chunks measured in model tokens (via
the offline tiktoken tokenizer) instead of characters, with controlled
token overlap between adjacent chunks.

Inputs:
    A plain-text string, such as the "cleaned_text" value produced by
    cleaner.clean_text() for one document, plus a chunk size and an
    overlap amount expressed in tokens.

Outputs:
    A list of chunk records, one per chunk, each a dict with "text"
    (str), "start_token" (int, inclusive token offset), "end_token"
    (int, exclusive token offset), and "token_count" (int). The module
    also prints, when run directly: the resulting chunk count and a
    couple of example chunks with their token counts, plus a side-by-side
    demonstration of a sentence sitting on a chunk boundary being cut in
    half with overlap off and preserved intact with overlap on.

No network calls or API keys are used anywhere in this module; tiktoken
runs fully offline once its encoding data is installed/cached locally.
"""

import os

import tiktoken

# cl100k_base is the tokenizer used by gpt-3.5-turbo and gpt-4. Sizing
# chunks against it keeps the token counts reported here meaningful for
# both context-window budgeting and per-token embedding/generation cost
# on those models.
ENCODING_NAME = "cl100k_base"

# 300 tokens (roughly 1,100-1,300 characters of English prose) keeps a
# single chunk small relative to an 8K-token context window (the base
# gpt-4 context size): a handful of retrieved chunks, the system prompt,
# and the user's question all still fit comfortably together. A 60-token
# overlap (20% of the chunk size) trades a modest increase in stored and
# embedded tokens across the corpus for protection against severing an
# idea that happens to fall on a chunk boundary -- cheap insurance next
# to the cost of retrieving a chunk whose key sentence is truncated.
DEFAULT_CHUNK_SIZE_TOKENS = 300
DEFAULT_OVERLAP_TOKENS = 60


def get_encoding(encoding_name=ENCODING_NAME):
    """
    Load a tiktoken encoding by name.

    Args:
        encoding_name (str): Name of the tiktoken encoding to load, e.g.
            "cl100k_base".

    Returns:
        tiktoken.Encoding: The loaded encoding, used to convert between
            text and token ids.
    """
    return tiktoken.get_encoding(encoding_name)


def count_tokens(text, encoding):
    """
    Count how many tokens a piece of text encodes to.

    Args:
        text (str): The text to measure.
        encoding (tiktoken.Encoding): The tokenizer to use.

    Returns:
        int: The number of tokens text encodes to under encoding.
    """
    return len(encoding.encode(text))


def chunk_by_tokens(text, encoding, chunk_size, overlap):
    """
    Split text into fixed-size, overlapping windows measured in tokens.

    Args:
        text (str): The text to split.
        encoding (tiktoken.Encoding): The tokenizer used to measure and
            reconstruct chunks.
        chunk_size (int): Maximum number of tokens per chunk.
        overlap (int): Number of tokens repeated at the start of each
            chunk from the tail of the previous chunk.

    Returns:
        list[dict]: One record per chunk, each with "text" (str, the
            decoded chunk), "start_token" (int, inclusive token offset
            into the encoded text), "end_token" (int, exclusive token
            offset), and "token_count" (int, end_token - start_token).
    """
    token_ids = encoding.encode(text)
    total_tokens = len(token_ids)

    chunks = []
    start = 0
    while start < total_tokens:
        end = min(start + chunk_size, total_tokens)
        window = token_ids[start:end]
        chunks.append({
            "text": encoding.decode(window),
            "start_token": start,
            "end_token": end,
            "token_count": len(window),
        })
        if end == total_tokens:
            break
        start = end - overlap

    return chunks


def build_boundary_demo_text(encoding, chunk_size):
    """
    Build synthetic text whose token stream deliberately straddles a
    chunk boundary with one identifiable sentence.

    Args:
        encoding (tiktoken.Encoding): The tokenizer used to place the
            sentence at an exact token offset.
        chunk_size (int): The chunk size (in tokens) the boundary should
            be constructed against; the sentence is centered on the
            token offset equal to chunk_size.

    Returns:
        tuple[str, str]: (demo_text, boundary_sentence) where demo_text
            is a document whose token at index chunk_size falls inside
            boundary_sentence, and boundary_sentence is the exact
            sentence to search for in the resulting chunks.
    """
    filler_sentence = "The retrieval pipeline processes many similar documents in sequence. "
    boundary_sentence = (
        "The single most important design decision in this whole system is "
        "that overlap must be large enough to fully preserve any idea that "
        "would otherwise straddle a chunk boundary."
    )

    filler_tokens = encoding.encode(filler_sentence * (chunk_size // 4 + 20))
    boundary_tokens = encoding.encode(boundary_sentence)

    insert_at = chunk_size - len(boundary_tokens) // 2
    assembled_tokens = filler_tokens[:insert_at] + boundary_tokens + filler_tokens[insert_at:2 * chunk_size]

    return encoding.decode(assembled_tokens), boundary_sentence


def sentence_intact_in_chunks(chunks, sentence):
    """
    Check whether a sentence appears whole inside at least one chunk.

    Args:
        chunks (list[dict]): Chunk records as returned by
            chunk_by_tokens, each with a "text" key.
        sentence (str): The exact sentence to search for.

    Returns:
        bool: True if sentence is a substring of at least one chunk's
            text, False otherwise.
    """
    return any(sentence in chunk["text"] for chunk in chunks)


def print_chunk_examples(chunks, label, sample_count=2):
    """
    Print a couple of example chunks together with their token counts.

    Args:
        chunks (list[dict]): Chunk records as returned by
            chunk_by_tokens, each with "text", "start_token",
            "end_token", and "token_count" keys.
        label (str): A short name for this run, used in the printed
            header.
        sample_count (int): Maximum number of chunks to print.

    Returns:
        None
    """
    print("{}: {} chunk(s)".format(label, len(chunks)))
    for index, chunk in enumerate(chunks[:sample_count]):
        preview = " ".join(chunk["text"].split())
        if len(preview) > 160:
            preview = preview[:160] + "..."
        print("  chunk {} [tokens {}:{}] ({} tokens): {}".format(
            index + 1, chunk["start_token"], chunk["end_token"], chunk["token_count"], preview
        ))


if __name__ == "__main__":
    from loader import load_corpus
    from cleaner import clean_text

    encoding = get_encoding()

    corpus_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")
    loaded_records = load_corpus(corpus_folder)
    target_record = next(r for r in loaded_records if r["source"].endswith("long_report.txt"))
    sample_text = clean_text(target_record["text"])

    print()
    print("Token-based chunking on: {}".format(target_record["source"]))
    print("Document length: {} tokens ({} chars)".format(
        count_tokens(sample_text, encoding), len(sample_text)
    ))
    print("Chunk size: {} tokens, overlap: {} tokens".format(
        DEFAULT_CHUNK_SIZE_TOKENS, DEFAULT_OVERLAP_TOKENS
    ))
    print(
        "Rationale: 300 tokens keeps each chunk small next to an 8K-token "
        "context window (gpt-4-class model), leaving room for several "
        "retrieved chunks plus the prompt; a 60-token (20%) overlap adds a "
        "modest token/cost overhead in exchange for not losing ideas that "
        "land on a chunk boundary."
    )
    print()

    document_chunks = chunk_by_tokens(sample_text, encoding, DEFAULT_CHUNK_SIZE_TOKENS, DEFAULT_OVERLAP_TOKENS)
    print_chunk_examples(document_chunks, "Document chunks")
    print()

    print("Overlap effect demonstration:")
    demo_text, boundary_sentence = build_boundary_demo_text(encoding, DEFAULT_CHUNK_SIZE_TOKENS)
    print("  boundary sentence: \"{}\"".format(boundary_sentence))
    print("  boundary sentence token count: {}".format(count_tokens(boundary_sentence, encoding)))
    print()

    chunks_without_overlap = chunk_by_tokens(demo_text, encoding, DEFAULT_CHUNK_SIZE_TOKENS, overlap=0)
    intact_without_overlap = sentence_intact_in_chunks(chunks_without_overlap, boundary_sentence)
    print_chunk_examples(chunks_without_overlap, "  Without overlap (overlap=0)")
    print("  sentence appears intact in a single chunk: {}".format(intact_without_overlap))
    print()

    chunks_with_overlap = chunk_by_tokens(demo_text, encoding, DEFAULT_CHUNK_SIZE_TOKENS, DEFAULT_OVERLAP_TOKENS)
    intact_with_overlap = sentence_intact_in_chunks(chunks_with_overlap, boundary_sentence)
    print_chunk_examples(chunks_with_overlap, "  With overlap (overlap={})".format(DEFAULT_OVERLAP_TOKENS))
    print("  sentence appears intact in a single chunk: {}".format(intact_with_overlap))
    print()

    print("Result: overlap={} {} the boundary sentence, overlap=0 {} it.".format(
        DEFAULT_OVERLAP_TOKENS,
        "preserves" if intact_with_overlap else "does NOT preserve",
        "splits" if not intact_without_overlap else "does not split",
    ))
