# Personal Learning System V2 设计

## 1. 设计结论

系统从“博客、笔记、错题、复习和 AI 功能的集合”重构为统一的个人学习工作台。知识节点是跨内容、题目、错题、复习、项目和公开文章的连接中心；PostgreSQL 是正式数据的唯一事实来源；GitHub 只承担导出、归档、公开站点构建输入和灾难恢复副本。

登录后的日常入口统一为 `/today`，管理端只承担 AI 治理、审计、系统状态、备份恢复等系统治理工作。

## 2. 目标架构

```text
Next.js Web
  Today / Capture / Learn / Review / Knowledge / Projects / Publish
        |
FastAPI
  Identity / Content / Knowledge / Learning / Review / Search
  Ingestion / Publishing / AI Gateway / Audit / Statistics / Admin
        |
PostgreSQL + Redis
        |
Worker: OCR / AI / Index / Export / Backup / Reports
```

核心数据对象分为：

- `content_items` 与 `content_revisions`
- `knowledge_nodes`、`knowledge_edges`、内容知识关联
- `questions`、`question_attempts`、`mistake_cases`
- `review_items`、`review_events`
- `ingestion_items`、附件、任务和发布快照
- 现有 AI Gateway、Prompt、Task、Validator、AI Run 与审计链路

## 3. Bounded Context 划分

每个 Service 必须属于一个明确的 Bounded Context。跨 Context 的读取通过 query/summary contract，跨 Context 的状态变化通过 command、领域事件或明确的 service facade 完成，不允许直接访问另一个 Context 的内部 model。

| Context | 负责的事实 | 不负责的事实 | 典型服务 |
| --- | --- | --- | --- |
| Identity | 用户、owner、会话、权限、审计身份 | 内容、学习状态 | `IdentityService`、`AuthorizationService` |
| Content | Markdown 正文、标题、版本、可见性 | 知识掌握度、复习调度 | `ContentService` |
| Knowledge | 节点 canonical identity、别名、标签、关系边 | Review、Project、Publish、AI Run 状态 | `KnowledgeService` |
| Learning | 学科、章节、学习会话、项目使用记录 | 知识节点身份、复习排程 | `LearningService`、`ProjectService` |
| Practice | 题目本体、作答事实、练习报告 | 复习时机、知识节点定义 | `QuestionService`、`AttemptService` |
| Mistake | 具体错误、错因、预防规则、关闭条件 | 复习调度算法 | `MistakeService` |
| Review | 复习项、复习事件、下一次复习时间 | 题目正文、错题正文 | `ReviewService`、`ReviewScheduler` |
| Ingestion | 原始输入、附件、OCR 和结构化草稿 | 正式业务对象的最终事实 | `IngestionService`、`OcrService` |
| AI | AI Run、建议、引用、验证和人工审核状态 | 正式内容和知识关系的最终写入 | `AiSuggestionService` |
| Publish | 发布快照、公开版本、撤回和公开索引 | 私有原稿的编辑状态 | `PublishService` |

### 3.1 KnowledgeNode 的边界

`KnowledgeNode` 只负责知识身份和知识关系：

```text
canonical_name
slug
aliases
node_type
subject_id
tags
knowledge_edges
status
```

以下状态不得直接放入 `knowledge_nodes`：

```text
mastery_level / review_due_at
project_status / publish_status
ai_run_id / ai_review_status
mistake_count 的派生快照
```

掌握度属于 Learning/Analytics projection，复习时间属于 Review，项目关联属于 Project，发布状态属于 Publish，AI 建议状态属于 AI。节点详情可以聚合这些信息，但聚合结果不是 KnowledgeNode 的事实字段。

### 3.2 TodayOrchestrator 的边界

Today 是 Dashboard Orchestrator，不拥有学习业务事实。它只负责并行调用并组合以下只读摘要：

```python
ReviewSummaryProvider.get_today()
CaptureSummaryProvider.get_pending()
LearningSummaryProvider.get_active()
MistakeSummaryProvider.get_recent()
ProjectSummaryProvider.get_due()
AiSummaryProvider.get_pending_reviews()
```

`TodayOrchestrator.build_dashboard()` 负责超时、局部失败、摘要排序和响应 DTO；不得创建错题、修改复习、解析 WikiLink 或直接操作 Repository。

