# 笔记编辑器多维度扩展 — 任务清单

> 版本: 3.0
> 日期: 2026-05-30
> 关联: `docs/note-editor-design.md` | `docs/note-editor-requirements.md`

---

## 执行边界

所有开发工作遵守以下约束：

1. **默认不 git add / commit / push** — 除非显式要求
2. **默认不修改 `.env`** — 后端环境变量仅读取，不写入
3. **默认不重启线上服务** — 仅在本地开发分支操作
4. **默认只在本地开发分支操作** — 不触碰 main/master
5. **每个阶段完成后输出阶段报告** — 格式见各阶段验收任务

---

## 阶段回滚策略

| 阶段 | 回滚方式 |
|------|---------|
| P0 | 移除新组件文件(`note-toolbar.tsx` / `note-templates.tsx` / `use-note-editor.ts`)，恢复原 `write-note/page.tsx` 和 `write-note/[slug]/page.tsx` |
| P1 | 关闭 Markdown 扩展(在 `marked.use()` 中注释掉新 extensions)，保留原 renderer 逻辑；移除 `slash-command-menu.tsx` |
| P2 | 不注册 `ai_polish` router(从 `main.py` 移除 import)，不显示 AI 面板(从页面移除组件引入) |
| P3 | 移除 `mermaid` 依赖(`npm uninstall mermaid`)，移除 `use-markdown-render.tsx` 中的 post-process 逻辑 |

---

## 任务概览

| 阶段 | 任务范围 | 任务数 | 子任务数 |
|------|---------|--------|---------|
| P0 基础编辑体验 | Hook + 工具栏 + 模板 + 页面集成 + 验收 | 5 | 22 |
| P1 斜杠命令与基础渲染 | 安全加固 + Alerts + 高亮 + details + 斜杠 + 验收 | 6 | 27 |
| P2 AI 辅助编辑 | Schema + Service + Router + 前端 API + AI 面板 + 验收 | 6 | 31 |
| P3 高级能力 | 图片粘贴 + 脚注 + Mermaid + 斜杠增强 + 验收 | 5 | 22 |
| **合计** | | **22** | **102** |

---

## 依赖关系图

```
P0 ──────────────────────────────────────────────────────────────
  T-01 (use-note-editor 基础 Hook)
    ├── T-02 (NoteToolbar 基础组件)
    │     └── T-03 (NoteTemplates 模板系统)
    └── T-04 (create/edit 页面集成)
          └── T-05 (P0 验收)

P1 ──────────────────────────────────────────────────────────────
  T-06 (Markdown sanitizer 安全加固)
    ├── T-07 (GitHub Alerts 渲染)
    ├── T-08 (高亮标记渲染)
    └── T-09 (details 样式增强)
  T-10 (SlashCommandMenu 基础版) ── 依赖 T-01
    └── T-11 (P1 验收)

P2 ──────────────────────────────────────────────────────────────
  T-12 (AI 后端 Schema)
    └── T-13 (AI 后端 Service)
          └── T-14 (AI 后端 Router)
                └── T-15 (AI 前端 API 客户端)
                      └── T-16 (AI 副面板)
                            └── T-17 (P2 验收)

P3 ──────────────────────────────────────────────────────────────
  T-18 (剪贴板图片上传) ── 依赖 T-01
  T-19 (脚注系统) ── 依赖 T-06
  T-20 (Mermaid 懒加载渲染) ── 依赖 T-06
  T-21 (斜杠命令增强) ── 依赖 T-10
    └── T-22 (P3 验收)
```

---

## 阶段 P0: 基础编辑体验

> 目标: 用最小改动让笔记编辑器获得格式化工具栏、键盘快捷键和模板能力。
> 验收: 手动测试全部通过 + `npx tsc --noEmit` 通过 + `npm run build` 通过。
> 回滚: 移除新组件文件，恢复原 write-note 页面。

---

### T-01: use-note-editor 基础 Hook

**对应需求**: FR-2
**依赖**: 无
**文件**: `src/app/write-note/hooks/use-note-editor.ts` (新建)

**子任务**:

- [ ] T-01.1 定义 Hook 接口
  ```typescript
  function useNoteEditor(options: {
    textareaRef: RefObject<HTMLTextAreaElement | null>
    content: string
    onContentChange: (content: string) => void
  }): {
    handleKeyDown: (e: KeyboardEvent<HTMLTextAreaElement>) => void
    insertText: (text: string) => void
    wrapSelection: (before: string, after: string, fallback?: string) => void
  }
  ```

- [ ] T-01.2 实现 `insertText(text)`
  - **优先路径**: `document.execCommand('insertText', false, text)` — 保持 undo 栈
  - **必须实现 fallback**: 直接修改 `content` + `setSelectionRange`
  - 不能把 `execCommand` 作为唯一路径
  - fallback 路径至少保证: 内容正确更新、光标位置正确、选区不异常
  - **验收约束**: 如果 fallback 下浏览器原生 undo 栈无法完整保留，必须在阶段报告中说明哪些浏览器/场景受影响
  - 参考 `src/app/write/components/editor.tsx:12-31`

- [ ] T-01.3 实现 `wrapSelection(before, after, fallback?)`
  - 获取 `selectionStart` / `selectionEnd` / `selectedText`
  - 检测前后是否已有 `before`/`after` 包裹: 已包裹则去除，未包裹则包裹
  - 无选中文字时使用 `fallback`（默认 `'文本'`）
  - 包裹/去除后正确恢复光标位置

- [ ] T-01.4 实现 `handleKeyDown` 快捷键
  - `Ctrl/Cmd + B` → `wrapSelection('**', '**')` (FR-2.1)
  - `Ctrl/Cmd + I` → `wrapSelection('*', '*')` (FR-2.2)
  - `Ctrl/Cmd + K` → `insertText('[文本](url)')` 并选中 `url` (FR-2.3)
  - `Tab` → `insertText('\t')` (FR-2.4)
  - `Shift + Tab` → 移除行首一个 `\t` 或两个空格 (FR-2.5)
  - `Ctrl/Cmd + Shift + T` → `insertText(dayjs().format('YYYY-MM-DD HH:mm'))` (FR-2.6)

- [ ] T-01.5 使用 `dayjs` 格式化时间戳（项目已安装 `dayjs@^1.11.18`，无需新增依赖）

**不在 P0 实现**:
- ~~剪贴板图片上传~~ → T-18
- ~~slashState / 斜杠命令触发~~ → T-10

**验收标准**:
1. 各快捷键在 create/edit 页面 textarea 中正常触发
2. 选中文字 + Ctrl+B → 包裹为 `**选中文字**`
3. 已包裹文字 + Ctrl+B → 去除包裹
4. Ctrl+Z / Ctrl+Y 撤销/重做: `execCommand` 路径下不丢失操作；fallback 路径下内容和光标不异常（undo 栈限制需在报告中说明）
5. Tab 插入制表符，Shift+Tab 移除缩进
6. 光标位置在每次操作后正确恢复

