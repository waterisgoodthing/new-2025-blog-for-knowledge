# Personal Learning System V2 详细任务组

## 执行状态与批准门

- 当前状态：Phase A 已执行完成；Phase B 设计文档已完成，Phase B 实施仍等待单独批准。
- 本轮只完成设计文档，不执行任何 `src/`、`backend/`、配置、迁移或部署修改。
- 获得批准后，仍按任务组逐项执行；每完成一项立即更新本文件和验证证据。
- 任何新增表、API、权限、路由、外部服务或数据源都必须先回写 `design.md` / `requirements.md` 并重新审批。

## 任务组 B0：Phase B Architecture Design

### [x] B0-01 Source of Truth 收敛设计

任务编号：B0-01  
完成标准：覆盖 notes、questions、mistakes、review_items、knowledge_points、managed_content_entries、attachments、AI runs，逐项指定当前来源、目标来源和 `preserve/migrate/archive/compatibility-read` 策略。  
执行结果：已完成，见 [`source-of-truth.md`](./source-of-truth.md)。

### [x] B0-02 Owner 覆盖矩阵

任务编号：B0-02  
完成标准：审计私有实体的 `owner_id`、权限边界和迁移必要性，并区分 `created_by` 与 owner。  
执行结果：已完成，见 [`owner-coverage-matrix.md`](./owner-coverage-matrix.md)。

### [x] B0-03 Auth boundary 设计

任务编号：B0-03  
完成标准：覆盖 public、authenticated user、admin、worker，以及 `AUTH_BYPASS`、`ENABLE_REGISTRATION`、`/manage` 和 `/api/admin`。  
执行结果：已完成，见 [`auth-boundary-design.md`](./auth-boundary-design.md)；未修改认证配置。

### [x] B0-04 Schema ownership 决策

任务编号：B0-04  
完成标准：明确 Alembic 与 `Base.metadata.create_all` 的唯一 schema authority 和执行门槛。  
执行结果：已完成，见 [`schema-ownership.md`](./schema-ownership.md)；未修改 `backend/main.py` 或数据库。

### [x] B0-05 Backup validation plan

任务编号：B0-05  
完成标准：设计 `pg_dump` 验证、restore 演练、attachment 恢复验证和 Migration 018 恢复验证，并保持未执行状态。  
执行结果：已完成，见 [`backup-validation-plan.md`](./backup-validation-plan.md)。

### [x] B0-06 Phase B 文档验证与范围确认

任务编号：B0-06  
完成标准：记录文档验证、未执行项和业务代码/数据库变更为 0。  
执行结果：已完成，见 [`validation.md`](./validation.md)。

## 任务组 A：现状审计与冻结

### [x] A-01 数据源与实体盘点

任务编号：A-01  
任务名称：建立旧数据、文件、附件、AI 结果和发布内容清单  
优先级：P0  
来源需求：REQ-PLS-002、REQ-PLS-008  
涉及文件：`docs/workflows/personal-learning-system-v2/audit.md`、`scripts/verify_data/`  
UI 设计：绘制“来源 -> 正式对象 -> 公开输出”的数据流图，标记当前用户可见入口。  
后端实现：实现只读审计函数 `scan_legacy_sources()`、`collect_entity_inventory()`、`calculate_content_hash()`，输出来源、数量、旧 ID、哈希和冲突候选。  
完成标准：每个正式对象能定位来源；重复对象进入 `migration_conflicts` 候选，不自动覆盖。  
验证方式：数据库结构检查、静态文件清单、GitHub 导出清单、正文和附件哈希抽查。  
依赖：无。  
执行结果：已完成只读数据库、模型、迁移、文件系统和 GitHub/Markdown 数据流审计；证据见 `audit/data-inventory.md`。  
风险说明：旧模型与目标模型必须分开标注，不能把目标实体当作已实现事实。

### [x] A-02 路由、API 与权限审计

任务编号：A-02  
任务名称：建立用户入口、写操作、后端路由和认证边界矩阵  
优先级：P0  
来源需求：REQ-PLS-007、REQ-PLS-008  
UI 设计：标记公开页面、管理员页面、学习页面、管理页面和未登录时的降级行为。  
后端实现：实现只读审计函数 `scan_frontend_routes()`、`scan_backend_routes()`、`map_auth_dependencies()`、`find_write_paths()`。  
完成标准：每个写操作都有前端调用、API route、service、认证依赖和审计记录。  
验证方式：源码搜索、路由表、匿名请求和管理员请求对照。  
依赖：A-01。  
执行结果：已完成前端路由、AuthGate、API client、后端 router/service/schema/model 和认证依赖审计；证据见 `audit/access-matrix.md`。  
风险说明：不得误封公开 `/notes`、`/blog`、`/mistakes` 读取层。

