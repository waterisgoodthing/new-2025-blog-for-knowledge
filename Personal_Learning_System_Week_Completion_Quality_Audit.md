# 个人学习系统全 Week 完成质量技术审计

> 文档治理（2026-10-09）：历史审计/建议快照保留。测试、版本、缺陷与权限描述只对应报告原时点；本轮重新核验结果以当前审查和状态为准，不覆盖原裁定。 当前入口见 [文档索引](docs/DOCUMENTATION_INDEX.md)。

审计日期：2026-09-27。对象：`/Users/limengyang/2025-blog-public` 的当前工作树。分支 `refactor/baseline`，HEAD `4a954eaa92952fcc5a6b18a2e15d2e824b094e41`。主负责人：GPT-6 Astra 主 Agent；实际审计 Worker 均为 `gpt-6-luna`。

本报告是审计交付，不是修复、提交或发布批准。代码、数据库迁移文件及既有数据均未修改；测试只写本轮新建的本地隔离 PostgreSQL 集群。报告中的百分比是验收面覆盖估计，不是测试通过率、开发工时或生产可用率。

## 1. Executive Summary

**系统结论：PARTIAL；当前不能宣称完整学习闭环或生产发布门禁通过。** Convergence Week 1–4 的主要功能已落地，估计实现与验收覆盖约 **75–85%，Medium confidence**。不能用此区间抵消任何失败的硬性验收。通用 September W1–W5 是另一条路线，不混入这个分母。

本轮实际通过：前端 70 文件、522 测试；后端 922 测试、47 subtests，另有 9 skipped；两套 TypeScript 检查；Next.js 与 OpenNext 构建；PostgreSQL 16 空库升级 033、空库 033→027→033；workerd 20/20 资源与 23/23 smoke；Chromium 5/5 E2E，包含真实错答草稿生成和再答复习记录回读。

但补充业务探针发现：

1. **P1 / F01：多选题再答不能表达多选集合。** 点 A、C 后仅提交 C，API 返回 incorrect。当前 E2E 只覆盖短答，组件测试主要使用单选样本。
2. **P1 / F02：题目知识点在错答→草稿→错题链上默认丢失。** 复习记录成功生成，但该知识点的 review/lapse/due 指标没有相应回流；Dashboard 与后续选题因此可能基于不完整信息。
3. **P1 / F03：legacy mistake 写冻结存在元数据入口遗漏。** suggestions 的 move_to_folder 对旧错题仍返回 200 并改写 folder_id。
4. **P1 / F04：schema authority 未对齐。** `alembic check` 把 026 的迁移专有表、列以及 033 索引识别为待删除对象。升级通过，但不能安全地无审查采用 autogenerate。
5. **P1 / F05：AI creation target 回填仍停留在 helper。** 没有生产确认入口调用；Capture 对现有实体的 linkage 已存在，不能把它们一起说成未接线。

旧报告中的 CI 数据库名不兼容、CLI event-loop 生命周期、latest-challenge 串扰和 E2E 只测外壳等问题，当前源码已发生修复；本报告不继续沿用旧失败结论。OCR 真实样本质量、远端 CI、生产部署与真实库数据状态仍是 **NOT_VERIFIED**。

## 2. Audit Scope

覆盖主学习路线 Phase 0、Week 1–4（PR-01–19）、September 通用 W1–W5、W6+ 候选及其他历史计划的路线边界；审查 frontend/backend/API/ORM/migrations/tests/CI、跨周依赖、学习闭环、技术债和 Future Work。

当前技术栈由 `package.json`、`backend/requirements.txt` 及运行环境确认：Next.js 16.2.12、React 19.2.1、Tailwind 4、SWR 2、Zustand 5、FastAPI/SQLAlchemy async/Pydantic、Alembic，隔离验证 PostgreSQL 16.14。初轮前端单测和 tsc 使用现场 Node 26.0.0；正式构建和浏览器套件显式使用 Node 24；为消除CI等价性疑问又在Node24补跑前端522项全通过（frontend-test-node24.txt），符合项目 engines。Python 使用 `backend/.venv`。

范围限制：没有改生产数据、调用真实付费 OCR/LLM、推送 GitHub 或触发远端流水线；没有对全站每页面做 WCAG/Lighthouse、对生产做压力测试。跳过项、源码推断、历史记录不能包装成当前运行证据。所有旧脏文件保留；本轮新增审计报告、workflow 与证据。

## 3. Audit Methodology

采用 Requirement → 当前 Implementation → 验证 Evidence → 判定。A=本轮运行/测试/数据库/浏览器；B=解释业务语义的当前源码；C=文件/路由存在；D=计划或历史声明。历史运行结果明确标“历史 A”，不能替代当前 A。

任务状态限定为 VERIFIED_COMPLETE、COMPLETE_WITH_DEBT、PARTIAL、SURFACE_COMPLETE、IMPLEMENTED_UNVERIFIED、NOT_IMPLEMENTED、REGRESSION、OBSOLETE。NOT_VERIFIED 用于证据/运行范围，不用来假称未实现。没有证明“曾正确而现在退化”时只标 PARTIAL，不滥用 REGRESSION。

Worker 分工与源报告位于 `docs/workflows/week-completion-quality-audit-2026-09-27/workers/`：baseline_week12（需求基线及 Week1–2/September）、week3_architecture（Week3/架构与前端）、week4_backend（Week4/数据库与工程测试）。同一 Worker 接续专项仍是实际子代理，不伪称新增独立审稿人。上游曾发生 502，恢复后延续原任务。

主 Agent 独立完成运行验证、复现、裁决和最终整合。反向复核包括全部最终 P1、全部表面完成/未实现项、跨周主链。曾怀疑键盘数字被再答输入冒泡拦截，完整 JSX 显示评分组与输入是兄弟节点，已撤回；Practice 页面可转到有真实作答功能的 QuestionEditor，因此“没有任何练习执行链”也被撤回。

证据索引（下文 E 路径均相对此目录）：`docs/workflows/week-completion-quality-audit-2026-09-27/evidence/`。

| 编号 | 当前证据 | 结果与适用范围 |
|---|---|---|
| E01 | frontend-test.txt | 70 files / 522 pass；jsdom/单测不证明真实浏览器 |
| E02 | typecheck.txt、test-typecheck.txt | exit 0；保留树排除项另述 |
| E03 | build.txt、build-cf.txt | Node24 Next/OpenNext exit0；不是部署证据 |
| E04 | migration-upgrade.txt、migration-empty-roundtrip.txt | PG16 fresh033、033→027→033成功；不覆盖生产旧数据 |
| E05 | backend-test.txt | 922 pass、9 skip、2 warning、47 subtests；无deselect |
| E06 | alembic-check.txt | exit255；metadata/autogenerate drift |
| E07 | runtime-smoke.txt | 20/20 assets、23/23 checks；只证明所查入口 |
| E08 | e2e.txt | Chromium5/5；真实登录、写作、错答草稿、再答记录、Error/Retry |
| E09 | probe-multiple-choice.cjs、probe-multiple-choice.txt、multiple-choice-failure.png | 真实UI A+C→C→incorrect，未确认错误rating |
| E10 | probe_learning.py、probe-learning.txt | 真实PG/service KP断链；事务观察后rollback |
| E11 | probe_freeze.py、probe-freeze.txt | ASGI真实handler+PG元数据写成功；admin依赖合成，不用于证明认证 |
| E12 | migration-downgrade.txt | 有2个live challenge时033降级被拒绝；预期fail-closed，非迁移缺陷 |
| E13 | skipped-tests.txt、frontend-test-node24.txt | 9skip逐条原因；Node24 522/522补验 |

完成度区间按任务实际行为、验收覆盖和证据缺口综合估计；较宽区间反映未经本轮重演的细节。每个 Week 的硬 Gate 单独裁决。生产成熟度不以这些百分比表示。

## 4. Week Completion Overview

| 路线/Week | 原始目标 | 当前状态 | 完成区间/Confidence | 下一阶段前置 |
|---|---|---|---|---|
| Convergence Phase0 | 工程命令、runtime拓扑 | COMPLETE_WITH_DEBT | 85–95% / Medium | 本地拓扑可用，远端未验 |
| C-W1 | Trusted Runtime/写作/异步态/guest migration | COMPLETE_WITH_DEBT | 90–97% / Medium-High | 主要基础成立；生产状态不推定 |
| C-W2 | Closed Review Loop | PARTIAL | 80–90% / High（缺陷），Medium（区间） | 多选再答阻断完整 Gate |
| C-W3 | Canonical Learning | PARTIAL | 70–85% / Medium-High | KP断链、freeze遗漏阻断可靠基础 |
| C-W4 | Release Gate | PARTIAL；release未通过 | 65–80% / Medium | OCR/AI治理/当前P1尚未闭合 |
| September W1–W5 | 拆除、视觉、编辑器、渲染、SEO性能 | 分路线逐项见§5 | 不与C-W合算 | 多项未实施或未验收 |
| C候选PR20–26、Sept W6+ | 未独立批准的后续能力 | 路线占位 | 不计完成率/逾期 | 需独立需求与授权 |

