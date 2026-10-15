# 任务清单：Batch 1 UI 壳层与首页轻量改造

> 状态：用户已批准。执行时必须遵守 2026-07-02 增加的四条硬约束。

## P0-01 建立受保护的管理工作区壳层

- [x] 新增 route-group layout 与 ManageSidebar、ManageTopbar、ManagePageHeader。
- 来源需求：REQ-B1-02、REQ-B1-05
- 涉及文件：
  - `src/app/manage/(workspace)/layout.tsx`
  - `src/app/manage/components/manage-sidebar.tsx`
  - `src/app/manage/components/manage-topbar.tsx`
  - `src/app/manage/components/manage-page-header.tsx`
- 修改内容：使用现有 AuthGate 统一保护子路由；提供桌面与移动导航；保留 `/manage`
  根页作为登录与旧管理面板。
- 完成标准：新子页共享壳层，未登录跳转 `/manage`，没有重定向自循环。
- 验证方式：TypeScript、未登录/已登录浏览器验收、移动视口截图。
- 风险说明：不得将 AuthGate 放到 `/manage` 根页；不得修改、删除、迁移、拆分、
  重命名或重构 `src/app/manage/page.tsx` 旧业务逻辑。

## P0-02 建立 Dashboard 与统一占位页

- [x] 新增 Dashboard 和六个后续业务占位路由。
- 来源需求：REQ-B1-03、REQ-B1-04
- 涉及文件：
  - `src/app/manage/components/manage-placeholder-page.tsx`
  - `src/app/manage/(workspace)/dashboard/page.tsx`
  - `src/app/manage/(workspace)/drafts/page.tsx`
  - `src/app/manage/(workspace)/questions/page.tsx`
  - `src/app/manage/(workspace)/mistakes/page.tsx`
  - `src/app/manage/(workspace)/attachments/page.tsx`
  - `src/app/manage/(workspace)/subjects/page.tsx`
  - `src/app/manage/(workspace)/review/page.tsx`
- 修改内容：Dashboard 使用静态状态；其他页面显示统一、诚实的批次占位。
- 完成标准：全部路由可达、无死链、无真实业务请求或可误触操作。
- 验证方式：静态 import 检查与逐路由浏览器验收。
- 风险说明：不得提前实现 Batch 2 至 Batch 6；不得出现“新建题目”“上传附件”
  “开始审核”“完成复习”等真实动作按钮。提及动作必须标注“后续批次启用”。

## P0-03 增加首页轻入口

- [x] 新增 LearningSpaceCard 并接入现有首页。
- 来源需求：REQ-B1-01、REQ-B1-06
- 涉及文件：
  - `src/app/(home)/learning-space-card.tsx`
  - `src/app/(home)/page.tsx`
- 修改内容：加入待复习、待审核、进入学习空间、上传资料四个静态入口；复用现有
  视觉 token，不改配置 JSON、不请求管理员 API。
- 完成标准：首页仍低密度，桌面与移动端不遮挡；四个入口链接正确且可访问。
- 验证方式：TypeScript、API import 检查、桌面/移动浏览器截图。
- 风险说明：首页现有卡片使用可拖拽绝对布局；实现必须以真实截图调整位置，不能重排
  或重构其他卡片，不得改变旧卡片排序、拖拽逻辑、布局算法或全局视觉 token。

## P0-04 回归鉴权与公开页面

- [x] 已验证 `/manage` 旧入口、新子页登录保护、登录态壳层和公开读取边界。
- 来源需求：REQ-B1-05、REQ-B1-06
- 涉及文件：原则上不新增修改；若发现本批引入的问题，只修正 P0-01 至 P0-03 文件。
- 修改内容：验证未登录、已登录、AuthGate loading、旧管理入口和公开路由。
- 完成标准：无重定向循环；旧管理可用；`/blog`、`/notes`、`/mistakes` 仍公开。
- 验证方式：真实浏览器逐路径验收与控制台检查。
- 风险说明：现有 `/manage` 真实功能较多，不能把既存问题误归因于本批。

## P0-05 验证、审查与移交

- [x] 创建 `audit.md` 与 `validation.md`。
- [x] 更新 Batch 1 `checklist.md`。
- [x] 填写 Batch 1 `handoff.md`，但不代替用户确认。
- [x] 核对本轮 diff 只包含本批允许文件；既存未跟踪文档状态已区分记录。
- 来源需求：全部
- 涉及文件：
  - `docs/workflows/mvp-rebuild-batch-1-ui-shell/audit.md`
  - `docs/workflows/mvp-rebuild-batch-1-ui-shell/validation.md`
  - `docs/specs/mvp-rebuild/batch-1-ui-shell/checklist.md`
  - `docs/specs/mvp-rebuild/batch-1-ui-shell/handoff.md`
- 修改内容：记录 TypeScript、浏览器、权限、响应式、公开回归、失败项和风险。
- 完成标准：Batch 1 进入“待用户验收”，不自动进入 Batch 2。
- 验证方式：`npx tsc --noEmit`、浏览器验收、`rg`、`git diff --check`、文件清单。
- 风险说明：若 TypeScript 因既存问题失败，必须记录第一条失败、是否涉及本批新增
  文件、本批新增文件是否有新错误及补充验证，不能伪称通过。

## 执行顺序

严格按 P0-01 → P0-02 → P0-03 → P0-04 → P0-05 执行。每完成一项立即更新本文件，
不得最后批量回填。

## 审批记录

- [x] 用户已于 2026-07-02 明确批准执行本任务清单，并附加四条硬约束。
