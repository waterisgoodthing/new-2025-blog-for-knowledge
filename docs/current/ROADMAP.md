# 下一阶段开发建议：原计划续接

日期：2026-10-09。以原收敛计划 M1–M4 / PR01–19 为主线，B00–B07 为返工闭环，N00–N07 仅作本轮审查的续接索引。历史结果保留，当前状态见 [PROJECT_STATUS](PROJECT_STATUS.md)，缺陷证据见 [ARCHITECTURE_AUDIT](audits/ARCHITECTURE_AUDIT.md)。本文仅整理建议，不授权业务修改、schema、迁移、provider、commit/push 或部署。

## 原计划来源与编号

- [原收敛需求](workflows/personal-learning-system-convergence/requirements.md)、[PR与UI任务](workflows/personal-learning-system-convergence/tasks.md)：本文的 `CONV-Rxx` 指这套需求，仍保留原验收。
- [修复需求](workflows/week-completion-remediation-2026-09-27/requirements.md)、[旧修复任务](workflows/week-completion-remediation-2026-09-27/tasks.md)：`REM-R00–R07` 是另一套编号，不能与 CONV-Rxx 混用。
- [B返工方案](workflows/week-completion-remediation-2026-09-27/rework-plan.md)、[最新本地账本](workflows/week-completion-remediation-2026-09-27/rework-evidence/STATUS.md)：旧 REM 候选 FAIL 后已有 B 本地实现 PARTIAL；不能从旧 FAIL 重新宣称所有实现缺失，也不能从历史测试绿关闭 B07。
- [Week3执行合同](workflows/personal-learning-system-convergence/week3/README.md)、[Week4执行合同](workflows/personal-learning-system-convergence/week4/README.md)优先解释各周具体依赖。原任务编号、历史批准与验收记录不改写。

保留原目标：可信运行与写作 → 固定间隔复习及再答 → canonical 切换与 KP 反馈 → 可靠性、CI、AI治理及受控 legacy 收缩。ReviewItem 的 mastered、KP统计与确定性练习已经有代码；独立 KP mastery / 持久 StudyPlan 属后续能力，不补写为原 M3 必做。

## 原需求与当前工作的映射

以下均是保留的验收要求，不是本次执行结果。所有 PR 当前整项状态为 PARTIALLY_COMPLETE；历史 Gate 与局部通过的范围见 PROJECT_STATUS。

|原需求 / 里程碑|PR|本轮续接|必须保留的原退出条件|
|---|---|---|---|
|CONV-R31 / M1|PR01|A15 → N00/N06|build:cf + workerd、引用资产全部200、smoke失败退出非0、发布runbook；本地不证明生产原子切换|
|CONV-R03 / M1|PR02|A12 → N04；版本语义 → N05|Note新建/编辑、Blog新建、旧写路由redirect、单ContentEditor、保存后新请求回读|
|CONV-R03b / M1|PR03|N04/N06|loading/empty/error/retry区分，API失败显错且Retry可执行；仅触及切片|
|CONV-R32 / M1|PR04|N06|fresh PostgreSQL经迁移有Guestbook且可读写，不用create_all补表|
|CONV-R01 / M2|PR05|N06|Review state/last_rating/Record状态跨model/schema/client/DB一致，原并发Case D保留|
|CONV-R01 / M2|PR06|N06；A08另列N05|lapse reset、3/7/14/30固定阶梯、mastered条件、Case A–D；不换调度算法|
|CONV-R02 / M2|PR07|N06；A09另列N05|三档再答判定、review context、Record/Attempt归属，错→lapse→到期→正确→mastered持久读回|
|CONV-R02 / M2|PR08|A13 → N01；B01 → N06|0–5评分、同一再答评价与Attempt关联、人工全链；保留合法普通评分；真实Undo不在此项|
|CONV-R04 / M3|PR09|B03 → N06；广义退休 → N07|全部legacy写冻结、active+public allowlist、幂等迁移/visibility对账、空态不fallback legacy；兼容读不因本轮强删|
|CONV-R05 / M3|PR10|A04 → N03；B02 → N06|四指标及派生/lapse/排序、practice/review资格、零分母、稳定tie、非N+1；A07/A08另列设计裁决|
|CONV-R05b / M3|PR11|B02 → N06|今日复习/练习、weak Top3、recent mastered4可追溯canonical行，确定性fallback；非每日AI计划|
|CONV-R06 / M3|PR12|B03 → N06|NoteKP Unique/FK、link/unlink、权限/并发负测、fresh与增量迁移；不默认删除多态关系|
|CONV-R09 / M3|PR13|A04 → N03；B02 → N06|只读admin today，候选0/1/2/3/>10，weak优先、recent/archive/mastered过滤与稳定顺序；不建PracticeSession|
|CONV-R10 / M4|PR14|B06 → N06；A11 → N04|诊断分类、失败可见可处置；授权样本10中≥8或明确不可用。当前OCR关闭，验完整人工链；不调用真实provider|
|CONV-R33 / M4|PR15|B04 → N06|三ceremony：registration/authentication/operator_registration；TTL/purpose/binding/原子消费/并发隔离、fresh与增量迁移|
|CONV-R34 / M4|PR16|N06|账户+IP、实际递增延迟、成功重置、可配置；拓扑扩展另做实验，不默认Redis|
|CONV-R22/R22b / M4|PR17|A13 → N01；A15 → N06|四CI job、两套TS、fresh migration、生产工件smoke、原五条E2E workers=1；本地与远端分列|
|Legacy Cleanup / M4|PR18|N06验已删范围；N07评剩余|Stop write→Switch read→Observe→前端→endpoint→service→DB后期；每删项static/test/runtime三证据，不以净减行数验收|
|CONV-R11 / M4|PR19|A01–A03 → N02；B05a/b → N06|polish transient、既有target调用时绑定、创建型确认后原子回填、放弃可NULL；B05可信输入/最终快照合同继续有效|

