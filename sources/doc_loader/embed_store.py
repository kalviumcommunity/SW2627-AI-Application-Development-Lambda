"""
Generates embeddings for prepared text chunks through a free, local
embedding backend (Ollama running the nomic-embed-text model behind an
OpenAI-compatible endpoint) and stores the results together with each
chunk's source metadata.

Inputs:
    A list of chunk records, such as the ones produced by
    metadata.build_corpus_chunk_records(), each with at least a "text"
    key plus source metadata (source document, chunk index, section).
    The embedding backend's base URL, API key placeholder, and model
    name are read from environment variables, falling back to a ".env"
    file next to this script -- none of the three is hard-coded here.

Outputs:
    A list of embedding records, one per input chunk, each pairing the
    chunk's text and metadata with its embedding vector. Printed to
    stdout: how many chunks were embedded, the shared vector length, and
    a few sample (trimmed) vector values. Written to disk: a JSON sample
    file (embedding_sample_output.json, next to this script) holding
    each record's text, metadata, vector dimension, and a trimmed vector
    preview, so a run can be inspected afterward.

Uses Ollama's local, free, OpenAI-compatible embedding endpoint
(http://localhost:11434/v1 by default) with the nomic-embed-text model.
No paid OpenAI key is used or required anywhere in this module.
"""

import json
import os

import requests

ENV_FILE_NAME = ".env"
OUTPUT_FILE_NAME = "embedding_sample_output.json"
VECTOR_PREVIEW_LENGTH = 5

REQUIRED_ENV_VARS = ("EMBEDDING_BASE_URL", "EMBEDDING_API_KEY", "EMBEDDING_MODEL")


class EmbeddingRequestError(RuntimeError):
    """
    Raised when an embedding request fails.

    The "retryable" attribute is True when the failure is transient
    (connection problem, timeout, rate limit, or server error) and False
    when repeating the same request would not help.
    """

    def __init__(self, message, retryable):
        """
        Create the error.

        Args:
            message (str): Human-readable description of the failure.
            retryable (bool): True if the failure is transient and the
                request is worth retrying.

        Returns:
            None
        """
        super().__init__(message)
        self.retryable = retryable


def load_dotenv_file(path):
    """
    Parse a simple KEY=VALUE ".env" file.

    Args:
        path (str): Path to the .env file to read.

    Returns:
        dict[str, str]: Mapping of variable name to value for every
            non-blank, non-comment "KEY=VALUE" line found. Returns an
            empty dict if the file does not exist.
    """
    values = {}
    if not os.path.isfile(path):
        return values

    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            values[key.strip()] = value.strip()

    return values


def get_embedding_config(env_path):
    """
    Resolve the embedding backend's base URL, API key, and model name.

    Args:
        env_path (str): Path to a .env file to fall back on for any
            variable not already set in the process environment.

    Returns:
        dict[str, str]: A dict with keys "base_url", "api_key", and
            "model_name", sourced from os.environ first and the .env
            file second.

    Raises:
        RuntimeError: If any of EMBEDDING_BASE_URL, EMBEDDING_API_KEY,
            or EMBEDDING_MODEL is not set in either the environment or
            the .env file.
    """
    dotenv_values = load_dotenv_file(env_path)
    resolved = {}
    missing = []

    for var_name in REQUIRED_ENV_VARS:
        value = os.environ.get(var_name) or dotenv_values.get(var_name)
        if not value:
            missing.append(var_name)
        resolved[var_name] = value

    if missing:
        raise RuntimeError(
            "missing required embedding configuration: {} "
            "(set as environment variables or in {})".format(", ".join(missing), env_path)
        )

    return {
        "base_url": resolved["EMBEDDING_BASE_URL"],
        "api_key": resolved["EMBEDDING_API_KEY"],
        "model_name": resolved["EMBEDDING_MODEL"],
    }


def embed_texts(texts, base_url, api_key, model_name):
    """
    Request embedding vectors for a list of texts from the backend.

    Args:
        texts (list[str]): The text chunks to embed, in order.
        base_url (str): Base URL of an OpenAI-compatible embeddings
            endpoint, e.g. "http://localhost:11434/v1".
        api_key (str): API key placeholder sent as a bearer token. A
            local Ollama server does not check its value, but an
            OpenAI-compatible client is still expected to send one.
        model_name (str): Name of the embedding model to use, e.g.
            "nomic-embed-text".

    Returns:
        list[list[float]]: One embedding vector per input text, in the
            same order as texts.

    Raises:
        EmbeddingRequestError: If the backend cannot be reached, returns
            a non-200 response, or returns a body that cannot be parsed
            into embeddings. The error's "retryable" attribute is True
            for connection failures, timeouts, HTTP 429, and HTTP 5xx.
    """
    try:
        response = requests.post(
            "{}/embeddings".format(base_url.rstrip("/")),
            headers={
                "Authorization": "Bearer {}".format(api_key),
                "Content-Type": "application/json",
            },
            json={"model": model_name, "input": texts},
            timeout=60,
        )
    except (requests.ConnectionError, requests.Timeout) as error:
        raise EmbeddingRequestError("embedding backend unreachable: {}".format(error), retryable=True)

    if response.status_code != 200:
        retryable = response.status_code == 429 or response.status_code >= 500
        raise EmbeddingRequestError(
            "embedding request failed with status {}: {}".format(response.status_code, response.text),
            retryable=retryable,
        )

    payload = response.json()
    try:
        ordered_data = sorted(payload["data"], key=lambda entry: entry["index"])
        return [entry["embedding"] for entry in ordered_data]
    except (KeyError, TypeError) as error:
        raise RuntimeError("unexpected embedding response shape: {}".format(error))


