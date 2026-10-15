# 设计文档：Batch 4 错题与简单复习

## 1. 架构决定

采用“新私有 Mistake/Review + 旧公开 Note 原样共存”：

```text
Question / QuestionDraft
  → MistakeDraft(pending)
  → 人工编辑 / 拒绝
  → confirm(version)
  → Mistake(active, private) + ReviewItem(active)
  → rating(0..5)
  → ReviewRecord(immutable) + ReviewItem.next_review_at
```

旧 `/mistakes`、`/notes/[slug]` 与 `/api/notes` 继续只读旧 Note。本批不把新 Mistake
公开，也不建立双写或历史回填。

## 2. 数据设计

### 扩展 `draft_items`

013 安全替换已知 check constraints：

- `draft_type IN ('question','mistake')`
- `source_type IN ('manual','question','question_draft')`
- converted target_type 与 draft_type 对应。

保留现有 Question 草稿数据与约束语义，不改表数据。

### `mistake_drafts`

- UUID id、唯一 draft_item_id
- question_id / question_draft_id：恰好一个非空
- subject_id
- title、question_text snapshot
- my_answer、correct_answer_snapshot、explanation_snapshot
- reason_category：`concept | calculation | reading | careless | unknown`
- mistake_reason、difficulty
- created_at、updated_at

KnowledgePoint 通过 `knowledge_point_links(target_type=mistake_draft)`。

### `mistakes`

- UUID id、唯一 source_draft_item_id
- 非空 question_id；若来源是 QuestionDraft，确认前必须先已有 converted Question，
  否则返回 conflict，不在本批隐式转换 QuestionDraft
- subject_id、题目与答案/解析/错因快照
- status：`active | archived`
- visibility：固定 `private`
- version、created_at、updated_at

KnowledgePoint target_type=`mistake`。

### `review_items`

- UUID id
- target_type 固定 `mistake`、target_id Mistake UUID 字符串
- state：`active | paused`
- algorithm 固定 `fixed_interval_v1`
- interval_days、repetitions
- next_review_at、last_reviewed_at、created_at、updated_at
- 唯一 `(target_type,target_id)`

### `review_records`

- UUID id、review_item_id
- rating 0..5、reviewed_at
- previous_interval_days、next_interval_days
- previous_next_review_at、next_review_at
- created_at

记录无 update/delete service 或 API。

## 3. 事务与幂等

### Mistake conversion

锁 DraftItem；converted 直接返回既有 Mistake/ReviewItem；校验 version、来源、taxonomy；
创建 Mistake、manual knowledge links、ReviewItem；更新 converted target。唯一
source_draft_item 和 review target 作为数据库兜底。

### Review submit

锁 ReviewItem；要求 active 且 `next_review_at <= now`；计算固定间隔；创建 Record；
更新 Item。为避免双击重复，提交请求带 `expected_next_review_at`，不匹配返回 409。

## 4. API

全部 `/api/admin/**` 且依赖 `get_current_admin`：

- `GET/POST /api/admin/mistake-drafts`
- `GET/PUT /api/admin/mistake-drafts/{id}`
- `POST /api/admin/mistake-drafts/{id}/reject`
- `POST /api/admin/mistake-drafts/{id}/convert`
- `GET /api/admin/mistakes`
- `GET/PUT/DELETE /api/admin/mistakes/{id}`（DELETE=archive）
- `GET /api/admin/review/items?due=true`
- `GET /api/admin/review/items/{id}/records`
- `POST /api/admin/review/items/{id}/submit`

不新增 public API，不修改旧 `/api/notes`。

## 5. 页面

- `/manage/mistakes`：MistakeDraft 创建入口、待审核与正式错题分区。
- `/manage/mistakes/[id]`：依据资源类型展示草稿审核或正式错题编辑；若路由歧义影响
  合同，则使用 `?kind=draft|mistake` 并在客户端保持显式。
- `/manage/review`：今日到期列表、错题快照、0..5 评分与提交结果。
- 不修改 `/mistakes` 与 `/notes/[slug]` 的业务 UI；只做回归。
- 公开 `/mistakes` 使用现有 `useAdminAuth` 判断管理员状态；仅管理员加载旧 review
  stats/plan 与 WeakPointDiagnosis，未登录时不发起这些 admin 请求。公开错题列表本身
  始终加载，不加 AuthGate。

## 6. 迁移与恢复

- 新增 013，只扩 DraftItem constraints 并创建 4 张新表。
- 执行前 inspect 012/current、目标表和真实 Note/Question/Draft 基线并备份。
- 目标表提前存在或约束名称漂移时停止，不 stamp、不 drop/recreate 有数据表。
- 验证 012→013、重复 upgrade、约束/index/FK、旧数据计数与公开页面。

## 7. 权限与异常

- 新 Mistake、MistakeDraft、ReviewItem/Record 全部默认私有。
- 未登录新 API 统一 401；不存在 404；version/state/幂等冲突 409；业务校验 400。
- `/manage/**` 继续使用 workspace AuthGate。
- 公开页面不得新增对本批 admin API 的探测请求。
- 同时清除当前已知的未登录 review/weak-points 重复 403：只做登录态条件加载，
  不重构公开错题页面布局或旧编辑器。

## 8. 暂缓

旧 Note 迁移、公开切流、完整练习、自动判错、BKT/mastery、复杂容量、抽题检测、
附件、AI/OCR、批审和错题编辑器全面重构。
