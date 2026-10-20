# LSR 需求与验收合同

## 1. 目标与当前状态

目标是把当前个人学习系统从并存的旧兼容链安全收敛到新版结构化学习体系，完成四阶段串行验证，并在有当前证据、独立复核和明确授权时才退休旧结构。当前 canonical 状态：LSR-01=`PASS/[x]`（静态 mapping）；LSR-02=`PASS/[x]`（静态迁移合同；Reviewer=`PASS_WITH_NOTES`、Verifier=`PASS`）；LSR-03=`PARTIAL/[ ]`（当前 fresh isolated runtime=`PASS`，完整 G2 证据仍缺）；G0/G1=`PASS`，G2 Database/Data/combined=`BLOCKED`，G3-G4=`NOT_VERIFIED`，G5=`NOT_AUTHORIZED`；LSR-04 及后续未启动。本文件冻结要求，不授权迁移、删除、切换、生产数据库、部署、commit 或 push。

2026-08-25 当前运行事实：权威证据目录 `/Users/limengyang/.codex/attachments/lsr03-g2-fresh-final-evidence-20260825-bootstrap-fixture-admin-cwd/` 的独立 Verifier 结论为 `PASS`，覆盖 fresh replay、026 idempotency、正向/负向路径、logical rollback、三类 inbound zero-mutation、pre-026 schema restore 与 cleanup。独立 G2 Gate 仍为 `BLOCKED`，因为本要求中的完整 target parity、`retained_public_only`、visibility/orphan/ReviewRecord、rollback replay/audit digest 与带数据 restore 尚无同一轮充分证据；这些仍属于 LSR-03，不得跳到 LSR-04。

## 2. 领域定义与保留边界

- 新体系：`Question/QuestionDraft/DraftItem`、`Mistake/MistakeDraft`、`ReviewItem/ReviewRecord`、`Subject/KnowledgePoint/QuestionKnowledgePoint/KnowledgePointLink`、`Capture` 和 `/manage/*`。
- 旧候选：`Note(type=mistake)` 及复习字段、旧 review API/页面、`/write-mistake` 和重复私有写入口，以及证实已被新体系替代的兼容消费者。
- 保留：普通 `Note`、Blog、公开内容、历史公开路由与未完成迁移的数据。不得把整个 Note 模型当作旧系统删除。
- 认证：stateful HttpOnly `admin_session` backed by `AdminSession`；受保护前端请求使用 `credentials: 'include'`；后端 `get_current_admin` 是真实授权边界。不得引入/描述 Bearer/JWT 迁移。
- 环境：数据库检查和写入仅限一次性隔离 PostgreSQL；融合验收必须使用隔离 DB、生产前端构建、真实 FastAPI 路由和真实 Chromium。生产、默认日常库和默认部署目标永远不在本合同的自动授权内。

### 2026-08-23 当前用户领域合同（覆盖相冲突历史决定）

用户原话：`以上三项同意`。本合同覆盖相冲突的历史决定/未决项，但不声称已实现或任何 Gate PASS：

1. 已发布且未隐藏的旧 `Note(type=mistake)` 保留为只读公开 Note，保留原 `/notes/{slug}` URL；关闭 `/mistakes` 聚合入口。新版 `Question/Mistake` 始终私有；旧公开 Note 与新版私有学习对象通过 source/provenance 关联。普通 Note/Blog 保持原职责。
2. 旧复习仅将当前调度状态迁移到 `ReviewItem`；原 `ef/interval/repetitions/next_review/last_reviewed` 保存在 provenance/`migration_notes`，不生成或伪造历史 `ReviewRecord`。语义不明或空值记录为 `paused`，等待人工确认。
3. Capture 允许同一操作同时生成 `QuestionDraft` 与 `MistakeDraft`；正式转换严格先 `QuestionDraft→Question`，再人工确认 `MistakeDraft→Mistake→ReviewItem`；两类草稿均不得绕过人工确认。

## 3. 功能需求

### 阶段一：迁移与退休

