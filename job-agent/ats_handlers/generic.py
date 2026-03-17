"""
Generic Handler — Fallback heuristic handler for unknown ATS platforms.

Uses common field name patterns to fill forms.
"""

import logging
from typing import Dict, Any

from .base import ATSHandler

logger = logging.getLogger(__name__)


class GenericHandler(ATSHandler):
    """Fallback handler for unrecognized ATS platforms."""
    
    async def fill_form(self, page: Any, candidate_data: Dict[str, Any]) -> bool:
        """
        Fill form using heuristic approach.
        
        Attempts to find and fill common field patterns.
        """
        logger.info("Filling generic form (heuristic approach)...")
        
        common_patterns = {
            "first_name": [
                "input[name*='first']",
                "input[placeholder*='first']",
            ],
            "last_name": [
                "input[name*='last']",
                "input[placeholder*='last']",
            ],
            "email": [
                "input[type='email']",
                "input[name*='email']",
            ],
            "phone": [
                "input[type='tel']",
                "input[name*='phone']",
            ],
        }
        
        success_count = 0
        for field_name, patterns in common_patterns.items():
            if field_name not in candidate_data or not candidate_data[field_name]:
                continue
            
            for selector in patterns:
                try:
                    if await page.locator(selector).is_visible():
                        await self.fill_text_field(page, selector, candidate_data[field_name])
                        success_count += 1
                        break
                except Exception:
                    continue
        
        logger.info(f"Generic form: filled {success_count} fields")
        return success_count > 0
    
    async def submit(self, page: Any) -> bool:
        """Submit form (look for submit button)."""
        logger.info("Submitting generic form...")
        
        submit_patterns = [
            "button[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Apply')",
            "input[type='submit']",
        ]
        
        for selector in submit_patterns:
            try:
                if await page.locator(selector).is_visible():
                    return await self.click_button(page, selector, wait_for_load=False)
            except Exception:
                continue
        
        logger.error("Could not find submit button")
        return False
    
    async def verify_success(self, page: Any) -> bool:
        """Verify submission (limited capability for generic handler)."""
        logger.info("Verifying generic form submission...")
        logger.warning("Generic handler cannot reliably verify submission")
        
        # Check if URL changed (navigation)
        try:
            await page.wait_for_load_state("networkidle", timeout=3000)
            logger.info("Network idle detected, assuming submission successful")
            return True
        except Exception:
            logger.warning("Could not verify submission")
            return False
