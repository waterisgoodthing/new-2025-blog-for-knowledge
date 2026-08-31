# 目标 API 设计

> 本文描述拟新增目标契约，不表示当前 `/api/notes` 等接口已完成迁移。

## API 分层

目标 API 使用两个清晰命名空间：

- `/api/public/**`：无需登录，只读，强制过滤公开且已发布的数据。
- `/api/admin/**`：后端强制管理员鉴权，承载管理读取和全部状态修改。

所有列表使用统一分页结构：`items`、`page`、`page_size`、`total`。错误使用稳定的 `code`、可读 `message` 和 `request_id`。写操作支持版本号或 `If-Match` 以避免覆盖并发编辑。

## Public API

| 方法与路径 | 功能域 | 行为 |
|---|---|---|
| `GET /api/public/posts` | Content Publishing | 返回已发布公开文章列表 |
| `GET /api/public/posts/{slug}` | Content Publishing | 返回单篇公开文章；不可见时 404 |
| `GET /api/public/notes` | Knowledge Notes | 返回已发布公开笔记列表 |
| `GET /api/public/notes/{slug}` | Knowledge Notes | 返回单篇公开笔记；不可见时 404 |
| `GET /api/public/mistakes` | Mistake System | 返回已发布公开错题列表 |
| `GET /api/public/mistakes/{slug}` | Mistake System | 返回单条公开错题；不可见时 404 |
| `GET /api/public/search` | Search | 仅检索公开且已发布内容 |

Public DTO 不包含内部状态、AI 输入、审计字段、附件存储键、复习调度或管理员标识。列表接口允许受控的 tag、subject、knowledge point、分页和排序参数。

## Admin 内容 API

每种实体还应具备 `GET /api/admin/{resource}` 与 `GET /api/admin/{resource}/{id}`，以支持草稿、隐藏内容和管理详情。

| 方法与路径 | 说明 |
|---|---|
| `POST /api/admin/posts` | 创建文章 |
| `PUT /api/admin/posts/{id}` | 更新文章 |
| `DELETE /api/admin/posts/{id}` | 软删除或归档文章 |
| `POST /api/admin/notes` | 创建笔记 |
| `PUT /api/admin/notes/{id}` | 更新笔记 |
| `DELETE /api/admin/notes/{id}` | 软删除或归档笔记 |
| `POST /api/admin/mistakes` | 创建错题 |
| `PUT /api/admin/mistakes/{id}` | 更新错题 |
| `DELETE /api/admin/mistakes/{id}` | 软删除或归档错题 |

创建成功返回 201 和完整 admin DTO；更新返回 200；删除建议返回 204。slug 冲突返回 409，版本冲突返回 409/412，校验失败返回 422。删除前应检查 Review、Attachment 和 AI Run 关系，并执行既定软删除策略。

## Review API

| 方法与路径 | 行为 |
|---|---|
| `GET /api/admin/review/queue` | 按 due time、subject 等返回当前队列 |
| `POST /api/admin/review/records` | 提交一次复习并原子更新状态与 schedule |
| `GET /api/admin/review/stats` | 返回时间、学科、知识点维度统计 |

`POST /records` 输入至少包含 `review_item_id`、`rating`、`reviewed_at` 和可选 `duration_ms`。服务端必须在一个事务中锁定 Review Item、写入不可变 Record、更新 Item、消费旧 Schedule 并生成新 Schedule。客户端不能直接提交 `ease_factor` 或 `next_review` 作为权威结果。

可补充：

- `POST /api/admin/review/items`：将 Note/Mistake 纳入复习。
- `PATCH /api/admin/review/items/{id}`：暂停、恢复或完成。
- `GET /api/admin/review/items/{id}/records`：读取历史。

## Question API

| 方法与路径 | 行为 |
|---|---|
| `GET /api/admin/questions` | 查询管理员私有题库 |
| `GET /api/admin/questions/{id}` | 读取题目本体、来源和关联摘要 |
| `POST /api/admin/questions` | 创建题目 |
| `PUT /api/admin/questions/{id}` | 更新题目 |
| `DELETE /api/admin/questions/{id}` | 软删除或归档题目 |

