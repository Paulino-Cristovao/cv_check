"""Job description analysis module."""

import logging
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class JobRequirements:
    """Structured job requirements data."""
    
    title: str
    company: Optional[str]
    required_skills: List[str]
    preferred_skills: List[str]
    required_experience: Optional[str]
    education_requirements: List[str]
    languages: List[str]
    location: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]
    job_level: str
    keywords: List[str]


class JobAnalyzer:
    """Analyzer for extracting structured data from job descriptions."""

    def __init__(self) -> None:
        """Initialize the job analyzer."""
        self.skill_patterns = [
            r'(?:required|must have|essential)[\s\w]*:?\s*([^\n.]+)',
            r'(?:skills?|technologies?|tools?)[\s\w]*:?\s*([^\n.]+)',
            r'(?:experience with|proficiency in|knowledge of)\s+([^\n.]+)',
        ]
        
        self.experience_patterns = [
            r'(\d+)(?:\+|\s*to\s*\d+)?\s*years?\s*(?:of\s*)?experience',
            r'(?:minimum|at least)\s*(\d+)\s*years?',
            r'(\d+)(?:\+|\-\d+)?\s*ans?\s*d[\'\'\""]expérience',  # French
        ]
        
        self.education_patterns = [
            r'(bachelor|master|phd|doctorate|degree|diploma)',
            r'(bac\+\d+|licence|master|doctorat)',  # French
        ]

    def analyze(self, job_description: str) -> JobRequirements:
        """
        Analyze job description and extract structured requirements.
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Structured job requirements
        """
        try:
            title = self._extract_job_title(job_description)
            company = self._extract_company_name(job_description)
            required_skills, preferred_skills = self._extract_skills(job_description)
            required_experience = self._extract_experience_requirement(job_description)
            education_requirements = self._extract_education_requirements(job_description)
            languages = self._extract_language_requirements(job_description)
            location = self._extract_location(job_description)
            industry = self._extract_industry(job_description)
            company_size = self._extract_company_size(job_description)
            job_level = self._determine_job_level(job_description)
            keywords = self._extract_keywords(job_description)

            return JobRequirements(
                title=title,
                company=company,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                required_experience=required_experience,
                education_requirements=education_requirements,
                languages=languages,
                location=location,
                industry=industry,
                company_size=company_size,
                job_level=job_level,
                keywords=keywords,
            )
            
        except Exception as e:
            logger.error(f"Error analyzing job description: {str(e)}")
            return JobRequirements(
                title="Unknown Position",
                company=None,
                required_skills=[],
                preferred_skills=[],
                required_experience=None,
                education_requirements=[],
                languages=[],
                location=None,
                industry=None,
                company_size=None,
                job_level="unknown",
                keywords=[],
            )

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from description."""
        # Look for common title patterns
        title_patterns = [
            r'(?:job title|position|poste|titre)[\s:]*([^\n]+)',
            r'(?:we are looking for|nous recherchons)[\s\w]*([^\n]+)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: use first line if it looks like a title
        first_line = text.split('\n')[0].strip()
        if len(first_line) < 100 and any(word in first_line.lower() for word in 
                                       ["engineer", "developer", "manager", "analyst", "consultant"]):
            return first_line
        
        return "Position"

    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from description."""
        company_patterns = [
            r'(?:company|société|entreprise)[\s:]*([^\n]+)',
            r'(?:at|chez)\s+([A-Z][^\n,]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _extract_skills(self, text: str) -> tuple[List[str], List[str]]:
        """Extract required and preferred skills."""
        required_skills = []
        preferred_skills = []
        
        # Technical skills keywords
        tech_skills = [
            "python", "java", "javascript", "react", "angular", "vue",
            "sql", "nosql", "mongodb", "postgresql", "mysql",
            "aws", "azure", "gcp", "docker", "kubernetes",
            "machine learning", "ai", "data science", "analytics",
            "agile", "scrum", "git", "ci/cd", "devops"
        ]
        
        text_lower = text.lower()
        
        # Look for required skills sections
        required_sections = re.findall(
            r'(?:required|must have|essential|obligatoire)[\s\w]*:?\s*([^.]+)', 
            text, re.IGNORECASE
        )
        
        for section in required_sections:
            for skill in tech_skills:
                if skill in section.lower():
                    required_skills.append(skill)
        
        # Look for preferred skills sections
        preferred_sections = re.findall(
            r'(?:preferred|nice to have|bonus|souhaité)[\s\w]*:?\s*([^.]+)', 
            text, re.IGNORECASE
        )
        
        for section in preferred_sections:
            for skill in tech_skills:
                if skill in section.lower():
                    preferred_skills.append(skill)
        
        # If no clear sections, categorize all found skills as required
        if not required_skills and not preferred_skills:
            for skill in tech_skills:
                if skill in text_lower:
                    required_skills.append(skill)
        
        return list(set(required_skills)), list(set(preferred_skills))

    def _extract_experience_requirement(self, text: str) -> Optional[str]:
        """Extract experience requirements."""
        for pattern in self.experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        return None

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements."""
        education = []
        
        for pattern in self.education_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append(match.group())
        
        return list(set(education))

    def _extract_language_requirements(self, text: str) -> List[str]:
        """Extract language requirements."""
        language_patterns = [
            r'(?:fluent|native|proficient|bilingual)\s+(?:in\s+)?(\w+)',
            r'(\w+)\s+(?:fluency|proficiency|speaker)',
            r'(?:français|anglais|espagnol|allemand|italien)',
            r'(?:french|english|spanish|german|italian)',
        ]
        
        languages = []
        for pattern in language_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                languages.append(match.group().strip())
        
        return list(set(languages))

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location."""
        location_patterns = [
            r'(?:location|lieu|localisation)[\s:]*([^\n]+)',
            r'(?:based in|situé à|basé à)\s+([^\n,]+)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Look for French cities
        french_cities = ["paris", "lyon", "marseille", "toulouse", "nice", "nantes", "strasbourg"]
        text_lower = text.lower()
        
        for city in french_cities:
            if city in text_lower:
                return city.title()
        
        return None

    def _extract_industry(self, text: str) -> Optional[str]:
        """Extract industry information."""
        industries = [
            "technology", "tech", "software", "fintech", "healthtech",
            "consulting", "finance", "healthcare", "automotive",
            "e-commerce", "retail", "manufacturing", "energy"
        ]
        
        text_lower = text.lower()
        for industry in industries:
            if industry in text_lower:
                return industry.title()
        
        return None

    def _extract_company_size(self, text: str) -> Optional[str]:
        """Extract company size information."""
        size_patterns = [
            r'(\d+)(?:\+|\s*to\s*\d+)?\s*(?:employees|people|personnes)',
            r'(?:startup|start-up|scale-up)',
            r'(?:sme|pme|large company|grande entreprise)',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return None

    def _determine_job_level(self, text: str) -> str:
        """Determine job seniority level."""
        text_lower = text.lower()
        
        senior_keywords = ["senior", "lead", "principal", "architect", "manager", "director"]
        junior_keywords = ["junior", "entry", "graduate", "intern", "débutant"]
        mid_keywords = ["mid", "intermediate", "confirmé"]
        
        if any(keyword in text_lower for keyword in senior_keywords):
            return "senior"
        elif any(keyword in text_lower for keyword in junior_keywords):
            return "junior"
        elif any(keyword in text_lower for keyword in mid_keywords):
            return "mid"
        
        return "mid"  # Default

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from job description."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "a", "an", "is", "are", "was", "were", "be", "been", "have", "has",
            "le", "la", "les", "et", "ou", "mais", "dans", "sur", "à", "pour", "de", "avec"
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Count frequency and return most common
        word_freq: Dict[str, int] = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 20
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:20]]