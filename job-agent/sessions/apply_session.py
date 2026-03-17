"""
Session A — Apply

Submits applications to ATS platforms.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def run_apply(
    base_path: Path,
    config: Dict[str, Any],
    logger: logging.Logger,
    queue: Dict,
    company: Optional[str] = None,
) -> None:
    """
    Run Session A: Apply.
    
    TODO:
    1. Filter job_queue for status == "cover_letter_ready"
    2. Sort by score (highest first)
    3. Optionally filter by company
    4. For each job:
       a. Load resume + cover letter
       b. Merge to PDF
       c. Spawn apply_universal.py
       d. Handle auth, form, submission
       e. Update job_queue & LinkedIn
    5. Return with updated queue
    """
    logger.info("Session A: Apply")
    logger.warning("Apply session: full implementation pending")
    
    # Placeholder
    pass
