# Requirements: 稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染

**版本**: v1.1
**日期**: 2026-06-07
**来源**: 线上问题排查
**触及域**: `deploy`, `mistakes`, `notes`, `write-mistake`, `write-note`, `ai`, `images`, `cors`, `wrangler`, `markdown`, `katex`

## 1. 用户角色

| 角色 | 场景 |
|------|------|
| 错题学习者 | 在 `/write-mistake` 录入错题，在 `/mistakes` 复习，在详情页查看图片和 AI 解析 |
| 内容作者 | 编辑已有错题/笔记，图片上传后在线上可见 |
| 管理员/部署者 | 执行部署脚本，确保最新代码上线 |

## 2. 核心问题

### CP1: 图片上传后线上不可见
后端 `POST /api/notes/upload-image` 写入本地 `public/images/pictures/`，返回相对路径 `/images/pictures/...`。前端部署在 Cloudflare Worker，Worker assets 只包含构建时 `.open-next/assets/` 内的文件，运行时写入的图片不会自动进入 assets。结果：错题详情页图片框存在但图片 404。

### CP2: 错题编辑模式缺失
`/write-mistake` 只有新增模式（调用 `createNote()`），没有编辑模式。编辑错题复用 `/write-note/[slug]` 通用编辑页，但：
- 新增页和编辑页 UI 差异大（新增页有 AI 图片分析，编辑页没有）
- 编辑时如果 slug 变更会导致冲突
- AI 元数据（`ai_metadata`）在编辑页部分字段可能丢失
- 图片上传后 URL 是相对路径，编辑保存后依然不可见

### CP3: AI 解析纯文字，缺结构化图示
`AnalyzeResponse` 返回的 `analysis`、`error_reason`、`key_step` 等字段全是纯文本。对网络拓扑、流程图、公式推导、几何图形类题目不够直观。前端已有 Mermaid/Markmap/ECharts 渲染能力（AI Polish 子系统），但错题分析流程没有利用。

### CP4: 部署脚本顺序不安全
只执行 `npm run deploy` 会上传已有 `.open-next` 产物，不一定包含最新源码。正确顺序应为 `tsc --noEmit` → `build:cf` → `wrangler deploy`。`wrangler.toml` 原本没写 `workers_dev = true`，导致 route/domain 尝试失败时 workers.dev 入口被关掉。

### CP5: api.limengyang.me CORS 问题
公开页面跨域请求 `api.limengyang.me` 时被 Cloudflare Access 拦截，返回登录页导致 CORS 报错。已通过 `public-api.limengyang.me` 解决，需确认所有公开 API 调用都走正确域名。

### CP6: 错题字段 Markdown/LaTeX 未渲染（P0）
错题详情页和复习页中，`question`、`my_answer`、`correct_answer`、`analysis`、`knowledge_points` 等字段通过 `StudyBlock` 组件渲染，该组件使用 `whitespace-pre-wrap` 纯文本输出。导致：
- Markdown 标题 `###` 原样显示，不渲染为 `<h3>`
- Markdown 列表 `-` 原样显示，不渲染为 `<ul>/<li>`
- LaTeX 公式 `\frac{6 \times 8}{100 \times 10^6}` 原样显示，不渲染为数学符号
- 数学单位 `\mu s` 不渲染为 μs
- 代码块不渲染语法高亮

项目已有完整 Markdown 渲染管线（`src/lib/markdown-renderer.ts` 使用 marked + katex + shiki，`src/hooks/use-markdown-render.tsx` 转为 React），但仅用于笔记/博客的 `content` 字段，错题字段完全未接入。

## 3. 功能需求

### FR1: 图片存储 URL 策略改造（P0）

- **输入**: 用户在错题编辑器上传图片
- **处理**: 后端上传接口改为返回完整公开 URL（基于配置的 base URL），而非相对路径。图片文件仍写入后端本地 `public/images/pictures/`，但返回的 URL 包含后端公开地址（如 `https://backend-domain/images/pictures/...`）
- **备选方案**: 改为上传到 R2/OSS，返回 CDN URL（P2 阶段实施）
- **输出**: 前端 `<img src>` 和 `<a href>` 使用完整 URL，线上可加载
- **失败处理**: 如果 base URL 未配置，回退到相对路径并打印警告
- **兼容**: 已有相对路径图片在详情页渲染时自动补全 base URL

