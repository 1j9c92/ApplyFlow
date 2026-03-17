# ApplyFlow Cover Letter Loop — Program Manual

Complete operational manual for the three-session cover letter optimization loop. Each session runs in a fresh Claude Code context, focused on a single task. Sessions chain automatically.

---

## Architecture Overview

The loop spans three separate Claude Code sessions per job application. Each session gets a clean context window and one clearly-scoped mission.

| Session | Purpose | Primary Input | Primary Output | Context |
|---------|---------|---------------|-----------------|---------|
| **A** | Research & Strategy | `next-jd.md` + career context + web research | `strategy-brief.md` | Fresh (research-heavy) |
| **B** | Drafting & Refinement | `strategy-brief.md` + skill files + voice guide | Best draft + critic feedback | Minimal (focus on writing) |
| **C** | Learning & Advancement | Draft + feedback + skill files | Updated skills + next JD | Clean (reflection-focused) |

### Why Three Sessions?

- **Fresh context per task:** Each session starts with mental focus on one job, not accumulated context from previous ones.
- **Specialization:** Session A specializes in research. Session B specializes in writing. Session C specializes in pattern extraction.
- **Autonomy:** Each session has explicit permission to modify only its own outputs.
- **Debugging:** If a session fails, you restart just that session without losing upstream work.

### Session Spawning (AppleScript Pattern)

```applescript
-- Session A spawn
tell application "Terminal"
  do script "cd /path/to/ApplyFlow/cover-letter-loop && claude --dangerously-skip-permissions /remote-control"
end tell

-- After Session A completes, Session B spawns with:
-- tell application "Terminal"
--   do script "cd /path/to/ApplyFlow/cover-letter-loop && claude --dangerously-skip-permissions /remote-control"
-- end tell
```

At each session transition, paste the session prompt into the terminal. Claude Code will load the loop context from CLAUDE.md.

---

## SESSION A: Research & Strategy

**Role:** Understand the company, role, and candidate fit. Produce a focused strategy brief that informs all downstream writing decisions.

**Input Files:**
- `next-jd.md` — The job description to analyze.
- Career context files (resume bullets, job search criteria, etc.) — Located at paths specified in user's AI Agent Context.
- Company research — Conducted live via web search.

**Output:**
- `strategy-brief.md` — A structured brief that becomes the entire context for Session B.

### Session A Workflow

#### Step 1: Intake and Setup
1. Read `next-jd.md`. Extract:
   - Company name, role title, department, location (if listed).
   - 3-5 key requirements (technical, domain, soft skills).
   - Role maturity (entry-level, mid-level, senior).
   - Hiring context clues (growth phase, rebuilding, specific problem).

2. Load career context files (via mounted AI Agent Context folder):
   - `resume-bullets.md` or equivalent — Candidate's experience bullets grouped by role.
   - `job-search-criteria.md` — Genuine interests, deal-breakers, role/company profile preferences.
   - Note: If these files are not mounted, flag for user to provide them.

3. Note the candidate's goal role/function from job-search-criteria.md.

#### Step 2: Three Parallel Research Agents

Run these in sequence or parallel, depending on context window comfort:

##### Agent 1: Company Researcher
- **Goal:** Understand the company beyond the JD.
- **Actions:**
  - Web search: company name + recent funding, partnerships, new products, acquisitions.
  - Web search: company + leadership changes, strategic challenges, market position.
  - Look for: unique business model elements, market position, growth patterns, pain points.
  - Aim for 1-2 insights not obvious from the JD.
- **Output:** 3-5 concise bullet points on company context.
- **Quality bar:** If all you learn is "they sell software," keep searching. If you find "they're expanding into enterprise after 5 years of SMB focus," you've got signal.

##### Agent 2: Fit Mapper
- **Goal:** Map the JD requirements against the candidate's bullets and assign a fit tier.
- **Actions:**
  1. For each JD requirement, scan resume bullets:
     - If bullet directly supports → mark as STRONG fit.
     - If bullet is adjacent (same domain, transferable skill) → mark as ADJACENT fit.
     - If no match → mark as WEAK/ABSENT fit.
  2. Count: # strong, # adjacent, # weak.
  3. Assign fit tier:
     - **Tier 1 (Strong Match):** 3+ strong fits, remaining are adjacent. Candidate is a natural fit.
     - **Tier 2 (Adjacent/Growth):** Mix of strong and adjacent, some weak. Role is reachable but requires story.
     - **Tier 3 (Stretch):** More weak fits than strong. Candidate is changing direction; needs to lean on transferable skills and learning agility.