### [x] A-03 备份、回滚与切换门槛

任务编号：A-03  
任务名称：冻结迁移前的安全与恢复标准  
优先级：P0  
来源需求：REQ-PLS-002、REQ-PLS-007  
UI 设计：设计备份状态、恢复演练结果、迁移冲突和“停止切换”状态的管理页面。  
后端实现：定义 `BackupService.create_snapshot()`、`BackupService.verify_snapshot()`、`BackupService.restore_snapshot()`、`MigrationGate.can_switch()` 的接口和失败码。  
完成标准：没有备份校验、恢复演练和冲突处理结果时，迁移任务不能进入切写。  
验证方式：备份/恢复演练设计、失败注入、门槛状态机审查。  
依赖：A-01、A-02。  
执行结果：已完成 Alembic、备份文档、上传目录、恢复记录和 migration 风险审计；Migration Gate 当前为 `BLOCKED`；证据见 `audit/migration-gate.md`。  
风险说明：本任务先建立契约，未经批准不得执行真实删除或切换。

## 任务组 B：统一数据与后端基础

本组的 B-01、B-02、B-03 是 Epic；实际执行必须以下列可独立验收的子任务为单位推进。

### [ ] B-01 ContentItem 与版本

任务编号：B-01  
任务名称：建立统一内容、版本和软删除模型  
优先级：P0  
来源需求：REQ-PLS-002、REQ-PLS-003、REQ-PLS-006  
UI 设计：设计内容列表、编辑器、版本抽屉、差异查看、恢复确认和发布状态组件。  
后端实现：新增 `ContentRepository`、`ContentService.create()`、`ContentService.update()`、`ContentService.create_revision()`、`ContentService.restore_revision()`；router 只做认证、校验和状态码。  
完成标准：正文、slug、visibility、revision、deleted_at 和 owner 可追踪；公开快照不被私有编辑静默改写。  
验证方式：Alembic migration、schema/API contract、版本恢复、owner 和软删除测试。  
依赖：A-03。  
风险说明：保留旧 Note 兼容读路径和回滚策略。

### [ ] B-02 KnowledgeNode 与关系

任务编号：B-02  
任务名称：建立知识节点、别名、关系边和内容关联  
优先级：P0  
来源需求：REQ-PLS-003  
UI 设计：设计知识节点详情、关系编辑、反向链接、关系审核和孤立节点空态。  
后端实现：实现 `KnowledgeService.resolve_node()`、`KnowledgeService.create_or_get_alias()`、`KnowledgeService.create_edge()`、`KnowledgeService.rebuild_backlinks()`、`KnowledgeService.get_local_graph()`。  
完成标准：节点名称唯一、别名可查、边可审计、关系可反向查询。  
验证方式：唯一约束、别名冲突、关系权限、删除节点和局部图谱测试。  
依赖：B-01。  
风险说明：首版不引入图数据库，不允许自由 JSON 取代关系表。

### [ ] B-03 搜索与查询层

任务编号：B-03  
任务名称：建立 PostgreSQL 全文、trigram 和结构化过滤查询  
优先级：P1  
来源需求：REQ-PLS-003、REQ-PLS-011  
UI 设计：设计全局搜索、筛选栏、结果分组、无结果、权限过滤和搜索失败状态。  
后端实现：实现 `SearchService.search_full_text()`、`SearchService.search_fuzzy()`、`SearchService.apply_filters()`、`SearchService.reindex_content()`。  
完成标准：标题、正文、标签、知识点、题干、错因和来源可检索，私有内容不泄露。  
验证方式：索引迁移、中文/英文/别名搜索、匿名过滤和排序测试。  
依赖：B-01、B-02。  
风险说明：首版不引入向量库或 RAG。

### [ ] B-01.1 Content migration 与约束

