# 笔记编辑器多维度扩展 — 需求文档

> 版本: 1.0
> 日期: 2026-05-30
> 关联设计文档: `docs/note-editor-design.md`

---

## 1. 项目背景

### 1.1 现状问题

当前笔记编辑器（`src/app/write-note/`）存在以下不足：

- **编辑工具缺失**: 仅有一个"图片"按钮，无格式化工具栏，用户必须手动输入 Markdown 语法
- **快捷键缺失**: 无 Ctrl+B/I/K 等基础快捷键，无 Tab 缩进，无剪贴板图片粘贴
- **渲染能力有限**: 仅支持数学公式、代码高亮、任务列表，不支持提示框、高亮标记、脚注、图表
- **无 AI 辅助**: 笔记编辑侧无任何 AI 能力（现有 AI 仅用于错题识别）
- **无场景化入口**: 缺少笔记模板、快速命令等降低写作门槛的功能

### 1.2 目标

为笔记编辑器增加**多维度的内容创建能力**，覆盖以下场景：

| 场景 | 当前 | 目标 |
|------|------|------|
| 快速格式化 | 手动输入 `**` | 工具栏按钮 + 快捷键 |
| 结构化笔记 | 手动输入 `#` `/` | 斜杠命令 + 模板 |
| 学习笔记 | 仅数学公式 | + 高亮 + 脚注 + 提示框 |
| 知识可视化 | 无 | + Mermaid 流程图 + 思维导图 |
| 内容优化 | 无 | + AI 润色/总结/扩写/续写/翻译 |
| 复习辅助 | 无 | + AI 生成问题 + 提取标签 |

---

## 2. 功能需求

### FR-1: 格式工具栏

**优先级**: P0

**描述**: 在笔记编辑区上方提供分组格式按钮，覆盖常用 Markdown 语法。

**需求细节**:

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-1.1 | 工具栏包含文本格式组: 加粗、斜体、删除线、高亮、行内代码 | 点击按钮在光标位置插入对应 Markdown 语法 |
| FR-1.2 | 工具栏包含标题组: H1、H2、H3 | 点击按钮在行首插入 `#`/`##`/`###` |
| FR-1.3 | 工具栏包含插入组: 链接、图片、表格、分割线 | 点击按钮插入对应 Markdown 模板 |
| FR-1.4 | 工具栏包含列表组: 无序列表、有序列表、任务列表、引用 | 点击按钮在行首插入对应前缀 |
| FR-1.5 | 工具栏包含高级组: 代码块、公式块、行内公式、脚注 | 点击按钮插入对应多行模板 |
| FR-1.6 | 工具栏包含提示框组: NOTE、TIP、WARNING、CAUTION、IMPORTANT | 点击按钮插入 `> [!TYPE]` 模板 |
| FR-1.7 | 选中文字后点击格式按钮，自动包裹选中文字 | 选中"内容" + 点击加粗 → `**内容**` |
| FR-1.8 | 已包裹的文字再次点击，去除包裹 | 光标在 `**内容**` 内 + 点击加粗 → `内容` |
| FR-1.9 | 工具栏 UI 遵循现有设计风格 | `rounded-lg bg-white/40 p-1.5`，按钮 `h-7 w-7 rounded-md` |
| FR-1.10 | 工具栏在 create 和 edit 页面均可用 | `write-note/page.tsx` 和 `write-note/[slug]/page.tsx` 共用 |

---

### FR-2: 键盘快捷键

**优先级**: P0

**描述**: 为笔记编辑器提供常用键盘快捷键。

