# Persona Worker Orchestration

## Assignment

Every non-trivial task has exactly one `primary_owner`. Other roles are explicit:

```yaml
primary_owner: senior-backend-engineer
consulted: [senior-security-engineer]
reviewers: [principal-technical-reviewer]
verifiers: [senior-qa-sdet]
required_gates: [G3_SECURITY_AUTH]
final_approver: project-lead-if-required
```

- **Owner** drives the task to its authorized terminal state.
- **Consulted** roles answer bounded specialist questions.
- **Reviewer** searches independently for defects and unsupported assumptions.
- **Verifier** produces reproducible evidence.
- **Gate reviewer** decides only the named domain gate.
- **Project Lead** supplies explicit approval where rules require it.

## Modes And Sequence

- `SOLO`: low-risk, single-domain task.
- `CONSULT`: Owner obtains bounded specialist input.
- `REVIEW`: design or implementation receives an independent pass.
- `GATE`: evidence must satisfy a high-risk boundary.
- `INCIDENT`: detect, contain, collect evidence, recover minimally, verify, and record follow-up.

Use the smallest safe mode:

```text
goal/boundaries -> current evidence -> risk/gates -> one Owner
-> consultation -> implementation/analysis -> review -> verification
-> gate reconciliation -> truthful report or approval request
```

## Independence And Conflicts

A single agent may use multiple Persona perspectives but must not call that independent review. Independent review requires a separate reviewer pass without implementation ownership, preferably a separately delegated agent when available and justified.

The Technical Reviewer does not repair reviewed implementation by default. QA may add tests and fixtures, but product-code repair returns to the Owner. A domain Worker that raises a block rechecks that domain after the fix.

Resolve disagreement through the exact disputed claim, domain ownership, current evidence, alternatives, and consequences—not seniority. Escalate material unresolved choices to the Project Lead.

## Status Separation

Keep implementation, verification, gate, approval, commit, push, migration, and deployment statuses independent. One status never implies another.

