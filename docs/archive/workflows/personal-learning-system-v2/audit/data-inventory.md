# Phase A A-01 数据源与实体盘点

## Summary

审计时间：2026-07-13  
审计方式：只读源码扫描、只读数据库查询、Alembic 状态检查、文件系统清单检查。  
当前判断：系统已经同时存在旧 `notes` 内容模型、独立题目/错题/复习模型、管理内容 JSON、附件/Capture 草稿链和 AI 审计链。PostgreSQL 是当前主要后端数据源，但尚不能据此证明所有正式内容都已由 PostgreSQL 唯一写入。

数据库当前 Alembic 版本为 `018 (head)`。本次查询没有执行写入、migration 或 `create_all`。

## Evidence

### 数据库实体清单

数量来自当前连接数据库的只读 `SELECT count(*)`；字段来自 `information_schema.columns`。数量是当前快照，不代表迁移目标数量。

| 实体 | 当前表 | 来源文件 | 主键 | 实际数量 | 当前职责 | 是否事实来源 | 风险 |
|---|---|---|---|---:|---|---|---|
| Note | `notes` | `backend/app/models/note.py:32` | UUID `id` | 13 | 博客、笔记、错题兼容模型；含错题字段和复习字段 | 是，旧内容线 | 一个表承载多种语义；没有 `owner_id` |
| Managed content | `managed_content_entries` | `backend/app/models/content.py:10` | `key` | 5 | about、shares、projects、pictures、snippets、bloggers、site-settings 等 JSON 内容 | 是，管理内容线 | `key/data` 无统一内容版本模型 |
| Question | `questions` | `backend/app/models/question.py:129` | UUID `id` | 3 | 正式题目本体 | 是 | 题目与旧 Note 内容线并存 |
| Question draft | `question_drafts` | `backend/app/models/question.py:86` | UUID `id` | 3 | 题目审核草稿 | 是 | 草稿与正式对象转换链需持续审计 |
| Draft item | `draft_items` | `backend/app/models/question.py:32` | UUID `id` | 6 | 通用草稿状态、来源、目标和校验错误 | 是 | `target_type/target_id` 跨域多态关联 |
| Mistake | `mistakes` | `backend/app/models/mistake.py:58` | UUID `id` | 3 | 独立正式错题 | 是 | 与 `Note(type='mistake')` 并存 |
| Mistake draft | `mistake_drafts` | `backend/app/models/mistake.py:11` | UUID `id` | 3 | 错题审核草稿 | 是 | 同时引用 question/question_draft |
| Review item | `review_items` | `backend/app/models/review_item.py:11` | UUID `id` | 3 | 独立复习项和调度状态 | 是 | 另有旧 `notes.next_review` 复习字段 |
| Review record | `review_records` | `backend/app/models/review_item.py:37` | UUID `id` | 4 | 独立复习事件 | 是 | 旧 Review API 仍以 Note 逻辑为主 |
| User | `users` | `backend/app/models/note.py:112` | UUID `id` | 6 | 账户和管理员标识 | 是 | 主要内容模型未统一 owner 约束 |
| Attachment | `attachments` | `backend/app/models/attachment.py:20` | UUID `id` | 1 | 私有文件元数据、hash、storage key | 是 | `storage_provider` 当前约束为 local；实际备份未证实 |
| Attachment link | `attachment_links` | `backend/app/models/attachment.py:62` | UUID `id` | 1 | 附件与业务对象的多态关联 | 是 | `target_type/target_id` 需逐对象校验 |
| Capture item | `capture_items` | `backend/app/models/capture.py:21` | UUID `id` | 0 | 图片识别、草稿和转换状态 | 是 | 当前无记录，不能证明流程已真实运行 |
| AI run | `ai_runs` | `backend/app/models/ai_run.py:11` | UUID `id` | 20 | AI 业务运行、验证和人工审核状态 | 是 | 输入/输出快照需继续核验敏感字段过滤 |
| AI call log | `ai_call_logs` | `backend/app/models/ai_call_log.py:11` | UUID `id` | 35 | Provider 调用、耗时、fallback、成本字段 | 是 | 与 AI Run 为两套审计粒度 |
| Audit log | `audit_logs` | `backend/app/models/audit.py:11` | UUID `id` | 99 | 登录和管理操作审计 | 是 | `before/after` 需要敏感字段审查 |
| Admin session | `admin_sessions` | `backend/app/models/session.py:12` | UUID `id` | 31 | cookie session、认证级别、撤销和过期 | 是 | 当前是 session cookie，不是 JWT 实现 |
| Folder | `folders` | `backend/app/models/folder.py:19` | UUID `id` | 2 | Note 文件夹层级 | 是 | 旧内容组织方式，与知识节点并存 |
| Subject | `subjects` | `backend/app/models/note.py:88` | integer `id` | 1 | 科目 taxonomy | 是 | 题目/错题/采集使用；Note 仍有字符串 subject |
| Chapter | `chapters` | `backend/app/models/taxonomy.py:20` | integer `id` | 0 | 科目章节 | 是 | 当前暂无记录 |
| Knowledge point | `knowledge_points` | `backend/app/models/taxonomy.py:46` | integer `id` | 3 | 当前知识点 taxonomy | 是 | 与 V2 KnowledgeNode 尚未统一 |
| Knowledge point link | `knowledge_point_links` | `backend/app/models/taxonomy.py:78` | UUID `id` | 6 | 知识点与 note/mistake 等目标关联 | 是 | 多态 link 不是 V2 edge 模型 |
| Tag | `tags` | `backend/app/models/note.py:79` | integer `id` | 34 | Note 标签 | 是 | 标签与知识别名、taxonomy 分离 |
| Category | `categories` | `backend/app/models/note.py:104` | integer `id` | 0 | 内容分类 | 是 | 与 subject/folder 并存 |

