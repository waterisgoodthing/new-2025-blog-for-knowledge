# Requirements

## 背景

Batch 11 已建立 `ai_runs` / `ai_call_logs` 双轨、Run 管理与人工决定流程，并已补证
真实同步 provider Run。遗留的 RISK-B11-003 只涉及两个 SSE generator 路径：

- `POST /api/ai/analyze-stream`
- `POST /api/ai/analyze-text-stream`

现有 `ai_gateway.call_stream()` 是同步 provider 调用的包装，不是逐 chunk generator。
本任务组先冻结设计边界，随后通过 Stream Endpoint Simplification Patch 关闭
RISK-B11-003：正式可审计生成链路迁出伪流式 SSE endpoint，旧 stream endpoint
保留为 deprecated / compatibility-only。

## 角色与目标

- 管理员：在错题编辑器中获得明确的分析进度、成功结果或断流提示。
- 运维/审计者：区分 provider 调用成功、最终 parser 成功及客户端是否取得结果。
- 开发者：获得可独立实施、可测试且不扩大敏感数据面的生命周期合同。

## 功能需求

### REQ-STREAM-001 调用现状

- 输入：endpoint、API client、UI 调用与测试代码。
- 处理：只读追踪调用链。
- 输出：每个 endpoint 的调用位置、使用状态、保留必要性与证据。
- 失败处理：路径不存在或无调用时明确记录，不以推测替代证据。

验收标准：`validation.md` 包含 endpoint 与调用点文件/行号。

### REQ-STREAM-002 Run 接入决策

- 比较方案 A（接入 `ai_runs`）与方案 B（暂不接入）。
- 说明正式可审计生成应走哪条路径。
- 不得把同步 Gateway Run 表述为完整 stream 生命周期证据。

验收标准：`design.md` 给出明确推荐及取舍。

### REQ-STREAM-003 生命周期合同

设计必须覆盖：

`created -> running -> succeeded | failed | interrupted`

并区分 provider completion、parser completion、SSE delivery completion 与 client
disconnect。

验收标准：每个转换均有触发条件、审计结果及 `validation_status` /
`review_status` 规则。

### REQ-STREAM-004 输出持久化

必须在“不保存 partial output”与“保存 partial artifact”之间作出选择，并定义 final
output 的清理与展示合同。

验收标准：明确是否写入 artifact、允许展示的数据和禁存数据。

### REQ-STREAM-005 前端影响

审查当前 UI 是否依赖逐 token 输出、是否需要 `run_id`、断流提示、Run 列表展示与
新状态标签。

验收标准：形成不实施代码的影响清单。

## 非功能需求

- 安全：不得保存 API Key、authorization、cookie、secret、token、storage_key、
  绝对路径、data URL、完整 replay input 或敏感原文。
- 一致性：不得出现 provider 已成功而 parser 失败却仍标记完整成功的歧义。
- 可审计性：未来实现必须确保 generator 的正常结束、异常及取消均有终态。
- 可测试性：mock 单测与受控断连集成测试分开；真实 provider 只能作为后续补证。
- 兼容性：不能破坏当前管理员写错题流程。

## 本轮边界

本任务组不实现真实 provider token streaming 生命周期，不保存 partial output，
不新增 migration、数据库表、成本、多供应商路由、Prompt 后台或 A/B 测试。

## 本轮验收

- 8 个要求文件存在。
- 代码证据来自只读命令。
- `tasks.md` 记录设计审查与 Stream Endpoint Simplification Patch 均已关闭。
- 声明 RISK-B11-003 的关闭方式，但不声明真实 provider token streaming 已完成。