1. LSR-01 必须覆盖模型字段、表/列、Alembic revisions、API、service、router、client、hook、page、navigation、tests、静态数据和导出消费者，并逐项标记 `迁移/保留/替换/删除/未知`。
2. LSR-02 必须冻结旧 Note 错题/复习到新版各实体的字段映射；slug/UUID、科目、知识点、答案、错因、难度、EF、interval、repetitions、复习时间、版本、来源、可见性和审计字段不得猜测或静默丢弃。
3. LSR-03 在 LSR-02 后直接进入隔离 PostgreSQL，完成空库 Alembic replay、合成或预先授权本地快照的迁移演练、前后计数/hash/关系/孤儿/重复/可见性/版本比较、幂等重跑、向前迁移和恢复/回滚；它生成 G2 证据，再由独立 Gate Worker 对账 G2；不得把 G2 `PASS` 设为 LSR-03 前置。

LSR-03 重开前静态预检要求（2026-08-25）：下一次 fresh isolated run 的实际表夹具必须由 admin session 完成 setup、baseline、zero-mutation 检查和 cleanup；adapter-runner 只调用受保护 rollback 函数，不直接读取 ledger。CaptureItem/Attempt 必须绑定 `target_mistake_draft_item_id`，MistakeDraft 入向必须绑定对应 `target_mistake_draft_id`/`attempt_id`。每个阻断样本必须验证固定 `SNAPSHOT_RESTORE_REQUIRED`、全部 ledger 可变/关键 provenance 与 inbound/attachment/audit-event 行 zero mutation、admin/adapter identity 以及 cleanup zero；helper 入口还必须独立拒绝非 `127.0.0.1:55432/lsr03_*`、URL 不一致和 non-recovery 失败。独立 `lsr03_reviewer`=`REVIEW: PASS`、`lsr03_verifier`=`VERIFY: PASS`，静态预检 `PASS`、`READY_FOR_FRESH_REHEARSAL=YES`；总体 LSR-03/G2 状态不变。

r3 runtime recheck 已按首错停止：guarded runner 导入阶段缺少 `sqlalchemy`，未执行 URL probe、Alembic、SQL 或 actual-table fixture。该失败只记录为 runtime `FAIL`，必须保留 r3 首错 manifest，不得以静态 PASS 推导 runtime 或 G2 PASS。

r3 首错后的无数据库合同修订已完成：历史 r3 首错与 evidence 不覆盖，r4 未启动。guarded runner 在 SQLAlchemy 导入/DB 动作前要求项目 `backend/.venv` runtime，错误解释器固定 `LSR03_PYTHON_RUNTIME_REQUIRED`/exit 64；所有 child 固定 `backend/.venv/bin/python`、`PYTHONPATH=.`、cwd=`backend`。`backend/.venv` targeted guarded/static tests=`20 passed`，`py_compile`/`diff-check`=`PASS`；`READY_FOR_R4=YES` 仅表示未来 fresh isolated runtime 可进入，不改变 LSR-03=`FAIL/[ ]`、G2=`NOT_VERIFIED`。

R4 fresh runtime recheck 已按首错停止：guarded identity、001→026、paused baseline 成功；首个 actual-table fixture 在 `_audit_event_snapshot` 查询 rollback audit 表不存在的 `id` 列而失败。未执行三条 inbound setup/rollback、zero-mutation 或 fixture cleanup；cluster stop 与 55432 无监听已证明。R4 evidence 为新目录 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r4/`，r2/r3 不覆盖；fixture cleanup=`NOT_RUN`，不以本结果推导 LSR-03/G2 PASS。

R4 首错后的无数据库定向修订已完成：按 026 DDL 主键 `ledger_id` 修正 rollback audit snapshot 排序，并新增 structural test 绑定该 DDL、禁止该表 `ORDER BY id`。仅修改 LSR-03 helper/test；`backend/.venv` targeted tests=`21 passed`，`py_compile`/`diff-check`=`PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R5=YES` 仅表示允许未来 fresh isolated runtime，禁止 r5 越过授权，LSR-03/G2 状态不变。

R5 fresh runtime recheck 已按首错停止：guarded identity、001→026、paused baseline、capture setup 与 rollback attempt 到达；zero-mutation 断言因比较 partial baseline 与 full ledger snapshot 而失败。未执行 Attempt/MistakeDraft.attempt_id fixture、后续 `SNAPSHOT_RESTORE_REQUIRED`/zero-mutation 完整验证或 cleanup；cluster stop 与 55432 无监听已证明。R5 evidence 为新目录 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r5/`，r2/r3/r4 不覆盖；fixture cleanup=`NOT_RUN`，不以本结果推导 LSR-03/G2 PASS。

