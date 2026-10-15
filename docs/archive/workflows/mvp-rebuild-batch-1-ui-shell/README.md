# MVP Rebuild Batch 1：UI 壳层与首页轻量改造

## 任务目标

在不接真实业务数据、不改变后端合同的前提下，建立公开首页轻入口与统一的
`/manage/*` 管理工作区壳层。

## 涉及领域

- home：增加低密度学习入口
- manage：新增管理工作区壳层与占位子页
- auth：复用现有 `AuthGate`，不改变后端鉴权
- shared UI：只在必要时复用既有 Card、样式 token 与图标

## 当前状态

**已验收完成。**

用户已于 2026-07-02 批准 [`tasks.md`](./tasks.md)，并增加四条硬约束：旧
`/manage/page.tsx` 业务逻辑不可重构；首页只新增 `LearningSpaceCard`；占位页不得
提供真实动作；TypeScript 失败必须按规定记录。

实现、TypeScript、构建、首页响应式、登录/未登录保护、管理壳层与公开回归均已通过。
临时管理员仅用于本地验收，验收后已注销并禁用。

用户已于 2026-07-02 确认 Batch 1 通过。Batch 2 可以进入独立 workflow 的规划与
tasks 审批阶段，但尚未获准实施。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)

执行完成后补充：

- `audit.md`
- `validation.md`
- Batch 1 `checklist.md` 与 `handoff.md`

## 关键约束

- `/manage` 当前是登录入口和旧管理面板，必须保留。
- 不得删除、迁移、拆分、重命名或重构 `src/app/manage/page.tsx` 旧业务逻辑。
- 新 `/manage/*` 工作区子路由使用统一受保护 layout。
- 首页入口只使用静态状态，不调用复习、草稿或附件 API。
- 首页只新增并接入 `LearningSpaceCard`，不改变旧卡片系统、配置、顺序或布局算法。
- 占位页只允许导航，不提供任何真实业务动作按钮。
- 不修改后端、数据库、依赖、配置或后续批次业务。
