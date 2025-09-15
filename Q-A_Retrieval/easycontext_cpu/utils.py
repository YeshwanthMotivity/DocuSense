# easycontext_cpu/utils.py

import os
from typing import Optional
from transformers import AutoTokenizer

def load_file(filepath: str) -> str:
    """Load text content from a file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def count_tokens(text: str, tokenizer_name: str = "gpt2") -> int:
    """Count the number of tokens using a tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    return len(tokenizer.encode(text))


def save_file(content: str, filepath: str):
    """Save generated text or processed content to file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
