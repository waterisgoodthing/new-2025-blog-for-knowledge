# Batch 8 验证记录

> 本文件随每个任务完成即时更新，不批量回填。

## P0-01 需求与现状审计（已完成）

### 审计方法

只读检查：模型、schema、service、router、前端 API 客户端、Alembic 状态、配置。

### 1. Alembic 状态

- `alembic current` = `014 (head)`
- `alembic heads` = `014 (head)`
- 最新迁移：`014_add_attachments.py`
- Batch 8 新迁移编号将为 `015`。
- 已知架构债：`main.py` 第 42 行使用 `Base.metadata.create_all`；Batch 8 不依赖它，坚持 migration-first，但不在本批移除该调用（超出范围）。

### 2. 附件系统（可复用）

| 组件 | 位置 | 关键事实 |
| --- | --- | --- |
| Attachment 模型 | `backend/app/models/attachment.py` | UUID 主键；`visibility=private` CHECK 约束；`status IN ('active','missing','deleted')`；`storage_provider='local'` CHECK 约束 |
| AttachmentLink 模型 | 同上 | `target_type IN ('question_draft','question','mistake')` CHECK 约束；`purpose IN ('source','question','answer','inline','ai_input','ai_output')` |
| 上传服务 | `attachment_service.create_attachment_from_bytes()` | 接受 bytes，本地存储，创建 private 记录；`MAX_UPLOAD_BYTES=10MB` |
| 链接服务 | `attachment_service.create_attachment_link()` | `_target_exists()` 仅校验 question_draft/question/mistake |
| 路由 | `routers/attachments.py` | `prefix=/api/admin/attachments`，`dependencies=[Depends(get_current_admin)]` |
| 前端 | `src/lib/api/attachments.ts` | `uploadAttachment(file)`，`AttachmentTargetType = 'question_draft'|'question'|'mistake'` |

**需扩展约束**：若通过 `attachment_links` 关联原图到 capture_item，需扩展 `target_type` CHECK 约束加入 `'capture_item'` 并更新 `_target_exists()`。替代方案是在 `capture_items` 上用直接 FK `source_attachment_id`，不改 attachment_links 约束。P0-02 冻结此决策。

### 3. 错题草稿系统（可复用，关键约束）

| 组件 | 位置 | 关键事实 |
| --- | --- | --- |
| MistakeDraft 模型 | `backend/app/models/mistake.py` | `draft_item_id` unique FK；`question_id` 或 `question_draft_id` 二选一（CHECK 约束） |
| MistakeDraftCreate schema | `backend/app/schemas/mistake.py` | `exactly_one_source` 校验：必须提供 question_id 或 question_draft_id |
| 创建服务 | `mistake_service.create_mistake_draft()` | 从 question/question_draft 获取 subject_id、title、question_text、correct_answer_snapshot、explanation_snapshot |
| 转换服务 | `mistake_service.convert_mistake_draft()` | 原子创建 Mistake + KnowledgePointLinks + ReviewItem；标记 DraftItem converted |
| 路由 | `routers/mistake_drafts.py` | `prefix=/api/admin/mistake-drafts`，admin-only |
| 前端 | `src/lib/api/mistakes.ts` | `createMistakeDraft()`，`convertMistakeDraft()` |

**关键发现**：`create_mistake_draft` 强制要求 question_id 或 question_draft_id。capture 转换不能直接创建 mistake_draft，必须先创建 question_draft（从 AI 题面草稿），再从 question_draft 创建 mistake_draft。`DraftItem.source_type` 对 mistake 仅允许 `'question'` 或 `'question_draft'`（CHECK 约束 `ck_draft_items_source`），不允许 `'capture'` 作为 source。

### 4. 题目草稿系统（可复用，转换入口）

| 组件 | 位置 | 关键事实 |
| --- | --- | --- |
| QuestionDraftCreate schema | `backend/app/schemas/question.py` | 需 subject_id、question_text（非空）、question_type、options、correct_answer、explanation、difficulty、knowledge_point_ids |
| 创建服务 | `draft_service.create_question_draft()` | 创建 DraftItem(draft_type="question", source_type="manual") + QuestionDraft + KnowledgePointLinks |
| 转换服务 | `draft_service.convert_question_draft()` | 创建 Question + QuestionSource + KnowledgePointLinks |

**capture 转换路径**：capture ready → 用 AI 题面草稿创建 QuestionDraft → 从 QuestionDraft 创建 MistakeDraft → 标记 capture converted。两个 draft 创建在同一事务中，不修改既有 service 签名。

### 5. 复习系统（可复用，不新增路径）

| 组件 | 位置 | 关键事实 |
| --- | --- | --- |
| ReviewItem 模型 | `backend/app/models/review_item.py` | `target_type='mistake'` CHECK 约束；`state IN ('active','paused')`；`algorithm='fixed_interval_v1'` |
| ReviewItem 创建 | `mistake_service.convert_mistake_draft()` 第 142 行 | **唯一创建路径**；capture 不创建 ReviewItem |
| 复习提交 | `review_item_service.submit_review()` | 固定间隔算法 `INTERVALS={0:1,1:1,2:1,3:3,4:7,5:14}` |

