# I9 验证

## 主验证

- 隔离 DB readiness：`PYTHONPATH=. DATABASE_URL=... alembic current` 与 `heads` 均为 `024 (head)`；`alembic check` 为 `No new upgrade operations detected`；`pg_trgm` 存在。
- 只读来源计数：`ai_runs=36`、`ai_call_logs=51`、`attempts=0`、`mistakes=3`、`review_items=3`、`admin_profiles=2`、`audit_logs=136`。
- I9 后端定向测试：`tests/test_i9_governance_routes.py` 2 passed；I7/I8/I9 路由组合 10 passed，`compileall` 通过。
- 前端定向测试：治理 API 与 AI 运行面板 4 passed；`npx tsc --noEmit` 通过；隔离 API 注入的 `npm run build` 40/40 页面生成成功。
- 浏览器主验证：新生产进程、新会话下匿名/失效会话均跳转 `/manage` 且治理 API 未被调用；管理员在 390×844、1280×800、1440×900 成功读取真实治理汇总，计数为 AI 87、学习 9、审计 147、设置 2、任务明确未提供，三尺寸无横向溢出；`/manage/ai` 读取 `/api/admin/ai/runs` 200。

## 独立交叉验证

- 以新后端进程、新浏览器上下文和新会话重新验证上述匿名、失效、管理员权限边界、来源计数和截图；治理 API 返回 200，匿名/失效返回 401。
- 独立前端组合测试确认 I9 页面行为；旧 AI 占位测试已按新产品边界更新。全量 Vitest 仍有 1 个既有 Capture 测试 `invariant expected app router to be mounted`，不属于 I9 代码，未以绿色测试掩盖。
- 后端跨模块组合中另有既有 asyncpg 跨 event-loop fixture 失败（Dashboard/FileWorkspace 测试），代码/数据库查询均未显示 I9 数据或 revision 问题；该风险保留为未解决的既有测试基础设施问题。

结论：I9 = PASS（治理代码、权限、真实来源和浏览器证据齐全；既有测试基础设施风险单独记录）。真实 provider 成功不是验收前提。

## 当前工作树独立复核（2026-07-26）

- 隔离目标重新核验为 `024 (head)`，`alembic check` clean；源库未被测试使用。
- 后端 I7/I8/I9 路由组合：10 passed。
- 前端治理/AI/设置/仪表盘/API 组合：6 test files、20 tests passed。复核先发现 `capability-state.test.tsx` 仍断言 AI/AI runs 为 `deferred`，与已实现且有治理证据的 `active` 状态不一致；已将该陈旧断言最小同步后重跑通过。
- AI 页面测试仍输出 React `act(...)` 警告；不影响断言结果，但保留为测试质量风险，不宣称零警告。
- 本次复核未重新取得浏览器截图：仓库/环境中未安装 `agent-browser`，且未发现 Playwright/Puppeteer 依赖；因此本条标为 `NOT VERIFIED`，不以构建结果替代浏览器证据。既有 I9 三尺寸独立浏览器证据仍保留，未扩大其覆盖范围。
