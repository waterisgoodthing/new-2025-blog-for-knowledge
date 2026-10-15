# MVP Goal Gap Analysis

> 审计性质：只读目标差距分析。审计期间未修改代码、未创建 migration、未写入数据库、未新增功能。
>
> 审计基线：分支 `notes-workspace-ux-upgrade`，HEAD `939ad1f`，数据库 `020 (head)`。

## 1. Executive Summary

原始 MVP 的目标不是完整 AI 学习平台，而是让个人管理员可以手工完成一条可验证的学习闭环：

```text
科目 → 知识点 → 题目草稿 → 人工审核 → 正式题目
→ 错题草稿 → 人工审核 → 正式错题 → 简单复习项 → 复习记录
```

按这个冻结边界，当前版本的核心手工 MVP 已经达到“有条件通过”：源码、API、数据库对象和本地验收记录均支持上述主链路；附件的上传、关联、读取和私有权限也有验收证据。

但“当前仓库”已经超出原始 Batch 0–7 范围，加入了 Capture、AI Gateway、Prompt Registry、AI Run 审计和 provider routing 等后续能力。这些增强不能反向提高原始 MVP 的完成度，也不能因代码存在就视为真实 AI/OCR 产品闭环已完成。

综合判断：

| 目标 | 结论 |
|---|---|
| Demo Ready | YES；已有演示脚本和本地验收对象 |
| Personal Use Ready | CONDITIONAL YES；手工核心闭环可用，仍有认证/运行环境和数据运维边界 |
| Production Ready | NO；缺少生产级运维、可恢复性、完整验证和若干长期能力 |

## 2. Original MVP Goal

### Product Goal

构建一个个人知识库与博客系统，兼顾公开内容展示、个人笔记、错题记录和复习；第一版优先跑通人工可操作、人工可审核、独立可验证的学习闭环。

### Target Users

- 主要用户：站点所有者/管理员/学习者，即单用户个人学习场景。
- 访客：匿名公开内容阅读者，只能读取已发布且未隐藏的公开内容。

### Core Workflow

管理员建立科目和知识点，手工录入并审核题目，再形成错题并提交简单复习；公开层展示允许公开的博客、笔记和错题内容，私有写入、附件、AI 和复习提交由后端管理员权限保护。

### Required MVP Capabilities

1. Subject 与 Knowledge Point 基础管理。
2. Question Draft → 人工审核 → Question。
3. Mistake Draft → 人工审核 → Mistake。
4. Active Mistake → Review Item → Review Record，使用固定间隔或简单 SM-2。
5. 管理员私有附件：上传、元数据、关联、读取和权限边界。
6. Blog、Notes、Mistakes 的公开读取与管理入口隔离。
7. 核心流程不依赖 AI、OCR、Capture、BKT 或完整练习系统。

### Deferred Capabilities

原始范围明确延期：真实 AI/OCR、Capture Router、批量导入、PDF 自动解析、任务队列、BKT/掌握度、复杂练习、搜索索引、Analytics、对象存储/R2、云部署和多用户系统。

## 3. Current System Capability Map

### 3.1 Learning Core

| 能力 | 数据模型 | 后端 API | 管理页面 | 用户流程 | 数据闭环 |
|---|---|---|---|---|---|
| Subject | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| Knowledge Point | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| Question Draft | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| Question | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| Mistake Draft | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| Mistake | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| Review Item | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| Review Record | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |

事实依据：当前数据库有 `subjects=1`、`knowledge_points=3`、`question_drafts=3`、`questions=3`、`mistake_drafts=3`、`mistakes=3`、`review_items=3`、`review_records=4`；对应 admin routers、前端 management routes 和 MVP 本地验收摘要均存在。这里的 COMPLETE 指原始 MVP 的“基础人工闭环”，不表示长期练习/掌握度系统完成。

### 3.2 Attachment System

| 能力 | 状态 | 结论 |
|---|---|---|
| upload | COMPLETE | admin-only upload API/UI；当前 `attachments=1` |
| link | COMPLETE | `attachment_links=1`，支持 question/question draft/mistake 关联 |
| read | COMPLETE | 通过 attachment id + storage helper 读取，验收记录有内容一致性证据 |
| permission | COMPLETE | 私有附件和 admin API 边界已验证 |
| storage boundary | PARTIAL | 当前是本地 private storage；对象存储/R2、派生文件和云部署延期 |

对原始 MVP 的“学习资料绑定、错题附件、私有访问”要求可判定为 COMPLETE；对生产级文件生命周期和可恢复性只能判定为 PARTIAL。

### 3.3 Public Content System