| 编号 | 快捷键 | 功能 | 验收标准 |
|------|--------|------|---------|
| FR-2.1 | `Ctrl/Cmd + B` | 加粗切换 | 选中文字时包裹/去除 `**`，未选中时插入 `**文本**` 并选中"文本" |
| FR-2.2 | `Ctrl/Cmd + I` | 斜体切换 | 同上，使用 `*` |
| FR-2.3 | `Ctrl/Cmd + K` | 插入链接 | 插入 `[文本](url)` 并选中 "url" 部分 |
| FR-2.4 | `Tab` | 缩进 | 在光标位置插入制表符 |
| FR-2.5 | `Shift + Tab` | 反缩进 | 移除行首一个制表符或两个空格 |
| FR-2.6 | `Ctrl/Cmd + Shift + T` | 插入时间戳 | 在光标位置插入 `YYYY-MM-DD HH:mm` |
| FR-2.7 | `Ctrl/Cmd + P` | 切换编辑/预览 | 已有功能，保持不变 |

**约束**: 使用 `document.execCommand('insertText')` 实现插入，以保持浏览器原生 undo/redo 栈。`execCommand` 不可用时回退到直接修改 value + `setSelectionRange`。

---

### FR-3: 剪贴板图片粘贴

**优先级**: P0

**描述**: 支持从剪贴板粘贴图片，自动上传并插入 Markdown 图片语法。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-3.1 | 粘贴事件检测 `clipboardData.items` 中的 `image/*` | 粘贴图片时不插入 base64，触发上传流程 |
| FR-3.2 | 调用现有 `uploadImage(file)` 上传 | 复用 `src/lib/api/notes.ts` 的 `uploadImage` |
| FR-3.3 | 上传成功后插入 `![](url)` | Markdown 预览中可正常显示图片 |
| FR-3.4 | 上传中显示 toast 提示 | `toast.loading('上传中...')` + `toast.success('上传成功')` |
| FR-3.5 | 上传失败显示错误 | `toast.error('上传失败: ' + message)` |

---

### FR-4: 斜杠命令菜单

**优先级**: P1

**描述**: 在编辑器中输入 `/` 弹出命令面板，支持中文和拼音搜索，快速插入内容块。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-4.1 | 输入 `/` 时在光标位置附近弹出菜单 | 菜单使用 `createPortal` 定位到 `document.body` |
| FR-4.2 | 继续输入字符过滤命令列表 | 输入 `/表` 只显示"表格"相关命令 |
| FR-4.3 | 支持中文关键词匹配 | 输入 `/代码` 匹配"代码块" |
| FR-4.4 | 支持拼音首字母匹配 | 输入 `/dmk` 匹配"代码块" |
| FR-4.5 | `↑`/`↓` 键导航命令列表 | 当前选中项高亮 `bg-brand/10 text-brand` |
| FR-4.6 | `Enter` 确认选中 | 删除 `/query` 文本，插入命令对应内容 |
| FR-4.7 | `Escape` 关闭菜单 | 不插入任何内容 |
| FR-4.8 | 点击菜单外部关闭 | 不插入任何内容 |
| FR-4.9 | 命令数量 ≥ 20 个 | 覆盖标题、格式、代码、公式、表格、列表、提示框、分割线、时间戳、折叠、图表、思维导图、脚注 |
| FR-4.10 | 菜单 UI 遵循现有设计风格 | `bg-card/95 backdrop-blur-xl rounded-xl border`，命令项 `rounded-lg px-3 py-2 text-sm` |
| FR-4.11 | 菜单最大高度 `max-h-64`，内容溢出时滚动 | 长命令列表可滚动 |

---

### FR-5: 笔记模板

**优先级**: P2

**描述**: 提供预设笔记模板，一键插入到编辑器。

| 编号 | 模板 | 验收标准 |
|------|------|---------|
| FR-5.1 | 学习笔记 | 包含: 标题、核心概念、要点整理、例题/案例、总结 |
| FR-5.2 | 会议记录 | 包含: 标题、时间/参会人、议题、结论、待办清单 |
| FR-5.3 | 日记/日志 | 包含: 日期标题、今日完成、明日计划、备注 |
| FR-5.4 | 读书笔记 | 包含: 书名、作者/日期、核心观点、精彩摘录、个人感想 |
| FR-5.5 | 项目笔记 | 包含: 标题、背景、方案对比、当前进度、风险提示 |
| FR-5.6 | 模板通过工具栏下拉菜单选择 | 点击模板项插入完整 Markdown 文本到光标位置 |
| FR-5.7 | 模板中的日期自动填充当天日期 | `# 2026-05-30 日志` |

