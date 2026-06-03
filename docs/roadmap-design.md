# 个人知识系统演进路线 — 设计文档

> 版本: 1.1
> 日期: 2026-06-03
> 状态: Draft
> 关联: `docs/personal-knowledge-system-design.md` | `docs/note-editor-design.md` | `docs/ui-upgrade-design.md` | `AGENTS.md`

---

## 0. 文档定位

本文档是对 `docs/personal-knowledge-system-design.md`（整体架构）和 `docs/note-editor-design.md`（编辑器扩展）的**实施级补充**。它基于当前代码库的实际状态，对 P0–P6 各阶段给出具体的技术方案、数据模型变更、API 设计、前端组件拆分和验收标准。

**与已有文档的关系**：

- `personal-knowledge-system-design.md`：产品愿景与架构原则（不变）
- `personal-knowledge-system-tasks.md`：任务清单（本文档产出后需同步更新）
- `note-editor-design.md` / `note-editor-tasks.md`：编辑器专项（P2/P3 中与编辑器强相关的部分引用其设计）
- `tasks.md` / `design.md`：早期闭环修复（部分已完成，本文档标注其遗留项）
- **`ui-upgrade-design.md`**：UI 层升级设计（导航、渲染引擎、写作工具链、空状态反馈）。本文档侧重后端/数据/业务逻辑；UI 层设计详见 ui-upgrade-design.md。

---

## 1. 当前系统状态摘要

### 1.1 已完成

| 领域 | 状态 | 说明 |
|------|------|------|
| taxonomy router 注册 | ✅ | `categories`、`subjects` router 已 include |
| 路由跳转分流 | ✅ | `getContentDetailHref` / `getContentEditHref` 按 type 分流 |
| 保存/删除落点 | ✅ | create/edit/delete 路径已统一 |
| 管理面板登录 | ✅ | 登录态验证 + 表格操作 |
| 错题 AI schema | ✅ | `AnalyzeResponse` 包含 `error_reason`、`key_step` 等 6 个扩展字段 |
| 复习规划 API | ✅ | `/api/review/queue`、`/stats`、`/plan` 已实现 |
| 错题列表规划卡片 | ✅ | 今日复习、薄弱点、科目统计已渲染 |
| 编辑器工具栏 | ✅ | `NoteToolbar` + `useNoteEditor` + 模板系统已实现 |
| 斜杠命令 | ✅ | `SlashCommandMenu` 基础版已实现 |
| AI 润色面板 | ✅ | `AIAssistantPanel` + SSE 流式已实现 |
| Markdown 扩展 | ✅ | Alerts、高亮、脚注、Mermaid 已实现 |

### 1.2 未完成 / 需复核

| 领域 | 状态 | 说明 |
|------|------|------|
| 批量删除文案 | ❌ | 当前 `confirm('确定删除 N 条内容？')` 未显示内容类型分布 |
| 危险操作红色弱背景 | ❌ | 删除按钮有 `bg-red-500/10`，但未统一所有危险操作 |
| /manage 登录态验证 | ⚠️ | 登录流程已实现，但 auth bypass 仍在（`get_current_user` 自动创建 admin） |
| tasks.md 陈旧项 | ⚠️ | 需复核后勾掉或删掉已处理项 |
| 错题 AI 扩展字段一等化 | ❌ | 当前合并进 `analysis/content`，未新增后端一等字段 |
| 错题详情跳转关联笔记 | ❌ | 无关联笔记机制 |
| 复习完成页升级 | ❌ | 当前仅显示"复习了 N 道题" |
| AI 端到端验收 | ⚠️ | 需真实 AI key 验收 |
| /mistakes/{slug} 独立路由 | ❌ | 当前复用 `/notes/{slug}` |

---

## 2. P0 — 尾巴收尾

### 2.1 管理面板批量删除文案升级

**现状**: `confirm('确定删除 ${selected.size} 条内容？')` — 无类型信息。

