# generate.py

from easycontext_cpu.utils import load_file
from easycontext_cpu.chunk import chunk_text
from easycontext_cpu.retrieve_chunks import get_top_k_chunks
from easycontext_cpu.infer_model import generate_answer

def run_easycontext_pipeline(text, query, k=5):
    """
    Runs the EasyContext pipeline on CPU:
    - Chunks the input text
    - Retrieves the top-k relevant chunks
    - Generates an answer using the selected chunks
    """
    print("🧩 Chunking input text...")
    chunks = chunk_text(text)

    print(f"🔍 Retrieving top-{k} relevant chunks...")
    top_chunks = get_top_k_chunks(chunks, query, k=k)

    print("🧠 Generating answer from selected chunks...")
    answer = generate_answer(query, top_chunks)

    return answer
