# I10 隔离 dry-run 报告

状态：`TECHNICAL PASS / GATE BLOCKED`。

`DRY_RUN_READY` 检查项：

- 来源可连接：PASS（`localhost:5432/blog_db`，源 revision 020，只读事务确认）。
- 来源计数与哈希：PASS（8 个核心表共同字段 count/hash 对账）。
- owner：BLOCKED（旧核心实体没有统一 owner_id，不能静默推断）。
- schema authority：PASS for isolated clone（Alembic 020→024，`alembic check` 通过）。
- 字段映射与冲突规则：PARTIAL（映射规则已记录，owner 冲突责任未确认）。
- 回滚与销毁：PASS（024→020→024，计数/hash/关系复核后销毁临时库）。

技术 dry-run 从源库只读导出到临时 clone，执行 020→024；8 个核心表共同字段 hash/count 全部一致，duplicate slug 为 0，Mistake→Question 与 ReviewItem→Mistake 关系完整。随后在同一 clone 执行 024→020→024 回滚重放并再次复核，最后销毁数据库。owner 闸门未通过，不能把技术 PASS 升级为生产/影子迁移授权。
