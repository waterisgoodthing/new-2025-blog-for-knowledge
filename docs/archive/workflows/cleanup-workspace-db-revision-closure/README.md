# CLEANUP 工作区与 DB Revision 收口

## 目标

解除 P0-AUTH 遗留的工作区 `PARTIAL`：

1. 按用户选择的方案 A 删除未跟踪 `src/app/workspace/` 原型，不建立重定向、不修复或纳入原型。
2. 只读导出日常 `localhost:5432/blog_db`，在独立临时 PostgreSQL clone 验证 Alembic `024 → 025 → 024 → 025`。
3. 完成主工作区 TypeScript、生产构建和三尺寸浏览器验收。

## 影响域

- Frontend：删除 `src/app/workspace/` 未完成原型。
- Database validation：只读日常库；允许写入并销毁临时 clone。
- Workflow：更新 P0-AUTH/R1 风险和 CLEANUP 验收记录。

## 当前状态

`CLEANUP-01～10 EXECUTED / PASS / NOT DEPLOYED`

用户已于 2026-07-30 明确批准 CLEANUP-01 至 CLEANUP-10。原型已按方案 A
可恢复删除；日常库保持 revision 024；隔离 clone 已通过
`024→025→024→025` 回放并销毁。

## 当前只读基线

- 删除目标：`src/app/workspace/`，当前仅含未跟踪 `page.tsx`。
- 目标功能已由 canonical `/manage/dashboard` 覆盖；方案 A 不保留 `/workspace` 兼容路由。
- 日常库已用只读事务核对：
  - database=`blog_db`
  - user=`blog_user`
  - host=`::1/128`
  - port=`5432`
  - revision=`024`
- migration `025_align_fresh_install_metadata.py` 的 `down_revision` 为 `024`。
- 025 涉及的 12 个 NOT NULL 列在当前日常库中均为 0 个 NULL；该事实只是升级前检查，不等于升级已执行。
- 本机具备 `pg_dump`、`pg_restore`、`initdb`、`pg_ctl`、`createdb`、`psql`、`shasum` 和系统 `trash`。

## 文档

- [需求](./requirements.md)
- [设计](./design.md)
- [任务清单](./tasks.md)
- [审计基线](./audit.md)
- [验证记录](./validation.md)
- [验收报告](./acceptance.md)
- [剩余风险](./risks.md)
- [下一轮需求](./next-requirements.md)
- [Diff 报告](./diff-report.md)
- [交接提示](./handoff-prompt.md)
