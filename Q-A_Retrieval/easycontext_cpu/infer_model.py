import ollama
import re
import time

# --- Configuration Constants ---
OLLAMA_MODEL_NAME = 'phi'
DEFAULT_TEMPERATURE = 0.3
DEFAULT_TOP_P = 0.9
DEFAULT_NUM_PREDICT = 350
# --- End Configuration Constants ---

class OllamaConnectionError(Exception):
    """Custom exception for Ollama connection failures."""
    pass

class OllamaModelNotFoundError(Exception):
    """Custom exception for when the specified Ollama model is not found."""
    pass

STOP_TOKENS = ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]

def build_prompt(context: str, query: str) -> str:
    """
    Constructs a prompt for the LLM based on context and query.
    """
    return (
        "You are a helpful assistant. Answer strictly using the following context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\nAnswer:"
    )

def clean_answer(txt: str) -> str:
    """
    Removes trailing stop tokens, boilerplate phrases, and cleans up whitespace.
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
    chunks: list[str],
    ollama_model_name: str = OLLAMA_MODEL_NAME,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    num_predict: int = DEFAULT_NUM_PREDICT,
    return_debug: bool = False
) -> str or tuple:
    """
    Generates an answer using the Ollama model with context.

    Args:
        query (str): The user's question.
        chunks (list[str]): A list of context chunks to use for the answer.
        ollama_model_name (str): The ID of the Ollama model to use (e.g., 'phi').
        temperature (float): Controls randomness; lower values make output more deterministic.
        top_p (float): Nucleus sampling parameter.
        num_predict (int): Maximum number of tokens to predict in the response.
        return_debug (bool): If True, returns debug information along with the answer.

    Returns:
        str or tuple: The cleaned answer string, or a tuple (answer, prompt, raw_output, elapsed_time)
                      if return_debug is True.
    Raises:
        OllamaConnectionError: If there's an issue connecting to the Ollama server.
        OllamaModelNotFoundError: If the specified model is not found on the Ollama server.
        Exception: For other unexpected errors during generation.
    """
    context = "\n---\n".join(chunks)
    prompt = build_prompt(context, query)

    t0 = time.time()

    try:
        print(f"Calling Ollama model '{ollama_model_name}'...")
        response = ollama.chat(
            model=ollama_model_name,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": num_predict
            }
        )
        raw_output = response['message']['content']
        answer = clean_answer(raw_output)
        elapsed = time.time() - t0
        print(f"Ollama call done in {elapsed:.2f}s")

        if return_debug:
            return answer, prompt, raw_output, elapsed
        return answer

    except ollama.ResponseError as e:
        if "no such file or directory" in str(e).lower() or "not found" in str(e).lower():
            raise OllamaModelNotFoundError(
                f"Ollama model '{ollama_model_name}' not found. "
                "Please ensure it's installed and running via `ollama run {model_name}`."
            ) from e
        raise OllamaConnectionError(f"Ollama server responded with an error: {e}") from e
    except Exception as e:
        raise Exception(f"An unexpected error occurred during Ollama generation: {e}") from e