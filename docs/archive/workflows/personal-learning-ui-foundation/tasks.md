# Tasks — F0–F5（串行，F5 后停止）

> 白名单外现有文件默认 READ-ONLY。任一任务触发 STOP 条件即停该项，
> 保已有安全成果并报告。

## Phase F0 — Baseline + Repository UI Audit
- [x] T-F0-1 建 workflow 五件套 + `docs/ui-v2/` 目录（本文件组）。
- [x] T-F0-2 冻结独立基线：`evidence/baseline-status-frontend.txt` +
  `evidence/baseline-frontend.diff`（PRE-EXISTING 52 项）。
- [ ] T-F0-3 Repository UI Audit：路由 / 组件 / token / api client 现状
  （输出 `docs/ui-v2/UI_V2_ARCHITECTURE.md`）。

## Phase F1 — Component Inventory
- [ ] T-F1-1 盘点 `src/components/*`（41 项）+ 相关 ui（manage/components、
  notes components、write editor ui），输出 KEEP / REFACTOR / REPLACE / MISSING
  （`docs/ui-v2/UI_V2_COMPONENT_INVENTORY.md`）。
- [ ] T-F1-2 仅对 MISSING 建最小 skeleton（types + 展示），REFACTOR 记候选不动。

## Phase F2 — Information Architecture
- [ ] T-F2-1 输出 Current Route → Proposed Route → Status
  （`docs/ui-v2/UI_V2_INFORMATION_ARCHITECTURE.md`），不迁移路由。

## Phase F3 — Design System Foundation
- [ ] T-F3-1 建立 additive token `src/components/ui-v2/tokens.css`（`--uiv2-*`）。
- [ ] T-F3-2 建立 `docs/ui-v2/UI_V2_DESIGN_SYSTEM.md`
 （Typography/Semantic Color/Spacing/Radius/Elevation/Interaction/Responsive/A11y）。
- [ ] T-F3-3 全局 CSS 修改评估：本轮结论为**无需修改**（`globals.css`/`theme.css`
  保持零改动）；如后需，先记此处再执行。

## Phase F4 — Contract / Mock / Adapter Skeleton
- [ ] T-F4-1 `src/contracts/ui-v2/`：`review-task.ts`（ReviewTask）、
  `mastery.ts`（MasteryScore）、`ui-state.ts`（LoadingState/PageState）、`index.ts`。
- [ ] T-F4-2 `src/mocks/ui-v2/`：`dashboard.ts`、`review.ts`、`mistakes.ts`（六态，
  `source: 'mock'`），`index.ts`。
- [ ] T-F4-3 `src/adapters/ui-v2/`：`from-backend.ts`（Backend unknown → UI Contract，
  缺字段 → null + estimated，不抛伪造值）、`index.ts`。
- [ ] T-F4-4 `src/features/ui-v2/`：仅 `README.md` 占位（后续业务组装位）。
- [ ] T-F4-5 Backend Gaps：`docs/ui-v2/UI_V2_BACKEND_GAPS.md` + `UI_V2_PROGRESS.md`。

## Phase F5 — Validation + Documentation
- [ ] T-F5-1 按仓库 scripts 执行：`tsc --noEmit` / `vitest run`（目标化）/
  lint（仓库无 lint script → NOT_APPLICABLE，如实记）/ `next build`（按成本决定，
  未跑则 NOT_APPLICABLE）/ `git diff --check`。
- [ ] T-F5-2 合规核对：Week2 files / Backend / Migration / Auth / 脏文件零新增修改
  （`git status` 对比基线）。
- [ ] T-F5-3 最终汇报（按授权 §21 格式），状态 STOP AFTER FOUNDATION。
