# 现状审计

当前状态：`F4 INPUT READY FOR SEPARATE APPROVAL — FIX-01～05 COMPLETE；G2/G3/G4 PASS；F4 NOT EXECUTED OR AUTHORIZED`。

## 2026-08-16 D1 方案 B 决策记录

- 用户已明确选择方案 B：Mermaid、Markmap、Chart 必须全部具备独立安全适配器并通过完整浏览器主动观测，G2 才能关闭；该条件现已满足。
- `markdown-special-adapter-enablement` 子工作夹现为 COMPLETE，G2 为 `PASS / GO FOR F3 EVIDENCE ONLY`。F3 仍不得越过尚未完成的 PSS/G3。
- 现有项目已经声明 Mermaid、Markmap、ECharts 和 D3 依赖，但版本、安全合同和最终输出仍须在 SA-01 用当前证据复核；现有依赖不等于适配器已经安全。
- 父工作夹修订清单和特殊适配器清单的用户批准已取得。SA-01 的独立 Mermaid 依赖/lockfile 判断亦已取得并完成；任何新的依赖、浏览器二进制或产品交互扩张仍须按暂停条件单独判断。

## 2026-08-16 F4 前总工作夹重组审计

### 当前结论

- 原始大任务是前端重构；本工作夹只覆盖其视觉改造和 F4 之前的技术基座。
- F0/G0、F1/G1 已完成；路由继续兼容共存，不实施删除、重定向或导航切换。
- Markdown M1～M6.9 已完成受控评估；其历史的三类 inert 结论已由方案 B 特殊适配器工作夹的 failing-first、浏览器和最终闭合证据取代，G2 现为 PASS。
- F2B 的 PSS-01 已完成合同与消费者冻结；PSS-02 的四项 endpoint 404 红灯已由 PSS-03 最小 route 转为 5 项通过。PSS-04 的 typed request/mode/invalidator 红灯已转为 focused 14 项通过；PSS-05/PSS-06 复核为 31 项相关回归通过。PSS-06 保留六个 `/api/folders` 的首次失败证据后，以最小 public folder guard 和 shared optional SWR key 修复，最终隔离浏览器 `3 passed`，无 strict/admin 噪音。
- G3 已由 PSS strict/optional/backend/browser 证据关闭，且 FIX-01 当前 `5 passed (12.6s)` 已补齐公开详情与真实挂载共享移动导航；G4 已由完整 editor contract 与 Option A 未获执行批准任务清单关闭。原 F4 输入包是历史快照；FIX-03～05 完成并独立复核前，F4 不是当前下一项。
- 父 workflow 仍含 M6.4/M6.5 旧当前态，两个子 workflow 仍写“等待已通过的 Gate”；这些是本轮 B1～B3 的文档同步目标，不是源代码状态。

### 历史与未来用户判断事项

| 决策               | 当前证据                                                | 若不判断的影响 | 推荐                                |
| ------------------ | ------------------------------------------------------- | -------------- | ----------------------------------- |
| D1 G2 产品接受边界 | 方案 B 的三类特殊适配器均已 `ENABLED_ISOLATED`；G2 PASS | 已解除 G2 前置 | 已选择 B，已满足                    |
| D2 编辑器方向      | 尚未执行 E1～E4，当前没有足够能力/成本矩阵              | G4 无法关闭    | 等证据完成后选择最小共享原语 + 共存 |

D1 与任务清单批准均已完成。D2 仍必须在 E1～E4 后判断，提前选择会把产品偏好冒充成源代码证据。

### 不需要用户逐项判断

- optional-session 的最小布尔 schema、错误分类、SWR key、缓存失效与消费者迁移顺序；
- 目标测试文件、隔离端口、合成夹具和浏览器断言的技术组织；
- E1～E4 的清点方法和对比维度。

