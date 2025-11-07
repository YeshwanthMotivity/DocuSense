import os
from typing import Optional
from transformers import AutoTokenizer

def load_file(filepath: str) -> str:
    """Load text content from a file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def count_tokens(text: str, tokenizer: Optional[AutoTokenizer] = None, tokenizer_name: str = "gpt2") -> int:
    """
    Count the number of tokens using a tokenizer.
    If a tokenizer object is provided, it will be used. Otherwise, a new tokenizer
    will be loaded using tokenizer_name.
    """
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    return len(tokenizer.encode(text))


def save_file(content: str, filepath: str):
    """Save generated text or processed content to file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Error writing to file '{filepath}': {e}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied when writing to file '{filepath}': {e}")