---

### FR-6: GitHub Alerts 提示框

**优先级**: P1

**描述**: 渲染器支持 GitHub 风格的 Alerts 提示框语法。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-6.1 | 支持 `> [!NOTE]` 语法 | 渲染为蓝色左边框提示框，标题"注意" |
| FR-6.2 | 支持 `> [!TIP]` 语法 | 渲染为绿色提示框，标题"技巧" |
| FR-6.3 | 支持 `> [!WARNING]` 语法 | 渲染为黄色提示框，标题"警告" |
| FR-6.4 | 支持 `> [!CAUTION]` 语法 | 渲染为红色提示框，标题"危险" |
| FR-6.5 | 支持 `> [!IMPORTANT]` 语法 | 渲染为紫色提示框，标题"重要" |
| FR-6.6 | 提示框内支持嵌套 Markdown | 段落、列表、代码等正常渲染 |
| FR-6.7 | 非 Alert 语法的普通 blockquote 不受影响 | `> 普通引用` 保持原有样式 |

---

### FR-7: 高亮标记

**优先级**: P1

**描述**: 渲染器支持 `==text==` 高亮语法。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-7.1 | `==文本==` 渲染为 `<mark>文本</mark>` | 黄色背景高亮显示 |
| FR-7.2 | 高亮内支持嵌套行内 Markdown | `==**粗体**和*斜体*==` 正常渲染 |
| FR-7.3 | 不匹配单个 `=` | `=text=` 不触发高亮 |

---

### FR-8: 脚注系统

**优先级**: P1

**描述**: 渲染器支持脚注语法，正文引用 + 文末定义。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-8.1 | 正文 `[^id]` 渲染为上标链接 | `<sup><a href="#fn-id">N</a></sup>` |
| FR-8.2 | 文末 `[^id]: 定义文本` 渲染为脚注列表 | `<section class="footnotes"><ol>...</ol></section>` |
| FR-8.3 | 脚注编号自动递增 | 按出现顺序编号 1, 2, 3... |
| FR-8.4 | 点击上标跳转到脚注定义 | `href="#fn-id"` 锚点跳转 |
| FR-8.5 | 脚注定义旁有返回链接 | 点击可跳回正文引用位置 |
| FR-8.6 | 无脚注定义的引用不渲染 | `[^unknown]` 保持原样 |

---

### FR-9: 可折叠区域

**优先级**: P2

**描述**: 增强 `<details>/<summary>` 标签的渲染样式。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-9.1 | `<details>` 渲染为带边框的圆角容器 | `border: 1px solid rgba(0,0,0,0.08); border-radius: 8px` |
| FR-9.2 | `<summary>` 显示为主题色可点击标题 | `color: var(--color-brand); font-weight: 600; cursor: pointer` |
| FR-9.3 | 展开时内容与标题间有间距 | `margin-bottom: 0.75em` |

---

### FR-10: Mermaid 图表 + 思维导图

**优先级**: P1

