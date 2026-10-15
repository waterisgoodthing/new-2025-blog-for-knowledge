# Week 3 Gate — CANONICAL LEARNING

```yaml
task_id: WEEK3-GATE
objective: 用全新守卫 scratch 库证明三问可答、公共 mistake 所有权 canonical、Note↔KP canonical、边界安全
execution_mode: WORKER
routing_reason: HIGH 综合 Gate；需要独立验证与多域 gate 裁决
scope:
  included:
    - 全新守卫 scratch 库 seed（两个差异化 KP、active/archived/recent/eligible 题、due/future/mastered ReviewItems、public/private canonical Mistakes + legacy Note mistakes、032 关联 Note）
    - Gate 六问矩阵逐项证据
    - 最终验证集（前后端全套、迁移回放、build:cf + workerd preview + runtime smoke + 真实 Chromium walkthrough、git diff --check）
    - 最终独立评审（零未决 BLOCKER/HIGH）
  excluded:
    - 生产迁移/部署/cutover
    - commit/push/merge
acceptance:
  - Gate 矩阵六行全部 PASS 且证据可复现
  - 最终验证集命令全绿或如实记录
  - 独立最终评审零未决 BLOCKER/HIGH
risk: HIGH
primary_owner: main-agent
code_acceptor: main-agent
required_gates: [G0, G2, G3, G4]
user_authorization: Week 3 实现已授权；Gate 通过不授权生产/版本控制操作
plan_and_solution: |
  仅在 PR-09～PR-11 全部 PASS 后执行。seed 数据按 week3/README.md §5 清单。
  六问证据必须可溯源到 canonical 行（SQL 抽查）与真实浏览器/API 观察。
assignments:
  - agent_id: GATE-seed-verify
    profile: senior-qa-sdet
    role: verifier
    objective: 建 seed、跑六问矩阵与最终验证集，产出证据
    write_scope: ["docs/workflows/personal-learning-system-convergence/week3/evidence/**", "scripts/**"]
    depends_on: [PR-11]
    acceptance: [六问 + 最终验证集证据齐备]
    validation: [守卫 scratch + 真实浏览器 + 全套测试]
    stop_conditions: [任一 Gate 问失败]
    required_output: [gate 证据包, unresolved_issues]
  - agent_id: GATE-final-review
    profile: principal-technical-reviewer
    role: reviewer（只读）
    objective: 最终独立评审，对照全部原始证据
    write_scope: []
    depends_on: [GATE-seed-verify]
    acceptance: [GATE_PASS/GATE_FAIL；零未决 BLOCKER/HIGH]
    validation: [逐项对照原始日志]
    stop_conditions: []
    required_output: [评审结论, findings]
  - agent_id: GATE-gate-db
    profile: database-architect
    role: gate-reviewer（G2）
    objective: 迁移 030→032 回放、downgrade/re-upgrade、完整性查询裁决
    write_scope: []
    depends_on: [GATE-seed-verify]
    acceptance: [G2 PASS/FAIL]
    validation: [隔离回放]
    stop_conditions: []
    required_output: [gate 决策, evidence]
  - agent_id: GATE-gate-security
    profile: senior-security-engineer
    role: gate-reviewer（G3）
    objective: 匿名边界、DTO 泄漏、认证不变
    write_scope: []
    depends_on: [GATE-seed-verify]
    acceptance: [G3 PASS/FAIL]
    validation: [负测]
    stop_conditions: []
    required_output: [gate 决策, evidence]
stop_conditions:
  - 任一 Gate 问不 PASS
  - 最终评审存在未决 BLOCKER/HIGH
validation:
  - 见 plan_and_solution 与 week3/README.md §5 Final verification set
```
