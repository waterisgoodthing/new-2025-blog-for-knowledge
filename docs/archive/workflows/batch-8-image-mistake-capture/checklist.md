# Batch 8 审批与验收检查表

## A. 当前任务组文档

- [x] README 说明目标、领域、状态、复用系统与 Batch 9–12 路线。
- [x] requirements 覆盖输入、处理、输出、失败和验收条件。
- [x] design 覆盖数据、调用边界、schema、状态机、权限、异常和验证。
- [x] tasks 拆成 P0-01 至 P0-09 的可审批任务。
- [x] risks 记录当前规划阶段风险。
- [x] handoff 明确下一位执行者的边界和停止条件。
- [x] 本轮只修改 `docs/workflows/batch-8-image-mistake-capture/**`。
- [x] 本轮未修改代码、API、迁移、依赖、数据库、上传目录或部署配置。
- [x] 用户已审查并明确批准 `tasks.md`。

## B. 实施前门禁（已完成）

- [x] 复核 `git status --short` 并保护所有既有用户改动。
- [x] 审计 Batch 4–7 与当前代码/数据库合同。（见 validation.md P0-01）
- [x] 确认最终管理端入口（`/manage/capture`）。
- [x] 确认单一 OCR/多模态实现和凭据边界。（capture_recognition.py，封装 call_ocr_model）
- [x] 确认 `capture_items` 字段、状态、迁移编号和附件关联策略。（migration 015，直接 FK source_attachment_id）
- [x] 确认 `MistakeDraftSuggestionV1`。（schemas/capture.py + capture_ai_draft.py）
- [x] 明确真实 AI/OCR 验收条件与不可用时的未验证标记。
- [x] 若计划超出当前批准范围，先更新文档并重新审批。

## C. 核心闭环验收（已完成，真实 AI/OCR 除外）

- [x] 管理员上传单张图片并保存 private attachment。（uploadAttachment → createCapture）
- [x] 图片与 capture item 可追踪关联。（source_attachment_id FK）
- [x] OCR/多模态状态可观察，结果可编辑。（状态徽章 + 可编辑识别文字区）
- [x] 用户可补充“我当时为什么错”。（user_error_context 编辑区）
- [x] AI 生成题面、解析、错因和知识点建议草稿。（triggerDraft → 草稿字段填充）
- [x] 所有 AI 字段可人工覆盖或删除。（patchCapture 支持所有草稿字段编辑）
- [x] 显式操作只生成一个 `mistake_draft`。（capture_service.convert_capture 创建唯一 mistake_draft）
- [x] `mistake_draft` 仍需人工确认才生成正式 `mistake`。（convert_capture 不调用 convert_mistake_draft）
- [x] `review_item` 仍只由正式 `mistake` 生成。（capture_service 不导入 ReviewItem 模型）
- [x] 原图继续作为 private attachment 保留。（attachments 表 visibility=private CHECK 约束）

## D. 失败与权限验收（已完成）

- [x] 上传失败不留下错误下游数据。（test_recognition_failure_zero_pollution 验证）
- [x] 识别失败不创建 mistake draft/mistake/review item。（test_recognition_failure_zero_pollution 验证）
- [x] AI/schema 失败不创建 mistake draft/mistake/review item。（test_draft_failure_zero_pollution mock 验证）
- [x] 转换失败事务回滚且可重试。（get_db 依赖管理事务，flush 失败自动回滚）
- [x] 重复转换不重复创建 mistake draft。（幂等路径：status=converted 返回既有结果）
- [x] 匿名 capture/AI/OCR/附件/转换请求为 401/403。（test_anon_capture_endpoints_denied 验证 7 端点）
- [x] API/日志/页面不泄露密钥、绝对路径或完整供应商原始响应。（CaptureOut 无 storage_key/raw_output；error_message_safe ≤300 字符）
- [x] 公开 `/blog`、`/notes`、`/mistakes` 不展示或请求 capture/AI/OCR 结果。（grep 确认无引用）
- [x] 权限验收不依赖 AUTH_BYPASS。（captures router 使用 get_current_admin JWT 鉴权）

## E. 严格禁止项（已验证）

- [x] 未建设完整 AI Gateway。
- [x] 未增加多供应商管理或模型路由。
- [x] 未增加 Prompt 管理后台、成本统计或完整 AI 审计系统。
- [x] 未增加 BKT、完整练习、批量 OCR 或 PDF 多页拆题。
- [x] 未公开 AI/OCR 结果。
- [x] 未迁移旧 `Note(type="mistake")`。
- [x] 未引入对象存储、云部署或生产级任务队列。

## 当前审批结论

**P0-01 至 P0-09 已完成并关闭。真实 AI/OCR：not verified（deepseek API 模型名称过期），作为后置补证项，不阻塞 Batch 8 关闭。所有自动化测试（14 passed）、schema/约束/索引、Alembic、TSC、build、匿名拒绝、禁止项搜索均通过。**
