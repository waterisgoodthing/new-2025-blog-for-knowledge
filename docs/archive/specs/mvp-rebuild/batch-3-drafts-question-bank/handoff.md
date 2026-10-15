# Handoff

## 本批完成内容

- 新增独立 DraftItem、QuestionDraft、Question、QuestionSource，与旧 Note 原样共存。
- 跑通手工创建草稿、编辑、拒绝、确认转换、正式题目编辑与归档。
- conversion 使用行锁、version、converted target 与唯一 manual source 保证幂等。
- 正式题目支持 Subject 和正式 KnowledgePoint 绑定。
- 完成 admin API、显式前端 DTO/client 与四个管理页面。

## 架构决定

- 本批不回填、不迁移、不双写旧 Note；旧错题仍是 `Note(type="mistake")`。
- 正式 Question 只能由草稿确认转换产生，不提供直接 create API。
- Question 默认 private，不提供 public API。
- Question 删除语义为 archived；Draft 拒绝后不可编辑或转换。

## 数据与迁移

- Alembic：新增 012，当前 `012 (head)`，重复 upgrade 通过。
- 新表：`draft_items`、`question_drafts`、`questions`、`question_sources`。
- Taxonomy：复用 `knowledge_point_links`，target type 为 question_draft/question。
- 旧 Note 数量执行前后保持 blog=1、mistake=5、note=7。

## API 与页面

- Draft API：list/create/get/update/reject/convert，位于 `/api/admin/drafts`。
- Question API：list/get/update/archive，位于 `/api/admin/questions`。
- 页面：`/manage/drafts`、`/manage/drafts/[id]`、`/manage/questions`、
  `/manage/questions/[id]`。
- 全部 API 使用 `get_current_admin`；全部页面沿用 workspace AuthGate。

## 验证证据

- 后端最终定向测试：16 passed。
- TSC：通过。
- Production build：通过，32/32 页面生成。
- 真实浏览器：创建、v1→v2 编辑、知识点绑定、转换、刷新持久化、归档、390px 布局。
- 重复 convert：返回同一 Question；DB Question=1、Source=1。
- reject：状态为 rejected；未登录 admin API=401；public questions=404。
- console error=0；验收数据与临时管理员均已清理/禁用。

## 修改范围

- 新增 012 migration、Question/Draft models/schemas/services/routers/tests。
- 新增 Draft/Question 前端客户端与管理页面。
- 扩展 Batch 2 KnowledgePointSelect 文件，仅增加多选导出。
- 更新 Batch 3 workflow/checklist/handoff。
- 未修改首页、workspace shell、旧 `/manage/page.tsx` 或 Note model。

## 未完成事项

- 不包含旧 Note 迁移、独立 Mistake、Review、练习、附件、AI、OCR、Capture Router、
  批审、搜索、复杂去重或公开题库。

## 风险点

- lifespan `create_all` 的既有迁移漂移风险仍在，012 对提前存在目标表会主动失败。
- 列表按题加载来源/知识点，MVP 数据量可接受；有性能证据后再批量优化。
- 公开 `/mistakes` 的既有管理员 API 403 噪音未跨批修复。

## 下一批前置条件

必须由用户明确确认 Batch 3 通过后，才能开始 Batch 4 的独立规划。Batch 4 必须重新
设计 Question 与当前 `Note(type="mistake")` 的兼容/迁移边界，不得自动切换旧事实源。

## 用户确认

- [x] 用户已确认 Batch 3 关闭，可以开始 Batch 4 workflow 准备
