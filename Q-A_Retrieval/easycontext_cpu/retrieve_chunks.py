from sentence_transformers import SentenceTransformer, util
import torch

class ChunkRetriever:
    """
    A class to encapsulate the SentenceTransformer model and retrieval logic.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the ChunkRetriever with a specified SentenceTransformer model.

        Args:
            model_name (str): The name of the SentenceTransformer model to load.
        """
        self.model = SentenceTransformer(model_name)

    def get_top_k_chunks(
        self,
        query: str,
        chunk_texts: list[str],
        k: int = 3,
        chunk_embeddings: torch.Tensor = None
    ) -> list[str]:
        """
        Returns top-k most relevant text chunks for a given query using cosine similarity.

        Args:
            query (str): The query string.
            chunk_texts (list[str]): A list of text chunks to search within.
            k (int): The number of top relevant chunks to return. Must be a positive integer.
            chunk_embeddings (torch.Tensor, optional): Pre-computed embeddings for chunk_texts.
                                                      If provided, chunk_texts will not be re-encoded.

        Returns:
            list[str]: A list of the top-k most relevant text chunks.
        
        Raises:
            ValueError: If k is not a positive integer.
            TypeError: If chunk_embeddings is provided but not a torch.Tensor.
            ValueError: If the number of chunk_embeddings does not match the number of chunk_texts.
        """
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer.")
        
        # Embed the query
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Handle pre-computed chunk_embeddings or encode on the fly
        if chunk_embeddings is None:
            chunk_embeddings = self.model.encode(chunk_texts, convert_to_tensor=True)
        else:
            if not isinstance(chunk_embeddings, torch.Tensor):
                raise TypeError("chunk_embeddings must be a torch.Tensor if provided.")
            if chunk_embeddings.shape[0] != len(chunk_texts):
                raise ValueError("The number of chunk_embeddings must match the number of chunk_texts.")

        if len(chunk_texts) == 0:
            return []

        # Compute cosine similarity
        similarities = util.cos_sim(query_embedding, chunk_embeddings)[0]

        # Get top-k chunk indices. argsort handles k > len(similarities) gracefully.
        top_k_indices = similarities.argsort(descending=True)[:k]

        # Return top-k matching chunks
        top_chunks = [chunk_texts[i] for i in top_k_indices]
        return top_chunks