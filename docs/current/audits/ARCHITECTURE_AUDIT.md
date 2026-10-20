# 架构审查与偏移清单

日期：2026-10-09。Lead：`/root`；审查对象是带既有修改的工作区。**系统 PARTIAL；文档基线验收见 tracker。**本轮只改文档，不修改以下问题对应的代码。

## 总体评价与裁决方法

当前单仓库分层总体适合个人规模，正式学习模型、人审、权限与复习事实已建立。无需为“统一”移动目录或把所有领域塞入通用内容/节点抽象。核心风险是双模型写协议、来源/审计合同、生命周期口径与运行验收不足。架构成熟度为MVP能力骨架/部分闭环实现（运行可用性未验），尚不能主张全产品或发布就绪。

A/B/C/D为真实只读Worker；Lead亲自追踪跨模块链、直接复核高风险证据，并串行写文档。Worker结论只有通过当前源代码抽核才纳入。源码缺口与实际运行故障分别标注；本轮未执行线上或隔离DB反例。

分类：`CONFIRMED_DRIFT`=已实现层或明确合同不一致；`TRANSITIONAL`=已知兼容并存；`DOC_STALE`=文档失效；`DESIGN_GAP`=业务/验收语义缺口；`TECH_DEBT`=实现限制；`UNVERIFIED`=证据不足。HIGH不是已证实数据损坏或线上漏洞。

## 关键问题

源码路径均相对仓库根目录；行号是本轮读取的源码位置（本轮未改业务文件）。

|ID|分类/严重度|已证实证据|影响与最小建议|
|---|---|---|---|
|A01|CONFIRMED_DRIFT / HIGH|`admin_mistakes.py:156–169,217–224`生成input_hash，确认仅核Question id/version；`mistake-draft-entry.tsx:69–90,163–167,188–192,230–235`输入变更只清candidate、迟到响应直接覆盖|同题答案/生成错因变更没有来源校验；换题已有后端拒绝。需定义生成输入与可编辑输出，前端代次+服务端输入快照共同约束。实际污染未运行复现|
|A02|CONFIRMED_DRIFT / HIGH|`admin_mistakes.py:206–235`candidate只入hash，draft仍写原字段；`ai_creation_service.py:191–198`仅target/hash/time；`ai_run.py:52–60`无确认快照；原`rework-plan.md:105`要求快照/edited marker|最终人工确认不可重建，AI候选未作为业务字段采纳。先裁决参考/采纳语义，明确映射并保留受保护最终快照；不把原output_data当最终确认|
|A03|CONFIRMED_DRIFT / HIGH|confirm `_lock_run`见`ai_creation_service.py:106–117`；通用decision `ai_run_service.py:277–307`普通对象内存revision检查后flush，`ai_runs.py:91–101`未行锁/CAS|confirm/reject/accept未共享原子协议；并发状态冲突是可验证风险，具体结果UNVERIFIED。统一锁/条件更新并补两会话竞争；现有并发confirm测试不足|
|A04|CONFIRMED_DRIFT / HIGH|`questions.py:69–88`同时PUT/PATCH；`question_service.py:312–326`PUT只更新KnowledgePointLink，`:192–219`读取优先QuestionKnowledgePoint，PATCH`:404–422`双写|KP更新与返回/analytics/选题可能分叉。先查消费者，在兼容范围统一写协议；不能擅自删除PUT|
|A05|CONFIRMED_DRIFT / MEDIUM|`schemas/question.py:129–134`source_ref允许500；`models/question.py:192`和migration012:145为64；service`:427–435`直接写|本轮纯对象probe接受65字符但ORM声明64，数据库错误/HTTP表现未验。统一DTO/ORM/schema长度或准确限制|
|A06|CONFIRMED_DRIFT / MEDIUM|`schemas/question.py:14,151,202`Draft接受unspecified；`models/question.py:121–123`CHECK排除；`draft_service.py:135–138`原样flush|本轮纯对象probe已确认差异，DB结果未验。明确Draft专用枚举或归一NULL并跨层验证|
|A07|DESIGN_GAP / MEDIUM|`attempt.py:14–21`无Question version/KP快照；`kp_analytics_service.py:60–69`用当前QKP join历史practice Attempt|换KP会重新归因历史作答；Mistake已保留KP快照。先选择当前内容归因/作答时归因，再验证，不立即新建复杂事件系统|
|A08|DESIGN_GAP / MEDIUM|Question归档`question_service.py:443–466`未停ReviewItem；due`:review_item_service.py:28–31`仅看item；KP聚合`:90–94`排除归档Question；`reanswer_service.py:122–124`拒绝归档题|全局due与KP due可不同，队列仍能普通评分但不能再答。定版归档生命周期并做归档矩阵；禁止未经决定级联删历史|
|A09|TECH_DEBT / MEDIUM|`attempt_service.py:23–31`Practice值等同；`reanswer_service.py:61`起三态判定|essay/格式差异在practice可直接判错并起草，review可能人工/半自动。先明确Practice判答合同，保持已验证Review调度|
|A10|DESIGN_GAP / MEDIUM|`review_item_service.py:70–80`仅item mastered；KP analytics统计；`review.py:101–104`plan仍读Note|独立KP掌握度→持久学习计划未实现。先确定个人需求与最低计划语义，不为了目标蓝图强行引入BKT|
|A11|TECH_DEBT / MEDIUM|`capture-workspace.tsx:138–149`详情响应无代次；`:279–287`详情未按id隔离；`:865–873`转换仅重置部分字段|切换Capture可能迟到详情覆盖或答案/KP串状态；静态缺口确认、浏览器未复现。按capture.id约束响应和编辑生命周期|
|A12|CONFIRMED_DRIFT / MEDIUM|`manage/(workspace)/notes/page.tsx:15–18`默认第一页后过滤note/blog；`notes.py:72–73`默认20，无页面分页|后续页内容不可从此列表浏览，legacy占第一页可假空态；补server筛选/分页，不能把列表存在当完整管理验收|
|A13|CONFIRMED_DRIFT / MEDIUM|本轮测试类型检查exit2；`review-queue.test.tsx:169,219` TS2322；CI`:31–32`执行test:typecheck|当前本地质量门禁确实失败，530单测通过不能抵消。后续只修deferred类型并重验；本轮不修改测试|
|A14|DOC_STALE / HIGH|旧JWT/bypass方案、多份当前路线、AI旧绑定和NOT_YET_WIRED矛盾；见文档索引|误用会把错误权限/完成口径带入开发。本轮当前入口收敛、旧条款标历史，保留原始记录|
|A15|UNVERIFIED / HIGH|最新返工`rework-evidence/STATUS.md:3–9`明确未完成同源真浏览器E2E/独立实现复核；本轮不执行|B07不能闭合，远端CI/生产不明。下一阶段需最终源码身份+隔离DB+真实工件+新事务回读|

