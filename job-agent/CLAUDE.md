# ApplyFlow Job Agent — Session Instructions

This is the main orchestrator for the three-session job application architecture (S → A → O).

## Overview

ApplyFlow automates job search, application, and outreach via a three-session workflow:

1. **Session S (Search & Evaluate):** Scrapes saved jobs, evaluates fit, prepares for applications
2. **Session A (Apply):** Submits applications across ATS platforms
3. **Session O (Outreach):** Finds hiring managers, drafts connection messages

Each session runs independently but can chain via `--chain` flag.

## Architecture & Key Rules

### Automation Strategy
- **Playwright only** for headless automation (no Claude-in-Chrome or Kapture)
- **Subprocess pattern:** All browser automation runs in separate Python processes
- **Integration point:** Cover letter loop supplies application materials to job-agent
- **State management:** `agent_state.json` and `job_queue.json` track progress

### Config & Credentials
- All configuration loaded from `config.json` (see `config.example.json`)
- Credentials managed via 1Password OR fallback `accounts.json`
- No hardcoded paths, emails, or secrets
- Environment variables as override mechanism

### Session Spawning
On macOS, use AppleScript to launch new Terminal windows for chaining:
```bash
osascript -e 'tell application "Terminal" to do script "cd /path/to/ApplyFlow/job-agent && python main.py --session apply --chain"'
```

## Command Reference

```bash
# Session S: Search & evaluate
python main.py --session search --review              # Pause for human review
python main.py --session search --chain               # Auto-chain to apply

# Session A: Apply to jobs
python main.py --session apply --chain                # Apply & chain to outreach
python main.py --session apply --company "ACME"       # Apply only to ACME jobs

# Session O: Outreach to contacts
python main.py --session outreach --chain             # Continue chaining

# Full automated pipeline
python main.py --session search --chain               # Starts S → A → O
```

## Session Responsibilities

### Session S (Search & Evaluate)
- Run Playwright scraper to fetch LinkedIn saved jobs
- Deduplicate and normalize job data
- Evaluate each job using `claude -p` CLI (reads candidate profile, role preferences)
- Assign fit tier (1-3), compatibility score, preferred resume type
- Lookup matching cover letters from cover-letter-loop drafts
- Update job status: pending → evaluated → (cover_letter_ready / needs_cover_letter)
- Optional: Pause for human review before proceeding
- If --chain, auto-spawn Session A

### Session A (Apply)
- For each cover_letter_ready job (highest score first):
  - Fetch resume and cover letter from files
  - Merge resume + cover letter into single PDF
  - Launch `apply_universal.py` subprocess
  - Handle auth routing (1Password or local fallback)
  - Navigate ATS form, fill fields, upload documents, submit
  - On success: Mark applied, update LinkedIn status
  - On failure: Log error, move to next job
- If --chain, auto-spawn Session O

### Session O (Outreach)
- For each newly applied job:
  - Search LinkedIn for hiring manager
  - Search for secondary contact (HR/recruiting)
  - Draft 2 connection message options per contact (~300 chars each)
  - Write all drafts to `outreach/{YYYY-MM-DD}/{Company - Role}/outreach.md`
  - Note: Messages are **drafts only** — user sends manually

## File Structure

```
job-agent/
├── CLAUDE.md                    # This file
├── program.md                   # Detailed architecture & flow diagrams
├── main.py                      # Orchestrator entry point
├── apply_agent.py               # Application orchestrator
├── claude_agent.py              # Job evaluation via claude -p
├── job_search.py                # Scraper orchestrator
├── field_mapper.py              # Two-tier field mapping (pattern + LLM)
├── account_manager.py           # 1Password credential management
├── pattern_matcher.py           # Learn and match form field patterns
├── config.example.json          # Config template
├── candidate_profile.json       # Candidate data template
├── agent_state.json             # Runtime state (created on first run)
├── job_queue.json               # Queue of jobs to process
├── ats_handlers/
│   ├── base.py                  # Abstract base handler
│   ├── workday.py               # Workday multi-step
│   ├── greenhouse.py            # Greenhouse
│   ├── ashby.py                 # Ashby
│   ├── lever.py                 # Lever
│   └── generic.py               # Fallback heuristic
└── playwright_scripts/
    ├── apply_universal.py       # Primary ATS filler
    ├── search_linkedin.py        # LinkedIn saved jobs scraper
    ├── mark_linkedin_applied.py  # Post-apply LinkedIn update
    ├── linkedin_outreach.py      # Contact finder
    ├── fetch_gmail_code.py       # Greenhouse code fetcher
    ├── handle_ats_auth.py        # Auth state router
    ├── setup_linkedin_auth.py    # One-time LinkedIn auth
    └── mac_dialogs.py            # macOS dialog automation
```

## Integration Points

### With cover-letter-loop
- Job-agent reads final cover letters from `../cover-letter-loop/drafts/`
- Looks up by: job title, company, role level
- Expected format: `{company}_{role}_{date}.docx`

### With Claude CLI
- Evaluation via: `claude -p < evaluation_prompt.txt`
- Reads user's career context from `../career-context/profile.md`
- Reads job search criteria from `../career-context/job-search-criteria.md`

### With LinkedIn
- Playwright auth persisted in `{base_path}/playwright_scripts/linkedin_auth.json`
- Post-application LinkedIn updates via browser automation

### With 1Password
- Credentials fetched from vault (name configurable in config.json)
- Fallback to `accounts.json` if 1Password unavailable
- Warmup + keepalive pattern in account_manager

## State Management

### agent_state.json
```json
{
  "last_search": "2026-03-17T14:30:00Z",
  "last_apply": "2026-03-17T15:45:00Z",
  "last_outreach": null,
  "current_session": "search",
  "job_count_evaluated": 42,
  "job_count_applied": 8
}
```

### job_queue.json
```json
{
  "pending_evaluation": ["job_1", "job_2"],
  "pending_application": ["job_3", "job_4"],
  "pending_outreach": ["job_5"],
  "completed": ["job_6", "job_7"]
}
```

## Error Handling

- Failed Playwright navigation: Retry with increased timeout, then fail gracefully
- ATS form unrecognized: Log form HTML, prompt for manual intervention
- Missing cover letter: Mark job as needs_cover_letter, skip application
- 1Password unavailable: Fall back to accounts.json
- Greenhouse verification: Background Gmail poll via fetch_gmail_code.py

## Deployment

1. Copy ApplyFlow directory to desired location
2. Copy config.example.json → config.json, fill in your values
3. Create candidate_profile.json with your background
4. Run `python playwright_scripts/setup_linkedin_auth.py` (one-time)
5. Launch first session: `python main.py --session search --chain`

## Next Steps

See `program.md` for detailed flow diagrams and implementation details.
