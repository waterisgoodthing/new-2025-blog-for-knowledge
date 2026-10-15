# 审计

当前状态：`SA-01～04 HISTORICAL COMPLETE；Mermaid / Markmap / Chart 均 ENABLED_ISOLATED；G2 ISOLATED PASS；FIX-03～05 COMPLETE；F4 INPUT READY FOR SEPARATE APPROVAL；NO PRODUCTION MIGRATION OR F4`。

## 2026-08-16 方案 B 建档

- 用户已明确选择 D1 方案 B：Mermaid、Markmap、Chart 必须全部具备独立安全适配器并通过完整浏览器观测，G2 才能关闭。
- 现有 M6 证据不能满足该边界：三条路径当前均为精确文本 `DEFERRED_INERT`。
- 当前 `package.json`/`package-lock.json` 已声明 Mermaid、Markmap、ECharts 和 D3 相关依赖；这只说明候选实现存在，不证明其当前版本、安全边界或适配器可直接启用。
- Math 的 `ENABLED_ISOLATED` 结论不能转授给 SVG、DOM 或 Canvas 路径。
- 当前无需用户选择具体库或白名单细节；这些先由 SA-01 用当前证据收敛。

## 仍需用户判断

1. 历史：父工作夹修订清单、本工作夹任务和 SA-01 依赖/lockfile 判断已各自获批并关闭。
2. 当前：FIX-03 只同步历史快照与当前 Gate；不需要、也不取得生产迁移或 F4 授权。
3. 未来：任何新的依赖、浏览器二进制、产品交互扩张、生产消费者或 F4 均须重新独立批准。

除此之外，测试组织、白名单编码、隔离端口、synthetic fixtures、artifact 命名和逐适配器技术修正由执行代理按冻结合同处理。

## 2026-08-16 SA-01 当前证据与暂停

结论：`BLOCKED — dependency/lockfile approval required before SA-02`。

- 运行时为 Node `v24.18.0` / npm `11.16.0`；当前安装图中有 `@playwright/test@1.62.1`、`mermaid@11.15.0`、`markmap-lib@0.18.12`、`markmap-view@0.18.12`、`echarts@6.1.0`、`echarts-for-react@3.0.6`、`katex@0.16.47` 与 `marked@17.0.6`。对应直接包的记录许可证分别为 Apache-2.0、MIT、MIT、Apache-2.0、MIT、MIT、MIT。
- 现有浏览器缓存含 `chromium-1234` 与 `chromium_headless_shell-1234`；`npx playwright --version` 是 `1.62.1`。本阶段不需要下载浏览器二进制。
- `npm audit --omit=dev --json` 返回 8 条总公告（3 moderate / 5 high）。其中直接目标 `mermaid@11.15.0` 命中 5 条：GHSA-c4c3-pg64-4m4v（low）、GHSA-6x64-9x62-f2gx（moderate）、GHSA-3rrr-jr9j-h3q3（moderate）、GHSA-2v8p-3f2j-5mp7（moderate）和 GHSA-rhh3-jpg6-66xh（moderate）；所有受影响范围覆盖当前版本，修复范围均从 `11.16.1` 开始。
- 生产代码确有 Mermaid、Markmap、ECharts 动态消费者，但 Goal 禁止迁移它们；PoC 当前只对 Math 启用，Mermaid/Markmap/Chart 仍为 `DEFERRED_INERT`，且尚无 PoC-owned SVG/Markmap DOM/Canvas 边界。
- 最小可行下一步是将 Mermaid 解析/渲染库提升到至少 `11.16.1` 并重新锁定后再设计 Mermaid 白名单。这会改动当前用户已有的 `package.json` 与 `package-lock.json`；在获得明确批准前不得执行安装、升级、lockfile 写入、SA-02 或实现。

### 已批准的最小修正

- 用户已明确批准 Mermaid 升级及根 `package.json`/`package-lock.json` 更新。执行 `npm install mermaid@11.16.1 --save --ignore-scripts` 后，直接声明与锁定版本均为 `11.16.1`，许可证仍是 MIT。
- 锁文件中 Mermaid 的最小传递更新包括 `@mermaid-js/parser 1.2.0`、Cytoscape `3.33.3`、DOMPurify `3.4.12` 及其现有 Mermaid 解析链要求；没有修改 Markmap、ECharts、KaTeX、Playwright 或生产消费者声明。
- 复跑 `npm audit --omit=dev --json` 后，目标 `mermaid` 键不再出现；全仓仍有 7 条非 Mermaid 公告（2 moderate / 5 high），不构成对本适配器库已解除公告的替代证明，后续启用仍须通过独立白名单和浏览器合同。

