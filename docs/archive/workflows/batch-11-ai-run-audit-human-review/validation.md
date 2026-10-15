# Validation：Batch 11 AI Run 审计与人工流转

> 状态：**用户验收通过并关闭**
>
> 日期：2026-07-05

## 当前证据

- 当前 `AiCallLog` 只记录调用完成后的 Gateway 元数据，不表达完整生命周期。
- 当前 `/api/ai/call-logs` 和 `/stats` 均受 `get_current_admin` 保护。
- 当前 `/manage/ai` 使用旧 call-log API，展示统计与调用表格。
- 当前已有 `audit_logs` 与 `audit_action()`，可复用记录人工 Run 决策。
- 目标架构把 `ai_runs` 定义为管理员私有、可重试、可校验和可追踪对象。
- Batch 9 风险记录明确把流式日志完整性和完整审计留给 Batch 11。

## 自动化验证

### Migration

```text
PYTHONPATH=. .venv/bin/alembic upgrade head
PYTHONPATH=. .venv/bin/alembic downgrade -1
PYTHONPATH=. .venv/bin/alembic upgrade head
PYTHONPATH=. .venv/bin/alembic current
```

结果：018 upgrade、018 -> 017 downgrade、017 -> 018 re-upgrade 均通过；
最终为 `018 (head)`。018 只创建/删除 `ai_runs`，不读取、修改、rename、drop
或重建 `ai_call_logs`。

### Backend

```text
cd backend && .venv/bin/python -m pytest tests/ -ra
```

结果：**207 passed, 2 warnings in 3.23s**。两个 warning 是既有
`test_ai_gateway.py` AsyncMock RuntimeWarning，不影响断言。

Batch 11 专项测试最终结果：**19 passed**。

### Frontend 与 build

```text
npx tsc --noEmit
npm run build
git diff --check
```

结果：全部通过；Next build 成功生成 `/manage/ai`。build 输出包含既有
baseline-browser-mapping 过期提示和 Node `module.register()` deprecation warning。

### 禁止项

- 018 与 Batch 11 代码未新增 cost、routing CRUD、model profile 或 Prompt 后台。
- 未发现对 `ai_call_logs` 的 drop/rename。
- 旧 `/api/ai/call-logs` 与 `/stats` 合同测试通过。
- 新 `/api/admin/ai/runs` 匿名 route 测试返回 401。
- 列表与详情 DTO 均不返回 replay input 或 input summary；详情 output 递归清理
  credential、storage key、绝对路径和 data URL。

## 浏览器验证

- 既有 2025 dev 端口因旧进程/构建产物失配显示客户端异常，未计为通过。
- 隔离启动 2026 dev 端口后，`/manage/ai` 正常加载并把匿名用户引导到管理登录页；
  没有展示 Run 或技术日志数据。
- 当前浏览器没有管理员会话，因此已登录后的 Run 列表、详情、retry 与 decision
  交互未做视觉验收。该项记录为剩余风险，不能写成已验证。
- 本轮没有使用 `AUTH_BYPASS` 绕过权限。

## Stream 生命周期缺口

`ai_gateway.call_stream()` 当前仍是非流式 wrapper，可记录 Run；但
`/api/ai/analyze-stream` 与 `/api/ai/analyze-text-stream` 的生成器路径没有完整接入
Run start/finalize。客户端断开、生成器异常和最终 parser 状态仍可能缺失业务 Run。
本批不得把同步 Gateway Run 接入表述为“完整流式审计已完成”。

## 当前结论

Batch 11 migration、后端、权限合同、TSC、build 与匿名浏览器边界验证通过。
已登录浏览器交互和真实 provider 端到端没有验证，相关结论保持 `not verified`。
未进入 Batch 12。

## 用户验收确认

用户确认：

- P0-01 至 P1-05 全部完成。
- 专项测试 19 passed。
- 后端全量 207 passed / 0 failed / 2 warnings。
- TSC 与 build 通过。
- 018 migration 未触碰 `ai_call_logs`。
- 旧 call-log 端点和表保留，双轨边界成立。
- AI 输出不会直接写正式实体；人工接受只记录决策，不自动 apply。
- 14 条批准硬约束全部遵守，未进入 Batch 12。

三项 `not verified` 风险已诚实记录，用户明确确认其不阻塞 Batch 11 验收。
最终结论：**Batch 11 通过并关闭**。

## Browser Verification Patch（阻断）

> 日期：2026-07-05
>
> 状态：**P1 阻断，已暂停，未修改代码**

### 目标路由复现

访问：

```text
http://127.0.0.1:2025/manage/ai/runs
```

浏览器结果：

- URL 保持 `/manage/ai/runs`。
- 页面标题：`404: This page could not be found.`
- 页面显示 Next.js 404。

结论：验收范围要求的独立 Run 页面不存在。当前实现只有
`/manage/ai` 内嵌的 `AiRunsPanel`，因此 `/manage/ai` 与
`/manage/ai/runs` 的入口关系并不成立。

### 本轮已验证

