import logging
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer

# Configure basic logging for the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_easycontext_pipeline(text, query, k=5):
    """
    Runs the EasyContext pipeline on CPU:
    - Chunks the input text
    - Retrieves the top-k relevant chunks
    - Generates an answer using the selected chunks
    """
    chunks = None
    top_chunks = None
    answer = None

    try:
        logging.info("🧩 Chunking input text...")
        chunks = chunk_text(text)
    except Exception as e:
        logging.error(f"Failed to chunk text: {e}")
        return None

    try:
        logging.info(f"🔍 Retrieving top-{k} relevant chunks...")
        top_chunks = get_top_k_chunks(chunks, query, k=k)
    except Exception as e:
        logging.error(f"Failed to retrieve top-k chunks: {e}")
        return None

    try:
        logging.info("🧠 Generating answer from selected chunks...")
        answer = generate_answer(query, top_chunks)
    except Exception as e:
        logging.error(f"Failed to generate answer: {e}")
        return None

    return answer