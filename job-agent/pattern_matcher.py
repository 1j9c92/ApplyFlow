"""
Pattern Matcher — Learn and match form field selectors.

Tier 1 of field mapping strategy: instant pattern matching.
Grows over time as more applications are completed.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class PatternMatcher:
    """Learns and applies CSS selector patterns for form fields."""
    
    def __init__(self, base_path: Path):
        """
        Initialize pattern matcher.
        
        Args:
            base_path: Base path to job-agent directory
        """
        self.base_path = base_path
        self.patterns_file = base_path / "field_patterns.json"
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load patterns from file. Create empty dict if not found."""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load patterns: {e}")
                return {}
        
        return {}
    
    def save_patterns(self) -> None:
        """Save patterns to file."""
        with open(self.patterns_file, "w") as f:
            json.dump(self.patterns, f, indent=2)
        
        logger.debug(f"Saved {len(self.patterns)} pattern sets")
    
    def get_pattern(self, platform: str, form_id: str) -> Optional[Dict]:
        """
        Get learned pattern for a platform/form combination.
        
        Args:
            platform: ATS platform name (greenhouse, workday, etc)
            form_id: Form identifier (e.g., form's data-form-id or name)
        
        Returns:
            Pattern dict or None if not found
        """
        key = f"{platform}_{form_id}"
        
        if key in self.patterns:
            logger.debug(f"Found pattern for {key}")
            return self.patterns[key]
        
        logger.debug(f"No pattern found for {key}")
        return None
    
    def learn_pattern(
        self,
        platform: str,
        form_id: str,
        field_map: Dict[str, str],
    ) -> None:
        """
        Learn a new pattern from a successful application.
        
        Args:
            platform: ATS platform name
            form_id: Form identifier
            field_map: Dict of field_name -> css_selector mappings
        """
        key = f"{platform}_{form_id}"
        
        self.patterns[key] = {
            "platform": platform,
            "form_id": form_id,
            "fields": field_map,
            "learned_at": __import__("datetime").datetime.utcnow().isoformat(),
        }
        
        self.save_patterns()
        logger.info(f"Learned pattern for {key}")
    
    def get_all_patterns_for_platform(self, platform: str) -> List[Dict]:
        """Get all learned patterns for a platform."""
        return [p for p in self.patterns.values() if p.get("platform") == platform]
    
    def match_field(
        self,
        platform: str,
        field_name: str,
        form_html: str = None,
    ) -> Optional[str]:
        """
        Try to match a field selector using learned patterns.
        
        Args:
            platform: ATS platform name
            field_name: Name of field (first_name, email, resume, etc)
            form_html: HTML of form (for context if needed)
        
        Returns:
            CSS selector string or None if no match found
        """
        # Search all patterns for this platform
        for pattern_key, pattern_data in self.patterns.items():
            if pattern_data.get("platform") == platform:
                fields = pattern_data.get("fields", {})
                if field_name in fields:
                    selector = fields[field_name]
                    logger.debug(f"Matched {field_name} using pattern {pattern_key}: {selector}")
                    return selector
        
        logger.debug(f"No pattern match for {field_name} on {platform}")
        return None
    
    def merge_field_map(
        self,
        platform: str,
        form_id: str,
        new_fields: Dict[str, str],
    ) -> None:
        """
        Merge new field mappings into existing pattern.
        
        Args:
            platform: ATS platform name
            form_id: Form identifier
            new_fields: Dict of field_name -> selector pairs to add
        """
        key = f"{platform}_{form_id}"
        
        if key not in self.patterns:
            self.learn_pattern(platform, form_id, new_fields)
            return
        
        # Merge with existing
        existing_fields = self.patterns[key].get("fields", {})
        existing_fields.update(new_fields)
        self.patterns[key]["fields"] = existing_fields
        
        self.save_patterns()
        logger.info(f"Merged {len(new_fields)} fields into pattern {key}")


def get_common_selectors() -> Dict[str, List[str]]:
    """
    Get common CSS selectors for standard form fields.
    
    Returns:
        Dict mapping field names to list of common selectors (priority order)
    """
    return {
        "first_name": [
            "input[name='first_name']",
            "input[name='firstName']",
            "input[name='first-name']",
            "input[placeholder*='First']",
        ],
        "last_name": [
            "input[name='last_name']",
            "input[name='lastName']",
            "input[name='last-name']",
            "input[placeholder*='Last']",
        ],
        "email": [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='email']",
        ],
        "phone": [
            "input[type='tel']",
            "input[name='phone']",
            "input[name='phone_number']",
            "input[placeholder*='phone']",
        ],
        "resume": [
            "input[type='file'][accept*='pdf']",
            "input[type='file'][name*='resume']",
            "input[type='file'][name*='cv']",
        ],
        "cover_letter": [
            "input[type='file'][name*='cover']",
            "input[type='file'][accept*='pdf']",
        ],
        "message": [
            "textarea[name*='message']",
            "textarea[placeholder*='message']",
        ],
    }
