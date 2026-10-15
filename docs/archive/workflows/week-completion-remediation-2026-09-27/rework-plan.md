# 执行核验后的返工方案

> 文档治理（2026-10-09）：历史阶段账本保留，不把原 PASS/FAIL/未实施覆盖为本轮状态。当前见 PROJECT_STATUS；R 旧候选之后已有 B 本地返工 PARTIAL；UI V2 为独立组件轨，尚非主业务路由集成。 当前入口见 [文档索引](../../DOCUMENTATION_INDEX.md)。

日期：2026-09-27。本文补充本workflow已有的requirements/design/tasks/validation，不覆盖历史方案与执行记录。当前产品验收仍为 **FAIL**；本文是待执行方案，**不代表修复完成或实施授权**。

依据：[独立执行核验报告](execution-verification/README.md)。本轮再次比对核验起始清单，2,881份既有文件无变化；抽查当前Review/Capture/AiRun/草稿入口，仍与核验结论一致。未重新运行产品测试。旧的“R00–R07 PASS”不得作为本轮起点，525/941项通过仅作为回归基线。

执行模式WORKER：主Agent负责本方案与最终接受；独立rework_plan_review审阅方案。未来实现、独立代码review、QA及专业gate分别记录真实执行人，不能用本次方案审查充当实现验收。

## 目标与串行顺序

目标：关闭EV01–EV05，补齐R02缺失验收，使每个原R项具有与承诺相符的运行证据。保留已通过的多选集合、KP快照、现有冻结入口、Capture target和默认OCR关闭。

| 新任务 | 对应原项 | 工作与交付 | 退出依据 | 风险/专业门禁 |
|---|---|---|---|---|
| B00 | R00/R07 | 锁定当前工作树、可恢复源码副本、合同和反例索引；状态页区分历史/当前 | 基线hash+副本恢复抽查，EV→测试ID→命令→证据映射；不覆盖原脏文件 | MEDIUM；合同G0 |
| B01 | R01/EV01 | 请求代次控制，防迟到评价污染 | 同一浏览器竞争反例变为通过；无旧Attempt误关联 | MEDIUM；QA/前端review |
| B02 | R02 | 补跨事务KP与学习决策验收、只读存量候选报告；失败时只修对应不变量 | 空/替换/后改题目/失败/竞争矩阵，真实Record与Dashboard/Practice回读 | HIGH；G0/G4，若改schema加G2 |
| B03 | R03/EV02 | KP删除及间接关系写入冻结闭合 | 真cookie HTTP拒绝+新事务关系不变，正例不退化 | HIGH；G3；FK变化另G2 |
| B04 | R04/EV03 | 可运行的schema定义检查器与精确ownership清单 | 三个现有破坏反例全部报错，再补类型/约束/函数/索引反例 | HIGH；G2，安全guard定义G3 |
| B05a | R05/EV04 | canonical AI创建合同与增量schema设计 | UI、可信来源、保存幂等、状态机和迁移方案定版；独立门禁通过 | HIGH；G0/G1/G2/G3/G4按实际变更 |
| B05b | R05/EV04 | 实现真实生成→候选→确认保存，原子绑定 | V05全链、错来源、并发、重放、失败回滚均通过 | HIGH；独立Security/AI/QA |
| B06 | R06/EV05 | uploaded可手工编辑题面并转换，OCR仍关闭 | 真实图片上传→人工保存→转换→读回；无provider调用 | HIGH；G0/G4，上传安全回归G3 |
| B07 | R07 | 最终同源构建、业务E2E、专业门禁及状态更新 | 全部EV关闭、R02完整、无相关skip；独立复核通过 | HIGH；前述gate汇总；生产G5另授权 |

按 B00→B01→B02→B03→B04→B05a→B05b→B06→B07 串行执行。B04是任何增量迁移生成和执行的前置；前面的步骤若发现必须改schema，暂停该部分，先完成B04及变更审阅。B05a未通过不得借“先接线”绕过来源合同。

## B00：保留现场和证据纪律

在批准范围内复制当前未提交源码，排除.env凭据、上传、缓存和既有数据库；记录文件hash及副本位置，抽样恢复到临时目录验证。只有hash不能称备份，新worktree的HEAD不能代表本工作树。

把核验目录的probe转成自动失败断言：原probe退出0只表示采集成功，不能直接纳入CI当PASS。例如schema被破坏时断言checker必须非0；收到旧response后断言不可确认旧Attempt。保持原probe原样，另建回归测试。

