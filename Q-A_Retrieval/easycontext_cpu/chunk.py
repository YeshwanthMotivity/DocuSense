# utils/chunk_codebase.py

from transformers import AutoTokenizer
from typing import List

# def chunk_text(text: str, max_tokens: int = 2048, tokenizer_name: str = "gpt2") -> List[str]:
#     """Split a long text into token chunks of size <= max_tokens."""
#     tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
#     input_ids = tokenizer.encode(text)

#     # Break input_ids into chunks
#     chunks = [input_ids[i:i + max_tokens] for i in range(0, len(input_ids), max_tokens)]

#     # Decode chunks back to text
#     text_chunks = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]
#     return text_chunks

# import re

# def chunk_text(text, max_words=500):
#     """
#     Splits text into chunks of max_words words each,
#     attempting to split at sentence boundaries.

#     Args:
#         text (str): The full input text.
#         max_words (int): Maximum words per chunk.

#     Returns:
#         List[str]: List of text chunks.
#     """

#     # Split the text into sentences using punctuation marks as delimiters
#     sentences = re.split(r'(?<=[.!?])\s+', text.strip())

#     chunks = []
#     current_chunk = []

#     current_word_count = 0

#     for sentence in sentences:
#         sentence_word_count = len(sentence.split())

#         # If adding this sentence exceeds max_words, finalize current chunk
#         if current_word_count + sentence_word_count > max_words:
#             # Join sentences to form a chunk
#             chunks.append(" ".join(current_chunk))
#             current_chunk = []
#             current_word_count = 0

#         # Add current sentence to chunk
#         current_chunk.append(sentence)
#         current_word_count += sentence_word_count

#     # Add the last chunk if any sentences remain
#     if current_chunk:
#         chunks.append(" ".join(current_chunk))

#     return chunks

# easycontext_cpu/chunk.py

from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def chunk_text(text, max_tokens=1024,concat_chunks=False,concat_factor=2):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        tokens = tokenizer.encode(" ".join(current_chunk))
        if len(tokens) > max_tokens:
            current_chunk.pop()  # Remove last word to keep under limit
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    if concat_chunks and concat_factor > 1:
        return [" ".join(chunks[i:i+concat_factor])
                for i in range(0, len(chunks), concat_factor)]
    return chunks


