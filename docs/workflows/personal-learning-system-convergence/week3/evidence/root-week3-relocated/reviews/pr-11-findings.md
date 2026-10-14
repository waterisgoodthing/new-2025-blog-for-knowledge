# PR-11 findings (independent verification)

agent_id: PR-11-verify (senior-qa-sdet, verifier)
date: 2026-09-25T12:15Z
scope: dashboard/practice three-question integration
severity scale: BLOCKER > HIGH > MEDIUM > LOW > INFO

## Findings

### [LOW] PR11F-01 — service tests assume an empty scratch DB (test isolation)
The backend `test_pr11_dashboard_service.py` computes expected values (e.g.
`practice_today_count == 0`, weak_top3 ordering) against whatever canonical rows already exist
in the scratch DB. Running the suite *after* a PR11V seed pollutes it: 6 tests fail because the
seeded practice candidates/attempts are visible. They pass on a clean DB (101/101 in this run).
This is a test-hygiene property, not a product defect: production dashboard output is unaffected,
and the CI/verification sequence (pytest before seed) is the existing convention. Recommendation:
have the suite delete rows for a reserved test-subject prefix in `asyncSetUp`, or run on an empty
scratch DB.
Evidence: `tests/pr-11-verify-backend-pytest.txt` (clean DB, 101 passed) vs 6 failures observed
when the same suite ran on the seeded DB during this verification session.

### [LOW] PR11F-02 — weak_top3 lists zero-metric active KPs (inherited PR-10 behavior)
With no attempt/review signal the PR-10 ordering returns zero-metric active KPs ordered by id, so
"最弱 Top 3" can show KPs that are not demonstrably weak. This matches the locked PR-10 authority
(per `tasks/pr-11.md` and backend self-evidence) and is not introduced by PR-11; it is a known
semantic accepted at PR-10. Verified consistent between SQL recompute and API/UI output. Not a
regression; recorded as a note for the G4 recommendation gate.

### [INFO] PR11F-03 — error+retry is only reachable when the summary endpoint fails, not when the backend is fully down
When the whole backend process is stopped, `AuthGate` (client) redirects `/manage/dashboard` →
`/manage` before the dashboard's own error panel mounts. The dashboard error+retry flow was
therefore verified by aborting the summary endpoint only (auth still live), which is the failure
mode the component handles. This matches the shipped component contract and the `AsyncStatePanel`
degradation design; no product change required. Recorded so reviewers understand the browser
evidence boundary.

### [INFO] PR11F-04 — scratch DB carryover
`astra_week3_pr11_verify` retains the final canonical seed (subject 84) and a baked API base
`http://astra-pr11.localhost:8001` in `.open-next/`; the preview and backend are left running for
the review/gate phases. Re-running any empty-DB assumption tests requires the guard `run` on a
clean scratch DB (see PR11F-01).

## Unresolved / open items

- None blocking. The three questions, 今日先做 honesty, four async states, keyboard/reduced-motion,
  and panel regressions are all verified PASS.
- G3/G4 gate review (auth boundary; deterministic fallback without AI) remains for the named gate
  reviewers; verifier found no legacy-Note supply to the three questions (D evidence: NO MATCHES)
  and no AI dependency (today_first_action derives purely from counts).