JWT/Bearer 迁移、路由切换、生产 Markdown 切换、统一编辑器实现、视觉改造、F4、Git 和部署不是“代理可自行判断”，而是明确不在本轮范围。

## 已有子任务状态

| 子任务组                            | 当前状态                                  | 当前授权                                                  |
| ----------------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| route-ownership-alignment           | COMPLETE — R1–R5; G1 PASS                 | 总任务组统一授权已执行；兼容共存/暂缓切换；未实施路由变更 |
| markdown-rendering-security-poc     | M1–M6.9 complete as controlled assessment | D1 B was discharged by the special-adapter workflow       |
| markdown-special-adapter-enablement | COMPLETE — SA-01～04; G2 PASS             | isolated-only; no production Markdown migration           |
| editor-convergence                  | COMPLETE — D2 A; E1～E5; G4 PASS          | Option A list unapproved; no editor implementation        |
| public-session-state-optimization   | COMPLETE — PSS-01～06; G3 PASS            | Cookie-only optional/strict contract and browser evidence |

## 2026-08-16 G3 decision

`PASS — GO FOR F3 EVIDENCE ONLY`。

- 匿名 `/blog`、`/notes`、`/mistakes` 的隔离 Chromium 证据无 strict `/api/auth/me`、无 `/api/folders`/review/admin/AI/attachment 噪音，并维持可读 DOM；管理员显示态、登出、过期 Cookie 与 `/manage` 严格登录态全部闭环。
- 后端 optional/strict/auth-write 回归为 `14 passed`；严格匿名 `/api/auth/me` 仍为 401，`get_current_admin` 和写入、AI、上传、复习保护未改。frontend/Batch 7 为 `31 passed`，source TypeScript PASS。
- Gate 不构成产品切换授权：不改变 Cookie transport，不迁移 JWT/Bearer，不放松权限，不执行生产 Markdown、F4、Git、部署或视觉工作。它仅使 E1 源码盘点成为唯一下一项。
  | production-render-readiness-acceptance | OUT OF CURRENT EXECUTION SCOPE | only receives an F4 input package after G3/G4 |

历史授权来源：用户于 2026-08-10 明确要求交接 Prompt “携带我的全权批准”。该授权只覆盖当时清单。本轮已重组任务边界，源代码实施必须等待用户对修订 `tasks.md` 的明确批准。

## FFQ-01 当前消费者与依赖矩阵（2026-08-10，只读）

下表仅记录本轮从当前文件可复核的事实。`UNKNOWN` 表示尚未由当前源代码或本轮验证证明，不能以历史规划或浏览器记录替代。

