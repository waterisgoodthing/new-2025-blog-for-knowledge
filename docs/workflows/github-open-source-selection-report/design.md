# Design

## Scope

This is a documentation and technical-selection task. It affects shared infrastructure documentation while inspecting both active architectural lines:

1. Next.js App Router frontend and original static-blog system under `src/`.
2. FastAPI, PostgreSQL, JWT-authenticated personal knowledge backend under `backend/`.

The report will preserve these boundaries and will not propose an overall rewrite unless source evidence establishes a blocker that cannot be solved incrementally.

## Research Method

1. Establish the local baseline from tracked documentation, source, manifests, migrations, CI/deployment files, tests, Git history, and current workspace state.
2. Decompose the system into functional modules and mark each module's implementation status and open-source reuse suitability.
3. Build reproducible GitHub queries for only the modules where reuse could reduce meaningful engineering risk or cost.
4. Screen candidates using official repository evidence: license, releases, commit activity, issues, tests, deployment configuration, dependency manifests, and relevant source files.
5. Inspect primary and backup candidates at pinned commits or tags in an external temporary directory when source-level evidence is needed.
6. Score candidates using the requested weighted model without changing weights to favor a preferred result.
7. Recommend an integration mode for each candidate and document interfaces, data boundaries, deployment impact, security, supply-chain risk, rollback, and minimum reproducible experiments.
8. Produce the requested top-level report and record report validation in this workflow folder.

## Evidence Standard

- Important factual claims will cite a local path or an upstream URL plus repository, version/tag/commit, and relevant file where available.
- Time-sensitive repository facts will include the observation date.
- Unconfirmed facts will be labeled `待验证` and paired with a verification method.
- README-only claims will not be treated as sufficient evidence for key recommendations.
- License conclusions are engineering assessments, not legal advice.

## Change Boundary

Approved execution may create or update only:

- `docs/GitHub开源项目实现方案与技术选型报告.md`
- workflow status/validation files under `docs/workflows/github-open-source-selection-report/`

Candidate source, if cloned, must remain outside the repository under a temporary directory. No dependencies will be added to this project and no candidate code will be copied into business directories.

## Decision Gate

The final report will select exactly one gate state: `PASS`, `CONDITIONAL_PASS`, or `BLOCKED`. Any non-pass state will list explicit release conditions and reproducible verification methods.

