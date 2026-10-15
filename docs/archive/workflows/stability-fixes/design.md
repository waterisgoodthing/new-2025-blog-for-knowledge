# Design: 稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染

**版本**: v1.1
**日期**: 2026-06-07
**触及域**: `deploy`, `mistakes`, `notes`, `write-mistake`, `write-note`, `ai`, `images`, `cors`, `wrangler`, `markdown`, `katex`

## 1. 整体架构

```
┌─────────────────────────────────────────────────────┐
│                  Cloudflare Workers                   │
│  blog.limengyang.me                                  │
│  ┌─────────────────────────────────────────────┐    │
│  │  Next.js App (opennextjs-cloudflare)         │    │
│  │  /write-mistake        → 新增错题             │    │
│  │  /write-mistake/[slug] → 编辑错题（新增）      │    │
│  │  /notes/[id]           → 错题详情 + 图片 + 图表 │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
          │ fetch API                    │ fetch 图片
          ▼                              ▼
┌─────────────────────┐    ┌──────────────────────────┐
│ public-api.limengyang.me │    │ 后端图片服务               │
│ (公开只读 API)        │    │ public/images/pictures/  │
│ GET /api/notes/*     │    │ 或未来 R2/OSS            │
└─────────────────────┘    └──────────────────────────┘
          │
          ▼
┌─────────────────────┐
│ api.limengyang.me    │
│ (Admin API, Access)  │
│ POST /api/notes      │
│ PUT  /api/notes/:slug│
│ POST /api/ai/analyze │
│ POST /api/notes/upload-image │
└─────────────────────┘
```

## 2. 图片存储 URL 策略

### 2.1 当前问题

- 上传接口返回 `/images/pictures/mistake/slug/abc.png`（相对路径）
- 前端在 Cloudflare Worker 上，`<img src="/images/pictures/...">` 会请求 Worker assets，但图片不在 assets 中
- 图片实际在后端服务器的 `public/images/pictures/` 目录

### 2.2 设计方案

**方案: 前端拼接后端 base URL + 后端 CORS 允许**

改动点：

1. **后端 `config.py`** — 新增 `IMAGE_BASE_URL` 配置项，默认值为后端公开 URL
2. **后端上传接口 `routers/notes.py`** — 返回完整 URL：
   - 当前: `return {"url": f"/images/pictures/{relative_path}"}`
   - 改为: `return {"url": f"{settings.IMAGE_BASE_URL}/images/pictures/{relative_path}"}`
3. **后端静态文件服务** — 当前 `backend/main.py` **没有** `StaticFiles` 挂载。需要新增：
   ```python
   from fastapi.staticfiles import StaticFiles
   app.mount("/images", StaticFiles(directory="public/images"), name="images")
   ```
   挂载位置在 CORS 中间件之后、router include 之前。CORS 中间件对所有路由生效，包括 StaticFiles。
4. **前端兼容层** — 详情页渲染图片时，如果 URL 是相对路径，自动补全后端 base URL
5. **前端 `config.ts`** — 新增 `IMAGE_BASE_URL` 常量，从 `NEXT_PUBLIC_IMAGE_BASE_URL` 读取，回退到 API base URL

```typescript
// src/lib/api/config.ts
export const IMAGE_BASE_URL = process.env.NEXT_PUBLIC_IMAGE_BASE_URL 
  || API_BASE_URL  // 回退到 API base
```

```python
# backend/app/config.py
IMAGE_BASE_URL: str = "https://public-api.limengyang.me"
```

```python
# backend/app/routers/notes.py — upload-image 端点
return {"url": f"{settings.IMAGE_BASE_URL}/images/pictures/{relative_path}"}
```

### 2.3 图片 URL 兼容处理

```typescript
// src/lib/api/images.ts（新增）
export function resolveImageUrl(url: string): string {
  if (!url) return url
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  // 相对路径 → 拼接后端 base
  return `${IMAGE_BASE_URL}${url.startsWith('/') ? '' : '/'}${url}`
}
```

详情页和编辑页统一使用 `resolveImageUrl()` 渲染图片。

