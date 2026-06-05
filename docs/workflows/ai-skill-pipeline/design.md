# Design: AI Skill Pipeline Knowledge Base

## Architecture Line

This workflow primarily affects the personal knowledge backend under `backend/`, with frontend entry points under `src/` planned only after task approval.

The original static-blog system under `src/` should not be blurred with backend persistence. Blog generation can consume cited sources, but source data remains in the backend knowledge model unless explicitly exported.

## Phase 1 Concept

Phase 1 is a lightweight knowledge layer:

```text
notes / mistakes / reviews
  -> structured retrieval
  -> source references
  -> relation suggestions
  -> citation-backed generation
```

No vector database and no first-class `KnowledgePoint` model are introduced in phase 1.

## Existing Model Mapping

Implementation must verify current model fields before writing code. Based on the current backend, phase 1 should map onto the existing `Note` model instead of introducing a new knowledge-point entity.

Current data shape:

| Concept | Current source |
|---|---|
| Notes | `Note.type == "note"` |
| Blogs | `Note.type == "blog"` |
| Mistakes | `Note.type == "mistake"` |
| Subject | `Note.subject` |
| Difficulty | `Note.difficulty` |
| Question | `Note.question` |
| User answer | `Note.my_answer` |
| Correct answer | `Note.correct_answer` |
| Analysis | `Note.analysis` |
| Knowledge points | `Note.knowledge_points` string |
| Review state | `Note.ef`, `Note.interval`, `Note.repetitions`, `Note.next_review`, `Note.last_reviewed` |
| AI metadata | `Note.ai_metadata` JSON |
| Images | `Note.images` JSON |
| Tags | `Tag` through `note_tags` |
| URL target | `Note.slug` |

Implementation notes:

- Treat `knowledge_points` as a normalized string list at query time.
- Treat `ai_metadata` as optional and schema-flexible.
- Do not assume separate review rows unless a later approved task adds them.
- Use real field names from models and schemas before implementing filters.

## Skill Pipeline Design

### polish

```text
deepseek_polish
optional_humanizer
```

Purpose:

- Improve note and blog wording.
- Optionally reduce AI-like phrasing.

Safety:

- Do not run humanizer on OCR text, formulas, code, answers, or source references.
- Preserve streaming behavior when possible. If full-output humanizing is needed, it should be opt-in.

### mistake_text_analysis

```text
deepseek_solve
tone_refine_for_advice_fields
```

Purpose:

- Produce the structured mistake analysis.
- Refine only advice-style fields.

Field handling:

```text
Preserve:
  question
  correct_answer
  analysis
  knowledge_points

May refine:
  error_reason
  key_step
  generalization
  review_advice
  similar_traps
```

### mistake_ocr

```text
qwen_vl_ocr
optional_text_analysis
```

Purpose:

- Extract visible problem content from images.
- Optionally solve or complete analysis only when the user asks or when required data is absent.

Safety:

- OCR is faithful extraction, not rewriting.
- Humanizer must not run on OCR output.

### mistake_social_export

```text
card_generator
```

Purpose:

- Generate review cards, social cards, or article cover assets from structured mistake data.

Trigger:

- Manual export action from a mistake detail, weekly review, or share flow.
- Not automatic on save.

### knowledge_article

```text
notes_retrieval
citation_backed_generation
```

Purpose:

- Generate exam-review summaries, weak-point reports, outlines, and future blog drafts from existing sources.

Citation rule:

- Every factual claim should link back to source refs where possible.
- Uncited synthesis must be labeled as AI inference.

## Structured Retrieval

Suggested service:

```text
backend/app/services/knowledge_retrieval.py
```

Inputs:

```text
subject
knowledge_points
tags
type
difficulty
date range
review state
limit
```

Match strategy:

- Exact or normalized subject match.
- Split `knowledge_points` by comma-like separators and match with `ilike`.
- Tag overlap when tags are available.
- Mistakes with recent errors and due reviews get higher priority.
- Notes that share subject and knowledge-point terms are candidate explanations.

Suggested explainable scoring:

```text
score =
  subject_match * 3
+ knowledge_point_overlap * 4
+ tag_overlap * 2
+ type_match * 1
+ due_review_bonus * 2
+ recent_mistake_bonus * 2
- stale_penalty
```

The score is an internal ranking aid in phase 1. It does not create confirmed relationships.

## Source Reference Contract

Proposed source ref:

