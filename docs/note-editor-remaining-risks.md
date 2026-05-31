# 笔记编辑器修复后剩余风险设计文档

> 基于 Gemini 审查后的最小必要修复（2026-05-31），本文档记录 6 项仍未解决的剩余风险，包含根因分析、候选方案、推荐方案和实施建议。

---

## 风险 1：斜杠菜单软换行（Soft Wrap）定位偏差

### 根因

当前定位算法通过 `textBeforeCursor.split('\n').length` 计算"行号"，只统计硬换行符（`\n`），不感知 textarea 的 soft wrap（自动换行）。

当一行文本超过 textarea 宽度时，浏览器自动折行显示，但 JS 侧仍视为同一行。导致菜单位置向下偏移不足，可能覆盖在文本上方或悬空。

### 影响

- 长行输入 `/` 后，菜单出现在错误的 Y 坐标
- 不影响短行和硬换行场景

### 候选方案

#### 方案 A：Mirror Div 算法（推荐）

创建一个与 textarea 样式完全一致的隐藏 `<div>`，将光标前的文本复制进去，在末尾插入一个零宽 `<span>` 作为光标标记，读取该 span 的 `getBoundingClientRect()` 获取精确坐标。

```
<textarea> 样式同步 → hidden mirror div → 注入文本 + cursor span → 读取坐标
```

**优点**：精确，自动处理 soft wrap、字体、padding、scroll。
**缺点**：需要同步 textarea 的所有样式属性（font、padding、word-wrap、tab-size 等），实现稍复杂。

**局部化约束**：将 mirror 逻辑封装为独立函数 `getCaretCoordinates(textarea, offset)` 放入 `use-note-editor.ts` 或 `src/lib/caret-position.ts`，不改动现有 hook 接口。

```ts
// src/lib/caret-position.ts
export function getCaretCoordinates(
  textarea: HTMLTextAreaElement,
  offset: number
): { top: number; left: number } {
  const mirror = document.createElement('div')
  const style = getComputedStyle(textarea)
  // 同步关键样式
  const properties = [
    'fontFamily', 'fontSize', 'fontWeight', 'fontStyle',
    'letterSpacing', 'lineHeight', 'textTransform',
    'wordSpacing', 'wordWrap', 'whiteSpace',
    'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
    'borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth',
    'boxSizing', 'tabSize',
  ]
  for (const prop of properties) {
    ;(mirror.style as any)[prop] = (style as any)[prop]
  }
  mirror.style.position = 'absolute'
  mirror.style.visibility = 'hidden'
  mirror.style.whiteSpace = 'pre-wrap'
  mirror.style.wordWrap = 'break-word'
  mirror.style.overflow = 'hidden'
  mirror.style.width = `${textarea.clientWidth}px`

  const text = textarea.value.substring(0, offset)
  mirror.textContent = text

  const span = document.createElement('span')
  span.textContent = '\u200b' // zero-width space
  mirror.appendChild(span)

  document.body.appendChild(mirror)
  const spanRect = span.getBoundingClientRect()
  const textareaRect = textarea.getBoundingClientRect()
  const top = spanRect.top - textareaRect.top - textarea.scrollTop
  const left = spanRect.left - textareaRect.left
  document.body.removeChild(mirror)

  return { top, left }
}
```

#### 方案 B：Canvas measureText 逐字符估算

用 `canvas.measureText()` 逐行累加宽度，遇到超出 textarea 宽度时折行。自行计算 soft wrap 行数。

**优点**：不需要 DOM 操作。
**缺点**：需要自行处理 word-break 规则、tab、emoji 宽度等，精度不如 mirror div。

#### 方案 C：退化方案 — 固定显示在 textarea 可见区域顶部

直接将菜单定位在 `rect.top + 4`（textarea 可视区域顶部），放弃精确光标跟随。

**优点**：最简单，永远不会跑出 textarea 可视区。
**缺点**：用户体验差，菜单不跟随光标。

### 推荐

**方案 A**。封装为 `getCaretCoordinates()` 工具函数，`use-note-editor.ts` 中调用后叠加 viewport clamp。实现局部化，不影响 hook 签名。

### 实施建议

1. 新增 `src/lib/caret-position.ts`，导出 `getCaretCoordinates`
2. `use-note-editor.ts` 的两处定位代码替换为调用该函数
3. 保留 viewport clamp（`Math.min/Math.max`）
4. 删除 `charWidth = 8` 硬编码估算

---

## 风险 2：Mermaid SVG dangerouslySetInnerHTML 安全依赖

### 根因

`mermaid-block.tsx` 通过 `dangerouslySetInnerHTML={{ __html: svg }}` 注入 mermaid 渲染结果。安全性完全依赖 `mermaid.initialize({ securityLevel: 'strict' })`。