原五条 E2E 不被新增反例替代：E2E-01 login→Dashboard；02 create note→edit→save；03 Question→wrong Attempt→Draft；04 Mistake→Review→re-answer→Record；05 API failure→error→retry。

## B返工与审查问题续接

|返工 / 原修复需求|原修复任务|续接索引与剩余验收|
|---|---|---|
|B00 / REQ07|REM-R00/R07|N00：可恢复dirty源码副本、恢复抽查与EV→测试→命令→证据映射；hash不是备份|
|B01 / REQ01|REM-R01|N01修类型门禁；N06验迟到成功/失败、加载乱序、收起重开A/B、新Record绑定B及0–5|
|B02 / REQ02|REM-R02|N06保留跨事务KP继承/显式空/替换/后改题目/非法KP/竞争/rollback/Record与决策矩阵；不自动回填历史空集合；复核既有只读候选SQL/隔离fixture报告，列ID/可证明来源/人工清空不可区分及真实库未授权范围|
|B03 / REQ03|REM-R03|N06验KP delete、folder/tag/suggestions/link/unlink、混合批量、未登录及普通Note正例，关系回读不变|
|B04 / REQ04|REM-R04|N00设schema前置核验点；N06再验最终head的ORM+catalog定义、精确owner、类型/约束/函数/索引破坏probe|
|B05a → B05b / REQ05|REM-R05|N02补A01–A03：生成输入与最终确认快照、edited marker、共同锁/CAS；错actor/source/task/state拒绝，同payload题目改版重放同实体、异payload409、竞争/rollback|
|B06 / REQ06|REM-R06|N06验真小PNG上传→人工题面PATCH→ready→convert→刷新/新请求Draft；provider spy=0，recognize/retry仍关闭；A11另加N04身份反例|
|B07 / REQ07|REM-R07|N06：最终同hash两TS/full test/Next+OpenNext/workerd+FastAPI、原五条与新反例、9项历史skip逐项说明原因与替代覆盖，不删除skip充数；独立实现review及gate|

分类裁决：A01输入来源、A02最终确认快照/采纳语义、A03并发决定协议，是原 B05 未闭合；A13 是当前类型质量 FAIL。A04 KP写协议、A05 source_ref长度、A06 Draft difficulty，是新发现的跨层合同偏移，列具名增补，不能声称原 B02 已承诺这些全部修复。A11/A12 是当前交互缺陷建议。A07/A08 是归因/归档设计裁决；A09原在修复第二阶段；A10是远期能力；它们不自动追加为原 M1–M4 或 B07 通过条件。A14由文档治理处理；A15保留运行验收欠账。

## 执行顺序与门禁

原依赖继续成立，不按PR编号排序：

```text
M1: Phase0 T00/T00b → PR01/02/03/04 → Gate
M2: PR05 → PR06 → PR07 → PR08 → Gate
M3: W3-00 → PR09 → PR10 → PR12 → PR13 → PR11 → Gate
M4: W4-00 → PR14 → PR15 → PR19 → PR16 → PR17 → PR18 → Gate
B:  B00 → B01 → B02 → B03 → B04 → B05a → B05b → B06 → B07
```

