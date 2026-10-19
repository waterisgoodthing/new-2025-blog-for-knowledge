# Phase 5 启动 Prompt — 给 DeepSeek

你是本仓库的前端实施智能体，任务是完成 **Phase 5：公开端导航切换 + F4 会话状态优化**。只做 Phase 5，做完停下汇报。

## 0. 开工前必读

1. 先读 `AGENTS.md`（仓库强制规则），再读：
   - `docs/archive/workflows/public-session-state-optimization/design.md`（F4 的设计合同，权威来源）
   - `docs/archive/workflows/public-session-state-optimization/requirements.md`（F4 需求）
   - `docs/current/ui-technical-specification/04-execution/task-registry.md`
   - `docs/current/workflows/visual-system-consolidation/design.md` 第 3 节（公开端导航架构）
2. 本项目的 Next.js 版本有破坏性变更，写代码前查 `node_modules/next/dist/docs/` 中相关指南。
3. 运行 `git status --short`。Phase 1–4 均已提交并推送（最新 `a966b17`）。若开工时有未提交改动，视为用户改动，**不要回滚、重排、格式化或覆盖**。

## 1. 现场事实（已核实，优先于文档中的描述）

- 仓库：`/Users/limengyang/2025-blog-public`，分支 `refactor/baseline`
- 基线：`npx tsc --noEmit` 0 errors；`npx vitest run` 78 files / 657 passed；`npm run build` 成功
- **F4 前端基础已全部到位**，不需要重写：
  - `src/hooks/use-admin-auth.ts`：已有 `mode: 'optional' | 'strict'`，`OPTIONAL_ADMIN_SESSION_KEY`，`STRICT_ADMIN_SESSION_KEY`
  - `src/lib/api/auth.ts`：已有 `getSessionState()` → `GET /api/auth/session-state`
  - 后端 `backend/app/routers/auth.py:528`：`/api/auth/session-state` 端点已实现，返回 `{ authenticated, is_admin }`
- **公开页消费者现状**（大部分已是 optional，下面是完整清单，需逐一确认）：
  - `src/components/auth-gate.tsx`：`mode: 'strict'` ← 保留，不动
  - `src/components/mobile-nav.tsx`：`mode: 'optional'` ✓
  - `src/app/snippets/page.tsx`：`mode: 'optional'` ✓
  - `src/app/(home)/learning-space-card.tsx`：`mode: 'optional'` ✓
  - `src/app/bloggers/page.tsx`：`mode: 'optional'` ✓
  - `src/app/projects/page.tsx`：`mode: 'optional'` ✓
  - `src/app/pictures/page.tsx`：`mode: 'optional'` ✓
  - `src/app/mistakes/page.tsx`：`mode: 'optional'` ✓
  - `src/app/about/about-content.tsx`：`mode: 'optional'` ✓
  - `src/app/blog/[id]/blog-detail-content.tsx`：`mode: 'optional'` ✓
  - `src/app/blog/page.tsx`：`mode: 'optional'` ✓
  - `src/app/notes/page.tsx`：`mode: 'optional'` ✓
  - `src/app/notes/[id]/note-detail-content.tsx`：`mode: 'optional'` ✓
  - `src/app/share/page.tsx`：`mode: 'optional'` ✓
  - `vertical-nav.tsx`、`nav-card.tsx` 中是否有 `useAdminAuth` 调用，需你在开工后核查
- **现有公开端导航挂载点**（`src/layout/index.tsx`）：
  - 桌面内页（`!maxSM && isInnerPage`）：`<VerticalNav />`
  - 首页（所有宽度）：`<NavCard />`（挂在 main 内）
  - 移动端（`maxSM && !isWrite`）：`<MobileNav />`
- `src/components/ui-v2/PublicTopNav.tsx` 已完成（Phase 3 产物）：props 是 `entries`、`currentPath`、`brandLabel`，纯展示组件，不自己做 session 探测
- Token：只消费 `--nav-glass-bg` / `--nav-blur` / `--nav-active-bg` 等，不改色值
- **不要用** `--radius-*` / `--font-*` / `--shadow-*` 自定义同名变量（Tailwind 4 命名空间冲突）

## 2. 任务

### F4-PSS 会话状态确认（先做，低风险，纯核查）

核查所有公开页 `useAdminAuth` 消费者，确认没有遗漏的 `mode: 'strict'`（除 AuthGate 外）。

