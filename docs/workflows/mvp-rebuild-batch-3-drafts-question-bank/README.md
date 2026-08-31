# MVP Rebuild Batch 3：题目草稿 / 审核 / 题库

## 任务目标

在不迁移或改写旧 Note 数据的前提下，建立“手工题目草稿 → 人工修正 →
幂等确认转换 → 私有正式题库”的最小纵向闭环。

## 涉及领域

- drafts：统一草稿索引与 question 类型草稿
- questions：独立正式题目及 manual 来源
- taxonomy：复用 Batch 2 Subject、KnowledgePoint 与 `knowledge_point_links`
- manage：升级 `/manage/drafts`、`/manage/questions` 占位页并增加详情路由
- auth：全部草稿与题库 API、页面保持管理员保护
- shared infrastructure：Alembic 012、前后端类型合同和转换事务

## 当前状态

**Batch 3 已由用户确认关闭。**

用户已允许开始 Batch 4 workflow 准备，但这不等于批准 Batch 4 实施 tasks。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)

- [审查与剩余风险](./audit.md)
- [验证记录](./validation.md)
- [Batch 3 checklist](../../specs/mvp-rebuild/batch-3-drafts-question-bank/checklist.md)
- [Batch 3 handoff](../../specs/mvp-rebuild/batch-3-drafts-question-bank/handoff.md)

## 已确认起点

- Batch 2 已由用户确认通过；数据库当前为 Alembic `011 (head)`。
- Subject、Chapter、KnowledgePoint 与 `knowledge_point_links` 已可用。
- `/manage/drafts`、`/manage/questions` 当前仍为 Batch 1 占位页。
- 当前没有独立 Question/Draft 模型或 API。
- 旧 `Note` 仍承载 note/blog/mistake；错题仍是 `Note(type="mistake")`。

## 核心边界

- 新增独立 Question/Draft 表，与旧 Note 并存；本批不回填、迁移或双写旧 Note。
- 手工题目必须先建草稿；不提供绕过审核的直接 Question create API。
- Question 默认私有，不新增 public question API。
- 不实现错题、复习、练习、附件、AI、OCR、Capture Router 或批量审核。
