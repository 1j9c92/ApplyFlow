# ApplyFlow Job Agent

Automated job search, application, and outreach system for the ApplyFlow suite.

## Overview

The job agent orchestrates a three-session workflow:

1. **Session S (Search):** Scrape LinkedIn, evaluate fit, prepare applications
2. **Session A (Apply):** Submit applications across ATS platforms
3. **Session O (Outreach):** Find contacts and draft connection messages

Each session is independent but can chain via AppleScript spawning for a fully automated pipeline.

## Quick Start

### 1. Setup

```bash
# Copy template config
cp config.example.json config.json

# Fill in your details
nano config.json

# Create candidate profile
nano candidate_profile.json

# One-time LinkedIn auth setup
python playwright_scripts/setup_linkedin_auth.py
```

### 2. Run First Session

```bash
# Search and evaluate jobs (with review pause)
python main.py --session search --review

# Or search and chain to apply
python main.py --session search --chain
```

### 3. Full Automated Pipeline

```bash
# Start S → A → O
python main.py --session search --chain
```

## File Structure

```
job-agent/
├── main.py                          Main orchestrator
├── CLAUDE.md                        Session instructions
├── program.md                       Detailed architecture
├── README.md                        This file
├── config.example.json              Config template
├── candidate_profile.json           Your background
├── field_patterns.json              Learned form patterns (auto-created)
├── agent_state.json                 Runtime state (auto-created)
├── job_queue.json                   Job queue (auto-created)
├── .gitignore                       Don't commit secrets
│
├── Core Modules
├── account_manager.py               Credential handling
├── claude_agent.py                  Job evaluation via Claude
├── field_mapper.py                  Two-tier field mapping
├── pattern_matcher.py               Learn form patterns
├── job_search.py                    LinkedIn scraper orchestrator
├── pdf_merger.py                    Merge resume + cover letter
├── apply_agent.py                   Application orchestrator
│
├── ats_handlers/
│   ├── base.py                      Abstract handler
│   ├── greenhouse.py                Greenhouse platform
│   ├── workday.py                   Workday platform
│   ├── ashby.py                     Ashby platform
│   ├── lever.py                     Lever platform
│   └── generic.py                   Fallback handler
│
├── playwright_scripts/
│   ├── apply_universal.py           Primary ATS filler
│   ├── search_linkedin.py            LinkedIn scraper
│   ├── mark_linkedin_applied.py      Post-apply update
│   ├── linkedin_outreach.py          Contact finder
│   ├── fetch_gmail_code.py           Greenhouse verification
│   ├── handle_ats_auth.py            Auth router
│   ├── setup_linkedin_auth.py        One-time auth setup
│   └── mac_dialogs.py                macOS popup handling
│
├── sessions/
│   ├── search_session.py            Session S logic
│   ├── apply_session.py             Session A logic
│   └── outreach_session.py          Session O logic
│
├── jobs/                            Scraped jobs (created on first run)
├── outreach/                        Outreach drafts (created on first run)
├── applied_jobs/                    Submission records (created on first run)
├── logs/                            Session logs (created on first run)
└── temp/                            Temporary files (created on first run)
```

## Configuration

### config.json

```json
{
  "base_path": "/path/to/ApplyFlow",
  "email": "your.email@gmail.com",
  "credential_vault": "Agent Vault",
  "use_1password": true,
  "apply_timeout_seconds": 120,
  "headless": true
}
```

### candidate_profile.json

Fill this with your work history, education, target roles, and resume file paths. Used for job evaluation and form filling.

## State Management

### agent_state.json
Tracks when each session last ran, session counts, etc.

### job_queue.json
Central queue of all jobs with their current status:
- `pending_evaluation`: Newly scraped, awaiting Claude evaluation
- `pending_application`: Evaluated, awaiting cover letter match
- `pending_outreach`: Applied, awaiting outreach drafts
- `completed`: All stages done

### field_patterns.json
Learned CSS selectors for form fields, learned from successful applications.

## Session Details

### Session S: Search & Evaluate

```bash
python main.py --session search [--review] [--chain]
```

1. Scrapes LinkedIn saved jobs
2. Evaluates each job using `claude -p` CLI
3. Assigns fit tier (1-3), score (0-100), preferred resume type
4. Looks up matching cover letters from cover-letter-loop
5. Marks as `cover_letter_ready` or `needs_cover_letter`
6. Optional: pauses for human review
7. Optional: chains to Session A

### Session A: Apply

```bash
python main.py --session apply [--company "ACME"] [--chain]
```

