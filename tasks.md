# 闭环修复任务清单

> 来源：`design.md`。按优先级分组，组内按建议执行顺序排列。

---

## 禁止事项（全局）

以下操作在任何任务中均不得执行，除非任务卡明确允许：

- 不修改 `.env`、密钥、数据库连接配置、部署脚本、Cloudflare 配置
- 不执行 `alembic upgrade` / `alembic downgrade`（除非任务卡明确要求）
- 不执行 `npm install` / `pnpm add` / `yarn add`
- 不执行 `git add` / `git commit` / `git push`
- 不实现 Mermaid
- 不实现 AI 图片生成
- 不替换编辑器

---

## P0-A：低风险闭环修复

> 不修改数据库。不新增 Alembic 迁移。不改博客发布链路。不引入新依赖。
> 允许修改后端查询逻辑和 API 参数，但不得修改数据库模型，不得新增迁移。
> P0-A 任务在业务逻辑上互无强依赖，但多个任务修改同一批文件，建议按顺序执行，或由同一个智能体一次性完成。

---

### T-01 笔记编辑器 Markdown 预览

前置依赖：无

新建文件

- [ ] `src/app/write-note/hooks/use-note-editor-tab.ts` — Tab 切换 hook
- [ ] `src/app/write-note/components/note-preview-content.tsx` — 预览内容组件，复用 `useMarkdownRender`

修改文件

- [ ] `src/app/write-note/page.tsx` — 增加编辑/预览 Tab 切换条；编辑模式显示 textarea，预览模式显示 NotePreviewContent；快捷键 Ctrl/Cmd + P 切换
- [ ] `src/app/write-note/[slug]/page.tsx` — 同上

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/write-note/hooks/use-note-editor-tab.ts` | 新建 |
| `src/app/write-note/components/note-preview-content.tsx` | 新建 |
| `src/app/write-note/page.tsx` | 修改 |
| `src/app/write-note/[slug]/page.tsx` | 修改 |

验收标准

- [ ] 点击"编辑"/"预览" Tab 正确切换
- [ ] 预览模式正确渲染代码块（Shiki）、LaTeX（KaTeX）、图片
- [ ] Ctrl/Cmd + P 可切换编辑/预览
- [ ] mistake 类型预览使用拼接后的 Markdown content
- [ ] 保存功能不受影响

---

### T-02 笔记编辑器图片 URL 插入

前置依赖：无

修改文件

- [ ] `src/app/write-note/page.tsx` — textarea 上方增加工具栏；实现 `insertAtCursor` 光标插入逻辑；图片按钮弹出 URL 输入，插入 `![](url)`（必做）
- [ ] `src/app/write-note/[slug]/page.tsx` — 同上
- [ ] 工具栏可选扩展：加粗、斜体、代码按钮（实现成本低再做，非必做）

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/write-note/page.tsx` | 修改 |
| `src/app/write-note/[slug]/page.tsx` | 修改 |

验收标准

- [ ] 图片按钮弹出 URL 输入，插入 `![](url)` 到光标位置（必做）
- [ ] 详情页正确展示通过 URL 插入的图片（必做）
- [ ] 加粗/斜体/代码按钮在选中文本两端插入标记（可选）

---

### T-03 笔记表单增加分类字段

前置依赖：无

修改文件

- [ ] `src/app/write-note/page.tsx` — 加载 `listCategories()`，在标签输入下方增加 `<select>` 分类下拉；handleSave 传递 category
- [ ] `src/app/write-note/[slug]/page.tsx` — 同上，编辑时从 note.category 初始化

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/write-note/page.tsx` | 修改 |
| `src/app/write-note/[slug]/page.tsx` | 修改 |

验收标准

- [ ] 创建笔记时可从下拉选择分类
- [ ] 可选择"无分类"
- [ ] 保存后列表页和详情页正确展示 category
- [ ] 编辑时 category 正确回填

---

### T-04 笔记表单增加封面字段

前置依赖：无

修改文件

- [ ] `src/app/write-note/page.tsx` — 增加 cover URL 输入框和封面预览图；handleSave 传递 cover
- [ ] `src/app/write-note/[slug]/page.tsx` — 同上

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/write-note/page.tsx` | 修改 |
| `src/app/write-note/[slug]/page.tsx` | 修改 |

