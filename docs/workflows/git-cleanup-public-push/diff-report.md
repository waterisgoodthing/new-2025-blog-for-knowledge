# Diff Report — Git Cleanup And Public Push

Status: `completed with deployment blocked`

## Staged Release Scope

The approved release currently stages the full working-tree update set:

- architecture and workflow documentation through final handoff / backlog / acceptance reports
- Batch 8 through Batch 12 AI/capture/run/governance implementation files
- P1 acceptance cleanup patch
- setup/check scripts and README/env template updates
- frontend management, capture, AI, notes, mistakes, review, and navigation updates
- backend AI Gateway, prompt governance, capture, run audit, usage/cost/health, routing, and tests
- Alembic migrations through `018`
- GitHub templates/workflow files
- local music selection update and one public music file

## Staged Size

```text
251 files changed, 34052 insertions(+), 12867 deletions(-)
```

## Deployment-Affecting Changes

The staged set removes the old Cloudflare/OpenNext deployment path:

- `wrangler.toml` deleted
- `open-next.config.ts` deleted
- `scripts/watch-mymusic-deploy.sh` deleted
- `package.json` no longer has `build:cf`, `deploy`, `deploy:full`, `preview`, or `cf-typegen`
- `package-lock.json` no longer carries the old Wrangler/OpenNext dependency footprint

This is why public deployment is treated as blocked after Git push unless a deployment path is restored in a later approved task.

## Git Result

Release commit pushed:

```text
2b5453f feat: finalize AI learning system acceptance
```

Remote branch:

```text
mine/notes-workspace-ux-upgrade
```

## Explicit Non-Actions

- No destructive Git cleanup was used.
- No real `.env`, key, database dump, virtualenv, cache, or build artifact was staged.
- No deployment config was recreated in this workflow.

---

## 2026-07-29 Release Run — Initial Inventory

Status: `publication set classified; release blocked before staging`

The exact machine-readable snapshot is stored in
`assets/2026-07-29-git-inventory.json`.

Snapshot totals before adding the release-run workflow records:

- modified tracked files: 12
- untracked files: 334
- modified-file bytes: 215,044
- untracked-file bytes: 23,430,799
- branch: `notes-workspace-ux-upgrade`
- upstream after fetch: `mine/notes-workspace-ux-upgrade`
- divergence: 3 commits ahead, 0 behind

All dirty paths are under `docs/`. No source, backend, migration, package,
deployment-config, environment, or database file is dirty in this snapshot.

### Authenticated UI Evidence

Classification: `exclude from public Git; preserve locally`.

Scope:

- `docs/ui-review/artifacts/authenticated/` — 14 files
  (12 PNG screenshots and 2 JSON observation files)

Evidence:

- the JSON includes private/admin page text, content titles, tags, mistake and
  review material, activity timestamps, and analytics request identifiers
- the screenshots visibly contain the same authenticated management and private
  learning surfaces
- no password, bearer token, cookie value, private key, or session credential
  was found, but the private content itself is sufficient reason to exclude it

Planned cleanup: add this exact directory to `.gitignore`; do not delete or move
the local evidence.

### Migration, Recovery, And Owner Evidence

Classification: `publish`, except for the authenticated UI directory above.

Review findings:

- no database password, connection secret, API key, bearer token, cookie,
  private key, email address, database dump, or raw business row was found
- `source-manifest.json` contains only repository-relative file metadata,
  localhost database identity, revision, table counts, and SHA-256 aggregates
- reports contain localhost/temporary operational paths and one machine-local
  backup path; these are reproducibility evidence, not credentials
- an opaque canonical-owner UUID occurs in the duplicated C6-C12 report, but the
  same UUID is already tracked in the approved I-series workflow and is not a
  login name, password hash, token, email, or secret
- screenshots outside `artifacts/authenticated/` represent public, anonymous,
  synthetic, or isolated-test views and contain no discovered credential value

The review does not claim that operational hashes or IDs are secret; it records
why they are acceptable as public validation evidence in this repository.

### Candidate Classification

The exact per-file classification is stored in
`assets/2026-07-29-publication-classification.json`.

| Classification | Count | Decision |
| --- | ---: | --- |
| `publish` | 331 | Stage after cleanup and validation |
| `exclude` | 14 | Keep locally under an exact `.gitignore` rule |
| `publish_after_relocation` | 1 | Move the duplicated C6-C12 report to the owning workflow root, then stage |
| `needs user decision` | 0 | None |

The two release-run JSON records created after the initial snapshot are also
classified `publish`.

### Release Gate Result

The classified publication set was not staged. The fail-closed production audit
reported 10 high vulnerabilities before tests/build/deployment could continue.
No GitHub push or public deployment was attempted.
