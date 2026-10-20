# 任务清单：Batch 8 图片错题采集与 AI 错因草稿

> 状态：**已完成并关闭**。P0-01 至 P0-09 全部完成；真实 AI/OCR 保持 `not verified` 并转入后置补证项。
>
> 执行规则：批准后严格按 P0-01 → P0-09；每完成一项立即更新本文件，再开始下一项。

## P0-01 需求与现状审计

- [x] 审计 Batch 4–7、MVP 本地试运行、当前模型/API/管理页面和历史 AI 路由。（见 validation.md P0-01）
- 任务名称：冻结 Batch 8 可复用合同与冲突清单
- 优先级：P0
- 来源需求：REQ-B8-01、REQ-B8-06、REQ-B8-07、REQ-B8-10
- 涉及文件：既有代码只读检查；本 workflow `design.md`、`risks.md`、后续 `validation.md`
- 允许内容：只读确认 attachments、links、mistake draft 转换、review 生成、权限和 Batch 6 占位的真实现状；输出复用点与冲突清单。
- 完成标准：列出复用点、需扩展约束、旧 AI 能力隔离策略和停止条件。
- 验证方式：模型/schema/router/client/page 静态审计，Alembic current/heads，只读数据检查。
- 风险说明：若现状与文档不一致，先更新设计/需求/任务并在超出批准范围时重新申请审批。
- 依赖：用户批准 Batch 8 tasks。

## P0-02 capture_items 数据模型设计

- [x] 冻结 capture 状态机、字段、约束、附件关联与转换幂等方案。（见 validation.md P0-02）
- 任务名称：capture_items 数据模型与迁移规格
- 优先级：P0
- 来源需求：REQ-B8-01、REQ-B8-02、REQ-B8-03、REQ-B8-06、REQ-B8-08
- 涉及文件：候选 model/schema/migration、attachment link 约束、定向测试
- 允许内容：设计 `capture_items` 字段、约束、状态机；决定主附件引用方式；明确失败零污染和归档语义。
- 禁止内容：不新增 AI Gateway、完整 run 表、对象存储或任务队列表；不修改既有 mistakes/review_items 模型语义。
- 完成标准：字段、check/index/FK、状态转换、删除策略和 migration rollback 均可验证。
- 验证方式：migration inspection、约束测试、孤儿/级联测试、原有数据计数对比。
- 风险说明：不得顺手新增 AI Gateway、完整 run 表、对象存储或任务队列表。
- 依赖：P0-01。

## P0-03 OCR / 多模态调用边界设计

- [x] 定义单图识别 adapter、超时、错误分类、重试与最小运行记录。（见 validation.md P0-03）
- 任务名称：最小识别调用边界
- 优先级：P0
- 来源需求：REQ-B8-02、REQ-B8-08、REQ-B8-10
- 涉及文件：候选 adapter/service/config/schema 与定向测试
- 允许内容：让 capture service 依赖窄识别接口，不感知供应商路由；固定单图输入与识别结果；定义超时与错误分类。
- 禁止内容：不建设多供应商管理、模型路由、批量 OCR、PDF 拆题或生产级任务队列。
- 完成标准：成功/超时/失败/schema 异常可区分；失败时下游零写入；无批量/PDF/生产队列。
- 验证方式：fake adapter tests、timeout/error tests、敏感字段审查。
- 风险说明：真实供应商与凭据方案必须另行确认；不得把多供应商治理塞入本项。
- 依赖：P0-02。

## P0-04 AI 错因草稿输出 schema 设计

- [x] 冻结 `MistakeDraftSuggestionV1`、校验和人工编辑语义。（见 validation.md P0-04）
- 任务名称：AI 题面/解析/错因/知识点建议合同
- 优先级：P0
- 来源需求：REQ-B8-04、REQ-B8-05、REQ-B8-08
- 涉及文件：候选 Pydantic/TypeScript schema、adapter/service 与定向测试
- 允许内容：结构化题面、解析、错因、subject/knowledge point 建议和 warnings；固定 schema 校验；所有输出可编辑。
- 禁止内容：不建设 Prompt 管理后台、Validator 管理、完整 AI 审计或成本统计；不把 AI 输出直写 mistakes/review_items。
- 完成标准：有效/缺字段/错误类型/未知知识点均有稳定处理；所有输出可编辑。
- 验证方式：schema contract tests、invalid output tests、前后端类型对照。
- 风险说明：不建设 Prompt 后台、Validator 管理、完整 AI 审计或成本统计。
- 依赖：P0-03。

## P0-05 capture → mistake_draft 转换流程设计

- [x] 实现并验证显式、幂等、事务化的草稿转换边界。（见 validation.md P0-05）
- 任务名称：采集项转既有错题草稿
- 优先级：P0
- 来源需求：REQ-B8-06、REQ-B8-07
- 涉及文件：capture service、既有 mistake draft service、attachment links、定向测试
- 允许内容：校验 ready 状态和人工输入，原子创建一个 `mistake_draft`，关联原图，保存目标 id 并标记 converted。
- 禁止内容：不直接创建正式 `mistake` 或 `review_item`；不修改复习计划；不绕过既有人工确认门禁。
- 完成标准：重复转换只返回同一草稿；任何失败不创建 mistake/review item；正式确认链保持原样。
- 验证方式：事务回滚、并发/重复请求、DB 行数与关联检查、既有转换回归。
- 风险说明：不得直接创建正式 `mistake` 或 `review_item`。
- 依赖：P0-02、P0-04。