**方案**: 在确认弹窗中统计选中项的类型分布。

**修改文件**: `src/app/manage/page.tsx`

**实现**:

```typescript
const handleDeleteSelected = async () => {
  if (selected.size === 0) return
  const selectedItems = data?.items.filter(i => selected.has(i.slug)) ?? []
  const typeCounts = selectedItems.reduce((acc, item) => {
    acc[item.type] = (acc[item.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  const typeSummary = Object.entries(typeCounts)
    .map(([type, count]) => `${typeLabels[type as keyof typeof typeLabels]} ${count} 条`)
    .join('、')
  if (!confirm(`确定删除以下内容？\n${typeSummary}\n共 ${selected.size} 条，删除后不可恢复。`)) return
  // ... existing logic
}
```

**验收**: 选中 2 篇博客 + 3 篇笔记，确认弹窗显示"博客 2 条、笔记 3 条，共 5 条"。

### 2.2 危险操作统一红色弱背景和确认体验

**现状**: 删除按钮有 `bg-red-500/10 text-red-500`，但批量删除、单条删除、笔记详情删除的样式不完全一致。`confirm()` 是原生弹窗。

**方案**:

1. 统一危险操作按钮样式: `rounded bg-red-500/10 px-2 py-1 text-xs text-red-500 hover:bg-red-500/20 transition-colors`
2. 保留 `confirm()` 作为 P0 快速修复（不引入新依赖）。后续 P3 可升级为自定义 `ConfirmDialog` 组件。

**修改文件**:

- `src/app/manage/page.tsx` — 统一删除按钮样式
- `src/app/notes/[id]/note-detail-content.tsx` — 删除按钮样式对齐

**验收**: 所有删除操作按钮视觉一致，均有确认步骤。

### 2.3 /manage 登录态验证

**现状**: `ManagePage` 已实现登录表单和 `getMe()` 验证。但后端 `get_current_user` 存在 auth bypass（自动创建/返回 admin 用户）。

**方案**:

1. 后端移除 auth bypass，恢复真实 JWT 校验。
2. 前端 `/manage` 页面已有的登录流程无需改动。
3. 未登录时显示登录表单，已登录时显示管理面板。

**修改文件**: `backend/app/routers/auth.py`（或 `backend/app/utils/auth.py` 中的 `get_current_user`）

**风险**: 移除 bypass 后，所有需要认证的 API 都需要有效 token。需确保前端在请求头中正确携带 `Authorization: Bearer <token>`。

**验收**: 未登录访问 `/manage` 显示登录表单；登录后可正常查看/编辑内容。

### 2.4 清理 tasks.md 陈旧已修复项

**需复核的条目**:

| 条目 | 当前状态 | 操作 |
|------|----------|------|
| T-001 taxonomy router 注册 | ✅ 已完成 | 勾选 |
| T-002 路由跳转策略 | ✅ 已完成 | 勾选 |
| T-003 保存/取消/删除落点 | ✅ 已完成 | 勾选 |
| T-004 管理面板跳转分流 | ✅ 查看/编辑已分流，批量删除文案待补 | 标记部分完成 |
| T-005 按钮可理解性 | ✅ aria-label 已补，危险操作样式待统一 | 标记部分完成 |
| T-006 模板可见化 | ✅ 已完成 | 勾选 |
| T-007 P0 验证 | ⚠️ 登录态待补测 | 标记待补 |
| design.md 2.1 博客删除 DB 联动 | ✅ 已实现 `deleteNote` 调用 | 勾选 |
| design.md 2.2 元数据自动加载 | ✅ `listCategories`/`listSubjects` 已加载 | 勾选 |
| design.md 3.5 动态跳转路由 | ✅ `getContentDetailHref`/`getContentEditHref` 已实现 | 勾选 |
| design.md 3.6 alert→toast | ✅ 已替换 | 勾选 |
| design.md 4.1 Markdown 预览 | ✅ 已实现 | 勾选 |
| design.md 4.2 图片 URL 插入 | ✅ 已实现 | 勾选 |
| design.md 4.3 封面字段 | ✅ 已实现 | 勾选 |
| design.md 4.4 科目 datalist | ✅ 已实现 | 勾选 |
| design.md 4.5 冗余路由清理 | ✅ 已清理 | 勾选 |

