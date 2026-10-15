# Handoff

## 本批完成内容

- 新增受 AuthGate 保护的 `/manage/*` 管理工作区 layout。
- 新增 ManageSidebar、ManageTopbar、ManagePageHeader 和统一占位组件。
- 新增 Dashboard 与 drafts、questions、mistakes、attachments、subjects、review 路由。
- 首页只新增并接入一个 LearningSpaceCard。
- 完成 TypeScript、生产构建、桌面/移动首页、登录/未登录管理壳层和公开页面回归。
- 登录态验收后已注销并禁用临时管理员。

## 修改文件

- `src/app/(home)/page.tsx`
- `src/app/(home)/learning-space-card.tsx`
- `src/app/manage/(workspace)/layout.tsx`
- `src/app/manage/(workspace)/dashboard/page.tsx`
- `src/app/manage/(workspace)/drafts/page.tsx`
- `src/app/manage/(workspace)/questions/page.tsx`
- `src/app/manage/(workspace)/mistakes/page.tsx`
- `src/app/manage/(workspace)/attachments/page.tsx`
- `src/app/manage/(workspace)/subjects/page.tsx`
- `src/app/manage/(workspace)/review/page.tsx`
- `src/app/manage/components/manage-sidebar.tsx`
- `src/app/manage/components/manage-topbar.tsx`
- `src/app/manage/components/manage-page-header.tsx`
- `src/app/manage/components/manage-placeholder-page.tsx`
- `docs/workflows/mvp-rebuild-batch-1-ui-shell/*`
- `docs/specs/mvp-rebuild/batch-1-ui-shell/checklist.md`
- `docs/specs/mvp-rebuild/batch-1-ui-shell/handoff.md`

## 未完成事项

- 所有真实业务能力保持未实现，将由 Batch 2 至 Batch 6 分批处理。

## 风险点

- `/manage` 旧面板体量较大且继续独立存在；本批有意保持零 diff。
- 新首页卡片不进入旧配置与拖拽系统，这是本批硬约束；未来如需可配置必须另立任务。
- 管理壳层仍与站点全局导航共存；本批已验证桌面安全间距与移动横向滚动。

## 下一批前置条件

Batch 1 checklist、audit、validation 和本 handoff 已完成。只有用户明确确认 Batch 1
通过后，才能建立 Batch 2 workflow；Batch 2 仍需独立 requirements、design、tasks
和用户审批。

## 用户确认

- [x] 用户已于 2026-07-02 确认 Batch 1 通过，可以进入下一批