验收标准

- [ ] 可填写 cover URL
- [ ] 保存后后端返回 cover，编辑页可回填
- [ ] 详情页如已有展示位则展示，不做大规模详情页重构

---

### T-05 科目字段改为 datalist

前置依赖：无

修改文件

- [ ] `src/app/write-note/page.tsx` — subject 输入改为 `<input list="subject-options">` + `<datalist>`，数据来自 `listSubjects()`
- [ ] `src/app/write-note/[slug]/page.tsx` — 同上
- [ ] `src/app/write-mistake/page.tsx` — 同上

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/write-note/page.tsx` | 修改 |
| `src/app/write-note/[slug]/page.tsx` | 修改 |
| `src/app/write-mistake/page.tsx` | 修改 |

验收标准

- [ ] Subject 输入框有下拉建议列表
- [ ] 可从列表中选择已有科目
- [ ] 可手动输入新科目
- [ ] 保存后 subject 字段正确持久化
- [ ] 本任务只保证 Note.subject 字段持久化，不要求自动创建 Subject 表记录

---

### T-06 错题难度后端筛选

前置依赖：无

后端

- [ ] `backend/app/routers/notes.py` — list_notes 增加 `difficulty: Optional[str] = None` 参数，有值时 `query.where(Note.difficulty == difficulty)`

前端

- [ ] `src/lib/api/notes.ts` — NoteListParams 增加 `difficulty?: "easy" | "medium" | "hard"`
- [ ] `src/app/mistakes/page.tsx` — useNoteIndex 传入 difficulty 参数；删除前端 `.filter()` 逻辑，直接使用 `data?.items`

涉及文件

| 文件 | 变更类型 |
|---|---|
| `backend/app/routers/notes.py` | 修改 |
| `src/lib/api/notes.ts` | 修改 |
| `src/app/mistakes/page.tsx` | 修改 |

验收标准

- [ ] `GET /api/notes?type=mistake&difficulty=easy` 正确返回 easy 难度错题
- [ ] 翻页后筛选仍然有效（不再是只过滤当前页）
- [ ] 不传 difficulty 时返回全部难度

---

### T-07 清理错题冗余路由

前置依赖：无

- [ ] 删除 `src/app/mistakes/[id]/` 空目录
- [ ] 删除 `src/app/write-mistake/[slug]/` 空目录
- [ ] `src/app/notes/[id]/page.tsx` — 返回链接根据 note.type 判断：`mistake` → `/mistakes`，其他 → `/notes`

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/mistakes/[id]/` | 删除（空目录） |
| `src/app/write-mistake/[slug]/` | 删除（空目录） |
| `src/app/notes/[id]/page.tsx` | 修改 |

验收标准

- [ ] 空目录已删除，不影响路由
- [ ] 错题详情页返回链接指向 `/mistakes`
- [ ] 笔记详情页返回链接指向 `/notes`

---

### T-08 统一错误提示

前置依赖：无

替换规则

- 错误提示类 `alert()` → `toast.error()`
- 成功提示类 `alert()` → `toast.success()`
- 输入提示类 `alert()` → `toast.warning()`
- `confirm()` 暂时保留，不改变删除确认逻辑

修改文件