---

### T-02: NoteToolbar 基础组件

**对应需求**: FR-1
**依赖**: T-01
**文件**: `src/app/write-note/components/note-toolbar.tsx` (新建)

**子任务**:

- [ ] T-02.1 定义按钮数据结构
  ```typescript
  type ToolbarAction = {
    icon: ReactNode
    label: string
    shortcut?: string
    insert: string | ((selected: string) => string)
    cursorOffset?: number
    wrap?: boolean
  }
  type ToolbarGroup = { label: string; actions: ToolbarAction[] }
  ```

- [ ] T-02.2 实现 5 组按钮 (FR-1.1 ~ FR-1.5)
  - 文本格式: 加粗、斜体、删除线、高亮、行内代码
  - 标题: H1、H2、H3
  - 插入: 链接、图片 URL、表格、分割线
  - 列表: 无序、有序、任务、引用
  - 高级: 代码块、公式块、行内公式

- [ ] T-02.3 实现智能包裹逻辑 (FR-1.7, FR-1.8)
  - `wrap: true` 的按钮调用 `wrapSelection(before, after)`
  - 非 wrap 按钮调用 `insertText(text)`

- [ ] T-02.4 实现 UI 渲染 (FR-1.9)
  - 容器: `rounded-lg bg-white/40 p-1.5 flex flex-wrap items-center gap-0.5`
  - 按钮: `h-7 w-7 rounded-md text-gray-600 hover:bg-white/80 hover:text-gray-900`
  - 分隔线: `mx-1 h-5 w-px bg-gray-300/50`
  - 使用 `lucide-react` 图标（项目已有依赖）
  - `title` 属性显示按钮名称和快捷键

- [ ] T-02.5 组件 Props 定义
  ```typescript
  type NoteToolbarProps = {
    textareaRef: RefObject<HTMLTextAreaElement | null>
    insertText: (text: string) => void
    wrapSelection: (before: string, after: string, fallback?: string) => void
  }
  ```

**验收标准**:
1. 工具栏渲染正确，所有按钮可见
2. 点击每个按钮在光标位置插入正确内容
3. 选中文字 + 点击加粗/斜体/删除线/高亮/行内代码 → 正确包裹
4. 已包裹文字再次点击 → 去除包裹
5. UI 与现有编辑/预览 Tab 栏风格一致

---

### T-03: NoteTemplates 模板系统

**对应需求**: FR-5
**依赖**: T-02
**文件**: `src/app/write-note/components/note-templates.tsx` (新建)

**子任务**:

- [ ] T-03.1 定义模板数据结构
  ```typescript
  type NoteTemplate = {
    id: string
    label: string
    icon: ReactNode
    getContent: () => string   // 动态生成，点击时调用
  }
  ```
  **不得使用 `content: string` 固定模板内容** — 日期必须在点击时动态生成。

- [ ] T-03.2 实现 5 套模板的 `getContent` 函数 (FR-5.1 ~ FR-5.5)
  - 学习笔记: 标题 → 核心概念 → 要点整理 → 例题/案例 → 总结
  - 会议记录: 标题 → 时间/参会人 → 议题 → 结论 → 待办清单
  - 日记/日志: 日期标题 → 今日完成 → 明日计划 → 备注
  - 读书笔记: 书名 → 作者/日期 → 核心观点 → 精彩摘录 → 个人感想
  - 项目笔记: 标题 → 背景 → 方案对比 → 当前进度 → 风险

- [ ] T-03.3 日期在 `getContent()` 内部使用 `dayjs().format('YYYY-MM-DD')` 动态生成 (FR-5.7)
  - 项目已安装 `dayjs@^1.11.18`
  - **验收约束**: 日期在点击时生成，不在模块加载时固定

- [ ] T-03.4 导出模板列表
  ```typescript
  export const noteTemplates: NoteTemplate[]
  ```

- [ ] T-03.5 在 NoteToolbar 中集成模板下拉菜单 (FR-5.6)
  - 使用 `createPortal` + `AnimatePresence` 模式（参考 `src/components/select.tsx`）
  - 按钮: 工具栏末尾的模板图标按钮
  - 下拉: `bg-card/95 backdrop-blur-xl rounded-xl border`
  - 点击模板项 → `onInsert(template.getContent())`

**验收标准**:
1. 工具栏末尾显示模板按钮，点击展开下拉
2. 5 个模板均可点击，插入完整 Markdown 内容
3. 日记/日志模板中的日期为**点击当天**（修改系统时间后重新点击可验证动态性）
4. 下拉菜单点击外部可关闭

---

### T-04: create/edit 页面集成

**对应需求**: FR-1.10
**依赖**: T-01, T-02, T-03
**文件**: `src/app/write-note/page.tsx` (修改), `src/app/write-note/[slug]/page.tsx` (修改)

**子任务**:

- [ ] T-04.1 在两个页面中引入 `useNoteEditor` Hook
  - 替换现有 `insertAtCursor` 函数
  - 绑定 `handleKeyDown` 到 textarea 的 `onKeyDown`

- [ ] T-04.2 引入 `NoteToolbar` 组件
  - 放在编辑/预览 Tab 栏下方、textarea 上方
  - 仅在 `tab === 'edit'` 且非 mistake 类型时显示
  - Props 传递: `textareaRef`、`insertText`、`wrapSelection` 均从 Hook 获取

- [ ] T-04.3 移除旧的单个"图片"按钮（功能已被工具栏中的图片按钮替代）

- [ ] T-04.4 保留现有编辑/预览 Tab 切换逻辑（`useNoteEditorTab` 不变）

- [ ] T-04.5 编辑页面额外处理
  - 确保 `content` 初始值从 note 数据正确加载
  - Hook 的 `content` 与 `form.content` 同步

**验收标准**:
1. 创建页面: 工具栏显示，快捷键可用，预览正确
2. 编辑页面: 工具栏显示，已有内容正确加载，编辑后保存正确
3. mistake 类型不显示工具栏（保持原有表单布局）
4. 编辑/预览 Tab 切换不受影响

---

### T-05: P0 验收

**依赖**: T-01 ~ T-04
**文件**: 无新增

**子任务**:

- [ ] T-05.1 运行 `npx tsc --noEmit`，确认无新增类型错误
- [ ] T-05.2 运行 `npm run build`，确认构建通过
- [ ] T-05.3 如存在历史遗留类型/构建错误，列出: 文件、错误编号、是否本次引入
- [ ] T-05.4 手动测试创建笔记流程
- [ ] T-05.5 手动测试编辑笔记流程
- [ ] T-05.6 验证现有功能未受影响: 编辑/预览 Tab、mistake 表单、图片拖拽上传
- [ ] T-05.7 输出阶段报告

