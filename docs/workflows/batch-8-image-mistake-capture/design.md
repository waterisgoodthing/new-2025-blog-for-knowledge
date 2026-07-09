# 设计文档：Batch 8 图片错题采集与 AI 错因草稿

## 1. 总体架构

```text
admin capture page
  → existing attachment upload
  → Attachment(private)
  → AttachmentLink(target_type=capture_item, purpose=source)
  → CaptureItem
      → OCR / multimodal adapter
      → editable recognized_text
      → minimal AI draft adapter + schema validation
      → editable question/analysis/error/knowledge suggestions
  → explicit "生成错题草稿"
  → existing MistakeDraft
  → existing manual confirmation
  → existing Mistake
  → existing ReviewItem
```

Batch 8 新增的唯一候选业务实体是 `capture_items`。它是采集过程工作区，不是正式错题事实源。
附件、错题草稿、正式错题、复习项、科目和知识点均复用现有系统。

## 2. 数据设计

### `capture_items` 候选字段

- `id`：UUID。
- `status`：`uploaded | recognizing | recognized | drafting | ready | failed | converted | archived`。
- `attachment_id`：来源原图引用；实现时优先评估是否只通过扩展后的 `attachment_links` 表达，
  避免双重归属。最终方案在 P0-02 审计后确定。
- `recognized_text`：可人工编辑的 OCR/多模态文本。
- `user_error_context`：用户补充“我当时为什么错”。
- `question_draft_text`：AI 建议题面。
- `analysis_draft_text`：AI 建议解析。
- `error_summary_draft`：AI 建议错因总结。
- `subject_id`：可空建议/人工选择。
- `knowledge_point_suggestions`：建议 ID 与必要的显示快照；正式关联仍复用既有知识点关联机制。
- `model_output_version`：仅用于区分 Batch 8 固定输出 schema 版本，不是 Prompt 管理系统。
- `attempt_count`、`last_stage`、`error_code`、`error_message_safe`。
- `started_at`、`finished_at`、`created_by`、`created_at`、`updated_at`。
- `mistake_draft_id`：转换成功后保存目标引用，用于幂等与跳转。

约束建议：

- 一个 capture item 只对应一个主原图和至多一个已转换 `mistake_draft`。
- `mistake_draft_id` unique（非空时）。
- `converted` 必须有 `mistake_draft_id`。
- 错误字段只保存安全摘要，不保存密钥或完整供应商响应。
- 删除/归档 capture 不级联删除原图或已生成的业务对象。

### 附件关联

实施时可扩展 `attachment_links.target_type` 支持 `capture_item`，以
`purpose=source` 连接原图。若既有约束不允许安全扩展，P0-02 必须记录最小兼容方案。
原图的 `visibility` 始终为 `private`，读取继续走既有管理员附件接口。

## 3. AI/OCR 调用边界

Batch 8 只定义两个窄接口：

```text
recognize_image(attachment) -> RecognitionResult
draft_mistake(CaptureDraftInput) -> MistakeDraftSuggestionV1
```

要求：

- 供应商细节封装在小型 adapter 内，不进入 capture service、router 或前端 DTO。
- 第一版允许同步请求或进程内轻量后台执行，但必须有明确超时；不建设生产级队列。
- 不建设模型路由、多供应商配置、Prompt 后台、成本核算或完整 run 审计。
- Batch 9 可在不改变 capture 领域合同的前提下替换 adapter。

## 4. AI 输出 schema

`MistakeDraftSuggestionV1` 最小结构：

```text
question_text: string
analysis_text: string
error_summary: string
subject_suggestion: { id?: number, label?: string, confidence?: number } | null
knowledge_point_suggestions: Array<{ id?: number, label: string, confidence?: number }>
warnings: string[]
```

所有文本字段进入 capture 草稿区并允许编辑。schema 校验失败视为本次 AI 阶段失败，不得把非结构化
响应直接写入 `mistake_drafts`。置信度仅供提示，不自动完成正式关联。

## 5. 状态机与失败隔离

```text
uploaded
  → recognizing → recognized
  → drafting → ready
  → converted

recognizing / drafting → failed → manual retry → corresponding processing state
ready → edit → ready
```

- 上传失败：不创建 capture item，或由事务/补偿清理孤立记录。
- 识别失败：capture 保持 failed；`mistake_drafts`、`mistakes`、`review_items` 零写入。
- AI 失败：保留识别文本和用户补充；下游零写入。
- 转换失败：capture 保持 ready/failed-conversion 可重试；转换事务回滚。
- 重复转换：通过 `mistake_draft_id` 与服务幂等检查返回既有结果。

