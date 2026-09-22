"""
Sanity-checks embedding quality using a small set of query-chunk pairs
with a known correct answer, run against the corpus's stored embeddings.

Inputs:
    The persistent embedding store built by batch_embed.py
    (embedding_store.json, next to this script), plus a fixed list of
    test cases defined in this file. Each test case pairs a natural
    -language query with the specific chunk already known to be the
    relevant answer, and a small set of chunks known to be on an
    unrelated topic. Backend settings (used only to embed the queries)
    come from the same environment variables / .env file as the rest of
    the pipeline: EMBEDDING_BASE_URL, EMBEDDING_API_KEY, EMBEDDING_MODEL.

Outputs:
    Printed to stdout and saved to sanity_report.json (next to this
    script): a sanity report with the number of tests run, number
    passed, number failed, and, per test, the top-ranked source chunk
    and its similarity score, whether the known-relevant chunk still
    beat the unrelated baseline, and a short note -- including at least
    one case where the known-relevant chunk was not the top match,
    with an explanation of what that revealed about the chunking
    pipeline.

Reuses the same free, local embedding backend as the rest of this
pipeline (Ollama + nomic-embed-text, OpenAI-compatible). No paid API key
is used or required.
"""

import json
import os

import numpy as np

from batch_embed import ENV_FILE_NAME, STORE_FILE_NAME, load_store
from embed_store import embed_texts, get_embedding_config
from embeddings import cosine_similarity

REPORT_FILE_NAME = "sanity_report.json"

# Each test case pairs a query with the chunk_id already known to be the
# relevant answer, plus a couple of chunk_ids known to be on a clearly
# different topic, used to confirm the relevant chunk still outranks
# unrelated material. "note" is filled in only for cases worth a written
# explanation; run_test_case fills in the rest from live results.
TEST_CASES = [
    {
        "query": "What Python libraries are used to extract text from PDF and HTML documents?",
        "expected_chunk_id": "long_report.txt#1",
        "unrelated_chunk_ids": ["readme.md#0", "report.pdf#0"],
        "note": None,
    },
    {
        "query": "How does the pipeline remove repeated page headers and footers from documents?",
        "expected_chunk_id": "long_report.txt#2",
        "unrelated_chunk_ids": ["readme.md#0", "report.pdf#0"],
        "note": None,
    },
    {
        "query": "What is the downside of cutting text into fixed-size chunks?",
        "expected_chunk_id": "long_report.txt#7",
        "unrelated_chunk_ids": ["readme.md#0", "report.pdf#0"],
        "note": (
            "Chunk #7 opens with the bare pronoun \"Its\" and never restates "
            "\"fixed-size chunking\" -- the paragraph-based chunker split that "
            "phrase into the previous chunk (#6). Without the subject noun "
            "phrase in its own text, chunk #7's embedding has a weaker pull "
            "toward this query than chunks that do mention \"fixed-size\" "
            "explicitly, even though chunk #6 only describes the benefit, not "
            "the downside asked about. This shows sentence-level splitting can "
            "strand a pronoun-led sentence away from the topic it depends on."
        ),
    },
    {
        "query": "What is the downside of chunking text by paragraph?",
        "expected_chunk_id": "long_report.txt#9",
        "unrelated_chunk_ids": ["readme.md#0", "report.pdf#0"],
        "note": (
            "Same pattern as the fixed-size case: chunk #9 also opens with "
            "\"Its weakness is...\" with no restated subject, so it is "
            "outranked by sibling chunks #8 and #11 that name \"paragraph-based "
            "chunking\" or \"fixed-size chunking\" directly."
        ),
    },
    {
        "query": "What file formats are included in the sample corpus?",
        "expected_chunk_id": "readme.md#0",
        "unrelated_chunk_ids": ["long_report.txt#6", "report.pdf#0"],
        "note": None,
    },
    {
        "query": "What does the PDF report say about ingestion coverage?",
        "expected_chunk_id": "report.pdf#0",
        "unrelated_chunk_ids": ["long_report.txt#6", "readme.md#0"],
        "note": None,
    },
    {
        "query": "Why is paragraph-based chunking recommended for a real corpus of prose documents?",
        "expected_chunk_id": "long_report.txt#10",
        "unrelated_chunk_ids": ["readme.md#0", "report.pdf#0"],
        "note": None,
    },
]


def index_store_by_chunk_id(store):
    """
    Build a lookup from short chunk id to its stored record's key.

    Args:
        store (dict): The loaded embedding store, mapping storage key to
            a record with a "metadata" dict containing "chunk_id".

    Returns:
        dict[str, str]: Mapping of chunk_id (e.g. "long_report.txt#1")
            to the store's own key for that record.
    """
    return {record["metadata"]["chunk_id"]: key for key, record in store.items()}


def embed_query(query, config):
    """
    Embed a single query string through the embedding backend.

    Args:
        query (str): The natural-language query to embed.
        config (dict): Backend settings with "base_url", "api_key", and
            "model_name" keys, as returned by get_embedding_config.

    Returns:
        numpy.ndarray: The query's embedding vector.
    """
    vector = embed_texts([query], config["base_url"], config["api_key"], config["model_name"])[0]
    return np.array(vector)


def rank_chunks(query_vector, store):
    """
    Rank every stored chunk by cosine similarity to a query vector.

    Args:
        query_vector (numpy.ndarray): The query's embedding vector.
        store (dict): The loaded embedding store, mapping storage key to
            a record with "vector" and "metadata" (containing
            "chunk_id").

    Returns:
        list[dict]: One entry per stored chunk, sorted by descending
            similarity, each with "chunk_id" (str), "score" (float),
            and "source" (str, the chunk's source document path).
    """
    ranked = []
    for record in store.values():
        score = cosine_similarity(query_vector, np.array(record["vector"]))
        ranked.append({
            "chunk_id": record["metadata"]["chunk_id"],
            "score": float(score),
            "source": record["metadata"]["source"],
        })
    ranked.sort(key=lambda entry: entry["score"], reverse=True)
    return ranked


