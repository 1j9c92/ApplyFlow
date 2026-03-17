# ApplyFlow Job Agent — Detailed Architecture & Implementation

## System Overview

The job agent is a three-session automation system for job search, application, and outreach. Each session is independent but can chain via AppleScript spawning.

```
┌─────────────────────────────────────────────────────────────┐
│ Session S (Search & Evaluate)                               │
│ - Scrape LinkedIn saved jobs (Playwright)                   │
│ - Deduplicate & normalize                                   │
│ - Evaluate fit via claude -p CLI                            │
│ - Assign tier, score, resume type                           │
│ - Match cover letters from cover-letter-loop                │
│ - Update job status & queue                                 │
│ - [--review] Pause for human approval                       │
│ - [--chain] Spawn Session A                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│ Session A (Apply)                                           │
│ - Load cover_letter_ready jobs (sorted by score)            │
│ - For each job:                                             │
│   • Fetch resume + cover letter                             │
│   • Merge PDF                                               │
│   • Launch apply_universal.py subprocess                    │
│   • Handle auth, fill form, upload, submit                  │
│   • Mark applied, update LinkedIn                           │
│ - [--chain] Spawn Session O                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│ Session O (Outreach)                                        │
│ - For each newly applied job:                               │
│   • Search LinkedIn for hiring manager                      │
│   • Search for HR/recruiting contact                        │
│   • Draft 2 connection messages per contact                 │
│   • Write to outreach/{date}/{Company - Role}/outreach.md  │
│ - Session ends (no auto-continuation)                       │
└─────────────────────────────────────────────────────────────┘
```

## Session S: Search & Evaluate

### Input & Output

**Input:**
- LinkedIn credentials (Playwright auth.json)
- Candidate profile (candidate_profile.json)
- Job search criteria (career-context/job-search-criteria.md)

**Output:**
- `job_queue.json` updated with pending_evaluation → cover_letter_ready/needs_cover_letter
- New jobs written to `jobs/{YYYY-MM-DD}/` as JSON
- Human review pause (optional)

### Flow

```
1. Load Playwright context
2. Navigate LinkedIn → My Jobs → Saved
3. Scrape all job cards:
   - Extract title, company, URL, job posting text
   - Parse ATS platform from URL
4. Deduplicate (check job_queue.json & jobs/ history)
5. For each new job:
   a. Generate evaluation prompt
      - Insert candidate_profile.json (work history, skills, preferences)
      - Insert job posting text
      - Request: fit_tier (1-3), compatibility_score (0-100), resume_type
   b. Run: echo "{prompt}" | claude -p
   c. Parse response:
      - fit_tier: 1 (strong match), 2 (okay fit), 3 (weak fit)
      - score: 0-100
      - resume_type: "technical" / "executive" / "entrepreneurial"
   d. Lookup cover letter:
      - Query cover-letter-loop/drafts/ by job title, company, role level
      - If found: mark cover_letter_ready
      - If not found: mark needs_cover_letter
   e. Update job_queue.json & agent_state.json
6. If --review: Print summary, pause for user confirmation
7. If --chain: Spawn Session A via AppleScript
```

### Key Functions

**`search_and_evaluate()`**
- Coordinates entire flow
- Returns list of evaluated jobs

**`scrape_linkedin_jobs(browser_context)`**
- Uses Playwright to navigate LinkedIn
- Returns list of raw job dicts: {title, company, url, posting_text, ...}

**`deduplicate_jobs(new_jobs, existing_queue)`**
- Checks job_queue.json for duplicates
- Prevents re-evaluation

**`evaluate_job(job_posting, candidate_profile, preferences)`**
- Generates evaluation prompt
- Runs claude -p
- Parses response
- Returns {fit_tier, score, resume_type}

**`find_cover_letter(company, role_level, job_title)`**
- Searches cover-letter-loop/drafts/
- Returns path if found, None otherwise

**`update_job_status(job_id, status)`**
- Updates job_queue.json
- Possible statuses: pending, evaluated, cover_letter_ready, needs_cover_letter, applied, error

## Session A: Apply

### Input & Output

**Input:**
- job_queue.json (cover_letter_ready jobs)
- Resume files (from candidate_profile.json)
- Cover letters (from cover-letter-loop/drafts/)
- 1Password vault credentials

**Output:**
- Applications submitted to ATS platforms
- `applied_jobs/` directory with submission records
- LinkedIn status updates
- Updated job_queue.json (cover_letter_ready → applied/error)

### Flow