基线来自 `personal-learning-system-convergence/{requirements,design,tasks}.md` 与各周任务书；September 来自 `docs/roadmap-2026-09.md`。旧 `refactor-plan*` 的 Week 编号被 September 明示取代，标 OBSOLETE（计划权威，不等于代码删除）。本次逐任务覆盖所有检索到的活跃Week编号路线；非Week的Phase/UI大方案只做inventory与相关历史欠账映射，不声称已逐项验收所有Phase任务。June P0–P6、unification phases0–8、UI Foundation/UI V2 是独立计划，已纳入历史欠账线索，不能创造“Convergence Week5”。

## 5. Week-by-Week Audit

### 5.1 C-Week 1：可信运行与写作

原目标：workerd 工件可运行、笔记/博客新建编辑、错误可重试、guestbook 由迁移治理。前置 Phase0。当前主要链条有运行证据，未证明所有历史19项写作细节/全视口验收本轮重跑。

| ID | Task / Expected | Actual | Evidence | Status | Risk |
|---|---|---|---|---|---|
| T00/T00b | 工程命令与拓扑 | 当前可构建、迁移、启动、测试；lint与远端门禁另有欠账 | E01–08；ci.yml；runtime-smoke.mjs:120–149 | COMPLETE_WITH_DEBT | P2 |
| PR01 | smoke可阻断失败资源/API | 检查home引用资产、notes和health，失败计数形成退出状态 | scripts/runtime-smoke.mjs:120–149；E07 | VERIFIED_COMPLETE | 不是页面业务/性能验收 |
| PR02 | ContentEditor新建/编辑Note/Blog | manage notes三路由复用content-editor/use-note-editor，API持久化；本轮E2E创建与再次编辑笔记 | src/app/manage/(workspace)/notes/components/content-editor.tsx；src/hooks/use-note-editor.ts；E08 | COMPLETE_WITH_DEBT | Blog发布/移动Drawer未全部复演 |
| PR03 | loading/empty/error/retry | AsyncStatePanel实现重试、alert/focus/reduced-motion；notes错误恢复真实通过 | src/components/async-state-panel.tsx:26–89；src/app/notes/page.tsx；E08 | COMPLETE_WITH_DEBT | 全站并非都复用/覆盖 |
| PR04 | fresh guest schema与旧表保护 | 027检查双表、列/索引兼容和ownership；本轮全链fresh通过 | backend/alembic/versions/027_guestbook.py:13–95；E04、E05 | COMPLETE_WITH_DEBT | 生产旧表兼容未查 |

未完成/隐性问题：smoke成功不能证明API读取内容成功；E2E一条Note不能覆盖Blog发布/撤回；不同异步组件并存。八维：Architecture分层成立；Frontend共享编辑器有实用价值；Backend沿用受保护写接口；Database迁移可回放；API客户端接线成立；UX基本错误恢复可用；Testing有真实浏览器但覆盖非穷尽；Maintainability仍有旧路由树负担。最大风险是将本地证据当生产验收。

### 5.2 C-Week 2：复习状态机与再答

原目标：wrong Attempt→MistakeDraft→Mistake→ReviewItem→wrong re-answer/lapse→到期→连续正确→mastered，必须持久化。API/调度实现不是空壳；UI多选输入破坏了一个合法题型。

| ID | Task / Expected | Actual | Evidence | Status | Risk |
|---|---|---|---|---|---|
| PR05 | 028/029状态与last_rating/record状态 | 模型/schema/DTO有对应字段，migration更新存量算法 | backend/alembic/versions/028_review_items_v2.py、029_review_record_states.py；models/review_item.py；E04–05 | VERIFIED_COMPLETE | 老数据语义部署前盘点 |
| PR06 | lapse/阶梯/mastery/并发 | rating0/1→1天，2→2天并清streak；成功3/7/14/30；4连且末评≥4 mastered；锁行+expected_due防冲突 | backend/app/services/review_item_service.py:14–26,62–81；tests/test_review_scheduling_v2.py；E05 | COMPLETE_WITH_DEBT | mastery永久排出due是设计边界 |
| PR07 | 分题型再答+Attempt归属 | 自动/短答规范化/needs_human；review context排除practice统计，record校验题目关联 | backend/app/services/reanswer_service.py:73–148；review_item_service.py:44–60；E05、E08 | VERIFIED_COMPLETE | 人工判定仍落Boolean false，解释依赖context |
| PR08 | UI再答/建议/确认/6档 | 短答链真实成功；多选buttons每次覆盖单值 | review-queue.tsx:124–159,169–199；E08–09 | PARTIAL | P1 F01 |

八维：Architecture服务调度清楚；Frontend单值状态与集合题型冲突；Backend状态机有负测；Database记录/状态同事务；API多选支持正确但UI契约未贯通；UX多选不可用、参考答案辅助不足；Testing绿灯掩盖题型矩阵缺失；Maintainability需统一判分而非另建第三套。未完成：修复并以多选真浏览器复验；整条反复到期mastered的UI全链本轮未逐轮模拟，后端状态机已测。历史028窗口是否存在生产streak错配未查，列条件风险而非已发生数据事故。

### 5.3 C-Week 3：canonical数据与学习决策

原目标：public mistake切换、legacy冻结、KP指标、Note↔KP、daily practice选择、canonical Dashboard。执行依赖应为 PR09→PR10→PR12→PR13→PR11。

| ID | Task / Expected | Actual | Evidence | Status | Risk |
|---|---|---|---|---|---|
| W3-00 | 合同/030基线/安全runner | guard明确本地scratch，现链已至033；本轮使用全新独立集群 | app/utils/scratch_db_safety.py:15–72；scripts/week3-scratch-guard.py；E04–05 | COMPLETE_WITH_DEBT | 历史目标数据未重迁 |
| PR09 | public allowlist+031+冻结+ledger迁移 | active+public DTO成立；主要legacy写410；suggestions folder mutation遗漏 | routers/public_mistakes.py:12–30；routers/suggestions.py:66–78；E11 | PARTIAL | P1 F03 |
| PR10 | KP四指标/派生/weakness排序 | 聚合公式存在且单查询；QuestionKP与MistakeKP写链未贯通，自动错答复习漏统计 | services/kp_analytics_service.py:47–168；attempt_service.py:58–69；E10 | PARTIAL（端到端）；聚合函数有实现 | P1 F02 |
| PR11 | 三问Dashboard、Top3/recent4 | summary复用canonical服务，due/practice可跳转；依赖不完整KP输入，失败子查询会降为空 | dashboard_service.py:119–203,257–327；dashboard-content.tsx；E05、E08 | COMPLETE_WITH_DEBT | 不能证明建议完备 |
| PR12 | 032 FK/unique+link/unlink API/client | 新表联合PK、CASCADE与反向index；幂等关联；没有笔记页面消费者 | models/note_knowledge_point.py:10–41；services/note_knowledge_point_service.py；src/lib/api/notes.ts:194–221；E04–05 | COMPLETE_WITH_DEBT | API完成≠产品关联体验完成 |
| PR13 | 确定性选题，不足返回真实数量 | weak排序，排近期practice/mastered，默认3上限10；页面链接QuestionEditor，编辑页可真实作答 | practice_service.py:86–196；practice-today.tsx:66–88；question-editor.tsx；E05、E08 | COMPLETE_WITH_DEBT | 缺独立practice session；非选择API违约 |

八维：Architecture有canonical而非纯schema；Frontend已接Dashboard/Practice但操作借用编辑器；Backend存在链路契约遗漏；Database三类KP关系各有用途但复制规则不一致；API公开DTO与私有学习边界明确；UX自动草稿无知识点警示、弱点可能缺证据；Testing逐模块多、跨模块保留语义少；Maintainability有双代统计和双target表示。最大风险是“记录成功”被误认为“知识状态已更新”。原计划Unique冲突措辞与后续幂等合同需同步，但不能凭最早表格断言幂等实现错误。

### 5.4 C-Week 4：发布门禁

原目标：OCR诊断及真实样本/入口决策，WebAuthn持久化与防重用，login throttle，AI target纪律，四job+E2E，safe legacy cleanup。

