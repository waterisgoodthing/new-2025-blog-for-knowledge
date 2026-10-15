# Requirements

1. Preserve all pre-existing tracked and untracked user changes.
2. Do not modify business code, database schema/data, production configuration, deployment state, authentication settings, or remote Git state.
3. Inspect the current branch, worktree, recent history, project structure, technical documentation, manifests, environment examples, migrations, API routes, models, tests, CI/CD, deployment configuration, known issues, and TODO markers before external research.
4. Explicitly distinguish the frontend/static-blog line from the FastAPI/PostgreSQL knowledge-backend line.
5. Summarize the product goal, users, core flows, implemented capabilities, incomplete capabilities, constraints, and the technical question this research must answer.
6. Include the requested module decomposition and technical-document issue tables with the prescribed status and severity vocabularies.
7. Create a GitHub search plan for every module judged suitable for reuse, including queries, exclusions, candidate type, and validation focus.
8. For each reusable module, seek 3-8 initial candidates where the ecosystem supports it, narrow to 2-3重点 candidates, and identify one primary and one backup; document when no suitable candidate exists.
9. Verify重点 candidates from official GitHub repository evidence, including license, maintenance, release, issue, test, deployment, dependency, security, and relevant source evidence.
10. State an explicit reuse mode for every candidate: direct dependency, wrapper, local extraction, SDK, service, plugin, reference architecture/algorithm, replacement, self-build, or do not adopt.
11. Assess licenses and supply-chain risks without presenting the result as legal advice; candidates without clear licenses cannot be recommended as direct dependencies.
12. Use the requested 0-10 weighted scoring model and show the resulting total scores.
13. Include the requested combination architecture, adaptation tables, API/data/dependency compatibility, deployment/operations plan, minimum reproducible experiments, phased implementation plan, acceptance criteria, risk register, rollback plan, and evidence index.
14. Do not describe an unexecuted experiment as passed. Mark it `待验证` and supply exact verification steps.
15. Write the final report to `docs/GitHub开源项目实现方案与技术选型报告.md`, retaining valid content first if that file appears before execution.
16. Validate the report for all 30 requested sections, factual links, scoring arithmetic, evidence states, explicit recommendations, unresolved items, and one valid final gate state.
17. Record commands, checked evidence, actual file changes, and unexecuted checks in `validation.md`.