**阶段报告格式**:
```
## P0 阶段报告

### 完成任务
- T-01: ✅ / ❌
- T-02: ✅ / ❌
- T-03: ✅ / ❌
- T-04: ✅ / ❌

### 修改文件列表
- 新建: src/app/write-note/hooks/use-note-editor.ts
- 新建: src/app/write-note/components/note-toolbar.tsx
- 新建: src/app/write-note/components/note-templates.tsx
- 修改: src/app/write-note/page.tsx
- 修改: src/app/write-note/[slug]/page.tsx

### 执行命令与结果
- npx tsc --noEmit: PASS / FAIL (附错误)
- npm run build: PASS / FAIL (附错误)

### 手工验收结果
- [ ] 工具栏按钮插入正确
- [ ] 快捷键 Ctrl+B/I/K 正确
- [ ] 模板日期动态生成
- [ ] 撤销/重做正常 (execCommand 路径)
- [ ] 撤销/重做 fallback 路径说明: ...

### 未完成项
- (列出)

### 风险与回滚建议
- (列出)
```

**验收标准**: `npx tsc --noEmit` 通过 + `npm run build` 通过 + 手动测试全部通过。

---

## 阶段 P1: 斜杠命令与基础渲染

> 目标: 增加斜杠命令快速输入和基础 Markdown 渲染扩展。
> 前提: P0 全部验收通过。
> 回滚: 关闭 Markdown 扩展，移除 slash-command-menu.tsx。

---

### T-06: Markdown sanitizer 安全加固

**对应需求**: NFR-4 (安全性)
**依赖**: 无
**文件**: `src/lib/markdown-renderer.ts` (修改)

**安全策略**: P1 默认**不透传用户原始 HTML**。不依赖正则剥离 `on*` 属性作为主要安全方案。

**子任务**:

- [ ] T-06.1 在 `marked.use()` 中覆盖 `renderer.html`
  - 默认行为: **丢弃所有用户原始 HTML**，返回空字符串
  - 这是最关键的安全屏障: 用户在 Markdown 中写 `<script>` / `<iframe>` / `<img onerror>` 等全部被丢弃
  - 不使用正则匹配/剥离 — 直接全部丢弃

- [ ] T-06.2 自定义 `renderer.link` — 链接协议白名单
  - 仅允许: `http://`、`https://`、`mailto:`、相对路径（以 `/` 或字母开头，不含 `:`）
  - 禁止: `javascript:`、`data:`、`vbscript:`
  - 不合规链接: href 置为空字符串，保留链接文本

- [ ] T-06.3 自定义 `renderer.image` — 图片 src 协议白名单
  - 仅允许: `http://`、`https://`、相对路径
  - 禁止: `javascript:`、`data:`（可选放开，需在报告中说明决策）
  - 不合规图片: 替换为占位文本 `[图片: 协议不安全]`

- [ ] T-06.4 renderer 自己生成的 HTML 使用固定模板
  - Alerts / 高亮 / 脚注 / 代码块等由 renderer 代码生成
  - 用户文本在拼接进模板前必须经过 HTML 实体转义
  - 转义函数: `&` → `&amp;`、`<` → `&lt;`、`>` → `&gt;`、`"` → `&quot;`、`'` → `&#39;`

- [ ] T-06.5 代码块中的内容不受 sanitizer 影响
  - `renderer.code` 输出的 `<pre><code>` 内容保持原样（已由 Shiki 处理或手动转义）
  - 代码块内不执行 HTML 过滤

- [ ] T-06.6 确认项目无现有 sanitizer 库
  - 已检查: 无 DOMPurify / sanitize-html / rehype-sanitize
  - 决策: 使用 renderer 层级丢弃策略，不引入新依赖

**验收标准**:
1. `<script>alert(1)</script>` → 不渲染为脚本（被丢弃）
2. `[click](javascript:alert(1))` → 链接 href 为空
3. `<img onerror="alert(1)" src="x">` → 被丢弃
4. `[link](https://example.com)` → 正常渲染
5. 现有数学公式、代码高亮、任务列表、图片灯箱正常工作
6. `<details>` / `<summary>` / `<mark>` / `<sup>` 等**由 renderer 自身生成的标签**不受影响

---

### T-07: GitHub Alerts 渲染

**对应需求**: FR-6
**依赖**: T-06
**文件**: `src/lib/markdown-renderer.ts` (修改), `src/styles/article.css` (修改)

**子任务**:

- [ ] T-07.1 自定义 `renderer.blockquote`
  - 检测 token 内容首行是否匹配 `[!TYPE]`（TYPE = NOTE / TIP / WARNING / CAUTION / IMPORTANT）
  - 匹配时: 使用**固定 HTML 模板**输出，用户文本部分做 HTML 实体转义
  - 非匹配: 走默认 blockquote 渲染 (FR-6.7)

- [ ] T-07.2 输出格式
  ```html
  <div class="markdown-alert markdown-alert-{type}" data-alert="{type}">
    <p class="markdown-alert-title">{中文标题}</p>
    {转义后的用户内容}
  </div>
  ```
  TYPE 中文标题: NOTE→注意 / TIP→技巧 / WARNING→警告 / CAUTION→危险 / IMPORTANT→重要

- [ ] T-07.3 Alerts CSS 样式 (FR-13.1, FR-13.2)
  - `.markdown-alert` 基础: `border-left: 3px solid; border-radius: 8px; padding: 0.75em 1em`
  - `.markdown-alert-title`: `display: flex; align-items: center; gap: 0.5em; font-weight: 600`
  - 5 种类型各自配色（见设计文档 §4.1）

- [ ] T-07.4 Alerts 内支持嵌套 Markdown (FR-6.6)
  - 子 token 由 `marked.parser()` 递归渲染，继承 sanitizer 策略

**验收标准**:
1. `> [!NOTE]\n> 内容` 渲染为蓝色提示框
2. `> [!TIP]` / `> [!WARNING]` / `> [!CAUTION]` / `> [!IMPORTANT]` 各自正确渲染
3. `> 普通引用` 保持原有左边框样式不变
4. Alert 内嵌套列表/代码正常
5. `> [!NOTE]\n> <script>alert(1)</script>` → script 被转义，不执行

---

### T-08: 高亮标记渲染

**对应需求**: FR-7
**依赖**: T-06
**文件**: `src/lib/markdown-renderer.ts` (修改), `src/styles/article.css` (修改)

**子任务**:

- [ ] T-08.1 `marked.use()` 添加 inline 扩展
  - name: `'highlight'`
  - level: `'inline'`
  - tokenizer 匹配 `==[^=]+==` (FR-7.3: 不匹配单个 `=`)
  - renderer 输出 `<mark>{text}</mark>` — text 由 marked 内部处理，无需额外转义

