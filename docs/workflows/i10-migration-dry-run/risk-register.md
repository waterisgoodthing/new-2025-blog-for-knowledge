# I10 风险登记

| 风险 | 状态 | 处置 |
|---|---|---|
| 源库/生产误写 | CLOSED for this round | 源库仅建立只读连接；未执行 upgrade、写入或删除；migration 只作用于临时隔离 clone |
| 源数据库不可用 | CLOSED | 已定位默认实例 `localhost:5432/blog_db`，只读连接和 revision 020 已核验 |
| schema authority 未收敛 | CLOSED for clone | ADR-001/Alembic authority 与 clone `alembic check` 已核验；不代表生产切换授权 |
| 哈希/来源链断裂 | CLOSED for technical dry-run | 8 个核心表共同字段 count/hash、关系和冲突清单已独立复核 |
| owner/backfill 责任未收敛 | BLOCKED | 旧核心实体无统一 `owner_id`；不得静默把 admin/created_by 当 owner |
| 隔离 migration schema drift | CLOSED for source clone | source 020 schema restore 后 020→024 `alembic check` clean；空新库的既有 drift 仍保留为单独风险 |
| 隔离 dry-run 回滚/销毁 | CLOSED | 024→020→024、独立复核和临时库销毁均成功 |

逐表 owner 缺口、数量和解阻条件见 [owner-coverage.md](owner-coverage.md)；该风险仍为 I11 的阻断项。
