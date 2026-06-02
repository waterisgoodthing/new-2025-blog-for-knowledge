# 个人知识与博客系统整体演进 — 任务清单

> **历史参考文档**。当前权威任务清单见 `docs/roadmap-tasks.md`。本文档 P0 项已基本完成，P1-P6 项已迁移至新文档。

> 版本: 1.0
> 日期: 2026-06-02
> 关联: `docs/personal-knowledge-system-design.md` | `docs/personal-knowledge-system-requirements.md`

## 执行边界

所有开发工作遵守以下约束：

1. 每次开发前先执行 `git status --short`。
2. 明确 touched domain：`blog`、`notes`、`mistakes`、`review`、`auth`、`sync`、`home`、`share`、`manage` 或 shared infrastructure。
3. 不回退用户已有改动。
4. 不把静态内容线和后端知识库线继续混淆。
5. 前端 API 调用优先走 `src/lib/api/*`。
6. 后端 router 保持 thin，复杂逻辑进入 `backend/app/services/`。
7. 数据模型变更必须配套 schema、API client 和 Alembic migration。
8. UI 变更必须符合当前半透明卡片、圆角、轻量动效和个人工作台风格。
9. 默认不 `git add`、`git commit`、`git push`。

## 阶段回滚策略

| 阶段 | 回滚方式 |
|---|---|
| P0 路由与基础体验 | 移除新增跳转改动，恢复原页面链接；移除 `categories/subjects` router 注册 |
| P1 错题 AI 与复习规划 | 回退 AI prompt/schema，隐藏新增规划卡片，保留原错题列表和复习页 |
| P2 AI 写作助手 | 隐藏 AI 写作面板，保留原 `AIAssistantPanel` 或原编辑器 |
| P3 内容块能力 | 注释新增 block parser/renderer，保留原 Markdown 渲染 |
| P4 文件夹与拖拽排序 | 隐藏文件夹侧栏，保留 `folder_id/sort_order` 字段不使用或迁移回滚 |
| P5 AI 知识库管家 | 隐藏管家入口，不执行批量整理动作 |

## 任务概览

| 阶段 | 任务范围 | 任务数 |
|---|---|---:|
| P0 | 路由/API 对齐 + 按钮和模板可理解性 | 8 |
| P1 | 错题 AI 输出 + 复习规划 | 7 |
| P2 | AI 写作助手 | 6 |
| P3 | 内容块与渲染 | 7 |
| P4 | 文件夹与拖拽排序 | 8 |
| P5 | AI 知识库管家 | 6 |
| P6 | 数据可靠性与公开边界 | 5 |
| 合计 |  | 47 |

## 依赖关系图

```text
P0
  T-001 taxonomy router 注册
  T-002 路由跳转策略
  T-003 保存/取消/删除落点
  T-004 管理面板按类型分流
  T-005 按钮 tooltip 与 aria-label
  T-006 模板可见化入口
  T-007 基础验证

P1
  T-101 错题 AI schema/prompt
  T-102 错题创建页集成
  T-103 错题详情信息结构
  T-104 复习规划 API
  T-105 错题列表规划卡片
  T-106 复习完成总结

P2
  T-201 写作助手 API
  T-202 写作助手面板
  T-203 选区/光标上下文
  T-204 标题摘要标签应用
  T-205 图表/对比/思维导图生成

P3
  T-301 对比块语法
  T-302 思维导图语法
  T-303 颜色和高亮
  T-304 内容块插入器
  T-305 渲染与移动端适配

P4
  T-401 Folder 模型与迁移
  T-402 folders API
  T-403 前端 API client
  T-404 知识库侧栏
  T-405 拖拽移动和排序

P5
  T-501 管家分析服务
  T-502 整理建议卡片
  T-503 内容体检
  T-504 批量建议确认执行
```

## 阶段 P0: 路由/API 对齐与基础可理解性

目标：先修复当前结构审查中发现的确定性问题，让跳转、保存落点和基础按钮体验变清楚。

### T-001: 注册 taxonomy 后端路由

**对应需求**: FR-12.9, FR-12.10
**影响域**: shared infrastructure, notes
**文件范围**:

