# Design

## Workflow Model

The new mistake creation process is staged:

```text
Question Source
  -> AI Question Draft
  -> Learner Draft Review
  -> Learner Error Reason
  -> AI Error Interpretation Proposal
  -> Learner Acceptance Gate
  -> Final Analysis
  -> Teaching Diagram
  -> Save Mistake
```

Each stage has a clear owner:

- AI owns extracting and structuring question information.
- The learner owns confirming or correcting the extracted question draft.
- The learner owns the real error reason.
- AI owns interpreting that error reason.
- The learner owns acceptance or rejection.
- AI owns final analysis only after acceptance.

## Staged State Machine (T0-03)

### Frontend State

```text
States:
  idle           → initial state, no input
  uploading      → image/text being uploaded
  draft_pending  → AI question draft returned, awaiting learner review
  draft_confirmed → learner confirmed/edited the question draft
  reason_entered → learner wrote their error reason
  interpreting   → AI generating error interpretation
  interpretation_proposed → AI proposal shown, awaiting accept/reject
  interpreting_rejected   → learner rejected, AI regenerating
  analysis_ready → accepted interpretation, can generate final analysis
  analyzing      → AI generating final analysis
  analyzed       → final analysis returned
  diagram_ready  → can generate diagram
  diagramming    → AI generating diagram
  diagrammed     → diagram returned
  saving         → persisting to backend
  saved          → complete

Allowed transitions:
  idle → uploading
  uploading → draft_pending
  draft_pending → draft_confirmed  (learner edits + confirms)
  draft_confirmed → reason_entered  (learner writes error reason)
  reason_entered → interpreting
  interpreting → interpretation_proposed
  interpretation_proposed → analysis_ready  (accepted)
  interpretation_proposed → interpreting_rejected  (rejected with reason)
  interpreting_rejected → interpreting  (regenerate)
  analysis_ready → analyzing
  analyzing → analyzed
  analyzed → diagram_ready
  diagram_ready → diagramming
  diagramming → diagrammed
  diagrammed → saving
  saving → saved
```

### Backend Gate Rules

```text
POST /api/ai/mistake/question-draft:
  input:  image(s) and/or text
  output: question draft (no personal inference)
  gate:   none

POST /api/ai/mistake/error-interpretation:
  input:  confirmed question draft + learner error reason + optional rejections
  output: AI interpretation proposal
  gate:   question_draft_status == "confirmed"

POST /api/ai/mistake/final-analysis:
  input:  confirmed question draft + learner error reason + accepted interpretation
  output: final analysis
  gate:   error_interpretation_status == "accepted"

POST /api/ai/mistake/diagram:
  input:  confirmed question draft + accepted interpretation + final analysis
  output: diagram strategy + render data
  gate:   error_interpretation_status == "accepted"
```

## Frontend Page Layout

`/write-mistake` should become a guided workflow.

Suggested desktop layout:

```text
Left column: staged inputs and actions
Right column: live preview / final mistake card
```

Main sections:

1. `题目来源`
   - Upload image.
   - Paste text.
   - Run `识别题目`.
   - Show OCR/visual context result.
   - Let the learner edit and confirm the draft before moving on.

2. `我的错因`
   - Single primary input: `我当时为什么错？`
   - Example placeholder: `例如：没有结合 cost 来看，只按 TTL/跳数判断了。`
   - Optional quick tags.

3. `AI 对错因的理解`
   - Button: `生成错因理解`.
   - Proposal display.
   - Buttons: `采纳` and `不采纳，重写`.
   - Rejection reason textarea appears only after rejection.

4. `生成错题卡`
   - Button: `生成解析`, disabled until accepted.
   - Button: `生成图解`, disabled until accepted.
   - Button: `保存错题`, disabled until required fields exist.

## Backend Endpoint Shape

Candidate endpoints:

- `POST /api/ai/mistake/question-draft`
  - Input: image and/or text.
  - Output: structured question draft only.

- `POST /api/ai/mistake/error-interpretation`
  - Input: question draft, learner error reason, optional rejection history.
  - Output: AI interpretation proposal.

- `POST /api/ai/mistake/final-analysis`
  - Input: question draft, learner error reason, accepted interpretation.
  - Output: final analysis fields.

- `POST /api/ai/mistake/diagram`
  - Input: question draft, accepted interpretation, final analysis.
  - Output: diagram strategy plus render data.

## Data Model Strategy

Prefer storing new staged data in existing mistake metadata first to avoid a database migration unless source inspection proves a first-class model is needed.

Suggested metadata:

```json
{
  "question_ai_draft": {},
  "question_draft_status": "draft|confirmed",
  "user_error_reason": "",
  "ai_error_interpretation": {
    "id": "",
    "version": 1
  },
  "error_interpretation_status": "draft|accepted|rejected",
  "error_interpretation_rejections": [],
  "final_analysis": {
    "accepted_interpretation_id": ""
  },
  "diagram": {
    "strategy": "svg|mermaid|canvas|qwen_image",
    "source": "",
    "image_url": "",
    "caption": "",
    "accepted_interpretation_id": "",
    "uses_error_interpretation": true
  }
}
```

Final analysis and diagram generation must reject stale inputs when the accepted interpretation changes after generation.

## Diagram Strategy

Use a router before image generation:

```text
if question_type in structured types:
  use structured diagram renderer
else if structured renderer cannot represent the visual explanation:
  use qwen-image-2.0-pro fallback
```

Structured-first examples:

- OSPF/Dijkstra: SVG network graph with highlighted path and cost sum.
- IP fragmentation: SVG packet slices with offset/MF labels.
- Tree/graph algorithm: SVG/Mermaid graph.
- Flow/process: Mermaid.
- Tables and calculations: HTML/SVG table.

Qwen image fallback examples:

- Natural-science scene explanation.
- Physical experiment setup where spatial realism matters.
- Biological/geographic schematic that is not easily structured.

## Qwen Image Fallback

Configuration:

```env
DASHSCOPE_IMAGE_MODEL=qwen-image-2.0-pro
DASHSCOPE_IMAGE_BASE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

Rules:

- The fallback prompt must include the accepted error interpretation.
- The fallback prompt must request an educational diagram, not decorative art.
- Frontend never receives DashScope credentials.
- Generated image output should be stored as a URL/path plus metadata, not as a database blob.

## Render Safety

Structured renderers should prefer a constrained JSON graph/table/packet schema that React renders into SVG elements. Raw AI-generated SVG or HTML should not be injected directly. If Mermaid is used, it must pass the existing Mermaid safety checks and fallback behavior.

## Key Guardrail

If `user_error_reason` is non-empty, AI must treat it as the source of truth. It may clarify or structure it, but it must not replace it with a guessed cause derived from the wrong option.
