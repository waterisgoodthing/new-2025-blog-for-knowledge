# LSR 串行任务清单

进度只使用 `[x]`/`[ ]` checkbox。完整依赖链为 `LSR-00→01→02→03→04→05→06→10→11→12→13→14→15→16→20→21→22→23→30→31→32→33→34`；每次只执行依赖满足后的第一项。每项完成后必须立刻更新本文件和 [validation.md](./validation.md)。

## 任务合同字段

每项均固定包含 `depends_on`、Primary Owner、Reviewer、Verifier、触发 Gates、输入、允许写入、禁止边界、验收、暂停条件。实施/复核/验证 Worker 必须是独立真实 Persona Worker，使用 `luna/high`；本次只建立合同，没有执行后续业务任务。

## 阶段一：迁移并移除旧体系结构

### LSR-00 — 建立权威工作流骨架

- [x] LSR-00（本次实际完成；不代表任何业务 Gate PASS）。
- depends_on：无。
- Primary Owner：Principal Software Architect；Reviewer：Principal Technical Reviewer；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr00-owner`/Principal Software Architect；reviewer=`lsr00-reviewer`/Principal Technical Reviewer；verifier=`lsr00-verifier`/Senior QA / SDET；G0=`lsr00-g0-product`/Product Architect + `lsr00-g0-domain`/Senior Domain Analyst；G1=`lsr00-g1-architect`/Principal Software Architect + `lsr00-g1-reviewer`/Principal Technical Reviewer。所有 identity 独立，排除 `lsr00-owner`。
- 触发 Gates：G0、G1（仅核对合同是否已定义；不得自批高风险设计）。
- 输入：AGENTS.md、agents 治理文件、用户粘贴目标、历史工作流输入。
- 允许写入：仅 `docs/workflows/legacy-system-retirement/{README,design,requirements,tasks,validation}.md`。
- 禁止边界：产品代码/测试/迁移/数据库/运行时/凭据/服务/浏览器/部署/Git；不创建 audit/assets 或其它文件。
- 验收：五文件存在；状态和阶段顺序冻结；G0-G5、manifest、角色分离、admin_session、Note/Blog/公开保留、隔离 DB/Chromium/生产禁止边界齐全；LSR-01 为唯一下一项。
- 暂停条件：目标目录预先存在、路径重叠或 dirty worktree 无法保留；本次已核验目录不存在并保留 dirty worktree。
- 历史快照（已被最终当前结论取代）：`lsr00-reviewer`=`PASS_WITH_NOTES`；`lsr00-verifier`=`PASS`。当时仅覆盖五文件合同与仓库边界，G0/G1=`NOT_VERIFIED`。

### LSR-01 — 当前旧/新对象与消费者映射（唯一下一项）

- [x] LSR-01（当前结论 `PASS`，仅静态 mapping 验收范围；Reviewer=`PASS_WITH_NOTES`、QA=`PASS`、Data=`PASS`；G0=`PASS`；G1 Architect=`PASS`、Technical Reviewer=`PASS_WITH_NOTES`、combined G1=`PASS`；G2-G4=`NOT_VERIFIED`、G5=`NOT_AUTHORIZED`；LSR-02 静态合同已独立收束为 `PASS/[x]`）。
- depends_on：LSR-00。
- Primary Owner：Principal Software Architect；Reviewer：Principal Technical Reviewer；Verifier：Senior QA / SDET + Senior Data Engineer（两个真实独立 Worker，只读复核）。
- role matrix：owner=`lsr01-owner`/Principal Software Architect；reviewer=`lsr01-reviewer`/Principal Technical Reviewer；verifier=`lsr01-verifier-qa`/Senior QA / SDET + `lsr01-verifier-data`/Senior Data Engineer；G0=`lsr01-g0-product`/Product Architect + `lsr01-g0-domain`/Senior Domain Analyst；G1=`lsr01-g1-architect`/Principal Software Architect + `lsr01-g1-reviewer`/Principal Technical Reviewer。所有 identity 独立，排除 `lsr01-owner`。
- 触发 Gates：G0、G1（仅在只读盘点交付后独立对账，均不是 LSR-01 的前置）；Gate 结论不因本任务文档更新自动改变。
- 输入：当前源码、Alembic revisions、路由注册、API client/hook/page、服务、测试、静态数据/导出；历史工作流只作线索。
- 允许写入：仅本五文件的 manifest/checkbox；只读命令产物只能放任务专属仓库外临时目录并登记路径/hash/首次必要失败/清理结果。
- 禁止边界：不得查询日常/生产 DB 内容、连接真实凭据、启动服务、改产品/测试/迁移/路由；不得把历史清单当当前事实。
- 验收：列出旧/新对象字段、表列、revision、API、service、client、hook、page、导航、测试、静态/导出消费者；逐项标记迁移/保留/替换/删除/未知；记录调用图和隐藏消费者；未知项进入阻塞清单。纳入 2026-08-23 当前用户合同：旧公开 Note 只读保留及 URL、`/mistakes` 聚合关闭、新对象私有/provenance 关联；ReviewItem 当前状态迁移与旧字段 provenance/paused 规则；Capture 双草稿与严格人工确认顺序。上述只冻结验收/映射输入，不代表实现或 Gate PASS。
- 历史快照（已被最终 G1 结论取代）：G1 第二轮冻结输入包括 consumer owner、308/410 route matrix、A/B/C 无双写 review cutover、3×20 观察阈值、强 FK ledger DDL/state machine、QuestionKnowledgePoint/Attempt canonical owner、approval provenance 与 recovery runbook；当时仅评设计可否进入 LSR-02，实现与 G2/runtime 证据后续 `NOT_VERIFIED`。
- 暂停条件：owner、公开/私有语义、字段边界、当前 revision 或消费者无法由当前证据确定；需 DB 内容时暂停等待本任务依赖满足和隔离环境准备。

### LSR-02 — 数据迁移合同与可逆规则

- [x] LSR-02（当前 `PASS`：仅静态数据迁移合同；Senior Data Engineer Owner 完成修订，独立 Reviewer=`PASS_WITH_NOTES`、Verifier=`PASS`；G2 独立对账已 `FAIL`；后续 LSR-03 runtime 为 `PASS/[x]`，但不等于 G2 通过）。
- depends_on：LSR-01、G0 `PASS`、G1 `PASS`。
- Primary Owner：Senior Data Engineer；Reviewer：Principal Software Architect；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr02-owner`/Senior Data Engineer；reviewer=`lsr02-reviewer`/Principal Software Architect；verifier=`lsr02-verifier`/Senior QA / SDET；G0=`lsr02-g0-product`/Product Architect + `lsr02-g0-domain`/Senior Domain Analyst；G1=`lsr02-g1-architect`/Principal Software Architect + `lsr02-g1-reviewer`/Principal Technical Reviewer；G4=`lsr02-g4-recommendation`/Senior Recommendation Engineer + `lsr02-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr02-owner`。
- 触发 Gates：本任务不重新裁决已通过的 G0/G1；字段语义/AI 来源/复习规则若发生变更，必须由独立 Gate Worker 重开适用 Gate；G2 仅由 LSR-03 隔离证据触发并独立对账。
- 输入：LSR-01 final manifest、当前 model/schema/Alembic source、G0/G1 已冻结合同、用户三项决定；本任务不读取获批快照/用户数据。
- 允许写入：仅本五文件，主要为 `design.md`、`requirements.md`、`tasks.md`、`validation.md` 的 LSR-02 合同/manifest；不创建合同测试、迁移实现、脚本、DB 或额外 artifact。
- 禁止边界：不连接任何 DB、不读用户数据、不启动服务/browser；不改产品/schema/Alembic/test；不写五文件之外路径；不猜测 slug/UUID、科目、KP、答案、错因、难度、EF、interval、repetitions、复习时间、版本、来源或 owner；不静默丢弃字段、不让 AI 补事实。
- 验收：矩阵逐字段覆盖 Question/QuestionDraft/QuestionSource/QuestionKnowledgePoint/Mistake/MistakeDraft/ReviewItem/ledger/Subject/KP；包含 DraftItem source/status/version/approval/target IDs 与 draft subject/title/type/options/difficulty/question/answer/explanation/reason/snapshot/source-switch 字段的 source/target/type/normalization/default/provenance/disposition/lossiness/validation/rollback；冻结 active/paused 完整 target queue、mapped schedule/evaluation_time_utc、typed enum/check/index/FK/on-delete/immutable transition table/SECURITY DEFINER adapter+transition/composite target bundle（QKP/projection `INTEGER[]`）/idempotency/hash/mapping/approval/audit/migration_notes/events；明确 canonical_payload 完整重算、search_vector NULL sentinel、QKP canonical与Mistake ID-set projection、专用 `legacy_note_migration_adapter` exact interface/error enum/essay refusal、EF bit-exact、strict malformed-ID handling、Draft→final cross-entity mirrors、source concurrency、先 atomic-clear 再 FK deletion 的 logical-vs-snapshot rollback、unexpected Capture/Attempt failover、chapters/019 三类 fixture、source_ref 冲突选择、Attempt/Capture provenance、当前 route/mutation matrix、唯一 scoped SQL/TEMP snapshot/helper definitions/replay 与 LSR-03 fixtures/restore 输入；Owner 只运行限定 `rg`/links/diff-check/status 自检。
- 第五轮闭环附加验收：canonical payload required-key/type、逐行 archive/live-Note binding 与 wrong-note rejection（顶层 `legacy_ef_bits`）；invoker helper 最小 ACL/permission re-raise；MistakeDraft/Mistake 全 mirror 与反向 target-kind NULL；source/question/mistake/schedule/rollback 审批身份分离；active `ReviewItem.state/algorithm`；manifest 0/1/2 fail-closed；retained source/hash parity。仍只改五文件，Owner 不得自批。
- 第六轮闭环附加验收：owner-only pending/approval execution path and approval event IDs；源码精确 options normalization、stem/analysis mirror；knowledge_points/tags 归一化；archive/ledger 双向完整字段与 raw JSON；source_title helper；scoped rollback Capture/Attempt guard；微秒 UTC；finite EF；pgcrypto PUBLIC/app ACL。仍只改五文件，Owner 不得自批。
- 第七轮闭环附加验收：approval owner functions 写入独立 approval event IDs，transition 只验证对应 actor/event；按源码冻结 Question option-object、answer_data、stem/analysis 与 Mistake question/reason/snapshot mirror；archive↔snapshot↔live Note 双向 row/hash/raw JSON 绑定；source_url/title 与 mapping scope fail-closed；Capture/Attempt rollback SQL；EF finite/bits；pgcrypto ACL。仍只改五文件，Owner 不得自批。
- 第八轮闭环附加验收：两个 owner approval 函数必须是真实可执行 body 与精确 ACL/signature；options 空数组/非法 object/true_false answer_data 规则；failed→pending 全量清空并新 source approval；all-dispositions/final/retained scope 分离与 manifest 恰一行 fail-closed；rollback JSON canonical digest、rollback hash 与原子 Capture/Attempt guard；唯一 required-key 集绑定 source_note_id/source_url/legacy_review_json/legacy_ef_bits；verifier 仅 digest 权限。仍只改五文件，Owner 不得自批。
- 第十轮闭环附加验收：threat/role 模型与 NOLOGIN owner；structured exact-key marker、OLD/NEW/TG_* 全绑定、session/current_user 双重校验、一次性 nonce；create/approval/transition/rollback loader 紧邻 marker；ledger/events/audit TRUNCATE 无条件拒绝；合法路径与 forged/wrong/replay/second-use/truncate 负向 fixtures。仍只改五文件，Owner 不得自批。
- 第十二次闭环附加验收：pending typed source/schedule fields and manual/schedule state shape；active TRUE→FALSE schedule transition；QKP/projection canonical INTEGER[] exact sets；approval events cross-ledger/source/mapping/hash binding；owner-only consumed-nonce cleanup with exact ACL；owner minimum SELECT grants；manifest/archive/disposition/source empty-scope fail-closed checks；typed INSERT/UPDATE column/value and guard/transition parity fixtures。仍只改五文件，Owner 不得自批。
- 第十三次闭环附加验收：canonical typed/nullability/format/range validation before every cast；TEXT hash boundaries with exact lowercase-hex length checks；fixed transition reason/required-parameter errors；maintenance-runner-only nonce cleanup；archive/snapshot/disposition/source count equality plus bidirectional source set equality；failed/rolled_back counted as all-dispositions but never final-success。仍只改五文件，Owner 不得自批。
- 第十四次闭环附加验收：pending/approval 前 `char_length` 校验 canonical/live/parameter title，超 300 立即固定 `SOURCE_TITLE_TOO_LONG` 并进入独立 manual/failed rejection 记录；ready 防御复检；`lsr02_source_snapshot`、`lsr02_archive_rows`、`lsr02_archive_manifest`、disposition、live source 五方分别计数/hash/set 绑定；replay 必须非空、等数、FULL OUTER 检缺失/多余并逐行 IDs/hash 相等；Note 非空/可空/type 唯一矩阵贯穿 owner/live/snapshot/archive/replay，数组空值语义固定。仍只改五文件，Owner 不得自批。
- 第十六次闭环附加验收：rejection writer 必须复用锁定 live Note 的 canonicalize helper 并重算 hash，reason CHECK 仅 `SOURCE_TITLE_TOO_LONG`；独立 rolled_back replay manifest 对 rollback actor/event/reference/hash、transition event、audit digest 做 count/双向集合/FULL OUTER 逐列比较；last_reviewed 统一 UTC 微秒字符串，title 原样保留；16-key nonce marker 仅 ledger/events/rollback-audit，rejection 由独立 owner/session/ACL/append-only guard 保护。仍只改五文件，Owner 不得自批。
- 暂停条件：无损映射、owner、唯一性、版本/可见性或回滚方案未知；需不可逆 schema action 或生产数据。

