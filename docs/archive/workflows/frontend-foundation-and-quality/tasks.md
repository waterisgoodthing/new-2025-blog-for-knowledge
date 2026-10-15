# 任务清单：F4 前总工作夹

## 审批状态

Status: `F4 INPUT READY FOR SEPARATE APPROVAL — FIX-01～05 COMPLETE; G2/G3/G4 PASS; F4 NOT EXECUTED OR AUTHORIZED`

The 2026-08-16 F0–F3 execution record remains historical evidence. FIX-01 added the required public-detail and mounted shared-mobile-navigation browser evidence, so G3 is again `PASS`; the former F4-input-ready conclusion remains suspended until FIX-02 through FIX-05 have independent evidence.

用户已明确批准本修订任务清单与特殊适配器清单。该批准只覆盖本 Goal 的严格顺序任务，不改变各 Gate 的证据标准，也不授权保留为独立审批门的事项。

D2 在 E1～E4 证据完成后再由用户判断。本清单不授权 F4、视觉改造、统一创作面板、JWT/Bearer 迁移、生产 Markdown 切换、路由删除/重定向、Git 操作或部署。

## A. 已完成且不重做的基础

- [x] A1. F0 / FFQ-01～03：完成当前事实、认证合同、依赖和风险冻结；G0 PASS。
- [x] A2. F1 / FFQ-04：完成路由归属 R1～R5；G1 PASS；采用兼容共存/暂缓切换，未实施路由变更。
- [x] A3. F2A / FFQ-05～06：完成 Markdown M1～M6.9 受控评估与文档清理；该历史评估中 Code/Math 有隔离证据、三类特殊适配器为 `DEFERRED_INERT`。后续方案 B 特殊适配器工作夹已补齐三类 `ENABLED_ISOLATED` 证据并关闭 G2，见 C 节。

## B. 总工作夹重建与决策准备

- [x] B1. 已同步父工作夹 README、design、requirements、tasks、audit、validation、handoff，当前入口不再停留在 M6.4/M6.5。
- [x] B2. 已同步 `public-session-state-optimization` 当前前置状态：G0/G1 已通过，但修订清单批准前不得实施。
- [x] B3. 已同步 `editor-convergence` 当前前置状态：G1/G2 已通过，D1 已选 B；E1～E5 仍只做能力合同和后续实现清单，且必须等待 PSS/G3 后才可开始。
- [x] B4. 已建立 F4 输入模板：只列 G2/G3/G4 结论、场景、数据、风险、验证和清理要求，不执行 F4。
- [x] B5. 完成格式、链接、状态、尾随空格和工作树边界检查，并记录规划验证。

## C. D1 / G2：方案 B

- [x] D1. 用户于 2026-08-16 选择 Markdown 产品接受边界方案 B：
  - 方案 A（推荐）：接受 Code + Math 的隔离能力；Mermaid、Markmap、Chart 在 F4 前保持精确 inert fallback；G2 对该明确范围记为 scoped PASS，允许 F3 开始。
  - **已选择方案 B：**要求 Mermaid、Markmap、Chart 全部具备独立安全适配器并通过完整浏览器观测后才关闭 G2；该条件现已满足，F3 仍须等待 G3。