### 2.4 后端 CORS 配置

确认 `ALLOWED_ORIGINS` 包含 `https://blog.limengyang.me`（已包含）。

后端 `StaticFiles` 挂载需要确保 CORS 中间件对其生效。FastAPI CORS 中间件在 middleware 层，对所有路由生效，包括 StaticFiles。

### 2.5 R2/OSS 迁移路径（P2，不在本轮）

未来可将 `upload-image` 改为写入 R2，返回 R2 公开 URL。`IMAGE_BASE_URL` 改为 R2 bucket URL。数据库中已有 URL 不需迁移（R2 URL 和本地 URL 结构不同，需迁移脚本）。

## 3. 错题编辑模式

### 3.1 路由设计

| 路由 | 页面 | 行为 |
|------|------|------|
| `/write-mistake` | 新增错题 | `createNote()`，AI 图片/文字分析 |
| `/write-mistake/[slug]` | 编辑错题 | `getNote(slug)` 回填，`updateNote(slug, data)` 保存 |

### 3.2 组件复用策略

将 `write-mistake/page.tsx` 重构为：

```
src/app/write-mistake/
├── page.tsx                    → 新增模式入口（无 slug）
├── [slug]/
│   └── page.tsx                → 编辑模式入口（有 slug）
└── components/
    └── mistake-form.tsx        → 共享表单组件（新增/编辑复用）
```

`mistake-form.tsx` 接收 `mode: 'create' | 'edit'` 和可选的 `initialData`。

### 3.3 编辑模式数据流

```
/write-mistake/[slug]
  → useParams() 获取 slug
  → SWR: getNote(slug) 获取 note 数据
  → 回填表单: title, question, my_answer, correct_answer, analysis, knowledge_points, subject, difficulty, tags, images
  → 回填 aiMetadata: note.ai_metadata
  → 用户编辑...
  → handleSave(): updateNote(slug, {...fields, images, ai_metadata})
  → router.push(getContentDetailHref('mistake', slug))
```

### 3.4 图片管理

编辑模式下图片状态管理：

```typescript
const [existingImages, setExistingImages] = useState<string[]>([])  // 已有图片 URL
const [newImages, setNewImages] = useState<string[]>([])            // 新上传图片 URL
const [removedImages, setRemovedImages] = useState<string[]>([])    // 已删除图片 URL

// 最终保存时
const images = [...existingImages, ...newImages].filter(url => !removedImages.includes(url))
```

### 3.5 AI 元数据保留

编辑保存时，`ai_metadata` 字段从表单状态中取值（初始化时从 `note.ai_metadata` 回填），确保不会因为编辑其他字段而丢失。

### 3.6 编辑入口

在错题详情页 (`/notes/[id]`) 添加"编辑"按钮：

```tsx
// note-detail-content.tsx — mistake 类型时显示编辑按钮
{isAdmin && note.type === 'mistake' && (
  <Link href={`/write-mistake/${note.slug}`}>
    <Button>编辑错题</Button>
  </Link>
)}
```

当前详情页已有通用编辑按钮（跳转 `/write-note/[slug]`），需改为错题专用路径。

## 4. Markdown + LaTeX 统一渲染

### 4.1 当前问题

`StudyBlock` 组件（`note-detail-content.tsx:263-279`）渲染错题字段时使用纯文本：

```tsx
function StudyBlock({ title, content, fallback, tone, large = false }) {
    const value = content || fallback
    return (
        <section>
            <h2>{title}</h2>
            <div className='break-words whitespace-pre-wrap text-sm leading-6'>{value}</div>
        </section>
    )
}
```

复习页（`mistakes/review/page.tsx`）同样用 `<div className='whitespace-pre-wrap'>{text}</div>` 渲染所有字段。

项目已有完整渲染管线但未接入错题：
- `src/lib/markdown-renderer.ts` — marked + katex + shiki，输出 HTML string
- `src/hooks/use-markdown-render.tsx` — html-react-parser 转 React，含 Mermaid/CodeBlock/MathBlock
- KaTeX CSS 已全局引入

