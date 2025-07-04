"""Main Gradio application for CV Check."""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime
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

            # Always generate a comprehensive results document
            results_file = self._generate_complete_results_document(
                resume_data, job_requirements, score_breakdown, score,
                strong_points, weak_points, detailed_recommendations
            )

            return (
                score,
                strong_points_text,
                weak_points_text,
                improvements_text,
                results_file,
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

    def _generate_complete_results_document(
        self,
        resume_data: Any,
        job_requirements: Any,
        score_breakdown: Dict[str, Any],
        score: int,
        strong_points: list,
        weak_points: list,
        recommendations: list,
    ) -> Optional[str]:
        """Generate a comprehensive results document with all analysis."""
        try:
            # Create comprehensive content including basic analysis
            complete_content = {
                "analysis_summary": {
                    "score": score,
                    "candidate_name": resume_data.contact_info.get("name", "Candidate"),
                    "job_title": job_requirements.title[:100],  # Limit length
                    "company": job_requirements.company or "Company",
                    "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "score_breakdown": score_breakdown,
                "strong_points": strong_points,
                "weak_points": weak_points,
                "recommendations": recommendations,
                "resume_summary": {
                    "education": resume_data.education,
                    "experience_count": len(resume_data.experience),
                    "skills_count": len(resume_data.skills),
                    "has_phd": resume_data.has_phd,
                },
                "job_summary": {
                    "required_skills": job_requirements.required_skills,
                    "preferred_skills": job_requirements.preferred_skills,
                    "experience_required": job_requirements.required_experience,
                    "location": job_requirements.location,
                },
            }

            # Try to generate interview prep content if OpenAI is available
            if self.interview_prep_generator:
                try:
                    prep_content = self.interview_prep_generator.generate_prep_content(
                        resume_data, job_requirements, score_breakdown
                    )
                    if prep_content:
                        complete_content["interview_preparation"] = prep_content
                except Exception as e:
                    logger.warning(f"Could not generate AI interview prep: {str(e)}")
                    complete_content["interview_preparation"] = {
                        "note": "Advanced interview preparation requires OpenAI integration"
                    }
            else:
                # Provide basic interview preparation without AI
                complete_content["interview_preparation"] = self._generate_basic_interview_prep(
                    resume_data, job_requirements, strong_points, weak_points
                )

            # Generate Word document with all content
            doc_path = self.word_generator.generate_complete_analysis_document(
                complete_content, job_requirements.title, job_requirements.company
            )

            return doc_path if isinstance(doc_path, str) else None

        except Exception as e:
            logger.error(f"Error generating complete results document: {str(e)}")
            return None

    def _generate_basic_interview_prep(
        self, resume_data: Any, job_requirements: Any, strong_points: list, weak_points: list
    ) -> Dict[str, Any]:
        """Generate basic interview preparation without AI."""
        return {
            "company_research": {
                "about": f"Research {job_requirements.company or 'the company'} thoroughly before the interview",
                "mission": "Understand their mission, values, and recent developments",
                "industry": f"Learn about the {job_requirements.industry or 'industry'} trends",
            },
            "common_questions": [
                "Tell me about yourself",
                "Why are you interested in this position?",
                "What are your greatest strengths?",
                "What are your areas for improvement?",
                "Where do you see yourself in 5 years?",
                "Why are you leaving your current position?",
                "What interests you about our company?",
                "Describe a challenging project you worked on",
                "How do you handle stress and pressure?",
                "Do you have any questions for us?",
            ],
            "star_method": {
                "situation": "Describe the context or background",
                "task": "Explain what you needed to accomplish",
                "action": "Detail the specific actions you took",
                "result": "Share the outcomes and what you learned",
            },
            "questions_to_ask": [
                "What does success look like in this role?",
                "What are the biggest challenges facing the team?",
                "How would you describe the company culture?",
                "What opportunities are there for professional development?",
                "What are the next steps in the interview process?",
            ],
            "based_on_analysis": {
                "leverage_strengths": [point.get("point", "") for point in strong_points[:3]],
                "address_concerns": [point.get("point", "") for point in weak_points[:3]],
            },
        }

    def create_gradio_interface(self) -> gr.Blocks:
        """Create and configure a professional Gradio interface."""

        # Blue, white, and black color scheme with high contrast
        css = """
        /* Main container styling */
        .gradio-container {
            max-width: 1400px !important;
            margin: 0 auto !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            background-color: #ffffff !important;
        }
        
        /* Header styling - Blue gradient */
        .header-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
            color: white !important;
            padding: 2rem !important;
            border-radius: 12px !important;
            margin-bottom: 2rem !important;
            text-align: center !important;
            box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3) !important;
        }
        
        /* Score display styling - Blue theme */
        .score-container {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
            color: white !important;
            padding: 1.5rem !important;
            border-radius: 12px !important;
            text-align: center !important;
            margin: 1rem 0 !important;
            box-shadow: 0 6px 20px rgba(29, 78, 216, 0.3) !important;
        }
        
        .score-display {
            font-size: 3em !important;
            font-weight: bold !important;
            margin: 0 !important;
            color: white !important;
        }
        
        .score-label {
            font-size: 1.2em !important;
            opacity: 0.9 !important;
            margin-bottom: 0.5rem !important;
            color: white !important;
        }
        
        /* Input section styling - Light blue background */
        .input-section {
            background: #f8fafc !important;
            padding: 1.5rem !important;
            border-radius: 12px !important;
            border: 2px solid #e2e8f0 !important;
            margin-bottom: 1rem !important;
        }
        
        /* Button styling - Blue theme */
        .analyze-button {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 1rem 2rem !important;
            font-size: 1.1em !important;
            font-weight: bold !important;
            color: white !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(30, 64, 175, 0.4) !important;
            width: 100% !important;
            margin-top: 1rem !important;
        }
        
        .analyze-button:hover {
            background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(30, 58, 138, 0.6) !important;
        }
        
        /* Tab styling - High contrast */
        .tab-nav {
            background: #f1f5f9 !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            margin-bottom: 1rem !important;
            border: 1px solid #cbd5e1 !important;
        }
        
        /* Result sections - High contrast with black text */
        .result-section {
            background: white !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            margin: 1rem 0 !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
            border: 2px solid #e2e8f0 !important;
            border-left: 6px solid #1e40af !important;
        }
        
        /* Analysis cards with high contrast */
        .analysis-card {
            background: white !important;
            border-radius: 8px !important;
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
            border: 2px solid #e2e8f0 !important;
            transition: all 0.2s ease !important;
            color: #000000 !important;
        }
        
        .analysis-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
            border-color: #3b82f6 !important;
        }
        
        /* Enhanced text contrast for analysis content */
        .analysis-card h1, .analysis-card h2, .analysis-card h3, 
        .analysis-card h4, .analysis-card h5, .analysis-card h6 {
            color: #000000 !important;
            font-weight: bold !important;
        }
        
        .analysis-card p, .analysis-card li, .analysis-card span {
            color: #1f2937 !important;
            line-height: 1.6 !important;
        }
        
        .analysis-card strong, .analysis-card b {
            color: #000000 !important;
            font-weight: bold !important;
        }
        
        /* Download section - Blue theme */
        .download-section {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
            padding: 1.5rem !important;
            border-radius: 12px !important;
            text-align: center !important;
            margin: 2rem 0 !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.2) !important;
            border: 2px solid #93c5fd !important;
            color: #1e40af !important;
        }
        
        /* Footer styling - Dark blue/black */
        .footer-section {
            background: #0f172a !important;
            color: white !important;
            padding: 2rem !important;
            border-radius: 12px !important;
            margin-top: 2rem !important;
            border: 1px solid #1e293b !important;
        }
        
        /* Progress indicator - Blue theme */
        .progress-container {
            background: #e2e8f0 !important;
            border-radius: 10px !important;
            height: 8px !important;
            margin: 1rem 0 !important;
            overflow: hidden !important;
        }
        
        /* Loading animation - Blue theme */
        .loading {
            border: 3px solid #e2e8f0 !important;
            border-top: 3px solid #3b82f6 !important;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            animation: spin 1s linear infinite !important;
            margin: 1rem auto !important;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Tab content styling for better contrast */
        .tab-content {
            background: white !important;
            color: #000000 !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        /* Ensure all text in tabs is high contrast */
        .tab-content h1, .tab-content h2, .tab-content h3, 
        .tab-content h4, .tab-content h5, .tab-content h6 {
            color: #000000 !important;
            font-weight: bold !important;
        }
        
        .tab-content p, .tab-content li, .tab-content div {
            color: #1f2937 !important;
            line-height: 1.6 !important;
        }
        
        .tab-content strong, .tab-content b {
            color: #000000 !important;
            font-weight: bold !important;
        }
        
        /* Override Gradio's default bright colors */
        .gradio-container .prose {
            color: #000000 !important;
        }
        
        .gradio-container .prose h1, 
        .gradio-container .prose h2, 
        .gradio-container .prose h3 {
            color: #000000 !important;
        }
        
        .gradio-container .prose p {
            color: #1f2937 !important;
        }
        
        .gradio-container .prose strong {
            color: #000000 !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .gradio-container {
                max-width: 100% !important;
                padding: 1rem !important;
            }
            
            .score-display {
                font-size: 2em !important;
            }
            
            .header-container {
                padding: 1.5rem !important;
            }
            
            .result-section {
                padding: 1.5rem !important;
            }
            
            .analysis-card {
                padding: 1rem !important;
            }
        }
        """

        with gr.Blocks(
            css=css, 
            title="CV Check - Professional Resume Analysis",
            theme=gr.themes.Monochrome(
                primary_hue="blue",
                secondary_hue="blue", 
                neutral_hue="slate",
                font=["system-ui", "sans-serif"]
            )
        ) as interface:
            
            # Professional Header
            with gr.Row(elem_classes=["header-container"]):
                gr.HTML("""
                <div style="text-align: center;">
                    <h1 style="margin: 0; font-size: 2.5em; font-weight: 700;">
                        🎯 CV Check Professional
                    </h1>
                    <h2 style="margin: 0.5rem 0; font-size: 1.4em; opacity: 0.9; font-weight: 300;">
                        AI-Powered Resume Analysis for PhD Professionals
                    </h2>
                    <p style="margin: 1rem 0 0 0; font-size: 1.1em; opacity: 0.8;">
                        Transform your academic expertise into industry success
                    </p>
                </div>
                """)
            
            # Main content area
            with gr.Row(equal_height=False):
                # Left column - Input section
                with gr.Column(scale=5, min_width=400):
                    with gr.Group(elem_classes=["input-section"]):
                        gr.Markdown("### 📄 **Upload & Analyze**")
                        
                        gr.Markdown("*Supported formats: PDF, DOCX, DOC*")
                        resume_file = gr.File(
                            label="📎 Upload Your Resume",
                            file_types=[".pdf", ".docx", ".doc"],
                            type="filepath"
                        )
                        
                        gr.Markdown("*The more detailed the job description, the better the analysis*")
                        job_description = gr.Textbox(
                            label="📋 Job Description",
                            placeholder="Paste the complete job description here...\n\nInclude requirements, responsibilities, and company information for best results.",
                            lines=12,
                            max_lines=20
                        )
                        
                        with gr.Row():
                            analyze_btn = gr.Button(
                                "🚀 Start Analysis",
                                variant="primary",
                                size="lg",
                                elem_classes=["analyze-button"]
                            )
                            clear_btn = gr.Button(
                                "🔄 Clear All",
                                variant="secondary",
                                size="lg"
                            )
                
                # Right column - Results section  
                with gr.Column(scale=7, min_width=500):
                    # Score display
                    with gr.Group(elem_classes=["score-container"], visible=False) as score_section:
                        gr.HTML("""
                        <div class="score-label">Compatibility Score</div>
                        """)
                        score_display = gr.HTML("""
                        <div class="score-display">--</div>
                        """)
                    
                    # Results tabs
                    with gr.Group(elem_classes=["result-section"], visible=False) as results_section:
                        gr.Markdown("### 📊 **Detailed Analysis**")
                        
                        with gr.Tabs():
                            with gr.TabItem("💪 Strengths", elem_id="strengths-tab"):
                                strong_points_output = gr.Markdown(
                                    "Your analysis results will appear here...",
                                    elem_classes=["analysis-card", "tab-content"]
                                )
                            
                            with gr.TabItem("⚠️ Improvements", elem_id="improvements-tab"):
                                weak_points_output = gr.Markdown(
                                    "Areas for improvement will be shown here...",
                                    elem_classes=["analysis-card", "tab-content"]
                                )
                            
                            with gr.TabItem("🚀 Recommendations", elem_id="recommendations-tab"):
                                improvements_output = gr.Markdown(
                                    "Specific recommendations will be provided here...",
                                    elem_classes=["analysis-card", "tab-content"]
                                )
                            
                            with gr.TabItem("📈 Score Breakdown", elem_id="breakdown-tab"):
                                score_breakdown_output = gr.Markdown(
                                    "Detailed score breakdown will be available here...",
                                    elem_classes=["analysis-card", "tab-content"]
                                )
            
            # Download section
            with gr.Group(elem_classes=["download-section"], visible=False) as download_section:
                gr.Markdown("### 📋 **Complete Analysis Report**")
                gr.Markdown("*Get your comprehensive analysis document with interview preparation guide*")
                
                interview_prep_file = gr.File(
                    label="📄 Download Professional Analysis Report (Word Document)",
                    visible=True,
                    interactive=False
                )
            
            # Progress indicator
            progress_html = gr.HTML(visible=False)
            
            # Professional footer
            with gr.Group(elem_classes=["footer-section"]):
                gr.Markdown("""
                ### 💡 **How to Get the Best Results**
                
                **📎 Resume Tips:**
                - Upload your most recent, complete resume
                - Ensure all sections are clearly formatted
                - Include quantified achievements where possible
                
                **📋 Job Description Tips:**
                - Copy the complete job posting
                - Include requirements, responsibilities, and company info
                - Don't forget salary range and benefits if mentioned
                
                **🎯 Analysis Features:**
                - Real-time compatibility scoring (0-100)
                - Detailed strengths and improvement areas
                - Actionable recommendations with priority levels
                - Professional interview preparation guide
                - ATS optimization suggestions
                
                ---
                *🇫🇷 Specially designed for PhD professionals transitioning to industry roles in France*
                """)
            
            # Enhanced analysis function with UI updates
            def enhanced_analysis(resume, job_desc):
                """Enhanced analysis with proper UI state management."""
                if not resume or not job_desc or not job_desc.strip():
                    return [
                        gr.update(visible=False),  # score_section
                        gr.update(value="--"),      # score_display  
                        gr.update(visible=False),  # results_section
                        "Please upload a resume and provide a job description.",  # strong_points
                        "",  # weak_points
                        "",  # improvements  
                        "",  # score_breakdown
                        gr.update(visible=False),  # download_section
                        None,  # file
                        gr.update(visible=False)   # progress
                    ]
                
                # Run the analysis
                score, strong, weak, improvements, file_path = self.analyze_resume_job_match(resume, job_desc)
                
                # Format score display
                score_html = f"""<div class="score-display">{score}/100</div>"""
                score_breakdown = f"**Overall Score: {score}/100**\n\nThis score reflects the compatibility between your resume and the job requirements. Detailed breakdown is available in the downloadable analysis report."
                
                return [
                    gr.update(visible=True),   # Show score section
                    score_html,               # Update score display
                    gr.update(visible=True),   # Show results section
                    strong,                   # Strong points
                    weak,                     # Weak points
                    improvements,             # Improvements
                    score_breakdown,          # Score breakdown
                    gr.update(visible=True),   # Show download section
                    file_path,                # File path
                    gr.update(visible=False)   # Hide progress
                ]
            
            def clear_all():
                """Clear all inputs and outputs."""
                return [
                    None,  # Clear resume file
                    "",    # Clear job description
                    gr.update(visible=False),  # Hide score section
                    "--",  # Reset score display
                    gr.update(visible=False),  # Hide results section
                    "Your analysis results will appear here...",  # Reset strong points
                    "Areas for improvement will be shown here...",  # Reset weak points
                    "Specific recommendations will be provided here...",  # Reset improvements
                    "Detailed score breakdown will be available here...",  # Reset breakdown
                    gr.update(visible=False),  # Hide download section
                    None,  # Clear file
                    gr.update(visible=False)   # Hide progress
                ]
            
            # Connect the analysis function
            analyze_btn.click(
                fn=enhanced_analysis,
                inputs=[resume_file, job_description],
                outputs=[
                    score_section, score_display, results_section,
                    strong_points_output, weak_points_output, improvements_output, score_breakdown_output,
                    download_section, interview_prep_file, progress_html
                ]
            )
            
            # Clear button functionality
            clear_btn.click(
                fn=clear_all,
                outputs=[
                    resume_file, job_description, score_section, score_display, results_section,
                    strong_points_output, weak_points_output, improvements_output, score_breakdown_output,
                    download_section, interview_prep_file, progress_html
                ]
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