### 6. AI 服务（既有，需隔离）

| 组件 | 位置 | 关键事实 |
| --- | --- | --- |
| call_ocr_model | `ai_service.py` 第 205 行 | vision+json；preferred=dashscope_vision |
| call_text_model | `ai_service.py` 第 220 行 | text+json；preferred=deepseek |
| 多供应商回退 | `_call_with_fallback()` | deepseek → dashscope_vision → qwen_general |
| 旧 AI 提示词 | `mistake_staged_service.py` | Batch 6 占位：question_draft 生成、error_interpretation、final_analysis；已接入 AI 路由 |
| 配置 | `config.py` | DASHSCOPE_API_KEY、DEEPSEEK_API_KEY、AI_API_KEY、UPLOAD_ROOT、MAX_UPLOAD_BYTES |

**隔离策略**：Batch 8 capture 使用窄 adapter 调用 `call_ocr_model`/`call_text_model`，不修改 `mistake_staged_service.py` 或 `routers/ai.py`。旧 AI 能力保持原样。

### 7. 鉴权（可复用）

| 组件 | 位置 | 关键事实 |
| --- | --- | --- |
| get_current_admin | `routers/auth.py` 第 111 行 | 401 未认证；403 非管理员 |
| AUTH_BYPASS | `_is_auth_bypass_active()` 第 62 行 | 仅当 AUTH_BYPASS=true 且 AUTH_BYPASS_ALLOW=true 时激活 |
| 路由保护模式 | 所有 admin 路由 | `dependencies=[Depends(get_current_admin)]` 在 router 级别 |

**Batch 8**：capture 路由使用相同模式；权限验收不依赖 AUTH_BYPASS。

### 8. 前端管理端（可复用模式）

- 管理端路由在 `src/app/manage/(workspace)/` 下，已有 mistakes、attachments、drafts、questions、review 等子目录。
- 无 `/manage/capture` 存在；Batch 8 将创建 `src/app/manage/(workspace)/capture/`。
- API 客户端在 `src/lib/api/`，将新增 `captures.ts`。
- 管理布局 `src/app/manage/(workspace)/layout.tsx` 提供 AuthGate 等价保护。

### 9. 复用点清单

- `attachments` + `attachment_links`：保存和关联原图。
- `draft_service.create_question_draft()`：从 AI 题面创建题目草稿。
- `mistake_service.create_mistake_draft()`：从题目草稿创建错题草稿。
- `mistake_service.convert_mistake_draft()`：人工确认后生成正式 mistake + review_item。
- `attachment_service.create_attachment_from_bytes()`：图片上传。
- `get_current_admin`：所有 capture 接口鉴权。
- `call_ocr_model` / `call_text_model`：窄 adapter 内部调用。

### 10. 需扩展约束

| 约束 | 当前值 | Batch 8 方案 |
| --- | --- | --- |
| `attachment_links.target_type` CHECK | `'question_draft','question','mistake'` | P0-02 决策：扩展加 `'capture_item'` 或用 capture_items.source_attachment_id 直接 FK |
| `attachment_service._target_exists()` | 仅 question_draft/question/mistake | 若扩展 target_type 则同步更新 |

### 11. 旧 AI 能力隔离策略

- 不修改 `routers/ai.py`（65KB，大量既有端点）。
- 不修改 `mistake_staged_service.py`（Batch 6 占位提示词）。
- capture adapter 独立文件，仅调用 `call_ocr_model`/`call_text_model` 底层函数。
- 旧 AI 路由保持原样，capture 不复用其端点。

### 12. 停止条件

- 若 P0-02 发现 schema 与本审计不一致 → 停止并申请范围扩大。
- 若需要修改 DraftItem/MistakeDraft 核心 CHECK 约束 → 停止。
- 若需要修改旧 AI 路由或 staged service → 停止。

### 结论

P0-01 审计通过。现状与设计文档一致，复用路径明确，无需扩大范围。可进入 P0-02。

## P0-02 capture_items 数据模型设计（已完成）

### 设计决策

1. **附件关联**：采用直接 FK `source_attachment_id` 关联原图，不修改 `attachment_links` CHECK 约束。原图始终通过既有 `attachments` 表管理，保持 `visibility=private`。转换时再用 `attachment_links`（target_type='mistake', purpose='source'）关联原图到生成的 mistake_draft。
2. **幂等转换**：`mistake_draft_item_id` 为 UNIQUE FK 到 `draft_items`。converted 状态必须有此字段（CHECK 约束）。重复转换返回既有结果。
3. **状态机**：`uploaded → recognizing → recognized → drafting → ready → converted`；任一处理阶段可 `failed` 后重试；`archived` 为终态。
4. **失败隔离**：capture 失败只写 capture_items 错误字段，不写 mistake_drafts/mistakes/review_items。

