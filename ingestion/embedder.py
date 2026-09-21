from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    return _model

def generate_embedding(text: str) -> list:
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def generate_embeddings_batch(texts: list) -> list:
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return [embedding.tolist() for embedding in embeddings]

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