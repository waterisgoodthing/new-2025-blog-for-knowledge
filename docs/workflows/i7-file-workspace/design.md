# I7 设计

复用现有 `attachments`、`attachment_links`、`folders` 和 `audit_logs`；新增文件节点只能组织稳定资源引用，不成为 Note、Question、Mistake、Review 或发布实体的替代主数据。

资源状态：`temporary_upload -> verified -> active -> trashed -> restored`，失败为 `rejected`，存储丢失为 `missing`。所有 API 默认管理员保护，内容预览不得匿名可读；移动/重命名只改显示元数据，冲突显式返回 409 并写审计。
