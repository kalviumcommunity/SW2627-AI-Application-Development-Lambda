"""
Embeds a corpus of chunks in batches through a free, local embedding
backend (Ollama + nomic-embed-text, OpenAI-compatible), retries transient
failures with exponential backoff, skips chunks that already have a
stored embedding, and reports run totals.

Inputs:
    Chunk records built by the existing pipeline (loader, cleaner,
    metadata), each with "text" plus source metadata. Backend settings
    come from environment variables or the ".env" file next to this
    script: EMBEDDING_BASE_URL, EMBEDDING_API_KEY, EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE, and EMBEDDING_SIMULATED_COST_PER_1K_TOKENS.
    Optional command-line flags: --batch-size, --simulate-failures.

Outputs:
    A persistent embedding store (embedding_store.json, next to this
    script) mapping each chunk to its text fingerprint, metadata, and
    vector, so a re-run over the same corpus skips chunks that are
    already embedded. A printed run summary: batching used, total
    chunks, embeddings generated, chunks skipped, retries that happened,
    batches that ultimately failed (with reasons), and an approximate
    cost.

The backend is free, so actual spend is $0. The reported cost is a
SIMULATED estimate: approximate token count multiplied by a made-up
per-1K-token rate, present only to demonstrate cost tracking. No paid
API key is used or required.
"""

import argparse
import hashlib
import json
import os
import sys
import time

import tiktoken

from embed_store import (
    EmbeddingRequestError,
    confirm_uniform_dimension,
    embed_texts,
    get_embedding_config,
    load_dotenv_file,
)

ENV_FILE_NAME = ".env"
STORE_FILE_NAME = "embedding_store.json"
MAX_RETRIES = 3
BASE_DELAY_SECONDS = 0.5
TOKEN_ENCODING_NAME = "cl100k_base"


def get_run_settings(env_path):
    """
    Read batch size and simulated cost rate from the environment.

    Args:
        env_path (str): Path to a .env file to fall back on for any
            variable not set in the process environment.

    Returns:
        dict: {"batch_size": int, "cost_per_1k_tokens": float}. Missing
            values fall back to a batch size of 8 and a simulated rate
            of 0.0001 per 1K tokens.

    Raises:
        ValueError: If the batch size is not a positive integer or the
            rate is not a non-negative number.
    """
    dotenv_values = load_dotenv_file(env_path)

    def lookup(name, default):
        """
        Find a setting in the environment, then the .env file.

        Args:
            name (str): The variable name to look up.
            default (str): Value to use if the variable is not set.

        Returns:
            str: The resolved value.
        """
        return os.environ.get(name) or dotenv_values.get(name) or default

    batch_size = int(lookup("EMBEDDING_BATCH_SIZE", "8"))
    rate = float(lookup("EMBEDDING_SIMULATED_COST_PER_1K_TOKENS", "0.0001"))
    if batch_size < 1:
        raise ValueError("EMBEDDING_BATCH_SIZE must be a positive integer")
    if rate < 0:
        raise ValueError("EMBEDDING_SIMULATED_COST_PER_1K_TOKENS must not be negative")
    return {"batch_size": batch_size, "cost_per_1k_tokens": rate}


def load_store(path):
    """
    Load the persistent embedding store from disk.

    Args:
        path (str): Path to the JSON store file.

    Returns:
        dict: Mapping of chunk key to stored record. Empty if the file
            does not exist.
    """
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_store(path, store):
    """
    Write the embedding store to disk.

    Args:
        path (str): Path to the JSON store file.
        store (dict): Mapping of chunk key to stored record.

    Returns:
        None
    """
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(store, handle, ensure_ascii=False)


def chunk_key(chunk):
    """
    Build the stable identifier used to look a chunk up in the store.

    Args:
        chunk (dict): A chunk record with "source" (str) and
            "chunk_index" (int) keys.

    Returns:
        str: "<source>#<chunk_index>".
    """
    return "{}#{}".format(chunk["source"], chunk["chunk_index"])


