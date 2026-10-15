# 任务清单：Batch 6 AI / OCR 占位与依赖隔离

> 状态：用户已批准，按 P0-01 至 P0-09 顺序执行。

## P0-01 基线与禁止项审计

- [x] 检查现有 AI/OCR/Jobs/Settings 相关代码、路由、页面与导航入口。
- [x] 记录 Batch 3-5 主流程当前是否发出 AI/OCR 请求。
- 来源需求：REQ-B6-01 至 REQ-B6-06
- 涉及文件：本 workflow `validation.md`、现有 manage/AI/OCR 相关路径只读检查。
- 修改内容：只读审计，不实现。
- 完成标准：列出可复用/必须避开的旧 AI 入口，确认不得新增后端合同。
- 验证方式：`rg`、route scan、目录检查。
- 风险说明：若发现现有主流程已经依赖 AI/OCR，先记录并申请范围调整。
- 完成记录（2026-07-03）：确认旧 `/api/ai*`、旧 `/manage` AI tab 与旧 Note `ai_metadata`
  属于既有系统；Batch 3-5 新 workspace 主流程未 import `src/lib/api/ai*`，未出现 OCR/Capture/Jobs
  API 调用。Batch 6 不扩大旧 AI 能力访问面。

## P0-02 实现静态占位组件

- [x] 新增或复用专属占位组件，覆盖“暂未启用”的统一文案。
- 来源需求：REQ-B6-01、REQ-B6-02、REQ-B6-03
- 涉及文件：`src/app/manage/(workspace)/ai`、`jobs`、`settings` 相关组件。
- 修改内容：静态结构、禁用态说明、无请求逻辑。
- 完成标准：组件不 import `src/lib/api/ai*`、OCR、jobs 或 settings 写入 client。
- 验证方式：TSC、静态搜索。
- 风险说明：不得抽象成完整 AI/OCR framework。
- 完成记录（2026-07-03）：新增 `FutureCapabilityPage` 静态占位组件；无 API import/fetch，
  `npx tsc --noEmit` 通过。

## P0-03 新增 `/manage/ai` 占位页

- [x] 页面展示模型配置、Prompt 模板、调用记录三类占位结构。
- 来源需求：REQ-B6-01、REQ-B6-06
- 涉及文件：`src/app/manage/(workspace)/ai/page.tsx`。
- 修改内容：管理端静态占位页面。
- 完成标准：可访问、无请求、无虚构记录、文案明确“第一版暂未启用”。
- 验证方式：TSC、build、browser。
- 风险说明：不得连接旧真实 AI 操作入口。
- 完成记录（2026-07-03）：新增静态 `/manage/ai`；不连接旧 AI tab 或 API。

## P0-04 新增 `/manage/jobs` 占位页

- [x] 页面展示任务队列、任务类型、重试/错误观察占位。
- 来源需求：REQ-B6-02、REQ-B6-06
- 涉及文件：`src/app/manage/(workspace)/jobs/page.tsx`。
- 修改内容：管理端静态占位页面。
- 完成标准：可访问、无轮询、无 job API、无假成功状态。
- 验证方式：TSC、build、browser。
- 风险说明：不得新增 job table、worker 或轮询。
- 完成记录（2026-07-03）：新增静态 `/manage/jobs`；无轮询、无 job API、无 worker。

## P0-05 新增 `/manage/settings` 占位页

- [x] 页面展示 AI、OCR、Upload、Jobs、Privacy 设置分组占位。
- 来源需求：REQ-B6-03、REQ-B6-06
- 涉及文件：`src/app/manage/(workspace)/settings/page.tsx`。
- 修改内容：管理端静态占位页面。
- 完成标准：可访问、无保存按钮、无 settings API 写请求。
- 验证方式：TSC、build、browser。
- 风险说明：不得新增设置后端合同或假保存 toast。
- 完成记录（2026-07-03）：新增静态 `/manage/settings`；无保存按钮、无 settings API 写请求。

