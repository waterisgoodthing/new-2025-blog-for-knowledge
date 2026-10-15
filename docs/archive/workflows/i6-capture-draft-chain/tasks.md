# I6 任务清单

状态：`COMPLETE / PASS / I6-VERIFIED (2026-07-24)`

> 只有用户明确批准本清单后，才开始修改代码或测试。批准不包含源库/生产迁移、部署、推送、权威切换、真实 AI 成功调用或 I7 以后任务。

## 执行状态

- [x] I6-01 现有契约与 022 目标基线
- [x] I6-02 私有单文件 HTTP 闭环
- [x] I6-03 识别成功与失败隔离
- [x] I6-04 草稿生成与人工修正
- [x] I6-05 Draft 审核状态与版本冲突
- [x] I6-06 幂等转换与审计链
- [x] I6-07 管理员浏览器与移动验收
- [x] I6-08 最终质量、文档与下一轮门

## I6-01 现有契约与 022 目标基线（已完成）

优先级：P0
来源需求：REQ-I6-01～REQ-I6-05
涉及文件：`backend/app/models/`、`backend/app/schemas/`、`backend/app/routers/`、现有 022 隔离目标、workflow validation
修改内容：只读核对 Attachment/Capture/Draft 表、路由、依赖、唯一约束和当前 revision；如发现缺口先更新 design/requirements，不直接扩 scope。
完成标准：确认 `current=heads=022`、私有 API 均有管理员依赖、源链字段和状态约束与代码一致。
验证方式：Alembic current/heads、路由契约测试、数据库只读查询、现有定向测试基线。
风险说明：默认旧数据库可能是 020；不执行迁移解决 drift。实际验证使用既有 `pls_v2_i4_target`，current/heads 均为 022。

## I6-02 私有单文件 HTTP 闭环（已完成）

优先级：P0
来源需求：REQ-I6-01
涉及文件：附件/Capture routers、schemas、API client、Capture workspace tests
修改内容：补齐上传 → Capture 创建 → 列表/详情的管理员 HTTP 测试、非法文件与临时文件清理断言；仅修正实际缺口。
完成标准：管理员成功、匿名/失效 401、非法文件 4xx、私有内容不能匿名读取。
验证方式：022 目标 FastAPI/TestClient 或等价 HTTP 测试，移动浏览器手工证据。
风险说明：不新增公开附件路由，不改变公开内容权限。新增 HTTP 回归测试 2 项通过，上传后的隔离测试数据和文件已清理。

## I6-03 识别成功与失败隔离（已完成）

优先级：P0
来源需求：REQ-I6-02、REQ-I6-03
涉及文件：`capture_service.py`、recognition adapter、backend tests
修改内容：固化 fake 成功、附件缺失、空输入、无 provider、超时/provider/解析失败的独立回归测试和重试状态。
完成标准：失败只更新 Capture 安全字段，正式 Draft/Mistake/Question/ReviewItem 计数不变；成功只进入 recognized。
验证方式：service + HTTP tests、事务回滚/恢复检查。
风险说明：不以真实 provider 成功作为验收条件。新增失败矩阵测试覆盖附件缺失、空输入、超时、provider 错误和 schema 失败；定向 Capture 测试共 17 项通过。

## I6-04 草稿生成与人工修正（已完成）

优先级：P0
来源需求：REQ-I6-03
涉及文件：`capture_service.py`、`capture_ai_draft.py`、Capture schemas/UI/tests
修改内容：验证 fake 草稿生成、空文本、schema/provider 失败、failed → ready 人工修正；确保候选字段可覆盖且安全错误可重试。
完成标准：ready 状态只表示候选已准备，不表示正式学习对象已写入。
验证方式：后端状态机测试、前端组件/交互测试、浏览器断言。
风险说明：不得将 AI/OCR 设为保存或转换的强制前置。后端 Capture 状态测试 17 项组合通过，Capture/Draft 前端定向测试 7 项通过。

## I6-05 Draft 审核状态与版本冲突（已完成）

优先级：P0
来源需求：REQ-I6-04
涉及文件：`draft_service.py`、`drafts.py`、Question/Mistake draft schemas、Draft workspace
修改内容：补齐编辑、needs_fix、reject、confirm、过期 version 和来源失效测试；只允许人工确认后转换。
完成标准：rejected/converted 不可误编辑或二次转换；过期 version 为 409；修正递增 version 并保留来源。
验证方式：service/HTTP/前端测试和数据库目标对象核对。
风险说明：若需要新增审计表，先暂停并申请扩大批准范围。现有 Draft service 状态/版本测试与新增 Capture→Draft 来源链测试共 15 项通过，未新增审计表。

## I6-06 幂等转换与审计链（已完成）

优先级：P0
来源需求：REQ-I6-05
涉及文件：Capture/Draft services、models、tests
修改内容：验证重复 Capture 转换、重复 Draft 转换、并发/唯一约束和 `source → draft → target` 链；补齐最小审计字段的可重建证据。
完成标准：同一源最多一个目标，重复请求返回既有目标，不生成重复正式对象。
验证方式：重复/并发 service tests、022 数据库只读核对、错误后恢复查询。
风险说明：不得静默覆盖或依赖前端防重复。Capture service 既有幂等测试与新增来源链测试纳入组合，34 项 I6 后端组合测试通过；并发锁语义保留为 `with_for_update`，未引入重复目标。

## I6-07 管理员浏览器与移动验收（已完成）

优先级：P1
来源需求：REQ-I6-01～REQ-I6-05
涉及文件：`src/app/manage/(workspace)/capture/`、`drafts/`、assets
修改内容：在独立生产构建中完成管理员上传、状态推进、人工修正、拒绝/确认和重复操作；记录匿名边界、失败提示、来源显示、键盘和三尺寸证据。
完成标准：390×844、1280×800、1440×900 无横向溢出；关键按钮有名称；不展示本地路径或 provider 原始错误。
验证方式：Playwright/Chrome 或仓库可用浏览器执行器，截图与 DOM/网络记录。
风险说明：受控 fake/API fixture 只证明前端/状态契约，不宣称真实 AI provider 成功。390×844、1280×800、1440×900 均无横向溢出；失败提示、人工修正后 `待确认`、viewport 和键盘焦点证据已归档。

## I6-08 最终质量、文档与下一轮门（已完成）

优先级：P1
来源需求：所有 I6 需求
涉及文件：本 workflow、`personal-learning-system-v2-unification` 索引、源代码 changed files
修改内容：逐项回写 tasks/validation、风险清单和下一轮需求；执行定向测试、TypeScript、Python compileall、build、diff check 和范围审查。
完成标准：每个 P0 有证据；失败或未知项进入风险清单；未通过不得标 `COMPLETE / PASS`。
验证方式：最终验收报告、残余风险清单、下一轮需求文档。
风险说明：I6 通过不授权 I7、迁移、部署或切换。022 后端组合 51 项、前端定向 33 项、TypeScript、build、Python compileall 和 diff check 均通过；全仓库 Vitest 的既有 AI capture 路由失败仍不纳入本轮范围。
