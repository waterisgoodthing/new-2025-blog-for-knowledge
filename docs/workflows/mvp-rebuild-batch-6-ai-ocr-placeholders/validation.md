# Batch 6 验证记录

## 当前状态

执行中；中间证据不代表 Batch 6 已验收。

## P0-01 基线与禁止项审计

- 用户于 2026-07-03 明确批准 Batch 6 tasks。
- 现有旧入口：
  - `backend/app/routers/ai.py`
  - `backend/app/routers/ai_polish.py`
  - `backend/app/services/ai_service.py`
  - `backend/app/services/ai_polish_service.py`
  - `src/lib/api/ai.ts`
  - `src/lib/api/ai-polish.ts`
  - 旧 `/manage` 页面存在 `AITab` 与 `settings` tab。
- 现有旧 migration：`004_add_ai_metadata_to_notes.py`，属于旧 Note 系统历史字段。
- Batch 3-5 新 workspace 主流程检查范围：
  - `src/app/manage/(workspace)/drafts`
  - `src/app/manage/(workspace)/questions`
  - `src/app/manage/(workspace)/mistakes`
  - `src/app/manage/(workspace)/review`
  - `src/app/manage/(workspace)/attachments`
- 基线结论：
  - 新 workspace 主流程未 import `src/lib/api/ai*`。
  - 新 workspace 主流程未出现 OCR/Capture/Jobs API 调用。
  - 附件详情目前只有 attachment-links 关联，不包含 OCR 状态。
  - `/manage/(workspace)` 仍由 AuthGate 包裹。
- 风险说明：旧 AI 路由和旧 `/manage` AI tab 是既有系统能力；Batch 6 不扩大其访问面，不把它们包装为 MVP 新能力。

## P0-02 静态占位组件

- 新增 `src/app/manage/(workspace)/components/future-capability-page.tsx`。
- 组件只接收静态 props，不 import `src/lib/api/*`，不调用 `fetch` 或 `apiFetch`。
- 文案统一说明“第一版暂未启用”，并列出本批明确不提供的操作。
- `npx tsc --noEmit`：通过。

## P0-03 `/manage/ai` 占位页

- 新增 `/manage/ai` 页面。
- 覆盖模型配置、Prompt 模板、调用记录三类占位结构。
- 静态搜索确认页面无 API import、无 fetch、无真实 AI 请求。
- 禁用操作仅作为文字说明出现：生成分析、重新生成、保存 Prompt、切换模型、查看真实运行记录。

## P0-04 `/manage/jobs` 占位页

- 新增 `/manage/jobs` 页面。
- 覆盖队列状态、任务类型、重试与错误观察三类占位结构。
- 静态搜索确认页面无 API import、无 fetch、无轮询、无 job API。

## P0-05 `/manage/settings` 占位页

- 新增 `/manage/settings` 页面。
- 覆盖 AI/OCR、Upload/Jobs、Privacy 三类设置分组占位。
- 静态搜索确认页面无 API import、无 fetch、无 settings 写请求。
- “保存设置”等只出现在禁用操作说明里，没有真实保存按钮或 toast。

## P0-06 附件详情 OCR 未启用状态

- 在 `/manage/attachments/[id]` 详情页新增 OCR 状态卡片。
- 文案明确：
  - OCR 第一版暂未启用。
  - 当前不会自动识别。
  - 不会拆分 PDF。
  - 不会把识别结果写入草稿或正式题库。
- 未新增按钮，未新增请求。
- 静态搜索确认无“开始 OCR/重新识别”等可操作文案；只命中“无 OCR 请求”说明标签。
- `npx tsc --noEmit`：通过。

## P0-07 导航与 dashboard 入口

- `ManageSidebar` 新增：
  - `/manage/ai`
  - `/manage/jobs`
  - `/manage/settings`
- Dashboard 新增 Batch 6 入口，并把附件状态改为“私有上传已接入；OCR 暂未启用”。
- Dashboard 入口数量改用 `workspaceStatus.length`，避免硬编码。
- 静态搜索确认新增入口无 API import、无 fetch、无真实请求；禁用操作只作为说明文字出现。
- `npx tsc --noEmit`：通过。

## P0-08 主流程无 AI/OCR 依赖验证

- 静态搜索范围：
  - `backend/alembic/versions`
  - `backend/app/models`
  - `backend/app/routers`
  - `backend/app/services`
  - `src/app/manage/(workspace)`
  - `src/lib/api`
- 结论：
  - 未新增 `ai_runs`、`ocr_jobs`、`ocr_results`、`capture_jobs`、`capture_results` migration/model。
  - 未新增 `/api/admin/ai`、`/api/admin/ocr`、`/api/admin/capture`、`/api/admin/jobs`、`/api/admin/settings`。
  - 新 Batch 6 workspace 页面没有 import `src/lib/api/ai*`、没有 fetch/apiFetch。
  - 静态搜索命中的 `/api/ai*` 均位于既有旧系统：`backend/app/routers/ai.py`、
    `backend/app/routers/ai_polish.py`、`backend/app/routers/suggestions.py`、`src/lib/api/ai.ts`、
    `src/lib/api/ai-polish.ts`、`src/lib/api/knowledge.ts`、`src/lib/api/knowledge-assistant.ts`。
- `npm run build`：通过，新路由已进入 route table：
  - `/manage/ai`
  - `/manage/jobs`
  - `/manage/settings`
- 非阻塞警告：
  - `baseline-browser-mapping` 数据超过两个月。
  - Node `[DEP0205] module.register()` deprecation warning。

## P0-09 审查、验证与移交

- `git diff --check`：通过。
- `npx tsc --noEmit`：通过。
- `npm run build`：通过；route table 包含：
  - `/manage/ai`
  - `/manage/jobs`
  - `/manage/settings`
- 浏览器验证：
  - 现有 `localhost:2025` 被旧 `next-server` 进程占用，访问 `/manage/ai` 返回旧状态 404；
    未杀进程，改用备用端口 `3025` 启动临时 dev server。
  - 临时 dev server 日志显示 `/manage/ai`、`/manage/jobs`、`/manage/settings` 均返回 200。
  - 匿名浏览器访问 `http://localhost:3025/manage/ai`、`/manage/jobs`、`/manage/settings`
    被 `AuthGate` 拦截到 `/manage` 登录入口，符合管理页访问保护。
  - 当前浏览器没有管理员会话；未使用 `AUTH_BYPASS` 构造通过态，因此登录态视觉验收保留给用户验收阶段。
- 非阻塞警告：
  - `SiteSettingsLoader` 在浏览器中访问 `http://localhost:8000` 失败；该请求属于既有全站设置加载器，
    不是 Batch 6 占位页新增 AI/OCR 请求。
- 审查记录：已补充 `audit.md`，列明影响范围、权限边界、无副作用检查、剩余风险和后置能力。

## 总结

Batch 6 实现侧收口完成，状态为等待用户验收；不得自动进入 Batch 7。
