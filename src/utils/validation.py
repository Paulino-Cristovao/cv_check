"""Input validation and security guardrails for CV Check application."""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    error_message: str
    confidence_score: float  # 0-100
    detected_issues: List[str]


class SecurityGuardrails:
    """Security and content validation for preventing misuse."""

    def __init__(self):
        """Initialize validation patterns and rules."""
        
        # Prompt injection patterns
        self.injection_patterns = [
            r"ignore\s+(?:previous|all|above|prior)\s+(?:instructions?|prompts?|rules?)",
            r"(?:forget|disregard|bypass)\s+(?:your|the)\s+(?:instructions?|rules?|guidelines?)",
            r"(?:act|pretend|roleplay)\s+(?:as|like)\s+(?:a|an)?\s*(?:different|other)",
            r"you\s+are\s+(?:now|a|an)\s+(?:different|new|other)",
            r"(?:system|admin|root|developer)\s*(?:mode|access|override)",
            r"(?:tell|show|give)\s+me\s+(?:your|the)\s+(?:prompt|instructions?|system)",
            r"what\s+(?:are|were)\s+(?:your|the)\s+(?:original|initial)\s+instructions",
            r"(?:reveal|expose|show)\s+(?:hidden|secret|internal)\s+(?:prompt|instructions?)",
            r"(?:jailbreak|exploit|hack|bypass)\s+(?:the|your)\s+(?:system|ai|model)",
            r"(?:\\n|\\r|\\t|\\\\|\/\*|\*\/|<script|javascript:|data:)",  # Code injection
        ]
        
        # CV/Resume required elements
        self.cv_patterns = [
            r"(?:name|full\s+name)[\s:]+[A-Z][a-z]+\s+[A-Z][a-z]+",
            r"(?:email|e-mail)[\s:]*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            r"(?:phone|mobile|tel|telephone)[\s:]*[\+]?[\d\s\-\(\)]{8,}",
            r"(?:education|qualifications?|degree|university|college)",
            r"(?:experience|employment|work\s+history|career)",
            r"(?:skills?|competenc|abilit|proficient)",
            r"(?:address|location|city|country)",
        ]
        
        # Job description required elements
        self.job_patterns = [
            r"(?:position|role|job\s+title|we\s+are\s+(?:looking|seeking|hiring))",
            r"(?:responsibilities?|duties|tasks?|what\s+you.ll\s+do)",
            r"(?:requirements?|qualifications?|ideal\s+candidate|experience)",
            r"(?:company|organization|about\s+us|our\s+(?:company|team))",
            r"(?:location|office|remote|hybrid|work\s+from)",
            r"(?:salary|compensation|package|benefits?|offer)",
        ]
        
        # Suspicious content patterns
        self.suspicious_patterns = [
            r"(?:test|testing|example|sample|demo)\s+(?:resume|cv|job)",
            r"lorem\s+ipsum",
            r"placeholder\s+text",
            r"(?:fake|dummy|mock)\s+(?:data|content|information)",
            r"(?:john|jane)\s+doe",
            r"example\s*[@\.]",
            r"test\s*[@\.]",
            r"(?:123|456|999)[\-\s]*(?:123|456|999)",  # Fake phone numbers
        ]

    def validate_resume(self, text: str) -> ValidationResult:
        """Validate that the input is a legitimate resume/CV."""
        
        if not text or len(text.strip()) < 100:
            return ValidationResult(
                is_valid=False,
                error_message="Resume text is too short. Please provide a complete resume.",
                confidence_score=0.0,
                detected_issues=["Insufficient content length"]
            )
        
        # Check for prompt injection
        injection_score = self._check_injection_attempts(text)
        if injection_score > 0.3:
            return ValidationResult(
                is_valid=False,
                error_message="Input contains suspicious content. Please provide a legitimate resume.",
                confidence_score=0.0,
                detected_issues=["Potential prompt injection detected"]
            )
        
        # Check for CV elements
        cv_score = self._check_cv_elements(text)
        if cv_score < 0.4:
            return ValidationResult(
                is_valid=False,
                error_message="This doesn't appear to be a resume. Please upload a complete CV with personal information, education, experience, and skills.",
                confidence_score=cv_score * 100,
                detected_issues=["Missing essential resume elements"]
            )
        
        # Check for suspicious/fake content
        suspicious_score = self._check_suspicious_content(text)
        if suspicious_score > 0.2:
            return ValidationResult(
                is_valid=False,
                error_message="This appears to be test or placeholder content. Please provide a real resume.",
                confidence_score=(1 - suspicious_score) * 100,
                detected_issues=["Suspicious or fake content detected"]
            )
        
        return ValidationResult(
            is_valid=True,
            error_message="",
            confidence_score=cv_score * 100,
            detected_issues=[]
        )

    def validate_job_description(self, text: str) -> ValidationResult:
        """Validate that the input is a legitimate job description."""
        
        if not text or len(text.strip()) < 150:
            return ValidationResult(
                is_valid=False,
                error_message="Job description is too short. Please provide a complete job posting.",
                confidence_score=0.0,
                detected_issues=["Insufficient content length"]
            )
        
        # Check for prompt injection
        injection_score = self._check_injection_attempts(text)
        if injection_score > 0.3:
            return ValidationResult(
                is_valid=False,
                error_message="Input contains suspicious content. Please provide a legitimate job description.",
                confidence_score=0.0,
                detected_issues=["Potential prompt injection detected"]
            )
        
        # Check for job description elements
        job_score = self._check_job_elements(text)
        if job_score < 0.3:
            return ValidationResult(
                is_valid=False,
                error_message="This doesn't appear to be a job description. Please provide a complete job posting with role details, requirements, and company information.",
                confidence_score=job_score * 100,
                detected_issues=["Missing essential job description elements"]
            )
        
        # Check for suspicious/fake content
        suspicious_score = self._check_suspicious_content(text)
        if suspicious_score > 0.2:
            return ValidationResult(
                is_valid=False,
                error_message="This appears to be test or placeholder content. Please provide a real job description.",
                confidence_score=(1 - suspicious_score) * 100,
                detected_issues=["Suspicious or fake content detected"]
            )
        
        return ValidationResult(
            is_valid=True,
            error_message="",
            confidence_score=job_score * 100,
            detected_issues=[]
        )

    def _check_injection_attempts(self, text: str) -> float:
        """Check for prompt injection attempts."""
        text_lower = text.lower()
        matches = 0
        
        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                matches += 1
                logger.warning(f"Potential injection pattern detected: {pattern}")
        
        return min(matches / 3.0, 1.0)  # Normalize to 0-1

    def _check_cv_elements(self, text: str) -> float:
        """Check for essential CV elements."""
        matches = 0
        text_lower = text.lower()
        
        for pattern in self.cv_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                matches += 1
        
        return min(matches / len(self.cv_patterns), 1.0)

    def _check_job_elements(self, text: str) -> float:
        """Check for essential job description elements."""
        matches = 0
        text_lower = text.lower()
        
        for pattern in self.job_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                matches += 1
        
        return min(matches / len(self.job_patterns), 1.0)

    def _check_suspicious_content(self, text: str) -> float:
        """Check for suspicious or fake content."""
        matches = 0
        text_lower = text.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                matches += 1
        
        return min(matches / 2.0, 1.0)  # Normalize to 0-1

    def sanitize_input(self, text: str) -> str:
        """Sanitize input text for processing."""
        if not text:
            return ""
        
        # Remove potential script tags and dangerous characters
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'data:', '', text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Limit length
        if len(text) > 50000:  # 50KB limit
            text = text[:50000]
        
        return text.strip()


class ContentValidator:
    """High-level content validation coordinator."""

    def __init__(self):
        """Initialize the content validator."""
        self.guardrails = SecurityGuardrails()

    def validate_inputs(self, resume_text: str, job_text: str) -> Tuple[bool, str]:
        """
        Validate both resume and job description inputs.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        
        # Sanitize inputs
        resume_text = self.guardrails.sanitize_input(resume_text)
        job_text = self.guardrails.sanitize_input(job_text)
        
        # Validate resume
        resume_result = self.guardrails.validate_resume(resume_text)
        if not resume_result.is_valid:
            return False, f"Resume validation failed: {resume_result.error_message}"
        
        # Validate job description
        job_result = self.guardrails.validate_job_description(job_text)
        if not job_result.is_valid:
            return False, f"Job description validation failed: {job_result.error_message}"
        
        logger.info(f"Validation passed - Resume confidence: {resume_result.confidence_score:.1f}%, Job confidence: {job_result.confidence_score:.1f}%")
        
        return True, ""