任务编号：B-01.1  
任务名称：建立 `content_items`、`content_revisions`、owner、visibility 和软删除迁移  
优先级：P0  
来源需求：REQ-PLS-002、REQ-PLS-007、REQ-PLS-012  
涉及文件：`backend/app/models/`、`backend/alembic/versions/`、迁移测试  
修改内容：定义表、索引、外键、唯一约束、软删除和旧 Note 映射占位。  
完成标准：迁移可重复执行、可回滚；匿名读取不会返回私有或已删除内容。  
验证方式：Alembic upgrade/downgrade、约束测试、公开/私有查询测试。  
依赖：A-03。

### [ ] B-01.2 Content schema 与 repository

任务编号：B-01.2  
任务名称：实现内容 schema、repository 和版本事务  
优先级：P0  
来源需求：REQ-PLS-003、REQ-PLS-010、REQ-PLS-012  
涉及文件：`backend/app/schemas/`、`backend/app/services/`、`backend/app/repositories/`  
修改内容：实现 `ContentRepository`、`ContentService.create/update/create_revision/restore_revision` 和版本冲突错误。  
完成标准：service 处理 owner、事务、版本号、幂等和审计；repository 不包含 HTTP 逻辑。  
验证方式：service 单测、并发版本冲突、owner 越权和恢复测试。  
依赖：B-01.1。

### [ ] B-01.3 Content API 与 API client

任务编号：B-01.3  
任务名称：实现内容 router、DTO 和前端 API client  
优先级：P0  
来源需求：REQ-PLS-009、REQ-PLS-010、REQ-PLS-012  
涉及文件：`backend/app/routers/`、`src/lib/api/`、内容页面  
修改内容：接入 create/update/revision/restore API；页面只经 hook/API client 访问后端。  
完成标准：router 只做认证、校验、service 编排和状态码；组件不直接 fetch。  
验证方式：OpenAPI 对照、TypeScript 检查、匿名/管理员 API 测试。  
依赖：B-01.2。

### [ ] B-01.4 Content UI 与版本验收

任务编号：B-01.4  
任务名称：实现内容列表、编辑器、版本抽屉和恢复确认  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011  
涉及文件：内容 route、route-specific components、`ui-design.md` 对应页面  
修改内容：实现 loading/empty/error/conflict/saved 状态、版本 diff、恢复和发布状态。  
完成标准：编辑、保存、冲突、恢复和公开边界可在浏览器完成。  
验证方式：桌面/移动浏览器、键盘、长正文、断网和冲突验收。  
依赖：B-01.3。

### [ ] B-02.1 Knowledge migration 与纯模型

任务编号：B-02.1  
任务名称：建立纯 KnowledgeNode、alias、edge 和 link 表  
优先级：P0  
来源需求：REQ-PLS-003、REQ-PLS-012、REQ-PLS-013  
涉及文件：`backend/app/models/`、`backend/alembic/versions/`  
修改内容：禁止把 mastery、review、project、publish、AI 状态写入节点表。  
完成标准：知识模型只拥有身份、标签、别名和关系；跨域状态通过关联或 projection 查询。  
验证方式：模型字段审查、迁移约束、关系完整性测试。  
依赖：B-01.1。

### [ ] B-02.2 Knowledge service 与 query contract

任务编号：B-02.2  
任务名称：实现节点解析、别名、关系和反向链接 service  
优先级：P0  
来源需求：REQ-PLS-003、REQ-PLS-010、REQ-PLS-013  
涉及文件：`backend/app/services/knowledge/`、query schemas  
修改内容：实现 `resolve_node/create_or_get_alias/create_edge/rebuild_backlinks/get_local_graph`。  
完成标准：跨 Context 只通过 query contract 读取，不直接访问内部 repository。  
验证方式：别名冲突、关系审核、幂等、权限和图谱投影测试。  
依赖：B-02.1。

### [ ] B-02.3 Knowledge API 与 UI

任务编号：B-02.3  
任务名称：实现知识节点详情、关系编辑和图谱降级界面  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011  
涉及文件：知识库 route、`src/lib/api/`、知识组件  
修改内容：显示节点身份与聚合摘要；关系 API 失败时回退为列表。  
完成标准：不把复习/项目/发布状态伪装成节点字段。  
验证方式：局部失败、孤立节点、移动端、公开/私有和键盘验收。  
依赖：B-02.2。

### [ ] B-03.1 Search index migration

任务编号：B-03.1  
任务名称：建立全文、trigram 和过滤索引  
优先级：P1  
来源需求：REQ-PLS-003、REQ-PLS-012  
涉及文件：数据库 migration、`SearchRepository`、索引脚本  
修改内容：为标题、正文、标签、知识点、题干、错因和来源建立查询索引。  
完成标准：索引可重建，私有和已删除数据不进入公开查询。  
验证方式：迁移、重建、中文/英文/别名和权限过滤测试。  
依赖：B-01.1、B-02.1。

