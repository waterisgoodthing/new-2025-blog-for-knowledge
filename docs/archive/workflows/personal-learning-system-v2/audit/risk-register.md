# Phase A 风险登记

## Summary

Phase A 已完成只读证据采集和三类审计报告生成，但不能宣称系统已经安全、可迁移或可切换。当前工作区在审计开始前已经 dirty；本阶段没有修改业务代码、数据库 schema、migration、配置或部署。

当前 Migration Gate：`BLOCKED`。

## Evidence

- 数据库只读查询成功；重点表记录数量和字段已记录在 [data-inventory.md](./data-inventory.md)。
- Alembic 当前版本为 `018 (head)`；详见 [migration-gate.md](./migration-gate.md)。
- 前端 route、AuthGate、API client 和直接 fetch 已扫描；详见 [access-matrix.md](./access-matrix.md)。
- 后端 router、service、schema、model、认证依赖和 `AUTH_BYPASS` 已扫描；详见 [access-matrix.md](./access-matrix.md)。
- 备份恢复文档存在，但机器上未发现当前 dump、独立 backup 目录或自动调度证据；详见 [migration-gate.md](./migration-gate.md)。
- 现有 worktree 在 Phase A 开始前已包含大量修改和未跟踪文件；本阶段未清理。

## Risk

| ID | 风险 | 严重程度 | 影响 | 建议 |
|---|---|---|---|---|
| A-RISK-001 | PostgreSQL、`notes`、`managed_content_entries`、独立题目/错题/复习表存在重复事实边界 | 高 | 迁移、查询、权限、复习状态和发布一致性 | Phase B 建立逐实体 source-of-truth 矩阵 |
| A-RISK-002 | GitHub/Markdown 推送和静态 JSON 数据流仍存在 | 高 | 双写、人工冲突、幽灵内容 | 冻结写入口方向，GitHub 仅保留导出后再切换 |
| A-RISK-003 | 当前主要内容表没有统一 `owner_id` | 高 | 私有数据隔离、恢复和多用户扩展 | Phase B 先做 owner 覆盖审计，不立即补字段 |
| A-RISK-004 | `Note` 仍同时承载普通笔记、博客、错题和复习字段 | 高 | God Object、迁移去重和业务边界 | 采用兼容读路径 + 分阶段迁移 |
| A-RISK-005 | 当前 `knowledge_points` 与目标 KnowledgeNode 不一致 | 高 | WikiLink、别名、图谱和题目关联 | 先定义 taxonomy 映射和关系边界 |
| A-RISK-006 | Today 目标架构尚未对应当前实现，且现有 recommendation/review 入口分散 | 中 | 后续入口收敛和摘要一致性 | Phase B 设计 summary provider contract |
| A-RISK-007 | 管理页面的页面级保护依赖父级 layout，未完成运行验证 | 高 | 未登录访问和无效请求 | 下一阶段执行浏览器 401/403 和网络边界验证 |
| A-RISK-008 | `AUTH_BYPASS` 双开关存在，生产拒绝策略未在本阶段验证 | 高 | 认证绕过 | Phase B 设计启动时拒绝和配置审计 |
| A-RISK-009 | `ENABLE_REGISTRATION=True` | 高 | 个人系统开放注册 | 生产配置和注册策略需单独审批 |
| A-RISK-010 | router 与 service 分层不完全一致，部分 router 直接操作 model | 中 | 事务、测试和边界维护 | Phase B 按领域逐组重构，不在审计阶段修复 |
| A-RISK-011 | 备份自动调度、当前 dump 和附件恢复未被机器验证 | 高 | 迁移不可恢复 | 先达到 `BACKUP_READY` |
| A-RISK-012 | 历史恢复演练记录对应 migration 005，不是当前 018 | 高 | 当前版本恢复风险 | 用当前数据库做临时库恢复演练 |
| A-RISK-013 | `Base.metadata.create_all` 与 Alembic 并存 | 高 | schema 变更来源不唯一 | 建立 schema ownership ADR/门槛 |
| A-RISK-014 | 现有 worktree 无 clean baseline | 中 | diff 归因和报告可信度 | 保留现状，后续分离本轮报告与既有改动 |
| A-RISK-015 | Capture 当前记录为 0 | 中 | OCR/采集真实运行能力无法由数据证明 | 记录为证据缺口，后续做受控试运行 |

## Next Step

Phase B 只允许从以下顺序开始：

1. 备份和当前 018 恢复演练设计。
2. Source-of-truth 与 owner 覆盖矩阵。
3. Auth/API 权限边界修订方案。
4. Schema ownership 和 migration dry-run 门槛。
5. 逐阶段实现任务审批。

禁止因本报告发现风险而在 Phase A 直接修复、迁移、删除、改配置或切换写源。

## 收口状态

```text
Phase A Audit Completed: yes
A-01: completed, report generated
A-02: completed, report generated
A-03: completed, report generated; Migration Gate = BLOCKED

Generated Reports: 4
Business code modified: 0
Database schema modified: 0
Migration executed: 0
Config modified: 0
Deployment modified: 0
Baseline working tree: dirty before Phase A; preserved
```

