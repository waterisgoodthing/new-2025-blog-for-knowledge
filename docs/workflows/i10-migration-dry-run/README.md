# I10 迁移准备与隔离 dry-run

状态：`TECHNICAL PASS / DRY_RUN_READY BLOCKED`。源库已定位为默认实例 `blog_db:5432` 并只读核验；技术 clone、对账、回滚和销毁通过，但旧实体 owner/backfill 责任未收敛，不能进入 I11。逐表证据见 [owner-coverage](./owner-coverage.md)。文档：[audit](./audit.md) · [design](./design.md) · [requirements](./requirements.md) · [tasks](./tasks.md) · [validation](./validation.md) · [risk-register](./risk-register.md) · [next-requirements](./next-requirements.md)