执行日志逐项记录实现diff、命令/环境、原失败→通过、review与gate结果。采用新状态索引链接历史，不将原核验报告改写为PASS。失败反例未关闭前不执行最终accept。

## B01：把再答请求绑定到当前面板与答案

修改候选：review-queue.tsx、现有组件测试、E2E04及新增竞争用例。

推荐每个item维护递增generation和每次request序号：打开、关闭、换题、改答案、提交评分成功、卸载均使不再相关的请求失效。请求捕获itemId、questionId、答案快照、generation和requestId；成功/错误/finally仅在这些标识仍匹配时更新面板。openReanswer加载题目也必须保护，不能只管submitAnswer。

AbortController可用于取消网络，但不能作为正确性唯一保障：被取消的请求可能已在服务端创建Attempt。此Attempt允许保留历史，不得被新面板用于评分。提交期间按钮互斥是辅助，不替代代次检查。

把evaluation、attemptId、答案快照作为同一结果对象接受/丢弃。清除旧结果后不能继续显示旧推荐评分。保留原有独立人工评分能力，但明确不携带已失效Attempt；再答评价确认必须匹配当前答案。

验收：延迟A响应→收起→重开选B→返回A，B仍待判分；再提交B获得新的attemptId后确认，新请求读取Record绑定B。另测加载响应乱序、旧请求报错、卸载、快速双提交、空集/取消/乱序多选及rating0–5。使用真实后端，仅控制响应到达顺序。

## B02：验证KP事实保留，而非重写算法

不改变固定间隔调度或practice/review统计资格。自动错答创建时继承Question KP快照；人工显式[]与替换是权威；Question后续改KP不反向覆盖已确认Mistake。

分层夹具：创建并commit题目及两KP→独立请求错答→新请求读draft→人工确认→新请求读Mistake→错误再答并把返回attempt_id传给rating0→读Record/analytics→受控时钟到期→正确再答及确认→读Dashboard/Practice。每个阶段独立事务，不能只看同session对象。

断言按指标语义：review_count随Record增加；rating<=2增加lapse；due_count随到期状态变化；review Attempt不增加practice count。Dashboard与Practice应依据该夹具数据给出可解释结果，不硬编码不相关全库排序。

分别测试自动入口的省略继承与手工入口显式[]；不将当前手工表单总传[]误当省略。补显式清空、人工替换、非法学科/已失效KP、题目后改KP、重复/并发转换、确认失败rollback。首次变更前先运行；已有正确行为只补验收，不为“有改动”重写。

交付只读历史候选清单：缺关联对象ID、来源Attempt/Question、当前集合、可证明来源、人工清空无法区分标记。不得由空集合推定丢失，不自动回填。默认在隔离fixture证明查询；真实库扫描须另有明确目标与访问授权，无权限时交付查询和范围限制，不能伪造生产数量。

## B03：在关系被删除前检查冻结对象

修改候选：taxonomy_service.delete_knowledge_point、对应router错误映射、legacy freeze公共入口和HTTP测试。

删除KP前查询NoteKnowledgePoint JOIN Note：含legacy mistake则走已有freeze异常与410/code，整个事务无副作用；其他已有children/KnowledgePointLink约束保留。普通Note关联沿既有已核验合同处理，不因修冻结突然切换全局CASCADE行为。不能在删除后检查或把异常吞成成功。

检查竞态：选择稳定的锁顺序，删除与创建/删除Note↔KP链接均锁定同一KP或使用等价可证明的事务机制；不能只在删除端检查而不管并发新增关系。legacy新关联入口本来应拒绝，回归仍需覆盖既有数据与允许的并发路径。若需FK/trigger才能满足不变量，先给增量schema设计，不悄改026/032。

按真实handler列清单并测试：KP delete、folder delete/move、tag merge/delete、suggestions move/add_tag、Note↔KP link/unlink；混合legacy目标首位/末位，未登录、正常管理员、普通Note正例。不得根据一条ASGI case宣称覆盖整个清单。

## B04：双gate比较对象定义

修改候选：sql_owned.py、alembic/env.py、独立catalog检查器及manifest、test_f04_schema_ownership.py、CI backend job。

将schema manifest作为明确版本化的期望，不从被检库自动学习“正确值”。初版由已批准migration在干净scratch实例回放后提取，结合迁移SQL人工审阅，落入版本控制；与revision head绑定。新迁移改schema时必须有显式manifest diff。

检查范围覆盖026的public与legacy_migration命名空间、draft扩展列、受保护表/函数/触发器，以及033约束/索引。记录并比较：

