# 前端质量专项审计

## 结论

**PARTIAL。** 私有管理端已有清晰的 App Router 结构、带 session cookie 的类型化 API client、共享异步状态组件和部分真实浏览器流程。本轮主 Agent提供的 Vitest、类型检查、构建与 Chromium E2E 均通过；但一次真实浏览器 probe 已复现多选复答 UI 只能提交单个选项，练习入口也会把用户带入可编辑题目表单，QuestionEditor 的加载失败状态没有重试和辅助技术语义。这里仅做只读审查，未重跑验证，保留已有未提交工作。

## 范围与证据边界

审阅管理端 Dashboard、今日练习、复习队列、QuestionEditor、异步状态组件、API client/DTO、管理 shell/移动导航、UI v2 预留区和对应测试。使用既有 `evidence/frontend-test.txt`、typecheck/build/E2E 日志、`probe-learning.txt`、`probe-multiple-choice.txt`、`multiple-choice-failure.png` 与 `review-mobile.png`；这些结果由主 Agent提供，本专项未再次执行。

5 条 Chromium E2E 覆盖登录进入 Dashboard、笔记创建、capture 草稿、review 再答/ReviewRecord、公开笔记失败重试；没有覆盖今日练习选择→作答，也没有逐项追溯 Dashboard 显示值。本次手机截图为单一 390px review 页面视口，不代表屏幕阅读器、键盘、跨浏览器或完整移动设备矩阵。

## 已有质量

- `/manage/(workspace)` 页面由 `AuthGate` 包裹；核心读写经 `src/lib/api/*` typed client，`apiFetch` 统一使用 `credentials: 'include'` 和错误分类。UI 路由保护只负责导航体验，后端仍是实际授权边界。证据：`src/app/manage/(workspace)/layout.tsx:6-22`、`src/lib/api/client.ts:75-109`。
- Dashboard 使用 SWR 分开加载 summary/profile；今日练习明确区分 loading、empty、error、ready 并在重试成功后移动焦点。共享 `AsyncStatePanel` 提供 skeleton、`role=status`、错误 `role=alert`、重试 busy 状态和 reduced-motion。证据：`src/app/manage/(workspace)/dashboard/dashboard-content.tsx:10-34`、`src/app/manage/(workspace)/practice/practice-today.tsx:20-92`、`src/components/async-state-panel.tsx:40-85`。
- Review 多选项当前按钮具备文本名称及 `aria-pressed`，但交互语义对 multiple-choice 不成立，详见 FE-01。管理端抽屉实现 Escape、焦点约束、背景 inert 与焦点恢复，并有相应测试。
- `src/features/ui-v2/README.md` 明确其为预留业务组装位；当前学习主线仍是 `src/app/manage/(workspace)` 页面，不把 UI v2 的孤立组件测试当成已连接的业务验收。

## Findings

