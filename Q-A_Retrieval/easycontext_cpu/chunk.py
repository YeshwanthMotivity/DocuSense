from transformers import AutoTokenizer
from typing import List

def chunk_text(text: str, tokenizer: AutoTokenizer, max_tokens: int = 1024, concat_chunks: bool = False, concat_factor: int = 2) -> List[str]:
    """
    Splits a long text into chunks, ensuring each chunk (before optional concatenation)
    does not exceed a specified maximum number of tokens. Chunks are split on word boundaries.

    Args:
        text (str): The full input text to be chunked.
        tokenizer (AutoTokenizer): An instantiated tokenizer object (e.g., from transformers.AutoTokenizer).
                                   This allows for flexible and efficient tokenization.
        max_tokens (int): The maximum number of tokens allowed per chunk (before optional concatenation).
                          If a single word's token length exceeds this, that word will form a chunk
                          that itself exceeds `max_tokens`.
        concat_chunks (bool): If True, attempts to concatenate smaller chunks into larger ones
                              after initial splitting.
        concat_factor (int): The number of initial chunks to concatenate together if `concat_chunks` is True.
                             Note: Concatenated chunks can significantly exceed `max_tokens`.

    Returns:
        List[str]: A list of text chunks, each respecting the token limits (with the caveat
                   for single-word chunks exceeding `max_tokens`) and optional concatenation.
    """
    words = text.split()
    chunks = []
    current_chunk_token_ids: List[int] = []

    for word in words:
        # Determine token IDs for the current word. Prepend a space if it's not the first word
        # in the current accumulating chunk to accurately reflect tokenization with spaces.
        if not current_chunk_token_ids:
            word_token_ids = tokenizer.encode(word, add_special_tokens=False)
        else:
            word_token_ids = tokenizer.encode(" " + word, add_special_tokens=False)

        # Check if adding this word (and its preceding space if applicable) would exceed max_tokens
        if len(current_chunk_token_ids) + len(word_token_ids) > max_tokens:
            # If the current chunk is empty, it means the 'word' itself exceeds max_tokens.
            # In this case, we must add the 'word' as a chunk on its own.
            if not current_chunk_token_ids:
                chunks.append(tokenizer.decode(word_token_ids, skip_special_tokens=True))
                # Reset to ensure the next word starts a new chunk properly, even if this one was huge.
                current_chunk_token_ids = []
            else:
                # The current word makes the chunk too large. Finalize the current chunk.
                chunks.append(tokenizer.decode(current_chunk_token_ids, skip_special_tokens=True))
                # Start a new chunk with the current word.
                current_chunk_token_ids = word_token_ids
        else:
            # Add the word's tokens to the current accumulating chunk
            current_chunk_token_ids.extend(word_token_ids)

    # Add the last chunk if any tokens remain
    if current_chunk_token_ids:
        chunks.append(tokenizer.decode(current_chunk_token_ids, skip_special_tokens=True))

    if concat_chunks and concat_factor > 1:
        # Concatenate adjacent chunks.
        # Note: These concatenated chunks can exceed the original 'max_tokens' limit.
        return [" ".join(chunks[i:i + concat_factor])
                for i in range(0, len(chunks), concat_factor)]
    return chunks