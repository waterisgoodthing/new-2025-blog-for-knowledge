# INC-01 — `blog_v2` at revision 032 (read-only assessment)

- agent_id: `INC-01-assess` · profile: `database-architect` · role: `verifier`
- Mode: **strictly read-only**. No DML/DDL and no `alembic upgrade/downgrade` was run.
- Every `psql` session began with `SET default_transaction_read_only=on`.
- Target (redacted): `postgresql+asyncpg://***@localhost:5432/blog_v2` (`user=blog_user`).
- Incident: PR-12 reviewer ran `alembic upgrade head` on `blog_v2` past the guard, `026 → 032`.

## 1. Current state (confirmed)

| DB | host (redacted) | revision | role |
|----|-----------------|----------|------|
| `blog_v2` | localhost:5432 (PG 16.14 Homebrew) | **032** (single `alembic_version` row) | local dev runtime authority, writable |
| `blog_db` | localhost:5432 (same cluster) | **025** | legacy/production authority, read-only, **untouched** |

- Code head is `032`; `blog_v2` now matches code. `blog_db` did **not** move (still `025`).
- Week 3 scratch allowlist targets exist (`astra_week3_pr12`, `astra_week3_pr12_mig/_rev1/_verify`, `astra_week3_pr09_*`, `astra_week3_pr10_*`); guard `scripts/week3-scratch-guard.py:53-57` allowlists `^astra_week3_[a-z0-9_]+$` and explicitly rejects `blog_db`/`blog_v2` (`:54`, `:117-139`).

## 2. Migration-by-migration upgrade side effects (027–032)

| Rev | Change | In-place row mutation? |
|-----|--------|------------------------|
| 027 `_guestbook` | Creates `guest_messages` / `guest_message_bans` **only if absent**; `_assert_guest_schema_compatible` then early-returns when they pre-exist (`027:132-139`). Ownership marker `COMMENT` is set only in the create branch. | **No.** On `blog_v2` both tables already existed: their ownership comment is **NULL**, so 027 took the early-return branch and neither created nor altered them. 8 `guest_messages` rows preserved. |
| 028 `_review_items_v2` | Replaces `ck_review_items_state` (+`mastered`), adds nullable `last_rating`, widens `ck_review_items_algorithm`, then runs **unconditional** `UPDATE review_items SET algorithm='fixed_interval_v2'` and sets the column default (`028:89-112`). | **Yes.** This is the only revision with a bulk `UPDATE` over existing rows. |
| 029 `_review_record_states` | `ADD COLUMN previous_state/new_state VARCHAR(20) NOT NULL DEFAULT 'active'` on `review_records` + two checks (`029:65-82`). | Value-backfill only: all existing rows now read `'active'` (synthesized, not observed). |
| 030 `_reanswer_audit` | `ADD attempts.context_type NOT NULL DEFAULT 'practice'` (+check+index); `ADD review_records.attempt_id UUID NULL` + FK (`030:61-83`). | Value-backfill only; `attempts` is empty. |
| 031 `_mistake_visibility_public` | Drops/recreates `ck_mistakes_visibility` to allow `('private','public')` (`031:67-72`). | **No row writes.** |
| 032 `_note_knowledge_points` | Net-new `note_knowledge_points` table (composite PK, 2 CASCADE FKs, 1 index) (`032:60-91`). | **No.** Net-new table only. |

## 3. Data impact on `blog_v2`

| Table | Rows | Observation |
|-------|------|-------------|
| `review_items` | 3 | All `algorithm=fixed_interval_v2`, `state=active`, `last_rating` **NULL** (0 rated). 028's shape assertion guarantees the pre-state was `fixed_interval_v1`, so 028's UPDATE rewrote **all 3** rows `v1→v2`. Row count unchanged; nothing deleted. |
| `review_records` | 4 | `previous_state=new_state='active'`, `attempt_id` NULL. 029/030 only added columns; original columns untouched. `max(created_at)=2026-07-09` ⇒ no post-migration writes observed. |
| `attempts` | 0 | 030 additive only. |
| `mistakes` | 3 | All `visibility='private'` ⇒ 031 fully data-neutral; its downgrade gate (`031:88-95`) would pass. |
| `notes` / `knowledge_points` | 22 / 4 | Untouched by 027–032. |
| `note_knowledge_points` | 0 | Net-new, empty. |
| `guest_messages` / `guest_message_bans` | 8 / 0 | Preserved; 027 did not touch them. |

