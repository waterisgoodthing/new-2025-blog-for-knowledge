# Validation: Mistake Learning Reliability Upgrade

Date: 2026-06-12
Status: Code validation and local browser acceptance complete.

## Current Validation State

This document records code-level validation, local API acceptance, and local browser acceptance. Public deployment checks were not performed in this iteration and remain explicitly marked below.

## Baseline Notes

- `git status --short` was checked before creating workflow docs.
- Initial investigation showed unrelated dirty worktree entries before this workflow was created.
- A post-documentation re-check showed untracked non-workflow entries plus this new workflow folder.
- Any implementation agent must run a fresh `git status --short` before coding and must treat non-workflow dirty files as unrelated unless the user says otherwise.
- This workflow has only added documentation under `docs/workflows/mistake-learning-reliability-upgrade/`.

## Pre-Implementation Evidence

### API/Login/Public Fetch

Evidence status: Partially verified during live diagnosis.

Observed:

- Browser UI displayed generic `Failed to fetch`.
- Public API reliability depends on the correct browser API host and Cloudflare tunnel availability.

Required implementation validation:

- `curl https://public-api.limengyang.me/api/health`
- `curl https://public-api.limengyang.me/api/auth/passkey/status`
- `curl -H 'Origin: https://blog.limengyang.me' https://public-api.limengyang.me/api/subjects -i`
- Browser login/auth status check.

### Note Datetime Writes

Evidence status: Root cause identified from backend error trace during live diagnosis.

Observed:

- Review submit can fail when timezone-aware datetime values are written to timezone-naive columns.
- Adjacent note update/type-conversion paths also write `updated_at` and must not keep the same failure mode.

Required implementation validation:

- Submit a review quality score through `/mistakes/review`.
- Confirm the API returns success.
- Confirm backend logs contain no datetime mismatch.
- Confirm review metadata changes.
- Edit/update a note or mistake and confirm no datetime mismatch.
- Exercise type conversion if that route remains in scope and confirm no datetime mismatch.

### Slug Conflict

Evidence status: Root cause identified from UI toast and backend behavior.

Observed:

- Chinese titles containing the same ASCII token can produce duplicate slugs such as `ipv4`.

Required implementation validation:

- Create two mistakes with similar titles such as:
  - `IPv4子网划分选择题`
  - `IPv4子网广播地址计算`
- Confirm both save with unique slugs.

### Tag/Weak-Point UX

Evidence status: Verified by screenshot and source inspection.

Observed:

- Raw tags and raw knowledge points are displayed as flat pill lists.
- Weak-point diagnosis uses deterministic counts plus frontend template copy.

Required implementation validation:

- Browser screenshot of `/mistakes` after normalization.
- API response sample from `/api/knowledge/weak-points?days=30`.
- Confirm raw tags remain accessible through secondary UI.
- Generate/save a new AI-assisted mistake and confirm low-value quality labels such as `解析清晰` are not saved as primary tags.

### Personalized Error Context

Evidence status: Source inspection confirmed the current AI request does not require structured personal-answer context.

Observed:

- `my_answer` can be saved, but standard AI analysis does not necessarily receive it as a separate field.
- User self-analysis has no clearly validated separate persistence/display path in this workflow yet.

Required implementation validation:

- Enter `my_answer` and `user_error_analysis` in the write-mistake UI.
- Trigger AI analysis and confirm the request includes both fields.
- Save and reload the mistake.
- Confirm detail UI can distinguish user self-analysis from AI personalized diagnosis.

### Mistake Detail Layout

Evidence status: Verified by screenshot and source inspection.

Observed:

- `知识点归总` is rendered as a large lower study block.

Required implementation validation:

- Browser screenshot of `/notes/[id]`.
- Confirm tags and knowledge summary are adjacent in the right rail.
- Confirm non-mistake note layout remains unchanged.

### LaTeX Rendering

Evidence status: Renderer capability verified by source inspection; AI output compliance not fixed.

Observed:

- Existing renderer supports KaTeX via `RichText`.
- AI prompts request LaTeX, but no output validation/repair has been implemented for this workflow.

Required implementation validation:

- Save/render a sample mistake with:
  - inline math: `$E=mc^2$`
  - block math: `$$\\frac{6 \\times 8}{100 \\times 10^6}=0.48\\mu s$$`
- Confirm rendered detail page shows math output.

## Commands To Run After Implementation

```bash
npx tsc --noEmit
npm run build
```

Backend checks depend on the final touched files. At minimum:

```bash
python -c "from app.routers import ai, notes, review, knowledge"
python -c "from app.services import knowledge_retrieval"
```

Run from `backend/` with the project's active Python environment if required.

## Implementation Validation Results (2026-06-12)

### Frontend TypeScript
- `npx tsc --noEmit`: exit 0 (no errors)

### Frontend Build
- `npm run build`: success, all routes compiled
- Non-blocking warnings: stale `baseline-browser-mapping` data and Node `DEP0205` deprecation warning.
- Bundle boundary check: `.next/server` contains 0 `katex` matches; `.next/static/chunks` contains 4 `katex` matches. Math rendering is isolated to client chunks.

### Backend Imports
- `from app.routers import ai, notes, review, knowledge, suggestions, tags`: OK
- `from app.services import knowledge_retrieval, tag_canonicalization`: OK
- `from app.utils.datetime import utc_now_naive`: OK
- `from app.utils.slug import ensure_unique_slug, generate_slug`: OK