```json
{
  "source_type": "note",
  "source_id": "abc",
  "title": "条件概率笔记",
  "slug": "conditional-probability",
  "field": "content",
  "excerpt": "贝叶斯公式用于已知结果反推原因概率...",
  "url": "/notes/conditional-probability",
  "confidence": 0.86,
  "match_reasons": ["subject_match", "knowledge_point_overlap"]
}
```

For mistakes:

```json
{
  "source_type": "mistake",
  "source_id": "123",
  "title": "条件概率错题",
  "field": "analysis",
  "excerpt": "本题错误来自混淆 P(A|B) 与 P(B|A)...",
  "url": "/notes/conditional-probability-mistake",
  "confidence": 0.82,
  "match_reasons": ["subject_match", "error_reason_match"]
}
```

Source ref rules:

- `source_type`, `source_id`, and `field` are required.
- `excerpt` should be copied from existing source content and must not be humanized.
- AI must not invent source IDs, slugs, URLs, or excerpts.
- If a claim lacks source support, it must be emitted as AI inference.

## Relation Suggestion Contract

```json
{
  "source_type": "mistake",
  "source_id": "123",
  "target_type": "note",
  "target_id": "abc",
  "relation_type": "explains",
  "score": 0.82,
  "reason": "同属数学，知识点均包含条件概率、贝叶斯公式",
  "status": "suggested"
}
```

Phase 1 can return these suggestions without persistence. A later phase may add confirmation, ignore, and pin actions.

## Proposed API Shape

Phase 1 candidate endpoints:

```text
POST /api/knowledge/context-pack
GET /api/knowledge/weak-points?days=30
POST /api/ai/knowledge-summary
```

### `POST /api/knowledge/context-pack`

This endpoint only retrieves and ranks existing data. It must not call DeepSeek, Qwen, OpenAI, OpenClaw skills, Claude Code skills, or any external AI provider.

Request:

```json
{
  "subject": "数学",
  "knowledge_points": ["条件概率", "贝叶斯公式"],
  "tags": ["概率论", "错题"],
  "type": "mistake",
  "difficulty": "medium",
  "date_range": {
    "from": "2026-05-01",
    "to": "2026-06-05"
  },
  "review_state": "due",
  "limit": 10
}
```

`context-pack` response should include:

```json
{
  "sources": [],
  "related_notes": [],
  "related_mistakes": [],
  "suggested_relations": [],
  "stats": {
    "mistake_count": 0,
    "note_count": 0,
    "top_error_reasons": []
  }
}
```

### `GET /api/knowledge/weak-points?days=30`

This endpoint must be deterministic and must not call external AI providers.

Response:

```json
{
  "days": 30,
  "weak_points": [
    {
      "subject": "数学",
      "knowledge_point": "条件概率",
      "mistake_count": 5,
      "due_review_count": 2,
      "recent_error_count": 3,
      "top_error_reasons": ["混淆条件方向", "审题不完整"],
      "evidence_sources": []
    }
  ]
}
```

### `POST /api/ai/knowledge-summary`

This endpoint may call an AI provider, but only from source refs supplied by or derived from a context pack.

Output blocks must distinguish:

```text
source_backed_claim
ai_inference
insufficient_context
```

Response:

```json
{
  "title": "条件概率薄弱点总结",
  "blocks": [
    {
      "type": "source_backed_claim",
      "text": "你在条件概率题目中主要错误是混淆 P(A|B) 与 P(B|A)。",
      "source_refs": [
        {
          "source_type": "mistake",
          "source_id": "123",
          "field": "analysis"
        }
      ]
    },
    {
      "type": "ai_inference",
      "text": "后续复习应优先训练条件方向识别。",
      "source_refs": []
    }
  ]
}
```

If sources are insufficient:

```json
{
  "status": "insufficient_context",
  "message": "No usable source references are available for factual generation.",
  "outline": []
}
```

## Skill Installation In Design

Installed external skills are treated as capability providers for development and content workflows. Runtime product integration should use explicit backend services and safe contracts, not hidden Codex skill invocations.

This distinction matters:

- Codex/OpenClaw skills can help generate prompts, cards, images, and knowledge drafts during development.
- The blog system runtime should call explicit backend functions or configured providers.

## Future Phase

After the first round of knowledge accumulation:

- Promote frequently reused `knowledge_points` strings into first-class entities.
- Add relation persistence and user confirmation.
- Evaluate embeddings or vector retrieval.
- Consider NotebookLM-assisted external knowledge workflows.
- Add AI provider and skill-pipeline settings in manage UI.
