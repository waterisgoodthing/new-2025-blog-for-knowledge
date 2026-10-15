# W3-00 盘点 A — legacy mistake 写入方 / 读取方全量清单

- agent: W3-00-inv-inventory（profile=senior-backend-engineer，role=consulted/read-only）
- 日期: 2026-09-22
- 方法: source grep + 文件级引用（`rg`/Read）。未执行数据库命令、未跑写库测试。
- 范围: 使 Note `type='mistake'` **产生或变更**的写入路径；所有读取 legacy `Note(type='mistake')` 的路径。
- 说明: "活跃"指当前 dirty worktree 中可被调用（路由已注册或 UI 可达）；不代表近期被人工使用过。

---

## 1. 写入方清单（Writers）

约定: **产生** = 创建 `type='mistake'` 行或把已有 Note 的 type 改成/已是 mistake 后再改字段；**变更** = 修改既有 mistake 行（含 SM-2 调度字段）与删除。

### W-01 `POST /api/notes` — note create（产生）

- 位置: `backend/app/routers/notes.py:238-304`（`create_note`）
- 关键行: `notes.py:262` `type=req.type.value`（`NoteCreate.type` 可为 `mistake`，`backend/app/schemas/note.py:29`）；`notes.py:282-285` 当 `req.type == NoteType.mistake` 时 `note.next_review = date.today()`
- 触发: admin 会话（`get_current_admin`，`notes.py:243`）POST body `type='mistake'`
- 状态: **活跃**
- 备注: 同时写 `create_initial_version` / `sync_wikilinks` / audit（`notes.py:289-302`）

### W-02 `PUT /api/notes/{slug}` — update-type / 字段变更（产生 + 变更）

- 位置: `backend/app/routers/notes.py:307-354`（`update_note`）
- 关键行: `backend/app/schemas/note.py:55` `type: NoteType | None = None`（允许改 type）；`notes.py:334-336` type 枚举转值后 `setattr(note, key, value)` —— 可把任意 Note 的 `type` 改成 `'mistake'`，也可改既有 mistake 行的 title/content/question/my_answer/correct_answer/analysis/knowledge_points 等
- 触发: admin PUT body 含 `type='mistake'`（改 type）或对 `type='mistake'` 行的任意字段更新
- 状态: **活跃**
- 备注: 带 `expected_revision` 乐观锁（`notes.py:322-324`）；也写 note version + wikilinks + audit

### W-03 `POST /api/notes/{slug}/promote` — promote（产生）

- 位置: `backend/app/routers/notes.py:431-451`（`promote_note`）
- 关键行: `notes.py:443` `note.type = new_type.value`（`new_type: NoteType`，可 `mistake`）；`notes.py:444-447` 当 `new_type == NoteType.mistake` 且 `next_review is None` 时置 `next_review = date.today()`
- 触发: admin POST `?new_type=mistake`
- 状态: **活跃**（后端路由已注册于 `backend/main.py` 经 `notes.router`）
- 备注: 前端仅有客户端封装 `src/lib/api/notes.ts:178-179`（`promoteNote`），**未发现 UI 调用方**；API 面仍然开放，属冻结目标

### W-04 `POST /api/review/{slug}` — legacy SM-2 复习提交（变更）

- 位置: `backend/app/routers/review.py:33-63`（`submit_review`）
- 关键行: `review.py:47-58` 用 `sm2()`（`backend/app/services/sm2.py:4-22`）改写 `note.ef / note.interval / note.repetitions / note.next_review / note.last_reviewed / note.updated_at`
- 触发: admin POST `/api/review/{slug}`（`quality`）；目标行须 `Note.type == 'mistake'`（`review.py:41`）
- 状态: **活跃**（前端 `src/app/mistakes/review/page.tsx:66` `submitReview(item.slug, quality)`；API 封装 `src/lib/api/review.ts:41`）
- 备注: 不产生新行，但**变更** legacy mistake 行的复习状态字段 —— PR-09「冻结写入」是否涵盖此类变更见 §6

### W-05 `DELETE /api/notes/{slug}` 与 `POST /api/notes/batch-delete` — 删除（变更/消灭）

