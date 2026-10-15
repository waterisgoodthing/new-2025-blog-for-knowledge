# P0-AUTH 下一轮需求

状态：`PROPOSED / NOT AUTHORIZED`

## REQ-NEXT-P0-01 `/workspace` 原型归属决策

状态：`COMPLETED BY CLEANUP / ARCHIVED`

- 来源：RISK-P0-AUTH-01
- 问题描述：原型阻断全仓类型与构建门禁。
- 需求描述：明确选择修复并纳入、删除，或正式排除并建立可审计验证策略。
- 验收标准：主工作区 `npx tsc --noEmit` 与 `npm run build` 通过。
- 优先级：P0

## REQ-NEXT-P0-02 隔离数据库 revision 对齐

状态：`ISOLATED VALIDATION COMPLETE / SOURCE MIGRATION NOT AUTHORIZED`

- 来源：RISK-P0-AUTH-02
- 问题描述：源码期望 025，默认本地数据库为 024。
- 需求描述：在隔离目标执行 readiness、upgrade/rollback 和测试，不擅自迁移日常/生产库。
- 验收标准：带 lifespan 的后端测试可在 revision 025 隔离目标运行。
- 优先级：P0

## REQ-NEXT-P2-01 测试 warning 清理

- 来源：RISK-P0-AUTH-03
- 问题描述：React act、jsdom focus timer 和 Node 弃用 warning 降低测试信噪比。
- 需求描述：逐类定位归属并消除项目可控 warning。
- 验收标准：相关定向测试不再输出项目可控 warning。
- 优先级：P2
