"""
Claude Agent — Job evaluation via claude -p CLI.

Reads candidate profile and role preferences.
Scores job fit dynamically based on user's background.
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class JobEvaluator:
    """Evaluates job fit using claude -p."""
    
    def __init__(self, base_path: Path, config: Dict[str, Any]):
        """
        Initialize job evaluator.
        
        Args:
            base_path: Base path to ApplyFlow
            config: Configuration dict
        """
        self.base_path = base_path
        self.config = config
        self.candidate_profile = self._load_candidate_profile()
        self.job_criteria = self._load_job_criteria()
    
    def _load_candidate_profile(self) -> Dict[str, Any]:
        """Load candidate profile from candidate_profile.json."""
        profile_path = self.base_path / "job-agent" / "candidate_profile.json"
        
        if not profile_path.exists():
            logger.warning(f"Candidate profile not found at {profile_path}")
            return {}
        
        try:
            with open(profile_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load candidate profile: {e}")
            return {}
    
    def _load_job_criteria(self) -> Dict[str, Any]:
        """Load job search criteria from career-context."""
        career_context_path = self.base_path / self.config.get(
            "career_context_path", "../career-context"
        )
        
        criteria_file = career_context_path / "job-search-criteria.md"
        
        if not criteria_file.exists():
            logger.warning(f"Job search criteria not found at {criteria_file}")
            return {}
        
        try:
            with open(criteria_file) as f:
                return {"content": f.read()}
        except IOError as e:
            logger.error(f"Failed to load job criteria: {e}")
            return {}
    
    def evaluate_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate job fit.
        
        Args:
            job: Job data dict with title, company, posting_text, url
        
        Returns:
            Dict with fit_tier (1-3), score (0-100), resume_type (str)
        """
        prompt = self._build_evaluation_prompt(job)
        
        try:
            response = self._run_claude_prompt(prompt)
            parsed = self._parse_evaluation_response(response)
            logger.info(
                f"Evaluated {job.get('company')} - {job.get('title')}: "
                f"tier {parsed.get('fit_tier')}, score {parsed.get('score')}"
            )
            return parsed
        except Exception as e:
            logger.error(f"Failed to evaluate job: {e}", exc_info=True)
            return {
                "fit_tier": 3,
                "score": 50,
                "resume_type": "technical",
                "error": str(e),
            }
    
    def _build_evaluation_prompt(self, job: Dict[str, Any]) -> str:
        """Build the evaluation prompt for claude -p."""
        prompt = f"""You are evaluating job fit for a candidate applying to roles.

CANDIDATE PROFILE:
{json.dumps(self.candidate_profile, indent=2)}

JOB SEARCH CRITERIA:
{self.job_criteria.get("content", "No criteria provided")}

JOB TO EVALUATE:
Title: {job.get("title", "N/A")}
Company: {job.get("company", "N/A")}
URL: {job.get("url", "N/A")}

Job Posting:
{job.get("posting_text", "No posting text available")}

EVALUATION TASK:
Based on the candidate's background and the job search criteria, evaluate this job posting.

Return ONLY a JSON object (no other text) with these fields:
{{
  "fit_tier": 1,
  "compatibility_score": 85,
  "resume_type": "technical",
  "key_fit_reasons": ["reason 1", "reason 2"],
  "key_concerns": ["concern 1"] or []
}}

Where:
- fit_tier: 1 = strong match, 2 = moderate match, 3 = weak match
- compatibility_score: 0-100 (0=no fit, 100=perfect fit)
- resume_type: "technical", "executive", or "entrepreneurial"
- key_fit_reasons: Array of 1-3 reasons why this is a good fit
- key_concerns: Array of reasons to be cautious (or empty if none)
"""
        return prompt
    
    def _run_claude_prompt(self, prompt: str) -> str:
        """Run claude -p CLI with the prompt."""
        try:
            # Write prompt to temp file
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
                f.write(prompt)
                temp_path = f.name
            
            # Run claude -p
            result = subprocess.run(
                ["claude", "-p"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,  # Don't raise on non-zero exit
            )
            
            if result.returncode != 0:
                logger.warning(f"claude -p returned non-zero exit code: {result.returncode}")
                logger.warning(f"stderr: {result.stderr}")
            
            return result.stdout
        
        except FileNotFoundError:
            raise RuntimeError(
                "Claude CLI not found. Install via: npm install -g @anthropic-ai/claude"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude evaluation timed out after 30 seconds")
        finally:
            try:
                Path(temp_path).unlink()
            except NameError:
                pass
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from claude -p."""
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:].lstrip()
            
            data = json.loads(response)
            
            # Normalize field names
            return {
                "fit_tier": data.get("fit_tier", 3),
                "score": data.get("compatibility_score", 50),
                "resume_type": data.get("resume_type", "technical"),
                "fit_reasons": data.get("key_fit_reasons", []),
                "concerns": data.get("key_concerns", []),
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation response as JSON: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid JSON response from Claude: {str(e)}")


def evaluate_job_batch(
    jobs: list,
    base_path: Path,
    config: Dict[str, Any],
) -> list:
    """
    Evaluate a batch of jobs.
    
    Args:
        jobs: List of job dicts
        base_path: Base path to ApplyFlow
        config: Configuration dict
    
    Returns:
        List of jobs with evaluation data added
    """
    evaluator = JobEvaluator(base_path, config)
    evaluated_jobs = []
    
    for i, job in enumerate(jobs):
        logger.info(f"Evaluating job {i+1}/{len(jobs)}: {job.get('company')} - {job.get('title')}")
        
        eval_result = evaluator.evaluate_job(job)
        job.update(eval_result)
        evaluated_jobs.append(job)
    
    return evaluated_jobs
