# Audit：Batch 11 最终审计与关闭

> 日期：2026-07-05
>
> 状态：**用户验收通过并关闭**

## 现行合同

| 范围 | 当前事实 | Batch 11 决定 |
|---|---|---|
| Gateway | `call_text/call_vision/call_general/call_ocr_model` 返回既有 `GatewayCallResult` | 方法签名与返回合同不变 |
| 技术日志 | `ai_call_logs` 记录 provider/model/latency/success/fallback/attempts | 保留写入，继续作为技术调用日志 |
| 业务 Run | 尚不存在 `ai_runs` | 新增独立业务审计记录，不替代 call log |
| Prompt | Registry 提供 task type 与 version | Run 保存使用时的 prompt version |
| Validator | schema validator 与手动 parser 并存 | 不替换现有 parser；Run 只记录 validation status |
| 旧 API | `/api/ai/call-logs`、`/stats`，管理员保护 | 原样保留，继续查询技术日志 |
| 新 API | 尚不存在 | 新增私有 `/api/admin/ai/runs` |
| 管理页 | `/manage/ai` 读取 call logs | 增加 Run 区域，不删除技术日志视图 |
| 审计 | 已有 `audit_logs`、`audit_action()` | 复用记录接受/拒绝，不复制完整 output/note |

## 接入范围

同步 Gateway 调用在方法内部创建和完成 Run，并继续独立写 `ai_call_logs`。
技术调用日志失败与业务 Run 失败分别处理，任何一方不伪装另一方。

stream 端点目前不走完整同步 Gateway 生命周期，仍存在客户端断开或生成器异常导致
Run 无法完整结束的缺口。本批必须记录该缺口；除非后续专项实现和验证完成，不得宣称
流式审计完整。

## 数据禁区

不得持久化或从 API 返回：

- API key、Authorization、cookie、session token；
- 图片 base64、data URL、绝对文件路径、附件 `storage_key`；
- 完整敏感输入原文；
- provider 原始敏感错误响应；
- 人工 review note 原文进入通用 `audit_logs.before/after`。

列表 DTO 不含 `output_data` 或 `replay_input`。详情 DTO 对 output 做递归字段清理；
`replay_input` 永不返回前端。

## 人工流转边界

- `accepted/rejected` 使用 `review_revision` 乐观并发控制。
- 冲突 revision 或相反的既有决定返回 409。
- 接受仅确认该 Run 输出；本批不调用 Question、Mistake、Review Item 写入 service。
- 若未来进入 draft/staged artifact，必须由独立、显式领域命令完成，不在本批隐式实现。

## 历史与回滚

- 不 delete/rename/drop/rebuild `ai_call_logs`。
- `ai_runs` migration 不从技术日志复制成业务 Run，避免混淆双轨语义。
- downgrade 仅删除新 `ai_runs`。
- 旧 call-log endpoint 和统计继续使用 `ai_call_logs`。

## Batch 12 禁区

本批不增加模型 profile、路由规则、成本、预算、多供应商优化、Prompt 管理后台、
A/B、热更新或生产任务队列。任何此类需要均进入新 workflow 和审批，不在 Batch 11
顺手实现。

## 剩余风险

### RISK-B11-001：已登录管理页视觉交互未验证

- 风险类型：体验 / 验收
- 风险描述：浏览器没有管理员会话，只验证了匿名访问被引导到登录页。
- 影响范围：Run 列表、详情、retry、接受/拒绝的实际已登录交互。
- 严重程度：中
- 当前状态：未验证
- 建议措施：由管理员登录后补做 `/manage/ai` 浏览器验收。
- 是否进入下一轮需求：否；属于 Batch 11 验收补证，不进入 Batch 12。

### RISK-B11-002：现有 Gateway Run 缺少 replay input

- 风险类型：功能
- 风险描述：为保持原 Gateway 方法签名，Gateway 只保存安全摘要，不接收 replay
  input；因此现有 Gateway 生成的 Run 调用 retry 会按合同返回 409。
