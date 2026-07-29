# Phase A A-03 备份、恢复与迁移门槛审计

## Summary

当前 Migration Gate 状态：`BLOCKED`。

原因不是 Alembic 不可用，而是当前能验证到 migration head 和备份文档，尚不能在本轮只读审计中证明：

- 当前环境有自动备份调度。
- 当前环境存在可用的新鲜数据库 dump。
- 当前附件目录有独立可恢复副本。
- 最新备份已经在临时环境恢复并通过业务核验。
- 当前 schema 与所有 model 已完成漂移检查。

本轮未执行 migration、`pg_dump`、`pg_restore`、删除、恢复或 schema 写入。

## Evidence

### Alembic

```text
PYTHONPATH=. .venv/bin/alembic current
018 (head)
```

历史链为 `001 -> 002 -> 003 -> 1119bee5a419 -> 0ec85724afb9 -> 004 ... -> 018`，其中包含：

- `012_add_question_drafts_and_questions.py`
- `013_add_mistakes_and_review.py`
- `014_add_attachments.py`
- `015_add_capture_items.py`
- `016_add_ai_call_logs.py`
- `017_add_prompt_version.py`
- `018_add_ai_runs.py`

### Migration 风险扫描

已发现 downgrade 中存在以下操作：

- `drop_table`：questions、mistakes、review、attachments、capture、AI runs 等历史表。
- `drop_column`：notes.status、notes.ai_metadata、notes.images、folders 字段、subjects 字段等。
- `op.execute`：题目、错题、复习相关清理 SQL。
- `CASCADE`：note-tags、draft、session、taxonomy 等关联。
- `RESTRICT`：题目/错题/附件/复习对象的保护性外键。
- `SET NULL`：用户、附件、folder、session 等关系。

这些 downgrade 代码的存在不等于它们有问题，但任何回滚都必须在临时数据库和备份副本上演练，不能直接在生产库验证。

### Base metadata 行为

`backend/main.py` 的 lifespan 包含：

```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

该行为会在应用启动时尝试创建缺失表。它不是 migration，但会造成“数据库结构由 Alembic 和应用启动共同影响”的审计风险，必须在 Phase B 作为 schema ownership 问题处理。本阶段未修改或关闭它。

### Backup 文档与机器证据

`docs/backup-restore.md` 声明：

- 每日 `pg_dump -Fc`。
- `rsync` 备份 `/app/uploads/`。
- `pg_restore --no-owner --no-acl` 恢复。
- 公开 GitHub 导出与私有 `pg_dump` 分离。
- 曾记录 2026-06-03 的一次临时恢复演练，Alembic 当时为 `005`。

机器扫描结果：

- 发现 `backend/uploads/`，约 8 KB。
- 未发现仓库内业务 `backup/`、`backups/` 或 dump 文件。
- 未发现仓库内 cron、launchd、systemd 备份定义。
- 当前不能证明每日备份调度仍在运行。
- 当前不能证明 2026-06-03 之后的 `018` 数据库已完成恢复演练。

## Migration Gate

| 状态 | 当前是否满足 | 所需证据 |
|---|---|---|
| `BLOCKED` | 是 | 当前默认状态；备份和恢复能力未全部机器验证 |
| `AUDITED` | 部分 | A-01/A-02 报告完成，但仍需人工确认审计范围 |
| `BACKUP_READY` | 否 | 新鲜数据库 dump、附件副本、hash 和可读性验证 |
| `DRY_RUN_READY` | 否 | 映射、去重、冲突、回滚脚本和临时库演练 |
| `CAN_SWITCH` | 否 | dry-run、完整性、权限、公开读取和恢复验收通过 |
| `SWITCHED` | 否 | 需要单独人工批准和切换记录 |

### Gate 结论

```text
当前状态：BLOCKED
阻塞原因：Backup Ready 未证实，Dry Run 未执行，Recovery evidence 过期/不完整
允许动作：继续只读审计、设计 Phase B 门槛
禁止动作：migration、drop、切写、删除旧表、修改 GitHub 主写入逻辑
```

## Risk

| ID | 风险 | 严重程度 | 影响 | 建议 |
|---|---|---|---|---|
| A03-MIG-001 | 只有文档声明每日备份，当前机器未发现调度证据 | 高 | 数据迁移不可恢复 | Phase B 先验证真实备份调度和最近 dump |
| A03-MIG-002 | 最近记录的恢复演练对应 Alembic 005，不是当前 018 | 高 | 当前 schema/数据恢复能力未知 | 使用临时库对当前 head 做恢复演练 |
| A03-MIG-003 | `Base.metadata.create_all` 与 Alembic 并存 | 高 | schema ownership 不唯一 | Phase B 决定只由 migration 管理 schema |
| A03-MIG-004 | downgrade 含多处 drop/cascade/execute | 高 | 错误回滚可能造成数据丢失 | 禁止直接生产 downgrade，要求临时库演练 |
| A03-MIG-005 | 附件副本和本地上传目录的对应关系未证明 | 高 | 正文可恢复但图片不可恢复 | 建立附件 hash、数量和引用恢复核验 |
| A03-MIG-006 | GitHub 导出与数据库写入方向未完全确认 | 高 | 切换时可能丢失静态内容变更 | 完成 A-01 写入方向审计后再设计切换 |

## Next Step

1. Phase B 先完成真实备份、附件备份和临时恢复演练。
2. 将 `Base.metadata.create_all` 列入 schema ownership 设计决策。
3. 在 Migration Gate 达到 `DRY_RUN_READY` 前，不允许任何迁移脚本执行。
4. `CAN_SWITCH` 和 `SWITCHED` 必须另行人工批准。

