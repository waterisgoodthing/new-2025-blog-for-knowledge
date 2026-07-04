# 设计文档：Batch 3 题目草稿 / 审核 / 题库

## 1. 架构决定

采用“独立新模型 + 旧 Note 原样共存”：

```text
手工录入
  → DraftItem + QuestionDraft
  → 人工编辑 / 拒绝
  → convert(version)
  → Question + QuestionSource(manual)
  → DraftItem(converted, target_id)
```

本批不读取旧 Note 生成 Question，不建立双写，不修改 `Note(type="mistake")`。Batch 4
需要 Question/Mistake 兼容时必须另行设计和审批。

## 2. 数据设计

### `draft_items`

- `id UUID` 主键
- `draft_type`：本批仅 `question`
- `source_type`：本批仅 `manual`
- `source_id`：可空字符串引用，manual 默认空
- `status`：`pending | needs_fix | rejected | converted`
- `version`：从 1 开始，每次可编辑修改递增
- `validation_errors JSON`：结构化字段错误，默认空数组
- `target_type` / `target_id`：转换后为 `question` / Question UUID
- `created_by UUID`：引用 users
- `created_at` / `updated_at`

约束：converted 必须有 target；未 converted 不得有 target；version > 0。索引：
status + updated_at、draft_type + status。

### `question_drafts`

- `id UUID` 主键
- `draft_item_id UUID`：唯一、非空、CASCADE
- `subject_id`：引用 subjects，删除 RESTRICT
- `title` 可空
- `question_text` 非空
- `question_type`：`single_choice | multiple_choice | true_false | short_answer | essay`
- `options JSON`：选择题为字符串数组，其他题型为空数组
- `correct_answer`、`explanation` 可空
- `difficulty`：`easy | medium | hard`，可空
- `created_at` / `updated_at`

知识点不存 JSON ID 数组，复用 `knowledge_point_links`：
`target_type=question_draft, target_id=<draft UUID>`。

### `questions`

- 字段与 QuestionDraft 的正式题目字段对应
- `status`：`active | archived`
- `visibility`：本批固定 `private`
- `version`：从 1 开始
- 时间戳

知识点使用 `knowledge_point_links(target_type=question)`。

### `question_sources`

- `id UUID`、`question_id UUID`
- `source_type`：本批仅 `manual`
- `source_name` 可空，默认“手工录入”
- `source_ref`：保存来源 DraftItem UUID
- `created_at`

唯一约束 `(source_type, source_ref)` 作为转换第二道幂等保护。

### 删除与关系

- Draft/Question 不物理删除正式数据：草稿拒绝、Question 归档。
- Subject/KnowledgePoint 的既有删除冲突检查需覆盖 question/question_draft link 和 Question
  外键，不自动级联删除。
- `knowledge_point_links.target_id` 长度 64，UUID 字符串可直接使用。

## 3. 转换事务

1. `SELECT draft_items ... FOR UPDATE`。
2. 若已 converted：读取 target Question 并直接返回。
3. 比对请求 version；不一致返回 domain conflict。
4. 加载 QuestionDraft、Subject、KnowledgePoint links 并重新校验。
5. 创建 Question。
6. 创建 `QuestionSource(source_type=manual, source_ref=draft_item.id)`。
7. 复制 draft 的 knowledge point links 为 question links。
8. 设置 DraftItem status=converted、target_type=question、target_id、version+1。
9. flush；由请求数据库 session 统一 commit，异常整体 rollback。

不保留长期 `approved` 中间态，确认与转换是同一命令。

## 4. API 设计

全部使用 `get_current_admin`。

### Drafts

- `GET /api/admin/drafts?draft_type=question&status=...`
- `POST /api/admin/drafts/questions`
- `GET /api/admin/drafts/{id}`
- `PUT /api/admin/drafts/{id}`：body 含 version
- `POST /api/admin/drafts/{id}/reject`：body 含 version
- `POST /api/admin/drafts/{id}/convert`：body 含 version

### Questions

- `GET /api/admin/questions?subject_id=&status=`
- `GET /api/admin/questions/{id}`
- `PUT /api/admin/questions/{id}`：body 含 version
- `DELETE /api/admin/questions/{id}`：语义为归档，返回更新后的资源或 204

本批不提供 `POST /api/admin/questions`，防止绕过草稿审核。错误映射：
校验 400/422、不存在 404、状态/版本/重复冲突 409、未登录 401。

## 5. 前端设计

### `/manage/drafts`

- 紧凑列表：状态、题干摘要、科目、题型、更新时间。
- 顶部提供“手工创建题目草稿”表单/入口。
- 筛选 pending、needs_fix、rejected、converted。
- loading、empty、error 明确。

### `/manage/drafts/[id]`

- 编辑题干、题型、选项、答案、解析、难度、科目和正式知识点。
- 保存使用当前 version；409 时提示刷新，不静默覆盖。
- 主操作为“确认并转入题库”；次操作为“拒绝草稿”，均二次确认。
- converted 后只读展示目标 Question 链接。

### `/manage/questions`

- 正式题目列表，按科目/状态筛选。
- 不显示 pending/rejected 草稿。

### `/manage/questions/[id]`

- 编辑正式题目与知识点，使用 version。
- 展示 manual 来源和来源草稿链接。
- “归档”需确认，不物理删除。

路由页面只组合；域组件放各自 route `components/`，API 统一放
`src/lib/api/questions.ts` 和 `src/lib/api/drafts.ts`。复用 Batch 2 taxonomy 客户端，
必要时扩展 `KnowledgePointSelect` 为多选但不重构无关组件。

## 6. 权限与异常

- `/manage/**` 继续由既有 workspace AuthGate 保护。
- admin API 的 router 级 dependency 覆盖 GET 和写操作。
- 页面会话失效交给既有 API/AuthGate 处理。
- 表单网络失败保留输入。
- 草稿状态冲突、version 冲突、跨科目知识点分别显示可理解错误。
- 不使用 AUTH_BYPASS；真实浏览器可使用批准的一次性管理员。

## 7. 迁移与恢复

- 新增 `012_add_question_drafts_and_questions.py`，只创建新表/约束/索引。
- migration 前确认 current 011、head 012；inspect 目标表不存在，若意外存在则停止并盘点，
  不仿照历史漂移盲目覆盖。
- 012 不触碰旧 Note 或旧真实数据。
- 验证正常 011 → 012、重复 `upgrade head`、schema/constraint/index 和旧数据计数。
- 执行前创建仓库外数据库备份，验证完成后删除。

## 8. 安全与合规

- 题目与草稿默认私有，无 public endpoint。
- 不保存附件本地路径、AI 输入、OCR 内容或外部密钥。
- source_ref 只保存内部 Draft UUID。
- options 必须为受控字符串数组，拒绝任意 HTML/object payload。
- 转换、拒绝、归档均保留可追溯状态、版本、来源与时间戳。

## 9. 明确暂缓

AI/OCR、附件、Capture Router、批审、自动去重/合并、搜索、公开题库、练习、错题、
复习，以及旧 Note 数据迁移。
