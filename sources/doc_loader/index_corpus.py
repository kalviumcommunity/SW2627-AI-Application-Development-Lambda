"""
Indexes every chunk embedding produced for the corpus into the local
chromadb collection, then verifies what was stored.

Inputs:
    The sample corpus folder next to this script, run through the
    existing pipeline (loader, cleaner, metadata) to produce the full
    list of chunks. Embeddings come from the persistent embedding store
    maintained by batch_embed.py (embedding_store.json); any chunk not
    yet embedded is embedded first through the same free, local backend
    (Ollama + nomic-embed-text). Settings come from environment
    variables or the ".env" file next to this script: the EMBEDDING_*
    variables for the backend and the VECTOR_DB_* variables for the
    collection.

Outputs:
    Every chunk written to the chromadb collection as one record holding
    its embedding vector, source text, and metadata (source document,
    chunk index, total chunks, section, character offsets). Printed to
    stdout and saved to index_report.json next to this script: an
    indexing summary with records stored, the result of comparing the
    collection's record count and ids against the pipeline's chunks,
    any failures encountered, and spot-check results comparing records
    read back from the collection against their original chunks.

No paid database, paid API, or API key is used; chromadb runs in local
persistent mode and the embedding backend is local.
"""

import json
import os

import numpy as np

from batch_embed import (
    STORE_FILE_NAME,
    chunk_key,
    get_run_settings,
    load_store,
    run_batch_embedding,
    text_fingerprint,
)
from embed_store import embed_texts, get_embedding_config
from vector_db import (
    build_stored_record,
    connect_to_database,
    create_or_get_collection,
    get_vector_db_config,
    validate_vector_dimension,
)

ENV_FILE_NAME = ".env"
REPORT_FILE_NAME = "index_report.json"
UPSERT_BATCH_SIZE = 50
SPOT_CHECK_COUNT = 2


def build_corpus_chunks(corpus_folder):
    """
    Run the load, clean, and chunk steps over every file in a folder.

    Args:
        corpus_folder (str): Path to the corpus folder.

    Returns:
        list[dict]: Every chunk produced for the corpus, each with
            "chunk_id", "source", "chunk_index", "total_chunks",
            "section", "start_char", "end_char", and "text" keys.
    """
    from loader import load_corpus
    from cleaner import clean_text
    from metadata import build_corpus_chunk_records

    loaded_records = load_corpus(corpus_folder)
    cleaned_records = [
        {"source": record["source"], "cleaned_text": clean_text(record["text"])}
        for record in loaded_records
    ]
    return build_corpus_chunk_records(cleaned_records)


def collect_records_to_index(chunks, store, model_name, dimension):
    """
    Pair every chunk with its stored embedding, noting any that cannot
    be indexed.

    Args:
        chunks (list[dict]): Chunk records as returned by
            build_corpus_chunks.
        store (dict): The loaded embedding store from batch_embed.py.
        model_name (str): The embedding model in use. A stored vector
            only counts if it came from this model and from identical
            chunk text.
        dimension (int): The vector dimension the collection expects.

    Returns:
        tuple[list[dict], list[dict]]: (records, failures). records are
            shaped by vector_db.build_stored_record; failures each have
            "chunk_id" (str) and "reason" (str).
    """
    records = []
    failures = []
    for chunk in chunks:
        stored = store.get(chunk_key(chunk))
        if stored is None:
            failures.append({"chunk_id": chunk["chunk_id"], "reason": "no stored embedding"})
            continue
        if stored.get("model") != model_name or stored.get("text_hash") != text_fingerprint(chunk["text"]):
            failures.append({"chunk_id": chunk["chunk_id"], "reason": "stored embedding is stale (model or text changed)"})
            continue
        try:
            validate_vector_dimension(stored["vector"], dimension)
        except ValueError as error:
            failures.append({"chunk_id": chunk["chunk_id"], "reason": str(error)})
            continue
        records.append(build_stored_record(chunk, stored["vector"]))
    return records, failures


def upsert_in_batches(collection, records, batch_size):
    """
    Write records into the collection in batches.

    Args:
        collection (chromadb.api.models.Collection.Collection): The
            target collection.
        records (list[dict]): Records shaped by
            vector_db.build_stored_record.
        batch_size (int): Maximum records per write.

    Returns:
        tuple[int, list[dict]]: (records_written, failures). A batch
            that raises is recorded as one failure per record in it,
            each with "chunk_id" (str) and "reason" (str), and the
            remaining batches still run.
    """
    written = 0
    failures = []
    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]
        try:
            collection.upsert(
                ids=[record["id"] for record in batch],
                embeddings=[record["embedding"] for record in batch],
                documents=[record["text"] for record in batch],
                metadatas=[record["metadata"] for record in batch],
            )
        except Exception as error:
            failures.extend({"chunk_id": record["id"], "reason": "write failed: {}".format(error)} for record in batch)
            continue
        written += len(batch)
    return written, failures