| ID | 等级 | 状态 | 发现与证据 | 影响 / 建议 |
|---|---|---|---|---|
| FE-01 | P1 | 浏览器已复现 | ReviewQueue 在有选项时每次点击都执行 `answer: option.key`，未按 question type 支持多选。主 Agent提供的 Chromium probe 点击 A、C 后只有 C 的 `aria-pressed=true`，请求只发送 `submitted_answer: "C"` 并收到 incorrect。证据：`src/app/manage/(workspace)/review/review-queue.tsx:169-186`、`evidence/probe-multiple-choice.txt`、`evidence/multiple-choice-failure.png`。 | 多选题答案无法完整表达，用户可能看到错误复答结果，且这次 Attempt 可被关联到用户后续评分。按题型提供可多选控件并统一序列化格式。 |
| FE-02 | P1 | 跨层契约不一致 | QuestionEditor 的 practice 验证是自由文本框，不提示多选答案格式；practice scorer 对 list 按逗号拆分且精确比较，re-answer scorer 规范化规则不同。主 Agent提供 probe：practice 对 `"A C"`、`"a,c"` 均 false，re-answer 对两者均 correct；practice 错答会自动创建 MistakeDraft。源码：`src/app/manage/(workspace)/questions/components/question-editor.tsx:125-153`、`backend/app/services/attempt_service.py:23-44`；输出：`evidence/probe-learning.txt`。 | 合法答案可能被当作错答，污染错答草稿和 KP attempt/wrong 指标。领域合同确定后，应让两个输入界面与 scorer 采用相同的题型语义、分隔符和规范化规则。 |
| FE-03 | P2 / 范围外 UX 债务 | 源码确认 | 今日练习的“打开题目”链接到 `/manage/questions/{id}`，页面主体为“编辑正式题目”，含正确答案编辑字段，随后才是“作答验证”。作答验证调用 `submitAttempt`，因此 PR-13 并非没有 Practice Attempt 路径；但练习意图落到编辑表单。源码：`src/app/manage/(workspace)/practice/practice-today.tsx:73-87`、`src/app/manage/(workspace)/questions/components/question-editor.tsx:64-70,113-153`。 | 用户可能误入编辑模式或看到答案字段。专用练习会话属于后续 UX work item，不倒算为 PR-13 验收失败。 |
| FE-04 | P2 | 源码确认 | QuestionEditor 以 `Promise.all(getQuestion, listSubjects)` 加载；任一失败会写入 `error`，但未加载前始终只显示普通 `<p>`；无 `role=status/alert` 或 retry 控件。源码：`src/app/manage/(workspace)/questions/components/question-editor.tsx:25-33,61`。 | 错误对辅助技术不明确，用户需刷新或离开后重进。建议复用 AsyncStatePanel 或明确的加载/错误组件并提供重试。 |
| FE-05 | P2 / 需设备复核 | 截图观察 | `evidence/review-mobile.png` 的 390×844 review 视口里，全局底部移动导航覆盖 review 卡片的再答区域。源码 `src/components/mobile-nav.tsx:47-82` 固定在 `bottom-0`；workspace shell `src/app/manage/(workspace)/layout.tsx:11-18` 未见相应的小屏底部滚动留白。截图不足以证明最后控件不可达，但首屏操作区域确有遮挡。 | 用真实手机纵向滚动验证遮挡和末尾可达性，再决定给主内容预留 nav 高度和 safe-area；单张截图不构成整体移动端 FAIL/PASS。 |

## API、状态和移动端

核心学习 API 使用类型化 client 与 session credentials；未见 Dashboard、Practice、Review 页面重复拼接 API URL。Dashboard 和 Practice 的状态反馈较完整，Practice fallback `stable_order_fallback` 仍会原样显示英文 key（`src/app/manage/(workspace)/practice/practice-today.tsx:10-18`），是低优先级文案债务。PR-12 Note↔KP API 当前没有主线页面消费者，属于原计划范围外的后续整合，不作为本前端验收失败。

管理抽屉的焦点控制与站点级全局底部 nav 是两套独立组件。当前手机截图只观察到全局 nav 覆盖 review 内容；没有运行键盘/读屏器或其他小屏场景，不能据此宣称 WCAG、safe-area 或完整响应式验证通过。

## 验证状态

- **主 Agent提供，PASS：** Vitest 70 files / 522 tests、两套 TypeScript 检查、Node 24 build、Playwright Chromium 5/5。证据：`evidence/frontend-test.txt`、`evidence/typecheck.txt`、`evidence/test-typecheck.txt`、`evidence/build.txt`、`evidence/e2e.txt`。
- **主 Agent提供的定向运行观察：** Review 多选交互 probe 与 390px review 截图，以及 practice/re-answer scorer probe。它们发现 FE-01/FE-02，属于缺陷证据，不是通过证据。
- **本专项未运行：** 未执行测试、数据库或浏览器操作；未验证生产配置、跨浏览器、屏幕阅读器、WCAG 自动化、键盘逐页或真实手机全流程。

## 建议次序

1. 统一多选题输入 UI 与 practice/re-answer 评分合同，补覆盖同一 multiple-choice 题的浏览器作答和持久化读回。
2. 保留 PR-13 的候选选择验收范围；若产品要求“开始练习”专用体验，另建不暴露编辑字段的答题页面与 UX 任务。
3. 为 QuestionEditor 提供可访问且可重试的加载失败状态，并把 `stable_order_fallback` 映射为中文说明。
4. 用真实手机验证底部导航遮挡和卡片末尾可达性后，再决定需要的底部留白与 safe-area 调整。

**剩余风险：** 当前 E2E 未覆盖今日练习→Attempt→MistakeDraft 端到端交互，Dashboard KPI 未逐项和后端数据追溯；多选题输入和评分不一致会影响学习数据质量。此专项未修改代码，也不作主 Agent最终 Week Gate 接受裁定。