**执行方式**: 直接编辑 `tasks.md`，将已完成项的 `[ ]` 改为 `[x]`，并标注完成日期。

---

## 3. P1 — 错题与复习

### 3.1 错题 AI 扩展字段是否做成后端一等字段

**当前状态**: `AnalyzeResponse` schema 已定义 `error_reason`、`key_step`、`similar_traps`、`generalization`、`review_advice`、`variant_questions`。但保存时这些字段合并进 `analysis` 或 `content` 文本，`Note` 模型没有独立列。

**方案对比**:

| 方案 | 优点 | 缺点 |
|------|------|------|
| A. 新增一等字段 | 结构化查询、筛选、统计 | 需 migration、schema 同步、前端表单改造 |
| B. 保持合并进 content | 零 migration、前端简单 | 无法按字段查询/筛选、AI 输出结构丢失 |
| C. 使用 JSON 扩展字段 | 一个 JSON 列存所有扩展、灵活 | 查询不如一等字段方便、schema 需自行校验 |

**推荐方案 C**: 新增 `Note.ai_metadata` JSON 字段。

```python
# backend/app/models/note.py
ai_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
```

存储结构:

```json
{
  "error_reason": "...",
  "key_step": "...",
  "similar_traps": ["..."],
  "generalization": "...",
  "review_advice": "...",
  "variant_questions": ["..."]
}
```

**理由**: 6 个字段都是 AI 生成的辅助信息，不需要独立索引或筛选。JSON 方案 migration 成本最低，且保留了结构化语义。

**修改文件**:

- `backend/app/models/note.py` — 新增 `ai_metadata` 字段
- `backend/app/schemas/note.py` — NoteCreate/NoteUpdate/NoteOut 增加 `ai_metadata`
- `backend/alembic/versions/` — 新增 migration
- `src/lib/api/notes.ts` — 前端类型同步
- `src/app/write-mistake/page.tsx` — 保存时传入 `ai_metadata`
- `src/app/notes/[id]/note-detail-content.tsx` — 详情页展示扩展字段

**验收**: AI 分析后保存，详情页独立展示错误原因、关键步骤、变式题等。

### 3.2 错题详情支持跳转关联笔记

**方案**: 在 `Note` 模型中新增 `related_note_slugs: list[str] | None` JSON 字段（或复用 `ai_metadata` 中的 `related_notes` 键）。

**推荐**: 放入 `ai_metadata` 的 `related_notes` 键:

```json
{
  "error_reason": "...",
  "related_notes": [
    { "slug": "xxx", "title": "函数基础" }
  ]
}
```

**前端**: 错题详情页渲染关联笔记为可点击链接，跳转到 `/notes/{slug}`。

**修改文件**:

- `backend/app/schemas/ai.py` — `AnalyzeResponse` 增加 `related_notes`
- `backend/app/services/ai_service.py` — prompt 要求 AI 输出关联笔记
- `src/app/notes/[id]/note-detail-content.tsx` — 渲染关联笔记链接

**验收**: 错题详情页显示"关联笔记"区域，点击可跳转。

### 3.3 复习完成页升级

**现状**: `/mistakes/review` 完成后仅显示"复习了 N 道题" + 返回按钮。

**方案**: 升级完成页为结构化总结:

```
┌─────────────────────────────────────┐
│         ✅ 复习完成！                │
│                                     │
│  本次复习: 8 道题                    │
│                                     │
│  掌握程度分布:                       │
│  ██████████ 完美 (3)                │
│  ████████   略有犹豫 (2)            │
│  ██████     费力回忆 (1)            │
│  ████       有印象 (1)              │
│  ██         完全忘记 (1)            │
│                                     │
│  下一步建议:                         │
│  · "函数基础" 建议 2 天后再次复习    │
│  · "导数应用" 建议明天复习           │
│                                     │
│  [回到错题集]  [继续整理]  [再做一轮] │
└─────────────────────────────────────┘
```

