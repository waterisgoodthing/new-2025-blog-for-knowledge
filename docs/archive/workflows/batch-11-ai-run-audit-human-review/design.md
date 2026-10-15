# Design：Batch 11 AI Run 审计与人工流转

> 状态：**已完成并关闭**
>
> 关联：[requirements.md](./requirements.md) · [tasks.md](./tasks.md)

## 1. 现状与决策

现行 `AiCallLog` 记录 task、provider、model、latency、success、error、
fallback、attempts、input summary 和 Prompt version，但只在 Gateway 调用结束后写入。

Batch 11 采用新增 `ai_runs`、保留 `ai_call_logs` 的渐进方案：

- `ai_runs` 成为新写入和新管理界面的事实源；
- `ai_call_logs` 保留，不在本批删除；
- migration 不复制历史技术日志，避免把 call log 伪装成业务 Run；
- 旧 call-log API 作为兼容读取，不能继续驱动新页面。

选择此方案是为了避免在当前大量未提交改动中直接 rename/drop 历史表，也为回滚保留边界。

## 2. 数据模型

新增 `AiRun`：

```text
id UUID PK
task_type VARCHAR(50) NOT NULL
target_type VARCHAR(50) NULL
target_id VARCHAR(100) NULL

provider_used VARCHAR(50) NULL
model VARCHAR(100) NULL
prompt_version VARCHAR(20) NULL

status VARCHAR(20) NOT NULL
validation_status VARCHAR(20) NOT NULL
input_summary TEXT NULL
replay_input JSON NULL
output_data JSON NULL
warnings JSON NULL
error_code VARCHAR(50) NULL
error_message_safe TEXT NULL

attempt INTEGER NOT NULL DEFAULT 1
parent_run_id UUID NULL FK ai_runs.id

review_status VARCHAR(20) NOT NULL
review_revision INTEGER NOT NULL DEFAULT 0
reviewed_at TIMESTAMPTZ NULL
review_note TEXT NULL

latency_ms INTEGER NULL
started_at TIMESTAMPTZ NOT NULL
finished_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

约束：

- `status`: `running | succeeded | failed`
- `validation_status`: `pending | passed | failed | warning | not_applicable`
- `review_status`: `not_required | pending | accepted | rejected`
- `attempt >= 1`
- `parent_run_id != id`
- pending review 只用于已定义需要人工确认的 task type。

索引：`created_at`、`task_type`、`status`、`review_status`、`parent_run_id`。

`replay_input` 只保存允许重放的安全结构；任何 image data URL/base64、凭据或 header
必须在 service 入库前拒绝或删除。

## 3. 生命周期服务

新增薄接口：

```python
start_ai_run(...)
complete_ai_run(...)
fail_ai_run(...)
retry_ai_run(...)
decide_ai_run(...)
query_ai_runs(...)
get_ai_run(...)
```

Gateway 调用流程：

```text
start_ai_run
  -> provider call/fallback
  -> existing validator/parser
  -> complete_ai_run or fail_ai_run
  -> return existing endpoint response unchanged
```

Run 写入失败不得改变已有 API response schema。若 start 失败，Gateway 继续按既有合同
返回，但写结构化安全日志；这类审计缺口必须在 validation 中显式暴露。

## 4. 人工流转

首批人工流转只记录“接受/拒绝该 Run 输出”，不执行 Apply Controller：

```text
succeeded + validation passed/warning + review pending
  -> accepted
  -> rejected
```

非法路径：

- failed Run 不可接受；
- validation failed 不可接受；
- not_required 不可人工决定；
- accepted 与 rejected 之间不可直接改写；
- revision 不匹配返回 409。

人工决定复用现有 `audit_logs`：

```text
action: ai_run.accept | ai_run.reject
entity_type: ai_run
entity_id: run UUID
before: review status/revision
after: review status/revision/note-present
```

审计 before/after 不保存完整 output 或 note 正文。

## 5. API

新建独立 admin router，避免继续膨胀现有 `backend/app/routers/ai.py`：

```text
backend/app/routers/ai_runs.py
prefix=/api/admin/ai/runs
```

端点：

```text
GET  /
GET  /{run_id}
POST /{run_id}/retry
POST /{run_id}/decision
```

所有端点依赖 `get_current_admin`。列表使用轻量 DTO，详情才返回 `output_data`。

兼容端点 `/api/ai/call-logs` 与 `/stats` 暂保留。是否改为从 `ai_runs` 读取必须在
实现时用响应合同测试证明兼容；否则维持旧表读取并标注历史冻结。

## 6. 前端

沿用 `/manage/ai`，不新建公共路由。首批可在现页增加 list/detail 两级视图；
若组件体积过大，拆至：

```text
src/app/manage/(workspace)/ai/components/
src/app/manage/(workspace)/ai/hooks/
src/lib/api/ai-runs.ts
```

页面状态：

- loading / empty / error；
- filters；
- selected run detail；
- retry pending/error；
- decision pending/conflict/success。

前端不接收 `replay_input`，也不负责权限过滤。

## 7. 历史迁移与回滚

Alembic：

1. 创建 `ai_runs` 和索引/FK/约束。
2. 不读取或修改 `ai_call_logs`。
3. 不删除旧表。

downgrade 只删除 `ai_runs`，不触碰 `ai_call_logs`。

## 8. 安全

- 管理 API 后端鉴权是唯一真实边界。
- `input_summary` 和 `error_message_safe` 有长度上限。
- `replay_input` 由 allowlist 按 task type 构建。
- output_data 仅限管理详情。
- audit log 不复制完整 output、输入或 review note。
- 公开页面不得调用 Run API。

## 9. 验证

后端：

- migration upgrade/downgrade/current；
- model constraint；
- lifecycle、异常、重试、decision、revision；
- admin 权限与 DTO 泄露检查；
- 原 AI 端点合同回归；
- 全量 pytest。

前端：

- `npx tsc --noEmit`；
- `npm run build`；
- 浏览器检查 `/manage/ai` 的 loading/empty/list/detail/retry/decision。

边界：

- grep migration/代码确认没有 cost、routing CRUD、Prompt 管理后台和自动 apply；
- 不调用真实 provider 作为本批自动验收前提。
