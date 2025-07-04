"""Resume analysis module for extracting candidate information."""

import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResumeData:
    """Structured resume data."""
    
    contact_info: Dict[str, Optional[str]]
    education: List[Dict[str, str]]
    experience: List[Dict[str, str]]
    skills: List[str]
    languages: List[str]
    publications: List[str]
    certifications: List[str]
    has_phd: bool
    academic_background: bool


class ResumeAnalyzer:
    """Analyzer for extracting structured data from resume text."""

    def __init__(self) -> None:
        """Initialize the resume analyzer."""
        self.phd_keywords = [
            "phd", "ph.d", "doctorate", "doctoral", "doctor of philosophy",
            "dissertation", "thesis", "research", "publication", "postdoc"
        ]
        self.academic_keywords = [
            "university", "professor", "academic", "researcher", "scholar",
            "laboratory", "lab", "institute", "faculty", "postdoctoral"
        ]

    def analyze(self, resume_text: str) -> ResumeData:
        """
        Analyze resume text and extract structured data.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Structured resume data
        """
        try:
            resume_lower = resume_text.lower()
            
            contact_info = self._extract_contact_info(resume_text)
            education = self._extract_education(resume_text)
            experience = self._extract_experience(resume_text)
            skills = self._extract_skills(resume_text)
            languages = self._extract_languages(resume_text)
            publications = self._extract_publications(resume_text)
            certifications = self._extract_certifications(resume_text)
            has_phd = self._detect_phd(resume_lower)
            academic_background = self._detect_academic_background(resume_lower)

            return ResumeData(
                contact_info=contact_info,
                education=education,
                experience=experience,
                skills=skills,
                languages=languages,
                publications=publications,
                certifications=certifications,
                has_phd=has_phd,
                academic_background=academic_background,
            )
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            return ResumeData(
                contact_info={},
                education=[],
                experience=[],
                skills=[],
                languages=[],
                publications=[],
                certifications=[],
                has_phd=False,
                academic_background=False,
            )

    def _extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from resume."""
        contact: Dict[str, Optional[str]] = {"email": None, "phone": None, "location": None}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact["email"] = email_match.group()
        
        # Phone (French formats)
        phone_patterns = [
            r'\+33\s?[1-9](?:[\s.-]?\d{2}){4}',
            r'0[1-9](?:[\s.-]?\d{2}){4}',
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact["phone"] = phone_match.group()
                break
        
        # Location (basic extraction)
        location_keywords = ["paris", "lyon", "marseille", "toulouse", "nice", "france"]
        for keyword in location_keywords:
            if keyword in text.lower():
                contact["location"] = keyword.title()
                break
        
        return contact

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume."""
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(phd|ph\.d|doctorate|doctoral|doctor of philosophy)[\s\w]*(?:in\s+)?([^\n,]+)',
            r'(master|m\.s|m\.a|msc|ma)[\s\w]*(?:in\s+)?([^\n,]+)',
            r'(bachelor|b\.s|b\.a|bsc|ba)[\s\w]*(?:in\s+)?([^\n,]+)',
            r'(engineering degree|diplôme d\'ingénieur)[\s\w]*(?:in\s+)?([^\n,]+)',
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match.group(1),
                    "field": match.group(2).strip() if len(match.groups()) > 1 else "",
                    "type": "degree"
                })
        
        return education

    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume."""
        experience = []
        
        # Look for job titles and companies
        experience_keywords = [
            "engineer", "developer", "manager", "analyst", "consultant",
            "researcher", "scientist", "professor", "director", "lead"
        ]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            for keyword in experience_keywords:
                if keyword in line_lower and len(line.strip()) > 10:
                    experience.append({
                        "title": line.strip(),
                        "type": "work_experience"
                    })
                    break
        
        return experience[:5]  # Limit to top 5 entries

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume."""
        # Common technical skills
        skill_keywords = [
            "python", "java", "javascript", "c++", "sql", "html", "css",
            "machine learning", "data science", "artificial intelligence",
            "project management", "agile", "scrum", "git", "docker",
            "aws", "azure", "linux", "windows", "excel", "powerpoint"
        ]
        
        skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())
        
        return list(set(skills))  # Remove duplicates

    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from resume."""
        language_keywords = [
            "french", "english", "spanish", "german", "italian",
            "français", "anglais", "espagnol", "allemand", "italien"
        ]
        
        languages = []
        text_lower = text.lower()
        
        for language in language_keywords:
            if language in text_lower:
                languages.append(language.title())
        
        return list(set(languages))

    def _extract_publications(self, text: str) -> List[str]:
        """Extract publications from resume."""
        publications = []
        
        # Look for publication patterns
        pub_patterns = [
            r'(?:published|publication|paper|article|journal).*["\']([^"\']+)["\']',
            r'(\d{4}).*(?:published|journal|conference).*([^\n]+)',
        ]
        
        for pattern in pub_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                publications.append(match.group().strip())
        
        return publications[:3]  # Limit to top 3

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume."""
        cert_keywords = [
            "certified", "certification", "certificate", "diploma",
            "aws certified", "microsoft certified", "google certified",
            "pmp", "scrum master", "agile"
        ]
        
        certifications = []
        text_lower = text.lower()
        
        for cert in cert_keywords:
            if cert in text_lower:
                certifications.append(cert.title())
        
        return list(set(certifications))

    def _detect_phd(self, text_lower: str) -> bool:
        """Detect if candidate has a PhD."""
        return any(keyword in text_lower for keyword in self.phd_keywords)

    def _detect_academic_background(self, text_lower: str) -> bool:
        """Detect if candidate has strong academic background."""
        academic_count = sum(1 for keyword in self.academic_keywords if keyword in text_lower)
        return academic_count >= 2 or self._detect_phd(text_lower)