**描述**: 支持 Mermaid 语法渲染流程图、时序图、甘特图、思维导图等。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-10.1 | ` ```mermaid ` 代码块渲染为 SVG 图表 | 不走 Shiki 高亮，由 mermaid 库渲染 |
| FR-10.2 | 支持 `graph` 流程图 | 标准 Mermaid flowchart 语法 |
| FR-10.3 | 支持 `sequenceDiagram` 时序图 | 标准 Mermaid sequence 语法 |
| FR-10.4 | 支持 `mindmap` 思维导图 | 标准 Mermaid mindmap 语法 |
| FR-10.5 | 支持 `gantt` 甘特图 | 标准 Mermaid gantt 语法 |
| FR-10.6 | 支持 `pie` 饼图 | 标准 Mermaid pie 语法 |
| FR-10.7 | mermaid 库懒加载 | 首屏不加载，仅在遇到 mermaid 代码块时 `import('mermaid')` |
| FR-10.8 | mermaid 语法错误时显示原始代码 | 不崩溃，降级为普通代码块 |
| FR-10.9 | 图表容器居中，最大宽度 100% | `.prose .mermaid { text-align: center; max-width: 100% }` |
| FR-10.10 | 新增 `mermaid` 前端依赖 | `package.json` 添加 `"mermaid": "^11"` |

---

### FR-11: AI 润色服务

**优先级**: P1

**描述**: 后端新增 AI 文本处理端点，支持多种操作，SSE 流式返回。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-11.1 | 新增 `POST /api/ai/polish` 端点 | 返回 SSE 流式响应 |
| FR-11.2 | 支持 `action: "polish"` 润色 | 优化表达、修正语法、提升可读性 |
| FR-11.3 | 支持 `action: "summarize"` 总结 | 提取核心要点，生成摘要 |
| FR-11.4 | 支持 `action: "expand"` 扩写 | 补充细节、论据和例子 |
| FR-11.5 | 支持 `action: "continue"` 续写 | 根据上下文继续写作 |
| FR-11.6 | 支持 `action: "translate_en"` 中译英 | 中文翻译为英文 |
| FR-11.7 | 支持 `action: "translate_zh"` 英译中 | 英文翻译为中文 |
| FR-11.8 | 支持 `action: "extract_tags"` 提取标签 | 从内容中提取关键词/标签 |
| FR-11.9 | 支持 `action: "generate_questions"` 生成问题 | 基于笔记内容生成复习问题 |
| FR-11.10 | 复用 `ai_service._call_openai_compatible()` | 使用 DeepSeek API（已配置 key） |
| FR-11.11 | 每个 action 有独立的 system prompt | prompt 定义在 service 层 |
| FR-11.12 | 需要 JWT 认证 | `Depends(get_current_admin)` |
| FR-11.13 | 速率限制: 10 次/分钟 | 复用现有 rate limit 模式 |
| FR-11.14 | 请求体: `{ text, action, context? }` | `text` 为待处理文本，`context` 为可选的编辑器全文 |

**SSE 响应格式**:
```
Content-Type: text/event-stream

data: {"chunk": "处理"}
data: {"chunk": "后的"}
data: {"chunk": "文本"}
data: [DONE]
```

---

### FR-12: AI 副面板

**优先级**: P2

**描述**: 编辑器右侧可折叠的 AI 操作面板。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-12.1 | 面板位于编辑器右侧，可折叠/展开 | 折叠态仅显示展开按钮 |
| FR-12.2 | 展开宽度 `w-80` | 不挤压编辑区 |
| FR-12.3 | 包含 8 个 AI 操作按钮 | 润色、总结、扩写、续写、翻译(中→英)、翻译(英→中)、提取标签、生成问题 |
| FR-12.4 | 点击操作按钮后显示 loading 状态 | `animate-pulse` 骨架屏 |
| FR-12.5 | SSE 流式接收结果，逐字显示 | 结果区实时更新 |
| FR-12.6 | 完成后提供三个操作: 插入、替换、复制 | "插入"追加到光标，"替换"替换选中文字，"复制"写入剪贴板 |
| FR-12.7 | 未选中文字时操作全文 | `context` 传入编辑器全部内容 |
| FR-12.8 | 选中文字时仅操作选中部分 | `text` 为选中文字，`context` 为全文 |
| FR-12.9 | 面板 UI 遵循现有设计风格 | `rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm` |

---

### FR-13: 渲染器 CSS 样式

**优先级**: P0

**描述**: 为新增渲染功能提供 CSS 样式。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-13.1 | Alerts 5 种类型各自边框色和背景色 | 见设计文档 §4.1 |
| FR-13.2 | Alerts 标题行带图标 + 加粗文字 | `display: flex; align-items: center; gap: 0.5em` |
| FR-13.3 | 高亮 `<mark>` 黄色背景 | `background: #fef08a; border-radius: 3px` |
| FR-13.4 | 脚注区域上分割线 + 灰色小字 | `border-top: 1px solid; font-size: 0.9em; color: #666` |
| FR-13.5 | 脚注上标链接为主题色 | `color: var(--color-brand); font-weight: 600` |
| FR-13.6 | 可折叠区域边框 + 主题色标题 | 见设计文档 §4.4 |
| FR-13.7 | Mermaid 容器居中 | `text-align: center; max-width: 100%` |
| FR-13.8 | 所有新样式追加到 `src/styles/article.css` | 不新建文件，不破坏现有样式 |

