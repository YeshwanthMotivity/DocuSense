from sentence_transformers import SentenceTransformer, util
from typing import List, Optional

_retriever: Optional[SentenceTransformer] = None
_DEFAULT_MODEL = "all-MiniLM-L6-v2"

def _get_or_init_retriever(model_name: str = _DEFAULT_MODEL) -> SentenceTransformer:
    global _retriever
    if _retriever is None:
        _retriever = SentenceTransformer(model_name)
    return _retriever

def get_top_k_chunks(query: str, chunk_texts: List[str], k: int = 3) -> List[str]:
    if not chunk_texts:
        return []

    if k <= 0:
        raise ValueError("k must be a positive integer.")
    
    if k > len(chunk_texts):
        k = len(chunk_texts)

    retriever = _get_or_init_retriever()

    query_embedding = retriever.encode(query, convert_to_tensor=True)
    chunk_embeddings = retriever.encode(chunk_texts, convert_to_tensor=True)

    similarities = util.cos_sim(query_embedding, chunk_embeddings)[0]

    top_k_indices = similarities.argsort(descending=True)[:k]

    top_chunks = [chunk_texts[i] for i in top_k_indices]
    return top_chunks