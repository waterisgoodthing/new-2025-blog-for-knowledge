# W3-00 — Runtime & canonical contract inventory (read-only)

agent_id: W3-00-inv-runtime · profile: database-architect · role: consulted/read-only
Date: 2026-09-22 · Task: docs/workflows/personal-learning-system-convergence/week3/tasks/w3-00.md
Scope: migration head verification + canonical contract inventory for PR-09 / PR-12 / W3-D05.
No product/migration code modified. No database connected or created. `blog_db` / `blog_v2` / any production DB untouched.

---

## A. Migration single-head verification

### A.1 Command evidence (offline, no DB connection)

Run from `backend/` with repository venv (`backend/.venv`):

```text
$ PYTHONPATH=. .venv/bin/python -m alembic heads
030 (head)
EXIT:0
```

```text
$ PYTHONPATH=. .venv/bin/python -m alembic history | head -6
029 -> 030 (head), Re-answer audit linkage (R02/D4/D5).
028 -> 029, Add previous_state and new_state to review_records.
027 -> 028, Widen review_items state/algorithm enumerations and add last_rating.
026 -> 027, Provision the guestbook tables without taking ownership of legacy tables.
025 -> 026, Install the governed legacy Note migration contract.
024 -> 025, align fresh-install schema with current model metadata

$ PYTHONPATH=. .venv/bin/python -m alembic history | tail -6
003 -> 004, add ai_metadata to notes
1119bee5a419 -> 003, restore notes status index
0ec85724afb9 -> 1119bee5a419, add images to notes
002 -> 0ec85724afb9, add user admin field
001 -> 002, add status field
<base> -> 001, initial schema
```

**Conclusion:** single source head = **030**. `alembic heads` and `alembic history` are offline script-graph commands; they completed against the versions directory only. `backend/alembic.ini:4` declares a `sqlalchemy.url`, but these commands did not open a connection (no scratch/production DB was created, contacted, or required).

### A.2 Migrations 031 / 032 do not exist

```text
$ ls backend/alembic/versions/ | grep -E '03[12]'
NO 031/032 FILES
```

Static `down_revision` chain (grep of `backend/alembic/versions/*.py`) is linear with no branches:

`<base>→001→002→0ec85724afb9→1119bee5a419→003→004→005→006→007→008→009→010→011→012→013→014→015→016→017→018→019→020→021→022→023→024→025→026→027→028→029→030`

Terminal node `030` has `down_revision = "029"` (`backend/alembic/versions/030_reanswer_audit.py:19-20`) and no file declares `down_revision="030"`. Confirms head=030 is unique.

Scratch runtime expectation to pin before writing 031: any Week 3 replay tooling must target a fresh `astra_week3_*` scratch DB and assert `alembic heads` == `030` before upgrade.

---

## B. Canonical contract inventory (week3/README.md §2 cross-check)

### B.1 `Mistake.visibility` — private-only (PR-09 / migration 031 target)

| Layer | Evidence |
| --- | --- |
| Model | `backend/app/models/mistake.py:84` — `visibility: Mapped[str] = mapped_column(String(20), default="private", server_default="private", nullable=False)` |
| Model CHECK | `backend/app/models/mistake.py:91` — `CheckConstraint("visibility = 'private'", name="ck_mistakes_visibility")` |
| Migration (creation) | `backend/alembic/versions/013_add_mistakes_and_review.py:101` (column), `:109` — `sa.CheckConstraint("visibility='private'", name="ck_mistakes_visibility")` |
| Admin schema | `backend/app/schemas/mistake.py:98` — `visibility: Literal["private"]` |
| TS DTO | `src/lib/api/mistakes.ts:49` — `visibility: 'private'` |

Constraint name for 031 is exactly **`ck_mistakes_visibility`** (matches plan §PR-09 "replaces only `ck_mistakes_visibility`"). No later migration alters this constraint (grep of `backend/alembic/versions/` shows only 013 defines it). Sibling private-only constraints exist for questions (`ck_questions_visibility`, `backend/app/models/question.py:173`) and attachments (`ck_attachments_visibility`, `backend/app/models/attachment.py:58`) and are **out of PR-09 scope**.

### B.2 Key types for migration 032 (UUID/INTEGER)

