# I10 只读现状审计

## 2026-07-31 Owner Backfill 完整性审计

用户批准单管理员策略后，I10 在从 C5 024 备份恢复的一次性数据库执行
backfill dry-run，并仅在该隔离目标升级到当前代码 head 025。带
`REFERENCES users(id)` 的 sidecar 表接收 immutable manifest 的 121 条映射；
主验证和独立 SQL 均确认 121/121、单一 canonical owner、missing/extra/hash
drift/owner conflict/owner FK orphan/七类关系 orphan 全为 0。

日常 `blog_db` 当前 revision 024，执行前只读基线为 123 条；相对 121-row
immutable snapshot 的 2 条新增用户数据未进入本轮 backfill，也未被覆盖。
完整报告见 `assets/i10-owner-backfill-integrity-audit-20260731.json`。隔离
目标与隔离测试库均已销毁；日常库最终指纹恢复到执行前基线。E-05/E-06 未执行。

## 2026-07-24 历史基线

审计时间：2026-07-24；执行前已运行 `git status --short`，保持 dirty worktree 不变。

## 可验证旧系统来源

| 来源 | 结果 |
|---|---|
| `public/blogs/index.json` | 存在，3 bytes，JSON 空数组 |
| `public/blogs/categories.json` | 存在，23 bytes，`categories` 为空数组 |
| 静态内容对象数量 | 0 |
| 文件哈希 | 见 `assets/source-manifest.json` |

## 源数据库

仓库 `.env` 实际指向默认实例 `localhost:5432/blog_db`，而不是隔离验证实例 `55435`。只读事务确认 `current_database=blog_db`、角色 `blog_user`、revision `020`。核心计数和哈希见 `assets/source-manifest.json`。

## 当时的 Owner 与 Authority

ADR-001 确认 PostgreSQL 是事实来源，schema ownership 文档确认 Alembic 是目标 schema authority；隔离 clone 的 `alembic check` 通过。但旧 `notes`、`questions`、`mistakes`、`review_items` 等没有统一 `owner_id`，owner 覆盖矩阵要求不得把 `created_by` 或管理员角色静默当作 owner。因此业务 owner 仍为 UNKNOWN，`DRY_RUN_READY` 总门槛保持 BLOCKED。

因此：E-01 源库和静态文件盘点 PASS；E-02 映射/冲突规则已形成，但 owner 归属 UNKNOWN；不得进行源库写入或权威切换。

以上 UNKNOWN/BLOCKED 是 2026-07-24 的历史结论，已由 2026-07-31 的获批
单 owner manifest 与隔离验证取代。逐表证据见
[owner-coverage.md](owner-coverage.md)。
