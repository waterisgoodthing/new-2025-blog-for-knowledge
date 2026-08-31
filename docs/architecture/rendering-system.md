# 渲染系统规范

相关文档：[技术栈](./tech-stack.md)、[前端结构](./frontend-structure.md)、[权限](./permissions.md)、[图标系统](./icon-system.md)、[思维导图](./mindmap-system.md)。

## 1. 渲染系统目标

Post、Note、Mistake 的富文本统一进入同一安全、可扩展、可降级的渲染入口，消除页面各自解析 Markdown、代码、图表和图片的分叉实现。

## 2. 目标技术栈

- Markdown：`unified + remark + rehype`
- GFM：`remark-gfm`
- 数学语法：`remark-math`
- 数学渲染：`rehype-katex`
- 代码高亮：Shiki
- 流程图：`MermaidBlock`
- 思维导图：`MindMapBlock + Markmap`
- 安全：`rehype-sanitize + DOMPurify`
- React 统一入口：`RichText`

## 3. RichText 统一入口

目标调用：

```tsx
<RichText content={content} mode="public" />
<RichText content={content} mode="admin-preview" />
```

`RichText` 负责选择管线、识别特殊 fenced block、统一错误边界和组件映射。业务页面只传内容与显式 mode，不自行安装插件或解析 HTML。

目标结构：

```text
src/components/rich-text/
├── RichText.tsx
├── CodeBlock.tsx
├── MermaidBlock.tsx
├── MindMapBlock.tsx
├── MarkdownImage.tsx
├── RenderErrorBlock.tsx
└── types.ts
src/lib/rendering/
├── markdown-pipeline.ts
├── sanitize-schema.ts
├── code-highlight.ts
├── block-detect.ts
└── types.ts
```

## 4. Markdown 管线

推荐顺序为 parse Markdown、应用 GFM 与 math、识别 `mermaid`/`markmap` fenced block、转换为 HAST、受控插件处理、sanitize，再映射到 React 组件。插件顺序和允许属性必须集中配置，避免页面级差异。

普通 Markdown 失败时显示局部 `RenderErrorBlock` 或安全纯文本，不让单个内容块拖垮整页。

## 5. CodeBlock 与 Shiki

除 `mermaid`、`markmap` 外的 fenced code 由 `CodeBlock` 处理。Shiki 负责服务端或构建期可控高亮；未知语言回退为纯文本代码块。必须转义源码、限制超长内容、支持横向滚动和复制的可访问名称，不把高亮 HTML 免检放行。

## 6. KaTeX 数学公式

`remark-math + rehype-katex` 处理行内与块级公式。公式错误应局部降级为原始公式文本，不暴露内部堆栈；KaTeX 输出所需 class/属性应以最小白名单加入 sanitize schema。

## 7. MermaidBlock 流程图

Mermaid 由 ` ```mermaid ` 代码块触发，必须在 `MermaidBlock` 中隔离渲染。错误时：

- 不显示 `Syntax error in text`。
- 不显示 mermaid version。
- 不显示 parser 原文或 `error.message`。
- 显示简洁降级 UI，并允许用户折叠查看原始 Mermaid 代码。

渲染产物仍需净化，组件应使用稳定唯一 ID，避免多个图表冲突。

## 8. MindMapBlock 思维导图

` ```markmap ` 代码块交给 `MindMapBlock + Markmap`，仅在客户端渲染。组件负责容器高度、缩放、滚动、清理和错误降级，不处理 Mermaid 或普通代码。完整约束见 [思维导图系统](./mindmap-system.md)。

## 9. MarkdownImage 图片渲染

`MarkdownImage` 统一处理 `src`、`alt`、尺寸、懒加载和失败状态。公开模式只允许批准的 URL scheme/host/path，不暴露存储键、本地路径或临时路径。表达含义的图片必须有 alt；纯装饰图片使用空 alt。

## 10. public 与 admin-preview 模式

- `public`：最严格白名单，只渲染已发布内容，禁用任意 HTML 和交互脚本。
- `admin-preview`：允许编辑预览所需的诊断与草稿内容，但仍执行净化，不等于可信 HTML 沙箱。

两种 mode 共享语义渲染结果；差异集中在诊断、未发布附件和错误提示，不能形成两套 Markdown 方言。

## 11. 安全净化策略

公开模式必须严格 sanitize。AI 生成内容一律视为不可信输入，AI 内容不得直接作为 MDX 执行，不允许任意 HTML 穿透公开页面。`rehype-sanitize` 处理 AST 白名单，DOMPurify 作为客户端动态 SVG/HTML 的最后防线；二者不能因“管理员生成”而跳过。

同时禁止事件属性、脚本、危险 URL、iframe 和未经批准的样式。特殊组件只接受经过解析和长度限制的纯文本源。

## 12. 迁移策略

1. 只读盘点现有渲染入口与调用方，但不在本轮执行。
2. 建立并测试统一 `RichText` 与安全 schema。
3. 分别接入 Code、KaTeX、Mermaid、Markmap 和图片。
4. 先迁移一个低风险公开详情页，再迁移 admin preview。
5. 对视觉、安全、SSR bundle 和错误降级做验收后，逐页替换旧入口。
6. 旧入口调用归零后再删除，不进行全站一次性替换。

## 13. 禁止事项

- 不在业务页面自建 Markdown 管线。
- 不执行 Markdown/AI 内容中的 MDX、HTML 或 JavaScript。
- 不把 Mermaid 与 Markmap 合成职责模糊的万能组件。
- 不向访客暴露 parser 错误、版本或堆栈。
- 不以禁用 sanitize 解决样式或插件兼容问题。
- 不让浏览器专用渲染库无意进入服务端 bundle。
