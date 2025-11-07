import os
from typing import Optional
from transformers import AutoTokenizer

def load_file(filepath: str) -> str:
    """Load text content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {filepath}") from e
    except IOError as e:
        raise IOError(f"An I/O error occurred while reading file {filepath}: {e}") from e


def count_tokens(text: str, tokenizer: Optional[AutoTokenizer] = None, tokenizer_name: str = "gpt2") -> int:
    """
    Count the number of tokens using a tokenizer.
    An initialized tokenizer object can be passed to avoid repeated loading.
    """
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    return len(tokenizer.encode(text))


def save_file(content: str, filepath: str):
    """Save generated text or processed content to file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except PermissionError as e:
        raise PermissionError(f"Permission denied to write to file {filepath}: {e}") from e
    except IOError as e:
        raise IOError(f"An I/O error occurred while writing to file {filepath}: {e}") from e