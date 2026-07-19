# Phase 1.0 Productization

## Goal

将已经技术完成的个人学习 MVP 收口为用户感知完整、可恢复、可长期使用的个人学习产品 v1.0。

本工作流分为：

1. Phase 0：冻结当前版本并建立可复核 baseline。
2. Phase 0.5：Runtime Recovery Gate。
3. Phase 1.0A：UI / Product Polish。
4. Phase 1.0B：Production Hardening。
5. Phase 1.0 RC：全量验收与剩余风险收口。
6. Phase 1.0C：Learning Feedback；属于新增业务能力，必须在 RC 后单独审批。

## Touched Domains

- `home`：移动首页导航。
- `manage`：Dashboard、管理导航、页面状态与产品文案。
- `notes`、`mistakes`、`review`：只复用已有读取合同；不改变公开读取边界。
- `auth`：只做当前版本回归与必要的错误边界收口。
- shared infrastructure：当前 revision 的备份/恢复、health、错误记录和运行手册。

## Current Status

**Phase 0 complete with PARTIAL / CONDITIONAL result. Phase 0.5 Runtime Recovery Gate and Gate A UI / Product Polish are COMPLETE / PASS. Gate B is superseded by the Schema Authority closure: `RISK-P10-008` is resolved. Schema Authority Gate, RC Gate and the approved minimal Gate C Learning Feedback scope are COMPLETE / PASS.**

Canonical baseline: [v1.0-baseline.md](../../releases/v1.0-baseline.md).

Gate A 已修改 `home`、`manage` 与 Dashboard read-only backend 边界；没有 schema、migration、最终数据库数据、持久运行配置或部署变更。Phase 0 确认的本地 Next.js chunk 500 已由 Phase 0.5 clean runtime recovery 解除；`alembic check` 的 knowledge-point 元数据漂移仍是独立风险。

## Approval Gates

- Gate 0：已批准并执行；结论为 PARTIAL / CONDITIONAL。
- Gate 0.5：已执行并完整 PASS；frontend-runtime blocker 已解除。
- Gate A：已批准并完整 PASS。
- Gate B：已执行；任务完成，结论为 CONDITIONAL PASS。
- Schema Authority Gate：**COMPLETE / PASS**。用户选择 SA-A，以现有数据库索引/分层唯一性为 `knowledge_points` 权威合同；metadata/service alignment 通过，`current`/`heads` 为 `020 (head)`，`check` 无 upgrade operations。未执行 DDL/migration，恢复边界未变化。
- RC Gate：**COMPLETE / PASS**。最终 `current`/`heads` 为 `020 (head)`，`check` 无 upgrade operations；真实学习链路、权限、附件边界、浏览器和全量命令证据已归档，临时记录已清理。
- Gate C：**COMPLETE / PASS for the approved minimal scope**。Dashboard 仅基于既有管理员 summary counts 输出确定性下一步；没有新 API、schema、持久化、AI、Analytics Lite、BKT、推荐或多用户范围。
- Security Follow-up：用户已于 2026-07-19 明确要求直接启动修复。范围限定为生产启动的 `AUTH_BYPASS` 双开关硬阻断，以及将既有 JWT/CORS 启动拒绝改为标准 `RuntimeError`；不涉及 DDL、部署、生产数据或权限模型扩展。
- Release Safety Follow-up：`RISK-P10-011` 代码与本地回归已闭环，predeploy gate 已扩展为后端/Alembic fail-closed matrix。**部署资格为 BLOCKED**：工作树仍 dirty，且生产注册与 Cloudflare invocation-log 的安全/隐私政策未决；未执行部署、push、生产数据访问或生产配置读取。
- Deployment Readiness：`DEP-P0-01` 已完成 read-only release-boundary freeze，结论为使用 future approved commit 的隔离干净 worktree；当前缺少精确发布文件集与 release commit，因此发布仍 blocked。其余 `DEP-P0-02` 至 `DEP-P1-05` 必须逐项批准；准备本身不授权任何外部写操作。

## Hard Boundaries

- 不继续扩展 AI、OCR、BKT、完整练习或多用户能力。
- 不把历史验证结果自动当作当前 revision 的证据。
- 不在原数据库执行 restore、DDL、迁移或数据清理。
- 不通过 `AUTH_BYPASS` 证明权限正确。
- 不删除旧 `/write-*` 路由或静默迁移 `Note(type="mistake")` 数据。
- 不在 Dashboard 展示 mock 数字或伪造系统健康状态。

## Main Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [audit.md](./audit.md)
- [risks.md](./risks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
- [phase-0-5-runtime-recovery-gate.md](./phase-0-5-runtime-recovery-gate.md)
- [recovery-runbook.md](./recovery-runbook.md)
- [next-requirements.md](./next-requirements.md)
- [schema-authority-compatibility-matrix.md](./schema-authority-compatibility-matrix.md)

Phase 0 完成后生成项目级发布基线：

- `docs/releases/v1.0-baseline.md`
