# 任务清单：Batch 5 附件基础系统

> 状态：用户已批准，按 P0-01 至 P0-09 顺序执行。

## P0-01 TDD、存储与迁移门禁

- [x] 建立 upload/list/detail/content/link 权限与失败路径 RED 测试。
- [x] inspect Alembic/current、uploads 目录、目标表、Batch 3/4 目标实体基线。
- 来源需求：REQ-B5-01、REQ-B5-03、REQ-B5-04、REQ-B5-06
- 涉及文件：`backend/tests/test_attachment_service.py`、`backend/tests/test_attachment_routes.py`、
  本 workflow `validation.md`
- 修改内容：先用纵向 TDD 固定权限、路径安全、字段泄露和关联约束；记录 014 前置状态。
- 完成标准：RED 原因明确；目标表不存在或可安全处理；上传目录策略和停止条件完整。
- 验证方式：pytest、Alembic current/history/heads、schema/data inspection、文件系统检查。
- 风险说明：若目标表、uploads 目录或约束已被其他 diff 创建且语义不一致，停止并申请范围扩大。
- 完成记录（2026-07-03）：新增附件 service/route RED 测试；失败原因为
  `ModuleNotFoundError: No module named 'app.schemas.attachment'`。Alembic current/heads 为
  `013 (head)`；目标表不存在；`backend/uploads/` 尚不存在且 `.gitignore` 尚未覆盖，将在 P0-02
  纳入实现。

## P0-02 新增模型、storage helper 与 Alembic 014

- [x] 新增 Attachment、AttachmentLink model 与 014 migration。
- 来源需求：REQ-B5-01、REQ-B5-04、REQ-B5-06
- 涉及文件：`backend/app/models/attachment.py`、models init、`backend/alembic/env.py`、
  `014_add_attachments.py`、上传目录 ignore。
- 修改内容：创建 `attachments`、`attachment_links`，配置 local storage root 与 opaque storage_key。
- 完成标准：013→014 正常；重复 upgrade 通过；DB 不包含绝对路径；真实上传内容不入 Git。
- 验证方式：migration、constraint/index/FK inspection、`git status`、路径字段审查。
- 风险说明：不引入对象存储，不创建 OCR/derivatives 表，除非 tasks 重新审批。
- 完成记录（2026-07-03）：新增 Attachment/AttachmentLink model、014 migration、UPLOAD_ROOT/
  MAX_UPLOAD_BYTES 配置与 `backend/uploads/.gitkeep`；`.gitignore` 忽略真实上传内容。013→014
  与重复 upgrade 通过，目标表为空，旧 notes 与 Batch 3/4 计数不变。

## P0-03 实现 Attachment service

- [x] 完成上传、元数据读取、私有 content 读取、软删除/缺失状态处理。
- 来源需求：REQ-B5-01、REQ-B5-02、REQ-B5-03、REQ-B5-06
- 涉及文件：attachment schema/service/storage helper 与定向测试。
- 修改内容：MIME/大小校验、sha256、临时文件写入与 rename、路径穿越防护、响应字段过滤。
- 完成标准：上传文件 hash 一致；匿名不可读；content 读取不接受任意 path；错误可分类。
- 验证方式：逐条 RED→GREEN、文件存在/缺失、响应字段断言。
- 风险说明：不让 `storage_key` 或绝对路径进入前端 DTO。
- 完成记录（2026-07-03）：实现 Attachment schema、storage helper 与 service；覆盖 MIME/大小/
  空文件、opaque storage_key、hash、缺失文件、deleted、路径穿越防护。定向 service 测试
  `5 passed`。

## P0-04 实现 AttachmentLink service

- [x] 完成关联、解除关联、目标附件查询和目标存在校验。
- 来源需求：REQ-B5-04、REQ-B5-05、REQ-B5-06
- 涉及文件：attachment link schema/service 与定向测试。
- 修改内容：支持 `question_draft | question | mistake` 目标；校验 purpose、重复关联、deleted 附件。
- 完成标准：关联只写 `attachment_links`；重复关联稳定 conflict；目标不存在稳定 404/400。
- 验证方式：service tests、目标表存在性断言、DB 行数断言。
- 风险说明：不把 owner_type/owner_id 写入 attachments。
- 完成记录（2026-07-03）：实现 AttachmentLink 创建、查询、解除、目标存在校验和重复关联
  service-level conflict；deleted 附件拒绝关联。定向 service 测试 `7 passed`。

## P0-05 实现 thin admin routers 与权限

