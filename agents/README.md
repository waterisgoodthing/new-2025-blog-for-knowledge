# Agent Team

Shared repository rules live in [`../AGENTS.md`](../AGENTS.md). This directory defines selective specialist collaboration; Worker files add domain judgment without overriding shared rules.

## Default Execution

Use `SOLO` for simple tasks: the goal and scope are clear, risk is low, and the result is easy to verify. Non-simple tasks default to real Worker sub-agents, with bounded assignments and independent review. Apply the classification, exception handling, and sequence in [orchestration](orchestration.md); file count alone does not determine complexity.

The main agent is the single `primary_owner`. It plans the work, finalizes the design and modification scope, assigns Workers, resolves findings and rework, and makes the final code accept decision. Accept does not authorize commit, push, merge, migration, or deployment, and cannot override a failed gate or required user approval.

A Worker profile defines domain expertise; an assignment role defines whether that agent consults, implements, reviews, or verifies this task. Workers return findings, changes, evidence, and unresolved issues to the main agent. They cannot expand scope or make the final accept decision. The implementer cannot independently review the same change. Load only the profiles relevant to assigned work; never start the whole catalog by default.

## Selective Loading

1. Always read `AGENTS.md`.
2. Read [orchestration](orchestration.md) for non-trivial ownership or multi-role work.
3. Read [permissions](permissions.md) for review, verification, blocking, or approval boundaries.
4. Read [gates](gates.md) for high-risk scope.
5. Read only the Worker profiles relevant to each assigned task; the main agent is not required to adopt a Worker profile to be Primary Owner.

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
| [Learning Workflow Reviewer](workers/learning-workflow-reviewer.md) | End-to-end learning transitions and retained data links |
| [Compatibility / Retirement Engineer](workers/compatibility-retirement-engineer.md) | Coexisting paths, consumer compatibility, and staged retirement |
| [API Contract Reviewer](workers/api-contract-reviewer.md) | Consistency across backend contracts and frontend consumers |

“Worker” here means an agent assigned a specialist profile, not Cloudflare Worker or an application background worker. Reading a profile alone does not create a sub-agent or establish independent review.

## Candidate Specialist Modes

These are optional bounded assignments using existing profiles, not additional Worker files or mandatory stages:

- **Content publication consistency** (`content-publication-reviewer`): compare draft, published, and withdrawn visibility across pages, lists, search, and static exports. Use Domain/Security/QA expertise as relevant. Read-only by default; do not publish content, deploy, or replace security review.
- **Runtime delivery verification** (`runtime-delivery-verifier`): verify actual page behavior, JS/CSS resources, route navigation, and API connectivity, with the source/build/runtime identity recorded where verifiable. Use SRE/QA expertise. Read-only by default; report delivery defects to the implementation owner and keep deployment separately authorized.

## Shared Evidence Verification Mode

Any relevant specialist may receive a read-only evidence verification assignment. For each supplied claim, distinguish current source facts, observed runtime results, historical descriptions, and unverified assumptions. Return whether the claim is supported, partially supported, outdated, or unverified, with exact evidence and limits. Do not turn verification into unsolicited repair or treat a historical “complete” statement as current proof. These claim labels do not replace the task statuses in `AGENTS.md`.
