from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

def rerank_chunks(chunks, query, vectorizer: TfidfVectorizer, chunk_vectors: csr_matrix, top_k=5):
    """
    Re-ranks text chunks based on cosine similarity with the query,
    using a pre-fitted TF-IDF vectorizer and pre-vectorized chunks.
    
    Args:
        chunks (list of str): The list of original text chunks.
        query (str): The user's input query.
        vectorizer (TfidfVectorizer): A pre-fitted TfidfVectorizer instance.
        chunk_vectors (scipy.sparse.csr_matrix): Pre-computed TF-IDF vectors for the 'chunks'.
        top_k (int): Number of top chunks to return.

    Returns:
        List[str]: Top-k ranked chunks by similarity.
    """
    if not chunks:
        return []

    # Vectorize the query using the pre-fitted vectorizer
    query_vector = vectorizer.transform([query])
    
    # Compute cosine similarities between query vector and pre-computed chunk vectors
    similarities = cosine_similarity(query_vector, chunk_vectors).flatten()

    # Sort chunk indices by similarity score
    top_indices = similarities.argsort()[::-1][:top_k]

    # Return the top-k most relevant chunks
    top_chunks = [chunks[i] for i in top_indices]
    return top_chunks