### 新增文件

| 文件 | 说明 |
| --- | --- |
| `backend/app/models/capture.py` | CaptureItem 模型（21 字段，4 CHECK，4 FK，1 UNIQUE，2 索引） |
| `backend/app/schemas/capture.py` | CaptureCreate/CapturePatch/CaptureConvert/CaptureOut + KnowledgePointSuggestion |
| `backend/alembic/versions/015_add_capture_items.py` | 迁移 015，down_revision=014 |

### 修改文件

| 文件 | 修改 |
| --- | --- |
| `backend/app/models/__init__.py` | 注册 CaptureItem 导入与 `__all__` |

### 验证结果

- `alembic upgrade head`：014 → 015 成功。
- `alembic current`：`015 (head)`。
- 表结构检查：21 列全部存在，类型正确。
- 约束检查：11 个约束全部存在（4 FK + 1 PK + 4 CHECK + 1 UNIQUE + 1 索引）。
- 既有数据计数不变（零污染）：
  - attachments: 1, mistake_drafts: 3, mistakes: 3, review_items: 3, review_records: 3
  - draft_items: 6, question_drafts: 3, questions: 3
- capture_items: 0 行（新建空表）。
- 模型/schema 导入：OK。

### 约束清单

| 约束名 | 类型 | 规则 |
| --- | --- | --- |
| ck_capture_items_status | CHECK | status IN (8 种状态) |
| ck_capture_items_conversion | CHECK | converted 必须有 mistake_draft_item_id；非 converted 不能有 |
| ck_capture_items_attempt_count | CHECK | attempt_count >= 0 |
| ck_capture_items_last_stage | CHECK | last_stage IN ('recognize','draft','convert') 或 NULL |
| uq_capture_items_mistake_draft | UNIQUE | mistake_draft_item_id 唯一（防重复转换） |
| capture_items_source_attachment_id_fkey | FK | → attachments.id, RESTRICT |
| capture_items_subject_id_fkey | FK | → subjects.id, RESTRICT |
| capture_items_mistake_draft_item_id_fkey | FK | → draft_items.id, RESTRICT |
| capture_items_created_by_fkey | FK | → users.id, SET NULL |

### 结论

P0-02 完成。可进入 P0-03。

## P0-03 OCR / 多模态调用边界设计（已完成）

### 新增文件

| 文件 | 说明 |
| --- | --- |
| `backend/app/services/capture_recognition.py` | 窄识别 adapter，封装 `call_ocr_model` |

### 接口

```python
async def recognize_image(image_bytes, mime_type, *, use_fake=False, fake_text="") -> RecognitionResult
```

### 错误分类

| error_code | 说明 |
| --- | --- |
| empty_input | 图片字节为空 |
| empty_result | 识别返回空文本 |
| no_provider | 无 AI 供应商配置 |
| timeout | 请求超时 |
| provider_error | AI 供应商错误 |
| parse_error | 解析失败 |

### 隔离策略

- 不修改 `ai_service.py`、`routers/ai.py`、`mistake_staged_service.py`。
- adapter 只调用 `call_ocr_model` 底层函数。
- 失败返回 `RecognitionResult(success=False)`，不抛异常给 capture service。
- `use_fake=True` 用于无真实凭据时的 service/schema/状态机测试。
- 超时由底层 `httpx.AsyncClient(timeout=120)` 控制，不引入生产队列。

### 验证

- 导入：OK。
- fake adapter 测试：OK（返回 fake_text）。

### 结论

P0-03 完成。可进入 P0-04。

## P0-04 AI 错因草稿输出 schema 设计（已完成）

### 新增文件

| 文件 | 说明 |
| --- | --- |
| `backend/app/services/capture_ai_draft.py` | 窄 AI 草稿 adapter，封装 `call_text_model` |

### 新增 schema（在 `backend/app/schemas/capture.py`）

| schema | 说明 |
| --- | --- |
| `SubjectSuggestion` | { id?, label?, confidence? } |
| `MistakeDraftSuggestionV1` | 固定输出 schema：question_text, analysis_text, error_summary, subject_suggestion, knowledge_point_suggestions, warnings |
| `CaptureDraftInput` | AI 草稿输入：recognized_text, user_error_context, subject_id, subject_label |

### 接口

```python
async def draft_mistake(draft_input: CaptureDraftInput, *, use_fake=False) -> DraftResult
```

### 校验语义

- 原始 AI 输出经 `_validate_suggestion()` 规范化后构造 `MistakeDraftSuggestionV1`。
- schema 校验失败 → `error_code='schema_error'`，不写入 mistake_drafts。
- 所有字段进入 capture 草稿区并允许人工编辑。
- 知识点建议 id 为 null，由管理员确认后选择（建议与正式选择分离）。

### 错误分类