- 影响范围：管理页 retry 的可用范围。
- 严重程度：中
- 当前状态：已接受的合同边界
- 建议措施：未来由明确的 Run 创建/编排入口按 task allowlist 保存 replay input，
  不得从 summary 推断。
- 是否进入下一轮需求：否；无 replay input 返回 409 正是批准硬约束。

### RISK-B11-003：真实 stream endpoint 生命周期不完整

- 风险类型：数据完整性
- 风险描述：真实 SSE 生成器未完整接入 Run start/finalize，客户端断开可能缺记录。
- 影响范围：`analyze-stream`、`analyze-text-stream`。
- 严重程度：中
- 当前状态：未验证
- 建议措施：独立实现生成器 finally 收口与断开测试。
- 是否进入下一轮需求：是，但不自动进入 Batch 12；需单独审批。

### RISK-B11-004：未执行真实 provider 端到端

- 风险类型：验证
- 风险描述：本批测试使用 mock/fake provider，没有证明真实调用能同时落 Run 与 call log。
- 影响范围：生产审计完整性结论。
- 严重程度：中
- 当前状态：未验证
- 建议措施：在凭据和测试数据安全条件满足时做一次受控真实验证。
- 是否进入下一轮需求：否；属于验收补证。

## 最终验收结论

- P0-01 至 P1-05：全部完成。
- 专项测试：19 passed。
- 后端全量：207 passed / 0 failed / 2 warnings。
- TSC、build、018 migration 往返：通过。
- `ai_runs` / `ai_call_logs` 双轨边界成立。
- 人工接受不自动 apply 到正式 Question、Mistake 或 Review Item。
- 14 条批准硬约束全部遵守。
- RISK-B11-001、RISK-B11-003、RISK-B11-004 保持未验证，但用户确认不阻塞验收。
- Batch 11 已关闭；未进入 Batch 12。

## Browser Verification Patch 审计

### RISK-B11-005：目标管理路由不存在

- 风险类型：功能 / 导航 / 验收
- 风险描述：验收目标 `/manage/ai/runs` 实际返回 Next.js 404；当前 Run UI 仅内嵌于 `/manage/ai`。
- 复现路径：浏览器访问 `http://127.0.0.1:2025/manage/ai/runs`。
- 响应证据：页面标题为 `404: This page could not be found.`，页面显示 404。
- 影响范围：已登录 Run 列表、筛选、分页、详情、decision 与 retry 的目标路由验收全部无法开始。
- 严重程度：P1
- 当前状态：阻断 Browser Verification Patch
- 建议措施：由用户选择以下其一并重新批准：
  1. 新增 canonical `/manage/ai/runs` 页面，并明确 `/manage/ai` 到该页面的入口；
  2. 正式把本轮验收目标改为现有 `/manage/ai` 内嵌 Run 区域。
- 是否关闭 RISK-B11-001：否。
- 是否进入 Batch 12：否。

按照用户规则，本轮未自行修改代码，发现 P1 后即暂停。

### RISK-B11-006：Run 列表缺少分页

- 风险类型：功能 / 可用性
- 风险描述：`/manage/ai` 的 Run 列表固定请求 `limit=30`，没有 offset、上一页或下一页控件。
- 复现路径：临时管理员登录后访问 `/manage/ai`，检查“业务审计 Runs”区域。
- 响应证据：请求为 `GET /api/admin/ai/runs?limit=30`；页面只有状态筛选。
- 影响范围：超过 30 条 Run 时无法通过 UI 查看后续记录。
- 严重程度：P1
- 当前状态：阻断 Browser Verification Patch 完整通过
- 建议措施：新增 Run 分页状态、offset 请求与上一页/下一页反馈。
- 是否关闭 RISK-B11-001：否。
- 是否进入 Batch 12：否。

## 临时管理员补证结论

