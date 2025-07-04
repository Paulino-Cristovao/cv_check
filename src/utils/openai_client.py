"""OpenAI client for API interactions."""

import os
import logging
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4"

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate text completion using OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-1)
            system_message: Optional system message to set context
            
        Returns:
            Generated text or None if request fails
        """
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None

    def analyze_resume_job_match(
        self, resume_text: str, job_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze match between resume and job description.
        
        Args:
            resume_text: The resume content
            job_description: The job description
            
        Returns:
            Analysis results as dictionary or None if analysis fails
        """
        system_message = """You are an expert HR analyst specializing in resume optimization for PhD holders in France. 
        Your task is to analyze the match between a resume and job description, providing specific, actionable feedback.
        
        Focus on:
        1. PhD overqualification risks
        2. French job market specifics
        3. Skills alignment
        4. Experience level matching
        5. Keyword optimization
        
        Return your analysis in JSON format with these keys:
        - acceptance_score: integer 0-100
        - score_reasoning: string explaining the score
        - strong_points: list of 3-5 strengths with explanations
        - weak_points: list of 3-5 weaknesses with explanations
        - improvements: list of specific, actionable recommendations
        """

        prompt = f"""
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Please analyze this resume against the job description and provide detailed feedback.
        """

        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                max_tokens=3000,
                temperature=0.3,
            )
            
            if response:
                # Parse JSON response
                import json
                try:
                    return json.loads(response)  # type: ignore
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON response from OpenAI")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error in resume analysis: {str(e)}")
            return None

    def generate_interview_prep(
        self, resume_text: str, job_description: str, analysis_results: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate interview preparation content.
        
        Args:
            resume_text: The resume content
            job_description: The job description
            analysis_results: Results from resume analysis
            
        Returns:
            Interview preparation content or None if generation fails
        """
        system_message = """You are an expert interview coach specializing in helping PhD holders in France. 
        Create comprehensive interview preparation content based on the resume, job description, and analysis results.
        
        Include:
        1. Company and role analysis
        2. Predicted interview questions (8-10)
        3. Suggested answers using candidate's experience
        4. Stories and examples to prepare
        5. Questions to ask the interviewer
        6. French market salary insights
        7. Tips for addressing PhD overqualification concerns
        """

        prompt = f"""
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        ANALYSIS RESULTS:
        {analysis_results}
        
        Create a comprehensive interview preparation guide for this candidate.
        """

        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                max_tokens=4000,
                temperature=0.5,
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating interview prep: {str(e)}")
            return None