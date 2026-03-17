"""
Ashby Handler — Ashby ATS form filling.

Modern form builder, single page, custom field types.
"""

import logging
from typing import Dict, Any

from .base import ATSHandler

logger = logging.getLogger(__name__)


class AshbyHandler(ATSHandler):
    """Handler for Ashby ATS platform."""
    
    async def fill_form(self, page: Any, candidate_data: Dict[str, Any]) -> bool:
        """Fill Ashby form."""
        logger.info("Filling Ashby form...")
        
        try:
            # Ashby uses data-test-id attributes
            field_map = {
                "first_name": "input[data-test-id='first-name']",
                "last_name": "input[data-test-id='last-name']",
                "email": "input[data-test-id='email']",
            }
            
            for field_name, selector in field_map.items():
                if field_name in candidate_data and candidate_data[field_name]:
                    await self.fill_text_field(page, selector, candidate_data[field_name])
            
            # Resume upload
            if candidate_data.get("resume_path"):
                resume_selector = "input[data-test-id='resume']"
                await self.fill_file_field(page, resume_selector, candidate_data["resume_path"])
            
            return True
        except Exception as e:
            logger.error(f"Failed to fill Ashby form: {e}")
            return False
    
    async def submit(self, page: Any) -> bool:
        """Submit Ashby form."""
        logger.info("Submitting Ashby form...")
        
        try:
            submit_selector = "button[data-test-id='submit']"
            return await self.click_button(page, submit_selector)
        except Exception as e:
            logger.error(f"Failed to submit Ashby form: {e}")
            return False
    
    async def verify_success(self, page: Any) -> bool:
        """Verify Ashby submission success."""
        logger.info("Verifying Ashby submission...")
        
        try:
            success_selector = "text='Application submitted'"
            await page.wait_for_selector(success_selector, timeout=5000)
            return True
        except Exception:
            logger.warning("Could not verify Ashby submission")
            return False
