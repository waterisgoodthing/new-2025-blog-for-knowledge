# 任务清单：Batch 3 题目草稿 / 审核 / 题库

> 状态：用户已批准，按 P0-01 至 P0-08 顺序执行。

## P0-01 建立 TDD、迁移与真实数据门禁

- [x] 为草稿 schema、状态转换和幂等 conversion 建立失败测试并记录 RED。
- [x] 盘点 Alembic current/head、目标表冲突、旧 Note 与历史真实表基线，并创建仓库外备份。
- 来源需求：REQ-B3-01、REQ-B3-02、REQ-B3-04、REQ-B3-07
- 涉及文件：
  - `backend/tests/test_question_draft_service.py`
  - `docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/validation.md`
- 修改内容：先写 manual draft、version conflict、conversion idempotency 与拒绝行为测试；
  migration 前只读 inspect，不使用 `create_all`、stamp 或手工版本修改。
- 完成标准：测试因功能未实现而 RED；数据库前置状态、备份和恢复路径明确。
- 验证方式：定向 pytest、Alembic current/history/heads、schema 与数据计数。
- 风险说明：发现目标表提前存在或 current 漂移时必须停止并申请范围扩大。

## P0-02 新增独立模型与 Alembic 012

- [x] 新增 DraftItem、QuestionDraft、Question、QuestionSource 与约束/索引。
- 来源需求：REQ-B3-01、REQ-B3-02、REQ-B3-04、REQ-B3-05
- 涉及文件：
  - `backend/app/models/question.py`
  - `backend/app/models/__init__.py`
  - `backend/alembic/env.py`
  - `backend/alembic/versions/012_add_question_drafts_and_questions.py`
- 修改内容：创建 4 张新表；复用 Subject 与 knowledge_point_links；不触碰 Note。
- 完成标准：011 正常升级到 012；模型/schema 一致；重复 upgrade 无破坏。
- 验证方式：Alembic upgrade/current、SQLAlchemy metadata、schema/constraint/index inspection。
- 风险说明：不回填旧 Note、不 drop/recreate、不由 lifespan create_all 代替 migration。

## P0-03 实现 schemas 与 service 业务规则

- [x] 完成 manual draft、编辑、拒绝、幂等转换和正式 Question 更新/归档。
- 来源需求：REQ-B3-02、REQ-B3-03、REQ-B3-04、REQ-B3-05
- 涉及文件：
  - `backend/app/schemas/question.py`
  - `backend/app/services/question_service.py`
  - `backend/app/services/draft_service.py`
  - `backend/tests/test_question_draft_service.py`
- 修改内容：按 RED→GREEN 实现字段合同、题型/options 校验、taxonomy 一致性、version、
  行锁、唯一来源、知识点 link 复制和软归档。
- 完成标准：重复 conversion 返回同一 Question；事务失败不留半成品；状态机测试通过。
- 验证方式：定向 pytest、数据库事务/行数/映射断言。
- 风险说明：service 不依赖 FastAPI；不得新增直接 Question create 路径。

## P0-04 实现 thin admin routers 与权限

- [x] 注册 drafts/questions admin API，并映射稳定 HTTP 错误。
- 来源需求：REQ-B3-02、REQ-B3-03、REQ-B3-04、REQ-B3-05、REQ-B3-07
- 涉及文件：
  - `backend/app/routers/drafts.py`
  - `backend/app/routers/questions.py`
  - `backend/main.py`
  - 必要的定向 API 测试
- 修改内容：router 只做输入输出、dependency 和异常映射；所有端点统一
  `get_current_admin`；无 public Question API。
- 完成标准：合同与 design 一致；未登录全部 401；错误码 400/404/409/422 可复现。
- 验证方式：FastAPI import、OpenAPI 路由检查、匿名与管理员 HTTP 测试。
- 风险说明：不得复用 `/api/notes` 或开放未鉴权列表。

## P0-05 实现显式前端客户端

