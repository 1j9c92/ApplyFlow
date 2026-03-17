"""
Session S — Search & Evaluate

Scrapes LinkedIn, evaluates fit, prepares for application.
"""

import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def run_search(
    base_path: Path,
    config: Dict[str, Any],
    logger: logging.Logger,
    queue: Dict,
    review: bool = False,
) -> None:
    """
    Run Session S: Search & Evaluate.
    
    TODO:
    1. Scrape LinkedIn saved jobs
    2. Deduplicate against job_queue
    3. For each new job:
       a. Evaluate fit via claude -p
       b. Find matching cover letter
       c. Update job_queue status
    4. If review: pause for human approval
    5. Return with updated queue
    """
    logger.info("Session S: Search & Evaluate")
    logger.warning("Search session: full implementation pending")
    
    # Placeholder
    pass
