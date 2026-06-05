# AI Skill Pipeline Knowledge Base

## Goal

Design the first version of an AI skill pipeline for the personal knowledge system, with postgraduate exam review as the primary use case.

The pipeline should connect current AI actions, future skill capabilities, structured retrieval, source-backed generation, and optional visual/content export without changing runtime code before task approval.

## Touched Domains

- `mistakes`: mistake OCR, text analysis, review advice, related mistakes.
- `notes`: structured retrieval, related notes, source references.
- `review`: weak-point summaries and review context packs.
- `blog`: citation-backed knowledge article generation.
- `share`: future social card export.
- `manage`: future AI provider and skill pipeline settings.
- Shared infrastructure: backend AI services, AI orchestration, source citation contracts.

## Current Status

- Status: planning.
- Runtime implementation: not started.
- User decisions recorded:
  - Priority is postgraduate exam review.
  - Do not create first-class `KnowledgePoint` entities in phase 1.
  - Do not use a vector database in phase 1.
  - Use structured retrieval first.
  - Allow automatic bidirectional relation suggestions.
  - AI-generated knowledge output must include citations or source references.

## Skill Installation Notes

The following OpenClaw or Claude Code skills are planned as capability references:

```bash
cd ~/.openclaw/skills

# Or Claude Code:
# cd ~/.claude/skills

git clone https://github.com/op7418/Humanizer-zh.git
git clone https://github.com/op7418/guizang-social-card-skill.git
git clone https://github.com/helloianneo/ian-xiaohei-illustrations.git
git clone https://github.com/PleasePrompto/notebooklm-skill.git
```

Known setup notes:

- `ian-xiaohei-illustrations`: after clone, `SKILL.md` may be inside a nested subdirectory. Move nested files to the skill root:

```bash
cd ian-xiaohei-illustrations
mv ian-xiaohei-illustrations/* . && rmdir ian-xiaohei-illustrations
```

- `notebooklm-skill`: first use may install a Python virtual environment and Chromium browser. Network access must be available.
- `notebooklm-mcp` is not the target skill for this workflow. Use `notebooklm-skill`.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
- [report.md](./report.md)

## Completeness Review

The report review concludes that this workflow is suitable for formal planning, but it must remain blocked from runtime implementation until `tasks.md` is approved.

The current planning documents absorb the report's required additions:

- Existing model mapping for current `Note` / `Tag` / review fields.
- API request and response contracts for context packs, weak points, and citation-backed summaries.
- Retrieval scoring rules.
- Citation output block contract.
- Validation evidence format and scope-control checks.
- Handoff constraints, forbidden changes, and stop conditions.
