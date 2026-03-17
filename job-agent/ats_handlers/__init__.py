"""ATS Handlers — Platform-specific form filling."""

from .base import ATSHandler
from .greenhouse import GreenhouseHandler
from .workday import WorkdayHandler
from .ashby import AshbyHandler
from .lever import LeverHandler
from .generic import GenericHandler

__all__ = [
    "ATSHandler",
    "GreenhouseHandler",
    "WorkdayHandler",
    "AshbyHandler",
    "LeverHandler",
    "GenericHandler",
]


def get_handler(platform: str, url: str, field_patterns: dict) -> ATSHandler:
    """Get the appropriate handler for a platform."""
    handlers = {
        "greenhouse": GreenhouseHandler,
        "workday": WorkdayHandler,
        "ashby": AshbyHandler,
        "lever": LeverHandler,
    }
    
    handler_class = handlers.get(platform, GenericHandler)
    return handler_class(url, field_patterns)
