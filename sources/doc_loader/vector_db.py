"""
Sets up a free, local vector database (chromadb, running in persistent
on-disk mode with no server and no account) and defines the collection
schema used to store chunk embeddings.

Inputs:
    A single prepared chunk record (text plus source metadata: source
    document, chunk index, section), embedded through the same local
    embedding backend used elsewhere in this pipeline. Vector database
    settings -- the on-disk storage path, collection name, and distance
    metric -- are read from environment variables / the ".env" file next
    to this script: VECTOR_DB_PATH, VECTOR_DB_COLLECTION_NAME, and
    VECTOR_DB_DISTANCE_METRIC.

Outputs:
    A persistent chromadb collection on disk (under VECTOR_DB_PATH)
    holding one stored record per chunk, each with an id, an embedding
    vector, the chunk's source text, and its metadata. Printed to
    stdout, and saved to vector_db_report.json next to this script: the
    collection's configuration (name, vector dimension, distance
    metric) and the result of writing one test record and reading it
    back (id, vector length, text, metadata), confirming round-tripping
    works.

Uses chromadb in local persistent mode -- no server, no account, and no
API key are required for the vector database itself. Embedding the test
record still uses the same free, local, OpenAI-compatible backend
(Ollama + nomic-embed-text) as the rest of this pipeline.
"""

import json
import os

import chromadb

from embed_store import embed_texts, get_embedding_config, load_dotenv_file

ENV_FILE_NAME = ".env"
REPORT_FILE_NAME = "vector_db_report.json"
REQUIRED_VECTOR_DB_VARS = ("VECTOR_DB_PATH", "VECTOR_DB_COLLECTION_NAME", "VECTOR_DB_DISTANCE_METRIC")


def get_vector_db_config(env_path):
    """
    Resolve the vector database's storage path, collection name, and
    distance metric.

    Args:
        env_path (str): Path to a .env file to fall back on for any
            variable not already set in the process environment.

    Returns:
        dict[str, str]: A dict with keys "path", "collection_name", and
            "distance_metric".

    Raises:
        RuntimeError: If any of VECTOR_DB_PATH, VECTOR_DB_COLLECTION_NAME,
            or VECTOR_DB_DISTANCE_METRIC is not set in either the
            environment or the .env file.
    """
    dotenv_values = load_dotenv_file(env_path)
    resolved = {}
    missing = []

    for var_name in REQUIRED_VECTOR_DB_VARS:
        value = os.environ.get(var_name) or dotenv_values.get(var_name)
        if not value:
            missing.append(var_name)
        resolved[var_name] = value

    if missing:
        raise RuntimeError(
            "missing required vector database configuration: {} "
            "(set as environment variables or in {})".format(", ".join(missing), env_path)
        )

    return {
        "path": resolved["VECTOR_DB_PATH"],
        "collection_name": resolved["VECTOR_DB_COLLECTION_NAME"],
        "distance_metric": resolved["VECTOR_DB_DISTANCE_METRIC"],
    }


def connect_to_database(storage_path):
    """
    Connect to a local, persistent chromadb database and confirm it is
    reachable.

    Args:
        storage_path (str): Directory on disk where chromadb stores its
            data. Created automatically if it does not already exist.

    Returns:
        chromadb.api.ClientAPI: A connected client, only returned after
            a heartbeat call has confirmed the database responds.

    Raises:
        RuntimeError: If the client cannot be reached (its heartbeat
            call raises).
    """
    client = chromadb.PersistentClient(path=storage_path)
    try:
        client.heartbeat()
    except Exception as error:
        raise RuntimeError("vector database at {} is not reachable: {}".format(storage_path, error))
    return client


def create_or_get_collection(client, collection_name, dimension, distance_metric):
    """
    Create (or reopen) the collection that stores chunk embeddings.

    Args:
        client (chromadb.api.ClientAPI): A connected chromadb client.
        collection_name (str): Name of the collection to create or open.
        dimension (int): Vector dimension the collection is intended to
            store, recorded in the collection's own metadata for
            documentation and for this module's own insert-time checks
            (chromadb infers the dimension from the vectors it receives
            rather than enforcing a declared one).
        distance_metric (str): Distance metric used for similarity
            search, e.g. "cosine", "l2", or "ip".

    Returns:
        chromadb.api.models.Collection.Collection: The collection,
            ready to store records shaped as described in this module's
            docstring.
    """
    return client.get_or_create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": distance_metric,
            "embedding_dimension": dimension,
        },
    )


def validate_vector_dimension(vector, expected_dimension):
    """
    Confirm a vector has the dimension the collection expects.

    Args:
        vector (list[float]): The embedding vector to check.
        expected_dimension (int): The dimension the collection was set
            up to store.

    Returns:
        bool: True if the vector's length matches expected_dimension.

    Raises:
        ValueError: If the vector's length does not match
            expected_dimension.
    """
    if len(vector) != expected_dimension:
        raise ValueError(
            "vector has {} dimensions, collection expects {}".format(len(vector), expected_dimension)
        )
    return True


