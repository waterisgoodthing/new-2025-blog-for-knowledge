# PR-11-verify B: Real-Chromium verification

agent_id: PR-11-verify (senior-qa-sdet, verifier)
date: 2026-09-25T12:14Z
status: PASS (real Chromium via agent-browser)

## Environment

- Frontend: `npm run build:cf` (OpenNext/Cloudflare) served by `wrangler dev` workerd preview at `:8787`.
- Backend: FastAPI uvicorn `:8001` on scratch DB `astra_week3_pr11_verify`, launched through
  `scripts/week3-scratch-guard.py run --db-name astra_week3_pr11_verify -- ...`.
- API base baked at build time: `http://astra-pr11.localhost:8001` (a `*.localhost` loopback host so the
  page at `http://astra-pr11.localhost:8787` and the API share a site and the `SameSite=lax` session cookie
  round-trips). The prior build's `http://localhost.:8001` (trailing dot) broke the cookie; this build is
  the corrected one used for the recorded evidence.
- Browser: agent-browser real Chromium (CDP), session `pr11-verify-1290319b4876`.

## Canonical seed (from `sql/pr-11-verify-seed-recompute.py`, guarded)

Due active ReviewItems = 2; practice eligible = 4 (returned 3); weak Top3 = PR11V
Alpha/Beta/Gamma; recently mastered = 1 (PR11V m6); admin `pr11-verify-admin`.

## Results

| # | Item | Result |
|---|------|--------|
| B1 | Desktop populated: three questions + 今日先做 | PASS: 今日复习 2, 今日练习 3, weak Top3 Alpha/Beta/Gamma, 最近掌握 m6; banner "完成 2 项到期复习" with review CTA |
| B2 | 390px mobile populated | PASS: mobile nav present; same three-question values render |
| B3 | All-empty state | PASS: "今天没有安排", "今日无到期复习", "今日暂无合适练习", "暂无薄弱知识点", "暂无最近掌握"; no false CTA (archived PR11V rows via guard, then re-seeded) |
| B4 | Error + retry (summary endpoint) | PASS: "学习概览加载失败" + 重新尝试; click retry recovers to populated dashboard |
| B5 | Keyboard order + focus | PASS: Tab order = sidebar → quick actions → 今日先做 → 今日复习/今日练习 → weak Top3 → recently mastered; after retry focus moves to `region[学习概览结果]` |
| B6 | Reduced motion | PASS: under `prefers-reduced-motion: reduce` loading skeleton computed `animationName=none` (`motion-reduce:animate-none`); without reduced-motion it is `pulse`/2s |
| B7 | 今日先做 honesty | PASS: due → review CTA only; no-due → practice-first "完成 3 道今日练习" + 开始练习 and **no** 今日先做：开始复习 link (0 occurrences) |
| B8 | Practice route target | PASS: `/manage/practice` renders 3 items from weak KPs (78/79/80) with selection reasons |
| B9 | Profile/activity/storage panels no regression | PASS: 晚上好 welcome, 最近题目/最近复习, 内容统计 (题目6错题4知识点4附件0), 系统状态 (服务正常/数据库正常/暂无附件) all render |

## Screenshots (`week3/evidence/screenshots/`)

- pr-11-verify-desktop-populated.png — desktop populated
- pr-11-verify-desktop-practice.png — practice target route
- pr-11-verify-mobile-390-populated.png — 390px populated
- pr-11-verify-desktop-empty.png — all-empty
- pr-11-verify-mobile-390-empty.png — 390px all-empty
- pr-11-verify-desktop-error.png — error state
- pr-11-verify-reduced-motion-loading.png — loading skeleton under reduced-motion (static)
- pr-11-verify-practice-first.png — practice-first 今日先做
- pr-11-verify-desktop-regression-final.png — final populated + regression panels

## Notes

- With the backend process fully stopped, `AuthGate` redirects `/manage/dashboard` to `/manage`
  (login) before the dashboard error panel can render; the dashboard-level error+retry was therefore
  exercised with the summary endpoint aborted via the browser's network route (auth still live), which
  matches the component contract the product ships.