### LSR-03 — 隔离 PostgreSQL 迁移演练

- [ ] LSR-03（当前状态 `PARTIAL`：fresh isolated runtime 独立 Verifier=`PASS`，但独立 G2 Gate=`BLOCKED`；完整 target parity、真实 `retained_public_only`、visibility/orphan/ReviewRecord、rollback replay/audit digest 与带合成数据 restore 尚未闭合。当前证据 `/Users/limengyang/.codex/attachments/lsr03-g2-fresh-final-evidence-20260825-bootstrap-fixture-admin-cwd/`；LSR-04 未启动且禁止启动）。
- depends_on：LSR-02。
- Primary Owner：Senior Data Engineer；Reviewer：Senior DevOps / SRE；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr03-owner`/Senior Data Engineer；reviewer=`lsr03-reviewer`/Senior DevOps / SRE；verifier=`lsr03-verifier`/Senior QA / SDET；G2=`lsr03-g2-db`/Database Architect + `lsr03-g2-data`/Senior Data Engineer；适用 G4=`lsr03-g4-recommendation`/Senior Recommendation Engineer + `lsr03-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr03-owner`。
- 触发 Gates：G2；AI/来源链变更同时需 G4；真实部署永远另需 G5。
- 输入：LSR-02 合同、空库、获批合成数据/本地快照、完整 Alembic graph、可验证备份。
- 允许写入：任务专属一次性隔离 PostgreSQL、隔离附件根和精确列出的非生产迁移/验证脚本；仓库只允许本任务精确授权的脚本/测试与 `validation.md` manifest，其余产物在仓库外临时目录。
- 禁止边界：禁止日常/生产 DB、生产凭据、真实用户正文、默认 `DATABASE_URL`、真实外部存储；禁止以测试库结果授权源库切换。
- 验收：空库 replay；迁移前后计数/hash/关系/孤儿/重复/可见性/版本；幂等重跑；向前迁移和回滚/恢复；连接身份明确；生成 G2 所需证据后由 Database Architect 与 Senior Data Engineer 两个独立 Gate Worker 对账；失败即销毁隔离资源并保留首个原始失败证据。
- 暂停条件：目标身份不唯一、出现 drift/orphan/duplicate/UNKNOWN、回滚失败、隔离资源无法清理、误触日常库。
- 当前 fresh runtime 收束（2026-08-25）：同一 fail-fast driver 完成 58 项 no-DB、`001→026`、026 二次幂等、active/paused/retained/019 与幂等、5 项 DB negative、logical rollback、CaptureItem/Attempt/MistakeDraft.`attempt_id` zero-mutation、pre-026 restore 和 cleanup；Verifier=`PASS`、SHA256SUMS 42 项通过。Gate 对账确认这些仍不足以满足本任务“生成完整 G2 证据”的验收，因此保持 `[ ]`/`PARTIAL`，下一最小任务仍是补齐上述针对性断言与 fixture。
- Owner-side 修复记录（已被最终独立 `FAIL` 结论取代）：按首轮 findings 重建后，隔离 `127.0.0.1:55432/lsr03_replay` 完成空库 replay `001→026`，并形成 paused 正向/幂等、UUIDv5、QKP/projection、marker negative、logical rollback 与 custom dump 日志。证据位于 `/tmp/lsr03-tdd-red.PYec4J/`，与首个失败日志分离；这些局部证据不覆盖随后发生的默认 5432 边界事故，也不构成 G2。

- 边界事故与终止记录：独立 Verifier 误用 `LSR03_DATABASE_URL` 启动 Alembic，而项目实际读取 `DATABASE_URL`，因此连接了默认 `localhost:5432` 并尝试 `025→026`；操作因缺少 `CREATEROLE` 失败，Verifier 报告事务未提交。该连接本身已经违反明确禁止边界，故 LSR-03 立即转为 `FAIL` 并停止；不得以“无提交”降级事故。主代理未再次连接 5432，仅停止了 `/tmp/lsr03-tdd-red.PYec4J/data` 的 55432 隔离进程并保留证据。恢复本任务前必须先建立强制 fail-closed 的显式 URL/host/port/db identity guard，并获得用户方向。

- 事故只读核查与恢复授权（2026-08-25）：用户授权一次只读核查。独立审计仅连接 `127.0.0.1:5432/blog_v2`，强制 read-only，确认 Alembic 仍为 `025`，未发现 026、`legacy_migration` schema、合同表/函数/触发器/角色或相关活动会话；随后回滚并断开。证据 `/tmp/lsr03-incident-audit.i6qoKD`，原始输出 SHA-256=`7b55e7e65b2f853ec222638248345f7aee394e672985d150ad14c32c9b1b23fc`。该结果仅表示当前 catalog 未发现持久变化，不证明历史绝对无变化。用户授权在强制 host/port/database fail-closed 守卫后重启隔离 LSR-03；不得再次连接 5432。

- 本轮修复与验证子步骤（`lsr03-owner`）：026 增加 immutable `canonical_payload`、transition/rollback binding、16-key marker registry/one-use guard、rollback inbound check、pgcrypto ACL 与最小 owner/adapter grants；adapter 改为显式映射、UUIDv5、独立 question/mistake actors、SERIALIZABLE、QKP/projection exact IDs；validation helper 载入五方 TEMP manifest。该记录不等同独立 Gate 通过。

- 最终独立结论（2026-08-25）：稳定证据位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r2`，其 `SHA256SUMS` 绑定当前实现、archive、manifest、日志与 cleanup。独立 Reviewer=`FAIL`、Verifier=`PARTIAL`：TEMP 入向 predicate 已通过，但真实表 rollback 调用第一次因 adapter-runner 直接 ledger SELECT 权限失败，第二次因夹具错误绑定 `target_question_draft_item_id` 而非 `target_mistake_draft_item_id` 失败；修正后依“两次同类失败即停”规则未第三次运行。因此 LSR-03 不勾选，不能触发 G2 对账或进入 LSR-04。后续如获准重开，必须使用全新隔离数据库和已复核的实际表夹具，不得续跑本次失败环境。