**数据来源**: 前端在复习过程中收集每次 `submitReview` 的 `quality` 值，完成后本地统计。

**修改文件**: `src/app/mistakes/review/page.tsx`

**实现要点**:

1. 新增 `reviewResults` state: `Array<{ slug, title, quality, nextReview }>`
2. 每次 `handleReview` 后追加结果
3. 完成后渲染统计图表（纯 CSS 柱状图）
4. "下一步建议"从 `getReviewPlan()` 获取

**验收**: 完成一轮复习后，页面显示题数、掌握分布、下一步建议、三个导航按钮。

### 3.4 AI 端到端验收

**验收流程**:

1. 打开 `/write-mistake`
2. 上传一张错题图片 → 触发 AI 分析 → 检查表单填充
3. 粘贴一段错题文本 → 触发 AI 分析 → 检查表单填充
4. 保存 → 跳转详情页 → 检查所有字段
5. 检查 `ai_metadata` 字段是否包含扩展数据

**前置条件**: 需要有效的 `DEEPSEEK_API_KEY` 和 `DASHSCOPE_API_KEY`。

### 3.5 /mistakes/{slug} 独立路由

**决策**: 当前复用 `/notes/{slug}`，通过 `note.type === 'mistake'` 渲染错题特有区域。

**建议**: P1 阶段暂不新增独立路由。理由:

1. 复用已有详情页，减少维护成本
2. 错题详情的差异化渲染已在 `note-detail-content.tsx` 中通过 type 判断实现
3. 后续如有错题特有交互（如快速复习、变式题作答），再拆分不迟

**记录**: 在此文档中明确决策，后续如需拆分，新建 `src/app/mistakes/[slug]/page.tsx`。

---

## 4. P2 — AI 写作助手

### 4.1 后端写作助手 API

**现状**: `POST /api/ai/polish` 已实现，支持 `polish`、`summarize`、`expand`、`continue`、`translate_en`、`translate_zh`、`extract_tags`、`generate_questions` 8 种 action。

**需扩展的 action**:

| Action | 说明 | 请求额外字段 |
|--------|------|-------------|
| `title` | 根据全文生成标题 | `full_content` |
| `outline` | 根据全文生成目录 | `full_content` |
| `tags` | 推荐标签 | `full_content`, `existing_tags` |
| `diagram` | 文本转 Mermaid 流程图 | `selected_text` |
| `compare` | 生成对比块 | `selected_text`, `topic` |
| `mindmap` | 生成思维导图 | `selected_text` |

**方案**: 扩展现有 `ai_polish.py` router 和 service，不新建 router。

**修改文件**:

- `backend/app/schemas/ai_polish.py` — `PolishAction` 枚举增加 6 个值
- `backend/app/services/ai_polish_service.py` — 增加 6 个 system prompt
- `backend/app/routers/ai_polish.py` — 无需改动（已通配 action）

**请求体扩展**:

```python
class PolishRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    action: PolishAction
    context: str | None = Field(None, max_length=12000)
    title: str | None = None          # 当前笔记标题
    note_type: str | None = None      # note/blog/mistake
    existing_tags: list[str] | None = None  # 已有标签
```

**响应扩展**: 对于 `diagram`、`compare`、`mindmap`，返回结构化结果:

```python
class PolishChunkResponse(BaseModel):
    chunk: str
    structured: dict | None = None  # 仅 diagram/compare/mindmap 使用
```

### 4.2 前端 AI 面板扩展

**现状**: `AIAssistantPanel` 已实现 8 个操作按钮。

**需扩展**:

