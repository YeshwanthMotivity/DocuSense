import re, time
import ollama
import logging
from typing import List, Tuple, Union

# --- Configuration Management ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ollama model configuration
OLLAMA_MODEL_NAME = 'phi'  # Externalized Ollama model name
OLLAMA_GENERATION_OPTIONS = {  # Externalized generation options
    "temperature": 0.3,
    "top_p": 0.9,
    "num_predict": 350
}

STOP_TOKENS = ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]

def build_prompt(context: str, query: str) -> str:
    """
    Constructs a prompt for the Ollama model based on the given context and query.
    """
    return (
        "You are a helpful assistant. Answer strictly using the following context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\nAnswer:"
    )

def clean_answer(txt: str) -> str:
    """
    Cleans the raw model output by removing stop tokens, boilerplate phrases, and extra whitespace.
    """
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

def generate_answer(
    query: str,
    chunks: List[str],
    return_debug: bool = False
) -> Union[str, Tuple[str, str, str, float]]:
    """
    Generates an answer to a query using the Ollama model with provided context chunks.

    This function combines context chunks and a query into a prompt, sends it to a
    locally running Ollama model, and cleans the received response.

    Args:
        query: The user's question.
        chunks: A list of text segments to be used as context for the answer.
        return_debug: If True, returns a tuple containing the cleaned answer,
                      the full prompt, the raw model output, and the elapsed time.
                      Otherwise, returns only the cleaned answer.

    Returns:
        If return_debug is True:
            A tuple (cleaned_answer, prompt, raw_model_output, elapsed_time).
        If return_debug is False:
            The cleaned answer string.
        In case of an error, returns an error message string, or a tuple including it.
    """
    context = "\n---\n".join(chunks)
    prompt = build_prompt(context, query)

    t0 = time.time()

    try:
        logging.info(f"Calling Ollama model '{OLLAMA_MODEL_NAME}'...")
        response = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options=OLLAMA_GENERATION_OPTIONS
        )
        raw_output = response['message']['content']
        answer = clean_answer(raw_output)
        elapsed = time.time() - t0
        logging.info(f"Ollama call done in {elapsed:.2f}s")

        if return_debug:
            return answer, prompt, raw_output, elapsed
        return answer

    except Exception as e:
        error_message = f"Error calling Ollama: {e}"
        logging.error(error_message)
        if return_debug:
            return f"ERROR: {e}", prompt, str(e), 0.0
        return f"ERROR: {e}"