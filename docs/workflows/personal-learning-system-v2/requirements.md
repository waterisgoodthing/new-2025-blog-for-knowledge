# Personal Learning System V2 需求

## REQ-PLS-001 统一产品主链

问题：用户需要在笔记、错题、复习、AI 和管理入口之间自行判断下一步。

需求：系统必须以 `/today` 作为登录后的日常入口，并能链接采集、学习、复习、项目、知识库和发布。

验收：架构文档明确入口职责、主链和一级导航；后续实现任务不得新增孤立的学习入口。

## REQ-PLS-002 单一事实来源

问题：PostgreSQL、GitHub 文件、AI 草稿和静态博客可能形成重复主数据。

需求：正式数据以 PostgreSQL 为准，GitHub 仅作为导出、归档、构建输入和恢复副本。

验收：迁移设计包含来源清单、去重规则、冲突表、哈希校验、回滚和只读归档流程。

## REQ-PLS-003 统一知识模型

问题：同一知识点可能分散在笔记、题目、错题、复习卡片和文章中。

需求：建立知识节点、关系边和内容关联模型；支持 Markdown WikiLink、别名、反向链接和自动图谱。

验收：设计文档明确节点、边、关联、解析、待确认和关系审核状态。

## REQ-PLS-004 学习闭环

问题：错题记录、错因分析、复习和再次作答之间缺少统一闭环。

需求：题目作答错误可以形成 `mistake_case`，绑定知识点、预防规则和复习项，并通过延迟复习与再次作答改变状态。

验收：流程包含成功、失败、逾期、重新调度和关闭条件；调度器可替换。

## REQ-PLS-005 AI 可追踪与人工审核

问题：AI 结果若直接进入正式数据，会削弱可解释性、可撤销性和安全边界。

需求：AI 输出必须包含 AI Run ID、Prompt/模型版本、依据、置信度和审核状态；事实性生成保存引用。

验收：设计明确 generated、pending_review、accepted、rejected 状态和敏感日志过滤规则。

## REQ-PLS-006 发布可回溯

问题：私有内容修改可能静默改变已发布文章，删除也可能留下公开索引残留。

需求：公开文章通过发布快照生成，并在撤回时同步处理索引、缓存、sitemap 和导出文件。

验收：发布流程能定位源内容、源版本、公开版本和撤回状态。

## REQ-PLS-007 安全与恢复

问题：个人学习数据、附件、AI 输入和复习记录具有私密性，现有双数据源和开发服务不适合作为长期生产基础。

需求：所有私有实体具备 `owner_id`；写操作、AI、复习、上传和删除受后端权限保护；生产环境隔离、备份并可恢复演练。

验收：后续阶段必须提供匿名读取测试、权限测试、敏感字段过滤、软删除恢复、备份和恢复证据。

## REQ-PLS-008 文档驱动执行

问题：全量重构范围大，直接实现会造成不可审查的跨域变更。

需求：先完成现状审计和任务清单审批，再按阶段执行；每个阶段独立设计、实施、验证和风险收口。

验收：本任务组的 `tasks.md` 具备明确编号、依赖、完成标准、验证方式和批准门。

## REQ-PLS-009 UI 可执行设计

问题：只有抽象的信息架构不足以指导页面实施，容易重新产生入口割裂和状态缺失。

需求：每个用户流程必须有页面结构、组件职责、交互状态、响应式布局、可访问性和公开/私有边界设计。

验收：`ui-design.md` 为 `/today`、`/capture`、知识节点、编辑器和复习页提供线框、状态和响应式规则。

## REQ-PLS-010 后端函数契约

问题：只描述表和 API 会让业务逻辑重新堆进 router 或页面，难以测试和迁移。

需求：每个阶段必须明确前端 API client、FastAPI router、service、worker 函数职责、事务边界、错误码、认证和幂等规则。

验收：`design.md` 和 `tasks.md` 为每个核心流程列出可定位到模块的函数级实现任务。

## REQ-PLS-011 前后端对照验收

问题：页面完成不代表 API、权限、数据和异常路径完整。

需求：每个阶段必须同时验收 UI、后端、数据、权限和失败状态，并留下可复核证据。

验收：阶段验收报告按 UI、API、数据库、权限、浏览器和恢复证据分栏记录，不以构建成功替代功能验收。

## REQ-PLS-012 Architecture Boundary

问题：如果页面、router、worker 或 KnowledgeNode 越过职责边界，系统会逐渐形成不可测试的 God Object 和隐式数据写入。

需求：统一遵守以下调用链：

```text
Page / Component
-> Hook / API Client
-> FastAPI Router
-> Application Service
-> Repository
-> PostgreSQL
```

Worker 只能通过 service 或明确的 job handler 改变业务状态；KnowledgeNode 只拥有知识身份、别名、标签和关系；Today 只承担 Dashboard Orchestrator 职责。

验收：代码审查和静态扫描确认页面无直接数据库访问、组件无散落 fetch、router 无业务规则、worker 无绕过 service 的正式写入、KnowledgeNode 无复习/发布/项目状态字段。

## REQ-PLS-013 Bounded Context Ownership

问题：多个领域共享实体名称，但没有明确谁拥有事实，导致跨模块互相写字段。

需求：Identity、Content、Knowledge、Learning、Practice、Mistake、Review、Ingestion、AI 和 Publish 必须有明确的事实归属、读取 contract 和写入边界。

验收：`design.md` 的 Bounded Context 表覆盖所有核心 Service；每个跨 Context 调用可定位到 query、command、event 或 facade。

## REQ-PLS-014 Dashboard Orchestration

问题：Today 聚合过多业务逻辑后会成为不可维护的单体服务。

需求：Today 只能编排 Review、Capture、Learning、Mistake、Project 和 AI 的摘要 provider，负责超时、局部失败、排序和 DTO 组合。

验收：`TodayOrchestrator.build_dashboard()` 不创建或修改领域对象；每个区块可独立超时、失败、重试和验收。

## REQ-PLS-015 Legacy Retirement

问题：V1、V2 和 Compatibility 长期并存会阻止系统收敛。

需求：增加独立 Z 阶段，记录旧页面、旧 API、旧表、旧同步、兼容适配器和 feature flag 的删除条件、迁移证据和回滚窗口。

验收：每项 Legacy 删除都有 owner、前置验证、删除动作、回滚方案和最终验证；未满足条件的项目必须保留并标记原因。

## REQ-PLS-016 Learning Timeline 与 Command Palette

问题：用户需要跨 Review、Capture、Publish、Project 和 AI 结果回看历史，也需要快速跳转和执行高频命令。

需求：提供 Learning Timeline 和 Command Palette，支持时间筛选、对象类型、跳转、创建 Capture、搜索知识和开始 Review。

验收：`ui-design.md` 描述页面结构、快捷键、权限、空态、失败态、键盘操作和移动端降级；后端查询不泄露私有数据。

## 本轮非目标

- 不修改业务代码、数据库模型、迁移、API、配置或部署。
- 不立即删除旧路由、旧表、GitHub 文件或兼容逻辑。
- 不在未完成审计前决定具体表迁移脚本和切换时间。
- 不把 AI、OCR、向量库、RAG 或全自动图谱列为第一阶段强制实现。