---

## 3. 非功能需求

### NFR-1: 性能

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| NFR-1.1 | mermaid 库懒加载 | 首屏 JS bundle 不增加 mermaid 体积 |
| NFR-1.2 | 斜杠命令搜索使用防抖 | 输入停止 100ms 后才过滤，避免频繁重渲染 |
| NFR-1.3 | AI 流式响应逐字显示 | 使用 SSE，不等待全部返回 |
| NFR-1.4 | 工具栏按钮点击无延迟 | 使用 `execCommand` 而非受控组件模式 |

### NFR-2: 兼容性

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| NFR-2.1 | 不破坏现有 Markdown 渲染 | 现有数学公式、代码高亮、任务列表、图片灯箱、代码复制功能不变 |
| NFR-2.2 | 不破坏现有博客编辑器 | `src/app/write/components/editor.tsx` 不受影响 |
| NFR-2.3 | 不破坏现有错题识别流程 | `POST /api/ai/analyze` 和 `POST /api/ai/analyze-text` 不受影响 |
| NFR-2.4 | 非 Alert 语法的 blockquote 正常渲染 | `> 普通引用` 保持原有左边框样式 |
| NFR-2.5 | mermaid 加载失败时降级 | 显示为普通代码块，不崩溃 |

### NFR-3: 可维护性

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| NFR-3.1 | 工具栏按钮配置化 | 使用数据结构定义按钮列表，便于增删 |
| NFR-3.2 | 斜杠命令配置化 | 使用数据结构定义命令列表，便于增删 |
| NFR-3.3 | AI prompt 集中管理 | 所有 system prompt 定义在 `ai_polish_service.py` 中 |
| NFR-3.4 | 新增组件遵循现有文件组织 | 组件放 `write-note/components/`，hook 放 `write-note/hooks/` |

### NFR-4: 安全性

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| NFR-4.1 | AI 端点需要 JWT 认证 | `Depends(get_current_admin)` |
| NFR-4.2 | AI 端点有速率限制 | 10 次/分钟/用户 |
| NFR-4.3 | Mermaid 渲染使用 `startOnLoad: false` | 防止自动扫描页面中未授权的 mermaid 代码 |
| NFR-4.4 | AI 返回内容不直接注入 DOM | 经过 Markdown 渲染器处理后再显示 |

---

## 4. 文件变更矩阵

