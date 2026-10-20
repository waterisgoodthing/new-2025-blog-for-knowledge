# Batch 6 审查记录

## 审查结论

Batch 6 已完成实现侧收口，当前状态为：**等待用户验收，不自动进入 Batch 7**。

本批新增的 AI、Jobs、Settings 页面均为管理工作区内的静态占位；附件详情仅增加 OCR
第一版暂未启用说明。未发现新增真实 AI/OCR 后端合同、数据表、迁移、队列、worker、外部模型配置或
可触发真实调用的按钮。

## 影响范围

- manage：`/manage/ai`、`/manage/jobs`、`/manage/settings`
- manage navigation：`src/app/manage/components/manage-sidebar.tsx`
- manage dashboard：`src/app/manage/(workspace)/dashboard/page.tsx`
- attachments：`src/app/manage/(workspace)/attachments/components/attachment-detail.tsx`
- workflow/spec：Batch 6 workflow 与 specs 文档

## 权限边界

- 新页面位于 `/manage/(workspace)` 下，继承 `src/app/manage/(workspace)/layout.tsx` 的 `AuthGate`。
- 匿名浏览器访问 `/manage/ai`、`/manage/jobs`、`/manage/settings` 会被拦到 `/manage` 登录入口。
- 公开页面未新增 AI/OCR 管理入口。
- 本次审查未使用 `AUTH_BYPASS` 作为权限通过证据。

## 无副作用检查

- `FutureCapabilityPage` 只接收静态 props，不 import `src/lib/api/*`。
- `/manage/ai`、`/manage/jobs`、`/manage/settings` 页面无 `fetch`、无 `apiFetch`、无轮询。
- 附件详情 OCR 区域只展示文案和标签，不包含“开始 OCR”“重新识别”等触发控件。
- 静态搜索未发现新增 `ai_runs`、`ocr_jobs`、`capture_jobs`、AI/OCR/Capture/Jobs/Settings 管理后端合同。

## 验证证据

- `git diff --check`：通过。
- `npx tsc --noEmit`：通过。
- `npm run build`：通过；route table 包含：
  - `/manage/ai`
  - `/manage/jobs`
  - `/manage/settings`
- 浏览器只读访问：
  - 备用端口 `3025` 的匿名浏览器访问受 `AuthGate` 拦截到 `/manage` 登录入口。
  - 因当前浏览器无管理员会话，未完成登录态下的占位页视觉验收。

## 非阻塞警告

- 构建输出提示 `baseline-browser-mapping` 数据超过两个月。
- 构建输出提示 Node `[DEP0205] module.register()` deprecation warning。
- 浏览器访问时旧全站 `SiteSettingsLoader` 访问 `http://localhost:8000` 失败；该错误不来自 Batch 6
  占位页，也不是 AI/OCR 请求。

## 剩余风险

### RISK-B6-001

- 风险类型：体验 / 验收
- 风险描述：当前浏览器无管理员会话，因此只验证了匿名访问会被 AuthGate 拦截，未在登录态下截图/浏览器确认
  三个占位页的最终视觉呈现。
- 影响范围：`/manage/ai`、`/manage/jobs`、`/manage/settings`
- 严重程度：低
- 当前状态：部分处理
- 建议措施：用户验收时使用管理员会话访问三个页面和附件详情页，确认文案与无请求行为。
- 是否进入下一轮需求：否，作为 Batch 6 用户验收事项保留。

### RISK-B6-002

- 风险类型：既有系统 / 环境
- 风险描述：本地浏览器出现 `SiteSettingsLoader` API 连接失败，属于全站既有加载器或后端环境状态，不是本批新增
  AI/OCR 请求。
- 影响范围：全站设置加载体验
- 严重程度：低
- 当前状态：未处理
- 建议措施：如用户希望清理本地验收噪音，可单独开任务排查 API 服务与前端环境变量。
- 是否进入下一轮需求：否，除非用户要求处理环境噪音。

## 下一轮要求归档

真实 AI、OCR、Capture Router、任务队列、Prompt 保存、调用记录持久化、模型设置保存均保持后置，不进入
Batch 7，除非用户明确调整 MVP 范围。