这是原合同的依赖顺序，**不要求重做所有已经正确的实现**。逐项复核当前候选，失败仅修对应不变量；保留历史已验范围。Week4 PR19原允许与PR15/16并行；当前B05若涉及schema/安全则依实际gate串行，不能继承旧MEDIUM风险判断。任何新增schema设计/迁移前先完成B04定义门禁与变更review，若前序任务发现schema需要则先暂停该部分。

当前建议续接：N00锁定候选及B04前置 → N01类型门禁 → N02原B05缺口 → N03新增合同缺陷 → N04纳入候选的交互修复 → N06原范围完整复验。N03/N04纳入范围应在N00写清新增退出条件。N05属于第二阶段设计/工程债，N07属于后续能力和剩余退役；可先只读研究，未纳入发布范围时不成为N06额外依赖。此顺序不是改写B账本的实施历史。

|任务|优先级 / 依赖|最小工作与可观察退出条件|
|---|---|---|
|N00候选/合同锁定|P0，无|可恢复快照及恢复抽查、授权/范围、最终源码hash、环境与证据映射；提前核验B04再允许schema变化；保留provider/DB/生产边界|
|N01类型门禁|P0，N00|只修ReviewQueue deferred resolver类型，保留竞争断言；Node24应用/测试TS与既有前端全套通过|
|N02 AI来源/确认|P0，N01；schema依B04|先定不可变生成输入/可编辑输出、参考或采纳语义；代次/hash、最终快照/edited、共同锁/CAS；假provider仅替外部边界，HTTP/new transaction/双会话验B05矩阵；G0/G3/G4，schema加G2|
|N03 KP/输入契约|P0，N00/B04；版本承接N02|PUT/PATCH共用KP写协议、source_ref长度、Draft difficulty跨层一致；替换/清空后双关系/API/analytics/practice一致，65/500及unspecified边界HTTP/DB验；不擅自废API；按变化G0/G1/G2|
|N04交互可达性|P1，N01；AI UI依N02|Capture按id约束迟到详情/编辑字段；Notes服务端筛选分页；旧tab用API base并显错；浏览器乱序、同状态切换、21+notes、legacy首20不假空、失败重试验收|
|N06原范围最终验收|P0验收，N00所纳入修复定版后|fresh scratch迁移/ORM+catalog/破坏probe/full backend、两TS/full frontend、Next/OpenNext、同源workerd+FastAPI原五条+新反例；完整保留上两表退出条件；独立实现review与G2/G3/G4，不以smoke替代E2E|
|N05第二阶段领域/工程债|P1，核心事实可信后|A07历史归因、A08归档、A09Practice判分、Note版本语义先单变量实验及G0裁决；数据加G2、推荐加G4；每项另列实施范围，不先改调度|
|N07后续能力与剩余退役|P2，建议N06后选择；不是候选原合同的新增硬依赖|查legacy planner/PUT/tab真实消费者，按三证据退役；评估PR20–26、KP掌握度/持久计划与UI V2集成，定义用例/最小模型/回滚，不默认新增基础设施|

本地N06通过后，原CONV-R22仍要求**同一源码的远端四job全绿**。[Week4 Gate](workflows/personal-learning-system-convergence/week4/tasks/week4-gate.md)明确要求test push，并验证故意失败被CI捕获、修复后恢复全绿；Week4 README风险表允许Job3/4 local-only的宽松条款与其冲突，当前采用根requirements/Gate的完整要求，不能据local-only声称M4全绿。推送/远端运行/生产发布需相应授权；本文没有执行它们。历史Gate的固定033及旧测试计数不用于新候选，应按当前head034或后续获批head核验。

## 第二阶段与UI候选

原修复[第二阶段](workflows/week-completion-remediation-2026-09-27/requirements.md)保留：D07/FW05判分合同→N05；D10可信度/不可用状态；D09查询预算；D11 throttle并发/多实例；D15安全错误记录；D13当前状态治理已交文档基线；D14 guard/fixture skip与AsyncMock/lint债；UI-V2被排除树类型债；FW07/S06沿现有API的NoteKP/简洁练习；局部390视口/键盘UX；FW09隔离恢复。这些事项均需各自当前证据和范围，不因整合文档即声明完成。被证实的高危D11/D15或渲染问题应升级具名阻断，不沿P2拖延。

已纳入PR的写作、Error/Retry、Review六档、Today fallback、Capture失败UI仍是所属PR验收；**仅PR20–26新增候选不阻塞M1–M4**。