R5 首错后的无数据库定向修订已完成：先定位唯一 paused ledger `id`，再通过 `_ledger_snapshot(admin, baseline_id)` 获取全列 baseline；after 使用同一 helper，新增 structural test 禁止 partial mapping 作为 baseline。仅修改 LSR-03 helper/test；`backend/.venv` targeted tests=`22 passed`，`py_compile`/`diff-check`=`PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R6=YES` 仅表示允许未来 fresh isolated runtime，禁止 r6 越过授权，LSR-03/G2 状态不变。

R6 fresh runtime 已完成三条 actual-table inbound rollback：三条均精确返回 `LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED`，全 ledger/audit/event/relation/attachment zero-mutation、inbound retention、cleanup=0 和 guard/admin/adapter identity 证据齐全；集群停止且 55432 无监听。R6 evidence 为新目录 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r6/`，r2-r5 不覆盖；该结果等待独立 runtime Reviewer/Verifier，不改变 LSR-03/G2。

R7 首错后的无数据库运行时合同修订已完成：plain `postgresql://` 被 guard 接受后触发缺失 psycopg2，现固定只接受 `postgresql+asyncpg://`，并在 probe/child 前返回 `LSR03_DATABASE_URL_ASYNCPG_SCHEME_REQUIRED`/exit 64。无 DB tests=`24 passed`，`py_compile`/`diff-check`=`PASS`；独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R8=YES` 仅表示允许未来 fresh isolated runtime，禁止 r8 越过授权，LSR-03/G2 不变。

### LSR-02 数据合同验收要求（当前）

LSR-02 的交付必须满足以下全部设计要求；本任务只能达到 `PARTIAL`/等待独立复核，不得把下列设计写成当前实现：

