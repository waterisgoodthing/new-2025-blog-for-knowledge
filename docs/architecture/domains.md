# 功能域边界

> 本文描述目标架构。未落地部分均为待实现；当前 `Note(type="mistake")` 等行为按兼容旧系统处理。

## 系统边界总览

系统分为公开内容面和私有学习管理面。公开面只拥有博客与明确公开的笔记/文章读取；科目、题库、练习、错题、复习、附件、OCR、AI runs、草稿、任务、统计和设置默认属于私有面。两者可以共享渲染、附件元数据和后端基础设施，但不能共享不受控的数据契约。

新增目标域包括 Subject、Capture/OCR、Draft Review、Job Queue、Search、Analytics/Report 和 Settings；详细边界见各专项文档。

## 边界总览

内容发布、知识笔记、题库、练习、错题、复习和 AI 是不同功能域。题库存题，练习存一次做题行为，错题存需要复盘的结果，复习存调度状态与历史，AI 描述辅助处理过程。任何域都不得仅因页面相似而共享同一业务实体。

| 功能域 | 核心实体 | 主要产出 |
|---|---|---|
| Content Publishing | `posts` | 可公开发布的文章 |
| Knowledge Notes | `notes` | 知识笔记 |
| Question Bank | `questions`、`question_sources` | 可复用题目本体与来源 |
| Practice System | `practice_sessions`、`practice_attempts`、`practice_reports`、`practice_import_jobs` | 练习记录、导入与报告 |
| Mistake System | `mistakes` | 错题与复盘 |
| Review System | `review_items`、`review_records` | 学习状态、历史与队列；第一版由 `review_items.next_review_at` 调度 |
| AI Assistant | `ai_runs` | 可追踪的 AI 任务与结果 |
| Media / Attachments | `attachments` | 文件元数据与引用 |
| Taxonomy | `tags`、`taggings`、`subjects`、`knowledge_points`、`knowledge_point_links`、`knowledge_relations` | 业务对象归类与知识点关系 |
| Auth / Admin | `sessions`、`audit_logs` | 脚本生成通行密钥、单管理员会话与审计 |

## 1. Content Publishing

**负责什么**

- 文章草稿、发布、撤回、摘要、封面、公开 slug 和发布时间。
- `/blog` 公开展示与后台文章管理。
- 面向读者的稳定公开内容契约。

**不负责什么**

- 不承载个人笔记或错题字段。
- 不负责复习调度、AI 运行状态或文件存储实现。
- 不以 GitHub 文件同步替代领域模型；同步若保留，只是输出适配器。

**与其他域的关系**

- 通过 Taxonomy 获得标签和知识关联。
- 通过 Media / Attachments 引用封面和正文附件。
- 可由 AI Assistant 辅助润色，但发布决策始终属于本域。
- 写入操作由 Auth / Admin 保护。

## 2. Knowledge Notes

**负责什么**

- 保存个人知识笔记、摘要、正文、可见性、状态和稳定 slug。
- 支持笔记之间以及笔记与知识点之间的关联。
- 允许明确选择公开的笔记进入 `/notes`。

**不负责什么**

- 不模拟公开文章发布流程。
- 不承载错题专属的题目、作答、正确答案和错因。
- 不直接保存 SM-2 等复习算法状态。

**与其他域的关系**

- 使用 Taxonomy 组织知识。
- 可通过 Review System 被创建为复习项目，但笔记正文仍归本域。
- 可关联附件和 AI 运行结果。

## 3. Question Bank

**负责什么**

- 保存题目本体，并维护来源、学科、难度、知识点、状态与可见性。
- 使用规范化文本或 `canonical_hash` 支持题目去重和复用。
- 为练习记录、错题记录和复习对象提供稳定题目基础数据。
- 做对和做错的题都可以进入题库。

**不负责什么**

- 不记录用户每次作答，不判断用户是否做错。
- 不安排复习、生成复习计划或直接调用 AI。
- 不等于错题系统；题库题目不因被收录就自动成为错题。

**与其他域的关系**

- Practice Attempt 引用 Question 并记录一次作答。
- Mistake 可引用 Question，但只增加错题特有的复盘信息。
- Review 可在未来直接引用 Question；首期仍以已确认 Mistake 为主要来源。
- AI 可建议新题、拆题与去重候选，写入前必须结构化校验并由用户确认。

## 4. Practice System

**负责什么**

- 记录一次练习 `practice_session` 以及每道题的 `practice_attempt`。
- 支持图片、PDF、文本和批改结果的练习导入。
- 保存正确、错误、半对结果以及本次练习分析和报告。
- 将错误作答转换为 `mistake_drafts`，经用户确认后交给 Mistake System。
- 为复习系统提供练习来源依据。

**不负责什么**