删除前必须检查 Practice Attempt、Mistake 与 Review 引用；题目去重或合并必须保留来源映射与审计，不能仅凭 AI 相似度静默合并。

## Practice API

| 方法与路径 | 行为 |
|---|---|
| `GET /api/admin/practice-sessions` | 查询练习记录 |
| `GET /api/admin/practice-sessions/{id}` | 读取一次练习及汇总 |
| `POST /api/admin/practice-sessions` | 创建练习 |
| `PUT /api/admin/practice-sessions/{id}` | 更新练习元数据或受控状态 |
| `DELETE /api/admin/practice-sessions/{id}` | 取消、归档或按策略删除练习 |
| `GET /api/admin/practice-sessions/{id}/attempts` | 查询逐题作答 |
| `POST /api/admin/practice-sessions/{id}/attempts` | 添加逐题作答 |
| `PUT /api/admin/practice-attempts/{id}` | 修正一次作答 |
| `DELETE /api/admin/practice-attempts/{id}` | 删除一次作答并重算汇总 |
| `GET /api/admin/practice-sessions/{id}/report` | 读取练习报告 |
| `POST /api/admin/practice-sessions/{id}/report` | 创建或重新生成可追踪报告 |

Practice Attempt 是一次作答事实；Practice Report 是分析结果或建议，不直接改变正式复习计划。

## Practice Import API

| 方法与路径 | 行为 |
|---|---|
| `POST /api/admin/practice-import-jobs` | 创建 Practice Session 与导入任务 |
| `GET /api/admin/practice-import-jobs/{id}` | 查询导入状态、进度、警告和错误 |
| `POST /api/admin/practice-import-jobs/{id}/files` | 上传或关联导入文件 |
| `POST /api/admin/practice-import-jobs/{id}/analyze` | 启动可追踪的识别、拆题和批改 |
| `POST /api/admin/practice-import-jobs/{id}/confirm` | 确认结构化结果并生成正式题目、作答和草稿 |

多题上传、批量识别和练习分析统一走 Practice Import，不再走 Mistake API。分析必须创建 `ai_runs`，并关联 Practice Import Job、Practice Session、Practice Attempt 或 Mistake Draft；确认端点必须校验版本，避免把过期 AI 输出覆盖人工修正。

## Mistake Draft API

| 方法与路径 | 行为 |
|---|---|
| `GET /api/admin/mistake-drafts` | 查询待确认错题草稿 |
| `GET /api/admin/mistake-drafts/{id}` | 读取草稿、来源、置信度和警告 |
| `PUT /api/admin/mistake-drafts/{id}` | 人工修正草稿 |
| `POST /api/admin/mistake-drafts/{id}/convert` | 经用户确认，幂等转换为正式 Mistake |
| `POST /api/admin/mistake-drafts/{id}/reject` | 拒绝候选并保留审计 |

Mistake API 只处理正式错题和单题错题导入。AI 输出不是正式错题，必须经过用户确认后才能转换为 Mistake；加入 Review Item 也必须是独立、可审计的业务动作。

## AI API

| 方法与路径 | 行为 |
|---|---|
| `POST /api/admin/ai/runs` | 创建可追踪 AI 任务，返回 202 或同步完成结果 |
| `GET /api/admin/ai/runs` | 筛选运行列表 |
| `GET /api/admin/ai/runs/{id}` | 查询模型、路由、Prompt、校验、成本和错误 |
| `POST /api/admin/ai/runs/{id}/retry` | 以原运行快照创建新 attempt |

创建参数包括 `task_type`、`target_type`、`target_id`、结构化 input 和 `idempotency_key`。响应始终包含 run ID 与状态。

“分析错题”“识别练习”“生成图解”等快捷接口可以存在，例如 `POST /api/admin/mistakes/{id}/analyze`，但它们只能是编排入口：底层必须创建 `ai_runs`，返回 run ID，并把重试、错误、模型与结果纳入同一生命周期。`ai_service` 只负责模型调用，不直接写正式业务数据；快捷接口不得把输出只写回自由 JSON 而不留运行记录。