| ID | Task / Expected | Actual | Evidence | Status | Risk |
|---|---|---|---|---|---|
| PR14 | 失败分类、10受控样本、≥8/10或显式禁用 | 分类/重试有实现；报告明确mock-only，不能推出真实可用率与入口策略 | services/capture_failure_taxonomy.py；capture_recognition.py；week4/evidence/pr-14-ocr-baseline-report.md；E05 | PARTIAL | 真实OCR质量NOT_VERIFIED |
| PR15 | 三ceremony store/verify/consume+033 | 按client challenge hash+purpose/binding锁行；CLI单loop；当前负测与真实连续options通过 | services/passkey_service.py:48–80；webauthn_challenge_service.py:166–210；cli.py:159–229；E04–05 | COMPLETE_WITH_DEBT | F04 metadata；真实设备ceremony未验 |
| PR16 | 配置化双维延迟与观测 | 串行失败阶梯、账号容量/长key有界；先查后计数无inflight预约，IP只TTL | routers/auth.py:184–211；services/login_throttle.py:91–199 | COMPLETE_WITH_DEBT | P2并发/多进程能力边界 |
| PR17 | 4 jobs+5真实业务E2E | 名称guard相符；新版seed+readback；本轮本地5/5成功，远端未知 | .github/workflows/ci.yml；tests/e2e/03-capture.spec.ts、04-review-flow.spec.ts；E01–08 | COMPLETE_WITH_DEBT | 远端CI NOT_VERIFIED |
| PR18 | 三证据安全删除 | 小集合无引用组件已删除，SM2兼容仍被导入未乱删；构建/tests通过 | week4/evidence/pr-18-cleanup-components.md；git初始状态；E01–03 | COMPLETE_WITH_DEBT | 不等于September大拆除完成 |
| PR19 | transient/持久化分类及创建后回填 | Capture已有target；backfill helper无生产caller；其他调用点分类待闭合 | ai_run_service.py:178–203；capture_recognition.py:91–96；docs/architecture/ai-governance.md:35–50 | PARTIAL | F05 helper子能力SURFACE_COMPLETE |

八维：Architecture auth/gateway边界清楚但authority欠账；Frontend OCR错误展示/重试而非质量保证；Backend旧严重缺陷有修复，throttle非全局限流器；Database fresh可用而autogen不安全；API E2E真实读回；UX不能把mock成功率当承诺；Testing明显加强仍欠完整题型/生命周期；Maintainability CI可复现而治理分类未闭合。不存在证据支持当前M4发布通过。

### 5.5 September W1–W5 与候选边界

这是 `docs/roadmap-2026-09.md` 的另一套周计划，不能和上面的C-Week任务互相替代。逐项当前代码矩阵见本报告附录A；W5 metadata/GA/Lighthouse未实现或未完成，与学习功能可用并不矛盾。未批准不等于已经完成，也不自动意味着执行逾期。

Convergence PR20 Authentication UI、PR21 Today本地工作台、PR22候选确认、PR23跨设备布局、PR24 Review Undo、PR25 Daily AI、PR26 Capture后台任务是候选/路线占位；不是M1–M4欠账。现有登录功能不等于PR20设计切片完成。旧refactor Week1–5作为被替代计划标OBSOLETE，未兑现的仍有价值事项在September映射核查，不重复计数。

## 6. Architecture Audit

当前是 Next.js App Router → typed clients → FastAPI router → service → SQLAlchemy async → PostgreSQL，OpenNext/workerd提供前端运行。服务不是全无分层，也不需要为个人项目新增Repository层或微服务。`get_db`在请求结束commit/异常rollback（database.py:20–29）；关键状态转换显式锁行/版本检查。

canonical实体和旧Note型错题共存。保留只读兼容本身是批准边界，不等于架构错误；错误是冻结漏口、旧统计与新统计同屏以及关系复制遗漏。Blog/Notes公共内容、静态public资产、GitHub导出与PostgreSQL是不同owner，不建议在本次修复中整体迁移。

## 7. Canonical Data Model

| 节点/关系 | 已存在并实际使用 | 主业务语义/边界 |
|---|---|---|
| Subject→KnowledgePoint | FK/父子taxonomy，编辑与选题使用 | 是学科分类树，非先修DAG |
| Question→QuestionKnowledgePoint | 正式题目多KP连接 | attempt错误率/选题权威入口 |
| Attempt | practice/review context、Boolean correctness | 无通用ungraded状态；review needs_human用false而排除practice聚合 |
| MistakeDraft→Mistake | 人工确认、版本/转换、ReviewItem创建 | 默认KP并不从Question继承（F02） |
| KnowledgePointLink | 多态mistake/draft/其他实体 | 只有KP端有真实FK，target文本依赖service完整性 |
| ReviewItem | mistake_id FK及target_id文本共存 | active/paused/mastered与due；无两标识相等的DB证明 |
| ReviewRecord | item/attempt链、前后状态与间隔 | 真实持久化，并非日志外壳 |
| NoteKnowledgePoint | 双FK/联合主键 | API可用，未被编辑器/学习聚合消费 |
| mastery | ReviewItem派生状态 | 不是KnowledgePoint mastery score或概率估计 |
| Practice | 动态候选DTO | 不是持久化PracticeSession实体 |

依据 `backend/app/models/{question,attempt,mistake,review_item,taxonomy,note_knowledge_point}.py` 与§5服务。表存在仅C，以上“实际使用”均有service调用链B；E05/E08/E10提供部分A。

## 8. End-to-End Data Flow

```text
QuestionEditor（普通作答）
  → src/lib/api/attempts.ts → /api/admin/attempts
  → attempt_service → Attempt(practice)
  → 错答自动MistakeDraft [Question KP此处未复制]
  → MistakeDetail确认 → mistake_service.convert_mistake_draft
  → Mistake + ReviewItem → response → UI

ReviewQueue → /attempts/review → reanswer_service → Attempt(review)
  → 用户确认rating → /review/items/{id}/submit → 锁行/归属校验
  → ReviewRecord + ReviewItem新间隔/状态 → response →队列移除
  → Mistake KP links → KP analytics → Dashboard/Practice
                    ↑ F02使某些真实记录到不了此聚合
```

E08证明两条合法短答路径真实可执行；E09证明另一题型失败；E10证明持久化复习记录不保证统计回流。浏览器以cookie登录并credentials include；只有E11为了隔离handler业务将admin依赖替换，明确不是认证攻击复现。

## 9. Learning Loop Audit

系统已能“记录并安排复习”，也有确定性“下一步做什么”的初级选择，不能称纯记录本或纯Mock。仍未形成对所有合法输入可靠的闭环。

| 用户问题 | 当前回答能力 | 缺口 |
|---|---|---|
| 今天复习什么 | active且到期ReviewItem队列 | mastered永久退出自动队列，长期遗忘无观测 |
| 今天练什么 | 弱KP顺序+近期排除+mastered排除，缺样本Empty | 无独立练习会话；零样本与强弱证据不足需区分 |
| 哪些正在遗忘 | lapse历史计数/到期数 | 不是遗忘概率；漏KP会漏计 |
| 哪些题重做 | 错题队列+再答 | 多选输入失败；参考答案/人工判断UX不完整 |
| 薄弱在哪里 | practice错误率+review/lapse/due排序 | 两条关联路径必须完整，否则仅部分事实 |

E10：已关联KP=1的Question错答后draft_kps=[]、mistake_kps=[]；ReviewRecord创建，但review_count与lapse_count仍0；practice count从1→2。不是“分析算法复杂度不够”，先是输入关系没有保留。修关系和判分之后才讨论更先进调度。

## 10. Frontend Quality

App Router路线和管理workspace已有组织，共享ContentEditor与AsyncStatePanel存在。数据状态混合SWR与本地useEffect/useState；ReviewQueue采用本地加载/变更而非SWR，不能笼统说全部共享缓存。现有Zustand用途与服务端学习事实应分开，不把本地UI设置当持久化学习状态。

当前明确缺陷F01：`panel.answer = option.key`只支持单值，multiple_choice需要集合；按钮pressed也只单值。另有P2：Practice fallback枚举可能直出英文、公共/管理双导航操作成本、Review页面说明暴露内部design字段。手机390视口截图留存，固定底部导航覆盖部分卡片区域，但未证明滚动后末尾不可达，列待设备复核的P2；不代表全站responsive/WCAG验收。QuestionEditor加载失败只有普通文本，无retry（question-editor.tsx:25–33,61），也是P2。全站hydration/keyboard/focus/乐观回滚的穷尽验证未做。

