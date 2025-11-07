from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rerank_chunks(chunks: List[str], query: str, top_k: int = 5, pre_fitted_vectorizer=None) -> List[str]:
    if not chunks:
        return []

    if pre_fitted_vectorizer:
        query_vector = pre_fitted_vectorizer.transform([query])
        chunks_vectorized = pre_fitted_vectorizer.transform(chunks)
    else:
        documents = [query] + chunks
        all_vectors = TfidfVectorizer().fit_transform(documents)
        query_vector = all_vectors[0:1]
        chunks_vectorized = all_vectors[1:]
    
    similarities = cosine_similarity(query_vector, chunks_vectorized).flatten()

    top_indices = similarities.argsort()[::-1][:top_k]

    top_chunks = [chunks[i] for i in top_indices]
    return top_chunks