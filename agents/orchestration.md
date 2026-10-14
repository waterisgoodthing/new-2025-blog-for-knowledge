# Worker Orchestration

## Task Routing

Start with current evidence and briefly record `SOLO` or `WORKER` and the reason. Task complexity and domain risk are separate from whether a dedicated workflow folder is needed under `AGENTS.md`.

Use `SOLO` only if all conditions hold: a clear goal, small bounded scope, low risk, straightforward verification, and no auth, data/schema, API contract, core business/AI rule, or production boundary. The main agent directly handles and verifies simple tasks; no subagent or assignment document is required.

Use `WORKER` by default for non-simple tasks: multiple dependent stages, cross-module coordination, substantial design trade-offs, complex diagnosis, or high-risk boundaries. Do not use file count or lines changed as the deciding test. Do not force artificial delegation or split a complex task to evade review. Reclassify when new uncertainty or dependencies make a simple task non-simple; obtain only missing authorization before expanded high-risk work.

## Assignment And Decision Ownership

The main agent is the single `primary_owner`. Specialist profiles describe expertise, while assignment roles describe responsibility in this task. Each Worker is a real subagent with an explicit identity and bounded assignment.

```yaml
execution_mode: WORKER
primary_owner: main-agent
assignments:
  - agent_id: <actual executor id>
    profile: senior-backend-engineer
    role: implementer
    write_scope: [<authorized paths>]
  - agent_id: <actual independent reviewer id>
    profile: principal-technical-reviewer
    role: reviewer
    write_scope: []
consulted: []
verifiers: []
required_gates: [] # derive from actual scope, never from the sample
code_acceptor: main-agent
user_approval: <existing authorization or required decision>
```

- **Main agent / Primary Owner** understands the request, makes the plan, finalizes the solution and acceptance criteria, chooses changes, delegates, reconciles evidence, requests rework, and makes final code accept. Specialist proposals inform its decision; they do not replace it.
- **Implementer** changes only assigned files within the approved solution, self-tests, and returns a diff summary and evidence. It reports necessary scope or design changes before implementing them.
- **Consulted** roles answer bounded specialist questions and propose options.
- **Reviewer** independently searches for defects, regressions, and unsupported assumptions; it recommends a disposition but cannot grant final accept.
- **Verifier** produces reproducible evidence against acceptance criteria. An implementer's tests are self-checks, not independent verification.
- **Gate reviewer** decides only the named domain gate from evidence. The main agent cannot override a failing gate with accept.
- **Project Lead / user** supplies explicit authorization where required. Existing authorization remains valid within its scope; do not ask again merely because a Worker is assigned.

## Sequence And Coordination

```text
main agent: goal/boundaries -> current evidence -> classification/risk/gates
-> plan, solution, scope and acceptance finalized within user authorization
-> bounded Worker execution and self-checks
-> independent review and necessary verification
-> main agent assesses findings -> assigned rework and affected rechecks
-> gate reconciliation -> main agent final code accept and truthful report
```

Consultation may inform the solution before implementation. In non-simple work, delegate concrete bounded execution and independent review; the main agent may perform investigation, integration, and targeted corrections, but corrections remain subject to independent review. Spawn only when a subtask can run independently alongside useful main-agent work. Stage assignments when dependencies require it; do not keep idle agents merely to fill roles.

Each assignment must state objective, included/excluded scope, write ownership (or read-only), dependencies, acceptance, validation, stop conditions, and required output. Use actual agent identities to demonstrate independence. Parallel execution is allowed only for independent work with disjoint write ownership. Shared files need a single writer or an explicit sequential handoff. Never overwrite others' dirty changes. Required serial task items and gates cannot be bypassed by parallel dispatch.

Use consultation, review, gate checks, incident handling, and evidence verification as activities within the selected execution mode, not alternatives that bypass `WORKER`. Incidents still follow detect, contain, collect evidence, recover minimally, verify, and record follow-up within authorization.

## Independence, Rework And Constraints

For non-simple results, use a real separate reviewer with no implementation ownership. A single agent changing Persona is only a perspective pass. The Technical Reviewer does not repair reviewed implementation by default. QA may add tests and fixtures; product-code repair is assigned by the main agent to an implementer. A reviewer who starts implementing cannot independently review those changes. A domain Worker that raises a block rechecks it after the fix.

Reviewer and verifier activities may share one non-implementing agent for proportionate low/medium-risk work; high-risk work keeps implementation, independent review, verification, and named gate decisions separately assigned as required by the gates. The main agent records those decisions and retains final code accept, without replacing independent evidence or required user authorization.

If tools, capacity, or higher-priority rules prevent real subagents, state the limitation. Stage work when capacity is temporary. Safe authorized investigation may continue, but label any solo assessment as a perspective pass. Do not claim independent review or final accept for non-simple work while required independent review is missing; report `PARTIAL` or `BLOCKED` as appropriate. Simple work remains `SOLO`.

Resolve conflicts through the disputed claim, domain ownership, current evidence, alternatives, and consequences. The main agent determines changes within scope; unresolved material choices or missing authorization go to the user. Seniority and role titles are not evidence.

## Evidence Verification Activity

Any relevant Worker may receive a read-only evidence verification assignment. Input: exact claims, sources, and existing artifacts. Compare current source/tests, runtime evidence, and historical descriptions; report each claim as supported, partially supported, stale, or unverified, with paths or reproducible evidence and limitations. Do not repair while verifying or treat historical completion wording as current proof. This activity does not create a new specialist or replace independent review.

## Final Accept And Status Separation

Before accept, the main agent checks the actual changes against agreed scope and acceptance, resolves actionable review findings, confirms relevant validation and required gates, and reports remaining limitations. In `SOLO`, proportionate self-checks suffice. In `WORKER`, self-checks never replace required independent review. Acceptance means the authorized code/document changes are accepted; it is not a platform merge operation.

Keep implementation, review disposition, verification, domain gate, code accept, user authorization, commit, push, merge, migration, and deployment statuses independent. One status never implies another.
