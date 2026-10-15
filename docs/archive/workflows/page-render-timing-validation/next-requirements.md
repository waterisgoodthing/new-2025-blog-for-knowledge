# 下一轮需求

## REQ-RT-001

- 来源：RISK-RT-001；
- 问题描述：公开 `/notes` 在匿名访问时产生一次不必要的认证失败请求；
- 需求描述：设计并验证公开页面的管理员会话探测策略，避免无意义的 401 噪音，同时保留登录态下的管理入口；
- 验收标准：匿名公开访问不产生管理员认证失败噪音；登录态仍能显示相应管理操作；后端权限边界不变；
- 优先级：P1；
- 关联风险：RISK-RT-001。
- 后续任务组：[public-session-state-optimization](../public-session-state-optimization/README.md)。

## REQ-RT-002

- 来源：RISK-RT-002；
- 问题描述：当前时效仅有开发服务器与空数据库基线；
- 需求描述：在独立任务中建立生产构建、代表性内容量和网络条件的时效验收；
- 验收标准：报告区分浏览器冷/热、服务冷/热、真实列表和网络条件，并保留可复现证据；
- 优先级：P1；
- 关联风险：RISK-RT-002。
- 后续任务组：[production-render-readiness-acceptance](../production-render-readiness-acceptance/README.md)。
