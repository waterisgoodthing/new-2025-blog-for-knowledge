# I8 设计

Markdown 编辑/预览复用 Note 内容与稳定资源引用；版本为追加历史，不覆盖审计。WikiLink/反链以稳定资源 ID 或 slug 解析，移动显示路径不得改变链接。搜索使用 PostgreSQL 全文与 trigram，并在查询层应用管理员/公开可见性过滤。