- schema/table/column及类型（含长度）、nullable、server default；
- PK/UNIQUE/FK/CHECK定义、FK动作、约束验证状态；
- 索引列/表达式、顺序、唯一性、partial predicate；
- 函数签名/定义、security-definer与search_path等保护属性；
- trigger绑定表、事件/时机、函数及enabled状态；治理依赖的角色/权限按现有迁移合同检查。

用pg_catalog规范化比较，去除OID等环境差异；不要过度归一化导致谓词/类型变化被吞。未知增删对象必须报出，明确管理范围以外对象不自动删除。

autogenerate allowlist严格匹配schema+type+父表+对象名，并按reflected/compare_to语义限制；ORM对象仍正常比较。catalog checker是独立命令，非只存在于pytest helper；CI执行 ORM check 与 catalog check，任一失败阻断。

验收：clean033/最新head通过；EV03的改integer→bigint、drop purpose CHECK、disable guard trigger全部非0且指出对象；增加default/nullable、同名索引换定义、函数body变化、FK动作变化反例。每项独立事务rollback，结束重查clean通过。保留fresh升级、空库033→027→033与live challenge禁止降级；不越过026不可逆边界。

## B05：选择一条真实canonical创建路径完整修复

### 产品入口与范围

推荐复用现有“从题库记录错题”MistakeDraftEntry：已确认Question + 用户错误答案/错因 → 可选AI错因候选 → 人工编辑/确认 → canonical MistakeDraft。这是当前原方案未选定入口的具体推荐，B05a需G0定版；不能恢复旧Note型错题保存，也不新增工作台或全自动入库。

在现有canonical管理API域增加对应生成/确认动作，复用可适用的prompt/输出结构，但不要把legacy staged生成返回的任意run_id直接视为可信。严格限定新canonical创建任务类型/目的与可输出字段。Capture任务仍以Capture为target，不纳入本入口创建型绑定白名单。

### 服务端可信来源

推荐增量扩展AiRun的来源字段：请求管理员created_by、带版本的creation_context、confirmed_payload_hash（具体列名在B05a定版）。context由服务端构造且创建后不可改：purpose、source Question id/version、错误答案等输入的规范化hash、输出schema/prompt版本。可复用现有review_revision作确认版本，不使用input_summary或客户端回传context作权威。

这涉及新schema，不能宣称“无需迁移”：先B04/G2，新增下一可用revision，不修改旧迁移。历史run来源字段允许NULL，保留读能力，但不得冒认其符合新canonical确认资格。不为旧run猜owner或批量回填。

生成入口先验证get_current_admin与Question版本/可用性，持久化可信run上下文后才调用provider；记录创建失败则明确失败，不输出看似可保存的无run_id候选。gateway只接受服务端注入的上下文，不允许用户选择owner。调用完成后保存输出与validation状态，成功响应返回run_id/review_revision和候选内容。

人工修改候选是允许的，不要求确认文本逐字等于模型输出；保留原候选output与受权限保护的最终确认快照/人工编辑标记，记录确认payload hash及源版本，以区分合法人审修改和换题/换输入；快照按现有私有审计脱敏与访问合同保存，不能只留hash却丢失人审内容。来源题目或作为生成依据的答案变化时，UI清除候选；服务端也拒绝不匹配来源，用户可明确回到纯手工流程。不能声称可侦测用户将AI文字复制进纯手工表单，来源保证只覆盖系统内AI流程。

### 确认原子性、锁与幂等

AI确认使用显式动作且强制run_id；普通手工创建保留兼容，不通过可选source_run_id静默降级AI确认。旧的可选绑定入口也必须收敛到相同校验器或拒绝此用法，不能留下旁路。

事务顺序：按统一锁顺序锁定并刷新run（所有确认/绑定/拒绝路径一致），先校验actor、purpose/task和请求对已存来源context/确认payload的匹配，再区分已绑定与未绑定。禁止在已绑定重放之前用当前Question版本或旧expected revision拒绝请求。

- 已绑定且相同actor/已存来源context/确认payload：核验关联实体存在且归属完整，返回原草稿与一致响应，不再创建DraftItem；不重新要求当前Question版本等于生成时版本，也不重验首次确认用的旧revision。若关联实体缺失或审计状态不一致，报冲突而非新建补洞。
- 已绑定但payload/目标不同：409，绝不覆盖target；不得返回不属于请求者的实体。
- 未绑定run：再按一致锁顺序读取当前Question，核验其版本/可用性、生成输入、succeeded、validation passed/warning、非rejected和expected review_revision；全部满足后同一事务创建DraftItem/MistakeDraft/KP关系、绑定target、写确认hash/accepted/revision及审计，一次commit。
- 失败：所有业务创建/绑定/确认rollback，独立生成run仍可保留为待处理；不可声称外部调用费用回滚。

