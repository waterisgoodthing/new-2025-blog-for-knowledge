# Phase C Migration Gate Checklist

日期：2026-07-13  
最终状态：`Migration Gate = BLOCKED`

## 已完成

- [x] Phase A：数据库实体、API/Auth 边界、Migration Gate 审计文档已作为输入读取。
- [x] Phase B：Source of Truth design review。
- [x] Phase B：Owner Coverage Matrix。
- [x] Phase B：Authentication Boundary Design。
- [x] Phase B：Schema Ownership decision（目标为 Alembic-only，尚未实施）。
- [x] Phase B：Backup Validation Plan（设计完成，真实备份/恢复仍未证明）。
- [x] C-01：Alembic、schema inventory、data baseline 只读采集。
- [x] C-02：owner mapping readiness，明确没有 explicit owner，禁止 `created_by = owner_id` 默认推断。
- [x] C-03：schema authority audit，确认 `create_all` 与 Alembic 并存并发现 drift。
- [x] C-04：四身份 × 六实体 auth test matrix 与缺失测试清单。

## 未完成且阻断迁移

- [ ] 当前 schema/model drift 清理与三方对账：`alembic check` 当前失败。
- [ ] pg_dump validation：未执行，且不得在本阶段执行。
- [ ] restore rehearsal：未执行，当前没有 018 head 的机器证据。
- [ ] attachment checksum validation：未完成；只读目录存在不等于同批次可恢复副本。
- [ ] owner conflict resolution：未完成；10 个指定实体均无明确 owner contract。
- [ ] stable-key/content-hash mapping report：未生成逐行映射、去重和冲突队列。
- [ ] permission integration test：未完成；缺少 authenticated user/跨 owner/worker/敏感字段测试。
- [ ] polymorphic target integrity：review、attachment link、knowledge link、AI target 仍无真实 FK 的完整性证据。
- [ ] ai_run/ai_call_log correlation：`ai_call_logs` 当前没有 `ai_run_id` 或 owner，不能安全推断关联。
- [ ] application schema authority convergence：`Base.metadata.create_all` 尚未移出生产应用启动路径。
- [ ] Migration 018 restore evidence：未完成；不能在当前共享库执行 downgrade。
- [ ] compatibility window / old write path stop condition：未形成可执行切换证据。

## Gate state table

| Gate | 状态 | 证据结论 |
|---|---|---|
| `DESIGNED` | 部分完成 | Phase B 设计文档完成 |
| `BASELINED` | 部分完成 | C-01 只读 baseline 完成，但发现 drift |
| `BACKUP_READY` | 未完成 | 新鲜 dump、附件副本、hash 和可读性未证明 |
| `OWNER_READY` | 未完成 | owner 字段缺失，需逐行映射/人工冲突处理 |
| `AUTH_READY` | 未完成 | admin/anonymous 部分覆盖，owner/worker integration 缺失 |
| `DRY_RUN_READY` | 未完成 | 未做映射 dry run、恢复库演练或回滚证据 |
| `CAN_SWITCH` | 未完成 | 不能切写、切读或删除旧事实来源 |

## P0：阻断迁移的问题

1. **Schema authority 不唯一且存在 drift**：应用启动 `create_all` 与 Alembic 并存；`alembic check` 报 nullable/index 差异。
2. **Owner migration 不可安全自动化**：指定实体没有 explicit owner；admin/created_by/target 不能默认替代。
3. **恢复能力未被机器证实**：没有当前 018 head 的新鲜 dump、restore rehearsal、附件同批次 checksum 证据。
4. **权限闭环不完整**：当前是 admin-centric 实现，缺少 authenticated user owner isolation、worker contract、跨 owner integration tests。

## P1：迁移前必须解决

1. 生成逐行稳定键、内容 hash、关系完整性、owner evidence 和冲突队列。
2. 在隔离临时库完成 backup/restore、018 schema/数据/业务 smoke 验证。
3. 完成 attachments metadata/blob/checksum 同批次验证。
4. 固定 review/attachment/AI polymorphic target 的授权与存在性校验。
5. 固定 `ai_runs` 与 `ai_call_logs` 的审计关联或明确只归档不做 owner 映射。
6. 补齐 public/authenticated/admin/worker 权限 integration tests，包含 `AUTH_BYPASS` 三态矩阵。
7. 形成旧路径兼容窗口、单一写入方向、回滚与切换批准记录。

## P2：后续优化

1. 生产启动显式拒绝 `AUTH_BYPASS=true` 且 `AUTH_BYPASS_ALLOW=true`。
2. 按环境关闭或严格限制 `ENABLE_REGISTRATION`。
3. 建立可审计的 `/api/public`、`/api/me`、`/api/admin`、`/api/worker` 命名空间与 owner policy。
4. 为多态关系逐步引入可验证的关系模型或统一完整性服务。

## Stop rule

在所有 P0/P1 证据闭合、`validation.md` 记录完整并获得单独人工批准前：不得进入 Phase D，不得执行 migration、upgrade、downgrade、pg_dump、pg_restore、切写、删除旧表或修改生产配置。
