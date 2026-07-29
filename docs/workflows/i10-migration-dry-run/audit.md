# I10 只读现状审计

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

## Owner 与 authority

ADR-001 确认 PostgreSQL 是事实来源，schema ownership 文档确认 Alembic 是目标 schema authority；隔离 clone 的 `alembic check` 通过。但旧 `notes`、`questions`、`mistakes`、`review_items` 等没有统一 `owner_id`，owner 覆盖矩阵要求不得把 `created_by` 或管理员角色静默当作 owner。因此业务 owner 仍为 UNKNOWN，`DRY_RUN_READY` 总门槛保持 BLOCKED。

因此：E-01 源库和静态文件盘点 PASS；E-02 映射/冲突规则已形成，但 owner 归属 UNKNOWN；不得进行源库写入或权威切换。

逐表 owner 覆盖和冲突队列见 [owner-coverage.md](owner-coverage.md)。该报告由
只读 schema/count 证据生成，未做 owner 推断。
