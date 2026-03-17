# ApplyFlow

A self-improving job application pipeline powered by Claude Code.

---

## What Is This

ApplyFlow turns Claude Code into a strategic job application system. Unlike spray-and-pray tools that maximize volume with one-shot generated materials, ApplyFlow treats each application as a deliberate investment — and gets better at it over time.

The system has three components:

**Onboarding** — An AI-guided interview that builds your career knowledge base from scratch. Claude asks you detailed questions about your experience, skills, interests, and writing voice, then generates the structured files that power everything else.

**Cover Letter Loop** — A three-session architecture (Research → Draft → Learn) that writes cover letters through 3-5 critic cycles and feeds lessons back into skill files. Each block improves on the last.

**Job Agent** — An automated pipeline (Search → Apply → Outreach) that submits applications via Playwright and follows up with LinkedIn outreach.

## Architecture

### Cover Letter Loop (A → B → C)

```
Session A: Research & Strategy
  ├── Researcher agent (company context via web)
  ├── Fit Mapper agent (JD ↔ resume bullets)
  └── Interest Mapper agent (genuine interests ↔ role)
  → strategy-brief.md

Session B: Drafting & Critique
  ├── 3-5 draft/critique cycles
  ├── 5-dimension scoring (50 pts total)
  └── Regression guard (stops if score drops 2+ from best)
  → cover-letter.md + critic-feedback.md

Session C: Learning & Advancement
  ├── Classify feedback (tactical vs structural)
  ├── Update skill files with structural findings
  ├── Maintain "Top Active Issues" tracker
  └── Source next JD
  → improved skill files + next-jd.md

  ↓ loops back to Session A with better skills ↓
```

### Job Agent (S → A → O)

```
Session S: Search & Evaluate → scored job queue
Session A: Apply             → ATS form submissions
Session O: Outreach          → LinkedIn connection messages
```

Each session runs in a fresh Claude Code context window, chained via AppleScript.

## The Self-Improving Part

This is what separates ApplyFlow from volume tools:

- **Session C extracts structural patterns** from critic feedback after every block. One-time fixes are ignored; recurring patterns become permanent rules.
- **cover-letter-skill.md evolves** with each application. Block 1 starts with universal rules. By Block 10, the skill file contains your specific patterns, anti-patterns, and proof structures.
- **Top Active Issues** tracks recurring problems at the top of the skill file. Drafter sees these first every session. Issues graduate after 3 consecutive clean blocks.
- **Interest framings** that score well are documented in interest-mapper.md for reuse in similar roles.
- **Voice guide sharpens** as AI tells are identified and eliminated through critic feedback.

## vs. Volume-First Tools

| | ApplyFlow | Volume Tools |
|---|---|---|
| **Cover letter generation** | 3-5 critic cycles per letter | One-shot generation |
| **Learning** | Skill files improve each block | No feedback loop |
| **Application quality** | High (scored on 5 dimensions) | Variable |
| **Throughput** | ~2-4 applications/day | ~20-50 applications/day |
| **Best for** | Roles where the cover letter is a signal | High-volume spray |
| **Target roles** | Strategy, BizOps, Pricing, SF at 100-1000 person companies | Anything |

Neither approach is wrong. They optimize for different constraints. ApplyFlow is for people who would rather send 5 excellent applications than 50 mediocre ones.

## Getting Started

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (Max subscription recommended)
- Python 3.11+
- Node.js 18+ (for Claude Code)
- macOS (for AppleScript session chaining — Linux support planned)
- Optional: 1Password CLI (for credential management)
- Optional: Playwright (for job agent browser automation)

### Step 1: Onboard

```bash
git clone https://github.com/jcraig-fdsn/ApplyFlow.git
cd ApplyFlow

# Open Claude Code in the onboarding directory
cd onboarding
claude
# Claude will interview you and build your career knowledge base
# This creates your career-context/ folder with all the structured files
```

The onboarding session asks about your career history, skills, interests, and writing voice. It builds:
- `career-context/profile.md` — identity and positioning
- `career-context/work-history/` — detailed role files
- `career-context/resume-bullets.md` — pre-approved accomplishment statements
- `career-context/job-search-criteria.md` — target roles and genuine interests
- `cover-letter-loop/write-like-user.md` — your voice guide

You can also skip the interview and upload existing documents (resume, LinkedIn export, cover letters) for the AI to extract and organize.

### Step 2: First Cover Letter

