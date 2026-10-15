# Mistake Learning Reliability Upgrade

## Goal

Fix the current mistake-learning workflow as one coherent task group: public API/login reliability, review submission failures, duplicate slug save failures, fragmented tags, template-like weak-point diagnosis, misplaced knowledge summaries, LaTeX output quality, and missing personalized error-cause analysis.

## Touched Domains

- `auth`: public admin/passkey session checks and API host behavior.
- `mistakes`: mistake list, write-mistake flow, tag display, weak-point diagnosis.
- `review`: SM-2 review submission and review plan stability.
- `notes`: mistake detail layout and rich text/math rendering.
- `shared infrastructure`: frontend API base URL, Cloudflare public API routing assumptions, backend datetime handling, shared AI API contracts.

## Current Status

Implemented. Code validation, local API acceptance, and local browser acceptance are recorded in `validation.md`. Public deployment checks and live external AI-generation calls remain explicitly out of scope for this local closure pass.

## Background

Recent live usage surfaced multiple issues:

- Public requests sometimes fail with `Failed to fetch`, especially around login/API access.
- Review submission can fail after answering a review item.
- Creating a mistake can fail with `Slug already exists`.
- `/mistakes` shows many fragmented tags and weak points instead of grouped concepts.
- Weak-point diagnosis reads like a fixed template and does not use the learner's actual answer.
- Weak-point analysis takes too much page space and should move into a drawer-style interaction.
- The mistake detail page leaves too much empty space because `知识点归总` is placed as a large lower block instead of near tags.
- AI-generated formulas may remain plain text instead of LaTeX.
- AI analysis does not reliably receive `my_answer` or the user's own error analysis, so personalized diagnosis is weak.

## Workflow Files

| File | Purpose | Status |
|------|---------|--------|
| `audit.md` | Current evidence and root-cause review | Drafted |
| `requirements.md` | User-facing requirements and acceptance criteria | Drafted |
| `design.md` | Frontend, backend, API, data, and UX design | Drafted |
| `tasks.md` | Implementation task list requiring approval | Completed |
| `diff-report.md` | Expected implementation file scope | Drafted |
| `validation.md` | Initial validation plan and current evidence | Completed |
| `handoff-prompt.md` | Prompt for an implementation agent | Drafted |
| `assets/` | Local browser acceptance screenshots | Completed |

## Execution Rule

The user approved `tasks.md` on 2026-06-12. Implementation has been executed and validation evidence is recorded in `tasks.md` and `validation.md`.