| Column | Actual type | Evidence |
| --- | --- | --- |
| `KnowledgePoint.id` | **INTEGER** autoincrement PK | `backend/app/models/taxonomy.py:12` — `id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)` |
| `QuestionKnowledgePoint.knowledge_point_id` | **INTEGER** FK→`knowledge_points.id`, composite PK | `backend/app/models/question.py:213-217` |
| `QuestionKnowledgePoint.question_id` | **UUID** FK→`questions.id`, composite PK | `backend/app/models/question.py:208-212` |
| `Note.id` | **UUID** PK | `backend/app/models/note.py:35` — `id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)` |
| `KnowledgePointLink.knowledge_point_id` | **INTEGER** FK CASCADE | `backend/app/models/taxonomy.py:70-74` |

Confirms §2/§W3-D04: `note_knowledge_points.note_id` → UUID, `knowledge_point_id` → INTEGER. The older D8 UUID sketch is stale; current canonical models are authoritative.

### B.3 `MistakeOut` (admin) private fields — must not be reused as public DTO

`backend/app/schemas/mistake.py:84-105` — `MistakeOut` fields:

`id`, `source_draft_item_id`, `question_id`, `subject_id`, `title`, `question_text`, **`my_answer`**, `correct_answer`, `analysis`, `reason_category`, `mistake_reason`, `difficulty`, `status`, `visibility` (`Literal["private"]`), `version`, `knowledge_point_ids`, `review_item_id`, `created_at`, `updated_at`.

Private/internal fields excluded by W3-D03 allowlist: **`my_answer`** (`:91`), `source_draft_item_id` (`:86`), `subject_id` (`:88`), `version` (`:99`), `review_item_id` (`:101`). W3-D03 allowlist = `id, title, question_text, correct_answer, analysis, reason_category, mistake_reason, difficulty, knowledge_point_ids, created_at, updated_at` — all present in `MistakeOut` but the admin type additionally carries the private fields above and is bound to `get_current_admin` (`backend/app/routers/admin_mistakes.py:14`). Separate public DTO required.

### B.4 Dashboard summary — current data sources and not-yet-exposed capabilities

Router: `backend/app/routers/dashboard.py:22-23` — `GET /api/admin/dashboard/summary` → `dashboard_service.get_dashboard_summary` (`backend/app/services/dashboard_service.py:32-122`).

Current data sources (all canonical already):

| Summary element | Query | Evidence |
| --- | --- | --- |
| `counts.questions` | `Question.status=='active'` count | `dashboard_service.py:46` |
| `counts.mistakes` | `Mistake.status=='active'` count | `dashboard_service.py:47` |
| `counts.knowledge_points` | `KnowledgePoint.status=='active'` count | `dashboard_service.py:48` |
| `counts.due_reviews` | `ReviewItem.state=='active' AND next_review_at<=now` | `dashboard_service.py:49` |
| `counts.attachments` | `Attachment.status=='active'` | `dashboard_service.py:60` |
| `recent_questions` | active Questions, `updated_at DESC` limit 5 | `dashboard_service.py:72` |
| `recent_mistakes` | active Mistakes, `updated_at DESC` limit 5 | `dashboard_service.py:73` |
| `recent_reviews` | `ReviewRecord ⨝ ReviewItem ⨝ Mistake` (`ReviewItem.target_id == cast(Mistake.id, String)`), `reviewed_at DESC` limit 5 | `dashboard_service.py:74` |

Response shape `backend/app/schemas/dashboard.py:8-58` (`DashboardCounts/QuestionActivity/MistakeActivity/ReviewActivity/Sections/SystemStatus/Summary`) exposes **no** daily-practice count, **no** weak-KP ranking, **no** recently-mastered list — consistent with §2 "not yet expose daily practice, weak KnowledgePoints, or recently mastered".

Adjacent non-dashboard capabilities (must not be confused with the W3 targets):

- `GET /api/knowledge/weak-points` exists (`backend/app/routers/knowledge.py:33-39`) but `retrieve_weak_points` reads **legacy** `Note(type=='mistake')` with free-text `knowledge_points` clustering (`backend/app/services/knowledge_retrieval.py:247-311`) — not canonical KP analytics, not wired into Dashboard.
- `GET /api/admin/recommendations/today` exists (`backend/app/routers/recommendations.py:19-32`) — AI daily recommendation, explicitly out of Week 3 scope (§3 W3-D05 last bullet).
- No `/api/admin/practice/*` route exists (grep of `backend/app/routers/`).

### B.5 Public `/mistakes` read path (legacy Note)

Full chain:

1. `src/app/mistakes/page.tsx:27-38` — `useNoteIndex({ type: 'mistake', status: 'published', subject, difficulty, q, tag, folder_id, inbox, page, size: 20 })`.
2. `src/hooks/use-note-index.ts:5-15` — SWR key `/api/notes?...`, fetcher `listNotes`.
3. `src/lib/api/notes.ts:138` — `apiFetch<NoteListResponse>('/api/notes' + qs)`.
4. `backend/app/routers/notes.py:53-128` — `list_notes`: `select(Note).options(selectinload(Note.tags))` with `Note.type == type.value` (`:78-79`); non-admin forced `Note.hidden == False AND Note.status == 'published'` (`:81-83`). Queries the legacy **`notes`** table (`backend/app/models/note.py:32-78`), including legacy SM-2 fields (`ef`/`next_review`, `note.py:56-59`).

Conclusion: public `/mistakes` is legacy `Note(type='mistake')` via `useNoteIndex → listNotes → GET /api/notes`, matching §2. (Legacy review helpers on the same page, `useReviewStats`/`useReviewPlan` → `/api/review/stats|plan`, also read `Note` — `backend/app/routers/review.py:20-90`.)

### B.6 `Attempt.context_type` and `ReviewRecord.rating` (W3-D05 metrics)

| Item | Current contract | Evidence |
| --- | --- | --- |
| `Attempt.context_type` | `String(20)` default `practice`; CHECK `IN ('practice','review','editor_check')` | `backend/app/models/attempt.py:21`, `:25` (`ck_attempts_context_type`) |
| Attempt index for metrics | `idx_attempts_context_submitted (context_type, submitted_at)` | `backend/app/models/attempt.py:27` |
| `ReviewRecord.rating` | `Integer NOT NULL`; CHECK `BETWEEN 0 AND 5` | `backend/app/models/review_item.py:50`, `:64` (`ck_review_records_rating`) |
| `ReviewItem.last_rating` | `SmallInteger` nullable | `backend/app/models/review_item.py:28` |
| `ReviewItem.algorithm` | default `fixed_interval_v2`; CHECK `IN ('fixed_interval_v1','fixed_interval_v2')` | `backend/app/models/review_item.py:23`, `:35` |
| `ReviewItem.state` / record states | `IN ('active','mastered','paused')` on item and `previous_state`/`new_state` on record | `review_item.py:34`, `:66-67` |

W3-D05 notes: `context_type='practice'` is a first-class enum value (review re-answer uses `review` via `submitReanswer` → `/api/admin/attempts/review`, `src/lib/api/attempts.ts:34-38`), so practice accuracy can filter without parsing. `lapse_count` = `rating <= 2` is expressible against `ck_review_records_rating` (0..5). TS mirror: `ReviewRating = 0|1|2|3|4|5` (`src/lib/api/review-items.ts:3`), `AttemptContextType = 'practice'|'review'|'editor_check'` (`src/lib/api/attempts.ts:3`).

### B.7 Admin mutation optimistic-version / conflict pattern (PR-09 alignment reference)

Representative implementation — canonical `Mistake` update:

- Request carries `version: int = Field(ge=1)` (`backend/app/schemas/mistake.py:49-50` `MistakeUpdate`; bare `VersionCommand` at `:45-46` for delete).
- Service compare-and-bump: `backend/app/services/mistake_service.py:173-181` — `if r.version != payload.version: raise MistakeConflict("Mistake version conflict")` (`:175`), on success `r.mistake.version += 1` (`:181`). Same pattern at `:186` (archive) and `:96`/`:113`/`:143` for drafts.
- Router maps to HTTP **409**: `backend/app/routers/admin_mistakes.py:21-22` — `MistakeConflict → HTTPException(status_code=409)`.
- Identical pattern family: `QuestionConflict` (`backend/app/services/question_service.py:269-270`, router `backend/app/routers/questions.py:21-22`); `ReviewConflict` uses expected-state compare (`expected_next_review_at`, `backend/app/services/review_item_service.py:66-68` → 409 at `backend/app/routers/review_items.py:21-22`).

PR-09 visibility mutation should follow: payload `version` required → mismatch raises domain conflict → 409 → success increments `Mistake.version`.

### B.8 Existing API client shape (style reference for PR-09/PR-13 clients)

Shared transport: `src/lib/api/client.ts` — `apiFetch<T>()`, `ApiError { status, kind }` (`client.ts:5-17`).

Observed module style (snake_case fields mirroring backend Pydantic, no runtime validation, path constants inline):