- [ ] T-08.2 高亮内支持嵌套行内 Markdown (FR-7.2)
  - tokenizer 中 `text` 需要被 marked 再次 lex/parse

- [ ] T-08.3 CSS 样式 (FR-13.3)
  - `.prose mark { background: #fef08a; padding: 0.1em 0.3em; border-radius: 3px }`

**验收标准**:
1. `==文本==` 渲染为黄色背景高亮
2. `==**粗体**文本==` 内部粗体正常渲染
3. `=text=` 不触发高亮

---

### T-09: details 样式增强

**对应需求**: FR-9
**依赖**: T-06
**文件**: `src/styles/article.css` (修改)

**安全说明**: 由于 T-06 默认丢弃用户原始 HTML，用户手写的 `<details>` 标签会被 sanitizer 丢弃。本任务**只添加 CSS 样式**，不强制放行用户手写 HTML。`<details>` 的实际使用方式有两种:
1. 斜杠命令 `/折叠` 通过 renderer 生成（T-10 范围）— 安全，受 sanitizer 保护
2. 未来如需放行用户手写 `<details>`，需单独评估并更新 T-06 白名单

**子任务**:

- [ ] T-09.1 CSS 样式 (FR-13.6)
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
  .prose details[open] summary {
    margin-bottom: 0.75em;
  }
  ```

**验收标准**:
1. CSS 样式已添加到 `article.css`
2. 若 renderer 生成的 `<details>` 标签可到达前端，则样式正确应用
3. 若 sanitizer 丢弃了用户手写的 `<details>`，不视为本任务失败

---

### T-10: SlashCommandMenu 基础版

**对应需求**: FR-4 (P1 子集)
**依赖**: T-01
**文件**: `src/app/write-note/components/slash-command-menu.tsx` (新建), `src/app/write-note/hooks/use-note-editor.ts` (修改)

**状态流约束**: slashState 的更新不得绕过 React 的 `content` / `onContentChange` 状态流。

**子任务**:

- [ ] T-10.1 在 `useNoteEditor` 中新增 `handleChange` 函数
  ```typescript
  // 新增返回值
  handleChange: (e: ChangeEvent<HTMLTextAreaElement>) => void
  ```
  - `handleChange` 内部流程:
    1. 调用 `onContentChange(e.target.value)` 更新 content 状态
    2. 检测斜杠命令: 获取光标前的文本，判断是否处于 `/query` 模式
    3. 更新 `slashState`

- [ ] T-10.2 定义 `slashState` 结构
  ```typescript
  slashState: {
    open: boolean
    position: { top: number; left: number }
    query: string
    commandStart: number  // `/` 在 textarea 中的位置，用于替换
  }
  closeSlash: () => void
  ```

- [ ] T-10.3 定义命令数据结构
  ```typescript
  type SlashCommand = {
    id: string
    label: string
    description: string
    icon: ReactNode
    insert: string | ((selected: string) => string)
    cursorOffset?: number
  }
  ```

- [ ] T-10.4 定义至少 12 个核心命令 (FR-4.9 P1 子集)
  | 命令 | 插入内容 |
  |------|---------|
  | 标题1 | `# ` |
  | 标题2 | `## ` |
  | 标题3 | `### ` |
  | 代码块 | ` ```js\n\n``` ` |
  | 公式 | `$$\n\n$$` |
  | 表格 | 表格模板 |
  | 任务 | `- [ ] ` |
  | 引用 | `> ` |
  | 提示 | `> [!NOTE]\n> ` |
  | 警告 | `> [!WARNING]\n> ` |
  | 分割线 | `\n---\n` |
  | 时间戳 | `YYYY-MM-DD HH:mm` |

- [ ] T-10.5 实现中文关键词搜索 (FR-4.3)
  - 输入 `/表` → 过滤出"表格"
  - 拼音搜索不在 P1 实现 → T-21

- [ ] T-10.6 实现浮层 UI (FR-4.1, FR-4.10)
  - `createPortal` 到 `document.body`
  - 容器: `bg-card/95 backdrop-blur-xl rounded-xl border shadow-lg`
  - 最大高度 `max-h-64 overflow-y-auto` (FR-4.11)
  - 命令项: `rounded-lg px-3 py-2 text-sm`
  - 选中态: `bg-brand/10 text-brand font-medium`

- [ ] T-10.7 实现键盘导航 (FR-4.5, FR-4.6, FR-4.7)
  - `↑` / `↓` 导航命令列表
  - `Enter` 确认选中: 删除 `/query`（使用 `commandStart` 定位），插入内容
  - `Escape` 关闭

- [ ] T-10.8 实现点击外部关闭 (FR-4.8)

- [ ] T-10.9 在 create/edit 页面中集成
  - textarea 的 `onChange` 绑定到 `handleChange`（替代原来的直接 `update('content', ...)`）
  - 渲染 `SlashCommandMenu` 组件，绑定 `slashState` 和 `closeSlash`

**验收标准**:
1. 输入 `/` 弹出菜单
2. 继续输入中文过滤命令列表
3. `↑`/`↓` 导航，`Enter` 选择，`Escape` 关闭
4. 点击外部关闭
5. 至少 12 个命令可用
6. 选择后 `/query` 被删除，命令内容正确插入
7. content 状态始终与 textarea 内容同步（不出现状态丢失）

---

### T-11: P1 验收

**依赖**: T-06 ~ T-10
**文件**: 无新增

**子任务**:

- [ ] T-11.1 运行 `npx tsc --noEmit`，确认无新增类型错误
- [ ] T-11.2 运行 `npm run build`，确认构建通过
- [ ] T-11.3 如存在历史遗留错误，列出: 文件、错误编号、是否本次引入
- [ ] T-11.4 安全测试
  - `<script>alert(1)</script>` 不执行
  - `[x](javascript:alert(1))` 链接被过滤
  - `<img onerror="alert(1)">` 被丢弃
- [ ] T-11.5 手动测试 Alerts 5 种类型渲染
- [ ] T-11.6 手动测试高亮 `==text==` 渲染
- [ ] T-11.7 手动测试斜杠命令完整流程
- [ ] T-11.8 回归验证 P0 功能: 工具栏、快捷键、模板
- [ ] T-11.9 输出阶段报告

