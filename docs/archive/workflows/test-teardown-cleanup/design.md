# Design：Test Teardown Cleanup

## 1. 问题定义

当前后端测试共享由 `app.database` 创建的 async engine/session factory。数据库服务测试通常采用：

1. `IsolatedAsyncioTestCase` 为每个测试创建独立事件循环；
2. `asyncSetUp()` 创建 session 并开始 transaction；
3. `asyncTearDown()` rollback、close session、dispose 全局 engine。

现有失败包含两类不同问题，不能混为一个补丁：

### A. 数据断言不隔离

`test_mistake_review_service.py` 使用全表计数：

- 期望整个 `mistakes` 表为 0；
- 期望整个 `review_records` 表为 6。

当前测试库已有历史数据，因此该文件单独运行也稳定出现 `3 != 0` 与 `9 != 6`。这些断言验证了全库状态，而不是本测试创建实体的行为。

### B. 异步资源 teardown 风险

多个测试类在每个独立事件循环结束前对共享全局 engine 调用 `dispose()`。Attachment 测试当前单独运行通过，但既有全量验证记录它在套件中出现 asyncpg 连接清理问题。需要用可重复的顺序矩阵确认：

- 是哪个前序测试留下连接或 transaction；
- warning/failure 是否与 per-test `engine.dispose()` 和独立事件循环的组合有关；
- 文件系统临时目录是否始终清理。

## 2. 设计原则

1. **测试只断言自己创建的数据。** 计数必须按本测试的 `question_id`、`review_item_id` 或其他稳定归属键限定。
2. **不以清空整库掩盖问题。** 禁止对未确认是专用测试库的数据库执行全表 `DELETE`、`TRUNCATE`、drop/create。
3. **teardown 必须幂等。** 即使 setup 或测试主体中途失败，也应关闭 session，并清理临时文件。
4. **区分 transaction 清理与 engine 生命周期。** session rollback/close 属于每测试资源；共享 engine 的 dispose 应放在经过验证的安全边界。
5. **不修改生产事务语义。** 本轮不为测试便利改动 `get_db()`、service flush/commit 策略或生产 engine 配置。
6. **先最小复现，再修改。** Attachment 问题必须先在顺序矩阵或全量测试中重新捕获；若无法复现，只做有证据的 hardening，不猜测式重构。

## 3. 拟议方案

### 3.1 Mistake/review 断言收窄

- 未确认 draft 测试按该测试创建的 `question.id` 查询 Mistake，而不是统计全表。
- review record 测试按该测试创建的 `ReviewItem.id` 统计记录，而不是统计全表。
- due queue 断言只检查本测试实体未进入队列；如队列包含历史数据，不要求整个队列为空。

这让测试可以在非空测试库中保持确定性，但不会主动删除用户或其他测试数据。

### 3.2 Teardown 生命周期收口

先为现有数据库测试建立资源清单和失败顺序矩阵，再选择最小方案：

- 保留每测试 session rollback/close；
- 将临时文件清理放入无条件执行路径；
- 仅在证明确有跨 loop pooled connection 时，调整 engine 的测试生命周期；
- 优先测试侧修复，不修改生产 engine；
- 若需要共享 helper，只抽取已经在至少两个测试类中验证一致的 teardown 模式。

#### T0 后确定的最小方案

诊断确认生产 `lifespan` 已在 shutdown 调用 `engine.dispose()`，无需修改生产 engine。全量失败的旧 loop connection 来自模块级、非 context-managed `TestClient`：

1. 将实际访问数据库的 TestClient 改为 context manager，保证 lifespan startup/shutdown 在 TestClient 自身事件循环内完整执行。
2. `IsolatedAsyncioTestCase` 继续在每测试结束时 dispose engine，避免 pooled connection 进入下一个测试的新事件循环。
3. 使用 unittest cleanup stack 注册 rollback、close、dispose 和临时目录 cleanup，使 setup 中途失败时也能执行已注册清理。
4. 暂不抽取自定义 base class/helper；unittest 原生 cleanup API 已提供足够小且清晰的生命周期接口。

### 3.3 回归验证

验证必须覆盖：

1. 两个历史失败测试单独运行；
2. mistake/review 文件重复运行至少两次；
3. attachment 文件单独运行；
4. 两文件正序与逆序组合；
5. 全量 `backend/tests/`；
6. 检查是否仍有 asyncpg、未关闭连接、不同 event loop 警告；
7. 检查测试生成的 attachment 临时文件无残留。

## 4. 非目标

- 不清理开发或生产数据库中的现有业务数据。
- 不修改 Alembic migration。
- 不修改 mistakes/review/attachment 的 API 或业务规则。
- 不顺带处理 Batch 10.1 的 Prompt Registry 偏差。
- 不进入 Batch 11。
- 不将全部 unittest 测试迁移到 pytest fixture，除非诊断证明局部修复无法安全解决且重新审批扩展范围。

## 5. 风险与控制

| 风险 | 控制 |
|---|---|
| 测试连接到非专用数据库时误删数据 | 禁止无 guard 的全表清理；优先 scoped assertions 和 transaction rollback |
| 只让当前数据库“碰巧变绿” | 重复运行与正逆序组合验证 |
| engine 生命周期修改影响生产 | engine 改动限定测试侧；若必须触及 `app.database`，先更新设计并重新审批 |
| teardown 异常遮蔽原测试失败 | 清理异常单独记录，保持原始失败可见 |
| 引入过度抽象 | 先完成局部修复，只有重复模式稳定后再抽 helper |