如果 mermaid 库本身存在 SVG 注入漏洞（如通过恶意图表代码注入 `<script>` 或 `onload` 事件），此处在 Next.js 层面无法拦截。

### 影响

- 用户输入的 mermaid 代码如果包含 XSS payload，可能在预览时执行
- 当前系统是个人笔记系统，攻击面较小，但如果未来开放分享功能则风险升高

### 候选方案

#### 方案 A：DOMPurify 后处理 SVG（推荐）

在 `setSvg(rendered)` 前用 DOMPurify 清洗 SVG。

```ts
import DOMPurify from 'dompurify'

const clean = DOMPurify.sanitize(rendered, {
  USE_PROFILES: { svg: true },
  ADD_TAGS: ['style'],
  ADD_ATTR: ['transform', 'viewBox', 'fill', 'stroke'],
})
setSvg(clean)
```

**优点**：业界标准 SVG 清洗方案，白名单机制。
**缺点**：新增依赖（~10KB gzip），mermaid 内部样式可能被误杀。

#### 方案 B：iframe sandbox 隔离

将 mermaid SVG 渲染到 `<iframe sandbox="allow-same-origin">` 中，禁止脚本执行。

**优点**：零依赖，完全隔离。
**缺点**：样式隔离导致与主站主题不一致，交互受限。

#### 方案 C：维持现状 + 依赖 mermaid strict 模式

当前 `securityLevel: 'strict'` 已阻止 `<script>` 和事件属性。

**优点**：零改动。
**缺点**：安全责任完全转嫁给 mermaid 上游。

### 推荐

当前个人笔记场景下 **方案 C 可接受**。若未来开放分享功能，切换到 **方案 A**。

### 实施建议

1. 在 `NOTEBOOK_SYSTEM_FULL_CHAIN_USABILITY_AUDIT.md` 或 AGENTS.md 中记录：当分享功能上线时必须引入 DOMPurify
2. 如需立即实施方案 A：`pnpm add dompurify @types/dompurify`，修改 `mermaid-block.tsx` 约 5 行

---

## 风险 3：AI 面板 Abort 后 loading 状态间隙

### 根因

当用户快速点击不同 AI 操作时，执行顺序：

1. `runAction('polish')` → 创建 controller-1，设置 `loading=true`
2. `runAction('summarize')` → `abortRef.current?.abort()` 中断 controller-1，创建 controller-2，设置 `loading=true`

controller-1 的 `streamPolish` 捕获 AbortError 后静默 return，不调用 `onDone`/`onError`。此时 `runAction('polish')` 的 async 函数自然结束，但不会修改 `loading`。

如果 controller-2 的 `streamPolish` fetch 尚未返回第一个 chunk，`loading` 保持 `true`——这是正确行为。

**真正的间隙场景**：如果 `abort()` 发生在 `streamPolish` 内部 `reader.read()` 之间，存在极短的时间窗口（~1 tick）内旧回调可能已经执行了 `setResult` 但 `requestId` 检查阻止了它。这不是 bug，但值得确认。

### 影响

- 实际影响极低，requestId 机制已阻止脏数据
- 最坏情况：abort 后旧的 `setResult` 调用被 requestId 拦截，无副作用

### 验证方式

在浏览器 DevTools 中：
1. 打开 AI 面板
2. 快速连续点击"润色"→"总结"→"扩写"
3. 确认只有最后一次请求的 chunk 写入 result 区
4. 确认无 React `Can't perform a React state update on an unmounted component` warning

### 推荐

**当前实现已足够**。requestId 机制是正确的防护。无需额外修改。

---

## 风险 4：GitHub Alert 正则对未来 marked 版本的脆弱性

### 根因

当前 Alert 检测依赖对 marked 输出 HTML 的正则匹配：

```ts
body.match(/^<p[^>]*>\[!([A-Z]+)\]/)
```

这假设：
- Alert 类型标记在第一个 `<p>` 标签内
- `[!TYPE]` 是该 `<p>` 的起始内容
- marked 使用 `<p>` 标签包裹 blockquote 内容

如果 marked 未来版本改变 HTML 输出结构（如使用 `<div>` 替代 `<p>`、改变属性顺序、增加 `data-*` 属性），正则可能失效。

### 影响

- Alert 功能静默降级为普通 blockquote
- 不会导致崩溃或安全问题

### 候选方案

#### 方案 A：在 token 层面检测 Alert（推荐）

不依赖 HTML 正则，而是在 `blockquote` renderer 接收到的 `token.tokens` 中检查第一个子 token 是否匹配 `[!TYPE]` 模式。

