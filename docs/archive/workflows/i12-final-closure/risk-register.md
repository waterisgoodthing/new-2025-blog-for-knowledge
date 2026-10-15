# I12 风险登记

| 风险 | 状态 | 处置 |
|---|---|---|
| I11 owner/backfill gate 未收敛 | CLOSED | I10 E-03 与 I11 E-05 均 PASS |
| 源库 revision 陈旧记录 | CLOSED | 2026-08-01 只读复核为 `blog_db` revision 024；E-06 目标为 025 |
| 浏览器权限/三尺寸/键盘证据 | PASS | 同源隔离运行时的匿名、失效、非管理员、管理员矩阵及 390/1280/1440 尺寸、键盘、截图和空错误缓冲均有证据 |
| 旧 `:2025` 进程静态 chunk 500 | NON-BLOCKING HISTORICAL | 旧用户进程不作为本次 evidence source；E-06/F-01 使用独立隔离运行时完成，未停止或修改 `:2025` |
| I11 E-05 恢复/回滚证据 | CLOSED | sidecar rollback、shadow/test DB 销毁、source fingerprint 不变均已验证 |
| I11 E-06 权威切换 | CLOSED / PASS | source 025→target 025、观察、reverse delta、回切、最终重切、只读归档和清理后零 delta 均已验证 |
| 交叉验证曾误连源库 | CLOSED for this run | 已记录首次失败；停止重试，隔离目标重跑 10 passed；源库只读计数复核未变化 |
