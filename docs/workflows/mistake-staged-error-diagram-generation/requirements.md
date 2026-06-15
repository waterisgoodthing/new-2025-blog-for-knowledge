# Requirements

## Product Requirements

- **REQ-01** AI question extraction must be separate from error-reason analysis.
- **REQ-02** Uploading an image should first produce a question draft only: title, question, options, visual context, key conditions, candidate answer, knowledge points, and question type.
- **REQ-03** AI must not infer the learner's personal error reason during question extraction.
- **REQ-04** The learner must be able to review and edit the AI question draft before it becomes the source for later stages.
- **REQ-05** The learner must be able to enter their own error reason after the question draft is confirmed.
- **REQ-06** AI must generate an "error interpretation proposal" from the learner's written error reason before final analysis.
- **REQ-07** The learner must explicitly accept or reject the error interpretation proposal.
- **REQ-08** If rejected, the learner can write a rejection reason and ask AI to regenerate the interpretation.
- **REQ-09** Final analysis generation is blocked until an error interpretation proposal is accepted.
- **REQ-10** Final analysis must use the accepted error interpretation as the personalization source of truth.
- **REQ-11** AI must not override a non-empty learner error reason with option-based guessing.
- **REQ-12** The final mistake card should preserve the original image, visual context, learner error reason, accepted AI interpretation, final analysis, and generated diagram.
- **REQ-13** The system should include a "generate diagram" action for accepted mistakes.
- **REQ-14** Diagram generation should prefer deterministic structured rendering: SVG, Mermaid, canvas, or equivalent code-rendered diagrams.
- **REQ-15** Qwen image generation should be used only as a fallback when structured rendering is unsuitable.
- **REQ-16** Qwen image fallback should default to `qwen-image-2.0-pro`.
- **REQ-17** Generated diagrams must reflect the accepted error interpretation, not only the question.
- **REQ-18** Final analysis and diagram metadata must record the accepted interpretation version or ID used to generate them.
- **REQ-19** Generated structured diagrams must be sanitized or constrained so unsafe SVG/HTML cannot be injected into the page.
- **REQ-20** The implemented workflow must be verified locally and, when deployed, against the public site.

## UX Requirements

- **UX-01** `/write-mistake` should read like a workflow, not a long undifferentiated form.
- **UX-02** Primary stages should be visible: `识别题目`, `填写错因`, `AI 理解错因`, `采纳/打回`, `生成解析`, `生成图解`, `保存错题`.
- **UX-03** The page should show a preview panel for the current question draft and final mistake card.
- **UX-04** Rejection reason input should appear only after the learner clicks `不采纳，重写`.
- **UX-05** Buttons should be disabled when prerequisites are missing.
- **UX-06** The UI must clearly show which stages are complete, editable, accepted, rejected, or blocked.

## Technical Requirements

- **TECH-01** Keep frontend API calls in `src/lib/api/*`.
- **TECH-02** Backend routes remain thin; prompt orchestration and diagram strategy should live in services where practical.
- **TECH-03** Existing saved mistakes must remain readable.
- **TECH-04** New fields must be backward-compatible and optional.
- **TECH-05** No generated image or diagram should be stored as a database blob.
- **TECH-06** Store rendered diagram source/metadata and generated image URL/path separately.
- **TECH-07** Do not expose DashScope keys to the frontend.
- **TECH-08** Qwen image generation capability must be detected through backend provider status and should degrade cleanly when not configured.
- **TECH-09** Structured diagram renderers must output a restricted schema or sanitized markup.

## Acceptance Criteria

- **AC-01** Uploading a question image no longer immediately generates personalized wrong-reason analysis.
- **AC-02** If the learner writes `没有结合 cost 来看`, AI's interpretation is about cost/path selection, not guessed TTL misunderstanding.
- **AC-03** Final analysis cannot be generated until the learner accepts an AI error interpretation.
- **AC-04** Rejecting an interpretation with a reason causes the next proposal to address that rejection.
- **AC-05** A graph/network question uses structured diagram rendering rather than Qwen image generation.
- **AC-06** Qwen image fallback is reachable through backend configuration but not used for ordinary topology/algorithm diagrams.
- **AC-07** If the AI question draft is wrong, the learner can edit it before generating an error interpretation.
- **AC-08** Saved final analysis records the accepted interpretation it used.
- **AC-09** Public deployment no longer exposes the old one-shot personalized analysis path as the primary write-mistake flow.