**Conclusion:** no rows were added, lost, or deleted in `blog_v2` by 026→032. The only existing-row write is 028's bulk metadata rewrite of `algorithm` on all 3 `review_items` (`v1→v2`), plus value-backfills from the new default columns added in 029/030. No note/mistake/knowledge content was altered. This is an **authorization/process violation (guard bypass), not evident data corruption**.

## 4. Recovery options (recommendation only — nothing executed)

`downgrade 026` runs downgrades `032,031,030,029,028,027` in order:

- **032 downgrade** — drop index + drop table `note_knowledge_points`. Table is empty ⇒ lossless.
- **031 downgrade** — fail-closed if any `visibility='public'`. Current public count = 0 ⇒ succeeds and re-narrows the check ⇒ lossless.
- **030 downgrade** — drop `fk_review_records_attempt`, drop `review_records.attempt_id` (all NULL), drop index + `ck_attempts_context_type` + `attempts.context_type`. Lossless on current data (0 attempts, NULL links).
- **029 downgrade** — drop the two checks and the `previous_state`/`new_state` columns. These values were synthesized by the upgrade default, so no genuine transition history is lost.
- **028 downgrade** — set `state='active' WHERE mastered` (none), set **all** `review_items.algorithm='fixed_interval_v1'`, restore v1 checks, drop `last_rating` (all NULL). This exactly reverses the upgrade's UPDATE. Lossless *relative to the pre-incident state*; but it would clobber any legitimately-v2 row created after the upgrade (none observed: review timestamps stop at 2026-07-09).
- **027 downgrade** — `_owned_guest_tables` returns empty (ownership marker NULL) ⇒ early return, **guest tables and 8 rows preserved**.

**Option A — `alembic downgrade 026`:** on current evidence technically near-lossless, but it is itself an unauthorized-by-guard write to `blog_v2`, and 028/029/030 are lossy for any post-migration data not visible today. Requires explicit authorization + a fresh `pg_dump` first. No pre-incident `blog_v2` backup was found under `/Users/limengyang/.codex/backups/2025-blog-public/` (only `phase-d4`/`blog_db` artifacts).

**Option B — keep 032:** `blog_v2` is the code's runtime authority and code head is 032. Keeping it makes runtime consistent with shipped models/routers (`note_knowledge_points` is required by PR-12 code); reverting would put runtime behind code. Preserves all data; the only lingering effect is the 028 `algorithm` metadata rewrite. Treats INC-01 as a procedural finding.

**Option C — other:** leave schema at 032 but remediate the one real mutation by re-pointing `review_items.algorithm` back to v1 via a scoped, authorized DML (not recommended — introduces a second unmanaged write), or restore/promote from a dedicated snapshot (none exists for `blog_v2`).

**Recommendation: Option B (keep 032)**, unless the Week 3 review requires `blog_v2` to remain byte-equivalent to its pre-incident 026 shape. In that case prefer Option A **only** under explicit authorization, after `pg_dump blog_v2`, and re-verify `astra_week3_pr12` parity afterward. Net: the incident did not damage application data; the decision is scope/authorization, not recovery from corruption.

## 5. User adjudication

**Required.** Decide whether `blog_v2=032` is accepted (Option B) or a guarded `downgrade 026` is authorized (Option A, with backup). No `blog_v2` snapshot exists, so Option A cannot be undone except by re-upgrading.

## Read-only evidence (all sessions `SET default_transaction_read_only=on`)

- `select version_num from alembic_version` → `blog_v2=032`, `blog_db=025`.
- `select count(*)` over `review_items`(3), `review_records`(4), `attempts`(0), `mistakes`(3), `notes`(22), `knowledge_points`(4), `note_knowledge_points`(0), `guest_messages`(8), `guest_message_bans`(0).
- `select algorithm,state,count(*),count(last_rating) from review_items group by 1,2` → one row `fixed_interval_v2|active|3|0`.
- `pg_get_constraintdef` for `review_items`, `review_records`, `attempts`, `mistakes`, `note_knowledge_points`.
- `information_schema.columns` for the columns added by 029/030/032.
- `obj_description` on guest tables → NULL (027 early-return branch).
- `select datname from pg_database where datname like 'astra_week3%'` → 17 scratch DBs.
- `show track_commit_timestamp` → `off` (exact commit times not recoverable).
