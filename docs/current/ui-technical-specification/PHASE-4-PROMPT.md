# Phase 4 启动 Prompt — 给 DeepSeek

你是本仓库的前端实施智能体，任务是完成 UI 重构 **Phase 4：扩展接入 + 最终验收**（VSC-14 至 VSC-17）。只做 Phase 4，做完停下汇报。

## 0. 开工前必读

1. 先读 `AGENTS.md`（仓库强制规则），再读：
   - `docs/current/ui-technical-specification/04-execution/task-registry.md`（唯一执行清单，Phase 4 章节）
   - `docs/current/ui-technical-specification/04-execution/acceptance-criteria.md`
   - `docs/current/ui-technical-specification/02-to-be/design-foundations.md`
2. 本项目的 Next.js 版本有破坏性变更，写代码前查 `node_modules/next/dist/docs/` 中相关指南。
3. 运行 `git status --short`。Phase 1–3 均已提交（`d351efb` `c330db8` `f0d704b`）。若开工时仍有未提交改动，视为用户改动，**不要回滚、重排、格式化或覆盖**。

## 1. 现场事实（已核实，优先于文档中的描述）

- 仓库：`/Users/limengyang/2025-blog-public`，分支 `refactor/baseline`
- 基线：`npx tsc --noEmit` 0 errors；`npx vitest run` 77 files / 646 passed；`npm run build` 成功
- 前端：Next.js 16 + React 19 + Tailwind 4 + `motion` + `lucide-react`；测试 Vitest + `@testing-library/react`
- Token：`src/components/ui-v2/tokens.css` 已有完整双表面系统（含 `[data-theme='dark']` 暗色 token），只消费不改色值
- **不要用** `--radius-*` / `--font-*` / `--shadow-*` 同名自定义变量，它们是 Tailwind 4 主题命名空间；用 `--ui-*` / `--uiv2-*`
- `src/app/layout.tsx` 桥接变量故意没有 `|| '#fallback'`，暗色模式依赖这一点，不要改
- Phase 2/3 可复用基础：`src/hooks/use-overlay.ts`、`src/components/ui-v2/`（Modal、Drawer、ContextMenu、AppShell、AdminSidebar、PublicTopNav、MobileDrawer 等）
- 旧 overlay 消费者（**还未迁移**，本 Phase 处理）：
  - `src/app/manage/music-form-modal.tsx` 用 `DialogModal`
  - `src/app/blog/components/category-modal.tsx` 用 `DialogModal`
  - `src/app/mistakes/components/weak-point-diagnosis.tsx` 用 `Drawer`
- 管理后台真实路径：`src/app/manage/(workspace)/`（25 个页面，见下文），VSC-14 只接触其中的内容列表/管理类页面
- **暗色模式实现注意**：`tokens.css` 已用 `[data-theme='dark']` 属性选择器，**不是** `prefers-color-scheme`。切换逻辑需要操作 `document.documentElement.dataset.theme`，不要用 `@media (prefers-color-scheme: dark)` 覆写整套 token
- **依赖批准**：本 Phase 批准安装 `@vitest/coverage-v8`，作为 devDependency。安装命令：`npm install --save-dev @vitest/coverage-v8`。这是唯一允许新增的依赖，安装后在 `vitest.config.ts` 加 `coverage: { provider: 'v8', reporter: ['text', 'json'] }` 配置

## 2. Manage workspace 页面清单（真实路径）

```
src/app/manage/(workspace)/
  ai/page.tsx, ai/runs/page.tsx
  analytics/page.tsx
  attachments/page.tsx, attachments/[id]/page.tsx
  capture/page.tsx
  dashboard/page.tsx         ← Phase 2 已接入 admin token
  drafts/page.tsx, drafts/[id]/page.tsx
  jobs/page.tsx
  knowledge-points/page.tsx, knowledge-points/[id]/page.tsx
  mistakes/page.tsx, mistakes/[id]/page.tsx
  notes/page.tsx, notes/new/page.tsx, notes/[slug]/page.tsx
  practice/page.tsx
  questions/page.tsx, questions/[id]/page.tsx
  review/page.tsx
  search/page.tsx
  settings/page.tsx
  subjects/page.tsx, subjects/[id]/page.tsx
```

dashboard 已完成；VSC-14 优先覆盖**信息密度高、有列表/表格/弹窗的页面**：questions、mistakes、notes、drafts、review。其余页面（analytics、jobs、ai 等）如时间允许接入，否则在汇报里标 DEFERRED。

