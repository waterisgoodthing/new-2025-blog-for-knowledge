# Requirements: AI Skill Pipeline Knowledge Base

## Scope

This workflow defines an AI skill pipeline and first-stage knowledge base implementation plan. It does not authorize runtime implementation until `tasks.md` is explicitly approved.

## User Decisions

| Decision | Value |
|---|---|
| Primary goal | Postgraduate exam review |
| First-class `KnowledgePoint` entity | No, defer until data volume grows |
| Vector database | No, defer until after first knowledge-base round |
| First retrieval mode | Structured retrieval only |
| Automatic bidirectional relations | Allowed as suggestions |
| Citation requirement | Required for AI-generated knowledge output |

## Functional Requirements

### FR1: Skill Pipeline Map

The system design must preserve this pipeline allocation:

```text
polish:
  - deepseek_polish
  - optional_humanizer

mistake_text_analysis:
  - deepseek_solve
  - tone_refine_for_advice_fields

mistake_ocr:
  - qwen_vl_ocr
  - optional_text_analysis

mistake_social_export:
  - card_generator

knowledge_article:
  - notes_retrieval
  - citation_backed_generation
```

### FR2: Field Safety

Humanizing or tone refinement must not modify precision-sensitive fields:

- `question`
- `correct_answer`
- formulas
- code
- OCR text
- JSON keys
- source identifiers

Allowed tone-refinement fields:

- `error_reason`
- `key_step`
- `generalization`
- `review_advice`
- `similar_traps`

### FR3: Structured Retrieval

Phase 1 retrieval must use existing structured fields only:

- `subject`
- `knowledge_points`
- `tags`
- `type`
- `difficulty`
- `ai_metadata`
- `created_at`
- `updated_at`
- `last_reviewed`
- `next_review`

No vector database, embedding model, or first-class knowledge-point table is required in phase 1.

### FR4: Relation Suggestions

The system should suggest relationships without silently treating them as confirmed facts.

Initial relation types:

- `explains`: a note explains a mistake.
- `similar`: two mistakes are similar.
- `prerequisite`: one source provides prerequisite knowledge.
- `follow_up`: a source is useful for later review.
- `source_for`: a source can support generated summaries or articles.

### FR5: Citation-Backed Generation

AI-generated review summaries, weak-point reports, and knowledge articles must include source references.

Rules:

- Source-backed claims must list source IDs or source refs.
- AI-only inference must be labeled as AI inference.
- Generated text must not invent citations.
- Missing source coverage should be reported instead of hidden.
- Empty or insufficient source coverage must return `insufficient_context` instead of unsupported factual articles.

### FR6: Social Card Export

Social-card generation is a manual export action, not an automatic side effect of saving a mistake.

Input data may include:

- question
- my answer
- correct answer
- analysis
- error reason
- key step
- knowledge points
- variant questions

### FR7: Skill Installation Documentation

The workflow must record installation commands and known setup problems for:

- Humanizer-zh
- guizang-social-card-skill
- ian-xiaohei-illustrations
- notebooklm-skill

### FR8: Mistake Detail Related Knowledge Display

The existing mistake detail view must show structured related knowledge from `POST /api/knowledge/context-pack`.

Rules:

- Only render this panel for `note.type === "mistake"`.
- Use the current mistake's `subject`, `knowledge_points`, tags, `difficulty`, and type hints as query input.
- Show related notes, similar mistakes, relation suggestions, and source excerpts when available.
- Empty results must render a quiet empty state.
- Loading and API error states must not block the rest of the mistake detail page.
- Links must use existing `/notes/{slug}` detail routes.
- Do not persist relation suggestions in this phase.

### FR9: Weak-Point Summary Display

The existing mistakes/review surfaces must show structured weak points from `GET /api/knowledge/weak-points`.

Rules:

- Use the existing `/mistakes` overview and/or `/mistakes/review` page.
- Do not create a new route.
- Show knowledge point, subject, mistake count, due review count, recent error count, top error reasons, and evidence sources when available.
- Empty datasets must render a quiet empty state.
- Loading and API error states must not block existing review stats or review queue behavior.

### FR10: Frontend Scope Control

This frontend round must stay within display integration:

- No vector database.
- No `KnowledgePoint` entity or management UI.
- No relation persistence.
- No new top-level route.
- No NotebookLM runtime integration.
- No social card export UI.
- No AI summary generation UI unless separately approved.

## Non-Functional Requirements

| Type | Requirement |
|---|---|
| Accuracy | Review and OCR flows must prioritize correctness over natural style. |
| Safety | API keys must not be exposed to the frontend. |
| Performance | Optional skill steps should not slow down every AI call by default. |
| Extensibility | Pipeline design should allow future AI config management. |
| Traceability | Citation-backed output must be auditable from source refs. |
| Scope control | Avoid adding vector search or heavy graph modeling in phase 1. |
| Determinism | Retrieval and weak-point endpoints must not call external AI providers. |
| Auditability | Source-backed blocks must trace to source type, source ID, field, and excerpt when available. |
| UI resilience | Knowledge panels must degrade gracefully when backend data is empty or unavailable. |
| Frontend ergonomics | Operational pages should remain dense, readable, and review-focused. |

## Out of Scope For Phase 1

- Vector database setup.
- Embedding model selection.
- First-class `KnowledgePoint` database table.
- NotebookLM runtime integration.
- Silent automatic relation persistence.
- Full AI provider management UI.
- Production-grade API key encryption design.
- Runtime dependency on OpenClaw, Claude Code, Codex, or local skill folders.
- Automatic external AI calls inside deterministic retrieval endpoints.
- Silent overwrite of original note, mistake, OCR, formula, code, answer, or source-reference content.
- New frontend routes for this display round.
- Relation confirmation/persistence UI.
- AI summary generation UI.