def text_fingerprint(text):
    """
    Hash a chunk's text so edits to it can be detected.

    Args:
        text (str): The chunk text.

    Returns:
        str: The SHA-256 hex digest of the UTF-8 encoded text.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_pending(chunks, store, model_name):
    """
    Separate chunks that still need embedding from ones already stored.

    Args:
        chunks (list[dict]): Chunk records with "text", "source", and
            "chunk_index" keys.
        store (dict): The loaded embedding store.
        model_name (str): The embedding model in use. A stored vector
            only counts if it came from this same model and from
            identical chunk text.

    Returns:
        tuple[list[dict], list[dict]]: (pending, skipped) chunk lists.
    """
    pending = []
    skipped = []
    for chunk in chunks:
        stored = store.get(chunk_key(chunk))
        already_embedded = (
            stored is not None
            and stored.get("model") == model_name
            and stored.get("text_hash") == text_fingerprint(chunk["text"])
        )
        (skipped if already_embedded else pending).append(chunk)
    return pending, skipped


def make_batches(items, batch_size):
    """
    Split a list into consecutive batches.

    Args:
        items (list): The items to split.
        batch_size (int): Maximum number of items per batch.

    Returns:
        list[list]: The batches, in order; the last may be smaller.
    """
    return [items[start:start + batch_size] for start in range(0, len(items), batch_size)]


def embed_batch_with_retry(texts, embed_fn, max_retries, base_delay, sleep_fn=time.sleep):
    """
    Embed one batch, retrying transient failures with exponential backoff.

    Args:
        texts (list[str]): The batch's chunk texts.
        embed_fn (callable): Function taking a list of texts and
            returning a list of vectors; may raise EmbeddingRequestError.
        max_retries (int): Maximum number of retries after the first
            attempt.
        base_delay (float): Seconds to wait before the first retry; the
            wait doubles after each further retry.
        sleep_fn (callable): Function used to wait, replaceable for
            testing.

    Returns:
        dict: {"vectors": list or None, "retries": int, "error": str or
            None}. "vectors" is None and "error" is set when the batch
            ultimately failed; "retries" counts retries actually made.
    """
    retries = 0
    while True:
        try:
            return {"vectors": embed_fn(texts), "retries": retries, "error": None}
        except EmbeddingRequestError as error:
            if not error.retryable or retries >= max_retries:
                return {"vectors": None, "retries": retries, "error": str(error)}
            delay = base_delay * (2 ** retries)
            print("  transient error ({}); retry {}/{} in {:.1f}s".format(
                str(error)[:80], retries + 1, max_retries, delay
            ))
            sleep_fn(delay)
            retries += 1


def make_flaky_embed_fn(real_embed_fn):
    """
    Wrap an embed function to inject failures for demonstration.

    Args:
        real_embed_fn (callable): The real function taking a list of
            texts and returning vectors.

    Returns:
        callable: A function that behaves like real_embed_fn except that
            the first call raises a retryable rate-limit error (so one
            retry succeeds) and the third distinct batch always raises a
            retryable error (so it exhausts its retries and fails).
    """
    state = {"calls": 0, "batches_seen": 0, "current_batch_first_text": None, "first_call_failed": False}

    def flaky(texts):
        """
        Embed a batch, injecting the simulated failures described above.

        Args:
            texts (list[str]): The batch's chunk texts.

        Returns:
            list[list[float]]: One vector per text.
        """
        if texts[0] != state["current_batch_first_text"]:
            state["current_batch_first_text"] = texts[0]
            state["batches_seen"] += 1
        if state["batches_seen"] == 1 and not state["first_call_failed"]:
            state["first_call_failed"] = True
            raise EmbeddingRequestError("simulated rate limit (HTTP 429)", retryable=True)
        if state["batches_seen"] == 3:
            raise EmbeddingRequestError("simulated server error (HTTP 503)", retryable=True)
        return real_embed_fn(texts)

    return flaky


def estimate_tokens(texts, encoding):
    """
    Approximate how many tokens a list of texts contains.

    Args:
        texts (list[str]): The texts to measure.
        encoding (tiktoken.Encoding): Tokenizer used for the estimate.
            It is not the backend model's own tokenizer, so the result
            is approximate.

    Returns:
        int: Total approximate token count across texts.
    """
    return sum(len(encoding.encode(text)) for text in texts)


def run_batch_embedding(chunks, embed_fn, model_name, store_path, batch_size, cost_per_1k_tokens,
                        max_retries=MAX_RETRIES, base_delay=BASE_DELAY_SECONDS):
    """
    Embed a corpus in batches, skipping chunks that are already stored.

    Args:
        chunks (list[dict]): Chunk records with "text", "source",
            "chunk_index", and other metadata keys.
        embed_fn (callable): Function taking a list of texts and
            returning a list of vectors.
        model_name (str): Embedding model name, recorded with each
            stored vector.
        store_path (str): Path to the persistent JSON embedding store.
        batch_size (int): Maximum chunks per request.
        cost_per_1k_tokens (float): Simulated rate per 1,000 tokens.
        max_retries (int): Retries allowed per batch after the first
            attempt.
        base_delay (float): Seconds before the first retry (doubles
            each retry).

    Returns:
        dict: Run totals with keys "total_chunks", "embedded",
            "skipped", "batch_size", "num_batches", "retries",
            "failed_batches" (list of dicts with "batch_number",
            "chunk_count", "retries", "error"), "failed_chunks",
            "approx_tokens", "simulated_cost", "cost_per_1k_tokens",
            and "vector_length" (int or None).
    """
    store = load_store(store_path)
    pending, skipped = split_pending(chunks, store, model_name)
    batches = make_batches(pending, batch_size)
    encoding = tiktoken.get_encoding(TOKEN_ENCODING_NAME)

    embedded = 0
    total_retries = 0
    approx_tokens = 0
    failed_batches = []
    vector_length = None

    for number, batch in enumerate(batches, start=1):
        texts = [chunk["text"] for chunk in batch]
        print("Batch {}/{}: embedding {} chunk(s)".format(number, len(batches), len(batch)))
        result = embed_batch_with_retry(texts, embed_fn, max_retries, base_delay)
        total_retries += result["retries"]

        if result["vectors"] is None:
            failed_batches.append({
                "batch_number": number,
                "chunk_count": len(batch),
                "retries": result["retries"],
                "error": result["error"],
            })
            continue

        vectors = result["vectors"]
        if len(vectors) != len(batch):
            failed_batches.append({
                "batch_number": number,
                "chunk_count": len(batch),
                "retries": result["retries"],
                "error": "backend returned {} vectors for {} chunks".format(len(vectors), len(batch)),
            })
            continue

        length = confirm_uniform_dimension(vectors)
        if vector_length is not None:
            assert length == vector_length, "vector length changed between batches"
        vector_length = length

        for chunk, vector in zip(batch, vectors):
            metadata = {key: value for key, value in chunk.items() if key != "text"}
            store[chunk_key(chunk)] = {
                "model": model_name,
                "text_hash": text_fingerprint(chunk["text"]),
                "text": chunk["text"],
                "metadata": metadata,
                "vector": vector,
            }
        save_store(store_path, store)
        embedded += len(batch)
        approx_tokens += estimate_tokens(texts, encoding)

    if vector_length is None and skipped:
        vector_length = len(store[chunk_key(skipped[0])]["vector"])

    return {
        "total_chunks": len(chunks),
        "embedded": embedded,
        "skipped": len(skipped),
        "batch_size": batch_size,
        "num_batches": len(batches),
        "retries": total_retries,
        "failed_batches": failed_batches,
        "failed_chunks": sum(entry["chunk_count"] for entry in failed_batches),
        "approx_tokens": approx_tokens,
        "simulated_cost": approx_tokens / 1000 * cost_per_1k_tokens,
        "cost_per_1k_tokens": cost_per_1k_tokens,
        "vector_length": vector_length,
    }


def print_run_summary(summary):
    """
    Print the full run summary.

    Args:
        summary (dict): Run totals as returned by run_batch_embedding.

    Returns:
        None
    """
    print()
    print("Run summary")
    print("  batching: {} chunk(s) per request, {} batch(es) sent".format(
        summary["batch_size"], summary["num_batches"]
    ))
    print("  total chunks:                {}".format(summary["total_chunks"]))
    print("  embeddings generated:        {}".format(summary["embedded"]))
    print("  chunks skipped (already stored): {}".format(summary["skipped"]))
    print("  chunks in failed batches:    {}".format(summary["failed_chunks"]))
    print("  batches failed:              {}".format(len(summary["failed_batches"])))
    print("  retries that happened:       {}".format(summary["retries"]))
    print("  vector length:               {}".format(summary["vector_length"]))
    print("  approx tokens embedded:      {}".format(summary["approx_tokens"]))
    print("  SIMULATED cost estimate:     ${:.6f} (at a made-up ${} per 1K tokens; actual spend is $0, backend is local)".format(
        summary["simulated_cost"], summary["cost_per_1k_tokens"]
    ))
    for failure in summary["failed_batches"]:
        print("  FAILED batch {} ({} chunk(s), {} retries): {}".format(
            failure["batch_number"], failure["chunk_count"], failure["retries"], failure["error"]
        ))
    accounted = summary["embedded"] + summary["skipped"] + summary["failed_chunks"]
    print("  accounting check: {} embedded + {} skipped + {} failed = {} of {} chunks -> {}".format(
        summary["embedded"], summary["skipped"], summary["failed_chunks"], accounted,
        summary["total_chunks"], "OK" if accounted == summary["total_chunks"] else "MISMATCH"
    ))


def parse_arguments(argv):
    """
    Parse command-line flags.

    Args:
        argv (list[str]): Arguments excluding the program name.

    Returns:
        argparse.Namespace: Parsed flags "batch_size" (int or None) and
            "simulate_failures" (bool).
    """
    parser = argparse.ArgumentParser(description="Embed corpus chunks in batches.")
    parser.add_argument("--batch-size", type=int, default=None, help="chunks per request (overrides EMBEDDING_BATCH_SIZE)")
    parser.add_argument("--simulate-failures", action="store_true", help="inject transient errors to demonstrate retries and failed-batch reporting")
    return parser.parse_args(argv)


if __name__ == "__main__":
    from loader import load_corpus
    from cleaner import clean_text
    from metadata import build_corpus_chunk_records

    arguments = parse_arguments(sys.argv[1:])
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ENV_FILE_NAME)
    store_path = os.path.join(script_dir, STORE_FILE_NAME)

    config = get_embedding_config(env_path)
    settings = get_run_settings(env_path)
    batch_size = arguments.batch_size or settings["batch_size"]

    loaded_records = load_corpus(os.path.join(script_dir, "sample_corpus"))
    cleaned_records = [
        {"source": record["source"], "cleaned_text": clean_text(record["text"])}
        for record in loaded_records
    ]
    chunk_records = build_corpus_chunk_records(cleaned_records)

    print()
    print("Embedding backend: {} (model: {})".format(config["base_url"], config["model_name"]))
    print("Prepared {} chunk(s) from {} document(s).".format(len(chunk_records), len(cleaned_records)))
    print()

    def real_embed_fn(texts):
        return embed_texts(texts, config["base_url"], config["api_key"], config["model_name"])

    embed_fn = make_flaky_embed_fn(real_embed_fn) if arguments.simulate_failures else real_embed_fn

    run_summary = run_batch_embedding(
        chunk_records, embed_fn, config["model_name"], store_path,
        batch_size, settings["cost_per_1k_tokens"],
    )
    print_run_summary(run_summary)
    sys.exit(1 if run_summary["failed_batches"] else 0)
