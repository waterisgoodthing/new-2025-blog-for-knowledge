# UI Foundation Track — personal-learning-ui-foundation

> 文档治理（2026-10-09）：历史阶段账本保留，不把原 PASS/FAIL/未实施覆盖为本轮状态。当前见 PROJECT_STATUS；R 旧候选之后已有 B 本地返工 PARTIAL；UI V2 为独立组件轨，尚非主业务路由集成。 当前入口见 [文档索引](../../DOCUMENTATION_INDEX.md)。

独立前端轨，与 `docs/workflows/personal-learning-system-convergence/week2/` 完全独立。
本轨 PASS ≠ Week2 PASS；Week2 授权 ≠ 本轨授权。

## 授权（本轮第一阶段 F0–F5）

AUTHORIZED: WORKFLOW_CREATION / STATIC_AUDIT / FRONTEND_FOUNDATION_IMPLEMENTATION /
DOCUMENTATION / MOCK_IMPLEMENTATION / UI_CONTRACT_SKELETON / ADAPTER_SKELETON /
DESIGN_TOKEN_IMPLEMENTATION / SAFE_FOUNDATION_COMPONENT_WORK / VALIDATION

NOT_AUTHORIZED: STAGE / COMMIT / PUSH / MERGE / DEPLOY / PRODUCTION_WRITE /
WEEK2_PR05_08_MODIFICATION / BACKEND_MODIFICATION / DATABASE_MIGRATION /
AUTH_REFACTOR / API_SEMANTICS_CHANGE / BUSINESS_SEMANTICS_CHANGE /
UI-03~UI-12 / PR-08 / PR-11 / PR-14 / PR-20 / PR-21~PR-26 / WEEK3_PLUS

批准不跨阶段传递。完成后 STOP，等待下一次批准。

## Week2 强隔离（READ-ONLY）

`backend/app/models/review_item.py`、`backend/app/routers/review_items.py`、
`backend/app/schemas/review_item.py`、`backend/tests/test_review_schema_v2.py`、
`alembic/versions/027*` `028*` `029*` `030*`、
`src/lib/api/review-items.ts`、`src/lib/content-routes.ts`，
以及其他全部 `backend/app/{models,schemas,routers,services,repositories}/**` 与
`alembic/versions/**`。需改这些文件 → STOP，记 Gap，申请批准。

## 脏文件保护（READ_ONLY_UNTIL_OWNERSHIP_RESOLVED）

`manage-sidebar.tsx`、`dashboard-overview.tsx`、`notes/page.tsx`、`tag-input.tsx`、
`use-note-editor.ts`、`feature-state.tsx`、`dashboard-content.tsx` 及基线中其他已有
脏文件：先读 diff、保 provenance，禁止 revert/overwrite/reformat/stage。
绕不开 → STOP 并报告 FILE / CURRENT DIFF / WHY REQUIRED / COLLISION RISK /
PROPOSED OWNERSHIP。

## 写白名单

- `docs/workflows/personal-learning-ui-foundation/**`
- `docs/ui-v2/**`
- 新增：`src/contracts/ui-v2/**`、`src/mocks/ui-v2/**`、`src/adapters/ui-v2/**`、
  `src/components/ui-v2/**`、`src/features/ui-v2/**`（仓库无 canonical 目录时新建，
  最终路径记入 design.md）
- Design token 仅 additive，不改 Legacy 语义；全局 CSS 改动先记入 tasks.md，
  不得顺带重构。

## 阶段

F0 Baseline + Repository UI Audit → F1 Component Inventory → F2 Information
Architecture → F3 Design System Foundation → F4 Contract/Mock/Adapter Skeleton →
F5 Validation + Documentation。F5 后停止，不进业务页面实施。

## Gate

主适用 G0/G1。触及 Auth/credentials/私有路由/admin 端点即触发 G3 → STOP（当前
G3 内容 NOT_AUTHORIZED）。

## 基线

独立基线见 `evidence/baseline-status-frontend.txt` 与
`evidence/baseline-frontend.diff`（2026-09-13 冻结，52 项脏记录）。
PRE-EXISTING DIRTY WORK 与 THIS TRACK CHANGES 严格区分，已有脏修改不计入本轨成果。
