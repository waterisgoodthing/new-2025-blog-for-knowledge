# CLEANUP 下一轮需求

状态：`PROPOSED / NOT AUTHORIZED`

## REQ-NEXT-CLEANUP-P1-01 日常库 revision 运行决策

- 来源：已知运行约束
- 问题描述：源码 readiness 期望 025，日常库按本轮边界保持 024。
- 需求描述：另行决定迁移日常库、切换运行数据库或维持当前只读历史库。
- 验收标准：在明确授权、备份和回滚门禁下验证目标运行环境；不得从本轮隔离证据直接执行迁移。
- 优先级：P1
- 关联风险：P0-AUTH RISK-02

## REQ-NEXT-CLEANUP-P2-01 测试 warning 清理

- 来源：RISK-CLEANUP-004
- 问题描述：React act、jsdom/Node warning 降低测试日志信噪比。
- 需求描述：按所属测试逐类消除项目可控 warning。
- 验收标准：相关定向测试不再输出项目可控 warning。
- 优先级：P2

## REQ-NEXT-CLEANUP-P2-02 登录页 LCP 提示

- 来源：RISK-CLEANUP-006
- 问题描述：登录头像产生 Next.js LCP eager-loading 建议。
- 需求描述：评估首屏优先级并做最小图片加载配置调整。
- 验收标准：三尺寸登录页无该 LCP warning，视觉与加载行为无回归。
- 优先级：P2
