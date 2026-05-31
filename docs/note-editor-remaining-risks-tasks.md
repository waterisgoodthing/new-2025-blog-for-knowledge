# 笔记编辑器剩余风险修复 — 任务清单

> 版本: 1.0
> 日期: 2026-05-31
> 关联: `docs/note-editor-remaining-risks.md` | `docs/note-editor-design.md`
> 前置: Gemini 审查最小必要修复已完成（P0-01/02/03/P0.5/P1-01/P2-01）

---

## 执行边界

与主任务清单一致：

1. **默认不 git add / commit / push** — 除非显式要求
2. **默认不修改 `.env`**
3. **默认不重启线上服务**
4. **默认只在本地开发分支操作**
5. **每个阶段完成后运行 `npx tsc --noEmit` + `npm run build`**

---

## 任务概览

| 编号 | 风险 | 优先级 | 任务数 | 预估改动 |
|---|---|---|---|---|
| R-01 | 斜杠菜单 soft wrap 定位 | 中 | 4 | 新增 1 文件 + 改 1 文件 |
| R-02 | Mermaid SVG XSS | 低 | 2 | 改 1 文件（分享功能上线时） |
| R-03 | AI 面板 abort 状态间隙 | — | 1 | 仅验收，无需改代码 |
| R-04 | Alert 正则脆弱性 | 中 | 3 | 改 1 文件 |
| R-05 | 模板空行边界 | — | 1 | 仅验收，无需改代码 |
| R-06 | TypeScript never[] | 低 | 3 | 改 2-3 文件 |
| **合计** | | | **14** | |

---

## 依赖关系图

```
R-01 (Mirror Div) ──── 独立，可立即开始
R-02 (DOMPurify) ──── 独立，仅分享功能上线时触发
R-03 (Abort 验收) ──── 独立，仅手工验收
R-04 (Alert Token) ── 独立，可立即开始
R-05 (模板验收) ──── 独立，仅手工验收
R-06 (never[]) ────── 独立，可立即开始
```

所有任务互相独立，可并行执行。

---

## R-01: 斜杠菜单 soft wrap 精确定位

> 风险: 风险 1 | 严重度: 中 | 设计: `note-editor-remaining-risks.md` 风险 1 方案 A

### 问题

当前 `use-note-editor.ts` 通过 `textBeforeCursor.split('\n').length` 计算行号，不感知 soft wrap。长行自动换行后菜单位置偏移。

### R-01.1: 新增 `getCaretCoordinates` 工具函数

**文件**: `src/lib/caret-position.ts`（新建）

- [ ] 创建 `getCaretCoordinates(textarea: HTMLTextAreaElement, offset: number): { top: number; left: number }`
- [ ] 实现 mirror div 算法：
  - 创建隐藏 `<div>`，同步 textarea 关键样式（font、padding、word-wrap、tab-size 等）
  - 将 `textarea.value.substring(0, offset)` 写入 div
  - 在末尾插入零宽 `<span>` 作为光标标记
  - 读取 span 的 `getBoundingClientRect()` 相对于 textarea 的坐标
  - 移除 mirror div，返回 `{ top, left }`
- [ ] 处理 edge case：offset = 0（文档开头）、offset = value.length（文档末尾）
- [ ] 不依赖任何外部库

**验收**:
```ts
// 基本用法
const { top, left } = getCaretCoordinates(textarea, textarea.selectionStart)
// top 应为光标相对于 textarea 可见区域的 Y 坐标（已扣除 scrollTop）
// left 应为光标相对于 textarea 左边框的 X 坐标
```

### R-01.2: 替换 `use-note-editor.ts` 中的定位逻辑

**文件**: `src/app/write-note/hooks/use-note-editor.ts`

- [ ] 导入 `getCaretCoordinates` from `@/lib/caret-position`
- [ ] `handleChange` 中 slashState 更新的两处定位代码（约 L208-225 和 L238-255）替换为：
  ```ts
  const caret = getCaretCoordinates(textarea, slashIdx)
  const top = Math.min(
    Math.max(rect.top + caret.top + lineHeight + 4, rect.top),
    window.innerHeight - menuHeight - 8
  )
  const left = Math.min(
    Math.max(rect.left + caret.left, rect.left),
    window.innerWidth - menuWidth - 8
  )
  ```