### [ ] B-03.2 Search API 与全局搜索 UI

任务编号：B-03.2  
任务名称：实现搜索 service、API client、筛选栏和结果分组  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011、REQ-PLS-016  
涉及文件：搜索 route、`SearchService`、`src/lib/api/`  
修改内容：实现全文/模糊/结构化过滤、无结果、局部失败和权限降级。  
完成标准：搜索结果可跳转到正确对象，不暴露私有内容。  
验证方式：浏览器、API、排序、长标题和无结果验收。  
依赖：B-03.1。

## 任务组 C：今日工作台与采集

### [ ] C-01 `/today` 行动总览

任务编号：C-01  
任务名称：实现今日工作台页面、数据聚合和局部失败状态  
优先级：P0  
来源需求：REQ-PLS-001、REQ-PLS-009、REQ-PLS-011  
UI 设计：实现今日目标、到期复习、待整理采集、最近错题、进行中项目和 AI 待审核区块；每个区块有 loading/empty/error/busy/success。  
后端实现：实现 `TodayService.build_summary()`、`TodayService.get_due_reviews()`、`TodayService.get_pending_ingestions()`、`TodayService.get_recent_mistakes()`；提供 `GET /api/today`。  
完成标准：登录后默认进入 `/today`，区块失败不阻断其他行动入口，未知数量不显示为 0。  
验证方式：真实浏览器桌面/移动、匿名 401、局部 API 失败、空数据和恢复刷新。  
依赖：B-01、B-02、B-03。

### [ ] C-02 统一采集箱

任务编号：C-02  
任务名称：实现快速记录、文本、截图和文件导入  
优先级：P0  
来源需求：REQ-PLS-001、REQ-PLS-004、REQ-PLS-009  
UI 设计：实现采集方式切换、待处理列表、详情审核栏、原图/OCR 对照、保存草稿和失败保留输入。  
后端实现：实现 `IngestionService.create_item()`、`IngestionService.update_review()`、`IngestionService.transition_status()`、`IngestionService.attach_file()`、`POST /api/ingestion` 和 `POST /api/ingestion/{id}/review`。  
完成标准：所有未经整理输入先进入 `ingestion_items`，高风险对象必须经人工确认。  
验证方式：重复提交幂等、文件类型错误、超时、未认证、移动端和本地草稿恢复测试。  
依赖：A-02、B-01。

### [ ] C-03 OCR 与结构化审核

任务编号：C-03  
任务名称：实现图片错题的一页式 OCR 审核流程  
优先级：P1  
来源需求：REQ-PLS-004、REQ-PLS-005、REQ-PLS-009  
UI 设计：原图、OCR 文本、题干、选项、答案、用户答案、知识点候选和错因候选同屏展示；支持逐项接受/拒绝。  
后端实现：实现 `OcrService.create_job()`、`OcrService.persist_result()`、`CaptureService.build_question_draft()`、`CaptureService.build_mistake_draft()`、worker `run_ocr_job()`。  
完成标准：OCR/AI 只生成草稿，不直接写正式题目或错题；失败可重试且保留原始附件。  
验证方式：OCR 成功/失败、字段校正、重试、AI 不可用和草稿状态测试。  
依赖：C-02、B-01。

## 任务组 D：知识库与编辑器

本组的 D-01、D-02、D-03 是 Epic；实际执行必须拆成 parser、service、API、UI 和验证子任务。

### [ ] D-01 WikiLink 解析与编辑补全

任务编号：D-01  
任务名称：实现 Markdown WikiLink、标签和知识点自动补全  
优先级：P1  
来源需求：REQ-PLS-003、REQ-PLS-009、REQ-PLS-010  
UI 设计：编辑器双栏、补全菜单、未确认节点标记、引用插入和保存状态提示。  
后端实现：实现 `parse_wikilinks()`、`sync_content_knowledge_links()`、`suggest_nodes()`、`POST /api/content/{id}/resolve-links`。  
完成标准：名称、别名、显示文本和位置可保存；未确认链接不会丢失。  
验证方式：解析单测、中文别名、重复保存幂等、冲突和权限测试。  
依赖：B-01、B-02。

### [ ] D-02 反向链接与知识图谱

