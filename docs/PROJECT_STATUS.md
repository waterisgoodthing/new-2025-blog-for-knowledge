# 当前开发状态

源码/产品测试基线：2026-10-09；文档复核：2026-10-12。系统与学习闭环 `PARTIAL`；当前本地质量检查包含一个明确 FAIL（测试类型检查）。这不是撤销历史用户验收，也不是本轮发布验收。基线对象为 dirty工作区，完整结果见 [本轮证据](audits/CURRENT_REVIEW_EVIDENCE.md)。

## 状态口径

`VERIFIED_COMPLETE`只用于明确范围内当前已核验的交付；`PARTIALLY_COMPLETE`表示实现/部分证据存在但未满足全退出条件；`NOT_IMPLEMENTED`表示所列目标未找到实现；`BLOCKED`表示具体依赖阻断；`UNVERIFIED`表示本轮缺少足够证据；`OBSOLETE`表示作为当前执行依据已过期。历史PASS原样保留，不能把本轮“未重跑”伪装成历史失败。

2026-10-09首次审查已验证：文档/源码盘点、迁移图静态解析、121个无DB契约测试、前端530单测、应用TS；10/12本次文档重审未重跑这些产品测试。这些都是有范围的检查，不能使下面整项产品任务变为VERIFIED_COMPLETE。

10/11–12的[设计评估](architecture/DESIGN_RATIONALE_REVIEW.md)仅增加源码推导和本地浏览器只读观察；页面停在空区域/加载状态，未取得有效业务页面。视觉与完整交互验收仍NOT_VERIFIED；10/12文档重审没有再次浏览页面。下表测试通过/失败均指10/09实测及未修复状态。

## 当前候选门禁（与实现程度分开）

|维度|状态与证据|
|---|---|
|实现程度|PARTIAL；源码能力与缺口见下表，不等于Gate通过|
|已执行的类型门禁|FAIL；首次审查test:typecheck两处TS2322，文件未修，本次未复跑|
|完整DB/HTTP/browser/build/远端四job|NOT_VERIFIED；局部单测/静态probe不替代|
|当前候选放行|BLOCKED于已知类型FAIL，另有完整验收欠账；本次不作发布接受|
|历史Week/UI Gate|按原时点保留PASS/GRANTED；当前FAIL不回写历史裁定|


## Week与PR核验矩阵

主计划：[convergence tasks](workflows/personal-learning-system-convergence/tasks.md)。历史Week1/2/3记录Gate PASS；Week4和后来返工存在部分验收。当前不访问历史所称数据库或线上环境。

|任务|当前状态|当前源码/证据|原验收欠账 / 范围说明|
|---|---|---|---|
|PR01 smoke/runbook|PARTIALLY_COMPLETE|`scripts/runtime-smoke.mjs`、public-deploy-runbook|本轮未跑workerd/post-deploy；不能证明原子发布|
|PR02 Note/Blog写作|PARTIALLY_COMPLETE|manage notes路由、ContentEditor、typed notes API|浏览器保存回读未重跑；列表第一页问题A12|
|PR03异步状态|PARTIALLY_COMPLETE|AsyncStatePanel、notes/dashboard loading/error/tests|单测通过，真实交互未验|
|PR04 guestbook|PARTIALLY_COMPLETE|migration027、guest models/router|新库重放/真实schema未验|
|PR05 Review schema|PARTIALLY_COMPLETE|028/029与model/schema/client；10/09静态契约通过|DB重放/约束未验|
|PR06调度v2|PARTIALLY_COMPLETE|lapse、3/7/14/30阶梯、mastered源码；Worker纯函数probe通过|真实事务/并发未重跑|
|PR07再答API|PARTIALLY_COMPLETE|030、review Attempt、三态判定、Record关联|HTTP归属/事务回读未验|
|PR08再答UI|PARTIALLY_COMPLETE|六档评分、generation、ReviewQueue回归通过|test:typecheck失败；当前真浏览器竞争未验|
|PR09 legacy/public切换|PARTIALLY_COMPLETE|031、canonical public DTO、freeze、ledger runner|原验收：隔离迁移幂等/visibility对账及HTTP未复验；范围：兼容读允许保留，生产迁移另授权|
|PR10 KP analytics|PARTIALLY_COMPLETE|canonical practice/review/lapse/due统计及排序|原验收：完整指标/资格/排序矩阵未复验；范围：A07/A08另列设计裁决，BKT非PR10目标|
|PR11 Dashboard|PARTIALLY_COMPLETE|canonical counts、weak Top3、recent mastered、确定性行动|原验收：全链新事务/行动可追溯未验；范围：每日AI不属PR11|
|PR12 Note-KP|PARTIALLY_COMPLETE|032、link/unlink、B03 delete预检|当前HTTP/并发约束未重跑|
|PR13 daily practice|PARTIALLY_COMPLETE|只读确定性选题、recent/mastered排除|原验收：只读/数量边界/资格/排序未复验；范围：A09判答属第二阶段，持久计划不属PR13|
|PR14 OCR诊断/入口|PARTIALLY_COMPLETE|分类、错误DTO、默认关闭、uploaded人工题面|真实OCR质量未验；完整图片人工链未验|
|PR15 Passkey challenge|PARTIALLY_COMPLETE|033、purpose/TTL/hash/消费生命周期源码|真实三类ceremony/并发未重跑|
|PR16 throttling|PARTIALLY_COMPLETE|可配延迟、单测/集成测试源码|部署拓扑/计时/多实例未验|
|PR17 CI/E2E|PARTIALLY_COMPLETE|四job、两TS、Postgres迁移/双门禁、5 E2E|本轮test TS FAIL；远端/最新B源码E2E未验|
|PR18 legacy收缩|PARTIALLY_COMPLETE|已删5项历史记录、旧写redirect/freeze|原验收：已删除项三证据/当前CI未复验；范围：旧tab/planner的广义退休另评，不要求全部清空|
|PR19 AI治理|PARTIALLY_COMPLETE|Run分类/target、034 candidate/confirm|A01–A03与候选采纳语义未闭合|
|Week1 M1|PARTIALLY_COMPLETE|历史Gate PASS，当前实现存在|当前工件/写作/DB全范围未重跑|
|Week2 M2|PARTIALLY_COMPLETE|历史2026-09-21用户Gate PASS，当前主链存在|最新再答UI/类型门禁/数据库验收不完整|
|Week3 M3|PARTIALLY_COMPLETE|历史2026-09-22用户Gate PASS，canonical统计/练习存在|原验收：当前迁移/统计/练习/KP矩阵未复验，A04写协议具名增补；范围：旧读保留、A07/A08另列|
|Week4 M4|PARTIALLY_COMPLETE|可靠性实现/诊断/CI/审计源码存在|原验收：最新浏览器/远端四job/完整schema未验，类型门禁FAIL；范围：生产迁移/部署另授权|

