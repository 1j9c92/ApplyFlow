"""
Job Search — LinkedIn scraper orchestrator.

Deduplication, normalization, ATS platform detection.
"""

import json
import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class JobSearchOrchestrator:
    """Coordinates LinkedIn scraping and job normalization."""
    
    # Mapping of common ATS URLs to platform names
    ATS_PATTERNS = {
        r"greenhouse\.io": "greenhouse",
        r"workday\.com": "workday",
        r"ashby\.io": "ashby",
        r"lever\.co": "lever",
        r"apply\.workable\.com": "workable",
        r"bamboohr\.com": "bamboohr",
        r"smartrecruiters\.com": "smartrecruiters",
    }
    
    def __init__(self, base_path: Path, config: Dict):
        """
        Initialize job search orchestrator.
        
        Args:
            base_path: Base path to ApplyFlow
            config: Configuration dict
        """
        self.base_path = base_path
        self.config = config
        self.jobs_dir = base_path / "job-agent" / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape_linkedin_jobs(self) -> List[Dict]:
        """
        Scrape LinkedIn saved jobs.
        
        Returns:
            List of raw job dicts from LinkedIn
        """
        logger.info("Starting LinkedIn scrape...")
        
        script_path = (
            self.base_path / "job-agent" / "playwright_scripts" / "search_linkedin.py"
        )
        
        if not script_path.exists():
            raise FileNotFoundError(f"LinkedIn scraper not found: {script_path}")
        
        try:
            result = subprocess.run(
                ["python", str(script_path)],
                cwd=str(self.base_path / "job-agent"),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                check=False,  # Don't raise on non-zero
            )
            
            if result.returncode != 0:
                logger.error(f"LinkedIn scraper failed: {result.stderr}")
                raise RuntimeError(f"Scraper error: {result.stderr}")
            
            # Parse output as JSON
            try:
                jobs = json.loads(result.stdout)
                logger.info(f"Scraped {len(jobs)} jobs from LinkedIn")
                return jobs
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse scraper output as JSON: {e}")
                raise
        
        except subprocess.TimeoutExpired:
            raise RuntimeError("LinkedIn scraper timed out after 5 minutes")
    
    def normalize_job(self, raw_job: Dict) -> Dict:
        """
        Normalize a raw job from LinkedIn to standard format.
        
        Args:
            raw_job: Raw job dict from LinkedIn scraper
        
        Returns:
            Normalized job dict
        """
        # Extract ATS platform from URL
        ats_platform = self._detect_ats_platform(raw_job.get("url", ""))
        
        normalized = {
            "id": self._generate_job_id(raw_job),
            "title": raw_job.get("title", "").strip(),
            "company": raw_job.get("company", "").strip(),
            "url": raw_job.get("url", "").strip(),
            "posting_text": raw_job.get("posting_text", "").strip(),
            "ats_platform": ats_platform,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "location": raw_job.get("location", "").strip(),
            "job_type": raw_job.get("job_type", "").strip(),
            "seniority": raw_job.get("seniority_level", "").strip(),
            "linkedin_job_id": raw_job.get("linkedin_job_id", ""),
        }
        
        return normalized
    
    def _detect_ats_platform(self, url: str) -> str:
        """
        Detect ATS platform from job URL.
        
        Args:
            url: Job posting URL
        
        Returns:
            Platform name or "generic" if not recognized
        """
        for pattern, platform in self.ATS_PATTERNS.items():
            if re.search(pattern, url, re.IGNORECASE):
                logger.debug(f"Detected {platform} from {url}")
                return platform
        
        logger.debug(f"Unknown ATS platform for {url}")
        return "generic"
    
    def _generate_job_id(self, job: Dict) -> str:
        """Generate unique job ID from LinkedIn job ID or URL."""
        linkedin_id = job.get("linkedin_job_id")
        if linkedin_id:
            return f"linkedin_{linkedin_id}"
        
        # Fallback: hash URL
        import hashlib
        url_hash = hashlib.md5(job.get("url", "").encode()).hexdigest()[:12]
        return f"job_{url_hash}"
    
    def deduplicate_jobs(
        self,
        new_jobs: List[Dict],
        existing_queue: Dict,
    ) -> List[Dict]:
        """
        Deduplicate new jobs against existing queue.
        
        Args:
            new_jobs: List of new job dicts
            existing_queue: Existing job queue from job_queue.json
        
        Returns:
            List of genuinely new jobs
        """
        existing_ids = set()
        for job_id in existing_queue.get("jobs", {}).keys():
            existing_ids.add(job_id)
        
        deduplicated = []
        for job in new_jobs:
            if job["id"] not in existing_ids:
                deduplicated.append(job)
            else:
                logger.debug(f"Skipping duplicate job: {job['id']}")
        
        logger.info(f"Deduplicated {len(new_jobs)} jobs down to {len(deduplicated)} new jobs")
        return deduplicated
    
    def save_jobs_to_disk(self, jobs: List[Dict]) -> None:
        """
        Save jobs to disk in organized structure.
        
        Args:
            jobs: List of job dicts
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        date_dir = self.jobs_dir / today
        date_dir.mkdir(parents=True, exist_ok=True)
        
        for job in jobs:
            job_file = date_dir / f"{job['id']}.json"
            with open(job_file, "w") as f:
                json.dump(job, f, indent=2)
        
        logger.info(f"Saved {len(jobs)} jobs to {date_dir}")
    
    def load_jobs_from_disk(self, days: int = 30) -> List[Dict]:
        """
        Load jobs from disk (recent N days).
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of job dicts
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        jobs = []
        
        if not self.jobs_dir.exists():
            return jobs
        
        for date_dir in self.jobs_dir.iterdir():
            if not date_dir.is_dir():
                continue
            
            try:
                dir_date = datetime.fromisoformat(date_dir.name)
                if dir_date < cutoff_date:
                    continue
            except ValueError:
                continue
            
            for job_file in date_dir.glob("*.json"):
                try:
                    with open(job_file) as f:
                        jobs.append(json.load(f))
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load {job_file}: {e}")
        
        logger.info(f"Loaded {len(jobs)} jobs from disk")
        return jobs


def scrape_and_normalize(base_path: Path, config: Dict) -> List[Dict]:
    """
    End-to-end: scrape LinkedIn, normalize, save.
    
    Args:
        base_path: Base path to ApplyFlow
        config: Configuration dict
    
    Returns:
        List of normalized job dicts
    """
    orchestrator = JobSearchOrchestrator(base_path, config)
    
    # Scrape
    raw_jobs = orchestrator.scrape_linkedin_jobs()
    
    # Normalize
    normalized = [orchestrator.normalize_job(job) for job in raw_jobs]
    
    # Save
    orchestrator.save_jobs_to_disk(normalized)
    
    return normalized
