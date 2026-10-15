# GAP-001 Contract — 今日任务统一列表（B2，2026-09-20）

> 时态说明（2026-10-09）：下文是2026-09-20接口起点；Week2 Review依赖随后已解除、PR13练习已实现。统一任务流B-001真实集成仍未闭合；D008/PR13前置已具备，须验证其题目选集与统一任务字段的adapter映射，可先评估既有API组合而非预设新增端点；当前见 [状态](../PROJECT_STATUS.md)及[续接路线](../ROADMAP.md)，不将旧“Week3未开始”当现状。

只定文档，不动后端。GAP-001 保持 OPEN。

## 1. UI 契约位置（现状）

- `src/contracts/ui-v2/study-task.ts`：`StudyTask`（kind/status/priority/subject/
  dueAt/href/source/provenanceNote）。只描述展示意图，不发明调度语义。
- `src/mocks/ui-v2/today.ts`：六态 mock，全 `source: 'mock'` + 中文 provenance。
- 相关：`src/contracts/ui-v2/review-queue.ts`（DEPENDENCY-001，Week2 未定版前只做展示）。

## 2. 后端现状（只读引用，均为既有 client）

| 来源 | Client | 可用字段 |
|---|---|---|
| Dashboard 汇总 | `getDashboardSummary()` → `GET /api/admin/dashboard/summary` | `counts.due_reviews`、`recent_questions`、`recent_mistakes`、`recent_reviews` |
| 复习计划 | `getReviewPlan()` → `/api/review/plan` | `today_count`、`overdue_count`、`subject_summaries.due_today`、`weaknesses` |
| 复习队列 | `getReviewQueue()` → `/api/review/queue` | `NoteDetail[]`（到期项） |
| 错题 | `listMistakes()` | `Mistake[]`（状态过滤） |
| Week2 到期项 | `listDueReviewItems()`（READ-ONLY） | `ReviewItem[]`（语义未定版，只取存在性） |

**缺失**：统一任务流端点（无 dueAt/priority/status 三者齐备的单源）。
`GET /practice/today` 属 Week3 PR-13，未开始。

## 3. 组合映射规则（adapter 实现时遵守）

- `review` ← review 队列/计划：`today_count`/`overdue_count` 仅决定条数与 status；
  `overdue` 仅当后端给出已过期 due 日期，否则一律 `pending`。
- `mistake_retry` ← 错题列表；`new_practice` ← 题库；`note_review` ← 笔记。
- `priority`：后端给才用后端值，否则 `'medium'` + `source: 'estimated'`。
- `href`：深链到现有路由（`/manage/review`、`/manage/mistakes`、`/manage/questions`…），
  不新建路由。
- 禁止：由 UI 计算完成率、掌握度、排序权重；禁止把 mock 数量当真实计划展示；
  无数据时走 `empty` 态，不伪造任务。

## 4. 真实联调验收（Gap 关闭条件）

1. 统一端点存在，或多源组合方案经独立批准（含字段口径、失败 fallback）。
2. Review 语义侧 Week2 Gate 通过（DEPENDENCY-001 解除）。
3. Adapter 对每条 task 标注 `source: 'backend'` 且可回溯到具体 DTO 字段；
   抽查 3 条 mock→backend 替换无展示回归。
4. 空/失败/部分数据三态有真实浏览器证据。

## 5. 状态

GAP-001：OPEN。实现侧 BLOCKED（等统一端点或组合方案批准 + Week2 Gate）。
本文档的批准不等于后端实现批准。