1. 增加"插入内容"分组: 对比块、图表、思维导图
2. 增加"全文处理"分组: 生成标题、生成摘要、生成目录、推荐标签
3. 选区操作分组保持现有: 改写、扩写、总结、续写

**修改文件**:

- `src/app/write-note/components/ai-assistant-panel.tsx` — 增加按钮分组
- `src/lib/api/ai-polish.ts` — 增加新 action 类型

### 4.3 选区替换与光标插入

**现状**: `AIAssistantPanel` 已有"插入"和"替换"按钮。

**需增强**:

1. "标题"结果 → 应用到标题输入框（不插入正文）
2. "摘要"结果 → 应用到摘要输入框
3. "标签"结果 → 合并到 tags 数组
4. "目录"结果 → 插入到正文光标位置

**修改文件**: `src/app/write-note/components/ai-assistant-panel.tsx`

**接口**: 面板需要接收 `onApplyTitle`、`onApplySummary`、`onApplyTags` 回调。

### 4.4 移动端适配

**方案**: 屏幕宽度 < 768px 时，AI 面板改为底部抽屉。

**实现**: 使用 `motion/react` 的 `AnimatePresence` + 条件渲染。

---

## 5. P3 — 内容块与渲染

### 5.1 :::compare 对比块

**语法**:

```markdown
:::compare
title: 函数与方法对比
left: 函数
right: 方法
- 定义位置不同
- 调用方式不同
- this 绑定不同
:::
```

**渲染**: 左右两列卡片，移动端纵向堆叠。

**实现**: 在 `markdown-renderer.ts` 中添加 block 扩展，匹配 `:::compare` ... `:::` 语法。

**修改文件**:

- `src/lib/markdown-renderer.ts` — 新增 compare block parser
- `src/components/compare-block.tsx` — 新建对比块组件
- `src/styles/article.css` — 对比块样式

### 5.2 Mermaid mindmap 模板

**现状**: Mermaid 渲染已实现（`T-20`），支持 `graph`、`sequenceDiagram`、`gantt`、`pie`。

**需验证**: `mindmap` 类型是否在当前 mermaid 版本中可用。

**方案**: 如果 mermaid mindmap 可用，直接使用 ` ```mermaid\nmindmap\n` ` 语法。如果不可用，提供 `:::mindmap` 自定义语法作为降级。

### 5.3 文字高亮与字体颜色

**现状**: `==text==` 高亮已实现。

**需新增**: 字体颜色。使用受控色板:

```markdown
{red|红色文字}、{blue|蓝色文字}
```

**色板定义** (8 色):

| Token | 颜色 | 用途 |
|-------|------|------|
| `red` | `#ef4444` | 重要/错误 |
| `blue` | `#3b82f6` | 链接/信息 |
| `green` | `#10b981` | 正确/成功 |
| `yellow` | `#f59e0b` | 注意 |
| `purple` | `#8b5cf6` | 重点 |
| `orange` | `#f97316` | 警告 |
| `gray` | `#6b7280` | 次要 |
| `pink` | `#ec4899` | 标记 |

**实现**: `marked.use()` inline 扩展，匹配 `{color|text}`。

### 5.4 内容块插入器

**方案**: 在 `NoteToolbar` 中增加"插入"下拉菜单:

```
┌─────────────────────┐
│ 📊 图表 (Mermaid)   │
│ 🔄 对比块           │
│ 🧠 思维导图         │
│ 📋 表格             │
│ 🃏 复习卡片         │
└─────────────────────┘
```

点击后插入对应模板 Markdown 到光标位置。

### 5.5 图片/Mermaid 全屏查看

**现状**: `DiagramViewer` 组件已存在，但未集成到所有 Mermaid/图片渲染点。

**方案**: 为所有 Mermaid 渲染块和 Markdown 图片添加点击全屏查看能力:

1. Mermaid 块: 点击打开 `DiagramViewer`，支持缩放、重置
2. Markdown 图片: 点击打开 lightbox
3. 移动端: 全屏查看，双指缩放

