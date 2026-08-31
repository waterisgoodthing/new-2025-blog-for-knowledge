# I10 风险登记

| 风险 | 状态 | 处置 |
|---|---|---|
| 日常库测试残留 | CLOSED | 用户授权后按两个精确 ID、task type 和失败状态各删除 1 行；最终 123-row aggregate 恢复为执行前值 |
| 源数据库不可用 | CLOSED | 已定位默认实例 `localhost:5432/blog_db`，只读连接和 revision 020 已核验 |
| schema authority 未收敛 | CLOSED for clone | ADR-001/Alembic authority 与 clone `alembic check` 已核验；不代表生产切换授权 |
| 哈希/来源链断裂 | CLOSED for technical dry-run | 8 个核心表共同字段 count/hash、关系和冲突清单已独立复核 |
| owner/backfill 责任未收敛 | CLOSED | 用户批准单管理员策略；隔离 sidecar 121/121、单 owner、owner FK orphan=0 |
| 隔离 migration schema drift | CLOSED for source clone | source 020 schema restore 后 020→024 `alembic check` clean；空新库的既有 drift 仍保留为单独风险 |
| 隔离 dry-run 回滚/销毁 | CLOSED | 024→020→024、独立复核和临时库销毁均成功 |

逐表 owner 历史缺口见 [owner-coverage.md](owner-coverage.md)。Owner gate 与
日常库恢复均已通过；E-03=PASS，E-05/E-06=`READY / NOT AUTHORIZED`。
