# 笔记编辑器多维度扩展 — 设计文档

> 遵循现有 UI 设计风格：毛玻璃卡片（`bg-white/60 backdrop-blur-sm border-white/40`）、`rounded-xl` 圆角、`motion/react` 动画、`lucide-react` 图标、`var(--color-brand)` 主题色。

---

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    write-note/page.tsx                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  NoteToolbar  ← 格式按钮 + AI 下拉 + 模板下拉        │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  SlashCommandMenu  ← 斜杠命令浮层（portal）           │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────┬────────────────────────┐  │
│  │  <textarea> 编辑区           │  AI 副面板（可折叠）   │  │
│  │  use-note-editor hook        │  - 润色/总结/扩写      │  │
│  │  - 快捷键                    │  - 翻译/提取标签       │  │
│  │  - 图片粘贴                  │  - 生成问题            │  │
│  │  - 斜杠命令触发              │  - 对话式交互          │  │
│  └──────────────────────────────┴────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  NotePreviewContent  ← 渲染预览（支持新语法）         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、组件设计

### 2.1 NoteToolbar — 格式工具栏

**文件**: `src/app/write-note/components/note-toolbar.tsx`

**UI 规格**:
- 容器: `rounded-lg bg-white/40 p-1.5`（与现有编辑/预览 Tab 栏风格一致）
- 按钮: `h-7 w-7 rounded-md text-gray-600 hover:bg-white/80 hover:text-gray-900`
- 分隔线: `mx-1 h-5 w-px bg-gray-300/50`
- 下拉菜单: 复用 `<Select>` 组件的 portal + `AnimatePresence` 模式，`bg-card/95 backdrop-blur-xl rounded-xl border`
- 活跃态: `bg-brand/10 text-brand`

**分组布局**（单行，溢出时换行）:

```
[ B ] [ I ] [ S ] [ == ] [ ` ] | [ H1 ] [ H2 ] [ H3 ] | [ 🔗 ] [ 🖼 ] [ 📊 ] [ — ]
[ • ] [ 1. ] [ ☐ ] [ > ] | [ ``` ] [ Σ ] [ ^1 ] | [ 💡 ] [ ⚡ ] | [ AI ▾ ] [ 📝 ▾ ]
```

**AI 下拉菜单**:
```
┌─────────────────────┐
│ ✨ 润色              │
│ 📝 总结              │
│ 📖 扩写              │
│ ✍️  续写              │
│ 🌐 翻译 (中→英)      │
│ 🌐 翻译 (英→中)      │
│ 🏷️  提取标签          │
│ ❓ 生成复习问题       │
└─────────────────────┘
```

**模板下拉菜单**:
```
┌─────────────────────┐
│ 📚 学习笔记          │
│ 📋 会议记录          │
│ 📅 日记/日志         │
│ 📖 读书笔记          │
│ 🗂️  项目笔记          │
└─────────────────────┘
```

**交互逻辑**:
- 点击格式按钮 → 调用 `onInsert(text)` 插入/包裹文本
- 选中文字 + 点击加粗 → 智能包裹 `**...**`
- 已包裹的文字 + 再次点击 → 去除包裹
- AI 菜单项 → 调用 AI API，结果插入/替换编辑器内容
- 模板项 → 插入预设模板文本到编辑器

---

### 2.2 SlashCommandMenu — 斜杠命令面板

**文件**: `src/app/write-note/components/slash-command-menu.tsx`

**UI 规格**:
- 浮层定位: `createPortal` 到 `document.body`，跟随光标位置
- 容器: `bg-card/95 backdrop-blur-xl rounded-xl border shadow-lg`
- 最大高度: `max-h-64 overflow-y-auto`
- 搜索输入: 顶部 `input`，`placeholder="搜索命令..."`
- 命令项: `rounded-lg px-3 py-2 text-sm hover:bg-gray-100/50 active:scale-[0.98]`
- 选中态: `bg-brand/10 text-brand font-medium`
- 图标 + 标签 + 简短描述（灰色小字）

**触发逻辑**:
1. 用户在 textarea 输入 `/`
2. 检测到 `/` 后，记录光标位置，弹出菜单
3. 继续输入字符作为搜索过滤（如 `/表` 过滤出"表格"）
4. `↑↓` 键导航，`Enter` 选择，`Escape` 关闭
5. 选择后删除 `/` 及搜索文本，插入对应内容
6. 输入空格或光标离开时自动关闭

**命令列表**（支持中文+拼音搜索）:

| 关键词 | 拼音别名 | 插入内容 | 图标 |
|--------|---------|---------|------|
| 标题1 | bt1, heading1 | `# ` | H1 |
| 标题2 | bt2, heading2 | `## ` | H2 |
| 标题3 | bt3, heading3 | `### ` | H3 |
| 加粗 | jb, bold | 包裹 `**...**` | B |
| 斜体 | xt, italic | 包裹 `*...*` | I |
| 代码块 | dmk, code | ` ```js\n\n``` ` | `{}` |
| 公式 | gs, math | `$$\n\n$$` | Σ |
| 行内公式 | hngs, inline-math | 包裹 `$...$` | $ |
| 表格 | bg, table | 表格模板 | ⊞ |
| 任务 | rw, task | `- [ ] ` | ☐ |
| 引用 | yy, quote | `> ` | " |
| 提示 | ts, note | `> [!NOTE]\n> ` | ℹ |
| 技巧 | jq, tip | `> [!TIP]\n> ` | 💡 |
| 警告 | jg, warning | `> [!WARNING]\n> ` | ⚠ |
| 危险 | wx, caution | `> [!CAUTION]\n> ` | 🔥 |
| 重要 | zy, important | `> [!IMPORTANT]\n> ` | ⭐ |
| 分割线 | fgx, hr | `\n---\n` | — |
| 时间戳 | sjb, timestamp | `2026-05-30 22:11` | 🕐 |
| 折叠 | zd, details | `<details><summary>` 模板 | ▶ |
| 图表 | tb, mermaid | ` ```mermaid\ngraph TD\n` | 📊 |
| 思维导图 | swdt, mindmap | ` ```mermaid\nmindmap\n` | 🧠 |
| 脚注 | jz, footnote | `[^1]` + 定义 | ^1 |

---

### 2.3 NoteTemplates — 模板选择器

**文件**: `src/app/write-note/components/note-templates.tsx`

作为工具栏的下拉菜单实现，不单独占位。点击后将模板文本插入编辑器光标位置。

**模板内容**:

```markdown
<!-- 学习笔记 -->
# [科目/主题]

## 核心概念

- 概念1:
- 概念2:

## 要点整理

1. 
2. 
3. 

## 例题/案例

> [!TIP]
> 

## 总结


```

```markdown
<!-- 会议记录 -->
# 会议: [主题]

- **时间**: 2026-05-30
- **参会人**: 

## 议题

### 1. 

## 结论

- 

## 待办

- [ ] 
- [ ] 

```

```markdown
<!-- 日记/日志 -->
# 2026-05-30 日志

## 今日完成

- 

## 明日计划

- [ ] 

## 备注


```

```markdown
<!-- 读书笔记 -->
# 《书名》

- **作者**: 
- **阅读日期**: 2026-05-30

## 核心观点

1. 

## 精彩摘录

> 

## 个人感想


```

```markdown
<!-- 项目笔记 -->
# 项目: [名称]

## 背景


## 方案

### 方案A

### 方案B

## 当前进度

- [ ] 

## 风险与问题

> [!WARNING]
> 

```

---

### 2.4 use-note-editor — 编辑器 Hook

**文件**: `src/app/write-note/hooks/use-note-editor.ts`

**职责**:
1. 键盘快捷键处理
2. 剪贴板图片粘贴
3. 斜杠命令触发
4. `insertAtCursor` 封装（使用 `execCommand` 保持 undo 栈）

**接口**:
```typescript
function useNoteEditor(options: {
  textareaRef: RefObject<HTMLTextAreaElement | null>
  content: string
  onContentChange: (content: string) => void
  onImageUpload?: (file: File) => Promise<string>
}): {
  handleKeyDown: (e: KeyboardEvent<HTMLTextAreaElement>) => void
  handlePaste: (e: ClipboardEvent<HTMLTextAreaElement>) => void
  insertText: (text: string) => void
  slashState: { open: boolean; position: { top: number; left: number }; query: string }
  closeSlash: () => void
}
```

**快捷键映射**:
- `Ctrl/Cmd + B` → 切换 `**粗体**`
- `Ctrl/Cmd + I` → 切换 `*斜体*`
- `Ctrl/Cmd + K` → 插入 `[文本](url)`
- `Tab` → 插入 `\t`
- `Shift + Tab` → 移除行首缩进
- `Ctrl/Cmd + Shift + T` → 插入时间戳

**图片粘贴流程**:
1. `paste` 事件中检测 `clipboardData.items` 含 `image/*`
2. `preventDefault()` 阻止默认粘贴
3. 调用 `onImageUpload(file)` 上传
4. 成功后 `insertText(`![](${url})`)`

**斜杠命令触发**:
1. `input` 事件中检测最近输入的 `/`
2. 计算光标屏幕坐标（`textarea.getBoundingClientRect()` + 行高估算）
3. 设置 `slashState.open = true`
4. 后续输入累积到 `slashState.query`
5. 非 `/` 开头或空格/Escape 时关闭

---

### 2.5 AIAssistantPanel — AI 副面板

**文件**: `src/app/write-note/components/ai-assistant-panel.tsx`

**UI 规格**:
- 位置: 编辑器右侧，可折叠
- 展开宽度: `w-80`
- 容器: `rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm`
- 折叠态: 仅显示一个展开按钮（`◀` 图标）
- 展开态: 标题栏 + 操作按钮组 + 结果区

**布局**:
```
┌──────────────────────────┐
│  AI 助手           [ ▶ ] │
├──────────────────────────┤
│  [润色] [总结] [扩写]    │
│  [续写] [翻译] [标签]    │
│  [问题]                  │
├──────────────────────────┤
│  结果预览区              │
│  ┌────────────────────┐  │
│  │ AI 返回的内容...    │  │
│  │                    │  │
│  └────────────────────┘  │
│  [插入] [替换] [复制]    │
└──────────────────────────┘
```

**交互流程**:
1. 用户选中编辑器文字（或不选中操作全文）
2. 点击 AI 操作按钮（如"润色"）
3. 面板显示 loading 状态（`animate-pulse` 骨架屏）
4. SSE 流式返回结果，逐字显示
5. 完成后可选: "插入"（追加到光标）、"替换"（替换选中文字）、"复制"

---

## 三、渲染器扩展

### 3.1 GitHub Alerts

**文件**: `src/lib/markdown-renderer.ts`

**实现**: 拦截 `renderer.blockquote`，检测 token 内容是否以 `[!TYPE]` 开头。

**HTML 输出**:
```html
<div class="markdown-alert markdown-alert-note" data-alert="note">
  <p class="markdown-alert-title">
    <svg>...</svg> 注意
  </p>
  <p>提示内容</p>
</div>
```

**类型映射**:
| TYPE | 中文标题 | 图标 (lucide) | 颜色 |
|------|---------|--------------|------|
| NOTE | 注意 | `info` | blue |
| TIP | 技巧 | `lightbulb` | green |
| WARNING | 警告 | `alert-triangle` | amber |
| CAUTION | 危险 | `flame` | red |
| IMPORTANT | 重要 | `star` | purple |

### 3.2 高亮标记

**实现**: `marked.use()` 添加 inline 扩展，匹配 `==[^=]+==`。

**HTML 输出**: `<mark>文本</mark>`

### 3.3 脚注

**实现**: 两阶段处理：
1. inline 扩展匹配 `[^id]`，生成 `<sup><a href="#fn-id">N</a></sup>`
2. block 扩展匹配 `[^id]: 定义文本`，收集到脚注列表
3. 在文档末尾生成 `<section class="footnotes"><ol>...</ol></section>`

### 3.4 Mermaid 图表

**实现**: 
- 代码块预处理阶段，检测 `lang === 'mermaid'`
- 不走 Shiki 高亮，改为生成 `<div class="mermaid">graph TD...</div>`
- 前端 `use-markdown-render.tsx` 中，post-process 阶段检测 `.mermaid` 元素
- 动态 `import('mermaid')` 初始化后调用 `mermaid.run()` 渲染

**懒加载策略**:
```typescript
let mermaidLoaded = false
async function loadMermaid() {
  if (mermaidLoaded) return
  const mermaid = await import('mermaid')
  mermaid.default.initialize({ startOnLoad: false, theme: 'default' })
  mermaidLoaded = true
}
```

---

## 四、CSS 样式

**文件**: `src/styles/article.css`（追加）

### 4.1 Alerts

```css
.prose .markdown-alert {
  border-left: 3px solid;
  border-radius: 8px;
  padding: 0.75em 1em;
  margin: 1em 0;
  font-size: 0.95em;
}
.prose .markdown-alert-title {
  display: flex;
  align-items: center;
  gap: 0.5em;
  font-weight: 600;
  margin-bottom: 0.5em;
  font-size: 0.9em;
}
.prose .markdown-alert p { margin: 0.5em 0; }

.prose .markdown-alert-note    { border-color: #3b82f6; background: #eff6ff; }
.prose .markdown-alert-tip     { border-color: #10b981; background: #ecfdf5; }
.prose .markdown-alert-warning { border-color: #f59e0b; background: #fffbeb; }
.prose .markdown-alert-caution { border-color: #ef4444; background: #fef2f2; }
.prose .markdown-alert-important { border-color: #8b5cf6; background: #f5f3ff; }

.prose .markdown-alert-note .markdown-alert-title    { color: #2563eb; }
.prose .markdown-alert-tip .markdown-alert-title     { color: #059669; }
.prose .markdown-alert-warning .markdown-alert-title { color: #d97706; }
.prose .markdown-alert-caution .markdown-alert-title { color: #dc2626; }
.prose .markdown-alert-important .markdown-alert-title { color: #7c3aed; }
```

### 4.2 高亮

```css
.prose mark {
  background: #fef08a;
  padding: 0.1em 0.3em;
  border-radius: 3px;
}
```

### 4.3 脚注

```css
.prose .footnotes {
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  margin-top: 2em;
  padding-top: 1em;
  font-size: 0.9em;
  color: #666;
}
.prose .footnotes ol { margin-left: 1.5em; }
.prose .footnotes li { margin: 0.3em 0; }
.prose sup a {
  color: var(--color-brand);
  text-decoration: none;
  font-weight: 600;
}
.prose sup a:hover { text-decoration: underline; }
```

### 4.4 可折叠区域

```css
.prose details {
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 0.75em 1em;
  margin: 1em 0;
}
.prose details summary {
  cursor: pointer;
  font-weight: 600;
  color: var(--color-brand);
}
.prose details[open] summary { margin-bottom: 0.75em; }
```

### 4.5 Mermaid 容器

```css
.prose .mermaid {
  margin: 1em 0;
  text-align: center;
}
.prose .mermaid svg { max-width: 100%; }
```

---

## 五、后端 API

### 5.1 POST /api/ai/polish

**文件**: `backend/app/routers/ai_polish.py` + `backend/app/services/ai_polish_service.py` + `backend/app/schemas/ai_polish.py`

**请求**:
```json
{
  "text": "要处理的文本",
  "action": "polish | summarize | expand | continue | translate_en | translate_zh | extract_tags | generate_questions",
  "context": "可选，编辑器全文上下文"
}
```

**响应**（SSE 流式）:
```
data: {"chunk": "处理"}
data: {"chunk": "后的"}
data: {"chunk": "文本"}
data: [DONE]
```

**实现**:
- 复用 `ai_service._call_openai_compatible()`
- 使用 DeepSeek API（已配置 key）
- 每个 action 有对应的 system prompt
- SSE 流式返回，前端逐字显示

**System Prompt 示例**:
```
polish: "你是一个文本润色助手。请优化以下文本的表达，修正语法错误，提升可读性，保持原意不变。直接返回润色后的文本，不要解释。"
summarize: "请对以下内容提取核心要点，生成简洁的摘要。用要点列表形式输出。"
expand: "请对以下简短内容进行扩写，补充细节、论据和例子，使内容更充实。保持原文风格。"
continue: "请根据以下上下文继续写作，保持风格和主题一致。直接续写，不要重复已有内容。"
```

---

## 六、依赖变更

| 包 | 版本 | 用途 |
|----|------|------|
| `mermaid` | `^11` | 图表/思维导图渲染 |

后端无新增依赖。

---

## 七、文件清单

| 操作 | 文件路径 | 说明 |
|------|---------|------|
| 新建 | `src/app/write-note/components/note-toolbar.tsx` | 格式工具栏 |
| 新建 | `src/app/write-note/components/slash-command-menu.tsx` | 斜杠命令面板 |
| 新建 | `src/app/write-note/components/ai-assistant-panel.tsx` | AI 副面板 |
| 新建 | `src/app/write-note/hooks/use-note-editor.ts` | 编辑器 hook |
| 新建 | `src/lib/api/ai-polish.ts` | AI 润色前端 API |
| 新建 | `backend/app/routers/ai_polish.py` | AI 润色路由 |
| 新建 | `backend/app/services/ai_polish_service.py` | AI 润色服务 |
| 新建 | `backend/app/schemas/ai_polish.py` | AI 润色 schema |
| 修改 | `src/lib/markdown-renderer.ts` | Alerts / 高亮 / 脚注 / Mermaid |
| 修改 | `src/hooks/use-markdown-render.tsx` | Mermaid post-process |
| 修改 | `src/styles/article.css` | 新增样式 |
| 修改 | `src/app/write-note/page.tsx` | 集成全部新组件 |
| 修改 | `src/app/write-note/[slug]/page.tsx` | 同上 |

---

## 八、交互流程图

### 8.1 斜杠命令流程

```
用户输入 "/"
  ↓
检测到 "/" → 记录位置 → 打开菜单
  ↓
继续输入 → 过滤命令列表（中文/拼音匹配）
  ↓
↑↓ 键导航 / 鼠标悬停
  ↓
Enter / 点击 → 删除 "/query" → 插入选中命令内容
  ↓
Escape / 空格 / 点击外部 → 关闭菜单
```

### 8.2 AI 润色流程

```
用户选中文字（可选）
  ↓
点击 AI 操作按钮
  ↓
面板显示 loading 状态
  ↓
POST /api/ai/polish (SSE)
  ↓
流式接收 → 逐字显示在结果区
  ↓
完成 → 用户选择 [插入] / [替换] / [复制]
  ↓
[插入] → 追加到光标位置
[替换] → 替换编辑器选中文字
[复制] → 写入剪贴板
```

### 8.3 智能包裹流程

```
用户选中文字 "重要内容"
  ↓
点击加粗按钮 / Ctrl+B
  ↓
检查前后是否已有 "**" 包裹
  ├── 否 → 插入 "**重要内容**"
  └── 是 → 去除包裹，保留 "重要内容"
```
