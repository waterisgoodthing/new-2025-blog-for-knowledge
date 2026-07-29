# I10 任务清单

- [x] I10-01 E-01 旧系统只读盘点、哈希、来源基线（PASS：源 `blog_db:5432` revision 020 与静态索引均已核对）
- [x] I10-02 E-02 字段映射、重复、冲突、legacy alias（PARTIAL：规则和技术映射通过；owner 归属 UNKNOWN）
- [x] I10-03 E-03 `DRY_RUN_READY` 门槛（已判定 `BLOCKED`：owner/backfill 责任未明确）
- [x] I10-04 E-04 隔离 dry-run、对账、回滚、销毁（TECHNICAL PASS；不授权源库写入或切换）
- [x] I10-05 主验证与独立交叉验证（PARTIAL：新进程 hash/关系/回滚/销毁复核通过；owner 闸门仍 BLOCKED）
