from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional
from scipy.sparse import csr_matrix

def rerank_chunks(
    chunks: list[str],
    query: str,
    top_k: int = 5,
    tfidf_vectorizer: Optional[TfidfVectorizer] = None,
    chunks_tfidf_matrix: Optional[csr_matrix] = None
) -> List[str]:
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

    query_vector = None
    document_vectors = None

    if tfidf_vectorizer is not None and chunks_tfidf_matrix is not None:
        # Optimized path: use pre-fitted vectorizer and pre-computed chunk matrix
        query_vector = tfidf_vectorizer.transform([query])
        document_vectors = chunks_tfidf_matrix
    else:
        # Original path: instantiate and fit_transform on combined documents
        # Combine query and chunks into a single list for vectorization
        documents = [query] + chunks
        
        # Instantiate TfidfVectorizer
        vectorizer_obj = TfidfVectorizer() 
        
        # Fit and transform the documents, renaming the result for clarity (Suggestion 2)
        all_documents_tfidf_matrix = vectorizer_obj.fit_transform(documents)
        
        # Extract query vector (index 0) and chunk vectors (rest)
        query_vector = all_documents_tfidf_matrix[0:1]
        document_vectors = all_documents_tfidf_matrix[1:]
    
    # Compute cosine similarities
    similarities = cosine_similarity(query_vector, document_vectors).flatten()

    # Sort chunk indices by similarity score
    top_indices = similarities.argsort()[::-1][:top_k]

    # Return the top-k most relevant chunks
    top_chunks = [chunks[i] for i in top_indices]
    return top_chunks