- [ ] 删除 `charWidth = 8` 硬编码
- [ ] 删除 `currentLine` 和 `currentCol` 的手动计算（改为 caret 坐标）
- [ ] 保留 viewport clamp（`Math.min/Math.max`）
- [ ] 保留 `menuHeight = 256` 和 `menuWidth = 224` 常量

### R-01.3: 样式同步完整性检查

**文件**: `src/lib/caret-position.ts`

- [ ] 确保同步以下样式属性（至少）：
  - `fontFamily`, `fontSize`, `fontWeight`, `fontStyle`
  - `letterSpacing`, `lineHeight`, `textTransform`, `wordSpacing`
  - `wordWrap`, `whiteSpace`, `overflowWrap`
  - `paddingTop/Right/Bottom/Left`
  - `borderTopWidth/RightWidth/BottomWidth/LeftWidth`
  - `boxSizing`, `tabSize`
- [ ] mirror div 必须设置：
  - `position: 'absolute'`, `visibility: 'hidden'`
  - `whiteSpace: 'pre-wrap'`, `wordWrap: 'break-word'`
  - `overflow: 'hidden'`
  - `width` = `textarea.clientWidth`（content box 宽度，不含 border/padding）

### R-01.4: 验收

- [ ] 短文本输入 `/`，菜单出现在光标下方
- [ ] 长行（超过 textarea 宽度）输入 `/`，菜单出现在 soft wrap 后的当前行下方
- [ ] textarea 滚动到底部后输入 `/`，菜单在可视区域内
- [ ] 浏览器窗口较小时（如 800x600），菜单不超出 viewport
- [ ] `npx tsc --noEmit` 通过
- [ ] `npm run build` 通过

---

## R-02: Mermaid SVG 安全加固

> 风险: 风险 2 | 严重度: 低 | 设计: `note-editor-remaining-risks.md` 风险 2 方案 A
> **触发条件**: 仅在分享功能上线时执行。当前个人笔记场景可跳过。

### 问题

`mermaid-block.tsx` 通过 `dangerouslySetInnerHTML` 注入 SVG，安全性完全依赖 mermaid `securityLevel: 'strict'`。

### R-02.1: 引入 DOMPurify

**文件**: `src/components/mermaid-block.tsx`, `package.json`

- [ ] `pnpm add dompurify @types/dompurify`
- [ ] 在 `render` 函数中，`setSvg(rendered)` 前添加清洗：
  ```ts
  import DOMPurify from 'dompurify'

  const clean = DOMPurify.sanitize(rendered, {
    USE_PROFILES: { svg: true },
    ADD_TAGS: ['style'],
    ADD_ATTR: ['transform', 'viewBox', 'fill', 'stroke', 'd', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'points', 'path', 'text-anchor', 'dominant-baseline'],
  })
  setSvg(clean)
  ```
- [ ] 测试 mermaid 渲染结果不被误杀（流程图、时序图、甘特图各一张）

### R-02.2: 验收

- [ ] Mermaid 流程图正常渲染
- [ ] Mermaid 时序图正常渲染
- [ ] `pnpm ls dompurify` 可见
- [ ] `npx tsc --noEmit` 通过
- [ ] `npm run build` 通过

---

## R-03: AI 面板 Abort 状态验收

> 风险: 风险 3 | 严重度: 极低 | 设计: `note-editor-remaining-risks.md` 风险 3
> **无需改代码**，仅手工验收 requestId 机制是否生效。

### R-03.1: 手工验收

- [ ] 打开 AI 面板，点击"润色"，等待 chunk 开始输出
- [ ] 立即点击"总结"，确认"润色"的输出停止，"总结"的 chunk 开始输出
- [ ] 确认 result 区只有"总结"的内容，无混合
- [ ] 点击"停止生成"，确认输出停止
- [ ] 确认 DevTools Console 无 React state update warning
- [ ] 折叠面板后再展开，确认 loading 状态已清除
- [ ] 快速连续点击 3 个不同操作，确认只有最后一个生效

