# utils/retrieve_chunks.py

from sentence_transformers import SentenceTransformer, util

# Load a small sentence embedding model (CPU-compatible)
retriever = SentenceTransformer("all-MiniLM-L6-v2")  # 80MB model

def get_top_k_chunks(query, chunk_texts, k=3):
    """
    Returns top-k most relevant text chunks for a given query using cosine similarity.
    """
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
