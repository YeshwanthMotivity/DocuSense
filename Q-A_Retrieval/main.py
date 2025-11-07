import os
import time
import logging

from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.rerank import rerank_chunks
from easycontext_cpu.infer_model import generate_answer

# --- Configuration ---
# Parameters for the analysis workflow, externalized into a dictionary.
# In a larger application, this could be loaded from a .env, YAML, or JSON file.
CONFIG = {
    "FILEPATH": os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt"),
    "CHUNK_MAX_TOKENS": 512,
    "CHUNK_CONCAT_CHUNKS": True,
    "CHUNK_CONCAT_FACTOR": 2,
    "RETRIEVE_K": 6,
    "RERANK_TOP_K": 3,
    "QUERY": "Explain the key developer concerns raised about the Apple App Store."
}

# --- Logging Setup ---
# Configure basic logging for better output control.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_analysis(config: dict):
    """
    Executes the 1M Token Codebase Analyst workflow based on the provided configuration.

    Args:
        config (dict): A dictionary containing all necessary configuration parameters
                       for file loading, chunking, retrieval, reranking, and query.
    """
    logger.info("⚙️ Starting 1M-Token Codebase Analyst (CPU mode)")

    filepath = config["FILEPATH"]
    query = config["QUERY"]

    # 1) Load sample document
    try:
        text = load_file(filepath)
        logger.info(f"Loaded file successfully: {filepath}")
    except FileNotFoundError:
        logger.error(f"❌ File not found! Ensure '{filepath}' exists at the specified path.")
        return # Exit the function if the file cannot be found

    # 2) Chunk and (optionally) concatenate for longer context
    chunks = chunk_text(
        text,
        max_tokens=config["CHUNK_MAX_TOKENS"],
        concat_chunks=config["CHUNK_CONCAT_CHUNKS"],
        concat_factor=config["CHUNK_CONCAT_FACTOR"]
    )
    logger.info(f"Text chunked into {len(chunks)} segments.")

    # 3) User query
    logger.info(f"🔍 User Query: {query}")

    # 4) Retrieve + Rerank relevant chunks
    top_chunks = get_top_k_chunks(query, chunks, k=config["RETRIEVE_K"])
    logger.info(f"Retrieved {len(top_chunks)} top chunks based on similarity.")

    reranked_chunks = rerank_chunks(top_chunks, query, top_k=config["RERANK_TOP_K"])
    logger.info(f"Reranked to select top {len(reranked_chunks)} chunks for answer generation.")

    # 5) Generate answer
    logger.info("Starting answer generation...")
    answer, prompt, raw_output, elapsed_time = generate_answer(query, reranked_chunks, return_debug=True)

    logger.info(f"\n--- Prompt Sent to Model (truncated) ---")
    logger.info(f"{prompt[:400]}...")
    logger.info(f"\n--- Raw Model Output (truncated) ---")
    logger.info(f"{raw_output[:400]}...")
    logger.info(f"\n⏱️ Generation time: {round(elapsed_time, 2)} seconds")
    logger.info(f"\n✅ FINAL ANSWER:\n{answer}")

def main():
    """
    Main entry point for the 1M-Token Codebase Analyst application.
    Orchestrates the analysis by calling run_analysis with the predefined CONFIG.
    """
    run_analysis(CONFIG)

if __name__ == "__main__":
    main()