| 工作线            | 当前源文件和已知消费者                                                                                                                                                                                                                                                                                                             | 前置 Gate                                            | 既定验证                                                                                 | 回滚责任/边界                                                                                                |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 路由归属          | `src/lib/content-routes.ts` 将内容详情分派到 `/blog/[id]` 或 `/notes/[id]`，而旧 `write-*` 编辑链接已指向 `/manage/*`；实际页面仍同时存在 `src/app/write*`、`src/app/write-note*`、`src/app/write-mistake*` 和 `src/app/manage/(workspace)`。                                                                                      | G0 后执行 FFQ-04；G1 才能作为后续路线依赖。          | route 子任务 R1–R5：源、链接、重定向、AuthGate 与文档核对。                              | 本线只形成 retain/redirect/new-route/deferral 决策；删除、重定向、导航切换另立实施清单。                     |
| Markdown 信任边界 | `src/lib/markdown-renderer.ts` 以 `marked` 产生 HTML；`src/hooks/use-markdown-render.tsx` 使用 `html-react-parser`，并按动态块进入 Mermaid、Markmap、Chart、KaTeX。当前调用点包括 `src/components/blog-preview.tsx`、`src/components/rich-text.tsx`、笔记详情和笔记预览。                                                          | G1 后执行 FFQ-05/06；G2 是任何后续预览收敛的证据门。 | M1–M7：恶意/语义夹具、SSR、hydration、浏览器、类型与构建。                               | PoC 仅隔离；在 G2 前不迁移生产消费者，也不把旧渲染器作为不安全回退。                                         |
| 编辑器能力        | 博客旧编辑器为 `src/app/write/components/editor.tsx`；笔记编辑器为 `src/app/write-note/page.tsx` 与其 hooks/components；错题旧兼容入口为 `src/app/write-mistake/components/staged-mistake-form.tsx`。`src/lib/api/notes.ts` 和 `backend/app/schemas/note.py` 均保留 `mistake` 的 question/answer/analysis/knowledge-point 等字段。 | G1 与 G2 后执行 FFQ-09/10；G4 为方案决策门。         | E1–E5：能力、保存、预览、字段和权限矩阵。                                                | 不预设 UnifiedEditor；字段不能降级为普通 Markdown，输出仅为最小共享原语或共存方案与后续清单。                |
| 公开会话状态      | `src/hooks/use-admin-auth.ts`、`src/lib/api/auth.ts` 及多个公开页面/详情/导航消费者构成当前共享状态链；精确机制、错误合同和后端依赖留待 FFQ-02 审计冻结。                                                                                                                                                                          | G0 与 G1 后执行 FFQ-07/08；G3 为权限与浏览器闭环。   | PSS-01–PSS-06：先后端失败测试，再前端 hook/消费者与浏览器网络证据。                      | 公开读取不加 AuthGate；`/api/auth/me`、`get_current_admin`、写入/AI/上传/复习与 AUTH_BYPASS 规则不得被放宽。 |
| 生产渲染就绪      | 本轮在 `src` 与 `backend` 搜索 `data-render-state`、`performance.mark`、`Performance.mark`、LCP/ready 相关标识，未找到当前实现的页面 ready mark 或 data attribute。历史空数据探测仅是输入证据。                                                                                                                                    | 必须同时等待 G3、G4；随后 FFQ-11–14。                | PRA-01–PRA-08：先 readiness 失败测试与最小标记，再隔离构建、合成数据、浏览器样本与清理。 | 不连接真实生产 API、真实数据或凭据；隔离构建不可行即 BLOCKED。                                               |

### 依赖与授权复核

```text
FFQ-01 + FFQ-02 + FFQ-03 -> G0
G0 -> FFQ-04 -> G1
G1 -> FFQ-05 -> FFQ-06 -> G2 -> FFQ-09 -> FFQ-10 -> G4
G1 + G0 -> FFQ-07 -> FFQ-08 -> G3
G3 + G4 -> FFQ-11 -> FFQ-12 -> FFQ-13 -> FFQ-14
```

- 五个子任务组均有 README、design、requirements、tasks、validation；R1–R5 和 G1 已完成，Markdown 线已完成 M1、正在补强 M2，其余线保持等待对应 Gate；未发现循环依赖。
- 2026-08-10 的统一授权允许按上述已有任务执行，但不能把任何未取得当前证据的 Gate 视作已通过。
- `UNKNOWN`：最终 Markdown 特殊渲染安全合同、其 Node 24 下的测试运行能力、编辑器共用边界、optional/strict 的实际认证合同、以及隔离生产构建可行性，均仍等待对应 Gate 的当前证据。

## FFQ-02 认证合同差异审计（2026-08-10，只读）

### 当前实现事实

