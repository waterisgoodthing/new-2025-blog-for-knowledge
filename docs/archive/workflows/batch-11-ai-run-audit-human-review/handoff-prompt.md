# Handoff：Batch 11 关闭后的可选补证

> Batch 11 已通过并关闭。本文件仅保留三项可选补证，不批准 Batch 12，
> 且这些补证不阻塞已完成的验收结论。

## 当前实现

- `ai_runs`：业务审计。
- `ai_call_logs`：技术调用日志，旧表和旧 endpoint 保留。
- `/api/admin/ai/runs`：管理员列表、详情、retry、decision。
- `/manage/ai`：业务 Run 与技术日志双轨界面。
- 人工接受只改变 Run review 状态，不写正式实体。

## 待补证

### 1. 已登录浏览器

管理员登录后检查 `/manage/ai`：

- Run loading/empty/list/detail；
- 列表无 output/replay/input summary；
- 详情 output 无 credential、绝对路径、storage key、data URL；
- 无 replay input 的 retry 返回可读 409；
- pending 决策成功；
- 两个页面同时操作时，旧 revision 返回 409；
- 接受提示明确不会直接写正式内容；
- 技术 call-log 区域仍可用。

### 2. 真实 provider

仅在用户另行批准并提供安全测试输入后执行。必须证明同一次真实同步调用分别写入：

- 一个 `ai_runs` 业务记录；
- 一个 `ai_call_logs` 技术记录。

不得把 mock/fake 结果写成真实验证。

### 3. Stream

当前 SSE endpoint 不具备完整 Run 生命周期证据。需要单独任务实现：

- generator 开始前 Run；
- 正常完成 finalize；
- provider 失败 finalize；
- parser 失败 validation failed；
- 客户端断开 finally 收口。

该任务不得顺带进入 Batch 12 的成本、路由或多供应商治理。