| error_code | 说明 |
| --- | --- |
| empty_input | 识别文本为空 |
| schema_error | AI 输出 schema 校验失败 |
| no_provider | 无 AI 供应商配置 |
| timeout | 请求超时 |
| provider_error | AI 供应商错误 |
| parse_error | 解析失败 |

### 验证

- 导入：OK。
- fake adapter 测试：OK（返回固定假数据，含 suggestion）。

### 结论

P0-04 完成。可进入 P0-05。

## P0-05 capture → mistake_draft 转换流程设计（已完成）

### 新增文件

| 文件 | 说明 |
| --- | --- |
| `backend/app/services/capture_service.py` | capture 业务逻辑服务，管理完整生命周期和转换 |

### 接口

| 函数 | 签名 | 职责 |
| --- | --- | --- |
| `create_capture` | `(session, payload: CaptureCreate, *, created_by) -> CaptureItem` | 从已上传 attachment 创建 capture_item |
| `get_capture` | `(session, capture_id, *, for_update=False) -> CaptureItem` | 获取 capture，支持行锁 |
| `list_captures` | `(session, *, status=None) -> list[CaptureItem]` | 列出 capture |
| `patch_capture` | `(session, capture_id, payload: CapturePatch) -> CaptureItem` | 人工编辑草稿字段 |
| `trigger_recognition` | `(session, capture_id, *, use_fake, fake_text) -> CaptureItem` | 触发 OCR 识别 |
| `trigger_draft` | `(session, capture_id, *, use_fake) -> CaptureItem` | 触发 AI 草稿生成 |
| `convert_capture` | `(session, capture_id, payload: CaptureConvert, *, created_by) -> ConvertResult` | 显式幂等转换 |

### 转换流程

```
capture(ready)
  ├─ 1. create_question_draft()  → QuestionDraft + DraftItem(question)
  ├─ 2. create_mistake_draft()   → MistakeDraft + DraftItem(mistake)
  ├─ 3. create_attachment_link() → attachment_links(source → question_draft)
  └─ 4. capture.status = converted, mistake_draft_item_id = draft_item.id
```

### 关键设计决策

1. **不创建正式 mistake 或 review_item**：`convert_capture` 只调用 `create_question_draft` 和 `create_mistake_draft`，不调用 `convert_mistake_draft`。人工仍需在 mistake_draft 链路确认后才能进入正式 mistake。
2. **幂等转换**：`mistake_draft_item_id` 为 UNIQUE FK。已 converted 的 capture 重复调用 `convert_capture` 返回既有结果，不创建新草稿。
3. **事务化**：所有步骤在同一 session 中执行，由 `get_db()` 依赖管理事务。任何步骤 flush 失败自动回滚，不留半成品。
4. **人工输入为权威源**：`CaptureConvert` payload 是自包含的确认数据，不依赖 capture 草稿字段。AI 输出只进入 capture 草稿区作为建议。
5. **附件关联**：原图通过 `attachment_links`（target_type='question_draft', purpose='source'）关联到 question_draft，不修改 attachment_links CHECK 约束。
6. **失败零污染**：OCR/AI 失败只写 capture_items 错误字段，不创建 mistake_draft/mistake/review_item。
7. **手动路径**：用户可跳过 AI，手动 patch `question_draft_text` 后状态自动转为 ready，直接 convert。

### 状态转换

```
uploaded → recognizing → recognized → drafting → ready → converted
                ↓              ↓           ↓          ↓
              failed         failed      failed     (终态)
                ↓                          ↓
           (patch → ready)          (patch → ready)
```

### 安全检查

- 不导入 `Mistake` 或 `ReviewItem` 模型：OK
- 不调用 `convert_mistake_draft()`：OK（不会创建正式 mistake/review_item）
- 使用 `create_question_draft()` 和 `create_mistake_draft()`：OK（只创建草稿）
- `for_update=True` 防止并发转换：OK
- 附件链接 `AttachmentConflict` 被捕获并记录日志：OK

### 验证

- 导入：OK（所有函数、异常类、dataclass 可导入）
- 函数签名：OK（7 个函数 + 4 个异常类 + 1 个 dataclass）
- 安全检查：OK（不直接创建 mistake/review_item）
- 既有测试回归：82 passed，2 failed（均为 `test_mistake_review_service.py` 既有数据残留问题，与 capture 无关）
- 数据库零污染：
  - capture_items: 0
  - mistake_drafts: 3（不变）
  - mistakes: 3（不变）
  - review_items: 3（不变）
  - draft_items: 6（不变）
  - question_drafts: 3（不变）
  - alembic version: 015
- git diff：新增 `capture_service.py`，未修改任何既有业务代码

### 结论

P0-05 完成。可进入 P0-06。

## P0-06 管理端页面与交互设计（已完成）

### 新增文件

