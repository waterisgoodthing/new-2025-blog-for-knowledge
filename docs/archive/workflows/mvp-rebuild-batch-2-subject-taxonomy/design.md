# 设计文档：Batch 2 科目 / 知识点基础

## 1. 设计原则

1. 兼容优先：扩展现有 `subjects`，保留 `/api/subjects` 与前端调用方。
2. 简单优先：管理路由使用整数 ID，不在本批引入公开 slug 路由。
3. 单一数据源：正式科目、章节、知识点只存 PostgreSQL。
4. 迁移保守：不自动转换 Note 的自由文本 subject / knowledge points。
5. 管理员专用：分类管理 API 与页面全部受管理员保护。
6. 后续可接：提供稳定 ID 与选择器接口，但不提前实现 question 或 mistake 关联。

## 2. 当前实现与兼容策略

### 已存在

- `subjects(id, name)`。
- `Subject` SQLAlchemy 模型位于 `backend/app/models/note.py`。
- `/api/subjects` 列表、创建、删除。
- `src/lib/api/meta.ts` 的 Subject 类型和客户端。
- 写笔记、写错题页面读取 subjects 列表。

### 本批策略

- 保留 `Subject` 当前位置，避免为整洁而移动既有模型。
- 在同一模型上增加 MVP 字段，不替换表。
- 保留 `/api/subjects` 路径，新增详情与更新能力。
- 新增 taxonomy service，让 router 只负责 HTTP 与依赖。
- 现有写作页面继续通过兼容的 `listSubjects()` 使用 `{id,name}` 子集。
- 新管理客户端放入 `src/lib/api/taxonomy.ts`；`meta.ts` 的兼容方法可转调或保持。

不新增 `/api/admin/subjects` 平行合同。长期架构文档中的 admin namespace 是目标方向，
本批以避免破坏现有调用为优先。

## 3. 数据设计

### `subjects`（原位扩展）

| 字段 | 类型 | 约束 |
| --- | --- | --- |
| `id` | integer | 既有主键 |
| `name` | varchar(100) | 非空、唯一 |
| `description` | text | 可空 |
| `is_active` | boolean | 非空，默认 true |
| `sort_order` | integer | 非空，默认 0 |
| `created_at` | datetime | 非空，server default now |
| `updated_at` | datetime | 非空，server default now |

MVP 不增加 parent、预算、exam weight 或 phase；这些属于后续 Subject 扩展。

### `chapters`

| 字段 | 类型 | 约束 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `subject_id` | integer | FK subjects，CASCADE |
| `name` | varchar(150) | 非空 |
| `description` | text | 可空 |
| `sort_order` | integer | 默认 0 |
| `is_active` | boolean | 默认 true |
| `created_at` / `updated_at` | datetime | server default now |

唯一约束：`(subject_id, name)`。本批只做单层章节，不做 `parent_id` 树。

### `knowledge_points`

| 字段 | 类型 | 约束 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `subject_id` | integer | FK subjects，CASCADE |
| `chapter_id` | integer | 可空 FK chapters，SET NULL |
| `name` | varchar(200) | 非空 |
| `description` | text | 可空 |
| `sort_order` | integer | 默认 0 |
| `is_active` | boolean | 默认 true |
| `created_at` / `updated_at` | datetime | server default now |

唯一约束：`(subject_id, name)`。若 `chapter_id` 非空，service 必须验证章节属于同一科目。

### `knowledge_point_links`

Batch 2 只建立可供后续批次使用的最小结构，不提供写入 UI：

| 字段 | 类型 | 约束 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `knowledge_point_id` | integer | FK knowledge_points，CASCADE |
| `target_type` | varchar(30) | 非空 |
| `target_id` | varchar(64) | 非空 |
| `created_at` | datetime | server default now |

唯一约束：`(knowledge_point_id, target_type, target_id)`。

本批不创建 link API；Batch 3 在 question ID 合同确定后再启用。`target_id` 使用字符串以
兼容当前 UUID Note 与未来实体 ID，但不代表所有 target type 已获准。

### 不进入本批

- `tags`、`taggings`
- `knowledge_aliases`
- `knowledge_relations`
- `knowledge_point_suggestions`
- `subject_review_settings`
- BKT / mastery 表

## 4. 迁移设计

### 当前风险

代码 migration head 是 `010`，本地数据库 current 是 `005`。不能直接生成或应用 011。

### 执行门禁

1. 使用 `PYTHONPATH=. .venv/bin/alembic current` 与 `history` 保存证据。
2. 审查 006–010 的 upgrade 内容及与当前数据库的冲突风险。
3. 对本地数据库做备份或可恢复性确认。
4. 若 006–010 对象已被 `create_all` 提前创建，禁止删除有数据的表，也禁止直接 stamp。
5. 经用户追加批准后，将 006、008、009、010 改为“存在时验证并补索引，不存在时创建”
   的可重放迁移；007 继续负责把 folder FK 改为 SET NULL。
6. 006 中 `passkey_credentials.public_key` 的新库类型同步当前模型为 BYTEA，不能继续
   创建与模型冲突的 VARCHAR。
7. 执行并验证 `upgrade 010`。
8. 新增单一 `011_add_subject_taxonomy.py`。
9. 执行 `upgrade 011`，检查表、列、约束与 downgrade 路径。

若 006–010 任一迁移失败，停止 Batch 2，不以 stamp、删表或手工改版本表绕过。

当前调查已确认：006、008、009、010 的表均已存在且部分含真实数据，007 的 folder
FK 仍为 CASCADE。根因是后端 lifespan 的 `Base.metadata.create_all` 提前创建表，
但不会推进 Alembic 版本或修改既有约束。

## 5. 后端架构

