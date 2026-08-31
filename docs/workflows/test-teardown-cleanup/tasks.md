# Tasks：Test Teardown Cleanup

> 状态：**全部完成**
>
> 规则：只有用户明确批准本任务列表后才能执行。每完成一项，必须立即将对应 checkbox 改为 `[x]`，再开始下一项。

## T0 基线与安全边界

- [x] **T0-01** 记录当前测试数据库识别方式，确认测试命令不会连接生产数据库；不得输出或提交凭据。
  - 证据：运行时 URL 脱敏检查显示 `postgresql+asyncpg://…@localhost:5432/blog_db`，没有独立 test database 标识；因此本任务禁止 destructive cleanup，只采用 scoped assertions、transaction rollback 与资源清理。
- [x] **T0-02** 建立最小复现矩阵：mistake/review 单跑、attachment 单跑、两文件正序与逆序、mistake/review 连跑两次。
  - 证据：mistake/review 单跑稳定 2 failed；attachment 单跑 7 passed；正序与逆序均仅出现相同 2 个全表计数失败，未出现顺序相关新增失败。
- [x] **T0-03** 捕获全量测试中的首个 asyncpg/事件循环 teardown 证据，并区分 assertion failure、warning 与 cleanup exception。
  - 证据：全量测试为 170 passed、3 failed、3 warnings；attachment 首个失败是 pooled asyncpg Future 绑定到旧事件循环，随后 `engine.dispose()` 关闭旧 loop connection 时产生 `Connection._cancel was never awaited`；另两个是独立的全表计数 assertion failures。
- [x] **T0-04** 盘点所有数据库型 `IsolatedAsyncioTestCase` 的 session、transaction、engine 和临时文件生命周期。
  - 证据：5 个真实数据库 service test class 均为 per-test session/begin → rollback/close/dispose；attachment 另有 TemporaryDirectory。`test_anon_capture_access.py` 使用模块级、非 context-managed TestClient 调用公开 notes API，未触发 lifespan shutdown 的 `engine.dispose()`，是旧 loop connection 进入共享 pool 的最强证据。

## T1 收窄数据断言

- [x] **T1-01** 将“未确认 draft 不进入 review”测试改为只查询本测试 question/draft 对应的 Mistake。
  - 证据：Mistake count 增加 `Mistake.question_id == question.id` 条件；定向测试通过，不再依赖全库已有 3 条 Mistake。
- [x] **T1-02** 将 due queue 断言改为验证本测试实体未出现，不要求共享数据库的整个队列为空。
  - 证据：使用同一固定 `due_at` 比较创建未确认 draft 前后的 due item ID 集合；定向测试通过，并允许共享库存在无关队列项。
- [x] **T1-03** 将 ReviewRecord 计数限定到本测试创建的 `review_item_id`。
  - 证据：ReviewRecord count 增加 `review_item_id == item.id` 条件；原失败测试定向运行通过。
- [x] **T1-04** 增加非空数据库基线下仍能通过的回归证明，避免将历史数据清空后制造假通过。
  - 证据：运行前共享库已有 3 条 Mistake、3 条 ReviewRecord；未清库情况下完整 mistake/review 文件 5 passed。

## T2 Teardown hardening

- [x] **T2-01** 根据 T0 证据确定 engine dispose 的最小安全边界，并先在 `design.md` 记录最终选择。
  - 选择：DB TestClient 使用 lifespan context；IsolatedAsyncioTestCase 保留 per-test dispose；生产 `app.database` 不改。最终方案已写入 design.md。
- [x] **T2-02** 确保 session rollback/close 在测试主体或 setup 失败时仍执行。
  - 证据：5 个真实数据库 IsolatedAsyncioTestCase 改用 unittest cleanup stack，在 session 创建后立即注册 rollback/close/dispose；定向 35 tests passed。
- [x] **T2-03** 确保 attachment 临时目录和生成文件无条件清理。
  - 证据：TemporaryDirectory 创建后立即注册 `addCleanup(self.tmp.cleanup)`；capture 生成文件注册 async cleanup；相关定向测试通过。
- [x] **T2-04** 如两个以上测试类需要相同逻辑，增加最小测试 helper；否则保留局部实现，避免提前抽象。
  - 决策：使用 unittest 原生 cleanup stack，无需新增自定义 helper/base class。
- [x] **T2-05** 验证 teardown 不遮蔽测试主体的原始异常。
  - 证据：独立 unittest harness 中主体 assertion failure 保留为 1 failure、0 cleanup errors，同时 async/sync cleanup 均执行。
- [x] **T2-06** 将实际访问数据库的模块级 TestClient 改为 context-managed lifespan 边界，确保其事件循环关闭前 dispose engine。
  - 证据：anon capture → attachment 原失败顺序以 RuntimeWarning 作为 error 运行，9 passed。

## T3 定向与顺序回归

- [x] **T3-01** 运行 mistake/review 定向测试并记录结果。
  - 结果：`5 passed`，RuntimeWarning 作为 error，仍通过。
- [x] **T3-02** 连续两次运行 mistake/review 测试，确认结果不随历史数据增长而变化。
  - 结果：两个独立 pytest invocation 均为 `5 passed`。
- [x] **T3-03** 运行 attachment 定向测试并检查临时文件残留。
  - 结果：`7 passed`；独立 case 运行后 `TemporaryDirectory` 路径不存在。
- [x] **T3-04** 运行两文件正序与逆序组合，确认无顺序依赖。
  - 结果：正序与逆序均为 `12 passed`。
- [x] **T3-05** 检查输出中无 asyncpg connection、`different loop`、未关闭 session/connection 警告。
  - 结果：T3 全部命令以 RuntimeWarning 作为 error；无 asyncpg、different loop 或未关闭资源输出。

## T4 全量验证与收口

- [x] **T4-01** 运行 `cd backend && .venv/bin/python -m pytest tests/`。
  - 结果：`173 passed, 2 warnings`；3 个目标失败全部消失，asyncpg teardown warning 清零。
- [x] **T4-02** 如改动共享 Python 测试支持代码，运行相关 import/start check。
  - 结果：未新增共享 helper；6 个修改测试文件通过 `python -m py_compile`。
- [x] **T4-03** 更新 `validation.md`，记录命令、通过数、失败数、警告数与残留风险。
  - 已记录 173 passed、0 failed、2 个 out-of-scope AI Gateway mock warnings，以及基线对比。
- [x] **T4-04** 更新 `README.md` 状态与 handoff 结论。
  - README 已标记完成；本任务无需外部 agent handoff。
- [x] **T4-05** 最终检查 diff 仅包含获批的测试 teardown/isolation 范围。
  - 结果：`git diff --check` 通过；本任务仅修改 6 个 backend test 文件与本 workflow 文档，未触及生产代码。

## 暂停与重新审批条件

出现以下任一情况时必须停止并请求重新审批：

- 需要修改生产数据库 engine/session 行为；
- 需要执行全表删除、truncate、drop/create；
- 需要迁移全部 unittest 到 pytest fixtures；
- 发现失败根因属于业务逻辑而非测试隔离；
- 需要进入 Batch 11 或修改 API/model/migration。
