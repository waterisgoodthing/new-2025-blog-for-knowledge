# 设计文档：Batch 1 UI 壳层

## 1. 现状

### 首页

首页位于 `src/app/(home)/page.tsx`，由可配置、可拖拽的卡片组成，使用浅色、
玻璃质感和响应式移动端纵向布局。Batch 1 必须在这一视觉语言内增加轻入口，
不能将首页改成数据 Dashboard。

### 管理入口

`src/app/manage/page.tsx` 当前同时包含：

- 密码与 Passkey 登录。
- 已登录后的旧标签式管理面板。
- 内容、音乐、AI、设置、安全、审计、留言等真实管理功能。

这些既有能力不属于 Batch 1 重构范围，不能删除或迁移。

### 鉴权

`src/components/auth-gate.tsx` 使用 `useAdminAuth()` 检查管理员会话，未登录时跳转
`/manage`。因此 `/manage` 根页不能再被同一个 AuthGate 包裹，否则会形成重定向
自循环；新子页应在独立 route-group layout 中统一保护。

## 2. 路由设计

```text
src/app/manage/
  page.tsx                         # 完全保留现有登录与旧管理面板业务逻辑
  components/
    manage-sidebar.tsx
    manage-topbar.tsx
    manage-page-header.tsx
    manage-placeholder-page.tsx
  (workspace)/
    layout.tsx                     # AuthGate + 统一壳层
    dashboard/page.tsx
    drafts/page.tsx
    questions/page.tsx
    mistakes/page.tsx
    attachments/page.tsx
    subjects/page.tsx
    review/page.tsx
```

路由组 `(workspace)` 不进入 URL，最终路径仍是 `/manage/dashboard` 等。

`/manage` 根页保持现状，作为唯一登录入口和旧管理功能的兼容入口。Batch 1 不强制
重定向已登录用户，避免让旧标签页失去可达性。本批不得修改、删除、迁移、拆分、
重命名或重构 `src/app/manage/page.tsx` 的旧业务逻辑。

## 3. 视觉与交互纲领

- 视觉命题：延续现有浅蓝绿色、柔和玻璃材质与轻盈卡片语言，管理工作区更克制、
  更密集，但不引入第二套设计系统。
- 内容计划：首页只增加一个四入口 LearningSpaceCard；管理端由导航、当前页标题、
  静态 Dashboard 和诚实占位组成。
- 交互命题：只保留导航选中态、链接 hover/focus 与移动导航展开等壳层交互；
  不制造真实业务按钮、假数据动画或装饰性复杂动效。

## 4. 管理壳层

### ManageSidebar

职责：

- 展示 Dashboard、草稿、题库、错题、附件、科目、复习入口。
- 根据 pathname 标记当前项。
- 桌面端固定侧栏；窄屏使用可折叠或横向紧凑导航。
- 使用现有 `lucide-react` 图标，每个图标入口有可见文本或 accessible name。
- 提供“返回旧管理面板”链接到 `/manage`。

不承担数据请求、权限判断或业务计数。

### ManageTopbar

职责：

- 展示“学习管理空间”名称。
- 提供返回公开首页与旧管理面板的轻入口。
- 为未来账户区预留位置，但 Batch 1 不新增会话请求或退出逻辑。

### ManagePageHeader

统一页面标题、说明与可选 actions 区。占位页不提供会误导用户的可执行主按钮。

### ManagePlaceholderPage

统一显示“当前批次仅建立壳层；业务将在对应批次实现”，可列出后续批次，不显示
假数据、假成功或不可用表单。允许返回 Dashboard 或切换到其他占位页的导航链接，
但不得出现“新建题目”“上传附件”“开始审核”“完成复习”等真实动作。若文案需要
提及动作，必须明确标注“后续批次启用”。

## 5. 页面设计

### Dashboard

静态展示工作区导航和四个 MVP 状态占位：

- 待审核
- 待复习
- 科目与知识点
- 附件

数值显示 `—` 或“尚未接入”，不能伪造数量，也不能发 API 请求。

### 其他子页

统一 PageHeader 与 Placeholder：

| 页面 | 文案归属 |
| --- | --- |
| `/manage/drafts` | Batch 3 |
| `/manage/questions` | Batch 3 |
| `/manage/mistakes` | Batch 4 |
| `/manage/review` | Batch 4 |
| `/manage/attachments` | Batch 5 |
| `/manage/subjects` | Batch 2 |

## 6. 首页轻入口

新增路由专属 `LearningSpaceCard`，只包含四个入口：

| 入口 | 链接 | 状态 |
| --- | --- | --- |
| 待复习 | `/manage/review` | 静态 `—` |
| 待审核 | `/manage/drafts` | 静态 `—` |
| 进入学习空间 | `/manage/dashboard` | 导航 |
| 上传资料 | `/manage/attachments` | 导航 |

设计要求：

- 沿用浅蓝绿色、圆角、玻璃边框与轻阴影。
- 信息量限制为四个入口，不增加图表或真实统计。
- 移动端进入现有纵向卡片流；桌面端不遮挡现有卡片。
- 不修改站点配置 JSON，不为该卡新增可编辑配置合同。
- 不改变现有卡片排序、拖拽逻辑、布局算法或全局视觉 token。
- 除新增 `learning-space-card.tsx` 并在首页接入外，不重构任何现有首页卡片。
- 所有图标按钮或链接具有可访问名称。

具体位置应在实现时基于真实浏览器截图微调，但不得重排或重构其他首页卡片。

## 7. 权限与失败状态

- `/manage/*` 新子页由 route-group layout 统一使用 `AuthGate`。
- 未登录访问子页时跳转 `/manage`，不展示工作区骨架。
- `/manage` 登录页保持可访问，避免重定向循环。
- Batch 1 不修改后端权限，也不依赖 `AUTH_BYPASS`。
- Auth 检查期间沿用明确的“验证中”状态。
- 首页公开访问时不请求管理员 API，因此不会产生 401/403 噪音。

## 8. 数据与 API

无新数据表、API 客户端或真实请求。页面数据全部为明确标注的静态占位。

## 9. 验证设计

### 静态验证

- `npx tsc --noEmit`
- 检查路由文件、链接、accessible name 和未引入 API import。
- `git diff --check`

### 浏览器验收

- 未登录访问 `/`：轻入口可见，首页仍低密度。
- 未登录访问 `/manage/dashboard`：跳转 `/manage`，不出现工作区内容。
- 已登录访问所有新 `/manage/*`：统一 Sidebar、Topbar、PageHeader。
- 检查桌面与移动视口。
- 检查 `/blog`、`/notes`、`/mistakes` 仍可公开访问。

若 `tsc` 因已知 JSON `never[]` 等既存问题失败，记录第一条相关失败，并用本批文件
范围的静态检查与浏览器验收补充证据；不得把 `ignoreBuildErrors` 当作通过。
`validation.md` 必须明确记录第一条失败、是否涉及本批新增文件、本批新增文件是否
存在新的 TypeScript 错误，以及使用了哪些补充验证。
