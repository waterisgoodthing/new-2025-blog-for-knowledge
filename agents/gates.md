# Decision Gates

Gates are triggered by actual scope. Decisions require current evidence; gate state remains separate from approval.

## G0 — REQUIREMENT_DOMAIN

Trigger: product semantics, personal-learning rules, content ownership/visibility, review behavior, or acceptance criteria change.

Evidence: current behavior, user goal, definitions, edge cases, testable acceptance, affected data/routes. Review by Product Architect and Domain Analyst when meaning changes. Block contradictory or unknown core meaning.

## G1 — ARCHITECTURE

Trigger: architectural boundary, ownership cutover, breaking API, major refactor, infrastructure, or service split.

Evidence: current architecture, problem, alternatives, dependency/data flow, compatibility, migration, rollback, operations. Review by Architect and independent Technical Reviewer. Block unproven necessity, ownership, compatibility, or safe evolution.

## G2 — DATA_DATABASE

Trigger: schema/model, Alembic migration, constraint/index, bulk mutation, source/version, backup/restore, or destructive data action.

Evidence: revision graph, schema authority, migration diff, isolated replay, integrity queries, rollback, consumers. Review by Database Architect with Data/QA as relevant. Production execution needs separate explicit approval.

## G3 — SECURITY_AUTH

Trigger: login/session, authorization, admin/public ownership, uploads, secrets, external input, resource ownership, CORS, or bypass behavior.

Evidence: current `admin_session`/`get_current_admin` contract, threat case, negative tests, resource authorization, exposure/secret checks. Review by Security and QA. Block unresolved Critical/High findings. Auth migration is never inferred.

## G4 — RECOMMENDATION_AI

Trigger: learning/review recommendation, ranking, scheduling, provider behavior, prompt/output contract, automated parsing, or AI-persisted data.

Evidence: baseline, examples/data, deterministic invariants, provenance, evaluation, failure/fallback, audit, cost/latency as relevant. Block unverified output treated as fact, missing evaluation/provenance, or possible corruption of trusted data.

## G5 — RELEASE_PRODUCTION

Trigger: deployment, production config/data, credentials, runtime upgrade, migration execution, public cutover, or rollback.

Evidence: release identity, clean authorized scope, tests/build, preceding gates, monitoring, rollback, target, explicit approval. Review by SRE and QA with Security/Database as applicable. Commit, push, deployment, migration, and production writes remain separately authorized.

