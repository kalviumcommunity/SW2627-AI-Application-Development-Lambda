"""
Runs the full ingestion pipeline (load, clean, chunk, tag metadata) end
to end over every file in a sample corpus folder, and validates that
nothing was silently lost along the way.

Inputs:
    A folder path containing the corpus to ingest (defaults to the
    sample_corpus folder next to this file). No other input is needed;
    the whole run is driven by this one folder.

Outputs:
    Printed to stdout:
        - An ingestion summary: total source documents found, documents
          successfully ingested, total chunks created, and every file
          that failed or was skipped, with its reason.
        - A reconciliation check confirming that
          (ingested documents + failed documents) equals the total
          number of source documents found, with a visible warning if
          it does not.
        - A sample of chunks (first and last chunk of each ingested
          document) printed with their full metadata, for manual
          inspection of text quality, boundaries, source identifier,
          and position.
    Also written to disk: a JSON report at ingestion_report.json (next
    to this file) capturing the same summary and sample chunks, so a run
    can be inspected or diffed after the fact.

Running `python pipeline.py` with no arguments reproduces the entire run
from a single command. No network calls or API keys are used anywhere in
this module.
"""

import json
import os
import warnings

from loader import extract_text
from cleaner import clean_text
from metadata import build_corpus_chunk_records, verify_consistent_fields

SAMPLE_CORPUS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")
REPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingestion_report.json")


def discover_files(folder_path):
    """
    List every file in a folder, walked recursively.

    Args:
        folder_path (str): Path to the folder to walk.

    Returns:
        list[str]: Every file path found under folder_path, in a stable
            sorted order.
    """
    found = []
    for current_dir, _subdirs, filenames in os.walk(folder_path):
        for filename in filenames:
            found.append(os.path.join(current_dir, filename))
    return sorted(found)


def ingest_corpus(folder_path):
    """
    Load every file in a folder, separating successes from failures.

    Args:
        folder_path (str): Path to the folder to walk.

    Returns:
        tuple[list[dict], list[dict]]: (ingested_records, failures).
            ingested_records has one entry per successfully loaded file,
            each with "source" (str, file path) and "text" (str, raw
            extracted text). failures has one entry per file that could
            not be loaded, each with "source" (str, file path) and
            "reason" (str, the error message). Every file discovered
            under folder_path appears in exactly one of the two lists.
    """
    ingested_records = []
    failures = []

    for file_path in discover_files(folder_path):
        try:
            text = extract_text(file_path)
        except Exception as error:
            failures.append({"source": file_path, "reason": str(error)})
            continue
        ingested_records.append({"source": file_path, "text": text})

    return ingested_records, failures


def clean_ingested_records(ingested_records):
    """
    Apply text cleaning to every successfully ingested document.

    Args:
        ingested_records (list[dict]): Records as returned by
            ingest_corpus, each with "source" (str) and "text" (str).

    Returns:
        list[dict]: One record per input record, each with "source"
            (str, unchanged) and "cleaned_text" (str, the result of
            cleaner.clean_text on that document's raw text).
    """
    return [
        {"source": record["source"], "cleaned_text": clean_text(record["text"])}
        for record in ingested_records
    ]


def reconcile_counts(total_found, ingested_count, failure_count):
    """
    Confirm that every discovered file was accounted for exactly once.

    Args:
        total_found (int): Number of source files discovered in the
            corpus folder.
        ingested_count (int): Number of files successfully ingested.
        failure_count (int): Number of files that failed or were
            skipped.

    Returns:
        bool: True if total_found equals ingested_count + failure_count,
            False otherwise. When False, a warning is both raised
            (via the warnings module) and printed prominently, but the
            run is allowed to continue so the mismatch is visible in the
            output rather than hidden by a crash.
    """
    accounted_for = ingested_count + failure_count
    if accounted_for == total_found:
        return True

    message = (
        "reconciliation mismatch: {} source document(s) found, but only "
        "{} were accounted for ({} ingested + {} failed)".format(
            total_found, accounted_for, ingested_count, failure_count
        )
    )
    warnings.warn(message)
    print("WARNING: {}".format(message))
    return False


def print_ingestion_summary(total_found, ingested_records, failures, total_chunks):
    """
    Print a clear summary of one ingestion run.

    Args:
        total_found (int): Number of source files discovered.
        ingested_records (list[dict]): Successfully ingested records, as
            returned by ingest_corpus.
        failures (list[dict]): Failed/skipped records, as returned by
            ingest_corpus, each with "source" and "reason".
        total_chunks (int): Total number of chunks produced across every
            ingested document.

    Returns:
        None
    """
    print("Ingestion summary")
    print("  source documents found:        {}".format(total_found))
    print("  documents successfully ingested: {}".format(len(ingested_records)))
    print("  documents failed or skipped:   {}".format(len(failures)))
    print("  total chunks created:          {}".format(total_chunks))
    if failures:
        print("  failed/skipped files:")
        for failure in failures:
            print("    {} -- {}".format(failure["source"], failure["reason"]))