## 2026-08-16 SA-02 测试先行共享基线

结论：`COMPLETE — shared harness green; all three adapter output contracts intentionally red`。

- 首个失败：新浏览器测试要求 `window.__markdownPocBrowserHarness.unmount`，当前值是 `undefined`，因此无法验证重复渲染后的显式 React 清理。最小修正只在 test-only harness 中将既有 React root 的 `unmount()` 暴露为 `unmount()`；不触及 renderer 或生产代码。修正后该测试 `1 passed`。
- 三条共享候选测试在 SSR、hydration、恶意输入更新、两次安全重复 render、合成 click/error/load、主动 pageerror/console/dialog/request/navigation/download 观察和卸载后才断言最终输出。三条均以预期 `true / 1 / 1`、实际 `false / 0 / 0` 失败，证明当前 `DEFERRED_INERT` 状态而不是环境或观察器故障。
- 三条红灯均未出现 script sentinel、page/console error、dialog、download、非 localhost request 或 post-hydration navigation；这只是当前 inert 安全基线，绝不等同于方案 B 的 enablement。
- artifacts：harness 的首个失败截图/trace/error context 与 Mermaid、Markmap、Chart 各自的失败截图/trace/error context 均保留在 `assets/playwright-test-results/`。没有删除历史 assets。

## 2026-08-16 Mermaid-01 最终 SVG 合同

结论：`COMPLETE — structural boundary only; browser enablement remains unproven`。

- 首个聚焦运行 `mermaid-isolated.test.ts` 为 `2 failed`：有效 synthetic flowchart 仍无 `svg[data-poc-mermaid]`，恶意 Mermaid 结果仍为 `inert` 而不是带 `LOCAL_FALLBACK` 的精确代码文本。完整失败记录在 `assets/mermaid-01-first-failure.md`。
- 最小隔离边界限制为 4 个方向的非交互式 flowchart 和无 HTML/引号/实体的节点文本；SSR 输出仅为安全 SVG placeholder，浏览器最终输出另由 Mermaid 渲染后净化。它不使用生产 `MermaidBlock`、旧 Markdown renderer 或 bindFunctions。
- Sanitizer 合同白名单允许有限 SVG 元素/属性和本地 marker fragment；移除 style，并拒绝任何未知结构、`foreignObject`、script、链接/外部 URL、事件、href/xlink、style、HTML labels 或不受控 id。每个生成 id 重写在 `poc-mermaid-*` 根下。
- 聚焦结果为 `1 file / 3 tests passed`。两轮有新证据的修正均局限于 source gate：先允许流程箭头的 `>`，再按 XML 实际属性名接受 `markerWidth`/`markerHeight`。未扩大输入语法或产品交互。

## 2026-08-16 Mermaid-02：PoC-owned final SVG browser boundary — COMPLETE

- 首个真实浏览器失败显示 Mermaid `11.16.1` 即使采用 strict/no-html-label configuration，仍为普通 flowchart 生成 `foreignObject`、HTML `div`/`span`/`p`、`style`、filters 及 data attributes。PoC 没有将这些元素或属性纳入白名单，也没有把旧生产链作为 fallback。
- 以这项单一新证据作第三次也是最后一次聚焦架构修正：保留已冻结的 4 个方向、非交互、受限节点标签语法，改由 `src/lib/markdown-poc/mermaid.ts` 直接构造其有限 SVG schema。节点标签、rect 和 marker 连线仍可用；不存在 HTML、CSS、外部 URL、事件、网络请求或 Mermaid `bindFunctions`。
- Playwright 的完整单适配器周期通过。它覆盖 SSR、安全 hydration、恶意更新到精确 local fallback、两次安全更新、最终 SVG、script sentinel、click/error/load、page/console error、dialog、request、navigation、download 与 explicit unmount。唯一 warning 是环境已有的 `NO_COLOR`/`FORCE_COLOR`，没有安全观察。
- 首个失败记录为 `assets/mermaid-02-first-failure.md`，其 Playwright screenshot/error context/trace 在同名 `playwright-test-results` 目录；最终通过截图为 `assets/mermaid-02-final-pass.png`。该完成只允许 Mermaid-03 关闭验证继续，尚不把 Mermaid 记为 `ENABLED_ISOLATED`，G2 仍为 BLOCKED / NOT GO。

