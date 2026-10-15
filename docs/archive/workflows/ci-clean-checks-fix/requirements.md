# Requirements

1. A clean GitHub checkout must type-check `LiquidGrass` without relying on ignored `next-env.d.ts`.
2. CI must use Node 24, matching the project's declared Node engine.
3. Before backend tests execute, the disposable CI PostgreSQL database must be upgraded to the Alembic head using the test database URL.
4. The migration step must not receive production credentials or target a non-CI database.
5. Local verification must cover TypeScript, the relevant backend migration/test path where feasible, and workflow YAML validity.
6. Validation evidence must distinguish local verification from the subsequent GitHub Actions run.
