"""
Utility functions and helpers
"""
import os
import hashlib
from datetime import datetime
from typing import Any, Dict


def generate_id(prefix: str, text: str) -> str:
    """Generate a unique ID"""
    hash_obj = hashlib.md5(text.encode())
    return f"{prefix}_{hash_obj.hexdigest()[:8]}"


def ensure_dir(directory: str):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)


def format_date(date: datetime) -> str:
    """Format datetime to string"""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (value / total) * 100
