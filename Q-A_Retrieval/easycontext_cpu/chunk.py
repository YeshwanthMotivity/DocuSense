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
    Splits a long text into token-based chunks, ensuring each chunk does not exceed max_tokens.

    This function first tokenizes the entire text using the specified tokenizer, then iterates
    through the resulting token IDs to create sub-lists of token IDs, each respecting the
    `max_tokens` limit. These token ID chunks are then decoded back into text strings.

    If `concat_chunks` is True, these initial token-based text chunks are further grouped
    and joined according to `concat_factor`.

    Args:
        text (str): The full input text to be chunked.
        max_tokens (int): The maximum number of tokens allowed per chunk.
                          Defaults to 2048.
        tokenizer_name (str): The name of the Hugging Face tokenizer to use
                              (e.g., "gpt2", "bert-base-uncased"). Defaults to "gpt2".
        concat_chunks (bool): If True, concatenates the initial token-based chunks
                              into larger units based on `concat_factor`.
                              This step happens *after* initial token-based chunking.
                              Defaults to False.
        concat_factor (int): The number of initial token-based chunks to concatenate
                             together when `concat_chunks` is True. Must be greater than 1
                             for concatenation to occur. Defaults to 2.

    Returns:
        List[str]: A list of text chunks. Each chunk in the list will either
                   respect the `max_tokens` limit (if `concat_chunks` is False)
                   or be a concatenation of such chunks (if `concat_chunks` is True).
                   Empty strings resulting from decoding and stripping are filtered out.
    """
    if not text:
        return []

    # Pass Tokenizer as Argument: Initialize tokenizer using the provided name
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)

    # Optimize Tokenization Strategy: Tokenize the entire text once
    # Use add_special_tokens=False to ensure max_tokens applies purely to content
    input_ids = tokenizer.encode(text, add_special_tokens=False)

    # Handle Overly Long Words: This is implicitly handled by tokenizing the entire text
    # and then splitting the `input_ids`. If a "word" (or any sequence) is very long
    # in terms of tokens, its tokens will naturally span across multiple `max_tokens`
    # chunks if necessary, ensuring no single chunk exceeds the token limit.

    # Break input_ids into token ID chunks
    token_chunks_ids: List[List[int]] = []
    for i in range(0, len(input_ids), max_tokens):
        token_chunks_ids.append(input_ids[i : i + max_tokens])

    # Decode token ID chunks back to text strings
    initial_text_chunks: List[str] = [
        tokenizer.decode(chunk_id, skip_special_tokens=True).strip()
        for chunk_id in token_chunks_ids
    ]
    # Filter out any potentially empty strings that might result from stripping
    initial_text_chunks = [chunk for chunk in initial_text_chunks if chunk]

    # Remove Redundant `concat_chunks` Parameter Check:
    # Keep `concat_factor > 1` explicitly as `concat_factor=1` implies no meaningful concatenation.
    if concat_chunks and concat_factor > 1:
        final_chunks: List[str] = []
        for i in range(0, len(initial_text_chunks), concat_factor):
            # Join multiple initial chunks together
            combined_chunk = " ".join(initial_text_chunks[i : i + concat_factor]).strip()
            if combined_chunk:
                final_chunks.append(combined_chunk)
        return final_chunks
    
    return initial_text_chunks