| 能力 | 状态 | Gap |
|---|---|---|
| Blog public view | COMPLETE | 公开读取存在，编辑能力隔离 |
| Notes public view | COMPLETE | 匿名读取过滤 published/non-hidden |
| Mistakes public view | COMPLETE | 公开错题列表/详情与 admin review 分开 |
| Knowledge consolidation | PARTIAL | 公开内容可读，但学习实体与历史 Note 系统仍并存 |
| Share/deployment boundary | PARTIAL | 公开站存在；公网/生产级部署与持续运维不等于本地验收已完成 |

当前 `Note(type="mistake")` 历史合同与独立 `mistakes` 新链路同时存在。兼容层能支撑当前使用，但增加了数据真源和路由语义的长期维护成本。

### 3.4 Review System

| 项目 | 状态 | 说明 |
|---|---|---|
| review item | COMPLETE | `review_items` 存在，约束为 mistake + fixed_interval_v1 |
| review record | COMPLETE | `review_records` 不可变记录结构和提交 API 存在 |
| simple schedule | COMPLETE | `next_review_at` 与简单间隔更新已实现 |
| reminders | MISSING | 未发现提醒/通知机制 |
| statistics | PARTIAL | 有基础 queue/stats/plan API；没有长期指标事实仓库 |
| trend analysis | MISSING | `learning_metrics_*` / reports 表不存在 |
| learning feedback | PARTIAL | 可展示复习结果，但无完整反馈与改进策略闭环 |
| BKT/mastery | DEFERRED | `knowledge_mastery` 等表不存在，符合原始 MVP 边界 |

因此：原始 MVP review 目标 COMPLETE；“完整学习系统”目标 PARTIAL，提醒、趋势、掌握度和复杂调度继续延期是合理的。

### 3.5 AI Capability

| 能力 | 状态 | 事实 |
|---|---|---|
| AI Gateway | COMPLETE | Gateway 与 provider caller、fallback 和 call log 链路存在；Batch 9 有真实 Gateway 方法验证记录 |
| Prompt management | COMPLETE | Prompt Registry、标准化和 validator 代码存在；不是 Batch 6 静态占位页 |
| Model abstraction | COMPLETE | provider capability、fallback、routing policy 和 typed result 存在 |
| AI run tracking | COMPLETE | `ai_runs=28`，有运行状态、校验状态、人工 review 状态和 admin API |
| AI generated draft workflow | PARTIAL | AI 可生成 Capture/Mistake 草稿并要求人工确认，但未形成所有业务类型的统一正式入库闭环 |
| usage/cost accuracy | PARTIAL | 当前明确以 `unknown` 表达缺失 token/cost；不是精确账单 |
| provider health | PARTIAL | 有基于近期调用的 snapshot；无真实 health event、熔断或临时禁用体系 |

这些能力已超出原始 MVP；它们应被称为“后续能力已实现/部分实现”，不能用来宣称原始 MVP 的 AI 目标已完成，因为原始 MVP 本来就不要求 AI。

### 3.6 OCR / Capture

| 能力 | 状态 | 事实 |
|---|---|---|
| image input | PARTIAL | attachment + admin capture API/UI 存在；当前 `capture_items=0` |
| OCR adapter | PARTIAL | 有窄 adapter、状态机和 fake 测试；真实 OCR 未在本次审计运行 |
| document/PDF parsing | MISSING | 未发现完整 OCR result/block 表；PDF 拆分/解析延期 |
| auto-generated Draft | PARTIAL | Capture 可生成 mistake draft suggestion，并保留人工编辑字段 |
| human confirmation | COMPLETE | `ready → convert` 为显式、幂等、人工确认边界 |
| real provider closure | NOT VERIFIED | Batch 8 validation 明确写明真实 AI/OCR 闭环未验证 |
| batch import | MISSING | 未实现批量导入 |

Capture 的架构边界是健康的：OCR/AI 输出先进入 capture/draft，不直接写正式 Mistake/Review；但真实外部能力、文档解析和运行数据仍是明显差距。

### 3.7 Product Completeness

| 用户步骤 | 当前结论 |
|---|---|
| 发现问题 | PARTIAL：可通过手工 Capture 或管理页进入；自动发现/导入有限 |
| 记录 | COMPLETE：手工题目/错题草稿和正式实体可用 |
| 整理 | COMPLETE：Subject/Knowledge Point/Question/Mistake 结构存在 |
| 复习 | COMPLETE：基础 review item/record 闭环存在 |
| 反馈 | PARTIAL：有基础复习结果/计划，缺少趋势和学习反馈系统 |
| 改进 | PARTIAL：可再次人工记录和复习，但无指标驱动的改进建议闭环 |

结论：个人手工 MVP 闭环成立；自动采集、可量化反馈和持续改进闭环尚未完整成立。

## 4. Domain Gap Analysis

### 4.1 What is already complete for MVP

