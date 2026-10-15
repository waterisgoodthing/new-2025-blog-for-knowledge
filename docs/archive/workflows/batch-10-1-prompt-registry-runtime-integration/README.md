# Batch 10.1：Prompt Registry Runtime Integration

> 状态：**通过，已关闭**
> 关联：[design.md](./design.md) | [requirements.md](./requirements.md) | [tasks.md](./tasks.md) | [validation.md](./validation.md) | [handoff.md](./handoff.md)
> 前置：[Batch 10 Task / Prompt / Validator 管理](../batch-10-task-prompt-validator/)

## 任务目标

Batch 10 建立了 Prompt Registry（`PROMPT_REGISTRY` + `PromptTemplate` + `get_prompt_template()`），但生产代码中 **0 处调用** `get_prompt_template()`——Registry 是"影子注册表"，定义了但没接上调用链。各 service 仍直接引用 `ai_prompts.py` 常量手动构建 messages。

Batch 10.1 的目标：**让 Registry 真正接上调用链**，使 `PromptTemplate` 的 `system_prompt` / `version` / `preferred_provider` / `max_tokens` / `json_mode` 等元数据被运行时使用。

## 核心问题

| 问题 | 现状 | 目标 |
|------|------|------|
| `get_prompt_template()` 0 调用 | service 直接引用常量 | service 通过 registry 获取 prompt |
| `preferred_provider` 未使用 | gateway 参数硬编码 | gateway 从 registry 读取默认值 |
| `max_tokens` 未使用 | gateway 参数硬编码 | gateway 从 registry 读取默认值 |
| `json_mode` 未使用 | gateway 参数硬编码 | gateway 从 registry 读取默认值 |
| `version` 未记录 | ai_call_logs 无版本字段 | 调用日志记录 prompt_version |
| 内联字符串未收敛 | ai.py 有 `"你是一个严谨的..."` | 收敛到 registry |
| `build_prompts_response` 手动引用 | 逐个引用常量构建 | 从 registry 动态生成 |

## 触及域

- `ai` — AI 调用链管理层
- `capture` — 采集草稿区
- `mistakes` — 分阶段错题流程

## 不做（边界）

- 不改变现有端点的请求/响应 schema 和 HTTP 状态码
- 不改变 AI 输出的业务语义
- 不引入 Prompt 热更新 / A/B 测试 / 效果评估（Level 4）
- 不引入 few-shot examples / Prompt 测试集（Level 3）
- 不新增 Prompt 管理数据库表（version 存储在代码中，非数据库）
- 不改变 ai_prompts.py 中的 Prompt 文本内容

## 当前状态

- ✅ 全部 13 个任务完成（P1-01 ~ P1-13）
- ✅ Registry 从"影子注册表"升级为运行时驱动组件
- ✅ 23 处注册表驱动调用点（6 直接 + 17 间接）
- ✅ 验收结论：通过，2 个偏差已记录于 [validation.md](./validation.md) 第 7 节和 [handoff.md](./handoff.md)