- 重开前静态预检（2026-08-25，Primary Owner=`lsr03-reopen-owner`/Senior Data Engineer）：`PASS`（仅无数据库范围；`lsr03_reviewer`=`REVIEW: PASS`、`lsr03_verifier`=`VERIFY: PASS`）。已复核 026、adapter、guard runner、相关模型/迁移和 r2 `actual-inbound-fixture-status.md`/`SHA256SUMS`；未连接数据库、未启动服务、未执行 Alembic。仅修改 `backend/tests/lsr03_rollback_rehearsal.py` 与 `backend/tests/test_lsr03_rollback_static_contract.py`：setup/cleanup 继续由 admin session 执行，rollback 只由 adapter-runner 调用，不在该会话直接 SELECT ledger；所有实际入向 setup 绑定 `target_mistake_draft_item_id`；失败后验证全列 ledger/inbound/attachment/audit-event zero mutation、`SNAPSHOT_RESTORE_REQUIRED`、identity 与 cleanup zero，入口拒绝非隔离/不一致/non-recovery identity。`READY_FOR_FRESH_REHEARSAL=YES`，仅放行全新 runtime recheck；总体 LSR-03/G2 状态不变。
- r3 runtime recheck（2026-08-25）：`FAIL`。全新 `lsr03_r3` 集群仅在 `127.0.0.1:55432` 启动；首个 guarded runner 步骤在导入 `sqlalchemy` 时失败，未进入 URL/identity、Alembic、SQL 或三条 actual-table inbound rollback。按首错规则立即停止、不修复、不重跑；证据与 SHA manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r3/`，r2 未覆盖/未修改。LSR-03 仍 `FAIL/[ ]`，G2 仍 `NOT_VERIFIED`。
- r3 首错后的无数据库 runtime-contract 修订（2026-08-25）：r3 首错及其 evidence 保留为历史，r4 未启动。`backend/tests/lsr03_guarded_runner.py` 延迟 SQLAlchemy 导入，并在 probe/DB 动作前要求 `backend/.venv`，错误解释器固定 `LSR03_PYTHON_RUNTIME_REQUIRED`/exit 64；child 固定 `backend/.venv/bin/python -m pytest`、`PYTHONPATH=.`、cwd=`backend`。新增错误解释器 fail-before-probe/child 与正确私有 venv identity 测试；无产品/模型/迁移/adapter 改动。`backend/.venv` targeted guarded/static tests=`20 passed`，`py_compile`/`diff-check`=`PASS`；`READY_FOR_R4=YES` 仅放行未来 fresh isolated runtime，不裁决 LSR-03/G2。
- R4 fresh isolated runtime recheck（2026-08-25）：`FAIL`。新 `lsr03_r4` 集群仅绑定 `127.0.0.1:55432`；guarded identity、001→026 和 paused baseline 成功。首个 actual-table fixture 在 `_audit_event_snapshot` 对 `legacy_migration_rollback_audits ORDER BY id` 失败（无 `id` 列）；按首错规则停止，不修复、不重跑，三条 inbound setup/rollback、zero-mutation、attachment 与 fixture cleanup 未执行。新证据与 SHA256 manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r4/`；集群已停止且 55432 无监听；fixture cleanup=`NOT_RUN`。LSR-03 仍 `FAIL/[ ]`，G2 仍 `NOT_VERIFIED`。

- R4 首错后的无数据库定向修订（2026-08-25）：已根据 026 DDL 将 `legacy_migration_rollback_audits` audit snapshot 从 `ORDER BY id` 改为主键 `ORDER BY ledger_id`，并新增 structural test 绑定 DDL 主键且拒绝错误排序。仅修改 LSR-03 helper/test；`backend/.venv` targeted tests=`21 passed`，`py_compile`/`diff-check`=`PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R5=YES` 仅放行未来 fresh isolated runtime，不启动 r5，不裁决 LSR-03/G2。
- R5 fresh isolated runtime recheck（2026-08-25）：`FAIL`。新 `lsr03_r5` 仅绑定 `127.0.0.1:55432`；guarded identity、001→026、paused baseline、capture setup 与 rollback attempt 成功到达。首个 zero-mutation 断言错误地将 partial baseline 与 full ledger snapshot 比较并失败；按首错规则停止，不修复、不重跑。Attempt/MistakeDraft.attempt_id、完整 `SNAPSHOT_RESTORE_REQUIRED`/zero-mutation、attachment 与 cleanup 未执行。证据与 SHA256 manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r5/`；集群已停止且 55432 无监听；fixture cleanup=`NOT_RUN`。LSR-03 仍 `FAIL/[ ]`，G2 仍 `NOT_VERIFIED`。
- R5 首错后的无数据库定向修订（2026-08-25）：先只定位唯一 paused ledger `id`，再用 `_ledger_snapshot(admin, baseline_id)` 获取完整 baseline；after 继续使用同一 helper，并新增结构测试禁止 partial mapping 直接设为 baseline。仅修改 LSR-03 helper/test；`backend/.venv` targeted tests=`22 passed`，`py_compile`/`diff-check`=`PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R6=YES` 仅放行未来 fresh isolated runtime，不启动 r6，不裁决 LSR-03/G2。
- R6 fresh isolated runtime recheck（2026-08-25）：成功完成三条 actual-table inbound rollback。CaptureItem、Attempt、MistakeDraft.`attempt_id` 均精确命中 `LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED`；全 ledger/audit/event/relation/attachment zero-mutation、inbound retention、每条 cleanup=0 与 guard/admin/adapter identity 均有证据。新 `lsr03_r6` 仅绑定 `127.0.0.1:55432`，集群已停止且无监听；证据与 SHA256 manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r6/`，r2-r5 未覆盖。R6 结果等待独立 runtime Reviewer/Verifier，不自批 LSR-03/G2。
- R7 首错后的无数据库运行时合同修订（2026-08-25）：R7 发现 plain `postgresql://` 被 guard 接受后，Alembic 尝试缺失 psycopg2；runner 现仅接受 `postgresql+asyncpg://`，plain scheme 在 probe/child 前固定 `LSR03_DATABASE_URL_ASYNCPG_SCHEME_REQUIRED`/exit 64。新增 asyncpg/psycopg2 与 fail-before-probe/child 测试；`backend/.venv` targeted tests=`24 passed`，`py_compile`/`diff-check`=`PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R8=YES` 仅放行未来 fresh isolated runtime，不启动 r8，不裁决 LSR-03/G2。

