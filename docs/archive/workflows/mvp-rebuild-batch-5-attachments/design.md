# 设计文档：Batch 5 附件基础系统

## 1. 架构决定

采用“本地私有文件存储 + 独立附件元数据 + 独立关联表”：

```text
admin upload
  → storage helper validates type/size/hash
  → local uploads/<safe-key>
  → Attachment(private, storage_provider=local, storage_key=<opaque key>)
  → AttachmentLink(target_type, target_id, purpose)
  → admin preview/download
```

第一版不让附件成为公开内容库，也不把文件归属写入 `attachments`。同一附件可以被多个业务对象引用，
删除前必须检查引用关系，避免误删共享文件。

## 2. 数据设计

### `attachments`

- UUID id
- original_name：清洗后的原始文件名，仅用于展示
- storage_provider：第一版固定 `local`
- storage_key：不含绝对路径的 opaque key，唯一
- mime_type、size_bytes、checksum_sha256
- visibility：第一版默认 `private`
- status：`active | missing | deleted`
- created_by、created_at、updated_at、deleted_at

约束：

- `storage_key` unique。
- `size_bytes >= 0`。
- visibility 第一版只允许 `private`，若预留 public 也不得暴露公开读取 API。
- status check。

### `attachment_links`

- UUID id
- attachment_id FK
- target_type：`question_draft | question | mistake`
- target_id：目标 UUID 字符串
- purpose：`source | question | answer | inline | ai_input | ai_output`
- sort_order、created_at

约束：

- `(attachment_id, target_type, target_id, purpose)` unique。
- service 校验目标存在，不靠数据库跨表 polymorphic FK。
- 第一版只启用 `source/question/answer/inline`；AI purpose 仅作为后续兼容枚举，若实现需明确不触发 AI。

## 3. 存储策略

- 根目录建议为 `backend/uploads/`，由配置项控制，例如 `UPLOAD_ROOT`。
- 上传文件名不直接作为磁盘路径；使用 UUID/日期分片生成 `storage_key`。
- 写入流程使用临时文件 + fsync/rename，避免半文件记录。
- 数据库只保存 `storage_key`，读取时由 storage helper 解析为真实路径。
- `.gitignore` 必须忽略真实上传内容，例如 `backend/uploads/*`，但可保留 `backend/uploads/.gitkeep`。

## 4. API

全部 `/api/admin/**` 且依赖 `get_current_admin`：

- `POST /api/admin/attachments`：multipart upload，返回附件元数据。
- `GET /api/admin/attachments`：列表，支持简单分页/状态过滤。
- `GET /api/admin/attachments/{id}`：详情。
- `GET /api/admin/attachments/{id}/content`：私有读取/预览，返回受控文件响应。
- `DELETE /api/admin/attachments/{id}`：软删除或拒绝删除仍有关联的附件。
- `GET /api/admin/attachment-links?target_type=&target_id=`：查目标附件。
- `POST /api/admin/attachment-links`：创建关联。
- `DELETE /api/admin/attachment-links/{id}`：删除关联。

不新增 public attachment API。公开内容若未来需要附件，必须单独设计 public-safe DTO。

## 5. 页面

- `/manage/attachments`：上传表单、附件列表、状态/类型/大小、错误状态。
- `/manage/attachments/[id]`：元数据、预览区域、关联列表、删除/解除关联入口。
- 草稿、题目、错题管理详情：第一版只加入基础“关联附件”区域，允许选择已有附件并设置 purpose。

若直接把关联 UI 接到所有详情页导致 diff 过大，优先完成附件中心与 API，再在 tasks 中明确最小关联入口。

## 6. 权限与安全

- 上传、列表、详情、私有读取、关联、删除全部需要管理员。
- 未登录请求必须 401/403，不得因前端隐藏入口而取消后端权限。
- API 响应不得包含绝对路径、临时路径、`UPLOAD_ROOT` 或内部目录。
- 禁止路径穿越：读取只能通过 attachment id 和 storage helper，不接受任意 path 参数。
- 限制 MIME 与大小；第一版建议允许 PNG/JPEG/WebP/PDF/text，拒绝可执行/压缩包。
- 删除策略默认保守：有关联时拒绝物理删除；软删除只改变状态。

## 7. 验证策略

- TDD：先写 upload/list/detail/content/link 权限与失败路径测试。
- Alembic：从 013 到 014，检查表、约束、索引、重复 upgrade。
- 文件系统：验证上传文件存在、hash 一致、数据库不含绝对路径。
- HTTP：匿名全部拒绝；管理员上传/预览/关联可用。
- 前端：TSC、build、管理页面浏览器检查。

## 8. 暂缓

OCR、Capture Router、PDF 自动解析、缩略图/派生文件管线、对象存储/R2、公开媒体库、
云部署、附件全文检索、AI 读取附件、批量导入。