- [ ] `src/app/write-note/page.tsx` — handleSave 中的 alert
- [ ] `src/app/write-note/[slug]/page.tsx` — handleSave 中的 alert
- [ ] `src/app/write-mistake/page.tsx` — handleSave、handleImageUpload、handleTextAnalyze 中的 alert
- [ ] `src/app/notes/[id]/page.tsx` — handleDelete catch 中的 alert
- [ ] `src/app/mistakes/review/page.tsx` — handleReview 中的 alert
- [ ] `src/app/manage/page.tsx` — handleDeleteSelected、handleDeleteOne、handleSync 中的 alert

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/write-note/page.tsx` | 修改 |
| `src/app/write-note/[slug]/page.tsx` | 修改 |
| `src/app/write-mistake/page.tsx` | 修改 |
| `src/app/notes/[id]/page.tsx` | 修改 |
| `src/app/mistakes/review/page.tsx` | 修改 |
| `src/app/manage/page.tsx` | 修改 |

验收标准

- [ ] 错误提示类 alert 已替换为 toast.error
- [ ] 成功提示类 alert 已替换为 toast.success
- [ ] confirm() 保留，删除确认逻辑不变
- [ ] 保存失败能显示错误原因
- [ ] AI 分析失败能显示错误原因
- [ ] 复习提交失败能显示错误原因
- [ ] 删除确认逻辑不变

---

## P0-B：博客数据链路迁移专项

> **本组任务不得直接执行。必须先完成 T-09 方案确认。**
>
> 核心原则：
> - PostgreSQL 后端 Note(type=blog) 是唯一主数据源
> - GitHub 静态文件是发布产物，不是数据源
> - 迁移期允许静态文件作为 fallback，但 fallback 数据必须可识别来源
> - 不允许长期维持 GitHub + PostgreSQL 双主数据源

---

### T-09 博客迁移方案确认

前置依赖：无

本任务为决策任务，不涉及代码修改。

需确认事项

- [ ] 确认 PostgreSQL 后端 Note(type=blog) 为唯一主数据源
- [ ] 确认 GitHub 静态文件定位：发布产物 + 迁移期 fallback
- [ ] 确认博客草稿不同步 GitHub（仅 published 同步）
- [ ] 确认旧博客迁移策略：惰性迁移（首次编辑时导入）vs 批量迁移
- [ ] 确认博客图片上传继续走 GitHub（不改图片链路）

涉及文件：无

验收标准

- [ ] 以上 5 项决策已明确记录
- [ ] 决策结果回填到 design.md 第 8 节

---

### T-10 status 字段（依赖 T-09）

前置依赖：T-09

后端

- [ ] `backend/app/models/note.py` — 增加 `status` 字段，String(20)，default "published"，加索引
- [ ] `backend/app/schemas/note.py` — 增加 `NoteStatus` 枚举（draft/published）；NoteCreate、NoteUpdate、NoteOut、NoteListItem 增加 status
- [ ] `backend/app/routers/notes.py` — list_notes 增加 `status: Optional[NoteStatus] = None` 参数
- [ ] 新建迁移 `backend/alembic/versions/002_add_status_field.py`

前端

- [ ] `src/lib/api/notes.ts` — NoteCreateInput、NoteUpdateInput、NoteListParams 增加 status
- [ ] `src/app/notes/page.tsx` — 查询传 `status=published`
- [ ] `src/app/mistakes/page.tsx` — 查询传 `status=published`

涉及文件

| 文件 | 变更类型 |
|---|---|
| `backend/app/models/note.py` | 新增字段 |
| `backend/app/schemas/note.py` | 修改 |
| `backend/app/routers/notes.py` | 修改 |
| `backend/alembic/versions/002_add_status_field.py` | 新建 |
| `src/lib/api/notes.ts` | 修改 |
| `src/app/notes/page.tsx` | 修改 |
| `src/app/mistakes/page.tsx` | 修改 |

验收标准

- [ ] `GET /api/notes?status=draft` 返回草稿
- [ ] `GET /api/notes?status=published` 返回已发布
- [ ] `GET /api/notes` 不传 status 返回全部（兼容）
- [ ] 前端笔记/错题列表只展示 published
- [ ] 管理面板可查看所有状态

---

### T-11 博客写入后端（依赖 T-10）

前置依赖：T-10

后端

- [ ] 验证 `POST /api/notes` type=blog 可正常创建（已支持，仅确认）

前端

- [ ] `src/app/write/services/push-blog.ts` — 发布时先调用 `createNote(type='blog', status='published')`；成功后再执行 GitHub 操作；后端失败则中止，不触发 GitHub
- [ ] `src/app/write/hooks/use-publish.ts` — 适配新流程

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/write/services/push-blog.ts` | 重构 |
| `src/app/write/hooks/use-publish.ts` | 修改 |

