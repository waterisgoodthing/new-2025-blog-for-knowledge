# Batch 4 验证记录

## 当前状态

执行中；中间证据不代表 Batch 4 已验收。

## P0-01 TDD、迁移与兼容门禁

- 用户于 2026-07-03 明确批准 Batch 4 tasks。
- RED：`ModuleNotFoundError: No module named 'app.schemas.mistake'`，与尚未实现一致。
- Alembic current/heads：`012 (head)`。
- 4 张目标表均不存在，无 create_all 提前建表。
- DraftItem constraints 已按真实数据库确认：
  `ck_draft_items_type/source/status/version/conversion_target`，名称与 012 一致。
- 数据基线：
  - notes=13（blog=1、mistake=5、note=7）
  - draft_items/question_drafts/questions/question_sources=0
  - knowledge_point_links=0
- 仓库外备份 `/tmp/blog-db-pre-batch4.dump`，mode 600，`pg_restore --list` 通过。

## P0-02 模型与 013

- DraftItem type/source/conversion check 已安全扩展，未改写现有行。
- 新增 mistake_drafts、mistakes、review_items、review_records。
- `012 -> 013` 正常；current=`013 (head)`；重复 upgrade 通过。
- schema inspection：MistakeDraft 15列/4FK/3check，Mistake 17列/3FK/3check，
  ReviewItem 11列/4check，ReviewRecord 9列/1FK/2check。
- 旧 notes 仍为 13。

## P0-03 MistakeDraft/Mistake service

- 完成 Question/QuestionDraft 来源校验、snapshot、taxonomy link、version conflict、
  拒绝、幂等确认、正式错题更新与归档。
- 确认在同一事务中仅创建 1 个 Mistake 与 1 个 ReviewItem；重复确认返回原记录。
- 未确认 MistakeDraft 不创建 Mistake，也不进入复习队列。
- 正式 Mistake 固定为 private；归档时 ReviewItem 同步 paused。
- 定向验证：`5 passed`；与 Batch 3 service 合并回归：`12 passed`。

## P0-04 固定间隔 Review service

- due queue 仅返回 active 且到期的 ReviewItem。
- submit 使用行锁与 `expected_next_review_at` 乐观并发门禁；陈旧重复提交返回 conflict。
- rating 0/1/2/3/4/5 已逐项验证为 1/1/1/3/7/14 天。
- 每次提交只新增不可变 ReviewRecord，并记录更新前后 interval/next_review_at。
- 定向验证：`5 passed`（同一用例覆盖全部 6 个 rating 与 stale submit）。

## P0-05 私有 admin routers

- 已注册 mistake-drafts、mistakes、review items/records/submit 合同，router 保持 HTTP 编排。
- 所有新增路由统一依赖 `get_current_admin`；三个列表入口匿名请求均实测为 401。
- OpenAPI/route 集合确认不存在 `/api/mistakes` 或 `/api/review/items` 新公开合同，
  不存在 ReviewRecord update/delete。
- domain error 映射：not found=404、conflict=409、validation=400；Pydantic 请求错误=422。
- 路由、权限与 service 合并定向验证：`10 passed`；FastAPI import 成功，155 routes。

## P0-06 前端 DTO/client

- 新增显式 MistakeDraft/Mistake/ReviewItem/ReviewRecord DTO；未使用 `any`。
- client 覆盖草稿创建/更新/拒绝/确认、正式错题读取/更新/归档、due queue/records/submit。
- rating 类型固定为 0..5，submit 显式发送 `expected_next_review_at`。
- `npx tsc --noEmit`：通过，无 TypeScript 错误。

## P0-07 管理错题与复习页面

- `/manage/mistakes` 已替换占位页，支持从 active Question 创建 MistakeDraft，并展示 pending
  草稿与 active 私有错题列表。
- `/manage/mistakes/[id]?kind=draft|mistake` 已新增直接详情路由；草稿支持保存、拒绝、确认入错题，
  正式错题支持保存与归档。草稿 API path 统一使用 `draft_item_id`。
- `/manage/review` 已替换占位页，支持读取 due queue、0..5 评分提交、查看单项 ReviewRecord。
- `npx tsc --noEmit`：通过，无 TypeScript 错误。
- 待 P0-08/P0-09：真实浏览器闭环、移动视口、console/network 与刷新持久化证据。

## P0-08 公开页面管理员请求噪音与兼容

- `src/hooks/use-note-index.ts`：`useReviewStats(enabled)` 与 `useReviewPlan(enabled)` 使用
  `enabled ? key : null`，未启用时不发起 SWR 请求。
- `src/hooks/use-knowledge.ts`：`useWeakPoints(days, enabled)` 使用 `enabled ? key : null`。
- `src/app/mistakes/page.tsx`：公开错题列表继续使用旧 `useNoteIndex({ type: 'mistake' })`；
  review stats/plan、WeakPointDiagnosis、开始复习入口、添加错题入口均仅在 `isAdmin=true` 时显示/加载。
- `src/app/mistakes/review/page.tsx`：补充 `AuthGate`，保护旧 Note 复习页面。
- 静态搜索确认 `/mistakes` 的 review/weak-points SWR key 均受 `isAdmin`/`enabled` 门禁约束。
- `npx tsc --noEmit`：通过。
- `cd backend && .venv/bin/python -m pytest -q tests/test_mistake_review_service.py tests/test_mistake_routes.py tests/test_question_routes.py`：
  `10 passed in 0.68s`。
- 浏览器说明：本地 2025/8000 服务均在运行；in-app browser 访问 `/mistakes` 时 DOM 只返回
  Next flight script，`tab.dev.logs` 无 error/warn，无法形成可靠真实浏览器闭环证据。该项不作为
  已验证闭环，保留到 P0-09/用户验收。

## P0-09 审查、验证与移交

- `npm run build`：通过。非阻塞警告：
  - `baseline-browser-mapping` 数据超过两个月。
  - Node `[DEP0205] module.register()` deprecation warning。
- `git diff --check`：通过。
- `rg` 检查：
  - 未发现新增公开 `/api/mistakes` 或 `/api/review/items`。
  - `/manage/(workspace)` 继续由 AuthGate 包裹。
  - 公开 `/mistakes` 未加 AuthGate；管理员模块受 `isAdmin` 与 enabled SWR key 约束。
- 已更新：
  - `audit.md`
  - `docs/specs/mvp-rebuild/batch-4-mistakes-review/checklist.md`
  - `docs/specs/mvp-rebuild/batch-4-mistakes-review/handoff.md`
- Batch 4 当前状态：等待用户验收；不自动进入 Batch 5。
