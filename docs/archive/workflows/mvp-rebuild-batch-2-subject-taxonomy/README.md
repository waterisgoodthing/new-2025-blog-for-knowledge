# MVP Rebuild Batch 2：科目 / 知识点基础

## 任务目标

在兼容现有 Subject 与 Note 字符串字段的前提下，建立科目、章节、知识点的管理 CRUD
与可复用选择器，为 Batch 3 题目绑定提供稳定分类底座。

## 涉及领域

- subjects：扩展现有 Subject，不建立平行模型
- taxonomy：新增 Chapter、KnowledgePoint 与候选 link 基础
- manage：将 `/manage/subjects` 占位升级为真实管理界面
- auth：所有分类读写 API 均使用现有管理员鉴权
- shared infrastructure：Alembic 迁移与前后端类型合同

## 当前状态

**Batch 2 已由用户确认通过。**

任务清单已按批准顺序完成；因真实迁移漂移触发的 006–010 修复已获得用户追加批准。
用户已允许开始 Batch 3 规划，但这不等于批准 Batch 3 实施任务。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)

- [审查](./audit.md)
- [验证](./validation.md)
- [Batch 2 checklist](../../specs/mvp-rebuild/batch-2-subject-taxonomy/checklist.md)
- [Batch 2 handoff](../../specs/mvp-rebuild/batch-2-subject-taxonomy/handoff.md)

## 已确认现状

- `subjects` 表已在初始迁移中存在，目前只有 `id`、`name`。
- `backend/app/models/note.py` 已定义最小 `Subject`。
- `/api/subjects` 已提供列表、创建、删除，更新尚缺。
- `src/lib/api/meta.ts` 已提供 Subject 类型和部分客户端函数。
- 现有 Note 仍使用 `subject: string`、`knowledge_points: string`；本批不迁移这些字段。
- 执行前本地数据库 Alembic current 为 `005`、代码 head 为 `010`；现已沿正常迁移链
  推进到新增的 `011 (head)`。

## 核心边界

- 原位扩展现有 Subject；不新增第二套 Subject API 或表。
- 不修改 Note 字符串字段语义，不批量迁移旧数据。
- 不实现知识图谱、BKT、AI、题目、错题、附件或统计。
- tags/taggings 不进入本批。
- 新迁移必须建立在已安全补齐 006–010 的数据库上。