### LSR-04 — 新旧等价性与逐项切换/退出

- [ ] LSR-04（`NOT_VERIFIED`：未启动；LSR-03 未完成且 combined G2=`BLOCKED`，不得启动）。
- depends_on：LSR-03、G1 `PASS`、G2 `PASS`。
- Primary Owner：Principal Software Architect；Reviewer：Principal Technical Reviewer；Verifier：Senior QA / SDET + Senior Security Engineer（两个真实独立 Worker）。
- role matrix：owner=`lsr04-owner`/Principal Software Architect；reviewer=`lsr04-reviewer`/Principal Technical Reviewer；verifier=`lsr04-verifier-qa`/Senior QA / SDET + `lsr04-verifier-security`/Senior Security Engineer；G3=`lsr04-g3-security`/Senior Security Engineer + `lsr04-g3-qa`/Senior QA / SDET；适用 G4=`lsr04-g4-recommendation`/Senior Recommendation Engineer + `lsr04-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr04-owner`。
- 触发 Gates：G3；若触及 AI/复习则 G4；G5 无生产范围时为 `NOT_AUTHORIZED`。
- 输入：LSR-01/02 manifest、LSR-03 隔离结果、API/页面/导航/权限回归基线。
- 允许写入：本任务精确列出的单一 API/service、页面/导航或旧入口变更及对应测试；每次只改一个边界并登记 rollback；文档 manifest；生产路径不在授权内。
- 禁止边界：不批量切换、不删除旧代码、不改变 `admin_session` 合同、不私有化公开 Note/Blog、不部署/commit/push。
- 验收：顺序为 client/service→`/manage/*`→旧入口安全退出→旧消费者；每步有匿名 401、非管理员 403、管理员成功、公开匿名可读、失败回滚和真实浏览器/网络证据；这些权限负向、浏览器/网络证据用于 G3（适用时 G4），再由 Senior Security Engineer、Senior QA / SDET 及 Senior Recommendation Engineer/Senior AI / LLM Engineer 的独立 Worker 对账；旧入口无意外写入。
- 暂停条件：新版不等价、权限/可见性回归、route owner 冲突、观察期失败、出现旧消费者或回滚不可用。

### LSR-05 — 零消费者后的旧结构删除

- [ ] LSR-05。
- depends_on：LSR-04、G1 `PASS`、G2 `PASS`、G3 `PASS`，若适用则 G4 `PASS`。
- Primary Owner：Principal Software Architect；Reviewer：Database Architect + Senior Security Engineer（两个真实独立 Worker）；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr05-owner`/Principal Software Architect；reviewer=`lsr05-reviewer-db`/Database Architect + `lsr05-reviewer-security`/Senior Security Engineer；verifier=`lsr05-verifier`/Senior QA / SDET；G1=`lsr05-g1-architect`/Principal Software Architect + `lsr05-g1-reviewer`/Principal Technical Reviewer；G2=`lsr05-g2-db`/Database Architect + `lsr05-g2-data`/Senior Data Engineer；G3=`lsr05-g3-security`/Senior Security Engineer + `lsr05-g3-qa`/Senior QA / SDET；适用 G4=`lsr05-g4-recommendation`/Senior Recommendation Engineer + `lsr05-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr05-owner`。
- 触发 Gates：G1、G2、G3；若适用 G4；任何生产删除触发 G5 `NOT_AUTHORIZED` 并停止。
- 输入：LSR-04 每项切换证据、全仓引用/路由/网络请求审计、迁移完整性与可恢复备份。
- 允许写入：仅本任务精确列出的旧产品/测试/迁移路径；文档 manifest；隔离删除演练。普通 Note/Blog/公开内容不在允许删除清单。
- 禁止边界：不得按名称或“零旧代码”删除整个 Note、公开路由、历史数据、仍有消费者的模型/表/测试；不得生产删除。
- 验收：零未解释消费者；数据已迁移且计数/关系/版本/可见性完整；隔离删除后恢复可用；旧 API/page/client 不再被网络调用；独立 Reviewer/Verifier 签字。
- 暂停条件：任一残留未知、数据/备份不完整、普通内容职责不清、删除不可逆、需生产 schema/数据。

### LSR-06 — 阶段一独立审查、验证与 Gate 对账

- [ ] LSR-06。
- depends_on：LSR-05、LSR-01～05 的适用 Gate 均为 `PASS`。
- Primary Owner：Principal Technical Reviewer；Reviewer：Product Architect + Senior Domain Analyst（两个真实独立 Worker）；Verifier：Senior QA / SDET + Database Architect + Senior Security Engineer（分别复核）。
- role matrix：owner=`lsr06-owner`/Principal Technical Reviewer；reviewer=`lsr06-reviewer-product`/Product Architect + `lsr06-reviewer-domain`/Senior Domain Analyst；verifier=`lsr06-verifier-qa`/Senior QA / SDET + `lsr06-verifier-db`/Database Architect + `lsr06-verifier-security`/Senior Security Engineer；G0=`lsr06-g0-product`/Product Architect + `lsr06-g0-domain`/Senior Domain Analyst；G1=`lsr06-g1-architect`/Principal Software Architect + `lsr06-g1-reviewer`/Principal Technical Reviewer；G2=`lsr06-g2-db`/Database Architect + `lsr06-g2-data`/Senior Data Engineer；G3=`lsr06-g3-security`/Senior Security Engineer + `lsr06-g3-qa`/Senior QA / SDET；适用 G4=`lsr06-g4-recommendation`/Senior Recommendation Engineer + `lsr06-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr06-owner`。
- 触发 Gates：G0、G1、G2、G3；若涉及 AI/采集则 G4；任何生产动作触发 G5 并停。
- 输入：LSR-01～05 manifest、原始失败证据、diff/status、迁移/回滚/权限/浏览器证据。
- 允许写入：仅 `tasks.md`/`validation.md` 对账和结论；不得修改实施结果或替实施者修复。
- 禁止边界：不得以文档完整替代实验证据；不得批准自己的设计；不得进入阶段二而未有 G0-G3 独立 PASS。
- 验收：逐项重跑引用扫描、迁移/恢复、权限负向、旧请求扫描和架构对账；Gate 结论逐项为 `PASS`/`PARTIAL`/`FAIL`/`BLOCKED`/`NOT_VERIFIED`/`NOT_AUTHORIZED`；没有历史结论继承。
- 暂停条件：Reviewer/Verifier 结论冲突、证据不可重算、Gate 未通过或授权边界不清。

## 阶段二：七个体系逐项主链验证

下列任务必须按编号逐一完成，不得批量勾选。每项仅允许写入对应精确测试/验证路径、五文件状态和隔离临时证据；禁止跨体系修补或提前融合。

### LSR-10 — Subject 与 KnowledgePoint

- [ ] LSR-10。
- depends_on：LSR-06。
- Primary Owner：Senior Backend Engineer；Reviewer：Product Architect；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr10-owner`/Senior Backend Engineer；reviewer=`lsr10-reviewer`/Product Architect；verifier=`lsr10-verifier`/Senior QA / SDET；G0=`lsr10-g0-product`/Product Architect + `lsr10-g0-domain`/Senior Domain Analyst；G1=`lsr10-g1-architect`/Principal Software Architect + `lsr10-g1-reviewer`/Principal Technical Reviewer；G2=`lsr10-g2-db`/Database Architect + `lsr10-g2-data`/Senior Data Engineer；G3=`lsr10-g3-security`/Senior Security Engineer + `lsr10-g3-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr10-owner`。
- 触发 Gates：G0、G1、G2、G3。
- 输入：当前 taxonomy model/schema/service/router/client/hook/page、隔离 DB、阶段一 manifest。
- 允许写入：精确 taxonomy 实现/测试路径与五文件 manifest；隔离 DB 合成数据。
- 禁止边界：不改 owner/auth 合同、不改公开 Note、不得跳过依赖或并行下一体系。
- 验收：Subject 创建/修改；知识点树/父子/归档/删除约束；正常、空、错误、401/403、重复提交；pytest/Vitest/typecheck/真实 Chromium（必要时）；关系无孤儿。
- 暂停条件：父子约束、权限、删除语义或空态未知/失败。

