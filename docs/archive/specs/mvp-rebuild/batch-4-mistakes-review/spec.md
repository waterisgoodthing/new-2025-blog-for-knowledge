# Batch 4：错题草稿 / 错题系统 / 简单复习

## 目标

跑通“正式题目 → 错题草稿 → 人工确认 → 正式错题 → 简单复习项 → 复习记录”。

## 背景

当前错题是 `Note(type="mistake")`，并不存在已确认的独立 mistakes 表或
`/api/mistakes`。附件提出的候选新模型与现有公开读取、编辑和复习合同有直接冲突，
必须先做架构与迁移设计，不能静默替换。

## 任务范围

1. 先决定继续扩展 `Note(type="mistake")`，还是经迁移引入独立错题模型。
2. 支持从正式题目创建错题草稿，并关联 `question_id` 或 `question_draft_id`。
3. 支持人工审核错题草稿，确认后生成正式错题。
4. 正式错题进入 active 状态后生成简单复习项。
5. `/manage/mistakes` 提供列表与详情。
6. `/manage/review` 展示待复习项并支持完成一次复习。
7. 完成后生成复习记录并简单更新 `next_review_at`。
8. 保持 `/mistakes` 与错题详情公开读取已发布、未隐藏内容；管理操作保持受保护。

## 允许修改范围

- 本批对应 workflow 与必要架构决策文档。
- 经批准的错题、复习模型或现有 Note 扩展、schema、service、router、migration。
- 对应 `src/lib/api/` 客户端。
- `/manage/mistakes`、`/manage/review` 及直接相关管理组件。
- 现有公开错题页面仅限保持兼容所必需的小范围适配。
- 直接相关测试与验证材料。

## 禁止事项

- 不做完整练习系统或自动判错。
- 不做 BKT、复杂容量控制或题库抽题检测。
- 不假设已有 mistakes 表或 `/api/mistakes`。
- 不给公开 `/mistakes` 或 `/notes/[slug]` 强制加 `AuthGate`。
- 不让公开页面重复请求管理员复习接口。
- 不把错题编辑器大型重构混入本批。

## 涉及页面

- `/manage/mistakes`
- `/manage/mistakes/[id]`
- `/manage/review`
- `/mistakes`（只做公开兼容验证）
- `/notes/[slug]`（当前错题详情兼容验证）

## 涉及数据表

候选表：

- `mistake_drafts`
- `mistakes`
- `review_items`
- `review_records`

当前真实模型仍以 `notes` 中的 `type="mistake"` 为核心；最终方案必须在本批设计获批。

## 验收标准

1. 可以从正式题目创建并审核错题草稿。
2. 确认后只生成一个正式错题。
3. active 错题生成复习项。
4. 可以完成一次复习并生成复习记录。
5. 复习后 `next_review_at` 按简单规则更新。
6. 未确认错题不进入复习。
7. 管理员写入与复习操作受保护，公开错题读取未受损。
8. 模型迁移、权限和异常路径均有验证证据。

## 非目标

BKT、完整练习、自动判错、复杂容量控制、抽题检测和错题编辑器全面重构。

## 完成后 handoff 要求

记录错题模型决定、兼容策略、复习规则、API/页面/迁移、权限证据、风险和 Batch 5
前置条件，并等待用户确认。
