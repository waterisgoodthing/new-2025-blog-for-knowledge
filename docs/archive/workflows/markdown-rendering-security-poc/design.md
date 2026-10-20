# Design

The PoC boundary is:

Untrusted Markdown -> bounded parse -> approved syntax -> structural sanitize -> React mapping -> constrained special renderer -> final DOM or SVG validation.

Public and admin-preview modes share the same HTML, URL, event-attribute, and SVG safety baseline. Administrator and AI content do not receive a broader trust policy. Dangerous URLs, raw HTML, scripts, iframe content, unsafe SVG features, and generated output failures must degrade locally to inert text or a safe block error.

Inert output must preserve its decoded source text exactly. HTML escaping supplies the structural boundary; the renderer must not insert zero-width characters or otherwise rewrite event-like or protocol-like text merely to satisfy string-based checks. M5 acceptance must compare parsed-node `textContent` with the source and inspect parsed elements, attributes, and URL values directly. Serialized-HTML checks remain useful supporting evidence but are not the sole DOM-safety proof.

The PoC is exposed only through a fixture or disabled-by-default flag. It must not delete marked, modify the existing hook, or switch a public or private production consumer.

## 验证分层（2026-08-10 M3 纠偏修订）

PoC 安全验证按执行环境分三层，不可提前合并或跳过：

| 层级          | 阶段 | 验证内容                                                                                           | 工具                                          |
| ------------- | ---- | -------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| L1 结构合同   | M3   | 结构/URL 合同、真实 SSR（renderToString）、真实 React hydration（hydrateRoot）、jsdom DOM 安全合同 | vitest + jsdom + react-dom/server             |
| L2 浏览器执行 | M6   | 真实浏览器中的 SVG 渲染、Canvas 绘制、事件分发、危险导航拦截                                       | Playwright 或 Puppeteer（届时重新查询并安装） |
| L3 证据门     | G2   | 综合 L1+L2：没有真实浏览器执行证据不得给 GO                                                        | Playwright/Puppeteer 测试报告                 |

**规则：**

- M3–M5 不安装 Playwright/Puppeteer；M5 只完成共享结构合同和逐适配器决策，真实浏览器执行统一推迟到 M6。
- G2 是硬门：没有真实浏览器证据不得给 GO。
- jsdom 只能证明 DOM/HTML 结构，不能证明真实浏览器执行。

## M6 受控扩展设计（2026-08-15；已执行，2026-08-16 文档清理）

M6 不把四个特殊适配器捆绑为一次性启用。它按下列阶段顺序执行：

`runner/evidence freeze -> inert browser baseline -> Math -> Mermaid -> Markmap -> Chart -> fallback closure -> M6 evidence matrix`

执行结果：Math 为 `ENABLED_ISOLATED`；Mermaid、Markmap、Chart 为 `DEFERRED_INERT`。这不是 G2 GO。当前记录必须使用配置文件指定的 Playwright 命令，不得使用不存在的 `chromium` 命名项目；历史 trace 缺失以及 deferred 路径观测覆盖不足均保留为 G2 风险。

每个适配器都必须独立完成元素、属性、URL、样式或配置白名单，再进入真实浏览器验证。最终状态只能是：

- `ENABLED_ISOLATED`：仅在隔离 PoC 中启用，结构合同和真实浏览器证据均通过。
- `DEFERRED_INERT`：保留 M5 的精确文本 inert fallback，记录失败证据和未满足的合同。

某一适配器被延后不阻断后续适配器的评估，也不允许通过弱化测试来换取启用结论。

### 真实浏览器观测合同

每个启用候选至少必须观测：

- 页面启动、SSR 到 hydration 及安全内容更新为恶意内容时，没有未解释的 `pageerror`、hydration error 或安全合同变化。
- `window.__markdownPocXss` 等执行哨兵不得被脚本、事件或 formatter 改写。
- 真实分发 `click`、`error`、`load` 等相关事件后，不得触发内联事件处理器、危险导航或未授权下载。
- 捕获并断言导航、弹窗、下载、网络请求、console error 和页面异常；不以“没有看到异常”替代主动断言。
- 安全相邻块、TOC、warnings 和 outcome 在局部失败后保持可观测；全局失败必须进入 PoC 自有的安全 fallback，不得调用旧 Markdown 渲染链。

### 适配器顺序与单一变量

- Math：只改变 KaTeX 最终 HTML 的元素、class 和 style-value 过滤边界。
- Mermaid：只改变 Mermaid 最终 SVG 的元素、属性、命名空间和 URL 边界。
- Markmap：在已验证的 SVG 基础上，单独处理链接、缩放/平移与下载边界。
- Chart：只接受 JSON 数据子集和显式配置白名单；禁止 formatter 函数、任意代码、动态 import 和非预期网络请求。

### 边界与暂停条件

- M6 仍只允许隔离 PoC 和测试表面；不修改生产 Markdown 链、路由、auth、API、DTO、数据库、持久化或部署。
- M6.1 只读核对 runner 候选、当前官方版本、license、advisory、peer、lockfile 和浏览器二进制影响。任何安装、升级、删除或 lockfile 变更都必须在该记录后单独获得明确批准。
- 每个适配器最多进行 3 轮有新证据的聚焦修正；仍不满足合同时标记 `DEFERRED_INERT` 并继续下一项。
- 如必须修改生产消费者、放宽信任策略、使用旧渲染器 fallback、使用真实私有内容或执行 Git/部署动作，立即暂停并请求新授权。
