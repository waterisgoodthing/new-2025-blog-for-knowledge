# 需求文档：Batch 2 科目 / 知识点基础

## 1. 背景

题目、错题和复习需要稳定的科目与知识点 ID。仓库已有最小 Subject，但章节和正式
知识点仍不存在，Note 仅保存自由文本。Batch 2 需要建立管理底座，同时保持现有写作
与公开读取兼容。

## 2. 使用者

- 个人管理员：管理科目、章节和知识点。
- Batch 3 题目编辑器：读取稳定的知识点选项。
- 现有写笔记/错题页面：继续读取兼容 Subject 列表。
- 公开访客：不直接访问本批管理数据或操作。

## 3. 功能需求

### REQ-B2-01：Subject 完整 CRUD

- 输入：名称、描述、启用状态、排序。
- 处理：原位扩展并管理现有 Subject。
- 输出：Subject 列表、详情和更新结果。
- 失败处理：重复名 409；有下级数据时删除 409；无权限 401/403。
- 验收：现有 Subject 调用兼容，创建、查询、更新、删除均可验证。

### REQ-B2-02：Chapter CRUD

- 输入：subject ID、名称、描述、启用状态、排序。
- 处理：在指定 Subject 下创建和管理单层章节。
- 输出：按 Subject 排序的章节列表与详情。
- 失败处理：Subject 不存在 404；同科同名 409；有知识点时删除 409。
- 验收：章节只能属于一个有效 Subject。

### REQ-B2-03：KnowledgePoint CRUD

- 输入：subject ID、可选 chapter ID、名称、描述、启用状态、排序。
- 处理：创建和管理正式知识点。
- 输出：可按 subject/chapter/active 过滤的列表与详情。
- 失败处理：chapter 不属于 subject 时 400；重复名 409；有 link 时删除 409。
- 验收：知识点与科目、章节关系保持一致。

### REQ-B2-04：管理页面

- 输入：管理员访问 subjects 与 knowledge point 页面。
- 处理：加载列表、编辑、创建、确认删除并显示失败。
- 输出：可完成基础分类管理。
- 失败处理：空、加载、网络、验证、权限、冲突状态均有明确 UI。
- 验收：桌面与移动浏览器中完成真实 CRUD。

### REQ-B2-05：选择器基础

- 输入：subject ID 与可选 chapter ID。
- 处理：读取 active knowledge points 并转换为稳定 option。
- 输出：`{value,label}` 选项列表。
- 失败处理：无数据返回空列表，不伪造选项；请求失败向调用方抛出。
- 验收：Batch 3 可直接复用前端类型与 option adapter。

### REQ-B2-06：迁移安全

- 输入：本地数据库 current 005、代码 head 010 与新 011。
- 处理：审查、备份、顺序升级并验证。
- 输出：数据库与模型一致。
- 失败处理：006–010 任一失败立即停止，不 stamp、不跳迁移。
- 验收：current 到 011，表列约束存在，回滚策略有证据。

若对象已被 `create_all` 提前创建，迁移必须保留数据并验证结构；不得删除重建。

### REQ-B2-07：兼容旧 Note

- 输入：现有 Note.subject 与 Note.knowledge_points 字符串数据。
- 处理：本批保持原字段和读写行为不变。
- 输出：公开笔记、错题与旧编辑流程不受损。
- 失败处理：任何需要转换的情况记录为后续迁移需求。
- 验收：旧 Note 合同零语义变化，公开页面回归通过。

## 4. 非功能需求

- 安全：所有 taxonomy API 由后端管理员鉴权。
- 一致性：前端类型、Pydantic、SQLAlchemy 与 migration 同步。
- 可恢复：迁移前确认备份或恢复路径，不修改 Alembic 版本表绕过错误。
- 可维护：router 保持 thin，业务规则集中在 service。
- 可访问：表单 label、错误提示、删除确认和键盘操作清楚。
- 性能：列表按 subject 和 sort order 使用索引，MVP 不做复杂搜索。
- 审计：至少记录真实 CRUD 验收与数据清理；业务审计日志若复用现有模式需列入 tasks。

## 5. 本批不做

- 不迁移 Note 的自由文本 subject / knowledge points。
- 不做章节树、多级 Subject、slug 路由或公开 taxonomy 页面。
- 不做知识别名、知识关系、知识图谱、AI 建议、BKT 或统计。
- 不做 tags/taggings。
- 不实现 question、mistake、review 或 attachment 关联写入。
- 不修改首页、旧 `/manage` 或公开内容页面。

## 6. 验收标准

1. Subject、Chapter、KnowledgePoint CRUD 与错误合同通过。
2. KnowledgePoint 的 chapter/subject 一致性被后端强制。
3. 管理页面包含空、加载、失败和删除确认。
4. 选择器基础输出稳定 ID/label。
5. 未登录 API 被拒绝，管理员 API 可用。
6. 迁移从真实 current 005 安全升级到 010，再到 011。
7. Note 旧字段与公开页面无回归。
8. TypeScript、生产构建、后端测试、HTTP 与浏览器验收均有证据。