**阶段报告格式**:
```
## P1 阶段报告

### 完成任务
- T-06: ✅ / ❌
- T-07: ✅ / ❌
- T-08: ✅ / ❌
- T-09: ✅ / ❌
- T-10: ✅ / ❌

### 修改文件列表
- 修改: src/lib/markdown-renderer.ts
- 修改: src/styles/article.css
- 新建: src/app/write-note/components/slash-command-menu.tsx
- 修改: src/app/write-note/hooks/use-note-editor.ts
- 修改: src/app/write-note/page.tsx
- 修改: src/app/write-note/[slug]/page.tsx

### 执行命令与结果
- npx tsc --noEmit: PASS / FAIL
- npm run build: PASS / FAIL

### 安全测试结果
- [ ] script 标签被丢弃
- [ ] javascript: 协议被过滤
- [ ] onerror 事件被丢弃

### 手工验收结果
- [ ] Alerts 5 种类型正确渲染
- [ ] 高亮 ==text== 正确渲染
- [ ] 斜杠命令 12 个可用
- [ ] 斜杠命令中文搜索可用

### details 样式说明
- 当前 sanitizer 策略: 用户手写 <details> 被丢弃
- renderer 生成的 <details> 是否可用: 是/否

### 未完成项
- (列出)

### 风险与回滚建议
- (列出)
```

**验收标准**: `npx tsc --noEmit` 通过 + `npm run build` 通过 + 安全测试通过 + 手动测试全部通过。

---

## 阶段 P2: AI 辅助编辑

> 目标: 为笔记编辑器增加 AI 润色/总结/扩写等能力。
> 前提: P1 全部验收通过。
> 回滚: 不注册 ai_polish router，不显示 AI 面板。

---

### T-12: AI 后端 Schema

**对应需求**: FR-11
**依赖**: 无
**文件**: `backend/app/schemas/ai_polish.py` (新建)

**子任务**:

- [ ] T-12.1 定义 `PolishAction` 枚举（白名单）
  ```python
  class PolishAction(str, Enum):
      polish = "polish"
      summarize = "summarize"
      expand = "expand"
      continue_ = "continue"
      translate_en = "translate_en"
      translate_zh = "translate_zh"
      extract_tags = "extract_tags"
      generate_questions = "generate_questions"
  ```

- [ ] T-12.2 定义 `PolishRequest`
  ```python
  class PolishRequest(BaseModel):
      text: str = Field(..., min_length=1, max_length=8000)
      action: PolishAction
      context: str | None = Field(None, max_length=12000)
  ```

- [ ] T-12.3 定义 `PolishChunkResponse`
  ```python
  class PolishChunkResponse(BaseModel):
      chunk: str
  ```

**验收标准**: Schema 可被 FastAPI 路由引用，`text` 超过 8000 字符时返回 422 验证错误。

---

### T-13: AI 后端 Service

**对应需求**: FR-11
**依赖**: T-12
**文件**: `backend/app/services/ai_polish_service.py` (新建)

**子任务**:

- [ ] T-13.1 定义 8 个 action 的 system prompt
  - `polish`: "你是一个文本润色助手。请优化以下文本的表达，修正语法错误，提升可读性，保持原意不变。直接返回润色后的文本，不要解释。"
  - `summarize`: "请对以下内容提取核心要点，生成简洁的摘要。用要点列表形式输出。"
  - `expand`: "请对以下简短内容进行扩写，补充细节、论据和例子，使内容更充实。保持原文风格。"
  - `continue`: "请根据以下上下文继续写作，保持风格和主题一致。直接续写，不要重复已有内容。"
  - `translate_en`: "请将以下中文翻译为英文，保持专业术语准确，语言自然流畅。只返回翻译结果。"
  - `translate_zh`: "请将以下英文翻译为中文，保持专业术语准确，语言自然流畅。只返回翻译结果。"
  - `extract_tags`: "请从以下内容中提取 3-8 个关键词标签，返回 JSON 数组格式。不要输出其他内容。"
  - `generate_questions`: "请根据以下笔记内容，生成 3-5 个复习问题。每个问题一行，以问号结尾。"

- [ ] T-13.2 实现 `async def polish_stream(text, action, context, request)` 异步生成器
  - 构建 messages: system prompt + optional context + user text
  - 复用 `ai_service._call_openai_compatible()` 并启用 `stream=True`
  - 使用 DeepSeek API（已配置 key）

- [ ] T-13.3 SSE 输出格式
  ```
  data: {"chunk": "处理后的文本片段"}

  data: [DONE]

  ```

- [ ] T-13.4 客户端断连检测
  - 接收 `request: Request` 参数
  - 生成循环中**周期性检查** `await request.is_disconnected()`（每生成 1-2 个 chunk 检查一次）
  - 同时捕获 `asyncio.CancelledError`
  - 断连后立即停止生成，break 退出循环

- [ ] T-13.5 SSE 超时 60 秒
  - 整个生成过程设置 60 秒超时
  - 超时后停止生成，发送 `data: {"error": "AI 服务超时，请重试"}\n\n` + `data: [DONE]\n\n`

- [ ] T-13.6 日志规范
  - **不记录**完整 `text` / `context` 内容
  - 只记录: `action`、`text_len`、`context_len`、`耗时(ms)`、`状态码`
  - 格式: `logger.info("ai_polish action=%s text_len=%d context_len=%d duration_ms=%d status=%s", ...)`

**验收标准**: `polish_stream()` 可被路由调用，返回正确 SSE 流，断连后停止生成，日志不含用户内容。

---

### T-14: AI 后端 Router

**对应需求**: FR-11
**依赖**: T-12, T-13
**文件**: `backend/app/routers/ai_polish.py` (新建), `backend/app/main.py` (修改)

**子任务**:

- [ ] T-14.1 创建路由 `APIRouter(prefix="/api/ai", tags=["ai"])`
- [ ] T-14.2 实现 `POST /api/ai/polish`
  - 请求体: `PolishRequest`
  - 认证: `Depends(get_current_user)` — 使用 `current_user` 而非 `current_admin`
  - 将 `request: Request` 传入 `polish_stream()` 用于断连检测
  - 响应: `StreamingResponse(polish_stream(...), media_type="text/event-stream")`

- [ ] T-14.3 速率限制
  - 10 次/分钟/用户
  - key 使用 `user.id`
  - **复用 `backend/app/routers/ai.py` 中的 `_rate_limit_store` / `_check_rate_limit` 模式**
  - 由于该模式是模块级私有函数，本任务将其提取为共享工具（放入 `backend/app/utils/rate_limit.py`），供 `ai.py` 和 `ai_polish.py` 共用
  - 超限返回 `HTTP 429`，body: `{"detail": "Rate limit exceeded. Max 10 requests per 60s."}`
  - **无 Redis**: 当前系统使用内存限流，进程重启后重置。这是现有策略，本任务沿用。

- [ ] T-14.5 错误处理
  - `text` 为空 / 超长 → 422（Pydantic 自动处理）
  - LLM API 超时 → SSE 中发送 `data: {"error": "..."}\n\n` + `data: [DONE]\n\n`
  - LLM API key 缺失 → 500