类型检查有价值但不证明业务值正确；`next.config.ts`当前未开启ignoreBuildErrors。保留ui-v2测试树排除问题见§13，未路由mock组件不能直接当线上假数据。

## 11. Backend Quality

主链router/service分层、Pydantic参数验证、请求事务存在；Review行锁+expected_next_review_at防重复推进，Draft convert有幂等检查。主要短板不是API未返回，而是不同service对同一实体/判分采用不同语义。

`attempt_service._is_correct`对list按逗号切分、区分大小写；reanswer evaluator支持空白/逗号与规范化。同一多选答案`A C`或`a,c`在practice判false、review判correct（E10）。D5原文主要约束re-answer，因此记为B类设计/语义债，不虚构PR07实现违约。essay practice裸字符串相等需要明确机器可评分资格。

Review due list每个item再查Mistake，public mistake列表逐项加载KP，存在N+1；小规模尚无性能失效证据，列P2，先建立查询预算再优化。Dashboard weak/mastered异常被降级为空会把不可用与无数据混合，需可诊断状态。未因源码写法简短就自动要求全面重构。

## 12. Database Quality

本轮新建 PG16 集群地址127.0.0.1:55439，数据库均为 `astra_week4_quality_*_20260927`。Fresh升级033和空数据局部回退/再升级成功。033存在live challenge时拒绝降级，是预期保护；没有强行删除challenge使其绿灯。026明确irreversible，不能将033→027解释为全链可回滚。

F04复核：registry只排除guest两表；026 SQL专有ledger表和draft六列无ORM对应；033四索引没有metadata对应。`alembic check`真实返回drop候选，属于schema生命周期治理缺口，不是已经执行drop，也不是当前数据损坏。下一次迁移必须先表示ownership、引入窄allowlist/一致性检查，禁止为了check过而删除迁移专有对象。

FK/unique/版本与事务提供基础完整性；多态target、复制KP、ReviewItem双ID仍依赖service不变量。没有查询真实生产孤儿行，因此生产orphan数量未知。未来审计应有只读一致性SQL，并将修复动作独立批准。

## 13. Testing Quality

现有测试不是全无价值：922后端包含真实隔离PG、HTTP/service合同与negative；5 E2E现在真正操作并读回记录。不能把过往弱E2E结论继续复制。

| 验收面 | 当前证据 | 尚缺 |
|---|---|---|
| 状态机/归属/并发 | 后端调度与reanswer测试E05 | 完整合法题型穿过真实UI |
| 错答→草稿 | E2E03读回question/attempt/pending | 草稿→确认后保留KP，再统计回流 |
| 再答→record | E2E04短答、rating4、attempt_id | multiple_choice、人工判定、错误/竞争路径浏览器 |
| 写作/错误恢复 | E2E02/05 | Blog发布撤回/移动焦点全矩阵 |
| schema | fresh与roundtrip | ORM-owned/SQL-owned漂移；旧真实数据迁移 |
| AI/OCR | mocked失败分类/治理helper | 授权真实10样本、canonical确认后target回读 |

9 skipped不得计入通过；本轮补跑三个相关测试文件并用-rs取得精确原因（E13 `skipped-tests.txt`）：3项Week2动态迁移测试只接受旧week2库名前缀，与现行guard可接受的week3/4名称不一致；6项要求LSR03专用fixture环境。补跑35 passed/9 skipped/6 subtests，未绕过guard。Week2这三项在现有统一连接guard下不能靠改库名直接放行，应单独修复测试环境合同；属于测试基础设施债。隔离legacy迁移fixture缺省等特殊环境测试不能由922替代。2 warning含AI日志测试的AsyncMock使用导致未await提示，应修测试建模，不能直接推断生产泄漏。没有启用全量代码覆盖率，计数不能当覆盖率。

`tsconfig.test.json`排除保留ui-v2树；主tsconfig排除所有*.test文件但检查其余ui-v2源；test tsconfig进一步排除ui-v2五棵树，故这部分测试类型债未被门禁覆盖。现行活跃主线绿灯不为候选ui-v2实现背书。无集成lint script、ruff/mypy门禁不足，属于原工程计划欠账/定版偏差，非本轮命令失败。

## 14. Engineering Quality

四job配置当前可由本地对应命令重现，DB安全guard未弱化。远端GitHub Actions对当前脏工作树无run证据，标NOT_VERIFIED；不能以旧HEAD CI绿证明未提交功能。Node24正式构建符合契约；单测初轮Node26偏差已由Node24的522/522补跑消除，依赖未在本轮升级。

测试数据库隔离、无secret输出、日志与复现脚本归档是优点。缺口：lint/dependency更新治理、schema漂移门禁、备份恢复演练、性能预算、结构化业务故障可观测性。Next build/OpenNext成功不证明Workers生产API域名/CORS/cookie/数据库连接规模已验收。仓库dirty是审计快照，不授权commit/push。

## 15. Architecture Drift

Original Design：冻结旧错题写，canonical事实供Dashboard/Practice，AI持久化产物可追踪。Current：主路径大体符合，存在F02/F03/F05断点；通用路线要求旧入口拆除，但重定向后旧代码仍编译，safe cleanup并未完成整棵路线退役。

三种KP表不应机械合并：Question与Mistake语义可不同，Note又是参考资料。需要明确“初始继承/人工覆写/后续变更同步”规则，而不是让复制行为偶然发生。ReviewItem target_id兼容字段也应先建不变量再评估退役，不能本轮顺手删。

## 16. Surface Completion / Fake Completion Findings

“假完成”描述证据与承诺不匹配，不推断开发者动机。

| ID | 外观 | 实际 | 裁定 |
|---|---|---|---|
| S01 | AiRun backfill helper与测试已绿 | 无生产确认caller | 子能力SURFACE_COMPLETE，PR19整体PARTIAL |
| S02 | Review再答支持options | UI只能单选，多选类型不可表达 | PARTIAL真实缺陷，非整页stub |
| S03 | KP metrics API已返回数值 | 有记录但缺KP link导致未计入 | PARTIAL端到端，聚合SQL非空实现 |
| S04 | AI question-draft confirm返回confirmed | routers/ai.py:487–497只echo无DB dependency | 仅暂态确认；若用作持久化证据则是表面完成 |
| S05 | OCR10样本/测试通过 | mock harness不测真实provider正确率 | 实测证据不足，不能称OCR质量达标 |
| S06 | NoteKP表/API存在 | 没有笔记UI消费者 | API范围完成；产品闭环未实现，不扣成PR12全未做 |

反例：Practice不是无行为按钮，它能进入题目编辑页真实作答；unrouted ui-v2 mocks不是线上fake data；当前E2E03/04不是只检查标题。以上均已裁决。

## 17. Technical Debt Register

| ID | Debt / 类型 | Source Week | Severity | Impact | Evidence | Recommended Fix |
|---|---|---|---|---|---|---|
| F01 | 多选单值输入 / Code+UX | C-W2 PR08 | P1 | 合法正确答案判错 | E09；review-queue:173–185 | 集合状态/序列化+真实多选回归 |
| F02 | 自动草稿KP丢失 / Data+Architecture | C-W2→W3 | P1 | review/weakness反馈缺失 | E10；attempt_service:58–69 | 定义继承/覆写规则，补穿链不变量 |
| F03 | legacy元数据冻结漏口 / Code | C-W3 PR09 | P1 | 源可变、冻结承诺不成立 | E11；suggestions:66–78 | 共用guard覆盖相关mutations与负测 |
| F04 | migration-only metadata缺失 / Data+Testing | 026历史→W4 | P1 | autogen可能提删除持久对象 | E06；registry/env/model | ownership映射+drift gate |
| F05 | creation target未回填 / Architecture | C-W4 PR19 | P1 | 生成记录与确认产物关联不完整 | ai_run_service:178–203 | 真实confirm/save携带run_id与原子关联 |
| D06 | OCR真实基线缺失 / Product+Testing | C-W4 PR14 | P1验收欠账 | 无法承诺可用率 | mock-baseline声明 | 独立授权真实评估或显式禁用策略 |
| D07 | 练习/复答判分差异 / Product | 历史attempt→C-W2/3 | P2 | 一题不同路径不同结果 | E10第二行 | shared grading contract+ungraded策略 |
| D08 | 调度mastered不可自动遗忘 / Product | C-W2设计 | P2 | 长期掌握可能失真 | review_item_service:29–31,71 | 先测延迟抽样再评估重入策略 |
| D09 | due/public查询N+1 / Code | C-W2/3 | P2 | 规模增长延迟 | review_item_service:29–32 | query count预算后批量加载 |
| D10 | Dashboard异常降为空 / UX+Code | C-W3 | P2 | 误以为无薄弱点/掌握记录 | dashboard_service:257–327 | unavailable状态与correlation |
| D11 | throttle并发/进程/IP容量 / Security | C-W4 PR16 | P2 | 防滥用强度有边界 | auth:184–211、login_throttle:170–199 | 并发准入实验与IP容量预算 |
| D12 | 测试按模块不按信息保留 / Testing | 全周 | P1 | F01/F02不被绿灯发现 | E05/E08对比E09/E10 | 题型×状态×关联穿链矩阵 |
| D13 | 状态文档与范围漂移 / Documentation | PR06/08与双路线 | P2 | 错判已完成/授权 | baseline-week12报告 | 单一当前状态+历史证据独立保留 |
| D14 | lint/依赖/性能门禁不足 / Engineering | Sept W1/W5 | P2 | 静态缺陷/退化无及时门禁 | package.json/ci.yml | 最小基线逐步收敛 |
| D15 | generic异常文本仍可写AiRun / Code | C-W4 | P2风险 | 潜在日志敏感信息暴露 | ai_gateway:157–165,204–220 | stable safe code+特定异常allowlist |

