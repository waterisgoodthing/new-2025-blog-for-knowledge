# 基线与 convergence Week 1–2 审计

审计日：2026-09-27。范围：任务/路线 inventory、convergence Week 1（PR-01–04）和 Week 2（PR-05–08）、基线证据与当前多选再答缺陷。工作区 `refactor/baseline`，HEAD `4a954eaa92952fcc5a6b18a2e15d2e824b094e41`；开始时已有大量 dirty/untracked 改动。按只读审计执行，未改业务代码、未连接现有共享数据库、未运行测试；本报告是主审计的一个专项目录，Week 3/4 及前后端专项由其他负责人核验。

## 结论

- convergence Week 1 在 2026-09-09 的历史 Gate 记录为 PASS。PR-01–04 有实现、测试、scratch PostgreSQL、真实 Chromium、workerd smoke 和独立评审证据。PR-02/03 后续触及文件已有 dirty 改动，历史浏览器结果不等于对 2026-09-27 当前代码重跑；Week 1 的当前重验状态因此带有证据债。
- convergence Week 2 的历史 Gate 在 2026-09-21 记为 PASS，但本次在当前源代码上发现并由主 Agent 真实 Chromium 重现的 P1：多选题再答 UI 每次点击覆盖答案，只能提交单项；后端按精确集合判分，正确多选会被判错。故本次快照整体状态为 **PARTIAL**，不能沿用历史 PASS 表示当前 Gate 仍通过。
- 暂估 Week 1 完成区间 **92–97%（中高置信度）**；Week 2 **80–90%（中等置信度）**。区间是按验收面覆盖估计，不是代码行数统计；Week 2 的 P1 功能失败和人工全链证据留存矛盾拉低当前结论。
- 本范围未确认 P0。已确认 P1 只有上述再答多选提交错误。PR-06 迁移窗口期的 repetitions 偏差按原 PR 记录是 scratch-only 且书面接受，不报告成已发生的生产缺陷；部署前仍应验证实际旧数据并按需要重推导。

## 路线 inventory 与边界

仓库里存在多组不同命名的计划，不能把同名 Week 或 Phase 合并计算：

| 路线 | 覆盖 | 本专项目录中的判定 |
|---|---|---|
| `docs/workflows/personal-learning-system-convergence/` | 主学习系统交付：Week 1–4、PR-01–19 | Week 1/2 见本报告；Week 3/4 当前总体仍需主审计结合专项 worker 证据验收。没有独立的 convergence Week 5+ 已批准工作包。PR-20–26 是另行批准候选，不属于 Week 1–4 Gate。 |
| `docs/roadmap-2026-09.md` | 通用产品/技术债路线 W1–W5 与 W6+ 候选池 | 是另一套路线，不与上表的 convergence Week 编号等同。逐项状态见后表；未发现路线图本身能授权实施。 |
| `docs/roadmap-tasks.md` | June P0–P6 路线 | 独立历史计划；本 worker 只记录其存在，不把它填充进 convergence 后续 Week，也不折算到本次完成率。 |
| `docs/workflows/personal-learning-system-v2-unification/` | 统一方案 phases 0–8 | 独立方案；当前目标/阶段状态应按该目录的任务和验证文件核验，不能据名称推断与 convergence Week 3/4 等价。 |
| UI Foundation F0–F5、UI V2 U1–U16 与 I-series | 独立 UI/历史收尾计划 | 独立计划 inventory 项；本 worker 未逐项验收，不得计为已授权欠账或 convergence Week 5。 |

### 9 月通用路线 W1–W5 逐项映射

这里用路线图自身的 W 编号。每行状态依据当前代码/配置是否承载该要求；`IMPLEMENTED_UNVERIFIED` 表示功能路径存在，但路线要求的验收证据没有在此处完成；`NOT_IMPLEMENTED` 表示要求的实现/产物未见。路线图是独立路线，本表不把未批准的产品工作自动当成历史 Gate 欠账。

