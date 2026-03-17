"""
ATS Handler Base Class — Abstract handler for ATS platforms.

All platform-specific handlers inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ATSHandler(ABC):
    """Abstract base handler for ATS platforms."""
    
    def __init__(self, url: str, field_patterns: Dict[str, str]):
        """
        Initialize ATS handler.
        
        Args:
            url: Job posting URL
            field_patterns: Dict of field_name -> css_selector mappings
        """
        self.url = url
        self.field_patterns = field_patterns
    
    @abstractmethod
    async def fill_form(self, page: Any, candidate_data: Dict[str, Any]) -> bool:
        """
        Fill form fields with candidate data.
        
        Args:
            page: Playwright page object
            candidate_data: Dict with fields like name, email, phone, resume_path, cover_letter_path
        
        Returns:
            True if successful, False if form structure unrecognized or fill failed
        """
        pass
    
    @abstractmethod
    async def submit(self, page: Any) -> bool:
        """
        Submit the form.
        
        Args:
            page: Playwright page object
        
        Returns:
            True if submission successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def verify_success(self, page: Any) -> bool:
        """
        Verify submission success (check for success page/message).
        
        Args:
            page: Playwright page object
        
        Returns:
            True if success detected, False otherwise
        """
        pass
    
    async def fill_text_field(
        self,
        page: Any,
        selector: str,
        value: str,
        delay_ms: int = 50,
    ) -> bool:
        """
        Fill a text input field.
        
        Args:
            page: Playwright page object
            selector: CSS selector for field
            value: Text value to enter
            delay_ms: Delay between keystrokes (ms)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await page.fill(selector, value, delay=delay_ms)
            logger.debug(f"Filled {selector} with text value")
            return True
        except Exception as e:
            logger.warning(f"Failed to fill {selector}: {e}")
            return False
    
    async def fill_file_field(
        self,
        page: Any,
        selector: str,
        file_path: str,
    ) -> bool:
        """
        Fill a file upload field.
        
        Args:
            page: Playwright page object
            selector: CSS selector for file input
            file_path: Path to file to upload
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await page.set_input_files(selector, file_path)
            logger.debug(f"Uploaded file to {selector}")
            return True
        except Exception as e:
            logger.warning(f"Failed to upload file to {selector}: {e}")
            return False
    
    async def click_button(
        self,
        page: Any,
        selector: str,
        wait_for_load: bool = True,
        wait_timeout_ms: int = 5000,
    ) -> bool:
        """
        Click a button (typically submit or next).
        
        Args:
            page: Playwright page object
            selector: CSS selector for button
            wait_for_load: Whether to wait for navigation/load after click
            wait_timeout_ms: Timeout for wait_for_load
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if wait_for_load:
                async with page.expect_navigation(timeout=wait_timeout_ms):
                    await page.click(selector)
            else:
                await page.click(selector)
            
            logger.debug(f"Clicked {selector}")
            return True
        except Exception as e:
            logger.warning(f"Failed to click {selector}: {e}")
            return False
    
    async def wait_for_element(
        self,
        page: Any,
        selector: str,
        timeout_ms: int = 5000,
    ) -> bool:
        """
        Wait for element to appear in DOM.
        
        Args:
            page: Playwright page object
            selector: CSS selector
            timeout_ms: Maximum wait time
        
        Returns:
            True if element found, False if timeout
        """
        try:
            await page.wait_for_selector(selector, timeout=timeout_ms)
            logger.debug(f"Element found: {selector}")
            return True
        except Exception as e:
            logger.warning(f"Timeout waiting for {selector}: {e}")
            return False
    
    async def get_form_html(self, page: Any, form_selector: str) -> Optional[str]:
        """
        Get HTML of form element (for debugging/logging).
        
        Args:
            page: Playwright page object
            form_selector: CSS selector for form
        
        Returns:
            HTML string or None if not found
        """
        try:
            return await page.locator(form_selector).inner_html()
        except Exception as e:
            logger.debug(f"Failed to get form HTML: {e}")
            return None
