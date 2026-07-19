# Next Requirements

## REQ-P05-001 Restore a reproducible frontend runtime

- 来源：Phase 0 validation / `RISK-P10-009` / user-approved planning request.
- 问题描述：本地 Next.js route documents 返回 200，但 generated JS/CSS chunks 返回 500，导致页面空白或永久 loading。
- 需求描述：审计并恢复干净的本地前端运行环境，在不修改数据库和 migration 的前提下形成可重复启动、可浏览器验收的 runtime baseline。
- 验收标准：目标 route documents、first-party JS/CSS、关键 assets 全部为 200 或有效 304；hydration 成功；浏览器 console error 为 0；数据库 counts 不变；Alembic 保持 `020 (head)`。
- 优先级：P0。
- 关联风险：`RISK-P10-009`。

## Archive Decision

- `RISK-P10-008` Alembic metadata drift 不并入 Runtime Recovery Gate；保留给 Production Hardening/schema-authority scope。
- UI/Product Polish requirements 不在 Phase 0.5 实施；仅在 Runtime Recovery Gate PASS 后恢复可执行状态并重新审批。
