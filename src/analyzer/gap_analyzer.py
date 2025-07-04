"""Gap analysis module for identifying strengths and weaknesses."""

import logging
from typing import List, Dict, Any, Tuple
from analyzer.resume_analyzer import ResumeData
from analyzer.job_analyzer import JobRequirements

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """Analyzer for identifying gaps between resume and job requirements."""

    def __init__(self) -> None:
        """Initialize the gap analyzer."""
        pass

    def analyze_gaps(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        score_breakdown: Dict[str, Any],
    ) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
        """
        Analyze gaps between resume and job requirements.
        
        Args:
            resume_data: Structured resume data
            job_requirements: Structured job requirements
            score_breakdown: Score calculation breakdown
            
        Returns:
            Tuple of (strong_points, weak_points, improvements)
        """
        try:
            strong_points = self._identify_strong_points(
                resume_data, job_requirements, score_breakdown
            )
            weak_points = self._identify_weak_points(
                resume_data, job_requirements, score_breakdown
            )
            improvements = self._generate_improvements(
                resume_data, job_requirements, weak_points
            )
            
            return strong_points, weak_points, improvements
            
        except Exception as e:
            logger.error(f"Error in gap analysis: {str(e)}")
            return [], [], []

    def _identify_strong_points(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        score_breakdown: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Identify candidate's strong points."""
        strong_points = []
        
        # Skills match
        if score_breakdown.get("skills_match", 0) >= 70:
            matching_skills = self._find_matching_skills(resume_data, job_requirements)
            if matching_skills:
                strong_points.append({
                    "category": "Skills",
                    "point": f"Strong technical skills match: {', '.join(matching_skills[:3])}",
                    "explanation": "Your technical expertise aligns well with the job requirements.",
                    "leverage": "Highlight these skills prominently in your resume and mention specific projects where you used them."
                })
        
        # Education match
        if score_breakdown.get("education_match", 0) >= 80:
            if resume_data.has_phd and job_requirements.job_level in ["senior", "mid"]:
                strong_points.append({
                    "category": "Education",
                    "point": "Advanced academic credentials (PhD)",
                    "explanation": "Your PhD demonstrates deep expertise and research capabilities.",
                    "leverage": "Emphasize problem-solving skills, analytical thinking, and ability to work independently."
                })
            elif resume_data.education:
                degree_info = resume_data.education[0]
                strong_points.append({
                    "category": "Education",
                    "point": f"Relevant educational background: {degree_info.get('degree', '')}",
                    "explanation": "Your educational credentials meet or exceed the job requirements.",
                    "leverage": "Connect your academic learnings to practical business applications."
                })
        
        # Experience relevance
        if score_breakdown.get("experience_match", 0) >= 70:
            if len(resume_data.experience) >= 3:
                strong_points.append({
                    "category": "Experience",
                    "point": "Substantial professional experience",
                    "explanation": "You have relevant work experience that demonstrates practical skills.",
                    "leverage": "Quantify your achievements and focus on results you delivered."
                })
        
        # Language skills
        if score_breakdown.get("language_match", 0) >= 80:
            strong_points.append({
                "category": "Languages",
                "point": f"Language proficiency: {', '.join(resume_data.languages[:2])}",
                "explanation": "Your language skills meet the position requirements.",
                "leverage": "Mention specific contexts where you used these languages professionally."
            })
        
        # Location advantage
        if score_breakdown.get("location_match", 0) >= 90:
            strong_points.append({
                "category": "Location",
                "point": "Optimal location match",
                "explanation": "Your location aligns perfectly with the job location.",
                "leverage": "Emphasize your local market knowledge and availability for in-person collaboration."
            })
        
        # Ensure we have at least 3 strong points
        while len(strong_points) < 3:
            strong_points.extend(self._generate_generic_strong_points(resume_data))
            strong_points = strong_points[:5]  # Limit to 5
        
        return strong_points[:5]

    def _identify_weak_points(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        score_breakdown: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Identify candidate's weak points."""
        weak_points = []
        
        # Skills gaps
        if score_breakdown.get("skills_match", 0) < 60:
            missing_skills = self._find_missing_skills(resume_data, job_requirements)
            if missing_skills:
                weak_points.append({
                    "category": "Skills",
                    "point": f"Missing key technical skills: {', '.join(missing_skills[:3])}",
                    "explanation": "Some required technical skills are not evident in your resume.",
                    "impact": "This may lead to automatic filtering by ATS systems."
                })
        
        # Overqualification risk
        overqualification_penalty = score_breakdown.get("overqualification_penalty", 0)
        if overqualification_penalty > 20:
            if resume_data.has_phd and job_requirements.job_level == "junior":
                weak_points.append({
                    "category": "Overqualification",
                    "point": "PhD for junior-level position",
                    "explanation": "Your advanced degree may be seen as overqualification for this role.",
                    "impact": "Employers might worry about retention, salary expectations, or cultural fit."
                })
            elif resume_data.academic_background and job_requirements.industry not in [
                "technology", "research", "consulting"
            ]:
                weak_points.append({
                    "category": "Industry Fit",
                    "point": "Academic background for industry role",
                    "explanation": "Strong academic background may not align with industry expectations.",
                    "impact": "May be perceived as lacking practical business experience."
                })
        
        # Experience gaps
        if score_breakdown.get("experience_match", 0) < 50:
            if job_requirements.job_level == "senior" and len(resume_data.experience) < 4:
                weak_points.append({
                    "category": "Experience",
                    "point": "Limited professional experience for senior role",
                    "explanation": "The position requires more extensive industry experience.",
                    "impact": "May not meet minimum experience requirements."
                })
        
        # Language requirements
        if score_breakdown.get("language_match", 0) < 50:
            weak_points.append({
                "category": "Languages",
                "point": "Language requirements not clearly met",
                "explanation": "Required language proficiency is not evident in your resume.",
                "impact": "May be filtered out if language skills are mandatory."
            })
        
        # Education mismatch
        if score_breakdown.get("education_match", 0) < 40:
            weak_points.append({
                "category": "Education",
                "point": "Educational requirements not met",
                "explanation": "Your educational background doesn't match the specified requirements.",
                "impact": "May not meet minimum qualification criteria."
            })
        
        # Ensure we have at least 3 weak points
        while len(weak_points) < 3:
            weak_points.extend(self._generate_generic_weak_points(resume_data, job_requirements))
            weak_points = weak_points[:5]  # Limit to 5
        
        return weak_points[:5]

    def _generate_improvements(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        weak_points: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """Generate specific improvement recommendations."""
        improvements = []
        
        # Address skills gaps
        missing_skills = self._find_missing_skills(resume_data, job_requirements)
        if missing_skills:
            improvements.append({
                "category": "Skills Enhancement",
                "recommendation": f"Add experience with: {', '.join(missing_skills[:3])}",
                "action": "Include any projects, courses, or exposure to these technologies in your resume.",
                "priority": "High",
                "impact": "Improves ATS keyword matching and demonstrates technical relevance."
            })
        
        # Address overqualification
        if resume_data.has_phd and job_requirements.job_level in ["junior", "mid"]:
            improvements.append({
                "category": "PhD Positioning",
                "recommendation": "Reframe PhD as practical problem-solving experience",
                "action": "Focus on transferable skills: analytical thinking, project management, communication.",
                "priority": "High",
                "impact": "Reduces overqualification concerns and emphasizes business value."
            })
        
        # Industry transition advice
        if resume_data.academic_background and job_requirements.industry not in [
            "technology", "research", "consulting"
        ]:
            improvements.append({
                "category": "Industry Positioning",
                "recommendation": "Emphasize business impact over academic achievements",
                "action": "Quantify results, use business language, highlight practical applications.",
                "priority": "High",
                "impact": "Demonstrates industry readiness and practical value."
            })
        
        # Experience presentation
        if len(resume_data.experience) > 0:
            improvements.append({
                "category": "Experience Optimization",
                "recommendation": "Quantify achievements with specific metrics",
                "action": "Add numbers: budget managed, team size, performance improvements, etc.",
                "priority": "Medium",
                "impact": "Makes your contributions more tangible and impressive."
            })
        
        # Keyword optimization
        job_keywords = job_requirements.keywords[:5]
        if job_keywords:
            improvements.append({
                "category": "Keyword Optimization",
                "recommendation": f"Include key terms: {', '.join(job_keywords)}",
                "action": "Naturally integrate these terms throughout your resume content.",
                "priority": "Medium",
                "impact": "Improves ATS parsing and keyword density scores."
            })
        
        return improvements[:5]

    def _find_matching_skills(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> List[str]:
        """Find skills that match between resume and job requirements."""
        resume_skills_lower = [skill.lower() for skill in resume_data.skills]
        all_job_skills = job_requirements.required_skills + job_requirements.preferred_skills
        job_skills_lower = [skill.lower() for skill in all_job_skills]
        
        matching = []
        for job_skill in job_skills_lower:
            for resume_skill in resume_skills_lower:
                if job_skill in resume_skill or resume_skill in job_skill:
                    matching.append(job_skill.title())
                    break
        
        return list(set(matching))

    def _find_missing_skills(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> List[str]:
        """Find skills that are required but missing from resume."""
        resume_skills_lower = [skill.lower() for skill in resume_data.skills]
        required_skills_lower = [skill.lower() for skill in job_requirements.required_skills]
        
        missing = []
        for req_skill in required_skills_lower:
            found = any(req_skill in resume_skill for resume_skill in resume_skills_lower)
            if not found:
                missing.append(req_skill.title())
        
        return missing

    def _generate_generic_strong_points(
        self, resume_data: ResumeData
    ) -> List[Dict[str, str]]:
        """Generate generic strong points when specific ones are limited."""
        generic_points = []
        
        if resume_data.has_phd:
            generic_points.append({
                "category": "Research Skills",
                "point": "Advanced research and analytical capabilities",
                "explanation": "PhD training provides strong analytical and problem-solving skills.",
                "leverage": "Emphasize your ability to tackle complex problems systematically."
            })
        
        if len(resume_data.skills) > 3:
            generic_points.append({
                "category": "Technical Diversity",
                "point": "Diverse technical skill set",
                "explanation": "You demonstrate adaptability across multiple technologies.",
                "leverage": "Show how you can quickly learn and apply new technologies."
            })
        
        if len(resume_data.languages) > 1:
            generic_points.append({
                "category": "Communication",
                "point": "Multilingual communication abilities",
                "explanation": "Multiple language skills demonstrate cultural adaptability.",
                "leverage": "Highlight your ability to work in international environments."
            })
        
        return generic_points

    def _generate_generic_weak_points(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> List[Dict[str, str]]:
        """Generate generic weak points when specific ones are limited."""
        generic_points = []
        
        generic_points.append({
            "category": "Keyword Optimization",
            "point": "Limited keyword alignment with job description",
            "explanation": "Your resume may not contain enough keywords from the job posting.",
            "impact": "ATS systems might not rank your resume highly."
        })
        
        generic_points.append({
            "category": "Quantification",
            "point": "Achievements could be more quantified",
            "explanation": "Your accomplishments lack specific metrics and numbers.",
            "impact": "Makes it harder for recruiters to assess your impact."
        })
        
        generic_points.append({
            "category": "Industry Language",
            "point": "Could use more industry-specific terminology",
            "explanation": "Your resume might benefit from more business-focused language.",
            "impact": "May not resonate as strongly with hiring managers."
        })
        
        return generic_points