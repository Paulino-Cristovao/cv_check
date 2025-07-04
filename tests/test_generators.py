"""Tests for generator modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.generator.recommendations import RecommendationGenerator
from src.generator.word_generator import WordDocumentGenerator
from src.generator.interview_prep import InterviewPrepGenerator
from src.analyzer.resume_analyzer import ResumeData
from src.analyzer.job_analyzer import JobRequirements
from src.utils.openai_client import OpenAIClient


class TestRecommendationGenerator:
    """Test cases for RecommendationGenerator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.generator = RecommendationGenerator()

    def test_init(self) -> None:
        """Test generator initialization."""
        assert isinstance(self.generator, RecommendationGenerator)

    def test_generate_recommendations_basic(self) -> None:
        """Test basic recommendation generation."""
        resume_data = ResumeData(
            contact_info={"email": "test@email.com"},
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
            keywords=["python", "developer"]
        )
        
        weak_points = [{"category": "Skills", "point": "Missing JavaScript"}]
        score_breakdown = {"skills_match": 50}
        
        recommendations = self.generator.generate_recommendations(
            resume_data, job_requirements, weak_points, score_breakdown
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 8

    def test_generate_skills_recommendations(self) -> None:
        """Test skills-related recommendations."""
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
        
        score_breakdown = {"skills_match": 40}
        
        recommendations = self.generator._generate_skills_recommendations(
            resume_data, job_requirements, score_breakdown
        )
        
        assert len(recommendations) > 0
        assert any("Skills" in rec["category"] for rec in recommendations)

    def test_generate_phd_recommendations(self) -> None:
        """Test PhD-specific recommendations."""
        resume_data = ResumeData(
            contact_info={},
            education=[{"degree": "PhD", "field": "Computer Science"}],
            experience=[],
            skills=[],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=True,
            academic_background=True
        )
        
        job_requirements = JobRequirements(
            title="Junior Developer",
            company=None,
            required_skills=[],
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
        
        score_breakdown = {"overqualification_penalty": 30}
        
        recommendations = self.generator._generate_phd_recommendations(
            resume_data, job_requirements, score_breakdown
        )
        
        assert len(recommendations) > 0
        assert any("PhD" in rec["category"] for rec in recommendations)


class TestWordDocumentGenerator:
    """Test cases for WordDocumentGenerator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.generator = WordDocumentGenerator()

    def test_init(self) -> None:
        """Test generator initialization."""
        assert isinstance(self.generator.output_dir, Path)

    @patch('docx.Document')
    @patch('pathlib.Path.mkdir')
    def test_generate_interview_prep_document_success(
        self, mock_mkdir: Mock, mock_document: Mock
    ) -> None:
        """Test successful document generation."""
        # Mock document
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        prep_content = {
            "company_analysis": {"overview": "Company overview"},
            "interview_questions": [
                {"category": "Technical", "question": "What is Python?"}
            ],
            "suggested_answers": {"technical_example": "Example answer"},
            "star_stories": [
                {"title": "Project Story", "situation": "Test situation"}
            ],
            "questions_to_ask": [
                {"category": "Role", "question": "What does the role involve?"}
            ],
            "salary_insights": {"market_context": "French market info"},
            "overqualification_tips": [
                {"concern": "PhD concern", "strategy": "Strategy"}
            ]
        }
        
        result = self.generator.generate_interview_prep_document(
            prep_content, "Software Engineer", "Tech Corp"
        )
        
        assert result is not None
        assert result.endswith(".docx")
        mock_doc.save.assert_called_once()

    @patch('docx.Document')
    def test_generate_interview_prep_document_exception(self, mock_document: Mock) -> None:
        """Test document generation with exception."""
        mock_document.side_effect = Exception("Document error")
        
        prep_content = {"company_analysis": {}}
        
        result = self.generator.generate_interview_prep_document(
            prep_content, "Software Engineer"
        )
        
        assert result is None

    def test_setup_document_styles(self) -> None:
        """Test document styles setup."""
        with patch('docx.Document') as mock_document:
            mock_doc = MagicMock()
            mock_styles = MagicMock()
            mock_doc.styles = mock_styles
            mock_document.return_value = mock_doc
            
            # Test that the method doesn't raise an exception
            self.generator._setup_document_styles(mock_doc)


class TestInterviewPrepGenerator:
    """Test cases for InterviewPrepGenerator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.utils.openai_client.OpenAI'):
                self.openai_client = OpenAIClient()
                self.generator = InterviewPrepGenerator(self.openai_client)

    def test_init(self) -> None:
        """Test generator initialization."""
        assert self.generator.openai_client == self.openai_client

    def test_generate_prep_content_success(self) -> None:
        """Test successful prep content generation."""
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
            title="Software Engineer",
            company="Tech Corp",
            required_skills=["Python"],
            preferred_skills=[],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location="Paris",
            industry="Technology",
            company_size=None,
            job_level="mid",
            keywords=[]
        )
        
        analysis_results = {"acceptance_score": 80}
        
        result = self.generator.generate_prep_content(
            resume_data, job_requirements, analysis_results
        )
        
        assert result is not None
        assert isinstance(result, dict)
        expected_keys = [
            "company_analysis", "interview_questions", "suggested_answers",
            "star_stories", "questions_to_ask", "salary_insights"
        ]
        for key in expected_keys:
            assert key in result

    def test_generate_company_analysis(self) -> None:
        """Test company analysis generation."""
        job_requirements = JobRequirements(
            title="Software Engineer",
            company="Tech Corp",
            required_skills=[],
            preferred_skills=[],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location="Paris",
            industry="Technology",
            company_size="100 employees",
            job_level="mid",
            keywords=[]
        )
        
        analysis = self.generator._generate_company_analysis(job_requirements)
        
        assert isinstance(analysis, dict)
        assert "overview" in analysis
        assert "industry_context" in analysis

    def test_generate_interview_questions(self) -> None:
        """Test interview questions generation."""
        resume_data = ResumeData(
            contact_info={},
            education=[],
            experience=[],
            skills=["Python"],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=True,
            academic_background=True
        )
        
        job_requirements = JobRequirements(
            title="Software Engineer",
            company="Tech Corp",
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
        
        analysis_results = {}
        
        questions = self.generator._generate_interview_questions(
            resume_data, job_requirements, analysis_results
        )
        
        assert isinstance(questions, list)
        assert len(questions) > 0
        
        # Check for PhD-specific questions
        phd_questions = [q for q in questions if q.get("category") == "PhD Background"]
        assert len(phd_questions) > 0

    def test_generate_star_stories(self) -> None:
        """Test STAR stories generation."""
        resume_data = ResumeData(
            contact_info={},
            education=[],
            experience=[],
            skills=["Python", "JavaScript"],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=True,
            academic_background=True
        )
        
        job_requirements = JobRequirements(
            title="Software Engineer",
            company=None,
            required_skills=[],
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
        
        stories = self.generator._generate_star_stories(resume_data, job_requirements)
        
        assert isinstance(stories, list)
        assert len(stories) > 0
        
        for story in stories:
            assert "title" in story
            assert "situation" in story
            assert "task" in story
            assert "action" in story
            assert "result" in story

    def test_generate_questions_to_ask(self) -> None:
        """Test questions to ask generation."""
        job_requirements = JobRequirements(
            title="Software Engineer",
            company=None,
            required_skills=[],
            preferred_skills=[],
            required_experience=None,
            education_requirements=[],
            languages=[],
            location=None,
            industry="Technology",
            company_size=None,
            job_level="mid",
            keywords=[]
        )
        
        questions = self.generator._generate_questions_to_ask(job_requirements)
        
        assert isinstance(questions, list)
        assert len(questions) > 0
        
        for question in questions:
            assert "category" in question
            assert "question" in question
            assert "purpose" in question

    def test_generate_overqualification_tips_phd(self) -> None:
        """Test overqualification tips for PhD candidate."""
        resume_data = ResumeData(
            contact_info={},
            education=[],
            experience=[],
            skills=[],
            languages=[],
            publications=[],
            certifications=[],
            has_phd=True,
            academic_background=True
        )
        
        job_requirements = JobRequirements(
            title="Junior Developer",
            company=None,
            required_skills=[],
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
        
        tips = self.generator._generate_overqualification_tips(
            resume_data, job_requirements
        )
        
        assert isinstance(tips, list)
        assert len(tips) > 0
        
        for tip in tips:
            assert "concern" in tip
            assert "strategy" in tip
            assert "example" in tip