A01–A06、A11、A13由Lead直接逐行/命令复核；A07/A08链式JOIN/过滤与归档条件也由Lead抽核。A02按与明确B05返工合同偏移分类；仅从当前产品能力看同时构成DESIGN_GAP，不重复计数。

## 次级债务与待验证项

|事项|证据及界限|建议|
|---|---|---|
|Note版本语义|`notes.py:354–360`先创建next version再应用新正文；`knowledge_markdown_service.py:24–35`编号递增保存旧正文|TECH_DEBT/MEDIUM；明确版本代表变更前/后，运行读回后裁决，不能现在宣布丢数据|
|旧安全/审核tab同源fetch|`security-tab.tsx:27–35,117–123`、`audit-tab.tsx:50–60`绕过API base，审核失败可被空态吞掉；Next无rewrites/app api|TECH_DEBT/MEDIUM；反代补偿未验证，不能断言生产404。后续统一typed client与错误态|
|AI审计失败后仍外发|`ai_gateway.py:153–155,304–326`记录失败返回None，仍调用provider；canonical最后502|TECH_DEBT/MEDIUM；实体不绕过绑定但费用/审计可能缺口，考虑canonical生成fail closed|
|附件与DB非原子|`attachment_service.py:94–119`文件先落，只有flush失败补偿；request稍后commit失败未覆盖|TECH_DEBT/MEDIUM；最小失败probe后决定补偿，不新增通用saga|
|多态关系完整性|`taxonomy.py:66–88`target无FK，实体双字段/双KP关系并存|TRANSITIONAL；先消费者/完整性清单与退出条件，避免机械拆表/删兼容|
|会话切换SWR缓存|`use-admin-auth.ts:37–38`仅刷新auth keys；业务key不按会话分区|UNVERIFIED；没有本轮泄露证据，需logout/login真实负测|
|migration034部分重放|`:56–58`发现creation_context整体return|UNVERIFIED；部分安装形状需专用probe，不能当已有schema漂移|
|未挂载ui-v2与重复治理摘要|features/adapters没有app引用；analytics/jobs均GovernanceOverview|TRANSITIONAL；保留原型边界，先决策用途，不通过搬目录解决产品验收|

## 历史缺陷的当前裁决

旧EV01、EV02、EV03、EV05已有针对源码修补：Review generation、KP delete预检、catalog definition checker、uploaded人工题面。EV04已增加可信context和显式candidate/confirm，仍有A01–A03。**不能复用旧候选FAIL为当前所有EV仍失败，也不能将源码修补升级为最终PASS。**034、manifest与CI双门禁存在，本轮无DB验证，不继续宣称旧033 drift必然还在。

## 本轮结果与未验证