def select_inspection_sample(chunk_records):
    """
    Pick the first and last chunk of every document for manual review.

    Args:
        chunk_records (list[dict]): Chunk records as returned by
            metadata.build_corpus_chunk_records.

    Returns:
        list[dict]: A subset of chunk_records containing, for each
            distinct source document (in first-seen order), its
            chunk_index 0 record and, if that document produced more
            than one chunk, its final chunk record as well.
    """
    by_source = {}
    for record in chunk_records:
        by_source.setdefault(record["source"], []).append(record)

    sample = []
    for source_records in by_source.values():
        source_records.sort(key=lambda record: record["chunk_index"])
        sample.append(source_records[0])
        if len(source_records) > 1:
            sample.append(source_records[-1])

    return sample


def print_inspection_sample(sample_records):
    """
    Print chunk text and full metadata for a sample of chunks.

    Args:
        sample_records (list[dict]): Chunk records to print, as returned
            by select_inspection_sample.

    Returns:
        None
    """
    for record in sample_records:
        preview = " ".join(record["text"].split())
        if len(preview) > 160:
            preview = preview[:160] + "..."
        position = "first" if record["chunk_index"] == 0 else "last"
        print("[{} chunk] {}".format(position, record["chunk_id"]))
        print("  text: {}".format(preview))
        print("  source:      {}".format(record["source"]))
        print("  chunk_index: {} of {}".format(record["chunk_index"], record["total_chunks"]))
        print("  section:     {}".format(record["section"]))
        print("  char range:  [{}:{}]".format(record["start_char"], record["end_char"]))
        print()


def save_report(path, total_found, ingested_records, failures, chunk_records, sample_records, reconciled):
    """
    Save the ingestion summary and a chunk sample to a JSON file.

    Args:
        path (str): File path to write the report to.
        total_found (int): Number of source files discovered.
        ingested_records (list[dict]): Successfully ingested records.
        failures (list[dict]): Failed/skipped records, each with
            "source" and "reason".
        chunk_records (list[dict]): Every chunk produced across the
            corpus.
        sample_records (list[dict]): The chunk sample selected for
            manual inspection, as returned by select_inspection_sample.
        reconciled (bool): Result of reconcile_counts for this run.

    Returns:
        None
    """
    report = {
        "source_documents_found": total_found,
        "documents_ingested": len(ingested_records),
        "documents_failed": len(failures),
        "failures": failures,
        "total_chunks": len(chunk_records),
        "reconciled": reconciled,
        "sample_chunks": sample_records,
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)


def run_pipeline(folder_path):
    """
    Run the full load-clean-chunk-tag pipeline over one corpus folder.

    Args:
        folder_path (str): Path to the corpus folder to ingest.

    Returns:
        dict: A summary with keys "total_found" (int), "ingested_count"
            (int), "failure_count" (int), "total_chunks" (int), and
            "reconciled" (bool), describing the outcome of the run.
    """
    total_found = len(discover_files(folder_path))
    ingested_records, failures = ingest_corpus(folder_path)

    cleaned_records = clean_ingested_records(ingested_records)
    chunk_records = build_corpus_chunk_records(cleaned_records)
    if chunk_records:
        verify_consistent_fields(chunk_records)

    print()
    print_ingestion_summary(total_found, ingested_records, failures, len(chunk_records))
    print()

    reconciled = reconcile_counts(total_found, len(ingested_records), len(failures))
    print("Reconciliation check: {} == {} ingested + {} failed -> {}".format(
        total_found, len(ingested_records), len(failures), "OK" if reconciled else "MISMATCH"
    ))
    print()

    sample_records = select_inspection_sample(chunk_records)
    print("Sample chunks for manual inspection ({} of {} total chunks):".format(
        len(sample_records), len(chunk_records)
    ))
    print()
    print_inspection_sample(sample_records)

    save_report(REPORT_PATH, total_found, ingested_records, failures, chunk_records, sample_records, reconciled)
    print("Full report written to: {}".format(REPORT_PATH))

    return {
        "total_found": total_found,
        "ingested_count": len(ingested_records),
        "failure_count": len(failures),
        "total_chunks": len(chunk_records),
        "reconciled": reconciled,
    }


if __name__ == "__main__":
    run_pipeline(SAMPLE_CORPUS_FOLDER)
