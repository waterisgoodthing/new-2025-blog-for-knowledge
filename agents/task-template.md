# Task Assignment Template

```yaml
task_id: TASK-000
objective: <observable outcome>
execution_mode: SOLO | WORKER
routing_reason: <complexity and risk, not file count>
scope: {included: [], excluded: []}
acceptance: []
risk: LOW | MEDIUM | HIGH | CRITICAL
primary_owner: main-agent
code_acceptor: main-agent
plan_and_solution: <main-agent finalized approach>
assignments:
  - agent_id: <actual id; never invent an executed assignment>
    profile: <relevant worker profile>
    role: implementer | consulted | reviewer | verifier | gate-reviewer
    objective: <bounded outcome>
    write_scope: [] # empty means read-only
    excluded_scope: []
    depends_on: []
    acceptance: []
    validation: []
    stop_conditions: []
    required_output: [changes, evidence, unresolved_issues]
required_gates: []
user_authorization: <existing approved scope or missing decision>
current_evidence: []
assumptions: []
stop_conditions: []
validation: []
```

Use only when assignment structure adds value. Simple `SOLO` work does not need a task document or assignments. Record actual identities when dispatching; planned assignments are not execution evidence. Apply workflow-folder requirements separately under `AGENTS.md`. The main agent records review findings, rework, verification, gates, and final accept without treating any of them as production or Git authorization.