已通过：

- 管理员真实密码 session 登录。
- `/manage/ai` Run 列表、状态筛选与详情。
- 无 replay input 的 retry 409 与前端错误反馈。
- 匿名 Run API 401。
- 当前样本页面敏感字段检查。
- `/`、`/blog`、`/notes` 未请求 `/api/admin/ai/runs`。

未通过或未验证：

- `/manage/ai/runs`：P1 404。
- Run UI 分页：P1 缺失。
- 接受/拒绝和 revision 409：无 pending fixture，未验证。

临时账号 `codex-b11-browser` 已禁用，隔离服务已停止。未修改代码，未进入 Batch 12。

## Browser Fix Patch 审计结论（2026-07-06）

### RISK-B11-005：目标管理路由不存在

- 当前状态：**已关闭**。
- 关闭证据：新增 `/manage/ai/runs`；浏览器已登录访问成功；production build route
  清单包含 `○ /manage/ai/runs`。
- 入口关系：`/manage/ai` 是技术调用日志控制台，并链接到独立业务 Run 审计页；Run
  页面提供返回 AI 控制台入口。

### RISK-B11-006：Run 列表缺少分页

- 当前状态：**已关闭**。
- 关闭证据：后端返回 total/limit/offset；浏览器验证 20 条第一页、7 条第二页、上一页/
  下一页及筛选回第一页。
- 安全边界：分页列表 item 没有 output、replay input、input summary 或敏感字段。

### RISK-B11-007：decision 响应序列化 500

- 风险类型：人工流转 / 数据库异步加载。
- 发现证据：真实浏览器 accept 后服务端返回 500；日志显示数据库生成的 `updated_at`
  在 Pydantic 响应序列化阶段触发 `MissingGreenlet`。
- 修复：人工决定 flush 和审计记录后显式 refresh Run，再交给响应 DTO 序列化。
- 回归证据：service test 断言 refresh；accept/reject 浏览器请求均为 200；全量
  209 passed。
- 当前状态：**已关闭**。

### RISK-B11-001：已登录浏览器交互

- 当前状态：**已关闭**。
- 已验证：独立路由、列表、筛选、分页、详情、accept、带 note 的 reject、成功反馈、
  stale revision 409、retry 409、匿名保护、敏感字段清理、公开页无 Run API 请求。
- 人工接受/拒绝只更新 Run review 状态与 audit log；没有调用 Question、Mistake 或
  Review Item 写入 service。

仍保留且不在本补丁范围：

- RISK-B11-003：真实 stream 生命周期未验证。
- RISK-B11-004：真实 provider 端到端未验证。

未进入 Batch 12。

## Provider Verification Patch 审计结论（2026-07-06）

### RISK-B11-004：未执行真实 provider 端到端

- 当前状态：**已关闭**。
- 执行范围：一次无个人数据、`max_tokens=80` 的真实同步
  `netease_reason` Gateway 调用。
- 真实路径：首选 provider 尝试失败后，fallback 到
  `qwen_general/qwen3.7-plus` 成功；共 2 attempts。
- 落库证据：同一唯一 marker 和调用时间窗内，`ai_runs` 与 `ai_call_logs`
  各新增且仅新增 1 条匹配记录。
- 一致性证据：两条记录的 task、provider、model、Prompt `v2`、延迟
  `32962ms` 与成功状态一致，均无错误。
- Run 证据：`status=succeeded`、已完成、output 存在；
  `validation_status=not_applicable` 与无 schema 任务合同一致。
- 数据安全：未记录 provider 密钥、模型正文或完整敏感输入；文档只保留测试 marker、
  元数据、记录 ID 与输出哈希前缀。

本补证证明真实同步 Gateway 双轨落库成立，不证明模型内容质量，也不覆盖真实 SSE
生成器的 start/finalize/断开生命周期。RISK-B11-003 保持 `not verified`，未进入
Batch 12。
