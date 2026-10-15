# Requirements

## Objective

Ship an open-source-safe version of the repository that no longer depends on GitHub sync as a write path and that has a clear single-source-of-truth story for active content domains.

Current extension objective: complete the repository-level open-source preparation so external contributors can understand, configure, validate, and contribute to the project with minimal reverse engineering.

## Scope

In scope:

- Remove GitHub sync write capabilities from the active application flow.
- Identify and replace UI flows that still depend on GitHub sync.
- Close the highest-risk public/private data exposure gaps that are directly affected by sync removal.
- Clarify runtime and contributor setup for open-source use.
- Record validation evidence for the new architecture.
- Migrate currently editable legacy static-content domains onto backend APIs so editing remains available after sync removal.
- Update GitHub-facing repository content into Chinese.
- Add a clear Chinese disclosure that this repository is adapted from an original open-source project.
- Add mixed Chinese/English open-source materials for contributor-facing GitHub surfaces.
- Add CI, issue templates, pull request template, environment examples, database bootstrap instructions, package metadata, and a validation command matrix.

Out of scope unless explicitly approved later:

- Broad redesign of unrelated frontend routes.
- Production secret rotation or live deployment operations.
- Data migration of user-owned production content outside the repository.
- Changing the source license or removing required upstream license notices.
- Rebranding the runtime product UI unless a later task explicitly scopes it.
- Publishing a package to npm or changing the runtime product name beyond repository metadata.
- Solving unrelated notes/AI dirty-worktree changes.
- Adding large new runtime dependencies.
- Platform-specific deployment flows or documentation.

## Functional Requirements

1. Active admin write flows must no longer require GitHub repository write access.
2. Public readers must not receive hidden, draft, or admin-only note content through the post-change public API.
3. Editable legacy static-content domains must retain edit capability through backend-owned APIs after GitHub sync removal.
4. README setup instructions must match the actual package manager and runtime expectations in the repo.
5. Open-source collaboration basics must be documented with at least contribution and security guidance.
6. The repository must have a clear documented source-of-truth model for each active content domain after migration.
7. GitHub-facing documentation must be written in Chinese for the target audience.
8. Repository documentation must explicitly state that the project is adapted from an original open-source project.
9. The upstream-origin statement must not overclaim authorship of the original project and must preserve license/attribution intent.
10. GitHub-facing contributor materials must be bilingual or mixed Chinese/English, with Chinese as the primary explanatory language and English labels where useful for external contributors.
11. CI must provide a basic pull-request health baseline for frontend and backend checks.
12. Environment examples must cover frontend/public variables and backend settings defined in `backend/app/config.py`.
13. Local setup docs must include database initialization with Alembic.
14. `package.json` must include open-source repository metadata without implying npm publication.
15. One-command setup should guide local initialization and validation, not a platform-specific deployment flow.
16. One-command setup should provide two modes: a conservative guided setup and a fuller local all-in-one setup.
17. If required tools are missing, the setup flow must detect them first and ask the user for explicit permission before attempting any system-level installation.
18. One-command setup must include an AI configuration confirmation step that can be skipped safely.
19. AI setup should support multiple common OpenAI-compatible providers plus a custom provider option, without hard-coding the runtime architecture to a single vendor.
20. Provider presets whose native APIs are not supported by the current runtime must be mapped through the custom OpenAI-compatible config path or clearly marked as unavailable until an adapter is implemented.
21. One-command setup/check scripts must have a non-destructive dry-run or check-only path for validation.
22. AI setup must distinguish model purpose/capability: general assistant, text generation/analysis, OCR/vision recognition, and image generation.

## Non-Functional Requirements