- 手工学习核心链路已经有真实数据库对象、admin API、管理页面和验收数据。
- 复习基础算法和不可变复习记录已满足冻结的 MVP Review 约束。
- 附件基础系统已满足本地私有 MVP 要求。
- 公开 Blog/Notes/Mistakes 与私有管理/复习/AI/附件边界已被源码和验收记录覆盖。

### 4.2 What is only partially complete

- Review 还不是完整学习系统：无 reminders、趋势、学习指标和 mastery。
- Capture 的状态机与草稿人工确认已实现，但真实 OCR/AI、PDF/文档解析和批量导入未闭环。
- AI 治理已出现较完整的代码基础，但 usage/cost、health、队列和运营控制仍不完整。
- 旧 Note 错题兼容链与新独立 Mistake 链并存，未来需要明确长期真源和迁移策略。

### 4.3 What is missing or explicitly deferred

当前数据库确认不存在：`chapters`、`practice_sessions`、`practice_attempts`、`jobs`、`job_steps`、`job_logs`、`ocr_jobs`、`ocr_results`、`ocr_blocks`、`learning_metrics_daily`、`learning_reports`、`knowledge_mastery` 等表。它们属于长期目标或明确延期项，不应作为当前 MVP 失败项全部追责；其中 jobs、备份/恢复和生产运维能力会成为生产化门槛。

## 5. MVP Gap Matrix

| Domain | Original Goal | Current Status | Gap | Priority |
|---|---|---|---|---|
| Learning Core | 手工完成 subject→KP→question→mistake→review | COMPLETE | 无原始 MVP 阻断差距；保留 Note/独立实体双线风险 | P1 强烈建议 |
| Attachments | 私有上传、绑定、读取 | COMPLETE | 本地存储，缺生产级对象存储/备份/派生文件 | P1 强烈建议 |
| Public Content | 公开 Blog/Notes/Mistakes 读取 | COMPLETE | 持续部署与公开运行验收仍需独立证据 | P1 强烈建议 |
| Basic Review | fixed interval/简单 SM-2 + records | COMPLETE | 无原始 MVP 阻断差距 | P2 后续增强 |
| Review Productization | reminders、统计、趋势、反馈 | PARTIAL | 无通知、指标仓库、趋势和完整反馈闭环 | P1 强烈建议 |
| AI | MVP 不依赖 AI | COMPLETE（按 MVP 边界） | 后续 AI 已实现部分治理，但不应扩大 MVP 承诺 | Deferred |
| OCR/Capture | MVP 不依赖 OCR/Capture | COMPLETE（按 MVP 边界） | 后续 Capture 真实 provider、PDF、批量导入未完成/未验证 | Deferred |
| Production Auth/Config | 管理写入真实受保护 | PARTIAL | 仍需生产环境认证、CORS、bypass、域名和错误处理的端到端证据 | P0 必须补齐 |
| Operations | 个人可持续使用 | PARTIAL | 备份、恢复、任务执行、监控、失败重试和数据运维不完整 | P0 必须补齐 |
| Multi-user | 原始 MVP 非目标 | MISSING | 未实现用户/租户/共享权限模型 | Deferred |
| Full Practice | 长期学习产品能力 | MISSING | practice session/attempt 等表不存在 | Deferred |

## 6. Technical Debt

### Architecture risks

1. 数据模型双线：目标架构把 Mistake 作为独立实体，但旧公开内容仍有 `Note(type="mistake")` 合同；继续扩展时必须明确真源、同步和迁移边界。
2. API 边界已明显分层，但旧 `/api/notes`、旧 AI 路由和新 `/api/admin/*` 管理合同并存；路由存在不能替代完整行为/权限验证。
3. Migration 当前稳定在 `020 (head)`，但长期目标表大量不存在；未来连续迁移会增加从现有真实数据升级的风险。
4. Capture/AI 目前没有生产任务队列；同步请求、外部 provider latency 和失败重试仍受当前请求链限制。
5. 附件 storage boundary 目前是本地 private 文件系统；跨机器部署、备份恢复和文件/DB 一致性仍未形成生产闭环。

### Current known issues

| Issue | Category | Status |
|---|---|---|
| `LT-ISSUE-002` 历史认证错误处理问题 | non-blocking for accepted local core, production risk | 验收摘要记录为已修复/关闭，但应在生产验收中复核 |
| 既有测试隔离/AsyncMock warnings | non-blocking | Batch 9/12 记录了全量测试历史失败或 2 个 warning；不能用“单个定向测试通过”替代全量持续稳定性证据 |
| `baseline-browser-mapping` freshness、Node `DEP0205` | non-blocking warning | 不阻塞 build，但应纳入依赖治理 |
| 真实 AI/OCR Capture | blocker for claiming real Capture product closure | 明确 NOT VERIFIED；fake/mock 证据不能替代真实 provider/browser proof |
| production backup/recovery/operations | blocker for Production Ready | 本次未发现完整恢复演练、任务队列、指标/报警和生产数据运维闭环 |
| clean worktree | no issue at audit time | `git status --short --untracked-files=all` 为空；历史“dirty worktree”记录属于旧快照，不作为当前问题 |

