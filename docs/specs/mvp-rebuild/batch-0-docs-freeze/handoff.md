# Handoff

## 本批完成内容

- 建立 MVP 第一版权威范围文档。
- 固定 Batch 0 至 Batch 7 的顺序和用户验收门禁。
- 冻结公开首页低密度、`/manage` 高密度原则。
- 将 Review MVP 限定为简单复习项、复习记录和 `next_review_at`。
- 明确 AI、OCR、BKT、完整练习和复杂容量控制后置。
- 明确候选 question / mistake 模型不等于已经实现。

## 修改文件

- `docs/architecture/mvp-scope.md`
- `docs/architecture/review-system.md`
- `docs/architecture/README.md`
- `docs/workflows/mvp-rebuild-batch-0-docs-freeze/README.md`
- `docs/workflows/mvp-rebuild-batch-0-docs-freeze/design.md`
- `docs/workflows/mvp-rebuild-batch-0-docs-freeze/requirements.md`
- `docs/workflows/mvp-rebuild-batch-0-docs-freeze/tasks.md`
- `docs/workflows/mvp-rebuild-batch-0-docs-freeze/audit.md`
- `docs/workflows/mvp-rebuild-batch-0-docs-freeze/validation.md`
- `docs/specs/mvp-rebuild/batch-0-docs-freeze/checklist.md`
- `docs/specs/mvp-rebuild/batch-0-docs-freeze/handoff.md`

## 未完成事项

- 独立 question 模型与 Note 的关系：后续 Batch 3 处理。
- 独立 mistake 模型与 `Note(type="mistake")` 的关系：后续 Batch 4 处理。
- 候选表的字段、约束、索引和迁移：对应 Batch 2 至 Batch 5 处理。
- 本批没有业务实现，也没有验证候选页面或数据表存在。

## 风险点

- 其他长期架构文档仍描述全量蓝图；后续必须以 `mvp-scope.md` 为 MVP 权威边界。
- 当前错题仍是 `Note(type="mistake")`，不得假设已有独立表或 `/api/mistakes`。
- `docs/architecture/` 在本批开始前整体未跟踪，Git 无法提供相对 HEAD 的逐文件基线；
  本轮验证依据实际补丁记录和执行前状态。

## 下一批前置条件

Batch 0 checklist、audit、validation 和本 handoff 已完成。只有用户明确确认 Batch 0
通过后，才能建立 Batch 1 workflow；Batch 1 仍需独立 requirements、design、tasks
和用户审批。

## 用户确认

- [x] 用户已于 2026-07-02 确认 Batch 0 通过，可以进入下一批