- `backend/app/routers/auth.py` 的 `login` 与 `login-passkey` 创建 `AdminSession`、仅在响应中设置 `admin_session` HttpOnly Cookie（路径 `/api`）；token 本体不返回给前端。
- 同一文件的 `_resolve_session_user`、`get_current_user`、`get_current_admin`、`get_optional_user` 和 `/api/auth/me` 都从该 Cookie 读取会话 token，并用数据库中的 `AdminSession`、撤销状态和过期时间解析身份。当前文件没有解析 `Authorization: Bearer …`、`HTTPBearer` 或 JWT 的认证代码。
- `src/lib/api/client.ts` 的通用 `apiFetch` 使用 `credentials: 'include'`；`src/lib/api/auth.ts` 的 password/passkey 登录、`getMe` 和注销均经该 Cookie 会话流。`src/hooks/use-admin-auth.ts` 的 optional 显示状态与 strict `AuthGate` 目前都会调用严格 `GET /api/auth/me`，只是 SWR key、重新验证和去重间隔不同。
- 受保护的 notes 写入、上传、review 和 AI 路由仍依赖 `get_current_admin`；`backend/tests/test_manage_write_permissions.py` 对非公开写路由依赖以及匿名/无效 Cookie、非管理员 Cookie 的 notes 写入拒绝均有覆盖。
- 当前本地运行配置的非敏感状态为 `ENV=development`、`AUTH_BYPASS_ACTIVE=False`；本轮没有启用或依赖旁路。

### 目标架构规则

- 根 `AGENTS.md` 的架构规则仍规定：后端受保护 mutation 使用 `Authorization: Bearer <token>` 的 JWT，并把 `get_current_admin` 作为真实写入边界；它同时要求公开读取不被前端 AuthGate 封闭，且不允许以 `AUTH_BYPASS` 通过权限验收。
- 因而“Bearer/JWT 是目标规则”与“当前运行实现是 stateful HttpOnly Cookie 会话”是已证实的架构偏差，不可把任一方描述成另一方已经实现。

### 本任务组的冻结边界与结论

- 本任务组不授权认证提供方迁移、JWT 发行/校验、Cookie 到 Bearer 的双栈、CORS 扩展、`get_current_admin` 放宽或 `AUTH_BYPASS` 使用。
- F2B 只能在不变更 strict `/api/auth/me`、不变更受保护 mutation 的前提下，为**当前 Cookie 会话**设计 optional display-state 合同；这不是对 AGENTS Bearer/JWT 目标的实现宣告。若后续需要使当前实现符合该目标，必须建立独立的认证迁移任务、明确兼容与回滚方案，并重新取得范围授权。
- 当前差异可被一致解释为“目标规则未在当前实现中兑现、但本任务不触碰认证迁移”；它不是 F1 路由只读决策的阻塞项。它仍是 F2B 的强制冻结条件：任何会话改动必须保持 Cookie 严格机制和所有既有后端权限不变。

## FFQ-03 风险与 Gate 冻结（2026-08-10）

### G0：`PASS — 证据型基线通过`

| 判定项                       | 证据                                                                                | 结论                                                           |
| ---------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 五条线、前置 Gate 与统一授权 | FFQ-01 的当前矩阵和五个子 workflow 全文核对                                         | PASS：无循环依赖、无相互矛盾的执行授权。                       |
| 认证实现事实                 | `auth.py` 的 Cookie/session 解析、前端 include credentials、`/api/auth/me` 与消费者 | PASS：当前机制可复核为 Cookie，而非猜测为 JWT。                |
| 认证目标规则与本轮边界       | 根 `AGENTS.md`、FFQ-02 冻结结论                                                     | PASS：明确目标与现状不同，并已限定为不迁移；差异不被掩盖。     |
| 严格权限基础                 | `get_current_admin` 路由依赖、权限测试 `9 passed`、旁路状态为 false                 | PASS：本轮未放宽写入、AI、上传或复习权限，未启用 AUTH_BYPASS。 |

### 残余风险与归属

