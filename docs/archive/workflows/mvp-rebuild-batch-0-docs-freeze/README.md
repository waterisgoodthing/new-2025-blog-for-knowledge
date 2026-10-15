# MVP Rebuild Batch 0：文档冻结与实现约束

## 任务目标

冻结 MVP 第一版范围，消除现有目标架构文档与
`docs/specs/mvp-rebuild/batch-0-docs-freeze/spec.md` 之间的范围歧义，为 Batch 1
至 Batch 7 提供不可越界的实现约束。

## 涉及领域

- shared infrastructure：架构治理、范围冻结、批次门禁
- home、manage：只定义信息密度原则，不修改 UI
- subjects、questions、mistakes、review、attachments：只定义候选模型与批次边界
- AI、OCR、practice：明确后置，不做实现

## 当前状态

**已验收完成。**

用户已于 2026-07-02 确认 Batch 0 通过。Batch 1 可以进入独立 workflow 的规划与
tasks 审批阶段，但尚未获准实施。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)

执行完成后补充：

- `validation.md`
- `audit.md`
- 必要时更新本批 spec 的 `checklist.md` 与 `handoff.md`

## 允许范围

- `docs/workflows/mvp-rebuild-batch-0-docs-freeze/`
- `docs/architecture/mvp-scope.md`
- `docs/architecture/review-system.md`
- `docs/architecture/README.md`（仅索引与第一版范围同步）
- `docs/specs/mvp-rebuild/batch-0-docs-freeze/checklist.md`
- `docs/specs/mvp-rebuild/batch-0-docs-freeze/handoff.md`

本批不修改任何业务代码、样式、配置、依赖、迁移或数据。