---

## 6. P4 — 文件夹与拖拽排序

### 6.1 后端 Folder 模型

```python
# backend/app/models/folder.py
class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    children: Mapped[list["Folder"]] = relationship(back_populates="parent", lazy="selectin")
    parent: Mapped["Folder | None"] = relationship(back_populates="children", remote_side="Folder.id")
```

**Note 模型扩展**:

```python
# 在 Note 模型中新增
folder_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
)
sort_order: Mapped[int] = mapped_column(Integer, default=0)
```

**Alembic migration**: 新增 `folders` 表 + `notes` 表增加 `folder_id`、`sort_order` 列 + 索引。

### 6.2 Folders API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/folders` | 返回文件夹树（嵌套结构） |
| POST | `/api/folders` | 创建文件夹 |
| PUT | `/api/folders/{id}` | 重命名 / 移动 / 排序 |
| DELETE | `/api/folders/{id}` | 删除文件夹（子文件夹级联，笔记 folder_id 置空） |
| POST | `/api/folders/reorder` | 批量更新同级文件夹排序 |
| POST | `/api/notes/{slug}/move` | 移动笔记到文件夹 |

**响应结构** (GET `/api/folders`):

```json
[
  {
    "id": "uuid",
    "name": "数学",
    "parent_id": null,
    "sort_order": 0,
    "children": [
      { "id": "uuid", "name": "函数", "parent_id": "uuid", "sort_order": 0, "children": [] }
    ],
    "note_count": 5
  }
]
```

### 6.3 前端知识库侧栏

**组件**: `src/app/notes/components/knowledge-sidebar.tsx`

**结构**:

```
┌──────────────────────┐
│ 📥 收件箱             │
│ 📄 全部内容           │
│ 📝 笔记              │
│ 📰 博客              │
│ ❌ 错题              │
│──────────────────────│
│ 📁 文件夹             │
│   📁 数学             │
│     📁 函数           │
│     📁 导数           │
│   📁 英语             │
│   📁 编程             │
│──────────────────────│
│ 🏷️ 标签               │
│   React (12)          │
│   数学 (8)            │
│   写作 (5)            │
└──────────────────────┘
```

**响应式**: 桌面端左侧固定侧栏，移动端收进抽屉（汉堡菜单触发）。

### 6.4 拖拽排序

**方案**: 使用 `@dnd-kit/core` + `@dnd-kit/sortable`（轻量、React 19 兼容）。

**能力**:

1. 拖笔记到文件夹 → 调用 `POST /api/notes/{slug}/move`
2. 拖文件夹排序 → 调用 `POST /api/folders/reorder`
3. 拖笔记在同一文件夹内排序 → 更新 `sort_order`

**移动端替代**: 笔记列表项长按弹出"移动到"菜单；文件夹提供"上移/下移"按钮。

---

## 7. P5 — AI 知识库管家

### 7.1 查询与分析服务

**后端**: `backend/app/services/knowledge_assistant.py`

**能力**:

1. 查询最近 N 天创建/修改的内容
2. 查询缺标签的内容（tags 为空）
3. 查询缺文件夹的内容（folder_id 为 null）
4. 聚合错题薄弱点（按 subject、knowledge_points 分组统计）
5. 生成整理建议

**建议类型**:

| 类型 | 说明 | 示例 |
|------|------|------|
| `tag` | 推荐标签 | "这篇笔记涉及 React Hooks，建议添加 'React' 标签" |
| `folder` | 推荐文件夹 | "3 篇数学笔记未归档，建议移入 '数学' 文件夹" |
| `summary` | 内容摘要 | "本周新增 5 篇笔记，主要集中在算法和英语" |
| `related` | 关联笔记 | "错题'导数应用'与笔记'导数基础'相关，建议关联" |
| `review` | 复习建议 | "函数基础已超期 3 天未复习，建议今天复习" |

### 7.2 前端建议卡片