## 4. 关键业务流程

### 3.1 今日工作流

`/today` 聚合到期复习、未整理采集、最近错题、学习计划、项目任务和待审核 AI 建议，只展示可执行行动项。

### 3.2 采集工作流

```text
文本 / 图片 / PDF / 网页摘录 / 截图
-> ingestion_items
-> OCR 或结构化整理
-> 用户校正
-> 知识点与对象关联
-> Question / MistakeCase / ContentItem / ReviewItem
```

图片错题使用一页式审核界面，避免在采集、草稿、题目和错题页面之间重复跳转。

### 3.3 知识关系工作流

Markdown 中的 `[[知识点]]` 在保存时解析为内容关联；已有名称或别名直接复用，不存在的名称进入待确认节点。反向链接、局部图谱和全局图谱由关系数据自动生成，不要求手动画线。

### 3.4 错题复习工作流

```text
作答错误
-> mistake_case
-> 绑定知识点
-> 确认错因与预防规则
-> review_item
-> 延迟复习与再次作答
-> 关闭或重新调度
```

复习调度器独立为接口，首版使用最近结果、连续正确次数、严重程度、重要性和逾期情况；未来可替换算法而不改变业务表。

### 3.5 AI 与发布工作流

AI 输出统一经过 `generated -> pending_review -> accepted / rejected`。知识性生成必须保存引用关系。公开文章从私有内容创建发布快照，发布后私有原稿修改不静默改变已经发布的版本。

## 5. 分阶段落地

1. 冻结与审计：数据来源、路由、API、权限、重复内容和写入口清单。
2. 基础架构与安全：环境隔离、统一认证、`owner_id`、CORS、敏感日志过滤、队列和生产托管。
3. 统一数据模型：内容、知识、题目、作答、错题、复习、采集和发布快照。
4. 统一学习工作台：`/today`、`/capture`、`/learn`、`/review`、命令面板和快速记录。
5. 知识库与编辑器：Markdown、WikiLink、反向链接、图谱、模板、版本历史和导入导出。
6. 错题与复习闭环：OCR 审核、结构化题目、错因确认、调度、再做题和统计。
7. AI 管家：关系建议、薄弱点分析、总结、周报、引用和人工接受/拒绝。
8. 发布与迁移切换：快照、隐私检查、导出、旧数据迁移、重定向和只读归档。

每一阶段都必须有独立的 `requirements.md`、`design.md`、`tasks.md`、验收证据和剩余风险；不得把全量重构压成一个不可回滚的大 diff。

## 6. 前后端实现契约

以下函数名是后续实现阶段的最低职责契约。具体模块路径可以随现有代码结构调整，但不得把业务逻辑重新堆进页面或 HTTP router。

### 5.1 前端函数职责

```ts
getTodaySummary(): Promise<TodaySummary>
listIngestionItems(filter: IngestionFilter): Promise<IngestionPage>
createQuickCapture(input: QuickCaptureInput): Promise<IngestionItem>
saveCaptureReview(id: string, input: CaptureReviewInput): Promise<IngestionItem>
resolveWikiLinks(markdown: string): WikiLinkToken[]
saveContentDraft(input: SaveContentInput): Promise<ContentItem>
acceptAiSuggestion(id: string): Promise<AiSuggestion>
submitReview(itemId: string, input: ReviewSubmitInput): Promise<ReviewResult>
publishContent(contentId: string, input: PublishInput): Promise<PublishSnapshot>
```

页面组件只负责调用 hook 或 API client、渲染状态和触发用户动作；DTO、错误码和请求重试策略放在 `src/lib/api/` 或 route service 中。

### 5.2 FastAPI router 职责

```python
GET  /api/today
GET  /api/ingestion
POST /api/ingestion
POST /api/ingestion/{item_id}/review
GET  /api/knowledge/{slug}
POST /api/content
PUT  /api/content/{content_id}
POST /api/review/{item_id}/submit
POST /api/ai/suggestions/{suggestion_id}/accept
POST /api/ai/suggestions/{suggestion_id}/reject
POST /api/publish/{content_id}
POST /api/publish/{snapshot_id}/withdraw
```

router 只负责认证依赖、参数校验、状态码和 service 编排。

### 5.3 Service 函数职责

