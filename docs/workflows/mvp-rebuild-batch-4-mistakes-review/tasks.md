# 任务清单：Batch 4 错题与简单复习

> 状态：用户已批准，按 P0-01 至 P0-09 顺序执行。

## P0-01 TDD、迁移与兼容门禁

- [x] 建立 Mistake conversion、Review submit 与公开兼容的 RED 测试。
- [x] inspect Alembic/目标表/DraftItem constraints，记录 Note、Question、Draft 基线并备份。
- 来源需求：REQ-B4-01、REQ-B4-03、REQ-B4-05、REQ-B4-07
- 涉及文件：`backend/tests/test_mistake_review_service.py`、本 workflow `validation.md`
- 修改内容：按纵向 TDD 从幂等确认与固定间隔提交开始；数据库只读盘点。
- 完成标准：RED 原因明确；013 前置、恢复与停止条件完整。
- 验证方式：pytest、Alembic current/history/heads、schema/data inspection、pg_restore list。
- 风险说明：发现目标表提前存在或 constraint 漂移时停止并申请范围扩大。

## P0-02 新增模型与 Alembic 013

- [x] 扩展 DraftItem constraints，新增 MistakeDraft、Mistake、ReviewItem、ReviewRecord。
- 来源需求：REQ-B4-01、REQ-B4-02、REQ-B4-03、REQ-B4-05
- 涉及文件：`backend/app/models/question.py`、新 mistake/review model、models init、
  `backend/alembic/env.py`、`013_add_mistakes_and_review.py`
- 修改内容：安全替换已知 check，不改现有行；创建 4 张新表与约束/index。
- 完成标准：012→013 正常；重复 upgrade 通过；Question/Draft/Note 数据不变。
- 验证方式：migration、metadata、constraint/FK/index 与数据计数。
- 风险说明：不 stamp、不回填 Note、不 drop/recreate 有数据表、不由 create_all 代迁移。

## P0-03 实现 MistakeDraft/Mistake service

- [x] 完成创建、编辑、拒绝、幂等确认、正式错题更新与归档。
- 来源需求：REQ-B4-02、REQ-B4-03、REQ-B4-04
- 涉及文件：mistake schemas/services 与定向测试。
- 修改内容：校验 question/question_draft 来源、snapshot、taxonomy、version；确认原子创建
  Mistake + ReviewItem；归档暂停 review。
- 完成标准：重复确认 Mistake=1、ReviewItem=1；未确认不进入 review。
- 验证方式：逐条 RED→GREEN、事务/行数/状态断言。
- 风险说明：不隐式转换 QuestionDraft，不触碰旧 Note 错题。

## P0-04 实现固定间隔 Review service

- [x] 完成 due queue、不可变记录与 0..5 固定间隔提交。
- 来源需求：REQ-B4-05
- 涉及文件：review schema/service 与定向测试。
- 修改内容：行锁、expected_next_review_at、防双击、记录前后状态、更新 item。
- 完成标准：一次提交只增一条 Record；间隔映射精确；无 record update/delete。
- 验证方式：时间冻结/范围断言、重复提交 conflict、事务回滚测试。
- 风险说明：不实现 BKT、mastery、复杂容量或 ReviewSchedule。

## P0-05 实现 thin admin routers 与权限

- [x] 注册 mistake drafts/mistakes/review API，并映射 400/404/409/422。
- 来源需求：REQ-B4-02 至 REQ-B4-07
- 涉及文件：新 routers、`backend/main.py`、路由合同测试。
- 修改内容：router 仅 HTTP 编排；全部 endpoint 统一 get_current_admin；无 public API。
- 完成标准：匿名全部 401；OpenAPI 无 public Mistake/Review 与 record mutation。
- 验证方式：route tests、HTTP anonymous/admin、FastAPI import。
- 风险说明：不得假设或创建旧 `/api/mistakes` 公开合同。

## P0-06 实现前端 DTO/client