- 位置: `backend/app/routers/notes.py:396-420`（`delete_note`）、`notes.py:423-428`（`batch_delete_notes`）
- 触发: admin 删除 slug（可含 `type='mistake'` 行；路由不按 type 过滤，`notes.py:404-405,425-426`）
- 状态: **活跃**
- 前端调用: `src/app/notes/page.tsx:163`、`src/app/notes/[id]/note-detail-content.tsx:130`、`src/app/manage/(workspace)/notes/page.tsx:23`、`src/app/manage/page.tsx:116,131`、`src/app/write/services/delete-blog.ts:5`、`src/app/blog/services/save-blog-edits.ts:11`、`src/app/blog/services/batch-delete-blogs.ts:8`
- 备注: 大部分 UI 只删 note/blog，但 `notes/page.tsx` 与 `notes/[id]` 的删除入口可作用于 mistake 行

### W-06 legacy writer UI — `write-mistake`（产生 + 变更）

- 入口路由: `src/app/write-mistake/page.tsx`（新建，挂 `StagedMistakeForm`）、`src/app/write-mistake/[slug]/page.tsx`（编辑，挂 `MistakeForm`）
- 写入点 1: `src/app/write-mistake/components/staged-mistake-form.tsx:409-424` — `createNote({ ..., type: 'mistake', ... })`
- 写入点 2: `src/app/write-mistake/components/mistake-form.tsx:361-383` — payload 含 `type: 'mistake' as const`（`:364`），edit 模式 `updateNote(initialData.slug, payload)`（`:379`），create 模式 `createNote({...payload, slug})`（`:383`）
- 状态: **活跃**（`src/app/batch7-compatibility.test.ts:27-28,43-44` 显式断言这两条路由文件存在）

### W-07 legacy writer UI — `write-note/[slug]` 编辑 mistake 行（变更）

- 位置: `src/app/write-note/[slug]/page.tsx:209-225` — `updateNote(slug, {...})`；当 `form.type === 'mistake'` 时写 `difficulty/question/my_answer/correct_answer/analysis/knowledge_points/images/ai_metadata`（`:216-225`）
- 触发: 打开既有 `type='mistake'` Note 的 `/write-note/{slug}` 并保存
- 状态: **活跃**
- 备注: UI 显示类型「不可更改」（`:247`），但不阻止对 mistake 字段的更新；`write-note/page.tsx:56,168` 的新建入口仅 `note|blog`，**不是** mistake 写入方

### W-08 以下 UI **不是** legacy mistake 写入方（排除项，留证）

| 路径 | 证据 | 结论 |
| --- | --- | --- |
| `src/app/manage/(workspace)/notes/components/content-editor.tsx:150,173` | `type: 'note' \| 'blog'`（`:15`）；`notes/new/page.tsx:9` 与 `notes/[slug]/page.tsx:20` 拒绝 mistake | 不写 mistake |
| `src/app/write/services/push-blog.ts:78,82` | `type: 'blog'` | 不写 mistake |
| `src/app/notes/components/weekly-summary-card.tsx:85-89` | `type: 'note'` | 不写 mistake |
| `src/app/blog/services/save-blog-edits.ts:25` | blog 编辑 | 不写 mistake |
| `src/app/manage/(workspace)/capture/components/mistake-draft-entry.tsx:8,67` | 调 `createMistakeDraft`（canonical `/api/admin/mistake-drafts`），非 `createNote` | canonical 链路，**不是** legacy 写入方 |
| `backend/app/routers/suggestions.py:223-230` | `Note(..., type="note")` | 只写 note |

### W-09 测试/夹具中的 legacy mistake 写入（非产品写入方）

| 位置 | 行为 | 活跃性 |
| --- | --- | --- |
| `backend/tests/lsr03_seed_rehearsal.py:99-104` | INSERT notes `type='mistake'` 夹具（`mapping_version="v1-paused"` 迁移，`:154-157`） | 排练脚本，非生产 |
| `backend/tests/lsr03_final_verifier_harness.py:98` | INSERT note `type='mistake'` 夹具 | 同上 |
| `src/app/manage/(workspace)/notes/page.test.tsx:45` | mock 数据 `{ type: 'mistake', ... }` | 纯前端 mock |
| `src/hooks/use-note-index.test.ts` | mock `/api/review/*` | 纯前端 mock |

### W-10 `backend/app/services/legacy_note_migration_adapter.py` — 不写 legacy mistake（排除项）

