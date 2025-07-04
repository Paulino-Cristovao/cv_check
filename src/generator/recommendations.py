"""Recommendation generator for resume improvements."""

import logging
from typing import List, Dict, Any, Tuple
from analyzer.resume_analyzer import ResumeData
from analyzer.job_analyzer import JobRequirements

logger = logging.getLogger(__name__)


class RecommendationGenerator:
    """Generator for creating specific resume improvement recommendations."""

    def __init__(self) -> None:
        """Initialize the recommendation generator."""
        pass

    def generate_recommendations(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        weak_points: List[Dict[str, str]],
        score_breakdown: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """
        Generate specific, actionable recommendations for resume improvement.
        
        Args:
            resume_data: Structured resume data
            job_requirements: Structured job requirements
            weak_points: Identified weak points from gap analysis
            score_breakdown: Score calculation breakdown
            
        Returns:
            List of specific recommendations with priority and impact
        """
        try:
            recommendations = []
            
            # Skills-based recommendations
            skills_recs = self._generate_skills_recommendations(
                resume_data, job_requirements, score_breakdown
            )
            recommendations.extend(skills_recs)
            
            # Experience presentation recommendations
            experience_recs = self._generate_experience_recommendations(
                resume_data, job_requirements, score_breakdown
            )
            recommendations.extend(experience_recs)
            
            # PhD-specific recommendations
            if resume_data.has_phd:
                phd_recs = self._generate_phd_recommendations(
                    resume_data, job_requirements, score_breakdown
                )
                recommendations.extend(phd_recs)
            
            # Keyword optimization recommendations
            keyword_recs = self._generate_keyword_recommendations(
                resume_data, job_requirements
            )
            recommendations.extend(keyword_recs)
            
            # Format and presentation recommendations
            format_recs = self._generate_format_recommendations(
                resume_data, job_requirements
            )
            recommendations.extend(format_recs)
            
            # Sort by priority and limit to top recommendations
            recommendations = self._prioritize_recommendations(recommendations)
            
            return recommendations[:8]  # Return top 8 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _generate_skills_recommendations(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        score_breakdown: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Generate skills-related recommendations."""
        recommendations = []
        
        skills_score = score_breakdown.get("skills_match", 0)
        
        if skills_score < 70:
            # Missing required skills
            missing_skills = []
            resume_skills_lower = [skill.lower() for skill in resume_data.skills]
            
            for req_skill in job_requirements.required_skills:
                found = any(req_skill.lower() in resume_skill for resume_skill in resume_skills_lower)
                if not found:
                    missing_skills.append(req_skill)
            
            if missing_skills:
                recommendations.append({
                    "category": "Skills Enhancement",
                    "recommendation": f"Add experience with required technologies: {', '.join(missing_skills[:3])}",
                    "action": "Include any exposure to these technologies, even from personal projects, courses, or brief work experience",
                    "priority": "High",
                    "impact": "Significantly improves ATS keyword matching and shows technical relevance",
                    "implementation": f"Example: 'Developed familiarity with {missing_skills[0]} through [course/project/self-study]'"
                })
        
        # Skills depth recommendation
        if len(resume_data.skills) < 5:
            recommendations.append({
                "category": "Skills Breadth",
                "recommendation": "Expand your listed technical skills",
                "action": "Include tools, frameworks, methodologies, and soft skills relevant to the role",
                "priority": "Medium",
                "impact": "Increases keyword density and shows technical versatility",
                "implementation": "Add skills like: project management tools, communication skills, analytical abilities"
            })
        
        return recommendations

    def _generate_experience_recommendations(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        score_breakdown: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Generate experience-related recommendations."""
        recommendations = []
        
        experience_score = score_breakdown.get("experience_match", 0)
        
        if experience_score < 60:
            if len(resume_data.experience) < 3:
                recommendations.append({
                    "category": "Experience Expansion",
                    "recommendation": "Include all relevant experience: internships, projects, research",
                    "action": "Add research projects, academic collaborations, consulting work, or significant personal projects",
                    "priority": "High",
                    "impact": "Demonstrates practical application of skills and increases perceived experience",
                    "implementation": "Format as: '[Role/Project] - [Duration] - [Key achievements with metrics]'"
                })
        
        # Quantification recommendation
        recommendations.append({
            "category": "Achievement Quantification",
            "recommendation": "Add specific metrics and numbers to your achievements",
            "action": "Include budget sizes, team sizes, performance improvements, timelines, or research outcomes",
            "priority": "High",
            "impact": "Makes your contributions tangible and impressive to recruiters",
            "implementation": "Examples: 'Led team of 5', 'Improved efficiency by 30%', 'Managed €50K budget', 'Published 3 papers'"
        })
        
        return recommendations

    def _generate_phd_recommendations(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        score_breakdown: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Generate PhD-specific recommendations."""
        recommendations = []
        
        overqualification_penalty = score_breakdown.get("overqualification_penalty", 0)
        
        if overqualification_penalty > 15:
            if job_requirements.job_level in ["junior", "mid"]:
                recommendations.append({
                    "category": "PhD Positioning",
                    "recommendation": "Reframe PhD as business-relevant experience",
                    "action": "Emphasize transferable skills: problem-solving, project management, data analysis, communication",
                    "priority": "High",
                    "impact": "Reduces overqualification concerns and highlights business value",
                    "implementation": "Focus on: 'Managed complex 3-year research project' rather than 'PhD in X'"
                })
        
        if resume_data.academic_background:
            recommendations.append({
                "category": "Language Adjustment",
                "recommendation": "Use business language instead of academic terminology",
                "action": "Replace academic terms with industry equivalents",
                "priority": "Medium",
                "impact": "Makes your background more accessible to non-academic hiring managers",
                "implementation": "Research → Analysis, Publications → Reports, Dissertation → Project, Laboratory → Team"
            })
        
        return recommendations

    def _generate_keyword_recommendations(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
    ) -> List[Dict[str, str]]:
        """Generate keyword optimization recommendations."""
        recommendations = []
        
        # Job-specific keywords
        job_keywords = job_requirements.keywords[:5]
        if job_keywords:
            recommendations.append({
                "category": "Keyword Optimization",
                "recommendation": f"Integrate key job terms: {', '.join(job_keywords)}",
                "action": "Naturally incorporate these terms throughout your resume content",
                "priority": "Medium",
                "impact": "Improves ATS parsing and keyword density matching",
                "implementation": "Use variations and context: 'data analysis', 'analyzed data', 'analytical approach'"
            })
        
        # Industry-specific terms
        if job_requirements.industry:
            recommendations.append({
                "category": "Industry Terminology",
                "recommendation": f"Include {job_requirements.industry} industry terminology",
                "action": "Research and include common terms used in the industry",
                "priority": "Medium",
                "impact": "Shows industry awareness and cultural fit",
                "implementation": f"Study job postings in {job_requirements.industry} to identify common phrases and requirements"
            })
        
        return recommendations

    def _generate_format_recommendations(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
    ) -> List[Dict[str, str]]:
        """Generate format and presentation recommendations."""
        recommendations = []
        
        # Contact information
        if not resume_data.contact_info.get("email"):
            recommendations.append({
                "category": "Contact Information",
                "recommendation": "Ensure complete contact information is prominently displayed",
                "action": "Include professional email, phone number, and LinkedIn profile",
                "priority": "High",
                "impact": "Essential for recruiters to contact you",
                "implementation": "Place contact info at the top: professional email, phone, LinkedIn, location"
            })
        
        # Professional summary
        recommendations.append({
            "category": "Professional Summary",
            "recommendation": "Add a targeted professional summary at the top",
            "action": "Write 2-3 sentences highlighting your key qualifications for this specific role",
            "priority": "Medium",
            "impact": "Immediately communicates your value proposition to hiring managers",
            "implementation": f"Example: 'Experienced {job_requirements.title} with expertise in [key skills] seeking to apply analytical and technical skills in [industry] environment'"
        })
        
        # ATS-friendly formatting
        recommendations.append({
            "category": "ATS Optimization",
            "recommendation": "Ensure ATS-friendly formatting",
            "action": "Use standard headings, bullet points, and avoid complex formatting",
            "priority": "Medium",
            "impact": "Ensures your resume is properly parsed by applicant tracking systems",
            "implementation": "Use headings like: Professional Experience, Education, Skills, Certifications"
        })
        
        return recommendations

    def _prioritize_recommendations(
        self, recommendations: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Sort recommendations by priority and impact."""
        
        def priority_score(rec: Dict[str, str]) -> int:
            priority = rec.get("priority", "Medium").lower()
            category = rec.get("category", "").lower()
            
            score = 0
            
            # Priority weighting
            if priority == "high":
                score += 100
            elif priority == "medium":
                score += 50
            else:
                score += 10
            
            # Category importance
            if "skills" in category:
                score += 30
            elif "phd" in category or "positioning" in category:
                score += 25
            elif "experience" in category:
                score += 20
            elif "keyword" in category:
                score += 15
            
            return score
        
        return sorted(recommendations, key=priority_score, reverse=True)