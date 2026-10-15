# 验证记录

Status: `SA-01～04 HISTORICAL COMPLETE; Mermaid / Markmap / Chart = ENABLED_ISOLATED; G2 ISOLATED PASS; FIX-03～05 COMPLETE; F4 INPUT READY FOR SEPARATE APPROVAL; NO PRODUCTION MIGRATION OR F4`

Current repair interpretation: SA-01～04 and their fixed totals below are dated 2026-08-16 historical snapshots. G2 remains an isolated-scope PASS; FIX-05 must supply any new full-run count before an F4 input can be declared ready.

## 2026-08-16 建档

- 已记录 D1 方案 B，G2 保持 BLOCKED / NOT GO，F3 保持阻塞。
- 已把 Mermaid、Markmap、Chart 拆为独立的失败测试、最小实现和关闭验证任务。
- 已保留依赖/lockfile/浏览器变更、生产消费者、M7、Git 和部署的独立授权边界。
- 本轮只创建规划文档，没有修改源码、依赖、lockfile 或浏览器环境，也没有运行实现测试。
- 父工作夹、原 Markdown PoC、编辑器工作夹和本工作夹的当前状态已同步；受影响文档格式、本地链接和行尾空白检查通过。
- 当前执行 Goal 已集中到父工作夹 `handoff-prompt.md`，本工作夹交接文件只保留权威链接，避免两份 Prompt 漂移。

实施验证从 SA-01 获批后开始。每项必须记录首个相关失败、修正、最终命令、版本、计数、warnings、artifacts 和残余风险。

## 2026-08-16 SA-01 验证

结论：`BLOCKED — 未获依赖/lockfile 变更批准；G2 = BLOCKED / NOT GO`。

| 检查               | 精确命令或观察                                                                                                                                                                                                | 结果                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 运行时与直接安装图 | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" node --version && npm --version && npm ls --depth=0 @playwright/test mermaid markmap-lib markmap-view echarts echarts-for-react react react-dom katex marked` | Node `v24.18.0`、npm `11.16.0`；目标包均已安装，Mermaid 为 `11.15.0`                                    |
| lockfile / license | 读取根 `package.json` 和 `package-lock.json` 的 `packages` 条目                                                                                                                                               | `@playwright/test@1.62.1`、Mermaid `11.15.0`、Markmap `0.18.12`、ECharts `6.1.0`；许可证已记录在 audit  |
| 浏览器可用性       | `npx playwright --version` 与 `$HOME/Library/Caches/ms-playwright` 目录清点                                                                                                                                   | runner `1.62.1`；已有 Chromium/headless shell `1234`，零下载                                            |
| 公告               | `npm audit --omit=dev --json`                                                                                                                                                                                 | 退出码 `1`；总计 `3 moderate / 5 high`。目标 Mermaid 命中 5 条公告，其中 4 moderate，修复下限 `11.16.1` |
| 当前隔离缺口       | `rg` 当前生产消费者与 `src/lib/markdown-poc/` 特殊适配器状态                                                                                                                                                  | PoC Mermaid/Markmap/Chart 均 `DEFERRED_INERT`；尚无自有 SVG/DOM/Canvas 边界                             |

没有运行 failing-first 测试或 Playwright 矩阵，因为 SA-02 尚未获准进入；没有生成失败/通过 artifact，也没有修改源码、依赖、lockfile 或浏览器缓存。残余风险是当前 Mermaid 安全公告未解除；不得以 inert 结论冒充方案 B 的 G2 PASS。

### 已批准依赖修正（2026-08-16）

- 用户批准后执行：`env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npm install mermaid@11.16.1 --save --ignore-scripts`。结果：`added 1 package, changed 2 packages`；根声明 `^11.16.1`、锁定版本 `11.16.1`、MIT 许可证。
- `npm ls --depth=0 mermaid` → `mermaid@11.16.1`。`npm audit --omit=dev --json` 仍以退出码 `1` 返回全仓 7 条非 Mermaid 公告（2 moderate / 5 high），但 JSON 中没有 `mermaid` 键；此前的 5 条 Mermaid 公告已解除。
- Playwright 缓存清点仍为既有 Chromium/headless shell `1228`/`1234`，没有浏览器下载。没有运行 SA-02 测试，未修改 `src/lib/markdown-poc/`、生产消费者、认证、路由、数据、Git 或部署。

## 2026-08-16 SA-02 验证

结论：`COMPLETE — failing-first baseline retained; no adapter enabled`。

