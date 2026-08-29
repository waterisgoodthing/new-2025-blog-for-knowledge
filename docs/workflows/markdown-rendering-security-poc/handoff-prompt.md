# Codex Goal Prompt：受控扩展完成 M6

> **Status: ARCHIVED — M6 CLOSED; DO NOT EXECUTE.** M6.1–M6.8 已完成，M6.9 已在 2026-08-16 完成文档同步。下方 `/goal` 仅保留为历史执行记录，不能再次授权 M6、依赖/lockfile 变更、浏览器安装、M7、Git 操作或部署。M7 仍需单独的路线迁移授权。

## 推荐执行版（中文，可直接复制）

```text
/goal 在本地仓库 `/Users/limengyang/2025-blog-public` 中，严格按 `docs/workflows/markdown-rendering-security-poc/tasks.md` 的 M6.1→M6.8 顺序，以受控扩展方式完成隔离 Markdown 安全 PoC 的 M6：先冻结真实浏览器 runner 与证据合同，再验证 Code 和现有 Math/Mermaid/Markmap/Chart inert fallback 的浏览器基线，然后按 Math→Mermaid→Markmap→Chart 逐个实现最小的 PoC 自有白名单/安全边界并做结构与真实浏览器验证，最后关闭局部/全局 fallback 和 M6 证据矩阵。执行本 Goal 即视为用户只批准 M6.1–M6.8 清单；不得跳项、并行跨越适配器或扩大范围。
验证：开始前完整阅读根 `AGENTS.md`、Markdown 子工作流与 `frontend-foundation-and-quality` 的 README/design/requirements/tasks/audit/validation、当前 `src/lib/markdown-poc/**` 源码/夹具/测试、生产 Markdown 链以及 `package.json`/lockfile，并先执行 `git status --short` 保护现有未跟踪和用户修改。所有正式 Node 命令显式使用 `env PATH="/opt/homebrew/opt/node@24/bin:$PATH"`。M6.1 先从官方一手资料重新核对 Playwright/Puppeteer/Vitest Browser 候选的当前版本、license、advisory、peer/Node 24 兼容性、lockfile、浏览器二进制/缓存和 artifact 影响，只记录决策，不安装。M6.2 起每项都必须先增加能对当前缺口产生红灯的最小结构/真实浏览器测试，主动捕获并断言 script sentinel、`pageerror`、console error、dialog、request、navigation、download、`click/error/load` 事件、SSR→hydration→safe-to-malicious update、DOM/SVG 结构、Canvas/container 创建、safe neighbours、TOC、warnings/outcome 和重复渲染残留；截图只能作为辅助证据。每个子项运行直接相关的结构与浏览器测试；M6.8 最终运行 `npx vitest run src/lib/markdown-poc/__tests__/`、M6.1 选定并记录的精确浏览器测试命令、`npx tsc --noEmit`、`npx prettier --check src/lib/markdown-poc/ docs/workflows/markdown-rendering-security-poc/ docs/workflows/frontend-foundation-and-quality/`、`npx vitest run src/app/batch7-compatibility.test.ts`，并检查生产隔离、workflow 相对链接、尾随空格、重复运行稳定性与 artifacts。记录实际 runner/浏览器/Node/npm 版本、测试文件与通过/失败计数、所有警告和浏览器观测、artifact 路径、每个适配器决策与第一条相关失败。
约束：严格测试先行且一次只改变一个适配器边界。M6.2 只建立 browser harness/inert 基线并关闭 Code 的精确元素/属性 schema 证据债，不启用特殊适配器。Math 必须有 PoC 自有的 KaTeX element/class/attribute/style-value 白名单；Mermaid 必须有最终 SVG element/attribute/namespace/URL/style 白名单并禁止 `foreignObject`/事件/危险链接；Markmap 不得自动继承 Mermaid 的启用结论，需独立验证链接、DOM 变换、pan/zoom、导航和下载；Chart 只接受解析后 JSON 与显式 option 白名单，禁止函数/formatter、任意代码、动态 import、不安全 HTML label/tooltip、非预期网络和未授权下载。每个适配器最终只能记录 `ENABLED_ISOLATED` 或 `DEFERRED_INERT`；延后时必须保留 M5 的精确 decoded-text fallback 和结构化 warning，且不阻断后续适配器。局部失败必须保留安全相邻块/TOC/warnings/outcome；全局失败只能返回 PoC 自有 inert/安全错误面，禁止 import 或调用 `src/lib/markdown-renderer.ts`、`src/hooks/use-markdown-render.tsx` 或生产 special-renderer 链作为 fallback。不得用 jsdom、字符串正则、空输出或截图冒充真实浏览器安全证据，不得弱化、删除或改名测试制造绿灯。
边界：允许写入仅限 `src/lib/markdown-poc/**`、`docs/workflows/markdown-rendering-security-poc/{README.md,design.md,requirements.md,tasks.md,audit.md,validation.md,handoff-prompt.md,assets/**}` 和状态同步直接需要的 `docs/workflows/frontend-foundation-and-quality/{README.md,tasks.md,audit.md,validation.md}`。M6.1 可读取项目依赖/官方文档，但不得写入 `package.json`、`package-lock.json`、其他 lockfile、环境文件或浏览器缓存。不得修改 `src/lib/markdown-renderer.ts`、`src/hooks/use-markdown-render.tsx`、现有生产 Math/Mermaid/Markmap/Chart 组件、任何生产消费者、路由、导航、auth、API、DTO、数据库、持久化、公开内容或部署配置；不得使用真实私有内容/凭据，不得暂存、提交、推送、部署、迁移数据、删除未跟踪文件或覆盖无关用户修改。
迭代策略：一次只执行一个 M6.x，开始前确认前一项已关闭。每项先增加或收紧红灯测试，再做最小修正，读取失败输出后才调整；每次有意义变更后重跑直接测试。完成一项后必须立即勾选 `tasks.md` 该项并把命令、首个失败、修正、计数、浏览器观测、适配器决策和残余风险写入 `validation.md`，然后才能进入下一项。相同失败不得原样重试；连续两次后必须换证据来源，例如实际 DOM/SVG、浏览器 trace、网络/导航/下载事件、上游类型/源码或最小复现。M6.2 共享基线最多 3 轮仍无法满足时暂停；M6.3–M6.6 每个适配器最多 3 轮，仍不满足时记录 `DEFERRED_INERT` 并继续下一个。除触发暂停条件外，不因普通红灯、可诊断 warning 或某个适配器延后而请求用户介入。
完成条件：M6.1–M6.8 已按顺序逐项更新；M6.2 真实浏览器 inert 基线和 Code 精确 schema 通过；Math/Mermaid/Markmap/Chart 每个都有独立、证据支持的 `ENABLED_ISOLATED` 或 `DEFERRED_INERT` 结论；所有已启用路径具有 SSR、hydration、update、DOM/SVG/Canvas 和事件/导航/下载/请求的真实浏览器证据；局部/全局 fallback 通过且没有旧渲染链调用；无未解释红灯；M6.8 必要检查全部通过或只剩明确证明的非目标 warning；`validation.md` 含完整证据矩阵、实际命令和 artifacts。M6 可在部分适配器 `DEFERRED_INERT` 时以“受控评估完成”关闭，但必须对这些路径保持 G2 NO-GO/PARTIAL；不得因 M6 完成而开始 M7 或生产迁移。
暂停条件：M6.1 判定需要安装/升级/删除依赖、修改任何 lockfile 或下载持久浏览器二进制时，必须先记录候选与影响并暂停，单独请求明确批准。任何项需要修改生产 Markdown 链/消费者、放宽信任或 sanitizer 合同、使用旧渲染器 fallback、修改路由/auth/API/DTO/数据库/持久化/公开内容/部署、使用真实数据或凭据、执行 Git/部署/破坏性清理，或与用户现有修改发生实质冲突时，立即保留安全状态、更新 `tasks.md`/`validation.md` 为真实 PARTIAL/BLOCKED 并请求最小必要决定。M6.2 共享基线在 3 轮有新证据的修正后仍失败时同样暂停；不得自行扩权、绕过依赖审批、弱化安全合同或把失败包装为完成。
```

默认选择理由：先用真实浏览器关闭现有 inert 基线，再按风险从低到高逐个扩展适配器，可以在不放大生产与依赖权限的前提下获得可审查、可停止的 G2 证据。

## Goal Draft (English-compatible)

```text
/goal In the local repository `/Users/limengyang/2025-blog-public`, complete the isolated Markdown-security PoC M6 in the exact M6.1→M6.8 order defined by `docs/workflows/markdown-rendering-security-poc/tasks.md` using controlled expansion: freeze the real-browser runner and evidence contract; prove the Code and current Math/Mermaid/Markmap/Chart inert baseline in a real browser; then evaluate Math, Mermaid, Markmap, and Chart one at a time with the smallest PoC-owned allow-list/security boundary and both structural and real-browser evidence; finally close local/global fallback and the M6 evidence matrix. Invoking this Goal is explicit approval for M6.1–M6.8 only; do not skip items, work across adapters in parallel, or expand scope.
Verification: first read the root `AGENTS.md`, both relevant workflow document sets, current `src/lib/markdown-poc/**` source/fixtures/tests, production Markdown boundaries, and dependency/lockfile state, then run `git status --short` and preserve all user and untracked changes. Run formal Node commands with `env PATH="/opt/homebrew/opt/node@24/bin:$PATH"`. M6.1 must re-query official primary sources for current Playwright/Puppeteer/Vitest Browser versions, licenses, advisories, peers/Node 24 compatibility, lockfile, persistent browser-binary/cache, and artifact impact without installing anything. Starting at M6.2, every item must begin with the smallest failing structural/real-browser test and actively assert script sentinels, page/console errors, dialogs, requests, navigation, downloads, relevant `click/error/load` dispatch, SSR→hydration→safe-to-malicious updates, DOM/SVG structure, Canvas/container creation, safe neighbours, TOC, warnings/outcomes, and repeat-render residue; screenshots are supporting evidence only. At M6.8 run `npx vitest run src/lib/markdown-poc/__tests__/`, the exact browser command selected and recorded by M6.1, `npx tsc --noEmit`, `npx prettier --check src/lib/markdown-poc/ docs/workflows/markdown-rendering-security-poc/ docs/workflows/frontend-foundation-and-quality/`, `npx vitest run src/app/batch7-compatibility.test.ts`, and production-isolation, workflow-link, trailing-whitespace, deterministic-repeat, and artifact checks. Record actual runner/browser/Node/npm versions, file/test/pass/fail counts, all warnings and browser observations, artifact paths, each adapter decision, and the first relevant failure.
Constraints: enforce test-first work and change only one adapter boundary at a time. M6.2 establishes the browser harness/inert baseline and exact Code element/attribute schema only. Math requires a PoC-owned KaTeX element/class/attribute/style-value allow-list. Mermaid requires a final-SVG element/attribute/namespace/URL/style allow-list that excludes `foreignObject`, events, and dangerous links. Markmap must not inherit Mermaid approval and needs independent link, transformed-DOM, pan/zoom, navigation, and download evidence. Chart may accept only parsed JSON plus an explicit option allow-list and must reject functions/formatters, arbitrary code, dynamic imports, unsafe HTML labels/tooltips, unexpected networking, and unapproved downloads. Each adapter finishes only as `ENABLED_ISOLATED` or `DEFERRED_INERT`; a deferral preserves the M5 exact decoded-text fallback and structured warning and does not block the next adapter. Local failure preserves safe neighbours/TOC/warnings/outcome; global failure uses only a PoC-owned inert/safe error surface and never imports or calls the production/legacy Markdown or special-renderer chain. Never substitute jsdom, string regexes, empty output, or screenshots for real-browser execution evidence, and never weaken, delete, or rename tests to manufacture green results.
Boundaries: writes are limited to `src/lib/markdown-poc/**`, `docs/workflows/markdown-rendering-security-poc/{README.md,design.md,requirements.md,tasks.md,audit.md,validation.md,handoff-prompt.md,assets/**}`, and directly required status synchronization in `docs/workflows/frontend-foundation-and-quality/{README.md,tasks.md,audit.md,validation.md}`. M6.1 may read dependency and official documentation evidence but may not modify `package.json`, `package-lock.json`, any lockfile, environment file, or persistent browser cache. Do not modify `src/lib/markdown-renderer.ts`, `src/hooks/use-markdown-render.tsx`, existing production Math/Mermaid/Markmap/Chart components, production consumers, routes, navigation, auth, APIs, DTOs, database, persistence, public content, or deployment configuration. Do not use private content/credentials, stage, commit, push, deploy, migrate data, delete untracked files, or overwrite unrelated user changes.
Iteration policy: execute exactly one M6.x item at a time and confirm the previous item is closed. Add or tighten a failing test first, make the minimum correction, inspect evidence, and rerun direct checks after each meaningful change. Immediately after each item, mark its checkbox and record commands, first failure, correction, counts, browser observations, decision, and residual risks in `validation.md` before continuing. Never repeat the same failed attempt unchanged; after two consecutive failures change the evidence source to actual DOM/SVG, browser trace, network/navigation/download events, upstream types/source, or a minimal reproduction. Pause if the shared M6.2 baseline still fails after three evidence-changing rounds. Give each M6.3–M6.6 adapter at most three evidence-changing rounds, then record `DEFERRED_INERT` and continue. Do not request intervention for ordinary red tests, diagnosable warnings, or one adapter deferral unless a pause condition is triggered.
Stop when: M6.1–M6.8 have been updated sequentially; the real-browser inert baseline and exact Code schema pass; Math, Mermaid, Markmap, and Chart each have an independent evidence-backed `ENABLED_ISOLATED` or `DEFERRED_INERT` decision; every enabled path has SSR, hydration, update, DOM/SVG/Canvas, event, navigation, download, request, and real-browser evidence; local/global fallback passes with no legacy-renderer call; no unexplained red test remains; M6.8 checks pass or only proven non-target warnings remain; and `validation.md` contains the complete matrix, commands, counts, artifacts, decisions, and risks. M6 may close as controlled evaluation with some adapters deferred, but those paths must remain G2 NO-GO/PARTIAL. Do not start M7 or a production migration.
Pause if: M6.1 determines that any package install/upgrade/removal, lockfile change, or persistent browser-binary download is required; record the decision and impact, then request separate explicit approval before mutation. Also pause for any production Markdown/consumer change, weaker trust or sanitizer policy, legacy-renderer fallback, route/auth/API/DTO/database/persistence/public-content/deployment change, private data or credentials, Git/deployment/destructive action, material conflict with user changes, or a shared M6.2 baseline that still fails after three evidence-changing rounds. Preserve the safe state, update `tasks.md`/`validation.md` truthfully as PARTIAL/BLOCKED, and request the smallest necessary human decision; never self-authorize broader scope or disguise failure as completion.
```

---

# Archived Codex Goal Prompt：自助迭代完成 M5

> **Status: ARCHIVED — COMPLETED 2026-08-15. DO NOT EXECUTE.** M5.1–M5.7 已完成并通过文档收尾复核；下方 `/goal` 仅保留为历史执行记录，不再构成当前交接入口。本文后部的 M3 Prompt 同样已归档，不得执行。

## 推荐执行版（中文，可直接复制）

```text
/goal 在本地仓库 `/Users/limengyang/2025-blog-public` 中，严格按 `docs/workflows/markdown-rendering-security-poc/tasks.md` 的 M5.1→M5.7 顺序，自助迭代完成隔离 Markdown PoC 的 M5：先建立精确 decoded-text 与 direct parsed-DOM 共享验收基线，再分别关闭 Code、Math、Mermaid、Markmap、Chart 的最终输出合同，最后形成逐路径关闭矩阵。执行本 Goal 即视为用户只批准修订后的 M5.1–M5.7；无需在子项之间重复申请批准，但不得越过任务顺序或扩大范围。
验证：开始前完整阅读根 `AGENTS.md`、两个相关 workflow 的 README/design/requirements/tasks/audit/validation、当前 PoC 源码/夹具/测试及生产 Markdown 边界，并执行 `git status --short` 保护现有未跟踪和用户修改。所有正式命令显式使用 `/opt/homebrew/opt/node@24/bin` 下的 Node 24/npm 11。每个 M5.x 先添加能对当前缺口产生红灯的最小测试，再做最小实现并运行直接相关测试；M5.7 最终运行 `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/`、`env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx tsc --noEmit`、`env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx prettier --check src/lib/markdown-poc/ docs/workflows/markdown-rendering-security-poc/ docs/workflows/frontend-foundation-and-quality/`、`env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/app/batch7-compatibility.test.ts`，并检查生产隔离、workflow 相对链接和尾随空格。记录实际测试文件数、通过/失败数、非目标 warning、Node/npm 版本、每个适配器的决定及第一条相关失败；不得用构建忽略配置、字符串正则或空输出冒充安全通过。
约束：严格执行测试先行。M5.1 只建立共享 parsed-DOM/精确文本合同，不启用适配器；M5.2 必须移除普通 fenced/inline code 的零宽字符改写并证明 hostile-looking source 仍只是文本；M5.3 对 Math 记录 `ENABLED` 或 `DEFERRED_INERT`；M5.4–M5.6 对 Mermaid、Markmap、Chart 分别记录 `ENABLED_PENDING_M6_BROWSER` 或 `DEFERRED_INERT`。启用结论必须来自最终输出的元素、属性、URL、`textContent`、warnings/outcome、SSR 与 hydration 证据；不满足合同就保留精确文本的 inert fallback，禁止弱化、删除或改名测试来制造绿灯。真实浏览器 SVG/Canvas、事件、导航、下载和脚本执行只归 M6/G2；M5 不安装或运行 Playwright/Puppeteer，不宣告 G2 GO。
边界：只允许修改 `src/lib/markdown-poc/**`、`docs/workflows/markdown-rendering-security-poc/{README.md,design.md,requirements.md,tasks.md,audit.md,validation.md,handoff-prompt.md}` 和为状态同步直接需要的 `docs/workflows/frontend-foundation-and-quality/{README.md,tasks.md,audit.md,validation.md}`。不得修改 `src/lib/markdown-renderer.ts`、`src/hooks/use-markdown-render.tsx`、现有生产 special-renderer 组件、任何生产消费者、路由、导航、auth、API、DTO、数据库、持久化、公开内容、环境文件、`package.json` 或 lockfile；不得暂存、提交、推送、部署、迁移数据、清理未跟踪文件或覆盖无关用户修改。
迭代策略：一次只执行一个 M5.x。开始子项前确认前一项已关闭；先写或收紧失败测试，再实现最小改动，读取失败输出后才调整。每完成一个子项，必须立即在同一轮勾选 `tasks.md` 的该项并把命令、结果、决定和残余风险写入 `validation.md`，然后才能进入下一项；不得最后批量补文档。相同失败不得原样重试；连续两次失败后必须更换证据来源，例如检查解析后的 DOM、上游库真实最终输出、类型声明或最小复现。每个子项最多进行 3 轮有新证据的聚焦修正：M5.3–M5.6 仍不满足时记录 `DEFERRED_INERT` 并继续下一个适配器；M5.1 或 M5.2 仍不满足时按暂停条件停止。除触发暂停条件外，持续自助推进直至 M5.7 完成，不因普通红灯、可诊断警告或某个适配器被延后而向用户请求介入。
完成条件：M5.1–M5.7 均已逐项标记完成；Code 精确 decoded-text 和 direct parsed-DOM 合同通过；Math/Mermaid/Markmap/Chart 各有独立、证据支持的启用或 inert 决定；没有 unexplained red test；M5.7 的全部检查通过，或仅有已明确证明为既存且非目标的 warning；`validation.md` 含最终关闭矩阵、实际命令和结果；README/audit/父 workflow 状态一致；M6 被设为唯一下一入口，但未开始 M6、未宣告 G2 GO、未授权生产路由迁移。完成后报告 COMPLETE/PARTIAL/BLOCKED、各 M5.x 结果、每个适配器决定、验证计数、修改文件、未触及边界和剩余 M6/G2 风险。
暂停条件：任何子项需要新增/升级/删除依赖或改 lockfile、修改生产 Markdown 链或消费者、进入 M6/真实浏览器、改变路由/auth/API/DTO/数据库/持久化、使用真实数据或凭据、暂存/提交/推送/部署、执行破坏性清理、处理与用户现有修改发生实质冲突，或 M5.1/M5.2 在 3 轮有新证据的聚焦修正后仍不能满足合同。暂停时保留安全状态，立即更新 `tasks.md` 与 `validation.md` 为真实 PARTIAL/BLOCKED，给出阻塞证据、已尝试路径和所需的最小用户决定；不得自行扩权、弱化安全合同或把失败包装为完成。
```

默认选择理由：该目标把可安全延后的特殊适配器与不可绕过的共享安全基线分开，既允许 Codex 连续自助迭代，也不会为了“完成 M5”而越过生产、依赖或真实浏览器边界。

## Goal Draft (English-compatible)

```text
/goal In the local repository `/Users/limengyang/2025-blog-public`, autonomously iterate through and complete the isolated Markdown PoC M5 in the exact M5.1→M5.7 order defined by `docs/workflows/markdown-rendering-security-poc/tasks.md`: establish the exact decoded-text and direct parsed-DOM acceptance baseline, close the Code, Math, Mermaid, Markmap, and Chart final-output contracts independently, and finish with a per-path closure matrix. Invoking this Goal is explicit approval for the revised M5.1–M5.7 only; do not request repeated approval between items, skip their order, or expand scope.
Verification: before changes, read the root `AGENTS.md`, both relevant workflow document sets, the current PoC source/fixtures/tests, and the production Markdown boundaries, then run `git status --short` and preserve all user and untracked changes. Use Node 24/npm 11 explicitly from `/opt/homebrew/opt/node@24/bin`. For every M5.x item, add the smallest failing-first test for the current gap, implement the minimum correction, and run the directly relevant checks. At M5.7 run the focused PoC suite, `npx tsc --noEmit`, Prettier over the PoC and both workflows, Batch 7 compatibility tests, production-isolation checks, relative-link checks, and trailing-whitespace checks. Record actual file/test/pass/fail counts, non-target warnings, Node/npm versions, every adapter decision, and the first relevant failure. Never treat ignored build errors, string-only regexes, or empty output as security evidence.
Constraints: enforce test-first work. M5.1 adds only the shared parsed-DOM/exact-text contract; M5.2 removes zero-width rewriting from fenced and inline code and proves hostile-looking source remains text; M5.3 records Math as `ENABLED` or `DEFERRED_INERT`; M5.4–M5.6 record Mermaid, Markmap, and Chart individually as `ENABLED_PENDING_M6_BROWSER` or `DEFERRED_INERT`. Enablement requires final-output element, attribute, URL, `textContent`, warning/outcome, SSR, and hydration evidence. If a renderer cannot meet the contract, preserve an exact-text inert fallback; never weaken, delete, or rename tests to manufacture green results. Real-browser SVG/Canvas, events, navigation, downloads, and script execution belong only to M6/G2. Do not install or run Playwright/Puppeteer or declare G2 GO in M5.
Boundaries: writes are limited to `src/lib/markdown-poc/**`, the directly related Markdown PoC workflow files, and the parent frontend-foundation workflow status/evidence files. Do not modify the production renderer, hook, existing production special-renderer components, consumers, routes, navigation, auth, APIs, DTOs, database, persistence, public content, environment files, dependencies, or lockfiles. Do not stage, commit, push, deploy, migrate data, remove untracked files, or overwrite unrelated user changes.
Iteration policy: execute exactly one M5.x item at a time. Confirm the previous item is closed, create or tighten a failing test, make the smallest implementation change, and inspect failure output before adjusting. Immediately after each item, mark that exact checkbox in `tasks.md` and record commands, results, decisions, and residual risks in `validation.md` before starting the next item; do not batch documentation at the end. Never repeat the same failed attempt unchanged; after two consecutive failures, change the evidence source by inspecting parsed DOM, real upstream final output, type declarations, or a minimal reproduction. Allow at most three evidence-backed focused correction rounds per item. If M5.3–M5.6 still fail, record `DEFERRED_INERT` and continue; if M5.1 or M5.2 still fail, pause. Unless a pause condition is met, continue autonomously through M5.7 without asking for help because of ordinary red tests, diagnosable warnings, or an adapter deferral.
Stop when: M5.1–M5.7 are individually complete; exact Code text and direct parsed-DOM contracts pass; Math, Mermaid, Markmap, and Chart each have an evidence-backed enabled or inert decision; no unexplained red test remains; all M5.7 checks pass or only proven pre-existing non-target warnings remain; `validation.md` contains the final matrix and actual command evidence; child and parent workflow states agree; and M6 is the only next entry without starting M6, declaring G2 GO, or authorizing production route migration. Report COMPLETE/PARTIAL/BLOCKED, every M5.x result, adapter decisions, validation counts, changed files, untouched boundaries, and remaining M6/G2 risks.
Pause if: any item requires a dependency or lockfile change, production Markdown/consumer modification, M6 or a real browser, route/auth/API/DTO/database/persistence changes, real data or credentials, Git staging/commit/push, deployment, destructive cleanup, a material conflict with existing user changes, or M5.1/M5.2 still cannot meet the contract after three evidence-backed focused correction rounds. Preserve the safe state, immediately record truthful PARTIAL/BLOCKED status in `tasks.md` and `validation.md`, and report the blocking evidence, attempts, and smallest required user decision. Never self-authorize broader scope, weaken the security contract, or present failure as completion.
```

---

## Archived: GLM 交接 Prompt — M3 最小纠偏

> **Status: ARCHIVED — COMPLETED 2026-08-10. DO NOT EXECUTE.** 本 Prompt 所要求的 M3 最小纠偏已经完成；当前状态已推进为 `M4 COMPLETE / M5 NEXT`。以下内容仅保留为历史交接记录，不再代表当前入口。

复制下面整段内容交给 GLM。本 Prompt 携带用户对 `frontend-foundation-and-quality` F0–F4 既定任务的统一执行批准，但不扩展范围。

````text
你现在接手本地仓库 `/Users/limengyang/2025-blog-public` 的 `frontend-foundation-and-quality` 总任务组。当前工作线为 F2A / `markdown-rendering-security-poc`。

## 一、授权与目标

用户已批准 F0–F4 既定任务，并明确要求纠正当前验收时点过度提前的问题。你无需再次请求 M3 最小纠偏批准。

本轮唯一目标：保留已有 Node 24、M2 和测试先行成果，以最小改动把 M3 修正为真实 SSR、真实 React hydration 和准确命名的 jsdom DOM 安全合同；把真实浏览器执行推迟到 M5/M6，并保留为 G2 前的强制证据。

本轮不安装 Playwright/Puppeteer，不实现 M4，不迁移生产消费者，不部署、不提交、不推送、不暂存、不使用真实数据或凭据。

## 二、当前已验证事实

- F0/G0 PASS；F1/G1 PASS。
- M1 COMPLETE。
- M2 COMPLETE：Homebrew keg-only Node `v24.18.0`、npm `11.16.0`；23 个 fixture id 唯一；TypeScript、Prettier、隔离和文档检查已通过。
- M3 当前有4个测试文件、252项测试，Node 24 下可复现为54红/198绿；既有 `batch7-compatibility` 4项通过。
- 54个红灯确实来自 `NOT_IMPLEMENTED` stub，不是模块、TypeScript或配置错误。
- 但 M3 不能保持 COMPLETE：
  1. `ssr.test.ts` 导入 `renderToString` 却未调用；
  2. `hydration.test.ts` 没有 React组件、服务端HTML或 `hydrateRoot`；
  3. `browser.test.ts` 运行于 jsdom，jsdom不执行脚本、不渲染SVG，47项在空输出下全部通过；
  4. 总 `tasks.md` 的 FFQ-05 实际仍为未勾选状态且状态过期；
  5. 浏览器候选评审把 Playwright `1.49.0` 写成 latest，已过期；当前是否安装依赖留到 M5/M6 再重新核验。

所以当前正确结论是：`M2 PASS; M3 PARTIAL; FFQ-05 PARTIAL; M4 NOT READY`。

## 三、开始前必须完成

1. 完整阅读根 `AGENTS.md`。
2. 执行 `git status --short`；保护当前未跟踪工作流和 `src/lib/markdown-poc/`，不清理、不回滚、不覆盖。
3. 阅读并交叉核对：
   - `docs/workflows/frontend-foundation-and-quality/{README,design,requirements,tasks,audit,validation}.md`
   - `docs/workflows/markdown-rendering-security-poc/{README,design,requirements,tasks,audit,validation}.md`
   - `src/lib/markdown-poc/fixtures.ts`
   - `src/lib/markdown-poc/types.ts`
   - `src/lib/markdown-poc/render-poc.ts`
   - `src/lib/markdown-poc/__tests__/*`
4. 所有命令显式使用 Node 24：

```bash
NODE24_BIN="$(brew --prefix node@24)/bin"
env PATH="$NODE24_BIN:$PATH" node --version
env PATH="$NODE24_BIN:$PATH" npm --version
```

## 四、先修订设计和任务状态

按照仓库“计划改变先更新 design/requirements/tasks”的规则，在测试代码修改前完成：

1. Markdown `design.md` 明确三层验证：
   - M3：结构/URL合同、真实SSR、真实React hydration、jsdom DOM安全合同；
   - M5/M6：真实浏览器中的SVG、Canvas、事件与危险导航执行；
   - G2：没有真实浏览器证据不得给 GO。
2. Markdown `requirements.md` 保留“browser execution”总要求，但注明其执行阶段为 M5/M6、验收阶段为 G2，不删除该要求。
3. Markdown `tasks.md`：
   - M1、M2保持已勾选；
   - M3改为未勾选的 `PARTIAL — SSR/hydration correction in progress`；
   - M4继续等待；
   - M5/M6增加真实浏览器最终输出责任，但不开始执行。
4. 总 `tasks.md`：FFQ-05保持未勾选的 `PARTIAL`，说明只差M3最小纠偏；FFQ-06继续等待。
5. README/audit/validation同步当前状态，不得继续宣称“M1–M3 COMPLETE”或“M4 NEXT”。

这不是扩大范围，也不需要新建任务组。

## 五、最小修正 SSR 测试

只修改测试，不实现 parser/sanitizer：

- 保留 `renderMarkdownPoC` stub；
- 建立测试专用 React surface，把 `renderMarkdownPoC` 结果放入可序列化组件；
- 必须实际调用 `renderToString`，并对最终序列化 HTML 断言；
- 至少覆盖：
  1. 安全语义必须存在，因此 stub 产生红灯；
  2. 危险 script/event/URL 不得出现在最终 SSR HTML；
  3. TOC/outcome/warnings 合同仍由结构测试覆盖；
  4. Math/Mermaid/Markmap/Chart 在 M5 前只允许 inert fallback。

若 JSX 更清晰，可以把测试改为 `.test.tsx`；不要为此修改生产代码。

## 六、最小修正 hydration 测试

必须测试真实 React hydration，而不是两次普通函数调用：

1. 创建测试专用 React 组件，接收 `markdown` 和 `mode`；
2. 用 `renderToString` 生成服务端 HTML；
3. 把 HTML 放入 jsdom 容器；
4. 使用 `hydrateRoot` 完成 hydration；
5. 更新为安全→恶意 Markdown；
6. 使用 React `act` 或项目现有 Testing Library 稳定等待方式；
7. 断言：
   - 没有非预期 hydration mismatch；
   - 安全哨兵内容仍存在；
   - 危险节点、属性和协议没有出现或残留；
   - 局部失败不清空整篇安全内容；
   - stub 因没有安全内容/合同输出而产生有意义红灯。

不要只检查字符串函数的两次返回值。

## 七、重新定义现有 browser.test.ts

本轮不安装真实浏览器依赖。

- 将现有 `browser.test.ts` 重命名为准确的 `dom-safety.test.ts` 或等价名称；
- 文档和测试标题统一称为“jsdom DOM安全合同”，不得称为真实browser execution；
- 保留危险tag、attribute、protocol和转义文本检查；
- 增加至少一个安全哨兵/非空输出断言，使 `NOT_IMPLEMENTED` 空输出不能让整组测试真空通过；
- 删除或修正“jsdom attack flag 能证明脚本没有执行”的表述；只能证明DOM/HTML结构，不能证明真实浏览器执行。

`browser-candidate-review.md` 应改为 deferred 记录：删除“latest stable”和无来源的安全/体积断言，说明M5/M6开始前必须重新查询官方npm元数据并决定最小runner。

## 八、验证与完成标准

在 Node 24 下执行：

```bash
NODE24_BIN="$(brew --prefix node@24)/bin"

env PATH="$NODE24_BIN:$PATH" npx tsc --noEmit
env PATH="$NODE24_BIN:$PATH" npx prettier --check src/lib/markdown-poc/
env PATH="$NODE24_BIN:$PATH" npx vitest run src/lib/markdown-poc/__tests__/
env PATH="$NODE24_BIN:$PATH" npx vitest run src/app/batch7-compatibility.test.ts
```

不要追求维持252/54/198原计数，测试语义优先。M3完成必须同时满足：

- SSR测试实际调用 `renderToString`；
- hydration测试实际调用 `hydrateRoot` 并执行更新；
- jsdom测试命名准确且空stub不能整组真空通过；
- 测试可编译、可运行；
- 红灯只来自M4–M6合同未实现；
- TypeScript、Prettier和既有兼容测试通过；
- 无生产消费者导入 `markdown-poc`；
- 未修改依赖或lockfile。

满足后立即：

1. 将Markdown M3恢复为已勾选；
2. 将总FFQ-05改为已勾选；
3. README/audit/validation同步真实测试数量、红绿数量、实际API证据和剩余真实浏览器Gate；
4. 把M4设置为唯一下一入口；
5. 明确真实浏览器仍是M5/M6任务和G2硬门，不得因为M3完成而删除。

## 九、停止点

完成M3最小纠偏后停止并向用户报告，不要在同一轮开始M4。

报告必须包含：

1. PASS / PARTIAL / BLOCKED；
2. 修订后的阶段分层；
3. SSR中 `renderToString` 的实际调用证据；
4. hydration中 `hydrateRoot` 和更新流程证据；
5. jsdom DOM合同的新文件名和非真空断言；
6. 实际测试文件、数量、红绿结果；
7. TypeScript、Prettier、兼容测试和生产隔离结果；
8. 修改文件；
9. 未触及边界；
10. M4是否成为唯一下一入口，以及真实浏览器仍归属M5/M6和G2。
````
