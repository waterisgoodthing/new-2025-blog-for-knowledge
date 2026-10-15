# 任务清单

Status: `SA-01～04 HISTORICAL COMPLETE; G2 ISOLATED PASS RETAINED; FIX-03～05 COMPLETE; F4 INPUT READY FOR SEPARATE APPROVAL; NO PRODUCTION MIGRATION OR F4`

## 审批边界

本清单只授权后才能开始实施。即使本清单获批，新增/升级/删除依赖、lockfile 修改、持久浏览器二进制下载、生产消费者、M7、Git 和部署仍需单独授权。

## A. 冻结与共享基线

- [x] SA-01. **COMPLETE (2026-08-16):** 已核对当前适配器源文件、依赖、版本/license/advisory/peer/runtime、lockfile、浏览器缓存和 PoC 缺口。用户明确批准后，`mermaid` 从 `11.15.0` 升级并锁定到 `11.16.1`；目标 Mermaid 公告已清除，现有 Playwright 浏览器缓存保持不变。升级同时更新 Mermaid parser、Cytoscape、DOMPurify 等锁定传递依赖；没有升级/新增其他直接产品依赖或下载浏览器。证据见 `audit.md` 与 `validation.md`。
- [x] SA-02. **COMPLETE (2026-08-16):** 测试先行建立共享失败基线。先以缺失 `unmount()` 的运行时红灯证明浏览器 harness 无法验证清理，再用最小测试支持使其通过；随后 Mermaid、Markmap、Chart 各自得到同一条可复现的浏览器红灯：SSR、hydration、恶意更新、重复渲染及卸载均完成，主动观测无安全事件，但三者的隔离输出计数为 `false / 0 / 0`。失败截图、trace、error context 位于 `assets/playwright-test-results/`；Mermaid-01 是唯一下一项。

## B. Mermaid

- [x] Mermaid-01. **COMPLETE (2026-08-16):** 已写入并保留最终 SVG 合同的首个失败测试：安全 flowchart 当时无 SVG，恶意输入仍是 inert 而非局部回退。最终 3/3 聚焦结构测试覆盖元素、属性、命名空间、URL/id/fragment 重写、无 style/`foreignObject`/事件/外部资源和精确局部失败。首个红灯见 `assets/mermaid-01-first-failure.md`；Mermaid-02 是唯一下一项。
- [x] Mermaid-02. **COMPLETE (2026-08-16):** 最小隔离 renderer 已落在 `src/lib/markdown-poc/mermaid.ts`：只接受受限静态 flowchart 语法，并由 PoC 直接构造有限 SVG（保留节点标签和连线），不插入 Mermaid 库的 `foreignObject`/HTML/CSS 输出，也不调用生产渲染链。真实浏览器周期通过；首个失败和最终通过 artifacts 分别为 `assets/mermaid-02-first-failure.md`、`assets/mermaid-02-final-pass.png`。Mermaid-03 是唯一下一项。
- [x] Mermaid-03. **COMPLETE / `ENABLED_ISOLATED` (2026-08-16):** 全 PoC `284/284`、Mermaid 专用加既有浏览器基线 `11/11` 均通过；覆盖有限 SVG 结构、SSR、hydration、恶意更新的精确 local fallback、重复 render、主动观察和卸载。`src` 在 PoC 目录外对 `markdown-poc` 的引用为零；现存生产 Mermaid 链未修改、未用作 fallback。first-failure/final-pass artifacts 已保留。Markmap-01 是唯一下一项；G2 继续 BLOCKED / NOT GO。

## C. Markmap

- [x] Markmap-01. **COMPLETE (2026-08-16):** 已独立写入结构和真实浏览器 failing-first 合同，覆盖受控 final SVG、链接/HTML 拒绝、恶意更新、重复渲染、click/error/load/wheel/pointerdown、page/console error、dialog、request、navigation、download 与卸载。首个运行为 unit `2 failed`、browser `1 failed`，证明当前仍是 inert 而不是隔离 enablement；artifact 见 `assets/markmap-01-first-failure.md` 和相邻 Playwright bundle。Markmap-02 是唯一下一项。
- [x] Markmap-02. **COMPLETE (2026-08-16):** `src/lib/markdown-poc/markmap.ts` 仅接受受限 `#`～`###` 标题树，并由 PoC 直接构造有限静态 SVG。该最小视图没有链接、HTML、CSS、平移缩放、下载、导航或外部资源；所有超出语法的输入精确 local fallback。unit `2/2` 与 browser `1 passed (1.2s)`；最终 artifact 为 `assets/markmap-02-final-pass.png`。Markmap-03 是唯一下一项。
- [x] Markmap-03. **COMPLETE / `ENABLED_ISOLATED` (2026-08-16):** 全 PoC `285/285`、Markmap 专用加既有 browser baseline `11/11` 通过；覆盖有限 static SVG、SSR/hydration、恶意 link-like update 的 exact local fallback、重复 render、主动观察和 unmount。`src` 在 PoC 外零 `markdown-poc` 引用；旧生产 Markmap 链未修改、未作 fallback。first/final artifacts 已保留。Chart-01 是唯一下一项；G2 继续 BLOCKED / NOT GO。

