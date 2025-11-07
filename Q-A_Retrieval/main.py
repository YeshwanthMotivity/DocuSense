import os, time
from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.rerank import rerank_chunks
from easycontext_cpu.infer_model import generate_answer, clean_answer

# Configuration constants
DEFAULT_FILEPATH = os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt")
CHUNK_MAX_TOKENS = 512
CHUNK_CONCAT_FACTOR = 2
DEFAULT_QUERY = "Explain the key developer concerns raised about the Apple App Store."
RETRIEVAL_TOP_K = 6
RERANK_TOP_K = 3

def main():
    print("⚙️ 1M-Token Codebase Analyst (CPU mode)")

    # 1) load sample document
    filepath = DEFAULT_FILEPATH
    try:
        text = load_file(filepath)
    except FileNotFoundError:
        print(f"❌ File not found! Make sure '{filepath}' exists.")
        return

    # 2) chunk & (optionally) concatenate for longer context
    chunks = chunk_text(text, max_tokens=CHUNK_MAX_TOKENS, concat_chunks=True, concat_factor=CHUNK_CONCAT_FACTOR)

    # 3) user query
    query = DEFAULT_QUERY
    print("🔍  Query:", query)

    # 4) retrieve + rerank
    top_chunks  = get_top_k_chunks(query, chunks, k=RETRIEVAL_TOP_K)
    reranked    = rerank_chunks(top_chunks, query, top_k=RERANK_TOP_K)

    # 5) answer
    answer, prompt, raw, elapsed = generate_answer(query, reranked, return_debug=True)

    # 6) Clean the generated answer
    cleaned_answer = clean_answer(answer)

    print("\n--- prompt ---------------------------------\n", prompt[:400], "...\n")
    print("--- raw model output (truncated) -----------\n", raw[:400], "...\n")
    print("⏱️  generation time:", round(elapsed, 2), "s")
    print("\n✅  FINAL ANSWER:\n", cleaned_answer)

if __name__ == "__main__":
    main()