```text
router
  -> Pydantic schema
  -> taxonomy_service
  -> Subject / Chapter / KnowledgePoint
  -> response schema
```

建议文件：

- `backend/app/models/taxonomy.py`：只放新增 Chapter、KnowledgePoint、
  KnowledgePointLink；Subject 保留原位置。
- 更新 `backend/alembic/env.py` 导入新增模型，确保 metadata 完整。
- `backend/app/schemas/taxonomy.py`
- `backend/app/services/taxonomy_service.py`
- `backend/app/routers/chapters.py`
- `backend/app/routers/knowledge_points.py`
- 更新既有 `backend/app/routers/subjects.py` 为 thin router。
- 更新 `backend/main.py` 注册新 router。

后端 lifespan 现有 `Base.metadata.create_all` 不能替代 Alembic 验证；Batch 2 必须以
migration current 与实际 schema inspection 作为数据库完成证据。

## 6. API 设计

所有端点依赖 `get_current_admin`。

### Subjects

- `GET /api/subjects`
- `POST /api/subjects`
- `GET /api/subjects/{id}`
- `PUT /api/subjects/{id}`
- `DELETE /api/subjects/{id}`

### Chapters

- `GET /api/chapters?subject_id=`
- `POST /api/chapters`
- `GET /api/chapters/{id}`
- `PUT /api/chapters/{id}`
- `DELETE /api/chapters/{id}`

### Knowledge points

- `GET /api/knowledge-points?subject_id=&chapter_id=&active_only=`
- `POST /api/knowledge-points`
- `GET /api/knowledge-points/{id}`
- `PUT /api/knowledge-points/{id}`
- `DELETE /api/knowledge-points/{id}`

### 错误合同

- 400：章节与知识点科目不一致、无效过滤条件。
- 401：未登录。
- 403：非管理员。
- 404：实体不存在。
- 409：同一作用域名称冲突；删除仍被依赖的实体。
- 422：字段长度或类型校验失败。

删除策略由 service 显式检查并返回 409，不依赖数据库 CASCADE 静默删除管理数据：

- Subject 有 chapter / knowledge point 时拒绝删除。
- Chapter 有 knowledge point 时拒绝删除。
- Knowledge point 有 link 时拒绝删除。

## 7. 前端合同

`src/lib/api/taxonomy.ts` 定义显式类型：

- Subject / SubjectCreate / SubjectUpdate
- Chapter / ChapterCreate / ChapterUpdate
- KnowledgePoint / KnowledgePointCreate / KnowledgePointUpdate
- 列表与 CRUD 函数

提供 `listKnowledgePointOptions({subjectId, chapterId?})` 或等价纯客户端适配，返回稳定
`{value:id,label:name}` 结构，供 Batch 3 复用。选择器组件本身放在 manage route 下；
Batch 3 若跨路由复用，再经证据提升到共享组件。

## 8. 页面设计

### `/manage/subjects`

- 使用 Batch 1 壳层。
- 左侧/上方为科目列表与创建表单。
- 右侧/下方显示选中科目的章节与知识点摘要。
- 提供明确空状态、加载状态、错误状态。

### `/manage/subjects/[id]`

- 编辑科目名称、描述、启用状态与排序。
- 管理该科目的章节。
- 显示知识点列表并提供进入详情的链接。

### `/manage/knowledge-points/[id]`

- 编辑名称、描述、科目、可选章节、启用状态和排序。
- 更换科目时清空不属于新科目的章节。

### 交互限制

- 删除必须二次确认并显示依赖冲突。
- 不显示掌握度、AI 建议、图谱或统计。
- 不修改公开首页或旧 `/manage`。

## 9. 权限设计

- 页面：全部位于 Batch 1 AuthGate 工作区。
- API：GET 与写操作全部要求 `get_current_admin`。
- 前端保护不能替代后端权限。
- 不使用 AUTH_BYPASS 作为测试通过依据。
- 临时管理员只允许用于本地验收，验收后必须注销并禁用。

## 10. 异常与一致性

- 名称 trim 后不能为空。
- 同作用域名称比较应一致，至少阻止完全相同名称。
- Chapter 只能引用存在的 Subject。
- KnowledgePoint 的 Chapter 必须属于同一 Subject。
- API 失败后表单保留输入并展示错误。
- 删除冲突不从 UI 乐观移除。
- 请求成功后重新验证列表，不维护第二份长期客户端缓存。

## 11. 验证设计

### TDD

按 vertical slice：

1. Subject 更新与删除冲突。
2. Chapter CRUD 与 Subject 归属。
3. KnowledgePoint CRUD 与 Chapter/Subject 一致性。
4. 选择器输出。
5. 页面真实操作。

### 后端

- taxonomy service 定向测试。
- schema 验证测试。
- 本地临时管理员 HTTP CRUD 验收，测试数据使用唯一前缀并清理。
- migration upgrade/downgrade 在可恢复数据库或隔离库验证。

### 前端

- `npx tsc --noEmit`
- `npm run build`
- 管理员真实浏览器 CRUD。
- 未登录 API 返回 401/403。
- 桌面与移动页面验收。

### 合同

- 比对 SQLAlchemy、Pydantic、OpenAPI、TypeScript 字段。
- 检查旧 `listSubjects()` 调用仍可工作。
- 检查 Note 的 `subject`、`knowledge_points` 字符串字段未被迁移或改义。

## 12. 已知非阻塞债务

- Subject 暂留 `models/note.py`，避免本批做纯整理移动。
- Note 的自由文本 subject / knowledge points 与新 taxonomy 并存，迁移由后续批次单独设计。
- 架构长期文档包含 slug、树、别名、关系、预算等字段，本批只实现 MVP 子集。
