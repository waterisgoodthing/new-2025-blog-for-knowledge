# Batch 1：UI 壳层与首页轻量改造

## 目标

建立清晰的 UI 分层：公开首页保持青春柔和、低密度；`/manage` 成为高密度管理工作台。

## 背景

首页承担公开展示和轻入口职责，不应被改造成后台 Dashboard。管理操作需要统一、
受保护且可扩展的壳层。

## 任务范围

1. 保留首页浅蓝绿色、玻璃卡片和低密度风格。
2. 首页只增加“待复习”“待审核”“进入学习空间”“上传资料”轻入口。
3. 新增 `/manage` 壳层。
4. 新增或整理 `ManageSidebar`、`ManageTopbar`、`ManagePageHeader`。
5. 新增 `/manage/dashboard` 占位页。
6. 为其他规划中的 `/manage` 子页面提供一致占位。
7. 管理入口和占位页遵守既有管理员访问保护。

## 允许修改范围

- 本批对应 workflow 文档。
- 首页路由及其现有组件。
- `/manage` 路由、路由专属组件与必要的共享管理壳组件。
- 导航配置与直接相关的前端测试。
- 本批 checklist、handoff 和验证材料。

具体文件须在本批 workflow 的 tasks 中列明并获批。

## 禁止事项

- 不接真实业务数据。
- 不做 AI、OCR 或完整表单逻辑。
- 不做复杂统计图表。
- 不改数据库、后端模型或 API。
- 不把首页改成 Dashboard。
- 不破坏公开博客、笔记、错题读取。

## 涉及页面

- `/`
- `/manage`
- `/manage/dashboard`
- `/manage/drafts`
- `/manage/questions`
- `/manage/mistakes`
- `/manage/attachments`
- `/manage/subjects`
- `/manage/review`

## 涉及数据表

无。本批只能使用静态占位状态，不引入真实数据合同。

## 验收标准

1. 首页没有变成 Dashboard。
2. 首页只展示约定的轻量状态与入口。
3. `/manage` 有统一 Sidebar、Topbar 和 PageHeader。
4. 可以从首页进入受保护的 `/manage`。
5. `/manage` 子页面占位视觉一致。
6. 公共页面访问和管理员保护边界未被破坏。
7. TypeScript 检查及相关浏览器验收有记录。

## 非目标

真实 CRUD、业务统计、数据库改造、AI/OCR、最终表单和完整响应式细节收口。

## 完成后 handoff 要求

记录新增路由和组件、浏览器截图或验收路径、权限行为、未完成占位、风险和 Batch 2
前置条件，并等待用户确认。
