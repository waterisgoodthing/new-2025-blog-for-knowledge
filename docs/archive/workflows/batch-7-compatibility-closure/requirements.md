# Requirements

## In Scope

1. Audit and, where approved, preserve compatibility for old public and management entry points.
2. Verify public routes return only public Note/content data and do not expose private management controls.
3. Verify private write, review, upload, AI, and manage routes have page-level `AuthGate` where required.
4. Record dead-link candidates and missing route references without deleting data automatically.
5. Add small user-facing confirmations or error states only where a documented existing workflow requires them.
6. Produce local trial instructions and final closure evidence.

## Candidate Compatibility Areas

- `/write-note` and `/write-note/[slug]` versus `/manage/**` note workflows.
- `/write-mistake` and `/write-mistake/[slug]` versus private manage mistake/capture workflows.
- `/mistakes` and `/notes/[id]` public reads versus `/manage/review` private operations.
- `/blog`, `/blog/[id]`, `/notes`, and shared internal links.
- Sidebar/home/dashboard links to routes that are placeholders or future capabilities.

## Explicitly Out Of Scope

Cloud deployment, public API redesign, data migration, schema changes, new AI/OCR/Capture behavior, Search, Analytics, Practice, BKT, multi-user permissions, and broad visual redesign.

## Acceptance

- Every proposed change has a route/permission/data compatibility rationale.
- Public anonymous flows remain usable without admin API error noise.
- Private actions remain protected by frontend gate and backend authorization.
- Database remains at `020 (head)` with audited row preservation.
- Batch 7 closes with a handoff and no automatic next-batch start.
