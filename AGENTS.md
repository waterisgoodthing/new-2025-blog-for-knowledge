# Repository Agent Rules

This is the mandatory entry point for AI agents working in this repository. Read it before inspecting or editing project files. Current source, tests, runtime evidence, and explicit user instructions outrank historical descriptions and remembered architecture.

Detailed orchestration and Persona Worker guidance lives under [`agents/`](agents/README.md).

## 1. Start With Current Reality

Before changing anything:

1. Run `git status --short` and identify existing user changes.
2. Read the files and tests in the touched domain.
3. Identify whether the task affects the Next.js frontend, FastAPI backend, PostgreSQL data, deployment, or more than one boundary.
4. State important assumptions when they cannot be verified cheaply.
5. Prefer existing project patterns over speculative redesign.

Never revert, overwrite, reformat, stage, or include unrelated dirty files. Historical workflow documents are evidence of prior decisions, not proof of current implementation or authorization.

## 2. Use Process Proportionate To Risk

Workflow documents are a risk-control tool, not mandatory ceremony.

Proceed directly without a dedicated `docs/workflows/<task-name>/` folder when work is clear, bounded, reversible, and low risk, including:

- small documentation, wording, link, formatting, prompt, comment, example, or Agent-rule updates;
- read-only inspection, search, status checks, and test execution;
- small single-domain fixes with explicit acceptance criteria and no high-risk boundary.

For these tasks, inspect relevant files, preserve unrelated changes, validate proportionately, and report the exact result. Do not create empty planning documents merely to satisfy process.

Create or reuse a workflow folder when the user requests a plan/audit/report, or when work is multi-phase, cross-domain, architectural, difficult to reverse, or touches:

- authentication, authorization, security, or public/private route ownership;
- API contracts, database schema, migrations, data ownership, or bulk data changes;
- core recommendation/AI behavior or runtime-impacting dependencies;
- production configuration, credentials, deployment, external writes, destructive actions, commit, push, or release.

Required workflow files are normally:

```text
docs/workflows/<task-name>/
  README.md
  design.md
  requirements.md
  tasks.md
  validation.md
```

When a workflow is required:

1. Establish goal, scope, requirements, task order, risks, and validation.
2. Obtain explicit approval for the task list or named phase before implementation.
3. Execute approved items serially when the workflow requires serial execution.
4. Update the exact task and evidence immediately after each item.
5. Do not carry approval into later phases, migrations, deployment, production writes, commit, or push.

If an initially exempt task expands into a high-risk boundary, stop before the expanded work and establish the required workflow and approval.

## 3. Project Shape And Boundaries

The active system contains:

- Next.js App Router frontend under `src/`, delivered through OpenNext/Cloudflare Workers.
- FastAPI backend under `backend/app/` with PostgreSQL, personal knowledge, notes, mistakes, review, search, files, AI, recommendation, audit, and administration capabilities.
- Static/public content and legacy GitHub/export flows that coexist with backend-managed data.

Do not collapse these boundaries or migrate ownership without explicit, separately verified authorization.

### Frontend

- `src/app/`: route composition and route-owned UI.
- `src/components/`: shared UI used by multiple routes.
- `src/hooks/`: shared React hooks.
- `src/lib/api/`: typed API clients and DTOs; no React components.
- `src/lib/`: shared pure utilities, rendering, auth helpers, and client helpers.
- `src/config/`: static configuration with explicit public types.
- `public/`: intentionally public static assets and generated public content only.

Use `page/component -> hook or local action -> src/lib/api/* -> backend API`. Do not put direct API calls in components when a suitable API client exists. Do not invent a new top-level route when an existing domain owns the flow.

### Backend

- `backend/app/models/`: SQLAlchemy persistence models.
- `backend/app/schemas/`: Pydantic request/response contracts.
- `backend/app/routers/`: HTTP routing, dependencies, status codes, and thin orchestration.
- `backend/app/services/`: domain and application behavior.
- `backend/app/utils/`: small framework-independent helpers.
- `backend/app/config.py`: settings.
- `backend/alembic/versions/`: migrations.

Use `router -> schema validation -> service/model -> response schema`. Keep routers thin. A contract or model change must be reconciled across affected schemas, clients, migrations, and tests; do not add a field in only one layer.

### Domain And Data

Confirm domain facts from current models, migrations, routes, clients, and compatibility tests. The repository currently contains canonical `Question`/`Mistake` models and private `/api/admin/questions` and `/api/admin/mistakes` boundaries while legacy note-based mistake flows may still coexist. Do not assume either generation is the sole authority or delete/cut over a compatibility path without current evidence and separate authorization.

For persistence changes, identify whether the owner is static files under `public/`, PostgreSQL through FastAPI, GitHub/export output, external storage, or another verified system.