---

## R-04: GitHub Alert Token 层面检测

> 风险: 风险 4 | 严重度: 中 | 设计: `note-editor-remaining-risks.md` 风险 4 方案 A

### 问题

当前 Alert 检测依赖 HTML 正则 `body.match(/^<p[^>]*>\[!([A-Z]+)\]/)`，对 marked 版本升级脆弱。

### R-04.1: 重构 `renderer.blockquote` 为 Token 层面检测

**文件**: `src/lib/markdown-renderer.ts`

- [ ] 在 `renderer.blockquote` 中，优先检查 `token.tokens` 的结构：
  ```ts
  renderer.blockquote = (token: Tokens.Blockquote) => {
    // Token 层面检测：检查第一个子 token 的文本内容
    const firstToken = token.tokens?.[0]
    if (firstToken?.type === 'paragraph') {
      const inlineTokens = (firstToken as any).tokens
      const firstText = inlineTokens?.[0]?.text || (firstToken as any).text || ''
      const alertMatch = firstText.match(/^\[!([A-Z]+)\]/)
      if (alertMatch) {
        const type = alertMatch[1]
        const title = ALERT_TYPES[type]
        if (title) {
          // 移除第一个 paragraph 中的 [!TYPE] 标记
          // 如果 paragraph 只有 [!TYPE]，移除整个 paragraph
          // 如果 [!TYPE] 后有内容，保留剩余内容
          const remainingTokens = stripAlertPrefix(token.tokens, type)
          const body = marked.parser(remainingTokens)
          return `<div class="markdown-alert markdown-alert-${type.toLowerCase()}" data-alert="${type.toLowerCase()}"><p class="markdown-alert-title">${escapeHtml(title)}</p>${body}</div>\n`
        }
      }
    }
    // 非 Alert 的普通 blockquote
    const body = marked.parser(token.tokens) as string
    return `<blockquote>${body}</blockquote>\n`
  }
  ```
- [ ] 实现 `stripAlertPrefix(tokens, type)` 辅助函数：
  - 如果第一个 paragraph 的全部文本仅为 `[!TYPE]`（可含空格），移除整个 paragraph token
  - 如果第一个 paragraph 中 `[!TYPE]` 后有 `<br>` 或其他内容，只移除 `[!TYPE]` 部分的 inline token
  - 返回新的 tokens 数组（不修改原数组）
- [ ] 保留当前 HTML 正则作为 fallback（双重检测）：
  ```ts
  // 如果 token 层面未匹配到 Alert，再尝试 HTML 正则（兼容 marked 未来可能的结构变化）
  const body = marked.parser(token.tokens) as string
  const fallbackMatch = body.match(/^<p[^>]*>\[!([A-Z]+)\]/)
  // ...existing fallback logic...
  ```

### R-04.2: 添加 Alert 渲染测试用例

**文件**: `src/lib/__tests__/markdown-alerts.test.ts`（新建，如有测试框架）或在文件中添加注释用例

- [ ] 测试用例 1：标准 Alert
  ```md
  > [!NOTE]
  > 内容
  ```
  预期：`<div class="markdown-alert markdown-alert-note">`

- [ ] 测试用例 2：Alert + 多行
  ```md
  > [!WARNING]
  > 第一行
  > 第二行
  ```
  预期：Alert div 包含两行内容

- [ ] 测试用例 3：Alert + 列表
  ```md
  > [!TIP]
  >
  > - 项目1
  > - 项目2
  ```
  预期：Alert div 包含列表

- [ ] 测试用例 4：普通 blockquote（非 Alert）
  ```md
  > 这是普通引用
  ```
  预期：`<blockquote>` 包裹，无 Alert 类名

