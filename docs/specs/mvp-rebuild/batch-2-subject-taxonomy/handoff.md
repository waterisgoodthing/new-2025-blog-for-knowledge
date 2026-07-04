# Handoff

## 本批完成内容

- 原位扩展 Subject，并新增 Chapter、KnowledgePoint、KnowledgePointLink 数据基础。
- 完成三类 taxonomy CRUD、校验、依赖删除冲突和管理员权限保护。
- 完成显式前端 DTO/客户端、旧 Subject 客户端兼容层和可复用知识点选择器。
- 将 `/manage/subjects` 占位页升级为真实列表/创建页，新增科目与知识点详情编辑页。
- 真实浏览器完成 CRUD、错误态、持久化、桌面与移动布局验收。

## 批准范围扩大：历史迁移漂移修复

Batch 2 执行时发现数据库 Alembic 记录停在 005，但 006–010 目标表已被
`create_all` 提前创建并含真实数据，且 007 未生效。用户于 2026-07-03 明确批准仅为
修复迁移链扩大范围。

- 006、008、009、010 改为 inspect-first、数据保留型可重放迁移。
- 007 的 folder FK 已真实从 CASCADE 修正为 SET NULL。
- 未 stamp、未删表、未丢数据、未 drop/recreate、未跳过迁移、未用 create_all
  代替迁移。
- 数据库实际从 005 正常推进到 010，再执行 011；当前为 `011 (head)`。
- 重复 `alembic upgrade head` 通过。

## 最终数据合同

- Subject：id、name、description、is_active、sort_order、created_at、updated_at。
- Chapter：subject_id + name 在科目内唯一；单层章节。
- KnowledgePoint：必属 Subject，可选 Chapter；subject_id + name 在科目内唯一。
- KnowledgePointLink：仅建表作为后续关联基础，本批无 API/UI。
- 删除：有下级或 link 依赖时返回 409，不自动级联删除管理数据。

## API 与页面

- API：`/api/subjects`、`/api/chapters`、`/api/knowledge-points`，均提供
  list/detail/create/update/delete，全部要求管理员身份。
- 页面：`/manage/subjects`、`/manage/subjects/[id]`、
  `/manage/knowledge-points/[id]`。
- 旧 `src/lib/api/meta.ts` 的 Subject 调用方式保持兼容。

## 验证证据

- 后端定向测试：7 passed。
- `npx tsc --noEmit`：通过。
- `npm run build`：通过，32/32 静态页面生成。
- 真实浏览器：CRUD、409、刷新持久化、390px 无横向溢出、公开页面无 console error。
- 迁移：`011 (head)`，重复 upgrade 通过；历史真实数据不少于修复前基线。
- 临时管理员已注销并禁用，验收 taxonomy 数据已清理。

## 修改范围

- 历史迁移：006–010；新增迁移：011。
- 后端：taxonomy models/schemas/service/routers/tests，Subject 原位扩展，main 注册。
- 前端：taxonomy API、meta 兼容层、选择器、三个 manage 页面及路由组件。
- 文档：Batch 2 workflow、checklist、handoff。

## 未完成事项

- tags/taggings 未纳入。
- 不包含题目草稿、题库、错题、复习、附件、AI、OCR、知识图谱、BKT 或统计。
- `knowledge_point_links` 的业务关联留给获批的后续批次。

## 风险点

- lifespan 的既有 `create_all` 仍可能造成未来 Alembic 漂移；后续 schema 变更必须
  坚持 migration-first。
- 极端并发重复创建由数据库唯一约束兜底，可能返回通用数据库错误；个人管理场景风险低。

## 下一批前置条件

Batch 2 已具备技术完成证据，但必须由用户明确确认通过后才能进入 Batch 3。

## 用户确认

- [x] 用户已确认 Batch 2 通过，可以开始 Batch 3 规划