def build_stored_record(chunk, vector):
    """
    Shape one chunk and its embedding into the collection's record
    schema.

    Args:
        chunk (dict): A chunk record with "text" (str), "chunk_id"
            (str), "source" (str), "chunk_index" (int), "total_chunks"
            (int), "section" (str or None), "start_char" (int), and
            "end_char" (int) keys, such as those produced by
            metadata.build_corpus_chunk_records.
        vector (list[float]): The chunk text's embedding vector.

    Returns:
        dict: A record ready for insert_record, with "id" (str, the
            chunk's chunk_id), "embedding" (list[float]), "text" (str,
            the source text), and "metadata" (dict with "source",
            "chunk_index", "total_chunks", "section", "start_char", and
            "end_char"; chromadb metadata values must be strings,
            numbers, or booleans, so a missing section is stored as the
            empty string rather than None).
    """
    return {
        "id": chunk["chunk_id"],
        "embedding": vector,
        "text": chunk["text"],
        "metadata": {
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "total_chunks": chunk["total_chunks"],
            "section": chunk["section"] or "",
            "start_char": chunk["start_char"],
            "end_char": chunk["end_char"],
        },
    }


def insert_record(collection, record):
    """
    Write one record into the collection (creating or replacing it).

    Args:
        collection (chromadb.api.models.Collection.Collection): The
            target collection.
        record (dict): A record as returned by build_stored_record, with
            "id", "embedding", "text", and "metadata" keys.

    Returns:
        None
    """
    collection.upsert(
        ids=[record["id"]],
        embeddings=[record["embedding"]],
        documents=[record["text"]],
        metadatas=[record["metadata"]],
    )


def read_back_record(collection, record_id):
    """
    Read one record back from the collection by id.

    Args:
        collection (chromadb.api.models.Collection.Collection): The
            collection to read from.
        record_id (str): The id of the record to fetch.

    Returns:
        dict: {"id" (str), "vector_length" (int), "text" (str),
            "metadata" (dict)} for the fetched record.

    Raises:
        KeyError: If no record with record_id exists in the collection.
    """
    result = collection.get(ids=[record_id], include=["embeddings", "documents", "metadatas"])
    if not result["ids"]:
        raise KeyError("no record with id {} found in the collection".format(record_id))

    return {
        "id": result["ids"][0],
        "vector_length": len(result["embeddings"][0]),
        "text": result["documents"][0],
        "metadata": result["metadatas"][0],
    }


def print_collection_config(collection_name, dimension, distance_metric, record_count):
    """
    Print the collection's configuration.

    Args:
        collection_name (str): Name of the collection.
        dimension (int): The collection's vector dimension.
        distance_metric (str): The collection's distance metric.
        record_count (int): Number of records currently stored.

    Returns:
        None
    """
    print("Collection configuration")
    print("  name:            {}".format(collection_name))
    print("  vector dimension: {}".format(dimension))
    print("  distance metric: {}".format(distance_metric))
    print("  records stored:  {}".format(record_count))


def print_readback(readback):
    """
    Print a record read back from the collection.

    Args:
        readback (dict): A record as returned by read_back_record, with
            "id", "vector_length", "text", and "metadata" keys.

    Returns:
        None
    """
    print("Readback result")
    print("  id:            {}".format(readback["id"]))
    print("  vector length: {}".format(readback["vector_length"]))
    print("  text:          {}".format(readback["text"]))
    print("  metadata:")
    for key, value in readback["metadata"].items():
        print("    {}: {}".format(key, value))


def save_report(path, collection_config, readback):
    """
    Save the collection configuration and readback result to disk.

    Args:
        path (str): File path to write the JSON report to.
        collection_config (dict): Collection configuration, with "name",
            "dimension", "distance_metric", and "record_count" keys.
        readback (dict): The readback result, as returned by
            read_back_record.

    Returns:
        None
    """
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"collection": collection_config, "readback": readback}, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from loader import load_corpus
    from cleaner import clean_text
    from metadata import build_corpus_chunk_records

    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ENV_FILE_NAME)
    report_path = os.path.join(script_dir, REPORT_FILE_NAME)

    embedding_config = get_embedding_config(env_path)
    db_config = get_vector_db_config(env_path)
    storage_path = os.path.join(script_dir, db_config["path"])

    print("Connecting to local vector database at: {}".format(storage_path))
    client = connect_to_database(storage_path)
    print("Vector database is reachable (heartbeat responded).")
    print()

    loaded_records = load_corpus(os.path.join(script_dir, "sample_corpus"))
    cleaned_records = [
        {"source": record["source"], "cleaned_text": clean_text(record["text"])}
        for record in loaded_records
    ]
    chunk_records = build_corpus_chunk_records(cleaned_records)
    test_chunk = chunk_records[0]

    print("Embedding test chunk {} through: {} (model: {})".format(
        test_chunk["chunk_id"], embedding_config["base_url"], embedding_config["model_name"]
    ))
    test_vector = embed_texts(
        [test_chunk["text"]], embedding_config["base_url"], embedding_config["api_key"], embedding_config["model_name"]
    )[0]
    dimension = len(test_vector)
    print("Measured embedding dimension: {}".format(dimension))
    print()

    collection = create_or_get_collection(client, db_config["collection_name"], dimension, db_config["distance_metric"])

    stored_record = build_stored_record(test_chunk, test_vector)
    validate_vector_dimension(stored_record["embedding"], dimension)
    insert_record(collection, stored_record)

    readback = read_back_record(collection, stored_record["id"])

    collection_config = {
        "name": db_config["collection_name"],
        "dimension": dimension,
        "distance_metric": db_config["distance_metric"],
        "record_count": collection.count(),
    }

    print_collection_config(
        collection_config["name"], collection_config["dimension"],
        collection_config["distance_metric"], collection_config["record_count"],
    )
    print()
    print_readback(readback)
    print()

    save_report(report_path, collection_config, readback)
    print("Full report written to: {}".format(report_path))
