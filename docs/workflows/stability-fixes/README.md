# 稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染

- **目标阶段**: P0/P1/P2 混合修复
- **触及域**: `deploy`, `mistakes`, `notes`, `write-mistake`, `write-note`, `ai`, `images`, `cors`, `wrangler`, `markdown`, `katex`
- **状态**: 已部署公网（等待用户最终验收）

## 问题来源

本轮线上暴露 6 类问题，按优先级分 3 个阶段修复：

| 优先级 | 问题 | 类别 |
|--------|------|------|
| P0-1 | 图片上传返回相对路径，线上 Worker 无法加载 | 图片存储 |
| P0-2 | 错题编辑复用新增页，字段丢失/slug 冲突 | 错题编辑 |
| P0-3 | Markdown 标题/LaTeX 公式/列表在错题详情和复习页原样输出，未渲染 | 文本渲染 |
| P1 | AI 解析纯文字，缺结构化图示 | 解析体验 |
| P2 | 部署脚本顺序不安全，wrangler.toml 缺 route | 部署链路 |
| — | R2/OSS 正式资产存储（不在本轮，归入后续迭代） | 图片存储 |

## 工作流文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `requirements.md` | 需求说明（6类问题 × 功能需求 + 验收标准） | ✅ 已交叉验证 |
| `design.md` | 技术设计（图片URL策略、编辑模式、RichText组件、AI schema、部署脚本） | ✅ 已交叉验证 |
| `tasks.md` | 带 checkbox 的任务清单（25项） | ✅ 25/25 完成（用户最终验收待确认） |

## 本轮变更范围

以下文件属于本轮稳定性修复：

**后端（5 文件）**
- `backend/app/config.py` — +`IMAGE_BASE_URL`
- `backend/app/routers/ai.py` — LaTeX + diagram prompt 规范
- `backend/app/routers/notes.py` — 上传返回完整 URL
- `backend/app/schemas/ai.py` — +`DiagramItem`, +`diagrams`
- `backend/main.py` — +`StaticFiles` 挂载

**前端（10 文件）**
- `src/lib/api/config.ts` — +`IMAGE_BASE_URL`
- `src/lib/api/images.ts` — 新建 `resolveImageUrl()`
- `src/lib/api/ai.ts` — +`DiagramItem` 类型, +`diagrams`
- `src/lib/content-routes.ts` — 错题编辑路径
- `src/components/rich-text.tsx` — 新建
- `src/app/notes/[id]/note-detail-content.tsx` — RichText + resolveImageUrl + diagrams
- `src/app/mistakes/review/page.tsx` — RichText
- `src/app/write-mistake/page.tsx` — 薄包装
- `src/app/write-mistake/components/mistake-form.tsx` — 新建共享表单
- `src/app/write-mistake/[slug]/page.tsx` — 新建编辑路由

**配置 + 文档（4 文件）**
- `package.json` — +`deploy:full`
- `wrangler.toml` — 无变更（`workers_dev = true` 已存在）
- `docs/workflows/stability-fixes/` — 全部新建

**不属于本轮**（并行任务/其他工作流）：
- `docs/workflows/ai-skill-pipeline/*`
- `src/app/mistakes/page.tsx`, `src/app/mistakes/components/`
- `src/app/notes/[id]/components/`
- `src/hooks/use-knowledge.ts`
- `public/images/pictures/mistake/`（运行时上传产物）

## 关键约束

- 前端部署在 Cloudflare Workers（opennextjs-cloudflare），后端在独立服务器
- 公开只读 API 域名 `public-api.limengyang.me` 已存在，不受 Access 保护
- 图片当前写入后端本地 `public/images/pictures/`，不会自动进入 Worker assets
- SM-2 复习字段由后端管理，前端不设置
- Markdown 渲染管线（marked + katex + shiki）已存在，但错题字段未接入
- 图片代理采用方案 B（前端直连后端 base URL），不新增代理端点
- R2/OSS 迁移不在本轮，IMAGE_BASE_URL 未来可切换为 R2 bucket URL
