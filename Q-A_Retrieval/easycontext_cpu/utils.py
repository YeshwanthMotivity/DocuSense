import os
from typing import Optional
from transformers import AutoTokenizer

_tokenizer_cache = {}

def get_tokenizer(tokenizer_name: str = "gpt2"):
    """Get a tokenizer from cache or load it if not present."""
    if tokenizer_name not in _tokenizer_cache:
        _tokenizer_cache[tokenizer_name] = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    return _tokenizer_cache[tokenizer_name]

def load_file(filepath: str) -> str:
    """Load text content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied when trying to read file: {filepath}. Error: {e}")
    except IOError as e:
        raise IOError(f"An I/O error occurred while loading file: {filepath}. Error: {e}")

def count_tokens(text: str, tokenizer_name: str = "gpt2") -> int:
    """Count the number of tokens using a tokenizer."""
    tokenizer = get_tokenizer(tokenizer_name)
    return len(tokenizer.encode(text))

def save_file(content: str, filepath: str):
    """Save generated text or processed content to file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)