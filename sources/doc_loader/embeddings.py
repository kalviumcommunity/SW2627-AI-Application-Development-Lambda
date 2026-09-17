"""
Demonstrates what text embeddings are by generating them locally with
sentence-transformers and comparing them for meaning.

Inputs:
    A small, fixed set of short sample texts defined in this file,
    including at least one pair with closely related meaning and one
    text that is clearly unrelated to the others. No external input is
    required.

Outputs:
    Printed to stdout: every sample text, the vector dimension of each
    generated embedding (with confirmation that all dimensions match),
    the cosine similarity score for a similar pair and for a dissimilar
    pair, a full pairwise similarity table across all sample texts, and
    a short explanation of what the numbers represent.

Uses the local, offline sentence-transformers library (model
all-MiniLM-L6-v2). The model weights are fetched once on first use and
cached locally by the library; no API key and no per-run network call is
needed. No other network calls are made by this module.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

SAMPLE_TEXTS = [
    "The cat sat quietly on the warm windowsill.",
    "A cat was resting peacefully by the sunny window.",
    "The stock market rallied sharply after the interest rate announcement.",
    "Retrieval systems convert documents into vector embeddings for search.",
    "Embeddings let a search engine compare meaning instead of exact words.",
]

SIMILAR_PAIR = (0, 1)
DISSIMILAR_PAIR = (0, 2)


def load_model(model_name=MODEL_NAME):
    """
    Load a local sentence-transformers model.

    Args:
        model_name (str): Name of the sentence-transformers model to
            load, e.g. "all-MiniLM-L6-v2".

    Returns:
        sentence_transformers.SentenceTransformer: The loaded model,
            ready to encode text into embedding vectors.
    """
    return SentenceTransformer(model_name)


def generate_embeddings(model, texts):
    """
    Encode a list of texts into embedding vectors.

    Args:
        model (sentence_transformers.SentenceTransformer): A loaded
            sentence-transformers model.
        texts (list[str]): The texts to embed.

    Returns:
        numpy.ndarray: A 2D array of shape (len(texts), vector_dimension)
            where row i is the embedding for texts[i].
    """
    return model.encode(texts)


def check_uniform_dimension(embeddings):
    """
    Confirm every embedding in a set has the same vector dimension.

    Args:
        embeddings (numpy.ndarray): A 2D array of embeddings, one row
            per text.

    Returns:
        int: The shared vector dimension.

    Raises:
        AssertionError: If any row's length differs from the first row's
            length.
    """
    dimensions = [len(vector) for vector in embeddings]
    first_dimension = dimensions[0]
    assert all(dimension == first_dimension for dimension in dimensions), (
        "embeddings do not share a common dimension: {}".format(dimensions)
    )
    return first_dimension


def cosine_similarity(vector_a, vector_b):
    """
    Compute the cosine similarity between two vectors.

    Args:
        vector_a (numpy.ndarray): The first vector.
        vector_b (numpy.ndarray): The second vector.

    Returns:
        float: The cosine similarity between vector_a and vector_b, in
            the range [-1.0, 1.0], where 1.0 means the vectors point in
            exactly the same direction.
    """
    dot_product = float(np.dot(vector_a, vector_b))
    magnitude_a = float(np.linalg.norm(vector_a))
    magnitude_b = float(np.linalg.norm(vector_b))
    return dot_product / (magnitude_a * magnitude_b)


def build_similarity_table(texts, embeddings):
    """
    Compute cosine similarity between every pair of embedded texts.

    Args:
        texts (list[str]): The original texts, in the same order as
            embeddings.
        embeddings (numpy.ndarray): A 2D array of embeddings, one row
            per text, aligned with texts by index.

    Returns:
        list[dict]: One entry per unique pair of texts (i < j), each
            with "index_a" (int), "index_b" (int), "text_a" (str),
            "text_b" (str), and "similarity" (float, cosine similarity
            between the pair's embeddings).
    """
    table = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            table.append({
                "index_a": i,
                "index_b": j,
                "text_a": texts[i],
                "text_b": texts[j],
                "similarity": cosine_similarity(embeddings[i], embeddings[j]),
            })
    return table


def print_results(texts, embeddings, dimension, similarity_table, similar_pair, dissimilar_pair):
    """
    Print the full set of results: texts, dimensions, and similarities.

    Args:
        texts (list[str]): The sample texts.
        embeddings (numpy.ndarray): Embeddings aligned with texts by
            index.
        dimension (int): The shared vector dimension across embeddings.
        similarity_table (list[dict]): Pairwise similarity entries as
            returned by build_similarity_table.
        similar_pair (tuple[int, int]): Indices into texts of the pair
            expected to have closely related meaning.
        dissimilar_pair (tuple[int, int]): Indices into texts of the
            pair expected to be clearly unrelated.

    Returns:
        None
    """
    print("Sample texts:")
    for index, text in enumerate(texts):
        print("  [{}] {}".format(index, text))
    print()

    print("Vector dimension per embedding:")
    for index, vector in enumerate(embeddings):
        print("  [{}] {} dimensions".format(index, len(vector)))
    print("All embeddings share the same dimension: {}".format(dimension))
    print()

    print("Pairwise cosine similarity (all sample texts):")
    for entry in similarity_table:
        print("  [{}] vs [{}]: {:.4f}".format(entry["index_a"], entry["index_b"], entry["similarity"]))
    print()

    similar_score = cosine_similarity(embeddings[similar_pair[0]], embeddings[similar_pair[1]])
    dissimilar_score = cosine_similarity(embeddings[dissimilar_pair[0]], embeddings[dissimilar_pair[1]])

    print("Similar-meaning pair [{}] vs [{}]: {:.4f}".format(similar_pair[0], similar_pair[1], similar_score))
    print("  \"{}\"".format(texts[similar_pair[0]]))
    print("  \"{}\"".format(texts[similar_pair[1]]))
    print()
    print("Unrelated pair [{}] vs [{}]: {:.4f}".format(dissimilar_pair[0], dissimilar_pair[1], dissimilar_score))
    print("  \"{}\"".format(texts[dissimilar_pair[0]]))
    print("  \"{}\"".format(texts[dissimilar_pair[1]]))
    print()
    print("Similar pair scores higher than unrelated pair: {} ({:.4f} > {:.4f})".format(
        similar_score > dissimilar_score, similar_score, dissimilar_score
    ))


if __name__ == "__main__":
    print("Loading model: {}".format(MODEL_NAME))
    model = load_model()

    embeddings = generate_embeddings(model, SAMPLE_TEXTS)
    dimension = check_uniform_dimension(embeddings)
    similarity_table = build_similarity_table(SAMPLE_TEXTS, embeddings)

    print()
    print_results(SAMPLE_TEXTS, embeddings, dimension, similarity_table, SIMILAR_PAIR, DISSIMILAR_PAIR)

    print()
    print(
        "What these vectors are: each {}-dimensional vector is a numeric "
        "summary of a sentence's meaning, produced by a model trained to "
        "place sentences with related meaning near each other in that "
        "space. They are not random identifiers -- the same sentence "
        "always maps to the same vector, and different sentences with "
        "similar meaning map to nearby vectors even when they share few "
        "or no exact words. They are also not simple keyword counts -- a "
        "keyword-count vector would score the cat/stock-market pair near "
        "zero purely because the two sentences share no words, but it "
        "would not recognize that \"cat sat on the windowsill\" and \"cat "
        "was resting by the window\" mean nearly the same thing despite "
        "using different words; the embeddings above do recognize that, "
        "which is exactly what the higher cosine similarity score on the "
        "similar pair demonstrates.".format(dimension)
    )
