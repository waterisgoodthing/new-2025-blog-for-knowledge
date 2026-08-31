# Handoff

## 本批完成内容

- 建立管理员私有附件基础：
  - local upload
  - Attachment 元数据
  - 私有 content 读取
  - missing/deleted 状态
  - attachment links 独立关联
- `/manage/attachments` 支持上传、列表、状态筛选。
- `/manage/attachments/[id]` 支持元数据展示、图片/PDF/text 基础预览、新窗口打开、软删除、
  创建/查看/解除 attachment links。
- 新 API 全部为 `/api/admin/**`，无 public attachment API。

## 修改文件

- workflow：`docs/workflows/mvp-rebuild-batch-5-attachments/`
- spec：`docs/specs/mvp-rebuild/batch-5-attachments/`
- 后端：
  - `backend/alembic/versions/014_add_attachments.py`
  - `backend/app/models/attachment.py`
  - `backend/app/schemas/attachment.py`
  - `backend/app/services/attachment_service.py`
  - `backend/app/routers/attachments.py`
  - `backend/app/config.py`
  - `backend/app/models/__init__.py`
  - `backend/alembic/env.py`
  - `backend/main.py`
  - `backend/tests/test_attachment_service.py`
  - `backend/tests/test_attachment_routes.py`
- 前端：
  - `src/lib/api/attachments.ts`
  - `src/app/manage/(workspace)/attachments/page.tsx`
  - `src/app/manage/(workspace)/attachments/[id]/page.tsx`
  - `src/app/manage/(workspace)/attachments/components/attachment-workspace.tsx`
  - `src/app/manage/(workspace)/attachments/components/attachment-detail.tsx`
- 存储/ignore：
  - `.gitignore`
  - `backend/uploads/.gitkeep`

## 未完成事项

- 真实浏览器登录态验收仍待用户执行或确认。
- 关联 UI 第一版需要手工输入目标 UUID；未嵌入草稿/题目/错题编辑器主体。
- OCR、Capture Router、AI 附件读取、PDF 自动拆页、复杂缩略图、对象存储、R2、云部署均保持后置。
- 旧 Note 图片迁移到 attachments 不属于本批。

## 风险点

- 路径穿越已在 service 测试覆盖；后续改 storage helper 时必须保留该约束。
- 当前删除为软删除，不物理清理文件；孤儿文件回收需要后续清理策略。
- `backend/uploads` 是本地运行数据，备份/恢复策略需在真正导入私人材料前明确。
- 后续若公开附件，必须新增 public-safe DTO，不能复用 admin API。

## 下一批前置条件

- 用户验收 Batch 5。
- 如需浏览器证据，补跑登录态 `/manage/attachments` 上传、预览、关联/解除、移动视口与 console/network。
- 用户明确批准进入 Batch 6。

## 用户确认

- [x] 用户已确认可以进入下一批（2026-07-03：Batch 5 可以关闭，进入 Batch 6 workflow 准备阶段）
