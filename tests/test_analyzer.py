"""Tests for analyzer modules."""

import pytest
from unittest.mock import Mock, patch
from src.analyzer.resume_analyzer import ResumeAnalyzer, ResumeData
from src.analyzer.job_analyzer import JobAnalyzer, JobRequirements
from src.analyzer.scorer import CompatibilityScorer
from src.analyzer.gap_analyzer import GapAnalyzer


class TestResumeAnalyzer:
    """Test cases for ResumeAnalyzer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = ResumeAnalyzer()

    def test_init(self) -> None:
        """Test analyzer initialization."""
        assert isinstance(self.analyzer.phd_keywords, list)
        assert isinstance(self.analyzer.academic_keywords, list)
        assert "phd" in self.analyzer.phd_keywords
        assert "university" in self.analyzer.academic_keywords

    def test_analyze_empty_text(self) -> None:
        """Test analyzing empty resume text."""
        result = self.analyzer.analyze("")
        assert isinstance(result, ResumeData)
        assert result.has_phd is False
        assert result.academic_background is False

    def test_analyze_phd_resume(self) -> None:
        """Test analyzing resume with PhD."""
        resume_text = """
        John Doe
        john.doe@email.com
        +33 1 23 45 67 89
        PhD in Computer Science from University of Paris
        Research experience in machine learning
        Publications in top-tier journals
        Python, machine learning, data science
        """
        
        result = self.analyzer.analyze(resume_text)
        assert result.has_phd is True
        assert result.academic_background is True
        assert result.contact_info["email"] == "john.doe@email.com"
        assert len(result.skills) > 0
        assert any("python" in skill.lower() for skill in result.skills)

    def test_analyze_non_phd_resume(self) -> None:
        """Test analyzing resume without PhD."""
        resume_text = """
        Jane Smith
        jane.smith@email.com
        Software Engineer
        Bachelor in Computer Science
        5 years experience in web development
        JavaScript, React, Node.js
        """
        
        result = self.analyzer.analyze(resume_text)
        assert result.has_phd is False
        assert len(result.skills) > 0

    def test_detect_phd_variations(self) -> None:
        """Test PhD detection with various formats."""
        texts_with_phd = [
            "PhD in Computer Science",
            "Ph.D in Mathematics", 
            "Doctor of Philosophy",
            "Doctoral degree in Physics",
            "Dissertation research"
        ]
        
        for text in texts_with_phd:
            result = self.analyzer._detect_phd(text.lower())
            assert result is True

    def test_contact_info_extraction(self) -> None:
        """Test contact information extraction."""
        text = """
        John Doe
        john.doe@university.edu
        +33 6 12 34 56 78
        Paris, France
        """
        
        contact = self.analyzer._extract_contact_info(text)
        assert contact["email"] == "john.doe@university.edu"
        assert contact["phone"] is not None
        assert contact["location"] is not None

    def test_skills_extraction(self) -> None:
        """Test skills extraction."""
        text = "Experience with Python, machine learning, SQL, and project management"
        skills = self.analyzer._extract_skills(text)
        
        expected_skills = ["Python", "Machine Learning", "Sql", "Project Management"]
        for expected in expected_skills:
            assert any(expected.lower() in skill.lower() for skill in skills)


class TestJobAnalyzer:
    """Test cases for JobAnalyzer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = JobAnalyzer()

    def test_init(self) -> None:
        """Test analyzer initialization."""
        assert isinstance(self.analyzer.skill_patterns, list)
        assert isinstance(self.analyzer.experience_patterns, list)

    def test_analyze_basic_job_description(self) -> None:
        """Test analyzing basic job description."""
        job_desc = """
        Software Engineer Position
        We are looking for a talented software engineer
        Required skills: Python, JavaScript, SQL
        Minimum 3 years of experience
        Bachelor's degree required
        Location: Paris, France
        """
        
        result = self.analyzer.analyze(job_desc)
        assert isinstance(result, JobRequirements)
        assert len(result.required_skills) > 0
        assert result.location is not None

    def test_extract_experience_requirements(self) -> None:
        """Test experience requirement extraction."""
        texts = [
            "Minimum 5 years of experience",
            "3+ years experience required",
            "2 to 4 years of experience"
        ]
        
        for text in texts:
            result = self.analyzer._extract_experience_requirement(text)
            assert result is not None

    def test_determine_job_level(self) -> None:
        """Test job level determination."""
        senior_text = "Senior Software Engineer position"
        junior_text = "Junior Developer role for fresh graduates"
        mid_text = "Mid-level engineer with some experience"
        
        assert self.analyzer._determine_job_level(senior_text) == "senior"
        assert self.analyzer._determine_job_level(junior_text) == "junior"
        assert self.analyzer._determine_job_level(mid_text) == "mid"

    def test_extract_skills(self) -> None:
        """Test skills extraction from job description."""
        job_text = """
        Required skills: Python, JavaScript, React
        Nice to have: Docker, Kubernetes
        Experience with SQL databases preferred
        """
        
        required, preferred = self.analyzer._extract_skills(job_text)
        assert len(required) > 0 or len(preferred) > 0


