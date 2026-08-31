# Batch 5 验证记录

## 当前状态

执行中；中间证据不代表 Batch 5 已验收。

## P0-01 TDD、存储与迁移门禁

- 用户于 2026-07-03 明确批准 Batch 5 tasks。
- RED：`ModuleNotFoundError: No module named 'app.schemas.attachment'`，与附件 schema/router 尚未实现一致。
- Alembic current/heads：`013 (head)`。
- 目标表检查：`attachments`、`attachment_links` 均不存在。
- 数据基线：
  - notes=13
  - draft_items=0
  - question_drafts=0
  - questions=0
  - mistake_drafts=0
  - mistakes=0
  - review_items=0
  - review_records=0
- 上传目录基线：未发现 `backend/uploads/`。
- `.gitignore` 基线：仅已有 `/public/images/pictures/` runtime uploads 规则，尚未覆盖 `backend/uploads/*`。
- Alembic 运行说明：当前环境需在 `backend/` 下使用 `PYTHONPATH=.` 调用 `.venv/bin/alembic`。

## P0-02 模型、storage 配置与 014

- 新增 `Attachment`、`AttachmentLink` model，并加入 Alembic metadata import。
- 新增配置：
  - `UPLOAD_ROOT` 默认指向 `backend/uploads`
  - `MAX_UPLOAD_BYTES` 默认 10 MiB
- 新增 `.gitignore` 规则：`backend/uploads/*`，保留 `backend/uploads/.gitkeep`。
- 新增 Alembic `014_add_attachments.py`。
- `013 -> 014` 正常；current=`014 (head)`；重复 upgrade 通过。
- schema inspection：
  - `attachments` 13 列，含 `storage_provider/storage_key/mime_type/size_bytes/checksum_sha256/visibility/status`
  - `attachment_links` 7 列，含 `(attachment_id,target_type,target_id,purpose)` unique
  - check constraints 覆盖 local provider、private visibility、状态、大小、checksum、target_type、purpose。
- 数据计数：notes=13；Batch 3/4 相关表仍为 0；attachments=0；attachment_links=0。

## P0-03 Attachment service

- 新增 Attachment schema 与 service/storage helper。
- upload 行为：
  - 清洗原始文件名，拒绝路径型文件名与不支持 MIME。
  - 校验非空与 `MAX_UPLOAD_BYTES`。
  - 写入 local uploads，生成 opaque `storage_key`，不保存绝对路径。
  - 计算 `checksum_sha256`，默认 `storage_provider=local`、`visibility=private`、`status=active`。
- content 行为：
  - 仅通过 attachment id + storage helper 解析文件路径。
  - storage_key 路径穿越会被拒绝。
  - 文件缺失时标记 `missing`，错误信息不包含 upload root。
  - `deleted` 附件不可读取。
- 定向验证：`cd backend && .venv/bin/python -m pytest -q tests/test_attachment_service.py`
  通过，`5 passed in 0.26s`。

## P0-04 AttachmentLink service

- 新增 AttachmentLink service 行为：
  - 支持 `question_draft | question | mistake` 目标类型。
  - 创建前校验附件存在且 `status=active`。
  - 创建前校验目标实体存在。
  - 创建前先查重复关联，返回 stable conflict，避免数据库 IntegrityError 破坏当前事务。
  - 支持按 target 或 attachment 查询关联。
  - 支持解除关联。
- 失败路径：
  - 缺失目标返回 AttachmentNotFound。
  - deleted/missing 附件拒绝关联并返回 AttachmentConflict。
  - 重复关联返回 AttachmentConflict。
- 定向验证：`cd backend && .venv/bin/python -m pytest -q tests/test_attachment_service.py`
  通过，`7 passed in 0.33s`。

## P0-05 Admin routers 与权限

- 新增 `backend/app/routers/attachments.py`：
  - `GET/POST /api/admin/attachments`
  - `GET/DELETE /api/admin/attachments/{attachment_id}`
  - `GET /api/admin/attachments/{attachment_id}/content`
  - `GET/POST /api/admin/attachment-links`
  - `DELETE /api/admin/attachment-links/{link_id}`
- 已在 `backend/main.py` 注册 router。
- 全部新增路由统一依赖 `get_current_admin`。
- route 合同确认不存在公开 `/api/attachments`。
- FastAPI import 成功，当前 routes=163。
- 定向验证：`cd backend && .venv/bin/python -m pytest -q tests/test_attachment_service.py tests/test_attachment_routes.py`
  通过，`10 passed in 0.57s`。

## P0-06 前端 DTO/client

- 新增 `src/lib/api/attachments.ts`。
- DTO 覆盖 Attachment 与 AttachmentLink；不包含 `storage_key`、`UPLOAD_ROOT`、绝对路径或临时路径。
- client 覆盖上传、列表、详情、content URL、删除、链接查询、创建和删除。
- upload 使用 FormData，并沿用 `apiFetch` 的 credentials/error 语义。
- `npx tsc --noEmit`：通过，无 TypeScript 错误。

## P0-07 `/manage/attachments` 与详情预览

- `/manage/attachments` 已替换占位页，支持上传文件、按状态筛选附件列表、刷新列表。
- `/manage/attachments/[id]` 已新增详情页，展示元数据、图片/PDF/text 基础预览、新窗口打开与标记删除。
- 页面继承 `/manage/(workspace)` AuthGate；未新增公开附件页面。
- `npx tsc --noEmit`：通过。
- 附件后端定向测试仍通过：`10 passed in 0.54s`。

## P0-08 基础关联 UI 与兼容回归

- 在 `/manage/attachments/[id]` 新增最小 attachment links 关联区：
  - 选择 `question_draft | question | mistake`
  - 输入目标 UUID
  - 选择 `source | question | answer | inline`
  - 创建关联、列出现有关联、解除关联
- 未改草稿/题目/错题编辑器主体，避免与业务编辑器重构混在一个 diff。
- `npx tsc --noEmit`：通过。
- 附件 service+route 定向测试：`10 passed in 0.54s`。
- `npm run build`：通过。非阻塞警告：
  - `baseline-browser-mapping` 数据超过两个月。
  - Node `[DEP0205] module.register()` deprecation warning。

## P0-09 审查、验证与移交

- `git diff --check`：通过。
- `rg` 检查：
  - 前端 DTO 不包含 `storage_key`。
  - 未发现公开 `/api/attachments`。
  - 新路由均为 `/api/admin/attachments` 或 `/api/admin/attachment-links`。
  - `backend/uploads/*` 已被 `.gitignore` 忽略，仅保留 `.gitkeep`。
- 已更新：
  - `audit.md`
  - `docs/specs/mvp-rebuild/batch-5-attachments/checklist.md`
  - `docs/specs/mvp-rebuild/batch-5-attachments/handoff.md`
- Batch 5 当前状态：等待用户验收；不自动进入 Batch 6。
