# MVP Rebuild Batch 4：错题草稿 / 错题 / 简单复习

## 任务目标

在保持旧公开错题 Note 完全兼容的前提下，建立“Question → MistakeDraft → 人工确认 →
私有 Mistake + ReviewItem → ReviewRecord”的最小手工闭环。

## 涉及领域

- mistake drafts：从正式 Question 或 QuestionDraft 形成待确认错题
- mistakes：独立、默认私有的新错题实体
- review：只服务 active Mistake 的固定间隔复习
- taxonomy：复用 Subject、KnowledgePoint 与 knowledge_point_links
- manage：升级 `/manage/mistakes`、`/manage/review` 并增加详情
- public compatibility：只验证旧 `/mistakes` 与 `/notes/[slug]`，不切换数据源
- infrastructure：Alembic 013、事务幂等、权限与显式前后端合同

## 当前状态

**Batch 4 已完成实现与文档收口，等待用户验收。**

本批不自动进入 Batch 5；进入下一批前需要用户明确确认。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)
- [验证记录](./validation.md)
- [审查记录](./audit.md)

Batch 4 checklist 与 handoff 位于 `docs/specs/mvp-rebuild/batch-4-mistakes-review/`。

## 已确认起点

- Batch 3 已关闭；数据库当前为 Alembic `012 (head)`。
- 新 Question/Draft 默认私有并可绑定正式 KnowledgePoint。
- 旧公开错题仍是 `Note(type="mistake")`，公开读取走 `/api/notes`。
- 旧 Note 内含 review 元数据；本批不迁移或删除这些历史字段。
- `/manage/mistakes` 与 `/manage/review` 当前仍为占位页。

## 核心边界

- 新 Mistake/Review 与旧 Note 并存；不回填、不双写、不切旧公开读取。
- 新 Mistake 第一版固定 private；不新增 public Mistake API。
- 只有人工确认产生的 active Mistake 才自动获得唯一 ReviewItem。
- Review 只实现固定间隔与不可变记录，不实现 BKT、练习或复杂调度。