| 风险                                               | 状态                                                                                                                                                    | 归属/解除条件                                           |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| 当前 Cookie 会话未满足根规则的 Bearer/JWT 目标     | OPEN，非阻塞 F1；禁止借本任务隐式迁移                                                                                                                   | 独立认证迁移任务，须有兼容、回滚、测试和新的范围授权。  |
| 公共消费者仍用严格 `/api/auth/me` 并会产生匿名 401 | OPEN，受控等待 G1                                                                                                                                       | F2B PSS-01–06；必须先按冻结 Cookie 合同与失败测试验证。 |
| Markdown 特殊块安全、编辑器共用边界、隔离生产构建  | Node 24 阻塞已解除；M4 隔离普通内容合同完成（256/256 green）；M5 已拆为共享基线、Code、Math、Mermaid、Markmap、Chart 和关闭矩阵；真实浏览器执行仍未完成 | 分别由 M5.1–M5.7、M6/G2、G4 和 F4 当前证据决定。        |

### 历史时点的下一阶段入口

本段记录 2026-08-15 的历史入口：当时 M6 是唯一下一项。M6 现已完成受控评估与 M6.9 文档清理。当前入口见本文件顶部：D1 已选 B，等待父/特殊适配器任务清单批准；获批后先执行特殊适配器，F3 仍等待 G2。

## G1 路由方案决定（2026-08-10）

`PASS — 方案决策门`。采用 `route-ownership-alignment/design.md` 的兼容共存/暂缓切换方案：公开读取路径不动；`/manage/*` 保持私有工作区 owner；仍由页面和 dashboard 链接使用的 legacy writer routes 保留且继续严格保护；已存在的 `/mistakes/review` 私有兼容重定向不变。

理由：这是唯一同时由当前 route files、导航、AuthGate 约束和 `batch7-compatibility` 测试证明的可逆方案，不假设 `/manage/dashboard` 已与每个旧编辑器功能等价。路由实施仍需独立任务与授权。G1 已允许 F2A 与 F2B 的既定前置任务；F2A 现到 G2 决策点，F2B 尚未开始。

## 已有运行证据

- 匿名 `/notes` 空数据本地开发基线：内容就绪代理中位数 284.9ms，最大 362.8ms；
- 管理员正常登录至 `/manage`：中位数 201.0ms，最大 334.5ms；
- 匿名 `/notes` 会调用严格 `GET /api/auth/me` 并得到预期 401，UI 可正常降级；
- 上述证据不代表生产构建、真实内容量、移动网络或服务器冷启动。

## 当前主要未知

1. 三类特殊适配器能否在不扩大信任边界和生产范围的条件下全部达到 `ENABLED_ISOLATED`；
2. optional-session 在当前 Cookie 机制下的最小合同能否同时消除匿名噪音并保持严格失败显式；
3. 当前三个编辑器是否存在足够收益支持共享原语，或应继续共存；
4. F4 的隔离生产构建能否在不使用真实 API/DNS 放宽的情况下运行（本轮只记录输入，不验证）。

这些未知已经分别映射到 D1/G2、G3、D2/G4 和 F4。

## 工作树边界

当前工作树存在多份用户未跟踪文档和 workflow。总任务组必须只修改获批阶段的目标文件，不得清理、覆盖或提交无关内容。

## 2026-08-16 SA-01 Gate：BLOCKED / NOT GO

- 当前 Node/npm 是 `v24.18.0` / `11.16.0`；已安装并锁定 `mermaid@11.15.0`、Markmap `0.18.12`、ECharts `6.1.0`、Playwright `1.62.1`。现有 Playwright Chromium `1234` 缓存与 runner 匹配，无需浏览器下载。
- SA-01 的 `npm audit --omit=dev --json` 显示当前 Mermaid 版本命中 5 条公告（1 low、4 moderate），范围均覆盖 `11.15.0` 并要求至少 `11.16.1` 才脱离受影响范围。此证据使安全启用 Mermaid 前的最小变更成为依赖升级与 lockfile 重算。
- `package.json` 和 `package-lock.json` 已经是用户脏工作树的一部分（其中包含 Playwright runner 的既有改动）；本 Goal 不会覆盖、暂存或重写它们。升级 Mermaid 仍会触及这两份文件，属于 Goal 明定的独立审批门。
- 因此 SA-01 已完成核对但整体路径 `BLOCKED`，G2 保持 `BLOCKED / NOT GO`，SA-02、三类适配器、PSS、F3 与 F4 输入包都尚未开始。安全状态没有变更：没有生产消费者、认证、路由、数据、`AUTH_BYPASS`、Git 或部署动作。

