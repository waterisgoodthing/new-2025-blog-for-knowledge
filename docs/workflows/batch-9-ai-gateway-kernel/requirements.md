# Requirements：Batch 9 AI Gateway 最小内核

> 关联：[README.md](./README.md) | [design.md](./design.md) | [tasks.md](./tasks.md)

## 一、功能需求

### 1.1 统一 Gateway 调用入口

- 所有 AI 模型调用必须经过 `ai_gateway.py`，不直接调用 `ai_service.py` 的 `call_*` 函数。
- Gateway 提供按用途的调用方法：文本调用、视觉/OCR 调用、通用调用、流式调用。
- 每次调用携带 `task_type` 标识（如 `analyze_mistake`、`question_draft`、`ocr`、`diagram`、`polish`）。
- Gateway 委托 `ai_service.py` 执行实际 provider 调用与 fallback。

### 1.2 调用日志持久化

- 每次 Gateway 调用（无论成功或失败）写入 `ai_call_logs` 表。
- 记录字段：task_type、provider_used、model、latency_ms、success、error（截断）、fallback_used、attempts（JSON）、input_summary（截断）、created_at。
- 日志写入失败不阻塞主调用（catch + log warning）。
- 日志不记录完整 prompt 内容（可能含用户数据），只记录摘要。

### 1.3 ai.py 路由瘦身

- 把 `ai.py` 中的业务逻辑函数抽离到 service 层：
  - LaTeX 修复（`_repair_latex_in_text`、`_repair_latex_in_result`）
  - deterministic repair（`_check_deterministic_fields`、`_repair_deterministic_result`）
  - 结果解析（`_parse_result`）
  - 个人上下文构建（`_build_personal_context`）
  - 相关笔记查找（`_find_related_notes`）
- 路由只做：请求接收、参数校验、调用 service/Gateway、返回响应。
- 瘦身后 `ai.py` 行数目标 < 600 行（当前 1605 行）。

### 1.4 调用日志查询

- `GET /api/ai/call-logs`（admin only）：分页查询调用日志，支持按 task_type、success、provider 过滤。
- `GET /api/ai/call-logs/stats`（admin only）：聚合统计（按 task_type/provider 的成功率、平均延迟）。
- `/manage/ai` 页面展示调用日志列表与统计。

### 1.5 现有调用迁移

- `capture_ai_draft.py`：从 `call_text_model` 改为 `ai_gateway.call_text`。
- `diagram_service.py`：从直调 dashscope 改为经 Gateway。
- `ai_polish.py`：迁移到 Gateway。
- `ai.py` 中所有 `call_ocr_model` / `call_text_model` 调用改为 `ai_gateway.call_*`。

## 二、非功能需求

### 2.1 权限

- 所有 AI 调用端点必须受 `get_current_admin` 保护（既有规则，不变）。
- 调用日志查询端点必须受 `get_current_admin` 保护。
- 调用日志不暴露给公开页。
- Gateway 层不做权限校验（权限在路由层），Gateway 只做调用编排。

### 2.2 数据安全

- `ai_call_logs` 不存储完整 prompt 和完整输出（可能含用户错题数据）。
- `input_summary` 截断至 200 字符。
- `attempts` 只存 provider/model/success/latency/error，不存请求体。
- 调用日志表不包含 PII。

### 2.3 向后兼容

- 现有 AI 端点的请求/响应 schema 不变。
- `ai_service.py` 的 `call_*` 函数保留（Gateway 内部调用），但外部不应直接调用。
- `get_provider_status()` 保留，前端 `ai-tab.tsx` 不受影响。
- migration 016 只新增表，不改现有表。

### 2.4 性能

- 调用日志写入使用独立 DB session（不阻塞主调用事务）。
- 日志查询端点有分页（默认 20，最大 100）。
- 统计端点有索引支持（task_type, created_at）。

## 三、数据流

```text
路由层 (ai.py)
  → service 层 (ai_analyze_service.py 等, 瘦身后)
    → ai_gateway.py (call_text / call_vision / call_stream)
      → ai_service.py (_call_with_fallback)
        → provider HTTP 调用
      → ai_call_logs 写入 (独立 session)
    → 返回 CallResult
  → 响应
```

## 四、ai_call_logs 表结构（草案）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | UUID PK | |
| task_type | String(50) | analyze_mistake / question_draft / ocr / diagram / polish |
| provider_used | String(50) | deepseek / dashscope_vision / qwen_general |
| model | String(100) | |
| latency_ms | Integer | |
| success | Boolean | |
| error | Text (nullable) | 截断 500 字符 |
| fallback_used | Boolean | |
| attempts | JSON (nullable) | [{provider, model, success, latency_ms, error}] |
| input_summary | Text (nullable) | 截断 200 字符 |
| created_at | DateTime(tz) | server_default now() |

索引：`idx_ai_call_logs_created_at`、`idx_ai_call_logs_task_type`、`idx_ai_call_logs_success`。

## 五、验收要求

1. 所有 AI 调用经 Gateway，无直接 `ai_service.call_*` 外部调用。
2. `ai_call_logs` 表正确创建（migration 016）。
3. 每次调用有日志记录（成功和失败均记录）。
4. `ai.py` 行数 < 600，业务逻辑在 service 层。
5. 现有 AI 端点行为不变（schema 兼容）。
6. 调用日志查询端点正常工作（admin only）。
7. `/manage/ai` 展示调用日志。
8. 后端单元测试覆盖：Gateway 调用、日志写入、fallback、错误处理。
9. `npx tsc --noEmit` 通过；`npm run build` 通过。
10. 后端测试通过（`pytest backend/tests/`）。