| 文件 | 说明 |
| --- | --- |
| `backend/app/routers/captures.py` | admin-only 路由，7 个端点 |
| `src/lib/api/captures.ts` | 前端 API 客户端，类型与函数 |
| `src/app/manage/(workspace)/capture/page.tsx` | 管理端页面入口 |
| `src/app/manage/(workspace)/capture/components/capture-workspace.tsx` | 采集工作台主组件 |

### 修改文件

| 文件 | 修改 |
| --- | --- |
| `backend/app/schemas/capture.py` | 新增 `ConvertResultOut` schema |
| `backend/main.py` | 注册 `captures` 路由 |
| `src/app/manage/components/manage-sidebar.tsx` | 新增「采集」导航入口 |

### 后端 API 端点

| 方法 | 路径 | 职责 |
| --- | --- | --- |
| GET | `/api/admin/captures` | 列出采集项（可选 status 过滤） |
| POST | `/api/admin/captures` | 从 attachment_id 创建采集项 |
| GET | `/api/admin/captures/{id}` | 获取采集项详情 |
| PATCH | `/api/admin/captures/{id}` | 人工编辑草稿字段 |
| POST | `/api/admin/captures/{id}/recognize` | 触发 OCR 识别 |
| POST | `/api/admin/captures/{id}/draft` | 触发 AI 草稿生成 |
| POST | `/api/admin/captures/{id}/convert` | 转为错题草稿 |

所有端点均受 `get_current_admin` 保护（router 级 dependencies）。

### 前端交互流程

```
上传图片 → createCapture(attachment_id)
  ↓
触发识别 → triggerRecognition → 显示可编辑识别文字
  ↓
补充错因 → patchCapture(user_error_context)
  ↓
生成草稿 → triggerDraft → 显示可编辑题面/解析/错因草稿
  ↓
人工确认 → 选择学科/知识点/难度/错误类型
  ↓
convertCapture → 跳转到 /manage/drafts
```

### 状态展示

- `uploaded` → 灰色「待识别」
- `recognizing` → 蓝色 + 旋转图标「识别中」
- `recognized` → 蓝色「已识别」
- `drafting` → 蓝色 + 旋转图标「草稿生成中」
- `ready` → 绿色「待确认」
- `failed` → 红色「失败」+ 错误信息
- `converted` → 紫色「已转换」+ 跳转链接

### 关键设计

1. **图片预览**：通过 `fetch` + `credentials: 'include'` 获取 blob URL，不泄露 storage_key。
2. **草稿编辑**：所有 AI 字段（题面、解析、错因、知识点建议）均可人工编辑和覆盖。
3. **手动路径**：用户可跳过 AI，手动填写题面后直接 convert。
4. **知识点建议展示**：AI 建议的知识点以标签形式展示（含置信度），人工选择正式知识点。
5. **转换后跳转**：convert 成功后跳转到 `/manage/drafts`，提示「仍需人工确认」。
6. **响应式布局**：桌面双栏（列表 + 详情），移动单栏。

### 验证

- 后端导入：OK（7 路由全部注册）
- 后端 app 路由检查：7 个 `/api/admin/captures` 路由
- 前端 TSC：OK（无类型错误）
- 前端 build：OK（`/manage/capture` 路由已构建）
- 侧边栏导航：「采集」入口已添加（Camera 图标）

### 结论

P0-06 完成。可进入 P0-07。

## P0-07 权限、公开边界与失败状态设计（已完成）

### 验证方法

代码审计 + grep 搜索 + schema 字段检查 + 路由依赖检查。

### 1. Admin-only 防线

| 检查项 | 结果 |
| --- | --- |
| captures router 有 `Depends(get_current_admin)` | ✓ router 级 dependencies |
| 所有 7 个端点在 `/api/admin/captures` 下 | ✓ 无公开路由 |
| 无 `/api/captures` 公开路由 | ✓ |
| 附件内容端点 admin-only | ✓ `/api/admin/attachments/{id}/content` |

### 2. Private 原图

| 检查项 | 结果 |
| --- | --- |
| attachments 表 `visibility='private'` CHECK 约束 | ✓ `ck_attachments_visibility` |
| 前端图片预览通过 `credentials: 'include'` fetch blob | ✓ 不泄露 storage_key |
| CaptureOut 不含 storage_key | ✓ |

### 3. 公开回归

| 检查项 | 结果 |
| --- | --- |
| 公开 `/mistakes`、`/notes`、`/blog` 不引用 captures API | ✓ grep 确认 |
| 公开页面不请求 `/api/admin/` 端点 | ✓ grep 确认 |
| captures API 仅在 `manage/(workspace)/capture/` 引用 | ✓ |
| CaptureOut 不含 AI/OCR 原始输出（raw_output） | ✓ |

### 4. 失败隔离

| 检查项 | 结果 |
| --- | --- |
| OCR 失败只写 capture_items 错误字段 | ✓ `error_code` + `error_message_safe` |
| AI 失败只写 capture_items 错误字段 | ✓ |
| 转换失败事务回滚 | ✓ `get_db` 自动 rollback |
| 失败不创建 mistake_draft/mistake/review_item | ✓ 安全检查确认 |

