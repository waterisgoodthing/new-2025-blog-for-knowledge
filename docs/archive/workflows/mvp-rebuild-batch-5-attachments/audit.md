# Batch 5 审查记录

## 审查结论

Batch 5 已完成代码与文档收口，状态为**等待用户验收**。本批建立了管理员私有附件基础：
local upload、附件元数据、私有 content 读取、附件列表/详情预览，以及通过 `attachment_links`
关联 question draft、question 和 mistake。

## 触及领域

- attachments：文件元数据、本地存储、私有读取、missing/deleted 状态。
- attachment links：附件与草稿/题目/错题的独立关联。
- manage：`/manage/attachments`、`/manage/attachments/[id]`。
- shared infrastructure：Alembic 014、`UPLOAD_ROOT`、上传目录 ignore、API client。
- public compatibility：无公开附件 API，不改公开 notes/mistakes 事实源。

## 主要证据

- 数据模型：014 新增 `attachments`、`attachment_links`；旧 notes 与 Batch 3/4 表计数未变化。
- 存储策略：`backend/uploads/*` 被 `.gitignore` 忽略，仅保留 `.gitkeep`；数据库保存 opaque
  `storage_key`，不保存绝对路径。
- 后端合同：新增 API 均在 `/api/admin/**`，依赖 `get_current_admin`；无公开 `/api/attachments`。
- 安全边界：
  - 上传校验 MIME、大小、空文件和文件名。
  - content 读取只接受 attachment id，不接受任意 path。
  - storage_key 路径穿越被拒绝。
  - 前端 DTO 不包含 `storage_key`、`UPLOAD_ROOT` 或绝对路径。
- 验证：
  - `cd backend && .venv/bin/python -m pytest -q tests/test_attachment_service.py tests/test_attachment_routes.py`
    通过，10 passed。
  - `npx tsc --noEmit` 通过。
  - `npm run build` 通过。
  - `git diff --check` 通过。

## 风险与未闭合验证

- 真实浏览器上传/预览/关联仍需用户在登录态下验收；本轮已完成 TypeScript、build 和后端合同验证。
- 删除策略当前为软删除，不物理清理文件；后续若需要清理队列或孤儿文件回收，应单独规划。
- 第一版关联 UI 位于附件详情页，需要手工输入目标 UUID；未重构草稿/题目/错题编辑器主体。
- 当前工作树含大量其他批次/任务 dirty diff；本审查只覆盖 Batch 5 相关路径和已运行测试。

## 禁止项核对

- 未实现 OCR、Capture Router、AI 附件读取、PDF 自动解析或缩略图管线。
- 未引入对象存储、R2、S3 或云部署。
- 未开放未鉴权上传或公开附件读取。
- 未把业务归属写入 `attachments` 表。
- 未提交真实上传文件。