| Sept 路线任务 | 预期与验收 | 审计状态 | 证据 / 风险 |
|---|---|---|---|
| W1-a 死路由树拆除 | 删除 `/write*`、`/write-note*`、`/write-mistake*`、`/mistakes/review` 路由树及仅其引用模块；保留的重定向应在一个周期后清理；净减 ≥6,000 行 | `PARTIAL` | `next.config.ts:46-53` 已将旧入口重定向到 `/manage/*`，但当前 `src/app/write/`、`write-note/`、`write-mistake/`、`mistakes/review/` 仍有页面/组件，同名源树尚未删除。尚未以 HEAD 做净行数比较。 |
| W1-b 管理入口收敛 | `manage/page.tsx` 收敛进 `(workspace)`，拆 5 个内联 tab | `PARTIAL` | `/manage/(workspace)/layout.tsx:10-21` 有 AuthGate 与新工作区；旧 `src/app/manage/page.tsx:34-46` 仍保留 9 个 tab，并在同文件定义大型 `ContentTab`。两代入口并存。 |
| W1-c CRUD 抽象 | `projects/share/pictures/bloggers/snippets` 五列表共用 `useContentCollection` hook 与管理弹窗 | `NOT_IMPLEMENTED` | 当前五目录各自保留 `page.tsx`、服务/列表及 create/upload dialog；`src/app`、`src/hooks`、`src/lib` 未找到 `useContentCollection`。 |
| W1-d CI/静态护栏 | CI 前端 job 跑 `npm test` 与 `test:typecheck`；加 ruff、eslint、dependabot | `PARTIAL` | `.github/workflows/ci.yml:28-38` 已运行 shipped/test typecheck、unit tests、build；目前 `.github` 只有 CI workflow/模板，没有 dependabot 配置；`package.json` 没 lint 脚本，CI 注释说明无 ruff/mypy。 |
| W1 acceptance | `src` 净减 ≥6,000 行、全测试绿、UI 无可见变化、CI 含前端测试 | `PARTIAL` | CI 前端门禁存在，但路由树/旧管理页仍在；本 worker 未量化净行数，也未做前后 UI 差异验收。 |
| W2-a editorial tokens | 设计变量集落在 Tailwind 4 的 `theme.css` | `PARTIAL` | `src/styles/theme.css:1-15` 仅定义少量旧色彩/字体变量。较丰富的变量在 `src/components/ui-v2/tokens.css:1-54` 的 `--uiv2-*` namespace 并保持 additive-only；尚未与旧 `theme.css` 收敛成单一 editorial token 层。 |
| W2-b 统一导航 | sticky 浮动顶栏替代桌面 VerticalNav/sidebar 与移动底部 MobileNav | `NOT_IMPLEMENTED` | 当前 `manage/(workspace)/layout.tsx:11-16` 组合桌面 `ManageSidebar`、移动 `ManageMobileNav`、普通 `ManageTopbar`；`ManageSidebar` 是左侧常驻分组导航，无 sticky 顶栏替代。 |
| W2-c Modal/Drawer/Popover 可访问性合同 | 键盘可操作、焦点管理、背景隔离 | `PARTIAL` | 管理移动抽屉有 Escape、focus trap、inert、开闭焦点处理（`manage-mobile-nav.tsx:36-115`）；通用 `DialogModal` 只有 scroll lock/Escape，`Drawer` 只有 scroll lock/Escape（`dialog-modal.tsx:22-46`、`drawer.tsx:23-35`），未形成所有浮层通用焦点合同。 |
| W2-d 视觉回归验收 | 全站导航和浮层有基线截图对照、无可见回归 | `IMPLEMENTED_UNVERIFIED` | 当前 legacy、workspace、UI V2 多套视觉/组件同时存在；本 worker 未找到证明该 Sept 路线全站基线对照通过的记录。 |
| W3-a 三编辑器共享原语 | capture、notes、mistakes 使用同一共享原语库，明确不做 UnifiedEditor | `PARTIAL` | 笔记/博客在 `manage/(workspace)/notes/components/content-editor.tsx:10-32` 复用 `useNoteEditor`；采集独立在 `capture/components/capture-workspace.tsx`；canonical 错题详情编辑独立在 `mistakes/components/mistake-detail.tsx` 并用 `ManageFormPanel`，旧错题表单也仍单独存在。未见三者接入的通用 editor primitive 库。 |
| W3-b AuthGate 清单 | editor route ownership 与授权覆盖表通过 | `IMPLEMENTED_UNVERIFIED` | workspace layout 包 AuthGate；旧 write/edit 页面也有局部 AuthGate。但本路线要求的全三编辑器 route coverage checklist 当前未见，本 worker 未实测未登录行为。 |
| W4-a Sanitization 白名单 | 按路线要求补 `rehype-sanitize` | `NOT_IMPLEMENTED` | `package.json` 无 `rehype-sanitize`，源码未有 `rehypeSanitize`。现生产 `markdown-renderer.ts:109-127` 有 raw HTML drop 与 link/image protocol allowlist，这是部分自定义防护，不能等同该 sanitizer 交付。 |
| W4-b 加固 M7 生产切换 | `use-markdown-render` 改用 M7 hardened renderer | `NOT_IMPLEMENTED` | 生产 `src/hooks/use-markdown-render.tsx:45-47` 仍调用 `@/lib/markdown-renderer`。`src/lib/markdown-poc/render-poc.ts:1-7` 明写 PoC 且生产不得 import；本 worker 搜到的调用都在 PoC 测试/fixture，未见产品 import。 |
| W4-c PoC 收尾 | 删除或归档 `src/lib/markdown-poc/` | `NOT_IMPLEMENTED` | PoC 源码、浏览器 harness 与多组测试仍在 `src/lib/markdown-poc/`。 |
| W4-d 生产路径安全与渲染验收 | sanitizer、Mermaid/Markmap/Math/Chart 的截图/安全测试在产品路径通过 | `PARTIAL` | PoC 下有测试（如 `markdown-poc/__tests__/dom-safety.test.ts`），但这些测试调用隔离 `renderMarkdownPoC`；未找到生产 `markdown-renderer` 的同范围安全测试文件，也未证明新 renderer 已进入产品路径。 |
| W5-a SEO 元数据 | blog/notes 页面真实 `generateMetadata` / OG | `NOT_IMPLEMENTED`（源码搜索范围内） | 当前源码未找到页面 metadata/OG 定义；路线要求分享链接真实标题/OG。 |
| W5-b GA 配置 | Analytics ID 移入环境变量 | `NOT_IMPLEMENTED` | [head.tsx](../../../../src/layout/head.tsx#L18) 仍硬编码 `G-ZNSFR7C9PM`。 |
| W5-c Lighthouse 性能门禁 | CI Lighthouse，LCP < 2.5 秒并处理 RISK-PRA-001/002 | `NOT_IMPLEMENTED` | 当前 CI workflow 未见 Lighthouse 门禁；本 worker 未自行采集 LCP。 |
| W5-d LikeButton 定时器 | 清理组件卸载时 timer | `PARTIAL` | [like-button.tsx](../../../../src/components/like-button.tsx#L25) 的 `justLiked` timer 有 cleanup，但首次显示和粒子 timer 未清理。 |
| W5-e 图标按钮可访问性 | icon-button `aria-label` 专项清查 | `PARTIAL` | `LikeButton` 有 `aria-label='Like this post'`；仅这一处 source observation 不能代表全站专项清查，未见完整检查产物。 |

路线图 W6+ 列出监控/告警、coverage 工具、SBOM/NOTICE、对象存储迁移、cmdk 创作面板和旧 refactor 报告归档删除。这些属于候选池，不是已批准的 W1–W5 任务，不能标为逾期或并入 convergence 完成率。

## Week 1/2 逐 PR 证据矩阵

分类采用八种审计状态：`VERIFIED_COMPLETE`、`COMPLETE_WITH_DEBT`、`PARTIAL`、`SURFACE_COMPLETE`、`IMPLEMENTED_UNVERIFIED`、`NOT_IMPLEMENTED`、`REGRESSION`、`OBSOLETE`。状态针对当前快照；PR 文档中的历史 PASS 单独注明，不自动覆盖当前复验结论。

| PR | 预期 | 当前实际与证据 | 状态 | 风险 |
|---|---|---|---|---|
| PR-01 Runtime Smoke | workerd 生产工件，资源/页面/API 健康检查可阻断发布 | `week1/README.md` 记录脚本 15/15、production preview 资产 20/20、checks 23/23，正向 exit 0、失效 API exit 1。证据索引 `week1/evidence/README.md` 与技术报告。 | `VERIFIED_COMPLETE`（历史 Gate） | 当前 CI 接线与生产端真实部署不在 PR-01 scratch/local 证据范围内。 |
| PR-02 Note/Blog 写作 | `/manage/notes` 新建/编辑，ContentEditor，保存错误恢复、确认发布、移动端可用 | `week1/README.md` 记载 workerd Chromium 19/19、scratch 行读回；技术报告存截图及运行摘要。 | `COMPLETE_WITH_DEBT` | 管理写作相关当前源码后来有 dirty 改动；未在本审计重跑 19 项。历史浏览器证据不证明本快照行为。 |
| PR-03 Error/Retry | `/notes` 与 Dashboard 主要面板具备 loading/empty/error/retry，焦点和 reduced-motion 合理 | 历史 Chromium 9/9，失败后重试恢复；报告载明焦点/reduced-motion 观察。 | `COMPLETE_WITH_DEBT` | Dashboard/notes 源码在当前工作树已改；没重跑历史浏览器路径。 |
| PR-04 Guestbook migration 027 | 新库可创建；存量表安全 no-op；局部不一致 fail-closed | PR-04 记录 fresh、模拟存量、partial 三类 scratch upgrade/downgrade，runtime POST/GET 持久化；未连接真实 `blog_db`。README 表明真实库当时停在 025，026/027 生产升级需另行授权。 | `COMPLETE_WITH_DEBT` | 真实部署库 revision/schema 适配仍未核验；不属于历史 scratch Gate 失败，也不能据此宣称生产迁移完成。 |
| PR-05 review schema 028/029 | 状态/算法/last_rating 与 ReviewRecord 状态跨 migration/model/schema/TS 一致 | `week2/pr-05.md` 记载隔离空库 replay、rollback、跨层契约；targeted 42 passed、当时全量 451 passed/6 skipped。当前审计 evidence 的 Alembic 空库 roundtrip 已到 033。 | `VERIFIED_COMPLETE` | PR-06 条件性历史 repetitions 数据风险见下行；生产 DB 数据状态没有被本 worker 查询。 |
| PR-06 fixed interval v2 | lapse reset、间隔阶梯、mastery 规则、并发保护 | `week2/pr-06.md` 记载 scratch 验证、状态机 9/9、相关服务共 51 passed、Gate/acceptance PASS。 | `COMPLETE_WITH_DEBT` | PR-05→06 窗口期如存在真实触碰数据，部署前需以 `review_records` 重推导 repetitions；原记录说明仅 scratch 受影响并接受此偏差，生产库未由本 worker 验证。 |
| PR-07 Re-answer API | single/multiple/true_false 自动判断、短答规则、审计 Attempt 关联及 DTO 一致 | `week2/pr-07.md` 记载 030 scratch 往返、判分 17/17、当时后端全量 476 passed、前端 Vitest 464；本次主审计隔离 E2E 中 Review 全链 1 项通过。当前源代码的 multi-choice API 精确集合判分见 `reanswer_service.py:82-90`。 | `VERIFIED_COMPLETE`（API） | API 正确性与 PR-08 UI 输入缺陷形成跨层不一致。 |
| PR-08 Review 再答 UI | 从题面提交作答、显示判定/建议、确认并写 ReviewRecord；六档值保真 | 历史组件测试覆盖 single-choice 与自动化全链；2026-09-27 真实 Chromium 依次点击 A、C 后 `aria-pressed` 只有 C=true，POST 201 发送 `submitted_answer="C"`，返回 `is_correct=false` / `recommendation=2`。证据：`evidence/probe-multiple-choice.txt`、`probe-multiple-choice.cjs`、`multiple-choice-failure.png`。源码 `review-queue.tsx:173-185` 单值覆盖；后端 `reanswer_service.py:82-90` 做 exact-set 判定。测试 `review-queue.test.tsx:49-57,91-107` 的 mock 题型为 single-choice。 | `PARTIAL`（当前 Gate） | **P1**：多选题正确答案不能通过当前 UI 提交，用户正确作答会收到错误判定和低建议分。Week2 历史 PASS 被本次复现推翻。 |

### Week 1–2 当前源码对照（与历史 Gate 分开）

| PR | 当前实现路径与可确认行为 | 当前源码结论 |
|---|---|---|
| PR-01 | [runtime-smoke.mjs](../../../../scripts/runtime-smoke.mjs#L22) 抽取脚本/link 资产、排除 connection hint 并去重，检查首页、`/notes`、backend health；`:79-80` 任一失败返回 exit 1。`.github/workflows/ci.yml:112-196` 的 Job 3 实际构建 workerd、启动 backend/preview 并调用 smoke。 | 实现和 CI 接线仍在；历史真实 smoke 证据之外，本轮未重跑。 |
| PR-02 | 新建 [notes/new/page.tsx](../../../../src/app/manage/%28workspace%29/notes/new/page.tsx#L7) 将 Blog/Note type 传给共享 `ContentEditor`；编辑 [notes/[slug]/page.tsx](../../../../src/app/manage/%28workspace%29/notes/%5Bslug%5D/page.tsx#L9) 取 detail 后复用同一组件，组件调用 `useNoteEditor`。 | 统一 workspace 写作路径还在；旧写作 route tree 与 redirect 仍并存。 |
| PR-03 | [AsyncStatePanel](../../../../src/components/async-state-panel.tsx#L40) 提供 loading skeleton、error/alert、Retry 与焦点恢复；`src/app/notes/error.tsx` 和 `(workspace)/dashboard/error.tsx` 接该组件。 | 公共组件与当前错误边界存在；本轮未重新制造请求失败检查浏览器行为。 |
| PR-04 | [027_guestbook.py](../../../../backend/alembic/versions/027_guestbook.py#L29) 检查 guest tables 双表存在/精确 schema；不一致抛错；文件后段以 ownership marker 限定 downgrade 删除对象。 | 迁移保护代码仍存在；不代表目标生产库已升级或现场 schema 符合。 |
| PR-05 | `028_review_items_v2.py:81-112` 在检查 v1 shape 后扩展 constraints、新增 `last_rating`，将存量 `algorithm` 设置 v2；model/schema/TS DTO 现存。 | 跨层实现路径可见；仍需按目标 DB 数据条件做部署前检查。 |
| PR-06 | `review_item_service.py:21-37,62-79` 通过 `schedule_v2` 与 submit service 更新 repetitions、interval、last_rating；PR-06 文档保留窗口期重推导条件。 | 当前服务行为存在；不由源码证明真实库是否有被影响的历史行。 |
| PR-07 | [attempts router](../../../../backend/app/routers/attempts.py#L10) router 级 `get_current_admin`，`POST /review` 调用 reanswer service；客户端 [attempts.ts](../../../../src/lib/api/attempts.ts#L34) 将提交答案作为字符串传入。 | API 边界和 DTO 仍是单字符串；多选 UI 必须将选中集合按 API 约定序列化，当前无法表达该集合。 |
| PR-08 | 当前 UI `review-queue.tsx:173-185` 将点击答案覆盖成单字符串；该字段传给 PR-07 字符串 DTO。 | 见上表 P1 真实 Chromium 复现。 |

### Week 2 文档证据一致性

- `week2/pr-06.md:3` 文件开头仍写 implementation/review/verification/G0/G2/acceptance `NOT_VERIFIED`，而 `:35-44` 状态区写各项 PASS。基于后文详细 dated evidence 与 Week2 README，实际历史结论更支持 PASS；文件开头是未同步的 stale metadata。
- `week2/pr-08.md:34-37` 写人工 walk-through 未执行且 Week2 Gate `NOT_VERIFIED`；`:48-49` 又写 2026-09-21 用户走通并由 primary owner 接受，week2 README 也说 Gate PASS。证据目录里没有对应人工 walk-through 的独立浏览器记录。此证据留存问题与 2026-09-27 新的多选 probe 是两件事：新 probe 已归档，但并未复演 Week2 所有人工全链验收。
- 撤回先前怀疑的数字快捷键截获再答输入：`ratingKeyDown` 在评分组容器内注册，评分组与再答面板是兄弟 DOM 节点（`review-queue.tsx:263-292` 及 `:204` 起）。没有证据支撑“键盘 handler 截获再答答案”，本报告不把它列为缺陷。

## 八维质量画像

| 维度 | Week 1 | Week 2 | 证据边界 |
|---|---|---|---|
| 1. 业务目标与闭环 | runtime smoke、写作流程与错误恢复历史 Gate PASS | Re-answer API→评分→ReviewRecord 主链已实现；multi-choice UI 缺口使完整复习闭环未达标 | Week1 测试是 2026-09-09 历史；Week2 多选是当前真实浏览器 P1。 |
| 2. 用户体验与交互 | 历史覆盖新建/编辑、确认发布、移动 Drawer、retry/focus、reduced-motion | 六档评分、推荐覆写和普通 Toast 已实现；动效编排延期；multi-choice 输入模型错误 | Week2 历史 motion 仍是记录延期；真实 probe 证明题型功能错误。 |
| 3. 架构与边界 | smoke 与 UI/backend 健康职责分开；ContentEditor 共用 | Review API/业务 service/schema/client分层齐全；UI 以单字符串承载了多选集合 | 本报告不代表对全站架构全面审查。 |
| 4. API 与契约 | `/notes` 及 health 行为有历史 Chromium/runtime 证据 | PR-05/07 migration、model、Pydantic、TS 有历史契约验证；multi-choice API exact-set 判分正确 | 缺陷在 UI/API 语义接线，不是后端多选判分器。 |
| 5. 数据正确性与迁移 | 027 新建/存量/partial 安全行为在 scratch 通过；生产库未升级 | 028–030 scratch 链与 rollback 有历史证据；旧 review-item repetitions 生产状态待部署前核验 | 本 worker 未查询共享/生产 DB；当前审计使用隔离 scratch roundtrip。 |
| 6. 安全、授权与隐私 | Week1 没有弱化 admin boundary；生产 migration 未获此任务授权 | 新 API 延用管理边界；Week2 记录没有扩大公开路由。未重审所有权限路径 | 仅在对应 PR 变更和已有证据范围内核对，不声称穷尽式安全评估。 |
| 7. 可访问性、响应式与性能 | 有历史多视口/reduced-motion/focus evidence，Smoke 证明资源加载，不等于 LCP 预算 | 44px 触控目标有 PR-08 记录；motion 未完成；新缺陷可通过屏幕 reader pressed 状态观察 | 未在当前快照执行 Lighthouse 或完整 WCAG audit。 |
| 8. 测试、运维与可追溯 | Week1 43 files/395 frontend、416 backend + 7 skipped、Smoke 20/20 是历史记录 | PR-05–08 有定向和历史 full-suite；本次 workflow artifacts 记录全仓 backend **922 passed/9 skipped/2 warnings/47 subtests**、frontend **522 passed**；真实 Playwright business E2E 5/5、build/runtime smoke 与 migration 033 roundtrip 有归档 evidence | 这些 922/522/E2E 由主 Agent 在并行审计中运行；本 worker 未运行/复核执行环境。全仓绿灯没有捕捉 multi-choice，因为 PR-08 现存组件测试只走 single-choice。 |

## 当前专项证据清单与限制

- PR 记录：`personal-learning-system-convergence/week1/README.md`、`week1/week1-technical-report.md`、`week1/pr-01.md`–`pr-04.md`、`week2/README.md`、`week2/pr-05.md`–`pr-08.md`。
- 2026-09-27 审计运行件（由主 Agent 产生）：`evidence/backend-test.txt`、`frontend-test.txt`、`e2e.txt`、`build-cf.txt`、`runtime-smoke.txt`、`migration-empty-roundtrip.txt`、`probe-multiple-choice.txt` 及 Playwright 截图。这里只读取已归档结果；不把它们描述为本 worker 本地重跑。
- 本 worker 未连接数据库、未执行迁移、未运行测试，也未修改项目文件；证据结论来自当前源码/文档、主 Agent 归档的真实浏览器和测试输出，以及 Week1/2 历史记录。

## 处理优先级建议

1. **P1，修复和复验另开授权工作项**：让多选 UI 维护一个可序列化的集合（并按 API 契约提交），新增真实浏览器测试覆盖点选/取消、精确集合判对、漏选/多选判错及 ReviewRecord 回链；合并后重跑 PR-08 Gate。此审计没有修改代码。
2. **发布前条件**：只读盘点目标库从 028 到 PR-06 生效之间是否存在 review activity；若有，先从完整 `review_records` 轨迹重推导 repetitions，并在隔离库验算结果。不能把历史书面接受当作生产库“无数据”的证明。
3. **证据整理**：统一 PR-06/PR-08 状态头部与正文；补入 Week2 人工 walk-through 归档，或将该验收明确改成未完成并重新判断 Gate。
4. **Week1 当前态复验**：如果要把 Week1 历史 PASS 作为当前 release statement，应对 dirty 工作区改过的 Notes、Dashboard、manage 写作路径重跑关键 Chromium flows。现阶段它只支持“2026-09-09 Gate 曾 PASS”。

路线分层、Sept W1–W5 其余 NOT_VERIFIED 项、Week3/4 和 P0/P1 全局复核，留待主审计汇总其他 worker 证据。本文件不授权修复、共享数据库写入、生产迁移、提交、推送或部署。
