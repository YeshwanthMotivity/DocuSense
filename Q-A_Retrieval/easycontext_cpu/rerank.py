from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rerank_chunks(chunks, query, tfidf_vectorizer, top_k=5):
    """
    Re-ranks text chunks based on cosine similarity with the query.
    
    Args:
        chunks (list of str): The list of text chunks.
        query (str): The user's input query.
        tfidf_vectorizer: An already fitted `TfidfVectorizer` object.
        top_k (int): Number of top chunks to return.

    Returns:
        List[str]: Top-k ranked chunks by similarity.
    """
    if not chunks:
        return []

    # Transform query and chunks using the pre-fitted vectorizer
    query_vector = tfidf_vectorizer.transform([query])
    chunk_vectors = tfidf_vectorizer.transform(chunks)
    
    # Compute cosine similarities
    similarities = cosine_similarity(query_vector, chunk_vectors).flatten()

    # Sort chunk indices by similarity score
    top_indices = similarities.argsort()[::-1][:top_k]

    # Return the top-k most relevant chunks
    top_chunks = [chunks[i] for i in top_indices]
    return top_chunks