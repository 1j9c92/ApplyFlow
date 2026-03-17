# ApplyFlow Onboarding System

This directory contains the complete onboarding framework for ApplyFlow — a self-improving job application pipeline that uses Claude.

## Quick Start

To run the onboarding for a new user:

1. Start a Claude Code session in this directory
2. Have Claude read `ONBOARD.md` as the system instructions
3. Claude will guide the user through a 7-phase interview
4. After completion, the user will have a complete career context knowledge base

---

## Files & Structure

### Main Files

- **`ONBOARD.md`** — The instructions Claude reads when starting an onboarding session. Contains the 7-phase interview structure and guide.

### Templates (in `/templates/`)

All template files are in `/templates/` and are copied into a user's personal career context directory after onboarding.

**Career Context Templates** (`/templates/career-context/`):
- `preferences.md` — Writing voice rules, application defaults
- `profile.md` — Contact info, career narrative, positioning
- `job-search-criteria.md` — Target roles, industries, company preferences, genuine interests
- `education.md` — Degrees, certifications, bootcamps
- `skills-and-tools.md` — Skills organized by category with proficiency levels
- `resume-bullets.md` — Pre-approved accomplishment statements with metadata
- `work-history/template.md` — Template for a single job entry (duplicated for each role)

**Router & Domain Files** (`/templates/.claude/`):
- `CLAUDE.md` — Navigation router pointing to career context and domain files
- `domains/job-search.md` — Long-term learning file for job search strategy and what works
- `domains/ai-automation.md` — Long-term learning file for AI usage and automation experiments

---

## The 7-Phase Interview

The onboarding interview is structured in 7 phases:

1. **Identity & Contact** — Name, email, phone, location, LinkedIn
2. **Career History** — For each job: actual daily work, accomplishments with metrics, what you learned
3. **Education** — Degrees, schools, certifications, relevant coursework
4. **Skills & Tools** — Technical, business, and professional skills organized by category
5. **Job Search Criteria** — Target roles, industries, company stage, geography, compensation, **what energizes you**
6. **Writing Voice** — Your authentic writing style (analyzed from your examples)
7. **Resume Bullets** — Extract pre-approved accomplishment statements from your work history

After each phase, the user can review and correct information. At the end, Claude generates a summary of the complete career context.

---

## Key Design Principles

**Authenticity first**: Emphasis on what you actually did and genuinely care about, not aspirational positioning.

**Concrete over vague**: Daily work, metrics, relationships, and evidence — not job descriptions.

**Pre-approved materials**: Accomplishment statements are vetted during onboarding so they can be rapidly tailored later.

**Continuous learning**: Domain files (job-search.md, ai-automation.md) capture what works and evolve over time.

**No personal info in templates**: All templates are generic and reusable. Personal information is added during onboarding.

---

## How to Customize

### Adjust Interview Phases

Reorder or combine phases as needed. For example:
- Move skills earlier for technical candidates
- Combine education and certifications
- Add a "Values & Culture" phase for culture-fit focus

### Add Domain Files

Create additional domain files for specific contexts:
- `domains/personal.md` — Life admin, personal finance, long-term planning
- `domains/productivity.md` — Task management systems and workflows
- `domains/industry-specific.md` — Industry-specific learnings if targeting a particular sector

### Adjust Interview Depth

Current prompts assume detailed input for in-depth career context. Can be simplified for quick onboarding or expanded for deeper narrative building.

---

## Integration with ApplyFlow

After onboarding, the user's career context feeds into:

1. **Cover Letter Loop** — Uses resume-bullets.md and preferences.md for tailoring and voice
2. **Job Agent** — Uses job-search-criteria.md for filtering and evaluating opportunities
3. **Feedback Loop** — Updates job-search.md and ai-automation.md based on application results

---

## Testing & Deployment

### Test Checklist

- [ ] Run ONBOARD.md through all 7 phases with a test user
- [ ] Verify files are created in correct directory structure
- [ ] Confirm user can review and correct at each phase
- [ ] Check that final summary accurately reflects captured information
- [ ] Test document upload flow (if implemented)

### Deployment Notes

1. This system is template-based and can be deployed to multiple users
2. Each user gets their own copy of the templates filled with their information
3. Router file (CLAUDE.md) is updated with user-specific paths
4. Domain files are user-specific and evolve with each application cycle

---

## Files Delivered

Total: 11 files across 4 directories

```
onboarding/
├── ONBOARD.md
├── README.md (this file)
└── templates/
    ├── career-context/
    │   ├── preferences.md
    │   ├── profile.md
    │   ├── job-search-criteria.md
    │   ├── education.md
    │   ├── skills-and-tools.md
    │   ├── resume-bullets.md
    │   └── work-history/
    │       └── template.md
    └── .claude/
        ├── CLAUDE.md
        └── domains/
            ├── job-search.md
            └── ai-automation.md
```

---

## Next Steps

1. **Run onboarding** with a test user to validate the flow
2. **Refine templates** based on feedback
3. **Integrate with cover-letter-loop** and job-agent components
4. **Build feedback collection** to continuously update domain files
5. **Document lessons learned** to improve future onboardings

---

For questions or improvements, refer to the delivery summary in `../ONBOARDING_DELIVERY.md`.
