# Architecture Decision Records

这里记录影响个人学习系统 V2 长期边界的架构决策。ADR 解释“为什么这样设计”，而 `docs/architecture/` 描述“目标系统是什么”，`docs/workflows/` 描述“如何分阶段执行”。

## 决策索引

- [ADR-001 PostgreSQL 是唯一事实来源](./ADR-001-postgresql-source-of-truth.md)
- [ADR-002 KnowledgeNode 不使用图数据库作为事实存储](./ADR-002-knowledge-node-relational-storage.md)
- [ADR-003 Today 是统一入口与编排层](./ADR-003-today-orchestrator.md)
- [ADR-004 AI 输出必须经过人工审核](./ADR-004-ai-human-review.md)

新增或修改核心边界时，先新增或修订 ADR，再更新架构、需求和任务文档。

