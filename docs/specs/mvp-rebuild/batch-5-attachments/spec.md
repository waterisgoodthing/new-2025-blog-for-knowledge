# Batch 5：附件基础系统

## 目标

让草稿、题目和错题能够安全关联原始材料。

## 背景

MVP 只需要可恢复、可授权的本地附件基础，不需要 OCR、缩略图管线、对象存储或
云部署。上传属于管理员写入，读取必须遵守 private 默认值。

## 任务范围

1. 支持管理员本地附件上传。
2. 保存文件元数据及 `storage_provider`、`storage_key`。
3. 提供附件列表与详情预览。
4. 支持附件关联 question draft、question 和 mistake。
5. 附件默认 private。
6. 第一版文件存储使用 local `uploads/`，并明确不提交真实上传内容。
7. 使用独立 attachment links 表达业务归属，不把归属字段写死在 attachments。

## 允许修改范围

- 本批对应 workflow 与必要架构文档。
- 经批准的附件模型、schema、service、router、migration、存储 helper 与测试。
- 对应 `src/lib/api/` 客户端。
- `/manage/attachments` 路由、专属组件和必要的关联选择 UI。
- 上传目录忽略规则及本批验证材料，但不得提交真实私人附件。

## 禁止事项

- 不做 OCR、PDF 自动解析或复杂缩略图管线。
- 不做对象存储或 Cloudflare R2。
- 不做云部署。
- 不开放未鉴权上传。
- 不泄露本地路径、临时路径或内部存储细节。
- 不把业务归属写死在 attachments 表。

## 涉及页面

- `/manage/attachments`
- `/manage/attachments/[id]`
- 草稿、题目、错题管理详情中的基础附件关联区域。

## 涉及数据表

- `attachments`
- `attachment_links`

## 验收标准

1. 管理员可以上传并查看附件。
2. 附件列表和详情预览可用。
3. 附件可关联草稿、题目和错题。
4. 附件默认 private，未登录用户不能上传或读取私有附件。
5. 数据库只保存抽象存储信息，不泄露绝对本地路径。
6. 业务归属只通过 attachment links 表达。
7. 上传失败、无权限、文件不存在与不支持预览均有明确处理。

## 非目标

OCR、缩略图服务、PDF 解析、对象存储、公开媒体库和云部署。

## 完成后 handoff 要求

记录存储路径策略、数据模型、权限、API、页面、失败路径证据、未完成项、风险和
Batch 6 前置条件，并等待用户确认。
