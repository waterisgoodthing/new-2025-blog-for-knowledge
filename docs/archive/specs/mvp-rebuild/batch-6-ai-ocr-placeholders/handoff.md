# Handoff

## 本批完成内容

- 新增 `/manage/ai` 静态占位页，覆盖模型配置、Prompt 模板、调用记录三类结构。
- 新增 `/manage/jobs` 静态占位页，覆盖队列状态、任务类型、重试与错误观察结构。
- 新增 `/manage/settings` 静态占位页，覆盖 AI/OCR、Upload/Jobs、Privacy 设置归属。
- 附件详情新增“OCR 第一版暂未启用”状态区域。
- 管理侧栏和 dashboard 增加 Batch 6 入口，并明确占位/暂未启用状态。
- 完成主流程无 AI/OCR 依赖的静态审查与构建验证。

## 修改文件

- `src/app/manage/(workspace)/components/future-capability-page.tsx`
- `src/app/manage/(workspace)/ai/page.tsx`
- `src/app/manage/(workspace)/jobs/page.tsx`
- `src/app/manage/(workspace)/settings/page.tsx`
- `src/app/manage/(workspace)/attachments/components/attachment-detail.tsx`
- `src/app/manage/components/manage-sidebar.tsx`
- `src/app/manage/(workspace)/dashboard/page.tsx`
- `docs/workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/`
- `docs/specs/mvp-rebuild/batch-6-ai-ocr-placeholders/checklist.md`
- `docs/specs/mvp-rebuild/batch-6-ai-ocr-placeholders/handoff.md`

## 未完成事项

- 真实 AI、OCR、模型配置、Prompt 保存、调用记录和队列必须列为后置。
- Capture Router、多模型路由、worker、轮询、重试、成本统计均未接入。
- 当前浏览器无管理员会话，登录态视觉验收留给用户验收阶段。

## 风险点

- 若未来继续 AI/OCR，不得复用本批占位文案声称能力已启用；必须重新补后端合同、权限、数据表和验证。
- 旧 `/api/ai*` 与旧 `/manage` AI tab 属于既有系统能力，本批没有扩大访问面。
- 匿名访问已被 AuthGate 拦截；未使用 `AUTH_BYPASS` 做权限通过验收。
- 本地浏览器出现既有 `SiteSettingsLoader` API 连接失败噪音，不是 Batch 6 AI/OCR 请求。

## 下一批前置条件

- 用户使用管理员会话完成 Batch 6 页面视觉验收，或明确接受当前源码/build/匿名拦截证据。
- 所有占位页稳定、主流程无 AI/OCR 依赖、权限验收通过，且用户批准进入 Batch 7。

## 用户确认

- [x] 用户已确认可以进入下一批（2026-07-03：确认 Batch 6 通过，允许进入 Batch 7 workflow 准备阶段）