- `backend/main.py`
- 可选：后端 router import 测试或启动检查

**子任务**:

- [x] 在 `backend/main.py` include `categories.router`。
- [x] 在 `backend/main.py` include `subjects.router`。
- [x] 确认 `/api/categories` 返回列表。
- [x] 确认 `/api/subjects` 返回列表。

**验收标准**:

- `/write-note` 和 `/write-note/{slug}` 分类下拉、科目 datalist 能加载候选。
- `src/lib/api/meta.ts` 中的 API 路径均有对应后端 router。

**验证**:

- 后端 import/start check。
- 浏览器打开写笔记页检查网络请求。

### T-002: 明确详情入口跳转策略

**对应需求**: FR-12.1, FR-12.2, FR-12.3
**影响域**: blog, notes, mistakes, manage
**文件范围**:

- `src/app/blog/page.tsx`
- `src/app/notes/page.tsx`
- `src/app/mistakes/page.tsx`
- `src/app/manage/page.tsx`
- `src/app/notes/[id]/note-detail-content.tsx`

**子任务**:

- [x] 确认 `blog` 主要详情入口为 `/blog/{slug}`。
- [x] 确认 `note` 主要详情入口为 `/notes/{slug}`。
- [x] 决策 `mistake` 是否新增 `/mistakes/{slug}`。当前临时复用 `/notes/{slug}`，P1 再决定是否独立。
- [x] 若暂不新增错题详情页，在验收记录中明确错题详情复用笔记详情。
- [x] 更新管理面板标题链接按类型分流。

**验收标准**:

- 博客从列表、首页、管理面板点击标题时进入同一类展示体验。
- 普通笔记进入通用笔记详情。
- 错题进入明确的错题详情入口或明确复用入口。

### T-003: 统一保存、取消、删除后的落点

**对应需求**: FR-12.6, FR-12.7, FR-12.8
**影响域**: blog, notes, mistakes
**文件范围**:

