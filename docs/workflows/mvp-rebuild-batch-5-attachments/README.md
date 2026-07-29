# MVP Rebuild Batch 5：附件基础系统

## 任务目标

在不引入 OCR、对象存储或云部署的前提下，建立管理员私有附件基础：本地上传、元数据、
私有读取、附件列表/详情预览，以及通过 `attachment_links` 关联 question draft、question
和 mistake。

## 涉及领域

- attachments：文件元数据、local storage、私有读取、删除/缺失文件处理
- attachment links：附件与草稿、题目、错题的独立关联
- manage：`/manage/attachments`、`/manage/attachments/[id]` 与必要关联 UI
- shared infrastructure：Alembic 014、上传目录 ignore、API client、权限与验证
- public compatibility：不新增公开附件库，不向公开 API 泄露 `storage_key` 或本地路径

## 当前状态

**Batch 5 已完成实现与文档收口，等待用户验收。**

本批不自动进入 Batch 6；进入下一批前需要用户明确确认。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)
- [验证记录](./validation.md)
- [审查记录](./audit.md)

Batch 5 checklist 与 handoff 位于 `docs/specs/mvp-rebuild/batch-5-attachments/`。

## 已确认起点

- Batch 4 已由用户确认关闭，可以进入 Batch 5 workflow 准备。
- `/manage/attachments` 目前来自 Batch 1 UI shell，仍是占位能力。
- Batch 5 只做本地私有附件基础；OCR、PDF 自动解析、复杂缩略图、对象存储、R2、云部署均后置。
- 附件默认 private；上传、读取私有文件、关联和删除必须由管理员权限保护。

## 核心边界

- `attachments` 只保存文件本体元数据与抽象存储引用，不保存业务归属字段。
- 业务归属只通过 `attachment_links(attachment_id,target_type,target_id,purpose)` 表达。
- 数据库和 API 不返回绝对本地路径、临时路径或内部目录结构。
- 不提交真实上传文件；仅允许 `.gitkeep` 或测试 fixture（如需要）进入仓库。