## 2026-08-16 Mermaid-03：关闭验证 — PASS / `ENABLED_ISOLATED`

- 初始全 PoC 回归为 `9 files / 285 tests`，8 个失败全都来自历史 `DEFERRED_INERT` expectation；没有 SVG、SSR/hydration、恶意输入或观察器安全失败。以此单一失败类别更新 fixtures、decision registry 与历史 inert assertions，明确有效静态图为 allow、恶意图为 exact `LOCAL_FALLBACK`。
- 同一全 PoC 命令最终为 `9 files / 284 tests passed`。jsdom 输出有既有 `act(...)` test-environment messages（12），不涉及 Mermaid 可执行行为；无新增 Vitest failure。
- 同配置 Chromium 的 `inert-baseline.spec.ts` 加 `mermaid-isolated.spec.ts` 为 `11 passed (2.1s)`。专用 Mermaid case 覆盖 SSR/hydration/hostile update/two safe rerenders/final SVG/script sentinel/click-error-load/page-console error/dialog/request/navigation/download/unmount；没有安全观察，唯一环境 warning 是 `NO_COLOR`/`FORCE_COLOR`。
- `rg` 证明 `src/` 在 `src/lib/markdown-poc/` 之外零 `markdown-poc` 引用。生产 `MermaidBlock`/`use-markdown-render` 和 notes detail 仍有旧 Mermaid 参考，但完全未改、未被这个 adapter 调用或作为 fallback；这正是生产迁移未获授权的安全边界。
- Mermaid 现在单独为 `ENABLED_ISOLATED`。Markmap、Chart 仍为 `DEFERRED_INERT`，所以 G2 仍 `BLOCKED / NOT GO`，F3 不得开始。

## 2026-08-16 Markmap-01：独立失败基线 — COMPLETE

- Markmap 没有继承 Mermaid 的安全边界。新的 unit contract 先要求有限 `svg[data-poc-markmap="rendered"]` 和恶意 link-like source 的 exact local fallback；当前分别以无 SVG、`inert` 而非 `local-fallback` 失败（`2 failed`）。
- 新的 Chromium test 先对 SSR `data-poc-markmap="rendered"` 失败，实际只得到 inert code surface。failure bundle 有 screenshot/error context/trace，首个失败正文在 `assets/markmap-01-first-failure.md`。
- 失败路径没有调用 production `MarkmapBlock`、Markmap library、链接、导航、下载或外部资源。下一项唯一是 Markmap-02；G2/F3 仍 BLOCKED / NOT GO。

## 2026-08-16 Markmap-02：PoC-owned static SVG boundary — COMPLETE

- 最小实现不接受 production `markmap-lib`/`markmap-view` 的 transform 或交互输出。它只解析 `#`～`###` 的受限、安全标题树，并生成 rect/text/path 的有限 SVG；标签、边和 IDs 都由 PoC 给出，源文本不直接转成 DOM/URL。
- 自动平移缩放、链接、导航、下载、CSS 和外部资源均明确禁用而不是靠前端隐藏。恶意或不完整标题树直接成为 exact `code[data-poc-inert="markmap"]` 加 `LOCAL_FALLBACK`。
- 聚焦 unit `1 file / 2 tests passed`；真实 Chromium case `1 passed (1.2s)`，覆盖 SSR/hydration、恶意更新、两次安全更新、final SVG、script sentinel、click/error/load/wheel/pointerdown、page/console error、dialog/request/navigation/download 和 unmount。唯一 warning 是 `NO_COLOR`/`FORCE_COLOR`。
- first-failure artifact 为 `assets/markmap-01-first-failure.md` 与 failure bundle，final-pass screenshot 为 `assets/markmap-02-final-pass.png`。Markmap-03 仍必须独立关闭；G2/F3 保持 BLOCKED / NOT GO。

## 2026-08-16 Markmap-03：关闭验证 — PASS / `ENABLED_ISOLATED`

