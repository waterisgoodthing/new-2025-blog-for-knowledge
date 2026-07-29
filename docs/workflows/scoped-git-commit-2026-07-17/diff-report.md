# Diff Report

## Baseline — C0-01

- Branch: `notes-workspace-ux-upgrade`.
- Upstream: `mine/notes-workspace-ux-upgrade`.
- Relation: ahead 1, behind 0.
- Index: empty; no staged paths.
- Worktree: mixed tracked and untracked changes across backend, frontend, tests, migrations, architecture docs, and workflow docs.
- Safety: no staging, commit, migration, push, or deployment performed by this task group so far.

## Proposed Classification — C0-02

The following groups are based on the existing Batch 2–7 workflow boundaries. They are proposed scopes, not yet staged.

### Group A — Batch 2 taxonomy

`backend/app/models/{__init__.py,note.py,registry.py,taxonomy.py}`, `backend/app/routers/{chapters.py,knowledge_points.py,subjects.py}`, `backend/app/schemas/taxonomy.py`, `backend/app/services/taxonomy_service.py`, `backend/alembic/versions/019_align_subject_knowledge_tree.py`, `backend/tests/test_taxonomy_service.py`, `src/app/manage/(workspace)/subjects/**`, `src/app/manage/(workspace)/knowledge-points/**`, `src/app/manage/components/knowledge-point-select.tsx`, `src/lib/api/taxonomy.ts`, and `docs/workflows/batch-2-subject-knowledge-point/**`.

Risk note: `models/__init__.py`, `models/registry.py`, and `note.py` are shared registry/model files and require diff review before inclusion.

### Group B — Batch 3 question system

`backend/app/models/{__init__.py,question.py,registry.py}`, `backend/app/schemas/question.py`, `backend/app/routers/questions.py`, `backend/app/services/{question_service.py,draft_service.py}`, `backend/alembic/versions/020_add_canonical_question_contract.py`, `backend/tests/{test_question_routes.py,test_question_domain.py,test_batch7_compatibility.py}`, `src/app/manage/(workspace)/questions/**`, `src/app/manage/(workspace)/capture/components/{manual-question-entry.tsx,question-create-form.tsx}`, `src/lib/api/questions.ts`, and `docs/workflows/batch-3-question-system/**`.

Risk note: shared model/registry files overlap Group A; `draft_service.py` and `test_batch7_compatibility.py` need confirmation against the intended commit boundary.

### Group C — Batch 4 mistake/review

`backend/app/services/mistake_service.py`, `backend/tests/test_mistake_review_service.py`, `src/app/manage/(workspace)/mistakes/**`, `src/app/manage/(workspace)/review/**`, `src/app/manage/(workspace)/capture/components/mistake-draft-entry.tsx`, and `docs/workflows/batch-4-mistake-review/**`.

### Group D — Batch 5 attachments

`backend/app/routers/attachments.py`, `backend/app/schemas/attachment.py`, `backend/app/services/attachment_service.py`, `backend/tests/{test_attachment_routes.py,test_attachment_service.py}`, `src/app/manage/(workspace)/attachments/**`, `src/lib/api/attachments.ts`, and `docs/workflows/batch-5-attachments/**`.

### Group E — Batch 6 AI/OCR placeholders

`src/app/manage/(workspace)/ai/**`, `src/app/manage/(workspace)/capture/page.tsx`, `src/app/manage/(workspace)/components/future-capability-page.tsx`, `src/app/manage/(workspace)/ai/components/ai-runs-panel.test.tsx`, `src/app/manage/(workspace)/ai/page.test.tsx`, `src/app/manage/(workspace)/ai/static-placeholders.test.tsx`, and `docs/workflows/batch-6-ai-ocr-placeholders/**`.

### Group F — Batch 7/manage shell compatibility

`backend/main.py`, `src/app/manage/(workspace)/{dashboard,page.tsx,jobs,page.tsx,layout.tsx,settings/page.tsx}`, `src/app/manage/components/{manage-sidebar.tsx,manage-topbar.tsx,manage-empty-state.tsx,manage-form-panel.tsx,manage-panel.tsx,manage-status-badge.tsx,manage-table-container.tsx,manage-mobile-nav.tsx,manage-mobile-nav.test.tsx}`, `src/app/manage/(workspace)/drafts/**`, `src/app/manage/(workspace)/capture/components/capture-workspace.tsx`, `src/app/manage/(workspace)/capture/components/capture-content.tsx`, `src/app/manage/(workspace)/capture/components/capture-content.test.tsx`, `src/app/manage/(workspace)/analytics/**`, `src/app/manage/(workspace)/search/**`, `src/hooks/use-note-index.test.ts`, `tsconfig.json`, `tsconfig.test.json`, `vitest.config.ts`, `vitest.setup.ts`, and `docs/workflows/batch-7-compatibility-closure/**`.

Risk note: this group is a cross-domain compatibility/UI consolidation set and should not be silently combined with Batch 2–6.

### Group G — architecture and handoff documentation

`docs/adr/**`, `docs/architecture/personal-learning-system-v2.md`, `docs/batch1-*.md`, `docs/workflows/dependency-runtime-risk-cleanup/**`, `docs/workflows/manage-ui-consolidation/**`, `docs/workflows/personal-learning-system-v2/**`, `docs/workflows/phase-c-execution-preparation/**`, `docs/workflows/public-mistake-review-api-gate/**`, `docs/workflows/schema-provenance-drift-closure/**`, and the modified validation files under `docs/architecture/README.md`, `docs/workflows/mvp-rebuild-batch-1-ui-shell/validation.md`, and `docs/workflows/notes-workspace-ux-upgrade/validation.md`.

### Group H — this commit task group

`docs/workflows/scoped-git-commit-2026-07-17/**`.

### Exclude by default / `待人工确认`

- Any path not explicitly included in an approved group.
- Shared files appearing in multiple groups until one owner group is confirmed.
- `backend/alembic/versions/019_*.py` and `020_*.py` unless migration files are explicitly approved for commit; this does not execute migrations.
- The deletion of `backend/app/routers/chapters.py` until its removal is explicitly confirmed.
- Existing modified validation documents whose ownership is not confirmed.
- Any user changes introduced after this audit baseline.

No path has been staged. The exact selected groups and commit messages remain pending `C0-03` approval.