| 项目 | 结果 |
|---|---|
| `/manage/ai/runs` 可访问 | **失败（P1）**：404 |
| 目标页面不泄露 Run 数据 | 通过：404 页面未展示 Run 数据 |
| 原则上不修改代码 | 通过 |
| 不进入 Batch 12 | 通过 |

### 因阻断未继续验证

- 管理员登录后的 Run 列表加载。
- 筛选、分页和详情。
- 接受/拒绝确认、loading、成功和失败反馈。
- revision 冲突 409 提示。
- retry 无 replay input 的 409 提示。
- 详情敏感字段的浏览器级核对。
- 公开页面是否发起 Run API 请求。

以上项目不能因 `/manage/ai` 内存在相似组件而自动判定通过。按照本轮停止规则，
发现 P1 阻断后已暂停，等待用户决定是新增 `/manage/ai/runs`，还是把验收目标正式
改为 `/manage/ai`。

### Workflow 路径说明

用户指令中的 `docs/workflows/batch-11-ai-run-audit-review/` 不存在。为遵守仓库
“继续既有任务时复用原目录，不创建近似平行目录”的规则，本证据写入现有 canonical
目录 `docs/workflows/batch-11-ai-run-audit-human-review/`。

## Browser Verification Patch：临时管理员补证

> 日期：2026-07-06
>
> 状态：**部分通过；两个 P1 与两项未验证**

### 验证环境

- 创建一次性管理员：`codex-b11-browser`。
- 未使用 `AUTH_BYPASS`。
- 既有 2025/8000 进程版本失配：前端 `/manage/ai` 客户端异常，旧后端 Run API
  返回 404；不计入当前代码验收。
- 隔离启动当前代码：
  - frontend：`http://localhost:3001`
  - backend：`http://127.0.0.1:8001`
- 验收结束后已禁用临时管理员，并停止 3001/8001 隔离进程。

### 结果矩阵

| 验证项 | 结果 | 证据 |
|---|---|---|
| 管理员登录 | 通过 | 密码登录后管理工作区显示，随后可访问 `/manage/ai` |
| `/manage/ai/runs` | **P1 失败** | 独立路由返回 Next.js 404 |
| `/manage/ai` Run 列表 | 通过 | 当前后端返回 200，页面显示 Run 行 |
| 状态筛选 | 通过 | 选择 `failed` 后请求 `GET /api/admin/ai/runs?status=failed&limit=30` 返回 200 |
| 分页 | **P1 失败** | Run 列表固定请求 `limit=30`，页面无上一页/下一页或 offset 控件 |
| 详情查看 | 通过 | 点击 Run 后详情 API 返回 200，右侧显示 task、attempt、provider、Prompt version 与受控 output |
| retry 无 replay input | 通过 | `POST .../retry` 返回 409；前端显示 `AI Run has no replay input` |
| 接受/拒绝反馈 | 未验证 | 当前数据库没有 `review_status=pending` Run；未伪造业务数据 |
| revision 冲突 409 | 未验证 | 同上，没有可安全执行的 pending fixture |
| 匿名 Run API | 通过 | 无 cookie `GET /api/admin/ai/runs` 返回 401 |
| 页面敏感字段 | 通过（当前样本） | Run 区域未出现 `replay_input`、`storage_key`、`api_key`、`authorization`、`cookie`、`secret`、`token` 或绝对路径 |
| 公开页面 Run API 请求 | 通过 | 依次访问 `/`、`/blog`、`/notes`；隔离后端日志未出现 `/api/admin/ai/runs` |
| 入口关系 | **P1 失败** | 侧栏只有 `/manage/ai`，没有 `/manage/ai/runs`；目标独立路由 404 |

### 清理

```text
python -m app.cli disable-temp-admin --username codex-b11-browser
```

结果：`Temporary admin account disabled: codex-b11-browser`。

### Browser Patch 结论

- RISK-B11-001 **未关闭**。
- 已登录列表、筛选、详情、retry 409、匿名保护与当前样本敏感字段验证已补齐。
- `/manage/ai/runs` 缺失与分页缺失是 P1。
- 接受/拒绝和 revision 409 因没有 pending fixture 保持 `not verified`。
- 按用户规则未修改代码，等待是否批准 P1 修复或修改验收目标。

## Browser Fix Patch（通过）

> 日期：2026-07-06
>
> 状态：**通过；RISK-B11-001 已关闭**

### 修复与合同

- 新增 canonical 管理页 `/manage/ai/runs`；`/manage/ai` 保留技术调用日志，并提供清晰的
  “打开 Run 审计页”入口。
- Run 列表 API 返回兼容分页 envelope：`items`、`total`、`limit`、`offset`。
- 前端每页 20 条，支持上一页/下一页；状态或人工审核筛选变化后回到第一页。
- 列表 envelope 仍使用 `AiRunListItem`，不含 output、replay input 或 input summary。
- 人工决定使用页面内确认面板；拒绝支持最长 1000 字 note；提交期间禁用相关按钮并显示
  `提交中…`。
- decision 409 显示：`该 Run 已被更新，请刷新后重试。`
- retry 无 replay input 的 409 显示：`无法重试：该 Run 缺少 replay input。`

### 浏览器证据

隔离环境：