### FR2: 图片 URL 前端兼容（P0）

- **输入**: 前端请求图片 URL（可能是相对路径或完整 URL）
- **处理**: 采用方案 B — 前端拼接后端 base URL 直接访问（后端 CORS 已允许 `blog.limengyang.me`）。新建 `resolveImageUrl()` 工具函数：完整 URL 直接返回，相对路径拼接 `IMAGE_BASE_URL`
- **输出**: 线上图片可正常加载
- **失败处理**: 图片不存在时显示占位；`IMAGE_BASE_URL` 未配置时回退到 API_BASE_URL 并 console.warn
- **备选**: 如方案 B 遇 CORS 问题，切换到方案 A（后端图片代理端点 `GET /api/images/{path}`）

### FR3: 错题编辑模式（P0）

- **输入**: 用户从错题详情页点击"编辑"进入 `/write-mistake/[slug]`
- **处理**:
  1. 新增路由 `/write-mistake/[slug]`，复用 write-mistake 页面组件
  2. 页面初始化时检测 slug 参数，存在则调用 `getNote(slug)` 回填所有字段
  3. 保存时调用 `updateNote(slug, data)` 而非 `createNote()`
  4. 保留已有 `images` 和 `ai_metadata`，编辑时合并而非覆盖
  5. 编辑模式标题改为"编辑错题"，按钮改为"保存"
- **输出**: 错题可编辑，字段完整保留
- **失败处理**: slug 不存在时显示 404；保存失败时保留表单状态，显示错误提示

### FR4: 错题编辑页图片管理（P0）

- **输入**: 编辑已有错题时查看/管理图片
- **处理**:
  1. 加载已有图片列表（从 `note.images` 回填）
  2. 支持新增图片（上传后追加到列表）
  3. 支持删除已有图片（从列表移除，保存时生效）
  4. 图片 URL 兼容相对路径和完整 URL
- **输出**: 编辑页显示已有图片缩略图，可增删
- **失败处理**: 图片加载失败时显示占位

### FR5: Markdown + LaTeX 统一渲染（P0）

