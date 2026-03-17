#!/usr/bin/env python3
"""
ApplyFlow Job Agent — Main Orchestrator

Routes to Search, Apply, or Outreach sessions.
Manages state, job queue, and session chaining.
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup logging
def setup_logging(base_path: Path, session: str) -> logging.Logger:
    """Configure logging to session-specific log file."""
    log_dir = base_path / "logs" / session
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Also log to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def load_config(base_path: Path) -> dict:
    """Load configuration from config.json."""
    config_path = base_path / "config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Copy config.example.json to config.json and fill in your values."
        )
    
    with open(config_path) as f:
        return json.load(f)


def load_state(base_path: Path) -> dict:
    """Load agent state. Create if missing."""
    state_path = base_path / "agent_state.json"
    
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    
    # Initialize new state
    return {
        "last_search": None,
        "last_apply": None,
        "last_outreach": None,
        "current_session": None,
        "job_count_evaluated": 0,
        "job_count_applied": 0,
    }


def save_state(base_path: Path, state: dict) -> None:
    """Save agent state."""
    state_path = base_path / "agent_state.json"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def load_job_queue(base_path: Path) -> dict:
    """Load job queue. Create if missing."""
    queue_path = base_path / "job_queue.json"
    
    if queue_path.exists():
        with open(queue_path) as f:
            return json.load(f)
    
    # Initialize new queue
    return {
        "jobs": {},
        "pending_evaluation": [],
        "pending_application": [],
        "pending_outreach": [],
        "completed": [],
    }


def save_job_queue(base_path: Path, queue: dict) -> None:
    """Save job queue."""
    queue_path = base_path / "job_queue.json"
    with open(queue_path, "w") as f:
        json.dump(queue, f, indent=2)


def run_search_session(
    base_path: Path,
    config: dict,
    logger: logging.Logger,
    review: bool = False,
    chain: bool = False,
) -> None:
    """Run Session S (Search & Evaluate)."""
    logger.info("=" * 60)
    logger.info("Session S: Search & Evaluate")
    logger.info("=" * 60)
    
    try:
        # Import here to avoid circular dependencies
        from sessions.search_session import run_search
        
        state = load_state(base_path)
        queue = load_job_queue(base_path)
        
        state["current_session"] = "search"
        state["last_search"] = datetime.utcnow().isoformat() + "Z"
        
        run_search(base_path, config, logger, queue, review)
        
        save_state(base_path, state)
        save_job_queue(base_path, queue)
        
        logger.info("Session S completed")
        
        if chain:
            logger.info("Chaining to Session A...")
            spawn_session("apply", base_path, config, logger, chain=True)
    
    except Exception as e:
        logger.error(f"Session S failed: {e}", exc_info=True)
        sys.exit(1)


def run_apply_session(
    base_path: Path,
    config: dict,
    logger: logging.Logger,
    company: Optional[str] = None,
    chain: bool = False,
) -> None:
    """Run Session A (Apply)."""
    logger.info("=" * 60)
    logger.info("Session A: Apply")
    logger.info("=" * 60)
    
    try:
        from sessions.apply_session import run_apply
        
        state = load_state(base_path)
        queue = load_job_queue(base_path)
        
        state["current_session"] = "apply"
        state["last_apply"] = datetime.utcnow().isoformat() + "Z"
        
        run_apply(base_path, config, logger, queue, company)
        
        save_state(base_path, state)
        save_job_queue(base_path, queue)
        
        logger.info("Session A completed")
        
        if chain:
            logger.info("Chaining to Session O...")
            spawn_session("outreach", base_path, config, logger, chain=True)
    
    except Exception as e:
        logger.error(f"Session A failed: {e}", exc_info=True)
        sys.exit(1)


def run_outreach_session(
    base_path: Path,
    config: dict,
    logger: logging.Logger,
) -> None:
    """Run Session O (Outreach)."""
    logger.info("=" * 60)
    logger.info("Session O: Outreach")
    logger.info("=" * 60)
    
    try:
        from sessions.outreach_session import run_outreach
        
        state = load_state(base_path)
        queue = load_job_queue(base_path)
        
        state["current_session"] = "outreach"
        state["last_outreach"] = datetime.utcnow().isoformat() + "Z"
        
        run_outreach(base_path, config, logger, queue)
        
        save_state(base_path, state)
        save_job_queue(base_path, queue)
        
        logger.info("Session O completed")
    
    except Exception as e:
        logger.error(f"Session O failed: {e}", exc_info=True)
        sys.exit(1)


def spawn_session(
    session: str,
    base_path: Path,
    config: dict,
    logger: logging.Logger,
    chain: bool = False,
) -> None:
    """Spawn next session in new Terminal window via AppleScript (macOS only)."""
    cmd = f'cd "{base_path}/job-agent" && python main.py --session {session}'
    if chain:
        cmd += " --chain"
    
    script = f'''
tell application "Terminal"
    do script "{cmd}"
end tell
'''
    
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        logger.info(f"Spawned Session {session.upper()} in new Terminal window")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to spawn session: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ApplyFlow Job Agent — Search, Apply, Outreach"
    )
    parser.add_argument(
        "--session",
        choices=["search", "apply", "outreach"],
        required=True,
        help="Session to run",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Pause for human review (Search session only)",
    )
    parser.add_argument(
        "--chain",
        action="store_true",
        help="Auto-spawn next session after completion",
    )
    parser.add_argument(
        "--company",
        type=str,
        help="Filter jobs by company (Apply session only)",
    )
    
    args = parser.parse_args()
    
    # Determine base path (parent of job-agent/)
    base_path = Path(__file__).parent.parent
    
    # Load config
    try:
        config = load_config(base_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Setup logging
    logger = setup_logging(base_path / "job-agent", args.session)
    logger.info(f"ApplyFlow Job Agent v1.0 starting")
    logger.info(f"Session: {args.session.upper()}")
    logger.info(f"Base path: {base_path}")
    
    # Route to session
    if args.session == "search":
        run_search_session(base_path, config, logger, args.review, args.chain)
    elif args.session == "apply":
        run_apply_session(base_path, config, logger, args.company, args.chain)
    elif args.session == "outreach":
        run_outreach_session(base_path, config, logger)
    
    logger.info("ApplyFlow Job Agent exited successfully")


if __name__ == "__main__":
    main()
