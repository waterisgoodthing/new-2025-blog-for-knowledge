# 个人知识与博客系统整体演进设计

## 1. 设计目标

本项目后续不再按普通博客系统扩展，而是演进为一个只服务个人长期使用的知识系统。

核心目标：

- 用一个统一知识库承载博客、普通笔记、错题和复习状态。
- 保留当前柔和、轻量、卡片化的 UI 气质，不推翻现有视觉风格。
- 引入两个 AI 角色：知识库 AI 管家和编辑器 AI 写作助手。
- 提升笔记编辑体验，支持图表、对比块、颜色、高亮、思维导图和模板。
- 建立文件夹、拖拽排序和清晰的信息归档结构。
- 升级错题 AI 解析、复习计划和知识点归总能力。

## 2. 当前系统定位

当前项目有两条架构线：

- `src/`：Next.js App Router 前端与原静态博客系统。
- `backend/`：FastAPI、PostgreSQL、JWT、notes、mistakes、review、AI、GitHub sync 后端。

后续应以 `backend` 的 `Note` 模型为主数据源：

- `type=blog`：公开博客或博客草稿。
- `type=note`：普通个人笔记。
- `type=mistake`：错题记录和复习对象。

`public/` 和 GitHub sync 只作为公开发布、静态资源或备份出口，不应继续作为主要业务数据源。

## 3. 总体架构

```text
用户操作
  -> Next.js 前端工作台
  -> src/lib/api/*
  -> FastAPI router
  -> service/domain logic
  -> PostgreSQL
  -> 可选：对象存储 / GitHub 公开导出 / 私有备份
```

推荐架构分层：

```text
前端展示层
  - 首页
  - 博客公开页
  - 笔记工作台
  - 错题与复习页
  - 管理面板

前端业务层
  - route-specific components/hooks
  - src/lib/api typed clients
  - editor state
  - drag-and-drop state

后端 API 层
  - auth router
  - notes router
  - review router
  - ai router
  - folders/taxonomy router
  - sync/export router

后端服务层
  - note service
  - mistake analysis service
  - review planning service
  - knowledge assistant service
  - export/backup service

数据层
  - PostgreSQL
  - durable image/object storage
  - optional public static export
```

## 4. 产品主线

### 4.1 AI 知识库管家

AI 管家面向整个知识库，而不是当前编辑器文本。

能力范围：

- 分析最近笔记、错题和博客内容。
- 发现重复内容、缺少标签、缺少分类、解析不完整的错题。
- 推荐文件夹、标签、科目和关联笔记。
- 总结本周学习薄弱点和高频错误类型。
- 生成每日、每周复习规划。
- 对批量整理动作给出建议，由用户确认后执行。

典型入口：

- `/notes` 顶部或侧边的“AI 整理建议”卡片。
- `/mistakes` 顶部的“薄弱点与复习规划”卡片。
- `/manage` 中的“内容体检”面板。
- 首页卡片中的“今日建议”摘要。

管家行为原则：

- 默认只给建议，不直接修改数据。
- 所有批量修改必须让用户确认。
- 建议应引用具体笔记、错题、标签或文件夹。
- 管家输出应短而可执行，避免变成泛泛聊天。

### 4.2 AI 写作助手

AI 写作助手面向当前正在编辑的一篇内容。

能力范围：

- 续写、改写、扩写、总结。
- 根据当前内容生成标题、摘要、标签和目录。
- 把一段内容转换成表格、对比块、流程图、思维导图。
- 把口语化记录整理成结构化笔记。
- 把错题解析转换成知识点笔记。
- 根据选中文本生成复习卡片或提问。

编辑上下文：

- 当前笔记标题。
- 当前笔记类型。
- 当前全文。
- 当前选中文本。
- 光标位置。
- 已有标签、分类、文件夹。

UI 位置：

- 写笔记页面右侧轻量面板。
- 重要操作也可以出现在顶部工具栏的 AI 分组中。