| 切片                 | 精确命令                                                                                                                                                                                                                        | 结果与 artifact                                                                                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cleanup first red    | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test --config=src/lib/markdown-poc/browser-tests/playwright.config.ts --reporter=line --grep 'SA-02 browser harness exposes explicit cleanup'`                   | `1 failed`：期望 `function`，实际 `undefined`；`assets/playwright-test-results/sa-02-harness-cleanup-SA-0-6f2f4-cit-cleanup-after-hydration/{test-failed-1.png,error-context.md,trace.zip}`                   |
| cleanup green        | 同一命令，最小 harness `root.unmount()` 修正后                                                                                                                                                                                  | `1 passed (922ms)`；仅保留已产生的红灯 artifact                                                                                                                                                               |
| shared candidate red | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test --config=src/lib/markdown-poc/browser-tests/playwright.config.ts --reporter=line src/lib/markdown-poc/browser-tests/sa-02-special-adapter-baseline.spec.ts` | `3 failed`：Mermaid、Markmap、Chart 各自实际 SSR/hydration/repeat `false / 0 / 0`，合同期望 `true / 1 / 1`；每条有截图、error context、trace 于 `assets/playwright-test-results/sa-02-special-adapter-base-*` |

浏览器警告仅为 `NO_COLOR` 与 `FORCE_COLOR` 环境冲突；三条测试已在失败前完成 script sentinel、click/error/load、pageerror、console、dialog、request、navigation、download、恶意更新及卸载断言，均无安全观察。局部 fallback 的精确文本/warning 与四条路径 global fallback 仍由既有结构合同覆盖；SA-03 会在三条启用后作交叉闭环。新增范围仅在 `src/lib/markdown-poc/` 与本工作夹；没有生产消费者、依赖、认证、路由、数据、Git 或部署变更。

补充结构复核：`env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/m6-adapter-deferral.test.ts --reporter=verbose` → `1 file / 7 tests passed`，其中四条 deterministic global fallback 覆盖 Math、Mermaid、Markmap、Chart；这只证明 PoC-owned global inert error surface 仍存在，不将未启用适配器误记为通过。

## 2026-08-16 Mermaid-01 验证

