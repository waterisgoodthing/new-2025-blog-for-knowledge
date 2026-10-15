# Audit Record

## Repository baseline

- Branch: `notes-workspace-ux-upgrade`
- HEAD: `939ad1f docs: record scoped commit validation`
- `git status --short --untracked-files=all`: clean at audit time.
- Architecture lines inspected separately: Next.js/static public content under `src/`; FastAPI/PostgreSQL knowledge backend under `backend/`.

## Database snapshot

- Alembic current/head: `020 (head)`.
- Read-only counts: `users=6`, `notes=13`, `subjects=1`, `knowledge_points=3`, `draft_items=6`, `question_drafts=3`, `questions=3`, `mistake_drafts=3`, `mistakes=3`, `review_items=3`, `review_records=4`, `attachments=1`, `attachment_links=1`, `capture_items=0`, `ai_call_logs=43`, `ai_runs=28`.
- Confirmed absent target tables: `chapters`, `knowledge_aliases`, `knowledge_relations`, `practice_sessions`, `practice_attempts`, `jobs`, `job_steps`, `job_logs`, `ocr_jobs`, `ocr_results`, `ocr_blocks`, `attachment_derivatives`, `learning_metrics_daily`, `learning_reports`, `knowledge_mastery`.

## Main source evidence

- Current backend mounts admin routes for subjects, knowledge points, question drafts/questions, mistake drafts/mistakes, review items, attachments, captures and AI Runs; these routers use `get_current_admin`.
- Current frontend contains management pages for subjects, knowledge points, drafts, questions, mistakes, review, attachments, capture, AI, jobs, settings, search and analytics.
- Current `ai_runs`, `ai_call_logs`, Prompt Registry and Gateway code are real implementation surfaces, not merely the Batch 6 placeholder pages.
- Current Capture state machine exists in `capture_items` and has admin-only routes, but the database snapshot contains no capture rows.

## Evidence limits

- This audit did not perform live browser acceptance or real provider/OCR calls.
- Historical validation records are time-stamped snapshots. Where they conflict, the report preserves the uncertainty rather than treating the newest document as universal proof.
- The original MVP acceptance package says the manual core passed locally, while later AI/Capture records explicitly say real AI/OCR was not verified.
