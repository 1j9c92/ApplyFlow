# ApplyFlow: Cover Letter Loop

Entry point for Claude Code sessions in the three-session cover letter optimization loop.

## Quick Start

1. **Check your position:** Read `loop-state.md` for current block and session assignment.
2. **Follow your session:** See `program.md` for detailed instructions for Session A, B, or C.
3. **Reference materials:** Job description in `next-jd.md`, strategy brief in `strategy-brief.md`, drafts in `drafts/`.

## The Loop

Three Claude Code sessions per job application:
- **Session A:** Research & Strategy — understand the company and role, produce strategy brief.
- **Session B:** Drafting — write and refine the cover letter through critic cycles.
- **Session C:** Learning — extract patterns, update skill files, source next job.

Each session runs in a fresh context window focused on a single task. Sessions chain via AppleScript.

## Files You Need to Know

- `loop-state.md` — Current position and carry-forward decisions.
- `program.md` — Full operational manual for all three sessions.
- `cover-letter-skill.md` — Working rules and patterns (updated by Session C).
- `interest-mapper.md` — Interest mapping framework (updated by Session C).
- `questions.md` — Open questions and decisions.
- `user-answers.md` — Your answers to loop questions.

## Running a Session

1. Note your session letter (A, B, or C) from `loop-state.md`.
2. Open `program.md` and find the section for your session.
3. Follow the instructions exactly.
4. When finished, note the output location and signal completion.

Session C will update `loop-state.md` and trigger the next session.