```bash
# Paste a job description into next-jd.md
cd cover-letter-loop
# Edit next-jd.md with your target JD

# Run Session A (Research & Strategy)
claude
# Claude reads the JD, researches the company, and produces a strategy brief

# Run Session B (Drafting)
# (Spawned automatically by Session A, or start manually)
# 3-5 critic cycles produce a polished cover letter

# Run Session C (Learning)
# Extracts patterns, updates skill files, generates PDF
```

### Step 3: Set Up Job Agent (Optional)

```bash
cd job-agent
cp config.example.json config.json
# Edit config.json with your settings

# One-time LinkedIn auth setup
python playwright_scripts/setup_linkedin_auth.py

# Run the full pipeline
python main.py --session search --chain
```

## Project Structure

```
ApplyFlow/
├── README.md
├── LICENSE
├── .gitignore
│
├── onboarding/                    # Career knowledge base builder
│   ├── ONBOARD.md                 # Claude session prompt for interview
│   ├── README.md
│   └── templates/                 # Template files populated during onboarding
│       ├── career-context/
│       │   ├── preferences.md
│       │   ├── profile.md
│       │   ├── job-search-criteria.md
│       │   ├── education.md
│       │   ├── resume-bullets.md
│       │   ├── skills-and-tools.md
│       │   └── work-history/
│       └── .claude/
│           ├── CLAUDE.md
│           └── domains/
│
├── cover-letter-loop/             # Self-improving cover letter system
│   ├── CLAUDE.md                  # Session entry point
│   ├── program.md                 # Three-session architecture manual
│   ├── cover-letter-skill.md      # Evolving craft rules (updated by Session C)
│   ├── interest-mapper.md         # Interest framing patterns
│   ├── write-like-user.md         # Voice guide (built during onboarding)
│   ├── cover_letter_pdf.py        # PDF generator
│   ├── loop-state.md              # Block tracking and score history
│   ├── user-answers.md            # User Q&A record
│   ├── questions.md               # Loop-generated questions
│   ├── next-jd.md                 # Current JD input
│   └── drafts/                    # Output: dated cover letter folders
│
├── job-agent/                     # Automated application pipeline
│   ├── CLAUDE.md                  # Session instructions
│   ├── program.md                 # S→A→O architecture
│   ├── main.py                    # Orchestrator
│   ├── config.example.json        # Configuration template
│   ├── candidate_profile.json     # ATS form data template
│   ├── apply_agent.py             # Application submission
│   ├── claude_agent.py            # Job evaluation via Claude CLI
│   ├── job_search.py              # LinkedIn scraper orchestration
│   ├── field_mapper.py            # LLM-in-the-loop form mapping
│   ├── account_manager.py         # 1Password integration
│   ├── pattern_matcher.py         # Learned form field patterns
│   ├── pdf_merger.py              # Resume + cover letter merge
│   ├── ats_handlers/              # Platform-specific form handlers
│   │   ├── workday.py
│   │   ├── greenhouse.py
│   │   ├── ashby.py
│   │   ├── lever.py
│   │   └── generic.py
│   └── playwright_scripts/        # Browser automation
│       ├── apply_universal.py
│       ├── search_linkedin.py
│       └── ...
│
└── docs/                          # Additional documentation
```

## How Cover Letters Are Scored

The critic uses a 5-dimension rubric, each scored 1-10:

| Dimension | What It Measures |
|---|---|
| **Argument Strength** | Are claims specific, supported by evidence, and relevant to the role? |
| **Interest Authenticity** | Does the opening feel genuine, not manufactured or generic? |
| **Voice Fidelity** | Does it sound like the user wrote it, not AI? |
| **Structural Integrity** | Is it well-organized, within 275 words, with clear paragraph hierarchy? |
| **Fit Honesty** | Does it acknowledge gaps rather than overclaim capabilities? |

Fit-tier ceilings prevent inflated scores on stretch roles:
- Tier 1 (strong fit): ceiling ~48/50
- Tier 2 (adjacent): ceiling ~44/50
- Tier 3 (stretch): ceiling ~41/50

## Contributing

Areas that need help:

- **Linux session spawning** — Replace AppleScript with a cross-platform solution
- **Multi-board discovery** — Add Indeed, Glassdoor, Workday portal scraping (currently LinkedIn-only)
- **Additional ATS handlers** — More platform-specific knowledge
- **Test coverage** — Unit tests for evaluation, field mapping, pattern matching
- **Windows support** — Playwright scripts assume macOS paths

## License

AGPL-3.0. If you deploy this as a service, share your improvements.

## Credits

Built by [Jason Craig](https://github.com/jcraig-fdsn). Born from a real job search where the system produced 32+ blocks of iteratively refined cover letters across a three-month period.