- [x] SA-PLAN. 建立独立的 `markdown-special-adapter-enablement` 工作夹及可审批任务清单。
- [x] SA-01. **COMPLETE (2026-08-16):** 用户已单独批准 Mermaid 依赖/lockfile 更新；`mermaid@11.16.1` 现已锁定，目标 Mermaid 公告清除，浏览器缓存未下载或改变。SA-02 是唯一下一项；证据见特殊适配器工作夹及本工作夹 `audit.md`/`validation.md`。
- [x] SA-02. **COMPLETE (2026-08-16):** 共享 browser harness 现可卸载；三类候选各有 SSR/hydration/恶意更新/重复渲染/卸载与主动观测的红灯基线，隔离输出当前均为 `false / 0 / 0`，artifacts 已留存。Mermaid-01 是唯一下一项。
- [x] Mermaid-01. **COMPLETE (2026-08-16):** Mermaid 最终 SVG 结构合同从 2 个红灯收敛到 3/3 聚焦通过；首个失败 artifact 已留存。该结构证据不等同于浏览器启用。
- [x] Mermaid-02. **COMPLETE (2026-08-16):** 受限静态 flowchart 由 PoC 直接构造有限 SVG；SSR/hydration、恶意更新的精确局部回退、重复渲染、事件、主动浏览器观察与卸载均通过。Mermaid 库的实际 HTML-bearing SVG 未被接纳为最终输出；首个失败与通过 artifacts 已留存。Mermaid-03 是唯一下一项。
- [x] Mermaid-03. **COMPLETE / `ENABLED_ISOLATED` (2026-08-16):** 全 PoC 及相关 Chromium matrix 均通过，Mermaid 仅在隔离 PoC 的受限静态 flowchart 语法下输出 PoC-owned finite SVG；恶意输入精确 local fallback。没有生产 `markdown-poc` 引用、生产消费者切换或 legacy fallback。Markmap-01 是唯一下一项；G2 继续 BLOCKED / NOT GO。
- [x] Markmap-01. **COMPLETE (2026-08-16):** 独立 unit/browser failing-first 合同已留存；安全 Markmap 没有 final SVG，恶意链接输入仍是 inert，unit `2 failed`、browser `1 failed`。没有 Mermaid 结论继承或生产调用。Markmap-02 是唯一下一项。
- [x] Markmap-02. **COMPLETE (2026-08-16):** PoC-owned 受限标题树直接生成静态 finite SVG；链接/HTML/CSS、平移缩放、下载、导航、外部资源均不进入输出，恶意输入精确 local fallback。聚焦 unit/browser 通过，final-pass artifact 已留存。Markmap-03 是唯一下一项。
- [x] Markmap-03. **COMPLETE / `ENABLED_ISOLATED` (2026-08-16):** 全 PoC 及相关 Chromium matrix 通过；Markmap 仅在隔离 PoC 的受限标题树语法下输出 PoC-owned static finite SVG，恶意 link-like source exact local fallback。没有生产 `markdown-poc` 引用或生产消费者切换。Chart-01 是唯一下一项；G2 继续 BLOCKED / NOT GO。
- [x] Chart-01. **COMPLETE (2026-08-16):** 独立 Canvas/JSON failing-first 合同为 unit `2 failed`、browser `1 failed`；安全 JSON 无 Canvas，formatter JSON 仍 inert。没有 ECharts/生产调用。Chart-02 是唯一下一项。
- [x] Chart-02. **COMPLETE (2026-08-16):** PoC-owned strict bar JSON parser + SSR Canvas + client 2D draw 通过；未批准 config/local code/network/download 全为 exact local fallback。Chart-03 是唯一下一项。
- [x] Chart-03. **COMPLETE / `ENABLED_ISOLATED` (2026-08-16):** strict JSON、SSR/hydration Canvas draw、恶意 local fallback、重复 render/主动观察/unmount 全部通过；生产 consumer 未改。SA-03 是唯一下一项；G2 仍 BLOCKED / NOT GO。
- [x] SA-03. **COMPLETE (2026-08-16):** 三适配器混合 unit/browser 闭环通过，安全输出共存、恶意输入局部回退且无主动安全事件。SA-04 是唯一下一项。
- [x] SA-04. **COMPLETE (2026-08-16):** full PoC `288/288`、passing Chromium matrix `15/15`、TypeScript、Batch 7 `4/4`、Prettier、production isolation、links/whitespace 全部 PASS。
- [x] G2. **PASS / GO FOR F3 EVIDENCE ONLY (2026-08-16):** 三适配器均 `ENABLED_ISOLATED`，SA-03/04 通过；不授权生产 Markdown consumer 切换或任何 M7/视觉/Git/部署动作。

## D. F2B：公开会话状态优化

严格执行 `public-session-state-optimization/tasks.md`，一次只做一项；每完成一项立即同步父/子 `tasks.md` 与 `validation.md`。

