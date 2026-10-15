# Design: Mistake Learning Reliability Upgrade

Version: v1.0
Date: 2026-06-12
Status: Draft, awaiting task approval

## Architecture Overview

This workflow touches both active project lines:

- Frontend and original static-blog system under `src/`.
- Personal knowledge backend under `backend/`.

Primary flow after the upgrade:

```text
write/review/detail page
  -> route hook or local action
  -> src/lib/api/*
  -> backend router
  -> schema validation
  -> service/model
  -> response schema
  -> frontend state and rich rendering
```

The design keeps deterministic weak-point aggregation separate from AI generation:

```text
Mistake records
  -> deterministic aggregation and canonicalization
  -> weak-point clusters with source refs
  -> optional personalized AI diagnosis using validated sources + personal fields
```

## Page Design

### `/mistakes`

Current problem:

- Sidebar renders raw tags.
- Review plan renders raw `weaknesses`.
- `WeakPointDiagnosis` renders a large inline section.

New layout:

- Left sidebar:
  - Show broad filters only: all mistakes, folder, top canonical concepts.
  - Move raw tags into a compact secondary "更多标签" area or searchable drawer.
- Top summary:
  - Keep review stats and today's plan.
  - Show top 3 canonical weak-point clusters.
- Weak-point diagnosis:
  - Replace full inline diagnosis with a compact trigger row.
  - Open a drawer for detailed diagnosis.
  - Drawer contents: cluster summary, personalized cause, evidence mistakes, next checklist, variant/card actions.

Desktop drawer:

- Right-side drawer, max width around 420-520 px.
- Does not resize the main mistake list.

Mobile drawer:

- Bottom drawer.
- Full-width, scrollable body, fixed close action.

### `/notes/[id]` For Mistakes

Current problem:

- Tags are in the right rail.
- `知识点归总` is a large lower block, leaving empty space.

New layout:

- Main column:
  - Image evidence.
  - Question.
  - My answer.
  - Correct answer.
  - Personal error analysis.
  - Detailed solution analysis.
  - AI diagrams and related knowledge.
- Right rail:
  - Review status.
  - Tags.
  - Knowledge summary directly below tags.
  - Next action/checklist.
  - Related mistake links if compact.

### `/write-mistake`

Current problem:

- AI analysis only receives image or one text blob.
- `my_answer` exists in the form but is not part of the structured AI request.
- The current `analysis` field mixes AI solution and user reflection.

New interaction:

- Keep question/image input.
- Add or clarify personal context fields:
  - `我的答案`
  - `我当时的思路`
  - `我自己判断的错因`
- AI actions:
  - "解析题目": solve/analyze the problem.
  - "分析我的错因": compare my answer and self-analysis with the correct answer.
  - "生成知识点": extract canonical concepts.
- Save behavior:
  - Preserve `my_answer`.
  - Preserve user self-analysis separately in `ai_metadata.user_error_analysis` unless a schema migration is approved.
  - Preserve AI-personalized diagnosis in `ai_metadata.personalized_diagnosis`.
  - Do not merge the user's self-analysis into the generic `analysis` blob as the only stored copy.

## API Design

### Public API Reliability

Frontend:

- `src/lib/api/config.ts` remains the single source of API base URL.
- `apiFetch` should classify:
  - browser network failure,
  - CORS/opaque failure,
  - auth failure,
  - backend JSON error,
  - non-JSON upstream/Cloudflare response.

Backend:

- No source code should hardcode Cloudflare-only operational assumptions.
- Health/status endpoints should remain simple to probe publicly.

### Note Datetime Writes

Endpoint:

- Existing `POST /api/review/{slug}`.
- Existing note update/type-conversion paths that assign `Note.updated_at`.

Design:

- Add a backend timestamp helper for current `Note` datetime columns.
- Use the helper anywhere this workflow touches `Note.updated_at` or `Note.last_reviewed`, including review submit and adjacent note update/type-conversion paths.
- Keep SM-2 logic unchanged unless validation exposes another issue.

Error behavior:

- Backend returns JSON error if note not found or invalid quality.
- Frontend shows backend detail instead of generic `Failed to fetch`.

### Unique Slugs

Endpoint:

- Existing `POST /api/notes`.

Design options:

1. Preferred minimal approach: backend ensures uniqueness when `slug` is provided by app-generated flows.
2. Alternative: frontend calls a slug-preview endpoint before save.

Chosen draft:

- Add a backend helper to normalize and suffix slugs: `base`, `base-2`, `base-3`.
- Preserve explicit user-provided slugs in edit flows; only auto-suffix create conflicts.
- Improve frontend error parsing for residual `409`.

### Personalized AI Analysis

Existing endpoints:

- `POST /api/ai/analyze`
- `POST /api/ai/analyze-text`
- streaming variants.

Draft contract extension:

