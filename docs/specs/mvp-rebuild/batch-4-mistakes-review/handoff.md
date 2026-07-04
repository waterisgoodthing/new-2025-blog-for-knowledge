# Handoff

## 本批完成内容

- 建立“Question/QuestionDraft → MistakeDraft → 人工确认 → Mistake + ReviewItem →
  ReviewRecord”的最小私有闭环。
- 新 Mistake/Review 与旧公开 `Note(type="mistake")` 并存；本批不迁移、不回填、不双写、
  不切换公开读取事实源。
- `/manage/mistakes` 支持从正式 Question 创建错题草稿、查看 pending 草稿和 active 私有错题。
- `/manage/mistakes/[id]?kind=draft|mistake` 支持草稿保存/拒绝/确认、正式错题保存/归档。
- `/manage/review` 支持 due queue、0..5 固定评分提交和 ReviewRecord 查看。
- 公开 `/mistakes` 只在管理员态加载旧 review stats/plan 与 weak-points，未登录不再触发这些
  管理接口；旧 `/mistakes/review` 已补 AuthGate。

## 修改文件

- workflow：`docs/workflows/mvp-rebuild-batch-4-mistakes-review/`
- spec：`docs/specs/mvp-rebuild/batch-4-mistakes-review/`
- migration/model/router/service/schema/API client：
  - `backend/alembic/versions/013_add_mistakes_and_review.py`
  - `backend/app/models/mistake.py`
  - `backend/app/models/review_item.py`
  - `backend/app/routers/mistake_drafts.py`
  - `backend/app/routers/admin_mistakes.py`
  - `backend/app/routers/review_items.py`
  - `backend/app/services/mistake_service.py`
  - `backend/app/services/review_item_service.py`
  - `backend/app/schemas/mistake.py`
  - `backend/app/schemas/review_item.py`
  - `src/lib/api/mistakes.ts`
  - `src/lib/api/review-items.ts`
- 页面与 hooks：
  - `src/app/manage/(workspace)/mistakes/`
  - `src/app/manage/(workspace)/review/`
  - `src/app/mistakes/page.tsx`
  - `src/app/mistakes/review/page.tsx`
  - `src/hooks/use-note-index.ts`
  - `src/hooks/use-knowledge.ts`
  - `src/app/mistakes/components/weak-point-diagnosis.tsx`
  - `src/app/mistakes/components/weak-points-panel.tsx`
- 测试：
  - `backend/tests/test_mistake_review_service.py`
  - `backend/tests/test_mistake_routes.py`

## 未完成事项

- 真实浏览器完整闭环、移动视口、登录态操作和刷新持久化仍需用户验收或稳定浏览器会话补证。
- 不包含 BKT、mastery、复杂容量、完整练习、自动判错、题库抽题检测、附件、AI/OCR、批审。
- 不包含旧 `Note(type="mistake")` 向新 Mistake 的迁移，也不包含公开错题切流。

## 风险点

- 旧公开错题仍由 Note 承载，新私有 Mistake 暂不公开；后续若切流必须单独规划迁移/兼容。
- Review 第一版只用固定间隔 `fixed_interval_v1` 与 `review_items.next_review_at`，不得声称已具备
  BKT 或完整学习调度能力。
- 当前仓库工作树含其他批次/任务 dirty diff；继续 Batch 5 前应先确认 Batch 4 相关 diff 与
  外部变更边界。

## 下一批前置条件

- 用户验收 Batch 4。
- 如需浏览器证据，补跑登录态 `/manage/mistakes`、`/manage/review`、匿名 `/mistakes`、
  移动视口与 console/network。
- 用户明确批准进入 Batch 5。

## 用户确认

- [x] 用户已确认可以进入下一批（2026-07-03：Batch 4 可以关闭，进入 Batch 5 workflow 准备阶段）