- **Output:** Fit tier (1, 2, or 3) + breakdown (strong/adjacent/weak counts) + 2-3 sentence justification.

##### Agent 3: Interest Mapper
- **Goal:** Identify authentic interest alignment between the candidate's genuine interests and the company/role.
- **Actions:**
  1. Review the genuine interests section of `job-search-criteria.md`. Examples: "interested in business model design," "want to work with sharp analytical teams," "drawn to consumer monetization," etc.
  2. Review company research + JD for elements that align:
     - Does company's model match an interest?
     - Does the role solve a problem the candidate cares about?
     - Does the team/function offer something the candidate values?
  3. For each matched interest, note:
     - Interest (from criteria).
     - Company/role element it maps to.
     - Why it's authentic (not manufactured).
- **Output:** 3-5 interest-to-role alignments with authenticity check.

#### Step 3: Synthesize into Strategy Brief

Create a file: `strategy-brief.md`

Structure (see template below):

```
# Strategy Brief: [Company] — [Role]

## Company Context
[Researcher output: 3-5 bullet points]

## Role Summary
[2-3 sentence summary of the role, team, and key requirements]

## Fit Assessment
**Tier:** [1/2/3]
**Breakdown:** [X strong, Y adjacent, Z weak]
**Justification:** [2-3 sentences on why this tier]

## Argument Threads

Name the 2 strongest capability threads:

### Thread 1: [Capability Name]
- Resume bullets (ranked by strength):
  1. [Bullet A] — Proof of capability (score: strong/adjacent)
  2. [Bullet B] — Supporting evidence (score: adjacent)
- **Best proof point:** [1-2 sentences on which bullet is strongest and why]

### Thread 2: [Capability Name]
- Resume bullets (ranked by strength):
  1. [Bullet C]
  2. [Bullet D]
- **Best proof point:** [1-2 sentences]

## Interest Alignment
[3-5 bullets: interest → company element → authenticity check]

## Word Budget
Total: 275 words (hard limit for cover letters)
Suggested allocation:
- P1 (Opening/Interest): 50 words
- P2 (Argument 1): 75 words
- P3 (Argument 2): 75 words
- P4 (Closing): 50 words
- Overhead (salutation, date): 25 words

## Verification Checklist
Fact-check these before handing off to Session B:
- [ ] Company name spelled correctly
- [ ] Role title matches JD exactly
- [ ] Hiring manager name (if mentioned) verified
- [ ] Any numbers/metrics in research accurate
- [ ] Company's business model summary is correct
- [ ] Specific company detail in opening is defensible (not derived from JD alone)
```

#### Step 4: Handoff to Session B

Signal completion with output location and a brief summary:

```
Session A Complete.
Output: /path/to/cover-letter-loop/strategy-brief.md

Strategy Summary:
- Tier: [1/2/3]
- Strongest threads: [Thread 1], [Thread 2]
- Interest alignment: [1-2 key alignments]

Next step: Session B will draft the cover letter using this strategy.
```

---

## SESSION B: Drafting & Refinement

**Role:** Write and refine a cover letter that is specific, authentic, and structurally sound. Iterate through critic cycles until score plateaus or stabilizes above tier-appropriate threshold.

**Context is deliberately minimal:**
- `strategy-brief.md` (only strategic context, no research notes)
- `cover-letter-skill.md` (rules and patterns)
- `write-like-user.md` (voice guide)
- No access to career context; no re-research. All research is in the strategy brief.

This keeps the drafting session focused and prevents context bloat.

**Output:**
- Best draft → `drafts/{YYYY-MM-DD}/{Company - Role}/cover-letter.md`
- All critic feedback → `critic-feedback.md`

### Session B Workflow

