# AI Admin Console

> 状态：拟新增的私有管理能力。

## 职责

提供模型连接、路由规则、Prompt 模板、任务 Playground、运行日志、校验结果和成本统计。它管理 AI 基础设施，不替代题库、草稿审核或业务编辑页面。

## 路由

`/manage/ai`、`/manage/ai/models`、`/manage/ai/routing`、`/manage/ai/prompts`、`/manage/ai/playground`、`/manage/ai/runs`、`/manage/ai/validators`、`/manage/ai/costs`。

`/manage/ai/runs` 是唯一目标主路径；旧 `/manage/ai-runs` 只能重定向到该页面。页面调用 `/api/admin/ai/runs`。

所有页面均受管理通行密钥会话保护；日志中的附件、输入和输出默认私有并按需脱敏。

管理台的数据基础为 `ai_model_profiles`、`ai_routing_rules`、`ai_prompt_templates` 和 `ai_runs`。Runs 列表与详情必须展示命中的模型、路由规则、Prompt 版本、validation status、confidence、warnings、token、成本、延迟和错误，确保每次执行可解释。

## 设计方向

可借鉴 LiteLLM 的网关、fallback 和成本追踪，Langfuse 的 Prompt/Trace/Observability，以及 Open WebUI 的连接体验；不直接嵌入通用聊天系统。

## 第一版范围

模型 profile CRUD、连接测试、任务到模型路由、版本化 Prompt、结构化 Playground、运行筛选、失败重试、校验详情和成本汇总。

## 暂缓范围

多人审批、复杂预算中心、实时协作、通用聊天和自动发布 AI 输出。