- 该适配器**读取** legacy Note（经 `legacy_migration.canonicalize_legacy_note`，`adapter.py:595-597`）并**写入 canonical** `mistakes` / `mistake_drafts` / `review_items`（`adapter.py:435-484,510-552`）
- 它创建 canonical mistake 时 `visibility` **恒为 `'private'`**（`adapter.py:458`、`adapter.py:533`，两处 INSERT 均硬编码 `'active','private',1`）—— 详见 `w3-00-inventory-migration-adapter.md` §2
- 源域限定: migration 026 的 `canonicalize_legacy_note` 对非 `type='mistake'` 源抛 `SOURCE_TYPE_NOT_MISTAKE`（`backend/alembic/versions/026_legacy_system_retirement.py:275,386`）—— 适配器源域恰为 legacy mistake Notes
- 状态: 活跃（rehearsal 入口 `backend/tests/lsr03_rehearsal.py:14,74,103-104` 调 `migrate()`）

---

## 2. 读取方清单（Readers of `Note(type='mistake')`）

### R-01 公共 `/mistakes` 页面主读路径（PR-09 切换目标）

| 层 | 位置 | 行为 |
| --- | --- | --- |
| 页面 | `src/app/mistakes/page.tsx:27-38` | `useNoteIndex({ type: 'mistake', status: 'published', ... })` |
| Hook | `src/hooks/use-note-index.ts:5-14` | SWR → `listNotes` |
| 客户端 | `src/lib/api/notes.ts:138` | `GET /api/notes?...` |
| 后端 | `backend/app/routers/notes.py:53-128`（`list_notes`） | `:78-79` `Note.type == type.value`；匿名/非 admin 强制 `hidden==False AND status=='published'`（`:81-83`） |

- 状态: **活跃**。链接到 `/notes/{slug}` 详情（`mistakes/page.tsx:226`）→ `R-02`

### R-02 Note 详情（含 mistake 渲染）

- 后端: `backend/app/routers/notes.py:216-235`（`get_note`，slug 查 Note，非 admin 过滤 `hidden/status`，`:231-233`）
- 前端: `src/app/notes/[id]/note-detail-content.tsx:86-87,159`（`typeLabels`/`typeColors` 含 mistake；`:159` `if (note.type === 'mistake')` 专属渲染）
- 状态: **活跃**

### R-03 legacy `/api/review/*`（SM-2 复习读 + 写）

| 端点 | 位置 | 读取 |
| --- | --- | --- |
| `GET /api/review/queue` | `backend/app/routers/review.py:20-30` | `Note.type=='mistake' AND next_review<=today`（`:26-27`） |
| `GET /api/review/stats` | `review.py:66-85` | 4 个 `Note.type=='mistake'` 计数（`:70-82`） |
| `GET /api/review/plan` | `review.py:88-91` | 全量 mistake Notes → `build_review_plan`（`backend/app/services/review_planner.py:18`） |
| `POST /api/review/{slug}` | `review.py:33-63` | 读 + **写**（见 W-04） |

- 前端读: `src/lib/api/review.ts:37-52`、`src/hooks/use-note-index.ts:17-26`（`useReviewStats`/`useReviewPlan`）、`src/app/mistakes/page.tsx:40-41`、`src/app/mistakes/review/page.tsx:6,47`
- 状态: **活跃**。兼容证据: `src/hooks/use-note-index.test.ts:14`（"public mistake review API gate"）、`backend/tests/test_batch7_compatibility.py:25-28`（路由存在性 + admin 依赖断言）

### R-04 knowledge / suggestion / weak-point 服务

| 组件 | 位置 | 读取点 |
| --- | --- | --- |
| `knowledge_assistant.aggregate_weaknesses` | `backend/app/services/knowledge_assistant.py:46-75` | `:49,60` `Note.type=='mistake'` + `subject`/`knowledge_points` 聚合 |
| `knowledge_assistant.generate_suggestions` | `knowledge_assistant.py:86+` | 复用上者；经 `GET /api/ai/suggestions`（`backend/app/routers/suggestions.py:23-29`） |
| `knowledge_retrieval.retrieve_context_pack` | `backend/app/services/knowledge_retrieval.py:114-244` | `:97,190,221` 判 `note.type=='mistake'`，产出 `related_mistakes`（`:222,241`） |
| `knowledge_retrieval.retrieve_weak_points` | `knowledge_retrieval.py:247-311` | `:257` `Note.type=='mistake'` 近 30 天 → weak-point 诊断 |
| `knowledge_relations.suggest_relations` | `backend/app/services/knowledge_relations.py:61-151` | `:95,115,119,132` 按 `type=='mistake'` 定关系类型 |
| `recommendation.collect_context` | `backend/app/services/recommendation.py:14-80` | `:31,44,56` 最近/待复习/含 KP 的 mistake Notes |
| `suggestions` 周报 | `backend/app/routers/suggestions.py:86-246` | `:98,101,105,115` 与 `:161,164,168,178` 计数/聚合 mistake Notes |
| `review_planner.build_review_plan` | `backend/app/services/review_planner.py:18-79` | 消费 mistake Notes（`next_review` 等） |

