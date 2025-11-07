import logging
from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_easycontext_pipeline(text: str, query: str, k: int = 5) -> str:
    """
    Runs the EasyContext pipeline on CPU:
    - Chunks the input text
    - Retrieves the top-k relevant chunks
    - Generates an answer using the selected chunks
    """
    logging.info("🧩 Chunking input text...")
    try:
        chunks = chunk_text(text)
    except Exception as e:
        logging.error(f"Error during text chunking: {e}")
        return "Error: Failed to chunk text."

    logging.info(f"🔍 Retrieving top-{k} relevant chunks...")
    try:
        top_chunks = get_top_k_chunks(chunks, query, k=k)
    except Exception as e:
        logging.error(f"Error during retrieval of top-{k} chunks: {e}")
        return "Error: Failed to retrieve relevant chunks."

    logging.info("🧠 Generating answer from selected chunks...")
    try:
        answer = generate_answer(query, top_chunks)
    except Exception as e:
        logging.error(f"Error during answer generation: {e}")
        return "Error: Failed to generate an answer."

    return answer