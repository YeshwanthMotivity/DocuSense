import os
import functools
from typing import Optional
from transformers import AutoTokenizer

def load_file(filepath: str) -> str:
    """Load text content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except IOError as e:
        raise IOError(f"Error reading file '{filepath}': {e}")


@functools.lru_cache(maxsize=128)
def _get_tokenizer(tokenizer_name: str):
    return AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)

def count_tokens(text: str, tokenizer_name: str = "gpt2") -> int:
    """Count the number of tokens using a tokenizer."""
    tokenizer = _get_tokenizer(tokenizer_name)
    return len(tokenizer.encode(text))


def save_file(content: str, filepath: str):
    """Save generated text or processed content to file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Failed to save content to file '{filepath}' due to an I/O error: {e}")