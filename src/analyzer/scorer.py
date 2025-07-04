"""Compatibility scoring module for resume-job matching."""

import logging
from typing import Dict, Any, Tuple
from analyzer.resume_analyzer import ResumeData
from analyzer.job_analyzer import JobRequirements

logger = logging.getLogger(__name__)


class CompatibilityScorer:
    """Scorer for calculating resume-job compatibility."""

    def __init__(self) -> None:
        """Initialize the compatibility scorer."""
        self.weights: Dict[str, float] = {
            "skills_match": 0.35,
            "experience_match": 0.25,
            "education_match": 0.20,
            "overqualification_penalty": 0.10,
            "language_match": 0.05,
            "location_match": 0.05,
        }

    def calculate_score(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate compatibility score between resume and job.
        
        Args:
            resume_data: Structured resume data
            job_requirements: Structured job requirements
            
        Returns:
            Tuple of (score, breakdown) where score is 0-100 and breakdown contains details
        """
        try:
            breakdown = {}
            
            # Calculate individual scores
            skills_score = self._calculate_skills_match(resume_data, job_requirements)
            breakdown["skills_match"] = skills_score
            
            experience_score = self._calculate_experience_match(resume_data, job_requirements)
            breakdown["experience_match"] = experience_score
            
            education_score = self._calculate_education_match(resume_data, job_requirements)
            breakdown["education_match"] = education_score
            
            overqualification_penalty = self._calculate_overqualification_penalty(
                resume_data, job_requirements
            )
            breakdown["overqualification_penalty"] = overqualification_penalty
            
            language_score = self._calculate_language_match(resume_data, job_requirements)
            breakdown["language_match"] = language_score
            
            location_score = self._calculate_location_match(resume_data, job_requirements)
            breakdown["location_match"] = location_score
            
            # Calculate weighted total
            total_score = (
                skills_score * self.weights["skills_match"] +
                experience_score * self.weights["experience_match"] +
                education_score * self.weights["education_match"] +
                language_score * self.weights["language_match"] +
                location_score * self.weights["location_match"]
            ) - (overqualification_penalty * self.weights["overqualification_penalty"])
            
            # Ensure score is between 0 and 100
            final_score = max(0, min(100, int(total_score)))
            
            breakdown["final_score"] = final_score
            breakdown["score_explanation"] = self._generate_score_explanation(  # type: ignore
                final_score, breakdown
            )
            
            return final_score, breakdown
            
        except Exception as e:
            logger.error(f"Error calculating compatibility score: {str(e)}")
            return 0, {"error": str(e), "score_explanation": "Error in calculation"}

    def _calculate_skills_match(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> float:
        """Calculate skills matching score."""
        if not job_requirements.required_skills:
            return 50.0  # No requirements specified
        
        resume_skills_lower = [skill.lower() for skill in resume_data.skills]
        required_skills_lower = [skill.lower() for skill in job_requirements.required_skills]
        preferred_skills_lower = [skill.lower() for skill in job_requirements.preferred_skills]
        
        # Check required skills match
        required_matches = sum(
            1 for skill in required_skills_lower 
            if any(skill in resume_skill for resume_skill in resume_skills_lower)
        )
        
        # Check preferred skills match
        preferred_matches = sum(
            1 for skill in preferred_skills_lower 
            if any(skill in resume_skill for resume_skill in resume_skills_lower)
        )
        
        # Calculate score
        if required_skills_lower:
            required_score = (required_matches / len(required_skills_lower)) * 70
        else:
            required_score = 70
        
        if preferred_skills_lower:
            preferred_score = (preferred_matches / len(preferred_skills_lower)) * 30
        else:
            preferred_score = 30
        
        return min(100, required_score + preferred_score)

    def _calculate_experience_match(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> float:
        """Calculate experience matching score."""
        # Simple heuristic based on number of experience entries
        experience_count = len(resume_data.experience)
        
        if job_requirements.job_level == "junior":
            target_experience = 1
        elif job_requirements.job_level == "mid":
            target_experience = 3
        elif job_requirements.job_level == "senior":
            target_experience = 5
        else:
            target_experience = 2
        
        if experience_count >= target_experience:
            return 90.0
        elif experience_count >= target_experience * 0.7:
            return 70.0
        elif experience_count >= target_experience * 0.5:
            return 50.0
        else:
            return 30.0

    def _calculate_education_match(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> float:
        """Calculate education matching score."""
        if not job_requirements.education_requirements:
            return 80.0  # No specific requirements
        
        education_text = " ".join([edu.get("degree", "") for edu in resume_data.education]).lower()
        requirements_text = " ".join(job_requirements.education_requirements).lower()
        
        # Check for degree level matches
        if "phd" in requirements_text or "doctorate" in requirements_text:
            return 100.0 if resume_data.has_phd else 30.0
        elif "master" in requirements_text:
            if resume_data.has_phd:
                return 95.0  # PhD exceeds master requirement
            elif "master" in education_text:
                return 90.0
            else:
                return 40.0
        elif "bachelor" in requirements_text:
            if resume_data.has_phd or "master" in education_text:
                return 95.0  # Higher degree meets requirement
            elif "bachelor" in education_text:
                return 85.0
            else:
                return 30.0
        
        return 70.0  # Default if no clear match

    def _calculate_overqualification_penalty(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> float:
        """Calculate penalty for overqualification."""
        penalty = 0.0
        
        # PhD penalty based on job level
        if resume_data.has_phd:
            if job_requirements.job_level == "junior":
                penalty += 40.0  # High penalty for junior roles
            elif job_requirements.job_level == "mid":
                penalty += 20.0  # Moderate penalty for mid-level
            elif job_requirements.job_level == "senior":
                penalty += 5.0   # Low penalty for senior roles
        
        # Academic background penalty for non-academic roles
        if resume_data.academic_background:
            if job_requirements.industry and job_requirements.industry.lower() not in [
                "technology", "research", "consulting", "education"
            ]:
                penalty += 15.0
        
        # Experience overqualification
        experience_count = len(resume_data.experience)
        if job_requirements.job_level == "junior" and experience_count > 3:
            penalty += 10.0
        
        return min(50.0, penalty)  # Cap penalty at 50%

    def _calculate_language_match(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> float:
        """Calculate language matching score."""
        if not job_requirements.languages:
            return 80.0  # No specific language requirements
        
        resume_languages_lower = [lang.lower() for lang in resume_data.languages]
        required_languages_lower = [lang.lower() for lang in job_requirements.languages]
        
        matches = sum(
            1 for req_lang in required_languages_lower
            if any(req_lang in resume_lang for resume_lang in resume_languages_lower)
        )
        
        if matches == len(required_languages_lower):
            return 100.0
        elif matches > 0:
            return 70.0
        else:
            return 30.0

    def _calculate_location_match(
        self, resume_data: ResumeData, job_requirements: JobRequirements
    ) -> float:
        """Calculate location matching score."""
        if not job_requirements.location:
            return 80.0  # No specific location requirement
        
        resume_location = (resume_data.contact_info.get("location") or "").lower()
        job_location = job_requirements.location.lower()
        
        if resume_location and job_location:
            if resume_location in job_location or job_location in resume_location:
                return 100.0
            else:
                return 40.0
        
        return 60.0  # Unknown location

    def _generate_score_explanation(
        self, score: int, breakdown: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation of the score."""
        if score >= 80:
            level = "Excellent"
            explanation = "Strong match with most requirements met."
        elif score >= 60:
            level = "Good"
            explanation = "Good match with some areas for improvement."
        elif score >= 40:
            level = "Moderate"
            explanation = "Moderate match with several gaps to address."
        else:
            level = "Low"
            explanation = "Significant gaps between resume and job requirements."
        
        return f"{level} compatibility ({score}%). {explanation}"