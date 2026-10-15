# Validation：Test Teardown Cleanup

> 状态：**基线已记录，实施验证待 tasks.md 审批后执行**

## 1. 2026-07-05 基线

### 1.1 Mistake/review 定向测试

```bash
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py -q
```

结果：`3 passed, 2 failed`。

失败：

- `test_review_uses_fixed_interval_and_rejects_stale_submission`：全表 `ReviewRecord` 计数为 9，断言期望 6。
- `test_unconfirmed_draft_does_not_enter_review_queue`：全表 `Mistake` 计数为 3，断言期望 0。

### 1.2 Attachment 定向测试

```bash
cd backend && .venv/bin/python -m pytest tests/test_attachment_service.py -q
```

结果：`7 passed`。

### 1.3 两文件组合

```bash
cd backend && .venv/bin/python -m pytest \
  tests/test_mistake_review_service.py \
  tests/test_attachment_service.py -q
```

结果：`10 passed, 2 failed`；失败与 1.1 相同。

## 2. 既有全量验证证据

- Batch 10：`160 passed, 3 failed, 3 warnings`。
- Batch 10.1：`170 passed, 3 failed`。
- 两轮均记录相同两个 mistake/review 失败；attachment 失败/警告仅在全量环境出现，单独运行通过。

## 3. 当前判断

- mistake/review 两个失败可稳定复现，且直接原因是共享数据库上的全表绝对计数。
- attachment 的 teardown 问题尚未在本轮定向运行复现，实施前必须完成顺序矩阵和全量证据捕获。
- 当前未修改任何测试或业务代码。

## 4. 实施后验证

### 4.1 T0-01 数据库安全边界

运行时数据库 URL 仅输出脱敏结构：

```text
driver=postgresql+asyncpg
host=localhost
port=5432
database=blog_db
username_present=true
password_present=true
```

结论：当前测试使用本机 `blog_db`，没有独立测试库命名或 test-environment guard。不得执行全表删除、truncate 或 drop/create。本任务采用非破坏性的 scoped assertions 与资源生命周期修复。

### 4.2 T0-02 最小复现矩阵

| 顺序 | 结果 |
|---|---|
| mistake/review | 3 passed, 2 failed |
| attachment | 7 passed |
| mistake/review → attachment | 10 passed, 2 failed |
| attachment → mistake/review | 10 passed, 2 failed |

两种组合顺序均只出现相同的 `Mistake 3 != 0` 与 `ReviewRecord 9 != 6`。Attachment 定向和组合运行未出现新增失败或 warning。

说明：在同一次 pytest invocation 中重复传入同一文件会被 pytest 去重，不能作为真正的连续两轮验证；连续两轮将在 T3-02 使用两个独立 invocation 完成。

### 4.3 T0-03 全量失败分类

```bash
cd backend && .venv/bin/python -m pytest tests/ -ra
```

结果：`170 passed, 3 failed, 3 warnings`。

| 类型 | 证据 |
|---|---|
| cleanup/loop failure | Attachment 测试从 pool 取得绑定到旧 loop 的 asyncpg connection，报 `Future ... attached to a different loop` |
| cleanup warning | `engine.dispose()` 尝试在当前 loop 关闭旧 loop connection，出现 `Event loop is closed` 与 `Connection._cancel was never awaited` |
| assertion failure | Mistake 全表计数 `3 != 0` |
| assertion failure | ReviewRecord 全表计数 `9 != 6` |
| 其他预存在 warning | AI gateway 两处 AsyncMock `session.add()` coroutine 未 await；不属于本任务的 asyncpg teardown 范围 |

### 4.4 T0-04 资源生命周期盘点

