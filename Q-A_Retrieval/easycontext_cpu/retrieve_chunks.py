from sentence_transformers import SentenceTransformer, util

class ChunkRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the ChunkRetriever with a SentenceTransformer model.

        Args:
            model_name: The name of the SentenceTransformer model to load.
        """
        self.retriever = SentenceTransformer(model_name)

    def get_top_k_chunks(self, query: str, chunk_texts: list[str], k: int = 3) -> list[str]:
        """
        Returns top-k most relevant text chunks for a given query using cosine similarity.

        Args:
            query: The query string.
            chunk_texts: A list of text chunks to search within.
            k: The number of top chunks to retrieve.

        Returns:
            A list of the top-k most relevant text chunks.

        Raises:
            ValueError: If k is not a positive integer.
        """
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer.")

        if not chunk_texts:
            return []

        # Cap k if it's greater than the number of available chunks
        k = min(k, len(chunk_texts))

        query_embedding = self.retriever.encode(query, convert_to_tensor=True)
        chunk_embeddings = self.retriever.encode(chunk_texts, convert_to_tensor=True)

        similarities = util.cos_sim(query_embedding, chunk_embeddings)[0]

        top_k_indices = similarities.argsort(descending=True)[:k]

        top_chunks = [chunk_texts[i] for i in top_k_indices]
        return top_chunks