def confirm_uniform_dimension(vectors):
    """
    Confirm every embedding vector has the same length.

    Args:
        vectors (list[list[float]]): Embedding vectors to check.

    Returns:
        int: The shared vector length.

    Raises:
        AssertionError: If vectors is empty, or if any vector's length
            differs from the first vector's length.
    """
    assert vectors, "no vectors to check"
    lengths = [len(vector) for vector in vectors]
    first_length = lengths[0]
    assert all(length == first_length for length in lengths), (
        "embedding vectors do not share a common length: {}".format(lengths)
    )
    return first_length


def build_embedding_records(chunk_records, vectors):
    """
    Pair each chunk's text and metadata with its embedding vector.

    Args:
        chunk_records (list[dict]): Chunk records to embed, each with at
            least a "text" key and any number of metadata keys (for
            example "source", "chunk_index", "section").
        vectors (list[list[float]]): Embedding vectors aligned with
            chunk_records by index.

    Returns:
        list[dict]: One record per chunk, each with "text" (str),
            "metadata" (dict, every key from the chunk record except
            "text"), "vector" (list[float], the full embedding), and
            "vector_dimension" (int, len(vector)).
    """
    records = []
    for chunk_record, vector in zip(chunk_records, vectors):
        metadata = {key: value for key, value in chunk_record.items() if key != "text"}
        records.append({
            "text": chunk_record["text"],
            "metadata": metadata,
            "vector": vector,
            "vector_dimension": len(vector),
        })
    return records


def print_verification(embedding_records, dimension):
    """
    Print verification output for one embedding run.

    Args:
        embedding_records (list[dict]): Records as returned by
            build_embedding_records, each with "text", "metadata",
            "vector", and "vector_dimension" keys.
        dimension (int): The shared vector length across all records.

    Returns:
        None
    """
    print("Chunks embedded: {}".format(len(embedding_records)))
    print("Vector length: {}".format(dimension))
    print()
    print("Sample vector values (first {} dimensions):".format(VECTOR_PREVIEW_LENGTH))
    for record in embedding_records[:3]:
        preview = [round(value, 5) for value in record["vector"][:VECTOR_PREVIEW_LENGTH]]
        print("  {} -> {}".format(record["metadata"].get("chunk_id", record["metadata"].get("source")), preview))


def save_sample_output(embedding_records, output_path):
    """
    Save embedding records to a JSON file, with vectors trimmed.

    Args:
        embedding_records (list[dict]): Records as returned by
            build_embedding_records, each with "text", "metadata",
            "vector", and "vector_dimension" keys.
        output_path (str): File path to write the JSON output to.

    Returns:
        None
    """
    trimmed_records = []
    for record in embedding_records:
        trimmed_records.append({
            "text": record["text"],
            "metadata": record["metadata"],
            "vector_dimension": record["vector_dimension"],
            "vector_preview": [round(value, 5) for value in record["vector"][:VECTOR_PREVIEW_LENGTH]],
        })

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(trimmed_records, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from loader import load_corpus
    from cleaner import clean_text
    from metadata import build_corpus_chunk_records

    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ENV_FILE_NAME)
    output_path = os.path.join(script_dir, OUTPUT_FILE_NAME)

    config = get_embedding_config(env_path)
    print("Embedding backend: {} (model: {})".format(config["base_url"], config["model_name"]))
    print()

    corpus_folder = os.path.join(script_dir, "sample_corpus")
    loaded_records = load_corpus(corpus_folder)
    cleaned_records = [
        {"source": record["source"], "cleaned_text": clean_text(record["text"])}
        for record in loaded_records
    ]
    chunk_records = build_corpus_chunk_records(cleaned_records)

    print("Prepared {} chunk(s) from {} document(s).".format(len(chunk_records), len(cleaned_records)))
    print()

    chunk_texts = [record["text"] for record in chunk_records]
    vectors = embed_texts(chunk_texts, config["base_url"], config["api_key"], config["model_name"])
    dimension = confirm_uniform_dimension(vectors)

    embedding_records = build_embedding_records(chunk_records, vectors)

    print_verification(embedding_records, dimension)
    print()

    save_sample_output(embedding_records, output_path)
    print("Sample output written to: {}".format(output_path))
