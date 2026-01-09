import re, time
import ollama

STOP_TOKENS = ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]

def build_prompt(context: str, query: str) -> str:
    """Builds a strict prompt for the model."""
    return (
        "You are a helpful assistant. Answer strictly using the following context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\nAnswer:"
    )

def clean_answer(txt: str) -> str:
    """Cleans the model output by removing artifacts and filler phrases."""
    for tok in STOP_TOKENS:
        txt = txt.replace(tok, " ")
    txt = re.sub(r"\s+", " ", txt).strip()

    boring = [
        r"based (solely|entirely)? on the (provided )?context[, ]*",
        r"according to the context[, ]*",
        r"the context (states|says) that[, ]*",
    ]
    for pat in boring:
        txt = re.sub("^" + pat, "", txt, flags=re.I).strip()

    return txt

def generate_answer(query, chunks, return_debug=False):
    """
    Generates an answer using the local Ollama model (phi).
    """
    context = "\n---\n".join(chunks)
    prompt = build_prompt(context, query)

    t0 = time.time()

    try:
        print("Calling Ollama model...")
        response = ollama.chat(
            model='phi',  # ensure this matches your local Ollama model name exactly
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 350
            }
        )
        raw_output = response['message']['content']
        answer = clean_answer(raw_output)
        elapsed = time.time() - t0
        print(f"Ollama call done in {elapsed:.2f}s")

        if return_debug:
            return answer, prompt, raw_output, elapsed
        return answer

    except Exception as e:
        print("Error calling Ollama:", e)
        if return_debug:
            return "ERROR", prompt, str(e), 0.0
        return 'ERROR'
