# Batch 4 审查记录

## 审查结论

Batch 4 已完成代码与文档收口，状态为**等待用户验收**。本批建立了新私有
MistakeDraft/Mistake/ReviewItem/ReviewRecord 闭环，同时保留旧公开 `Note(type="mistake")`
事实源。

## 触及领域

- mistakes：新私有错题草稿与正式错题。
- review：新固定间隔复习队列与不可变记录。
- manage：`/manage/mistakes`、`/manage/mistakes/[id]`、`/manage/review`。
- public compatibility：公开 `/mistakes` 最小门禁修正，旧 `/mistakes/review` 增加 AuthGate。
- shared infrastructure：Alembic 013、API client、SWR hooks enabled 门禁。

## 主要证据

- 数据模型：013 新增 `mistake_drafts`、`mistakes`、`review_items`、`review_records`，并扩展
  DraftItem constraints；旧 notes 基线未迁移、未双写。
- 后端合同：新增 API 均在 `/api/admin/**`，依赖 `get_current_admin`；未新增公开
  `/api/mistakes` 或 `/api/review/items`。
- 幂等与事务：重复确认只返回同一 Mistake/ReviewItem；复习提交使用
  `expected_next_review_at` 防双击。
- 前端：管理工作区继承 `/manage/(workspace)` AuthGate；公开 `/mistakes` 不加 AuthGate，
  只在管理员态加载 review stats/plan 与 weak-points。
- 验证：
  - `npx tsc --noEmit` 通过。
  - `npm run build` 通过。
  - `cd backend && .venv/bin/python -m pytest -q tests/test_mistake_review_service.py tests/test_mistake_routes.py tests/test_question_routes.py`
    通过，10 passed。
  - `git diff --check` 通过。

## 风险与未闭合验证

- in-app browser 对当前本地 `/mistakes` 的 DOM 水合检查不稳定，只返回 Next flight script，
  console 无 error/warn；因此真实浏览器完整闭环、移动视口、登录态操作仍应由用户验收或在
  稳定浏览器会话中补证。
- 当前工作树含大量非 Batch 4 dirty diff；本审查只覆盖 Batch 4 相关路径与已运行测试覆盖的
  Batch 3/B4 合同。
- 新管理错题页面第一版为最小闭环，不包含批审、AI/OCR、附件、BKT、完整练习或公开切流。

## 禁止项核对

- 未给公开 `/mistakes` 或 `/notes/[slug]` 加 AuthGate。
- 未新增公开新 Mistake API。
- 未假设旧错题有独立 `/api/mistakes` 合同。
- 未迁移、删除或回填旧 `Note(type="mistake")`。
- 未把错题编辑器大型重构混入本批。