- [x] PSS-01. **COMPLETE (2026-08-16):** 已冻结 optional/strict Cookie-session 合同和 16 个运行时消费者矩阵：14 个 hook 调用点（12 public、1 shared nav、1 strict AuthGate）及 2 个 direct strict 调用均已归属。
- [x] PSS-02. **COMPLETE (2026-08-16):** failing-first backend contract `4 failed / 1 passed / 3 warnings` 在 endpoint 缺失时成立；PSS-03 后最终 `5 passed`、warnings 归零，strict anonymous `/api/auth/me` 保持 401。
- [x] PSS-03. **COMPLETE (2026-08-16):** 最小 `SessionStateOut` + Cookie-resolver route 通过目标 `5/5` 和既有 auth/write `9/9` 回归；`get_current_admin`、写入、AI、上传、复习均未改。PSS-04 是唯一下一项。
- [x] PSS-04. **COMPLETE (2026-08-16):** frontend red suite `5 failed / 3 passed` became focused `14 passed`; typed optional state, explicit modes/error visibility, dual-key invalidation and explicit strict AuthGate are in place. Source TypeScript PASS; PSS-05 is the only next item.
- [x] PSS-05. **COMPLETE (2026-08-16):** explicit optional-source contract `14 failed` became full focused `30 passed`; all 12 public pages/details, shared nav and blog-index display state now avoid strict `/api/auth/me`. Source TypeScript PASS; PSS-06 is the only next item.
- [x] PSS-06. **COMPLETE (2026-08-16):** failing browser evidence first retained six `/api/folders` requests, then final isolated Playwright `3 passed (7.8s)` proved anonymous no strict/admin noise, valid admin display state, logout, expired-session anonymous downgrade, strict `/manage` login state, zero strict-page 5xx, and port cleanup. Shared optional key and public folder guards only; no permission broadening.
- [x] G3. **PASS / GO FOR F4 INPUT REPAIR ONLY (2026-08-16):** 历史 PSS-01～06 browser `3 passed` 的列表/会话证据现由 FIX-01 当前隔离 Playwright `5 passed (12.6s)` 补齐公开博客详情、公开笔记详情和 390px 真实挂载共享移动导航。匿名场景均无 strict `/api/auth/me`、folders/review/admin/AI/attachments、管理入口、page error、意外 5xx、就绪后导航、对话框或下载；严格 `/api/auth/me`、`/manage` 和既有后端权限未改。只允许继续质量修复与形成 F4 输入；不授权 F4、JWT/Bearer、权限放宽、生产 Markdown 迁移、Git 或部署。

## E. F3：编辑器能力收敛

前置：G2 已按 D1 关闭。F3 不实施统一编辑器，不移动路由，不改 schema。

- [x] E1. **COMPLETE (2026-08-16):** source-only inventory recorded all current note/blog/mistake owners, save paths, preview owners, typed Note fields and AuthGate/backend boundaries. It records the legacy `/write/[slug]` page-level AuthGate gap without changing it; backend mutations remain protected. E2 is the only next item.
- [x] E2. **COMPLETE (2026-08-16):** capability matrix identifies only typed mutation boundary, tag/save-state support and a blog/note-only Markdown selection/insert/wrap core as future candidates. Preview, AI, image, version/review, route access and all mistake-specific behavior are explicit non-common exclusions. E3 is the only next item.
- [x] E3. **COMPLETE (2026-08-16):** field/save/preview/permission matrices freeze first-class mistake and review data, protected AI/upload/review, public-read filters, backend `get_current_admin`, differing concurrency semantics and the legacy blog-edit page-gate residual. No normalization or source change. E4 is the only next item.
- [x] E4. **COMPLETE (2026-08-16):** source-backed comparison supports only “minimal shared primitives + domain-editor coexistence” as a future direction with import-level rollback. Larger unified-owner option is documented high-risk and unevidenced; no source refactor. D2 is now required.
- [x] D2. **COMPLETE (2026-08-16):** user selected the evidenced “minimal shared primitives + domain-editor coexistence” direction. It releases E5 documentation only; it does not authorize editor implementation, route/AuthGate changes, schema/API/renderer changes, visual work, Git, deployment or F4.
- [x] E5. **COMPLETE (2026-08-16):** `editor-convergence/implementation-tasks.md` is a separate, explicitly unapproved Option A implementation list. It starts with characterization tests, limits any future extraction to blog/note primitives, preserves typed mistake/review data, and isolates the legacy blog edit AuthGate gap as security work. No implementation occurred; G4 is next.
- [x] G4. **PASS / GO FOR F4 INPUT ONLY (2026-08-16):** E1–E5 source-backed matrices and the separately gated Option A implementation list complete the editor contract. First-class mistake/review fields, save/preview owners, strict/backend permission boundaries and rollback are explicit. Residual legacy blog-edit AuthGate gap, concurrency divergence and unchanged renderer are carried forward; no editor/security implementation is claimed.

## F. F4 输入包与本轮关闭

