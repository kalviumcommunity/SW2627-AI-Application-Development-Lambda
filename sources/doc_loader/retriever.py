"""
Retrieves the corpus chunks most similar to a question from the local
chromadb collection built by index_corpus.py.

Inputs:
    A question string. Settings come from environment variables or the
    ".env" file next to this script: EMBEDDING_BASE_URL,
    EMBEDDING_API_KEY, EMBEDDING_MODEL (to embed the question with the
    same model used for the corpus) and VECTOR_DB_PATH,
    VECTOR_DB_COLLECTION_NAME, VECTOR_DB_DISTANCE_METRIC (to open the
    collection).

Outputs:
    A list of the closest chunks, each a dict with "chunk_id", "section",
    "text", "source", and "distance". Contains no prompt wording; the
    callers pass these chunks to the prompts package.

No paid API key is used or required.
"""

import os

from embed_store import embed_texts, get_embedding_config
from vector_db import connect_to_database, get_vector_db_config

ENV_FILE_NAME = ".env"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class Retriever:
    """Embeds questions and looks up their closest chunks in chromadb."""

    def __init__(self, env_path=os.path.join(SCRIPT_DIR, ENV_FILE_NAME)):
        """
        Open the embedding backend settings and the chromadb collection.

        Args:
            env_path (str): Path to the .env file holding the embedding
                and vector database settings.

        Returns:
            None

        Raises:
            RuntimeError: If settings are missing, the database is not
                reachable, or the collection is empty (run
                index_corpus.py first).
        """
        self.embedding_config = get_embedding_config(env_path)
        db_config = get_vector_db_config(env_path)
        client = connect_to_database(os.path.join(SCRIPT_DIR, db_config["path"]))
        self.collection = client.get_or_create_collection(db_config["collection_name"])
        if self.collection.count() == 0:
            raise RuntimeError("collection {} is empty; run index_corpus.py first".format(db_config["collection_name"]))

    def retrieve(self, question, top_k):
        """
        Find the chunks closest in meaning to a question.

        Args:
            question (str): The question to look up.
            top_k (int): Number of chunks to return.

        Returns:
            list[dict]: Up to top_k chunks, closest first, each with
                "chunk_id" (str), "section" (str or None), "text" (str),
                "source" (str), and "distance" (float, lower is closer).
        """
        vector = embed_texts(
            [question], self.embedding_config["base_url"],
            self.embedding_config["api_key"], self.embedding_config["model_name"],
        )[0]
        result = self.collection.query(
            query_embeddings=[vector], n_results=top_k, include=["documents", "metadatas", "distances"],
        )
        chunks = []
        for chunk_id, text, metadata, distance in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            chunks.append({
                "chunk_id": chunk_id,
                "section": metadata.get("section") or None,
                "text": text,
                "source": metadata.get("source"),
                "distance": float(distance),
            })
        return chunks