### 5. 信息安全

| 检查项 | 结果 |
| --- | --- |
| CaptureOut 不含 storage_key | ✓ |
| CaptureOut 不含 raw_output | ✓ |
| CaptureOut 不含 model_key/api_key | ✓ |
| error_message_safe 字段 ≤300 字符 | ✓ `String(300)` |
| adapter 错误信息截断 `str(e)[:200]` | ✓ |
| 错误消息为通用描述，不含堆栈 | ✓ |

### 6. AUTH_BYPASS 不依赖

| 检查项 | 结果 |
| --- | --- |
| captures router 使用 `get_current_admin`（JWT） | ✓ |
| 不依赖 `AUTH_BYPASS` 环境变量 | ✓ |

### 结论

P0-07 完成。所有权限、公开边界和失败隔离验证通过。可进入 P0-08。

## P0-08 测试与验收方案（已完成）

### 1. pytest 定向测试

| 测试文件 | 测试数 | 结果 |
| --- | --- | --- |
| `tests/test_capture_service.py` | 12 | 12 passed |
| `tests/test_anon_capture_access.py` | 2 | 2 passed |

**test_capture_service.py 覆盖场景：**

| 测试 | 场景 |
| --- | --- |
| test_create_capture_sets_uploaded_status | 创建 capture，验证 uploaded 状态 |
| test_get_capture_raises_for_missing_id | 不存在的 ID 抛异常 |
| test_list_captures_returns_list | 列出 capture |
| test_recognition_with_fake_succeeds | fake OCR 成功 |
| test_draft_with_fake_succeeds | fake AI 草稿成功 |
| test_patch_capture_manual_path | 手动编辑题面后自动进入 ready |
| test_patch_capture_clears_failed_status | failed 状态编辑后清除错误 |
| test_convert_is_idempotent | 重复转换返回同一草稿 |
| test_convert_requires_ready_status | 非 ready 状态拒绝转换 |
| test_recognition_failure_zero_pollution | OCR 失败下游零污染 |
| test_draft_failure_zero_pollution | AI 失败下游零污染（mock 模拟） |
| test_convert_creates_drafts_not_mistakes | 转换只创建草稿不创建正式 mistake/review_item |

**test_anon_capture_access.py 覆盖场景：**

| 测试 | 场景 |
| --- | --- |
| test_anon_capture_endpoints_denied | 7 个 capture 端点无认证返回 401/403 |
| test_public_notes_api_works | 公开 GET /api/notes 不受影响 |

### 2. Alembic current / heads / upgrade

| 检查项 | 结果 |
| --- | --- |
| `alembic current` | `015 (head)` |
| `alembic heads` | `015 (head)` |
| 迁移文件 | `015_add_capture_items.py` |
| upgrade 状态 | 已成功升级到 015 |

### 3. schema / constraint / index inspection

| 检查项 | 结果 |
| --- | --- |
| 列数 | 21 列全部存在，类型正确 |
| 约束数 | 10 个（4 FK + 1 PK + 4 CHECK + 1 UNIQUE） |
| 索引数 | 4 个（1 PK + 2 普通 + 1 UNIQUE） |
| ck_capture_items_status | 8 种状态 CHECK |
| ck_capture_items_conversion | converted 必须有 mistake_draft_item_id |
| ck_capture_items_attempt_count | attempt_count >= 0 |
| ck_capture_items_last_stage | last_stage IN ('recognize','draft','convert') 或 NULL |
| uq_capture_items_mistake_draft | mistake_draft_item_id UNIQUE（幂等防重） |

### 4. fake adapter 成功 / 失败 / 超时 / schema 异常测试

| 场景 | 测试 | 结果 |
| --- | --- | --- |
| fake 成功 | test_recognition_with_fake_succeeds / test_draft_with_fake_succeeds | ✓ |
| fake 失败零污染 | test_recognition_failure_zero_pollution | ✓ OCR 失败（无真实凭据 1x1 PNG） |
| AI 失败零污染 | test_draft_failure_zero_pollution（mock provider_error） | ✓ |
| 状态校验 | test_convert_requires_ready_status | ✓ |

### 5. capture → mistake_draft 幂等转换测试

| 检查项 | 结果 |
| --- | --- |
| 首次转换创建 mistake_draft | ✓ |
| 重复转换返回同一 mistake_draft_item_id | ✓ |
| 转换后 capture.status = converted | ✓ |
| question_draft_id 正确返回 | ✓ |

### 6. 失败零污染测试

| 场景 | mistakes | mistake_drafts | review_items | draft_items |
| --- | --- | --- | --- | --- |
| OCR 失败前后 | 不变 | 不变 | 不变 | 不变 |
| AI 失败前后（mock） | 不变 | 不变 | 不变 | 不变 |
| 转换只建草稿 | 不变 | +1 | 不变 | +2 |

### 7. 匿名访问拒绝测试

