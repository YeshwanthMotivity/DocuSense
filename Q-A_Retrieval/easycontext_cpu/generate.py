import logging
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_easycontext_pipeline(text, query, k=5):
    """
    Runs the EasyContext pipeline on CPU:
    - Chunks the input text
    - Retrieves the top-k relevant chunks
    - Generates an answer using the selected chunks
    """
    if not isinstance(k, int) or k <= 0:
        raise ValueError("Parameter 'k' must be a positive integer.")

    logger.info("🧩 Chunking input text...")
    chunks = chunk_text(text)

    logger.info(f"🔍 Retrieving top-{k} relevant chunks...")
    top_chunks = get_top_k_chunks(chunks, query, k=k)

    logger.info("🧠 Generating answer from selected chunks...")
    answer = generate_answer(query, top_chunks)

    return answer