P0：本轮没有足够证据确认；不代表无P0或完整安全认证。F04尚未造成drop，D11/D15是边界/风险而非已证明生产入侵。未把条件风险夸大为事故。

## 18. Regression Risks

当前明确失败F01/F02/F03未取得“以前正确”的证据，因此不标REGRESSION；历史Gate PASS不能证明相应边界曾被覆盖。真正易退化面：旧新KP映射、Question答案格式变更、review rating/streak、公共DTO、auth并发challenge、migration-only权限。PR18删文件需消费者三证据，不按行数KPI扩大删除。回归应绑定工作树/构建身份，不能拿旧截图替换当前。

## 19. Cross-Week Dependency Analysis

```text
C-W1 runtime/写作基础 → C-W2 state machine/Attempt/Record
                               ↓ F01题型边界
C-W3 canonical公共读 + KP aggregation + practice + dashboard
      ↑ F02关联丢失           ↑ F03 legacy仍可变
C-W4 auth/CI/OCR/AI治理 → release gate
      ↑ F04 schema authority  ↑ F05确认后追踪
```

Week3依赖Week2提供可信输入；没有MistakeKP，SQL能运行也不能补出缺失事实。Week4 E2E可以绿色而Week2合法题型失败，因此发布Gate必须验收领域边界，而非只收五条通路。Week1已经能提供运行环境，不是当前学习语义缺口的主要来源。September债务路线与学习路线共享代码但验收不同，不能用safe cleanup替代大退役、用写作页替代SEO。

## 20. Current System Maturity

| 维度 | 当前成熟度 | 证据与限制 |
|---|---|---|
| Product completeness | 可用的个人学习工具原型/受限Beta | capture/Question/Mistake/review/dashboard存在；计划未全闭合 |
| Functional completeness | 主happy path较完整，合法分支不足 | E08通过；E09多选失败 |
| Architecture maturity | 模块化单体基础合理、owner不变量未稳 | service/ORM存在；F02/F04/F05 |
| Data integrity | 事务/FK/版本有效，跨链语义不足 | fresh033和后端通过；KP可漏 |
| Testing maturity | 单元/集成/E2E层次已建立 | 数量多而合法题型/关系保留少 |
| UX maturity | 管理型工作流能用 | 编辑器承担练习；手机/焦点全站未验 |
| Maintainability | 中等，有可审计基础和明显欠账 | 证据/guard好；双代、漂移、状态头陈旧 |
| Scalability readiness | 仅小规模个人使用假设 | 无负载/LCP基线；N+1、全量候选、in-process throttle |

不提供一个“成熟度总分”。本地小规模成功不能推导多用户隔离、多实例安全或长期数据资产可恢复。

## 21. Remaining Work

**Must Fix：** F01/F02/F03、迁移前F04、PR19真实目标关联F05；为上述跨链增加验收；明确OCR未达标时的入口策略。若要宣称发布完成，还需同源构建远端CI、目标环境/回滚与授权。

**Should Fix：** shared grading语义、zero-evidence弱点状态、Dashboard unavailable、query预算、throttle并发实验、日志safe code、文档状态、最小lint与依赖治理。

**Could Improve：** 独立practice会话、NoteKP页面体验、键盘效率、学习趋势；只在基础数据可信后做。高级图谱/模型训练不排入紧接下一轮。

## 22. Planned but Unfinished

A类，已经在明确计划内但证据不支持完成：PR08合法多选再答；PR09完整legacy冻结；PR19确认后AiRun target；PR14真实受控样本与入口验收；September W1拆除/护栏、W2统一导航与浮层、W3三编辑器共享原语、W4生产渲染统一、W5SEO/性能（逐项见附录A）。F02是原canonical学习目标没有贯通的欠账，具体修复规则需定版。

不是欠账：未经批准的PR20–26和Sept W6+候选；FSRS/Graph/Redis等明确不做项。历史生产迁移未授权是边界，不是执行者擅自应补的任务。历史June/Phase方案仅作为来源交叉映射，不重复总数。

## 23. Planned but Insufficient

B类：fixed interval/mastered足以构成原计划状态机，却不能估计遗忘；KP lifetime wrong_rate能排序，却不能把“无证据”与“强掌握”区分；NoteKP API能写关系，却没把笔记作为练习复习参考；Dashboard能显示计数，却缺可信度/不可用说明；throttling延迟能提高成本，却不是全局并发速率控制；schema upgrade能成功，却未治理autogenerate authority。

以上不能一概扣为原任务未完成。下一轮应先最小合同和验证，再决定扩展，避免换算法掩盖数据问题。

## 24. Future Work Discovery

每项建议沿 Current→Boundary→实际问题→Value→Requirement→实现方向推导。A/B/C表示与原计划关系，Category表示技术类别，两者不能混淆。C类“原计划没有”仅指本轮检索到的计划集，未声称穷尽外部未入库想法。

C1：**学习事实解释与覆盖诊断**。现有analytics数值却无输入完整性说明，F02显示“0”可能不是没学；增每KP的有效样本/缺链诊断与来源解释，先只读，不自动修数据。适合个人系统，因为能防止错误学习决策；成本M，依赖F02与指标契约，Near-term。

C2：**个人数据恢复验收场景**。当前有export/迁移/版本能力，仍未证明恢复后Question→Record→附件引用可重建；增小型恢复演练样本与业务对账。不是新备份平台；成本M，依赖schema authority/现有导出，Near-term。备份本身已有通用工程建议，新增的是“以学习闭环资产为恢复验收单位”。

C3：**mastered延迟抽样实验**。目前mastered退出due；先低频抽查已掌握题是否仍会，再决定需要何种遗忘模型。成本S/M，依赖可追溯attempt与人工反馈，Mid-term；单变量是抽样重测开关，不先引入FSRS。

C4：**题型与关系不变量注册表**。现有测试按组件/service分组，新建可执行验收索引：每个合法题型/状态转移/关系保留有代表样本。成本S/M，依赖F01–03，Next Iteration。一般E2E原已计划（B），新增是从跨链不变量组织验收的具体方法（C），不重复算功能数量。

## 25. Product Capability Gaps

独立PracticeSession可减少“去编辑器作答”的操作成本，但当前可借用QuestionEditor完成普通练习，不应为造新实体而重写。先做一个简洁答题呈现，复用现有Attempt，观察是否需要会话持久化。

搜索：已有notes搜索/filters和服务，跨Question/Mistake/Note统一检索还需当前覆盖评估；优先类型筛选、权限正确与普通全文检索，不建议向量库。导入：已有legacy adapter与ledger，应先对账/预览/幂等再扩CSV/Markdown批量题目导入；人工确认出处与字段可信度要保留。NoteKP UI让关联资料真正可找，不等于自动改写掌握度。

## 26. Learning System Evolution

| 方案 | 价值/解释性 | 数据与成本 | 当前建议 |
|---|---|---|---|
| fixed_interval_v2 | 规则清楚，已测状态机 | 现有rating即可，低 | 保留并修数据链，作为baseline |
| legacy SM-2 | 简单常见，但旧Note域 | 与canonical并行会混淆 | 不再扩展旧caller；不立刻迁算法 |
| 简化遗忘/重入 | 回答mastered是否仍掌握 | 需要延迟重测，S/M | 先C3小实验 |
| FSRS | 个体化间隔可能有价值 | 足量长期history/校准/迁移，M/L | 暂缓；数据质量稳定后对照 |
| Knowledge prerequisite DAG | 可能解释卡住原因 | 人工维护边/环验证，L | 先用Subject/KP树与引用关系 |