### LSR-11 — Question 主链

- [ ] LSR-11。
- depends_on：LSR-10。
- Primary Owner：Senior Backend Engineer；Reviewer：Principal Software Architect；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr11-owner`/Senior Backend Engineer；reviewer=`lsr11-reviewer`/Principal Software Architect；verifier=`lsr11-verifier`/Senior QA / SDET；G0=`lsr11-g0-product`/Product Architect + `lsr11-g0-domain`/Senior Domain Analyst；G1=`lsr11-g1-architect`/Principal Software Architect + `lsr11-g1-reviewer`/Principal Technical Reviewer；G2=`lsr11-g2-db`/Database Architect + `lsr11-g2-data`/Senior Data Engineer；G3=`lsr11-g3-security`/Senior Security Engineer + `lsr11-g3-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr11-owner`。
- 触发 Gates：G0、G1、G2、G3。
- 输入：QuestionDraft/DraftItem/Question 合同、Subject/KnowledgePoint 证据、隔离 DB。
- 允许写入：精确题目 model/schema/service/router/client/hook/page/test 路径及隔离数据。
- 禁止边界：不得绕过草稿确认、伪造来源/答案、私有数据公开、并行 Mistake/Review 改造。
- 验收：输入→draft→校验修正→正式 Question→来源/知识点关联→编辑/归档；空/错/401/403/重复和 type/test/browser 证据齐全。
- 暂停条件：草稿闸门、来源、版本、关系或鉴权有未知/失败。

### LSR-12 — Mistake 主链

- [ ] LSR-12。
- depends_on：LSR-11。
- Primary Owner：Senior Backend Engineer；Reviewer：Product Architect + Principal Software Architect（两个真实独立 Worker）；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr12-owner`/Senior Backend Engineer；reviewer=`lsr12-reviewer-product`/Product Architect + `lsr12-reviewer-architect`/Principal Software Architect；verifier=`lsr12-verifier`/Senior QA / SDET；G0=`lsr12-g0-product`/Product Architect + `lsr12-g0-domain`/Senior Domain Analyst；G1=`lsr12-g1-architect`/Principal Software Architect + `lsr12-g1-reviewer`/Principal Technical Reviewer；G2=`lsr12-g2-db`/Database Architect + `lsr12-g2-data`/Senior Data Engineer；G3=`lsr12-g3-security`/Senior Security Engineer + `lsr12-g3-qa`/Senior QA / SDET；G4=`lsr12-g4-recommendation`/Senior Recommendation Engineer + `lsr12-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr12-owner`。
- 触发 Gates：G0、G1、G2、G3、G4（若 AI/解析参与）。
- 输入：Question/QuestionDraft、MistakeDraft/Mistake schema/service/router/client/page、来源链。
- 允许写入：精确错题实现/测试路径、隔离合成数据、五文件 manifest。
- 禁止边界：不得直接把 AI 输出写成正式事实、删除 Note 历史、跳过人工确认、修改复习调度合同。
- 验收：可从 `QuestionDraft` 创建 `MistakeDraft` 草稿；正式转换必须严格先 `QuestionDraft→Question`，再人工确认 `MistakeDraft→Mistake→ReviewItem`；两类草稿均不得绕过人工确认；错因/答案/难度/来源保存；编辑/归档、失败/401/403/重复、type/test/browser 通过。
- 暂停条件：人工确认缺失、来源不可追溯、字段丢失、权限/完整性失败。

### LSR-13 — Review 主链

- [ ] LSR-13。
- depends_on：LSR-12。
- Primary Owner：Senior Recommendation Engineer；Reviewer：Product Architect；Verifier：Senior QA / SDET + Database Architect（两个真实独立 Worker）。
- role matrix：owner=`lsr13-owner`/Senior Recommendation Engineer；reviewer=`lsr13-reviewer`/Product Architect；verifier=`lsr13-verifier-qa`/Senior QA / SDET + `lsr13-verifier-db`/Database Architect；G0=`lsr13-g0-product`/Product Architect + `lsr13-g0-domain`/Senior Domain Analyst；G2=`lsr13-g2-db`/Database Architect + `lsr13-g2-data`/Senior Data Engineer；G3=`lsr13-g3-security`/Senior Security Engineer + `lsr13-g3-qa`/Senior QA / SDET；G4=`lsr13-g4-recommendation`/Senior Recommendation Engineer + `lsr13-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr13-owner`。
- 触发 Gates：G0、G2、G3、G4。
- 输入：Mistake、ReviewItem/ReviewRecord、评分/调度规则、隔离 DB。
- 允许写入：精确 review service/router/client/page/test 路径和隔离数据。
- 禁止边界：不改变未获 Gate 对账的复习算法、不暴露私有复习数据、不绕过 `get_current_admin`。
- 验收：到期队列→0–5 评分→ReviewRecord→`next_review_at`；验证新版 `interval_days`、`repetitions`、`next_review_at`、`last_reviewed_at` 等实际字段及当前调度语义；另行验证旧 `ef/interval/repetitions/next_review/last_reviewed` 只保存在 provenance/`migration_notes`，不写入不存在的新字段，不恢复或伪造历史 `ReviewRecord`；并发冲突、重复提交、空/401/403、回滚和 type/test/browser 证据。
- 暂停条件：时间/并发/重复语义不清，调度结果不可重算，权限或孤儿失败。

### LSR-14 — Note 主链与公开过滤

- [ ] LSR-14。
- depends_on：LSR-13。
- Primary Owner：Senior Backend Engineer；Reviewer：Senior Security Engineer + Senior UX / Interaction Designer（两个真实独立 Worker）；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr14-owner`/Senior Backend Engineer；reviewer=`lsr14-reviewer-security`/Senior Security Engineer + `lsr14-reviewer-ux`/Senior UX / Interaction Designer；verifier=`lsr14-verifier`/Senior QA / SDET；G0=`lsr14-g0-product`/Product Architect + `lsr14-g0-domain`/Senior Domain Analyst；G1=`lsr14-g1-architect`/Principal Software Architect + `lsr14-g1-reviewer`/Principal Technical Reviewer；G2=`lsr14-g2-db`/Database Architect + `lsr14-g2-data`/Senior Data Engineer；G3=`lsr14-g3-security`/Senior Security Engineer + `lsr14-g3-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr14-owner`。
- 触发 Gates：G0、G1、G2、G3。
- 输入：当前 Note model/schema/router/client/editor/Markdown/version/tag/folder/backlink、公开内容合同。
- 允许写入：仅 Note/Blog 相关精确实现/测试路径与隔离数据；五文件 manifest。
- 禁止边界：不得把 Note 整体迁为 Question/Mistake、不得公开私有笔记、不得删除 Blog/公开路由、不得无关 UI 重构。
- 验收：创建/编辑→Markdown→版本→标签/文件夹→反向链接→公开/隐藏/草稿过滤；匿名公开可读且私有不泄露，管理写入严格鉴权；错误/401/403/重复、type/test/browser 证据。
- 暂停条件：Note 保留职责、公开过滤、版本/链接、鉴权或 renderer owner 无法证明。

### LSR-15 — Capture 主链

- [ ] LSR-15。
- depends_on：LSR-14。
- Primary Owner：Senior AI / LLM Engineer；Reviewer：Senior Recommendation Engineer + Senior Security Engineer（两个真实独立 Worker）；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr15-owner`/Senior AI / LLM Engineer；reviewer=`lsr15-reviewer-recommendation`/Senior Recommendation Engineer + `lsr15-reviewer-security`/Senior Security Engineer；verifier=`lsr15-verifier`/Senior QA / SDET；G0=`lsr15-g0-product`/Product Architect + `lsr15-g0-domain`/Senior Domain Analyst；G1=`lsr15-g1-architect`/Principal Software Architect + `lsr15-g1-reviewer`/Principal Technical Reviewer；G2=`lsr15-g2-db`/Database Architect + `lsr15-g2-data`/Senior Data Engineer；G3=`lsr15-g3-security`/Senior Security Engineer + `lsr15-g3-qa`/Senior QA / SDET；G4=`lsr15-g4-recommendation`/Senior Recommendation Engineer + `lsr15-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr15-owner`。
- 触发 Gates：G0、G1、G3、G4（必需）；涉及数据转换时 G2。
- 输入：Capture、识别、人工修正、draft/formal conversion 合同、隔离附件/合成数据。
- 允许写入：精确 Capture/AI/draft 实现与测试路径、隔离附件、五文件 manifest。
- 禁止边界：不得接触真实 provider key/用户附件、不得让 AI 绕过人工确认、不得在默认 DB 写入、不得把识别输出当事实。
- 验收：Capture→识别→人工修正→draft→正式转换；成功/无 provider/坏输入/重复/401/403、来源/审计/幂等、type/test/真实 Chromium；真实 AI 成功不是默认假设。
- 暂停条件：来源/人工闸门、失败回退、秘密扫描、权限、幂等或 provider 行为未知。