| 操作 | 文件路径 | 对应需求 |
|------|---------|---------|
| 新建 | `src/app/write-note/components/note-toolbar.tsx` | FR-1, FR-5 |
| 新建 | `src/app/write-note/components/slash-command-menu.tsx` | FR-4 |
| 新建 | `src/app/write-note/components/ai-assistant-panel.tsx` | FR-12 |
| 新建 | `src/app/write-note/hooks/use-note-editor.ts` | FR-2, FR-3, FR-4 |
| 新建 | `src/lib/api/ai-polish.ts` | FR-11 |
| 新建 | `backend/app/routers/ai_polish.py` | FR-11 |
| 新建 | `backend/app/services/ai_polish_service.py` | FR-11 |
| 新建 | `backend/app/schemas/ai_polish.py` | FR-11 |
| 修改 | `src/lib/markdown-renderer.ts` | FR-6, FR-7, FR-8, FR-10 |
| 修改 | `src/hooks/use-markdown-render.tsx` | FR-10.7 |
| 修改 | `src/styles/article.css` | FR-13 |
| 修改 | `src/app/write-note/page.tsx` | FR-1~5, FR-12 |
| 修改 | `src/app/write-note/[slug]/page.tsx` | FR-1~5, FR-12 |
| 修改 | `package.json` | FR-10.10 |

---

## 5. 依赖关系

```
FR-1 (工具栏) ─────────────────────┐
FR-2 (快捷键) ──→ use-note-editor ──┤
FR-3 (图片粘贴) ──→ use-note-editor ┤
                                     ├──→ write-note/page.tsx
FR-4 (斜杠命令) ──→ use-note-editor ┤    write-note/[slug]/page.tsx
FR-5 (模板) ────────────────────────┘

FR-6 (Alerts)  ──┐
FR-7 (高亮)    ──┤
FR-8 (脚注)    ──┼──→ markdown-renderer.ts → article.css
FR-9 (折叠)    ──┤
FR-10 (Mermaid) ─┘

FR-11 (AI 后端) ──→ ai-polish.ts (前端 API) ──→ FR-12 (AI 面板)
```

---

## 6. 实施阶段

| 阶段 | 范围 | 对应需求 |
|------|------|---------|
| **阶段 1** | 编辑器基础体验 | FR-1, FR-2, FR-3, FR-13 (CSS 部分) |
| **阶段 2** | 渲染器扩展 | FR-6, FR-7, FR-8, FR-9, FR-10, FR-13 |
| **阶段 3** | 斜杠命令 + 模板 | FR-4, FR-5 |
| **阶段 4** | AI 后端 + 前端集成 | FR-11, FR-12 |

阶段间有依赖关系: 阶段 3 依赖阶段 1（use-note-editor hook），阶段 4 的前端依赖阶段 1。

---

## 7. 验证方法

| 需求组 | 验证方式 |
|--------|---------|
| FR-1, FR-2, FR-3 | 手动测试: 在 create/edit 页面操作工具栏按钮、快捷键、粘贴图片 |
| FR-4 | 手动测试: 输入 `/`，搜索、导航、选择、关闭 |
| FR-5 | 手动测试: 选择模板，验证插入内容和日期自动填充 |
| FR-6~10 | 手动测试: 在预览中渲染包含新语法的 Markdown 内容 |
| FR-11 | API 测试: `curl -N -X POST /api/ai/polish -H "Authorization: Bearer ..." -d '{"text":"...", "action":"polish"}'` |
| FR-12 | 手动测试: 打开 AI 面板，执行操作，验证结果插入/替换/复制 |
| NFR-2 | 回归测试: 验证现有功能（数学公式、代码高亮、任务列表、图片灯箱、错题识别）不受影响 |

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| mermaid 包体积大（~2MB） | 首屏加载 | 懒加载，仅在遇到 mermaid 代码块时加载 |
| DeepSeek API 不稳定 | AI 功能不可用 | 超时 120s + 错误 toast 提示 + 可重试 |
| `execCommand` 被废弃 | 快捷键失效 | 回退方案: 直接修改 textarea value + `setSelectionRange` |
| 斜杠命令与已有 `/` 输入冲突 | 误触发 | 仅在行首或空格后检测 `/`，或提供设置开关 |
| Alerts blockquote 覆盖普通 blockquote | 引用样式异常 | 严格匹配 `[!TYPE]` 模式，非匹配走原逻辑 |