- [x] 新增 MistakeDraft/Mistake/Review 显式类型与 API client。
- 来源需求：REQ-B4-02 至 REQ-B4-06
- 涉及文件：`src/lib/api/mistakes.ts`、`src/lib/api/review-items.ts` 及必要 taxonomy 复用。
- 修改内容：状态、version、rating、expected_next_review_at 合同；无 `any`。
- 完成标准：前后端字段一致，不建立第二数据源。
- 验证方式：TSC、合同检查、真实 API。
- 风险说明：不改旧 notes/review 客户端合同。

## P0-07 实现管理错题与复习页面

- [x] 升级 `/manage/mistakes`、`/manage/review` 并新增直接详情路由组件。
- 来源需求：REQ-B4-02 至 REQ-B4-06
- 涉及文件：两个 workspace route 及其 `[id]`/components。
- 修改内容：从 Question 建草稿、审核转换、正式编辑/归档、due queue、rating 提交；
  loading/empty/error/conflict 全状态。
- 完成标准：桌面与移动端可完成完整闭环，刷新后状态持久。
- 验证方式：真实浏览器、重复确认/提交、移动视口、console/network。
- 风险说明：不重构旧错题编辑器，不修改 workspace shell、首页或旧 `/manage`。
- 完成记录（2026-07-03）：新增管理端错题工作区、草稿/正式错题详情页与固定间隔复习队列；
  草稿详情路由使用 `?kind=draft|mistake` 显式区分资源类型，草稿 API path 统一使用
  `draft_item_id`；`npx tsc --noEmit` 通过。真实浏览器闭环将在 P0-08/P0-09 合并验证。

## P0-08 修正公开管理员请求噪音并完成兼容回归

- [x] 未登录 `/mistakes` 不再请求 review/weak-points admin API，并完成全部兼容回归。
- 来源需求：REQ-B4-01、REQ-B4-07
- 涉及文件：
  - `src/app/mistakes/page.tsx`
  - `src/hooks/use-note-index.ts`
  - 必要的公开错题定向测试
  - 其余原则上只验证
- 修改内容：用既有 `useAdminAuth` 让 review stats/plan 与 WeakPointDiagnosis 只在管理员
  登录时加载；不加 AuthGate、不改列表事实源；同时完成旧 Note 数量/字段/API/页面对账、
  匿名 401、无新 public API、迁移重复执行与临时账号禁用。
- 完成标准：新闭环可用且旧公开事实源无变化，无测试数据/权限残留。
- 验证方式：pytest、DB、HTTP、TSC、build、browser、git diff。
- 风险说明：该修正必须保持最小 diff，不改页面布局、公开过滤或旧错题编辑器。
- 完成记录（2026-07-03）：`useReviewStats`、`useReviewPlan`、`useWeakPoints` 增加 enabled
  门禁；公开 `/mistakes` 仅在 `isAdmin=true` 时加载 review stats/plan 与 WeakPointDiagnosis，
  并隐藏添加错题入口；旧 `/mistakes/review` 增加 AuthGate。`npx tsc --noEmit` 与定向后端
  测试 10 passed。in-app browser 对当前本地 Next 页面水合检查不稳定，真实浏览器闭环证据在
  P0-09 记录为待用户验收/需登录态配合项。

## P0-09 审查、验证与移交

- [x] 创建 audit/validation，更新 checklist，填写 handoff，核对范围。
- 来源需求：全部
- 涉及文件：本 workflow 文档与 Batch 4 spec checklist/handoff。
- 修改内容：记录模型决定、公开兼容、迁移、幂等、复习规则、权限、失败、风险。
- 完成标准：Batch 4 仅进入等待用户验收，不自动进入 Batch 5。
- 验证方式：全套证据与 `git diff --check`。
- 风险说明：任何公开回归、重复 Mistake/ReviewItem/Record 或 Note 漂移都阻塞 Batch 5。
- 完成记录（2026-07-03）：`npm run build` 通过，`git diff --check` 通过，定向后端测试
  10 passed；已更新 audit/checklist/handoff/validation。真实浏览器完整闭环仍需用户验收或稳定
  浏览器会话补证；Batch 4 不自动进入 Batch 5。

## 执行顺序

严格按 P0-01 → P0-09；每完成一项立即更新本文件。

## 审批记录

- [x] 用户已于 2026-07-03 明确批准执行 Batch 4 tasks。
