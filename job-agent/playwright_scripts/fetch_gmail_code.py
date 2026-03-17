#!/usr/bin/env python3
"""
Fetch Gmail Code — Retrieve Greenhouse verification code from Gmail.

Background thread to poll Gmail for verification emails.

TODO: Implement Gmail API polling.
"""

import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_verification_code(email: str, timeout_seconds: int = 30) -> str:
    """
    Poll Gmail for verification code from Greenhouse.
    
    TODO:
    1. Use Gmail API to poll for emails from greenhouse.io
    2. Extract verification code from email body
    3. Return code or timeout
    """
    logger.warning("fetch_gmail_code: full implementation pending")
    raise TimeoutError("No verification code found")


def main():
    """Entry point."""
    if len(sys.argv) < 2:
        logger.error("Usage: fetch_gmail_code.py <email> [timeout_seconds]")
        sys.exit(1)
    
    email = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    try:
        import asyncio
        code = asyncio.run(fetch_verification_code(email, timeout))
        print(json.dumps({"code": code}))
    except Exception as e:
        logger.error(f"Failed to fetch code: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
