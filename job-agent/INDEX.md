# ApplyFlow Job Agent — Complete Index

## Start Here

1. **APPLYFLOW_DELIVERY_SUMMARY.md** (in parent directory) — High-level overview of what was delivered
2. **README.md** — User-facing documentation and quick start guide
3. **CLAUDE.md** — Session instructions and architecture overview

## Deep Dives

- **program.md** — Detailed S→A→O flows, data structures, field mapper architecture
- **IMPLEMENTATION_SUMMARY.md** — What's fully implemented vs stubbed, implementation gaps with guidance
- **MANIFEST.md** — Complete file inventory with size and purpose

## Core Files (Implementation Complete)

### Main Entry Point
- `main.py` — Session orchestrator, routing, chaining

### Configuration & Credentials
- `config.example.json` — Configuration template
- `candidate_profile.json` — Candidate background template
- `account_manager.py` — 1Password + local credential management

### Job Evaluation
- `claude_agent.py` — Score jobs via claude -p CLI
- `job_search.py` — LinkedIn scraper orchestration, ATS detection

### Form Filling
- `field_mapper.py` — Two-tier field mapping (pattern + LLM)
- `pattern_matcher.py` — Learn and apply CSS selectors
- `ats_handlers/` — Platform-specific form handlers (7 files)

### Application Flow
- `apply_agent.py` — Orchestrate applications
- `pdf_merger.py` — PDF utilities

## Session Files (Needs Implementation)

- `sessions/search_session.py` — Session S (Search & Evaluate)
- `sessions/apply_session.py` — Session A (Apply)
- `sessions/outreach_session.py` — Session O (Outreach)

## Playwright Scripts (Needs Implementation)

All in `playwright_scripts/` directory:
- `apply_universal.py` — Universal ATS form filler (PRIMARY)
- `search_linkedin.py` — LinkedIn scraper
- `mark_linkedin_applied.py` — Post-apply update
- `linkedin_outreach.py` — Contact finder
- `fetch_gmail_code.py` — Greenhouse verification
- `setup_linkedin_auth.py` — One-time auth setup
- `mac_dialogs.py` — Dialog handling

## Understanding the System

### Architecture Overview
```
LinkedIn → Session S (Evaluate) → Job Queue → Session A (Apply) → LinkedIn Update
                                                                   ↓
                                              Session O (Outreach) → Draft Messages
```

### Job Flow
```
Scraped → Normalized → Evaluated → Matched with → Status: cover_letter_ready
                                    cover letters
                                         ↓
                                    Applied → LinkedIn marked → Status: applied
                                         ↓
                                    Contacts found → Messages drafted → Status: outreach_drafted
```

### Data Structures
- `agent_state.json` — Last run times, session counts
- `job_queue.json` — Central queue with job status
- `field_patterns.json` — Learned CSS selectors

## Configuration

**What You Need to Provide:**

1. `config.json` (copy config.example.json, fill in)
   - base_path, email, credential_vault, etc

2. `candidate_profile.json`
   - Your work history, education, target roles, resume files

3. `accounts.json` (if not using 1Password)
   - LinkedIn and Gmail credentials

## Quick Start Checklist

- [ ] Copy `config.example.json` → `config.json`
- [ ] Edit `config.json` with your values
- [ ] Edit `candidate_profile.json` with your background
- [ ] Optional: Set up 1Password vault
- [ ] Run `python playwright_scripts/setup_linkedin_auth.py`
- [ ] Run `python main.py --session search --review`
- [ ] Review jobs, check cover-letter-loop status
- [ ] Run `python main.py --session apply --chain` (or manually for each)

## Development

### To Add a New ATS Platform
1. Create `ats_handlers/myplatform.py`
2. Subclass `ATSHandler` from `base.py`
3. Implement `fill_form()`, `submit()`, `verify_success()`
4. Register in `ats_handlers/__init__.py`
5. Add URL pattern to `job_search.py`

