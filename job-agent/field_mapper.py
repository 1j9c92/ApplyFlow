"""
Field Mapper — Two-tier strategy for form field identification.

Tier 1: Pattern matcher (fast, learned from past applications)
Tier 2: LLM-in-the-loop (accurate, learns new patterns)
"""

import base64
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any

from pattern_matcher import PatternMatcher

logger = logging.getLogger(__name__)


class FieldMapper:
    """Maps form fields using two-tier strategy."""
    
    def __init__(self, base_path: Path, config: Dict[str, Any]):
        """
        Initialize field mapper.
        
        Args:
            base_path: Base path to job-agent directory
            config: Configuration dict
        """
        self.base_path = base_path
        self.config = config
        self.pattern_matcher = PatternMatcher(base_path)
    
    async def map_fields(
        self,
        page: Any,
        platform: str,
        form_id: str,
        form_selector: str,
    ) -> Dict[str, str]:
        """
        Map form fields to candidate data fields.
        
        Tries Tier 1 (pattern match) first, falls back to Tier 2 (LLM) if needed.
        
        Args:
            page: Playwright page object
            platform: ATS platform name
            form_id: Form identifier
            form_selector: CSS selector for form element
        
        Returns:
            Dict mapping field_name -> css_selector
        """
        logger.info(f"Mapping fields for {platform}/{form_id}...")
        
        # Tier 1: Try pattern matcher
        pattern = self.pattern_matcher.get_pattern(platform, form_id)
        if pattern:
            logger.info("Using learned pattern (Tier 1)")
            return pattern.get("fields", {})
        
        # Tier 2: LLM-in-the-loop
        logger.info("Using LLM-in-the-loop (Tier 2)...")
        field_map = await self._map_fields_llm(page, form_selector)
        
        if field_map:
            self.pattern_matcher.learn_pattern(platform, form_id, field_map)
        
        return field_map
    
    async def _map_fields_llm(
        self,
        page: Any,
        form_selector: str,
    ) -> Optional[Dict[str, str]]:
        """
        Use LLM to identify form fields.
        
        Args:
            page: Playwright page object
            form_selector: CSS selector for form
        
        Returns:
            Dict of field_name -> css_selector or None if failed
        """
        try:
            # Get form HTML
            form_html = await page.locator(form_selector).inner_html()
            if not form_html:
                logger.error("Could not get form HTML")
                return None
            
            # Build LLM prompt
            prompt = self._build_field_mapping_prompt(form_html)
            
            # Call Claude
            response = await self._call_claude_for_mapping(prompt)
            
            # Parse response
            field_map = self._parse_field_mapping_response(response)
            
            if field_map:
                logger.info(f"LLM identified {len(field_map)} fields")
            
            return field_map
        
        except Exception as e:
            logger.error(f"LLM field mapping failed: {e}")
            return None
    
    def _build_field_mapping_prompt(self, form_html: str) -> str:
        """Build prompt for Claude to identify form fields."""
        prompt = f"""Analyze this HTML form and map each field to its purpose.

HTML:
{form_html}

Return ONLY a JSON object (no other text) mapping field names to CSS selectors:
{{
  "first_name": "input[name='first_name']",
  "last_name": "input[name='last_name']",
  "email": "input[type='email']",
  ...
}}

Standard field names: first_name, last_name, email, phone, resume, cover_letter, message, linkedin_url, website, etc.

For each visible input/textarea in the form, identify what it's for and provide its CSS selector.
"""
        return prompt
    
    async def _call_claude_for_mapping(self, prompt: str) -> str:
        """Call Claude CLI for field mapping."""
        try:
            result = subprocess.run(
                ["claude", "-p"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            
            return result.stdout
        except FileNotFoundError:
            logger.error("Claude CLI not found")
            return ""
    
    def _parse_field_mapping_response(self, response: str) -> Optional[Dict[str, str]]:
        """Parse JSON response from Claude."""
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1].lstrip("json").strip()
            
            field_map = json.loads(response)
            return field_map
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse field mapping response: {e}")
            return None