- 不维护正式错题内容，不实现复习算法。
- 不负责公开文章展示、笔记编辑或 AI prompt 和模型调用底层实现。
- 不把所有题目都转成错题。

**与其他域的关系**

- 使用 Question Bank 保存和复用题目本体。
- 错误或需复盘的 Attempt 可生成 Mistake Draft；正式 Mistake 必须经用户确认。
- AI Assistant 负责识别、拆题、批改、分析与报告，Practice System 负责校验和编排落库。

## 5. Mistake System

**负责什么**

- 管理需要复盘的错题及错题特有的错因、解析、知识点和状态。
- 支持单题错题导入，并承接练习系统产生的 `mistake_drafts`。
- 管理草稿确认、正式错题详情、编辑、公开状态和隐藏状态。

**不负责什么**

- 不作为 `notes` 的一种 `type`。
- 不负责多题练习导入、题目本体去重、完整做题记录或做对题目的保存。
- 不生成练习报告、每日练习统计、复习队列或复习算法。
- 不拥有复习间隔、下次复习时间或历史复习成绩。
- 不要求先完成 AI 分析才能保存。

**与其他域的关系**

- 可关联 Question、Practice Attempt、Subject 和 Knowledge Point。
- Review System 以错题 ID 创建学习项目。
- AI Assistant 可生成分析建议，人工确认后再写入业务字段。
- 图片由 Attachments 管理。

## 6. Review System

**负责什么**

- 把可学习实体注册为 `review_items`。
- 管理调度算法参数、下次复习时间、暂停/完成状态。
- 记录每次评分、前后状态和复习时间，生成队列与统计。

**不负责什么**

- 不直接拥有或复制错题、笔记的正文。
- 不决定内容是否公开。
- 不把一次复习覆盖为业务实体上的几个可变字段。

**与其他域的关系**

- 基于 Mistake、Note 或未来其他 target 创建 `review_items`；首期可只开放 Mistake。
- 使用 Taxonomy 做学科和知识点维度统计。
- AI 可提供复习建议，但调度结果必须由可解释的复习规则落库。

## 7. AI Assistant

**负责什么**

- 记录输入快照、任务类型、模型、状态、结构化输出、错误和耗时。
- 支持异步执行、重试、幂等与审计。
- 为文章、笔记、错题或复习提供可选建议。
- 为练习导入识别题目、答案和批改痕迹，完成拆题、批改、错因分析、知识点归纳、练习报告和复习建议。

**不负责什么**

- AI 不是文章、笔记、错题或复习记录本体。
- 不把模型输出自动视为已确认业务事实。
- 不静默写入正式错题库，不直接决定正式复习计划。
- 输出必须经过结构化校验；转为正式错题或正式业务修改前必须由用户确认。
- 不绕过管理员权限，不直接决定公开状态。

**与其他域的关系**

- 通过目标实体类型与 ID 关联业务域。
- 可引用输入/输出附件。
- 所有操作由 Auth / Admin 保护，并记录 Audit Log。

## 8. Media / Attachments

**负责什么**

- 文件上传、存储键、公开 URL、MIME、大小、校验和、状态与生命周期。
- 记录附件属于哪个实体、用途和排序。
- 隔离对象存储、本地文件或 CDN 的实现差异。

**不负责什么**

- 不理解文章内容、错题答案或 AI 结论。
- 不通过 JSON URL 数组代替引用完整性。
- 不默认让所有上传文件公开。

**与其他域的关系**

- 被 Post、Note、Question、Practice Import、Mistake、AI Run 引用。
- 上传和删除由 Auth / Admin 保护；公开实体只能暴露允许公开的附件。

## 9. Taxonomy

**负责什么**

- 管理标签、学科、知识点及知识点之间的有向关系。
- 通过多态 `taggings` 为内容实体添加标签。
- 提供规范化、去重、层级或先修关系。

**不负责什么**

- 不保存内容正文。
- 不负责搜索引擎索引或推荐结果本身。
- 不把自由文本自动提升为权威知识点。

**与其他域的关系**

- Posts、Notes、Questions、Mistakes 使用标签。
- Questions 与 Mistakes 关联学科和知识点。
- Review 通过源实体的分类做聚合。
- AI 可建议分类，但最终写入需管理员确认。

## 10. Auth / Admin

**负责什么**

- 管理通行密钥、管理员会话、撤销与过期；复杂账号、密码和 Passkey 设计暂缓。
- 统一解析管理员身份与能力。
- 记录创建、编辑、删除、上传、复习和 AI 操作审计。

**不负责什么**

- 不承载业务内容。
- 不把 `AuthGate` 当作权限校验。
- 不允许生产环境认证绕过。

**与其他域的关系**

- 为所有 admin API 提供后端身份依赖。
- 向 Audit Log 提供 actor、session、IP 和 user agent。
- 访客无需会话即可访问经过发布过滤的 public API。