旧 `/api/admin/ai-runs` 如在迁移期保留，只能兼容转发至 `/api/admin/ai/runs`，不得出现在新客户端或目标契约中。

## Attachments 与 Taxonomy API

建议的 admin API：

- `POST /api/admin/attachments`：申请上传或接收上传，校验类型与大小。
- `GET /api/admin/attachments`、`DELETE /api/admin/attachments/{id}`。
- `GET/POST/PUT /api/admin/tags`。
- `GET/POST/PUT /api/admin/subjects`。
- `GET/POST/PUT /api/admin/knowledge-points`。
- `POST/DELETE /api/admin/knowledge-links`。

对公开内容返回附件时，只输出可公开 URL 和展示元数据，不输出 `storage_key`、本地路径或临时上传信息。

`attachments` API 只创建和读取文件本体元数据。附件与业务对象的关联统一通过 `/api/admin/attachment-links` 或领域内受控关联命令写入 `attachment_links.target_type/target_id`；不得在 `attachments` 中保存业务对象引用。

## 学习系统 Admin API 模块

第一版目标命名空间：

- `/api/admin/subjects/**`、`/api/admin/taxonomy/**`
- `/api/admin/questions/**`、`/api/admin/practice/**`、`/api/admin/mistakes/**`、`/api/admin/review/**`
- `/api/admin/attachments/**`、`/api/admin/ocr/**`、`/api/admin/capture/**`
- `/api/admin/ai/**`、`/api/admin/drafts/**`、`/api/admin/jobs/**`
- `/api/admin/search`、`/api/admin/analytics/**`、`/api/admin/reports/**`、`/api/admin/settings/**`

| 方法与路径 | 行为 |
|---|---|
| `POST /api/admin/attachments` | 创建私有附件或上传会话 |
| `POST /api/admin/ocr/jobs` | 对附件创建 OCR job |
| `POST /api/admin/capture/jobs` | 对 OCR/附件创建分类 job |
| `GET /api/admin/drafts` | 查询统一草稿队列 |
| `PUT /api/admin/drafts/{id}` | 修正草稿并进行类型化校验 |
| `POST /api/admin/drafts/{id}/convert` | 幂等确认并通过领域 service 写正式表 |
| `GET /api/admin/jobs/{id}` | 查询步骤、进度和安全日志 |
| `POST /api/admin/jobs/{id}/retry` | 按策略创建重试 attempt |
| `GET /api/admin/analytics/overview` | 返回确定性计算指标 |
| `GET/PUT /api/admin/settings/{section}` | 读取或更新类型化设置 |

## AI / OCR / Capture 写入边界

OCR 输出只能写 `ocr_results/ocr_blocks`，Capture Router 只能写 `capture_results` 和草稿，AI 只能写 `ai_runs`、草稿、建议、报告或分析。三者不得直接写 `questions`、`mistakes`、`practice_attempts`、`knowledge_points`、`review_items` 或 mastery。正式入库统一经过 draft conversion 或显式领域命令，并写审计。

所有 AI/OCR/Capture 业务候选必须先创建 `draft_items`，再创建包含 `draft_item_id` 的类型化草稿；不得直接从运行结果转换正式表。

Practice Attempt 的权威结果字段为 `result_type`，枚举为 `correct`、`wrong`、`partial`、`unknown`、`skipped`。创建与更新 Attempt 的 API 必须校验该枚举；`is_correct` 只可作为旧兼容派生字段。

## 兼容旧 API

当前 `GET/POST/PUT/DELETE /api/notes` 及既有 AI/复习接口在迁移期仍可能承担生产能力。目标 `/api/public/**` 和 `/api/admin/**` 上线前，应保持旧契约可用并逐调用方切换；不得仅凭本文档删除旧 API。

## 一致性与安全

- 所有 admin 写请求都写入 `audit_logs`。
- POST 创建类操作支持 `Idempotency-Key`。
- 业务实体、附件、AI Run 与 Review 更新使用数据库事务。
- public 与 admin 使用不同响应 schema，不能依靠前端删字段。
- 搜索、排序字段使用白名单；分页设最大值。
- AI、上传等高成本接口增加速率限制、大小限制和超时。
