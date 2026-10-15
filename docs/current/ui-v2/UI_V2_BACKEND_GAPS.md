# UI V2 Backend Gaps（后端缺口）

> **2026-10-15 复核并冻结**：本表原写于 F4 阶段（2026-09-13），此后 PR-07/10/11 等已落地。下表已按**当前代码**重新核对状态。此处只记录，**不修后端**；后端改动不在 UI V2 轨授权内，进入实施需单独批准。

## 当前状态（2026-10-15 复核）
| Gap ID | UI 需求 | 后端现状（复核）| 状态 |
|---|---|---|---|
| GAP-001 | 今日任务统一列表（ReviewTask 含 dueAt/priority/status）| 已有 `dashboard/summary`（含 due）、`load_weak_top3`、practice 选题；但**无单一"今日任务流"端点**，字段口径未统一 | **PARTIAL** |
| GAP-002 | 掌握度数值（MasteryScore.value）| 无独立 mastery 端点；仅 `ReviewItem.mastered` + KP 统计 | **OPEN** |
| GAP-003 | 薄弱 Top3（确定性口径）| `dashboard_service.load_weak_top3` 已实现 | **RESOLVED** |
| GAP-004 | 博客列表数据源 | `public/blogs/index.json` 仍为空 | **OPEN** |
| GAP-005 | Review 再答三档判定 + attempt 归属 | `reanswer_service` + `attempts` 路由已实现（PR-07）| **RESOLVED** |

## 结论
- 原 5 个 GAP 中 **2 个已解决（003/005）**、**1 个部分（001）**、**2 个仍开放（002/004）**。
- 其余字段级口径（Today 的 priority/status 映射）仍待裁决；属后端合同，需单独授权。

## 边界
- 本表是**缺口记录**，不是实施授权。
- 如需任一 OPEN/PARTIAL Gap 进入实施：STOP 本轨相关项，单独申请批准（后端改动不在 UI V2 轨内）。