| 端点 | 方法 | 状态码 |
| --- | --- | --- |
| /api/admin/captures | GET | 401 |
| /api/admin/captures | POST | 401 |
| /api/admin/captures/{id} | GET | 401 |
| /api/admin/captures/{id} | PATCH | 401 |
| /api/admin/captures/{id}/recognize | POST | 401 |
| /api/admin/captures/{id}/draft | POST | 401 |
| /api/admin/captures/{id}/convert | POST | 401 |

所有端点在无 Authorization header 时返回 401。AUTH_BYPASS 未设置。

### 8. 公开页面回归

| 检查项 | 结果 |
| --- | --- |
| 公开页面不引用 captures API | ✓ grep 确认 |
| 公开 GET /api/notes 返回 200 | ✓ |
| TestClient + asyncpg 事件循环兼容性 | 已知问题，与 capture 无关 |

### 9. TSC

| 检查项 | 结果 |
| --- | --- |
| `npx tsc --noEmit` | 无错误 |

### 10. build

| 检查项 | 结果 |
| --- | --- |
| `npm run build` | 成功 |
| `/manage/capture` 路由 | ✓ 已构建（静态预渲染） |

### 11. 真实浏览器单图流程

**真实 AI/OCR：not verified**

原因：环境中存在 DASHSCOPE_API_KEY、DEEPSEEK_API_KEY、AI_API_KEY，但：
- deepseek API 返回 400 错误（模型名称不被支持："The supported API model names are deepseek-v4-pro or deepse..."）
- 回退到其他供应商时 30 秒超时
- 无法完成真实 AI 草稿生成

根据用户批准要求：「如果没有真实可用的 OCR / 多模态模型凭据，则可以用 fake adapter 完成 service、schema、状态机和失败隔离测试，但不能宣称真实 AI/OCR 闭环通过。」

**结论：真实 AI/OCR 闭环未验证。** 所有自动化测试使用 fake adapter 和 mock 完成，service/schema/状态机/失败隔离/权限验证均已通过。

### 12. git diff --check

| 检查项 | 结果 |
| --- | --- |
| 空白错误 | 无 |

### 13. git diff --name-only

**Batch 8 修改文件：**

| 文件 | 类型 |
| --- | --- |
| `backend/app/models/__init__.py` | 修改（注册 CaptureItem） |
| `backend/main.py` | 修改（注册 captures 路由） |
| `src/app/manage/components/manage-sidebar.tsx` | 修改（添加采集导航入口） |
| `backend/alembic/versions/015_add_capture_items.py` | 新增 |
| `backend/app/models/capture.py` | 新增 |
| `backend/app/routers/captures.py` | 新增 |
| `backend/app/schemas/capture.py` | 新增 |
| `backend/app/services/capture_ai_draft.py` | 新增 |
| `backend/app/services/capture_recognition.py` | 新增 |
| `backend/app/services/capture_service.py` | 新增 |
| `backend/tests/test_capture_service.py` | 新增 |
| `backend/tests/test_anon_capture_access.py` | 新增 |
| `src/lib/api/captures.ts` | 新增 |
| `src/app/manage/(workspace)/capture/page.tsx` | 新增 |
| `src/app/manage/(workspace)/capture/components/capture-workspace.tsx` | 新增 |

### 14. 禁止项搜索

| 禁止项 | 搜索结果 |
| --- | --- |
| capture_service 调用 convert_mistake_draft | ✓ 仅注释中提及，无实际调用 |
| capture_service 导入 Mistake/ReviewItem 模型 | ✓ 未找到 |
| CaptureOut 含 storage_key/raw_output/api_key | ✓ 未找到 |
| 公开 /api/captures 路由 | ✓ 未找到 |
| 公开页面引用 captures API | ✓ 未找到 |
| create_all 代替迁移 | ✓ capture_service 中未找到 |
| 批量 OCR / PDF 拆题 | ✓ services 目录中未找到 |

### 结论

P0-08 完成。14 项验证全部执行并记录。

**真实 AI/OCR：not verified**（deepseek API 模型名称过期，回退供应商超时）。

所有自动化测试（14 passed）、schema/约束/索引检查、Alembic 验证、TSC、build、匿名拒绝、禁止项搜索均通过。可进入 P0-09。

## P0-09 handoff 与下一批接口预留（已完成）

### 1. 实现范围记录

| 范围 | 状态 |
| --- | --- |
| capture_items 数据模型 | ✓ 21 字段，10 约束，4 索引，迁移 015 |
| OCR 窄 adapter（capture_recognition.py） | ✓ 封装 call_ocr_model，6 种错误分类 |
| AI 草稿窄 adapter（capture_ai_draft.py） | ✓ 封装 call_text_model，MistakeDraftSuggestionV1 |
| capture_service.py | ✓ 7 函数 + 4 异常类 + ConvertResult |
| captures.py 路由 | ✓ 7 端点，admin-only |
| capture.py schema | ✓ CaptureCreate/Patch/Convert/Out + ConvertResultOut |
| 前端 captures.ts API 客户端 | ✓ 类型与函数 |
| 前端 /manage/capture 页面 | ✓ 采集工作台组件 |
| manage-sidebar 导航入口 | ✓ Camera 图标 |
| 定向测试 | ✓ 12 + 2 = 14 passed |