#### Step 1: Setup
1. Read `strategy-brief.md`. Extract:
   - Company name, role title.
   - Fit tier (determines score ceiling).
   - Two argument threads (names and best proof points).
   - Interest alignment (for P1 opening).
   - Word budget and suggested paragraph allocation.

2. Read `cover-letter-skill.md`:
   - Note any "Top Active Issues" — watch for these in drafting.
   - Familiarize with draft structure, body paragraph rules, P1 rules, closing rules.
   - Review edit checklist (you will run this before submitting to critic).

3. Read `write-like-user.md`:
   - Note vocabulary blacklist, tone guidelines, structural preferences.
   - This is your voice anchor throughout drafting.

4. Create a working directory:
   ```
   drafts/2026-03-17/{Company - Role}/
   ```

#### Step 2: First Draft

Write a cover letter following the structure and rules in `cover-letter-skill.md`:

```
[Header: Name | Email | Phone | Location]

[Date]

[Salutation]

**[P1 — Opening/Interest]**
- Company-specific detail (not from JD alone)
- Demonstrates genuine interest without industry proclamations
- ~50 words

**[P2 — Argument 1]**
- Thesis: name the capability, don't describe what you did
- Proof: strongest resume bullet, specific evidence
- Closer: name the system, condition, evidence
- ~75 words

**[P3 — Argument 2]**
- Thesis: name the second capability
- Proof: second-strongest bullet
- Closer: evidence and condition
- ~75 words

**[P4 — Closing]**
- Callback to P1 with fresh detail
- Forward-looking without presumption
- Specific ask or natural next step
- ~50 words

[Sign-off: Sincerely, / [Name]]
```

#### Step 3: Pre-Critic Edit Pass

Before submitting to critic, run the edit checklist from `cover-letter-skill.md`:

- [ ] Pyramid structure: strongest argument first?
- [ ] Specificity: concrete numbers/names/dates, not abstractions?
- [ ] Blacklist check: no banned vocabulary from write-like-user.md?
- [ ] Contractions: none in professional writing?
- [ ] Dashes: no em or en dashes?
- [ ] Word count under 275?
- [ ] Unique closing (not recycled)?
- [ ] Term repetition: no domain term used 3+ times?

Fix any issues before moving to critic. This prevents low scores on mechanical issues.

#### Step 4: Critic Cycle (Repeat 3-5 times or until regression guard triggers)

##### The Critic Role

The critic scores the draft on 5 dimensions. Each dimension is scored 1-10 (50 points total).

**Dimensions:**

1. **Argument Strength (AS):** Are the proof points specific, supported by evidence, and directly relevant to the company/role? Do the arguments build a coherent case? (1-10)
   - 1-3: Vague claims, weak or missing proof.
   - 4-6: Some specificity, proof present but generic.
   - 7-8: Specific, supported claims clearly relevant to role.
   - 9-10: Detailed evidence, clear relevance, no overclaiming.

2. **Interest Authenticity (IA):** Does the opening/closing express genuine interest, or does it sound manufactured? Does it avoid false enthusiasm while demonstrating real thought? (1-10)
   - 1-3: Manufactured ("excited to grow with your team"), vague.
   - 4-6: Some authenticity but with generic language.
   - 7-8: Clear genuine interest, specific company observation.
   - 9-10: Distinctive authentic voice, you can feel the real interest.

3. **Voice Fidelity (VF):** Does the letter sound like the user (per write-like-user.md), or does it sound like AI? Is the tone appropriate to the user's style? (1-10)
   - 1-3: Formulaic, inauthentic voice, sounds like template.
   - 4-6: Some personality but inconsistent or strained.
   - 7-8: Clear voice, consistent with user's style.
   - 9-10: Unmistakably the user's voice, natural and authentic.

4. **Structural Integrity (SI):** Is the letter well-organized, within word limits, with clear paragraph hierarchy and flow? (1-10)
   - 1-3: Disorganized, exceeds word limit, unclear hierarchy.
   - 4-6: Organized but choppy flow, slightly over limit.
   - 7-8: Clear structure, good flow, within limit.
   - 9-10: Excellent structure, flows naturally, tight on word count.