任务编号：D-02  
任务名称：实现节点上下文、反向链接和局部/全局图谱  
优先级：P1  
来源需求：REQ-PLS-003、REQ-PLS-009  
UI 设计：节点页正文、关系摘要、相关题目/错题/复习和图谱标签页；图谱加载失败时回退为关系列表。  
后端实现：实现 `KnowledgeService.get_backlinks()`、`get_related_content()`、`get_graph_projection()`、`GET /api/knowledge/{slug}/backlinks`。  
完成标准：任意节点能聚合笔记、题目、错题、项目和复习状态。  
验证方式：关系查询、权限、孤立节点、节点删除和图谱降级测试。  
依赖：D-01、B-03。

### [ ] D-03 版本化 Markdown 编辑器

任务编号：D-03  
任务名称：实现编辑、预览、自动保存、历史版本和 AI 对比  
优先级：P1  
来源需求：REQ-PLS-003、REQ-PLS-005、REQ-PLS-009  
UI 设计：编辑/预览分栏、右侧上下文栏、自动保存状态、版本差异、恢复确认和专注模式。  
后端实现：实现 `ContentService.autosave()`、`create_revision()`、`diff_revisions()`、`restore_revision()`；API 返回版本号和冲突错误 `CONTENT_REVISION_CONFLICT`。  
完成标准：并发编辑不静默覆盖，AI 修改以 diff 或草稿呈现。  
验证方式：自动保存、断网恢复、版本冲突、恢复和键盘可达测试。  
依赖：B-01、D-01。

### [ ] D-01.1 Markdown parser

任务编号：D-01.1  
任务名称：实现 WikiLink、alias、anchor 和待确认节点解析器  
优先级：P0  
来源需求：REQ-PLS-003、REQ-PLS-010、REQ-PLS-012  
涉及文件：`packages/markdown/` 或现有 markdown utility、parser tests  
修改内容：输出稳定 token、位置、显示文本和 canonical 候选，不执行数据库写入。  
完成标准：解析器纯函数可独立测试，未知链接保留原文。  
验证方式：中文、别名、嵌套标点、代码块排除和快照测试。  
依赖：B-02.1。

### [ ] D-01.2 Link sync service

任务编号：D-01.2  
任务名称：实现内容保存后的知识关联同步  
优先级：P0  
来源需求：REQ-PLS-003、REQ-PLS-013  
涉及文件：Content/Knowledge service、事务测试  
修改内容：实现 `sync_content_knowledge_links()`、未知节点待确认、旧链接清理和幂等。  
完成标准：内容保存与关联更新在明确事务边界内完成，失败可回滚正文关联。  
验证方式：新增/删除/改名链接、事务失败和重复保存测试。  
依赖：D-01.1、B-02.2。

### [ ] D-01.3 Editor completion UI

任务编号：D-01.3  
任务名称：实现编辑器自动补全、保存状态和关联提示  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011  
涉及文件：编辑器 route components、API client  
修改内容：补全菜单、未确认链接提示、保存中/已保存/失败和重试。  
完成标准：键盘可完成补全，保存失败不丢失正文。  
验证方式：键盘、移动端、断网、长正文和补全冲突验收。  
依赖：D-01.2。

### [ ] D-02.1 Graph projection

任务编号：D-02.1  
任务名称：实现局部图谱和反向链接查询投影  
优先级：P1  
来源需求：REQ-PLS-003、REQ-PLS-013  
涉及文件：Knowledge query service、图谱 DTO、索引/缓存策略  
修改内容：提供 `get_backlinks/get_related_content/get_graph_projection`，不引入 GraphDB。  
完成标准：查询结果来自关系表，图谱可重算。  
验证方式：关系增删、孤立节点、权限、重算和性能基线测试。  
依赖：B-02.2、D-01.2。

### [ ] D-02.2 Graph and backlinks UI

任务编号：D-02.2  
任务名称：实现节点页反向链接、关系列表和图谱标签页  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011  
涉及文件：知识节点 route、图谱组件、移动端布局  
修改内容：图谱加载失败回退为列表；聚合 Review、Mistake、Project 状态但不修改其事实。  
完成标准：节点页在图谱不可用时仍能完成导航和关联查看。  
验证方式：浏览器、局部失败、窄屏和公开边界验收。  
依赖：D-02.1。

## 任务组 E：题目、错题与复习

