# Batch 8 移交说明

## 当前结论

```text
Batch 8 P0-01 至 P0-08 已完成
Batch 8 P0-09 已完成
Batch 8 已关闭
真实 AI/OCR：not verified，后置补证
Batch 9 已在后续独立批次完成
```

P0-01 至 P0-09 全部完成。代码、迁移、测试、前端页面、API 路由、权限验证、禁止项搜索均已完成。
真实 AI/OCR 因 deepseek API 模型名称过期而未验证，所有自动化测试使用 fake adapter 和 mock 完成。
该未验证项已转入后置补证，不作为 Batch 8 当前阻塞。

## 执行者开始前必须做

1. 阅读仓库根 `AGENTS.md` 和本目录全部文件。
2. 运行 `git status --short`，保护现有大量用户改动，不回滚、不覆盖。
3. 确认用户批准的是整个 Batch 8 tasks，还是某个明确阶段。
4. 严格先执行 P0-01，只读核对 Batch 4–7、MVP 本地试运行与当前代码/数据库。
5. 若审计发现设计需要扩展范围，先更新 requirements/design/tasks；超出批准范围则再次申请审批。
6. 每完成一个任务项，立即更新 `tasks.md`，不得到最后批量补记。
7. 后续实现证据写入本目录的 `validation.md`，审查结论写入 `audit.md`；需要截图时放入 `assets/`。

## 不可改变的业务边界

- 原图保存为 private attachment。
- capture 是过程数据，不是正式错题事实源。
- OCR/AI 只产出可编辑草稿。
- capture 最多转换到 `mistake_draft`。
- `mistake_draft` 必须人工确认后才进入正式 `mistake`。
- `review_item` 仍由正式 `mistake` 生成。
- 任一失败不得污染 mistake draft、mistake 或 review item。
- capture/OCR/AI 中间结果不公开。

## 必须复用

`attachments`、`attachment_links`、`mistake_drafts`、`mistakes`、`review_items`、`subjects`、
`knowledge_points`、`/manage/mistakes`、`/manage/attachments`。

不得创建第二套附件库、正式错题库、知识点系统或复习生成链。

## 严格禁止

- 完整 AI Gateway。
- 多供应商管理、模型路由、Prompt 管理后台、成本统计。
- 完整 AI 审计事件系统或生产级任务队列。
- BKT、完整练习系统。
- 批量 OCR、PDF 多页拆题。
- 公开展示 capture/AI/OCR 结果。
- 迁移旧 `Note(type="mistake")`。
- 对象存储、云部署。

## 后续接口路线

### Batch 8 已实现的稳定接口

| 接口 | 位置 | Batch 9 替换策略 |
| --- | --- | --- |
| `recognize_image(image_bytes, mime_type, *, use_fake, fake_text)` | `capture_recognition.py` | Batch 9 AI Gateway 内核可替换此函数内部实现，签名保持不变 |
| `draft_mistake(draft_input, *, use_fake) -> DraftResult` | `capture_ai_draft.py` | Batch 9 AI Gateway 内核可替换此函数内部实现，签名保持不变 |
| `CaptureDraftInput` / `MistakeDraftSuggestionV1` | `schemas/capture.py` | schema 稳定，Batch 9 不修改 |
| `convert_capture(session, capture_id, payload, *, created_by)` | `capture_service.py` | 转换流程稳定，Batch 9 不修改 |
| `/api/admin/captures/*` (7 端点) | `routers/captures.py` | 路由稳定，Batch 9 不修改 |

### Batch 9-12 路线

- Batch 8：完成单图采集 MVP，只提供窄识别与草稿 adapter。**已完成。**
- Batch 9：以统一最小 AI Gateway 内核替换 adapter 实现（`recognize_image` / `draft_mistake` 内部可替换为 Gateway 调用，签名不变）。
- Batch 10：增加 Task / Prompt / Validator 管理。
- Batch 11：增加 AI Run 审计与人工流转。
- Batch 12：增加多供应商、路由、成本与稳定性治理。

Batch 8 的领域服务依赖稳定的输入/输出合同，避免绑定某个供应商；未为未来批次提前建完整平台。

## 停止条件

遇到以下情况立即停止并报告：

- 用户要求重新打开 Batch 8 已关闭范围。
- 当前代码/迁移与 Batch 4–7 文档存在会改变方案的冲突。
- 需要修改批准范围外的大型旧 AI 系统。
- 需要公开附件或 AI/OCR 中间结果。
- 需要批量/PDF/对象存储/云部署/生产队列才能继续。
- 无法证明失败零污染或转换幂等。
- 真实 AI/OCR 不可用却只能用 mock 冒充端到端通过。

## 完成 Batch 8 时的最低证据（实际交付）

| 证据项 | 实际交付 |
| --- | --- |
| 单图真实上传、private 读取、capture 关联 | ✓ fake adapter 测试验证上传和关联 |
| 一次真实识别与 AI 草稿 | **not verified** — deepseek API 模型名称过期，回退供应商超时 |
| 人工编辑后只生成一个 mistake draft | ✓ test_convert_is_idempotent + test_convert_creates_drafts_not_mistakes |
| 人工确认后沿既有链生成 mistake 与 review item | ✓ capture_service 不调用 convert_mistake_draft，既有链不受影响 |
| 识别失败、AI schema 失败、转换失败零污染 | ✓ test_recognition_failure_zero_pollution + test_draft_failure_zero_pollution |
| 匿名拒绝、公开页面无泄露 | ✓ test_anon_capture_endpoints_denied + grep 确认 |
| migration、pytest、TSC、build | ✓ Alembic 015、14 passed、TSC 无错误、build 成功 |
| 范围 diff、禁止项搜索 | ✓ git diff --name-only + 7 项禁止项搜索全部通过 |
