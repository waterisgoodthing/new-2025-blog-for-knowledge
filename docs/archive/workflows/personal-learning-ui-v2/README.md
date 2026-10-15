# UI V2 Full Implementation Track — personal-learning-ui-v2

> 文档治理（2026-10-09）：历史阶段账本保留，不把原 PASS/FAIL/未实施覆盖为本轮状态。当前见 PROJECT_STATUS；R 旧候选之后已有 B 本地返工 PARTIAL；UI V2 为独立组件轨，尚非主业务路由集成。 当前入口见 [文档索引](../../DOCUMENTATION_INDEX.md)。

执行模式 `WORKER`；main agent 为唯一 `primary_owner` 与 `code_acceptor`。
分类理由：16 个阶段（U1–U16）多阶段串行 + 跨模块契约边界 + Week2 并行隔离 +
API Contract 边界，非简单任务。文件数量不是分类依据。

## Baseline

- Foundation Track `docs/workflows/personal-learning-ui-foundation/` F0–F5 = PASS（本轨 baseline evidence，不推翻，不删除）。
- HEAD `4a954ea`（branch `refactor/baseline`），本轨启动基线见 `evidence/baseline-status-uiv2.txt`。
- `git diff --check` 启动时 exit 0。
- Week2（`personal-learning-system-convergence/week2/`）：PR-05 PASS；
  PR-06 / PR-07 / PR-08 = NOT_VERIFIED，Week2 Gate = NOT_VERIFIED。
  Review 语义与集成归 Week2 所有，本轨只读。

## 授权（本轮 U1–U16）

AUTHORIZED: WORKFLOW_CREATION / UI_V2_IMPLEMENTATION（additive）/
UI_CONTRACT_EXTENSION / MOCK_EXTENSION / ADAPTER_EXTENSION /
DOMAIN_COMPONENT_IMPLEMENTATION / HOOK_IMPLEMENTATION（co-located 于 features/ui-v2）/
TEST_IMPLEMENTATION（co-located）/ DOCUMENTATION / VALIDATION /
INDEPENDENT_REVIEW（via Task subagent）

NOT_AUTHORIZED: STAGE / COMMIT / PUSH / MERGE / DEPLOY / PRODUCTION_WRITE /
BACKEND_MODIFICATION / DATABASE_MIGRATION / AUTH_REFACTOR / API_SEMANTICS_CHANGE /
BUSINESS_SEMANTICS_CHANGE（Review 六档评分、Mastery/Weakness/Recommendation 算法）/
WEEK2_PR05_08_MODIFICATION / ROUTE_MIGRATION（不迁移现有路由、不新增顶层路由）/
DESTRUCTIVE_FILE_OPERATION

批准不跨阶段传递到 commit / push / migration / deploy。

## Week2 强隔离（READ-ONLY）

`backend/app/models/review_item.py`、`backend/app/routers/review_items.py`、
`backend/app/schemas/review_item.py`、`backend/tests/test_review_schema_v2.py`、
`alembic/versions/027*` `028*` `029*`、`src/lib/api/review-items.ts`、
`src/lib/content-routes.ts`，以及其他全部
`backend/app/{models,schemas,routers,services,repositories}/**` 与
`alembic/versions/**`。需改这些文件 → STOP，记 Gap/Dependency，申请批准。

## 脏文件保护（READ_ONLY）

Foundation `evidence/baseline-status-frontend.txt` 所列 29 项 tracked modified
（含 `manage-sidebar.tsx`、`dashboard-overview.tsx`、`dashboard-content.tsx`、
`notes/page.tsx`、`tag-input.tsx`、`use-note-editor.ts`、`feature-state.tsx`、
`AGENTS.md`、`agents/*` 等）一律只读。
本轨新增的 Week2 落地文件（`review_item_service.py`、
`test_mistake_review_service.py` 等）同样只读。
绕不开 → STOP 并报告 FILE / CURRENT DIFF / WHY REQUIRED / COLLISION RISK /
PROPOSED OWNERSHIP，记 Blocker 后继续独立任务。

## 写白名单（additive only）

- `docs/workflows/personal-learning-ui-v2/**`
- 新增/扩展：`src/contracts/ui-v2/**`、`src/mocks/ui-v2/**`、
  `src/adapters/ui-v2/**`、`src/components/ui-v2/**`、`src/features/ui-v2/**`
  （含 co-located hooks 与 tests；`src/contracts|mocks|adapters|features` 无
  canonical 目录，沿用 Foundation 决议的 `*/ui-v2` 命名空间）
- Design token 仅 additive（`--uiv2-*`）；`src/styles/theme.css` /
  `globals.css` 零修改；Legacy 语义零改变。

现有页面/路由/layout/sidebar 文件一律不改：U1 App Shell 以新命名空间下的
presentational 组件 + 导航配置形式交付，不替换 `layout.tsx`。

## 阶段

U1 App Shell → U2 Dashboard → U3 Today → U4 Mistakes → U5 Review（UI/Mock/Contract，
集成 BLOCKED_BY_WEEK2）→ U6 Questions → U7 Knowledge → U8 Notes → U9 Analytics →
U10 Resources → U11 Settings → U12 Responsive → U13 Accessibility →
U14 Integration（稳定契约）→ U15 Final QA → U16 Final Gate（申请，不自批）。

每阶段循环：Read → Ownership → Dependencies → Tracker IN_PROGRESS → Implement →
Test → Review → Fix → Re-test → Validate → Docs → Tracker VERIFIED → 下一 READY。

## Gate

主适用 G0（IA/产品语义）/ G1（架构/契约边界）。
触及 Auth/credentials/私有路由/admin 端点语义即触发 G3 → STOP（本轨 G3 内容
NOT_AUTHORIZED）。后端/schema/AI 算法/deploy 分别对应 G2/G4/G5，均不在本轨授权内。

## 唯一总账本

`UI_V2_MASTER_TRACKER.md`（本目录）是 UI V2 唯一进度账本，任务/评审/Gate/
验证/阻塞发生后持续更新，不在结束时补写。