## R/B返工时间谱系

[旧执行核验](workflows/week-completion-remediation-2026-09-27/execution-verification/README.md)针对R00–R07旧候选，结论FAIL；[返工方案](workflows/week-completion-remediation-2026-09-27/rework-plan.md)是当时待实施文件；随后[返工STATUS](workflows/week-completion-remediation-2026-09-27/rework-evidence/STATUS.md)明确本地实现PARTIAL。历史945后端/530前端/smoke23/23是2026-09-27记录，不能冒认本轮重跑。

|任务|当前状态|判断与剩余|
|---|---|---|
|R00–R07原候选|OBSOLETE（作为当前基线）|旧FAIL与EV反例保留；当前需看B源码|
|B00可恢复快照|UNVERIFIED|历史账本路径含临时省略，未恢复核验；本轮哈希快照只证明保存检查，不是可恢复备份|
|B01迟到再答|PARTIALLY_COMPLETE|generation和三类回归存在，10/09 Vitest通过；真实浏览器竞争未验|
|B02 KP保留矩阵|PARTIALLY_COMPLETE|自动草稿KP、人工空/替换、convert等综合测试存在；本轮未跑DB；完整竞争/rollback/换KP后analytics矩阵不足|
|B03间接freeze|PARTIALLY_COMPLETE|锁/legacy关联预检/410已写源码；HTTP与并发未重跑|
|B04 schema定义门禁|PARTIALLY_COMPLETE|精确allowlist+manifest/checker+CI双门禁和破坏probe；本轮仅静态验证，不是catalog PASS|
|B05a来源/schema|PARTIALLY_COMPLETE|034 owner/context/hash、显式合同存在；原输入校验/最终快照与通用decision缺口|
|B05b UI确认|PARTIALLY_COMPLETE|candidate/confirm已可达；迟到候选、采纳字段和最终审计未闭合|
|B06 OCR关闭人工入口|PARTIALLY_COMPLETE|uploaded人工题面路径和相关测试源码存在，历史单测记录保留；真实上传/refresh/读回/provider0未验|
|B07综合产品验收|PARTIALLY_COMPLETE|10/09局部质量检查已执行；test TS FAIL且无完整同源浏览器/DB；不能关闭所有EV|

## 其他计划家族

全库每份任务文件和workflow目录的状态/范围见 [完整清单](audits/DOCUMENTATION_INVENTORY.md)。下面对主要产品演进家族做语义核验；未列具体微任务不自动算完成。