## P0-06 管理端页面与交互设计

- [x] 冻结入口并实现单图上传到 mistake draft 的管理端工作流。（见 validation.md P0-06）
- 任务名称：图片错题采集工作台
- 优先级：P0
- 来源需求：REQ-B8-01 至 REQ-B8-09
- 涉及文件：候选 `/manage/capture` 或 `/manage/mistakes/capture`、route components/hooks、`src/lib/api/*`
- 允许内容：上传/选图、预览、状态、用户错因、草稿编辑、知识点选择、重试、转换与跳转；桌面/移动单图闭环。
- 禁止内容：不做批量 OCR、PDF 拆题、公开页入口或完整 AI 管理台；不把 AI 中间结果加入公开 DTO。
- 完成标准：桌面/移动均可完成单图闭环；empty/loading/failed/converted 状态明确。
- 验证方式：TSC、build、真实浏览器、console/network、刷新恢复。
- 风险说明：不做批量 OCR、PDF 拆题、公开页入口或完整 AI 管理台。
- 依赖：P0-03、P0-04、P0-05。

## P0-07 权限、公开边界与失败状态设计

- [x] 完成 admin-only 防线、private 原图、公开回归和失败隔离验证。（见 validation.md P0-07）
- 任务名称：权限与失败零污染
- 优先级：P0
- 来源需求：REQ-B8-01、REQ-B8-02、REQ-B8-06、REQ-B8-08、REQ-B8-10
- 涉及文件：管理路由/页面、capture/attachment service、权限与回归测试
- 允许内容：所有 capture/AI/OCR/转换接口使用 `get_current_admin`；页面使用既有管理保护；公开页面不请求管理接口。
- 禁止内容：不把前端 AuthGate 当唯一安全边界；不误伤公开 `/mistakes`、`/notes`、`/blog`；不公开附件或 AI 中间结果。
- 完成标准：匿名全部拒绝；失败 capture 不新增 mistake draft/mistake/review item；无路径或 AI 中间结果泄露。
- 验证方式：匿名/admin HTTP、DB 前后计数、公开 API/页面、AUTH_BYPASS=false 的真实权限测试。
- 风险说明：前端 AuthGate 不是唯一安全边界；不得误伤公开 `/mistakes`、`/notes`、`/blog`。
- 依赖：P0-03 至 P0-06。

## P0-08 测试与验收方案

- [x] 完成自动化、合同、迁移、浏览器和真实单图验收。（见 validation.md P0-08）
- 任务名称：Batch 8 端到端验证
- 优先级：P0
- 来源需求：全部
- 涉及文件：定向 tests、本 workflow `checklist.md`、后续 `validation.md` 与必要 assets
- 允许内容：覆盖成功、识别失败、AI schema 失败、重试、编辑、转换幂等、权限和公开回归；记录真实证据。
- 禁止内容：不以 mock 冒充真实端到端通过；不跳过失败零污染与匿名拒绝验证；不放宽禁止项检查。
- 完成标准：至少一张无敏感信息测试图片完成真实闭环；失败场景证明下游零污染。
- 验证方式：pytest、Alembic、FastAPI import、TSC、build、browser、DB/附件检查、`git diff --check`。
- 风险说明：若无法使用真实 AI/OCR，只能标为未验证，不得用 mock 证据宣称完整闭环通过。
- 依赖：P0-01 至 P0-07。

## P0-09 handoff 与下一批接口预留

- [x] 完成审查、验证记录、残余风险与 Batch 9–12 边界移交。（见 validation.md P0-09）
- 任务名称：Batch 8 收口与分阶段治理接口
- 优先级：P0
- 来源需求：全部
- 涉及文件：本 workflow README/checklist/risks/handoff/tasks，后续 audit/validation
- 允许内容：记录实现范围、证据、未验证项、Batch 9 gateway adapter 接口和 Batch 10–12 后置项；更新 README/checklist/risks。
- 禁止内容：不自行启动 Batch 9；不把阶段性完成表述为整个 AI 系统闭环；不提前实现后续治理能力。
- 完成标准：Batch 8 只进入等待用户验收；未把后续治理误标为已实现。
- 验证方式：范围 diff、禁止项搜索、文档与代码合同交叉审查。
- 风险说明：不得自行启动 Batch 9，不得把 Batch 8 阶段性完成表述为整个 AI 系统闭环。
- 依赖：P0-08。

## 审批记录

- [x] 用户已明确批准执行 Batch 8 tasks。
- 当前结论：**已批准，P0-01 至 P0-09 已完成并关闭。真实 AI/OCR：not verified，作为后置补证项，不阻塞本批关闭。**