```
1. Load job_queue.json
2. Filter for status == "cover_letter_ready"
3. Sort by compatibility_score (highest first)
4. For each job:
   a. Load resume file (use resume_type to select correct resume)
   b. Load cover letter file
   c. Merge resume + cover letter → combined.pdf
   d. Determine ATS platform from job.url
   e. Auth check:
      - Load credentials from 1Password (fallback: accounts.json)
      - Auto-login if session expired
   f. Spawn apply_universal.py subprocess:
      - Pass: url, combined.pdf, form_field_patterns.json, ats_platform
      - apply_universal.py handles navigation, field filling, submission
   g. On success:
      - Write submission record to applied_jobs/{job_id}.json
      - Mark job status: applied
      - Call mark_linkedin_applied.py to update LinkedIn
   h. On failure:
      - Log error details
      - Mark job status: error
      - Move to next job
5. If --chain: Spawn Session O via AppleScript
```

### Key Functions

**`apply_to_jobs(job_queue, config)`**
- Filters cover_letter_ready jobs
- Iterates and applies

**`prepare_application_pdf(resume_path, cover_letter_path)`**
- Merges resume + cover letter
- Returns path to combined PDF

**`get_ats_platform(job_url)`**
- Pattern matches URL to determine platform
- Returns: workday / greenhouse / ashby / lever / generic

**`submit_application(url, pdf_path, ats_platform, field_patterns)`**
- Spawns apply_universal.py subprocess
- Waits for completion
- Returns {success, error_msg, submission_time}

**`mark_applied(job_id, submission_record)`**
- Updates job_queue.json
- Writes submission record

**`post_apply_linkedin_update(job_url, company_name)`**
- Spawns mark_linkedin_applied.py subprocess
- Updates LinkedIn status (if enabled)

### Error Handling

- **Form unrecognized:** Log form HTML, skip job, continue
- **Auth failed:** Attempt re-auth via account_manager, retry once
- **Network error:** Retry with exponential backoff (3 attempts max)
- **PDF load error:** Skip job, log details

### Greenhouse Verification Flow (Background)

For Greenhouse ATS:
1. Catch verification code prompt during form submission
2. Spawn background thread running fetch_gmail_code.py
3. Poll Gmail for verification email from Greenhouse
4. Extract code, return to main process
5. Continue submission

## Session O: Outreach

### Input & Output

**Input:**
- Applied jobs list from job_queue.json
- LinkedIn context (Playwright auth)

**Output:**
- `outreach/{YYYY-MM-DD}/{Company - Role}/outreach.md` files
- 2 draft connection messages per contact found

### Flow

```
1. Load job_queue.json
2. Filter for status == "applied" AND last_updated in last 24h
3. For each newly applied job:
   a. Extract company name & job title
   b. Search LinkedIn for hiring manager:
      - Try: "{company} hiring manager" OR "{company} {job_title} hiring manager"
      - Return top 1-3 results
   c. Search for secondary contact:
      - Try: "{company} HR" OR "{company} recruiting"
      - Return top 1-3 results
   d. For each contact found:
      i. Generate 2 draft connection messages
         - Message 1: Focused on role relevance
         - Message 2: Focused on company mission fit
         - Each ~300 chars, personalized with contact name
      ii. Write to outreach/{date}/{Company - Role}/{contact_name}.md
   e. Update job_queue.json: mark outreach_drafted
4. Session ends
```

### Key Functions

**`find_outreach_contacts(company_name, role_title)`**
- Searches LinkedIn via Playwright
- Returns list of {name, title, profile_url, contact_type}

**`draft_connection_messages(contact_name, company, role, candidate_profile)`**
- Generates 2 personalized messages
- Returns list of message strings

**`write_outreach_drafts(company, role, contact_list, messages)`**
- Creates outreach/{date}/{Company - Role}/
- Writes outreach.md with all contacts + messages
- Returns path

### Message Template (per contact)

```
Option 1: [Role-focused]
Hi [Name], I recently applied to [Role] at [Company] and really
resonated with your work in [Department/Industry]. Would love to
connect and learn more about your perspective on [specific team/project].

Option 2: [Company-focused]
[Name], I'm impressed by [Company]'s approach to [mission/initiative].
I just applied for [Role] and think my background in [relevant skill]
could contribute to [specific goal]. Would appreciate a moment to connect.
```

## Key Data Structures

### candidate_profile.json
```json
{
  "personal": {
    "name": "User Name",
    "email": "user@example.com",
    "phone": "+1-555-0000",
    "location": "City, State"
  },
  "work_history": [
    {
      "company": "Company A",
      "title": "Title",
      "duration_years": 2,
      "key_skills": ["skill1", "skill2"]
    }
  ],
  "education": [
    {
      "school": "University",
      "degree": "Degree",
      "field": "Field",
      "graduation_year": 2020
    }
  ],
  "target_roles": [
    "BizOps",
    "Pricing Strategy",
    "Strategic Finance"
  ],
  "resumes": {
    "technical": "path/to/technical_resume.docx",
    "executive": "path/to/executive_resume.docx",
    "entrepreneurial": "path/to/entrepreneurial_resume.docx"
  }
}
```