| 证据         | 命令                                                                                                                                       | 结果                                                                                                 |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| 首个结构红灯 | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/mermaid-isolated.test.ts --reporter=verbose` | `1 file / 2 failed`：安全 SVG 缺失，恶意块为 `inert`；artifact：`assets/mermaid-01-first-failure.md` |
| 最终结构合同 | 同一命令                                                                                                                                   | `1 file / 3 tests passed`；无 Vitest warnings                                                        |

残余风险：真实 Mermaid library 的 browser final SVG 仍未经当前白名单实际样本验证；SSR placeholder 不应被误述为完成的图。Mermaid-02/03 仍须证明浏览器 render、输出净化、恶意更新、重复 render/unmount 及所有主动观察。

## 2026-08-16 Mermaid-02 验证 — COMPLETE

| 检查                   | 精确命令                                                                                                                                                                                          | 结果 / artifacts                                                                                                                                                                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 最终 SVG unit contract | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/mermaid-isolated.test.ts --reporter=verbose`                                                        | `1 file / 3 tests passed`；无 Vitest warnings。                                                                                                                                                                                                            |
| browser first failure  | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/mermaid-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` | 初次失败：safe flowchart 最终为 exact inert local fallback 而非 rendered SVG；`assets/mermaid-02-first-failure.md`，并保留 `assets/playwright-test-results/mermaid-isolated-Mermaid-0-0b120-ls-back-for-hostile-updates/` screenshot/error context/trace。 |
| browser final pass     | 同一 Playwright 命令                                                                                                                                                                              | `1 passed (1.2s)`；SSR、hydration、恶意更新、两次安全更新、最终 SVG、script sentinel、click/error/load、page/console error、dialog、request、navigation、download、unmount 均通过；最终截图 `assets/mermaid-02-final-pass.png`。                           |

原始 Mermaid 11.16.1 输出存在 `foreignObject`/HTML/CSS/filter 等未批准结构，故最终实现不使用该输出；改由 PoC-owned、受限静态 flowchart generator 构造有限 SVG。唯一 warning 为 `NO_COLOR`/`FORCE_COLOR` 环境冲突。没有生产 Markdown 消费者、认证、路由、数据、Git 或部署变更。Mermaid-03 与 G2 仍未执行，故当前状态不是 `ENABLED_ISOLATED`。

## 2026-08-16 Mermaid-03 关闭验证 — PASS / `ENABLED_ISOLATED`

| 检查                     | 精确命令                                                                                                                                                                                                                                                    | 结果 / warnings / artifacts                                                                                                                                                   |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 初始全 PoC 分类          | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/ --reporter=verbose`                                                                                                                                          | `9 files / 285 tests`，8 failed；全部是历史 Mermaid `DEFERRED_INERT` 预期，与实际已隔离 allow/local-fallback 冲突，不是安全输出失败。                                         |
| 全 PoC closing run       | 同一命令                                                                                                                                                                                                                                                    | `9 files / 284 tests passed`；12 个已知 jsdom `act(...)` environment messages，零失败。                                                                                       |
| 相关 real-browser matrix | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/inert-baseline.spec.ts src/lib/markdown-poc/browser-tests/mermaid-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` | `11 passed (2.1s)`；仅 `NO_COLOR`/`FORCE_COLOR` environment warnings，零 page/console error、dialog、download、非本地 request、post-hydration navigation 或 script sentinel。 |
| 生产隔离与空白           | `rg -n "markdown-poc" src --glob '!src/lib/markdown-poc/**'`; `rg -n ' +$'`（Mermaid touched files）                                                                                                                                                        | PoC 外零引用；无行尾空白。生产 Mermaid 链存在但未改，未作 fallback。                                                                                                          |

结论：Mermaid 是 `ENABLED_ISOLATED`，仅限 `src/lib/markdown-poc/` 的静态受限 flowchart grammar 与 PoC-owned finite SVG。首个相关失败与最终通过 artifacts 为 `assets/mermaid-02-first-failure.md`、相邻 Playwright failure bundle、`assets/mermaid-02-final-pass.png`。G2 仍为 `BLOCKED / NOT GO`，因为 Markmap/Chart 还没有独立 enablement；F3 未开始。

## 2026-08-16 Markmap-01 failing-first 验证 — COMPLETE

| 检查                    | 精确命令                                                                                                                                                                                          | 结果 / artifact                                                                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| isolated structural red | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/markmap-isolated.test.ts --reporter=verbose`                                                        | `1 file / 2 failed`：safe source 无 rendered SVG；hostile source 是 `inert` 而非 `local-fallback`。                                                                                            |
| isolated browser red    | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/markmap-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` | `1 failed`：SSR 未包含 `data-poc-markmap="rendered"`；`assets/markmap-01-first-failure.md` 与 `assets/playwright-test-results/markmap-isolated-Markmap-0-c17a3-wnload-or-lifecycle-residue/`。 |

Playwright 只有 `NO_COLOR`/`FORCE_COLOR` 环境 warning。当前安全状态仍是 exact inert fallback；没有 production Markmap consumer、链接、导航、下载、网络、认证、路由、数据、Git 或部署动作。Markmap-02 是唯一下一项，G2/F3 继续 BLOCKED / NOT GO。

## 2026-08-16 Markmap-02 验证 — COMPLETE

| 检查                     | 精确命令                                                                                                                                                                                          | 结果 / artifacts                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| focused SVG structure    | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/markmap-isolated.test.ts --reporter=verbose`                                                        | `1 file / 2 tests passed`；有限 static SVG 和恶意 link-like source 的 exact local fallback 均通过。 |
| focused browser boundary | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/markmap-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` | `1 passed (1.2s)`；最终截图 `assets/markmap-02-final-pass.png`。                                    |

实现只在 `src/lib/markdown-poc/`。输出没有 production Markmap library 的 DOM/SVG、链接、pan/zoom、下载、导航、CSS 或外部资源；超出受限标题树的输入为 exact local fallback。唯一 warning 是 `NO_COLOR`/`FORCE_COLOR`。Markmap-03 与 G2 未执行，故状态尚不是 `ENABLED_ISOLATED`。

## 2026-08-16 Markmap-03 关闭验证 — PASS / `ENABLED_ISOLATED`

| 检查                              | 精确命令                                                                                                                                                                                                                                                    | 结果 / warnings / artifacts                                                                                                                                                         |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| initial full PoC classification   | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/ --reporter=verbose`                                                                                                                                          | `10 files / 286 tests`，8 failed；全是历史 inert expectation，与实际 allow/local-fallback 冲突。                                                                                    |
| full PoC closing run              | 同一命令                                                                                                                                                                                                                                                    | `10 files / 285 tests passed`；12 个已知 jsdom `act(...)` environment messages，零失败。                                                                                            |
| related real-browser matrix       | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/inert-baseline.spec.ts src/lib/markdown-poc/browser-tests/markmap-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` | `11 passed (2.2s)`；仅 `NO_COLOR`/`FORCE_COLOR` environment warnings，零 page/console error、dialog、download、非 localhost request、post-hydration navigation 或 script sentinel。 |
| production isolation / whitespace | `rg -n "markdown-poc" src --glob '!src/lib/markdown-poc/**'`; `rg -n ' +$'`（Markmap touched files）                                                                                                                                                        | PoC 外零引用；无行尾空白。生产 Markmap 链存在但未改、未作 fallback。                                                                                                                |

结论：Markmap 是 `ENABLED_ISOLATED`，仅限 PoC-owned bounded heading-tree static SVG；links、pan/zoom、navigation 与 download 均不实现。first-failure/final-pass artifacts 为 `assets/markmap-01-first-failure.md`、相邻 failure bundle、`assets/markmap-02-final-pass.png`。Chart 尚未启用，故 G2/F3 仍 BLOCKED / NOT GO。

## 2026-08-16 Chart-01 failing-first 验证 — COMPLETE

- `npx vitest run src/lib/markdown-poc/__tests__/chart-isolated.test.ts --reporter=verbose` → `1 file / 2 failed`：无 safe Canvas、hostile formatter source 仍 inert。
- `npx playwright test src/lib/markdown-poc/browser-tests/chart-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` → `1 failed`：SSR 缺 `data-poc-chart="rendered"`；artifact 为 `assets/chart-01-first-failure.md` 与相邻 Playwright bundle。唯一 warning 是 `NO_COLOR`/`FORCE_COLOR`。

没有生产 Chart、ECharts、动态执行、网络、下载或 Git/部署动作。Chart-02 是唯一下一项，G2/F3 继续 BLOCKED / NOT GO。

## 2026-08-16 Chart-02 验证 — COMPLETE

- `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/chart-isolated.test.ts --reporter=verbose` → `1 file / 2 tests passed`。
- `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/chart-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` → `1 passed (1.0s)`；Canvas context/draw marker 通过，最终 artifact `assets/chart-02-final-pass.png`。唯一 warning 为 `NO_COLOR`/`FORCE_COLOR`。

实现只在 PoC；没有 ECharts/生产 Chart、动态执行、外部请求、下载、认证、路由、数据、Git 或部署。Chart-03 与 G2 未执行，尚不是 `ENABLED_ISOLATED`。

## 2026-08-16 Chart-03 关闭验证 — PASS / `ENABLED_ISOLATED`

- initial full PoC：`11 files / 287 tests`，8 historical inert expectation failures；closing run：`11 files / 286 tests passed`，12 个已知 jsdom `act(...)` messages。
- `npx playwright test src/lib/markdown-poc/browser-tests/inert-baseline.spec.ts src/lib/markdown-poc/browser-tests/chart-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` → `11 passed (2.1s)`，仅 `NO_COLOR`/`FORCE_COLOR` warnings，零 page/console error/dialog/download/non-local request/navigation/sentinel。
- first/final artifacts：`assets/chart-01-first-failure.md`、相邻 failure bundle、`assets/chart-02-final-pass.png`。Chart 现 `ENABLED_ISOLATED`，但 SA-03/SA-04/G2 还未完成。

## 2026-08-16 SA-03 cross-adapter closure — COMPLETE

- `npx vitest run src/lib/markdown-poc/__tests__/sa-03-cross-adapter.test.ts --reporter=verbose` → `1 file / 2 tests passed`。
- `npx playwright test src/lib/markdown-poc/browser-tests/sa-03-cross-adapter.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts` → `1 passed (1.4s)`；三输出共存，三恶意块 exact local fallback，零 XSS/error/dialog/download/non-local request/navigation/residue；仅环境 warning。

## 2026-08-16 SA-04 / G2 validation — PASS

- `npx vitest run src/lib/markdown-poc/__tests__/ --reporter=verbose` → `12 files / 288 tests passed`（12 existing jsdom `act(...)` messages）。
- passing-state Playwright matrix（baseline、cleanup、Mermaid、Markmap、Chart、SA-03）→ `15 passed (3.1s)`；only `NO_COLOR`/`FORCE_COLOR` warnings。
- `npx tsc --noEmit` PASS；`npx vitest run src/app/batch7-compatibility.test.ts --reporter=verbose` → `1 file / 4 tests passed`；Prettier, PoC-outside zero reference, local links, trailing whitespace PASS。
- G2 PASS / GO only for F3 evidence. No production migration, M7, route/auth/visual/data/Git/deploy action occurred.

记录完整性：首次 `npx prettier --check` 仅报告本文件的格式问题；运行 `npx prettier --write docs/workflows/markdown-special-adapter-enablement/validation.md` 后，父子六份 SA-01 记录的 `npx prettier --check`、本地 Markdown 链接检查和 `rg -n ' +$'` 均通过。无文档链接、行尾空白或格式 warning；没有 Git 操作。
