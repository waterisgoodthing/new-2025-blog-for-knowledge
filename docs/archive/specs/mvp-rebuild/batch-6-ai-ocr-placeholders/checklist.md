# Checklist

- [x] 已建立对应 workflow，并由用户批准 tasks。
- [x] `/manage/ai` 占位页已进入 build route table。
- [x] `/manage/jobs` 占位页已进入 build route table。
- [x] `/manage/settings` 占位页已进入 build route table。
- [x] 附件详情明确显示 OCR 尚未启用。
- [x] AI 控制台只有模型、Prompt、调用记录占位结构。
- [x] 所有相关文案明确“第一版暂未启用”。
- [x] 主流程不发出 AI/OCR 请求。
- [x] 没有新增真实 AI/OCR 表、API、依赖或配置。
- [x] 管理员访问保护与公开页面权限边界已验证。
- [x] 占位页面登录态浏览器验收无错误，或用户接受当前源码 / build / 匿名拦截证据。
- [x] 已填写 `handoff.md`。

## 说明

- 匿名浏览器访问 Batch 6 管理页会被 `AuthGate` 拦截到 `/manage`，权限边界符合预期。
- 当前浏览器无管理员会话，未使用 `AUTH_BYPASS` 造验收通过态；登录态视觉验收留给用户验收阶段。
- 用户已于 2026-07-03 确认 Batch 6 通过，并允许进入 Batch 7 workflow 准备阶段。
