"""Interview preparation content generator."""

import logging
from typing import Dict, List, Any, Optional
from analyzer.resume_analyzer import ResumeData
from analyzer.job_analyzer import JobRequirements
from utils.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class InterviewPrepGenerator:
    """Generator for creating comprehensive interview preparation content."""

    def __init__(self, openai_client: OpenAIClient) -> None:
        """
        Initialize the interview prep generator.
        
        Args:
            openai_client: OpenAI client for content generation
        """
        self.openai_client = openai_client

    def generate_prep_content(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        analysis_results: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Generate comprehensive interview preparation content.
        
        Args:
            resume_data: Structured resume data
            job_requirements: Structured job requirements
            analysis_results: Analysis results from scoring
            
        Returns:
            Dictionary containing interview preparation sections
        """
        try:
            # Generate company and role analysis
            company_analysis = self._generate_company_analysis(job_requirements)
            
            # Generate interview questions
            interview_questions = self._generate_interview_questions(
                resume_data, job_requirements, analysis_results
            )
            
            # Generate suggested answers
            suggested_answers = self._generate_suggested_answers(
                resume_data, job_requirements, interview_questions
            )
            
            # Generate STAR stories
            star_stories = self._generate_star_stories(resume_data, job_requirements)
            
            # Generate questions to ask
            questions_to_ask = self._generate_questions_to_ask(job_requirements)
            
            # Generate salary insights
            salary_insights = self._generate_salary_insights(job_requirements)
            
            # Generate overqualification handling
            overqualification_tips = self._generate_overqualification_tips(
                resume_data, job_requirements
            )
            
            return {
                "company_analysis": company_analysis,
                "interview_questions": interview_questions,
                "suggested_answers": suggested_answers,
                "star_stories": star_stories,
                "questions_to_ask": questions_to_ask,
                "salary_insights": salary_insights,
                "overqualification_tips": overqualification_tips,
            }
            
        except Exception as e:
            logger.error(f"Error generating interview prep content: {str(e)}")
            return None

    def _generate_company_analysis(
        self, job_requirements: JobRequirements
    ) -> Dict[str, str]:
        """Generate company and role analysis."""
        company_info = {
            "company_name": job_requirements.company or "The Company",
            "industry": job_requirements.industry or "Unknown Industry",
            "role_title": job_requirements.title,
            "location": job_requirements.location or "Not specified",
            "company_size": job_requirements.company_size or "Not specified",
        }
        
        analysis = {
            "overview": f"You're applying for a {job_requirements.title} position",
            "industry_context": f"This role is in the {job_requirements.industry or 'technology'} industry",
            "role_level": f"This appears to be a {job_requirements.job_level}-level position",
            "key_focus": "Focus on demonstrating technical skills and cultural fit",
        }
        
        if job_requirements.company:
            analysis["company_focus"] = f"Research {job_requirements.company}'s recent projects, values, and market position"
        
        return analysis

    def _generate_interview_questions(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        analysis_results: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Generate likely interview questions."""
        questions = []
        
        # Technical questions based on required skills
        for skill in job_requirements.required_skills[:3]:
            questions.append({
                "category": "Technical",
                "question": f"Can you describe your experience with {skill}?",
                "type": "experience"
            })
        
        # Behavioral questions
        behavioral_questions = [
            "Tell me about a challenging project you worked on and how you overcame obstacles.",
            "Describe a time when you had to learn a new technology quickly.",
            "How do you handle conflicting priorities and tight deadlines?",
            "Give an example of how you collaborated with a diverse team.",
            "Describe a situation where you had to explain complex technical concepts to non-technical stakeholders.",
        ]
        
        for bq in behavioral_questions:
            questions.append({
                "category": "Behavioral",
                "question": bq,
                "type": "behavioral"
            })
        
        # PhD-specific questions if applicable
        if resume_data.has_phd:
            phd_questions = [
                "How do you see your PhD experience translating to this industry role?",
                "What made you decide to transition from academia to industry?",
                "How do you plan to adapt your research skills to business objectives?",
            ]
            
            for pq in phd_questions:
                questions.append({
                    "category": "PhD Background",
                    "question": pq,
                    "type": "transition"
                })
        
        # Company and role specific
        questions.append({
            "category": "Company Fit",
            "question": f"Why are you interested in working for {job_requirements.company or 'our company'}?",
            "type": "motivation"
        })
        
        questions.append({
            "category": "Role Fit",
            "question": f"What attracts you to this {job_requirements.title} position?",
            "type": "motivation"
        })
        
        return questions

    def _generate_suggested_answers(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        interview_questions: List[Dict[str, str]],
    ) -> Dict[str, str]:
        """Generate suggested answer frameworks."""
        suggested_answers = {}
        
        # Technical answer framework
        if job_requirements.required_skills:
            skill = job_requirements.required_skills[0]
            suggested_answers["technical_example"] = f"""
            For technical questions about {skill}:
            1. Start with your level of experience: "I have X years/months of experience with {skill}"
            2. Provide a specific example: "In my recent project/research, I used {skill} to..."
            3. Mention the outcome: "This resulted in... / This helped achieve..."
            4. Show continued learning: "I'm currently exploring... / I'm planning to deepen my knowledge in..."
            """
        
        # PhD transition answer
        if resume_data.has_phd:
            suggested_answers["phd_transition"] = """
            For PhD transition questions:
            1. Acknowledge the transition: "My PhD gave me strong analytical and problem-solving skills"
            2. Connect to business value: "I learned to break down complex problems systematically"
            3. Show industry interest: "I'm excited to apply these skills to real-world business challenges"
            4. Demonstrate commitment: "I've been preparing for this transition by..."
            """
        
        # Behavioral answer framework (STAR method)
        suggested_answers["behavioral_framework"] = """
        Use the STAR method for behavioral questions:
        - Situation: Set the context and background
        - Task: Describe your responsibility or goal
        - Action: Explain the specific steps you took
        - Result: Share the outcome and what you learned
        """
        
        return suggested_answers

    def _generate_star_stories(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> List[Dict[str, str]]:
        """Generate STAR story templates based on resume."""
        stories = []
        
        # Technical project story
        if resume_data.skills:
            stories.append({
                "title": "Technical Problem Solving",
                "situation": "Describe a challenging technical project or research problem",
                "task": "Explain your role and what needed to be accomplished",
                "action": f"Detail how you used skills like {', '.join(resume_data.skills[:2])} to solve it",
                "result": "Quantify the impact: performance improvement, time saved, problem solved"
            })
        
        # Collaboration story
        stories.append({
            "title": "Team Collaboration",
            "situation": "Think of a time you worked with a diverse team or stakeholders",
            "task": "What was your role in ensuring project success?",
            "action": "How did you communicate, coordinate, or resolve conflicts?",
            "result": "What was achieved through effective collaboration?"
        })
        
        # Learning and adaptation
        stories.append({
            "title": "Learning New Technology/Skill",
            "situation": "Recall when you had to quickly learn something new for a project",
            "task": "What was the deadline and learning goal?",
            "action": "How did you approach the learning process?",
            "result": "How successfully did you apply the new knowledge?"
        })
        
        # PhD-specific story
        if resume_data.has_phd:
            stories.append({
                "title": "Research Project Management",
                "situation": "Describe your PhD research or a major research project",
                "task": "What were the objectives and challenges?",
                "action": "How did you plan, execute, and manage the research?",
                "result": "What were the outcomes and broader impact?"
            })
        
        return stories

    def _generate_questions_to_ask(
        self, job_requirements: JobRequirements
    ) -> List[Dict[str, str]]:
        """Generate thoughtful questions for the candidate to ask."""
        questions = [
            {
                "category": "Role Understanding",
                "question": "What does a typical day/week look like in this role?",
                "purpose": "Shows interest in day-to-day responsibilities"
            },
            {
                "category": "Team Dynamics",
                "question": "Can you tell me about the team I'd be working with?",
                "purpose": "Demonstrates interest in collaboration"
            },
            {
                "category": "Growth Opportunities",
                "question": "What opportunities are there for professional development and growth?",
                "purpose": "Shows long-term thinking and ambition"
            },
            {
                "category": "Company Culture",
                "question": "How would you describe the company culture and values?",
                "purpose": "Indicates cultural fit awareness"
            },
            {
                "category": "Success Metrics",
                "question": "How do you measure success in this position?",
                "purpose": "Shows performance orientation"
            },
            {
                "category": "Challenges",
                "question": "What are the biggest challenges facing the team/company right now?",
                "purpose": "Demonstrates strategic thinking"
            },
        ]
        
        # Industry-specific questions
        if job_requirements.industry:
            questions.append({
                "category": "Industry Focus",
                "question": f"How is the company positioned in the {job_requirements.industry} market?",
                "purpose": "Shows industry awareness and strategic interest"
            })
        
        return questions

    def _generate_salary_insights(
        self, job_requirements: JobRequirements
    ) -> Dict[str, str]:
        """Generate salary negotiation insights for French market."""
        insights = {
            "market_context": "French salary discussions typically happen after initial interest is established",
            "timing": "Wait for the employer to bring up compensation, usually in second or third interview",
            "components": "Consider total package: salary, benefits, vacation (5+ weeks standard), training budget",
            "negotiation_style": "French negotiations tend to be more formal and less aggressive than US style",
        }
        
        # Location-specific insights
        if job_requirements.location:
            location_lower = job_requirements.location.lower()
            if "paris" in location_lower:
                insights["location_factor"] = "Paris salaries are typically 10-20% higher but cost of living is also higher"
            elif any(city in location_lower for city in ["lyon", "toulouse", "nice"]):
                insights["location_factor"] = "Regional French cities offer good work-life balance with competitive salaries"
        
        # Level-specific insights
        if job_requirements.job_level == "junior":
            insights["level_guidance"] = "Focus on learning opportunities and growth potential over immediate salary"
        elif job_requirements.job_level == "senior":
            insights["level_guidance"] = "Emphasize leadership experience and strategic contributions"
        
        return insights

    def _generate_overqualification_tips(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> List[Dict[str, str]]:
        """Generate tips for handling overqualification concerns."""
        tips = []
        
        if resume_data.has_phd and job_requirements.job_level in ["junior", "mid"]:
            tips.extend([
                {
                    "concern": "Why are you interested in this level of position?",
                    "strategy": "Emphasize learning opportunities and desire to apply skills in new context",
                    "example": "I'm excited to apply my analytical skills to real business problems and learn industry best practices"
                },
                {
                    "concern": "Won't you leave for a higher position quickly?",
                    "strategy": "Show genuine interest in the role and company growth",
                    "example": "I see this as an opportunity to build a long-term career in industry and grow with the company"
                },
                {
                    "concern": "Are your salary expectations realistic?",
                    "strategy": "Emphasize learning and growth over immediate compensation",
                    "example": "I'm more interested in the right opportunity and learning experience than maximizing short-term salary"
                },
            ])
        
        if resume_data.academic_background:
            tips.append({
                "concern": "Can you adapt from academic to business environment?",
                "strategy": "Highlight transferable skills and business awareness",
                "example": "My research experience taught me to work with deadlines, manage projects, and communicate complex ideas clearly"
            })
        
        return tips