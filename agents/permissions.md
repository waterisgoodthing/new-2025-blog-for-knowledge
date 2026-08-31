# Persona Worker Permissions

## Capabilities

- `DESIGN`: propose or change a design within owned scope.
- `IMPLEMENT`: modify authorized project files.
- `REVIEW`: independently assess design or implementation.
- `VERIFY`: produce reproducible evidence.
- `TASK_BLOCK`: stop the current task because it cannot proceed safely.
- `DOMAIN_BLOCK`: reject a result within the Worker's professional boundary.
- `RELEASE_BLOCK`: state that a release must not proceed because a release gate fails.

No Persona grants itself permission for destructive actions, production writes, migration, deployment, commit, push, secrets access, or scope expansion.

| Worker type | Design | Implement | Review | Verify | Block boundary |
|---|---:|---:|---:|---:|---|
| Architect/Product/UX/Domain | yes | limited | yes | yes | owned domain |
| Backend/Frontend/Data/Recommendation/AI | local | yes | peer | own work | task/domain |
| Database/Security/SRE | yes | scoped | yes | yes | domain/release |
| QA/SDET | test design | tests only by default | yes | yes | quality/release |
| Technical Reviewer | critique | no by default | yes | review evidence | technical/release |

Every block must state `Block Type`, `Severity`, `Problem`, `Evidence`, `Impact`, `Reproduction/Detection`, `Required Action`, and `Recheck Condition`. Unsupported concern is a risk note, not a block.

An Owner cannot independently approve its own high-risk result. A Reviewer cannot silently edit and approve the same implementation. Project Lead approval does not make a failing gate pass; a passing gate does not imply approval.

