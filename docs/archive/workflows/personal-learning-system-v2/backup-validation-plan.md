# Phase B：Backup Validation Plan

状态：设计完成，当前不执行 `pg_dump`、`pg_restore`、migration 或文件恢复。  
目标：在任何数据迁移/切写前证明 PostgreSQL、附件 blob、Alembic 018 结构和业务读取链可恢复。

## 验证分层

| 层 | 输入 | 必须证明 | 失败处理 |
|---|---|---|---|
| 数据库 dump | 新鲜 `pg_dump -Fc`，记录数据库标识、时间、Alembic revision、大小、SHA-256 | dump 可读取，包含目标表、约束、索引和私有数据；没有把公开 GitHub 导出当作私有数据库备份 | 标记 `BLOCKED`，不进入迁移 |
| 临时 restore | dump 恢复到隔离 PostgreSQL，使用 `pg_restore --no-owner --no-acl` 或经批准等价命令 | 恢复库能连接，Alembic revision 可识别，关键实体数量/哈希/外键一致 | 锁定 dump 与 restore 日志，禁止切换 |
| attachment restore | 同一备份批次的 `backend/uploads/` 文件副本 + attachments metadata | 每个 active attachment 的 storage key、文件存在性、size、MIME、SHA-256 一致；missing/deleted 状态不伪造为 active | 进入附件冲突队列；业务对象保持可读但不能宣称附件完整 |
| Migration 018 restore | 含 018 head 的 dump/restore 副本，必要时单独演练 017/018 | `ai_runs` 表、字段、索引、check constraint、parent_run 链、review 状态和相关审计数据可恢复 | 只在临时库继续排查，不对共享库 downgrade |
| 业务验证 | 匿名、authenticated、admin、worker 代表性 query/command | 公开过滤、owner 隔离、admin 管理和 worker 受限写入在恢复后保持一致 | 记录首个失败链路，恢复验证不通过 |

## pg_dump 验证设计

执行阶段（本轮不执行）必须固定命令版本、环境和输出目录，并避免把凭据写入日志。验证记录至少包括：

1. dump 文件名、创建时间、数据库/环境标识、Alembic revision。
2. `sha256`、文件大小、`pg_restore --list` 可读性和表清单。
3. `notes/questions/mistakes/review_items/review_records/knowledge_points/managed_content_entries/attachments/ai_runs/ai_call_logs` 的行数快照；数量差异必须解释，不以全表数量单独作为一致性证明。
4. 代表对象的稳定 ID、业务字段哈希、owner 映射状态、外键/多态 link 完整性。
5. dump 与附件副本使用同一 backup batch ID；两者任一缺失，整体 Gate 不通过。

## restore 演练

在隔离临时环境：创建空目标库，恢复 dump，运行 schema drift check，再启动只读应用验证。验证结束后销毁临时环境或按保留策略封存证据，不触碰当前工作区数据库。应记录 restore duration、首个错误、修复动作、重试结果和最终 revision。

## 附件恢复验证

恢复程序按 metadata 驱动而不是按目录文件数驱动：读取每个 `storage_key`，验证路径安全、文件存在、size、MIME 和 SHA-256；再按 `attachment_links` 验证 question/mistake target 存在且 owner 一致。不可读文件进入 `missing`，孤立文件进入待人工确认，不自动删除。

## Migration 018 恢复演练

单独保留 018 证据包：

- 018 head dump/restore 记录；
- `ai_runs` schema、index、constraint 清单；
- 运行中、成功、失败、pending/accepted/rejected review 状态的代表数据；
- `parent_run_id` 链、`attempt`、`prompt_version`、provider/model 字段核验；
- `ai_call_logs` 对应关系与敏感字段脱敏核验；
- 恢复后 `/api/admin/ai/runs` 只读查询和 admin 权限结果。

## Gate 判定

只有当数据库 dump、临时 restore、附件恢复、018 恢复、业务权限和哈希抽查全部通过，且证据已写入本 workflow 的 `validation.md`，Migration Gate 才能从 `BLOCKED` 进入下一阶段评估。任何一项未知、未执行或仅靠文档声明的结果都记为 `UNVERIFIED`，不得切写。