5. **Fit Honesty (FH):** Does the letter acknowledge any gaps (Tier 2/3 candidates) rather than overclaim? Is it truthful about the fit? (1-10)
   - 1-3: Oversells fit, ignores obvious gaps.
   - 4-6: Mostly honest but minor overclaiming.
   - 7-8: Honest assessment, acknowledges relevant gaps.
   - 9-10: Transparent and truthful, reframes gaps as learning opportunities.

**Score Thresholds by Fit Tier:**
- **Tier 1:** Target ~48+/50. Ceiling is high because you're defending a strong fit; every point matters.
- **Tier 2:** Target ~44+/50. You're building a story to bridge gaps; some gaps are OK.
- **Tier 3:** Target ~41+/50. You're making a compelling case for transferable skills; some weakness is expected.

**Regression Guard:**
- Track the best score achieved so far.
- If a score drops 2+ points from the best, STOP iterating. Use the best draft, not the current one.
- Regression often signals over-editing or chasing feedback that doesn't serve the core argument.

##### Critic Output Format

After scoring, the critic provides:

```
**Cycle [N] Score:** [AS]/10 + [IA]/10 + [VF]/10 + [SI]/10 + [FH]/10 = [Total]/50

**Dimension Breakdown:**
- Argument Strength (AS): [Score] — [1-2 sentence explanation]
- Interest Authenticity (IA): [Score] — [1-2 sentence]
- Voice Fidelity (VF): [Score] — [1-2 sentence]
- Structural Integrity (SI): [Score] — [1-2 sentence]
- Fit Honesty (FH): [Score] — [1-2 sentence]

**Top 3 Improvement Opportunities:**
1. [Issue + specific example from draft]
2. [Issue + specific example]
3. [Issue + specific example]

**Strengths to Preserve:**
- [What's working well]
- [What's working well]
```

#### Step 5: Drafter Revision

Based on critic feedback, revise the draft:

1. Prioritize the top 3 improvement opportunities.
2. Make surgical edits (avoid rewriting the whole letter).
3. Run the edit checklist again before resubmitting.
4. Loop back to Step 4 (Critic Cycle).

#### Step 6: Stop Condition

Stop iterating when:
- **Target score reached:** You hit the threshold for your fit tier (Tier 1: 48+, Tier 2: 44+, Tier 3: 41+).
- **Regression triggered:** Score dropped 2+ points from best; use the best draft instead.
- **5 cycles completed:** Move on even if target not reached. Sometimes good-enough is enough.

#### Step 7: Export and Document

1. Save the best draft to:
   ```
   drafts/{YYYY-MM-DD}/{Company - Role}/cover-letter.md
   ```

2. Create a file summarizing all critic cycles:
   ```
   critic-feedback.md
   ```
   Include:
   - A table of all cycle scores.
   - The full critic feedback from each cycle.
   - Reasons for stopping (threshold hit, regression guard, 5 cycles).

3. Signal completion:
   ```
   Session B Complete.
   Output: /path/to/drafts/{YYYY-MM-DD}/{Company - Role}/cover-letter.md
   Best Score: [Score]/50 (Cycle [N])
   Fit Tier: [1/2/3]
   
   Critic feedback saved to critic-feedback.md.
   Next step: Session C will analyze patterns and update skill files.
   ```

---

## SESSION C: Learning & Advancement

**Role:** Extract patterns from the draft and feedback. Update skill files with structural learnings. Source the next job. Advance the loop state.

**Input:**
- Best draft from Session B.
- Critic feedback from all cycles in `critic-feedback.md`.
- Current skill files: `cover-letter-skill.md`, `interest-mapper.md`.
- Current state: `loop-state.md`.

**Output:**
- Updated `cover-letter-skill.md` (new learnings, graduated issues).
- Updated `interest-mapper.md` (new reusable interest framings if discovered).
- PDF export of the best draft (using `cover_letter_pdf.py`).
- Next job in `next-jd.md` (if sourcing a new job).
- Updated `loop-state.md` with block completion and carry-forward decisions.

### Session C Workflow

#### Step 1: Intake

1. Read the best draft from Session B.
2. Read `critic-feedback.md` — all cycles.
3. Load current state from `loop-state.md`:
   - Block number.
   - Score history.
   - Active issues.

#### Step 2: Pattern Classification

For each piece of feedback from the critic cycles, classify it:

**Tactical:** One-time issue, specific to this company/draft.
- Example: "Closing callback is too vague for this specific company."
- Action: Don't generalize; don't add to skill file.

**Structural:** Recurring pattern across multiple cycles or across previous blocks.
- Example: "P2 is still too abstract; no specific evidence. This happened in Cycle 1 and Cycle 3."
- Example: "Closing is always generic; reuse the same language. This was flagged in Block 2 and Block 3."
- Action: Add a rule to `cover-letter-skill.md` or update "Top Active Issues."

Guide:
- If feedback appears in Cycle 1 and persists through later cycles → structural.
- If feedback appears across different companies → likely structural.
- If feedback is about phrasing or word choice specific to one sentence → likely tactical.

#### Step 3: Update Top Active Issues

In `cover-letter-skill.md`, maintain a "Top Active Issues" section at the top:

```markdown
## Top Active Issues
- **[Issue Name]:** [Rule to remember]. [Frequency: appeared in Cycles X, Y across Blocks A, B, C].
- **[Issue Name]:** [Rule]. [Frequency].
```

Graduate an issue when it hasn't appeared in Cycle 1 of the last 3 consecutive blocks. Example:
- Block 3: Issue flagged in Cycle 1.
- Block 4: Issue not flagged in Cycle 1.
- Block 5: Issue not flagged in Cycle 1.
- Block 6: Issue not flagged in Cycle 1.
- → Graduate the issue; remove from Top Active Issues.

#### Step 4: Update cover-letter-skill.md

If you identified structural learnings:

1. Add the rule or guideline to the appropriate section (P1 Rules, Body Paragraph Rules, Closing Rules, Edit Checklist).
2. Keep rules concise and actionable.
3. Under "Process Findings," log the block and learning:
   ```
   Block N: [Finding]. [Rule derived].
   ```

Example:
```
Block 3: All drafts opened with vague interest ("excited by your mission"). Rule added to P1 Rules: "Company-specific detail must not be derivable from JD alone."

Block 4: P2 abstractions persisted despite feedback. Rule added to Body Paragraph Rules: "Proof-then-test closer: name the system, name the condition, name the evidence."
```

#### Step 5: Update interest-mapper.md