```json
{
  "images": [],
  "text": "题干或 OCR 文本",
  "question": "结构化题目",
  "my_answer": "我的答案",
  "correct_answer": "正确答案",
  "user_error_analysis": "我自己认为错在哪里",
  "analysis_mode": "solve_and_personalize"
}
```

Draft response extension:

```json
{
  "analysis": "通用解析",
  "error_reason": "通用易错原因",
  "personalized_diagnosis": "结合我的答案后的错因",
  "misread_signal": "题目中我忽略的信号",
  "next_time_checklist": ["先判断网络号", "再判断广播地址"],
  "latex_warnings": []
}
```

Compatibility:

- Existing clients can omit new fields.
- Existing response fields remain available.

### Weak-Point Clusters

Existing endpoint:

- `GET /api/knowledge/weak-points?days=30`

Draft response extension:

```json
{
  "subject": "计算机网络",
  "knowledge_point": "以太网交换",
  "canonical_name": "以太网交换",
  "aliases": ["交换机", "直通交换", "存储转发"],
  "mistake_count": 3,
  "due_review_count": 1,
  "recent_error_count": 1,
  "top_error_reasons": [],
  "evidence_sources": [],
  "personalization_available": true
}
```

Design rule:

- Aggregation stays deterministic.
- Any AI-generated personalized paragraph must live in a separate explicit endpoint or action.

## Data Design

Existing first-class mistake fields stay authoritative:

- `subject`
- `difficulty`
- `question`
- `my_answer`
- `correct_answer`
- `analysis`
- `knowledge_points`
- review metadata
- `ai_metadata`

Draft storage for new personalized fields:

- `ai_metadata.user_error_analysis`
- `ai_metadata.personalized_diagnosis`
- `ai_metadata.misread_signal`
- `ai_metadata.next_time_checklist`
- `ai_metadata.latex_warnings`

Rationale:

- This avoids a database migration in the first pass.
- If usage proves stable, a later workflow can promote selected fields into explicit columns.

Tag/concept normalization:

- Short-term: implement a service/helper mapping raw strings to canonical concepts.
- Medium-term: expose tag merge/alias management in the management UI.
- Out of scope now: a full `KnowledgePoint` table.

Tag-write hygiene:

- AI tag generation should prefer these categories only:
  - subject or course area, such as `计算机网络`;
  - canonical knowledge concept, such as `子网划分`;
  - question type or skill gap, such as `广播地址判断`;
  - stable review cue, such as `概念混淆`.
- The write flow should filter or demote obvious low-value tags before saving:
  - quality labels, such as `解析清晰`;
  - generic adjectives, such as `重要`, `常见`;
  - overly small fragments that have a canonical parent, such as displaying `直通交换` under `以太网交换` instead of as a primary tag;
  - duplicate aliases already represented by a canonical concept.
- Raw terms may remain in `knowledge_points`, evidence excerpts, or secondary details; they should not flood the primary tag navigation.

## LaTeX Design

Rendering:

- Keep the existing `RichText -> useMarkdownRender -> renderMarkdown -> KaTeX` path.

Generation:

- Strengthen prompts for all mistake analysis and variant/card endpoints.
- Add a validation step that detects:
  - bare LaTeX commands such as `\frac`,
  - formula-like lines with `=`, `^`, `/`, units, or Greek symbols,
  - block formulas not wrapped in `$$`.
- If invalid, repair the affected JSON string fields before returning to frontend.

Validation:

- Add a sample mistake containing inline and block math.
- Confirm it renders in `StudyBlock` fields.

## Exception Design

| Case | Behavior |
|------|----------|
| API host unreachable | Show network/API host diagnostic, not generic failed fetch. |
| Auth expired | Show login/session message and offer relogin path. |
| Cloudflare Access redirect | Detect non-JSON/HTML response and report API host access problem. |
| Slug conflict | Auto-suffix on create or show conflict with suggested slug. |
| Review timestamp failure | Covered by backend helper and regression validation. |
| Empty weak points | Show compact empty state and keep drawer closed. |
| Insufficient personalization | Show limited diagnosis and ask for `my_answer` or self-analysis. |
| Invalid LaTeX | Preserve source text, show warning in metadata, do not crash rendering. |

## Security And Privacy

- Do not log full personal answers in production logs.
- Do not commit `.env`, tunnel credentials, tokens, private keys, or screenshots containing secrets.
- Keep admin-only mutation paths protected by the existing JWT/session model.
- External Cloudflare tunnel config changes require explicit approval and should be recorded as operational validation, not source changes.

## Validation Strategy

- Frontend TypeScript: `npx tsc --noEmit`.
- Build-sensitive changes: `npm run build`.
- Backend import/start checks for changed routers/services.
- API probes:
  - public health,
  - auth/passkey status,
  - subjects/list endpoint with public Origin,
  - review submit against a test mistake.
- Browser checks:
  - login/auth status,
  - create two similar-title mistakes,
  - review one due mistake,
  - inspect `/mistakes` drawer,
  - inspect `/notes/[id]` layout and LaTeX rendering.
