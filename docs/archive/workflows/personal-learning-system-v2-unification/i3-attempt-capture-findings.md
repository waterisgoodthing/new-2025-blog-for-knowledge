# I3 现状发现

- `questions`、`mistakes`、`review_items`/`review_records`、`capture_items` 已存在，当前 Alembic revision 是 `020`。
- `Mistake` 已要求引用正式 Question，且其确认流程会创建 Review Item；`MistakeDraft` 当前只能从 Question 或 QuestionDraft 创建。
- 未发现 Attempt 表、schema、router、service、前端 API 或管理端页面。
- Capture 后端已有 `CapturePatch`、`CaptureConvert` 和 AI/OCR 失败字段；管理端 `/manage/capture` 目前是“未启用”占位页，未挂接现有 `CaptureWorkspace` 与 `ManualQuestionEntry`。
- 所有 I3 写入必须继续经管理员会话；不启用 `AUTH_BYPASS`。
