"""Tests for utility modules."""

import pytest
from unittest.mock import Mock, patch
from src.utils.helpers import (
    sanitize_text, 
    extract_email, 
    extract_phone, 
    count_words, 
    truncate_text
)
from src.utils.openai_client import OpenAIClient


class TestHelpers:
    """Test cases for helper functions."""

    def test_sanitize_text_basic(self) -> None:
        """Test basic text sanitization."""
        text = "  Hello    world!  "
        result = sanitize_text(text)
        assert result == "Hello world!"

    def test_sanitize_text_special_chars(self) -> None:
        """Test sanitization with special characters."""
        text = "Hello@#$%world!!!"
        result = sanitize_text(text)
        assert "@" in result  # Should keep @ symbol
        assert "$" not in result  # Should remove $ symbol

    def test_sanitize_text_empty(self) -> None:
        """Test sanitizing empty text."""
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""

    def test_extract_email_valid(self) -> None:
        """Test email extraction with valid emails."""
        text = "Contact John at john.doe@example.com for more info"
        result = extract_email(text)
        assert result == "john.doe@example.com"

    def test_extract_email_none(self) -> None:
        """Test email extraction with no email."""
        text = "No email address in this text"
        result = extract_email(text)
        assert result is None

    def test_extract_phone_french_format(self) -> None:
        """Test phone extraction with French formats."""
        texts = [
            "Call me at +33 1 23 45 67 89",
            "Phone: 01 23 45 67 89",
            "Contact: 0123456789"
        ]
        
        for text in texts:
            result = extract_phone(text)
            assert result is not None

    def test_extract_phone_none(self) -> None:
        """Test phone extraction with no phone."""
        text = "No phone number here"
        result = extract_phone(text)
        assert result is None

    def test_count_words(self) -> None:
        """Test word counting."""
        assert count_words("hello world") == 2
        assert count_words("") == 0
        assert count_words("one") == 1
        assert count_words("  multiple   spaces  between  words  ") == 4

    def test_truncate_text_no_truncation(self) -> None:
        """Test text truncation when no truncation needed."""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        assert result == text

    def test_truncate_text_with_truncation(self) -> None:
        """Test text truncation when truncation needed."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 20
        assert result.endswith("...")


class TestOpenAIClient:
    """Test cases for OpenAI client."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = OpenAIClient(api_key="test-key")
            assert client.api_key == "test-key"
            assert client.model == "gpt-4"

    def test_init_no_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                OpenAIClient()

    def test_init_from_environment(self) -> None:
        """Test initialization from environment variable."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'}):
            client = OpenAIClient()
            assert client.api_key == "env-key"

    @patch('src.utils.openai_client.OpenAI')
    def test_generate_completion_success(self, mock_openai: Mock) -> None:
        """Test successful completion generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = OpenAIClient()
            result = client.generate_completion("Test prompt")
            
            assert result == "Generated response"
            mock_client.chat.completions.create.assert_called_once()

    @patch('src.utils.openai_client.OpenAI')
    def test_generate_completion_failure(self, mock_openai: Mock) -> None:
        """Test completion generation failure."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = OpenAIClient()
            result = client.generate_completion("Test prompt")
            
            assert result is None

    @patch('src.utils.openai_client.OpenAI')
    def test_analyze_resume_job_match_success(self, mock_openai: Mock) -> None:
        """Test successful resume-job analysis."""
        # Mock OpenAI response with JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "acceptance_score": 85,
            "score_reasoning": "Good match",
            "strong_points": ["Technical skills", "Experience"],
            "weak_points": ["Missing some skills"],
            "improvements": ["Add more keywords"]
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = OpenAIClient()
            result = client.analyze_resume_job_match("Resume text", "Job description")
            
            assert result is not None
            assert isinstance(result, dict)
            assert "acceptance_score" in result

    @patch('src.utils.openai_client.OpenAI')
    def test_analyze_resume_job_match_invalid_json(self, mock_openai: Mock) -> None:
        """Test resume-job analysis with invalid JSON response."""
        # Mock OpenAI response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = OpenAIClient()
            result = client.analyze_resume_job_match("Resume text", "Job description")
            
            assert result is None

    @patch('src.utils.openai_client.OpenAI')
    def test_generate_interview_prep_success(self, mock_openai: Mock) -> None:
        """Test successful interview prep generation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Interview preparation content"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = OpenAIClient()
            result = client.generate_interview_prep(
                "Resume text", 
                "Job description", 
                {"acceptance_score": 80}
            )
            
            assert result == "Interview preparation content"