2026-10-09首次架构审查记录：Vitest 70 files/530 PASS、应用TS PASS、测试TS FAIL（此次文档复审未重跑）；无DB后端121 PASS/37 subtests；AST迁移图PASS；schema/HTTP/browser/build/provider/remote CI/production均未执行。完整命令、Worker分工、保留检查与最终文档验收见 [本轮证据](CURRENT_REVIEW_EVIDENCE.md)和[tracker](CURRENT_REVIEW_TRACKER.md)。下一阶段顺序见 [ROADMAP](../ROADMAP.md)。

## 文档重新审查裁决（2026-10-09）

以下均为DOC_STALE或表述/覆盖缺口，已由Lead修正文档。A01–A15业务问题未因这些改字而关闭。三项只读专项返回后，Lead核源码、原需求及历史总账再定稿；首次审查的产品测试不是本次新执行。

|ID / 等级|复查前问题与证据|当前处置与边界|
|---|---|---|
|DOC-R01 / MEDIUM|README Service仍写SM-2；review_item_service.py:21–26,70–71为fixed_interval_v2|README改当前调度，旧SM-2写冻结；不改算法|
|DOC-R02 / MEDIUM|ARCHITECTURE_CURRENT把mastered写“四连胜”|改连续至少4次rating≥3、末次≥4；普通评分合法，不等同四次再答正确|
|DOC-R03 / MEDIUM|AI owner摘要省略NULL兼容；ai_creation_service.py:127–131|正常candidate保存created_by；两非NULL才比对owner，旧无context行仍拒绝；不宣称现存越权|
|DOC-R04 / MEDIUM|STATUS把兼容读退休、BKT、Practice判分和生产放在原PR欠账列；与原requirements及修复第二阶段冲突|拆原验收/范围，第二阶段与发布另列；保留真实原退出条件|
|DOC-R05 / MEDIUM|STATUS只有实现PARTIAL，历史VERIFIED_COMPLETE与当前定义混用|加当前Gate表：类型FAIL/候选BLOCKED/运行NOT_VERIFIED；历史PASS/GRANTED注明时点，不被当前失败撤销|
|DOC-R06 / MEDIUM|UI总账摘要仍REQUESTED/GAP005阻塞，后续Change Log和Final Acceptance为GRANTED/MET|只更新当前摘要/依赖/Gap/决定状态，Change Log原字节保留；PR13前置具备，Today adapter字段映射未验，不预设新增端点|
|DOC-R07 / MEDIUM|ROADMAP B02漏只读历史候选报告；原rework-plan B02明确要求|补SQL/隔离fixture报告及人工清空不可区分/真实库未授权范围，不访问或回填真实库|
|DOC-R08 / LOW|N07后置可能误读为PR20–26新增硬依赖|明确只是Lead优先级建议，保留各候选原合同依赖|
|DOC-R09 / MEDIUM|1218默认rg扫描漏隐藏.github/pull_request_template.md|清单补为1219 Git追踪/非忽略非public Markdown；.agents 5份忽略MD明确排除，旧扫描记录不改|
|DOC-R10 / LOW|tracker同段“结合已PASS”又“未结束”；当前规则“事实只写一处”与分域当前文矛盾|清理残留时态；总览/分域说明一致，状态和路线统一入口；33设计+1架构入口计数明确|
|DOC-R11 / MEDIUM|CI复现遗漏B04双门禁；Known deviations仍称UI pending/测试TS可exit0；ci.yml:105–108|正文/命令/摘要补alembic check与schema_catalog_gate，旧结果标历史；组件批准/当前FAIL校正；本次未执行CI/DB命令|

另补AUTH_BYPASS双开关代码仍存在、main按声明ENV拒绝非开发启用的边界（auth.py:67–89 / main.py:38–55），实际部署配置未验。前次“旧bypass方案失效”不等于该代码已删除。

独立复核与最终数量/链接/保护结果按本阶段证据和tracker记录；没有新业务实现或发布接受。

## 2026-10-12 设计后文档重审

|编号 / 严重度|确认问题|处置及限度|
|---|---|---|
|DOC-R12 / MEDIUM|概览“可用MVP”超出当前完整运行证据|改为源码能力骨架；完整可用性未验，系统仍PARTIAL|
|DOC-R13 / LOW|“本轮”测试/浏览器时态跨多个阶段；tracker设计阶段仍称采集中|STATUS明示10/09测试、10/11–12加载观察、10/12仅文档；启动状态改为历史时点|
|DOC-R14 / LOW|设计提案在概览/架构导航/状态入口不易找到|增加提案入口，不升级为现行实现或Accepted ADR|
|DOC-R15 / LOW|AI通用决定证据链和前端快捷键描述精度不足；框数口径不明确|补router→读取→决定行号；快捷键写源码尝试而非实测效果；明示列表标记计数，1220行原统计无需改数|

源码专项独立复核未发现新的阻断性事实错误；原A01–A15与DR-B01–06未因本轮文档修订关闭。旧报告和测试结果保持原时点；本次未执行产品测试、浏览器或数据库。