本组的 E-01、E-02、E-03 是 Epic；实际执行必须按题目、错题、调度、API、UI 和验收拆分。

### [ ] E-01 题目与作答记录

任务编号：E-01  
任务名称：实现题目本体、作答事实和置信度记录  
优先级：P0  
来源需求：REQ-PLS-004、REQ-PLS-010  
UI 设计：题目详情、作答界面、答案揭示、耗时、置信度和“记录为错题”动作。  
后端实现：实现 `QuestionService.create()`、`QuestionService.get_for_practice()`、`AttemptService.record()`、`POST /api/questions/{id}/attempts`。  
完成标准：题目不保存某次作答；每次作答可独立追踪。  
验证方式：正确/错误、重复作答、耗时、并发提交和权限测试。  
依赖：B-01、B-02。

### [ ] E-02 MistakeCase 错因闭环

任务编号：E-02  
任务名称：实现具体错题、错因确认和预防规则  
优先级：P0  
来源需求：REQ-PLS-004、REQ-PLS-009  
UI 设计：错题详情分为题目、我的答案、正确方法、错因、预防规则、关联知识点和复习状态；AI 建议可逐条接受/拒绝。  
后端实现：实现 `MistakeService.create_from_attempt()`、`update_analysis()`、`bind_knowledge_nodes()`、`close_if_eligible()`、`POST /api/mistakes/{id}/analysis`。  
完成标准：错题不能只以 Markdown 文本承载核心字段；关闭必须满足规则。  
验证方式：字段校验、AI 不可用、关闭条件、恢复和公开/私有权限测试。  
依赖：E-01、B-02、C-03。

### [ ] E-03 ReviewScheduler 与复习页面

任务编号：E-03  
任务名称：实现复习队列、提交结果、调度和再次作答  
优先级：P0  
来源需求：REQ-PLS-004、REQ-PLS-007、REQ-PLS-009  
UI 设计：今日队列、专注复习卡、四种结果按钮、下一次复习时间、进度、撤销和历史统计。  
后端实现：实现 `ReviewScheduler.schedule()`、`ReviewService.list_due()`、`ReviewService.submit_event()`、`ReviewService.undo_event()`、`GET/POST /api/review`。  
完成标准：复习状态只由 `review_items` 和 `review_events` 作为事实来源；调度算法可替换。  
验证方式：遗忘/困难/记住/简单、逾期、重复提交、撤销、跨时区和权限测试。  
依赖：E-02、B-02。

### [ ] E-01.1 Question model 与 API

任务编号：E-01.1  
任务名称：建立题目本体、来源和知识点关联  
优先级：P0  
来源需求：REQ-PLS-004、REQ-PLS-010、REQ-PLS-012  
涉及文件：Question model/schema/repository/router/migration  
修改内容：实现题目 CRUD、来源、难度、options/answer/solution 和知识关联。  
完成标准：题目本体不保存某次作答和复习状态。  
验证方式：schema、owner、来源字段、关联约束和 API contract 测试。  
依赖：B-02.1。

### [ ] E-01.2 Attempt service

任务编号：E-01.2  
任务名称：实现独立作答事实和重复提交幂等  
优先级：P0  
来源需求：REQ-PLS-004、REQ-PLS-012  
涉及文件：Attempt model/service/router、作答 API client  
修改内容：实现 `AttemptService.record()`、耗时、置信度、正确性和 session 关联。  
完成标准：每次作答独立可追踪，重复请求不会产生重复事实。  
验证方式：正确/错误、重复提交、并发和权限测试。  
依赖：E-01.1。

### [ ] E-01.3 Practice UI

任务编号：E-01.3  
任务名称：实现题目作答、答案揭示和记录错题入口  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011  
涉及文件：practice route、question components、API client  
修改内容：展示题目、提交、耗时、置信度、答案揭示和记录为错题。  
完成标准：作答成功/失败/重复提交有明确反馈。  
验证方式：桌面/移动、键盘、网络失败和长题干验收。  
依赖：E-01.2。

### [ ] E-02.1 MistakeCase service

任务编号：E-02.1  
任务名称：实现从 Attempt 创建具体错题和错因状态机  
优先级：P0  
来源需求：REQ-PLS-004、REQ-PLS-012  
涉及文件：Mistake model/schema/service/router/migration  
修改内容：实现 `create_from_attempt/update_analysis/bind_knowledge_nodes/close_if_eligible`。  
完成标准：核心字段一等存储，状态转换可审计，关闭条件不可绕过。  
验证方式：字段、状态机、owner、公开/私有和恢复测试。  
依赖：E-01.2、B-02.2。

