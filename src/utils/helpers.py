"""Helper functions for the CV Check application."""

import logging
import re
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("cv_check.log"),
            logging.StreamHandler()
        ]
    )


def sanitize_text(text: str) -> str:
    """
    Clean and sanitize text content.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-.,;:!?()@#%&*+=/\[\]{}|\\~`"\'<>]', '', text)
    
    # Remove multiple consecutive punctuation marks
    text = re.sub(r'([.,;:!?]){2,}', r'\1', text)
    
    return text.strip()


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.
    
    Args:
        text: Input text
        
    Returns:
        Email address if found, None otherwise
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group() if match else None


def extract_phone(text: str) -> Optional[str]:
    """
    Extract phone number from text.
    
    Args:
        text: Input text
        
    Returns:
        Phone number if found, None otherwise
    """
    # French phone number patterns
    phone_patterns = [
        r'\+33\s?[1-9](?:[\s.-]?\d{2}){4}',  # +33 format
        r'0[1-9](?:[\s.-]?\d{2}){4}',        # 0X format
        r'\d{10}',                           # 10 digits
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of words
    """
    return len(text.split()) if text else 0


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."