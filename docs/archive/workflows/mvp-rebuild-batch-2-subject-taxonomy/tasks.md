# 任务清单：Batch 2 科目 / 知识点基础

> 状态：等待用户明确批准。批准前不得修改模型、API、迁移、客户端或页面。

## P0-01 建立 TDD 基线与迁移门禁

- [x] 为 taxonomy service/schema 建立第一条失败测试，并记录 RED。
- [x] 审查 Alembic 006–010，确认本地 current 005 的升级与恢复路径。
- 来源需求：REQ-B2-01、REQ-B2-02、REQ-B2-03、REQ-B2-06
- 涉及文件：
  - `backend/tests/test_taxonomy_service.py`
  - `docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/validation.md`
- 修改内容：先写 Subject 更新/重复/删除冲突行为测试；记录迁移 current、head、pending
  migration 和恢复前置条件。
- 完成标准：测试因功能未实现而失败；006–010 无未解释风险；可恢复路径明确。
- 验证方式：定向 pytest、`PYTHONPATH=. alembic current/history/heads`。
- 风险说明：当前数据库落后 5 个迁移；失败时禁止 stamp 或跳过。

## P0-02 扩展模型与新增 011 迁移

- [x] 扩展 Subject，新增 Chapter、KnowledgePoint、KnowledgePointLink 与 migration；
  已按追加授权完成 006–010 数据保留型修复并执行 011。
- 来源需求：REQ-B2-01、REQ-B2-02、REQ-B2-03、REQ-B2-06
- 涉及文件：
  - `backend/app/models/note.py`
  - `backend/app/models/taxonomy.py`
  - `backend/app/models/__init__.py`
  - `backend/alembic/env.py`
  - `backend/alembic/versions/006_add_admin_sessions.py`
  - `backend/alembic/versions/007_change_folder_cascade.py`
  - `backend/alembic/versions/008_add_audit_logs.py`
  - `backend/alembic/versions/009_add_music_daily.py`
  - `backend/alembic/versions/010_add_managed_content_entries.py`
  - `backend/alembic/versions/011_add_subject_taxonomy.py`
- 修改内容：先将已被 `create_all` 提前创建的 006/008/009/010 改为数据保留型可重放
  迁移，执行 007 FK 修正并升级到 010；再增加 MVP 字段、FK、唯一约束和 011。
- 完成标准：模型与数据库一致；迁移可重复检查；不存在平行 subjects 表。
- 验证方式：migration upgrade、schema inspection、定向模型测试。
- 风险说明：这是原批准范围外的历史迁移修复，必须获得用户追加批准；不得 stamp、
  删表、迁移 Note 自由文本或自动级联删除已有管理数据。

## P0-03 实现 thin routers、schemas 与 taxonomy service

- [x] 完成 Subject、Chapter、KnowledgePoint CRUD 与后端规则。
- 来源需求：REQ-B2-01、REQ-B2-02、REQ-B2-03
- 涉及文件：
  - `backend/app/schemas/taxonomy.py`
  - `backend/app/services/taxonomy_service.py`
  - `backend/app/routers/subjects.py`
  - `backend/app/routers/chapters.py`
  - `backend/app/routers/knowledge_points.py`
  - `backend/main.py`
  - `backend/tests/test_taxonomy_service.py`
- 修改内容：逐个 RED→GREEN 实现 CRUD、重复冲突、依赖删除和 chapter/subject 一致性；
  所有端点使用 `get_current_admin`。
- 完成标准：router 只做 HTTP 编排；service 测试通过；错误状态符合设计。
- 验证方式：定向 pytest、FastAPI import/start、临时管理员 HTTP 验收。
- 风险说明：不得新增 `/api/admin/subjects` 第二套合同；不得开放未鉴权 GET。

## P0-04 实现前端类型客户端与选择器基础

