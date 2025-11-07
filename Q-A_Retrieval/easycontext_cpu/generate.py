import logging
from typing import List, Optional

# Removed: from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_easycontext_pipeline(text: str, query: str, k: int = 5) -> Optional[str]:
    """
    Runs the EasyContext pipeline on CPU:
    - Chunks the input text
    - Retrieves the top-k relevant chunks
    - Generates an answer using the selected chunks
    """
    chunks: Optional[List[str]] = None
    top_chunks: Optional[List[str]] = None
    answer: Optional[str] = None

    try:
        logger.info("Chunking input text...")
        chunks = chunk_text(text)
    except Exception as e:
        logger.error(f"Failed to chunk text: {e}", exc_info=True)
        return None

    if not chunks:
        logger.warning("Text chunking resulted in no chunks. Aborting pipeline.")
        return None

    try:
        logger.info(f"Retrieving top-{k} relevant chunks...")
        top_chunks = get_top_k_chunks(chunks, query, k=k)
    except Exception as e:
        logger.error(f"Failed to retrieve top chunks: {e}", exc_info=True)
        return None

    if not top_chunks:
        logger.warning("No top chunks were retrieved. Aborting pipeline.")
        return None

    try:
        logger.info("Generating answer from selected chunks...")
        answer = generate_answer(query, top_chunks)
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}", exc_info=True)
        return None

    return answer