### 4.2 RichText 组件设计

新建 `src/components/rich-text.tsx`：

```tsx
'use client'

import { useMarkdownRender } from '@/hooks/use-markdown-render'

interface RichTextProps {
  content: string
  className?: string
  fallback?: string
}

export function RichText({ content, className, fallback }: RichTextProps) {
  const text = content || fallback
  if (!text) return null
  
  const { content: rendered, loading } = useMarkdownRender(text)
  
  if (loading) {
    return <div className={cn('animate-pulse bg-gray-100 rounded h-16', className)} />
  }
  
  return (
    <div className={cn('prose prose-sm max-w-none', className)}>
      {rendered || <div className='whitespace-pre-wrap'>{text}</div>}
    </div>
  )
}
```

核心逻辑：
- 复用 `useMarkdownRender` hook（内部调用 `renderMarkdown` → marked + katex + shiki）
- loading 状态显示骨架屏
- 渲染失败降级为 `whitespace-pre-wrap` 纯文本
- `prose prose-sm max-w-none` 与笔记详情页一致

### 4.3 替换范围

#### 4.3.1 `note-detail-content.tsx` — StudyBlock 改造

```tsx
// 改造前
<div className='break-words whitespace-pre-wrap text-sm leading-6'>{value}</div>

// 改造后
<RichText content={value} className='text-sm leading-6' />
```

涉及字段：`question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`
以及 AI metadata：`error_reason`, `key_step`, `generalization`, `review_advice`, `similar_traps`, `variant_questions`

#### 4.3.2 `mistakes/review/page.tsx` — 复习页改造

```tsx
// 改造前
<div className='whitespace-pre-wrap'>{item.question}</div>

// 改造后
<RichText content={item.question} />
```

涉及字段：`question`, `correct_answer`, `analysis`, `knowledge_points`

#### 4.3.3 不改动的位置

- `/write-note` 编辑器预览 — 已使用 `useMarkdownRender`
- 博客详情页 — 已使用 markdown 渲染
- 笔记详情页 `content` 字段 — 已使用 markdown 渲染

### 4.4 AI Prompt LaTeX 规范

在 `backend/app/routers/ai.py` 的 `OCR_SYSTEM_PROMPT` 和 `TEXT_SYSTEM_PROMPT` 中增加：

```
## 数学公式规范
所有数学公式必须使用 LaTeX 语法：
- 行内公式：$...$ 例如 $E = mc^2$
- 块级公式：$$...$$ 例如 $$\frac{6 \times 8}{100 \times 10^6} = 0.48\mu s$$
- 禁止输出裸 \frac、\sqrt、\int 等命令，必须包裹在 $ 或 $$ 中
- 希腊字母用 LaTeX：$\mu$ 而非 \mu 或 μ
- 单位用 LaTeX：$\mu s$、$m/s^2$
```

### 4.5 性能考量

- `useMarkdownRender` 内置 300ms debounce，避免输入时频繁渲染
- 详情页字段变化频率低（只在数据加载时变化），debounce 开销可忽略
- 复习页每次翻页触发一次渲染，单次渲染 <100ms（文本量小）
- KaTeX 已全局加载，无额外网络请求

## 5. AI 解析结构化图示

### 5.1 Schema 设计

```python
# backend/app/schemas/ai.py

class DiagramItem(BaseModel):
    type: Literal["flowchart", "timeline", "formula_breakdown", 
                  "network_topology", "geometry", "state_machine"]
    title: str
    mermaid: str  # Mermaid 语法，必填

class AnalyzeResponse(BaseModel):
    # ... 现有字段 ...
    diagrams: list[DiagramItem] = Field(default_factory=list)
```

本轮只支持 Mermaid 图表。ECharts 作为后续扩展（`DiagramItem.data` 字段留待后续迭代添加）。

### 5.2 AI Prompt 改动

在 `backend/app/routers/ai.py` 的 `OCR_SYSTEM_PROMPT` 和 `TEXT_SYSTEM_PROMPT` 中增加：