### Model / migration 证据

- `backend/app/models/note.py:32-76`：`notes` 同时保存 `type`、正文、错题字段、SM-2 字段、图片、AI metadata 和 folder。
- `backend/app/models/mistake.py:58-79`：独立 `mistakes` 表已经存在。
- `backend/app/models/review_item.py:11-48`：独立 `review_items` 和 `review_records` 已存在。
- `backend/app/models/taxonomy.py:46-91`：当前知识模型是 `knowledge_points` 和 `knowledge_point_links`。
- `backend/alembic/versions/012_add_question_drafts_and_questions.py`：题目/草稿链从 migration 012 开始。
- `backend/alembic/versions/013_add_mistakes_and_review.py`：错题、复习链从 migration 013 开始。
- `backend/alembic/versions/014_add_attachments.py`：附件表从 migration 014 开始。
- `backend/alembic/versions/015_add_capture_items.py`：Capture 表从 migration 015 开始。
- `backend/alembic/versions/016_add_ai_call_logs.py` 与 `018_add_ai_runs.py`：AI 调用和业务 Run 分开记录。

### 文件系统清单

只读扫描范围：`src/`、`backend/`、`docs/`、`public/`、`uploads/`、`attachments/`、`scripts/`。当前统计约为：423 个 Markdown 文件、17 个 JSON 文件、63 个图片文件。`backend/uploads/` 存在，当前约 8 KB；仓库根层未发现名为 `attachments/` 或 `backups/` 的业务目录。

| 来源 | 代表路径 | 类型 | 用途 | 是否可能为主数据 | 证据 |
|---|---|---|---|---|---|
| 前端静态内容 | `public/`、`public/blogs/`、`public/images/` | Markdown/JSON/图片 | 公开站点和静态资源 | 是，公开内容/构建输入 | `find` 清单、`src/app/blog` |
| Next.js route data | `src/app/*/list.json` | JSON | share、snippets、pictures、music 等页面数据 | 可能 | `src/app/share/list.json` 等 |
| 后端上传 | `backend/uploads/` | 图片/附件 | 后端上传内容 | 是，附件候选 | `backend/app/config.py:30` |
| 文档架构数据 | `docs/architecture/` | Markdown | 目标设计和历史方案 | 否 | 文档状态声明为目标架构 |
| 审计/流程文档 | `docs/workflows/` | Markdown | 流程证据和任务记录 | 否 | workflow 目录结构 |
| 构建/缓存产物 | `.next/`、`.open-next/`、`.pytest_cache/` | JSON/JS/cache | 生成产物 | 否 | 排除出主数据审计 |
| 脚本导出 | `scripts/`、`src/app/*/services/` | TS/JS/Python | 推送、导出或页面数据更新 | 可能 | `rg -i 'github|sync|export|push'` |

### GitHub / Markdown 数据流

扫描结果确认仓库中存在多类 GitHub/推送/导出相关引用，包含：

- `src/app/blog/services/push-blog.ts`
- `src/app/share/services/push-shares.ts`
- `src/app/snippets/services/push-snippets.ts`
- `src/app/pictures/services/push-pictures.ts`
- `src/app/write/services/push-blog.ts`
- `backend/app/services/content_store.py`
- `docs/backup-restore.md` 对“公开导出”和“私有 `pg_dump`”作了概念分离。

当前可确认：GitHub/Markdown 工作流仍存在，且静态内容与 PostgreSQL 内容模型并存。当前不能仅凭静态扫描证明所有写入都已收敛到 PostgreSQL；需要下一阶段逐个函数做写入方向确认。

## Risk

| ID | 风险 | 严重程度 | 影响 | 建议 |
|---|---|---|---|---|
| A01-DATA-001 | `notes` 与独立 `questions/mistakes/review_items` 并存 | 高 | 迁移去重、权限、复习事实和公开读取 | Phase B 前建立实体映射和唯一事实规则 |
| A01-DATA-002 | `managed_content_entries` 使用 `key/data` 保存管理内容 | 中 | 版本、审计、发布快照和正文检索 | 明确其是否迁移到统一 ContentItem |
| A01-DATA-003 | 当前 taxonomy 使用 `knowledge_points`，目标设计使用 KnowledgeNode | 高 | 关系、别名、图谱和跨域关联 | 单独制定 taxonomy 到 KnowledgeNode 映射 |
| A01-DATA-004 | GitHub/静态文件仍有推送入口 | 高 | 双主数据、幽灵内容、人工冲突 | 逐个写入口审计后冻结唯一写源 |
| A01-DATA-005 | 内容模型未统一 `owner_id` | 高 | 私有内容隔离和迁移安全 | Phase B 先建立 owner 覆盖矩阵 |
| A01-DATA-006 | `capture_items` 当前数量为 0 | 中 | 无法用当前数据证明 OCR/Capture 生产闭环 | 记录为流程证据缺口，不在本阶段修复 |

## Next Step

1. 将本报告与 A-02 权限矩阵、A-03 迁移门槛交叉核对。
2. 在 Phase B 设计中为每个旧实体指定保留、迁移、兼容或归档策略。
3. 在任何迁移前先获得独立批准，不执行删除或双源切换。