|候选|依赖与边界|当前处理|
|---|---|---|
|PR20会话/登录UI|PR15+16；不改认证语义|独立立项，不将组件存在视为整项通过|
|PR21 Today工作台|PR11；仅本地布局|与UI V2组件轨区分，不默认跨设备存储|
|PR22 OCR候选/类型推荐|PR14/R10入口可靠性合同|功能扩展；不借人工题面链启用OCR|
|PR23跨设备布局|PR21+revision/冲突API|先合同再实施|
|PR24真实Review撤销|PR08+Undo API/审计语义|Toast不是撤销；未实现目标保留|
|PR25 UTC+8每日AI|PR11/13/19+幂等/缓存/fallback|另有G4；确定性Dashboard不是每日AI|
|PR26 Capture后台状态|PR14+durable状态/生命周期合同|原图另画PR22→26，表只要求PR14；是否依候选步骤由获批生命周期裁决，不自动强制PR22或Redis|

[UI V2总账](workflows/personal-learning-ui-v2/UI_V2_MASTER_TRACKER.md)已记录U1–U16组件范围Final Gate **GRANTED**（2026-09-20），Review依赖随后解除；不能沿旧validation REQUESTED/BLOCKED否定这项历史验收。当前主路由未挂载；D008所指PR13前置已有实现，Today真实adapter/浏览器仍需核验。PR13题目选集与统一列表dueAt/priority/status合同的映射待裁决，可先评估既有API组合；不预设必须新建后端端点，也不自动关闭B-001。既有授权也不代表本轮获得新路由/后端实施权。

## September路线承接

[旧W1–W5](roadmap-2026-09.md)是独立路线，08/29基线不是当前缺陷证明。保留薄片、可回滚和真实性原则，不机械复用“先删后建/净减6000行”。

|旧路线|与当前主线结合方式|
|---|---|
|W1路由/管理收敛/CRUD/护栏|test TS承接N01/PR17；旧tab具体API/错误态承接N04；其余消费者退役、共享CRUD/lint/依赖治理另评；不大规模删路由|
|W2 tokens/导航/浮层/a11y|核心PR已触及子集保留验收；全站视觉重写为后续候选|
|W3编辑原语|在真实重复与交互证据上选局部共享；不建新UnifiedEditor|
|W4渲染安全/PoC|先审当前生产渲染路径，高危确证才升级阻断；PoC按三证据退休；不复述旧漏洞为现状|
|W5 SEO/GA/Lighthouse/a11y|单独基线与目标，M4后选；不据本次未测试断言未实现|

旧生产026迁移、音乐CDN、strict mode等决定须核对新状态与授权，不能作为本轮待执行动作；不引入新认证层、FSRS、图数据库、向量库或微服务。

## 最小实验与外部边界

|待裁决假设|只改变一个变量|信号与所需证据|
|---|---|---|
|AI确认绑定生成输入|同题只改错误答案，延迟旧候选|旧run被拒绝或明确编辑合同保留前后快照；请求/run/draft新事务回读|
|决定共享原子协议|两会话同run confirm与reject|至多一有效终态、target/revision一致，无失败副作用；屏障与最终行|
|Attempt历史归因|仅替换题目KP|按G0选择当前归因或作答时归因；对比指标/Practice，不预设必须加快照|
|归档学习生命周期|仅归档带到期ReviewItem的题|全局/KP due、再答/普通评分遵守同一获批策略，不级联删历史|
|Capture身份隔离|仅调换A/B详情响应顺序|选中id/详情/提交id/答案/KP一致；浏览器与新请求读回|

本次整合没有重跑产品测试，也没有DB/provider/浏览器/build/CI/生产操作。未来本地验收、真实样本外发、回填、生产迁移、Git和发布均有独立边界；本轮文档PASS不能替代它们。

## 2026-10-11 整体设计推导补充

[设计合理性评估](architecture/DESIGN_RATIONALE_REVIEW.md)解释上述任务的架构取舍：保留模块化单体，优先统一KP写协议和AI确认规则；前端区分公开展示与工作台布局职责，以八维标准及三条真实流程收敛既有token/导航/a11y和可复用UI组件；PR20–26按各自功能与合同依赖另行选择，不作为视觉达标或原M1–M4前置。新设计建议不改变原Week/B07验收合同，不代表代码或视觉优化已实施。当前localhost页面停留加载，视觉评分与响应式/动效验收NOT_VERIFIED；先建立有效页面证据再迭代。
