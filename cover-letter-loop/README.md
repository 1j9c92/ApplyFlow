# ApplyFlow Cover Letter Loop

A self-improving cover letter optimization system built for the ApplyFlow job application pipeline. Three-session architecture with fresh context per task, automated critic feedback, and pattern learning.

---

## Quick Start

1. **Enter the loop:** Read `CLAUDE.md`.
2. **Understand the system:** Read `program.md` (complete operational manual).
3. **Check your position:** Read `loop-state.md`.
4. **Paste your first job:** Add the job description to `next-jd.md`.
5. **Begin:** Follow the session instructions from `program.md`.

---

## System Overview

### Three Sessions Per Job

| Session | Task | Input | Output |
|---------|------|-------|--------|
| **A: Research & Strategy** | Understand company, map fit, produce strategy | `next-jd.md` + web research | `strategy-brief.md` |
| **B: Drafting & Refinement** | Write and iterate through critic cycles (3-5x) | `strategy-brief.md` + skill files | Best draft + feedback |
| **C: Learning & Advancement** | Extract patterns, update skills, source next job | Draft + feedback + skills | Updated skills + next job |

Each session runs in a fresh Claude Code context for focus and isolation.

### The Scoring Rubric

Critic evaluates cover letters on 5 dimensions (1-10 each, 50 total):

1. **Argument Strength (AS)** — Specific, supported, relevant claims
2. **Interest Authenticity (IA)** — Genuine interest, not manufactured enthusiasm
3. **Voice Fidelity (VF)** — Sounds like the user, not AI
4. **Structural Integrity (SI)** — Well-organized, within word limit, clear hierarchy
5. **Fit Honesty (FH)** — Acknowledges gaps rather than overclaiming

**Target scores by fit tier:**
- Tier 1 (strong fit): 48+/50
- Tier 2 (adjacent fit): 44+/50
- Tier 3 (stretch fit): 41+/50

### Self-Improving Loop

Session C extracts learnings from each block:
- **Structural issues** become rules in `cover-letter-skill.md`
- **Reusable interest framings** are logged in `interest-mapper.md`
- **Active issues** are tracked and graduated after 3 clean blocks
- **State** advances to the next block

---

## Files in This Directory

```
cover-letter-loop/
├── CLAUDE.md                  # Entry point (read this first)
├── program.md                 # Complete operational manual (300+ lines)
├── cover-letter-skill.md      # Draft rules and patterns (updated by Session C)
├── interest-mapper.md         # Interest framing templates (updated by Session C)
├── loop-state.md              # Current position and score history
├── questions.md               # Open questions, assumptions, flagged decisions
├── user-answers.md            # Your answers to loop questions
├── next-jd.md                 # Job description input (paste here)
├── cover_letter_pdf.py        # PDF generator (fpdf2-based)
├── README.md                  # This file
├── .claude/
│   └── settings.local.json    # Claude Code session configuration
└── drafts/
    └── {YYYY-MM-DD}/
        └── {Company - Role}/
            ├── cover-letter.md
            └── cover-letter.pdf
```

---

## Session A: Research & Strategy (read program.md for full details)

**Goal:** Understand the company and role, map candidate fit, identify argument threads.

**Workflow:**
1. Read `next-jd.md`
2. Load career context files (resume bullets, job search criteria)
3. Run three parallel research agents:
   - **Company Researcher:** News, market position, strategic context
   - **Fit Mapper:** Map JD requirements against resume; assign Tier 1/2/3
   - **Interest Mapper:** Connect genuine interests to company/role
4. Synthesize into `strategy-brief.md` with company context, fit tier, argument threads, interest alignment, and word budget

**Output:** `strategy-brief.md` becomes Session B's entire context.

---

## Session B: Drafting & Refinement (read program.md for full details)

**Goal:** Write a cover letter and refine it through 3-5 critic cycles.

**Context:** Deliberately minimal.
- Input: `strategy-brief.md`, `cover-letter-skill.md`, `write-like-user.md`
- No re-research; all research is in the strategy brief
- Keeps drafting focused

**Workflow:**
1. Read strategy brief; extract fit tier, argument threads, interest alignment
2. Write first draft following structure in `cover-letter-skill.md`
3. Run edit checklist (catch mechanical issues before critic)
4. Submit to critic; get scores on 5 dimensions
5. Revise based on top 3 improvement opportunities
6. Loop 3-5 times OR until:
   - **Target score reached** (Tier 1: 48+, Tier 2: 44+, Tier 3: 41+)
   - **Regression guard triggered** (score drops 2+ from best)
   - **5 cycles completed**

