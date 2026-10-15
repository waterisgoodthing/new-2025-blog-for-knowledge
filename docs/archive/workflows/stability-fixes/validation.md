# 交叉验证报告

**日期**: 2026-06-07
**版本**: v1.4（第四轮复审修复后）

## 验证范围

- `README.md` ↔ `requirements.md` ↔ `design.md` ↔ `tasks.md`
- 代码实现 vs 设计文档
- 变更文件范围 vs 本轮任务

## 第一轮修复（v1.1）

| # | 问题 | 修复 |
|---|------|------|
| 1 | README R2/OSS 标为 P2 但 requirements 归入边界 | README 改为"不在本轮" |
| 2 | FR2 方案 A/B 未明确选择 | requirements 改为明确选择方案 B |
| 3 | P0-1-05 涉及文件写 page.tsx 而非 mistake-form.tsx | 更新涉及文件 + 添加依赖 |
| 4 | AC19 build:cf 无对应任务 | P0-3-05 合并 tsc + build:cf |
| 5 | design §5.1 echarts 与 FR7 data 字段名不一致 | design 改为 data |
| 6 | 依赖图缺少 P0-2-01 → P0-1-05 | 依赖图更新 |
| 7 | FR1 失败处理 fallback 无任务覆盖 | 新增 P0-1-07 |

## 第二轮修复（v1.2）

| # | 问题 | 修复 |
|---|------|------|
| 8 | design 写"StaticFiles 已挂载"但 main.py 实际没有 | design 改为"需要新增挂载"，P0-1-06 改为"新增 FastAPI /images 静态文件挂载" |
| 9 | AI prompt 文件写成 ai_service.py，实际在 routers/ai.py | requirements、design、tasks 全部改为 `backend/app/routers/ai.py` |
| 10 | P1 图表范围过宽（Mermaid + ECharts） | 收窄为仅 Mermaid，复用 mermaid-block.tsx |
| 11 | DiagramItem.mermaid 可选 → 必填 | design §5.1 改为 `mermaid: str` |
| 12 | diagrams 默认值 `[]` 应为 `Field(default_factory=list)` | design §5.1 改为 `Field(default_factory=list)` |
| 13 | RichText 组件缺 'use client' | design + tasks 增加标注 |
| 14 | 缺公网图片可访问验证 | 新增 P0-1-08 |
| 15 | README 状态不一致 | 统一为"待审批" |

## 第三轮修复（v1.3）

| # | 问题 | 修复 |
|---|------|------|
| 16 | StaticFiles 挂载路径 `backend/public/images` 与上传目标 `<repo>/public/images` 不匹配 | `main.py` 改用 `Path(__file__).parent.parent / "public" / "images"` |
| 17 | `diagrams` 未进入前端 `AnalyzeResponse` 类型 | `src/lib/api/ai.ts` 新增 `DiagramItem` + `diagrams` |
| 18 | `applyResult` 未保存 `diagrams` 到 `aiMetadata` | `mistake-form.tsx` 新增 `diagrams: result.diagrams \|\| []` |
| 19 | RichText 在 hook 调用前 early return | 移到 hook 调用之后，`text` 默认为 `''` |
| 20 | README tasks.md 行仍写"待审批" | 改为"✅ 24/25 完成" |
| 21 | 变更范围未区分本轮/并行任务 | README 新增"本轮变更范围"节 |

## 第四轮复审修复（v1.4）

| # | 问题 | 修复 |
|---|------|------|
| 22 | `OCR_SYSTEM_PROMPT` / `TEXT_SYSTEM_PROMPT` 使用普通三引号字符串，`\frac`、`\times` 等 LaTeX 示例会触发 Python 转义污染 | 两个 system prompt 改为 raw string，保留原始 LaTeX 反斜杠 |
| 23 | JSON 示例未包含 `diagrams` 字段，和 P1 diagram 输出规则不完全一致 | 两个 JSON 示例补充 `diagrams` 字段 |
| 24 | `/images` 静态目录如果在后端首次启动时不存在，路由不会挂载 | 启动时主动创建 `public/images` 后再挂载 StaticFiles |
| 25 | 运行时上传的错题图片显示为 Git 未跟踪文件 | `.gitignore` 忽略 `/public/images/pictures/` |
| 26 | `serverExternalPackages` 将 Markdown/KaTeX/Mermaid/Shiki 等浏览器侧库打入 Worker server bundle，Cloudflare 免费计划部署超 3 MiB | 移除 `serverExternalPackages`，将图表组件改为 `ssr: false` 动态加载，关闭 Shiki 高亮路径，代码块降级为普通渲染 |

## 公网部署验证（2026-06-07）

| 项目 | 结果 |
|------|------|
| `npx tsc --noEmit` | ✅ 通过 |
| `npm run build:cf` | ✅ 通过 |
| `npx wrangler deploy --route 'blog.limengyang.me/*'` | ✅ 通过 |
| Worker Version ID | `ec29e69a-da33-4b99-a5c7-c1df90d531c5` |
| `curl -I https://blog.limengyang.me/mistakes` | ✅ 200 |
| `curl https://public-api.limengyang.me/api/health` | ✅ `{"status":"ok","db":"ok"}` |
| `curl -I https://public-api.limengyang.me/images/pictures/mistake/note-1780826561540/b58fc2ec.png` | ✅ 200, `image/png` |

## 最终验证矩阵

### README ↔ requirements ✅
6 个问题全部有对应 CP 或边界说明。

### requirements FR ↔ design ✅
8 个 FR 全部有 design section 覆盖。

### design ↔ tasks ↔ 代码 ✅
- §2 图片存储 → P0-1-01 ~ P0-1-08 → 代码路径已验证（上传目录 == 挂载目录）
- §3 错题编辑 → P0-2-01 ~ P0-2-07 → 路由 + 表单 + 保存链路完整
- §4 RichText → P0-3-01 ~ P0-3-05 → hook 顺序安全
- §5 AI 图示 → P1-01 ~ P1-03 → 后端 schema → 前端 type → applyResult → 详情页渲染
- §6 部署 → P2-01 ~ P2-02 → deploy:full 脚本

### AC ↔ tasks ✅
19 个 AC 全部有对应任务。

### 变更范围 ✅
README 已列出本轮 19 个文件（5 后端 + 10 前端 + 4 配置/文档），并标注不属于本轮的并行文件。

## 结论

四份文件形成闭环，共 **25 个任务**（P0-1: 8, P0-2: 7, P0-3: 5, P1: 3, P2: 2）。
25 个任务已完成，公网 curl 验证通过。
`tsc --noEmit` 零错误，`npm run build:cf` 成功。后端 venv 导入检查通过，确认 `/images` 路由已注册，LaTeX prompt 原始反斜杠已保留。
剩余开放项：用户最终 UI 验收。