- 只对 `Note.type='mistake'` 建 ledger；普通 Note/Blog zero ledger/target，公开职责不被迁移任务私有化。
- 保存不可变 source snapshot、`canonical_payload JSONB`（required keys 含独立顶层 `legacy_ef_bits`，逐 key 类型、typed archive projection、`id/type/slug`/所有字段与锁定 live Note 绑定、冻结 key/array/time/NULL/empty normalization）、canonical SHA-256、source UUID/slug/status/hidden/revision、完整 legacy review typed values + raw JSON、mapping version、idempotency key、分离的 source/question-conversion/mistake-conversion/schedule/rollback approval identity/audit；LSR-03 必须现场用 UTF-8 digest 重算并拒绝 archive 传入 hash，禁止静默丢字段或 AI 猜事实。
- 完成旧 Note 全字段→Question/QuestionSource/QuestionKnowledgePoint/Mistake/ReviewItem/ledger/Subject/KP 的 source/target/type/normalization/default/provenance/disposition/lossiness/validation/rollback 矩阵；chapter 只能映射已有 KP 树，不恢复独立 Chapter，不自由文本建 Subject/KP。
- `question` 缺失不得用 title/content 补齐；`correct_answer`/题型/options 不满足新版 answer contract 时进入 manual；`analysis` 的 canonical/mirror 双字段语义、`my_answer`、difficulty、source/status/hidden/version/audit 必须可审计。
- 旧 Note 没有独立 `reason_category`/`mistake_reason` 时只能使用明确的 `unknown`/`NULL` 默认并保留原 analysis provenance；不得从自由文本或 AI 猜错因。
- 旧 `ef` 只保留 provenance；`interval/repetitions/next_review/last_reviewed` 只在可证明合法时形成 ReviewItem 当前调度状态；空/无时区/歧义进入 `migrated_paused`，不创建 ReviewRecord，不伪造历史复习。
- `legacy_ef` 保持 FLOAT8/bit-exact，但 NaN、+Infinity、-Infinity 必须 fail closed 进入 manual/failed，不能进入 ready/active/paused；时间 canonicalization 使用 UTC 微秒，不得截断到毫秒。
- `migrated_active` 必须同时有 Question DraftItem+QuestionDraft、Mistake DraftItem+MistakeDraft、Question+QuestionSource+QKP+Mistake+当前 ReviewItem；`migrated_paused` 必须同时有两枚 DraftItem/两类 Draft、Question+QuestionSource+QKP+Mistake，但绝不创建 ReviewItem；`retained_public_only` 仅适用于已发布未隐藏且经批准继续公开的不可映射旧 Note；其余分入 manual/failed。
- 合法 active 调度值冻结在 ledger `mapped_next_review_at TIMESTAMPTZ`/`mapped_last_reviewed_at TIMESTAMPTZ`；LSR-03 run manifest 必须提供 `evaluation_time_utc`。`due` 只按 `state='migrated_active' AND mapped_next_review_at <= evaluation_time_utc` 计算，不假设 `ReviewItem.due` 列存在。
- 冻结 `legacy_note_migrations` DDL、逻辑 enum/check、FK `ON DELETE RESTRICT`、target uniqueness/index、单一 state transition、source hash/mapping/idempotency、approval/audit、`migration_notes`、`rollback_reference`。ReviewItem canonical successor 为 `mistake_id` FK；当前 `target_type/target_id` 不得被文档误称为已修复。
- 选择 `QuestionSource.source_ref='legacy-note:<UUID>'` bounded token 解决 model `String(64)` 与 schema 500 的长度冲突；不得截断 slug/URL或隐式扩列，完整 slug/URL 留在 ledger/snapshot/source_url。
- Capture 双草稿可同操作产生，但 QuestionDraft→Question 必须先于人工批准 MistakeDraft→Mistake→ReviewItem；Attempt/source_capture/approval actor/time/sequence/hash provenance 链必须明确，AI/OCR 输出不能成为事实。
- 幂等重跑必须返回同 target IDs、拒绝 hash drift/覆盖、原子创建 target+ledger state；恢复使用 immutable snapshot/backup 到 fresh isolated DB，禁止把 destructive Alembic downgrade 当 rollback。
- LSR-03 输入必须包含合成 fixtures（active、paused、public-only、missing/ambiguous、duplicate/collision、cross-subject、ordinary Note/Blog）及可执行 count/hash/FK/orphan/duplicate/visibility/version/ReviewRecord absence/restore SQL contract；LSR-02 不创建脚本、测试或 DB。
- 当前 route/mutation contract 必须进入 LSR-02 canonical table：`/mistakes` 与 `/mistakes/review` 为 308 successor；published&&!hidden `/notes/{slug}` 只读；legacy mistake single mutation 为 410、mixed batch 为 409；`/write-mistake*` 与 `/api/review/*` 在 cutover 为 410，且不留旧只读分支。实现仍属 LSR-04/`NOT_VERIFIED`。
- Note `search_vector` 只作 derived/public-search retained 字段；source hash 使用 NULL sentinel `CASE WHEN search_vector IS NULL THEN '<NULL>' ELSE '<VALUE>' || search_vector::text END`；迁移前后旧 Note 行、content/slug/status/hidden/version/search_vector 必须逐行不变，若重建必须有公共搜索 parity；Question KP canonical、Mistake KP links 只能是 projection（`target_qkp_ids`/`target_projection_ids` 统一 `INTEGER[]`，仅比较 KP ID set，不声称 role/order）。
- 受控回滚必须区分 logical rollback（先写外部 immutable JSON/hash；由唯一受控 transition 函数在同一事务把 ledger 置 `rolled_back`、写入 rollback_reference 并原子清空全部 draft/final/source/projection target columns/arrays/hash，再按 ReviewItem→Mistake projection→Mistake→MistakeDraft→Mistake DraftItem→QSource/QKP/generic links→Question→QuestionDraft→Question DraftItem 删除；legacy Note 不删）与 disaster snapshot restore（恢复前迁移 DB、ledger 行不存在，不得伪称 rolled_back）。旧 legacy import 不创建 Capture；若发现 Capture/Attempt unexpected inbound reference，logical rollback 必须失败并转 snapshot restore。source writer 使用锁定+隔离级别+commit 前漂移复算。
- LSR-02 后续只允许专用 `legacy_note_migration_adapter`（实现/G2 `NOT_IMPLEMENTED`）承接迁移；adapter 复用既有 domain invariants 但不调用 unchanged existing services，负责 UUIDv5、`DraftItem.source_type=legacy_note`、`QuestionSource.source_type=note`、双草稿审批/转换顺序、QuestionSource、禁止 generic Question link、paused 无 ReviewItem，并须覆盖 service-signature/side-effect/atomicity/idempotency 冲突测试合同。
- adapter 接口必须冻结 session/source_note_id/mapping_version/分离 approval actors+sequences/expected_source_hash/dry_run 输入，返回所有 DraftItem/Draft/QuestionSource/QKP/`target_projection_ids INTEGER[]`/Question/Mistake/ReviewItem IDs、state、各 approval audit、source_hash、idempotent_replay，并使用单 `SERIALIZABLE` + source `FOR UPDATE`；错误只能来自闭合 error enum（essay 固定 `ESSAY_MANUAL_REQUIRED`，source title 超长固定 `SOURCE_TITLE_TOO_LONG`）。schema-qualified invoker helper 必须有 adapter/verifier 最小 SELECT ACL，permission error 不得吞掉；必须接收精确 QuestionSource、source_title、source_note_id、mapping_version、source_hash，读取确定 provenance，TEXT/JSONB 显式统一；LSR-03 的唯一 SQL 必须定义可载入/校验的 `lsr02_run_manifest` 与含 canonical_payload 的 `lsr02_source_snapshot` TEMP TABLE。
- SECURITY DEFINER transition 只能由 `NOLOGIN` owner 通过精确 `session_user=legacy_note_adapter_runner` 的 adapter execution login 调用，`legacy_note_adapter` 承担仅执行授权；`app_role`/verifier 无 membership、EXECUTE 或 target/typed-field/event/transition-table 写权限；函数固定 `SET search_path=pg_catalog,legacy_migration`、锁 ledger/source、按目标状态校验对应 approval actor/time/sequence 与 target bundle，rollback 由独立授权管理员承担，nonce marker 不是唯一安全边界，direct/forged marker 必须拒绝。隔离 replay 先安装并验证 `public.pgcrypto`，不触生产。
- approval 执行路径必须由 owner-only `create_legacy_note_migration_pending(...)` 与 `record_legacy_note_migration_approval(...)` 写入 source/question/mistake/schedule 各自的 actor、UTC time、sequence、event ID；transition 只读取并校验这些锁定值，active actor 只能是 schedule approver，paused 不强制同人，rollback actor 独立授权；adapter 不能以单一 `p_actor` 或伪造事件替代对应审批链。
- 第八轮合同要求：pending 创建函数与 approval 记录函数必须有完整可执行 PL/pgSQL body、精确 signature/ACL/锁/expected state/hash/sequence；failed→pending 必须清空所有旧 approval/event/target/note 字段并重新走 source approval；唯一 SQL 分为 all-dispositions/final/retained scopes，required canonical keys 含 `source_note_id/source_url/legacy_review_json/legacy_ef_bits`；rollback 先校验不可变 rollback JSON digest 与 Capture/Attempt 入向引用，异常只转 snapshot restore；verifier 仅获 `digest(bytea,text)` 执行权，不获写表或随机 UUID 权限。
- 第十二次合同要求：pending INSERT 完整写入 typed legacy/schedule 字段并绑定 canonical payload；active 只能在 schedule approval、UTC mapped-next 与 fixed-interval ReviewItem 齐备时 TRUE→FALSE；QKP/projection INTEGER[] 必须无 NULL、去重、严格升序并与 canonical relation 双向等价；owner-only nonce cleanup 仅删除已消费过期行；owner 现有表最小 SELECT ACL；manifest/archive/all-dispositions/source scope 空集 fail-closed；approval event 必须跨 ledger/source/mapping/hash 绑定。
- 第十三次合同要求：canonical payload 先做逐 key JSON 类型/nullable、UUID、RFC3339 微秒 UTC、date round-trip、array/object、整数范围与 EF finite 校验，再进行任何 typed cast；`legacy_ef_bits` 先以 TEXT 校验恰为 16 个小写 hex 字节后才存 `CHAR(16)`；所有公开 hash 参数使用 TEXT 并先做恰 64 个小写 hex 校验；transition reason/必填参数使用固定错误码；nonce cleanup 唯一登录角色为 `legacy_migration_maintenance_runner`；replay 要求 snapshot/archive/archive-manifest/disposition/source 五方计数与 manifest 相等且 source_note_id 双向集合一致，failed/rolled_back 只能计入 all-dispositions，不能冒充 final success。
- 第十四次合同要求：`create_legacy_note_migration_pending` 在任何 ledger INSERT/approval 前以 `char_length`（与 `QuestionSource VARCHAR(300)` 相同的字符长度语义）同时校验参数、canonical title 与锁定 live Note title，超长固定 `SOURCE_TITLE_TOO_LONG` 并走独立 manual/failed rejection 记录路径；`ready` 再次防御性检查。验收必须使用相互独立的 `lsr02_source_snapshot`、`lsr02_archive_rows`、`lsr02_archive_manifest`、disposition 与 live-source 五方关系，分别计数、哈希和双向集合绑定；replay 使用非空且等数的显式计数、FULL OUTER/双向 EXCEPT 检出缺失/多余，禁止空 INNER JOIN 通过。Note 当前非空/可空/类型矩阵是唯一规范：snapshot/archive/live/replay/owner 共用，`knowledge_points`/`tags` 为规范化非空数组，所有 required key 的 NULL/type 违规均 fail closed；ordinary Note/Blog 仍 zero ledger/target。
- 第十六次合同要求：title rejection writer 必须调用同一 owner-only `legacy_migration.canonicalize_legacy_note(UUID)` helper 锁定 live Note 并现场重算 source hash；错误 hash 为 `LEGACY_MIGRATION_SOURCE_DRIFT`，snapshot_ref 必须由重算 hash 绑定，rejection 表 CHECK 只接受 `SOURCE_TITLE_TOO_LONG`（其他 canonical/EF 错误不伪装成 title rejection）。新增独立 rolled_back replay manifest，按 source/mapping/hash、rollback actor/event/reference/hash、transition event 与 immutable audit digest 做 count、双向集合和 FULL OUTER 逐列比较；positive replay 不得过滤它。last_reviewed 全路径使用 UTC 微秒字符串，title 原样 UTF-8 保留（无 trim/blank-to-NULL/truncation，仅 QuestionSource char_length>300 gate）；16-key nonce marker 仅覆盖 ledger/events/rollback-audit，rejection 走独立 owner/session/ACL/append-only guard。仍需静态 SQL/links/diff 检查，Owner 不得自批。
- LSR-03 必须覆盖 draft-chain、EF bits、chapters/019 三类、search_vector、retained_public_only、paused→active approval、source/target duplicate/collision 与非法 state/event transition fixtures；所有 nonzero 均 fail。

