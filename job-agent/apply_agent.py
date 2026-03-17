"""
Apply Agent — Application orchestrator.

Handles auth routing, PDF creation, subprocess spawning, error handling.
"""

import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Optional

from account_manager import AccountManager
from pdf_merger import merge_pdfs

logger = logging.getLogger(__name__)


class ApplyAgent:
    """Orchestrates applications to jobs."""
    
    def __init__(self, base_path: Path, config: Dict[str, Any]):
        """
        Initialize apply agent.
        
        Args:
            base_path: Base path to ApplyFlow
            config: Configuration dict
        """
        self.base_path = base_path
        self.config = config
        self.account_manager = AccountManager(config, base_path)
    
    def apply_to_job(
        self,
        job: Dict[str, Any],
        resume_path: str,
        cover_letter_path: str,
    ) -> Dict[str, Any]:
        """
        Apply to a single job.
        
        Args:
            job: Job dict with title, company, url, ats_platform
            resume_path: Path to resume file
            cover_letter_path: Path to cover letter file
        
        Returns:
            Result dict with success, error_msg, etc
        """
        logger.info(f"Applying to {job['company']} - {job['title']}")
        
        try:
            # 1. Merge PDF
            combined_pdf = self._create_combined_pdf(resume_path, cover_letter_path)
            if not combined_pdf:
                return {
                    "success": False,
                    "error_msg": "Failed to create combined PDF",
                    "job_id": job["id"],
                }
            
            # 2. Warmup auth
            self.account_manager.warmup_1password()
            
            # 3. Load field patterns
            field_patterns = self._load_field_patterns()
            
            # 4. Prepare candidate data
            candidate_data = self._load_candidate_data(resume_path, cover_letter_path, combined_pdf)
            
            # 5. Spawn apply_universal.py
            result = self._spawn_apply_subprocess(
                job,
                combined_pdf,
                candidate_data,
                field_patterns,
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Application failed: {e}", exc_info=True)
            return {
                "success": False,
                "error_msg": str(e),
                "job_id": job["id"],
            }
    
    def _create_combined_pdf(self, resume_path: str, cover_letter_path: str) -> Optional[str]:
        """Merge resume and cover letter to single PDF."""
        output_path = self.base_path / "job-agent" / "temp" / "combined.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if merge_pdfs(resume_path, cover_letter_path, str(output_path)):
            return str(output_path)
        
        return None
    
    def _load_field_patterns(self) -> Dict:
        """Load learned field patterns."""
        patterns_file = self.base_path / "job-agent" / "field_patterns.json"
        
        if patterns_file.exists():
            try:
                with open(patterns_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load patterns: {e}")
        
        return {}
    
    def _load_candidate_data(
        self,
        resume_path: str,
        cover_letter_path: str,
        combined_pdf: str,
    ) -> Dict[str, Any]:
        """Prepare candidate data for form filling."""
        profile_path = self.base_path / "job-agent" / "candidate_profile.json"
        
        if profile_path.exists():
            try:
                with open(profile_path) as f:
                    profile = json.load(f)
                    personal = profile.get("personal", {})
                    return {
                        "first_name": personal.get("name", "").split()[0] if personal.get("name") else "",
                        "last_name": personal.get("name", "").split()[-1] if personal.get("name") else "",
                        "email": personal.get("email", ""),
                        "phone": personal.get("phone", ""),
                        "resume_path": resume_path,
                        "cover_letter_path": cover_letter_path,
                        "combined_pdf_path": combined_pdf,
                    }
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load candidate profile: {e}")
        
        return {"resume_path": resume_path, "combined_pdf_path": combined_pdf}
    
    def _spawn_apply_subprocess(
        self,
        job: Dict[str, Any],
        pdf_path: str,
        candidate_data: Dict[str, Any],
        field_patterns: Dict,
    ) -> Dict[str, Any]:
        """
        Spawn apply_universal.py subprocess.
        
        TODO: Implement subprocess spawning with proper arg passing.
        """
        logger.warning("_spawn_apply_subprocess: full implementation pending")
        
        return {
            "success": False,
            "error_msg": "Not implemented",
            "job_id": job["id"],
        }