具体做：
- 运行 `grep -rn "useAdminAuth" src --include="*.tsx" --include="*.ts" | grep -v manage | grep -v test | grep -v "ui-v2"` 得到完整清单
- 对照上面的现场事实，找出任何还在用默认 `mode: 'strict'` 的公开消费者（`mode` 未写等于 `strict`，因为默认值是 `strict`）
- 把发现的消费者切换到 `mode: 'optional'`
- 更新对应的测试（如果有），确认测试仍然通过

验证：`npx tsc --noEmit` + `npx vitest run`（全部通过）

### PUB-NAV 公开端导航切换（主体工作）

**目标**：`src/layout/index.tsx` 里的 `VerticalNav`（桌面内页）和 `MobileNav`（移动端）由 `PublicTopNav` + `MobileDrawer`（基于 Phase 2/3 的 `Uiv2Drawer`）取代。首页 `NavCard` 的处理方式见下文。

**管理员入口处理**：
- `PublicTopNav` 是纯展示组件，不自己探测 session。调用方（`layout/index.tsx`）用 `useAdminAuth({ mode: 'optional' })` 获取 `isAdmin`，再决定要不要往 `entries` 里加管理员入口
- 当 `isAdmin === true` 时，在 `entries` 里追加一个"管理后台"入口（指向 `/manage`）；`isAdmin === false` 或 loading 时不加
- 这样匿名访客看不到管理入口，已登录管理员能看到，且零 401 噪音

**首页 NavCard**：
- NavCard（`src/components/nav-card.tsx`）在首页显示，在内页变成 mini 或 icons 形态，逻辑比较复杂
- Phase 5 **不改 NavCard 的显示逻辑**，只确保它和 PublicTopNav 不同时出现在同一视口内
- 具体：内页（`isInnerPage === true`）加 PublicTopNav，首页（`isHome === true`）保留 NavCard，不重叠
- 如果首页也需要玻璃顶栏，那是 Phase 6 的事，本阶段只做内页切换

**移动端**：
- 把 `MobileNav`（底部 tab bar）替换成一个汉堡按钮触发的 `MobileDrawer`（基于 Phase 3 的 `Uiv2MobileDrawer`）
- 移动端的 `main` 不再需要 `pb-14`（底部导航消失了）
- 路由切换后 Drawer 自动关闭

**执行顺序**：
1. 先写测试（`src/layout/layout.test.tsx` 或同目录）：内页有 PublicTopNav、首页无 PublicTopNav、移动端 Drawer 开关、管理员入口在 `isAdmin=true` 时出现
2. 再改 `src/layout/index.tsx`
3. 验证现有测试全部通过

**保留文件**：`vertical-nav.tsx`、`mobile-nav.tsx`、`nav-card.tsx` 文件本身保留，只是不再从 layout 渲染 VerticalNav 和 MobileNav（NavCard 继续渲染）。这些组件的现有测试保留并继续通过。

## 3. 权限边界（必须遵守）

- `AuthGate` 只用 `mode: 'strict'`，不动
- 不改后端、API 合约、`get_current_admin`、`AUTH_BYPASS`、CORS
- 不改 `tokens.css` 色值
- 不改 `globals.css` 的 cursor 规则
- 不新增依赖
- 不删除现有路由，不重命名路由
- 不 commit、不 push、不部署

## 4. 验收

| 检查 | 要求 |
|---|---|
| `npx tsc --noEmit` | 0 errors |
| `npx vitest run` | 全部通过，数量 ≥ 657 + 新增 |
| `npm run build` | 成功，路由表与基线一致 |
| `git diff --check` | clean |
| 浏览器（真实 Chromium） | 内页（/blog, /notes）顶部有玻璃导航条；首页无顶栏冲突；移动端 390px 有汉堡按钮，点击后 Drawer 从右侧滑入；管理员登录后刷新，导航条出现"管理后台"入口；匿名时无此入口；截图各情况 |
| 网络请求 | 匿名访问 `/blog`、`/notes`、`/mistakes` 时，Network 里无 `GET /api/auth/me` 的 401 请求（只有 `/api/auth/session-state` 的 200） |

截图放 `docs/current/workflows/visual-system-consolidation/assets/phase5-*.png`。

## 5. 汇报格式

先给结论（PASS / PARTIAL / FAIL / BLOCKED / NOT_VERIFIED），然后：

- **Changes**：按任务列出新增/修改文件
- **Verification**：每条命令和结果
- **Browser evidence**：截图和网络请求日志
- **Deviations**：与上述描述不一致的地方及原因
- **Remaining / NOT_VERIFIED**：未完成项；iOS/Android 真机做了写 VERIFIED，没做写 NOT_VERIFIED

如果用了独立子代理审查，写明审查者 ID 和它报的问题；没有就写"未做独立审查"。
