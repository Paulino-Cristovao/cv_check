"""Main Gradio application for CV Check."""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import gradio as gr

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DocxParser
from analyzer.resume_analyzer import ResumeAnalyzer
from analyzer.job_analyzer import JobAnalyzer
from analyzer.scorer import CompatibilityScorer
from analyzer.gap_analyzer import GapAnalyzer
from generator.interview_prep import InterviewPrepGenerator
from generator.word_generator import WordDocumentGenerator
from generator.recommendations import RecommendationGenerator
from utils.openai_client import OpenAIClient
from utils.helpers import setup_logging, sanitize_text

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


class CVCheckApp:
    """Main application class for CV Check."""

    def __init__(self) -> None:
        """Initialize the CV Check application."""
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()
        self.resume_analyzer = ResumeAnalyzer()
        self.job_analyzer = JobAnalyzer()
        self.scorer = CompatibilityScorer()
        self.gap_analyzer = GapAnalyzer()
        self.recommendation_generator = RecommendationGenerator()
        self.word_generator = WordDocumentGenerator()

        # Initialize OpenAI client
        self.openai_client = self._initialize_openai_client()
        if self.openai_client:
            self.interview_prep_generator: Optional[
                InterviewPrepGenerator
            ] = InterviewPrepGenerator(self.openai_client)
        else:
            self.interview_prep_generator = None

    def _initialize_openai_client(self) -> Optional[OpenAIClient]:
        """Initialize OpenAI client with API key."""
        try:
            return OpenAIClient()
        except ValueError as e:
            logger.error(f"OpenAI client initialization failed: {str(e)}")
            return None

    def parse_resume(self, file_path: Optional[str]) -> Optional[str]:
        """
        Parse resume file and extract text.

        Args:
            file_path: Path to the uploaded resume file

        Returns:
            Extracted text or None if parsing fails
        """
        if not file_path or not os.path.exists(file_path):
            return None

        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == ".pdf":
                result = self.pdf_parser.parse(file_path)
                return result if isinstance(result, str) else None
            if file_ext in [".docx", ".doc"]:
                result = self.docx_parser.parse(file_path)
                return result if isinstance(result, str) else None

            logger.error(f"Unsupported file format: {file_ext}")
            return None

        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return None

    def analyze_resume_job_match(
        self, resume_file: Optional[str], job_description: str
    ) -> Tuple[int, str, str, str, Optional[str]]:
        """
        Analyze resume against job description and return results.

        Args:
            resume_file: Path to uploaded resume file
            job_description: Job description text

        Returns:
            Tuple of (score, strong_points, weak_points, improvements, interview_prep_file)
        """
        try:
            # Validate inputs
            if not resume_file or not job_description.strip():
                return (
                    0,
                    "❌ Please upload a resume and provide a job description.",
                    "",
                    "",
                    None,
                )

            # Parse resume
            resume_text = self.parse_resume(resume_file)
            if not resume_text:
                return (
                    0,
                    "❌ Failed to parse resume. Please check the file format (PDF or DOCX).",
                    "",
                    "",
                    None,
                )

            # Sanitize inputs
            resume_text = sanitize_text(resume_text)
            job_description = sanitize_text(job_description)

            # Analyze resume and job
            resume_data = self.resume_analyzer.analyze(resume_text)
            job_requirements = self.job_analyzer.analyze(job_description)

            # Calculate compatibility score
            score, score_breakdown = self.scorer.calculate_score(
                resume_data, job_requirements
            )

            # Perform gap analysis
            strong_points, weak_points, _ = self.gap_analyzer.analyze_gaps(
                resume_data, job_requirements, score_breakdown
            )

            # Generate detailed recommendations
            detailed_recommendations = (
                self.recommendation_generator.generate_recommendations(
                    resume_data, job_requirements, weak_points, score_breakdown
                )
            )

            # Format outputs
            strong_points_text = self._format_strong_points(strong_points)
            weak_points_text = self._format_weak_points(weak_points)
            improvements_text = self._format_improvements(detailed_recommendations)

            # Generate interview preparation document
            interview_prep_file = None
            if self.interview_prep_generator:
                interview_prep_file = self._generate_interview_prep_document(
                    resume_data, job_requirements, score_breakdown
                )

            return (
                score,
                strong_points_text,
                weak_points_text,
                improvements_text,
                interview_prep_file,
            )

        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            return (0, f"❌ Analysis failed: {str(e)}", "", "", None)

    def _format_strong_points(self, strong_points: list) -> str:
        """Format strong points for display."""
        if not strong_points:
            return "No specific strong points identified."

        formatted = "## 🎯 Strong Points\n\n"
        for i, point in enumerate(strong_points, 1):
            formatted += f"**{i}. {point.get('point', 'Strong point')}**\n"
            formatted += f"*{point.get('category', 'General')}*\n\n"
            formatted += f"{point.get('explanation', '')}\n\n"
            if point.get("leverage"):
                formatted += f"💡 **How to leverage:** {point['leverage']}\n\n"
            formatted += "---\n\n"

        return formatted

    def _format_weak_points(self, weak_points: list) -> str:
        """Format weak points for display."""
        if not weak_points:
            return "No significant weak points identified."

        formatted = "## ⚠️ Areas for Improvement\n\n"
        for i, point in enumerate(weak_points, 1):
            formatted += f"**{i}. {point.get('point', 'Improvement area')}**\n"
            formatted += f"*{point.get('category', 'General')}*\n\n"
            formatted += f"{point.get('explanation', '')}\n\n"
            if point.get("impact"):
                formatted += f"📊 **Impact:** {point['impact']}\n\n"
            formatted += "---\n\n"

        return formatted

    def _format_improvements(self, improvements: list) -> str:
        """Format improvement recommendations for display."""
        if not improvements:
            return "No specific improvements recommended."

        formatted = "## 🚀 Specific Recommendations\n\n"
        for i, rec in enumerate(improvements, 1):
            priority = rec.get("priority", "Medium")
            priority_emoji = (
                "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
            )

            formatted += f"**{i}. {rec.get('recommendation', 'Recommendation')}** {priority_emoji}\n"
            formatted += f"*{rec.get('category', 'General')} - {priority} Priority*\n\n"
            formatted += f"**Action:** {rec.get('action', '')}\n\n"
            formatted += f"**Impact:** {rec.get('impact', '')}\n\n"
            if rec.get("implementation"):
                formatted += f"**Implementation:** {rec['implementation']}\n\n"
            formatted += "---\n\n"

        return formatted

    def _generate_interview_prep_document(
        self, resume_data: Any, job_requirements: Any, score_breakdown: Dict[str, Any]
    ) -> Optional[str]:
        """Generate interview preparation document."""
        if not self.interview_prep_generator:
            return None

        try:
            # Generate prep content using OpenAI
            prep_content = self.interview_prep_generator.generate_prep_content(
                resume_data, job_requirements, score_breakdown
            )

            if not prep_content:
                logger.warning("Failed to generate interview prep content")
                return None

            # Generate Word document
            doc_path = self.word_generator.generate_interview_prep_document(
                prep_content, job_requirements.title, job_requirements.company
            )

            return doc_path if isinstance(doc_path, str) else None

        except Exception as e:
            logger.error(f"Error generating interview prep document: {str(e)}")
            return None

    def create_gradio_interface(self) -> gr.Blocks:
        """Create and configure Gradio interface."""

        # Custom CSS for better styling
        css = """
        .gradio-container {
            max-width: 1200px !important;
        }
        .score-display {
            font-size: 2em !important;
            font-weight: bold !important;
            text-align: center !important;
        }
        """

        with gr.Blocks(css=css, title="CV Check - PhD Resume Optimizer") as interface:
            # Header
            gr.Markdown(
                """
            # 🎯 CV Check - PhD Resume Optimizer
            ### AI-powered resume analysis for PhD holders in the French job market
            
            Upload your resume and paste a job description to get:
            - **Compatibility Score** (0-100)
            - **Strong Points** analysis with leverage tips
            - **Weak Points** identification with impact assessment  
            - **Specific Improvements** with actionable recommendations
            - **Interview Preparation** document (Word format)
            """
            )

            with gr.Row():
                with gr.Column(scale=1):
                    # Input section
                    gr.Markdown("## 📄 Input")

                    resume_file = gr.File(
                        label="Upload Resume (PDF or DOCX)",
                        file_types=[".pdf", ".docx", ".doc"],
                        type="filepath",
                    )

                    job_description = gr.Textbox(
                        label="Job Description",
                        placeholder="Paste the complete job description here...",
                        lines=10,
                        max_lines=15,
                    )

                    analyze_btn = gr.Button(
                        "🔍 Analyze Resume", variant="primary", size="lg"
                    )

                with gr.Column(scale=2):
                    # Output section
                    gr.Markdown("## 📊 Analysis Results")

                    with gr.Row():
                        score_display = gr.Number(
                            label="Compatibility Score",
                            precision=0,
                            elem_classes=["score-display"],
                        )

                    with gr.Tabs():
                        with gr.TabItem("💪 Strong Points"):
                            strong_points_output = gr.Markdown()

                        with gr.TabItem("⚠️ Weak Points"):
                            weak_points_output = gr.Markdown()

                        with gr.TabItem("🚀 Improvements"):
                            improvements_output = gr.Markdown()

            # Interview prep download section
            with gr.Row():
                gr.Markdown("## 📋 Interview Preparation")
                interview_prep_file = gr.File(
                    label="Download Interview Preparation Guide (Word Document)",
                    visible=True,
                )

            # Footer
            gr.Markdown(
                """
            ---
            **Tips for best results:**
            - Upload a complete, up-to-date resume
            - Provide the full job description including requirements and responsibilities
            - Review all recommendations carefully before implementing changes
            - Use the interview preparation guide to practice your responses
            
            *Built for PhD holders navigating the French job market* 🇫🇷
            """
            )

            # Connect the analysis function
            analyze_btn.click(
                fn=self.analyze_resume_job_match,
                inputs=[resume_file, job_description],
                outputs=[
                    score_display,
                    strong_points_output,
                    weak_points_output,
                    improvements_output,
                    interview_prep_file,
                ],
            )

        return interface


def main() -> None:
    """Main entry point for the application."""
    try:
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
            print("Please set your OpenAI API key to enable full functionality.")
            print("Example: export OPENAI_API_KEY='your-api-key-here'")
            return

        # Initialize and launch app
        app = CVCheckApp()
        interface = app.create_gradio_interface()

        print("🚀 Starting CV Check application...")
        print("📊 AI-powered resume optimization for PhD holders")
        print("🌐 Gradio will show the local URL when ready...")

        interface.launch(
            server_name="0.0.0.0",
            server_port=None,  # Let Gradio find an available port
            share=False,
            show_error=True,
        )

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        print(f"❌ Error starting application: {str(e)}")


if __name__ == "__main__":
    main()