Mastery score若要新增，至少区分evidence count、accuracy、recency、confidence和难度来源；未经校准的单分数不应直接驱动自动停复习。当前最有价值的算法工作是可信样本资格与漏链检测。

## 27. Engineering Evolution

先把已有安全guard、CI本地重现、迁移回放变成可持续维护证据。最低投入：schema authority map、typed安全日志、一个备份恢复演练、少量性能/查询预算、依赖更新节奏与lint基线。个人规模不需要微服务/消息总线/全量可观测平台。

审计发现与发布身份需绑定hash/构建/环境；多进程throttle若实际部署需要，先决定数据库/边缘限流是否足够，再评估共享store。API versioning只在确有外部消费者或breaking change需求时引入，现阶段优先DTO契约同步。

## 28. AI Opportunities

| 具体机会 | Value | Reliability / 人工确认 | Cost / Latency | Hallucination Risk | 时机 |
|---|---|---|---|---|---|
| 错因/知识点候选 | 减少手工录入 | 只出候选，确认后写；不可覆盖可信标签 | M；一次交互秒级需测 | 中高，错误会污染选题 | F02/F05后 |
| OCR结构提取 | 图片转草稿 | 先真实10样本分层评估，保留原图 | provider成本/延迟未实测 | 漏公式/条件风险高 | PR14补验 |
| Notes→Question草稿 | 复用资料 | 原文来源与答案逐项确认 | M/L | 高，不自动发布 | Mid-term小实验 |
| 弱点解释 | 让现有指标易理解 | 只解释确定性facts，不造诊断 | S/M、缓存 | 中；可用模板先做 | 指标可信后 |
| 自动变式练习 | 扩充题库 | 必须题解/答案校验、人审 | L，高审校成本 | 高 | 暂缓 |
| 个人学习助手 | 结合目标与history选行动 | 必须可追溯、可拒绝和deterministic fallback | L/XL | 高 | Long-term |

排序、到期、权限、关联校验优先deterministic算法，不能交给LLM猜。所有AI产物先草稿；run_id/target/版本/拒绝状态必须可追踪。polish暂态返回可豁免target，不以“所有调用必须有实体”制造无意义记录。

## 29. Not Recommended Yet

| Feature | Why Not Now | Revisit Condition |
|---|---|---|
| 全量Knowledge Graph/图数据库 | 现有taxonomy和关系都未保证完整 | 有可验证先修查询需求、足够高质量边 |
| 直接替换FSRS | 数据分布/缺链/判分不稳，无法归因收益 | 跨月history可信、离线/小规模对照优于baseline |
| 向量库/Elasticsearch | 未证明现有检索规模和质量不足 | 代表查询集合显示普通全文无法满足 |
| Redis/微服务全面改造 | 运维成本大于个人规模收益 | 实际多实例/吞吐瓶颈有测量 |
| 自动生成并入库练习 | 错题事实可信度更易恶化 | 人审/答案验证和AiRun回链稳定 |
| 大一统UnifiedEditor/设计系统重写 | 当前问题是输入合同和保留信息 | 共享原语确有多处重复并有回归基线 |
| 跨设备布局、真撤销、每日AI大工作台 | 不是当前P1的解决方案 | 独立授权且撤销/幂等/冲突合同齐全 |

## 30. Future Work Matrix

优先级综合价值、必要性、依赖成熟度与成本，不伪造可比较乘积分数。Tier A基础、B核心学习、C体验、D高级、E实验。

| ID | Future Work | A/B/C | Category | Current Gap | User/Technical Value | Cost | Dependency | Priority/Tier | Horizon |
|---|---|---|---|---|---|---|---|---|---|
| FW01 | 多选+KP保留+freeze闭合 | A | Product/Data | F01–03 | 避免错误反馈、确保事实流 | M | 当前基线 | P1/A | Next Iteration |
| FW02 | schema authority与drift gate | B | Data/Testing | F04 | 防误删；可安全演进 | M | 026/033清单 | P1/A | Next Iteration |
| FW03 | canonical确认AiRun关联 | A | AI/Architecture | F05 | 可回溯内容来源 | M | 调用分类与confirm合同 | P1/A | Next Iteration |
| FW04 | OCR真实基线/入口决策 | A | AI/Product | 未测可用率 | 避免无依据产品承诺 | S/M | provider授权、样本 | P1/A | Next Iteration |
| FW05 | 判分资格与统一语义 | B | Learning Algorithm | practice/review不同 | 统计可信、主观题不过度判错 | M | FW01 | P2/B | Near-term |
| FW06 | facts覆盖/解释诊断 | C | Product/Data | 0与缺证据混合 | 用户知道建议依据 | M | FW01/05 | P2/B | Near-term |
| FW07 | NoteKP与简洁practice交互 | B | UX | API/编辑器承担日常学习 | 降低操作成本 | M | FW01 | P2/C | Near-term |
| FW08 | 查询/性能预算与最低lint | A/B | Infrastructure | 缺门禁、N+1 | 提前发现退化 | S/M | 本轮测量基线 | P2/A | Near-term |
| FW09 | 学习资产恢复验收 | C | Data/Infrastructure | 恢复后闭环未证明 | 保护长期个人资产 | M | FW02、既有导出 | P2/A | Near-term |
| FW10 | mastered延迟抽样 | C | Learning Algorithm | 无遗忘观测 | 决定是否需要新调度 | S/M | FW01/05 | P2/E | Mid-term |
| FW11 | 题型×状态×关系验收索引 | C | Testing | 绿灯漏关键分支 | 改善测试真实覆盖 | S/M | 本轮probes | P1/A | Next Iteration |
| FW12 | 受审知识点AI候选 | B | AI | 录入成本 | 减少重复操作 | M | FW03/04 | P3/D | Mid-term |
| FW13 | 自适应调度/助手 | C候选 | Learning Algorithm/AI | 长期数据不足 | 潜在学习效率收益 | L/XL | FW10有收益 | P3/E | Long-term/Optional |

每项的当前能力、适用性和实现方向见§23–28；C项不是已批准任务。FW13不是当前推荐立即实施，只保留复评条件。

## 31. Revised Development Roadmap

不沿用旧周编号，以退出条件驱动，遵循 Current→Stabilization→Core Loop→Intelligence→UX/Analytics→Advanced。

| Layer / Phase | Objective | Tasks | Dependencies | Acceptance / Verification | Exit Criteria |
|---|---|---|---|---|---|
| 1 / Stabilization | 已有系统做实 | F01/02/03；schema authority；AiRun真实分类/回填；OCR入口决策 | 本报告基线、逐项授权 | 三个probe转回归；真实UI正确多选、KP metrics读回、legacy410；alembic check无未解释删除；run→entity读回 | P1已关闭、原验收无矛盾、独立复核通过 |
| 2 / Core Loop Completion | Question→Mistake→Review→Mastery→Practice→Feedback可靠 | 判分资格、canonical关系不变量、最小practice UX、NoteKP入口、unavailable状态 | Layer1通过 | 代表题型与错/对/人工/竞争矩阵；记录和统计同源；真实用户可完成一轮 | 所有合法路径有验收，数据可解释 |
| 3a / Learning Intelligence | 从可信事实改善建议 | 样本数/时效解释、mastered抽样、负载/积压决策 | Layer2+真实history | 单变量对照；记录复习收益与用户负担，不能只看点击率 | 证明收益或明确放弃，无统计污染 |
| 3b / UX & Analytics | 降低每日使用成本 | 手机/键盘、参考资料、趋势/积压、普通检索 | Layer2，指标定义 | 每指标对应行动；可访问性/操作步骤/查询预算 | 体验改善有测量，不新增无用仪表 |
| 3c / Advanced | 有条件的AI/自适应/助手 | 仅批准的实验候选 | 3a收益证据、治理与恢复基础 | 数据质量、成本、延迟、人审、fallback对照 | 达到收益阈值才产品化，否则停止 |

每阶段完成不自动授权下一阶段；不把本报告的建议当开发、迁移、生产发布许可。

## 32. Recommended Next Iteration

**Goal：修复已经存在的学习事实和输入链，使当前功能可信，而不是增加能力数量。**

顺序：N1锁定题型/知识点继承/冻结范围与schema owner合同；N2修F01并真实多选正负测；N3修F02并验证错答→确认→rating→KP/Dashboard/Practice；N4补F03后端入口负测；N5解决F04 metadata与迁移生成防护；N6将PR19分类、确认target与PR14真实评估/禁用决策分别关闭；N7重验现有Week Gate和独立审查。

