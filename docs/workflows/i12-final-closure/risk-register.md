# I12 风险登记

| 风险 | 状态 | 处置 |
|---|---|---|
| I11 owner/backfill gate 未收敛 | BLOCKED | 单独继续批准已记录；E-05/E-06 仍不得执行，最终报告明确 NOT AUTHORIZED |
| 源库 revision 020 | BLOCKED | 不宣称生产 readiness |
| 浏览器匿名三尺寸/键盘证据 | PASS for anonymous | 新 production server `:3025` 的三个全新 session、截图、无溢出、登录/失败态和键盘焦点均有证据；管理员、恢复仍 NOT VERIFIED |
| 旧 `:2025` 生产进程静态 chunk 500 | OPEN | 不信任旧进程；新构建 `:3025` 静态 chunk 全部 200，旧进程问题仍需外部运行时解释 |
| 恢复/回滚证据 | BLOCKED | 依赖 I10 owner gate 与 I11 E-05/E-06，不执行源库或生产写入 |
| 交叉验证曾误连源库 | CLOSED for this run | 已记录首次失败；停止重试，隔离目标重跑 10 passed；源库只读计数复核未变化 |