### LSR-16 — 学习首页与建议

- [ ] LSR-16。
- depends_on：LSR-15。
- Primary Owner：Senior Frontend Engineer；Reviewer：Principal Software Architect；Verifier：Senior QA / SDET + Senior Recommendation Engineer（两个真实独立 Worker）。
- role matrix：owner=`lsr16-owner`/Senior Frontend Engineer；reviewer=`lsr16-reviewer`/Principal Software Architect；verifier=`lsr16-verifier-qa`/Senior QA / SDET + `lsr16-verifier-recommendation`/Senior Recommendation Engineer；G0=`lsr16-g0-product`/Product Architect + `lsr16-g0-domain`/Senior Domain Analyst；G1=`lsr16-g1-architect`/Principal Software Architect + `lsr16-g1-reviewer`/Principal Technical Reviewer；G3=`lsr16-g3-security`/Senior Security Engineer + `lsr16-g3-qa`/Senior QA / SDET；G4=`lsr16-g4-recommendation`/Senior Recommendation Engineer + `lsr16-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr16-owner`。
- 触发 Gates：G0、G1、G3、G4。
- 输入：LSR-10～15 各自 PASS manifest、Dashboard API/client/hook/page、隔离合成数据。
- 允许写入：仅学习首页聚合/展示精确路径和测试；隔离数据；五文件 manifest。
- 禁止边界：不得以零值伪装未知、不得读取旧权威、不得放宽管理权限、不得提前做阶段三全链路。
- 验收：待复习、最近题目/错题/复习、知识点统计、下一步建议均读新版权威数据；空/局部失败/401/403、type/test/browser 与来源对账清楚。
- 暂停条件：任一上游未 PASS、数据 owner 不明、局部失败丢失、推荐输出无来源/回退。

## 阶段三：跨体系融合验证

### LSR-20 — 核心学习 E2E

