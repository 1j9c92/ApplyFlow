"""
Lever Handler — Lever ATS form filling.

Single page, custom rich text fields, file upload.
"""

import logging
from typing import Dict, Any

from .base import ATSHandler

logger = logging.getLogger(__name__)


class LeverHandler(ATSHandler):
    """Handler for Lever ATS platform."""
    
    async def fill_form(self, page: Any, candidate_data: Dict[str, Any]) -> bool:
        """Fill Lever form."""
        logger.info("Filling Lever form...")
        
        try:
            # Lever uses name attributes
            field_map = {
                "first_name": "input[name='firstName']",
                "last_name": "input[name='lastName']",
                "email": "input[name='email']",
                "phone": "input[name='phone']",
            }
            
            for field_name, selector in field_map.items():
                if field_name in candidate_data and candidate_data[field_name]:
                    await self.fill_text_field(page, selector, candidate_data[field_name])
            
            # Resume
            if candidate_data.get("resume_path"):
                resume_selector = "input[name='resume']"
                await self.fill_file_field(page, resume_selector, candidate_data["resume_path"])
            
            return True
        except Exception as e:
            logger.error(f"Failed to fill Lever form: {e}")
            return False
    
    async def submit(self, page: Any) -> bool:
        """Submit Lever form."""
        logger.info("Submitting Lever form...")
        
        try:
            submit_selector = "button:has-text('Apply')"
            return await self.click_button(page, submit_selector)
        except Exception as e:
            logger.error(f"Failed to submit Lever form: {e}")
            return False
    
    async def verify_success(self, page: Any) -> bool:
        """Verify Lever submission success."""
        logger.info("Verifying Lever submission...")
        
        try:
            success_selector = "text='Thank you for applying'"
            await page.wait_for_selector(success_selector, timeout=5000)
            return True
        except Exception:
            logger.warning("Could not verify Lever submission")
            return False
