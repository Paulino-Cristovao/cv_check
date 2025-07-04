"""Tests for document parsers."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.parsers.pdf_parser import PDFParser
from src.parsers.docx_parser import DocxParser


class TestPDFParser:
    """Test cases for PDFParser."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = PDFParser()

    def test_init(self) -> None:
        """Test parser initialization."""
        assert self.parser.supported_extensions == [".pdf"]

    def test_is_supported_pdf(self) -> None:
        """Test PDF file format support."""
        assert self.parser.is_supported("test.pdf") is True
        assert self.parser.is_supported("test.PDF") is True

    def test_is_supported_non_pdf(self) -> None:
        """Test non-PDF file format support."""
        assert self.parser.is_supported("test.docx") is False
        assert self.parser.is_supported("test.txt") is False

    def test_parse_nonexistent_file(self) -> None:
        """Test parsing non-existent file."""
        result = self.parser.parse("nonexistent.pdf")
        assert result is None

    def test_parse_unsupported_format(self) -> None:
        """Test parsing unsupported file format."""
        with patch('pathlib.Path.exists', return_value=True):
            result = self.parser.parse("test.txt")
            assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data=b'mock pdf data')
    @patch('PyPDF2.PdfReader')
    @patch('pathlib.Path.exists', return_value=True)
    def test_parse_successful(self, mock_exists: Mock, mock_reader: Mock, mock_file: Mock) -> None:
        """Test successful PDF parsing."""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text content"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_reader.return_value = mock_reader_instance

        result = self.parser.parse("test.pdf")
        assert result == "Sample text content"

    @patch('builtins.open', new_callable=mock_open, read_data=b'mock pdf data')
    @patch('PyPDF2.PdfReader')
    @patch('pathlib.Path.exists', return_value=True)
    def test_parse_empty_content(self, mock_exists: Mock, mock_reader: Mock, mock_file: Mock) -> None:
        """Test parsing PDF with empty content."""
        # Mock PDF reader with empty text
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_reader.return_value = mock_reader_instance

        result = self.parser.parse("test.pdf")
        assert result is None

    @patch('builtins.open', side_effect=Exception("File error"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_parse_exception(self, mock_exists: Mock, mock_file: Mock) -> None:
        """Test parsing with exception."""
        result = self.parser.parse("test.pdf")
        assert result is None


class TestDocxParser:
    """Test cases for DocxParser."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = DocxParser()

    def test_init(self) -> None:
        """Test parser initialization."""
        assert self.parser.supported_extensions == [".docx", ".doc"]

    def test_is_supported_docx(self) -> None:
        """Test DOCX file format support."""
        assert self.parser.is_supported("test.docx") is True
        assert self.parser.is_supported("test.doc") is True
        assert self.parser.is_supported("test.DOCX") is True

    def test_is_supported_non_docx(self) -> None:
        """Test non-DOCX file format support."""
        assert self.parser.is_supported("test.pdf") is False
        assert self.parser.is_supported("test.txt") is False

    def test_parse_nonexistent_file(self) -> None:
        """Test parsing non-existent file."""
        result = self.parser.parse("nonexistent.docx")
        assert result is None

    def test_parse_unsupported_format(self) -> None:
        """Test parsing unsupported file format."""
        with patch('pathlib.Path.exists', return_value=True):
            result = self.parser.parse("test.txt")
            assert result is None

    @patch('docx.Document')
    @patch('pathlib.Path.exists', return_value=True)
    def test_parse_successful(self, mock_exists: Mock, mock_document: Mock) -> None:
        """Test successful DOCX parsing."""
        # Mock document with paragraphs
        mock_paragraph = Mock()
        mock_paragraph.text = "Sample paragraph text"
        
        mock_doc_instance = Mock()
        mock_doc_instance.paragraphs = [mock_paragraph]
        mock_doc_instance.tables = []
        
        mock_document.return_value = mock_doc_instance

        result = self.parser.parse("test.docx")
        assert result == "Sample paragraph text"

    @patch('docx.Document')
    @patch('pathlib.Path.exists', return_value=True)
    def test_parse_with_tables(self, mock_exists: Mock, mock_document: Mock) -> None:
        """Test parsing DOCX with tables."""
        # Mock document with paragraphs and tables
        mock_paragraph = Mock()
        mock_paragraph.text = "Paragraph text"
        
        mock_cell = Mock()
        mock_cell.text = "Cell text"
        mock_row = Mock()
        mock_row.cells = [mock_cell]
        mock_table = Mock()
        mock_table.rows = [mock_row]
        
        mock_doc_instance = Mock()
        mock_doc_instance.paragraphs = [mock_paragraph]
        mock_doc_instance.tables = [mock_table]
        
        mock_document.return_value = mock_doc_instance

        result = self.parser.parse("test.docx")
        assert "Paragraph text" in result
        assert "Cell text" in result

    @patch('docx.Document')
    @patch('pathlib.Path.exists', return_value=True)
    def test_parse_empty_content(self, mock_exists: Mock, mock_document: Mock) -> None:
        """Test parsing DOCX with empty content."""
        # Mock document with empty content
        mock_paragraph = Mock()
        mock_paragraph.text = ""
        
        mock_doc_instance = Mock()
        mock_doc_instance.paragraphs = [mock_paragraph]
        mock_doc_instance.tables = []
        
        mock_document.return_value = mock_doc_instance

        result = self.parser.parse("test.docx")
        assert result is None

    @patch('docx.Document', side_effect=Exception("Document error"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_parse_exception(self, mock_exists: Mock, mock_document: Mock) -> None:
        """Test parsing with exception."""
        result = self.parser.parse("test.docx")
        assert result is None