### [ ] E-02.2 Mistake review UI

任务编号：E-02.2  
任务名称：实现错题详情、错因确认和预防规则编辑  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011  
涉及文件：mistake route、components、API client  
修改内容：展示题目、我的答案、正确方法、错因、预防规则、关联知识点和复习状态。  
完成标准：AI 建议逐条审核，保存失败保留输入，未登录不出现管理操作。  
验证方式：浏览器、权限、空态、错误态、AI 不可用和长文本验收。  
依赖：E-02.1。

### [ ] E-03.1 ReviewScheduler contract

任务编号：E-03.1  
任务名称：实现可替换复习调度器和时间边界  
优先级：P0  
来源需求：REQ-PLS-004、REQ-PLS-012  
涉及文件：Review model/service、scheduler protocol、migration  
修改内容：实现 `ReviewScheduler.schedule()`、四种结果、逾期、时区和 scheduler_version。  
完成标准：调度器不修改题目/错题正文，review_items/events 是唯一复习事实。  
验证方式：结果矩阵、逾期、时区、重复提交和回滚测试。  
依赖：E-02.1。

### [ ] E-03.2 Review API

任务编号：E-03.2  
任务名称：实现复习队列、提交、撤销和历史 API
优先级：P0  
来源需求：REQ-PLS-007、REQ-PLS-010  
涉及文件：Review router/schema/service/API client  
修改内容：实现 `list_due/submit_event/undo_event`、认证、幂等和审计。  
完成标准：未认证不能读取或提交私有复习数据。  
验证方式：匿名 401、越权 403、重复请求、审计和 API contract 测试。  
依赖：E-03.1。

### [ ] E-03.3 Review UI

任务编号：E-03.3  
任务名称：实现专注复习卡、结果按钮、进度和历史  
优先级：P1  
来源需求：REQ-PLS-009、REQ-PLS-011  
涉及文件：review route、review components、移动端布局  
修改内容：实现 loading/empty/error/busy/success、撤销、下一次时间和返回今日上下文。  
完成标准：用户可从今日开始、完成、撤销一次复习并回到原上下文。  
验证方式：真实浏览器、键盘、窄屏、失败重试和公开页面边界验收。  
依赖：E-03.2。

## 任务组 F：AI 建议与发布

### [ ] F-01 AI 建议中心

任务编号：F-01  
任务名称：实现知识关系、薄弱点、总结和周报建议中心  
优先级：P1  
来源需求：REQ-PLS-005、REQ-PLS-009  
UI 设计：建议列表、依据、关联对象、置信度、AI Run、接受/拒绝、重试和结果 diff。  
后端实现：实现 `AiSuggestionService.create()`、`validate_output()`、`accept()`、`reject()`、`retry()`、`CitationService.attach()`。复用现有 AI Gateway 和审计链路。  
完成标准：AI 不直接覆盖正式数据，所有结果可追踪、可审核、可撤销。  
验证方式：Provider 失败、Validator 失败、敏感日志、引用缺失、接受/拒绝和重试测试。  
依赖：B-01、B-02、E-02。

### [ ] F-02 发布快照与撤回

任务编号：F-02  
任务名称：实现私有内容选择性发布、快照和撤回  
优先级：P1  
来源需求：REQ-PLS-006、REQ-PLS-007  
UI 设计：发布检查清单、隐私字段提醒、源版本、公开预览、发布状态和撤回确认。  
后端实现：实现 `PublishService.validate_privacy()`、`create_snapshot()`、`withdraw_snapshot()`、`invalidate_public_indexes()`、`POST /api/publish/{id}`。  
完成标准：公开版本对应明确源版本；撤回后不残留公开索引。  
验证方式：匿名读取、版本对照、撤回、缓存/sitemap/export 一致性测试。  
依赖：B-01、D-03。

## 任务组 G：迁移、部署与收口

### [ ] G-01 旧数据迁移与冲突处理