## 3. 任务

### VSC-14 管理页面扩展接入

- 目标页面：`questions` / `mistakes` / `notes` / `drafts` / `review`（workspace 下的 page.tsx 和 components/）
- 换用 `--admin-*` token 和 UI V2 Card/Button/Badge/PageHeader；页内弹窗换成 `ui-v2/Modal`（Drawer 保留 Phase 2 的 Uiv2Drawer）
- 迁移 `music-form-modal.tsx` 从 `DialogModal` 到 `ui-v2/Modal`（已有测试应继续通过）
- 数据流、接口调用、权限逻辑、路由一律不动
- 逐页迁移后立即用 `npx tsc --noEmit` 和相关测试验证，再继续下一页

### VSC-15 公开内容页扩展接入

- 目标页面：`src/app/blog/page.tsx`、`src/app/mistakes/page.tsx`（公开端列表），及各自的 `components/` 目录
- 换用 `--editorial-*` token 和 UI V2 组件；卡片网格保持现有布局
- 迁移 `src/app/blog/components/category-modal.tsx` 从 `DialogModal` 到 `ui-v2/Modal`
- 迁移 `src/app/mistakes/components/weak-point-diagnosis.tsx` 从旧 `Drawer` 到 `ui-v2/Drawer`
- **公开端 VerticalNav/MobileNav/NavCard 一律不动**（切换留待单独批准）
- 数据流、API、公开/私有可见性不动

### VSC-16 暗色模式切换 UI

- 新建 `src/components/ui-v2/ThemeToggle.tsx`：轻量 icon button，切换 `document.documentElement.dataset.theme`，持久化到 `localStorage`（try/catch 包裹），初始化时读 `localStorage`，没有记录时跟随 `prefers-color-scheme`
- 把 `ThemeToggle` 接入 manage workspace 的 `ManageTopbar`（`src/app/manage/components/manage-topbar.tsx`）和 `/dev/tokens` 预览页
- 测试：初始化逻辑、切换、localStorage 读写、`prefers-color-scheme` fallback、`localStorage` 不可用时不崩

### VSC-17 最终验收

1. 安装 `@vitest/coverage-v8`，配置 `vitest.config.ts`，运行 `npx vitest run --coverage`，报告 UI V2 新增组件的行覆盖率
2. 运行 `npx tsc --noEmit`（0 errors）
3. 运行 `npx vitest run`（全部通过，数量 ≥ 646 + 新增）
4. 运行 `npm run build`（成功，路由表与 Phase 3 基线对比只新增 `/dev/nav` 以内的路由）
5. 运行 `git diff --check`（clean）
6. 浏览器验证（生产构建 + Chromium）：
   - `/manage/questions`、`/manage/notes`、`/manage/review`：admin 表面，截图
   - `/blog`、`/mistakes`：editorial 表面，截图
   - 暗色模式：切换后 editorial 和 admin 表面颜色均变，截图
   - 弹窗：Modal 和 Drawer 打开/关闭，背景 inert，焦点管理
   - 触控目标尺寸：至少抽查 3 个交互元素，验证 ≥ 44px
7. 更新 `task-registry.md` 和 `acceptance-criteria.md` 全部状态

## 4. 不允许做的事

- 改后端、API 合约、鉴权逻辑、路由（`/dev/` 预览页除外）
- 改 `src/layout/index.tsx`、`vertical-nav.tsx`、`mobile-nav.tsx`、`nav-card.tsx`
- 改 `tokens.css` 色值
- 改 `globals.css` 的 cursor 规则
- `layout.tsx` 的桥接变量加 `|| '#fallback'`
- 除 `@vitest/coverage-v8` 之外新增任何依赖
- commit、push、部署

## 5. 汇报格式

先给结论（PASS / PARTIAL / FAIL / BLOCKED / NOT_VERIFIED），然后：

- **Changes**：按任务列出新增/修改文件
- **Verification**：每条命令和结果；VSC-17 步骤 1 给出 UI V2 组件的行覆盖率数字（不强制阈值，只要有数字）
- **Browser evidence**：截图放 `docs/current/workflows/visual-system-consolidation/assets/phase4-*.png`
- **Deviations**：与 task-registry 不一致的地方及原因（DEFERRED 页面在这里列出）
- **Remaining / NOT_VERIFIED**：未完成项；iOS/Android 真机做了写 VERIFIED，没做写 NOT_VERIFIED

如果用了独立子代理审查，写明审查者 ID 和它报的问题；没有就写"未做独立审查"。
