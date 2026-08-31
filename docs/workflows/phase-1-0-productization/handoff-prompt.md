# Handoff Prompt

No external-agent handoff is currently required.

If another agent continues after approval, it must:

1. Read `AGENTS.md` and this entire workflow bundle.
2. Confirm the approval explicitly covers Phase 0.5 P05-01 through P05-05.
3. Execute one task at a time and immediately mark that exact checkbox complete.
4. Keep P05-01 read-only; only P05-02 may stop the confirmed project frontend process and quarantine generated `.next` output.
5. Stop and request a scope amendment if source, config, dependency or lockfile changes are required.
6. Preserve database counts and Alembic `020 (head)`; execute no DDL, DML or migration.
7. Require a strict PASS across document, JS, CSS, hydration, console and first-party assets; PARTIAL does not unlock Gate A/B.
8. Stop after Phase 0.5; do not enter Gate A or Gate B without new approval.