- 初始全 PoC 回归为 `10 files / 286 tests`，8 个失败都是历史 Markmap `DEFERRED_INERT` expectations；没有 static SVG、SSR/hydration、恶意 link-like source 或主动观察失败。fixture、decision registry 与历史 inert assertions 同步为 allow/local-fallback 后，同一命令为 `10 files / 285 tests passed`。
- 同配置 Chromium 的 `inert-baseline.spec.ts` 加 `markmap-isolated.spec.ts` 为 `11 passed (2.2s)`。它覆盖 SSR/hydration/hostile update/two safe rerenders/final SVG/script sentinel/click-error-load-wheel-pointerdown/page-console error/dialog/request/navigation/download/unmount；没有安全观察，仅有 `NO_COLOR`/`FORCE_COLOR` 环境 warnings。
- `rg` 证明 `src/` 在 `src/lib/markdown-poc/` 外零 `markdown-poc` 引用。原生产 `MarkmapBlock`/`use-markdown-render` 仍声明 Markmap library 动态导入，却未被本 adapter 改动或作为 fallback；生产迁移仍未获授权。
- Markmap 现在单独为 `ENABLED_ISOLATED`，且其受控能力特意是 static view（不启用 pan/zoom/link/navigation/download）。Chart 仍 `DEFERRED_INERT`，所以 G2/F3 继续 BLOCKED / NOT GO。

## 2026-08-16 Chart-01：独立失败基线 — COMPLETE

- 安全 bar JSON 缺少 final Canvas，formatter-bearing JSON 保持 inert；新的 unit contract 为 `2 failed`，Chromium SSR contract 为 `1 failed`。first-failure text 和 screenshot/error context/trace 已留存。
- 失败不调用 ECharts、动态代码、Canvas drawing、网络、下载、生产 ChartBlock 或旧 renderer。Chart-02 是唯一下一项；G2/F3 继续 BLOCKED / NOT GO。

## 2026-08-16 Chart-02：PoC-owned Canvas boundary — COMPLETE

- `chart.ts` 使用 JSON.parse 后的 exact-key allowlist，只允许 bounded bar `type`、labels、series 与 finite numbers；formatter、unknown key、HTML-like label、函数形态与不完整数据都 local-fallback。没有 ECharts 或生产 ChartBlock。
- SSR 仅输出固定尺寸、无 style/event/URL 的 Canvas；hydration effect 仅对该 Canvas 调用 PoC-owned 2D draw。browser 验证 `1 passed (1.0s)` 确认画布 context 与 `data-poc-chart-drawn=true`，同时无 network/download/navigation。
- `assets/chart-01-first-failure.md` 与 failure bundle 保留首个失败；最终 screenshot 为 `assets/chart-02-final-pass.png`。Chart-03 仍须关闭，G2/F3 BLOCKED / NOT GO。

## 2026-08-16 Chart-03：关闭验证 — PASS / `ENABLED_ISOLATED`

- 全 PoC 初始 `11 files / 287 tests` 的 8 failures 均是历史 Chart inert expectations；同步后 closing run 为 `11 files / 286 tests passed`。相关 Chromium matrix（inert baseline + chart）为 `11 passed (2.1s)`，仅 `NO_COLOR`/`FORCE_COLOR` warnings，零安全观察。
- Chart 仅允许 PoC-owned bounded bar JSON、SSR Canvas 和 client 2D draw；formatter/unknown keys/local code/network/download 均不进入输出并精确回退。生产 ChartBlock/ECharts 未调用；PoC 外 `markdown-poc` 引用为零。
- 三个特殊适配器现均 `ENABLED_ISOLATED`；下一项 SA-03 仍须完成跨适配器 fallback/TOC/warnings/outcome 残留闭环，G2/F3 目前不提前关闭。

## 2026-08-16 SA-03 cross-adapter closure — COMPLETE

- mixed unit `2/2` 与 Chromium `1 passed (1.4s)` 证明三条安全输出共存、三条恶意路径 local fallback、TOC/warnings/outcome/global fallback 无串扰；无 XSS/error/dialog/download/non-local request/navigation/unmount residue。SA-04 是唯一下一项。

## 2026-08-16 SA-04 / G2 — PASS

- Full PoC `12 files / 288 tests passed`; passing Chromium matrix `15 passed (3.1s)`; `tsc --noEmit` and Batch 7 `4/4` passed. Prettier, PoC-outside production reference check, six-file local links and trailing-whitespace checks passed.
- Residual non-target warnings: 12 existing jsdom `act(...)` environment messages and Playwright `NO_COLOR`/`FORCE_COLOR`; no security observation or production consumer reference exists.
- G2 is PASS only for the next F3 evidence work. It explicitly does not approve M7, production renderer migration, routing, visuals, Git, deployment, or real data.