- 出口路由: `backend/app/routers/knowledge.py:25`（`pack.related_mistakes`）、`suggestions.py:23-29,86`、`recommendations` 路由
- 前端消费: `src/app/mistakes/components/weak-point-diagnosis.tsx`（weak-point）、`src/app/notes/[id]/components/related-knowledge-panel.tsx:70,80`（`related_mistakes`）
- 状态: **活跃**

### R-05 AI 分析上下文（间接读）

- `backend/app/services/ai_analyze_service.py:246-250`（`request_body.context_pack.related_mistakes` 拼上下文）、`:304`（`SourceType.mistake` 引用字段白名单 `_MISTAKE_FIELDS`）
- 来源是 R-04 的 context pack，非直接查 Note；`:221` `find_related_notes` 显式 `Note.type == "note"`（排除 mistake）
- 状态: **活跃**（间接）

### R-06 管理端搜索

- `backend/app/routers/search.py:13-19`（`POST /api/admin/search`，admin-only）→ `backend/app/services/knowledge_markdown_service.py:68,77` `search_notes`
- `knowledge_markdown_service.py:77` 仅过滤 `hidden.is_(False), status=='published'`，**不按 type 过滤** → 结果可含 `type='mistake'` Note
- 状态: **活跃**

### R-07 列表 / 侧栏 / 路由元数据（按 type 过滤或展示）

| 位置 | 行为 |
| --- | --- |
| `src/app/notes/page.tsx:25-26,110,233,371` | typeLabels/typeColors 含 mistake；筛选器含 `mistake`；`:371` mistake 专属 `next_review` 展示 |
| `src/app/notes/components/knowledge-sidebar.tsx:292,295` | 侧栏含 `mistake` 类型项（`contentTypes` 过滤） |
| `src/lib/manage-display.ts:34` | `mistake: '错题'` 标签 |
| `src/lib/content-routes.ts:1,10,15` | `ContentType` 含 `mistake`；mistake 跳 `/manage/mistakes` / `/mistakes` |
| `src/app/manage/(workspace)/notes/page.tsx:16,18` | `useNoteIndex({type})` 后 `filter(item.type === 'note' \|\| item.type === 'blog')` —— **读到但丢弃** mistake |
| `src/app/discover/page.tsx:9,49` | `listNotes({ type: 'note', ... })` —— 不含 mistake（排除项） |
| `src/app/(home)/share-card.tsx:24`、`src/app/guestbook/page.tsx:21,29,136` | 展示标签/链接含 mistake（元数据，非数据读） |

### R-08 兼容/契约测试中的 legacy mistake 读

| 测试 | 位置 | 断言 |
| --- | --- | --- |
| 前端 review API gate | `src/hooks/use-note-index.test.ts:14-49` | `useReviewStats`/`useReviewPlan` 启用/停用与 `/api/review/stats`、`/api/review/plan` key |
| 路由兼容 | `src/app/batch7-compatibility.test.ts:13,24,27-28,39,43-44,54-57` | 公共 `mistakes/page.tsx` 存在、`write-mistake` 两页存在、`content-routes` 含 `/manage/mistakes`、`/mistakes` 不被重定向 |
| 后端路由契约 | `backend/tests/test_batch7_compatibility.py:25-28,43-46` | `/api/review/*` 四路由存在且 admin-gated；`/api/notes` 写路由 admin-gated |
| 权限 | `backend/tests/test_manage_write_permissions.py:47-49` | note create/update/delete 拒匿名与非 admin |
| 匿名读 | `backend/tests/test_anon_capture_access.py:43-49` | 公开 `GET /api/notes` 可用 |
| 管理列表 | `src/app/manage/(workspace)/notes/page.test.tsx:45` | mock 中含 `type: 'mistake'` 行，断言被列表过滤掉 |
| review 队列 UI | `src/app/manage/(workspace)/review/review-queue.test.tsx:10`、`src/features/ui-v2/review/review.test.tsx:56,86,107` | `target_type: 'mistake'`（**canonical ReviewItem**，非 legacy Note —— 不属本清单冻结面） |
| migration 契约 | `backend/tests/test_legacy_note_migration_contract.py`、`test_legacy_note_migration_static_contract.py`、`test_legacy_note_migration_adapter.py` | ledger/幂等键/镜像契约（读 ledger 与 canonical 表，非 legacy Note 写） |
| LSR03 排练 | `backend/tests/lsr03_*.py` | 见 W-09 + 适配器 `migrate()` 重放 |