- [x] 新增 drafts/questions DTO 与 API client，复用 taxonomy 正式 ID。
- 来源需求：REQ-B3-02、REQ-B3-03、REQ-B3-04、REQ-B3-05、REQ-B3-06
- 涉及文件：
  - `src/lib/api/drafts.ts`
  - `src/lib/api/questions.ts`
  - `src/app/manage/components/knowledge-point-select.tsx`（仅必要的多选扩展）
- 修改内容：显式定义 list/detail/create/update/convert/reject/archive 合同；无 `any`。
- 完成标准：前端字段、枚举、version 和后端 schema 对齐；不建立第二数据源。
- 验证方式：TypeScript、合同抽查、真实 API。
- 风险说明：不得重构 Batch 2 无关 taxonomy UI。

## P0-06 实现草稿与题库管理页面

- [x] 将两个占位页升级为真实列表，并新增草稿/题目详情页。
- 来源需求：REQ-B3-02、REQ-B3-03、REQ-B3-04、REQ-B3-05、REQ-B3-06
- 涉及文件：
  - `src/app/manage/(workspace)/drafts/page.tsx`
  - `src/app/manage/(workspace)/drafts/[id]/page.tsx`
  - `src/app/manage/(workspace)/drafts/components/*`
  - `src/app/manage/(workspace)/questions/page.tsx`
  - `src/app/manage/(workspace)/questions/[id]/page.tsx`
  - `src/app/manage/(workspace)/questions/components/*`
- 修改内容：创建、列表、筛选、详情编辑、拒绝、确认转换、正式题目编辑与归档；
  完整 loading/empty/error/conflict 状态。
- 完成标准：管理员可在桌面与移动端完成完整手工闭环；converted 可跳转唯一 Question。
- 验证方式：真实浏览器主流程、重复转换、冲突、刷新持久化、移动视口和 console/network。
- 风险说明：不修改 workspace shell、首页、旧 `/manage` 或公开页面。

## P0-07 回归迁移、权限、兼容与数据清理

- [x] 验证迁移、旧 Note、taxonomy、公开页面、匿名拒绝和临时数据清理。
- 来源需求：REQ-B3-01、REQ-B3-04、REQ-B3-07
- 涉及文件：原则上只验证；只修复 P0-02 至 P0-06 的本批缺陷。
- 修改内容：验证 current 012、重复 upgrade、历史数据计数、旧 `/api/notes`、公开页面、
  `/manage/page.tsx` 零 diff、无 Question public API；清理验收数据并禁用临时管理员。
- 完成标准：新闭环不改变旧系统事实源；没有测试数据或临时权限残留。
- 验证方式：pytest、HTTP、数据库查询、TSC、build、浏览器、git diff。
- 风险说明：旧 `/mistakes` 已知 admin API 403 噪音只记录，不跨批修复。

## P0-08 审查、验证与移交

- [x] 创建 `audit.md` 并完成 `validation.md`。
- [x] 更新 Batch 3 `checklist.md`。
- [x] 填写 Batch 3 `handoff.md`，但不代替用户确认。
- [x] 核对 Git diff 只包含本批批准范围。
- 来源需求：全部
- 涉及文件：
  - `docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/audit.md`
  - `docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/validation.md`
  - `docs/specs/mvp-rebuild/batch-3-drafts-question-bank/checklist.md`
  - `docs/specs/mvp-rebuild/batch-3-drafts-question-bank/handoff.md`
- 修改内容：记录架构决定、迁移、状态机、转换幂等、权限、浏览器、失败、风险与 Batch 4
  前置条件。
- 完成标准：Batch 3 进入等待用户验收，不自动进入 Batch 4。
- 验证方式：全套本批证据、`git diff --check`、范围审查。
- 风险说明：任何重复转换、半成品数据、权限泄露或旧 Note 回归都阻塞 Batch 4。

## 执行顺序

严格按 P0-01 → P0-02 → P0-03 → P0-04 → P0-05 → P0-06 → P0-07 → P0-08。
每完成一项立即更新本文件，不得最后批量回填。

## 审批记录

- [x] 用户已于 2026-07-03 明确批准执行 Batch 3 tasks。