LSR-02 的 `PARTIAL` 不是 G2/G3/G4 结论；schema implementation、isolated replay、runtime、browser、真实数据内容均 `NOT_VERIFIED`。
4. LSR-04 依赖 LSR-03、G1 `PASS` 和 G2 `PASS`，按 API/service、页面/导航、旧入口安全退出、旧消费者顺序逐项切换；它通过权限负向、真实浏览器/网络证据生成 G3，必要时生成 G4，再由独立 Gate Worker 对账；不得把由自身产生的 G3/G4 `PASS` 设为前置。每项有 rollback 和观察期。
5. LSR-05 只能在相应 G3/G4 `PASS` 后删除已证明零消费者且数据已迁移、备份/恢复可用的结构；普通 Note/Blog/公开内容和历史数据不得因“零旧代码”目标被删除。
6. LSR-06 只能在 LSR-05 和所有适用 Gate `PASS` 后，由独立 Reviewer/Verifier 重跑引用扫描、迁移/恢复、权限负向和架构对账；实施者不得审批自己的高风险结果。

G1 最小架构验收（冻结单一方案）：必须有完整消费者 owner/disposition 与 route matrix；`/mistakes` 使用 HTTP 308 永久 redirect `/notes`，旧 published&&!hidden Note 仅只读公开，根 `/manage` 仅普通 Note/Blog/content admin，`/manage/<workspace route>` 是私有学习写入唯一 owner；review C 阶段旧 `/api/review/*` 全部 410 + successor `/api/admin/review/items`，禁止只读分支；A/B/C 禁止双写并具备精确观察阈值和可恢复 rollback；provenance 使用强 FK ledger；QuestionKnowledgePoint 是 Question 唯一读写 owner；Attempt/provenance approval 字段链一致。G1 只判断该设计是否可进入 LSR-02，不把尚未实现或未产生的 G2/runtime 证据当作本轮 blocker；G1 未独立 PASS 前不得启动 LSR-02。

