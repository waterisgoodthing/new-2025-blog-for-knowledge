# 修复方案执行情况独立核验

日期：2026-09-27。**结论：FAIL（R00–R07 整体退出条件未满足）**。已有实质修改，但原 README 的“R00–R07 本地 PASS”不能成立。测试套件绿灯不能抵消本次实测的业务与治理缺陷。本结论不是“系统所有功能都失败”，也不评价未检查的生产状态。

本次授权：验证执行情况。WORKER；主 Agent 负责运行、反例、整合与报告，`/root/verify_ai_schema` 独立只读审查 R04/R05，`/root/verify_learning_freeze` 独立只读审查 R01/R02/R03/R06，并复核新增 OCR 反例。两位均无实现所有权。原方案的 `/root/plan_review` 只审过方案，不是本轮实现审查。主 Agent 接受本核验报告，**不接受当前修复候选为全项完成**。

写入范围仅本 execution-verification 目录。未修改业务源码/既有方案状态，未提交/推送/部署，未访问生产或调用真实 AI/OCR。运行使用本轮新建 PG16 集群（127.0.0.1:60535），独立 scratch 库、合成题目与真实测试管理员cookie；无认证bypass。结构破坏探针均事务rollback；本地夹具仅留于本轮临时集群。

## 逐项裁定

| 任务 | 当前状态 | 已证明完成的部分 | 未满足的退出条件 |
|---|---|---|---|
| R00 | PARTIAL | 原基线2872项无缺失，27项变化与记录数量一致；另有新增sql_owned和专项测试 | hash不是可恢复副本；未发现R00合同定版、串行专业gate和当时独立复核的完整证据。既有文件中的实施授权声明不替代本线程可核验的批准记录；不反推过去未经授权 |
| R01 | FAIL | 真实浏览器C后A提交为A,C并判correct；集合选择已修 | 收起/重开竞争会把旧判分和Attempt绑定到新答案，见EV01 |
| R02 | PARTIAL | 自动错答KP快照、draft→mistake传递；定向测试及浏览器提交后新请求读到review=1/lapse=1/practice attempt=1/due=0 | 显式空/替换/题目后改KP/并发失败完整矩阵、再次正确到Dashboard/Practice、历史只读候选清单未齐。现有chain测试正确A,C后人工rating0且未传attempt_id，不能替代完整V02 |
| R03 | FAIL | suggestions等主要冻结路径已有测试通过 | 删除KP经CASCADE仍能清掉legacy Note关联，真实鉴权HTTP204与新会话回读已证实，见EV02 |
| R04 | FAIL | fresh upgrade033与alembic check成功；四索引及CHECK入metadata | 列类型、CHECK删除和禁用保护trigger反例均被双gate漏报，见EV03 |
| R05 | FAIL | 网关新增run_id，保存服务可做局部绑定，原定向测试通过 | UI生成→canonical保存没有实际接线；缺可信来源核验、并发冲突和保存重放幂等，见EV04 |
| R06 | FAIL | 默认关闭识别；真实HTTP识别/重试均recognition_disabled、attempt_count=0；UI识别按钮隐藏 | 新uploaded项手工文字保存后无法进入题面/转换，见EV05；不能以service直接PATCH成功证明用户路径 |
| R07 | FAIL | 本轮Node24前端525通过、两套类型检查通过；空库后端941通过、9skip | 多个必修项反例失败；原实施没有真实浏览器/独立实现审阅，本轮补验发现缺陷；未满足所有REQ/V退出条件 |

## 必须返工的发现

### EV01 — P1：迟到判分污染新答案与ReviewRecord

位置：`src/app/manage/(workspace)/review/review-queue.tsx:124–137` 无请求代次校验；`:255–258` 收起不受busy限制。重开面板后仍按item.id接收旧响应。

真实Chromium步骤：选A提交→暂缓实际后端响应→收起→重开选B→放行A响应→页面显示B选中但出现A的评价→确认rating0。POST submit返回200；新请求读取ReviewRecord的attempt_id等于旧A Attempt。只延迟网络响应，不mock判分/保存服务。该结果违反V01“输入与结果不混淆”。

证据：[browser-probes.txt](evidence/browser-probes.txt) 的 RACE_VISIBLE/RACE_PERSISTED；[截图](evidence/race-stale-evaluation.png)；[可复现脚本](evidence/browser_probe.cjs)。反例脚本退出0表示成功观察到缺陷，不是业务验收PASS。

