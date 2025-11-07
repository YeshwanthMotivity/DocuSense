import os
import time
import logging

from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.rerank import rerank_chunks
from easycontext_cpu.infer_model import generate_answer, clean_answer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("⚙️ 1M-Token Codebase Analyst (CPU mode)")

    # Configuration parameters (can be loaded from YAML/TOML/CLI args in a real application)
    config = {
        "filepath": os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt"),
        "chunking": {
            "max_tokens": 512,
            "concat_chunks": True,
            "concat_factor": 2
        },
        "query": "Explain the key developer concerns raised about the Apple App Store.",
        "retrieval": {
            "top_k_chunks": 6
        },
        "reranking": {
            "top_k_reranked": 3
        }
    }

    # 1) Load sample document
    filepath = config["filepath"]
    try:
        text = load_file(filepath)
        logging.info(f"Loaded document from: {filepath}")
    except FileNotFoundError:
        logging.error(f"❌ File not found! Make sure '{filepath}' exists.")
        return # Exit if file not found

    # 2) Chunk & (optionally) concatenate for longer context
    chunking_config = config["chunking"]
    chunks = chunk_text(
        text,
        max_tokens=chunking_config["max_tokens"],
        concat_chunks=chunking_config["concat_chunks"],
        concat_factor=chunking_config["concat_factor"]
    )
    logging.info(f"Chunked text into {len(chunks)} chunks.")

    # 3) User query
    query = config["query"]
    logging.info(f"🔍 Query: {query}")

    # 4) Retrieve + rerank
    top_k_chunks_val = config["retrieval"]["top_k_chunks"]
    top_chunks = get_top_k_chunks(query, chunks, k=top_k_chunks_val)
    logging.info(f"Retrieved {len(top_chunks)} top chunks.")

    top_k_reranked_val = config["reranking"]["top_k_reranked"]
    reranked = rerank_chunks(top_chunks, query, top_k=top_k_reranked_val)
    logging.info(f"Reranked to {len(reranked)} top chunks.")

    # 5) Answer generation
    answer, prompt, raw_output, elapsed = generate_answer(query, reranked, return_debug=True)
    logging.info(f"⏱️ Generation time: {round(elapsed, 2)}s")

    logging.debug(f"\n--- Prompt Sent to Model (truncated) ---\n{prompt[:400]}...")
    logging.debug(f"\n--- Raw Model Output (truncated) ---\n{raw_output[:400]}...")

    # 6) Clean the generated answer
    answer_cleaned = clean_answer(answer)

    logging.info(f"\n✅ FINAL ANSWER:\n{answer_cleaned}")

if __name__ == "__main__":
    main()