- [x] 注册 `/api/admin/attachments` 与 `/api/admin/attachment-links`。
- 来源需求：REQ-B5-01 至 REQ-B5-06
- 涉及文件：新 routers、`backend/main.py`、路由合同测试。
- 修改内容：router 仅处理 HTTP 编排、multipart、状态码和 FileResponse；全部 endpoint 使用
  `get_current_admin`。
- 完成标准：匿名全部 401；OpenAPI 无 public attachment API；响应不含内部路径。
- 验证方式：route tests、HTTP anonymous/admin、FastAPI import。
- 风险说明：不得依赖前端隐藏入口或 AUTH_BYPASS 证明权限。
- 完成记录（2026-07-03）：新增 attachments router 与 attachment-links router，全部 admin-only；
  route 合同确认无 public attachment API。service+route 定向测试 `10 passed`，FastAPI import 成功。

## P0-06 实现前端 DTO/client

- [x] 新增 Attachment/AttachmentLink 显式类型与 API client。
- 来源需求：REQ-B5-01 至 REQ-B5-05
- 涉及文件：`src/lib/api/attachments.ts` 及必要复用类型。
- 修改内容：upload FormData、列表/详情/content URL、关联/解除关联；无 `any`。
- 完成标准：前后端字段一致；client 不暴露 storage_key；错误保留 ApiError 语义。
- 验证方式：TSC、合同检查、真实 API。
- 风险说明：不修改旧 notes API 或公开内容 DTO。
- 完成记录（2026-07-03）：新增 `src/lib/api/attachments.ts`，覆盖附件上传/读取/删除与
  attachment links；DTO 不暴露 `storage_key` 或本地路径。`npx tsc --noEmit` 通过。

## P0-07 实现 `/manage/attachments` 与详情预览

- [x] 升级附件管理占位页，新增详情路由与基础预览。
- 来源需求：REQ-B5-02、REQ-B5-03、REQ-B5-05
- 涉及文件：`src/app/manage/(workspace)/attachments/page.tsx`、`[id]`、components。
- 修改内容：上传表单、列表、详情 metadata、图片/PDF/text 基础预览或不可预览状态。
- 完成标准：桌面与移动端可完成上传、查看、预览/下载、删除/缺失错误展示。
- 验证方式：真实浏览器、console/network、移动视口。
- 风险说明：不接 OCR，不实现缩略图管线，不提交真实上传文件。
- 完成记录（2026-07-03）：实现附件上传/列表页与详情预览页，支持图片/PDF/text 基础预览和
  deleted/missing 状态提示。`npx tsc --noEmit` 与附件后端定向测试通过；真实浏览器验证将在
  P0-08/P0-09 合并记录。

## P0-08 实现基础关联 UI 并完成兼容回归

- [x] 提供附件与 question draft、question、mistake 的最小关联/解除入口。
- 来源需求：REQ-B5-04、REQ-B5-05、REQ-B5-06
- 涉及文件：附件详情或业务详情中的必要组件，原则上最小 diff。
- 修改内容：选择目标类型与 id/purpose 创建链接；查看目标现有关联；解除链接。
- 完成标准：至少一个稳定入口完成“上传 → 关联 → 查看关联 → 解除关联”；旧公开页面无回归。
- 验证方式：pytest、HTTP、TSC、build、browser、git diff。
- 风险说明：不重构草稿/题目/错题编辑器主体，不引入公开附件读取。
- 完成记录（2026-07-03）：在附件详情页实现最小关联/解除入口，支持 question_draft/question/
  mistake 与 source/question/answer/inline purpose；未改业务编辑器主体。TSC、build、附件后端测试通过。

## P0-09 审查、验证与移交

- [x] 创建 audit/validation，更新 checklist，填写 handoff，核对范围。
- 来源需求：全部
- 涉及文件：本 workflow 文档与 Batch 5 spec checklist/handoff。
- 修改内容：记录存储路径策略、模型、权限、API、页面、失败路径、风险和后置项。
- 完成标准：Batch 5 仅进入等待用户验收，不自动进入 Batch 6。
- 验证方式：全套证据与 `git diff --check`。
- 风险说明：任何路径泄露、匿名访问、真实上传内容入 Git 或公开回归都阻塞 Batch 6。
- 完成记录（2026-07-03）：`git diff --check` 通过；完成 audit/checklist/handoff/validation。
  Batch 5 等待用户验收，不自动进入 Batch 6。

## 执行顺序

严格按 P0-01 → P0-09；每完成一项立即更新本文件。

## 审批记录

- [x] 用户已于 2026-07-03 明确批准执行 Batch 5 tasks。
