# Phase 6 启动 Prompt — 给 DeepSeek

你是本仓库的前端实施智能体，任务是完成 **Phase 6：首页顶部导航接入**。只做 Phase 6，做完停下汇报。

## 0. 开工前必读

1. 先读 `AGENTS.md`（仓库强制规则）。
2. 本项目的 Next.js 版本有破坏性变更，写代码前查 `node_modules/next/dist/docs/` 中相关指南。
3. 运行 `git status --short`。Phase 1–5 均已提交并推送（最新 `9435a54`）。若开工时有未提交改动，视为用户改动，**不要回滚、重排、格式化或覆盖**。

## 1. 现场事实（已核实，优先于文档中的描述）

- 仓库：`/Users/limengyang/2025-blog-public`，分支 `refactor/baseline`
- 基线：`npx tsc --noEmit` 0 errors；`npx vitest run` 79 files / 668 passed；`npm run build` 成功
- 前端：Next.js 16 + React 19 + Tailwind 4 + `motion` + `lucide-react`；测试 Vitest + `@testing-library/react`
- **当前首页导航现状**（`src/layout/index.tsx`）：
  - 首页（`isHome === true`）：不渲染 PublicTopNav，只渲染 NavCard（在 main 内）
  - 内页（`isInnerPage === true`）：渲染 PublicTopNav（Phase 5 做的）
  - manage 路由（`isManageRoute === true`）：AdminSidebar（Phase 3 做的）
- **NavCard**（`src/components/nav-card.tsx`）行为：
  - `form='full'`（pathname === '/'）：渲染完整的左侧卡片式导航，含头像、站点标题、链接列表
  - `form='mini'`（pathname.startsWith('/write')）：渲染小头像+首页按钮
  - `form='icons'`（其他路径）：**直接 return null**，不渲染任何东西
  - 移动端（maxSM）：强制 `form='icons'`，等于不渲染
  - 所以内页的 NavCard 本来就是不渲染的，Phase 5 没有打破它
- **PublicTopNav**（`src/components/ui-v2/PublicTopNav.tsx`）：
  - 已有 `position: 'fixed' | 'sticky'` prop，内页用 `position='sticky'`
  - 首页用 `position='fixed'` 更合适（首页有全屏卡片布局，sticky 会在内容上方留出 72px 空白）
  - props：`entries`、`currentPath`、`brandLabel`、`position`
- Token：只消费，不改色值；不要用 `--radius-*`/`--font-*`/`--shadow-*` 自定义同名变量

## 2. 任务：首页加入 PublicTopNav

**目标**：首页顶部也出现玻璃导航条，视觉上和内页保持一致，让用户从首页到内页导航条不跳变。

**具体改动**：

### `src/layout/index.tsx`

1. 把 `isInnerPage` 的条件扩展到首页：原来 `!isManageRoute` 的路由都渲染 PublicTopNav
2. 首页用 `position='fixed'`，内页用 `position='sticky'`（或者统一用 `position='fixed'`，取决于首页卡片布局是否被遮挡——你需要在浏览器里核查）
3. 管理员入口逻辑不变（`isAdmin` 追加）

**首页布局冲突检查**：首页是绝对定位的卡片式浮动布局（`HomeDraggableLayer`，卡片用 `position: absolute`），`fixed` 导航条会叠在卡片上方。需要检查：
- 导航条 z-index（当前 `z-sticky` = 1100）是否高于首页卡片的 z-index
- 首页卡片的顶部间距是否需要调整，避免被导航条遮挡
- 如果首页卡片从顶部开始布局，需要给最顶部的卡片加一个 `top` 偏移或者用 `pt-18`（72px = 导航条高度）

### NavCard 的处理

NavCard 在首页（`form='full'`）渲染左侧完整导航卡片，现在首页又有了顶部 PublicTopNav，两者共存是否合理：
- **保留 NavCard**：两套导航并存，NavCard 是左侧卡片，PublicTopNav 是顶部条，功能有重叠但位置不同，视觉上可以接受
- **隐藏 NavCard 的链接区域**：保留 NavCard 的头像+标题卡片部分，隐藏导航链接（因为顶部已经有了）
- **完全隐藏 NavCard**：首页只用 PublicTopNav

**推荐**：先尝试两者并存，在浏览器里看效果。如果视觉上混乱（两套导航目的地完全重复），则把 NavCard 的 `form='full'` 链接区域改成只显示头像+标题+描述，不显示导航链接。具体做法在浏览器核查后决定，在 Deviations 里说明。

## 3. 测试

更新 `src/layout/layout.test.tsx`（Phase 5 新建的）：
- 首页渲染 PublicTopNav（新增断言）
- 首页 position prop 正确（fixed）
- 内页 position prop 正确（sticky）

## 4. 不允许做的事

- 改后端、API 合约、鉴权逻辑
- 改 `tokens.css` 色值
- 改 `globals.css` 的 cursor 规则
- 新增依赖
- 改 `NavCard` 的核心定位/拖拽逻辑（只允许改显示条件或 `form='full'` 时的链接区域）
- commit、push、部署

## 5. 验收

| 检查 | 要求 |
|---|---|
| `npx tsc --noEmit` | 0 errors |
| `npx vitest run` | 全部通过，数量 ≥ 668 + 新增 |
| `npm run build` | 成功，路由表与基线一致 |
| `git diff --check` | clean |
| 浏览器（真实 Chromium） | 首页顶部有玻璃导航条；滚动后导航条状态变化；首页卡片不被导航条遮挡；从首页点进内页，导航条连续不跳变；截图各情况 |

截图放 `docs/current/workflows/visual-system-consolidation/assets/phase6-*.png`。

## 6. 汇报格式

先给结论（PASS / PARTIAL / FAIL / BLOCKED / NOT_VERIFIED），然后：

- **Changes**：新增/修改文件
- **Verification**：每条命令和结果
- **Browser evidence**：截图，说明 NavCard 和 PublicTopNav 共存的处理方式
- **Deviations**：与上述描述不一致的地方及原因
- **Remaining / NOT_VERIFIED**：未完成项

如果用了独立子代理审查，写明审查者 ID 和它报的问题；没有就写"未做独立审查"。
