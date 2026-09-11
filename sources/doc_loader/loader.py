"""
Loads a folder of mixed-format documents into a single plain-text
representation for a retrieval pipeline.

Inputs:
    A folder path containing documents in any mix of the supported
    formats: PDF (.pdf), plain text (.txt), Markdown (.md), and HTML
    (.html/.htm). The folder is walked recursively.

Outputs:
    A list of records, one per successfully loaded document, where each
    record is a dict with:
        "source": the file path the text was extracted from
        "text":   the extracted plain-text string
    Files that are missing, corrupt, or in an unsupported format are
    skipped with a one-line message printed to stdout; they do not stop
    the run or appear in the returned list.

No network calls or API keys are used anywhere in this module.
"""

import os

from pypdf import PdfReader
from bs4 import BeautifulSoup

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".html", ".htm"}


def extract_text(file_path):
    """
    Extract plain text from a single document.

    Args:
        file_path (str): Path to a PDF, TXT, MD, or HTML file.

    Returns:
        str: The extracted plain-text content of the file.

    Raises:
        ValueError: If the file extension is not one of the supported
            formats.
        OSError: If the file does not exist or cannot be read.
        Exception: Any error raised by the underlying PDF or HTML parser
            when the file content is malformed.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        reader = PdfReader(file_path)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text)

    if extension in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8") as handle:
            return handle.read()

    if extension in (".html", ".htm"):
        with open(file_path, "r", encoding="utf-8") as handle:
            raw_html = handle.read()
        soup = BeautifulSoup(raw_html, "html.parser")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        return soup.get_text(separator=" ", strip=True)

    raise ValueError("unsupported file format: {}".format(extension))


def load_corpus(folder_path):
    """
    Walk a folder recursively and load every supported document in it.

    Args:
        folder_path (str): Path to the folder to walk.

    Returns:
        list[dict]: One record per successfully loaded document, each
            with keys "source" (str, the file path) and "text"
            (str, the extracted plain text). Files that are missing,
            corrupt, or unsupported are skipped and excluded from this
            list; a one-line message is printed for each skip.
    """
    records = []

    for current_dir, _subdirs, filenames in os.walk(folder_path):
        for filename in sorted(filenames):
            file_path = os.path.join(current_dir, filename)
            try:
                text = extract_text(file_path)
            except Exception as error:
                print("Skipped {}: {}".format(file_path, error))
                continue
            records.append({"source": file_path, "text": text})

    return records


def print_summary(records):
    """
    Print the character length and a short text sample for each record.

    Args:
        records (list[dict]): Records as returned by load_corpus, each
            with "source" and "text" keys.

    Returns:
        None
    """
    sample_length = 150
    for record in records:
        source = record["source"]
        text = record["text"]
        collapsed = " ".join(text.split())
        sample = collapsed[:sample_length]
        if len(collapsed) > sample_length:
            sample += "..."
        print("{} | {} chars | sample: {}".format(source, len(text), sample))


if __name__ == "__main__":
    corpus_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")
    loaded_records = load_corpus(corpus_folder)
    print()
    print("Loaded {} document(s):".format(len(loaded_records)))
    print_summary(loaded_records)
