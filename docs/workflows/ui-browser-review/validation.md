# Validation

## 2026-07-19 browser review

- Attached to the existing local Next server on `http://localhost:2025`; no server configuration was modified.
- Used Playwright Chromium to capture 105 PNGs: 46 desktop, 12 laptop, 46 mobile, 1 interaction-state capture.
- Stored raw browser observations in `docs/ui-review/artifacts/browser-observations-*.json`.
- Confirmed direct static-resource failures after the run: two current chunk URLs returned 500 and two returned 404.
- Created all requested reports under `docs/ui-review/`.
- No business code, database, migration, test account, Git commit, or existing user change was modified.

Initial inherited-instance result: **FAILED** because that active local frontend process did not load its required CSS/JS chunks.

## 2026-07-19 authenticated follow-up

- Started an independent local review instance on port 3000 without changing application source or configuration.
- Fresh public route smoke captures for `/`, `/blog`, `/notes`, `/mistakes`, and `/guestbook` had zero failed Next asset responses.
- Used user-supplied local temporary credentials for browser-only password login; credentials were not persisted in screenshots, report, or project files.
- Captured authenticated desktop `/manage`, `/manage/dashboard`, `/manage/questions`, `/manage/mistakes`, `/manage/review`, and `/manage/ai/runs`, plus mobile `/manage`, dashboard, questions, mistakes, and review.
- Identified UIR-007: legacy `/manage` table is not operable at 390px.

Revised result: **PARTIAL**. The inherited port-2025 server remains unhealthy, while a fresh port-3000 instance renders correctly; remaining full public/authenticated state coverage is still pending.
