"""
Session O — Outreach

Finds hiring managers and drafts connection messages.
"""

import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def run_outreach(
    base_path: Path,
    config: Dict[str, Any],
    logger: logging.Logger,
    queue: Dict,
) -> None:
    """
    Run Session O: Outreach.
    
    TODO:
    1. Filter job_queue for status == "applied" AND recently applied
    2. For each job:
       a. Search LinkedIn for hiring manager
       b. Search for HR/recruiting contact
       c. Draft 2 connection messages per contact
       d. Write to outreach/{date}/{Company - Role}/outreach.md
    3. Update job_queue with outreach_drafted status
    4. Return with updated queue
    """
    logger.info("Session O: Outreach")
    logger.warning("Outreach session: full implementation pending")
    
    # Placeholder
    pass
