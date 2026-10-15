# UI V2 Architecture — Repository UI Audit（F0，2026-09-13）

只读审计结论；本轮不改任何业务文件。

## 1. 路由现状（`src/app/**`）

| Current Route | 类型 | 说明 |
|---|---|---|
| `/` (home) | public | 首页 |
| `/blog`, `/blog/[slug]` | public | 博客列表 + 详情（静态 `public/blogs/index.json` 当前为空数组，后端迁移中） |
| `/notes` | public 读 + admin 写 | 笔记工作区（含 WeeklySummaryCard，admin 才挂载） |
| `/mistakes` | public 读（visibility 过滤） | 错题 |
| `/manage` + `/manage/(workspace)/*` | admin（`AuthGate` 仅 UX，真实边界 `get_current_admin`） | dashboard / notes / drafts / questions / mistakes / review / subjects / knowledge-points / capture / ai / attachments / jobs / search / analytics / settings |
| `/write`, `/write-note`, `/write-mistake` | admin | 旧三编辑器（refactor-plan 拟统一为 workspace） |
| 其余 | public | about / discover / guestbook / music / pictures / snippets / share / clock / live2d / image-toolbox / bloggers / projects / rss / sitemap |

## 2. 数据分层现状

`page/component → hook 或 local action → src/lib/api/* → backend API`。
`src/lib/api/*` 共 34 个 client（notes/questions/mistakes/review/review-items/
dashboard/knowledge/taxonomy/search/folders/drafts/captures/attempts/ai…），
DTO 为 snake_case 后端直映。`apiFetch` 经 `client.ts`，session 经 HttpOnly
`admin_session` cookie + `credentials: 'include'`。

## 3. 样式现状

- `src/styles/globals.css`：tailwind v4（`@import 'tailwindcss'`）+ base 层，
  全局 `border-border`、button cursor、range-track 品牌渐变。
- `src/styles/theme.css`（`@theme`，15 行）：`--color-brand #35bfab`、
  `--color-primary #334f52`、`--color-bg #eeeeee`、`--color-card #ffffff66`、
  Averia + PingFang 系统字体栈。**本轮零修改。**
- 玻璃拟态/圆角 16px 等见 `docs/refactor-plan/02-UI-DESIGN-SYSTEM-BLUE-WHITE.md`
 （规范文档，非本周实施）。

## 4. 关键约束（影响 V2 设计）

- `AuthGate` 不是安全边界；公开读路由 accidental 私有化是已知风险。
- `public/blogs/index.json` 为空：博客列表当前无静态数据源，V2 Mock 不得假装有真实博客。
- Review 调度/判定语义归 Week2（PR-05~08）所有，本轨只读。
- 无 `src/contracts|mocks|adapters|features` 目录 → 采用 `*/ui-v2` 新命名空间。
