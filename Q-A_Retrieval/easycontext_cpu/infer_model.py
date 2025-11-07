import re
import time
import ollama
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Module-level constant for Ollama model name
OLLAMA_MODEL_NAME: str = "phi"

# Define generation parameters as constants for easier tuning
TEMPERATURE: float = 0.3
TOP_P: float = 0.9
NUM_PREDICT: int = 350  # Corresponds to max_new_tokens for Ollama

# STOP_TOKENS for the 'phi' model.
# When prompted with "Answer:", phi model usually just starts answering.
# It might generate a newline or two, but rarely extraneous chat tags like <|user|>.
# The main concern would be it stopping abruptly or including remnants if the context ends with a specific pattern.
# For a clean answer after "Answer:", we primarily want to strip leading/trailing whitespace and common filler.
# Ollama's `num_predict` also helps control length, but it doesn't guarantee a clean stop.
# Based on typical phi model behavior, common chat tags are less likely to appear *within* the generated answer
# unless it's explicitly part of the prompt structure it's responding to (which `build_prompt` avoids).
# Removing `</s>` is often useful as it's an end-of-sequence token that `ollama.chat` might emit.
# For simplicity, we keep a minimal list and rely on the prompt structure to guide the model.
STOP_TOKENS: List[str] = ["</s>", "<|endoftext|>"]

def build_prompt(context: str, query: str) -> str:
    """
    Constructs a prompt for the Ollama `phi` model based on provided context and a query.

    Args:
        context (str): The relevant context information, typically from retrieved chunks.
        query (str): The user's question.

    Returns:
        str: The formatted prompt string for the LLM.
    """
    return (
        "You are a helpful assistant. Answer strictly using the following context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\nAnswer:"
    )

def clean_answer(txt: str) -> str:
    """
    Cleans the raw model output by removing stop tokens, boilerplate phrases,
    and excessive whitespace.

    Args:
        txt (str): The raw text output from the Ollama model.

    Returns:
        str: The cleaned answer.
    """
    # Strip stop tokens
    for tok in STOP_TOKENS:
        txt = txt.replace(tok, " ")
    txt = re.sub(r"\s+", " ", txt).strip()

    # Optional: cut generic sentence prefixes that might appear even after the prompt
    boring = [
        r"based (solely|entirely)? on the (provided )?context[, ]*",
        r"according to the context[, ]*",
        r"the context (states|says) that[, ]*",
        r"the answer is that[, ]*", # Added common filler observed with some models
    ]
    for pat in boring:
        txt = re.sub("^" + pat, "", txt, flags=re.IGNORECASE).strip()

    return txt

def generate_answer(query: str, chunks: List[str], return_debug: bool = False) -> str:
    """
    Generates a context-aware answer using the Ollama `phi` model.

    Args:
        query (str): The user's question.
        chunks (List[str]): A list of relevant text chunks to use as context.
        return_debug (bool): If True, returns additional debug information.

    Returns:
        str: The cleaned answer, or an error message if an exception occurs.
             If `return_debug` is True, returns a tuple: (answer, prompt, raw_output, elapsed_time).
    """
    context = "\n---\n".join(chunks)
    prompt = build_prompt(context, query)

    t0 = time.time()

    try:
        logger.info(f"Calling Ollama model '{OLLAMA_MODEL_NAME}' with query: {query[:50]}...")
        response = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "num_predict": NUM_PREDICT
            }
        )
        raw_output = response['message']['content']
        answer = clean_answer(raw_output)
        elapsed = time.time() - t0
        logger.info(f"Ollama call completed in {elapsed:.2f}s.")

        if return_debug:
            return answer, prompt, raw_output, elapsed
        return answer

    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        if return_debug:
            return "ERROR", prompt, str(e), 0.0
        return 'ERROR'