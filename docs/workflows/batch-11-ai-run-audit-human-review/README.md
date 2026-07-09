# Batch 11：AI Run 审计与人工流转

> 状态：**已通过并关闭**
>
> 前置：[Batch 9 AI Gateway](../batch-9-ai-gateway-kernel/) ·
> [Batch 10 Task / Prompt / Validator](../batch-10-task-prompt-validator/) ·
> [Batch 10.1 Runtime Integration](../batch-10-1-prompt-registry-runtime-integration/) ·
> [Batch 10.2 Prompt Standardization](../batch-10-2-prompt-engineering-standardization/)
>
> 主文档：[requirements.md](./requirements.md) · [design.md](./design.md) ·
> [tasks.md](./tasks.md) · [validation.md](./validation.md) ·
> [audit.md](./audit.md) · [handoff-prompt.md](./handoff-prompt.md)

## 目标

把当前 `ai_call_logs` 的“调用完成后记录一条网关元数据”升级为可追踪的
AI Run 生命周期，并为需要人工确认的输出建立私有、可审计的接受/拒绝流转。

本批交付的最小闭环：

```text
创建 Run
  -> 执行 Gateway
  -> 记录成功/失败与校验结果
  -> 需要人工确认时进入 pending
  -> 管理员接受或拒绝
  -> audit_logs 记录决策
```

人工接受仅确认该次 AI 输出可供后续业务流程使用，不直接写入正式
Question、Mistake、Review Item、Note 或公开内容。

## 触及域

- `ai`：Run 生命周期、查询、重试、人工决策。
- `manage`：私有 Run 列表、详情与决策入口。
- `auth`：只复用现有管理员鉴权，不改变认证模型。
- shared infrastructure：数据库 migration 与现有 `audit_logs`。

不触及公开 `blog`、`notes`、`mistakes` 读取合同。

## 明确边界

- 不实现 Batch 12 的多供应商管理、动态路由、成本统计或稳定性治理。
- 不建设 Prompt 管理后台、A/B 测试、热更新或通用 Playground。
- 不引入生产任务队列、分布式 worker 或后台调度器。
- 不允许 AI Run 或人工“接受”动作直接写正式业务实体。
- 不把输入图片 base64、密钥、Authorization、cookie 或完整敏感 Prompt 写入日志。
- 不删除 `ai_call_logs`，不在本批强制清理旧兼容端点。
- 不进入 Batch 12。

## 关闭状态

- P0-01 至 P1-05 已按批准顺序执行并逐项勾选。
- `ai_runs` 与 `ai_call_logs` 保持业务审计/技术日志双轨。
- Run lifecycle、受控 output、revision decision、审计、私有 API 与管理 UI 已实现。
- 专项测试 19 passed；后端 207 passed / 0 failed / 2 warnings。
- Alembic 018 往返、TSC、build 与 diff 通过。
- 匿名浏览器访问会进入管理登录页，不泄露 Run。

Batch 11 关闭时以下三项保持 `not verified`，并由用户确认不阻塞原验收：

1. 已登录后的 Run 列表/详情/retry/decision 浏览器验收。
2. 真实 provider 同时写入 Run 与 call log。
3. 真实 SSE stream 的完整 start/finalize/断开审计。

2026-07-06 的关闭后补证已验证第 1、2 项：

- RISK-B11-001 已由 Browser Fix Patch 关闭。
- RISK-B11-004 已由一次受控真实同步 provider 调用关闭；同一调用新增一个
  `ai_runs` 和一个 `ai_call_logs` 记录，真实 fallback 后两条记录的 provider、
  model、Prompt 版本、延迟与成功状态一致。
- RISK-B11-003 仍为 `not verified`；stream 生命周期需要独立审批。

用户已确认 14 条批准硬约束全部遵守。Batch 11 已关闭，未进入 Batch 12。