## P0-06 附件详情 OCR 未启用状态

- [x] 在附件详情页增加 OCR 第一版暂未启用状态卡片。
- 来源需求：REQ-B6-04、REQ-B6-05
- 涉及文件：`src/app/manage/(workspace)/attachments/components/attachment-detail.tsx`。
- 修改内容：只展示状态与说明，不加触发按钮。
- 完成标准：附件详情明确不会自动 OCR，不发 OCR 请求。
- 验证方式：TSC、browser、静态搜索。
- 风险说明：不得出现“开始 OCR”“重新识别”等可操作控件。
- 完成记录（2026-07-03）：附件详情新增 OCR 未启用状态卡片，无按钮、无请求；静态搜索与
  `npx tsc --noEmit` 通过。

## P0-07 导航与 dashboard 入口

- [x] 将 AI、Jobs、Settings 加入管理工作区导航；必要时更新 dashboard 入口说明。
- 来源需求：REQ-B6-01、REQ-B6-02、REQ-B6-03
- 涉及文件：`manage-sidebar.tsx`、`dashboard/page.tsx`。
- 修改内容：仅添加入口和占位状态，不展示虚构统计。
- 完成标准：导航可达，dashboard 文案不声称已启用。
- 验证方式：TSC、browser。
- 风险说明：不得影响既有 Batch 2-5 管理入口。
- 完成记录（2026-07-03）：管理侧栏新增 AI/任务/设置入口，dashboard 新增 Batch 6 占位入口；
  无 API import/fetch，`npx tsc --noEmit` 通过。

## P0-08 主流程无 AI/OCR 依赖验证

- [x] 静态和浏览器验证题目、错题、附件、复习主流程不发 AI/OCR 请求。
- 来源需求：REQ-B6-05、REQ-B6-06
- 涉及文件：`validation.md` 与必要测试/检查记录。
- 修改内容：验证和记录，不新增后端。
- 完成标准：无新增 AI/OCR 表、migration、router、service、API client 请求；占位页无真实请求。
- 验证方式：`rg`、`npx tsc --noEmit`、`npm run build`、browser console/network。
- 风险说明：若发现旧路径仍会发真实 AI 请求，记录为既有系统，不纳入 Batch 6 新能力。
- 完成记录（2026-07-03）：静态搜索确认无新增 AI/OCR/Capture/Jobs/Settings 后端合同和迁移；
  新占位页无 API import/fetch；`npm run build` 通过并包含 `/manage/ai`、`/manage/jobs`、
  `/manage/settings`。旧 `/api/ai*` 命中记录为既有系统，不纳入 Batch 6 新能力。

## P0-09 审查、验证与移交

- [x] 创建 audit/validation，更新 checklist，填写 handoff，核对范围。
- 来源需求：全部
- 涉及文件：本 workflow 文档与 Batch 6 spec checklist/handoff。
- 修改内容：记录占位页面、未启用能力、主流程无依赖、权限证据、风险和后置项。
- 完成标准：Batch 6 仅进入等待用户验收，不自动进入 Batch 7。
- 验证方式：全套证据与 `git diff --check`。
- 风险说明：任何真实 AI/OCR 调用、新表/API/依赖或误导性状态都阻塞 Batch 7。
- 完成记录（2026-07-03）：补齐 `audit.md`、`validation.md` P0-09、Batch 6 checklist 与
  handoff；`git diff --check`、`npx tsc --noEmit`、`npm run build` 通过。浏览器匿名访问确认
  AuthGate 拦截到 `/manage`；因当前无管理员会话，登录态视觉验收留给用户验收阶段。

## 执行顺序

严格按 P0-01 → P0-09；每完成一项立即更新本文件。

## 审批记录

- [x] 用户已于 2026-07-03 明确批准执行 Batch 6 tasks。
