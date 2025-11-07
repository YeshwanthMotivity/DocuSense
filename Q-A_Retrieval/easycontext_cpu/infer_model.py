import re
import time
import ollama
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STOP_TOKENS = ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]

def build_prompt(context: str, query: str) -> str:
    """
    Constructs the content for the user's message to the Ollama chat model.

    The prompt instructs the model to act as a helpful assistant and answer
    strictly from the provided context, ending with an explicit "Answer:"
    to encourage direct response generation.

    Args:
        context: The relevant context information, typically a concatenation of text chunks.
        query: The user's question.

    Returns:
        A formatted string to be used as the 'content' for the user role in ollama.chat.
    """
    return (
        "You are a helpful assistant. Answer strictly using the following context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\nAnswer:"
    )

def clean_answer(text: str) -> str:
    """
    Cleans the raw model output by removing stop tokens, redundant phrases,
    and excessive whitespace.

    Args:
        text: The raw string output from the language model.

    Returns:
        A cleaned string, typically the extracted answer.
    """
    for tok in STOP_TOKENS:
        text = text.replace(tok, " ")
    text = re.sub(r"\s+", " ", text).strip()

    boring_phrases = [
        r"based (solely|entirely)? on the (provided )?context[, ]*",
        r"according to the context[, ]*",
        r"the context (states|says) that[, ]*",
    ]
    for pattern in boring_phrases:
        text = re.sub("^" + pattern, "", text, flags=re.IGNORECASE).strip()

    return text

def generate_answer(
    query: str,
    chunks: list[str],
    ollama_model: str = 'phi',
    temperature: float = 0.3,
    top_p: float = 0.9,
    num_predict: int = 350,
    return_debug: bool = False
) -> str | tuple[str, str, str, float]:
    """
    Generates a context-aware answer using an Ollama-compatible language model.

    Args:
        query: The question to be answered.
        chunks: A list of relevant text chunks to provide as context.
        ollama_model: The name of the model to use from Ollama (e.g., 'phi', 'llama2').
        temperature: Controls randomness in generation. Lower values make output more deterministic.
        top_p: Controls nucleus sampling. A higher value means the model considers more tokens.
        num_predict: The maximum number of tokens to predict in the response.
        return_debug: If True, returns a tuple containing (answer, prompt, raw_output, elapsed_time).
                      Otherwise, returns only the cleaned answer.

    Returns:
        The cleaned answer string, or a tuple with debug information if `return_debug` is True.

    Raises:
        RuntimeError: If there is an error communicating with the Ollama service
                      or processing its response.
    """
    context = "\n---\n".join(chunks)
    prompt = build_prompt(context, query)

    t0 = time.time()

    try:
        logger.info(f"Calling Ollama model '{ollama_model}' with options: temperature={temperature}, top_p={top_p}, num_predict={num_predict}")
        response = ollama.chat(
            model=ollama_model,
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
        logger.info(f"Ollama call done in {elapsed:.2f}s for model '{ollama_model}'")

        if return_debug:
            return answer, prompt, raw_output, elapsed
        return answer

    except ollama.ResponseError as e:
        logger.error(f"Ollama API error: {e}")
        if return_debug:
            return "ERROR", prompt, str(e), 0.0
        raise RuntimeError(f"Ollama API error: {e}") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama call: {e}", exc_info=True)
        if return_debug:
            return "ERROR", prompt, str(e), 0.0
        raise RuntimeError(f"Failed to generate answer: {e}") from e