### R-09 不读 legacy mistake 的边界（排除项，留证）

- `backend/app/services/dashboard_service.py:47,69-73,96-104` — 只用 canonical `Mistake` 模型（`app.models.mistake.Mistake`），不查 `Note.type=='mistake'`
- canonical 复习/错题路由: `backend/app/routers/review_items.py`、`admin_mistakes.py`、`mistake_drafts.py` —— canonical `Mistake`/`ReviewItem`，不触 legacy Note

---

## 3. `legacy_note_migration_adapter.py` 的 visibility 行为（任务 A.6）

- **创建 canonical mistake 时 `visibility` 恒为 `'private'`**，无参数、不看源 Note 的 `status`/`hidden`：
  - `backend/app/services/legacy_note_migration_adapter.py:453-458`（`_create_targets` 内 INSERT `...,'active','private',1`）
  - `backend/app/services/legacy_note_migration_adapter.py:528-533`（`_finish_mistake_targets` 内 INSERT 同样 `'active','private',1`）
- 与 PR-09 已定映射规则冲突: 源 Note `status=='published' AND hidden==false` → `visibility='public'`（`docs/workflows/personal-learning-system-convergence/design.md:99`、`requirements.md:126`）。当前适配器**未实现**该规则
- `should_retain_public_only`（`adapter.py:282-295`）只决定「公开但确定性映射失败 → `retained_public_only` 不建目标」，与 created mistake 的 visibility 无关
- week3/README.md:29 已要求 PR-09 "reconcile this behavior instead of building a second, conflicting migrator"

---

## 4. PR-09「冻结写入」完整冻结目标清单

### 4.1 必须 fail-closed 的「产生」路径（新 legacy mistake 不再可能产生）

| # | 目标 | 位置 | 冻结动作 |
| --- | --- | --- | --- |
| F-1 | note create | `backend/app/routers/notes.py:238-304` | 拒绝 `req.type == NoteType.mistake`（400/409），保留 note/blog 创建 |
| F-2 | note update-type | `backend/app/routers/notes.py:307-354` + `backend/app/schemas/note.py:55` | 拒绝把 `type` 设为/改为 `'mistake'`（含从其他 type 改入） |
| F-3 | note promote | `backend/app/routers/notes.py:431-451` | 拒绝 `new_type == NoteType.mistake` |
| F-4 | legacy writer UI（新建） | `src/app/write-mistake/page.tsx` + `staged-mistake-form.tsx:409-424` | 入口 fail-closed（禁用/移除/跳转说明），不得再 `createNote(type:'mistake')` |
| F-5 | legacy writer UI（编辑保存） | `src/app/write-mistake/components/mistake-form.tsx:361-383` | 同上，含 edit 模式 `updateNote` |
| F-6 | `write-note/[slug]` mistake 编辑 | `src/app/write-note/[slug]/page.tsx:209-225` | 对 `note.type==='mistake'` 的保存 fail-closed |

### 4.2 建议一并冻结的「变更」路径（与 W3-D02 "freeze all new legacy mistake writes" 对齐；是否纳入见 §6 U-1）

| # | 目标 | 位置 | 理由 |
| --- | --- | --- | --- |
| F-7 | legacy SM-2 复习提交 | `backend/app/routers/review.py:33-63`（W-04） | 持续改写 mistake 行调度字段，会使迁移期源 hash/revision 漂移 |
| F-8 | mistake 行字段更新 | `backend/app/routers/notes.py:307-354`（对既有 `type='mistake'` 行） | 同上（`expected_revision` 亦变） |
| F-9 | mistake 行删除 | `backend/app/routers/notes.py:396-420,423-428`（W-05） | 删除会使迁移盘点源集不稳定 |

> W3-D02 措辞为 "freeze all new legacy mistake writes"，而 week3/README.md:110 与任务书枚举 "create, update-type, promote and the legacy writer UI"。两者宽严不一，见 §6 U-1。

### 4.3 不需冻结（非 legacy mistake 写）