返工验收：请求取消/代次或完整互斥解决面板切换，重复上述时序不得接受旧评价，更不得提交旧Attempt；保持正常多选、取消和六档评分。

### EV02 — P1：KP删除绕过legacy关联冻结

位置：`backend/app/services/taxonomy_service.py:247–267` 只检查KnowledgePointLink；`backend/app/models/note_knowledge_point.py:34–38` 的KP外键ON DELETE CASCADE。

夹具：legacy Note只通过NoteKnowledgePoint关联某KP，无子KP与多态link。服务层删除成功且关系数变0。随后另设已提交夹具，真实管理员登录发DELETE `/api/admin/knowledge-points/{id}` 返回204，新数据库会话读回关联数0。直接unlink被freeze保护而间接删除仍可写，违反V03。

证据：[invariant-probes.txt](evidence/invariant-probes.txt)、[browser-probes.txt](evidence/browser-probes.txt)、[http-persisted-readback.txt](evidence/http-persisted-readback.txt)。这是已登录业务冻结漏洞，不称认证绕过。

返工验收：把taxonomy删除及其关联副作用加入冻结预检和回归，命中legacy时拒绝且保持原关联；普通KP行为另测。现有test_f03单例并没有覆盖执行文档宣称的folder delete/tag merge/unlink/混合目标末位全部场景，证据索引须据实收敛。

### EV03 — P1：schema双门禁产生假阴性

位置：`backend/app/models/sql_owned.py:89–110` 排除SQL-owned对象；`backend/tests/test_f04_schema_ownership.py:76–124` 主要查对象名称存在，无完整shape/definition检查。

在全新033库中，每次独立事务、结束rollback：

1. 将draft_items.conversion_sequence从integer改为bigint；
2. 删除ck_webauthn_challenges_purpose；
3. 禁用trg_lnm_guard。

三项均为 `catalog_gate=[]`、`orm_gate=[]`。因此“alembic check无新增操作”不证明无漂移。模型声明CHECK不等于Alembic能比较CHECK。

证据：[invariant-probes.txt](evidence/invariant-probes.txt)、[probe_invariants.py](evidence/probe_invariants.py)。SQL-owned表内列/nullable/default、FK/CHECK、函数/触发器定义与启用状态等仍缺；allowlist也未实际检查schema/reflected，与自身说明不符。

返工验收：双gate需比较权威对象定义，至少以上三种反例必须失败；不能增加忽略范围凑绿。保留026不可逆边界与033活challenge保护。

### EV04 — P1：AI关联仍未形成可信的真实保存闭环

静态接线：全src的source_run_id只在API类型；canonical `capture/components/mistake-draft-entry.tsx:67–74` 不发送；生成调用仍在旧staged表单，其保存已冻结。新增类型/可选参数不等于用户可完成生成→保存。

来源：`ai_run_service.py:95–117` 仅查存在、状态、task和target；`mistake_service.py:85–92` 不传来源、版本或产物核验。隔离实测让output为“QUESTION A ONLY”的成功run绑定“UNRELATED QUESTION B”的草稿，成功。

竞争：两个独立会话先读取同一空target，按确定交错顺序分别bind不同target并commit；两者均成功，后写覆盖前写。db.get没有行锁/CAS。该探针是可实现竞争时序的确定重放，而非靠随机压力推断。

另外：每次保存先创建新Draft，重放同run不会返回原实体，只会因新id冲突；helper同target幂等不等于保存幂等。gateway记录失败可返回None、source_run_id可选，尚无可验证机制区分人工与必须追踪的AI来源。

证据：[invariant-probes.txt](evidence/invariant-probes.txt) 的wrong_source_bind/stale_concurrent_bind；源码及独立review。这里只运行合成run，无真实provider；来源反例为真实service+PG，不包装成完整UI成功链。

返工验收：补当前canonical生成/保存的实际消费者和可信来源绑定；V05覆盖同run重放、错题/错来源、并发、失败rollback、记录不可用；在真实HTTP/浏览器保存与新事务回读中验证，不只helper单测。保留Capture原target。

### EV05 — P1：OCR禁用后新采集手工路径走不通

已证实禁用本身有效，但用户按提示手工输入“识别文字”并保存PATCH200后，库中仍为uploaded、question_draft_text=null。页面题面字段、转换按钮、AI草稿按钮、识别按钮均为0。

