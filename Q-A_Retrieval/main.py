"""
This script demonstrates the 1M-Token Codebase Analyst in CPU mode.
It loads a document, chunks it, retrieves and reranks relevant sections based on a query,
and then generates an answer using a local inference model.
"""

import os, time
from easycontext_cpu.utils           import load_file
from easycontext_cpu.chunk           import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.rerank          import rerank_chunks
from easycontext_cpu.infer_model     import generate_answer

# Configuration Constants
DEFAULT_FILEPATH    = os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt")
DEFAULT_QUERY       = "Explain the key developer concerns raised about the Apple App Store."
MAX_TOKENS          = 512
CONCAT_FACTOR       = 2
RETRIEVAL_K         = 6
RERANK_TOP_K        = 3

def main():
    print("⚙️ 1M-Token Codebase Analyst (CPU mode)")

    # 1) Load sample document
    try:
        text = load_file(DEFAULT_FILEPATH)
    except FileNotFoundError:
        print(f"❌ File not found! Make sure '{DEFAULT_FILEPATH}' exists.")
        return

    # 2) Chunk & (optionally) concatenate for longer context
    chunks = chunk_text(text, max_tokens=MAX_TOKENS, concat_chunks=True, concat_factor=CONCAT_FACTOR)

    # 3) User query
    print("🔍  Query:", DEFAULT_QUERY)

    # 4) Retrieve + rerank
    top_chunks  = get_top_k_chunks(DEFAULT_QUERY, chunks, k=RETRIEVAL_K)
    reranked    = rerank_chunks(top_chunks, DEFAULT_QUERY, top_k=RERANK_TOP_K)

    # 5) Answer generation
    answer, prompt, raw, elapsed = generate_answer(DEFAULT_QUERY, reranked, return_debug=True)

    print("\n--- prompt ---------------------------------\n", prompt[:400], "...\n")
    print("--- raw model output (truncated) -----------\n", raw[:400], "...\n")
    print("⏱️  generation time:", round(elapsed, 2), "s")
    print("\n✅  FINAL ANSWER:\n", answer)

if __name__ == "__main__":
    main()