- canonical 链路: `admin_mistakes.py` / `mistake_drafts.py` / `capture`（W-08）/ `mistake_service.py`
- note/blog 创建与编辑: `write-note/page.tsx`、`push-blog.ts`、`content-editor.tsx`、`weekly-summary-card.tsx`
- migration 适配器本身（写的是 canonical Mistake，不写 legacy Note）

---

## 5. 「必须保留的兼容读」清单

冻结后仍须保留（作为兼容证据与 PR-09 切换前后回归依据）：

| # | 读路径 | 位置 | 保留理由 |
| --- | --- | --- | --- |
| K-1 | `GET /api/notes`（type 过滤） | `backend/app/routers/notes.py:53-128` | 公共 `/mistakes` 切换前的唯一数据源；切换后作 legacy 兼容读与对账证据 |
| K-2 | `GET /api/notes/{slug}` | `notes.py:216-235` | mistake 详情（`/notes/{slug}`）兼容读 |
| K-3 | `GET /api/review/queue` | `review.py:20-30` | legacy 复习队列读 |
| K-4 | `GET /api/review/stats` | `review.py:66-85` | legacy 统计读 |
| K-5 | `GET /api/review/plan` | `review.py:88-91` + `review_planner.py:18` | legacy 复习计划读 |
| K-6 | `useNoteIndex` / `useReviewStats` / `useReviewPlan` | `src/hooks/use-note-index.ts:5-26` | 前端兼容 hook（含 gate 测试 `use-note-index.test.ts`） |
| K-7 | 公共 `/mistakes` 页读 | `src/app/mistakes/page.tsx:27-38` | cutover 前读路径 + Empty/error 状态回归 |
| K-8 | mistake 详情渲染 | `src/app/notes/[id]/note-detail-content.tsx:159` | 旧 slug 链接兼容 |
| K-9 | knowledge/suggestion/recommendation/weak-point 读 | R-04 各行 | 非公共面但仍消费 legacy mistake；PR-09 不得顺手删除 |
| K-10 | 管理搜索读 | `knowledge_markdown_service.py:68,77` | admin 搜索兼容 |
| K-11 | 列表/侧栏/路由元数据 | R-07 | 导航与展示兼容 |
| K-12 | 兼容/契约测试 | R-08 全表 | 冻结与切换的回归证据基线 |

---

## 6. unresolved_issues

| # | 问题 | 影响 | 建议 |
| --- | --- | --- | --- |
| U-1 | **冻结范围歧义**: W3-D02 "freeze all new legacy mistake writes" vs week3/README.md:110 与 w3-00/pr-09 任务书枚举 "create, update-type, promote + legacy writer UI"。是否冻结 F-7（SM-2 复习提交）、F-8（既有 mistake 字段更新）、F-9（删除）未明确 | 冻结不全会在迁移期引入源漂移（`adapter.py:598-599` 的 `SOURCE_DRIFT` / `:607` hash mismatch） | 主 agent 定版：建议全冻 F-1～F-9（fail-closed 于「写 `type='mistake'` 行」），读保留 K-1～K-12 |
| U-2 | `POST /api/notes/{slug}/promote` 前端无调用方（仅 `src/lib/api/notes.ts:178-179` 封装），但 API 面开放 | 若只冻 UI 会漏掉 API 直调 | F-3 必须在后端路由层 fail-closed，不依赖 UI |
| U-3 | `knowledge_markdown_service.search_notes`（`search.py` 经 `:68,77`）不按 type 过滤，管理搜索会返回 mistake 行 —— 属兼容读还是要随公共切换收窄，计划未明说 | 影响 K-10 的保留边界 | 建议保留为兼容读（admin-only），不随 PR-09 收窄 |
| U-4 | `src/app/manage/(workspace)/notes/page.tsx:18` 读到 mistake 后前端丢弃 —— 若后端 list 收窄是否影响该列表，未在计划中定义 | 低（行为不变） | 列为 K-11 观察项，不要求改动 |
| U-5 | W-05 删除入口（`notes/page.tsx`、`notes/[id]`）可删 mistake 行，但多数删除 UI 面向 note/blog | 若 U-1 判定删除须冻结，需逐入口标注 | 随 U-1 一并定版 |
| U-6 | 计划外写入方搜索结论: 已覆盖 routers/notes.py、routers/review.py、前端 write-mistake/write-note/manage/write/blog/notes/weekly-summary/capture、suggestions 周报 Note 构造、测试夹具、migration 适配器。**未发现**其他能创建/改写 `type='mistake'` 的产品代码路径 | — | 若评审发现漏网写入方，按 stop_condition 上报 |