### 4.3 笔记编辑体验

编辑器应从单纯 Markdown textarea 升级为“Markdown + 可视化内容块”的体验。

第一阶段仍然保留 Markdown 作为主要存储格式，新增块语法和渲染能力：

- 图表：Mermaid。
- 思维导图：Mermaid mindmap 或自定义 mindmap block。
- 对比块：用于概念、方案、知识点对照。
- 高亮块：提示、重点、警告、总结。
- 表格：插入模板和编辑辅助。
- 字体颜色和高亮：使用受控色板。
- 复习卡片：从笔记生成问题和答案。

示例块语法：

```md
:::compare
title: 函数与方法对比
left: 函数
right: 方法
- 定义位置不同
- 调用方式不同
- this 绑定不同
:::
```

```md
:::mindmap
中心主题
  一级节点
    二级节点
:::
```

短期不要直接切换到复杂 JSON 编辑器。先增强 Markdown 渲染和插入体验，等内容块稳定后再评估结构化存储。

### 4.4 文件夹与拖拽排序

标签和分类适合横向组织，文件夹适合纵向归档。后续应新增文件夹系统。

建议数据模型：

- `Folder`
  - `id`
  - `name`
  - `parent_id`
  - `sort_order`
  - `created_at`
  - `updated_at`
- `Note.folder_id`
- `Note.sort_order`

核心能力：

- 文件夹树。
- 文件夹内笔记排序。
- 拖拽笔记到文件夹。
- 拖拽调整同级文件夹顺序。
- 收件箱：未归档内容默认进入收件箱。

推荐信息架构：

```text
全部内容
今日复习
收件箱
博客
笔记
错题

文件夹
  数学
    函数
    导数
  英语
  编程
  生活

标签
  React
  数学
  写作
```

### 4.5 错题解析与复习规划

错题模块后续应从“记录错题”升级为“分析错误、归纳知识、安排复习”。

AI 解析输出结构应固定为：

```text
题目识别
我的错误点
正确答案
完整解题步骤
关键转折点
为什么我会错
涉及知识点
相似易错点
举一反三
记忆提醒
复习建议
关联笔记
变式题
```

错题详情页建议分区：

```text
原题与图片证据
AI 解析
错误原因
知识点归纳
变式题
关联笔记
复习状态
复习历史
下一步计划
```

复习规划能力：

- 今日复习队列。
- 本周薄弱知识点。
- 按科目统计。
- 按知识点统计。
- 高频错误原因统计。
- 最近 7 天复习完成度。
- AI 每周学习总结。

## 5. UI 设计约束

后续功能必须符合当前 UI 布局和视觉风格。

保留特征：

- 半透明白色面板。
- `rounded-xl` 或相近圆角。
- 柔和品牌色 `var(--color-brand)`。
- 轻量 `motion/react` 动效。
- 居中内容宽度。
- 卡片化信息分区。
- 低压、个人化、非 SaaS 后台气质。

避免方向：

- 不做营销式 landing page。
- 不做重型企业后台风格。
- 不引入突兀的全新视觉语言。
- 不让按钮只剩抽象图标。
- 不再依赖用户记忆 `/` 指令才能使用模板。

### 5.1 按钮体验

当前主要问题是用户不知道按钮是什么、能做什么。改进规则：

- 重要操作使用“图标 + 文字”。
- 图标按钮必须有 `aria-label` 和 tooltip。
- 工具栏按钮按功能分组。
- 危险操作使用清晰的红色弱背景和二次确认。
- 发布、保存、删除、批量操作要有明确反馈。

推荐工具栏分组：

```text
保存  预览

插入
图片  表格  图表  对比  思维导图  代码

AI
续写  改写  总结  生成结构

格式
加粗  斜体  高亮  颜色  引用

模板
课堂笔记  错题解析  读书笔记  项目复盘
```

### 5.2 模板入口

模板不再主要依赖 `/` 指令。