**Output:**
- Best draft → `drafts/{YYYY-MM-DD}/{Company - Role}/cover-letter.md`
- Critic feedback → `critic-feedback.md`

---

## Session C: Learning & Advancement (read program.md for full details)

**Goal:** Extract patterns, update skill files, generate PDF, source next job, advance state.

**Workflow:**
1. Read best draft and all critic feedback
2. Classify each feedback as tactical (one-time) or structural (recurring pattern)
3. Update `cover-letter-skill.md` with structural learnings:
   - Add rules under appropriate sections (P1 Rules, Body Paragraph Rules, etc.)
   - Update Top Active Issues and graduation tracking
   - Log finding under "Process Findings"
4. Update `interest-mapper.md` if new reusable interest framing discovered
5. Generate PDF using `cover_letter_pdf.py`
6. Source next job (ask user if queue empty) → place in `next-jd.md`
7. Update `loop-state.md`:
   - Advance block number
   - Log score in history
   - Capture any carry-forward decisions

**Output:**
- Updated skill files and state
- PDF of best draft
- Next JD ready for Session A

---

## Running a Block

### Session A
```bash
cd /path/to/cover-letter-loop
claude --dangerously-skip-permissions /remote-control
# Type: "Start Session A. Read next-jd.md and follow program.md Session A instructions."
```

### Session B
```bash
cd /path/to/cover-letter-loop
claude --dangerously-skip-permissions /remote-control
# Type: "Start Session B. Read strategy-brief.md and follow program.md Session B instructions."
```

### Session C
```bash
cd /path/to/cover-letter-loop
claude --dangerously-skip-permissions /remote-control
# Type: "Start Session C. Read the best draft and critic feedback, then follow program.md Session C instructions."
```

Each session will load `CLAUDE.md` automatically and reference `program.md` for detailed instructions.

---

## Customization

### Content Rules
If you have specific content rules (e.g., "Never claim experience I don't have," "Always use specific numbers"), add them to `user-answers.md`. Session C will integrate them into `cover-letter-skill.md`.

### Changing the Architecture
To change the three-session model, scoring rubric, or program.md:
1. Flag the question in `questions.md` with a [meta] tag
2. Answer it in `user-answers.md`
3. Session C will implement only after user approval

### Voice Guide
Session B uses a `write-like-user.md` file for voice guidance. Ensure this file exists in the context root (or mount it from AI Agent Context).

---

## Troubleshooting

### Session fails or needs restart
- Check `loop-state.md` to see what inputs should be in place
- Re-run the session from Step 1

### Score plateaus in Session B
- After 5 cycles, move on; sometimes good-enough is enough
- Session C will flag as a carry-forward decision

### Regression guard triggers
- Stop immediately; use the best draft, not the current one
- You risk making it worse by continuing

### No new job in queue
- Session C will ask you to provide the next JD
- Paste it into `next-jd.md` and resume

---

## Key Principles

1. **Fresh context per session:** Each session gets a clean, focused window on a single task.
2. **Minimal context in Session B:** Drafting stays focused; no research noise.
3. **Structural learning only:** Session C updates skill files based on recurring patterns, not one-off feedback.
4. **Immutable core:** The three-session architecture and scoring rubric don't change without explicit user approval.
5. **Autonomy within bounds:** Sessions have clear permission to modify their outputs; nothing else.

---

## FAQ

**Q: What if I disagree with the critic feedback?**
A: You can override the critic. Session B follows your edits. Session C logs your decision as a carry-forward note.

**Q: Can I skip a session?**
A: No. Each session produces outputs the next session depends on. If you skip B, C has no draft to analyze.

**Q: How many blocks should I run?**
A: Run as many as you're applying to jobs. Each block is one job application.

**Q: Can I run multiple jobs in parallel?**
A: Technically yes, but each job should get its own block sequence (A→B→C complete) before starting the next. This keeps the learning loop clean.

**Q: What if the PDF generator fails?**
A: Ensure fpdf2 is installed (`pip install fpdf2`). Check that applicant name, email, etc., are provided to the function.

---

## Support

For detailed instructions, read:
- `CLAUDE.md` — Quick entry point
- `program.md` — Complete operational manual (read this for everything)
- `cover-letter-skill.md` — Draft rules and patterns
- `interest-mapper.md` — Interest framing guidance
- `loop-state.md` — Current position and history

---

**ApplyFlow Cover Letter Loop**
Self-improving cover letter optimization system.
Built for clarity, autonomy, and pattern learning.
