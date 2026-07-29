# Test Teardown Cleanup

> 状态：**已完成**

## 目标

修复后端数据库测试的隔离与 teardown 问题，使测试结果不依赖测试库中已有数据，也不因共享 async engine 跨事件循环清理而产生失败或资源警告。

## 所属范围

- 主要 domain：shared infrastructure / backend tests
- 关联 domain：mistakes、review、attachments
- 不修改业务 API、数据库模型、迁移或生产数据语义

## 当前进度背景

- Batch 10 已完成并关闭。
- Batch 10.1 已有条件通过并关闭。
- 两个批次的全量验证均记录了 3 个预存在测试隔离问题。
- 2026-07-05 重新定向验证：
  - `test_mistake_review_service.py`：3 passed、2 failed；
  - `test_attachment_service.py`：7 passed；
  - 两文件组合运行：10 passed、2 failed。
- 当前失败中的 `Mistake` 与 `ReviewRecord` 断言使用全表绝对计数，会受到测试库历史数据影响。
- 多个 `unittest.IsolatedAsyncioTestCase` 在每个测试的 teardown 中关闭 session 并 dispose 全局 engine，需要验证这是否是全量套件中 asyncpg 清理噪音的来源。

## 工作流文件

- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)

## 审批边界

用户已明确批准 [tasks.md](./tasks.md)，所有任务项已执行并验证。

## 完成结论

- 后端全量测试从 `170 passed, 3 failed, 3 warnings` 提升为 `173 passed, 2 warnings`。
- 3 个目标失败与 asyncpg teardown warning 已清零。
- 剩余 2 warnings 属于 AI Gateway 测试 mock，不在本任务范围内。
- 未清空共享 `blog_db`，未修改生产 engine、API、model、migration，也未进入 Batch 11。
- 无需外部 agent handoff，因此本任务不创建 `handoff-prompt.md`。
