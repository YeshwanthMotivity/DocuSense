import logging
from typing import List

from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_easycontext_pipeline(text: str, query: str, k: int = 5) -> str:
    """
    Runs the EasyContext pipeline on CPU:
    - Chunks the input text
    - Retrieves the top-k relevant chunks
    - Generates an answer using the selected chunks
    
    Args:
        text (str): The input text to be processed.
        query (str): The query string for retrieving relevant chunks and generating an answer.
        k (int): The number of top relevant chunks to retrieve. Must be a positive integer.

    Returns:
        str: The generated answer based on the query and retrieved chunks.

    Raises:
        ValueError: If `k` is not a positive integer.
        Exception: For errors occurring during chunking, retrieval, or answer generation.
    """
    # Input validation for k
    if not isinstance(k, int) or k <= 0:
        logging.error(f"Invalid value for k: {k}. k must be a positive integer.")
        raise ValueError("k must be a positive integer.")

    logging.info("Chunking input text...")
    try:
        chunks: List[str] = chunk_text(text)
    except Exception as e:
        logging.error(f"Error during chunking text: {e}")
        raise

    logging.info(f"Retrieving top-{k} relevant chunks...")
    try:
        top_chunks: List[str] = get_top_k_chunks(chunks, query, k=k)
    except Exception as e:
        logging.error(f"Error during retrieving top-k chunks: {e}")
        raise

    logging.info("Generating answer from selected chunks...")
    try:
        answer: str = generate_answer(query, top_chunks)
    except Exception as e:
        logging.error(f"Error during answer generation: {e}")
        raise

    return answer