- [ ] T-14.6 注册路由到 `backend/app/main.py`

**验收标准**:
1. `curl -N -X POST /api/ai/polish -H "Authorization: Bearer ..." -d '{"text":"test", "action":"polish"}'` 返回 SSE 流
2. 无 token → 401
3. `text` 超过 8000 字符 → 422
4. 超过 10 次/分钟 → 429

---

### T-15: AI 前端 API 客户端

**对应需求**: FR-11
**依赖**: T-14
**文件**: `src/lib/api/ai-polish.ts` (新建)

**子任务**:

- [ ] T-15.1 定义类型
  ```typescript
  export type PolishAction = 'polish' | 'summarize' | 'expand' | 'continue' | 'translate_en' | 'translate_zh' | 'extract_tags' | 'generate_questions'

  export type PolishCallbacks = {
    onChunk: (chunk: string) => void
    onDone: () => void
    onError: (error: string) => void
  }
  ```

- [ ] T-15.2 实现 `streamPolish(text, action, callbacks, options?)`
  - 使用 `fetch()` 读取 SSE 流
  - **SSE 解析器必须维护 buffer**:
    1. `ReadableStream` 用 `TextDecoder` 解码
    2. 按双换行 `\n\n` 分割 SSE event
    3. 支持一个网络 chunk 中包含多个 event
    4. 支持一个 event 被拆到多个网络 chunk
    5. 忽略空行和非 `data:` 行
    6. JSON parse 失败不导致页面崩溃（catch 后 continue）
  - `data: {"chunk": "..."}` → `callbacks.onChunk(chunk)`
  - `data: {"error": "..."}` → `callbacks.onError(error)`
  - `data: [DONE]` → `callbacks.onDone()`

- [ ] T-15.3 实现 `AbortController` 取消支持
  - 接受可选 `signal: AbortSignal` 参数
  - 调用方传入 `AbortController.signal`，可随时 `controller.abort()` 中断请求
  - abort 时 SSE 流终止，不触发 `onError`

- [ ] T-15.4 获取 JWT token
  - 复用 `src/lib/api/notes.ts` 中的 token 获取逻辑

**验收标准**:
1. 前端可调用 `streamPolish()` 接收流式数据
2. 一个 chunk 包含多个 event 时正确解析
3. 一个 event 跨多个 chunk 时正确拼接
4. 调用 `abort()` 可中断请求
5. 网络错误触发 `onError`
6. JSON parse 失败不崩溃

---

### T-16: AI 副面板

**对应需求**: FR-12
**依赖**: T-15
**文件**: `src/app/write-note/components/ai-assistant-panel.tsx` (新建)

**子任务**:

- [ ] T-16.1 实现折叠/展开状态管理 (FR-12.1, FR-12.2)
  - 折叠态: 仅显示展开按钮 (`◀` 图标)
  - 展开态: `w-80`
  - 动画: `AnimatePresence` + `motion.div`

- [ ] T-16.2 实现操作按钮组 (FR-12.3)
  - 8 个按钮: 润色、总结、扩写、续写、翻译(中→英)、翻译(英→中)、提取标签、生成问题
  - 按钮样式: `rounded-lg bg-white/60 px-3 py-1.5 text-sm hover:bg-white/80`

- [ ] T-16.3 实现空文本拦截
  - 编辑器无选中文字且内容为空时 → `toast.warning('请先输入内容')`，不调用 API

- [ ] T-16.4 实现 loading 状态 (FR-12.4)
  - 骨架屏: `animate-pulse` + 灰色块
  - 操作按钮在 loading 时 `disabled`

- [ ] T-16.5 实现停止生成按钮
  - loading 时显示"停止生成"按钮
  - 点击 → 调用 `AbortController.abort()`
  - 中断后保留已接收的部分结果

- [ ] T-16.6 实现 SSE 流式结果显示 (FR-12.5)
  - 结果区: `min-h-[120px] rounded-lg border border-white/40 bg-white/40 p-3 text-sm`
  - 逐字追加显示

- [ ] T-16.7 实现错误态
  - API 返回错误时显示错误信息（红色文字）
  - 提供"重试"按钮

- [ ] T-16.8 实现结果操作按钮 (FR-12.6)
  - "插入" → 调用 `insertText(result)` 追加到光标
  - "替换" → 替换编辑器选中文字
  - "复制" → `navigator.clipboard.writeText(result)` + `toast.success('已复制')`

- [ ] T-16.9 选中/全文逻辑 (FR-12.7, FR-12.8)
  - 有选中文字: `text = selectedText`, `context = fullContent`
  - 无选中文字: `text = fullContent`, `context = undefined`

- [ ] T-16.10 UI 遵循现有设计风格 (FR-12.9)
  - 容器: `rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm`
  - 标题栏: `flex items-center justify-between p-3 border-b`

- [ ] T-16.11 在 create/edit 页面中集成 AI 面板
  - 放在编辑器右侧
  - 编辑器区域使用 `flex` 排列
  - mistake 类型不显示 AI 面板

**验收标准**:
1. 面板可折叠/展开
2. 点击操作按钮显示流式结果
3. "停止生成"可中断并保留部分结果
4. 空文本不调用 API
5. 错误态显示错误信息和重试按钮
6. 结果可插入/替换/复制

---

### T-17: P2 验收

**依赖**: T-12 ~ T-16
**文件**: 无新增

**子任务**:

- [ ] T-17.1 运行 `npx tsc --noEmit`，确认无新增类型错误
- [ ] T-17.2 运行 `npm run build`，确认构建通过
- [ ] T-17.3 如存在历史遗留错误，列出: 文件、错误编号、是否本次引入
- [ ] T-17.4 后端测试
  - `POST /api/ai/polish` 正常返回 SSE 流
  - 无 token → 401
  - text 超长 → 422
  - 速率限制 → 429
- [ ] T-17.5 前端测试
  - AI 面板: 润色/总结/扩写/续写/翻译 均可正常调用
  - 停止生成: 中断后保留部分结果
  - 空文本: 不调用 API，显示 toast
  - 错误态: 显示错误信息
- [ ] T-17.6 回归验证 P0 + P1 功能
- [ ] T-17.7 输出阶段报告

