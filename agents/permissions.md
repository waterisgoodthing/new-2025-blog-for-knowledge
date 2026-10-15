# Persona Worker Permissions

## Main Agent And Worker Boundary

The main agent is the Primary Owner and final code acceptor. It owns planning, solution finalization, modification scope, assignments, rework decisions, and acceptance within user authorization. Worker profiles grant expertise, not final decision authority. Where a profile says it owns a design or acceptance criteria, it supplies specialist proposals and evidence for the main agent to finalize; named domain gates retain their independent blocking authority.

A Worker may modify only its assigned write scope and may not enlarge authorization, delegate additional work without main-agent assignment, or grant final code accept. Existing user approval does not need repetition for an in-scope handoff. Final accept never grants commit, push, merge, migration, deployment, or production permission.

## Capabilities

- `DESIGN`: investigate and propose a design within assigned scope; the main agent finalizes the solution and any design changes.
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
| Learning Workflow Reviewer | flow critique | no by default | yes | end-to-end evidence | learning flow |
| Compatibility Retirement Engineer | transition proposal | scoped compatibility work | peer | own work | compatibility |
| API Contract Reviewer | contract critique | no by default | yes | cross-layer evidence | contract |

Every block must state `Block Type`, `Severity`, `Problem`, `Evidence`, `Impact`, `Reproduction/Detection`, `Required Action`, and `Recheck Condition`. Unsupported concern is a risk note, not a block.

The main agent cannot accept its own high-risk result without required independent review, verification, gates, and user authorization. A Reviewer cannot silently edit and approve the same implementation. Project Lead approval does not make a failing gate pass; a passing gate does not imply approval.