### SA-01 已解除（用户批准后）

- 用户批准的最小依赖操作已执行：根声明和锁文件从 Mermaid `11.15.0` 更新至 `11.16.1`，其 Mermaid parser/Cytoscape/DOMPurify 传递锁定版本同步更新。没有改变 Markmap、ECharts、KaTeX 或 Playwright 的声明；没有下载浏览器。
- 复核安装图为 `mermaid@11.16.1`，并且审计输出不再有 `mermaid` 条目。全仓仍报告 7 条非 Mermaid 公告（2 moderate / 5 high），这些未被掩盖，也不在本项升级授权或后续 PoC 信任边界内。
- SA-01 现为 PASS/COMPLETE，G2 仍为 `BLOCKED / NOT GO`，下一项严格为 SA-02 的 failing-first 共享基线。

### SA-02 已完成：共享红灯基线

- 浏览器 harness 先以明确红灯证明缺少卸载接口，随后仅增加 test-only React root cleanup；聚焦回归 `1 passed`。这使后续适配器能证明重复 render/unmount，而不是只观察残留 DOM。
- Mermaid、Markmap、Chart 以相同完整周期红灯：SSR/hydration、恶意更新、两次安全重复 render、事件和所有主动浏览器观察、卸载均运行；每条最终隔离输出均实际 `false / 0 / 0`，而合同要求 `true / 1 / 1`。三条 artifacts 已落在特殊适配器工作夹。
- G2 继续 `BLOCKED / NOT GO`；这是 Mermaid-01 严格最终 SVG 合同测试的前置，而不是任何 renderer 的通过证据。

### Mermaid-01 已完成：结构合同

- Mermaid 的有效流程图和恶意 local fallback 均有测试先红后绿的结构证据（最终 `3/3`）。白名单、id/fragment 重写和拒绝 `foreignObject`/事件/URL/style 已在 PoC 中实现；首个失败 artifact 已保存。
- 当前只证明 SSR 安全占位与最终 SVG sanitizer 的结构合同；尚未证明真实 Mermaid browser render、hydration 更新和卸载无残留。因此 Mermaid 仍不是 `ENABLED_ISOLATED`，G2 继续 BLOCKED，下一项为 Mermaid-02。

### Mermaid-02 已完成：真实浏览器隔离边界

- 当前 Mermaid `11.16.1` 原始浏览器输出含 `foreignObject`、HTML/CSS 与 filters，不能安全纳入有限最终 schema。PoC 因此以已冻结的受限静态 flowchart 输入直接构造带节点标签和 marker 连线的 SVG；这不是 inert 路径，也没有触及生产消费者。
- `mermaid-isolated.spec.ts` 以 SSR/hydration、恶意更新、两次安全更新、最终 SVG、script sentinel、事件、page/console error、dialog、request、navigation、download 和 unmount 闭环通过。首个失败与最终通过 artifact 已在特殊适配器工作夹留存。
- Mermaid 尚未完成 Mermaid-03 的独立关闭验证，故状态仍不是 `ENABLED_ISOLATED`；G2 与 F3 继续 BLOCKED / NOT GO。

### Mermaid-03 已关闭：`ENABLED_ISOLATED`

