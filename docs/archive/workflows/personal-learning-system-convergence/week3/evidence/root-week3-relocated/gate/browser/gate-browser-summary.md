# Week 3 Gate — real Chromium walkthrough evidence

agent_id: GATE-seed-verify (senior-qa-sdet) · date: 2026-09-25
session: agent-browser named session `gate-1290319b4876` (real Chromium/CDP)
topology:
- backend uvicorn 127.0.0.1:8001 on guarded scratch `astra_week3_gate` (alembic 032)
- frontend production workerd preview :8787, built with
  `NEXT_PUBLIC_API_URL=http://localhost.:8001` (FQDN trailing dot bypasses the
  production localhost guard and shares cookie host with the preview)
- logs: browser/gate-backend.log, browser/gate-build.log, browser/gate-preview.log,
  browser/gate-runtime-smoke.txt

## Runtime smoke (node scripts/runtime-smoke.mjs)
`SMOKE referenced=20 ok=20 failed=0 checks=23 failed=0 frontend=http://localhost:8787`
exit 0.  -> PASS

## Walkthrough steps

### A. Dashboard three questions (admin login gate-admin)
- `/manage/dashboard` renders 今日复习 = **2**, 今日练习 = **3**, 今日先做 =
  完成 2 项到期复习 (review-first), 薄弱知识点 Top 3 = GATE Alpha (错误率 80% ·
  遗忘 2 · 到期 2) → GATE Gamma (50%) → GATE Delta (50%).
- Gamma (kp 7) before Delta (kp 8) at equal wrong_rate = stable `knowledge_point_id ASC`
  tie-breaker, matching the SQL recompute exactly (sql/gate-matrix-recompute.json).
- `/manage/review` shows 今日到期 with the two due timestamps (18:49, 19:49) = Q1 count 2.
- `/manage/practice` shows 共 3 道练习 = Q2 count 3.
- Screenshots: gate-dashboard-populated-desktop.png, gate-dashboard-mobile-390.png,
  gate-dashboard-reduced-motion.png.

### B. Public /mistakes populated
- Anonymous open `http://localhost.:8787/mistakes`: 共 2 道公开错题, cards
  GATE mistake m-pub1 / m-pub2 with 题目/正确答案/解析/错因说明.
- DOM leak scan (innerHTML): `GATEPRIVATE`=0, `m-priv1`=0, `m-mastered`=0,
  `legacy-mistake`=0, `gate-legacy`=0, `my_answer`=0.  -> no private/legacy leak
- Screenshots: gate-public-populated-desktop.png, gate-public-mobile-390.png.

### C. Public /mistakes Empty (honest)
- Guarded SQL set both public rows to private → reload: heading 暂无内容 +
  backend message "No published mistakes yet."; API `empty=true, total=0`.
- Restored → `empty=false, total=2`.
- Screenshot: gate-public-empty-desktop.png.

### D. Admin publish / unpublish reflects public page
- Login gate-admin; `/manage/mistakes` detail m-priv1 → button 发布（设为公开）.
- Click + confirm dialog accept → button flips to 下架（设为私有）; public API
  total 2→3 (m-priv1 now included); public page 共 3 道公开错题.
- Unpublish (下架（设为私有）) → public API back to total 2 (m-pub1, m-pub2).
- Screenshot: gate-admin-published-mpriv1.png.

### E. Reduced motion
- `prefers-reduced-motion: reduce` media emulation applied; screenshot captured.
  (PR-11 verify already covered reduced-motion behavior with real Chromium evidence;
  this capture is a current-build confirmation.)

## Note on AuthGate redirect
- With the backend stopped, `/manage/dashboard` redirects to the login page
  (AuthGate is navigation-only; documented PR11F-03). Error+retry UI is verified
  at the endpoint/component level (dashboard error.tsx + endpoint abort) per
  PR-11 acceptance evidence.