验收标准

- [ ] `/write` 发布博客后，`GET /api/notes?type=blog` 可查到
- [ ] GitHub 静态文件同步更新
- [ ] `/blog` 列表行为不变（仍从静态文件加载）
- [ ] 后端写入失败时不触发 GitHub 操作

---

### T-12 博客列表以后端为主数据源（依赖 T-11）

前置依赖：T-11

前端

- [ ] `src/hooks/use-blog-index.ts` — 重写 fetcher：
  - 主数据源：`GET /api/notes?type=blog&status=published`
  - fallback 数据源：`GET /blogs/index.json`
  - 合并规则：以 slug 去重，后端优先
  - 冲突处理：
    - 同 slug 以**后端**为准
    - 后端 status=draft 的记录**不得**被静态 fallback 覆盖重新公开
    - 后端 hidden=true 的记录**不得**被静态 fallback 覆盖重新公开
    - fallback 数据标记来源（如 `_source: 'static'`），便于调试

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/hooks/use-blog-index.ts` | 重构 |

验收标准

- [ ] `/blog` 同时展示旧博客（静态 fallback）和新博客（后端）
- [ ] 同 slug 不重复，后端版本为准
- [ ] 新博客发布后立即出现（不等部署）
- [ ] 后端 draft 记录不出现在公开列表
- [ ] 后端 hidden 记录不出现在公开列表（未登录时）

---

### T-13 博客详情/编辑切换到后端（依赖 T-12）

前置依赖：T-12

前端

- [ ] `src/app/blog/[id]/page.tsx` — 优先 `getNote(slug)` 加载；失败回退 `loadBlog(slug)` 静态文件
- [ ] `src/app/write/[slug]/page.tsx` — loadBlogForEdit 优先后端 `getNote(slug)`，失败回退 `loadBlog(slug)`
- [ ] `src/app/write/stores/write-store.ts` — loadBlogForEdit 适配双来源
- [ ] 编辑保存调用 `updateNote(slug, data)` 而非直接操作 GitHub；保存成功后触发 `syncPush()`

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/blog/[id]/page.tsx` | 修改 |
| `src/app/write/[slug]/page.tsx` | 修改 |
| `src/app/write/stores/write-store.ts` | 修改 |

验收标准

- [ ] 博客详情优先从后端加载
- [ ] 后端不可用时回退静态文件
- [ ] 博客编辑保存到后端
- [ ] 保存后同步到 GitHub

---

### T-14 旧博客导入后端（依赖 T-13）

前置依赖：T-13

前端

