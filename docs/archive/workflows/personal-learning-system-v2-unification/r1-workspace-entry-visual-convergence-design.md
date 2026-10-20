# R1 管理工作区入口与视觉收敛设计

状态：`APPROVED / EXECUTED / CLOSED`

## 1. 目标

在不改变数据权威、权限模型和领域编辑流程的前提下，将管理员日常入口收敛到现有 `/manage/dashboard`，并在现有蓝白玻璃语言上统一管理工作区的层级、状态和快捷入口。

影响架构线：

- Frontend / original blog：仅调整指向管理工作区的入口与兼容表达。
- Personal learning frontend：`src/app/manage/(workspace)/` 与其共享管理组件。
- Backend：R1 默认不修改；只有现有 Dashboard 契约不足且用户重新批准时才允许扩展。

## 2. 唯一入口决策

R1 延续已完成的 I4 决策：

```text
/manage             管理员登录入口
/manage/dashboard   canonical workspace
```

公开读取保持：

```text
/blog
/blog/[id]
/notes
/notes/[id]
/mistakes
```

R1 不把公开页面整体加入 `AuthGate`。公开页面中的管理员操作继续按登录态条件展示，真实安全边界仍是后端 `get_current_admin`。

当前未跟踪的 `/workspace` 视为原型，而不是第三个正式入口。其最终处理必须在 R1-02 形成明确决策：

1. 不纳入版本控制；或
2. 仅作为到 `/manage/dashboard` 的兼容重定向。

不得保留一套拥有独立数据请求、导航和子路由的平行工作区。

### R1-02 实际决策

2026-07-30 采用最保守方案：

- `src/app/workspace/page.tsx` 保持用户现有未跟踪原型状态。
- R1 不修改、删除、移动或提交该文件。
- R1 不创建 `/workspace/create`、`/workspace/capture` 或 `/workspace/review`。
- R1 不为 `/workspace` 增加重定向；正式入口继续是 `/manage/dashboard`。
- 后续若用户希望保留 `/workspace` 兼容 URL，必须另行批准一项窄范围重定向任务。

## 3. 视觉基线

采用“蓝白、克制玻璃、内容优先”的现有方向：

- 管理容器允许半透明背景、`backdrop-blur` 和轻量阴影。
- 卡片 hover 不默认上移 4px；只有可点击卡片才允许轻微反馈。
- 不把 `blur(20px) saturate(180%)` 批量应用到所有页面。
- 通过管理工作区共享 token 或组件类收敛重复样式，不对公开页面做全局机械替换。
- 支持 `prefers-reduced-motion`，保留清晰 focus ring、文字对比度和移动端可读性。

首批允许收敛的组件：

```text
WorkspaceShell
WorkspaceSection
WorkspaceCard
WorkspaceAction
WorkspaceState
WorkspaceMetric
```

组件名称是设计占位，实施时优先复用现有组件和类，不要求为名称而新增抽象。

## 4. Dashboard 信息结构

Dashboard 继续作为摘要编排器，不拥有其他领域的写入逻辑：

```text
今日与欢迎语
├── 待复习
├── 待处理草稿/采集
├── 最近内容
└── 系统/存储局部状态

快速行动
├── 写笔记
├── 写博客
├── 录错题/采集
└── 开始复习
```

每个行动必须落到已存在且受保护的真实路由。未实现能力必须显示为“后续”或不展示，禁止链接到不存在的 `/workspace/*`。

## 5. 创建入口策略

R1 只统一“从哪里开始”，不统一三类编辑器的内部实现。

实施前先建立能力矩阵：

| 内容类型 | 当前创建/编辑能力 | R1 允许动作 |
|---|---|---|
| note | Note API、文件夹、标签、版本、图片 | 为 Dashboard 提供真实入口；不删除实现 |
| blog | Note API、封面、图片、发布字段 | 为 Dashboard 提供真实入口；不做数据迁移 |
| mistake | Note mistake 字段、图片、AI/人工流程、复习关系 | 指向当前安全入口；不降级为普通 Markdown |

如果当前规范入口只能落到 `/manage/dashboard` 而不能直接进入创建流程，R1 应先增加可解释的 action surface，再考虑后续编辑器适配任务。不得以空白占位页冒充统一编辑器。

## 6. 路由兼容与退役

R1 内：

- 允许盘点和更新站内入口。
- 允许为明确批准的兼容路径增加重定向测试。
- 禁止删除 `src/app/write/`、`write-note/`、`write-mistake/`。
- 禁止改动数据 authority、执行 migration 或删除静态内容。

后续退役必须另建任务组，并具备：

1. 全仓调用方清单。
2. 三类编辑能力等价矩阵。
3. 深链、书签和回退策略。
4. 匿名、管理员、失效会话浏览器证据。
5. 独立观察窗口和用户批准。

## 7. 交付边界

R1 可交付：

- 入口/路由矩阵。
- 管理工作区视觉 token 与局部组件收敛。
- Dashboard 真实快捷行动和状态表达。
- 站内管理员入口统一。
- 响应式、权限、可访问性和构建验证。

R1 不交付：

- 博客迁移、schema 或数据库写入。
- 编辑器内核统一。
- 旧路由删除。
- GitHub sync 删除。
- AUTH_BYPASS、JWT、Passkey 或注册重构。
- S3、Redis、队列、容器化或部署迁移。
- 生产部署、推送或 authority switch。

## 8. 停止条件

出现任一条件立即停止并记录为 `BLOCKED`：

- 需要改变公开/管理权限边界。
- 需要新增或修改 backend contract、schema 或 migration。
- 现有三类创建能力无法在不丢字段的情况下接入。
- 公开页面出现登录要求或管理员 API 的 401/403 噪音。
- 需要删除用户未明确批准的未跟踪原型或旧路由。
- TypeScript、构建或浏览器验证出现无法归因的新回归。