class TestCompatibilityScorer:
    """Test cases for CompatibilityScorer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.scorer = CompatibilityScorer()

    def test_init(self) -> None:
        """Test scorer initialization."""
        assert isinstance(self.scorer.weights, dict)
        assert "skills_match" in self.scorer.weights

    def test_calculate_score_basic(self) -> None:
        """Test basic score calculation."""
        # Create mock resume data
        resume_data = ResumeData(
            contact_info={"email": "test@email.com"},
            education=[{"degree": "Master", "field": "Computer Science"}],
            experience=[{"title": "Software Engineer"}],
            skills=["Python", "JavaScript"],
            languages=["English", "French"],
            publications=[],
            certifications=[],
            has_phd=False,
            academic_background=False
        )
        
        # Create mock job requirements
        job_requirements = JobRequirements(
            title="Software Engineer",
            company="Tech Corp",
            required_skills=["Python", "JavaScript"],
            preferred_skills=["React"],
            required_experience="2 years",
            education_requirements=["Bachelor"],
            languages=["English"],
            location="Paris",
            industry="Technology",
            company_size="100 employees",
            job_level="mid",
            keywords=["software", "engineer", "python"]
        )
        
        score, breakdown = self.scorer.calculate_score(resume_data, job_requirements)
        assert 0 <= score <= 100
        assert isinstance(breakdown, dict)

    def test_phd_overqualification_penalty(self) -> None:
        """Test PhD overqualification penalty."""
        # PhD candidate for junior role
        resume_data = ResumeData(
            contact_info={},
            education=[{"degree": "PhD", "field": "Computer Science"}],
            experience=[],
            skills=["Python"],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=True,
            academic_background=True
        )
        
        job_requirements = JobRequirements(
            title="Junior Developer",
            company=None,
            required_skills=["Python"],
            preferred_skills=[],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location=None,
            industry=None,
            company_size=None,
            job_level="junior",
            keywords=[]
        )
        
        penalty = self.scorer._calculate_overqualification_penalty(resume_data, job_requirements)
        assert penalty > 0  # Should have penalty for junior role

    def test_skills_match_calculation(self) -> None:
        """Test skills matching calculation."""
        resume_data = ResumeData(
            contact_info={},
            education=[],
            experience=[],
            skills=["Python", "JavaScript", "React"],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=False,
            academic_background=False
        )
        
        job_requirements = JobRequirements(
            title="Developer",
            company=None,
            required_skills=["Python", "JavaScript"],
            preferred_skills=["React"],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location=None,
            industry=None,
            company_size=None,
            job_level="mid",
            keywords=[]
        )
        
        score = self.scorer._calculate_skills_match(resume_data, job_requirements)
        assert score > 80  # Should have high match


class TestGapAnalyzer:
    """Test cases for GapAnalyzer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = GapAnalyzer()

    def test_init(self) -> None:
        """Test analyzer initialization."""
        assert isinstance(self.analyzer, GapAnalyzer)

    def test_analyze_gaps_basic(self) -> None:
        """Test basic gap analysis."""
        resume_data = ResumeData(
            contact_info={},
            education=[],
            experience=[],
            skills=["Python"],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=False,
            academic_background=False
        )
        
        job_requirements = JobRequirements(
            title="Developer",
            company=None,
            required_skills=["Python", "JavaScript"],
            preferred_skills=[],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location=None,
            industry=None,
            company_size=None,
            job_level="mid",
            keywords=[]
        )
        
        score_breakdown = {"skills_match": 60, "experience_match": 70}
        
        strong_points, weak_points, improvements = self.analyzer.analyze_gaps(
            resume_data, job_requirements, score_breakdown
        )
        
        assert isinstance(strong_points, list)
        assert isinstance(weak_points, list)
        assert isinstance(improvements, list)

    def test_find_missing_skills(self) -> None:
        """Test missing skills identification."""
        resume_data = ResumeData(
            contact_info={},
            education=[],
            experience=[],
            skills=["Python"],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=False,
            academic_background=False
        )
        
        job_requirements = JobRequirements(
            title="Developer",
            company=None,
            required_skills=["Python", "JavaScript", "React"],
            preferred_skills=[],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location=None,
            industry=None,
            company_size=None,
            job_level="mid",
            keywords=[]
        )
        
        missing = self.analyzer._find_missing_skills(resume_data, job_requirements)
        assert "Javascript" in missing or "React" in missing

    def test_find_matching_skills(self) -> None:
        """Test matching skills identification."""
        resume_data = ResumeData(
            contact_info={},
            education=[],
            experience=[],
            skills=["Python", "JavaScript"],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=False,
            academic_background=False
        )
        
        job_requirements = JobRequirements(
            title="Developer",
            company=None,
            required_skills=["Python", "React"],
            preferred_skills=["JavaScript"],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location=None,
            industry=None,
            company_size=None,
            job_level="mid",
            keywords=[]
        )
        
        matching = self.analyzer._find_matching_skills(resume_data, job_requirements)
        assert len(matching) > 0
        assert any("python" in skill.lower() for skill in matching)