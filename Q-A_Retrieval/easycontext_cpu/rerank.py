# rerank.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rerank_chunks(chunks, query, top_k=5):
    """
    Re-ranks text chunks based on cosine similarity with the query.
    
    Args:
        chunks (list of str): The list of text chunks.
        query (str): The user's input query.
        top_k (int): Number of top chunks to return.

    Returns:
        List[str]: Top-k ranked chunks by similarity.
    """
    if not chunks:
        return []

    # Combine query and chunks into a single list for vectorization
    documents = [query] + chunks

    # Vectorize using TF-IDF
    vectorizer = TfidfVectorizer().fit_transform(documents)
    
    # Compute cosine similarities (query vector is index 0)
    similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()

    # Sort chunk indices by similarity score
    top_indices = similarities.argsort()[::-1][:top_k]

    # Return the top-k most relevant chunks
    top_chunks = [chunks[i] for i in top_indices]
    return top_chunks
