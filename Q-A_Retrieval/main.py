import os
import time
import argparse
import logging

from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.rerank import rerank_chunks
from easycontext_cpu.infer_model import generate_answer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(args):
    logging.info("⚙️ 1M-Token Codebase Analyst (CPU mode)")

    # 1) load sample document
    try:
        text = load_file(args.filepath)
        logging.info(f"Loaded file: {args.filepath}")
    except FileNotFoundError:
        logging.error(f"❌ File not found! Make sure '{args.filepath}' exists.")
        exit(1)
    except Exception as e:
        logging.error(f"❌ An error occurred while loading the file: {e}")
        exit(1)

    # 2) chunk & (optionally) concatenate for longer context
    chunks = chunk_text(text, max_tokens=args.max_tokens, concat_chunks=True, concat_factor=args.concat_factor)
    logging.info(f"Chunked text into {len(chunks)} chunks.")

    # 3) user query
    query = "Explain the key developer concerns raised about the Apple App Store."
    logging.info(f"🔍 Query: {query}")

    # 4) retrieve + rerank
    top_chunks = get_top_k_chunks(query, chunks, k=args.k_retrieve)
    logging.info(f"Retrieved top {len(top_chunks)} chunks.")
    reranked = rerank_chunks(top_chunks, query, top_k=args.top_k_rerank)
    logging.info(f"Reranked to {len(reranked)} chunks.")

    # 5) answer
    answer, prompt, raw, elapsed = generate_answer(query, reranked, return_debug=True)

    logging.info(f"\n--- prompt ---------------------------------\n{prompt[:400]} ...\n")
    logging.info(f"--- raw model output (truncated) -----------\n{raw[:400]} ...\n")
    logging.info(f"⏱️ Generation time: {round(elapsed, 2)} s")
    logging.info(f"\n✅ FINAL ANSWER:\n{answer}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="1M-Token Codebase Analyst (CPU mode)")
    parser.add_argument(
        "--filepath",
        type=str,
        default=os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt"),
        help="Path to the document file to be analyzed."
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=512,
        help="Maximum tokens per chunk."
    )
    parser.add_argument(
        "--concat_factor",
        type=int,
        default=2,
        help="Factor for concatenating chunks."
    )
    parser.add_argument(
        "--k_retrieve",
        type=int,
        default=6,
        help="Number of top chunks to retrieve initially (k for get_top_k_chunks)."
    )
    parser.add_argument(
        "--top_k_rerank",
        type=int,
        default=3,
        help="Number of top chunks to keep after reranking (top_k for rerank_chunks)."
    )

    args = parser.parse_args()
    main(args)