- `src/app/write/components/actions.tsx`
- `src/app/write/hooks/use-publish.ts`
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`
- `src/app/write-mistake/page.tsx`
- `src/app/notes/[id]/note-detail-content.tsx`

**子任务**:

- [x] 新建博客成功后跳转 `/blog/{slug}` 或展示“查看文章”入口。
- [x] 更新博客成功后跳转 `/blog/{slug}` 或展示“查看文章”入口。
- [x] 新建普通笔记成功后跳转 `/notes/{slug}`，而不是只回列表。
- [x] 新建错题成功后跳转错题详情入口或 `/mistakes`。当前跳转临时复用 `/notes/{slug}`。
- [x] 编辑普通笔记保存后保留 `/notes/{slug}`。
- [x] 删除后按类型回到 `/blog`、`/notes`、`/mistakes`。

**验收标准**:

- 所有 create/edit/delete 路径都有一致且可解释的落点。
- 用户保存后能立即看到自己刚保存的内容。

### T-004: 管理面板内容跳转分流

**对应需求**: FR-10, FR-12.4, FR-12.5
**影响域**: manage, blog, notes, mistakes
**文件范围**:

- `src/app/manage/page.tsx`

**子任务**:

- [x] 标题查看链接按 `item.type` 分流。
- [x] 编辑链接按 `item.type` 分流。
- [x] 删除按钮保留确认。
- [x] 批量删除文案显示影响内容类型和数量。

**验收标准**:

- 管理面板中 `blog` 不再默认进入通用 `/notes/{slug}`，除非产品明确允许。
- 管理面板查看/编辑路径和主列表一致。

### T-005: 全站关键按钮可理解性审查与修复

**对应需求**: FR-4, NFR-2
**影响域**: shared UI, notes, blog, mistakes, manage
**文件范围**:

- `src/app/write*`
- `src/app/notes*`
- `src/app/mistakes*`
- `src/app/manage/page.tsx`
- `src/components/*`

**子任务**:

- [x] 列出 icon-only 按钮。
- [x] 为写作工具栏、模板入口、图片删除、标签删除等高频 icon-only 按钮补 `aria-label`。
- [x] 为不熟悉的图标补 tooltip 或 `title`。
- [x] 重要操作改为“图标 + 文字”。模板入口保留文字。
- [x] 危险操作统一红色弱背景和确认。

**验收标准**:

- 用户不读文档也能理解主要按钮。
- 可访问性检查中无明显无名按钮。

### T-006: 模板可见化入口

**对应需求**: FR-5
**影响域**: notes
**文件范围**:

- `src/app/write-note/components/note-templates.tsx`
- `src/app/write-note/components/note-toolbar.tsx`
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`

**子任务**:

- [x] 新增或改造“模板”按钮。
- [x] 模板面板展示名称和一句用途说明。
- [x] 支持课堂笔记、错题解析、读书笔记、项目复盘。
- [x] 保留 `/` 指令为高级快捷方式。
- [x] 移动端模板入口可点击使用。

**验收标准**:

- 用户无需输入 `/` 即可插入模板。
- 模板入口符合当前半透明卡片风格。

### T-007: P0 验证

**对应需求**: P0 全部
**影响域**: shared

**验证命令/流程**:

- [x] `npx tsc --noEmit`
- [x] 后端 import/start check。
- [x] 手动打开 `/write-note`、`/write-note/{slug}`。
- [x] 手动走 `/blog -> /blog/{slug} -> /write/{slug}`。
- [x] 手动走 `/notes -> /notes/{slug} -> /write-note/{slug}`。
- [x] 手动走 `/mistakes -> detail -> edit`。
- [ ] 手动走 `/manage` 查看/编辑分流。未登录态已验收；登录态列表待凭证或后续补测。

**阶段报告必须包含**:

- 修改了哪些跳转。
- 保存后落点最终规则。
- 是否新增错题独立详情页。
- TypeScript 和后端检查结果。

## 阶段 P1: 错题 AI 与复习规划

目标：把错题从“简单记录”升级为“解析、归纳、复习规划”。

### T-101: 错题 AI 输出 schema 升级

**对应需求**: FR-8
**影响域**: mistakes, AI
**文件范围**:

- `backend/app/schemas/ai.py`
- `backend/app/services/ai_service.py`
- `backend/app/routers/ai.py`
- `src/lib/api/ai.ts`

**子任务**:

- [x] 定义结构化错题分析响应字段。
- [x] 增加 `error_reason`、`key_step`、`similar_traps`、`generalization`、`review_advice`、`variant_questions`。
- [x] 更新图片分析 prompt。
- [x] 更新文本分析 prompt。
- [x] 前端类型同步。

**验收标准**:

- AI 输出包含完整步骤、错误原因、知识点、举一反三、变式题和复习建议。
- 旧字段兼容或迁移路径明确。

### T-102: 错题创建页集成新解析

**对应需求**: FR-8
**影响域**: mistakes
**文件范围**:

- `src/app/write-mistake/page.tsx`
- `src/app/write-note/page.tsx`

**子任务**:

- [x] 将新 AI 字段映射到表单。
- [x] 让用户能编辑 AI 输出。当前合并进“分析与反思”文本域。
- [x] 未识别字段显示为空而不是报错。
- [ ] 保存时传入后端一等字段或扩展字段。当前先合并进现有 `analysis/content`，未新增一等字段。

**验收标准**:

- 上传图片/粘贴文本后，页面填充完整解析。
- 保存后详情页可看到完整内容。

### T-103: 错题详情页信息结构升级

**对应需求**: FR-8, FR-12.3
**影响域**: mistakes, notes
**文件范围**:

- `src/app/notes/[id]/note-detail-content.tsx`
- 可选：`src/app/mistakes/[slug]/page.tsx`
- 可选：`src/app/mistakes/[slug]/mistake-detail-content.tsx`

**子任务**:

- [x] 原题和图片证据置顶。
- [x] 独立展示错误原因、正确步骤、知识点、变式题。当前扩展字段合并展示在“错因与解析”。
- [x] 复习状态和下一次复习清晰展示。
- [ ] 支持跳转关联笔记。

**验收标准**:

- 错题详情像学习页，而不是普通笔记详情的附加区域。

### T-104: 复习规划后端 API

**对应需求**: FR-9
**影响域**: review, mistakes
**文件范围**:

- `backend/app/routers/review.py`
- `backend/app/services/review_planner.py`
- `backend/app/schemas/note.py` 或新 schema
- `src/lib/api/review.ts`

**子任务**:

- [x] 增加今日规划 endpoint。
- [x] 增加本周规划 endpoint。
- [x] 增加薄弱知识点聚合。
- [x] 按科目统计待复习和高频错误。
- [x] 前端 API client 同步。

**验收标准**:

- 前端能拿到今日、本周、薄弱点三个维度的数据。

### T-105: 错题列表规划卡片

**对应需求**: FR-9
**影响域**: mistakes
**文件范围**:

- `src/app/mistakes/page.tsx`
- 可选：`src/app/mistakes/components/review-plan-card.tsx`
- 可选：`src/app/mistakes/components/weakness-summary-card.tsx`

**子任务**:

- [x] 今日复习卡片。
- [x] 本周薄弱点卡片。
- [x] 科目统计卡片。
- [x] “开始复习”入口保持醒目。

**验收标准**:

- 用户进入 `/mistakes` 能立即知道今天该做什么。

### T-106: 复习完成总结

**对应需求**: FR-9.6
**影响域**: review
**文件范围**:

- `src/app/mistakes/review/page.tsx`
- `backend/app/routers/review.py`

**子任务**:

- [ ] 记录本次复习题数。
- [ ] 显示掌握程度分布。
- [ ] 显示下一步复习建议。
- [ ] 支持回到错题集或继续整理。

**验收标准**:

- 复习完成页不是只有“完成”，还包含总结和下一步。

### T-107: P1 验证

**验证**:

- [ ] 上传错题图片并触发 AI 分析。
- [ ] 粘贴错题文本并触发 AI 分析。需要真实 AI key 或 mock 验收。
- [ ] 保存错题后检查详情字段。需要配合真实 AI 或手工构造扩展内容。
- [ ] 完成一次复习并查看总结。
- [x] `npx tsc --noEmit`。
- [x] 后端 import/start check。

## 阶段 P2: AI 写作助手

目标：让 AI 基于当前编辑器上下文帮助写作。

### T-201: AI 写作助手后端 API

**对应需求**: FR-3
**影响域**: AI, notes
**文件范围**:

- `backend/app/schemas/ai_polish.py` 或新 schema
- `backend/app/services/writing_assistant.py`
- `backend/app/routers/ai_polish.py` 或新 router

**子任务**:

- [ ] 定义 action：rewrite、expand、summarize、continue、title、outline、tags、diagram、compare、mindmap。
- [ ] 请求体包含 selected text、full content、title、note type。
- [ ] 响应支持纯文本和 structured result。
- [ ] 保持鉴权和速率限制。

**验收标准**:

- 后端可按 action 返回不同写作结果。

### T-202: 前端 writing assistant API client

**对应需求**: FR-3
**影响域**: notes
**文件范围**:

- `src/lib/api/writing-assistant.ts`

**子任务**:

- [ ] 定义请求类型。
- [ ] 定义响应类型。
- [ ] 支持流式或普通响应。
- [ ] 错误信息对 UI 友好。

**验收标准**:

- 写笔记页面不直接散落 fetch。

### T-203: AI 写作面板 UI

**对应需求**: FR-3, NFR-1
**影响域**: notes
**文件范围**:

- `src/app/write-note/components/ai-writing-panel.tsx`
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`

**子任务**:

- [ ] 右侧可折叠面板。
- [ ] 移动端底部抽屉。
- [ ] 当前选区操作分组。
- [ ] 插入内容分组。
- [ ] 全文处理分组。
- [ ] loading 和错误状态。

**验收标准**:

- 面板符合当前 UI，不遮挡编辑器。

### T-204: 选区和光标上下文集成

**对应需求**: FR-3.2, FR-3.3, FR-3.4
**影响域**: notes
**文件范围**:

- `src/app/write-note/hooks/use-note-editor.ts`
- `src/app/write-note/components/ai-writing-panel.tsx`

**子任务**:

- [ ] 获取当前选中文本。
- [ ] 获取光标位置。
- [ ] 支持插入到光标。
- [ ] 支持替换选区。
- [ ] 保持撤销路径尽量自然。

**验收标准**:

- 用户能明确选择插入或替换。

### T-205: 表单字段应用

**对应需求**: FR-3.5
**影响域**: notes
**文件范围**:

- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`

**子任务**:

- [ ] 生成标题可应用到标题字段。
- [ ] 生成摘要可应用到摘要字段。
- [ ] 生成标签可合并到 tags。
- [ ] 生成目录插入正文。

**验收标准**:

- AI 不只插正文，也能帮助补元数据。

### T-206: P2 验证

**验证**:

- [ ] 选中文本改写。
- [ ] 选中文本总结。
- [ ] 光标插入续写。
- [ ] 生成标题/摘要/标签。
- [ ] 移动端面板可用。
- [ ] `npx tsc --noEmit`。

## 阶段 P3: 内容块与多样化表达

目标：让笔记支持图表、对比、思维导图、颜色和高亮。

### T-301: 对比块语法和渲染

**对应需求**: FR-6.3
**影响域**: notes, markdown
**文件范围**:

- `src/lib/markdown-renderer.ts`
- `src/hooks/use-markdown-render.tsx`
- `src/components/compare-block.tsx`
- `src/styles/article.css`

**子任务**:

- [ ] 定义 `:::compare` 语法。
- [ ] 渲染左右/多项对比。
- [ ] 移动端纵向堆叠。
- [ ] 样式符合文章卡片风格。

### T-302: 思维导图块

**对应需求**: FR-6.2
**影响域**: notes, markdown

**子任务**:

- [ ] 支持 Mermaid mindmap 模板。
- [ ] 可选支持 `:::mindmap` 语法。
- [ ] 渲染失败时显示原始内容。
- [ ] 使用现有 `DiagramViewer` 查看大图。

### T-303: 颜色与高亮色板

**对应需求**: FR-6.5, FR-6.6
**影响域**: notes, markdown

**子任务**:

- [ ] 定义受控色板。
- [ ] 工具栏支持高亮。
- [ ] 工具栏支持文字颜色。
- [ ] 渲染器仅允许受控颜色 token。

**验收标准**:

- 用户不能插入任意破坏 UI 的颜色。

### T-304: 内容块插入器

**对应需求**: FR-6
**影响域**: notes

**文件范围**:

- `src/app/write-note/components/content-block-inserter.tsx`
- `src/app/write-note/components/note-toolbar.tsx`

**子任务**:

- [ ] 插入表格。
- [ ] 插入图表模板。
- [ ] 插入对比块模板。
- [ ] 插入思维导图模板。
- [ ] 插入复习卡片模板。

### T-305: 图表和大图查看体验

**对应需求**: FR-6.7, NFR-4.3
**影响域**: shared UI, markdown

**文件范围**:

- `src/components/diagram-viewer.tsx`
- `src/components/markdown-image.tsx`
- `src/components/mermaid-block.tsx`
- `src/styles/article.css`

**子任务**:

- [ ] 图片可全屏查看。
- [ ] Mermaid 可全屏查看。
- [ ] 支持缩放和重置。
- [ ] 移动端不溢出。

### T-306: 内容块验收样例

**对应需求**: FR-6
**影响域**: notes

**子任务**:

- [ ] 创建测试笔记，包含图表、对比块、思维导图、表格、高亮、颜色。
- [ ] 检查编辑预览。
- [ ] 检查详情渲染。
- [ ] 检查移动端。

### T-307: P3 验证

**验证**:

- [ ] `npx tsc --noEmit`
- [ ] 前端 UI 手动检查。
- [ ] Mermaid 错误语法降级检查。

## 阶段 P4: 文件夹与拖拽排序

目标：建立真正的信息架构，让长期内容可归档、可排序。

### T-401: Folder 后端模型和迁移

**对应需求**: FR-7
**影响域**: notes, shared backend
**文件范围**:

- `backend/app/models/`
- `backend/app/schemas/`
- `backend/alembic/versions/`

**子任务**:

- [ ] 新增 `Folder` 模型。
- [ ] `Note` 增加 `folder_id`。
- [ ] `Note` 增加 `sort_order`。
- [ ] 增加索引。
- [ ] 新增 Alembic migration。

### T-402: Folder API

**对应需求**: FR-7
**影响域**: notes
**文件范围**:

- `backend/app/routers/folders.py`
- `backend/app/services/folder_service.py`
- `backend/main.py`

**子任务**:

- [ ] list folder tree。
- [ ] create folder。
- [ ] rename folder。
- [ ] delete folder。
- [ ] reorder folders。
- [ ] move note to folder。
- [ ] reorder notes in folder。

### T-403: 前端 folders API client

**对应需求**: FR-7
**影响域**: notes
**文件范围**:

- `src/lib/api/folders.ts`

**子任务**:

- [ ] 定义 Folder 类型。
- [ ] 定义 folder tree 类型。
- [ ] 定义移动和排序请求。
- [ ] 错误处理。

### T-404: 知识库侧栏

**对应需求**: FR-7, 信息架构需求
**影响域**: notes, mistakes, manage
**文件范围**:

- `src/app/notes/components/knowledge-sidebar.tsx`
- `src/app/notes/page.tsx`
- `src/app/mistakes/page.tsx`
- `src/app/manage/page.tsx`

**子任务**:

- [ ] 显示全部、收件箱、博客、笔记、错题。
- [ ] 显示文件夹树。
- [ ] 显示标签入口。
- [ ] 移动端抽屉。

### T-405: 拖拽移动和排序

**对应需求**: FR-7.4, FR-7.5, FR-7.6
**影响域**: notes

**子任务**:

- [ ] 选择轻量拖拽方案。
- [ ] 拖笔记到文件夹。
- [ ] 拖文件夹排序。
- [ ] 拖笔记排序。
- [ ] 刷新后顺序保持。

### T-406: 移动端替代操作

**对应需求**: FR-7.7
**影响域**: notes

**子任务**:

- [ ] 笔记列表项提供“移动到”菜单。
- [ ] 文件夹提供“上移/下移”或排序输入。
- [ ] 支持移动端完成同等核心操作。

### T-407: 文件夹验收

**验证**:

- [ ] 新建文件夹。
- [ ] 新建子文件夹。
- [ ] 移动笔记。
- [ ] 排序文件夹。
- [ ] 排序笔记。
- [ ] 刷新验证持久化。

### T-408: P4 验证

**验证**:

- [ ] Alembic migration 应用。
- [ ] 后端 import/start check。
- [ ] `npx tsc --noEmit`。
- [ ] 桌面/移动端手动检查。

## 阶段 P5: AI 知识库管家

目标：让 AI 帮助管理整个知识库，而不是只辅助当前文本。

### T-501: 知识库分析服务

**对应需求**: FR-2
**影响域**: AI, notes, mistakes
**文件范围**:

- `backend/app/services/knowledge_assistant.py`
- `backend/app/routers/ai.py` 或新 router
- `backend/app/schemas/`

**子任务**:

- [ ] 查询最近内容。
- [ ] 查询缺标签内容。
- [ ] 查询缺文件夹内容。
- [ ] 聚合错题薄弱点。
- [ ] 生成整理建议。

### T-502: AI 整理建议 API

**对应需求**: FR-2
**影响域**: AI

**子任务**:

- [ ] 定义建议类型：tag、folder、summary、related、review。
- [ ] 建议包含目标内容、理由、建议动作。
- [ ] 默认不执行修改。

### T-503: 前端整理建议卡片

**对应需求**: FR-2.7
**影响域**: notes, mistakes, manage, home
**文件范围**:

- `src/app/notes/components/ai-organize-card.tsx`
- `src/app/mistakes/components/weakness-summary-card.tsx`
- `src/app/manage/page.tsx`
- 可选：首页卡片

**子任务**:

- [ ] `/notes` 显示整理建议。
- [ ] `/mistakes` 显示薄弱点建议。
- [ ] `/manage` 显示内容体检。
- [ ] 首页显示简短今日建议。

### T-504: 批量建议确认执行

**对应需求**: FR-2.6, NFR-3.4
**影响域**: manage, notes

**子任务**:

- [ ] 建议详情弹窗。
- [ ] 用户确认后执行。
- [ ] 显示影响范围。
- [ ] 执行失败可回滚或提示补救。

### T-505: 每周学习总结

**对应需求**: FR-2.4, FR-9.7
**影响域**: review, mistakes, AI

**子任务**:

- [ ] 按周聚合错题和复习。
- [ ] AI 输出主要薄弱点。
- [ ] AI 输出下周建议。
- [ ] 可保存为笔记或展示为卡片。

### T-506: P5 验证

**验证**:

- [ ] 有内容时生成具体建议。
- [ ] 无内容时展示空状态。
- [ ] 批量执行前必须确认。
- [ ] `npx tsc --noEmit`。
- [ ] 后端 import/start check。

## 阶段 P6: 数据可靠性与公开边界

目标：保证个人长期内容不丢、不误公开。

### T-601: 图片持久化方案确认

**对应需求**: NFR-3.1
**影响域**: notes, mistakes, shared infrastructure

**子任务**:

- [ ] 评估对象存储、持久卷、GitHub/private backup。
- [ ] 明确 public/private 图片策略。
- [ ] 写入架构说明。

### T-602: 图片上传后端迁移

**对应需求**: NFR-3.1
**影响域**: backend, notes, mistakes

**子任务**:

- [ ] 上传不再依赖易丢失本地目录，或本地目录有持久卷。
- [ ] 数据库存储稳定 URL 或 object key。
- [ ] 删除图片有保留/清理策略。

### T-603: 公开导出过滤

**对应需求**: FR-1, NFR-3.2
**影响域**: sync, blog, notes, mistakes

**子任务**:

- [ ] RSS 只包含公开博客。
- [ ] sitemap 只包含公开博客。
- [ ] GitHub public export 只导出公开内容。
- [ ] 私有备份与公开导出分离。

### T-604: 数据备份和恢复说明

**对应需求**: NFR-3
**影响域**: shared infrastructure

**子任务**:

- [ ] 数据库备份流程。
- [ ] 图片备份流程。
- [ ] 恢复流程。
- [ ] 验证一次恢复演练。

### T-605: P6 验证

**验证**:

- [ ] 创建私有笔记，确认不出现在 RSS/sitemap。
- [ ] 创建公开博客，确认出现在 RSS/sitemap。
- [ ] 上传错题图片，重启/迁移后仍可访问。
- [ ] 执行备份恢复演练。

## 全局验证要求

按 touched domain 选择验证：

- 前端 TypeScript 变更：`npx tsc --noEmit`
- 前端 build-sensitive 变更：`npm run build`
- 前端 UI 变更：启动 dev server 并检查相关路由
- 后端 Python 变更：后端 import/start check
- API contract 变更：同步前端 client types 和后端 schema
- 数据库模型变更：Alembic migration

若验证失败，阶段报告必须记录：

- 失败命令。
- 第一处关键错误。
- 是否为既有问题。
- 本阶段是否引入新风险。

## 当前已知待处理结构问题

> **注意**: 本节内容已大部分修复。后续任务请参考 `docs/roadmap-tasks.md`（2026-06-02 版本）。

以下问题来自早期结构审查，修复状态如下：

- [x] `backend/main.py` import 了 `categories`、`subjects`，但当前未 include 对应 router。 → **已修复**: router 已 include。
- [x] 管理面板标题链接当前统一跳 `/notes/{slug}`，与 `blog` 的主要详情入口 `/blog/{slug}` 不一致。 → **已修复**: `getContentDetailHref` / `getContentEditHref` 按 type 分流。
- [ ] `/mistakes` 当前跳 `/notes/{slug}`，需要确认是否新增独立错题详情页。 → **已决策**: P1 阶段暂不新增，复用 `/notes/{slug}`。
- [x] `/write` 保存博客后只 toast 成功，没有统一跳转或"查看文章"入口。 → **已修复**: 保存后跳转已统一。
- [ ] 静态内容页仍走 JSON + `push-*` 服务，需要在系统地图中长期标注为静态配置线。 → **长期标注**，不做修改。
