# Requirements

## Background and Roles

Public visitors need predictable content readiness, administrators need predictable login-to-management readiness, and the site owner needs evidence that distinguishes browser, server, API, rendering, data-volume, and network effects.

## Functional Requirements

### PRA-REQ-01 Stable readiness evidence

- Input: page transitions through loading, ready, empty, or error states;
- Processing: expose a stable non-sensitive DOM state and/or Performance Mark at the actual UI transition;
- Output: browser automation can measure content readiness without guessing from API completion;
- Failure: error states are marked separately and never counted as successful ready states;
- Proof: component tests and browser timing entries.

### PRA-REQ-02 Representative synthetic data

- Input: an isolated database at the current migration revision;
- Processing: seed deterministic public notes and one representative Markdown-heavy detail without real personal data;
- Output: empty, first-page-full, and detail scenarios can be repeated;
- Failure: seed or cleanup failure blocks validation;
- Proof: counts, slugs, revision and cleanup record.

### PRA-REQ-03 Production-build execution

- Input: current tracked source, explicit API base, isolated backend and approved local/staging hostname;
- Processing: build and start production-mode frontend without sharing build output or using production data;
- Output: healthy frontend/backend pair with authentication bypass disabled;
- Failure: if production-safe API routing cannot be isolated, mark BLOCKED rather than use the real public API;
- Proof: build log, health checks and effective non-secret configuration.

### PRA-REQ-04 Browser performance matrix

- Input: anonymous list/detail and normal administrator login/manage scenarios;
- Processing: collect at least 10 browser-cold/server-warm samples per scenario plus explicitly separate server-cold samples where feasible;
- Output: p50, p90, maximum, failure rate, key API duration and readiness mark;
- Failure: missing marks, failed requests, incorrect auth or sample mixing invalidates the affected run;
- Proof: raw samples and summarized tables.

### PRA-REQ-05 Budget decision

- Input: verified representative baseline;
- Processing: compare results with existing proposed targets and identify the dominant delay;
- Output: recommended budgets and optimization tasks, each requiring separate approval;
- Failure: no target is marked achieved from empty-data development measurements alone;
- Proof: acceptance and residual-risk documents.

## Non-functional Requirements

- Security: normal cookie login only; no `AUTH_BYPASS` and no real credentials.
- Privacy: only deterministic synthetic content.
- Reproducibility: record commit, build mode, dataset profile, browser version, sample definitions and hostnames.
- Isolation: detached worktree/build output, isolated PostgreSQL and separate ports.
- Cleanup: temporary account, credentials, database process, browser sessions and worktree are removed or disabled and verified.

## Exclusions

- No public deployment, CDN configuration change, dependency addition, broad React refactor, cache redesign, or performance tuning in this task.
- No claim about mobile or geographic latency unless those conditions are explicitly emulated and recorded.
