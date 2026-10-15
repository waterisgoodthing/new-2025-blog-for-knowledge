# Requirements：Batch 11 AI Run 审计与人工流转

> 状态：**已完成并关闭**
>
> 关联：[design.md](./design.md) · [tasks.md](./tasks.md)

## 1. 背景

Batch 9 已建立 AI Gateway 和 `ai_call_logs`，Batch 10–10.2 已建立任务类型、
Prompt Registry、版本、输出 schema 与静态规范。当前记录仍有四个缺口：

1. 只在调用结束后写日志，无法表达 running、failed、retry 等生命周期。
2. 没有结构化 validation status、error code、输出快照和重试链。
3. 管理页只能看调用列表，不能查看单次 Run 详情。
4. 需要人工确认的 AI 输出没有统一接受/拒绝状态及审计动作。

## 2. 角色

- 管理员：创建、查看、筛选、重试 AI Run，并接受或拒绝待确认输出。
- 访客：不得读取、创建、重试或决策任何 AI Run。

## 3. 功能需求

### R1：AI Run 生命周期

输入：现有 Gateway task type、脱敏输入摘要、Prompt 版本和任务上下文。

处理：

- 调用前创建 Run；
- 状态按 `running -> succeeded | failed` 转换；
- 记录 provider/model、Prompt 版本、延迟、校验状态、错误码和安全错误消息；
- 异常路径也必须尽力完成 Run。

输出：稳定 run ID 和最终状态。

失败行为：Run 记录失败不得吞掉原 Gateway 结果；数据库记录失败必须记录安全日志，
不能使 AI 业务调用伪装成功。

验收标准：

- 成功、provider 失败、schema 失败和异常路径均有确定性测试。
- 每次接入的 Gateway 调用能关联一个 Run。

### R2：最小 `ai_runs` 数据模型

首批字段覆盖：

- 身份与任务：`id`、`task_type`、`target_type`、`target_id`；
- 配置快照：`provider_used`、`model`、`prompt_version`；
- 生命周期：`status`、`validation_status`、`started_at`、`finished_at`、
  `latency_ms`；
- 安全快照：`input_summary`、`output_data`、`warnings`；
- 错误：`error_code`、`error_message_safe`；
- 重试：`attempt`、`parent_run_id`；
- 人工流转：`review_status`、`review_revision`、`reviewed_at`、
  `review_note`；
- 审计时间：`created_at`、`updated_at`。

首批不加入 model profile、routing rule、cost estimate 或 token cost 计算。

验收标准：

- migration 可 upgrade / downgrade；
- 状态、重试父链与常用筛选字段有约束或索引；
- 不保存密钥、cookie、Authorization 或图片 base64。

### R3：历史兼容

- 保留 `ai_call_logs` 表用于回滚和历史核对。
- 不把旧技术调用日志复制成业务 Run，避免混淆两类记录的语义。
- 新调用切换为写 `ai_runs` 后，不继续无期限双写。
- 旧 `/api/ai/call-logs` 在本批可保留为兼容读取，但新页面和新客户端使用 Run API。

验收标准：

- `ai_runs` migration 只创建新表，不读取、更新或重建 `ai_call_logs`；
- 旧表不被删除；
- 新旧响应合同不会被静默混用。

### R4：Run 查询 API

管理员 API：

- `GET /api/admin/ai/runs`
- `GET /api/admin/ai/runs/{run_id}`

列表支持 task type、status、validation status、review status 和时间倒序分页。
详情返回安全输入摘要、结构化输出、warnings、错误、重试链和人工状态。

验收标准：

- 未认证请求返回 401/403（遵循现有鉴权语义）；
- 不存在的 run 返回 404；
- 列表 DTO 不默认返回完整 `output_data`；
- 详情 DTO 不返回敏感原始输入。

### R5：安全重试

`POST /api/admin/ai/runs/{run_id}/retry` 以原 Run 的安全任务快照创建新 attempt。

规则：

- 新 Run 使用新 ID；
- `parent_run_id` 指向被重试 Run；
- attempt 单调递增；
- 不覆盖原 Run；
- 缺少可重放输入时返回明确 409，不猜测或补造输入。

验收标准：

- 重试链可查询；
- 并发重复请求不会覆盖历史；
- 未认证请求被拒绝。

### R6：人工接受/拒绝

`POST /api/admin/ai/runs/{run_id}/decision` 接受：

- `decision=accepted | rejected`
- `expected_revision`
- 可选 `note`

规则：

- 只有 `review_status=pending` 且 Run 已成功、校验未失败时可以决策；
- 使用 `expected_revision` 防止过期页面覆盖新决定；
- 重复提交同一决定可幂等返回现状；
- 冲突决定返回 409；
- 决策写入 `audit_logs`，记录 actor/session/action/entity/result；
- 接受动作不直接写正式业务实体。

验收标准：

- 接受、拒绝、重复、冲突、越权和非法状态均有测试；
- audit log 有对应 `ai_run.accept` / `ai_run.reject` 动作。

### R7：管理界面

在 `/manage/ai` 现有页面基础上提供：

- Run 状态、校验状态、Prompt 版本和人工状态筛选；
- Run 详情；
- 失败 Run 的重试入口；
- pending Run 的接受/拒绝入口；
- 明确提示“接受不会直接写入正式内容”。

验收标准：

- 页面受现有管理访问保护；
- 空、加载、错误、冲突状态可读；
- icon-only 按钮有 accessible name；
- TypeScript 和浏览器检查通过。

## 4. 非功能需求

### N1：安全与隐私

- Run 永远是管理员私有数据。
- 输入只保存脱敏摘要或允许重放的安全结构，不保存图片 base64。
- 错误消息使用安全字段，不保存 provider 原始敏感响应。
- output_data 仅在详情接口返回。

### N2：一致性

- Run 状态更新和人工决策使用数据库事务。
- 人工决策用 revision 做乐观并发控制。
- 重试不修改父 Run。

### N3：兼容性

- 不改变现有 AI 业务端点 response schema。
- 不改变 `AiTaskType` 字符串值。
- 不替换 Batch 10 的 validator 或手动 parser 行为。

### N4：可验证

- 模型、service、API、权限、迁移和前端类型均有相应验证。
- 自动化测试不得依赖真实 provider。
- 如未执行真实 provider，不得声称端到端生产审计已验证。

## 5. 不做事项

- 不实现成本、预算、token 计费或成本图表。
- 不实现模型 profile CRUD、路由规则 CRUD 或自动 provider 优化。
- 不实现 Prompt 后台编辑、A/B 或热更新。
- 不实现生产队列、worker、取消运行或实时协作。
- 不做 AI 自动采纳、自动发布或自动写正式业务实体。
- 不迁移公开路由体系或重构全部旧 AI 端点。
- 不进入 Batch 12。