Dependencies：当前代码基线、隔离PG/浏览器可重現环境；provider实测单独明确授权。Acceptance：不能通过mock掉core service取得绿灯；保持公开只读不泄漏、legacy只读兼容、幂等与事务、六档评分值不丢失；无业务数据误写。Verification：本轮probes成为明确失败→通过证据，补完整题型矩阵后运行针对测试，再按影响范围full suite/build/browser。无新变化不机械重复已绿测试。

Exit：三个现证业务缺陷关闭，schema authority明确，AI/OCR未完成项有实际结果，远端/生产仍单列；主负责人及独立review完成后方可申请发布。预计M级工作包；不提供没有开发拆解支持的精确工日。

## 33. Final Technical Assessment

1. **原Week完成多少？** 主学习C-W1–4约75–85%，中等置信度；W1较实、W2/W3存在当前P1、W4发布未过。September路线单算，不能用相同编号混淆。
2. **已完成质量？** 已有真实DB、状态机、API和UI通路，测试与工程基础显著优于只搭外壳；跨题型/关联保留/治理完整性仍不足。
3. **表面完成有哪些？** AiRun回填helper、若将echo confirm当保存、mock OCR当真实质量等；Review不是整页stub，但多选不完整。
4. **历史欠账？** 多选再答、完整freeze、KP回流、AI确认target、OCR验收、September拆除/渲染/SEO工程任务。
5. **设计即使完成仍不足？** 固定间隔mastered不估遗忘、Boolean无ungraded、 lifetime错误率无样本置信度、API关联无产品消费者、upgrade无drift ownership。
6. **应新增什么？** 学习事实覆盖诊断、恢复后业务闭环对账、mastered抽样实验、题型/状态/关系验收索引。
7. **当前不值得做什么？** 图数据库、直接FSRS切换、向量库、微服务重构、未经人审自动出题入库、大工作台扩张。
8. **合理路线？** 先修现有缺陷和authority，再补核心闭环/解释，最后以实验决定智能化。
9. **现在停止能稳定做什么？** 在已验证本地小规模与受测路径内：登录、笔记新建编辑、短答错题草稿、短答复答/评分/复习记录、固定间隔、公共notes错误恢复；这不是生产稳定性承诺，多选与KP统计必须保留限制。
10. **存在但非生产级完成什么？** 完整题型复习、全面legacy freeze、知识状态/推荐完整性、AI provenance、真实OCR、无漂移迁移治理、远端CI/生产部署恢复及性能安全规模验证。

技术建议：把系统定位为“核心流程可运行、但仍需数据语义与跨链验收的个人学习系统”，不要继续宣称全Week完成。审计报告完成与产品Gate通过是两种不同结果。

## 附录 A：September W1–W5 当前逐任务矩阵

此附录是正式报告组成部分。源需求为 `docs/roadmap-2026-09.md`，Worker源码核查由主Agent对NOT_IMPLEMENTED/关键结论补充复核。它与C-W1–4不同，不合并百分比。证据B仅证明当前实现语义，视觉/性能验收未执行的范围明确保留。表内各任务预期与实际独立列出；风险主要为可维护性与产品未交付，W4还涉及渲染信任边界。