## D. Chart

- [x] Chart-01. **COMPLETE (2026-08-16):** 独立 unit/browser failing-first 合同覆盖 JSON allowlist、formatter/HTML-like 拒绝、Canvas/容器、恶意更新、重复 render、事件、page/console error、dialog/request/navigation/download 与 unmount。首轮 unit `2 failed`、browser `1 failed`，证明当前 inert 缺口；artifact 见 `assets/chart-01-first-failure.md` 与相邻 Playwright bundle。Chart-02 是唯一下一项。
- [x] Chart-02. **COMPLETE (2026-08-16):** `chart.ts` 只接受有限 bar JSON（`type`/`xAxis`/`series`）并在 SSR 输出受控 Canvas；hydration 后仅由 PoC-owned 2D draw 绘制。formatter、未知键、HTML-like labels、函数/动态执行、外部请求、下载均被拒绝为 exact local fallback。unit `2/2`、browser `1 passed (1.0s)`；final artifact `assets/chart-02-final-pass.png`。Chart-03 是唯一下一项。
- [x] Chart-03. **COMPLETE / `ENABLED_ISOLATED` (2026-08-16):** 全 PoC `286/286`、Chart 专用加既有 browser baseline `11/11` 通过；覆盖 strict JSON、SSR/hydration Canvas draw、formatter local fallback、重复 render、主动观察和 unmount。PoC 外零 `markdown-poc` 引用；旧生产 Chart 链未改、未作 fallback。SA-03 是唯一下一项；G2 仍 BLOCKED / NOT GO。

## E. 关闭

- [x] SA-03. **COMPLETE (2026-08-16):** mixed unit `2/2` 与 Chromium `1 passed (1.4s)` 同时覆盖三条安全输出、三条恶意局部回退、TOC/warnings/outcome、PoC global fallback、事件、error/dialog/request/navigation/download 与 unmount；无安全观察。SA-04 是唯一下一项。
- [x] SA-04. **COMPLETE (2026-08-16):** full PoC `12 files / 288 tests passed`、passing-state Chromium `15 passed (3.1s)`、`tsc --noEmit`、Batch 7 `4/4`、Prettier、PoC 外零引用、links/whitespace 均 PASS。warnings 仅为 12 条既有 jsdom `act(...)` 和 browser `NO_COLOR`/`FORCE_COLOR`；artifacts 已留存。
- [x] G2. **PASS / GO FOR F3 EVIDENCE ONLY (2026-08-16):** Mermaid、Markmap、Chart 均为 `ENABLED_ISOLATED`，SA-03/SA-04 PASS。此 Gate 不授权 M7、生产 Markdown consumer 切换、路由/视觉改造、Git 或部署。

## 执行纪律

一次只执行一个任务；每完成一项立即更新本文件、`validation.md` 和父工作夹对应条目。若计划需要扩大范围，先更新设计/需求/任务并重新请求批准。

## F4 前质量审查修复（待明确批准）

- [x] FIX-03-SA. **COMPLETE (2026-08-16):** SA-01～04 与 `288/288`、`15/15` 已明确为 2026-08-16 历史快照；当前交付只引用本轮实际完整回归（FIX-05）或明确的当轮聚焦结果，不把旧计数写成永恒输入。
- [ ] FIX-04-SA. 仅清理由本次修复造成的工作流格式噪音，保留所有适配器安全语义、artifacts 和生产隔离结论。
- [ ] FIX-05-SA. 复核特殊适配器相关未跟踪文件、当前全量测试/浏览器结果、warnings、生产零引用和残余风险，并把证据交给父级审计；不得启动 M7 或生产迁移。
