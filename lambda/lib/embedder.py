import requests
import logging

logger = logging.getLogger(__name__)

EMBEDDING_SERVICE_URL = "https://embedding-service-wxlf.onrender.com/embed"

def generate_embedding(text: str) -> list:
    response = requests.post(EMBEDDING_SERVICE_URL, json={"texts": [text]})
    response.raise_for_status()
    data = response.json()
    return data["embeddings"][0]

def generate_embeddings_batch(texts: list) -> list:
    response = requests.post(EMBEDDING_SERVICE_URL, json={"texts": texts})
    response.raise_for_status()
    data = response.json()
    return data["embeddings"]

if __name__ == "__main__":
    test_text = "This is a test sentence for embedding generation."
    embedding = generate_embedding(test_text)
    print(f"Generated embedding with {len(embedding)} dimensions")
    print(f"First 5 values: {embedding[:5]}")

    test_texts = [
        "First test sentence",
        "Second test sentence",
        "Third test sentence"
    ]
    embeddings = generate_embeddings_batch(test_texts)
    print(f"Generated {len(embeddings)} embeddings, each with {len(embeddings[0])} dimensions")
