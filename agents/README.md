# Agent Team

Shared repository rules live in [`../AGENTS.md`](../AGENTS.md). This directory defines selective specialist collaboration; Worker files add domain judgment without overriding shared rules.

## Selective Loading

1. Always read `AGENTS.md`.
2. Read [orchestration](orchestration.md) for non-trivial ownership or multi-role work.
3. Read [permissions](permissions.md) for review, verification, blocking, or approval boundaries.
4. Read [gates](gates.md) for high-risk scope.
5. Read the Primary Owner Worker and only relevant consulted/review Workers.

Do not load all Persona files by default.

## Core Files

- [Orchestration](orchestration.md)
- [Permissions](permissions.md)
- [Decision gates](gates.md)
- [Task template](task-template.md)
- [Report template](report-template.md)

## Persona Workers

| Worker | Default responsibility |
|---|---|
| [Principal Software Architect](workers/principal-software-architect.md) | Cross-boundary architecture and evolution |
| [Principal Technical Reviewer](workers/principal-technical-reviewer.md) | Independent technical challenge and review |
| [Product Architect](workers/product-architect.md) | Product intent, acceptance, workflow semantics |
| [Senior Backend Engineer](workers/senior-backend-engineer.md) | FastAPI services and backend contracts |
| [Senior Frontend Engineer](workers/senior-frontend-engineer.md) | Next.js UI, state, accessibility, browser behavior |
| [Database Architect](workers/database-architect.md) | PostgreSQL integrity, schema, migrations |
| [Senior Data Engineer](workers/senior-data-engineer.md) | Ingestion, provenance, transformation, quality |
| [Senior Recommendation Engineer](workers/senior-recommendation-engineer.md) | Learning/review recommendation and evaluation |
| [Senior AI / LLM Engineer](workers/senior-ai-llm-engineer.md) | Model integration, structured output, AI audit |
| [Senior QA / SDET](workers/senior-qa-sdet.md) | Test strategy and independent verification |
| [Senior Security Engineer](workers/senior-security-engineer.md) | Auth, authorization, secrets, abuse boundaries |
| [Senior DevOps / SRE](workers/senior-devops-sre.md) | Build, release, runtime, observability, incidents |
| [Senior UX / Interaction Designer](workers/senior-ux-interaction-designer.md) | Information architecture and interaction quality |
| [Senior Domain Analyst](workers/senior-domain-analyst.md) | Personal-knowledge and learning-domain semantics |

“Worker” here means Persona Worker, not Cloudflare Worker or an application background worker.

