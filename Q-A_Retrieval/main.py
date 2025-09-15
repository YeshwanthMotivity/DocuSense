# from easycontext_cpu.chunk import chunk_text
# from easycontext_cpu.generate import generate_answer
# from easycontext_cpu.rerank import rerank
# from easycontext_cpu.utils import load_file

# if __name__ == "__main__":
#     print("⚙️ Running 1M Token Codebase Analyst on CPU...")

#     # Step 1: Load sample file
#     try:
#         text = load_file(r'C:\Yash\1M-Token Codebase Analyst\EasyContext\PaulGrahamEssays\aord.txt')
#     except FileNotFoundError:
#         print("❌ File not found! Make sure 'gap.txt' exists at the given path.")
#         exit()

#     # Step 2: Chunk the text
#     chunks = chunk_text(text)

#     # Step 3: Rerank using keyword
#     reranked = rerank("startup", chunks)

#     # Step 4: Pick top chunk
#     top_chunk = reranked[0][0]

#     # Step 5: Generate a dummy response
#     response = generate_answer(top_chunk)

#     print("✅ Response Generated:\n", response)

# import os
# from easycontext_cpu.utils import load_file
# from easycontext_cpu.chunk import chunk_text
# from easycontext_cpu.retrieve_chunks import get_top_k_chunks
# from easycontext_cpu.rerank import rerank_chunks
# from easycontext_cpu.infer_model import generate_answer, clean_answer

# print("⚙️ Running 1M Token Codebase Analyst on CPU...")

# # # STEP 1: Load the essay or codebase input (modify path as needed)
# # filepath = os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt")  # ✅ Make sure this file exists
# # text = load_file(filepath)
# # STEP 1: Load the essay or codebase input (modify path as needed)
# filepath = os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt")  # ✅ Make sure this file exists
# try:
#     text = load_file(filepath)
# except FileNotFoundError:
#     print(f"❌ File not found! Make sure '{filepath}' exists.")
#     exit()
    




# # STEP 2: Chunk the input text
# chunks = chunk_text(text, max_tokens=512, concat_chunks=True, concat_factor=2)

# # STEP 3: Simulate a user query
# query = "Explain the key developer concerns raised about the Apple App Store."
# print(f"\n🔍 Query: {query}\n")

# # STEP 4: Retrieve top-k relevant chunks
# top_chunks = get_top_k_chunks(query, chunks, k=5)

# # STEP 5: Rerank chunks
# reranked_chunks = rerank_chunks(top_chunks, query)

# # STEP 6: Generate answer using reranked chunks (with verbose debug output)
# answer, prompt, raw_output = generate_answer(query, reranked_chunks, return_debug=True)

# # STEP 7: Clean the generated answer
# answer_cleaned = clean_answer(answer)

# # Debug Info
# print("\n--- Prompt Sent to Model ---\n")
# print(prompt)

# print("\n--- Raw Model Output ---\n")
# print(raw_output)

# # Final Result
# print("\n✅ Final Response Extracted:\n")
# print(answer_cleaned)


# main.py
import os, time
from easycontext_cpu.utils           import load_file
from easycontext_cpu.chunk           import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.rerank          import rerank_chunks
from easycontext_cpu.infer_model     import generate_answer

print("⚙️ 1M-Token Codebase Analyst (CPU mode)")

# 1) load sample document
FILEPATH = os.path.join("EasyContext", "PaulGrahamEssays", "apple.txt")
text     = load_file(FILEPATH)

# 2) chunk & (optionally) concatenate for longer context
chunks = chunk_text(text, max_tokens=512, concat_chunks=True, concat_factor=2)

# 3) user query
query = "Explain the key developer concerns raised about the Apple App Store."
print("🔍  Query:", query)

# 4) retrieve + rerank
top_chunks  = get_top_k_chunks(query, chunks, k=6)
reranked    = rerank_chunks(top_chunks, query, top_k=3)

# 5) answer
answer, prompt, raw, elapsed = generate_answer(query, reranked, return_debug=True)

print("\n--- prompt ---------------------------------\n", prompt[:400], "...\n")
print("--- raw model output (truncated) -----------\n", raw[:400], "...\n")
print("⏱️  generation time:", round(elapsed, 2), "s")
print("\n✅  FINAL ANSWER:\n", answer)
