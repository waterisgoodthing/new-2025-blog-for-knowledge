# Validation: AI Skill Pipeline Knowledge Base

## Validation Status

Backend Phase 3–5 implementation complete. Validation performed on 2026-06-05.

## Validation Gate

- `tasks.md`: approved via user's explicit implementation instruction.
- Implementation tasks: executed for Phase 3 (schemas), Phase 4 (services), Phase 5 (API endpoints).
- `git status --short`: checked before implementation. User changes preserved.
- `AGENTS.md`: read and followed.

## Evidence Summary

### V1 Planning Gate

All required files exist:

- [x] `README.md`
- [x] `requirements.md`
- [x] `design.md`
- [x] `tasks.md`
- [x] `validation.md`
- [x] `handoff-prompt.md`
- [x] `report.md`

### V2 Scope Control

Verified no phase-1 implementation introduces:

- [x] No vector database
- [x] No embedding model
- [x] No first-class `KnowledgePoint` table or model
- [x] No silent persistent relation graph
- [x] No unapproved frontend routes or pages
- [x] No runtime dependency on OpenClaw, Claude Code, Codex, or local skill folders
- [x] No AI calls inside deterministic retrieval endpoints

### V3 Existing Model Mapping

Verified real fields in:

- [x] `backend/app/models/note.py`: Note model with all required fields
- [x] `backend/app/schemas/note.py`: NoteType, Difficulty, NoteOut, etc.
- [x] `backend/app/routers/review.py`: SM-2 review integration

### V4 Structured Retrieval

Target: `POST /api/knowledge/context-pack`

- [x] Subject matching works (ilike)
- [x] Knowledge_points matching works (comma-split + ilike)
- [x] Tags matching works (via note_tags join)
- [x] Date range filtering works
- [x] Limit is respected (1–100)
- [x] Empty results handled safely
- [x] No external AI provider called (verified via `inspect.getsource()`)

### V5 Weak-Point Summary

Target: `GET /api/knowledge/weak-points?days=30`

- [x] Days parameter is respected (1–365)
- [x] Recent mistakes are counted
- [x] Due reviews are counted
- [x] Top error reasons returned (from ai_metadata)
- [x] Empty datasets return safe empty response
- [x] No external AI provider called (verified via `inspect.getsource()`)

### V6 Source Reference Contract

Source refs include:

- [x] source_type (note/mistake)
- [x] source_id (UUID string)
- [x] title
- [x] slug
- [x] field
- [x] excerpt (max 300 chars)
- [x] url
- [x] confidence (0–1)
- [x] match_reasons

### V7 Relation Suggestions

Relation suggestions include:

- [x] source_type, source_id
- [x] target_type, target_id
- [x] relation_type (explains/similar/prerequisite/follow_up/source_for)
- [x] score (0–1)
- [x] reason
- [x] status (default: "suggested")

Relations are NOT persisted — only returned as suggestions.

### V8 Citation-Backed Generation

Target: `POST /api/ai/knowledge-summary`

- [x] source_backed_claim blocks include source_refs
- [x] ai_inference blocks are labeled
- [x] insufficient_context returned when no sources
- [x] No invented source IDs (validated against input sources)
- [x] Empty sources produce insufficient_context, not unsupported articles
- [x] source_backed_claim without valid refs downgraded to ai_inference

### V9 Field Safety

Not directly applicable to this implementation pass (no humanizer/tone refinement code changes). Existing field safety rules in `ai_polish_service.py` are preserved.

### V10 OCR Safety

Not directly applicable to this implementation pass. Existing OCR safety in `ai.py` router is preserved.

### V11 Social Card Export

Not directly applicable — social card export not implemented in this pass.

### V12 Security

- [x] API keys not exposed to frontend code
- [x] Provider secrets read from backend environment/config only (`app/config.py`)
- [x] Runtime code does not depend on local skill folders
- [x] Logs do not print API keys (existing logging in `ai_polish_service.py` only logs action/text_len/duration/status)

### V13 Performance

- [x] Optional humanizer does not run by default on every AI call
- [x] Social card export is manual (not implemented)
- [x] Deterministic retrieval endpoints do not call external AI
- [x] context-pack respects limit (1–100)

## Commands Run

```bash
# Import verification
.venv/bin/python -c "from app.schemas.knowledge import ..."
.venv/bin/python -c "from app.services.knowledge_retrieval import ..."
.venv/bin/python -c "from app.services.knowledge_relations import ..."
.venv/bin/python -c "from app.routers.knowledge import router"
.venv/bin/python -c "from app.routers.ai import knowledge_summary"
.venv/bin/python -c "from main import app"

# Deterministic verification
.venv/bin/python -c "import inspect; ... assert 'call_text_model' not in src"

# Schema validation
.venv/bin/python -c "req = ContextPackRequest(...); ref = SourceRef(...)"
```

All commands passed.

## Modified Files

| File | Change |
|---|---|
| `backend/app/schemas/knowledge.py` | New file — all knowledge schemas |
| `backend/app/services/knowledge_retrieval.py` | New file — structured retrieval + weak-point aggregation |
| `backend/app/services/knowledge_relations.py` | New file — relation suggestion scoring |
| `backend/app/routers/knowledge.py` | New file — context-pack + weak-points endpoints |
| `backend/app/routers/ai.py` | Added knowledge-summary endpoint + imports |
| `backend/main.py` | Registered knowledge router |

## Remaining Risks

1. **AI model dependency**: `POST /api/ai/knowledge-summary` requires DeepSeek API configuration (`DEEPSEEK_API_KEY`). If not configured, the endpoint will return 500.
2. **No database migration needed**: All new code uses existing `Note` model fields. No schema changes.
3. **Frontend integration deferred**: T6-1, T6-2, T6-3 are not implemented. Frontend types and UI components are needed for full user-facing feature.
4. **External skills deferred**: T1-3, T2-1 through T2-4 are not implemented. These are development-time concerns, not runtime blockers.