### job_queue.json
```json
{
  "jobs": {
    "linkedin_job_12345": {
      "title": "Senior Pricing Analyst",
      "company": "ACME Corp",
      "url": "https://linkedin.com/jobs/view/12345",
      "posting_text": "...",
      "ats_platform": "greenhouse",
      "status": "cover_letter_ready",
      "fit_tier": 1,
      "score": 92,
      "resume_type": "technical",
      "cover_letter_path": "path/to/cover_letter.docx",
      "created_at": "2026-03-17T10:00:00Z",
      "evaluated_at": "2026-03-17T10:15:00Z",
      "applied_at": null,
      "error_msg": null
    }
  },
  "pending_evaluation": [...],
  "pending_application": [...],
  "pending_outreach": [...],
  "completed": [...]
}
```

### agent_state.json
```json
{
  "last_search": "2026-03-17T14:30:00Z",
  "last_apply": "2026-03-17T15:45:00Z",
  "last_outreach": "2026-03-17T16:00:00Z",
  "current_session": "search",
  "session_history": [
    {
      "session": "search",
      "started_at": "2026-03-17T14:30:00Z",
      "completed_at": "2026-03-17T14:35:00Z",
      "jobs_processed": 5
    }
  ]
}
```

## ATS Handler Architecture

Each ATS platform has unique quirks. Handlers inherit from `base.py`:

```python
class ATSHandler(ABC):
    def __init__(self, url: str, field_patterns: dict):
        self.url = url
        self.field_patterns = field_patterns
    
    @abstractmethod
    async def fill_form(self, page, candidate_data: dict) -> bool:
        """Fill form fields. Return True if successful."""
        pass
    
    @abstractmethod
    async def submit(self, page) -> bool:
        """Submit form. Return True if successful."""
        pass
    
    @abstractmethod
    async def verify_success(self, page) -> bool:
        """Verify submission success. Return True if success page detected."""
        pass
```

### Platform-Specific Logic

**Workday:** Multi-step form, React-based, requires waiting for field loads. Handle Next buttons, date pickers.

**Greenhouse:** Single-page form, verification code flow via email, PDF upload.

**Ashby:** Modern form builder, single page, custom field types.

**Lever:** Single page, custom rich text fields, file upload.

**Generic:** Heuristic approach — look for common field selectors (name, email, phone, resume).

## Field Mapper: Two-Tier Strategy

### Tier 1: Pattern Matcher (Fast)
- Load learned patterns from `field_patterns.json`
- Pattern: CSS selector → field type mapping
- ~95% success rate on repeated platforms
- 0 LLM cost

### Tier 2: LLM-in-the-Loop (Accurate)
- If Tier 1 fails or pattern not found
- Take screenshot of form
- Send to Claude: "Map these form fields to candidate data. Return JSON."
- Parse response, fill fields
- Learn new patterns, add to field_patterns.json
- ~100% success rate but 5-10s slower

### Pattern Format

```json
{
  "greenhouse_apply": {
    "form_selector": "form[id='greenhouse-form']",
    "fields": {
      "first_name": "input[name='first_name']",
      "last_name": "input[name='last_name']",
      "email": "input[type='email']",
      "resume": "input[type='file'][accept*='pdf']"
    }
  },
  "workday_apply": {
    "form_selector": "[data-form-id='workday_form']",
    "fields": { ... }
  }
}
```

## Session Chaining via AppleScript

When `--chain` is passed, main.py spawns the next session in a new Terminal window:

```python
def spawn_next_session(next_session: str, config: dict):
    """Spawn next session in new Terminal window via AppleScript."""
    cmd = (
        f'cd "{config["base_path"]}/job-agent" && '
        f'python main.py --session {next_session} --chain'
    )
    
    script = f'''
    tell application "Terminal"
        do script "{cmd}"
    end tell
    '''
    
    subprocess.run(['osascript', '-e', script])
```

This allows S → A → O to run as separate processes, each with its own stdout/stderr logging.

## Error Recovery & Logging

All sessions log to `logs/{session}/{YYYY-MM-DD}.log`.

Key patterns:
- Catch all exceptions at session entry point
- Log full traceback
- For recoverable errors (network, timeout): retry with exponential backoff
- For unrecoverable errors (form structure changed): log and skip
- Update job_queue.json with error status + message

Example:
```
2026-03-17 14:35:22 | INFO    | Session A started
2026-03-17 14:35:25 | INFO    | Applying to: Senior Pricing Analyst @ ACME (Greenhouse)
2026-03-17 14:35:30 | INFO    | Auth success
2026-03-17 14:35:45 | INFO    | Form fields filled (tier 1 patterns)
2026-03-17 14:36:02 | INFO    | PDF uploaded
2026-03-17 14:36:15 | INFO    | Greenhouse verification code requested
2026-03-17 14:36:22 | INFO    | Code fetched from Gmail: 123456
2026-03-17 14:36:35 | INFO    | Verification successful
2026-03-17 14:36:50 | INFO    | Application submitted successfully
```

## Next: Implementation Details

See individual Python files (main.py, apply_agent.py, claude_agent.py, etc.) for code structure and docstrings.