**各页面入口**:

| 页面 | 卡片位置 | 内容 |
|------|----------|------|
| `/notes` | 列表顶部 | 整理建议（缺标签、缺文件夹） |
| `/mistakes` | 列表顶部 | 薄弱点与复习建议 |
| `/manage` | 内容 Tab | 内容体检面板 |
| 首页 | 独立卡片 | 今日建议摘要 |

### 7.3 批量建议确认执行

**流程**:

1. AI 生成建议列表
2. 用户点击建议 → 打开详情弹窗
3. 弹窗显示: 建议内容、影响范围（涉及哪些笔记）、确认按钮
4. 用户确认 → 执行批量操作
5. 显示执行结果（成功/失败/部分失败）

**安全**: 所有批量操作必须二次确认。失败时显示哪些项失败，不自动回滚（避免二次破坏）。

### 7.4 周度总结

**数据源**: 本周复习记录 + 新增错题 + 知识点统计。

**输出**: 保存为 `type=note` 的笔记，或渲染为卡片。

---

## 8. P6 — 数据可靠性与公开边界

### 8.1 图片存储策略

**当前状态**: 图片通过 `POST /api/notes/upload-image` 上传到后端本地目录。

**过渡期方案 (已确认)**: 后端本地目录 + 定期备份。适合当前单机部署规模。

**正式期方案**: 如需扩展，迁移至 Cloudflare R2 或阿里云 OSS。

**public/private 策略**:

- `blog` 类型图片: 可公开访问
- `note`/`mistake` 类型图片: 当前同属本地目录，均需认证访问（通过 API 代理）

**Object key 规则**:

- 上传时生成: `{type}/{slug}/{filename}`
- 数据库存储完整 URL
- 删除笔记时: 图片保留（不级联删除），后续可按策略清理

### 8.2 图片 URL 稳定性

**规则**:

- 上传时生成 object key: `{type}/{slug}/{filename}`
- 数据库存储完整 URL 或 object key
- 删除笔记时: 图片保留（不级联删除），或标记为待清理

### 8.3 RSS/sitemap 公开过滤

**当前状态**: `src/app/rss.xml/route.ts` 和 `src/sitemap.ts` 需验证是否只包含公开内容。

**规则**:

- 只包含 `type=blog` + `status=published` + `hidden=false`
- `note` 和 `mistake` 永远不进入 RSS/sitemap

### 8.4 数据备份

**流程**:

1. PostgreSQL: `pg_dump` 定期备份（每日）
2. 图片: 对象存储版本控制 或 定期同步到 GitHub private repo
3. 恢复演练: 每季度一次

---

## 9. 文件变更总览

### 9.1 新建文件

| 文件 | 阶段 | 说明 |
|------|------|------|
| `backend/app/models/folder.py` | P4 | Folder 模型 |
| `backend/app/schemas/folder.py` | P4 | Folder schema |
| `backend/app/routers/folders.py` | P4 | Folders API |
| `backend/app/services/knowledge_assistant.py` | P5 | AI 知识库管家服务 |
| `src/lib/api/folders.ts` | P4 | 前端 folders API client |
| `src/lib/api/knowledge-assistant.ts` | P5 | 前端管家 API client |
| `src/app/notes/components/knowledge-sidebar.tsx` | P4 | 知识库侧栏 |
| `src/components/compare-block.tsx` | P3 | 对比块组件 |
| `src/components/confirm-dialog.tsx` | P0 | 自定义确认弹窗（可选） |

### 9.2 修改文件

