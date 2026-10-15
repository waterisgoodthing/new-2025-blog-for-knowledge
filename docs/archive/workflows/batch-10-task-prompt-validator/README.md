# Batch 10：Task / Prompt / Validator 管理

> 状态：**已完成**
> 关联：[design.md](./design.md) | [requirements.md](./requirements.md) | [tasks.md](./tasks.md) | [validation.md](./validation.md)
> 前置：[Batch 9 AI Gateway 最小内核](../batch-9-ai-gateway-kernel/)

## 任务目标

在 Batch 9 AI Gateway 最小内核的基础上，建立 AI 任务的结构化管理层：

1. **AI 任务类型定义** — 把散落在各 service 中的 task_type 字符串收敛为统一枚举。
2. **Prompt 模板版本管理** — 把散落在 7 个 service 文件中的 Prompt 常量收敛为统一注册表，带版本号。
3. **输出 schema / validator** — 为每种 AI 任务定义 Pydantic 输出 schema 和 validator，统一校验入口。
4. **失败结果进入草稿或错误状态** — 标准化失败处理路径，AI 失败不阻塞业务，结果进入草稿区或错误状态。

## 触及域

- `ai` — AI 调用链管理层
- `capture` — 采集草稿区（复用现有边界）
- `mistakes` — 分阶段错题流程（复用现有边界）

## 不做（边界）

- 不直接写正式业务实体（Note / mistake_drafts）
- 不建设 Prompt 管理后台 UI
- 不做多供应商路由或成本统计（Batch 12）
- 不建设完整 AI 审计事件系统（Batch 11）
- 不改变现有 AI 端点的请求/响应合同

## 当前状态

- **P0-01 至 P0-12 全部完成。**
- 16 个 task_type 字符串收敛为 `AiTaskType` 枚举。
- 14 个 Prompt 常量迁移到独立 `ai_prompts.py` module（无循环依赖）。
- 16 个 PromptTemplate 注册到 `PROMPT_REGISTRY`。
- 9 个有 schema 的 task_type 通过 `validate_ai_output` 统一校验。
- capture 模块集成 validator（带 fallback）。
- 生产代码中 0 处裸 task_type 字符串。
- 现有端点请求/响应 schema 和 HTTP 语义不变。
- 验证结果详见 [validation.md](./validation.md)。

### 后续批次

- [Batch 10.1 Prompt Registry Runtime Integration](../batch-10-1-prompt-registry-runtime-integration/) — ✅ 已通过。Registry 从"影子注册表"升级为运行时驱动组件，23 处注册表驱动调用点。

### 已知 deferred 项

- `mistake_staged_service` 集成 `validate_ai_output`：已有 normalize 逻辑，与 validator 集成需更细致测试，deferred 到后续迭代。
- stream 端点 task_type 枚举化：`"analyze_mistake_stream"` / `"analyze_text_stream"` 非直接 gateway 调用，保留为字符串。