- [ ] `src/app/manage/page.tsx` — 增加"导入旧博客"按钮
- [ ] 实现导入逻辑：扫描 `/blogs/index.json`，对每个不在后端中的 slug 调用 `loadBlog()` + `createNote(type='blog')`

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/app/manage/page.tsx` | 修改 |

验收标准

- [ ] 点击"导入旧博客"后，旧博客批量写入后端
- [ ] 导入后 `/api/notes?type=blog` 包含所有旧博客
- [ ] 重复导入不产生重复记录（slug 唯一约束）

---

## P1：核心体验补齐

> P1 任务依赖 P0-A 完成。涉及博客的 P1 任务依赖 P0-B 完成。

---

### T-15 图片存储方案确认

前置依赖：P0-A 完成

本任务为决策任务，不涉及代码修改。

需比较方案

| 方案 | 存储位置 | 优点 | 缺点 | 推荐 |
|---|---|---|---|---|
| A. GitHub 仓库 | `public/mistakes/{slug}/` | 复用现有上传逻辑 | 仓库膨胀；图片公开 | 适合图片量小 |
| B. Cloudflare R2 | R2 bucket + 后端上传接口 | 独立存储；S3 兼容；免出口费 | 需要配置 R2 bucket 和 API token | **推荐** |
| C. 本地文件服务 | 后端服务器本地目录 | 最简单 | 不适合多实例/Serverless | 仅开发环境 |
| D. base64 入库 | Note.images JSON 字段存 base64 | 无需额外基础设施 | 数据库膨胀；查询性能差 | **不推荐** |

需确认事项

- [ ] 确认是否可用 Cloudflare R2（或其他对象存储）
- [ ] 确认图片访问是否需要权限控制
- [ ] 确认过渡期方案（如暂无对象存储，先用方案 D 过渡）

验收标准

- [ ] 已选择存储方案并记录到 design.md
- [ ] 已确认过渡期方案（如需要）

---

### T-16 错题图片持久化（依赖 T-15）

前置依赖：T-15 存储方案确认

后端

- [ ] `backend/app/models/note.py` — 增加 `images` JSON 字段
- [ ] `backend/app/schemas/note.py` — NoteCreate/NoteUpdate/NoteOut 增加 images
- [ ] 新建迁移 `backend/alembic/versions/003_add_images_field.py`
- [ ] 如选择 R2：后端增加图片上传接口 `POST /api/upload`

前端

- [ ] `src/lib/api/notes.ts` — NoteCreateInput/NoteUpdateInput/NoteDetail 增加 images
- [ ] `src/app/write-mistake/page.tsx` — handleImageUpload 保留图片引用到 state；handleSave 传入 images
- [ ] `src/app/notes/[id]/page.tsx` — mistake 类型详情页展示图片

涉及文件

| 文件 | 变更类型 |
|---|---|
| `backend/app/models/note.py` | 新增字段 |
| `backend/app/schemas/note.py` | 修改 |
| `backend/alembic/versions/003_add_images_field.py` | 新建 |
| `src/lib/api/notes.ts` | 修改 |
| `src/app/write-mistake/page.tsx` | 修改 |
| `src/app/notes/[id]/page.tsx` | 修改 |
| `backend/app/routers/upload.py`（如选 R2） | 新建 |

验收标准

- [ ] AI 分析图片保存到后端
- [ ] 错题详情页可查看原始图片
- [ ] 图片 URL 可正常访问

---

## P2：后续增强

> P2 依赖 P0-A 完成。涉及博客的 P2 任务依赖 P0-B 完成。涉及 Note 模型变更的任务依赖模型稳定。涉及删除语义的任务依赖删除确认逻辑确认。

---

### T-17 统一搜索入口

前置依赖：P0-A 完成、P0-B 完成

- [ ] 新建 `src/components/global-search.tsx` — 调用 `GET /api/search?q=...`，展示统一结果列表，按 type 分组
- [ ] `src/layout/header.tsx` — 增加搜索入口

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/components/global-search.tsx` | 新建 |
| `src/layout/header.tsx` | 修改 |

验收标准

- [ ] 搜索结果包含博客、笔记、错题
- [ ] 按 type 分组展示

---

### T-18 统一标签和分类体系

前置依赖：P0-A 完成、P0-B 完成

- [ ] `src/hooks/use-categories.ts` — 改为从 `/api/categories` 加载（替代 `/blogs/categories.json`）
- [ ] `src/app/manage/page.tsx` — 增加标签/分类管理 tab

涉及文件

| 文件 | 变更类型 |
|---|---|
| `src/hooks/use-categories.ts` | 修改 |
| `src/app/manage/page.tsx` | 修改 |

验收标准

- [ ] 博客和笔记共享标签和分类
- [ ] 管理面板可管理标签和分类

---

### T-19 软删除

前置依赖：P0-A 完成、删除语义确认