任务编号：G-01  
任务名称：执行只读迁移、人工冲突处理和切换演练  
优先级：P0  
来源需求：REQ-PLS-002、REQ-PLS-007、REQ-PLS-008  
UI 设计：迁移进度、冲突队列、对象对比、人工选择、回滚状态和只读归档入口。  
后端实现：实现 `MigrationService.plan()`、`dry_run()`、`resolve_conflict()`、`verify_counts()`、`switch_write_source()`、`archive_legacy_source()`。  
完成标准：PostgreSQL 成为唯一事实来源，所有迁移对象有映射、哈希和审计。  
验证方式：数量/哈希/外键/正文/附件抽查、回滚演练和旧 URL 检查。  
依赖：A-03、B-01、E-03、F-02。

### [ ] G-02 生产运行与备份恢复

任务编号：G-02  
任务名称：建立生产进程、健康检查、日志和备份恢复流程  
优先级：P0  
来源需求：REQ-PLS-007、REQ-PLS-011  
UI 设计：系统状态、任务状态、备份状态、失败原因、恢复演练和只读治理页面。  
后端实现：实现 `HealthService.check_dependencies()`、`JobService.enqueue()`、`JobService.retry()`、`BackupService.verify_restore()`，并接入 worker 和结构化日志。  
完成标准：生产不依赖 dev server、reload 或 quick tunnel；异常可发现、可重启、可恢复。  
验证方式：生产构建、健康检查、任务失败重试、备份恢复、敏感日志审查。  
依赖：A-03、C-03、F-01。

### [ ] G-03 阶段验收与下一轮需求

任务编号：G-03  
任务名称：完成每阶段验收、剩余风险和下一轮需求回写  
优先级：P0  
来源需求：REQ-PLS-008、REQ-PLS-011  
UI 设计：验收证据按页面、状态、浏览器视口和公开边界归档。  
后端实现：验收 API、权限、数据库、任务、备份和日志证据；不新增业务功能。  
完成标准：需求、设计、任务、执行、验收、风险和下一轮需求七项齐全。  
验证方式：`validation.md`、`audit.md`、风险清单和下一轮需求审查。  
依赖：所有阶段任务。

## 任务组 Z：Legacy 清理与架构收口

Z 阶段只能在 G-01 迁移切换、公开内容回归、权限回归、备份恢复和运行稳定窗口完成后执行。Z 阶段的目标是删除已经没有事实责任的旧实现，不是继续扩展 V2 功能。

### [ ] Z-01 Legacy 页面与入口清理

任务编号：Z-01  
任务名称：删除已被 `/today`、`/capture`、`/knowledge`、`/review` 替代的旧页面和重复入口  
优先级：P0  
来源需求：REQ-PLS-015、REQ-PLS-016  
UI 设计：旧链接先显示明确迁移提示或重定向；确认无流量后移除导航、入口和 feature flag。  
后端实现：实现 `LegacyRetirementService.verify_no_references()`、`redirect_legacy_route()`、`remove_route_flag()`。  
完成标准：旧页面没有唯一业务能力；旧 URL 已有重定向或明确归档。  
验证方式：路由扫描、日志访问量、浏览器旧链接、导航和公开边界回归。  
依赖：G-01、G-03。

### [ ] Z-02 Legacy API、表与同步适配器清理

任务编号：Z-02  
任务名称：删除旧 API、兼容表、GitHub 主写入逻辑和无效同步适配器  
优先级：P0  
来源需求：REQ-PLS-002、REQ-PLS-012、REQ-PLS-015  
UI 设计：治理页面显示删除前检查、依赖引用、备份版本和不可逆操作确认。  
后端实现：实现 `LegacyRetirementService.find_dependents()`、`prepare_drop_plan()`、`archive_schema()`、`remove_sync_writer()`；每项删除必须有 migration。  
完成标准：PostgreSQL 是唯一写入源；旧表和旧 API 没有仍在使用的调用方。  
验证方式：全仓引用扫描、API 访问日志、数据库依赖、迁移 dry-run 和恢复演练。  
依赖：Z-01、G-01、G-02。

### [ ] Z-03 Legacy 清理最终验收

任务编号：Z-03  
任务名称：完成 V1/V2/Compatibility 收口报告  
优先级：P0  
来源需求：REQ-PLS-008、REQ-PLS-015  
UI 设计：归档清理前后路由、导航、数据来源和系统状态对照图。  
后端实现：执行健康检查、公开读取、私有写入、AI、复习、备份和恢复全量回归；不新增业务逻辑。  
完成标准：每项 Legacy 删除都有证据、回滚窗口和最终状态；未删除项都有明确原因和下一轮需求。  
验证方式：`validation.md`、`audit.md`、ADR 索引和风险清单完整。  
依赖：Z-01、Z-02。
