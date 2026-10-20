# 设计

## 测试生命周期隔离

将 lifecycle 测试改为 pytest async 测试或等价的单一事件循环边界，不在同一测试模块中反复调用 `asyncio.run()`。测试使用独立的异步 engine/session 工厂或在同一 loop 内完成 dispose；`TestClient` 只在 context manager 内使用，并不得与跨 loop 的全局 asyncpg 连接池混用。

测试必须验证：正常 dependency commit、异常 rollback、session close，以及异常后新的查询可以继续执行。生产数据库依赖实现不因测试需要而改变。

## 独立故障矩阵

服务测试分别注入：

1. learning 查询失败，activity/storage 仍可用。
2. activity 查询失败，learning/storage 仍可用。
3. storage 查询失败/unknown，learning/activity 仍可用。

每个场景分别断言区块状态、系统健康映射、其他区块数据未被清空以及 rollback 次数；不使用一个同时失败的测试替代三个场景。

## Viewport

保留标准 `width=device-width, initial-scale=1`，移除 `maximum-scale` 与 `user-scalable=no`。移动端证据覆盖 390×844，并检查页面无横向溢出、缩放元数据允许用户缩放。

## 022 证据与文档同步

已只读确认既有目标数据库为 `022 (head)`，因此 closure-fix-2 的旧 020 阻断已更新为通过。默认 `blog_db` 仍为 020 时不执行未批准迁移；本批次证据明确区分默认运行时与 022 隔离目标，浏览器部分明确标注受控 API fixture 限制。
