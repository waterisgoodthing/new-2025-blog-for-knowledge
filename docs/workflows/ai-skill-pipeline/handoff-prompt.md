# Handoff Prompt: AI Skill Pipeline Knowledge Base

Use this prompt only after the task list is approved.

The project is `/Users/limengyang/2025-blog-public`. Follow `AGENTS.md` strictly. The AI skill pipeline workflow lives in `docs/workflows/ai-skill-pipeline/`.

Primary goal: build a first-stage knowledge base for postgraduate exam review using structured retrieval, relation suggestions, and citation-backed AI generation. Do not add a vector database or first-class `KnowledgePoint` entity in phase 1.

Preserve the approved pipeline map:

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

Before implementation, check `git status --short`, preserve user changes, and update `tasks.md` immediately after each completed task item.

Before writing runtime code, read:

- `AGENTS.md`
- `docs/workflows/ai-skill-pipeline/requirements.md`
- `docs/workflows/ai-skill-pipeline/design.md`
- `docs/workflows/ai-skill-pipeline/tasks.md`
- `docs/workflows/ai-skill-pipeline/validation.md`

Forbidden in phase 1:

- vector database
- embedding retrieval
- first-class `KnowledgePoint` entity
- silent relation persistence
- unapproved schema migrations
- unapproved frontend routes or pages
- runtime dependency on OpenClaw, Claude Code, Codex, or local skill folders
- AI calls inside deterministic retrieval endpoints
- silent overwrite of protected fields

Stop and report if:

- `AGENTS.md` conflicts with the task.
- Required existing models cannot be found.
- A task requires schema changes but no migration is approved.
- A task requires frontend work not approved in `tasks.md`.
- External AI provider configuration is missing for an AI-generation task.
- Tests fail for reasons outside the current task scope.

After each completed task, update `tasks.md` with:

```text
changed files
tests run
manual verification
remaining risks
scope check
```