- 真实数据库 `IsolatedAsyncioTestCase`：attachment、capture、mistake/review、question draft、taxonomy，共 5 个 class。
- 这些 class 均在每个测试中创建 session/begin，并在 teardown 中 rollback、close、dispose engine。
- Attachment 另创建 `TemporaryDirectory`，当前在数据库清理之后调用 `cleanup()`。
- `test_anon_capture_access.py` 创建模块级 `TestClient`，并通过公开 notes API 实际访问数据库；client 未作为 context manager 关闭。
- FastAPI lifespan 已在 shutdown 中调用 `engine.dispose()`，但只有 context-managed TestClient 才保证 lifespan 的 startup/shutdown 边界。

结论：全量 attachment failure 的最小因果链为“非 context-managed TestClient 的 DB connection → TestClient event loop 关闭 → connection 留在全局 pool → 后续 IsolatedAsyncioTestCase 在新 loop checkout”。生产 engine 无需修改。

### 4.5 T1 非空数据库回归

运行前脱敏计数：

```text
mistakes=3
review_records=3
```

未清理共享库，运行：

```bash
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py -q
```

结果：`5 passed`。证明 scoped assertions 不依赖空数据库。

### 4.6 T2 Teardown hardening

- 5 个真实数据库 `IsolatedAsyncioTestCase` 已改为 unittest cleanup stack：rollback → close → engine dispose。
- Attachment 的 `TemporaryDirectory.cleanup` 与 Capture attachment 文件清理在资源创建后立即注册。
- 未新增自定义 helper/base class，避免包装 unittest 已有生命周期机制。
- `test_anon_capture_access.py` 的 TestClient 已改为 context manager。
- 原失败顺序 `anon_capture_access → attachment_service` 使用 `-W error::RuntimeWarning` 运行：`9 passed`。
- cleanup stack harness：主体故意失败时得到 `1 failure, 0 errors`，async/sync cleanup 均执行，原始 `primary failure` 保留。

### 4.7 T3 定向与顺序回归

所有 pytest 命令均增加 `-W error::RuntimeWarning`。

| 验证 | 结果 |
|---|---|
| mistake/review 定向 | 5 passed |
| mistake/review 独立 invocation 第 1 次 | 5 passed |
| mistake/review 独立 invocation 第 2 次 | 5 passed |
| attachment 定向 | 7 passed |
| attachment 单 case 后临时目录检查 | 1 passed；目录不存在 |
| mistake/review → attachment | 12 passed |
| attachment → mistake/review | 12 passed |

输出中未出现 asyncpg connection、`different loop`、未关闭 session/connection 或 RuntimeWarning。

### 4.8 T4 全量验证

```bash
cd backend && .venv/bin/python -m pytest tests/ -ra
```

结果：**173 passed, 2 warnings in 3.91s**。

最终收口复跑：**173 passed, 2 warnings in 3.68s**，结果一致。

与基线 `170 passed, 3 failed, 3 warnings` 对比：

- attachment 的 different-loop failure 已消失；
- mistake/review 的 2 个全表计数失败已消失；
- asyncpg `Connection._cancel was never awaited` warning 已消失；
- 剩余 2 warnings 均来自 `test_ai_gateway.py` 将同步 `session.add()` 配置为 AsyncMock，属于既有 AI Gateway 测试 mock 问题，不在本任务批准范围内。

修改测试文件的语法检查：

```bash
backend/.venv/bin/python -m py_compile \
  backend/tests/test_anon_capture_access.py \
  backend/tests/test_attachment_service.py \
  backend/tests/test_capture_service.py \
  backend/tests/test_mistake_review_service.py \
  backend/tests/test_question_draft_service.py \
  backend/tests/test_taxonomy_service.py
```

结果：通过，无输出。

## 5. 验收结论

Test Teardown Cleanup 的目标已完成：

- 目标 3 个失败全部修复；
- asyncpg/事件循环 teardown warning 清零；
- 非空共享数据库下测试稳定；
- 未删除数据库数据；
- 未修改生产 engine、API、model 或 migration；
- 未进入 Batch 11。

最终 scope check：

- 修改测试：anon capture access、attachment service、capture service、mistake review service、question draft service、taxonomy service。
- 修改文档：仅 `docs/workflows/test-teardown-cleanup/`。
- `git diff --check`：通过。
