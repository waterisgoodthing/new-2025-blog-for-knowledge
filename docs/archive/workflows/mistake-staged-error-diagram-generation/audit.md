# Front-Back Closure Audit

Audit date: 2026-06-15.

## Scope

This audit reviews whether the planned `mistake-staged-error-diagram-generation` task closes the full learner workflow:

```text
image/text input
-> AI question extraction
-> learner correction
-> learner error reason
-> AI interpretation proposal
-> learner accept/reject loop
-> final analysis
-> diagram generation
-> save
-> detail review
-> validation/deploy evidence
```

## Verdict

The original task set covered the main idea, but was not fully closed. The audit found several gaps that could let the implementation regress into another one-shot AI flow or make the generated analysis difficult to trust later.

This audit hardens the plan by adding:

- a learner confirmation gate for the AI question draft;
- accepted interpretation ID/version binding;
- stale-output handling when accepted inputs change;
- safe structured diagram payload rules;
- Qwen image model availability verification;
- production deploy/smoke-test closure.

## Closure Matrix

| Stage | Owner | Original Status | Audit Result | Required Closure |
|---|---|---:|---|---|
| Upload image/text | Learner | Covered | Pass | Keep as source stage. |
| AI question extraction | AI | Covered | Partial | Must not infer personal wrong reason. |
| Question draft correction | Learner | Missing | Finding | Add edit/confirm gate before error interpretation. |
| Learner error reason | Learner | Covered | Pass | Use as source of truth. |
| AI error interpretation | AI | Covered | Pass | Must cite learner reason and rejection history. |
| Accept/reject proposal | Learner | Covered | Pass | Preserve rejection history. |
| Final analysis | AI | Covered | Partial | Must require accepted interpretation ID/version. |
| Diagram strategy | System | Covered | Partial | Must prefer structured renderer and record strategy reason. |
| Structured diagram safety | System | Missing | Finding | Use safe schema or sanitized renderer. |
| Qwen image fallback | Backend | Covered | Partial | Need config/status/runtime availability check. |
| Save staged card | System | Covered | Partial | Must persist accepted interpretation and diagram provenance. |
| Detail review | Learner | Covered | Pass | Must remain backward-compatible. |
| Edit existing staged record | Learner/System | Missing | Finding | Mark generated outputs stale if source changes. |
| Production verification | System | Missing | Finding | Add deploy/public smoke task when implementation ships. |

## Findings

### Finding 1: AI question draft needs a learner confirmation gate

Risk: If OCR or visual extraction is wrong, the learner may write a correct error reason against an incorrect question draft. Later analysis would be personalized but still wrong.

Fix added:

- `REQ-04`, `AC-07`
- `T1-02`, `T2-02`, `T4-03`

### Finding 2: Final analysis must bind to the accepted interpretation version

Risk: The learner can accept one interpretation, then regenerate or edit inputs. Without a stable accepted interpretation ID/version, final analysis and diagrams cannot prove which interpretation they used.

Fix added:

- `REQ-18`
- metadata fields `accepted_interpretation_id`
- `T1-05`

### Finding 3: Structured diagram rendering needs an injection-safety rule

Risk: If AI outputs raw SVG/HTML/Mermaid and the frontend renders it directly, invalid or unsafe content could break the page or introduce injection risk.

Fix added:

- `REQ-19`
- `TECH-09`
- `Render Safety` section in `design.md`
- `T1-06`, `T3-06`

### Finding 4: Qwen image fallback needs capability verification

Risk: The model name can drift or the key may not have image-generation permissions. Without a verification task, the UI could expose a fallback button that fails at runtime.

Fix added:

- `TECH-08`
- `T0-04`
- `T6-01`

### Finding 5: Edit-mode stale output behavior was missing

Risk: A saved staged mistake may be edited later. If the question draft or accepted interpretation changes, old final analysis and diagrams may remain displayed as if valid.

Fix added:

- `T5-04`

### Finding 6: Production closure was not explicit

Risk: Previous issues in this repo have come from local code being correct while the public deployment remains stale. The task needs a public verification item when implementation ships.

Fix added:

- `REQ-20`
- `AC-09`
- `T7-07`

## Remaining Open Questions

1. Whether accepted interpretation records should live only inside `ai_metadata` or become first-class backend entities if rejection history grows.
2. Whether Qwen-generated fallback images should be stored under backend uploads, Cloudflare assets, or an object store.
3. Whether diagrams should be regenerated automatically when final analysis changes, or only by explicit learner action.

## Audit Conclusion

After the added requirements/design/tasks, the task set is now closed enough to proceed to approval. The strongest remaining implementation risk is scope size: the staged workflow touches backend AI contracts, write page UI, persistence, detail rendering, diagram rendering, and production validation. Implementation should proceed by vertical slices rather than one large rewrite.
