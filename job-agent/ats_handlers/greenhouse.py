"""
Greenhouse Handler — Greenhouse ATS form filling.

Handles single-page forms, verification code flow, PDF upload.
"""

import logging
from typing import Dict, Any

from .base import ATSHandler

logger = logging.getLogger(__name__)


class GreenhouseHandler(ATSHandler):
    """Handler for Greenhouse ATS platform."""
    
    async def fill_form(self, page: Any, candidate_data: Dict[str, Any]) -> bool:
        """
        Fill Greenhouse form.
        
        Looks for standard form fields: first_name, last_name, email, phone, resume.
        """
        logger.info("Filling Greenhouse form...")
        
        field_map = {
            "first_name": candidate_data.get("first_name", ""),
            "last_name": candidate_data.get("last_name", ""),
            "email": candidate_data.get("email", ""),
            "phone": candidate_data.get("phone", ""),
        }
        
        # Fill text fields
        for field_name, value in field_map.items():
            if not value:
                continue
            
            selector = self.field_patterns.get(field_name)
            if not selector:
                logger.warning(f"No selector for {field_name}")
                continue
            
            if not await self.fill_text_field(page, selector, value):
                return False
        
        # Upload resume
        resume_selector = self.field_patterns.get("resume")
        if resume_selector and candidate_data.get("resume_path"):
            if not await self.fill_file_field(
                page,
                resume_selector,
                candidate_data["resume_path"],
            ):
                logger.warning("Failed to upload resume, continuing anyway")
        
        logger.info("Greenhouse form filled")
        return True
    
    async def submit(self, page: Any) -> bool:
        """
        Submit Greenhouse form.
        
        Looks for submit button and clicks it.
        """
        logger.info("Submitting Greenhouse form...")
        
        # Common Greenhouse submit button selectors
        submit_selectors = [
            "button[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Apply')",
        ]
        
        for selector in submit_selectors:
            try:
                if await page.locator(selector).is_visible():
                    return await self.click_button(page, selector, wait_for_load=False)
            except Exception:
                continue
        
        logger.error("Could not find submit button")
        return False
    
    async def verify_success(self, page: Any) -> bool:
        """
        Verify Greenhouse submission success.
        
        Looks for success page indicators.
        """
        logger.info("Verifying Greenhouse submission...")
        
        success_indicators = [
            "text='Thank you'",
            "text='Application received'",
            "text='submitted successfully'",
        ]
        
        for indicator in success_indicators:
            try:
                if await page.locator(indicator).is_visible(timeout=3000):
                    logger.info("Greenhouse submission verified")
                    return True
            except Exception:
                continue
        
        logger.warning("Could not verify Greenhouse submission success")
        return False
