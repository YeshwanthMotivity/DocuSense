from typing import List
from transformers import PreTrainedTokenizerBase

def chunk_text(text: str, tokenizer: PreTrainedTokenizerBase, max_tokens: int = 1024) -> List[str]:
    """
    Splits a long text into token-based chunks, ensuring each chunk does not exceed
    a specified maximum token limit.

    This function first tokenizes the entire input text into a list of token IDs.
    It then iterates through these token IDs, creating sub-lists (chunks of token IDs)
    each adhering to the `max_tokens` limit. Finally, these token ID chunks are
    decoded back into readable text strings.

    Args:
        text (str): The full input text to be chunked.
        tokenizer (PreTrainedTokenizerBase): An instantiated tokenizer object
            (e.g., from `transformers.AutoTokenizer.from_pretrained` or `transformers.GPT2Tokenizer`).
            This improves modularity, testability, and allows for using different tokenizers.
        max_tokens (int): The maximum number of tokens allowed per chunk.
            Defaults to 1024.

    Returns:
        List[str]: A list of text strings, where each string is a chunk
            and its token count is less than or equal to `max_tokens`.
    """
    # Optimize tokenization: encode the entire input text into token IDs once.
    input_ids = tokenizer.encode(text)

    # Split token IDs into sub-lists (chunks) that adhere to max_tokens
    chunks_of_ids = [input_ids[i : i + max_tokens] for i in range(0, len(input_ids), max_tokens)]

    # Decode the token ID sub-lists back into text
    # skip_special_tokens=True is generally desired for content chunks
    text_chunks = [tokenizer.decode(chunk_ids, skip_special_tokens=True) for chunk_ids in chunks_of_ids]

    return text_chunks