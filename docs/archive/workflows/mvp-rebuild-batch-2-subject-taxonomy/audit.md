# Batch 2 审查记录

## 结论

通过，未发现阻塞 Batch 2 验收的问题。用户已确认 Batch 2 通过并允许开始 Batch 3
规划；Batch 3 仍须单独批准任务清单后才能实施。

## 范围审查

- 业务范围仅包含 Subject、Chapter、KnowledgePoint 分类底座及选择器。
- 未修改旧 `/manage/page.tsx`，未修改首页、现有卡片系统或配置 JSON。
- 未实现题目草稿、题库、错题、复习、附件、AI、OCR、知识图谱或 BKT。
- `Note.subject` 与 `Note.knowledge_points` 保持原字符串合同。
- tags/taggings 未纳入。

## 架构审查

- 沿用现有 `subjects` 表和 `/api/subjects`，未建立平行合同。
- 前端遵循 `page/component -> src/lib/api -> backend API`。
- 后端遵循 `router -> schema -> service/model`，router 不持有业务查询规则。
- 三组 taxonomy API 的读写均受 `get_current_admin` 保护。
- 管理页面位于既有 `/manage` 工作区，旧管理面板仍为登录入口。

## 迁移漂移专项审查

- 用户于 2026-07-03 批准扩大范围，仅修复历史 Alembic 链。
- 006、008、009、010 均先 inspect，再条件化创建/补齐；没有 stamp、删表、
  drop/recreate 或 `create_all` 替代迁移。
- 007 按数据库真实 FK 名称执行，最终为 `ON DELETE SET NULL`。
- 006 的 passkey `public_key` 以当前真实数据和模型为准保持 BYTEA；遇到未知且有数据
  的错误类型会主动失败，不猜测转换。
- 迁移实际沿 005 → 006 → 007 → 008 → 009 → 010 → 011 推进；重复 upgrade
  无破坏性行为。
- 修复前历史数据均保留；本轮新增的 session/audit 行属于真实验收行为，不是迁移丢失。

## 剩余风险

- 应用 lifespan 仍调用 `Base.metadata.create_all`，这是既有架构债；本批没有扩大范围移除。
  后续必须继续以 Alembic 为正式 schema 演进路径，避免再次产生版本漂移。
- 数据库唯一约束可防并发重复；service 的预检查负责友好 409，但极端并发竞争仍可能由
  数据库约束兜底并返回通用错误，当前个人管理场景风险低。
- `knowledge_point_links` 仅建立数据基础，本批没有开放 link API，符合后续批次边界。

## 验证结论

- 定向后端测试、TSC、生产构建、真实浏览器 CRUD、移动布局、权限、公开页面、
  Alembic current/重复 upgrade、schema 和数据保全检查均通过。
- 临时管理员已注销并禁用；浏览器验收数据已清理。
