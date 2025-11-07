from sentence_transformers import SentenceTransformer, util

def get_top_k_chunks(retriever: SentenceTransformer, query: str, chunk_texts: list[str], k: int = 3) -> list[str]:
    """
    Returns top-k most relevant text chunks for a given query using cosine similarity.

    Args:
        retriever: The SentenceTransformer model instance to use for embedding.
        query: The query string.
        chunk_texts: A list of text chunks to search within.
        k: The number of top chunks to return.

    Returns:
        A list of the top-k most relevant text chunks.
    """
    # Error handling: return empty list if no chunks are provided
    if not chunk_texts:
        return []

    # Embed the query and all chunks
    query_embedding = retriever.encode(query, convert_to_tensor=True)
    chunk_embeddings = retriever.encode(chunk_texts, convert_to_tensor=True)

    # Compute cosine similarity
    similarities = util.cos_sim(query_embedding, chunk_embeddings)[0]

    # Get top-k chunk indices
    # Ensure k does not exceed the number of available chunks
    actual_k = min(k, len(chunk_texts))
    top_k_indices = similarities.argsort(descending=True)[:actual_k]

    # Return top-k matching chunks
    top_chunks = [chunk_texts[i] for i in top_k_indices]
    return top_chunks