### 阶段二：七体系主链

Subject/KnowledgePoint、Question、Mistake、Review、Note、Capture、学习首页必须逐项验证 model/schema/service/router、client/hook/page、正常/空/错误/未登录/拒绝/重复提交、目标 pytest/Vitest、typecheck 和必要真实浏览器证据。任一项 `FAIL`、`BLOCKED`、`NOT_VERIFIED`，不得宣称该体系可用，也不得进入阶段三。

### 阶段三：融合

隔离环境必须完整验证 Capture→QuestionDraft→Question→MistakeDraft→Mistake→ReviewItem→ReviewRecord→Dashboard；Subject→KnowledgePoint→Question→Mistake→复习反馈；Note→关联/搜索/导航/可见性；登录→`/manage/*`→logout→严格 401；刷新/重登持久性；归档/删除的 FK/业务约束；旧 API/page/client 无意外请求；console/page error/failed request/unexpected navigation/秘密扫描无异常。jsdom 或单元测试不得替代真实 Chromium。

八条链路必须在 LSR-20～23 的 task-level acceptance 中逐条登记原始证据路径/hash：

1. LSR-20：Capture→QuestionDraft→Question→MistakeDraft→Mistake→ReviewItem→ReviewRecord→Dashboard。
2. LSR-21：Subject→KnowledgePoint→Question 关联→Mistake 继承/展示→薄弱知识点与复习反馈。
3. LSR-21：Note→KnowledgePoint/相关内容关联→搜索或导航→公开/私有可见性。
4. LSR-22：登录→`/manage/*` 私有操作→logout→严格接口 401，公开 Note/Blog 仍匿名可访问。
5. LSR-22：新版编辑、刷新、重新登录后数据保持一致。
6. LSR-23：删除/归档题目、错题、知识点时外键和业务约束不产生孤儿数据。
7. LSR-23：不存在旧 API、旧页面或旧客户端的意外网络请求。
8. LSR-23：浏览器 console、page error、failed request、unexpected navigation 与秘密值扫描无异常。