| Sept 路线任务 | 预期与验收 | 审计状态 | 证据 / 风险 |
|---|---|---|---|
| W1-a 死路由树拆除 | 删除 `/write*`、`/write-note*`、`/write-mistake*`、`/mistakes/review` 路由树及仅其引用模块；保留的重定向应在一个周期后清理；净减 ≥6,000 行 | `PARTIAL` | `next.config.ts:46-53` 已将旧入口重定向到 `/manage/*`，但当前 `src/app/write/`、`write-note/`、`write-mistake/`、`mistakes/review/` 仍有页面/组件，同名源树尚未删除。尚未以 HEAD 做净行数比较。 |
| W1-b 管理入口收敛 | `manage/page.tsx` 收敛进 `(workspace)`，拆 5 个内联 tab | `PARTIAL` | `/manage/(workspace)/layout.tsx:10-21` 有 AuthGate 与新工作区；旧 `src/app/manage/page.tsx:34-46` 仍保留 9 个 tab，并在同文件定义大型 `ContentTab`。两代入口并存。 |
| W1-c CRUD 抽象 | `projects/share/pictures/bloggers/snippets` 五列表共用 `useContentCollection` hook 与管理弹窗 | `NOT_IMPLEMENTED` | 当前五目录各自保留 `page.tsx`、服务/列表及 create/upload dialog；`src/app`、`src/hooks`、`src/lib` 未找到 `useContentCollection`。 |
| W1-d CI/静态护栏 | CI 前端 job 跑 `npm test` 与 `test:typecheck`；加 ruff、eslint、dependabot | `PARTIAL` | `.github/workflows/ci.yml:28-38` 已运行 shipped/test typecheck、unit tests、build；目前 `.github` 只有 CI workflow/模板，没有 dependabot 配置；`package.json` 没 lint 脚本，CI 注释说明无 ruff/mypy。 |
| W1 acceptance | `src` 净减 ≥6,000 行、全测试绿、UI 无可见变化、CI 含前端测试 | `PARTIAL` | CI 前端门禁存在，但路由树/旧管理页仍在；本 worker 未量化净行数，也未做前后 UI 差异验收。 |
| W2-a editorial tokens | 设计变量集落在 Tailwind 4 的 `theme.css` | `PARTIAL` | `src/styles/theme.css:1-15` 仅定义少量旧色彩/字体变量。较丰富的变量在 `src/components/ui-v2/tokens.css:1-54` 的 `--uiv2-*` namespace 并保持 additive-only；尚未与旧 `theme.css` 收敛成单一 editorial token 层。 |
| W2-b 统一导航 | sticky 浮动顶栏替代桌面 VerticalNav/sidebar 与移动底部 MobileNav | `NOT_IMPLEMENTED` | 当前 `manage/(workspace)/layout.tsx:11-16` 组合桌面 `ManageSidebar`、移动 `ManageMobileNav`、普通 `ManageTopbar`；`ManageSidebar` 是左侧常驻分组导航，无 sticky 顶栏替代。 |
| W2-c Modal/Drawer/Popover 可访问性合同 | 键盘可操作、焦点管理、背景隔离 | `PARTIAL` | 管理移动抽屉有 Escape、focus trap、inert、开闭焦点处理（`manage-mobile-nav.tsx:36-115`）；通用 `DialogModal` 只有 scroll lock/Escape，`Drawer` 只有 scroll lock/Escape（`dialog-modal.tsx:22-46`、`drawer.tsx:23-35`），未形成所有浮层通用焦点合同。 |
| W2-d 视觉回归验收 | 全站导航和浮层有基线截图对照、无可见回归 | `IMPLEMENTED_UNVERIFIED` | 当前 legacy、workspace、UI V2 多套视觉/组件同时存在；本 worker 未找到证明该 Sept 路线全站基线对照通过的记录。 |
| W3-a 三编辑器共享原语 | capture、notes、mistakes 使用同一共享原语库，明确不做 UnifiedEditor | `PARTIAL` | 笔记/博客在 `manage/(workspace)/notes/components/content-editor.tsx:10-32` 复用 `useNoteEditor`；采集独立在 `capture/components/capture-workspace.tsx`；canonical 错题详情编辑独立在 `mistakes/components/mistake-detail.tsx` 并用 `ManageFormPanel`，旧错题表单也仍单独存在。未见三者接入的通用 editor primitive 库。 |
| W3-b AuthGate 清单 | editor route ownership 与授权覆盖表通过 | `IMPLEMENTED_UNVERIFIED` | workspace layout 包 AuthGate；旧 write/edit 页面也有局部 AuthGate。但本路线要求的全三编辑器 route coverage checklist 当前未见，本 worker 未实测未登录行为。 |
| W4-a Sanitization 白名单 | 按路线要求补 `rehype-sanitize` | `NOT_IMPLEMENTED` | `package.json` 无 `rehype-sanitize`，源码未有 `rehypeSanitize`。现生产 `markdown-renderer.ts:109-127` 有 raw HTML drop 与 link/image protocol allowlist，这是部分自定义防护，不能等同该 sanitizer 交付。 |
| W4-b 加固 M7 生产切换 | `use-markdown-render` 改用 M7 hardened renderer | `NOT_IMPLEMENTED` | 生产 `src/hooks/use-markdown-render.tsx:45-47` 仍调用 `@/lib/markdown-renderer`。`src/lib/markdown-poc/render-poc.ts:1-7` 明写 PoC 且生产不得 import；本 worker 搜到的调用都在 PoC 测试/fixture，未见产品 import。 |
| W4-c PoC 收尾 | 删除或归档 `src/lib/markdown-poc/` | `NOT_IMPLEMENTED` | PoC 源码、浏览器 harness 与多组测试仍在 `src/lib/markdown-poc/`。 |
| W4-d 生产路径安全与渲染验收 | sanitizer、Mermaid/Markmap/Math/Chart 的截图/安全测试在产品路径通过 | `PARTIAL` | PoC 下有测试（如 `markdown-poc/__tests__/dom-safety.test.ts`），但这些测试调用隔离 `renderMarkdownPoC`；未找到生产 `markdown-renderer` 的同范围安全测试文件，也未证明新 renderer 已进入产品路径。 |
| W5-a SEO 元数据 | blog/notes 页面真实 `generateMetadata` / OG | `NOT_IMPLEMENTED`（源码搜索范围内） | 当前源码未找到页面 metadata/OG 定义；路线要求分享链接真实标题/OG。 |
| W5-b GA 配置 | Analytics ID 移入环境变量 | `NOT_IMPLEMENTED` | [head.tsx](src/layout/head.tsx#L18) 仍硬编码 `G-ZNSFR7C9PM`。 |
| W5-c Lighthouse 性能门禁 | CI Lighthouse，LCP < 2.5 秒并处理 RISK-PRA-001/002 | `NOT_IMPLEMENTED` | 当前 CI workflow 未见 Lighthouse 门禁；本 worker 未自行采集 LCP。 |
| W5-d LikeButton 定时器 | 清理组件卸载时 timer | `PARTIAL` | [like-button.tsx](src/components/like-button.tsx#L25) 的 `justLiked` timer 有 cleanup，但首次显示和粒子 timer 未清理。 |
| W5-e 图标按钮可访问性 | icon-button `aria-label` 专项清查 | `PARTIAL` | `LikeButton` 有 `aria-label='Like this post'`；仅这一处 source observation 不能代表全站专项清查，未见完整检查产物。 |


### 各周原目标、质量画像与准入

| September Week | 原目标/实际深度 | 完成区间/Confidence | 未完成/隐性问题/最大风险 | 后续前置 |
|---|---|---|---|---|
| S-W1 | 拆旧路由/管理页、CRUD共用与工程护栏；只完成redirect及部分CI | 25–45% / Medium | 34个旧路由树文件仍存在，redirect不等于拆除；没有完成净减6000行与视觉无变化验收 | 不能标整周完成；不阻止独立获批学习主线已存在事实 |
| S-W2 | token、全站单导航、浮层合同；局部有token/移动drawer | 15–35% / Medium | additive候选token不是全站替代；通用浮层一致性未完成 | 未达W3所期望视觉/交互基础 |
| S-W3 | 三编辑器共享原语；notes/blog有共用，capture/mistake仍各自维护 | 20–40% / Medium | 共享ContentEditor不等于三域共享；需要逐域证据而非新大一统 | 未达到本路线收敛验收 |
| S-W4 | 加固渲染器进入生产并退役PoC；仍旧生产实现 | 5–20% / Medium-High（未切换） | 有自定义raw HTML/protocol防护，但未履行指定统一管线；PoC测试不能覆盖生产 | 生产路径安全与复杂内容回归是准入条件 |
| S-W5 | SEO/性能/a11y；只有若干局部timer/label | 5–20% / Medium | 无generateMetadata、GA硬编码、无LHCI；不能假称LCP达标 | 尚不支持本路线可见性验收 |

| 质量维度 | S-W1 | S-W2 | S-W3 | S-W4 | S-W5 |
|---|---|---|---|---|---|
| Architecture | 两套入口/重定向并存 | 两套token/导航未收敛 | 三编辑器owner未共用 | PoC与生产分离 | SSR metadata未接 |
| Frontend | 旧树仍编译 | 部分drawer焦点成立 | notes共享；其他独立 | hook仍import旧renderer | 局部timer/labels |
| Backend | 此周无新API要求 | 无新后端要求 | 必须保留既有API | 不应靠后台绕过前端安全 | 无主要后端变更 |
| Database | 无schema目标 | 无schema目标 | 不应改变内容owner | 无schema目标 | 无schema目标 |
| API | redirect非接口迁移 | 无新数据合同 | API抽象可复用但未统一 | 输出HTML到React消费者需验证 | metadata要从真实公开数据读 |
| UX | 老新管理入口混合 | 导航/浮层规则不一致 | 编辑/练习操作角色混合 | 特殊内容外观未新验 | 分享预览不满足任务 |
| Testing | CI前端已接，减行验收未过 | 全站视觉基线未验证 | 未有三域整体验收 | PoC测试与生产隔离 | 无Lighthouse门禁 |
| Maintainability | 重复CRUD和dead-route负担 | 候选库不应被误认为主线 | 应最小共享原语 | 需唯一可信渲染路径 | 功能分散、无性能预算 |

### 主Agent对未实现项的反向核验

当前搜索 `src`/`package.json`/`.github` 无 `useContentCollection`、`rehype-sanitize`/`rehypeSanitize`、`generateMetadata`、Lighthouse/LHCI或dependabot配置；结合调用方检查而非只凭词未命中：`use-markdown-render.tsx:45–47`明确导入旧renderer；`head.tsx:18–25`直接使用GA常量；CI完整四jobs没有性能job；五个CRUD页面各自实现dialog/list；manage workspace与旧page、Sidebar/MobileNav仍被路由导入。未实现结论针对这些具体计划产物，不能推导全站没有任何安全防护/metadata/复用。

额外渲染探针 `evidence/markdown-probe.txt` 显示旧renderer的heading/link text可保留嵌入HTML；但产品hook对img替换为MarkdownImage，React处理又有差异，**未证实产品XSS执行**。这是补全生产路径sanitization测试的理由，不新增P0漏洞结论。

## 附录 B：反向复核与冲突裁决记录

| 争议/高影响项 | 主Agent检查 | 裁决 |
|---|---|---|
| F01多选 | 完整组件状态+Chromium点击A/C+HTTP响应 | P1成立；只证明review UI，不混称practice页面已同样复现 |
| F02知识点 | service/schema/convert/analytics与真实PG事务probe | P1成立；用户手动补KP可避开，不消除默认路径问题 |
| F03冻结 | scope写产生或变更；真实ASGI handler/PG move folder | P1成立；auth mock不用于证明认证缺陷 |
| F04 drift | registry/env/026/033与alembic check真实输出 | P1迁移演进风险；未发生drop |
| F05 helper | 全backend生产caller检索+确认端点/现有Capture分类 | helper-only成立；不宣称所有AI产物都丢关联 |
| throttle P1 vs P2 | auth读计数→await DB→记失败，无inflight限制；IP只有TTL | 本报告P2：原合同是延迟失败，不承诺严格并发限额；无生产暴露拓扑/可达攻击规模证据。上线前需容量/并发测试，若单实例暴露可低成本突破既定防暴力破解预算则升P1，不能称竞态已修复 |
| practice/review规范化P1 vs P2 | E10字符串差异+原D5仅明确re-answer范围 | 保留D07 P2合同债：没有证明practice承诺接受空格/大小写等价；若领域定版要求跨入口同语义，应纳入阻断验收；不能称review probe已证明practice多选UI同一缺陷 |
| 输入数字冒泡 | 完整JSX父子树 | 撤销误报，评分组与再答是兄弟 |
| Practice无执行链 | QuestionEditor submitAttempt+E2E03 | 撤销SURFACE_COMPLETE；仅独立session UX缺失 |
| Attempt NULL被计正确 | ORM/migration NOT NULL+D7公式 | 撤销NULL缺陷；保留ungraded资格与判分差异设计债 |
| archived mistake误排practice | archive正常流程将item paused | 没有正常路径可达证据，降防御性建议 |
| PR12 duplicate必须拒绝 | 早任务表与后幂等合同/服务 | 不据早期简表判运行缺陷；文档应同步 |
| 昨日CI/passkey/E2E缺陷 | 当前修复源码+E05/E08 | 旧结论已过时，保留为历史，不计当前缺陷 |

全部NOT_IMPLEMENTED主要来自September明确产物缺失，已按附录A核查；NoteKP消费端无caller也检查了notes编辑目录与client调用。全部SURFACE_COMPLETE仅限S01及若被当持久化承诺的S04；没有将合法只读选择器和保留mock目录误判为假完成。无已证实P0。