## 7. Product Risk

最大产品风险不是“缺少 AI”，而是把一个已经可用的手工学习 MVP 误认为完整智能学习平台：

1. 用户可以记录和复习，但还不能获得完整的长期反馈、趋势和改进建议。
2. Capture/AI 的界面和合同已存在，容易造成“真实 OCR/AI 已经可靠”的错觉；当前没有足够真实 provider/browser 证据。
3. Note 兼容链与新学习实体链并存，长期可能造成内容重复、公开视图和管理视图不一致。

## 8. Recommended Next Roadmap

### Phase Next：从 conditional pass 到 production-ready

**目标：** 先把当前手工 MVP 做成可持续、可恢复、可被真实环境验收的个人系统。

**建议投入：**

- 完成生产认证/CORS/AUTH_BYPASS/域名配置的端到端复核。
- 建立数据库与附件备份、恢复演练、文件/数据库一致性检查。
- 复跑全量前后端测试和关键浏览器路径，收敛测试隔离与 warning 证据。
- 明确 Note 与独立 Mistake 的长期真源，暂不进行未经批准的迁移。
- 补最小运营观测：错误日志、失败任务记录、恢复手册和数据健康检查。

**依赖条件：** 生产环境配置、可控的管理员会话、备份目标和批准的 schema/data 决策。

**预计复杂度：** 中等；以验证、运维和边界收口为主，避免新增大产品功能。

### Phase Growth：增强学习价值

**方向：** 完整 Review（提醒、趋势、基础指标）、真实 Capture/OCR provider 验证、PDF/文档解析、AI 草稿质量与人工采纳率统计。

**依赖条件：** Phase Next 的数据可靠性、真实样本、provider 成本边界、明确的 review/analytics 数据口径。

**预计复杂度：** 中高；会引入 jobs/metrics 等新数据合同，必须单独设计、迁移和验收。

### Phase Long-term：产品化

**方向：** 多用户与租户权限、云对象存储、生产任务队列、推荐系统、智能学习助手、完整练习系统和掌握度模型。

**依赖条件：** 稳定的独立领域模型、审计/隐私设计、可观测性、备份恢复和真实使用数据。

**预计复杂度：** 高；这已不是当前个人 MVP 的自然小步扩展，而是新的产品阶段。

## 9. Final Assessment

### 1. 当前距离最初 MVP 目标还有多少？

如果目标严格限定为冻结的手工 MVP：核心功能差距已经很小，当前属于“核心闭环完成、生产化收口未完成”。如果目标被误读为完整智能学习产品：差距仍然很大，主要缺少完整 Review/Analytics、真实 Capture/OCR 运营闭环、生产运维和长期练习/掌握度能力。

### 2. 当前版本是否达到三个等级？

- **Demo Ready：达到。** 有演示脚本、验收摘要和数据库样例。
- **Personal Use Ready：有条件达到。** 手工学习核心链路、公开读取和私有管理能力可用；使用范围应限定为当前已验证的个人/本地场景。
- **Production Ready：未达到。** 生产配置、备份恢复、运营监控、真实 Capture/OCR 验证和持续全量稳定性证据不足。

### 3. 最大三个差距

1. 生产化可靠性：认证/配置、备份恢复、文件一致性、监控和运行手册尚未形成完整证据。
2. 学习反馈闭环：基础复习能跑，但提醒、趋势、指标、掌握度和可执行反馈尚未完成。
3. 智能采集真实性与运营：Capture/AI/OCR 合同和状态机存在，但真实 provider、PDF/批量导入和长期成本/健康治理仍不完整或未验证。

### 4. 下一阶段最值得做什么？

优先做 Phase Next 的生产化收口和数据真源决策，而不是继续扩展 AI 表面能力。最值得投入的是：生产认证/配置复核、备份恢复、全量验证、附件运维和 Note/Mistake 边界治理。

### 5. 哪些功能应该继续延期？

继续延期多用户/租户、复杂练习、BKT/掌握度、推荐系统、云对象存储迁移、分布式任务队列、批量 OCR/PDF 解析、AI 自动决策和跨用户分析。真实 Capture/OCR 可进入 Growth，但在真实 provider 与成本/失败边界获证前，不应成为核心保存流程的强制前置。

## Audit boundary statement

本报告是基于代码、文档、数据库 schema/计数和历史验证记录的差距分析，不是修复报告，也不是生产上线批准。任何未验证项仍保持 `PARTIAL`、`MISSING`、`DEFERRED` 或 `NOT VERIFIED`，不得由本报告自动推进下一批开发。
