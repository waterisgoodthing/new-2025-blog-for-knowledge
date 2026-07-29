# AI System

> 状态：目标任务型 AI 架构，待实现。

## 系统定位

AI 是任务执行引擎，不是通用聊天框。它负责识别、分类、结构化、解释、总结、校验和生成草稿；正式事实仍由规则系统和管理员确认。

## 模块

`Prompt Policy → Task Templates → Context Builder → Model Router → Model Gateway → Output Validator → Apply Controller → AI Run Logger`

核心表：`ai_model_profiles`、`ai_routing_rules`、`ai_prompt_templates`、`ai_runs`。

- Model Profile 保存 provider、model、能力、`api_key_ref` 和启用状态。
- Routing Rule 按 `task_type`、条件和优先级选择主模型与 fallback。
- Prompt Template 保存 `task_type`、版本化模板、输出 schema 和 validator 配置。
- AI Run 必须记录 `task_type`、模型 profile、路由规则、Prompt 模板/版本、校验状态、置信度、warnings、输入/输出 token、成本估算、延迟和错误。

## 模型路由建议

第一版可评估 Qwen（视觉与 JSON）、DeepSeek（推理与错因）、Kimi（长文本/PDF）、豆包（低成本摘要）、GLM（推理/多模态备用）。这些是候选配置，不表示已经接入或批准采购。

## 输出边界

AI 输出只能进入 `draft`、`suggestion`、`report` 或 `analysis`。输出必须经过 schema、枚举、引用完整性、置信度和业务规则校验。AI 不得静默写题库、错题、复习计划、掌握度或公开内容，也不得自动判定 mastered。

每次运行必须保存任务类型、输入快照引用、`model_profile_id`、`routing_rule_id`、`prompt_template_id`、`prompt_version`、输出、`validation_status`、`confidence`、`warnings`、`token_input`、`token_output`、`cost_estimate`、`latency_ms`、`error_message` 和重试链。

目标 API 统一为 `/api/admin/ai/runs`；旧 `/api/admin/ai-runs` 仅可作为迁移兼容路径。

## 第一版范围

任务模板、模型配置、路由/fallback、结构化输出验证、运行日志、草稿生成和基础成本统计。

## 暂缓范围

通用聊天、RAG、向量库、本地推理、Agent 自主写库和 AI 自动改复习计划。