- 全 PoC 从 8 个历史 inert expectation failures 收敛到 `9 files / 284 tests passed`；相关 Chromium matrix 为 `11 passed (2.1s)`。有效受限 flowchart 是 PoC-owned finite SVG，恶意输入仍是 exact local fallback；没有把第三方 Mermaid HTML-bearing SVG 放进最终 DOM。
- `src` 在 PoC 目录外没有 `markdown-poc` 引用。旧生产 Mermaid consumer 仍存在但未改、未作为 fallback；因此本项不构成 M7 或生产迁移。
- Mermaid 现在满足独立 `ENABLED_ISOLATED`；Markmap、Chart 尚未启用，故 G2/F3 仍为 BLOCKED / NOT GO，下一项严格为 Markmap-01。

### Markmap-01 已完成：独立 failing-first 基线

- 新增结构和 Chromium 合同先以 unit `2 failed`、browser `1 failed` 证明当前没有安全 final SVG，恶意 link-like source 仍是 inert 而不是 local fallback。相关 first-failure artifacts 已保留。
- 这没有调用、修改或继承生产 Markmap 链；下一项为 Markmap-02，G2/F3 仍 BLOCKED / NOT GO。

### Markmap-02 已完成：PoC-owned static SVG boundary

- 受限 `#`～`###` 标题树仅生成 finite SVG 的 rect/text/path；生产 Markmap transform/view、链接、平移缩放、CSS、下载、导航、外部资源均不进入 PoC。
- 聚焦 unit `2/2` 和 Chromium `1 passed (1.2s)` 通过，first/final artifacts 已留存。Markmap-03 尚未关闭，G2/F3 保持 BLOCKED / NOT GO。

### Markmap-03 已关闭：`ENABLED_ISOLATED`

- 全 PoC 从 8 个历史 inert expectation failures 收敛到 `10 files / 285 tests passed`；相关 Chromium matrix 为 `11 passed (2.2s)`。有效标题树是 PoC-owned static finite SVG，恶意 link-like source 是 exact local fallback。
- `src` 在 PoC 目录外没有 `markdown-poc` 引用；旧生产 Markmap consumer 未改、未作 fallback。本项不是生产迁移。
- Markmap 现在满足独立 `ENABLED_ISOLATED`，但它刻意不启用 pan/zoom、链接、导航或下载。Chart-01 是唯一下一项，G2/F3 继续 BLOCKED / NOT GO。

### Chart-01 已完成：独立 failing-first 基线

- unit `2 failed` 和 browser `1 failed` 证明安全 JSON 尚无 Canvas、formatter JSON 仍 inert。没有生产或 ECharts 调用；Chart-02 是唯一下一项，G2/F3 继续 BLOCKED / NOT GO。

### Chart-03 已关闭：`ENABLED_ISOLATED`

- 全 PoC `11 files / 286 tests passed`，相关 Chromium matrix `11 passed (2.1s)`；strict bar JSON、Canvas drawing、恶意 local fallback、重复 render 与主动观察均通过。
- Chart 只在隔离 PoC 中启用；生产 ECharts/consumer 未改、未作 fallback。SA-03 是唯一下一项，G2/F3 尚未关闭。

### SA-03 已完成：三适配器交叉闭环

- mixed unit/browser 通过，三类安全输出可共存且恶意更新均为 local fallback；没有主动安全观察或卸载残留。SA-04 是唯一下一项，G2/F3 继续 BLOCKED / NOT GO。

### SA-04 / G2 PASS

- Full PoC `288/288`、passing Chromium `15/15`、TypeScript、Batch 7 `4/4`、format/link/whitespace/PoC isolation 均 PASS；已知 warnings 不改变结论。
- G2 仅解除 F3 evidence 前置；M7、生产 consumer 切换、路由/视觉/Git/部署继续未授权。

### Chart-02 已完成：PoC-owned Canvas boundary

- strict bar JSON allowlist 结合 SSR Canvas 和 PoC 2D draw；未批准 config/local code/network/download 均不进入 output。unit `2/2`、browser `1 passed (1.0s)` 通过，artifacts 已留存。Chart-03 是唯一下一项，G2/F3 保持 BLOCKED / NOT GO。