```text
frontend: http://localhost:3001
backend:  http://127.0.0.1:8001
temporary admin: codex-b11-fix
```

使用现有 service 创建 23 条 `target_type=browser_fixture`、`review_status=pending` 的
可清理 Run；未调用真实 provider。

| 验证项 | 结果 | 证据 |
|---|---|---|
| `/manage/ai/runs` | 通过 | 页面标题为“AI Run 审计”，列表 API 200；production build route 表含该路由 |
| 分页 | 通过 | 第一页 `1–20 / 27`；下一页 `21–27 / 27`；上一页恢复可用 |
| 筛选重置 | 通过 | 在第二页切换 `review_status=pending` 后显示 `1–20 / 23` |
| 详情安全 | 通过 | fixture 输入含敏感键；渲染 output 只保留 `fixture_label/result/nested.safe`，禁词匹配为空 |
| accept | 通过 | 显示明确确认文案；decision POST 200；页面 toast `已接受该输出` |
| reject | 通过 | note `浏览器验收：输出不采用` 可输入；确认后 POST 200；toast `已拒绝该输出` |
| stale revision | 通过 | 页面保留 revision 0，另一 reviewer 更新为 revision 1；旧 revision POST 返回 409；页面显示明确冲突提示 |
| 匿名页面 | 通过 | 无 localhost cookie 的 `127.0.0.1` 访问被重定向到 `/manage` 登录页 |
| 匿名 API | 通过 | 无 cookie `GET /api/admin/ai/runs` 返回 401 `Not authenticated` |
| 公开页面 | 通过 | 依次访问 `/`、`/blog`、`/notes`；后端日志没有 Run API 请求 |

浏览器过程中发现 decision 成功更新后，数据库生成的 `updated_at` 在响应序列化时被异步
过期，导致 500。已在 `decide_ai_run` 的审计写入后 refresh Run，并新增
`test_decision_uses_revision_and_writes_safe_audit` 中的 refresh 回归断言。修复后 accept、
reject 均为 200，stale revision 为 409。

### 最终命令

```text
cd backend && .venv/bin/python -m pytest tests/ -ra
209 passed, 2 warnings

npx tsc --noEmit
通过

npm run build
通过；包含 ○ /manage/ai/runs

git diff --check
通过
```

两条 warning 为既有 `test_ai_gateway.py` AsyncMock RuntimeWarning；本补丁未改 Gateway。

### 清理与结论

- 23 条 browser fixture 及其 audit fixture 已删除。
- 临时管理员 `codex-b11-fix` 已禁用。
- 3001/8001 隔离服务已停止。
- RISK-B11-005、RISK-B11-006 已关闭。
- RISK-B11-001 已关闭。
- 未做真实 provider 验证，未改 stream，未进入 Batch 12。

## RISK-B11-004：真实 provider 端到端补证（2026-07-06）

### 范围与安全边界

- 任务：已注册同步任务 `netease_reason`。
- 输入：虚构曲目信息，不含个人数据；输出正文不写入本验证文档。
- Provider 凭据只由 `backend/.env` 加载；补证输出不显示密钥值。
- `max_tokens=80`，只执行一次真实调用。
- 本轮不验证 SSE、不修改代码、不进入 Batch 12。

### 时间窗与 Gateway 结果

```text
marker: risk-b11-004-20260706T120559Z
UTC window: 2026-07-06T12:05:59.715429Z -> 2026-07-06T12:06:32.707501Z
gateway success: true
provider/model: qwen_general / qwen3.7-plus
latency_ms: 32962
fallback_used: true
attempt_count: 2
output_type: str
output_sha256 prefix: ba7217faeb5e
```

首选 provider 的真实尝试未成功，Gateway 自动 fallback 到 `qwen_general` 并成功。
此结果同时覆盖真实 provider 与真实 fallback 路径；不据此评价模型内容质量。

### 双轨落库证据

调用前后按 `task_type=netease_reason` 计数：

```text
ai_runs delta: +1
ai_call_logs delta: +1
```

使用唯一 marker 和调用开始时间查询得到且仅得到以下两条记录：

| 字段 | ai_runs | ai_call_logs |
|---|---|---|
| id | `8921c4dc-346e-4be9-b6a4-088b770c2fe2` | `0052f79d-e278-4bc5-b0b4-5966a920da5c` |
| task | `netease_reason` | `netease_reason` |
| success/status | `succeeded` | `true` |
| provider | `qwen_general` | `qwen_general` |
| model | `qwen3.7-plus` | `qwen3.7-plus` |
| prompt_version | `v2` | `v2` |
| latency_ms | `32962` | `32962` |
| fallback | 由双 attempt 结果证明 | `true`，2 attempts |
| error | 无 | 无 |

Run 另有 `finished_at`、output，`validation_status=not_applicable`、
`review_status=not_required`，符合无 schema、无需人工审核的任务合同。

### 结论

- **通过**：真实同步 provider 调用已同时写入一个业务 Run 和一个技术 call log。
- 两条记录的可比较元数据一致，成功状态完整，无 error。
- RISK-B11-004 已关闭。
- 结论不扩展到 RISK-B11-003；真实 SSE 生命周期仍未验证。