推荐方案：

- 顶部工具栏提供“模板”按钮。
- 点击后打开半透明模板面板。
- 每个模板显示名称和一句说明。
- 插入后用户可以直接编辑。

示例：

```text
模板
课堂笔记      适合整理课程概念、例题和总结
错题解析      适合记录错误原因、正确思路和复习提醒
读书笔记      适合整理观点、摘录和自己的想法
项目复盘      适合总结目标、过程、问题和改进
```

`/` 指令可以保留为高级快捷入口，但不作为主要入口。

### 5.3 AI 面板

AI 写作助手应贴合现有布局：

```text
编辑器主体
  左侧：Markdown 编辑区
  右侧：AI 助手面板
```

右侧面板分组：

```text
AI 助手

当前选区
改写  扩写  总结  提炼要点

插入内容
对比块  图表  思维导图  复习卡片

全文处理
生成标题  生成摘要  生成目录  推荐标签
```

面板应可折叠，移动端改为底部抽屉。

### 5.4 文件夹侧栏

文件夹不应破坏当前卡片式列表。推荐在 `/notes`、`/mistakes`、`/manage` 使用左侧轻量侧栏：

```text
┌──────────────┬──────────────────────────┐
│ 知识库侧栏   │ 当前列表 / 当前详情       │
│ 文件夹       │ 卡片列表                 │
│ 标签         │ 搜索、筛选、分页          │
└──────────────┴──────────────────────────┘
```

移动端侧栏收进抽屉。

## 6. 数据与权限原则

### 6.1 数据真源

推荐原则：

- PostgreSQL 是主数据源。
- `public/` 是静态资产或导出结果。
- GitHub sync 是发布器和备份器，不是内容真源。
- 图片证据和笔记图片应进入持久对象存储或有备份的持久卷。

### 6.2 公开规则

默认规则：

- `note` 默认私有。
- `mistake` 默认私有。
- `blog` 可以公开，但必须满足 `status=published` 且 `hidden=false`。
- RSS、sitemap、公开博客列表只能读取公开内容。

### 6.3 AI 操作规则

- AI 管家默认只建议，不直接批量修改。
- AI 写作助手可以直接插入当前编辑器，但要保留撤销路径。
- 任何删除、公开发布、批量移动、批量改标签都需要用户确认。

## 7. 后端演进建议

建议新增或扩展的后端模块：

```text
backend/app/models/folder.py
backend/app/schemas/folder.py
backend/app/routers/folders.py
backend/app/services/knowledge_assistant.py
backend/app/services/writing_assistant.py
backend/app/services/mistake_analysis.py
backend/app/services/review_planner.py
```

也可以先不新建所有文件，按照现有边界逐步演进：

- AI 管家逻辑放入 `backend/app/services/ai_service.py` 的新函数，稳定后拆分。
- 复习规划先扩展 `backend/app/services/sm2.py` 和 `backend/app/routers/review.py`。
- 文件夹必须新增模型、schema、router 和迁移。

## 8. 前端演进建议

推荐新增或调整的前端模块：

```text
src/app/notes/components/knowledge-sidebar.tsx
src/app/notes/components/ai-organize-card.tsx
src/app/write-note/components/editor-command-bar.tsx
src/app/write-note/components/template-panel.tsx
src/app/write-note/components/content-block-inserter.tsx
src/app/write-note/components/ai-writing-panel.tsx
src/app/mistakes/components/review-plan-card.tsx
src/app/mistakes/components/weakness-summary-card.tsx
src/components/tooltip.tsx
src/components/confirm-dialog.tsx
```

API client 建议：

```text
src/lib/api/folders.ts
src/lib/api/knowledge-assistant.ts
src/lib/api/writing-assistant.ts
src/lib/api/review-plan.ts
```

## 9. 开发阶段规划

### 阶段一：交互可理解性

目标：用户知道每个按钮做什么。

范围：