- `src/lib/api/attempts.ts:1-39` — exported TS enums as string-literal unions (`AttemptContextType`, `ReanswerVerdict`), `interface Attempt`, verb functions returning `Promise<T>` (`submitAttempt`, `submitReanswer`), `apiFetch<...>('/api/admin/attempts', { method, body: JSON.stringify(...) })`.
- `src/lib/api/review-items.ts:1-59` — `ReviewRating = 0|1|2|3|4|5`, `interface ReviewItem/ReviewRecord` with literal unions for state/algorithm, list/get/submit functions (`listDueReviewItems`, `listReviewRecords`, `submitReview` with optional field spread `...(attemptId === undefined ? {} : { attempt_id: attemptId })` at `:56`).
- `src/lib/api/mistakes.ts:1-55` — domain literal types (`MistakeReason`, `MistakeStatus`), `interface Mistake` with `visibility: 'private'` (`:49`), CRUD verbs against `/api/admin/mistakes` (`:138-156`).
- `src/lib/api/notes.ts:3-104` — list/detail/version/input interfaces + `NoteListParams` query typing.

New public-mistakes / practice clients should copy this pattern (interface + literal unions + `apiFetch` verb functions, admin vs public path prefix chosen per route ownership).

---

## C. W3-D04 model check — Note↔KP and `knowledge_point_links` polymorph

1. **Note↔KP association table: none exists today.**
   - The only association `Table` on `Note` is `note_tags` (`backend/app/models/note.py:24-29`) with `note_id UUID FK CASCADE` + `tag_id INTEGER FK CASCADE`.
   - `Note` relationships: `tags` via `secondary="note_tags"` (`note.py:71`) and `folder_id` FK (`note.py:63-65`). No relationship to `KnowledgePoint`.
   - Note stores subject as free text `subject: Mapped[str | None]` (`note.py:49`) and knowledge points as free text `knowledge_points: Mapped[str | None]` (`note.py:55`) — confirms §PR-12 "Note stores subject as free text rather than a canonical `subject_id`".
   - No `note_knowledge_points` table in models or in `backend/alembic/versions/` (grep of `note_knowledge` → zero hits). Migration 032 is a net-new table.

2. **`knowledge_point_links` polymorph — leave intact (PR-12 must not touch).**
   - Model: `backend/app/models/taxonomy.py:66-89` — `id INTEGER` autoincrement PK (`:69`), `knowledge_point_id INTEGER FK CASCADE` (`:70-74`), `target_type String(30)` (`:75`), `target_id String(64)` (`:76`), `created_at` (`:77-79`).
   - Uniqueness: `uq_knowledge_point_links_target (knowledge_point_id, target_type, target_id)` (`:82-87`); lookup index `idx_knowledge_point_links_target (target_type, target_id)` (`:88`).
   - Created in `backend/alembic/versions/011_add_subject_taxonomy.py:133-168`.
   - Observed `target_type` writers (string-literal polymorph, `target_id = str(uuid)`):
     - `"question"` / `"question_draft"` — `backend/app/services/question_service.py:117,323,419`, `backend/app/services/draft_service.py:144,236,332`.
     - `"mistake"` / `"mistake_draft"` — `backend/app/services/mistake_service.py:77,104-105,167,179-180`.
   - No service writes `target_type='note'`; Notes reach KPs only via free text (`note.py:55`) and via `knowledge_relations` suggestions (`backend/app/services/knowledge_relations.py:132` — a different table/domain).
   - Migration-026 governance restricts `DELETE` on `knowledge_point_links` to `legacy_migration_owner` (`backend/alembic/versions/026_legacy_system_retirement.py:1287-1300`) — further reason PR-12 adds a **new** association table (`note_knowledge_points`) instead of overloading this one.

---

## Unresolved issues

1. **UNRESOLVED (minor):** scratch DB runtime pin not executed here — this inventory is offline-only per constraints. PR-09/031 work must still run `alembic heads`/`current` inside the guarded `astra_week3_*` scratch environment to record the live `alembic_version` row value == `030` before upgrade. Static graph evidence is strong but is not a live DB check.
2. **UNRESOLVED (out of this task's lanes):** legacy mistake writers/readers full inventory and migration-026 adapter v1/v2 ReviewItem algorithm diff belong to `W3-00-inv-inventory` (separate assignment); only the touchpoints encountered incidentally are cited above (`mistake_service.convert_mistake_draft` hardcodes `visibility="private"` at `backend/app/services/mistake_service.py:165`, matching §2's adapter note, but the adapter itself `backend/app/services/legacy_note_migration_adapter.py` was not fully audited here).
3. **NOTE (not blocking):** `Question.visibility` and `Attachment.visibility` share the private-only pattern with their own constraint names (`ck_questions_visibility`, `ck_attachments_visibility`). PR-09 scope must stay on `ck_mistakes_visibility` only — flagged so 031 does not accidentally widen the others.