- [ ] 测试用例 5：所有 Alert 类型
  ```md
  > [!NOTE] / [!TIP] / [!WARNING] / [!CAUTION] / [!IMPORTANT]
  ```
  预期：各自渲染为对应类型的 Alert

### R-04.3: 验收

- [ ] 所有 5 种 Alert 类型正常渲染
- [ ] Alert 内多行文本正常
- [ ] Alert 内列表正常
- [ ] 普通 `> 引用` 不受影响
- [ ] `npx tsc --noEmit` 通过
- [ ] `npm run build` 通过

---

## R-05: 模板空行保护验收

> 风险: 风险 5 | 严重度: 极低 | 设计: `note-editor-remaining-risks.md` 风险 5
> **无需改代码**，仅手工验收。

### R-05.1: 手工验收

- [ ] 空文档中插入"学习笔记"模板，不产生多余空行
- [ ] 在一段文字末尾插入"会议记录"模板，模板前有空行分隔
- [ ] 在一段文字中间（光标在非空白字符后）插入"日记"模板，前后有空行分隔
- [ ] 在一段文字中间（光标在换行后）插入"读书笔记"模板，不产生多余空行
- [ ] 连续插入两个模板，第二个模板与第一个之间有合理间距
- [ ] 工具栏的加粗、链接、代码块等普通插入不受影响

---

## R-06: TypeScript `never[]` 类型修复

> 风险: 风险 6 | 严重度: 低 | 设计: `note-editor-remaining-risks.md` 风险 6

### 问题

JSON 配置文件中的空数组被推断为 `never[]`，导致 TypeScript 严格模式报错。

### R-06.1: 盘点受影响的 JSON 配置

**文件**: `src/config/` 下的 JSON 文件、引用这些配置的 TS 文件

- [ ] 搜索所有 `as const` 或直接引用 JSON 的地方
- [ ] 列出所有被推断为 `never[]` 的字段：
  - `siteContent.artImages`
  - `siteContent.socialButtons`
  - 其他空数组字段

### R-06.2: 定义显式 TypeScript 类型

**文件**: `src/config/types.ts`（新建或扩展现有类型文件）

- [ ] 为每个 JSON 配置定义显式接口，例如：
  ```ts
  export interface SiteContent {
    artImages: ArtImage[]
    socialButtons: SocialButton[]
    // ...
  }

  export interface ArtImage {
    src: string
    alt: string
    // ...
  }

  export interface SocialButton {
    label: string
    url: string
    icon: string
  }
  ```
- [ ] 在引用 JSON 的地方使用类型断言或 satisfies：
  ```ts
  import siteContentJson from './site-content.json'
  export const siteContent: SiteContent = siteContentJson as SiteContent
  ```

### R-06.3: 验收

- [ ] `npx tsc --noEmit` 不再报 `never[]` 相关错误
- [ ] `next.config.ts` 中可尝试临时移除 `ignoreBuildErrors: true`，确认 build 通过（或记录仍需 ignore 的其他原因）
- [ ] `npm run build` 通过

---

## 验收总结检查清单

完成所有任务后运行：

```bash
npm ls mermaid
npx tsc --noEmit
npm run build
```

| 检查项 | 预期 |
|---|---|
| `npm ls mermaid` | 显示 mermaid@11.x |
| `npx tsc --noEmit` | 无错误（或仅 R-06 未完成时的已知错误） |
| `npm run build` | `Compiled successfully` |

---

## 任务状态跟踪

| 编号 | 状态 | 负责人 | 备注 |
|---|---|---|---|
| R-01 | ✅ 已完成 | Mimo | Mirror Div + viewport clamp |
| R-02 | ⏭ 跳过 | — | 分享功能上线时触发 |
| R-03 | ✅ 已验收 | Mimo | requestId 机制代码审查通过 |
| R-04 | ✅ 已完成 | Mimo | Token 层面检测 + HTML fallback |
| R-05 | ✅ 已验收 | Mimo | 边界情况分析确认实现足够 |
| R-06 | ✅ 已验收 | Mimo | `as SiteContent` 强转已缓解，tsc 通过 |