- 重组写笔记工具栏。
- 给图标按钮补齐文字、tooltip、`aria-label`。
- 模板入口改为可见面板。
- 保留 `/` 指令作为高级快捷方式。

验收：

- 不看文档也能理解主要按钮。
- 重要操作不只有图标。
- 模板可以通过明确按钮打开。

### 阶段二：错题 AI 与复习规划

目标：错题解析更完整，复习计划更清楚。

范围：

- 改造 AI 解析 prompt 和响应 schema。
- 错题详情页增加解析分区。
- `/mistakes` 增加薄弱点和今日规划。
- `/mistakes/review` 增加复习完成总结。

验收：

- AI 输出包含错误原因、完整步骤、知识点、变式题和复习建议。
- 用户能看到今日、本周和薄弱点维度的复习规划。

### 阶段三：AI 写作助手

目标：AI 深度参与当前笔记写作。

范围：

- 右侧 AI 写作面板。
- 选区操作。
- 全文标题、摘要、目录、标签生成。
- 内容转换为图表、对比块、思维导图。

验收：

- AI 可以基于选中文本插入或替换。
- AI 结果能直接进入编辑器。
- 用户能明确选择“插入到光标”或“替换选区”。

### 阶段四：内容块体验

目标：笔记不只是一篇纯 Markdown。

范围：

- 对比块。
- Mermaid 图表模板。
- 思维导图模板。
- 颜色和高亮色板。
- 复习卡片块。

验收：

- 插入块可预览。
- 渲染结果符合现有文章样式。
- 移动端不溢出、不遮挡。

### 阶段五：文件夹与拖拽排序

目标：形成真正的知识空间。

范围：

- Folder 后端模型和迁移。
- 文件夹树 API。
- 知识库侧栏。
- 拖拽移动和排序。
- 收件箱。

验收：

- 笔记可以移动到文件夹。
- 同级文件夹和笔记可以排序。
- 刷新后顺序保持。
- 移动端可通过菜单/抽屉完成同等操作。

### 阶段六：AI 知识库管家

目标：AI 帮助管理整个知识库。

范围：

- 内容体检。
- 标签/文件夹建议。
- 关联笔记建议。
- 每周学习总结。
- 批量整理建议和确认执行。

验收：

- AI 输出具体条目和理由。
- 用户确认后才执行批量修改。
- 修改结果可在管理面板验证。

## 10. 风险与边界

主要风险：

- 一次性改太多导致现有写作链路不稳定。
- AI 输出不可控，影响错题质量。
- 文件夹和标签概念混用。
- 内容块语法过早复杂化。
- 图片存储不持久导致证据丢失。

控制方式：

- 按阶段推进，每阶段独立验收。
- AI 先建议后执行。
- 文件夹只负责归档，标签负责横向关联。
- 第一阶段继续使用 Markdown 存储。
- 图片持久化和备份作为基础设施优先项。

## 11. 优先级建议

最高优先级：

1. 按钮和模板入口可理解性。
2. 错题 AI 输出结构升级。
3. 复习规划卡片。
4. AI 写作助手选区操作。
5. 图片持久化和备份策略。

中期优先级：

1. 图表、对比块、思维导图。
2. 文件夹和拖拽排序。
3. AI 知识库管家。

暂缓：

1. 完整块编辑器替换 Markdown。
2. 多用户权限体系。
3. 复杂公开站点营销化改版。

## 12. 成功标准

这个设计完成后，系统应达到以下状态：

- 你可以放心把长期笔记、错题和博客放进同一个知识库。
- 每天打开系统能看到明确的复习、整理和写作入口。
- 写笔记时不用记忆隐藏命令，也能插入模板、图表、对比和思维导图。
- AI 能分别承担“当前内容写作助手”和“整体知识管理助手”两个角色。
- 错题不只是记录，而能形成解析、归纳、复习、变式题和周计划。
- UI 仍然像当前项目，而不是变成另一个陌生产品。