**阶段报告格式**:
```
## P2 阶段报告

### 完成任务
- T-12: ✅ / ❌
- T-13: ✅ / ❌
- T-14: ✅ / ❌
- T-15: ✅ / ❌
- T-16: ✅ / ❌

### 修改文件列表
- 新建: backend/app/schemas/ai_polish.py
- 新建: backend/app/services/ai_polish_service.py
- 新建: backend/app/routers/ai_polish.py
- 新建: backend/app/utils/rate_limit.py
- 修改: backend/app/main.py
- 新建: src/lib/api/ai-polish.ts
- 新建: src/app/write-note/components/ai-assistant-panel.tsx
- 修改: src/app/write-note/page.tsx
- 修改: src/app/write-note/[slug]/page.tsx

### 执行命令与结果
- npx tsc --noEmit: PASS / FAIL
- npm run build: PASS / FAIL
- 后端启动检查: PASS / FAIL

### 后端测试结果
- [ ] SSE 流正常返回
- [ ] 401/422/429 正确
- [ ] 断连后停止生成
- [ ] 日志不含用户内容

### 前端测试结果
- [ ] 8 种 AI 操作可用
- [ ] 停止生成可用
- [ ] 空文本拦截
- [ ] 错误态 + 重试

### 速率限制说明
- 实现方式: 内存限流（复用 ai.py 模式，提取为共享工具）
- Redis: 不可用，沿用现有策略
- 进程重启后限流状态重置: 是

### 未完成项
- (列出)

### 风险与回滚建议
- 回滚: 从 main.py 移除 ai_polish router import，前端移除 AI 面板组件
```

**验收标准**: `npx tsc --noEmit` 通过 + `npm run build` 通过 + 后端/前端测试通过。

---

## 阶段 P3: 高级能力

> 目标: 补充高级 Markdown 特性和编辑器增强。
> 前提: P2 全部验收通过。
> 回滚: 移除 mermaid 依赖与 post-process，移除斜杠拼音搜索。

---

### T-18: 剪贴板图片上传

**对应需求**: FR-3
**依赖**: T-01
**文件**: `src/app/write-note/hooks/use-note-editor.ts` (修改), `src/app/write-note/page.tsx` (修改), `src/app/write-note/[slug]/page.tsx` (修改)

**子任务**:

- [ ] T-18.1 在 `useNoteEditor` 中添加 `handlePaste`
  - 检测 `clipboardData.items` 中的 `image/*` (FR-3.1)
  - 调用 `onImageUpload(file)` (FR-3.2)
  - 成功后 `insertText(`![](${url})`)` (FR-3.3)

- [ ] T-18.2 更新 Hook 接口，添加 `onImageUpload` 可选参数和 `handlePaste` 返回值

- [ ] T-18.3 toast 提示 (FR-3.4, FR-3.5)
  - `toast.loading('上传中...')` → `toast.success('上传成功')` / `toast.error('上传失败')`

- [ ] T-18.4 在两个页面中绑定 `handlePaste` 到 textarea 的 `onPaste`

- [ ] T-18.5 保留现有拖拽上传功能，与粘贴功能共存

**验收标准**:
1. 在 textarea 中粘贴图片 → 自动上传 → 插入 `![](url)` → 预览可见
2. 拖拽上传不受影响
3. 上传失败显示错误 toast

---

### T-19: 脚注系统

**对应需求**: FR-8
**依赖**: T-06
**文件**: `src/lib/markdown-renderer.ts` (修改), `src/styles/article.css` (修改)

**子任务**:

- [ ] T-19.1 inline 扩展: 匹配 `[^id]`
  - 输出 `<sup><a href="#fn-{slugify(id)}">{N}</a></sup>`
  - `id` 必须 slug 化: 仅允许 `[a-z0-9-]`，其余字符丢弃

- [ ] T-19.2 block 扩展: 匹配 `[^id]: 定义文本`
  - 收集到 `footnotes: Map<string, { id: string; text: string; index: number }>`
  - 不在正文中渲染，从 token 流中移除

- [ ] T-19.3 在文档末尾生成脚注列表
  ```html
  <section class="footnotes">
    <ol>
      <li id="fn-{id}">{text} <a href="#fnref-{id}">↩</a></li>
    </ol>
  </section>
  ```

- [ ] T-19.4 编号按出现顺序自动递增 (FR-8.3)
- [ ] T-19.5 无定义的引用保持原样 (FR-8.6)
- [ ] T-19.6 CSS 样式 (FR-13.4, FR-13.5)
  - `.footnotes { border-top: 1px solid rgba(0,0,0,0.08); margin-top: 2em; font-size: 0.9em; color: #666 }`
  - `sup a { color: var(--color-brand); font-weight: 600 }`

**验收标准**:
1. 正文 `[^1]` 渲染为上标链接
2. 文末 `[^1]: 定义` 渲染为脚注列表
3. 点击上标跳转到脚注，点击 ↩ 跳回正文
4. `[^unknown]` 无定义时保持原样
5. 脚注 id 中的特殊字符被过滤

---

### T-20: Mermaid 懒加载渲染

**对应需求**: FR-10
**依赖**: T-06
**文件**: `src/lib/markdown-renderer.ts` (修改), `src/hooks/use-markdown-render.tsx` (修改), `src/styles/article.css` (修改), `package.json` (修改)

**安全约束**: Mermaid 渲染发生在 sanitized Markdown 容器内的 post-process 阶段。不得把用户原始 Mermaid 文本直接 innerHTML 到页面。Mermaid 代码内容进入 DOM 前必须 HTML 转义。

**子任务**:

- [ ] T-20.1 安装 mermaid 依赖
  ```bash
  npm install mermaid
  ```

- [ ] T-20.2 在 markdown-renderer 的代码块预处理中检测 `lang === 'mermaid'`
  - 不走 Shiki 高亮
  - 生成 `<div class="mermaid">{escaped_code}</div>`
  - **代码内容必须 HTML 转义**: `&` → `&amp;`、`<` → `&lt;`、`>` → `&gt;`、`"` → `&quot;`

- [ ] T-20.3 在 `use-markdown-render.tsx` 的 post-process 中检测 `.mermaid` 元素
  - 动态 `import('mermaid')`
  - 初始化配置:
    ```typescript
    mermaid.default.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'strict'
    })
    ```
  - `mermaid.default.run({ nodes: [element] })`

- [ ] T-20.4 懒加载策略
  - 首屏不加载 mermaid
  - 仅在遇到 `.mermaid` 元素时加载
  - 加载失败时降级为普通代码块 (FR-10.8)

- [ ] T-20.5 支持的图表类型 (FR-10.2 ~ FR-10.6)
  - `graph` 流程图
  - `sequenceDiagram` 时序图
  - `mindmap` 思维导图
  - `gantt` 甘特图
  - `pie` 饼图

- [ ] T-20.6 CSS 样式 (FR-13.7)
  - `.prose .mermaid { margin: 1em 0; text-align: center }`
  - `.prose .mermaid svg { max-width: 100% }`

**验收标准**:
1. ` ```mermaid\ngraph TD\nA-->B\n``` ` 渲染为 SVG 流程图
2. 语法错误时降级为普通代码块
3. 首屏 JS bundle 不包含 mermaid（检查 build 输出）
4. `securityLevel: 'strict'` 已设置
5. Mermaid 代码中的 `<` / `>` 被正确转义，不被浏览器解析为 HTML 标签