def validate_counts(collection, chunks):
    """
    Compare the collection's contents against the pipeline's chunks.

    Args:
        collection (chromadb.api.models.Collection.Collection): The
            collection to check.
        chunks (list[dict]): Chunk records as returned by
            build_corpus_chunks.

    Returns:
        dict: "collection_count" (int), "chunk_count" (int),
            "counts_match" (bool), "missing_ids" (list[str], chunk ids
            with no record in the collection), "extra_ids" (list[str],
            record ids that match no current chunk), and "ids_match"
            (bool, True when both lists are empty).
    """
    stored_ids = set(collection.get(include=[])["ids"])
    chunk_ids = {chunk["chunk_id"] for chunk in chunks}
    missing_ids = sorted(chunk_ids - stored_ids)
    extra_ids = sorted(stored_ids - chunk_ids)
    collection_count = collection.count()
    return {
        "collection_count": collection_count,
        "chunk_count": len(chunks),
        "counts_match": collection_count == len(chunks),
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "ids_match": not missing_ids and not extra_ids,
    }


def pick_spot_check_chunks(chunks, count):
    """
    Choose chunks to read back, spread across different documents.

    Args:
        chunks (list[dict]): Chunk records as returned by
            build_corpus_chunks.
        count (int): Number of chunks to pick.

    Returns:
        list[dict]: Up to count chunks: a middle chunk of the document
            with the most chunks, then the first chunk of other
            documents in corpus order.
    """
    by_source = {}
    for chunk in chunks:
        by_source.setdefault(chunk["source"], []).append(chunk)

    ordered_sources = sorted(by_source, key=lambda source: len(by_source[source]), reverse=True)
    largest = by_source[ordered_sources[0]]
    picks = [largest[len(largest) // 2]]
    for source in ordered_sources[1:]:
        if len(picks) >= count:
            break
        picks.append(by_source[source][0])
    return picks[:count]


def spot_check_record(collection, chunk, expected_vector):
    """
    Read one record back and compare it with its original chunk.

    Args:
        collection (chromadb.api.models.Collection.Collection): The
            collection to read from.
        chunk (dict): The original chunk record.
        expected_vector (list[float]): The embedding that was indexed
            for this chunk.

    Returns:
        dict: "chunk_id" (str), "found" (bool), and when found:
            "id_match", "text_match", "metadata_match",
            "vector_length_match", "vector_values_match" (all bool),
            "vector_length" (int), "stored_metadata" (dict),
            "mismatched_metadata_fields" (list[str]), and "passed"
            (bool, True only when every check matches). chromadb stores
            vectors as 32-bit floats, so values are compared with a
            small tolerance rather than exact equality.
    """
    result = collection.get(ids=[chunk["chunk_id"]], include=["embeddings", "documents", "metadatas"])
    if not result["ids"]:
        return {"chunk_id": chunk["chunk_id"], "found": False, "passed": False}

    expected = build_stored_record(chunk, expected_vector)
    stored_vector = result["embeddings"][0]
    stored_metadata = result["metadatas"][0]
    mismatched_fields = sorted(
        key for key in set(expected["metadata"]) | set(stored_metadata)
        if expected["metadata"].get(key) != stored_metadata.get(key)
    )

    checks = {
        "id_match": result["ids"][0] == expected["id"],
        "text_match": result["documents"][0] == expected["text"],
        "metadata_match": not mismatched_fields,
        "vector_length_match": len(stored_vector) == len(expected_vector),
    }
    checks["vector_values_match"] = checks["vector_length_match"] and bool(
        np.allclose(stored_vector, expected_vector, atol=1e-6)
    )

    return {
        "chunk_id": chunk["chunk_id"],
        "found": True,
        **checks,
        "vector_length": len(stored_vector),
        "stored_metadata": stored_metadata,
        "mismatched_metadata_fields": mismatched_fields,
        "passed": all(checks.values()),
    }


def print_indexing_summary(summary):
    """
    Print the indexing summary.

    Args:
        summary (dict): The summary assembled in run_indexing, with
            "collection", "records_stored", "count_validation",
            "failures", and "spot_checks" keys.

    Returns:
        None
    """
    collection = summary["collection"]
    validation = summary["count_validation"]

    print()
    print("Indexing summary")
    print("  collection:        {} ({}-dim, {})".format(
        collection["name"], collection["dimension"], collection["distance_metric"]
    ))
    print("  chunks in corpus:  {}".format(validation["chunk_count"]))
    print("  records written:   {}".format(summary["records_stored"]))
    print("  records in collection: {}".format(validation["collection_count"]))
    print("  count validation:  {} records vs {} chunks -> {}".format(
        validation["collection_count"], validation["chunk_count"],
        "MATCH" if validation["counts_match"] else "MISMATCH"
    ))
    print("  id validation:     {}".format(
        "every chunk id present, no extras" if validation["ids_match"]
        else "missing {}, extra {}".format(validation["missing_ids"], validation["extra_ids"])
    ))
    print("  failures:          {}".format(len(summary["failures"])))
    for failure in summary["failures"]:
        print("    {} -- {}".format(failure["chunk_id"], failure["reason"]))

    print()
    print("Spot checks (read back from the collection vs. original chunk)")
    for check in summary["spot_checks"]:
        if not check["found"]:
            print("  {}: NOT FOUND in collection".format(check["chunk_id"]))
            continue
        print("  {}: {}".format(check["chunk_id"], "PASS" if check["passed"] else "FAIL"))
        print("    id matches:            {}".format(check["id_match"]))
        print("    text matches exactly:  {}".format(check["text_match"]))
        print("    metadata matches:      {}".format(check["metadata_match"]))
        print("    vector length:         {} (matches: {})".format(check["vector_length"], check["vector_length_match"]))
        print("    vector values match:   {}".format(check["vector_values_match"]))
        if check["mismatched_metadata_fields"]:
            print("    mismatched fields:     {}".format(check["mismatched_metadata_fields"]))
        print("    stored metadata:       {}".format(check["stored_metadata"]))


def run_indexing(script_dir):
    """
    Embed any missing chunks, index the whole corpus, and verify it.

    Args:
        script_dir (str): Directory holding the corpus folder, .env
            file, embedding store, and chromadb storage.

    Returns:
        dict: The indexing summary, with "collection" (dict: "name",
            "dimension", "distance_metric"), "records_stored" (int),
            "count_validation" (dict, as returned by validate_counts),
            "failures" (list[dict]), and "spot_checks" (list[dict], as
            returned by spot_check_record).
    """
    env_path = os.path.join(script_dir, ENV_FILE_NAME)
    store_path = os.path.join(script_dir, STORE_FILE_NAME)
    embedding_config = get_embedding_config(env_path)
    db_config = get_vector_db_config(env_path)
    run_settings = get_run_settings(env_path)

    chunks = build_corpus_chunks(os.path.join(script_dir, "sample_corpus"))
    print()
    print("Pipeline produced {} chunk(s).".format(len(chunks)))
    print("Making sure every chunk has a stored embedding (already-embedded chunks are skipped):")

    def embed_fn(texts):
        """
        Embed a batch through the configured backend.

        Args:
            texts (list[str]): The texts to embed.

        Returns:
            list[list[float]]: One vector per text.
        """
        return embed_texts(texts, embedding_config["base_url"], embedding_config["api_key"], embedding_config["model_name"])

    embed_summary = run_batch_embedding(
        chunks, embed_fn, embedding_config["model_name"], store_path,
        run_settings["batch_size"], run_settings["cost_per_1k_tokens"],
    )
    print("  embedded now: {}, already stored: {}, failed: {}".format(
        embed_summary["embedded"], embed_summary["skipped"], embed_summary["failed_chunks"]
    ))

    store = load_store(store_path)
    dimension = embed_summary["vector_length"]
    if dimension is None:
        raise RuntimeError("no embeddings are available to index")

    client = connect_to_database(os.path.join(script_dir, db_config["path"]))
    collection = create_or_get_collection(client, db_config["collection_name"], dimension, db_config["distance_metric"])

    records, failures = collect_records_to_index(chunks, store, embedding_config["model_name"], dimension)
    records_stored, write_failures = upsert_in_batches(collection, records, UPSERT_BATCH_SIZE)
    failures.extend(write_failures)

    spot_checks = [
        spot_check_record(collection, chunk, store[chunk_key(chunk)]["vector"])
        for chunk in pick_spot_check_chunks(chunks, SPOT_CHECK_COUNT)
        if chunk_key(chunk) in store
    ]

    return {
        "collection": {
            "name": db_config["collection_name"],
            "dimension": dimension,
            "distance_metric": db_config["distance_metric"],
        },
        "records_stored": records_stored,
        "count_validation": validate_counts(collection, chunks),
        "failures": failures,
        "spot_checks": spot_checks,
    }


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    indexing_summary = run_indexing(here)
    print_indexing_summary(indexing_summary)

    report_path = os.path.join(here, REPORT_FILE_NAME)
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(indexing_summary, handle, indent=2, ensure_ascii=False)
    print()
    print("Full report written to: {}".format(report_path))