|家族|当前归类|已找到实现/历史交付|当前限度|
|---|---|---|---|
|MVP Batch0–7|PARTIALLY_COMPLETE|草稿/题库/错题/复习/附件/科目源代码与specs|历史基础完成不覆盖后续合同缺口；Batch6 AI/OCR占位已被后续轨扩展|
|Batch8–12 AI/Capture|PARTIALLY_COMPLETE|gateway、task/prompt/validator、runs、routing/usage/health摘要|真实provider、完整流审计/配额/队列不是已验产品范围|
|I0–I2设计/当期审查|UNVERIFIED（当前整项）|历史冻结/领域定义/审查文件存在且可读取|可读取仅证明交付存在，不独立证明历史验收充分；当前运行/schema未复验|
|I3 Attempt|PARTIALLY_COMPLETE|Attempt→MistakeDraft代码，被Week继续扩展|等值判答局限仍在|
|I4 Dashboard/closure|PARTIALLY_COMPLETE|分块/导航/行动已实现|历史浏览器不能证明现版本|
|I5 profile/settings|PARTIALLY_COMPLETE|admin profile/settings真实实现|10/09回归仅被前端全套覆盖，HTTP/持久化未验|
|I6 Capture|PARTIALLY_COMPLETE|采集与草稿链，后续B06人工入口|真实OCR与图片人工全链未验|
|I7 file workspace|PARTIALLY_COMPLETE|附件/组织/回收恢复切片|非完整workspace_node/对象存储目标|
|I8 Markdown/search|PARTIALLY_COMPLETE|版本/WikiLink/反链/后端搜索|工作区search仍deferred；权限/存储未复验|
|I9治理|PARTIALLY_COMPLETE|Runs与治理摘要|非完整异步任务执行器；B05审计缺口|
|I10 dry-run / I11切换|UNVERIFIED（当前运行）|历史迁移ledger/dry-run/切换证据保留|本轮不访问所称数据库；旧authority不是现时事实|
|I12 F01–F03当期关闭|OBSOLETE（作为当前发布基线）|报告/资格审查保留|旧025与307/64测试已被后续源码取代；不表示部署|
|UI Foundation F0–F5|PARTIALLY_COMPLETE（当前集成复核）|组件存在；最新UI总账保留Foundation历史PASS|原tasks勾选未同步属账本债；不因此否定历史PASS，当前整项运行未复验|
|UI V2 U1–U16|PARTIALLY_COMPLETE（当前产品集成）；历史组件Gate GRANTED|总账记录2026-09-20 Final Gate GRANTED；U1–U16组件范围完成，Review依赖2026-09-21解除|主路由未挂载；B-001统一Today任务流仍待集成/复验；旧REQUESTED不是最新批准状态|
|PR20–26候选产品轨|UNVERIFIED（逐项）|会话UI布局部分已有，候选/合同不是完成证明|真实撤销、持久Today、AI每日计划、后台OCR队列等NOT_IMPLEMENTED目标；不得整组算完成|
|安全/发布/编辑器/渲染/小修等其他workflow|UNVERIFIED（当前整项）|102目录均登记（101含Markdown，另1仅artifact），相关源代码/历史artifact可查|每目录逐条当前运行/授权不在本轮测试范围，清单有复查入口|

## 未实现与阻断必须分开

- NOT_IMPLEMENTED：持久StudyPlan/StudyTask、KP Mastery/BKT、Redis任务队列、完整PracticeSession、统一KnowledgeNode/content_items/publish_snapshots长期模型。
- BLOCKED：UI V2 Today真实集成B-001仍未闭合：D008所列PR13前置已实现，Review历史依赖已解除；PR13题目选集是否足以映射dueAt/priority/status未验证。可评估现有API组合，字段口径不足才另定contract，不预设必须新增端点。本轮不实施新contract。
- UNVERIFIED：最新同源业务E2E、schema定义/存量迁移/回滚、真实OCR/provider、生产/远端CI、恢复/多实例/整站性能与无障碍。
- NOT_AUTHORIZED：本轮任何业务修复、数据库操作、迁移、provider/生产/commit/push/部署。

下一步见 [ROADMAP](ROADMAP.md)。本轮文档基线PASS不使系统PARTIAL或质量FAIL变为发布PASS。

## 与原计划的接续口径

[合并路线与逐项映射](ROADMAP.md)保留CONV-R需求→PR01–19→M1–M4原验收，另列REM-R/REQ→B返工→A/N审查索引；不同R命名空间不混用。以具体Week3/4合同确定顺序，不重写历史任务勾选和Gate。

- 原验收欠账：B05的A01–A03及B07完整同源/持久化/独立review；A13当前测试TS FAIL。
- 新增合同缺陷：A04–A06，交互缺陷A11/A12；建议具名增补，不冒称原返工全部已经覆盖。
- 第二阶段裁决：A07/A08归因与归档、A09Practice判分、Note版本；远期A10不属于原R05/R09未完成条件。PR13资格过滤和PR10原指标仍须按原验收核验，不以新裁决取消它们。
- 原M4四CI job要求保留，Week4 README的local-only替代条款与requirements/Gate冲突；本地证据不能替代远端四job绿，也不因本轮缺远端证据撤销历史Gate记录。
- UI历史以[最新总账](workflows/personal-learning-ui-v2/UI_V2_MASTER_TRACKER.md)为准：组件范围已获批、Review依赖解除；当前路由/Today集成仍PARTIAL。PR20–26与September路线独立，未获新实施授权。

本次结合仅复核文档和已有证据；没有新的产品测试结果，没有关闭任何业务缺陷或产品Gate。