实现阶段可细化状态字段，但不得用一个模糊状态掩盖当前失败阶段。

## 6. capture → mistake_draft 转换

转换必须是显式管理员动作：

1. 校验 capture 为 `ready`，必填文本、subject 和知识点引用有效。
2. 使用既有 mistake draft service/schema 创建草稿；不直接创建正式 mistake。
3. 建立原图到 `mistake_draft` 的 `attachment_link`，保留 capture 来源引用。
4. 在同一事务中写入 `mistake_draft_id` 并把 capture 标记为 `converted`。
5. 返回草稿地址，交给 `/manage/mistakes` 继续人工检查和确认。

正式 `mistake` 和 `review_item` 的生成继续完全由既有流程负责。

## 7. 管理端页面

入口在 P0-06 二选一后冻结：

- `/manage/capture`：采集作为独立高频工作台；或
- `/manage/mistakes/capture`：强调它是错题管理的子流程。

最小页面区块：

- 单图上传与原图预览。
- 识别/AI 阶段状态。
- “我当时为什么错”输入。
- 可编辑题面、解析、错因。
- subject 选择、knowledge point 建议与人工选择。
- 失败提示和手动重试。
- “生成 mistake draft”确认按钮。
- 转换后跳转 `/manage/mistakes` 或具体草稿。

不提供批量上传、PDF 拆页、公开分享或自动确认。

## 8. API 候选合同

全部位于 `/api/admin/**` 并依赖 `get_current_admin`：

- `POST /api/admin/captures`：用已上传 attachment id 创建 capture，或采用单一编排上传入口。
- `GET /api/admin/captures`：最小列表/状态过滤。
- `GET /api/admin/captures/{id}`：详情与可编辑草稿。
- `PATCH /api/admin/captures/{id}`：更新识别文本、用户补充和人工编辑字段。
- `POST /api/admin/captures/{id}/recognize`：触发/重试识别。
- `POST /api/admin/captures/{id}/draft`：触发/重试 AI 草稿。
- `POST /api/admin/captures/{id}/convert`：幂等生成 `mistake_draft`。

具体路径、请求响应与错误码在 P0-03 至 P0-05 审批后冻结。router 只做权限、schema、状态码和服务编排。

## 9. 权限与公开边界

- capture 页面必须使用既有管理端 AuthGate/布局。
- capture、识别、AI 草稿、转换、私有附件读取全部后端 admin-only。
- 不使用 `AUTH_BYPASS` 作为正常权限验证手段。
- 公开 `/blog`、`/notes`、`/mistakes` 不加载 capture 或管理员 AI/OCR API。
- 不增加公开 capture API，不把 AI/OCR 字段加入公开 DTO。
- 已保存到正式 mistake 的人工确认内容是否公开，继续服从既有 mistake 发布规则；原始 capture 与 AI
  中间结果永不随之公开。

## 10. 最小运行记录

Batch 8 只在 capture item 上记录阶段、状态、次数、时间和安全错误摘要。可选增加一个极小的
`capture_attempts` 方案仅在 P0-02/P0-03 证明单行状态不足时提出，并需要重新确认范围。
完整 Task/Prompt/Validator、AI Run 审计和人工流转分别留给 Batch 10–11。

## 11. Batch 9–12 接口预留

- Batch 9 可用统一 gateway adapter 替换 Batch 8 的窄调用接口。
- Batch 10 可为固定 task、prompt、validator 增加版本实体，而不改变 capture 输出语义。
- Batch 11 可把最小运行记录升级为独立 AI run 与人工流转。
- Batch 12 可在 gateway 内加入多供应商、路由、成本和稳定性治理。

预留接口不等于提前建表或实现；Batch 8 不包含上述治理能力。

## 12. 验证设计

- 后端：状态机、失败零污染、转换幂等、权限、schema 校验、附件关联。
- 合同：前后端 DTO 与固定 AI 输出 schema 对齐。
- 数据库：迁移、约束、回滚、孤儿链接、原有数据计数不变。
- 前端：TSC、build、桌面/移动真实浏览器单图闭环。
- 安全：匿名 401/403、private 原图、无路径/密钥/供应商原始响应泄露。
- 回归：既有 `/manage/mistakes`、`/manage/attachments`、复习链和公开页面不回归。
