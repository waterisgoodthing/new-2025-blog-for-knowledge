# Design

The precheck has four evidence lanes:

1. Scope: identify the exact P0 assertions and their source files.
2. Source: compare management, note-detail, navigation, and authentication code with each assertion.
3. Validation: classify existing evidence as current, historical, missing, or unsafe to rerun without an isolated environment.
4. Decision: recommend no action, documentation correction, a scoped implementation task, or a separate authentication decision.

P0 implementation is not implied by a P0 precheck. In particular, auth bypass behavior and real administrator validation must remain separate from UI-only work, and tests that can write data require an isolated target and separate approval.