---

### T-21: 斜杠命令增强

**对应需求**: FR-4 (P3 补充)
**依赖**: T-10
**文件**: `src/app/write-note/components/slash-command-menu.tsx` (修改)

**子任务**:

- [ ] T-21.1 添加拼音首字母搜索 (FR-4.4)
  - 每个命令增加 `aliases: string[]` 字段
  - 搜索时同时匹配 `label` 和 `aliases`
  - 输入 `/dmk` → 匹配"代码块"

- [ ] T-21.2 扩展命令到 20+ 个
  - 新增: 加粗、斜体、行内公式、技巧(TIP)、危险(CAUTION)、重要(IMPORTANT)、折叠、图表、思维导图、脚注
  - 总计 ≥ 22 个

- [ ] T-21.3 搜索防抖 100ms (NFR-1.2)

**验收标准**:
1. 输入 `/dmk` 匹配"代码块"
2. 输入 `/swdt` 匹配"思维导图"
3. 命令总数 ≥ 22
4. 搜索无明显卡顿

---

### T-22: P3 验收

**依赖**: T-18 ~ T-21
**文件**: 无新增

**子任务**:

- [ ] T-22.1 运行 `npx tsc --noEmit`，确认无新增类型错误
- [ ] T-22.2 运行 `npm run build`，确认构建通过
- [ ] T-22.3 如存在历史遗留错误，列出: 文件、错误编号、是否本次引入
- [ ] T-22.4 手动测试图片粘贴上传
- [ ] T-22.5 手动测试脚注: 引用、定义、双向跳转、特殊字符过滤
- [ ] T-22.6 手动测试 Mermaid: 流程图、时序图、思维导图、语法错误降级
- [ ] T-22.7 手动测试斜杠命令增强: 拼音搜索、命令数量
- [ ] T-22.8 全量回归验证 P0 + P1 + P2 功能
- [ ] T-22.9 输出阶段报告

**阶段报告格式**:
```
## P3 阶段报告

### 完成任务
- T-18: ✅ / ❌
- T-19: ✅ / ❌
- T-20: ✅ / ❌
- T-21: ✅ / ❌

### 修改文件列表
- 修改: src/app/write-note/hooks/use-note-editor.ts
- 修改: src/app/write-note/page.tsx
- 修改: src/app/write-note/[slug]/page.tsx
- 修改: src/lib/markdown-renderer.ts
- 修改: src/hooks/use-markdown-render.tsx
- 修改: src/styles/article.css
- 修改: src/app/write-note/components/slash-command-menu.tsx
- 修改: package.json

### 执行命令与结果
- npx tsc --noEmit: PASS / FAIL
- npm run build: PASS / FAIL
- mermaid bundle 检查: 首屏不包含 / 包含

### 手工验收结果
- [ ] 图片粘贴上传正常
- [ ] 脚注双向跳转正常
- [ ] Mermaid 5 种图表可渲染
- [ ] Mermaid securityLevel: strict
- [ ] 拼音搜索可用
- [ ] 命令总数 ≥ 22

### 未完成项
- (列出)

### 风险与回滚建议
- 回滚: npm uninstall mermaid, 移除 use-markdown-render.tsx 中的 mermaid post-process
```

**验收标准**: `npx tsc --noEmit` 通过 + `npm run build` 通过 + 全量手动测试通过。

---

## 完整任务总览表

| ID | 任务 | 阶段 | 对应需求 | 依赖 | 文件 |
|----|------|------|---------|------|------|
| T-01 | use-note-editor 基础 Hook | P0 | FR-2 | — | `write-note/hooks/use-note-editor.ts` (新) |
| T-02 | NoteToolbar 基础组件 | P0 | FR-1 | T-01 | `write-note/components/note-toolbar.tsx` (新) |
| T-03 | NoteTemplates 模板系统 | P0 | FR-5 | T-02 | `write-note/components/note-templates.tsx` (新) |
| T-04 | create/edit 页面集成 | P0 | FR-1.10 | T-01~03 | `write-note/page.tsx` (改), `write-note/[slug]/page.tsx` (改) |
| T-05 | P0 验收 | P0 | NFR-2 | T-01~04 | — |
| T-06 | Markdown sanitizer 安全加固 | P1 | NFR-4 | — | `lib/markdown-renderer.ts` (改) |
| T-07 | GitHub Alerts 渲染 | P1 | FR-6, FR-13.1~2 | T-06 | `lib/markdown-renderer.ts` (改), `styles/article.css` (改) |
| T-08 | 高亮标记渲染 | P1 | FR-7, FR-13.3 | T-06 | `lib/markdown-renderer.ts` (改), `styles/article.css` (改) |
| T-09 | details 样式增强 | P1 | FR-9, FR-13.6 | T-06 | `styles/article.css` (改) |
| T-10 | SlashCommandMenu 基础版 | P1 | FR-4 (P1子集) | T-01 | `write-note/components/slash-command-menu.tsx` (新), `use-note-editor.ts` (改) |
| T-11 | P1 验收 | P1 | NFR-2 | T-06~10 | — |
| T-12 | AI 后端 Schema | P2 | FR-11 | — | `backend/schemas/ai_polish.py` (新) |
| T-13 | AI 后端 Service | P2 | FR-11 | T-12 | `backend/services/ai_polish_service.py` (新) |
| T-14 | AI 后端 Router | P2 | FR-11 | T-12, T-13 | `backend/routers/ai_polish.py` (新), `utils/rate_limit.py` (新), `main.py` (改) |
| T-15 | AI 前端 API 客户端 | P2 | FR-11 | T-14 | `lib/api/ai-polish.ts` (新) |
| T-16 | AI 副面板 | P2 | FR-12 | T-15 | `write-note/components/ai-assistant-panel.tsx` (新) |
| T-17 | P2 验收 | P2 | NFR-2 | T-12~16 | — |
| T-18 | 剪贴板图片上传 | P3 | FR-3 | T-01 | `use-note-editor.ts` (改), 两个 page (改) |
| T-19 | 脚注系统 | P3 | FR-8, FR-13.4~5 | T-06 | `lib/markdown-renderer.ts` (改), `styles/article.css` (改) |
| T-20 | Mermaid 懒加载渲染 | P3 | FR-10, FR-13.7 | T-06 | `lib/markdown-renderer.ts` (改), `use-markdown-render.tsx` (改), `styles/article.css` (改), `package.json` (改) |
| T-21 | 斜杠命令增强 | P3 | FR-4 (P3补充) | T-10 | `slash-command-menu.tsx` (改) |
| T-22 | P3 验收 | P3 | NFR-2 | T-18~21 | — |
