# 需求文档：Batch 8 图片错题采集与 AI 错因草稿

## 背景

Batch 0–7 已完成，MVP 已真实验证手工链路：

```text
subject → knowledge point → question draft → question → mistake draft
→ mistake → review item → review record → attachment upload/link/read
```

该链路功能完整，但日常从截图录入错题仍过于繁琐。个人管理员需要从一张图片开始，经最小
OCR/多模态识别和 AI 草稿辅助，人工确认后进入既有错题与复习系统。

## 用户角色

- 个人管理员：上传图片、补充自己的错误原因、检查和编辑 AI/OCR 输出、生成并确认错题草稿。
- 未登录访客：不得访问采集记录、原图私有附件、OCR 文本或 AI 草稿。

## 功能需求

### REQ-B8-01 单图采集与原图保留

- 输入：管理员上传一张受支持的图片。
- 处理：复用附件上传，保存为 private attachment；创建一个引用该附件的 `capture_item`。
- 输出：可追踪的采集项与原图附件关联。
- 失败：上传或建项失败时返回明确错误；不得产生半成品正式错题。
- 验收：每个 capture item 可定位一张 private 原图，API/页面不泄露本地路径。

### REQ-B8-02 OCR / 多模态识别状态

- 输入：有效 capture item 及其原图。
- 处理：通过最小调用适配边界触发一次识别，保存状态与原始文本结果。
- 输出：`pending | processing | succeeded | failed` 等可解释状态和可编辑识别文本。
- 失败：记录最小错误分类和可重试状态，不创建 `mistake_draft`。
- 验收：成功、失败、重试均可观察；不依赖生产级任务队列。

### REQ-B8-03 用户错误背景补充

- 输入：管理员填写“我当时为什么错”等可选上下文。
- 处理：与识别文本一起作为 AI 草稿输入；允许识别前后修改。
- 输出：保存在 capture item 的私有输入字段中。
- 失败：保存失败不丢失当前编辑内容，不触发正式错题写入。
- 验收：该字段可编辑、可留空，并明确不会公开展示。

### REQ-B8-04 AI 错题草稿输出

- 输入：识别文本、用户补充、可选 subject/knowledge point 上下文。
- 处理：AI 生成结构化候选内容：题面草稿、解析草稿、错因总结、知识点建议。
- 输出：符合固定 schema 的可编辑草稿输出。
- 失败：无效 schema、超时或模型错误进入 failed，不创建正式数据。
- 验收：所有字段均可人工编辑；AI 输出不得直接写 `mistakes`。

### REQ-B8-05 人工编辑与知识点选择

- 输入：AI/OCR 草稿、现有 `subjects` 与 `knowledge_points`。
- 处理：管理员编辑题面、解析、错因，选择或改正 subject/knowledge point。
- 输出：人工确认后的转换输入。
- 失败：引用失效或必填字段缺失时阻止转换并保留草稿。
- 验收：AI 建议只是建议；管理员可覆盖、删除或重写。

### REQ-B8-06 转换为 mistake_draft

- 输入：处于可转换状态且已通过人工检查的 capture item。
- 处理：调用专用转换服务，原子地创建一个 `mistake_draft`，建立来源关联并标记转换结果。
- 输出：既有管理端可继续编辑的 `mistake_draft`。
- 失败：转换失败不得创建 `mistake` 或 `review_item`；重复提交不得重复建草稿。
- 验收：capture 只到 `mistake_draft`，不跨越既有人工确认门禁。

### REQ-B8-07 既有确认与复习链复用

- 输入：由 capture 转换而来的 `mistake_draft`。
- 处理：继续使用 `/manage/mistakes` 的既有人工确认流程。
- 输出：确认后生成正式 `mistake`，再由正式错题生成 `review_item`。
- 失败：未确认草稿不得进入复习队列。
- 验收：不新增第二条正式错题或 review item 生成路径。

### REQ-B8-08 失败、重试与最小运行记录

- 输入：一次 OCR/多模态或 AI 草稿请求。
- 处理：记录 capture id、阶段、状态、开始/结束时间、尝试次数、错误分类和安全摘要。
- 输出：管理员可理解失败原因并手动重试。
- 失败：达到最小重试限制后保持 failed，允许编辑已有内容或重新发起。
- 验收：不保存密钥，不建立完整 AI 审计事件系统，不要求生产队列。

### REQ-B8-09 管理端闭环

- 输入：管理员进入 `/manage/capture` 或 `/manage/mistakes/capture`。
- 处理：上传、查看状态、补充错误背景、编辑结果、转换草稿、跳转既有错题管理。
- 输出：单图从上传到 mistake draft 的最小实用闭环。
- 失败：loading/empty/failed/retry/converted 状态均有明确反馈。
- 验收：桌面与移动视口可完成单图闭环，且无批量入口。

### REQ-B8-10 权限与公开边界

- 输入：匿名请求、公开页面请求、管理员请求。
- 处理：capture、OCR、AI、私有附件读取和转换全部由 `get_current_admin` 保护；管理页面使用既有
  `AuthGate`/管理布局。
- 输出：只有管理员可操作；公开读取链路不变。
- 失败：任何匿名 2xx、公开 DTO 泄露 capture/AI/OCR 内容均阻塞。
- 验收：匿名管理 API 为 401/403；公开 `/blog`、`/notes`、`/mistakes` 无新增 AI/OCR 内容或请求噪音。

## 非功能需求

- 安全：原图 private；不记录密钥、绝对路径或敏感供应商响应。
- 一致性：失败不污染下游；转换幂等；下游仍由既有确认服务负责。
- 可恢复：capture 状态、错误和结果可保存；失败后可人工重试。
- 可维护：router thin；调用适配、schema 校验、转换逻辑在服务边界内。
- 可审查：固定输出 schema，最小运行记录，人工确认明确可见。
- 性能：单图、单次处理；不承诺批量吞吐或生产队列 SLA。

## 明确边界

本批不得规划或实现：完整 AI Gateway、多供应商管理、模型路由、Prompt 管理后台、成本统计、
完整 AI 审计事件系统、BKT、完整练习系统、批量 OCR、PDF 多页拆题、公开展示 AI 结果、
旧 `Note(type="mistake")` 迁移、对象存储、云部署、生产级任务队列。

## 总体验收

管理员能上传一张图片并保留 private 原图，观察识别状态，补充自身错因，获得并编辑结构化 AI 草稿，
人工触发生成一个 `mistake_draft`，再沿既有人工确认链生成 `mistake` 与 `review_item`。任一 AI/OCR
失败都不污染下游；匿名和公开页面无法访问相关数据。
