# Design — UI Foundation Track

执行模式 WORKER；main agent 为唯一 primary_owner 与 code_acceptor。
分类理由：多阶段并行（F0–F5）+ Week2 串行隔离 + API 契约边界，非简单任务。

## 1. 分层架构

```text
Backend DTO (read-only，本轨不碰)
      ↓
Adapter  (src/adapters/ui-v2/*，纯函数映射 + source 标注)
      ↓
UI Contract (src/contracts/ui-v2/*，UI-facing types)
      ↓
UI Component (src/components/ui-v2/*，仅展示 + 状态)
      ↓
Mock (src/mocks/ui-v2/*，source: mock，六态数据)
```

`src/features/ui-v2/` 预留后续业务组装位，本轮只放 skeleton，不做完整页面。

## 2. 目录决策（2026-09-13 审计结论）

仓库现状无 `src/contracts|mocks|adapters|features` canonical 目录，
`src/components/*` 为扁平共享组件（41 项），`src/lib/api/*` 为 typed client
（34 项，`page/component → hook → src/lib/api/* → backend`），样式 token 在
`src/styles/theme.css`（`@theme`，brand `#35bfab`）与 `globals.css`。

决策：采用授权中的新命名空间 `*/ui-v2`（additive，与 Legacy 并存），
最终路径即 `src/{contracts,mocks,adapters,components,features}/ui-v2/`。
如后续发现 canonical 目录，以 design.md 修订版为准并迁移。

## 3. Design token 策略

- 现状 token（`src/styles/theme.css:1-15`）：`--color-brand #35bfab` 等，
  当前文件**非脏文件**，但本轮不修改它（避免全局回归）。
- 新 token 以 `src/components/ui-v2/tokens.css` additive 形式存在，
  仅定义 `--uiv2-*` 前缀变量；Legacy 语义零改变。
- 全局 CSS 修改（如确需）先记入 tasks.md，本轮 F3 未发现必须项，故未执行。

## 4. 组件策略

Inventory 先行（见 `docs/ui-v2/UI_V2_COMPONENT_INVENTORY.md`）：
KEEP（复用：empty-state、async-state-panel、auth-gate、tag-input 现状等）
/ REFACTOR（候选，不动）/ REPLACE / MISSING（本轮仅对 MISSING 建最小 skeleton：
types + 展示组件 + mock + adapter 纯函数）。

## 5. IA 策略

现状路由以 `src/app/**` 为准（blog/notes/mistakes/manage/(workspace)/* 等），
`manage/(workspace)` 下有 dashboard/notes/questions/mistakes/review/subjects/
knowledge-points/capture/ai/attachments/jobs/search/analytics/settings。
输出 Current → Proposed → Status 映射（见 `docs/ui-v2/UI_V2_INFORMATION_ARCHITECTURE.md`），
本轮不迁移路由。

## 6. Mock 与 Mastery 语义

Mock 数据全部 `source: 'mock'`，六态（normal/empty/loading/error/partial/overdue）。
MasteryScore `{ value: number | null, confidence, source }`；
`value: null` 时 UI 显示“暂无足够数据 / 数据积累中”，禁止伪造精度。

## 7. 治理与 STOP

- Week2/Backend/Migration/Auth 文件只读；触发 G3 即 STOP。
- 脏文件只读；ownership 冲突即 STOP（FILE / DIFF / WHY / RISK / PROPOSED）。
- Backend Gap 记入 `docs/ui-v2/UI_V2_BACKEND_GAPS.md`（GAP-ID 递增），不自行修后端。
