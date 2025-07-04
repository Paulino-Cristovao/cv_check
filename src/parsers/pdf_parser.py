"""PDF parser for extracting text from PDF resumes."""

import logging
from typing import Optional
from pathlib import Path
import PyPDF2

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for extracting text from PDF documents."""

    def __init__(self) -> None:
        """Initialize the PDF parser."""
        self.supported_extensions = [".pdf"]

    def parse(self, file_path: str) -> Optional[str]:
        """
        Parse PDF file and extract text content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content or None if parsing fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
                
            if path.suffix.lower() not in self.supported_extensions:
                logger.error(f"Unsupported file format: {path.suffix}")
                return None

            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()
                
                if not text.strip():
                    logger.warning(f"No text extracted from {file_path}")
                    return None
                    
                return text.strip()
                
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            return None

    def is_supported(self, file_path: str) -> bool:
        """
        Check if file format is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if supported, False otherwise
        """
        return Path(file_path).suffix.lower() in self.supported_extensions