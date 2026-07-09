# Batch 9：AI Gateway 最小内核

> 阶段：**已完成**（P0-01~P0-09 全部实施并验证）
> 前置：Batch 8（图片错题采集）已完成；Route Cutover Sprint 已完成
> 触碰域：`ai`、`capture`、`mistakes`、`review`、`manage`、后端共享基础设施

## 一、任务目标

在 Batch 8 留下的"窄调用边界"之上，建立统一的 AI Gateway 最小内核，为 Batch 10–12 打基础：

```text
ai.py (router, 瘦身)
  → ai_gateway.py (Gateway 层: 统一调用入口 + 调用日志)
    → ai_service.py (底层: provider caller + fallback)
    → ai_call_logs (DB: 调用记录持久化)
```

Batch 9 解决的问题：
- AI 调用散落在 `ai.py`（1605 行）、`capture_ai_draft.py`、`diagram_service.py` 中，无统一入口
- 调用结果不持久化，无法查询和统计
- `ai.py` 路由混入大量业务逻辑（LaTeX 修复、deterministic repair、parse result）
- provider 配置在 `ai_service.py` 和 `ai.py` 中重复

## 二、现状（代码事实）

### 现有 AI 调用链

| 文件 | 职责 | 行数 |
| --- | --- | --- |
| `backend/app/routers/ai.py` | AI 路由 + 大量业务逻辑 | 1605 |
| `backend/app/routers/ai_polish.py` | AI 润色路由 | — |
| `backend/app/services/ai_service.py` | provider 抽象 + fallback + CallResult | 317 |
| `backend/app/services/capture_ai_draft.py` | Batch 8 窄调用边界 | 188 |
| `backend/app/services/diagram_service.py` | 图解生成（直调 dashscope） | — |

### 现有 Provider 配置（`config.py`）

| Provider | 用途 | Key | Model |
| --- | --- | --- | --- |
| DeepSeek | 文本主路径 | `DEEPSEEK_API_KEY` | `deepseek-v4-pro` |
| DashScope Vision | OCR/视觉主路径 | `DASHSCOPE_API_KEY` | `qwen3.7-plus` |
| Qwen General | 通用 fallback | `DASHSCOPE_API_KEY` 或 `AI_API_KEY` | `qwen3.7-plus` |

### `ai_service.py` 已有的"准 Gateway"基础

- `ProviderAttempt` / `CallResult` 数据结构
- `_get_providers()` provider 注册
- `_select_providers()` capability 过滤 + preferred 排序
- `_call_with_fallback()` fallback 链 + latency 追踪
- `call_ocr_model()` / `call_text_model()` / `call_general_model()` 便捷封装
- `get_provider_status()` 状态查询

## 三、用户确认的架构决策

1. **Gateway 架构**：新建 `ai_gateway.py` 作为 Gateway 层；`ai_service.py` 降为底层 provider caller。
2. **调用日志**：新建 `ai_call_logs` 数据库表 + Alembic migration（016），持久化 AI 调用记录。
3. **范围边界**：包含 `ai.py` 轻量瘦身——把路由中的业务逻辑（LaTeX 修复、deterministic repair、parse result 等）抽离到 service 层。

## 四、本轮边界

本轮**做**：
- 新建 `ai_gateway.py` Gateway 层（统一调用入口 + 调用日志写入）
- 新建 `ai_call_log.py` 模型 + Alembic 016 migration
- `ai_service.py` 保留底层 provider caller，Gateway 委托调用
- `ai.py` 路由瘦身（业务逻辑抽离到 service）
- 现有 AI 调用迁移到 Gateway（capture_ai_draft、diagram_service 等）
- 调用日志查询端点 + `/manage/ai` 页面展示
- 后端单元测试

本轮**不做**：
- Prompt 管理后台（Batch 10）
- 完整 AI 审计事件系统（Batch 11）
- 多供应商路由 / 成本统计 / 模型路由策略（Batch 12）
- BKT、练习系统、批量 OCR、PDF 拆题
- 公开页展示 AI 调用日志
- 对象存储、云部署、生产级任务队列
- 改 Batch 8 capture 业务逻辑
- 改数据库现有表结构（只新增 ai_call_logs 表）

## 五、后续分阶段路线

| 批次 | 目标 |
| --- | --- |
| Batch 8 | 图片错题采集 MVP ✅ |
| Route Cutover | 新旧路由束口 ✅ |
| **Batch 9** | **AI Gateway 最小内核** |
| Batch 10 | Task / Prompt / Validator 管理 |
| Batch 11 | AI Run 审计与人工流转 |
| Batch 12 | 多供应商、路由、成本与稳定性治理 |

## 六、主线文件

| 文件 | 用途 |
| --- | --- |
| [requirements.md](./requirements.md) | 范围、约束、数据流、权限、验收要求 |
| [design.md](./design.md) | Gateway 架构、ai_call_logs 模型、接口设计、ai.py 瘦身方案 |
| [tasks.md](./tasks.md) | P0 实施勾选项（全部完成） |
| [risks.md](./risks.md) | 风险记录 |
| [validation.md](./validation.md) | 验证方案与记录 |

## 七、状态

- 文档准备：✅ 完成
- 代码实施：✅ 完成（P0-01~P0-09 全部完成）
- 验证：✅ 通过（详见 [validation.md](./validation.md)）
  - `test_ai_gateway.py` 11/11 passed
  - `npx tsc --noEmit` 0 error
  - Grep 确认无外部直接调用 `ai_service.call_*`
  - `ai.py` 1605 → 618 行（-61%）
