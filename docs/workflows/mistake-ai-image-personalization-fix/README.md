# AI Mistake And Prompt Management Upgrade

## Goal

Upgrade the AI learning workflow as one coherent task group with multiple small implementation phases:

- AI must collect the learner's wrong thought/error point before or alongside generation.
- "我的错误答案" should become broader user-facing wording such as "我的错误思路 / 当时答案".
- Image-based questions must preserve visual context instead of becoming text-only records.
- Image uploads should generate answer/analysis when the visible question is sufficient.
- AI analysis must not use "可能/也许/似乎/大概/推测" to bridge reasoning gaps.
- Invalid Mermaid must not break `/write-mistake`.
- General AI should use Qwen3.7 Plus with callable model ID `qwen3.7-plus`.
- DeepSeek text and DashScope vision routes should automatically fall back to `qwen3.7-plus` when unavailable.
- `/manage?tab=ai` should become a visual prompt editing and testing lab.
- Daily music should have an explicit generation/sync repair path: the public API is healthy, but daily song data is not generated and the management repair action may hit the wrong domain.

## Touched Domains

- `mistakes`: `/write-mistake` create/edit flow, AI upload/text analysis controls, saved mistake content labels.
- `notes`: mistake detail display of AI diagrams, visual context, and personalized diagnosis.
- `manage`: AI management tab UI.
- `music`: daily song public display, candidate-pool sync, and generation repair controls.
- `backend`: AI model routing, fallback, prompt/API behavior for OCR, solving, visual summaries, prompt tests, and personalized diagnosis.
- `shared infrastructure`: shared Mermaid rendering and typed AI API clients.

## Current Status

Final validation completed. Provider routing is closed, image-only AI acceptance now passes after deterministic repair, local browser checks cover AI management, write-mistake, and music diagnostics, and music production/public API evidence now shows a data/integration blocker: candidate pool is empty and NetEase API is unreachable.

### Implementation Summary

- **Backend**: Provider registry with fallback routing (DeepSeek→Qwen text, DashScope→Qwen vision), config defaults to `qwen3.7-plus`, centralized personal-context helper, deterministic-analysis repair for final answer fields, prompt registry/test/provider-status endpoints, music diagnostics endpoint.
- **Frontend**: Rebuilt AI management tab with provider cards + prompt lab + test panel, mistake form reordered with personalization context before AI, MermaidBlock hardened against syntax errors, music generate action fixed to use typed API wrapper, visual context display on detail page.
- **NOT used**: `qwen3.7-max` as multimodal fallback (HTTP 400 on image input).
- **Fix passes**: `qwen_general` provider now derives from DashScope settings when `DASHSCOPE_API_KEY` is present, independent of stale `AI_BASE_URL`/`AI_MODEL` in `.env`; polish streaming uses the same DashScope-first derivation; image/text mistake analysis repairs hedged or contradictory final fields before parsing.
- **Music conclusion**: Generate action reaches the backend and returns actionable `404 No candidates available`; daily music is blocked by empty candidate pool / unreachable NetEase API, not by frontend origin, CORS, Cloudflare, or API health.

## Model Name Verification

The user-facing name is "Qwen3.7 Plus"; the callable DashScope/OpenAI-compatible model ID is `qwen3.7-plus`.

Evidence gathered on 2026-06-14:

- Official Alibaba documentation lists `qwen3.7-plus`.
- Local runtime check with the configured DashScope key returned HTTP 200 for `qwen3.7-plus`.
- `qwen3.7-max` was also checked: text calls returned HTTP 200, but image input returned HTTP 400 (`Unexpected item type in content`). Therefore it is not suitable as the combined text+vision fallback for this workflow.

## Workflow Files

| File | Purpose | Status |
|------|---------|--------|
| `audit.md` | Root-cause review from screenshots and code inspection | Drafted |
| `requirements.md` | User-facing requirements and acceptance criteria | Drafted |
| `design.md` | Frontend, backend, routing, prompt lab, and validation design | Drafted |
| `tasks.md` | One combined implementation task list requiring approval | Completed |
| `validation.md` | Validation plan and evidence log | Completed |
| `diff-report.md` | Expected implementation scope | Drafted |
| `handoff-prompt.md` | External-agent handoff prompt if needed | Drafted |
| `assets/` | Screenshots or browser evidence | Optional; browser evidence is recorded textually in validation.md |

## Approval Gate

Per `AGENTS.md`, source implementation must not start until the user approves `tasks.md` in the conversation.
