from typing import List
from transformers import PreTrainedTokenizer

def chunk_text(text: str, tokenizer: PreTrainedTokenizer, max_tokens: int = 1024, concat_factor: int = 1) -> List[str]:
    """
    Splits a long text into token-based chunks, optionally concatenating them.

    This function first tokenizes the entire input text and then divides the resulting
    token IDs into segments, each containing up to `max_tokens`. These token segments
    are then decoded back into strings. Optionally, these initial text chunks can be
    further concatenated in groups determined by `concat_factor`.

    Args:
        text (str): The input text to be chunked.
        tokenizer (PreTrainedTokenizer): The tokenizer instance (e.g., from transformers library
                                        like `GPT2Tokenizer` or `AutoTokenizer.from_pretrained(...)`).
                                        It should have `encode` and `decode` methods.
        max_tokens (int): The maximum number of tokens allowed per initial chunk.
                          Note: The final chunk might be shorter.
        concat_factor (int): If > 1, initially created chunks will be concatenated
                             in groups of this factor. For example, if `concat_factor` is 2,
                             every two initial `max_tokens` chunks will be joined into one larger chunk.
                             If `concat_factor` is 1, no additional concatenation occurs beyond
                             the initial token-based splitting.

    Returns:
        List[str]: A list of text chunks. Each chunk will approximately respect the
                   `max_tokens` limit (or `max_tokens * concat_factor` if concatenation occurs),
                   though actual word counts may vary.
    """
    # Optimize Token Accumulation: Encode the entire text once to get token IDs.
    # Using add_special_tokens=False to prevent the tokenizer from adding
    # BOS/EOS tokens, which are usually handled at the model input level
    # and might skew chunking token counts.
    input_ids = tokenizer.encode(text, add_special_tokens=False)

    # Split these input_ids directly into chunks. This handles robustly cases
    # like very long "words" or sequences that cross traditional word boundaries.
    token_id_chunks = [input_ids[i:i + max_tokens] for i in range(0, len(input_ids), max_tokens)]

    # Decode token ID chunks back into text strings.
    # skip_special_tokens=True ensures that any special tokens (like [CLS], [SEP])
    # are removed during decoding, producing clean text.
    decoded_chunks = [tokenizer.decode(chunk_ids, skip_special_tokens=True) for chunk_ids in token_id_chunks]

    # Simplify concat_chunks Logic:
    # If concat_factor is greater than 1, concatenate the initially decoded chunks.
    if concat_factor > 1:
        concatenated_final_chunks = []
        for i in range(0, len(decoded_chunks), concat_factor):
            # Join `concat_factor` number of decoded chunks into a single string.
            # Using " " as a separator, which is common for text concatenation.
            concatenated_final_chunks.append(" ".join(decoded_chunks[i:i+concat_factor]))
        return concatenated_final_chunks
    else:
        # If concat_factor is 1 (or less), return the initial decoded chunks without further concatenation.
        return decoded_chunks