```ts
renderer.blockquote = (token: Tokens.Blockquote) => {
  const firstToken = token.tokens?.[0]
  if (firstToken?.type === 'paragraph') {
    const firstText = firstToken.tokens?.[0]?.text || firstToken.text || ''
    const alertMatch = firstText.match(/^\[!([A-Z]+)\]/)
    if (alertMatch) {
      const type = alertMatch[1]
      const title = ALERT_TYPES[type]
      if (title) {
        // 从第一个 paragraph token 中移除 [!TYPE] 标记
        const remainingTokens = stripAlertTag(token.tokens, type)
        const body = marked.parser(remainingTokens)
        return `<div class="markdown-alert ...">...</div>`
      }
    }
  }
  return `<blockquote>${marked.parser(token.tokens)}</blockquote>`
}
```

**优点**：不依赖 HTML 输出格式，与 marked 内部结构解耦。
**缺点**：需要理解 marked token 树结构，处理 `firstToken.tokens` 的嵌套。

#### 方案 B：使用 marked 扩展机制

注册一个 `marked.use({ extensions: [...] })` 的 block 级扩展，在 lexer 阶段将 Alert blockquote 转换为自定义 token 类型。

**优点**：最干净的集成方式。
**缺点**：与现有 math/highlight 扩展可能冲突，调试复杂。

#### 方案 C：维持 HTML 正则 + 添加回归测试

保持当前正则，但添加 markdown→HTML 的快照测试，确保 marked 升级时能及时发现破坏性变更。

**优点**：低改动成本。
**缺点**：被动防御。

### 推荐

**方案 A**。token 层面检测比 HTML 正则更稳定，且改动范围仅限 `renderer.blockquote` 函数。

### 实施建议

1. 在 `renderer.blockquote` 中优先检查 `token.tokens[0]` 的文本内容
2. 保留当前 HTML 正则作为 fallback（双重检测）
3. 为 Alert 添加 3-5 个 markdown→HTML 快照测试用例

---

## 风险 5：模板插入空行保护的边界情况

### 根因

当前实现检查光标前一个字符 `value[selectionStart - 1]` 和后一个字符 `value[selectionEnd]`，非空白时添加 `\n\n`。

边界情况：

1. **光标在文档开头**（`selectionStart === 0`）：`charBefore` 为空字符串，`if (charBefore && ...)` 为 false，不添加前导空行。正确。
2. **光标在文档末尾**（`selectionEnd === value.length`）：`charAfter` 为空字符串，不添加尾部空行。正确。
3. **模板内容本身以 `\n` 开头/结尾**：大多数模板以 `# 标题` 开头（无前导换行），以 `\n` 结尾。插入后效果合理。
4. **连续插入模板**：第一次插入后光标在模板末尾（`\n` 后），第二次插入时 `charBefore` 为 `\n`，不添加额外空行。但如果用户将光标移到模板内容中间（非空白处）再插入，会添加空行。符合预期。

### 影响

- 极端边界情况下可能多出 2 个空行，用户可手动删除
- 不会导致数据丢失或崩溃

### 推荐

**当前实现已足够**。无需修改。

---

## 风险 6：pre-existing TypeScript `never[]` 推断问题

### 根因

AGENTS.md 记录："TypeScript checking currently fails because JSON empty arrays infer as `never[]`"。这是 `siteContent.artImages`、`siteContent.socialButtons` 等从 JSON 文件读取的空数组在 TypeScript 严格模式下被推断为 `never[]`，导致后续赋值类型不兼容。

此问题在本次修复范围外，且 `next.config.ts` 的 `ignoreBuildErrors: true` 掩盖了它。

### 影响

- `npx tsc --noEmit` 可能对某些文件报错（本次未触发因为修改的文件不涉及这些类型）
- 不影响运行时，但阻碍未来移除 `ignoreBuildErrors`

### 推荐

单独提 issue 跟踪。修复方式为在 `src/config/` 或 `src/lib/` 中为 JSON 配置定义显式 TypeScript 类型，而非依赖推断。

---

## 优先级排序

| 编号 | 风险 | 严重度 | 修复紧迫度 | 推荐方案 |
|---|---|---|---|---|
| 1 | 斜杠菜单 soft wrap 定位 | 中 | 中 | Mirror Div |
| 2 | Mermaid SVG XSS | 低 | 低（分享功能上线时修复） | DOMPurify |
| 3 | AI 面板 abort 状态间隙 | 极低 | 无需修复 | 已由 requestId 覆盖 |
| 4 | Alert 正则脆弱性 | 中 | 中 | Token 层面检测 |
| 5 | 模板空行边界 | 极低 | 无需修复 | 当前实现足够 |
| 6 | TypeScript never[] | 低 | 低 | 显式类型定义 |