1. Changes should preserve existing admin workflows by migrating them to backend architecture rather than dropping edit support.
2. The new design should reduce accidental public exposure of private learning content.
3. The implementation should keep the codebase easier to understand, not replace GitHub sync with another hidden dual-write path.
4. Validation must distinguish verified runtime behavior from environment-blocked checks.
5. Documentation changes should be concise enough for GitHub visitors to understand the project quickly.
6. Chinese documentation should keep technical terms consistent with the existing architecture.
7. Bilingual content should stay concise and avoid duplicating every sentence when a mixed heading or short English alias is enough.
8. CI should avoid requiring production secrets or live external services.
9. New templates should guide contributors without creating bureaucratic overhead for a personal project.
10. Open-source setup should stay deployment-target neutral.
11. Setup scripts should be transparent and reversible: show planned actions before installing tools or changing configuration.
12. System package installation should be opt-in and should prefer documented commands over silent privileged changes.
13. AI setup should never print full API keys after input and should not require keys for local non-AI development.
14. Provider presets should be treated as setup convenience only; users must be able to override base URL and model.
15. Automatic installation support should be bounded to documented operating systems and package managers; unsupported environments should receive manual instructions instead of best-effort mutation.
16. Docker-backed database setup should be optional. If no compose file is added in this phase, setup may only detect Docker and print the exact manual/next command path.
17. AI capability labels must match current runtime behavior and must not imply that image generation and image recognition use the same endpoint.

## Decisions Needed During Implementation

1. Whether startup `create_all` remains temporarily tolerated during this task or is included in scope for final release cleanup.
2. How much cross-domain normalization is acceptable in one round versus route-by-route API migration with shared primitives underneath.
3. Whether the home/site settings domain should land in a generic config API or a more explicit site-settings contract.
4. Exact upstream project name, URL, and license if the repository does not already contain enough evidence to identify them.
5. Whether GitHub issue/PR templates or repository metadata should also be Chinese in this phase.
6. Whether to include Docker Compose in this round or keep it as a follow-up.
7. Whether package metadata should use the current Git remote URL as the repository URL.
8. Which operating systems and package managers the setup script should offer automatic prerequisite installation for.
9. Whether provider presets beyond the current `AI_*`, `DASHSCOPE_*`, and `DEEPSEEK_*` env groups should remain setup-only mappings or trigger runtime config expansion.

## Acceptance Criteria

1. No active UI action in the supported management flow calls the GitHub sync API path.
2. Backend GitHub sync endpoints and service code are removed or explicitly retired from the app surface.
3. Public note APIs enforce a safe anonymous-read policy.
4. Legacy editable static domains continue to support save/edit through backend APIs rather than GitHub sync.
5. Documentation explains how to run the project locally without GitHub sync secrets.
6. Validation notes record TypeScript, targeted backend checks, and route-level behavior relevant to the removed sync flow.
7. README, contribution guidance, and security guidance are Chinese or have Chinese as the primary language.
8. README contains a visible "来源与致谢" or equivalent section stating the project is adapted from an original open-source project.
9. Validation notes record the final changed documentation files and any attribution limits, such as unknown upstream URL.
10. `.github/workflows/` contains a basic CI workflow for repository validation.
11. `.github/ISSUE_TEMPLATE/` and a pull request template exist and use mixed Chinese/English guidance.
12. Root `.env.example` exists and backend `.env.example` covers documented settings.
13. README includes database bootstrap and validation commands.
14. `package.json` includes license and repository metadata while preserving the chosen package manager.
15. `npm run init`, `npm run setup`, and `npm run check` exist or are explicitly documented with implemented scripts.
16. Setup provides a check-only/dry-run path that can be validated without changing system state.
17. AI setup can be skipped, masks secrets, writes only local env files, and labels gateway/adapter requirements for providers not supported natively.
18. Admin setup generates `JWT_SECRET_KEY`, handles registration/passkey keys according to user choices, and never logs full secrets in summaries.
19. Any system-level installation attempt is preceded by a clear action summary and explicit user confirmation.
20. Final validation records script dry-run/check results, README/template inspection, secret-safety review, and any unsupported environment limits.
21. AI setup UI/docs show separate choices for general assistant, text generation/analysis, OCR/vision recognition, and image generation, with their env mappings.
