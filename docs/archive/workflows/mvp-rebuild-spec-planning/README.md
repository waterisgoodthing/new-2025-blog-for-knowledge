# MVP 重构 Spec 规划工作区

## 任务目标

在不修改业务代码、配置、依赖或数据库的前提下，建立
`docs/specs/mvp-rebuild/`，将 MVP 重构拆分为严格顺序执行的 8 个批次。

## 涉及领域

- shared infrastructure：任务治理、执行门禁与验收约束
- home、manage、notes、mistakes、review、auth：仅在后续批次 spec 中描述边界
- `docs/architecture/`：本轮默认只读取，不执行 Batch 0 的架构修订

## 当前状态

**等待用户审批任务清单。**

本工作区仅用于规划“创建 8 批 spec”这项文档任务。用户批准
[`tasks.md`](./tasks.md) 后，才能创建 `docs/specs/mvp-rebuild/`。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)

后续执行完成后再补充：

- `validation.md`
- 必要时的 `handoff-prompt.md`

## 范围边界

本轮获准写入：

- `docs/workflows/mvp-rebuild-spec-planning/`
- `docs/specs/`
- `docs/architecture/`

本轮计划实际不修改 `docs/architecture/`；其修改属于未来 Batch 0，需另行审批。
禁止修改任何业务代码、样式、配置、依赖、迁移或数据。
