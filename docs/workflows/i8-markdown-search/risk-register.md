# I8 风险登记

| 风险 | 状态 | 处置 |
|---|---|---|
| 搜索泄露隐藏/私有内容 | OPEN | SQL 层过滤与匿名负向测试 |
| WikiLink 依赖可变路径 | OPEN | 仅用稳定 ID/显式 slug 解析 |
| 版本写入源库 | BLOCKED | 仅隔离目标 |
| 隔离目标 revision 024 与应用 readiness 不一致 | CLOSED | 新后端启动通过 readiness，current=heads=024，浏览器 API 正常 |
| 公开页面请求管理员反链/搜索接口 | CLOSED | backlinks 使用 isAdmin 条件请求；匿名/失效网络日志无管理员搜索/反链请求 |