row lock或CAS需覆盖所有绑定/拒绝/确认入口，旧backfill helper不能成为无锁重绑通道。若使用FOR UPDATE，处理session identity map旧对象，确保锁查询真的刷新状态。两个会话同步到读取点后并发提交：相同请求得到同一实体，不同请求只有一个成功，另一个409。先绑定不同实体再检测不能保证保存幂等。

### 验收与授权

用假provider只替换外部适配器，真实gateway/router/service/数据库/UI贯通，人工点击生成→编辑→确认→新请求读AiRun/草稿。覆盖无run、错actor/来源/版本/task、failed/rejected、validation failed、重复同payload（包括首次成功后Question已改版）、异payload、并发、事务中断及run写失败。Capture原target与人工创建均不退化。

本轮方案不调用真实provider。后续本地实现可用fake adapter验闭环；真实provider成本/样本外发和生产开关另需明确授权。若新增schema或此最小入口不被接受，R05保持PARTIAL/未关闭，不能删掉验收义务而宣称完成。

## B06：让uploaded项直接填写题面

修改候选：CaptureDetail/DraftFieldsSection/ConvertForm、现有capture service及测试。

保留recognize/retry服务端默认关闭。对可编辑的uploaded/recognized/failed项展示“手工题面”入口；用户可显式“使用识别文字作为题面”，但识别文字不能静默变成已确认题面。表单名称区分人工内容与AI候选，避免把手工内容标为AI生成。

保存question_draft_text到现有PATCH服务，成功进入ready后才展示/启用转换。不要仅隐藏识别按钮，也不要为可达性把整个uploaded状态等同ready。只填recognized_text未填题面时给出明确下一步；空题面、保存失败不得假装就绪；recognizing/drafting并发和converted/archived编辑限制沿既有合同。

验收使用真实小PNG上传到本轮隔离UPLOAD_ROOT，再从新uploaded项完成填写→保存→ready→人工转换→新请求读草稿ID；页面刷新后可继续。补已有recognized/failed分支、空内容、HTTP失败/重试、重复转换、390视口/键盘。整个过程不点AI生成，fake provider spy调用次数0、外发封禁；服务端直连识别/重试保持关闭。

## B07：最终验收与交付

先每步定向失败→通过及独立review，再在最终hash上运行Node24全前端测试/两套类型检查，单独fresh库后端全测；专项破坏探针、浏览器夹具和全套测试各用独立库，防止seed污染。

构建Next/OpenNext后用同源workerd+FastAPI重跑原5个E2E及本轮新增竞争、OCR人工、AI确认、KP信息保留场景，跑runtime smoke。Next dev通过只作开发证据，不抵生产工件。保留公开读/legacy兼容/auth负测，不扩大到生产环境。

9项历史skip、2 warnings逐项记载；如果覆盖当前更改的关键门禁则必须补专用fixture运行，否则明确列未验收，不以deselect或删除测试放行。远端CI与生产证据单列。

最终文件：当前状态索引、B00–B07证据账本、题型/关系/竞争矩阵、schema manifest与checker输出、历史候选查询及范围说明、各专业gate和主Agentaccept。退出条件是所有EV和原REQ逐项关闭，不是单测数量增加。

## 执行边界与回退

当前用户请求仅制定返工方案；产品代码、迁移文件、数据库均未在本轮修改。未来实施需明确批准本地返工范围，其中B05新合同及增量schema先完成B05a gate。生产迁移、历史回填、真实provider、commit/push、部署不包含在本方案默认执行范围。

回退只回本轮独立diff，保留用户原脏改动；schema采用增量、旧记录可读，不承诺可逆删除新产生的来源数据。迁移downgrade遇存活绑定须保护性拒绝或单独恢复方案，不能清空审计数据换取绿灯。

遇到重叠编辑、来源合同冲突、无法保证隔离、专业gate失败或范围外schema/生产需求，停止相应项并记录原因，不用弱化权限/guard绕过。

## 本次方案审阅

方案文档：PASS。独立 `/root/rework_plan_review` 审阅通过；其关于AI确认幂等顺序的意见已纳入，并补充题目后改版重放用例。相对链接与新增文档空白检查通过，核验清单2,881份既有文件哈希无变化。本轮仅新增本文；产品状态仍FAIL，实施、专业实现门禁及修复运行验证未执行。