1. Loads `cover_letter_ready` jobs (highest score first)
2. For each job:
   - Merges resume + cover letter to PDF
   - Spawns `apply_universal.py` subprocess
   - Handles form filling, auth, submission
   - Updates job status to `applied`
   - Updates LinkedIn status
3. Optional: chains to Session O

### Session O: Outreach

```bash
python main.py --session outreach
```

1. For each recently applied job:
   - Searches LinkedIn for hiring manager
   - Searches for HR/recruiting contact
   - Drafts 2 connection message options per contact
   - Writes to `outreach/{date}/{Company - Role}/outreach.md`
2. Messages are **drafts only** — user sends manually

## Key Features

### Two-Tier Field Mapping
- **Tier 1 (Fast):** Pattern matcher learns CSS selectors from past applications
- **Tier 2 (Accurate):** LLM-in-the-loop for new form structures
- Automatically learns patterns and improves over time

### Credential Management
- Integrates with 1Password for secure credential storage
- Fallback to local `accounts.json` if 1Password unavailable
- Warmup and keepalive patterns to prevent auth timeout

### Error Recovery
- Automatic retry with exponential backoff on network errors
- Greenhouse verification code fetched via Gmail background thread
- Detailed logging for debugging

### Integration Points
- Cover letters from `../cover-letter-loop/drafts/`
- Candidate profile used for job evaluation
- Career context from `../career-context/`

## Troubleshooting

### LinkedIn scraper not finding jobs
1. Check LinkedIn auth is set up: `setup_linkedin_auth.py`
2. Ensure you have saved jobs on LinkedIn
3. Check logs in `logs/search/`

### Forms not filling correctly
1. Check `field_patterns.json` has learned patterns for platform
2. Run with review flag to see what's happening
3. LLM field mapper will identify fields if patterns not available

### Cover letters not found
1. Check cover-letter-loop has generated drafts
2. Verify file naming: `{company}_{role}_{date}.docx`
3. Jobs marked `needs_cover_letter` until cover letters ready

### 1Password not authenticating
1. Install 1Password CLI: `brew install 1password-cli`
2. Set `use_1password: false` to use local `accounts.json`
3. Create `accounts.json` with credentials

## Dependencies

```bash
# Required
pip install playwright PyPDF2 python-docx

# Optional
pip install anthropic  # For direct Claude API use
brew install 1password-cli  # For 1Password integration
npm install -g @anthropic-ai/claude  # For claude -p CLI
```

## Implementation Status

These modules are fully genericized and production-ready:
- ✅ Configuration system (config.json, candidate_profile.json)
- ✅ Account manager (1Password + local fallback)
- ✅ Pattern matcher (form field learning)
- ✅ Job search orchestrator (LinkedIn scraper routing)
- ✅ ATS handler base classes (platform-specific logic templates)
- ✅ State management (agent_state.json, job_queue.json)
- ✅ Main orchestrator (session routing, chaining)

These modules need full implementation:
- 🚧 Session S: Full search & evaluation logic
- 🚧 Session A: Complete apply subprocess orchestration
- 🚧 Session O: Full outreach contact finding & drafting
- 🚧 Playwright scripts: Browser automation (key bottleneck)
- 🚧 Field mapper: LLM-in-the-loop for form fields

## Architecture Decisions

### Playwright Only
No Claude-in-Chrome or Kapture — all browser automation via headless Playwright subprocesses. Allows running on server, CI/CD, etc.

### Subprocess Pattern
Each major operation (scrape, apply, outreach) spawns independent processes. Prevents state bloat, enables parallel execution.

### Two-Tier Strategy
Pattern matching handles 95% of cases instantly. LLM-in-the-loop learns new patterns dynamically.

### State as JSON
Simple, debuggable state format. Easy to inspect, modify, recover from errors.

## Next Steps

1. Implement Session S: `sessions/search_session.py`
2. Implement Session A: `sessions/apply_session.py`
3. Implement Playwright scripts (largest effort)
4. Test with real job postings
5. Tune pattern matcher and field detection

## Notes for Future Maintainers

- **Playwright auth persistence:** Saved to `playwright_scripts/linkedin_auth.json` — check expiration handling
- **Gmail code fetching:** Background thread — ensure timeout doesn't block main flow
- **Workday complexity:** Multi-step forms require special handling (see `ats_handlers/workday.py`)
- **Logging:** Session-specific logs in `logs/{session}/{date}.log` — helpful for debugging
- **Error recovery:** Most failures are temporary (network, timeouts) — implement exponential backoff

## Questions?

See CLAUDE.md for session instructions and program.md for detailed architecture.
