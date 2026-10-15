# Batch 10.2：Prompt Engineering Standardization

> 状态：**已完成并通过本地自动化验收**
>
> 前置：[Batch 10 Task / Prompt / Validator](../batch-10-task-prompt-validator/) · [Batch 10.1 Prompt Registry Runtime Integration](../batch-10-1-prompt-registry-runtime-integration/)
>
> 主文档：[requirements.md](./requirements.md) · [design.md](./design.md) · [tasks.md](./tasks.md) · [validation.md](./validation.md) · [audit.md](./audit.md)

## 任务目标

在 Batch 10.1 已完成 Prompt Registry 运行时接入的基础上，把当前 Prompt 从“集中存放、可运行”提升为“结构统一、变量可检查、输出合同可追踪、修改可回归”的工程化资产。

本批不以重写 Prompt 文案或追求主观效果为目标，而是建立最小、可自动验证的 Prompt 工程标准：

1. 固定 Prompt 的角色、任务、输入、约束、输出、失败语义等结构。
2. 为模板变量建立显式合同和安全渲染入口。
3. 使 Registry 中的输出 schema、JSON 模式和 Prompt 文本保持一致。
4. 消除业务 service 对 Prompt 常量的受控例外引用。
5. 增加静态规范检查和确定性单元测试。

## 触及域

- `ai`：Prompt 常量、Registry、消息构建、输出合同和测试。
- shared infrastructure：仅限 Prompt 规范检查；不改变 Gateway 的供应商调用职责。

本批不触及 `blog`、`notes`、`review`、`auth`、`sync`、`home`、`share`、`manage` 页面。

## 边界

- 不新增 Prompt 管理后台或公开页面。
- 不新增数据库表或 Alembic migration。
- 不做多供应商路由、成本治理或完整 AI Run 审计。
- 不改变现有 API 请求/响应 schema、HTTP 状态码和权限边界。
- 不让 AI 结果绕过 validator 或草稿确认流程写入正式业务实体。
- 不进入 Batch 11。

## 完成状态

- P0-01 至 P1-04 已按批准顺序完成。
- 目标测试 72 passed；后端全量 185 passed、2 个既有 warning。
- `npx tsc --noEmit` 与 `git diff --check` 通过。
- 静态 Prompt 因结构包装实际改变发送文本，版本从 `v1` 升级为 `v2`；
  两个动态 Prompt 保持 `v1`。
- 未新增 API response 字段、业务输出字段、数据库表或 migration。
- 未进入 Batch 11，未执行真实 provider 效果评估。
