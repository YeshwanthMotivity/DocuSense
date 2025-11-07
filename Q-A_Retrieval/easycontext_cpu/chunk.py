from transformers import AutoTokenizer
from typing import List

def chunk_text(
    text: str,
    max_tokens: int = 2048,
    tokenizer_name: str = "gpt2",
    concat_chunks: bool = False,
    concat_factor: int = 2
) -> List[str]:
    """
    Splits a long text into token-based chunks, ensuring each chunk does not exceed
    a specified maximum token count.

    This function first tokenizes the entire input text using the specified tokenizer
    and then divides the resulting token IDs into sub-lists, each representing a chunk.
    It prioritizes token count over word count for more accurate model compatibility.

    Args:
        text (str): The full input text to be chunked.
        max_tokens (int): The maximum number of tokens allowed per chunk.
                          Defaults to 2048 (common for models like GPT-2/3).
        tokenizer_name (str): The name of the Hugging Face tokenizer to use
                              (e.g., "gpt2", "bert-base-uncased").
                              Defaults to "gpt2".
        concat_chunks (bool): If True, attempts to concatenate adjacent chunks
                              after initial splitting to create larger chunks,
                              while still respecting `max_tokens`. Defaults to False.
        concat_factor (int): The number of initial chunks to attempt to concatenate
                             together if `concat_chunks` is True. Defaults to 2.

    Returns:
        List[str]: A list of text chunks, where each chunk's token count
                   is less than or equal to `max_tokens`.
    """
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    input_ids = tokenizer.encode(text)

    # Break input_ids into initial chunks
    # Each sublist 'chunk' will have length <= max_tokens
    chunks_token_ids: List[List[int]] = [
        input_ids[i:i + max_tokens] for i in range(0, len(input_ids), max_tokens)
    ]

    # Decode initial token ID chunks back to text
    text_chunks: List[str] = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks_token_ids]

    if concat_chunks and concat_factor > 1:
        # Concatenate adjacent chunks, but re-verify token limits
        concatenated_chunks: List[str] = []
        i = 0
        while i < len(text_chunks):
            # Attempt to combine 'concat_factor' chunks
            combined_segment_parts = text_chunks[i : i + concat_factor]
            combined_text = " ".join(combined_segment_parts)
            
            # Re-tokenize the combined text to ensure it still respects max_tokens
            combined_tokens = tokenizer.encode(combined_text)

            if len(combined_tokens) <= max_tokens:
                concatenated_chunks.append(combined_text)
                i += concat_factor
            else:
                # If concatenation exceeds max_tokens, append individual chunks
                # that were part of the attempted combination. This ensures no chunk
                # violates max_tokens and handles cases where one of the initial
                # chunks might itself be very close to the limit.
                concatenated_chunks.append(text_chunks[i])
                i += 1
        return concatenated_chunks

    return text_chunks