| 文件 | 阶段 | 变更 |
|------|------|------|
| `src/app/manage/page.tsx` | P0 | 批量删除文案、危险操作样式 |
| `backend/app/models/note.py` | P1/P4 | `ai_metadata` JSON 字段、`folder_id`、`sort_order` |
| `backend/app/schemas/note.py` | P1 | `ai_metadata` 字段同步 |
| `backend/app/schemas/ai_polish.py` | P2 | 扩展 action 枚举 |
| `backend/app/services/ai_polish_service.py` | P2 | 6 个新 system prompt |
| `src/app/write-note/components/ai-assistant-panel.tsx` | P2 | 扩展按钮分组 |
| `src/lib/api/ai-polish.ts` | P2 | 新 action 类型 |
| `src/lib/markdown-renderer.ts` | P3 | compare block、颜色语法 |
| `src/styles/article.css` | P3 | 对比块、颜色样式 |
| `src/app/mistakes/review/page.tsx` | P1 | 复习完成页升级 |
| `src/app/notes/[id]/note-detail-content.tsx` | P1 | 关联笔记、ai_metadata 展示 |
| `tasks.md` | P0 | 勾选已完成项 |

---

## 10. 开发顺序与依赖

```text
P0 (收尾)
  2.1 批量删除文案 ← 无依赖
  2.2 危险操作样式 ← 无依赖
  2.3 登录态验证 ← 后端 auth bypass 移除
  2.4 清理 tasks.md ← 无依赖

P1 (错题)
  3.1 ai_metadata 字段 ← migration
  3.2 关联笔记 ← 3.1
  3.3 复习完成页 ← 无依赖
  3.4 AI 端到端验收 ← 3.1 + AI key
  3.5 /mistakes/{slug} ← 决策（暂不做）

P2 (写作助手)
  4.1 扩展 action ← 无依赖
  4.2 面板扩展 ← 4.1
  4.3 字段应用 ← 4.2
  4.4 移动端 ← 4.2

P3 (内容块)
  5.1 compare ← 无依赖
  5.2 mindmap ← 验证 mermaid 版本
  5.3 颜色 ← 无依赖
  5.4 插入器 ← 5.1/5.2/5.3
  5.5 全屏查看 ← 无依赖

P4 (文件夹)
  6.1 模型 ← migration
  6.2 API ← 6.1
  6.3 侧栏 ← 6.2
  6.4 拖拽 ← 6.3

P5 (管家)
  7.1 分析服务 ← P4 (需要 folder 数据)
  7.2 建议 API ← 7.1
  7.3 建议卡片 ← 7.2
  7.4 批量执行 ← 7.3

P6 (可靠性)
  8.1 图片策略 ← 决策
  8.2 URL 稳定 ← 8.1
  8.3 RSS 过滤 ← 无依赖
  8.4 备份 ← 8.1
```

---

## 11. 验证矩阵

| 阶段 | tsc --noEmit | 后端 import check | Alembic migration | 手动测试 |
|------|:---:|:---:|:---:|:---:|
| P0 | ✅ | ✅ | — | 管理面板操作 |
| P1 | ✅ | ✅ | ✅ (ai_metadata) | AI 分析+保存+详情 |
| P2 | ✅ | ✅ | — | AI 面板全 action |
| P3 | ✅ | ✅ | — | 内容块渲染+移动端 |
| P4 | ✅ | ✅ | ✅ (folders) | 侧栏+拖拽+移动端 |
| P5 | ✅ | ✅ | — | 建议生成+确认执行 |
| P6 | ✅ | ✅ | — | 公开过滤+备份恢复 |

---

## 12. 风险与回滚

| 阶段 | 主要风险 | 回滚方式 |
|------|----------|----------|
| P0 | auth bypass 移除导致已有功能断裂 | 恢复 bypass，记录待修复 |
| P1 | ai_metadata migration 失败 | 回滚 migration，保持合并进 content |
| P2 | 新 action prompt 质量不稳定 | 回退到原有 8 个 action |
| P3 | compare/mindmap 语法与现有 Markdown 冲突 | 注释掉新 parser |
| P4 | @dnd-kit 与 React 19 不兼容 | 移除拖拽，保留文件夹手动操作 |
| P5 | AI 建议质量低 | 隐藏管家入口 |
| P6 | 图片迁移中断服务 | 保持现有本地存储 |