- [ ] LSR-20。
- depends_on：LSR-16。
- Primary Owner：Senior Backend Engineer；Reviewer：Principal Software Architect；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr20-owner`/Senior Backend Engineer；reviewer=`lsr20-reviewer`/Principal Software Architect；verifier=`lsr20-verifier`/Senior QA / SDET；G0=`lsr20-g0-product`/Product Architect + `lsr20-g0-domain`/Senior Domain Analyst；G1=`lsr20-g1-architect`/Principal Software Architect + `lsr20-g1-reviewer`/Principal Technical Reviewer；G2=`lsr20-g2-db`/Database Architect + `lsr20-g2-data`/Senior Data Engineer；G3=`lsr20-g3-security`/Senior Security Engineer + `lsr20-g3-qa`/Senior QA / SDET；适用 G4=`lsr20-g4-recommendation`/Senior Recommendation Engineer + `lsr20-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr20-owner`。
- 触发 Gates：G0-G4 的适用结论必须为 `PASS`；G5 无生产范围时为 `NOT_AUTHORIZED`，不作为非生产前置。
- 输入：LSR-10～16 全部 PASS、隔离 PostgreSQL、生产 frontend build、真实 FastAPI/Chromium、合成数据。
- 允许写入：任务专属仓库外临时目录中的隔离 DB/附件/融合 harness，以及本五文件；若脚本/测试持久化进仓库，必须先在本任务精确写入范围登记。
- 禁止边界：不得并行修产品、不得使用 jsdom 替代 Chromium、不得连接日常/生产服务/凭据。
- 验收：完整走通 Capture→QuestionDraft→Question→MistakeDraft→Mistake→ReviewItem→ReviewRecord→Dashboard；保留真实 Chromium 操作、API 响应、SQL 完整性和网络事件原始证据路径/hash；刷新/重登数据一致；持久化与审计证据可重算。
- 暂停条件：任一体系回归、真实路由/浏览器失败、数据不一致或环境无法隔离。

### LSR-21 — 公开/私有与认证负向融合

- [ ] LSR-21。
- depends_on：LSR-20。
- Primary Owner：Senior Frontend Engineer；Reviewer：Principal Technical Reviewer；Verifier：Senior QA / SDET + Senior Security Engineer（两个真实独立 Worker）。
- role matrix：owner=`lsr21-owner`/Senior Frontend Engineer；reviewer=`lsr21-reviewer`/Principal Technical Reviewer；verifier=`lsr21-verifier-qa`/Senior QA / SDET + `lsr21-verifier-security`/Senior Security Engineer；G3=`lsr21-g3-security`/Senior Security Engineer + `lsr21-g3-qa`/Senior QA / SDET；G5=`lsr21-g5-sre`/Senior DevOps / SRE + `lsr21-g5-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr21-owner`。
- 触发 Gates：G3、G5（仅检查生产是否被意外触达）。
- 输入：隔离服务、`admin_session`/`AdminSession`、`credentials: include`、`get_current_admin`、Subject/KnowledgePoint/Mistake 关联 fixtures、Note/Blog fixtures。
- 允许写入：任务专属仓库外临时目录的隔离测试/harness 和原始网络/浏览器证据、五文件 manifest；不得改 auth/route。
- 禁止边界：不使用 AUTH_BYPASS、不暴露 token/正文、不把 AuthGate 当后端授权、不改变 Cookie 合同。
- 验收：Subject→KnowledgePoint→Question 关联→Mistake 继承/展示→薄弱知识点与复习反馈；Note→KnowledgePoint/相关内容关联→搜索或导航→公开/私有可见性；保留 API/SQL/Chromium 原始证据路径/hash；匿名公开 Note/Blog 正常，私有数据不泄露。
- 暂停条件：任何越权、私有泄露、认证噪音、cookie 语义变化、失败状态无法复现。

### LSR-22 — login/manage/logout 401 与刷新重登一致性

- [ ] LSR-22。
- depends_on：LSR-21。
- Primary Owner：Senior Backend Engineer；Reviewer：Principal Technical Reviewer；Verifier：Senior QA / SDET + Senior Frontend Engineer（两个真实独立 Worker）。
- role matrix：owner=`lsr22-owner`/Senior Backend Engineer；reviewer=`lsr22-reviewer`/Principal Technical Reviewer；verifier=`lsr22-verifier-qa`/Senior QA / SDET + `lsr22-verifier-frontend`/Senior Frontend Engineer；G3=`lsr22-g3-security`/Senior Security Engineer + `lsr22-g3-qa`/Senior QA / SDET；适用 G4=`lsr22-g4-recommendation`/Senior Recommendation Engineer + `lsr22-g4-ai`/Senior AI / LLM Engineer；G5=`lsr22-g5-sre`/Senior DevOps / SRE + `lsr22-g5-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr22-owner`。
- 触发 Gates：G3；若涉及推荐/解析则 G4；G5 仅作生产范围检查，无生产范围时为 `NOT_AUTHORIZED`。
- 输入：隔离服务、`admin_session`/`AdminSession`、`credentials: include`、`get_current_admin`、公开 Note/Blog fixtures、刷新/重登 fixtures。
- 允许写入：任务专属仓库外临时目录的隔离测试/harness、HAR/console/网络原始证据和五文件 manifest；不得改 auth/route。
- 禁止边界：不使用 AUTH_BYPASS、不暴露 token/正文、不把 AuthGate 当后端授权、不连接生产。
- 验收：登录→`/manage/*` 私有操作→logout→严格接口 401，公开 Note/Blog 仍匿名可访问；新版编辑、刷新、重新登录后数据保持一致；保留 cookie、API、Chromium 原始证据路径/hash。
- 暂停条件：401/403 失败、logout 后仍可访问、私有泄露、刷新/重登数据不一致、证据不可重算。

### LSR-23 — 约束、归档删除、旧请求与浏览器诊断独立复核

- [ ] LSR-23。
- depends_on：LSR-22。
- Primary Owner：Senior Data Engineer；Reviewer：Senior Security Engineer + Principal Technical Reviewer（两个真实独立 Worker）；Verifier：Senior QA / SDET + Senior Frontend Engineer（两个真实独立 Worker）。
- role matrix：owner=`lsr23-owner`/Senior Data Engineer；reviewer=`lsr23-reviewer-security`/Senior Security Engineer + `lsr23-reviewer-technical`/Principal Technical Reviewer；verifier=`lsr23-verifier-qa`/Senior QA / SDET + `lsr23-verifier-frontend`/Senior Frontend Engineer；G1=`lsr23-g1-architect`/Principal Software Architect + `lsr23-g1-reviewer`/Principal Technical Reviewer；G2=`lsr23-g2-db`/Database Architect + `lsr23-g2-data`/Senior Data Engineer；G3=`lsr23-g3-security`/Senior Security Engineer + `lsr23-g3-qa`/Senior QA / SDET；适用 G4=`lsr23-g4-recommendation`/Senior Recommendation Engineer + `lsr23-g4-ai`/Senior AI / LLM Engineer。所有 identity 独立，排除 `lsr23-owner`。
- 触发 Gates：G1、G2、G3、G4 的适用结论必须为 `PASS`；G5 无生产范围时为 `NOT_AUTHORIZED`。
- 输入：融合环境、FK/业务约束、归档/删除规则、旧 route/API/client inventory、LSR-20～22 原始证据。
- 允许写入：仅任务专属仓库外临时目录的隔离 DB/网络/浏览器证据和五文件 manifest；若持久化检查脚本/测试，先登记精确路径授权。
- 禁止边界：不得在真实 DB 删除，不得删除 Note/Blog/公开内容，不得以“没有请求”替代静态消费者审计，不得忽略浏览器错误。
- 验收：删除/归档题目、错题、知识点时外键和业务约束不产生孤儿数据；不存在旧 API、旧页面或旧客户端意外网络请求；浏览器 console、page error、failed request、unexpected navigation 和秘密值扫描无异常；逐项保留 SQL/rg/Chromium 原始证据路径/hash。
- 暂停条件：FK/多态关系 orphan、旧请求命中、删除语义冲突、静态/运行时不一致、任何未解释浏览器/秘密异常。

## 阶段四：最终收束

### LSR-30 — 旧体系残留与消费者最终搜索

- [ ] LSR-30。
- depends_on：LSR-23、G0 `PASS`、G1 `PASS`、G2 `PASS`、G3 `PASS`，若适用则 G4 `PASS`；G5 无生产范围时为 `NOT_AUTHORIZED`。
- Primary Owner：Principal Software Architect；Reviewer：Principal Technical Reviewer；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr30-owner`/Principal Software Architect；reviewer=`lsr30-reviewer`/Principal Technical Reviewer；verifier=`lsr30-verifier`/Senior QA / SDET；G1=`lsr30-g1-architect`/Principal Software Architect + `lsr30-g1-reviewer`/Principal Technical Reviewer；G3=`lsr30-g3-security`/Senior Security Engineer + `lsr30-g3-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr30-owner`。
- 触发 Gates：G1、G3。
- 输入：阶段一删除 manifest、阶段三零请求证据、当前 source/migration/routes/clients/tests。
- 允许写入：只读搜索摘要、五文件 manifest。
- 禁止边界：不为达到零命中删除未知/保留 Note/Blog 内容，不改源码。
- 验收：代码、路由注册、导航、API client、模型导入、测试、迁移运行时残留逐项为已解释/保留/删除；旧入口零未解释消费者。
- 暂停条件：残留 owner 不明、公开内容受影响、静态与运行时不一致。

### LSR-31 — Alembic graph、空库 replay 与恢复

- [ ] LSR-31。
- depends_on：LSR-30。
- Primary Owner：Senior Data Engineer；Reviewer：Senior DevOps / SRE；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr31-owner`/Senior Data Engineer；reviewer=`lsr31-reviewer`/Senior DevOps / SRE；verifier=`lsr31-verifier`/Senior QA / SDET；G2=`lsr31-g2-db`/Database Architect + `lsr31-g2-data`/Senior Data Engineer；G5=`lsr31-g5-sre`/Senior DevOps / SRE + `lsr31-g5-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr31-owner`。
- 触发 Gates：G2；G5 无生产范围时为 `NOT_AUTHORIZED`，不作为非生产前置。
- 输入：最终候选 revision graph、不可变备份/manifest、隔离 PostgreSQL、恢复合同。
- 允许写入：一次性隔离 DB/恢复目录、验证脚本和五文件 manifest。
- 禁止边界：不改日常/生产 DB、不可逆 migration、不删除真实备份、不使用真实凭据。
- 验收：heads/current/check；空库完整 replay；升级后计数/关系/可见性/版本；恢复/回滚/销毁；catalog/进程清理为 0。
- 暂停条件：revision 漂移、孤儿/hash mismatch、恢复失败、清理失败或目标身份不明确。

### LSR-32 — 最终质量与真实浏览器重跑

- [ ] LSR-32。
- depends_on：LSR-31。
- Primary Owner：Senior QA / SDET；Reviewer：Principal Technical Reviewer；Verifier：Senior DevOps / SRE + Senior Frontend Engineer（两个真实独立 Worker）。
- role matrix：owner=`lsr32-owner`/Senior QA / SDET；reviewer=`lsr32-reviewer`/Principal Technical Reviewer；verifier=`lsr32-verifier-sre`/Senior DevOps / SRE + `lsr32-verifier-frontend`/Senior Frontend Engineer；G2=`lsr32-g2-db`/Database Architect + `lsr32-g2-data`/Senior Data Engineer；G3=`lsr32-g3-security`/Senior Security Engineer + `lsr32-g3-qa`/Senior QA / SDET；G4=`lsr32-g4-recommendation`/Senior Recommendation Engineer + `lsr32-g4-ai`/Senior AI / LLM Engineer；G5=`lsr32-g5-sre`/Senior DevOps / SRE + `lsr32-g5-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr32-owner`。
- 触发 Gates：G2、G3；若适用 G4；G5 无生产范围时为 `NOT_AUTHORIZED`。
- 输入：所有阶段 manifest、目标 pytest/Vitest/typecheck/build、隔离服务、真实 Chromium。
- 允许写入：隔离测试输出和必要首次失败证据、五文件 manifest；不改生产/部署。
- 禁止边界：不得把 jsdom 当浏览器、不得忽略失败、不得用构建缓存或历史数字代替当前结果。
- 验收：相关 pytest、Vitest、`npx tsc --noEmit`、生产 build、真实 Chromium 正常/异常/负向、console/page error/request/导航/秘密扫描；失败状态如实记录。
- 暂停条件：任一质量门失败、浏览器证据缺失、秘密/越权/failed request 未解释。

### LSR-33 — 临时资源与 worktree 收束

- [ ] LSR-33。
- depends_on：LSR-32。
- Primary Owner：Senior DevOps / SRE；Reviewer：Senior Security Engineer；Verifier：Senior QA / SDET。
- role matrix：owner=`lsr33-owner`/Senior DevOps / SRE；reviewer=`lsr33-reviewer`/Senior Security Engineer；verifier=`lsr33-verifier`/Senior QA / SDET；G3=`lsr33-g3-security`/Senior Security Engineer + `lsr33-g3-qa`/Senior QA / SDET；G5=`lsr33-g5-sre`/Senior DevOps / SRE + `lsr33-g5-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr33-owner`。
- 触发 Gates：G3；G5 无生产范围时为 `NOT_AUTHORIZED`。
- 输入：所有隔离 DB/服务/端口/浏览器/临时账户/附件/进程清单、dirty worktree 基线。
- 允许写入：仅隔离资源清理与五文件清单；任何删除只针对本任务创建的明确临时资源且可恢复优先。
- 禁止边界：不得清理用户既有 dirty、不得 stage/commit/push、不得删除生产/日常资源、不得接触凭据。
- 验收：隔离 DB/端口/进程/临时账户/附件和 browser context 清理；`git status` 仅保留既有及本目录五文件；无 staged paths；`git diff --check` 通过。
- 暂停条件：资源归属不明、清理可能误删用户数据、dirty 重叠、端口/进程无法确认。

### LSR-34 — 最终独立审查、报告与结论

- [ ] LSR-34。
- depends_on：LSR-33。
- Primary Owner：Principal Technical Reviewer；Reviewer：Product Architect + Senior Domain Analyst（两个真实独立 Worker）；Verifier：Senior QA / SDET + Database Architect + Senior Security Engineer + Senior DevOps / SRE（四个真实独立 Worker，按域复核）。
- role matrix：owner=`lsr34-owner`/Principal Technical Reviewer；reviewer=`lsr34-reviewer-product`/Product Architect + `lsr34-reviewer-domain`/Senior Domain Analyst；verifier=`lsr34-verifier-qa`/Senior QA / SDET + `lsr34-verifier-db`/Database Architect + `lsr34-verifier-security`/Senior Security Engineer + `lsr34-verifier-sre`/Senior DevOps / SRE；G0=`lsr34-g0-product`/Product Architect + `lsr34-g0-domain`/Senior Domain Analyst；G1=`lsr34-g1-architect`/Principal Software Architect + `lsr34-g1-reviewer`/Principal Technical Reviewer；G2=`lsr34-g2-db`/Database Architect + `lsr34-g2-data`/Senior Data Engineer；G3=`lsr34-g3-security`/Senior Security Engineer + `lsr34-g3-qa`/Senior QA / SDET；适用 G4=`lsr34-g4-recommendation`/Senior Recommendation Engineer + `lsr34-g4-ai`/Senior AI / LLM Engineer；G5=`lsr34-g5-sre`/Senior DevOps / SRE + `lsr34-g5-qa`/Senior QA / SDET。所有 identity 独立，排除 `lsr34-owner`。
- 触发 Gates：G0、G1、G2、G3，若适用 G4；G5 仅作生产范围检查，无生产范围时保持 `NOT_AUTHORIZED`，不是非生产收束前置。
- 输入：LSR-30～33、全部阶段 manifest/失败摘要/最终汇总、当前 status/diff。
- 允许写入：仅本五文件最终状态和报告；不修改任何产品或历史证据。
- 禁止边界：不得自批高风险设计、不得把“技术候选”写成已部署、不得 commit/push/deploy、不得省略未验证/未授权项。
- 验收：报告逐项列出删除/保留、新版七体系、融合、迁移/回滚、权限/可见性、残留、风险和决策；只有全部当前证据、独立签核和 Gate `PASS` 才能结论 `PASS`，否则使用 `PARTIAL`/`FAIL`/`BLOCKED`/`NOT_VERIFIED`/`NOT_AUTHORIZED`。
- 暂停条件：任一 Gate 未完成、独立结论冲突、证据缺失、生产/凭据/公开切换仍未授权。

### LSR-03 controlled restart execution evidence (2026-08-25)

- Status remains `PARTIAL` / `[ ]`; G2 remains `NOT_VERIFIED`; no LSR-04. A fresh cluster `/tmp/lsr03-final-cluster.3GsaS6` on `127.0.0.1:55432` was used exclusively through `backend/tests/lsr03_guarded_runner.py`, then stopped after evidence capture. No 5432 connection was made.
- Guarded empty replay `001→026` and second idempotent replay passed (`/tmp/lsr03-final-replay-2.log`, `/tmp/lsr03-final-replay-idempotent.log`). Adapter rehearsal passed active/paused/retained/chapter-019 and active idempotency (`/tmp/lsr03-final-rehearsal-2.log`); rollback audit/transition passed (`/tmp/lsr03-final-rollback-2.log`).
- 16 guarded tests passed; independent archive/source/disposition/live counts were `4/4/4/4/4`, bidirectional EXCEPT and FULL OUTER mismatches `0` (`/tmp/lsr03-final-validation.log`). Digest ACL negative/positive returned `false,false,false,false,true`; direct ledger mutation rejected by `LEGACY_MIGRATION_DIRECT_LEDGER_MUTATION_REJECTED`.
- Pre-migration 025 custom dump `/tmp/lsr03-pre-migration.dump` restored to `lsr03_pre_restore`; catalog check showed no `legacy_note_migrations` and retained base `questions`. Dump hash `45ff916d1a9d1becc13f12e607a0db0df758acb601014fb4ee6f9244a6322917`.
- Remaining: independent Reviewer/Verifier rerun, full Capture/Attempt/MistakeDraft inbound negative fixture, exhaustive nonce/hash/collision/search fixture matrix, and G2 decision. Final code/log hashes are recorded in validation.md; production/source writes remain unauthorized.
- Fixture-QA update (2026-08-25): independent archive NDJSON + separate expected-hash manifest + run manifest and guarded TEMP replay negatives are captured under `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r2/` (`SHA256SUMS`, 13 guarded tests passed). TEMP inbound predicate, nonce replay/second-use/cross-transaction, collision, search-vector sentinel, and chapters three-case fixtures pass. Actual-table CaptureItem/Attempt rollback was stopped after two consecutive fixture failures as required; it remains `NOT_VERIFIED` and does not change `LSR-03 PARTIAL/[ ]` or `G2 NOT_VERIFIED`.

- R8 首错后的 deterministic seed 修订（2026-08-25，历史，已被 R9 PASS superseded）：R6 Owner evidence 未持久化 machine-readable synthetic seed，R8 Verifier 在空 post-026 数据库执行 rehearsal，source Note 缺失。新增 `backend/tests/lsr03_seed_rehearsal.py` 与 no-DB contract，固定 users/approval authorization/rollback admin/taxonomy/source Note/paused baseline IDs，精确空集外 fail-closed，并要求 seed 先于 rehearsal。R8 evidence 保留；仅改 LSR-03 helper/static test/workflow，未改产品/model/migration/adapter；历史 readiness=`READY_FOR_R9=NO`，不代表当前状态。

- R9 唯一顺序冻结为：guard/private-venv Alembic `001→026` → 重复同一 Alembic 命令作 idempotent → `backend/.venv/bin/python tests/lsr03_seed_rehearsal.py` → `backend/.venv/bin/python tests/lsr03_rollback_rehearsal.py --inbound-fixtures`；全部从 `backend`、`PYTHONPATH=.`、同一 `postgresql+asyncpg://...@127.0.0.1:55432/lsr03_r9` URL 经 `lsr03_guarded_runner.py` 执行。不得 5432/default DB；总体 LSR-03/G2 不变。
- R9 runtime 记录（2026-08-25，G2 决定见下方最终对账）：按冻结顺序完成 identity、001→026、二次幂等、deterministic seed 与三条 actual-table inbound rollback；该 runtime evidence=`PASS`，不等于 G2。原始 R9 证据位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r9-verifier/`。
- R9 最终独立 runtime（2026-08-25）：按冻结顺序完成 identity、001→026、二次幂等、deterministic seed 与三条 actual-table inbound rollback。CaptureItem、Attempt、MistakeDraft.`attempt_id` 均精确返回 `SNAPSHOT_RESTORE_REQUIRED`；完整 ledger/relation/audit-event/attachment before-after 未变，三案 cleanup=0，admin/adapter identity 分离，cluster 已停止且 55432 无监听。新证据位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r9-verifier/`；Final Reviewer=`PASS`、Independent Verifier R9=`PASS`、LSR-03 runtime evidence=`PASS`，该 runtime PASS 不等于 G2。

- G2 最终独立对账（2026-08-25）：Database=`BLOCKED`、Data=`FAIL`、combined G2=`FAIL`。决定性问题分为两类：实现合同漂移（options 空值、idempotency key、mirror/provenance、retained predicate）与当前证据缺口（active/retained/019 实际 parity、logical rollback/pre-026 restore、R9 原始日志 hash）。因此 LSR-04 未启动且禁止启动；不得将 LSR-03 runtime PASS/[x] 写成 G2 PASS。
- 最终综合 G2 attempt（2026-08-25）：独立 Reviewer=`PASS`（实现修订）；Verifier attempt1/attempt2=`FAIL`，均因 QA fixture drift，按规则不进行第三次。fresh guard/001→026/idempotent/schema/ACL/check=`PASS`，但正向链未完成，negative/logical rollback/actual inbound/restore=`NOT_RUN`。证据=`/Users/limengyang/.codex/attachments/lsr03-g2-final-evidence-20260825/`；55432 stopped/no listener、no5432、无生产/commit/push/deploy。当前 LSR-03=`BLOCKED/[ ]`，G2 Database=`BLOCKED`、Data=`BLOCKED`、combined=`BLOCKED`；R9 runtime 仅作历史，已被当前 code hashes/final attempts supersede；LSR-04 未启动且禁止。