- [x] 新增 taxonomy 类型、CRUD 客户端和 knowledge point option adapter。
- 来源需求：REQ-B2-05、REQ-B2-07
- 涉及文件：
  - `src/lib/api/taxonomy.ts`
  - `src/lib/api/meta.ts`
  - `src/app/manage/components/knowledge-point-select.tsx`
  - 必要的前端定向测试文件（若仓库无测试基建则在 validation 记录替代验证）
- 修改内容：显式定义所有 DTO；保持旧 `listSubjects()` 调用兼容；选择器只读正式 active
  knowledge points。
- 完成标准：无 `any`；Batch 3 可复用稳定 ID/label；无第二数据源。
- 验证方式：TypeScript、客户端合同检查、真实 API 选项验证。
- 风险说明：组件暂放 manage route；无跨路由复用证据前不提升到 `src/components/`。

## P0-05 实现 Subject 与 KnowledgePoint 管理页面

- [x] 将 Batch 1 占位升级为真实管理页面与详情页。
- 来源需求：REQ-B2-04
- 涉及文件：
  - `src/app/manage/(workspace)/subjects/page.tsx`
  - `src/app/manage/(workspace)/subjects/[id]/page.tsx`
  - `src/app/manage/(workspace)/knowledge-points/[id]/page.tsx`
  - `src/app/manage/(workspace)/subjects/` 下必要 route-specific components/hooks/services
- 修改内容：实现列表、详情、表单、空/加载/错误、删除确认和依赖冲突显示。
- 完成标准：管理员可真实完成三类 CRUD；移动与桌面无溢出；不显示后置能力。
- 验证方式：真实浏览器 CRUD、控制台、桌面/移动截图与数据清理。
- 风险说明：不修改 Batch 1 壳层、首页、旧 `/manage` 或公开页面。

## P0-06 回归权限、兼容与迁移

- [x] 验证未登录拒绝、旧 Subject 调用、Note 字符串字段和公开页面。
- 来源需求：REQ-B2-06、REQ-B2-07
- 涉及文件：原则上只验证；若发现本批问题，只修正 P0-02 至 P0-05 范围。
- 修改内容：验证 401/403、旧编辑器 Subject 列表、公开笔记/错题、migration current。
- 完成标准：安全边界、旧合同和公开读取无回归，测试数据已清理。
- 验证方式：HTTP、浏览器、数据库查询、migration current。
- 风险说明：不得使用 AUTH_BYPASS；临时管理员验收后必须禁用。

## P0-07 审查、验证与移交

- [x] 创建 `audit.md` 与完成 `validation.md`。
- [x] 更新 Batch 2 `checklist.md`。
- [x] 填写 Batch 2 `handoff.md`，但不代替用户确认。
- [x] 核对 Git diff 只包含本批批准范围。
- 来源需求：全部
- 涉及文件：
  - `docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/audit.md`
  - `docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/validation.md`
  - `docs/specs/mvp-rebuild/batch-2-subject-taxonomy/checklist.md`
  - `docs/specs/mvp-rebuild/batch-2-subject-taxonomy/handoff.md`
- 修改内容：记录测试、迁移、合同、权限、浏览器、失败、剩余风险和 Batch 3 前置条件。
- 完成标准：Batch 2 进入待用户验收，不自动进入 Batch 3。
- 验证方式：pytest、migration、HTTP、`npx tsc --noEmit`、`npm run build`、浏览器、
  `git diff --check`。
- 风险说明：任何迁移、合同或数据清理缺口都阻塞 Batch 3。

## 执行顺序

严格按 P0-01 → P0-02 → P0-03 → P0-04 → P0-05 → P0-06 → P0-07 执行。
每完成一项立即更新本文件，不得最后批量回填。

## 审批记录

- [x] 用户已于 2026-07-02 明确批准执行本任务清单。
- [x] 用户已于 2026-07-03 追加批准数据保留型修复 006–010；禁止 stamp、删表、
  丢数据、跳过 007 或以 `create_all` 代替迁移。
