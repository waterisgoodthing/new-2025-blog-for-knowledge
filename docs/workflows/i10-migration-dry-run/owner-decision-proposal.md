# I10 Owner / Backfill Decision Proposal

Status: `SINGLE-OWNER MODE ACCEPTED / IDENTIFIER PENDING`

This proposal is a decision aid, not an owner assignment. It does not write a
database, authorize E-05, or convert provenance into ownership.

## Recommended rule for this single-owner personal system

Use one explicit canonical owner identity in the target system. The project
owner is also the mapping approver, conflict decider, audit authority, and
rollback decision-maker; no separate responsible-person or approval role is
required. Map a source row to that identity only after the owner-approved
mapping manifest is recorded. The source `users.is_admin` role, `created_by`,
folder/path, slug, target relation, or “first administrator” must never select
the identity.

The approved manifest must cover these populations independently:

`notes`, `questions`, `mistakes`, `review_items`, `review_records`,
`attachments`, `attachment_links`, `capture_items`, `draft_items`, `ai_runs`,
and `ai_call_logs`.

## Required exception rules

- Missing or contradictory provenance becomes `pending_owner_review`; it is
  not silently backfilled.
- Orphaned links and records whose target is absent remain quarantined and are
  counted in reconciliation.
- Duplicate stable IDs, slugs, or target relations are conflict rows requiring
  an explicit disposition before shadow migration.
- Public static blog indexes remain outside this personal-learning owner map;
  the current indexes are empty and are not a second migration source.
- Every approved mapping records source identifier, target identifier, rule
  used, the single owner decision, timestamp, and rollback target.

## Approval fields still required

The single project owner must provide:

1. canonical target owner identifier;
2. confirmation that the rule applies to each listed population;
3. disposition for ambiguous, orphaned, and duplicate rows;
4. confirmation that the owner is also the conflict/audit authority;
5. rollback and quarantine decision.

The single-owner governance decision is accepted. Until the canonical target
identifier, mapping manifest, and remaining row dispositions are supplied and
independently checked against the source, the I10 gate remains `BLOCKED`, even
though I11 has separately been approved.