- [x] F4-IN-01. **COMPLETE (2026-08-16):** `f4-input-package.md` 汇总 G2/G3/G4 的限定结论、残余风险和禁止项；没有把 Gate PASS 扩张为生产迁移或 F4 执行授权。
- [x] F4-IN-02. **COMPLETE (2026-08-16):** 输入包冻结 E0/L20/D1/M30：匿名列表/详情、确定性普通 Markdown 详情、管理员登录及管理列表。
- [x] F4-IN-03. **COMPLETE (2026-08-16):** 输入包冻结 ready/empty/error 状态、非敏感合成数据、隔离数据库/API/建议端口和构建/浏览器前提；端口必须先确认空闲，不得驱逐用户进程。
- [x] F4-IN-04. **COMPLETE (2026-08-16):** 输入包冻结失败保留、冷/热样本、每场景至少 10 个有效样本、p50/p90/最大值/失败率、artifact 与清理证据要求。
- [x] F4-IN-05. **COMPLETE (2026-08-16):** `production-render-readiness-acceptance` 当前任务清单成为单独审批入口；本轮未运行 instrumentation、生产构建、合成数据或性能采样。
- [x] CLOSE. **COMPLETE (2026-08-16):** 父/子状态已同步；F4 输入结论为 `READY FOR SEPARATE APPROVAL`，而非 F4 PASS；未暂存、提交、推送、部署或执行 F4。

The F4 entries above are a historical 2026-08-16 snapshot. They were not the current entry condition during FIX-01～FIX-05; the current conclusion is recorded by the completed repair section and validation audit below.

## G. F4 前质量审查修复（已批准；严格顺序执行）

- [x] FIX-01. **COMPLETE (2026-08-16):** PSS 当前隔离 Chromium 回归 `5 passed (12.6s)` 覆盖公开博客详情、公开笔记详情和 390px 真实挂载共享移动导航，所有要求的匿名网络、权限、页面副作用断言通过。G3 独立重判为 `PASS`；F4 仍未授权。
- [x] FIX-02. **COMPLETE (2026-08-16):** `markdownFixtures` 显式声明为 `readonly MarkdownFixture[]`，使 `MarkdownFixtureExpectation` 的可选 `contains`、`absent`、`toc` 在 unit/SSR fixture 筛选后安全访问；未使用 `any`、忽略指令、严格模式放宽或删/弱断言。`npm run test:typecheck` PASS，相关 Markdown PoC unit/SSR 为 `206 passed`。
- [x] FIX-03. **COMPLETE (2026-08-16):** 已同步六个相关父子 workflow 的 README/tasks/audit/validation 当前 Gate、下一任务和测试计数语义；父级 validation 顶部、route-ownership 的过期 `EXECUTING` 当前态及 F4 输入包固定计数均已修正。历史计数保留为明确快照；当前结论只引用本轮命令或 FIX-05 完整回归。
- [x] FIX-04. **COMPLETE (2026-08-16):** 已清理本轮 F4 输入包内同表格的纯格式对齐；PSS browser fixture、Markdown fixture 和本轮目标工作流文档通过 Prettier、尾随空白和 `git diff --check`。未格式化扩散到路由历史表格或 Playwright 生成 `.last-run.json`，并保留所有 Mermaid、Playwright、PSS、测试与权限语义修改。
- [x] FIX-05. **COMPLETE (2026-08-16):** 完成相关/无关修改、未跟踪文件、完整验证、warnings、残余风险、端口清理和交付边界审计。结论为“F4 输入已就绪，可等待单独审批”；F4、生产构建、部署、Git 发布均未执行。

执行纪律：严格按 FIX-01 → FIX-02 → FIX-03 → FIX-04 → FIX-05，一次只执行一项。每项完成后立即同步对应父子 `tasks.md` 与 `validation.md`，再开始下一项；先运行最小聚焦检查，再运行完整相关回归。源码或测试在本清单获明确批准前不得修改。

## 必须暂停

- D2 未由用户明确选择，却准备推进依赖它的阶段；
- 需要 JWT/Bearer 迁移、CORS 扩展、`AUTH_BYPASS`、真实数据/凭据或生产 API；
- 需要路由删除/重定向、生产 Markdown 切换、统一编辑器实现、视觉改造或 F4 实施；
- 公开页面被 AuthGate 封闭、严格权限被放宽或 mistake 一等字段可能丢失；
- 当前脏工作树与目标文件发生无法安全保留的重叠。