### 阶段四：收束

阶段四入口必须满足 G0、G1、G2、G3 均为 `PASS`，若实际触发 G4 则 G4 也必须为 `PASS`；非生产收束不以 G5 为前置，G5 在无生产范围时保持 `NOT_AUTHORIZED`。随后必须复核旧残留、Alembic graph/空库 replay/恢复、相关 pytest/Vitest/typecheck/build/Chromium、auth/session、公开过滤、秘密、端口、临时账户/DB/进程和 worktree；最终报告逐项列出已删除、保留、各体系、融合、迁移/回滚证据、未验证/未授权/剩余风险，并只有全部当前证据齐备时才允许 `PASS`。

## 4. 非功能与证据要求

- 严格串行：`LSR-00→01→02→03→04→05→06→10→11→12→13→14→15→16→20→21→22→23→30→31→32→33→34`；每次只执行依赖满足后的第一项。
- 角色分离：每项一个 Primary Owner；实施、Reviewer、Verifier、task-local Gate Worker 为真实独立 Persona Worker；每项必须使用唯一 task-local `worker_id` 矩阵，明确列出 Owner/Reviewer/Verifier 及每个触发 Gate 的完整 Worker 组合，并排除该项 Primary Owner 的 identity；同一 Persona 也不得复用同一 worker_id；若默认 Gate Persona 与 Owner 冲突，使用任务指定的独立替代者；统一 luna/high；Owner 不得自批。
- 每阶段一个 `validation.md` authoritative manifest、必要首次失败证据和最终汇总；禁止日志膨胀、重复正常重试和额外 `audit.md/assets`。
- 迁移必须幂等、可审计、可重跑、保留来源与版本、可恢复；不可无损字段进入 `migration_notes`/阻塞清单。
- manifest、Gate 和结论状态只允许 `PASS`、`PARTIAL`、`FAIL`、`BLOCKED`、`NOT_VERIFIED`、`NOT_AUTHORIZED`；任务进度只使用 `[x]`/`[ ]` checkbox，依赖关系用 `depends_on` 和自然语言表达。