### To Understand Field Mapping
- Read `field_mapper.py` (two-tier strategy)
- Read `pattern_matcher.py` (learning mechanism)
- See `program.md` for detailed flow

### To Implement Session Logic
- See stubs in `sessions/` directory
- Follow `program.md` flow diagrams
- Use `job_queue.json` as state store

### To Implement Playwright Scripts
- See stubs in `playwright_scripts/` directory
- Each stub has docstring with TODO guidance
- Pattern: navigate → detect ATS → fill form → submit → verify

## File Relationships

```
main.py
├─ calls account_manager.AccountManager
├─ calls job_search.JobSearchOrchestrator
├─ calls claude_agent.JobEvaluator
├─ calls apply_agent.ApplyAgent
│  └─ calls ats_handlers.get_handler()
│     └─ calls specific handler (greenhouse, workday, etc)
│        └─ uses field_mapper.FieldMapper
│           └─ uses pattern_matcher.PatternMatcher
│  └─ calls pdf_merger functions
└─ runs sessions.search_session.run_search()
   runs sessions.apply_session.run_apply()
   runs sessions.outreach_session.run_outreach()
```

## Testing

### Core Modules (Can Test Without Playwright)
- `account_manager.py` — Mock 1Password responses
- `pattern_matcher.py` — Mock learned patterns
- `job_search.py` — Mock scraped jobs
- `field_mapper.py` — Mock Claude responses

### Integration Tests
- Config loading
- State management
- Job queue transitions
- Error handling and recovery

### End-to-End (Requires Playwright)
- Full S→A→O pipeline
- Form filling on real ATS platforms
- LinkedIn interaction

## Common Tasks

### I want to understand the data flow
→ Read `program.md`

### I want to implement Session S
→ Look at `sessions/search_session.py` stub
→ See `program.md` "Session S" section
→ Key files: `job_search.py`, `claude_agent.py`

### I want to implement form filling
→ Look at `playwright_scripts/apply_universal.py` stub
→ See `program.md` "Field Mapper" section
→ Key files: `field_mapper.py`, `pattern_matcher.py`, `ats_handlers/`

### I want to add 1Password support
→ It's already there in `account_manager.py`
→ Just set `use_1password: true` in config.json

### I want to add a new ATS platform
→ See "To Add a New ATS Platform" above
→ Copy `ats_handlers/generic.py` as template

## Key Concepts

### Pattern Matcher
First application is slow (LLM learns patterns). Later applications are fast (pattern matched).

### Two-Tier Strategy
Tier 1: Fast pattern matching of CSS selectors
Tier 2: LLM-in-the-loop for new forms
Automatically learns and improves.

### Session Chaining
Each session can spawn next via AppleScript:
- `--chain` flag after session completes
- Spawn new Terminal window
- Run next session with `--chain` again
- Results in fully automated S → A → O pipeline

### State as JSON
Everything is JSON for inspectability:
- `agent_state.json` — When sessions ran
- `job_queue.json` — Job status and data
- `field_patterns.json` — Learned selectors

## Documentation Quality

| Document | Purpose | Audience |
|----------|---------|----------|
| README.md | Quick start, usage | End users |
| CLAUDE.md | Architecture, commands | Developers |
| program.md | Detailed flows, data | Implementers |
| IMPLEMENTATION_SUMMARY.md | Status, gaps, guidance | Contributors |
| MANIFEST.md | File inventory | Maintainers |
| INDEX.md | Navigation | Everyone |

## Next Steps

1. **For Using:** Read README.md, fill config.json, run python main.py --session search
2. **For Implementing:** Read IMPLEMENTATION_SUMMARY.md, identify which stub to work on
3. **For Contributing:** Read IMPLEMENTATION_SUMMARY.md "Contribution guidelines"
4. **For Architecture:** Read program.md, understand S→A→O flow

---

Last updated: March 17, 2026
Total files: 33
Total code: ~2,700 lines Python
Implementation status: Core complete, Playwright scripts pending