If a new reusable interest framing was discovered during drafting (e.g., a way to connect "interest in business model design" to a SaaS company's GTM strategy), log it:

```markdown
## Reusable Interest Framings

### [Framing Name]
- **When it applies:** [Company type, role type, or situation]
- **Example structure:** [2-3 sentence template]
- **Fit achieved:** [Score from this or previous block]

Example:
### Business Model → GTM Strategy
- **When it applies:** SaaS/marketplace companies, GTM or product roles
- **Example structure:** "Your expansion into enterprise after 5 years in SMB is compelling because it requires rethinking monetization around larger customer contracts. I have direct experience in this transition..."
- **Fit achieved:** 46/50 (Block 3)
```

#### Step 6: Generate PDF

Call the cover letter PDF generator (`cover_letter_pdf.py`) to create a polished PDF of the best draft:

```python
from cover_letter_pdf import generate_cover_letter_pdf

# Read the draft
with open('drafts/2026-03-17/{Company - Role}/cover-letter.md') as f:
    body_text = f.read()

# Generate PDF
output_path = generate_cover_letter_pdf(
    body_text=body_text,
    company='[Company Name]',
    department='[Role Title]',
    location='[Location]',
    output_path=f'drafts/2026-03-17/[Company - Role]/cover-letter.pdf',
    applicant_name='[User Name]',
    address='[Address from config]',
    email='[Email from config]',
    phone='[Phone from config]',
    letter_date='[Date from draft]',
    salutation='[Salutation from draft]'
)
print(f"PDF generated: {output_path}")
```

#### Step 7: Source Next Job

Choose one:

**Option A: Queue the next job yourself**
- If you have additional job descriptions, source the next one from `next-jd.md`.
- Paste the full JD into `next-jd.md` with a clear header (Company, Role, Link).

**Option B: Ask the user**
- If the job queue is empty, signal that you need the next JD.
- Example: "Job queue empty. Paste the next JD into `next-jd.md` to continue."

#### Step 8: Update loop-state.md

Update the "Current Position" section:

```markdown
## Current Position
- **Block:** [N+1]
- **Status:** Ready for Session A on [Company].
- **Mode:** loop

## Score History (Block Bests)
| Block | Company | Role | Score | Tier |
|---|---|---|---|---|
| 1 | [Company] | [Role] | [Score]/50 | [Tier] |
```

And any "Carry-Forward Decisions" if there are lessons to apply to the next block:

```markdown
## Carry-Forward Decisions
- Block N: [Decision]. Apply to Block N+1.
```

#### Step 9: Signal Completion

Output:

```
Session C Complete.

Block [N] Summary:
- Company: [Company]
- Best Score: [Score]/50 (Fit Tier [Tier])
- Tactical learnings: [#]
- Structural learnings: [#]
- New active issue: [Issue, if any]
- Graduated issue: [Issue, if any]

Files updated:
- cover-letter-skill.md (Top Active Issues, rules, process findings)
- interest-mapper.md (if new framing discovered)
- loop-state.md (block advance, score history)
- PDF export: drafts/2026-03-17/[Company - Role]/cover-letter.pdf

Next: Place next JD in next-jd.md. Session A will begin when ready.
```

#### Session C Self-Modification Rules

- **MAY update:** cover-letter-skill.md, interest-mapper.md, loop-state.md (within scope).
- **MAY NOT change:** The three-session architecture, the critic scoring rubric, or program.md without user approval.
- **MAY add:** New content rules if `user-answers.md` provides them.

---

## Troubleshooting & Edge Cases

### Session Failure or Restart

If a session fails or you need to restart it:
1. Identify which session (A, B, or C).
2. Restore the input files (check `loop-state.md` for what should be in place).
3. Re-run the session from its Step 1.

### Score Plateau in Session B

If scores plateau and can't reach the tier threshold:
- After 5 cycles, move on. Sometimes good-enough is enough.
- Session C will log this and flag it as a carry-forward decision: "Tier [N] ceiling may be unrealistic; reframe in Block [N+1]."

### Regression Guard Triggered

If regression guard triggers (score drops 2+ points):
- Stop immediately. Use the best draft.
- Don't try to "fix" further. You risk making it worse.
- Session C will note this: "Regression guard triggered Cycle [N]. Used Cycle [N-M] draft."

### Content Rule Additions

If the user provides new content rules (via `user-answers.md`), Session C MAY add them to a "User-Specific Content Rules" section in `cover-letter-skill.md`. Examples:
- "Never claim experience I don't have."
- "Always use specific numbers over vague claims."
- "Lead with [role] before [role]."

---

## Self-Modification & Governance

### What Sessions Can Change

- **Session A:** `strategy-brief.md` (output only).
- **Session B:** Drafts (in working directory), `critic-feedback.md` (output only).
- **Session C:** `cover-letter-skill.md`, `interest-mapper.md`, `loop-state.md` (within scope), PDFs (output only).

### What Sessions Cannot Change

- The three-session architecture.
- The critic scoring rubric (dimensions, thresholds, tier ceilings).
- This program.md file.
- Core rules in cover-letter-skill.md without flagging for user approval.

### How to Propose Changes

If Session C identifies a need to change the architecture, rubric, or program:
1. Flag it in `questions.md` under a [meta] tag.
2. Mark it as [open].
3. Wait for user approval in `user-answers.md`.
4. Do not implement until approved.

---

## Appendix: File Locations

```
/cover-letter-loop/
├── CLAUDE.md (this entry point)
├── program.md (this file)
├── loop-state.md (block tracking)
├── questions.md (open questions)
├── user-answers.md (user answers)
├── cover-letter-skill.md (draft rules, active issues, learnings)
├── interest-mapper.md (interest framing templates)
├── strategy-brief.md (Session A output)
├── critic-feedback.md (Session B cycles)
├── next-jd.md (job description input)
├── cover_letter_pdf.py (PDF generator)
├── .claude/
│   └── settings.local.json (Claude Code settings)
└── drafts/
    └── {YYYY-MM-DD}/
        └── {Company - Role}/
            ├── cover-letter.md (best draft)
            └── cover-letter.pdf (PDF export)
```

---

**End of Program Manual**