### Unit Tests
- `tag_canonicalization`: `直通交换`→`以太网交换`, `解析清晰`→filtered, `TCP`→`TCP协议`
- `utc_now_naive()`: returns naive UTC datetime
- LaTeX repair: `\frac`, `\sqrt`, `E=mc^2`, `0.48μs`, `v=v_0+at` wrapped; prose/Chinese/code-like lines untouched

### Local API Acceptance
- Environment: frontend `http://localhost:2025`, backend `http://127.0.0.1:8000`.
- Duplicate slug creation: two notes created from the same requested slug became `codex-acceptance-ipv4` and `codex-acceptance-ipv4-2`.
- Tag canonicalization: `直通交换` saved as `以太网交换`; `CIDR` saved as `CIDR表示法`; `解析清晰` was filtered.
- Review submit: local review call returned updated `repetitions: 1`, `interval: 1`, `next_review: 2026-06-13`, and `last_reviewed` without datetime mismatch.
- Review stats/plan: local calls returned non-error counts.
- Weak-point aggregation sample included canonical clusters with aliases, including `以太网交换`, `子网划分`, and `CIDR表示法`.
- Cleanup: temporary `codex-acceptance-*` notes were deleted; temporary local admin session was revoked.

### Local Browser Acceptance
- Environment: headless Chrome through Playwright against `http://localhost:2025`.
- `/notes/[id]`: personalized detail view showed `知识点归总`, user self-analysis, and personalized diagnosis.
- `/notes/[id]`: KaTeX rendered successfully with `.katex` count 2 and no raw `$...$` fallback text.
- `/mistakes`: authenticated dashboard loaded weak-point data.
- Weak-point drawer: desktop drawer opened and showed related mistakes; mobile drawer opened from a 390px viewport.
- Weak-point copy: fixed template sentence `建议针对此知识点进行专项练习` was absent.
- Generator actions: `生成变式题` and `生成知识卡片` buttons were visible in the drawer on desktop and mobile.
- Generator save actions: `保存为错题记录` and `保存为知识笔记` are present in code after generation results; live external AI generation was not triggered during this acceptance run.
- Ignored request failures: Google Analytics `collect` calls were blocked/aborted in the local test browser; app API calls passed.

### Browser Artifacts
- `assets/browser-mistakes-desktop-auth.png`
- `assets/browser-weakpoint-drawer-desktop.png`
- `assets/browser-weakpoint-drawer-mobile.png`
- `assets/browser-note-detail-latex-personalized.png`

### Not Validated
- Public deployment behavior on `blog.limengyang.me` / `public-api.limengyang.me`.
- Real passkey login in the public browser session.
- Live external AI generation calls for variant/card creation; button restoration is code-verified, not model-call verified.
- Network inspection of a real AI request with personal fields; code paths for text and image flows pass the fields, but no external request was sent in this local pass.

## Follow-up Validation Results (2026-06-13)

### Mistake Detail Knowledge Summary Placement
- `npx tsc --noEmit`: exit 0.
- Public deploy completed with Cloudflare Worker version `0634e591-f6c8-468c-963a-2fdb79844f07`.
- Public/local/worker `BUILD_ID`: `hu3u56h9l6YxH9ibdtOI2`.
- Right rail order changed to tags, knowledge summary, then review status.

### Mistake Detail Analysis Width
- `npx tsc --noEmit`: exit 0.
- `npm run build`: success.
- Public deploy completed with Cloudflare Worker version `2ba74464-e48a-4cc6-aa2c-04b988061d74`.
- Public/local `BUILD_ID`: `fbEjkqQR2fetc9U7uLpn0`.
- Local browser check at `http://localhost:2025/notes/ipv4`: non-admin view loaded; right rail still renders tags and `知识点归总`. Admin-only `错因与解析` was not visible in that local browser session.
- `错因与解析` no longer uses the two-column grid wrapper and is rendered as a full-width analysis block below the question/answer area.
- Large study blocks now use larger padding, heading spacing, line height, and minimum height for long-form reading.

## Acceptance Matrix

| Acceptance | Status | Evidence |
|------------|--------|----------|
| AC-P0-01 public API/auth works | Local verified; public not validated | Local authenticated API/browser checks passed. Public Cloudflare/API behavior not exercised. |
| AC-P0-02 errors are classified | Code-verified | `ApiErrorKind` types in `client.ts`; non-JSON/Access redirect detection. |
| AC-P0-03 review and covered note datetime writes succeed | Local API verified | Review submit returned updated review metadata without datetime mismatch; notes update/promote paths use `utc_now_naive()`. |
| AC-P0-04 duplicate slugs resolved | Local API verified | Duplicate requested slug auto-suffixed to `codex-acceptance-ipv4-2`. |
| AC-P1-01 tags/weak points grouped | Local API/browser verified | Saved tags canonicalized/filtered; weak-point response grouped canonical concepts with aliases; `/mistakes` loaded grouped data. |
| AC-P1-02 weak-point drawer works | Local browser verified | Desktop and mobile drawer opened; related mistakes and generator buttons visible; old fixed template sentence absent. |
| AC-P1-03 personalized diagnosis uses personal fields | Browser display verified; AI network not sent | Detail page displayed user self-analysis and personalized diagnosis. Text/image AI code paths pass personal fields; real external AI request not sent. |
| AC-P1-04 knowledge summary below tags | Local browser verified | `/notes/[id]` screenshot and DOM contained `知识点归总` in the right rail. |
| AC-P1-05 LaTeX renders | Local browser verified | Browser DOM contained `.katex` count 2 and no raw `$...$` fallback text. |
| AC-P1-06 workflow docs updated | Verified | tasks.md and validation.md updated with implementation results. |