```
如果题目涉及以下类型，必须在 diagrams 字段输出对应的图示：
- 流程/算法题 → type: "flowchart", 用 Mermaid graph TD 语法
- 时间线/事件顺序 → type: "timeline", 用 Mermaid timeline 语法
- 公式推导/数学证明 → type: "formula_breakdown", 用 Mermaid graph 语法展示推导步骤
- 网络拓扑/协议 → type: "network_topology", 用 Mermaid graph 语法
- 几何图形 → type: "geometry", 用 Mermaid 语法描述几何关系
- 状态机/有限自动机 → type: "state_machine", 用 Mermaid stateDiagram 语法

diagrams 为空数组 [] 表示该题不需要图示。
```

### 5.3 前端渲染

复用已有 `src/components/mermaid-block.tsx`（接受 `code: string`，内部懒加载 mermaid，渲染 SVG，自带错误降级和全屏查看）。

```tsx
// note-detail-content.tsx — AI 图示渲染
import { MermaidBlock } from '@/components/mermaid-block'

{note.ai_metadata?.diagrams?.length > 0 && (
  <div className="space-y-4">
    {note.ai_metadata.diagrams.map((diagram, idx) => (
      <div key={idx}>
        {diagram.title && <h3 className='text-sm font-medium mb-1'>{diagram.title}</h3>}
        <MermaidBlock code={diagram.mermaid} />
      </div>
    ))}
  </div>
)}
```

不新建 DiagramViewer 组件。`MermaidBlock` 已处理：
- 懒加载 mermaid 库（模块级单例）
- 随机渲染 ID 避免冲突
- 渲染失败降级为 `<pre><code>`
- loading 骨架屏
- 全屏查看 + 缩放 + 下载

### 5.4 写入流程

AI 分析返回 `diagrams` 后：
1. 存入 `ai_metadata.diagrams`
2. 前端在详情页渲染
3. 编辑时回填并保留

## 6. 部署脚本规范化

### 6.1 wrangler.toml

```toml
main = ".open-next/worker.js"
name = "2025-blog-public"
workers_dev = true
compatibility_date = "2025-03-25"
compatibility_flags = ["nodejs_compat"]

[[routes]]
pattern = "blog.limengyang.me/*"
zone_name = "limengyang.me"

[assets]
directory = ".open-next/assets"
binding = "ASSETS"
```

关键：`workers_dev = true` 确保 workers.dev 子域名始终可用，`[[routes]]` 绑定自定义域名。

### 6.2 package.json scripts

```json
{
  "deploy:full": "npx tsc --noEmit && npm run build:cf && npx wrangler deploy --route 'blog.limengyang.me/*'",
  "deploy:quick": "npm run deploy"
}
```

`deploy:full` = 完整流程（类型检查 → 构建 → 部署）
`deploy:quick` = 仅部署已有产物（需先手动 build）

### 6.3 推荐工作流

```bash
# 标准部署
npm run deploy:full

# 或分步
npx tsc --noEmit
npm run build:cf
npx wrangler deploy --route 'blog.limengyang.me/*'
```

## 7. 数据流总览

### 错题创建（现有，改进图片 URL）
```
用户上传图片 → POST /api/notes/upload-image → 写入本地 + 返回完整 URL
用户触发 AI 分析 → POST /api/ai/analyze → 返回 AnalyzeResponse（含 diagrams）
用户保存 → POST /api/notes → createNote({..., images: [完整URL], ai_metadata: {diagrams, ...}})
```

### 错题编辑（新增）
```
进入 /write-mistake/[slug] → GET /api/notes/:slug → 回填表单
用户编辑 + 新增/删除图片
用户保存 → PUT /api/notes/:slug → updateNote({..., images, ai_metadata})
```

### 错题查看（改进图片渲染 + 新增图示）
```
进入 /notes/[id] → GET /api/notes/:slug → 渲染详情
图片: resolveImageUrl(url) → 补全 base URL → <img src>
图示: note.ai_metadata.diagrams → DiagramViewer → Mermaid SVG
```