```python
async def build_today_summary(user_id: UUID, now: datetime) -> TodaySummary:
async def build_today_dashboard(user_id: UUID, now: datetime) -> TodayDashboard:
async def create_ingestion_item(user_id: UUID, command: CreateIngestionCommand) -> IngestionItem:
async def review_ingestion_item(user_id: UUID, item_id: UUID, command: ReviewIngestionCommand) -> StructuredResult:
async def parse_wikilinks(markdown_body: str) -> list[WikiLinkReference]:
async def sync_content_knowledge_links(content_id: UUID, refs: list[WikiLinkReference]) -> None:
async def record_question_attempt(user_id: UUID, question_id: UUID, command: AttemptCommand) -> AttemptResult:
async def create_mistake_case_from_attempt(attempt_id: UUID) -> MistakeCase:
async def schedule_review_item(item_id: UUID, event: ReviewEventCommand) -> ScheduleResult:
async def accept_ai_suggestion(user_id: UUID, suggestion_id: UUID) -> AcceptedSuggestion:
async def create_publish_snapshot(user_id: UUID, content_id: UUID, revision_id: UUID) -> PublishSnapshot:
async def withdraw_publish_snapshot(user_id: UUID, snapshot_id: UUID) -> None:
```

service 必须处理事务边界、owner 校验、状态机、幂等键、审计事件和领域错误；model 不承载跨领域编排。Today 只调用 summary provider，不在自身内部实现业务规则。

### 5.4 Worker 函数职责

```python
async def run_ocr_job(job_id: UUID) -> None:
async def run_ai_suggestion_job(job_id: UUID) -> None:
async def rebuild_search_index(job_id: UUID) -> None:
async def export_markdown_snapshot(job_id: UUID) -> None:
async def run_backup_job(job_id: UUID) -> None:
```

每个任务必须支持重试、超时、错误码、进度和幂等检查；worker 不直接绕过 service 写正式业务状态。

## 7. 每个实现阶段的交付包

每个阶段都必须同时提交以下四类内容：

1. UI：页面、组件、交互状态、空态、错误态、权限降级、响应式和浏览器证据。
2. Backend：model、schema、router、service、错误码、审计和权限测试。
3. Data：migration、索引、约束、回滚和数据完整性检查。
4. Closure：`tasks.md` 勾选、`validation.md`、`audit.md`、剩余风险和下一轮需求。

## 8. UI 与后端的阶段映射

| 阶段 | UI 交付 | 后端函数/模块交付 | 主要证据 |
| --- | --- | --- | --- |
| A 审计 | 路由与入口地图，不改页面 | 数据来源、API、权限和写路径清单 | audit.md |
| B 基础安全 | 登录态、错误和恢复状态规范 | auth、owner、审计、job、backup service | 权限/恢复测试 |
| C 统一模型 | 内容、知识、版本页面 | model/schema/migration/service | 合同和迁移测试 |
| D 工作台 | `/today`、`/capture`、命令面板 | today、ingestion、capture service | 浏览器端到端 |
| E 知识库 | 编辑器、节点详情、图谱 | WikiLink parser、link sync、search | 解析/关系测试 |
| F 闭环 | 错题审核、复习队列、再次作答 | attempt、mistake、scheduler service | 调度和流程测试 |
| G AI | 建议中心、引用和审核控件 | AI suggestion、validator、citation service | Run/审核/脱敏证据 |
| H 发布迁移 | 发布中心、版本、撤回 | snapshot、export、migration service | 哈希/回滚/匿名读取 |

## 9. 设计边界

- Obsidian 只提供 Markdown、WikiLink、反向链接、模板和命令面板等产品参考，不参与运行。
- 不继续维护 PostgreSQL 与 GitHub 两套可独立修改的主数据。
- AI 不直接覆盖正式正文、题目、错题、复习计划或知识关系。
- 不在本任务组内立即实现全部新表、API、页面、队列或生产部署。
- 当前旧模型、旧路由和旧 GitHub 文件流程视为兼容层，须经迁移审计后逐步收敛。
- 关键架构取舍必须记录在 [`docs/adr/`](../../adr/README.md)，实现任务不得用临时约定替代 ADR。
- Legacy 清理必须是独立的 Z 阶段，不能在迁移任务中顺手删除旧代码。
