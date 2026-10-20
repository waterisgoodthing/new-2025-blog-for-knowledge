# I7 风险登记

| 风险 | 状态 | 证据/处置 |
|---|---|---|
| 当前 `.env` 指向源 `blog_db` revision 020 | BLOCKED for writes | 只读；验证显式注入 55435/023 |
| 文件节点变成第二主数据 | OPEN | 复用附件/业务引用，禁止替代正式对象 |
| 匿名读取私有文件 | CLOSED for I7 | 路由依赖、匿名/失效 Playwright 401 与无公开附件 API 证据 |
| 前端全量测试存在既有 Capture failure | PARTIAL | 不与 I7 后端切片混修，待独立收口 |
| 浏览器验证工具缺失 | CLOSED | 使用 bundled Playwright 完成三尺寸新会话验证 |
