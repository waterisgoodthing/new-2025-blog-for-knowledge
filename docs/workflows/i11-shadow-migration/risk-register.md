# I11 风险登记

| 风险 | 状态 | 处置 |
|---|---|---|
| I11 单独批准缺失 | CLOSED | 2026-07-26 已收到用户明确“批准并继续” |
| owner/backfill 未收敛 | CLOSED | I10 E-03 PASS；121-row manifest 与隔离 backfill 已验证 |
| 2026-07-29 简化决策反转 | CLOSED | E-05 与 2026-08-01 E-06 均有独立明确授权和边界 |
| 源库/生产误写 | CLOSED | E-05 source 不变；E-06 live 写仅发生在获批维护窗口并由备份、停写、回切和零 delta 覆盖 |
| E-05 增量/回滚合同 | CLOSED | 双扫描、幂等 replay、tombstone=0、sidecar rollback 与 target 销毁均实证 |
| 当前 123 rows 与 v1 121 rows | CLOSED | v1 不变；2 个新增 user 由 delta manifest 覆盖并标记 ARCHIVED |
| Shadow runtime 不存在 | ACCEPTED | E-05 只验证一次性 tooling，不接正式 runtime |
| Backend AI mock warnings | OPEN / NON-BLOCKING | 307 tests PASS；两条既有 `AsyncMock` RuntimeWarning 进入后续测试债务 |
| 权威切换/旧系统停写 | CLOSED / PASS | E-06 首次切换、观察、reverse delta、回切、最终重切和 Legacy 只读归档均已验证 |