Protect data correctness, provenance, versioning, auditability, idempotency, and rollback. AI-generated or parsed content is not verified fact and must not silently overwrite trusted structured data.

## 4. Current Authentication And Authorization Contract

The currently verified admin contract is stateful session authentication:

- the backend issues an HttpOnly `admin_session` cookie backed by `AdminSession`;
- frontend API calls use `credentials: 'include'` where session state is required;
- `get_current_admin` is the backend authorization boundary for protected mutations and administrative operations;
- public reads may use optional session resolution but must filter content according to current publication/visibility rules.

Do not describe Bearer/JWT as the current contract and do not infer permission to migrate authentication. The GitHub App/private-key flow, where still present, is a separate integration boundary.

Security invariants:

- Backend authorization is the real boundary; `AuthGate` is navigation and user-experience protection only.
- Creating, editing, deleting, uploading, AI actions, private review/learning data, and management operations require current backend authorization unless source and approved design prove otherwise.
- Public content routes must not be made private accidentally.
- Never expose secrets, session tokens, private keys, database URLs, dumps, or unintentionally private content.
- Never enable or weaken authentication bypass in production.
- Verify current routes and tests before stating an exhaustive access matrix.

## 5. Change And Risk Discipline

- `LOW`: local, bounded, reversible, no security/data/contract risk.
- `MEDIUM`: multi-file or regression-prone but no high-risk boundary.
- `HIGH`: schema, auth, permissions, core domain rules, core recommendation/AI behavior, migrations, or broad architecture.
- `CRITICAL`: production data, credentials, destructive operations, irreversible migration, or production deployment.

Safe in-scope implementation may proceed when explicitly requested. High and critical operations require the evidence and approval defined in [`agents/gates.md`](agents/gates.md). Approval for analysis or one phase never implies approval for migration, deployment, production writes, commit, or push.

Keep changes minimal and domain-scoped. Do not perform opportunistic refactors, dependency upgrades, route cutovers, or file moves for tidiness.

## 6. Validation And Truthful Status

Validate in proportion to the touched boundary:

- TypeScript: targeted tests, `npx tsc --noEmit`, and build when build-sensitive.
- UI: relevant browser evidence when layout, interaction, SVG/Canvas, navigation, or real-browser behavior matters.
- Python: targeted tests using the repository environment; from `backend/`, use `PYTHONPATH=.` when required.
- API contracts: verify frontend clients and backend schemas together.
- Database: migration graph, isolated replay, integrity queries, and rollback evidence as risk requires.
- Documentation: link/file existence, internal consistency, targeted searches, and `git diff --check`.

Do not use jsdom as proof of real-browser behavior. Do not use ignored type/build errors as proof of health. If validation cannot run or fails for a pre-existing reason, report it precisely.

Allowed final states are `PASS`, `PARTIAL`, `FAIL`, `BLOCKED`, `NOT_VERIFIED`, and `NOT_AUTHORIZED`. Never claim execution, verification, approval, commit, push, migration, deployment, or production status without direct evidence.

## 7. Persona Workers And Collaboration

Persona Workers are specialist reasoning profiles under `agents/workers/`; they are not Cloudflare Workers or background jobs.

- Choose exactly one Primary Owner for a non-trivial task.
- Add consulted specialists only when the task crosses their domain.
- Keep implementation, independent review, verification, gate decisions, and final approval separate.
- A role title, seniority claim, or Persona voice is not evidence.
- Do not invoke all Workers by default.
- A single agent adopting several Personas in sequence is not independent review; label it as a perspective pass unless a separate agent/process actually reviewed it.

Follow [`agents/orchestration.md`](agents/orchestration.md), [`agents/permissions.md`](agents/permissions.md), [`agents/gates.md`](agents/gates.md), [`agents/task-template.md`](agents/task-template.md), and [`agents/report-template.md`](agents/report-template.md).

## 8. Stop Conditions

Stop and report evidence, impact, options, and recommendation when:

- scope or target cannot be resolved safely;
- requirements conflict or a critical fact is unknown;
- the operation may destroy data or expose secrets;
- schema, auth, route ownership, or production scope expands beyond approval;
- a required gate is blocked;
- unrelated dirty changes overlap and cannot be preserved;
- validation reveals a serious regression;
- specialist conclusions conflict on a material domain fact.

## 9. Final Report

Lead with the outcome. Include only relevant sections: `Conclusion`, `Changes`, `Evidence`, `Verification`, `Risks`, `Remaining`, and `Decision Needed`.

Distinguish completed, verified, blocked, deferred, unexecuted, and unauthorized work. See [`agents/report-template.md`](agents/report-template.md).