- [ ] `backend/app/models/note.py` — 增加 `deleted_at` TIMESTAMP 字段
- [ ] 新建迁移 `backend/alembic/versions/004_add_deleted_at.py`
- [ ] `backend/app/routers/notes.py` — delete 改为设置 deleted_at；所有查询默认 `where deleted_at IS NULL`；增加 `/api/notes/trash`、`/api/notes/{slug}/restore`、`/api/notes/{slug}/permanent`
- [ ] `src/app/manage/page.tsx` — 增加回收站 tab

涉及文件

| 文件 | 变更类型 |
|---|---|
| `backend/app/models/note.py` | 新增字段 |
| `backend/alembic/versions/004_add_deleted_at.py` | 新建 |
| `backend/app/routers/notes.py` | 修改 |
| `src/app/manage/page.tsx` | 修改 |

验收标准

- [ ] 删除后进入回收站
- [ ] 回收站可恢复
- [ ] 回收站可永久删除
- [ ] 列表默认不展示已删除记录

---

### T-20 导出

前置依赖：P0-A 完成

- [ ] `backend/app/routers/notes.py` — 增加 `GET /api/notes/{slug}/export?format=markdown|json`
- [ ] `src/app/notes/[id]/page.tsx` — 增加导出按钮

涉及文件

| 文件 | 变更类型 |
|---|---|
| `backend/app/routers/notes.py` | 新增接口 |
| `src/app/notes/[id]/page.tsx` | 修改 |

验收标准

- [ ] 可导出为 Markdown 文件
- [ ] 可导出为 JSON 文件

---

### T-21 收藏/置顶

前置依赖：P0-A 完成、Note 模型稳定

- [ ] `backend/app/models/note.py` — 增加 `pinned` BOOLEAN、`favorite` BOOLEAN
- [ ] 新建迁移 `backend/alembic/versions/005_add_pinned_favorite.py`
- [ ] `backend/app/routers/notes.py` — 列表排序 `order_by(pinned.desc(), updated_at.desc())`
- [ ] `src/app/notes/page.tsx` — 列表项显示置顶标记
- [ ] `src/app/notes/[id]/page.tsx` — 详情页增加收藏/置顶按钮

涉及文件

| 文件 | 变更类型 |
|---|---|
| `backend/app/models/note.py` | 新增字段 |
| `backend/alembic/versions/005_add_pinned_favorite.py` | 新建 |
| `backend/app/routers/notes.py` | 修改 |
| `src/app/notes/page.tsx` | 修改 |
| `src/app/notes/[id]/page.tsx` | 修改 |

验收标准

- [ ] 可标记收藏和置顶
- [ ] 置顶内容排在列表前面
- [ ] 收藏状态持久化

---

### T-22 版本历史

前置依赖：P0-A 完成、Note 模型稳定

- [ ] 新建 `backend/app/models/revision.py` — NoteRevision 表（id, note_id, title, content, revision_number, created_at）
- [ ] 新建迁移 `backend/alembic/versions/006_add_revisions.py`
- [ ] `backend/app/routers/notes.py` — update_note 时自动保存当前版本到 note_revisions
- [ ] 新建 `backend/app/routers/revisions.py` — GET `/api/notes/{slug}/revisions`、POST `/api/notes/{slug}/revisions/{rev_id}/restore`
- [ ] `src/lib/api/notes.ts` — 增加版本相关 API
- [ ] `src/app/notes/[id]/page.tsx` — 增加"历史版本"入口

涉及文件

| 文件 | 变更类型 |
|---|---|
| `backend/app/models/revision.py` | 新建 |
| `backend/alembic/versions/006_add_revisions.py` | 新建 |
| `backend/app/routers/notes.py` | 修改 |
| `backend/app/routers/revisions.py` | 新建 |
| `src/lib/api/notes.ts` | 修改 |
| `src/app/notes/[id]/page.tsx` | 修改 |

验收标准

- [ ] 编辑笔记自动保存版本
- [ ] 可查看历史版本列表
- [ ] 可恢复到指定版本
