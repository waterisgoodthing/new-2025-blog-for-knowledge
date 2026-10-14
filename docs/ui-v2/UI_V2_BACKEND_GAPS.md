# UI V2 Backend Gaps（F4 起，递增编号；只记录，不修后端）

| Gap ID | UI 需求 | 后端现状 | 影响 | 状态 |
|---|---|---|---|---|
| GAP-001 | 今日任务统一列表（ReviewTask 含 dueAt/priority/status） | `GET /api/admin/dashboard/summary` 仅 counts + recent 列表，无统一任务流 | Today 页（MIGRATE_LATER） | OPEN |
| GAP-002 | 掌握度数值（MasteryScore.value 非 null） | 无 mastery 端点；Week2 调度语义未定版 | 分析页（MIGRATE_LATER） | OPEN |
| GAP-003 | 薄弱 Top3（确定性口径） | Week3 PR-10 KP analytics 未开始 | 分析页（MIGRATE_LATER） | OPEN |
| GAP-004 | 博客列表数据源 | `public/blogs/index.json` 为空，迁移中 | 博客相关 UI 只能用 mock/empty | OPEN |
| GAP-005 | Review 再答三档判定 + attempt 归属 | Week2 PR-07 未开始 | Review 页（MIGRATE_LATER） | OPEN |

如需任一 Gap 进入实施：STOP 本轨相关项，单独申请批准（后端改动不在本轨授权内）。