def run_test_case(test_case, store, config):
    """
    Run one query-chunk sanity test against the stored embeddings.

    Args:
        test_case (dict): A test case with "query" (str),
            "expected_chunk_id" (str), "unrelated_chunk_ids"
            (list[str]), and "note" (str or None).
        store (dict): The loaded embedding store.
        config (dict): Backend settings, as returned by
            get_embedding_config.

    Returns:
        dict: The test result, with "query", "expected_chunk_id",
            "expected_rank" (int, 1-based position of the expected
            chunk in the ranking), "expected_score" (float),
            "top_chunk_id" (str, the highest-ranked chunk overall),
            "top_score" (float), "unrelated_max_score" (float, the
            highest score among the test's unrelated chunks),
            "beats_unrelated" (bool, whether the expected chunk outranks
            every unrelated chunk), "passed" (bool, whether the expected
            chunk was the single top match), and "note" (str or None).
    """
    query_vector = embed_query(test_case["query"], config)
    ranking = rank_chunks(query_vector, store)

    scores_by_id = {entry["chunk_id"]: entry["score"] for entry in ranking}
    positions_by_id = {entry["chunk_id"]: position for position, entry in enumerate(ranking, start=1)}

    expected_id = test_case["expected_chunk_id"]
    expected_score = scores_by_id[expected_id]
    expected_rank = positions_by_id[expected_id]

    unrelated_max_score = max(scores_by_id[uid] for uid in test_case["unrelated_chunk_ids"])

    top_entry = ranking[0]

    return {
        "query": test_case["query"],
        "expected_chunk_id": expected_id,
        "expected_rank": expected_rank,
        "expected_score": expected_score,
        "top_chunk_id": top_entry["chunk_id"],
        "top_score": top_entry["score"],
        "unrelated_max_score": unrelated_max_score,
        "beats_unrelated": expected_score > unrelated_max_score,
        "passed": expected_rank == 1,
        "note": test_case["note"],
    }


def run_sanity_suite(test_cases, store, config):
    """
    Run every test case in a sanity suite.

    Args:
        test_cases (list[dict]): Test cases as defined in TEST_CASES.
        store (dict): The loaded embedding store.
        config (dict): Backend settings, as returned by
            get_embedding_config.

    Returns:
        list[dict]: One result per test case, in order, as returned by
            run_test_case.
    """
    return [run_test_case(test_case, store, config) for test_case in test_cases]


def summarize_results(results):
    """
    Summarize pass/fail counts across a sanity suite's results.

    Args:
        results (list[dict]): Test results as returned by
            run_sanity_suite, each with a "passed" key.

    Returns:
        dict: {"total" (int), "passed" (int), "failed" (int)}.
    """
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    return {"total": total, "passed": passed, "failed": total - passed}


def print_sanity_report(results, summary):
    """
    Print the full sanity report.

    Args:
        results (list[dict]): Test results as returned by
            run_sanity_suite.
        summary (dict): Pass/fail totals, as returned by
            summarize_results.

    Returns:
        None
    """
    print("Sanity report")
    print("  tests run:    {}".format(summary["total"]))
    print("  passed:       {}".format(summary["passed"]))
    print("  failed:       {}".format(summary["failed"]))
    print()

    for number, result in enumerate(results, start=1):
        status = "PASS" if result["passed"] else "FAIL"
        print("[{}] {} -- {}".format(number, status, result["query"]))
        print("    expected chunk: {} (rank {}, score {:.4f})".format(
            result["expected_chunk_id"], result["expected_rank"], result["expected_score"]
        ))
        print("    top-ranked source: {} (score {:.4f})".format(result["top_chunk_id"], result["top_score"]))
        print("    beats unrelated baseline (max {:.4f}): {}".format(
            result["unrelated_max_score"], result["beats_unrelated"]
        ))
        if result["note"]:
            print("    note: {}".format(result["note"]))
        print()


def save_sanity_report(results, summary, path):
    """
    Save the sanity report to a JSON file.

    Args:
        results (list[dict]): Test results as returned by
            run_sanity_suite.
        summary (dict): Pass/fail totals, as returned by
            summarize_results.
        path (str): File path to write the JSON report to.

    Returns:
        None
    """
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"summary": summary, "results": results}, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ENV_FILE_NAME)
    store_path = os.path.join(script_dir, STORE_FILE_NAME)
    report_path = os.path.join(script_dir, REPORT_FILE_NAME)

    config = get_embedding_config(env_path)
    store = load_store(store_path)
    if not store:
        raise RuntimeError(
            "no embeddings found in {} -- run batch_embed.py first".format(store_path)
        )

    chunk_id_lookup = index_store_by_chunk_id(store)
    missing_ids = sorted({
        chunk_id
        for test_case in TEST_CASES
        for chunk_id in [test_case["expected_chunk_id"]] + test_case["unrelated_chunk_ids"]
        if chunk_id not in chunk_id_lookup
    })
    if missing_ids:
        raise RuntimeError("test cases reference chunk_ids not found in the store: {}".format(missing_ids))

    print("Embedding backend: {} (model: {})".format(config["base_url"], config["model_name"]))
    print("Store: {} chunk(s) loaded from {}".format(len(store), store_path))
    print()

    results = run_sanity_suite(TEST_CASES, store, config)
    summary = summarize_results(results)

    print_sanity_report(results, summary)
    save_sanity_report(results, summary, report_path)
    print("Full sanity report written to: {}".format(report_path))