### 2. 未验证项

| 未验证项 | 原因 | 标注 |
| --- | --- | --- |
| 真实 OCR 识别 | 未测试真实图片 OCR | not verified |
| 真实 AI 草稿生成 | deepseek API 模型名称过期，回退供应商超时 | not verified |
| 真实浏览器单图流程 | 依赖真实 AI/OCR，不可用 | not verified |

### 3. Batch 9 Gateway adapter 接口预留

| 接口 | 当前实现 | Batch 9 替换策略 |
| --- | --- | --- |
| `recognize_image(image_bytes, mime_type, *, use_fake, fake_text) -> RecognitionResult` | `capture_recognition.py` 封装 `call_ocr_model` | Gateway 内核可替换内部实现，签名不变 |
| `draft_mistake(draft_input, *, use_fake) -> DraftResult` | `capture_ai_draft.py` 封装 `call_text_model` | Gateway 内核可替换内部实现，签名不变 |
| `CaptureDraftInput` / `MistakeDraftSuggestionV1` | `schemas/capture.py` | schema 稳定，不修改 |
| `convert_capture(session, capture_id, payload, *, created_by)` | `capture_service.py` | 转换流程稳定，不修改 |
| `/api/admin/captures/*` (7 端点) | `routers/captures.py` | 路由稳定，不修改 |

### 4. Batch 10-12 后置项

| 批次 | 后置项 | Batch 8 是否提前实现 |
| --- | --- | --- |
| Batch 10 | Task / Prompt / Validator 管理 | 否 |
| Batch 11 | AI Run 审计与人工流转 | 否 |
| Batch 12 | 多供应商、路由、成本与稳定性治理 | 否 |

### 5. 范围 diff 验证

| 检查项 | 结果 |
| --- | --- |
| git diff --check | 无空白错误 |
| git diff --name-only | 3 修改 + 12 新增，均为 Batch 8 范围内 |
| 未修改既有业务代码 | ✓ capture_service 不修改 mistake_service/draft_service/ai_service |
| 未修改旧 AI 路由 | ✓ routers/ai.py 未修改 |
| 未修改旧 staged service | ✓ mistake_staged_service.py 未修改 |

### 6. 禁止项交叉审查

| 禁止项 | 代码搜索 | 文档交叉审查 |
| --- | --- | --- |
| 完整 AI Gateway | ✓ 未实现 | ✓ handoff 明确后置 Batch 9 |
| 多供应商管理 | ✓ 未实现 | ✓ handoff 明确后置 Batch 12 |
| 模型路由 | ✓ 未实现 | ✓ handoff 明确后置 Batch 12 |
| Prompt 管理后台 | ✓ 未实现 | ✓ handoff 明确后置 Batch 10 |
| 成本统计 | ✓ 未实现 | ✓ handoff 明确后置 Batch 12 |
| 完整 AI 审计 | ✓ 未实现 | ✓ handoff 明确后置 Batch 11 |
| BKT | ✓ 未实现 | ✓ 未在范围内 |
| 完整练习系统 | ✓ 未实现 | ✓ 未在范围内 |
| 批量 OCR | ✓ 未实现 | ✓ grep 确认 |
| PDF 多页拆题 | ✓ 未实现 | ✓ grep 确认 |
| 公开 AI/OCR 结果 | ✓ 未公开 | ✓ grep + 匿名测试确认 |
| 旧 Note(type="mistake") 迁移 | ✓ 未迁移 | ✓ 未在范围内 |
| 对象存储 | ✓ 未引入 | ✓ 使用本地存储 |
| 云部署 | ✓ 未引入 | ✓ 未在范围内 |
| 生产级任务队列 | ✓ 未引入 | ✓ 使用同步调用 |

### 7. 文档更新记录

| 文档 | 更新内容 |
| --- | --- |
| README.md | 当前状态从“待批准”更新为“已完成，待用户验收” |
| handoff.md | 当前结论、接口路线、证据交付表 |
| risks.md | 8 项风险状态全部更新为已处理/已缓解/已确认 |
| tasks.md | P0-01 至 P0-09 全部标记 [x] |
| checklist.md | D/E 部分全部标记完成，审批结论更新 |
| validation.md | P0-01 至 P0-09 验证记录完整 |

### 结论

P0-09 完成。Batch 8 全部任务（P0-01 至 P0-09）已完成。

**最终状态：Batch 8 待用户验收。**

- 不自行启动 Batch 9。
- 不宣称完整 AI 系统完成。
- 不宣称完整 AI Gateway 完成。
- 真实 AI/OCR：not verified。
