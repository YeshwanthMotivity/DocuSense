from sentence_transformers import SentenceTransformer, util
import os
from typing import List, Optional

_retriever_model: Optional[SentenceTransformer] = None

def _get_retriever_model(model_name: Optional[str] = None) -> SentenceTransformer:
    """
    Lazily loads and returns the SentenceTransformer model (singleton pattern).
    The model name can be configured via SENTENCE_TRANSFORMER_MODEL environment variable
    or passed directly as an argument.
    """
    global _retriever_model
    if _retriever_model is None:
        if model_name is None:
            model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
        _retriever_model = SentenceTransformer(model_name)
    return _retriever_model

def get_top_k_chunks(query: str, chunk_texts: List[str], k: int = 3) -> List[str]:
    """
    Returns top-k most relevant text chunks for a given query using cosine similarity.
    """
    # Input validation for k
    if not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive integer.")

    # Lazy load the retriever model
    retriever = _get_retriever_model()

    # Embed the query and all chunks
    query_embedding = retriever.encode(query, convert_to_tensor=True)
    chunk_embeddings = retriever.encode(chunk_texts, convert_to_tensor=True)

    # Compute cosine similarity
    similarities = util.cos_sim(query_embedding, chunk_embeddings)[0]

    # Get top-k chunk indices
    top_k_indices = similarities.argsort(descending=True)[:k]

    # Return top-k matching chunks
    top_chunks = [chunk_texts[i] for i in top_k_indices]
    return top_chunks