根因：UI `capture-workspace.tsx:592` 只PATCH recognized_text；service `capture_service.py:149–150,171–172` 只在有question_draft_text时进入ready；UI `:707–711` 对uploaded隐藏题面编辑、`:457` 只给ready显示ConvertForm、`:787–790` uploaded也无法生成草稿。

初次脚本等待转换表单超时，随后以数据库回读、页面计数和源码交叉验证，排除了仅locator不准的解释。后端测试 `test_capture_service.py:219–224` 直接PATCH question_draft_text绕过了实际UI。

证据：[ocr-browser.txt](evidence/ocr-browser.txt)、[ocr-deadend.txt](evidence/ocr-deadend.txt)、[截图](evidence/ocr-manual-deadend.png)。fixture附件只有合成元数据，无实际图片；它不用于证明上传/预览，只隔离验证上传后uploaded状态的手工路径。未启用/调用OCR或AI。

返工验收：禁用时新uploaded项应能在UI填写题面、保存、转换并新请求读回，不能依赖AI或开发者直接调用PATCH绕过。

## 本轮实际运行与限制

| 检查 | 结果/证据 |
|---|---|
| Node24前端完整单测 | 70 files / 525 passed；[日志](evidence/frontend-node24.txt) |
| shipped与test TypeScript | 两者exit0，关闭incremental写入；[shipped](evidence/typecheck-node24.txt)、[test](evidence/test-typecheck-node24.txt) |
| 后端定向 | 47 passed；[日志](evidence/targeted-backend.txt) |
| 后端完整，单独全新空库 | 941 passed / 9 skipped / 2 warnings / 47 subtests；[日志](evidence/clean-full-backend.txt)。与原记录940有数量差异，不据此判功能增减 |
| 初次后端完整，已有业务seed库 | 21 failed / 920 passed；[日志](evidence/full-backend.txt)。该次夹具不符合若干测试的空库假设，废弃为产品验收依据；随后在另一全新空库重跑通过，不隐去首次结果 |
| fresh migration与check | 两个新scratch库upgrade head成功；初始alembic check通过。不是生产迁移证据 |
| Chromium定向业务 | 正常多选correct；真实cookie登录；R01迟到响应持久化反例；R03删除204及关系回读；OCR识别/重试关闭和手工死路 |
| schema/AI反例 | 真PG执行，结构破坏逐例rollback；详见EV03/EV04 |

后端九skip：6项LSR03专用环境未提供，3项Week2测试仍要求旧scratch前缀；不能计入通过。2 warning来自既有AI日志AsyncMock未await。未弱化guard、没有deselect。

浏览器为本轮当前源码的Next开发服务+FastAPI+隔离PG，**不是OpenNext/workerd生产工件验收**。本轮未重跑Next/OpenNext构建、原全套5个E2E或workerd smoke；原执行记录的构建PASS只保留为历史声明。已有确定反例足以否决R07，继续堆叠通过计数不会关闭它们。

未验证：远端CI、真实provider10样本、真实设备passkey、生产数据/迁移/恢复/发布；未执行历史回填。V02/V03/V05等尚未全面覆盖的分支保持NOT_VERIFIED，不因本次局部实测扩大为全项PASS。

## 证据可信度与后续顺序

原执行文档混有“仅方案未授权”与“已执行”两代状态，且以jsdom和helper测试替代部分真实验收；其PASS需要撤回或精确缩小。保留原文不覆盖，本报告是独立核验结果。

建议先按原任务顺序返工EV01/EV02，补R02遗漏矩阵，再修EV03/EV04/EV05，最后重做R07同源运行与专业gate。不新增算法、不回填旧数据、不启用provider，也不通过改验收标准关闭问题。

完成返工后，必须复用本报告的反例转为回归，分别获得G2（schema）、G3（冻结/来源）、G4（AI/OCR）等实际门禁证据。当前结论为不通过，不构成任何代码、迁移或发布批准。

## 最终复核与现场保留

两位独立reviewer已复阅本报告及对应探针输出：verify_ai_schema确认EV03/EV04，verify_learning_freeze确认EV01/EV02/EV05；均认为结论与证据一致，无待修报告问题。这是报告复核通过，修复候选仍为FAIL。

本轮开始时记录的2,881份既有文件哈希在结束时均未变化，见[保留检查](evidence/preservation-check.json)。报告链接与空白检查通过。本轮启动的Next/FastAPI进程已发终止信号，PG集群已正常停止，见[清理记录](evidence/cleanup.json)；未删除任何原有服务或数据库。临时集群目录保留供需要时复查。