## 5. 强制暂停条件

旧/新边界或字段无法从当前证据确定；需要生产数据/凭据/部署/公开路由切换；需要不可逆迁移或删除历史内容；dirty worktree 与目标重叠不可隔离；鉴权、可见性、完整性或回滚出现严重失败；Worker 对架构、数据或安全结论产生实质冲突；连续两次同一失败未重新检查合同和证据。任一情况必须停止，不以补丁堆叠或历史状态绕过。

## 6. 当前授权边界

本轮将授权边界推进至第十六次修订；下方旧轮次文字仅为历史记录，当前以
`legacy_migration_guard_nonces`、逐字段 ledger guard 与 rollback event hash 合同为准。

LSR-01 及既定非生产任务项已预先获执行授权；LSR-01 当前结论为 `PASS`（仅静态 mapping 验收范围、checkbox `[x]`），Reviewer=`PASS_WITH_NOTES`、QA=`PASS`、Data=`PASS`；G0=`PASS`、G1=`PASS`（Architect=`PASS`、Technical Reviewer=`PASS_WITH_NOTES`）。LSR-02 静态合同已由独立 Reviewer=`PASS_WITH_NOTES`、Verifier=`PASS` 收束为 `PASS`/`[x]`；其实现、数据库和运行验证仍须 LSR-03 与后续独立 Gates。数据库内容查询须等到任务依赖满足且仅限隔离快照；脚本、harness、原始输出和隔离附件只能在任务专属仓库外临时目录，仓库只登记路径/hash/首次失败/清理结果。若要将脚本或测试持久化进仓库，必须先在精确任务范围扩展写入授权。生产数据库/服务、真实凭据或用户数据、公开路由生产切换、不可逆操作、部署、commit/push 仍为 `NOT_AUTHORIZED`。

## R8 首错后的 seed 合同修订（2026-08-25）

R6 Owner evidence 未持久化 machine-readable synthetic seed，R8 Verifier 在空 post-026 数据库中缺少 source Note；R8 evidence 保留。新增 deterministic `backend/tests/lsr03_seed_rehearsal.py`，只写必要 synthetic users、approval authorization、rollback admin、taxonomy、source Note，固定 IDs，精确空集外 fail-closed，并输出结构化 identity/count/IDs。R9 唯一命令序列、current hashes 与 `READY_FOR_R9=NO` 见 validation.md；未改产品、model、migration 或 adapter。