- **输入**: 错题详情页、复习页中展示的长文本字段
- **涉及字段**: `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, `review_advice`, `generalization`, `variant_questions`, AI summary/related knowledge 文本
- **处理**:
  1. 建立统一组件 `<RichText content={text} />`，内部调用现有 `useMarkdownRender` hook
  2. 替换所有直接使用 `<div>{text}</div>` 或 `<p>{text}</p>` 的位置
  3. AI prompt 层要求所有数学公式使用 LaTeX 语法：行内 `$...$`，块级 `$$...$$`
  4. 禁止输出裸 `\frac`，必须包裹在 `$` 或 `$$` 中
- **输出**: 标题渲染为 `<h1>`-`<h6>`，列表渲染为 `<ul>/<ol>`，LaTeX 渲染为数学符号，代码块有语法高亮
- **失败处理**: 内容为空时不渲染；Markdown/LaTeX 解析异常时降级为纯文本显示
- **性能**: 复用现有 debounce 机制（300ms），避免频繁重渲染

### FR6: AI prompt LaTeX 规范化（P0）

- **输入**: AI 分析错题时生成的文本
- **处理**: 在 `backend/app/routers/ai.py` 的 `OCR_SYSTEM_PROMPT` 和 `TEXT_SYSTEM_PROMPT` 中增加规则：
  1. 所有数学公式必须使用 LaTeX：行内 `$...$`，块级 `$$...$$`
  2. 计算过程示例：`$$\frac{6 \times 8}{100 \times 10^6} = 0.48\mu s$$`
  3. 禁止输出裸 `\frac`、`\sqrt`、`\int` 等命令
  4. 特殊字符（如希腊字母）用 LaTeX：`$\mu$`、`$\pi$`
- **输出**: AI 返回的 analysis、correct_answer 等字段包含标准 LaTeX 语法
- **失败处理**: 如果 AI 仍输出裸 LaTeX，前端渲染层降级显示原始文本

### FR7: AI 解析结构化图示字段（P1）

- **输入**: AI 分析错题时的原始内容（图片/文字）
- **处理**:
  1. `AnalyzeResponse` 新增可选字段 `diagrams: list[DiagramItem]`
  2. `DiagramItem` 包含 `type`（`flowchart`/`timeline`/`formula_breakdown`/`network_topology`/`geometry`/`state_machine`）、`title`、`mermaid`（Mermaid 语法）或 `data`（ECharts JSON）
  3. AI prompt 要求在分析数学/算法/网络/流程类题目时自动输出 diagram
  4. 前端详情页渲染 Mermaid 图（已有 `mermaid` 依赖）
- **输出**: 错题详情页展示结构化图示
- **失败处理**: AI 未返回 diagram 时不渲染（纯文字降级）；Mermaid 渲染失败时显示源码

### FR8: 部署脚本规范化（P2）

- **输入**: 部署者执行部署
- **处理**:
  1. `package.json` 新增 `deploy:full` 脚本：`npx tsc --noEmit && npm run build:cf && npx wrangler deploy --route 'blog.limengyang.me/*'`
  2. `wrangler.toml` 确认 `workers_dev = true`
  3. 保留 `npm run deploy`（opennextjs-cloudflare deploy）作为快速部署选项
- **输出**: 一条命令完成类型检查 → 构建 → 部署
- **失败处理**: 任何步骤失败则中止，不部署过时产物

## 4. 非功能需求

| 类型 | 要求 |
|------|------|
| 兼容性 | 已有相对路径图片在详情页自动补全，不破坏现有数据 |
| 类型安全 | `tsc --noEmit` 零错误 |
| 构建 | `npm run build:cf` 成功 |
| 性能 | 图片代理不引入明显延迟；Mermaid 渲染使用懒加载；RichText 复用 debounce |
| 安全 | 图片上传仍需 admin auth；代理端点不开放写操作 |
| 数据一致性 | 编辑错题时 `ai_metadata` 不丢失 |
| 渲染一致性 | 错题字段和笔记字段使用同一套 Markdown 渲染管线 |

## 5. 边界说明

**不在此轮范围**:
- R2/OSS 正式迁移（P2，需额外配置和迁移脚本）
- AI 生图/社交卡片生成
- 图片压缩/裁剪/CDN 优化
- 全文搜索优化
- 错题批量导入导出

## 6. 验收标准

| 编号 | 验收项 | 验证方式 |
|------|--------|----------|
| AC1 | 上传图片后返回完整 URL（非相对路径） | 调用上传接口，检查返回值 |
| AC2 | 线上错题详情页图片正常加载 | 部署后访问线上详情页 |
| AC3 | 已有相对路径图片在详情页自动补全为完整 URL | 访问含旧图片的错题 |
| AC4 | `/write-mistake` 新增错题正常（createNote） | 手动新增一个错题 |
| AC5 | `/write-mistake/[slug]` 编辑错题正常（getNote 回填 + updateNote） | 手动编辑已有错题 |
| AC6 | 编辑错题时 `ai_metadata` 字段完整保留 | 编辑后检查数据库 |
| AC7 | 编辑错题时已有图片正确显示 | 编辑含图片的错题 |
| AC8 | 编辑错题时可新增/删除图片 | 编辑页操作图片 |
| AC9 | 错题详情页 `question` 字段中的 `###` 渲染为标题 | 查看含 Markdown 标题的错题 |
| AC10 | 错题详情页 LaTeX 公式 `$\frac{1}{2}$` 渲染为数学符号 | 查看含 LaTeX 的错题 |
| AC11 | 错题详情页 Markdown 列表渲染为 `<ul>/<ol>` | 查看含列表的错题 |
| AC12 | 复习页 `analysis` 字段 LaTeX 正常渲染 | 进入复习流程查看 |
| AC13 | AI 新生成的 analysis 包含标准 LaTeX（`$...$`） | 调用 AI 分析，检查返回文本 |
| AC14 | AI 分析返回 `diagrams` 字段（数学/流程类题目） | 调用分析接口 |
| AC15 | 错题详情页渲染 Mermaid 图示 | 查看含 diagram 的错题 |
| AC16 | `deploy:full` 脚本一条命令完成部署 | 执行脚本 |
| AC17 | `wrangler.toml` 含 `workers_dev = true` | 检查文件 |
| AC18 | `tsc --noEmit` 零错误 | 命令行执行 |
| AC19 | `npm run build:cf` 成功 | 命令行执行 |
