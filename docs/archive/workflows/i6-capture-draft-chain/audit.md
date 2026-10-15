# I6 现状审计

日期：2026-07-24

## 已确认实现

| 区域 | 当前事实 | 证据入口 |
|---|---|---|
| 私有上传 | 附件服务支持流式上传、私有元数据、哈希/路径校验和内容读取；管理员附件路由受 `get_current_admin` 保护 | `backend/app/services/attachment_service.py`、`backend/app/routers/attachments.py` |
| Capture | `CaptureItem` 记录来源附件、状态、识别文本、草稿字段、失败安全码、尝试次数、阶段和转换目标 | `backend/app/models/capture.py` |
| 识别 | 单图识别适配器支持 fake 测试路径；无 provider、超时、provider、解析和空结果均转为安全失败 | `backend/app/services/capture_recognition.py` |
| 草稿 | AI 输出先进入 Capture 草稿字段；schema 校验失败或 provider 失败不写正式 Mistake | `backend/app/services/capture_ai_draft.py`、`backend/app/services/capture_service.py` |
| 转换 | Capture 转 Mistake Draft 已有 ready 校验、来源附件链接、人工字段和幂等返回 | `backend/app/services/capture_service.py` |
| 审核 | Question Draft 已有 pending/needs_fix/rejected/converted、版本校验、编辑、拒绝和幂等转换 | `backend/app/services/draft_service.py`、`backend/app/routers/drafts.py` |
| 前端 | Capture 工作区已有上传、列表、识别、草稿、人工编辑、学科/知识点和转换入口；Draft 工作区已有独立页面 | `src/app/manage/(workspace)/capture/`、`src/app/manage/(workspace)/drafts/` |

## 本轮需要补证的缺口

1. 用 022 隔离目标确认 Capture、Attachment、Draft 相关 HTTP 契约和权限，不使用默认旧 revision 作为结论。
2. 把识别失败、草稿失败、空输入、附件缺失、拒绝后转换、过期版本和重复转换分别固化为回归测试，不能只依赖 service happy path。
3. 证明自动化输出不会进入 `questions`、`mistakes` 或 `review_items`；只有人工确认的类型化草稿可以转换。
4. 确认“审计”最小证据采用现有 `source_*`、`created_by`、`version`、`target_*`、时间戳和安全错误字段；若不足，先在 design/tasks 中提出最小 schema 变更，不直接修改。
5. 重新取得管理员真实浏览器路径：上传私有图片 → 识别失败或 fake 成功 → 人工修正 → 草稿审核 → 拒绝/确认/重复操作，并记录匿名访问边界。

## 硬边界

- 不执行源库或生产迁移，不改变数据库权威，不部署、不推送。
- 不调用真实 AI provider 以证明成功；成功路径使用受控 fake adapter，真实 provider 只验证安全失败映射。
- 不把 CaptureItem 变成正式内容主数据，不新增公开附件 API。
