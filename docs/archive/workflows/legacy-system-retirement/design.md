# LSR-02 数据迁移合同与可逆规则（含 LSR-00/01 历史设计）

当前状态（canonical）：LSR-01=`PASS/[x]`（静态 mapping）；LSR-02=`PASS/[x]`（静态迁移合同；Reviewer=`PASS_WITH_NOTES`、Verifier=`PASS`）；LSR-03=`PARTIAL/[ ]`（当前 fresh isolated runtime=`PASS`，但独立 G2 Gate 因完整等价、rollback replay 与带数据 restore 证据缺口=`BLOCKED`）；G0/G1=`PASS`，G2 Database/Data/combined=`BLOCKED`，G3-G4=`NOT_VERIFIED`，G5=`NOT_AUTHORIZED`。本文件冻结 LSR-02 设计；LSR-03 结果以 `validation.md` 当前 manifest 为准，LSR-04 及后续未启动。

当前 LSR-03 权威运行证据为 `/Users/limengyang/.codex/attachments/lsr03-g2-fresh-final-evidence-20260825-bootstrap-fixture-admin-cwd/`。它证明 guard、fresh replay、026 idempotency、正向/负向 fixture、logical rollback、三类 actual inbound zero-mutation、pre-026 schema restore 与 cleanup 可执行；它没有改变本设计的完整 G2 验收范围。缺失项仍是逐目标 parity/visibility/orphan/ReviewRecord 断言、真实 `retained_public_only`、rollback replay/audit digest 和带合成源数据 restore，故不得把 runtime PASS 扩大成 LSR-03/G2/阶段一 PASS。

## LSR-03 重开前静态预检（2026-08-25）

这不是 LSR-03 或 G2 的重判。r2 `actual-inbound-fixture-status.md`/`SHA256SUMS` 记录的两次 setup 失败分别对应 adapter-runner 不应直接读取 ledger，以及错误使用 `target_question_draft_item_id`；当前 026 guard 与实际表夹具已静态对齐到三条入向边：`capture_items.mistake_draft_item_id`、`attempts.mistake_draft_item_id`、`mistake_drafts.attempt_id`。实际回滚 helper 的 admin session 负责 baseline/setup/zero-mutation/cleanup，adapter-runner 只调用受保护 rollback 函数并提供 identity；失败必须保留全部 ledger/inbound/attachment/audit-event 行不变，且 cleanup 计数归零。独立 `lsr03_reviewer`=`REVIEW: PASS`、`lsr03_verifier`=`VERIFY: PASS`，故静态预检 `PASS`、`READY_FOR_FRESH_REHEARSAL=YES`；总体 LSR-03/G2 状态不变。

### r3 runtime recheck result

全新 `lsr03_r3` 集群在 `127.0.0.1:55432` 启动后，首个 guarded runner 步骤因缺少 `sqlalchemy` 在导入阶段失败；未进入 URL/identity、Alembic、SQL 或 actual-table fixture。按首错合同立即停止；r3 首错、停止证明和 `SHA256SUMS` 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r3/`，r2 不被覆盖。该 runtime 结果为 `FAIL`，不改变静态预检 PASS，也不产生 LSR-03/G2 通过。

### r3 首错后的 runtime contract revision

r3 首错是历史证据，未被覆盖；r4 未启动。guarded runner 现在延迟导入 SQLAlchemy，并在任何 probe/DB 动作前要求 `sys.prefix` 与项目 `backend/.venv` 身份一致，错误解释器固定 `LSR03_PYTHON_RUNTIME_REQUIRED`/exit 64。guard/child 命令固定使用 `backend/.venv/bin/python`，unit child 仅允许 `-m pytest`，并强制 `PYTHONPATH=.`、cwd=`backend`。无数据库测试验证错误解释器在 probe/child 前退出和正确 venv identity；产品行为、模型、迁移、adapter 均未修改。

本轮 `backend/.venv` targeted guarded/static tests=`20 passed`，`py_compile` 与 `diff-check` 通过；`READY_FOR_R4=YES` 仅为未来 fresh isolated runtime recheck 条件，不是 LSR-03/G2 裁决。

### R4 fresh runtime recheck result

全新 `lsr03_r4` 集群在 `127.0.0.1:55432` 完成 guarded identity、001→026 和 paused baseline 后，首个 actual-table fixture 步骤在 `_audit_event_snapshot` 对 `legacy_migration_rollback_audits` 使用不存在的 `id` 列排序而失败。按首错合同停止；三条 actual-table setup/rollback、zero-mutation、attachment 保留与 fixture cleanup 均未到达。证据与 SHA256 manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r4/`；集群已停止且无 55432 listener。R4=`FAIL`，不改变 LSR-03/G2；fixture cleanup=`NOT_RUN`。

### R4 首错后的 no-DB revision

026 DDL 显示 `legacy_migration_rollback_audits` 的稳定主键是 `ledger_id`；helper audit snapshot 已改为按 `ledger_id` 排序，并由无数据库 structural test 绑定该 DDL、拒绝该表的 `ORDER BY id`。仅改 LSR-03 helper/test；`backend/.venv` targeted tests=`21 passed`，`py_compile`/`diff-check` 通过。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R5=YES` 仅放行未来 fresh runtime，不启动 r5，不改变 LSR-03/G2。

### R5 fresh runtime recheck result

全新 `lsr03_r5` 在 `127.0.0.1:55432` 完成 guarded identity、001→026、paused baseline、capture setup 与 rollback attempt；首个 zero-mutation 断言因 partial baseline 与 full `SELECT *` ledger snapshot 直接比较而失败。按首错合同停止；Attempt/MistakeDraft.attempt_id、后续精确错误验证、zero-mutation 完成和 cleanup 未到达。R5 evidence 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r5/`；集群已停止且无 55432 listener；fixture cleanup=`NOT_RUN`。R5=`FAIL`，不改变 LSR-03/G2。

### R5 首错后的 no-DB revision

baseline 现在只通过 SQL 定位唯一 paused ledger `id`，随后以 `_ledger_snapshot(admin, baseline_id)` 取得完整列；after 仍由 `_assert_zero_mutation` 调用同一 `_ledger_snapshot`，结构测试禁止 partial mapping 直接成为 baseline。仅改 LSR-03 helper/test；`backend/.venv` targeted tests=`22 passed`，`py_compile`/`diff-check` 通过。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R6=YES` 仅放行未来 fresh runtime，不启动 r6，不改变 LSR-03/G2。

### R6 fresh runtime recheck result

R6 在全新 `127.0.0.1:55432/lsr03_r6` 完成 001→026、paused baseline 与三条 actual-table inbound rollback。CaptureItem、Attempt、MistakeDraft.`attempt_id` 均命中精确 `LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED`；每条 ledger/audit/event/relation/attachment zero-mutation、inbound retention 和 cleanup=0 均已记录，guard/admin/adapter identity 一致。集群已停止且无 listener；证据位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r6/`。R6 runtime 成功不等于 LSR-03/G2 PASS，等待独立 runtime Reviewer/Verifier。

### R7 首错后的 runtime scheme revision

R7 首错证明 plain `postgresql://` 会绕过 asyncpg scheme 合同并触发缺失 psycopg2；runner 现只接受 `postgresql+asyncpg://`，并在 probe/child 前以固定 `LSR03_DATABASE_URL_ASYNCPG_SCHEME_REQUIRED`/exit 64 拒绝 plain scheme。无 DB 测试验证 asyncpg/psycopg2 环境合同、plain scheme fail-before-probe/child 和正确 scheme 接受；`backend/.venv` targeted tests=`24 passed`，`py_compile`/`diff-check` 通过。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R8=YES` 仅放行未来 fresh runtime，不启动 r8，不改变 LSR-03/G2。

## 1. 设计结论

本目标是一次高风险的跨边界收敛：对象所有权、数据迁移、私有/公开路由、认证、客户端消费者、AI/采集来源链和可恢复删除相互耦合。采用“先只读映射，再冻结迁移合同，再隔离演练，再逐项切换，最后删除”的单向串行设计。当前设计不是生产迁移授权，也不是对历史 PASS 的复核替代。

### 方案比较

| 方案 | 优点 | 不足/阻塞 | 结论 |
| --- | --- | --- | --- |
| A：兼容共存、只停写旧入口 | 可逆，降低一次切换风险 | 不能证明单体系，长期双消费者和数据漂移仍在 | 仅作为 LSR-01 的安全基线/回滚状态 |
| B：全量映射→隔离迁移→独立等价性→分批切换→零消费者后删除 | 可审计、可回滚、能证明数据/权限/路由边界 | 需要字段决策、隔离 PostgreSQL、真实浏览器和多重 Gate；不能偷跑 | 采用，作为本工作流唯一执行路径 |

## 2. 目标所有权与数据流

```text
Capture -> QuestionDraft ->（可创建 MistakeDraft 草稿）
QuestionDraft -> 人工确认 -> Question -> 人工确认 MistakeDraft -> Mistake -> ReviewItem
Mistake -> ReviewItem -> 0-5 评分 -> ReviewRecord -> next_review_at
Subject -> KnowledgePoint tree -> QuestionKnowledgePoint/KnowledgePointLink
Note -> Markdown/version/tag/folder/backlink -> public/private filters
以上私有学习写入均由 /manage/* + admin_session + get_current_admin 保护
```

### 2026-08-23 当前用户合同

用户原话：`以上三项同意`。该当前合同覆盖相冲突的历史决定/未决项，不代表实现或 Gate PASS：已发布且未隐藏的旧 `Note(type=mistake)` 为只读公开内容并保留 `/notes/{slug}`，关闭 `/mistakes` 聚合入口；新版 `Question/Mistake` 始终私有，旧公开 Note 与新版私有学习对象以 source/provenance 关联。旧复习只迁移当前调度状态到 `ReviewItem`，旧 SM-2 字段进入 provenance/`migration_notes`，不伪造 `ReviewRecord`，语义不明/空值为 `paused` 待人工确认。Capture 可同操作产生两类草稿，但正式转换严格先 `QuestionDraft→Question`，再人工确认 `MistakeDraft→Mistake→ReviewItem`，任何草稿不得绕过人工确认。普通 Note/Blog 保持。

这些是 LSR-01 的重查输入和 LSR-02 的映射合同；G0 已由独立 Product Architect + Senior Domain Analyst 复核为 `PASS`，G1 已由独立 Architect/Technical Reviewer 复核为 `PASS`/`PASS_WITH_NOTES`；后续仅保留实现、隔离 DB 和 runtime 证据为 `NOT_VERIFIED`。

### G1 最小架构修订合同（历史快照，已被最终 G1 结论取代）

以下是基于当前源码和 G1 findings 的保守假设，不是实现授权：

- Route owner：关闭 `/mistakes` 聚合时永久 redirect 到 `/notes`；保留 published&&!hidden 旧 Note 的 `/api/notes` 与 `/notes/{slug}` 只读公开；根 `/manage` 继续拥有普通 Note/Blog/content 管理；`/manage/*` workspace 是私有学习写入的唯一 owner。路由、导航、API、rollback 必须按匿名/admin 矩阵逐项验证。
- Review cutover 不双写：A=legacy 唯一写 owner；B=隔离 backfill/shadow、runtime 不变；C=短停写/冻结旧链，切新 client/page/API 为唯一 writer，旧 API 明确只读或 410 successor。每阶段要有 source-of-truth、读/写 owner、观察指标/失败阈值、entry/exit；rollback 恢复旧 client/router 并从已验证 backup/Note 恢复，不依赖 012/013/019/020 downgrade。
- Provenance 推荐强 FK ledger（LSR-02+G2 NEW DESIGN，`NOT_IMPLEMENTED`）：仅对 `source Note.type='mistake'` 建 row；ordinary Note/Blog 永不进入。记录 source_note_id、target question/mistake/review_item FK、source version/hash、单一 state、legacy review JSON/typed fields、migration_notes、idempotency key、audit/time；空/不明复习为 `migrated_paused`，不创建 ReviewItem，人工确认后才产生合法非空 `next_review_at`。
- `QuestionKnowledgePoint` 是 Question canonical 唯一 owner；generic `KnowledgePointLink` 不再作为 Question 权威，迁移/一致性/回滚需显式验证。Attempt 的 router/client/service 必须一致传 `attempt_id`；Draft/Capture provenance 与人工批准审计字段/时点必须可追溯。ReviewItem.mistake_id、Attempt/approval 字段均为 LSR-02+G2 NEW DESIGN，`NOT_IMPLEMENTED`。
- Recovery identity 必须包含代码/路由版本、不可变输入 hash、隔离 DB snapshot/restore identity、完整性查询和恢复后权限检查；历史 downgrade 不是主回滚。

### G1 第二轮冻结合同（历史快照，已被最终 G1 结论取代）

本节覆盖上一版方向性建议。G1 仅评合同是否足够机械、可进入 LSR-02；当前未实现、未运行、未做 G2/runtime/browser 不是本轮 G1 blocker，而是后续 `NOT_VERIFIED`。

- Consumer owner：public search/knowledge_markdown/RSS/sitemap/discover/home cards/content-routes/nav/guestbook/related public Note 全部由 `Note/Public Content owner` retained；旧 mistake aggregate/components/weak-point/recommendation/suggestions 全部由新版 private Question/Mistake/Review services replace，具体实现任务为 LSR-04/LSR-16/适用 G4。workspace search 当前是 Note 搜索（`src/app/manage/(workspace)/search` + `src/lib/api/search` + `/api/admin/search`），owner=`retained Note/Public Content admin search`，不得搜索/暴露 private Question/Mistake；未来 learning search 超出 LSR-01，新增时须独立 G1/G3/G4。import/export runtime 当前零实现/零注册，外部 GitHub/export boundary retained；任何新发现立即 `TASK-BLOCK`。
- Route：根 `/manage` 仅普通 Note/Blog/content admin，不拥有 learning writes；`/manage/<workspace route>` 是 private learning 唯一 owner。`/mistakes` 返回 308 `/notes`；`/mistakes/review` 返回 308 `/manage/review`，anonymous 随后由现有 auth boundary 处理；`/notes/{slug}` 与 `/api/notes` 保留 published&&!hidden 旧 Note read-only；public/mobile/vertical nav 移除 mistakes aggregate。`/write-mistake*` 在 C 阶段统一 410，不再写 Note。
- Review：A=legacy 唯一 writer；B=隔离 shadow、runtime 零写；C=短停写后 new client/page/API 唯一 writer，旧 `/api/review/*` 每个端点统一 410 Gone，响应 machine-readable successor=`/api/admin/review/items`，禁止只读分支。观察窗口为隔离环境写冻结、仅可回滚 synthetic transactions：3 个独立 cold-start cycles，每个关键操作至少 20 个合成样本；匿名 401/non-admin 403 是预期 PASS 单列；unexpected 4xx/5xx、旧写请求、重复、孤儿、hash drift、queue due/id/next_review_at UTC 逐行不一致、console/page/request 异常均必须为 0，任一非零立即 rollback。生产真实写/delta 另需 G5。
- Ledger：唯一推荐 `legacy_note_migrations`，DDL 见 validation；禁止无 FK 字符串关系。`review_item` canonical 改为 `mistake_id UUID FK`；旧 `target_type/target_id` 只允许过渡只读，不再写。QuestionKnowledgePoint 是唯一 Question read/write owner；generic Question links 只作迁移输入，transactional replace canonical 后停止写并在验证后删除。Attempt 的 MistakeDraftCreate client/router/service 全链传 `attempt_id` FK；Capture/Draft 记录 approval actor_id/approved_at/conversion_sequence/source_hash。
- Recovery：输入 source archive hash、route matrix hash、一次性 DB custom-format snapshot、attachment manifest、Alembic head、code identity；恢复到明确一次性 DB，验证 count/PK/hash/FK/orphan/visibility/session negative。C 冻结期间仅 synthetic writes 并记录 IDs；rollback 顺序固定为停服务→恢复 code/route artifact→restore pre-cutover snapshot→重跑 integrity/auth→确认旧 writer 唯一；不依赖 downgrade。

新版对象只能在当前模型、schema、service、router、client、hook、page、migration 和测试全部对账后被称作权威。旧对象只有在逐行映射、来源/版本、幂等、审计、回滚和零消费者证明齐备后才可退休。AI/解析输出是带来源的草稿，不是事实；任何不可无损映射字段必须进入 `migration_notes` 或阻塞清单。

## LSR-02 当前冻结合同（2026-08-24，静态合同最终收束）

本节是 LSR-02 当前设计合同；前文标为“历史快照”的内容只作输入。合同只处理 `Note.type='mistake'`。`Note.type in ('note','blog')` 不建立迁移 ledger、不创建 Question/Mistake/ReviewItem、不改变其公开/私有职责。所有迁移均指后续一次性隔离演练或经另行 Gate 批准的非生产动作；本轮没有 schema、产品代码、数据库或用户数据写入。

### 1. 来源快照与身份

每个候选源先生成不可变 canonical snapshot，再进行 target 写入。snapshot 以固定字段顺序、UTF-8、canonical JSON 保存于任务专属仓库外 immutable archive；ledger 只保存 `snapshot_ref`、`source_hash=SHA-256(canonical snapshot)`、源版本和必要 typed fields，不在工作流文档或普通日志中保存用户正文。`canonical_payload JSONB` 是 snapshot 的完整、可独立重算载荷。唯一规范 required-key 集由 8.10 的 `lsr02_required_payload_keys` 定义，且同时被 TEMP snapshot、archive manifest、adapter hash 输入和逐 key 绑定查询使用：它包含 `id,source_note_id,slug,source_url,title,content,type,status,hidden,created_at,updated_at,summary,cover,category,subject,difficulty,question,answers,analysis,knowledge_points,ef,legacy_ef_bits,interval,repetitions,next_review,last_reviewed,images,ai_metadata,folder_id,sort_order,revision,tags,search_vector_token,legacy_review_json`。其中 `answers` 是稳定对象 `{my_answer,correct_answer}`，`legacy_ef_bits` 是独立顶层 key（不是埋在 `ef` 内），`legacy_review_json` 是原始复习 JSON；`subject`、`knowledge_points`、`tags`、`images`、`ai_metadata` 的数组/对象按冻结规则序列化。canonical normalization 冻结为：JSON object key 按字典序、数组按源稳定 ID/name 排序（语义有序数组除外）、时间统一 UTC RFC3339、nullable keys 保持 JSON null、required typed keys 不得为 NULL，空字符串不转 NULL、缺失 key 不补默认；`canonical_payload::text` 使用 PostgreSQL JSONB canonical key order。`source_hash` 必须现场重算为 `pg_catalog.encode(public.digest(pg_catalog.convert_to(canonical_payload::text,'UTF8'),'sha256'),'hex')`（LSR-03 先验证 pgcrypto 前置依赖），不得信任 archive 传入 hash。hash 同时覆盖派生 `search_vector` 的 NULL-safe 稳定表达：`CASE WHEN search_vector IS NULL THEN '<NULL>' ELSE '<VALUE>' || search_vector::text END`；tags 以稳定 ID/name 排序，显式 null 也参与 hash，`ef` 与独立 `legacy_ef_bits=encode(float8send(ef),'hex')` 同时参与 hash（accepted pending rows require a finite non-null EF）。archive rows 必须逐行绑定 `(source_note_id,source_hash,canonical_payload)`；独立 archive manifest 只保存 expected hash/digest，不能只提供 aggregate hash；任何 payload 自洽但 `payload.id` 指向另一 Note 的 wrong-note 载荷都必须 FAIL。

The executable hash expression is exactly `pg_catalog.encode(public.digest(pg_catalog.convert_to(canonical_payload::text,'UTF8'),'sha256'),'hex')`; any shorter form in historical prose is not an executable alternative. The current matrix supersedes older prose that described nullable EF/interval/repetitions: the live Note model supplies these typed values by default, but a historical NULL in the live row is rejected before pending INSERT as `CANONICAL_PAYLOAD_INVALID` and returned as an adapter-level `manual|failed` outcome outside the title-rejection table; it is never represented as a ready/active snapshot. Consequently `legacy_ef_bits` is always a non-null required key for an accepted pending row, and no nullable EF branch is an acceptance path.

第十四次修订 supersedes the earlier archive shorthand: `lsr02_archive_rows`
is the independent immutable row payload carrying `(source_note_id,source_hash,
canonical_payload,legacy_review_json,source fields)`, while
`lsr02_archive_manifest` is the independent expected `(source_note_id,
expected_source_hash,expected_payload_digest)` relation. Both relations are
separately counted, set-compared, and bound to `lsr02_source_snapshot`; they are
not two names for one table.

Within that one set, `source_url` must equal the snapshot/ledger URL and is never reconstructed from a wrong slug; `legacy_review_json` is the required lossless typed/raw review object and must match the TEMP snapshot and ledger byte-for-byte after JSONB normalization; `source_note_id` is the required top-level string redundant with `id` so wrong-note binding is mechanically visible; and `legacy_ef_bits` is the required independent IEEE-754 key.
The single normative nullability/type matrix follows the current `Note` model
and pending owner contract: `id,source_note_id,slug,source_url,title,content,
type,status,hidden,created_at,updated_at,answers,knowledge_points,tags,
search_vector_token,legacy_review_json,ef,legacy_ef_bits,interval,repetitions,
revision` are non-null (`knowledge_points`/`tags` are normalized arrays, and
`ef`/interval/repetitions are numeric); `summary,cover,category,subject,
difficulty,question,analysis,next_review,last_reviewed,images,ai_metadata,
folder_id,sort_order` are nullable with one fixed type each. The same matrix is
used by owner validation, `lsr02_archive_rows`, `lsr02_archive_manifest`,
`lsr02_source_snapshot`, live Note binding, and replay; no replay query may
reintroduce a wider `number|null` or null scalar branch.
Time normalization is UTC with microseconds preserved: `to_char(value AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')`; no millisecond truncation is allowed.

源码字段归一化规则冻结为：Note `knowledge_points` TEXT 仅按当前 `_split_knowledge_points` 规则把中文逗号/顿号/换行/分号替换为逗号、trim、去空项，顺序保留；Note tags 从 `note_tags JOIN tags` 按 `(tag.id,tag.name)` 读取原名，去重/排序，不调用 AI 或 canonical cluster 猜测。canonical payload 保存归一化后的数组，同时 snapshot typed/raw 字段保留原文本/JSON，LSR-03 必须双向比较。

数据库 UUID/主键是稳定身份；slug 只是公开兼容标识，绝不代替 FK。Question/Mistake、QuestionDraft/MistakeDraft 及两枚 DraftItem target UUID 均使用 UUIDv5(namespace=`legacy-note-migration`, source_note_id, mapping_version, target-kind)；若 UUID 已存在但内容/source hash 不一致，立即 `failed`，不得覆盖。新版 target `version` 从 1 开始；旧 `revision` 只保存为 `source_revision`，不伪造编辑历史。target 时间由迁移事务产生，原时间只进入 snapshot/provenance。

`published AND hidden=FALSE AND type='mistake'` 的旧 Note 原记录保留为只读公开内容并保留 `/notes/{slug}`；新版 Question/Mistake 固定 private；`/mistakes` 关闭/308 redirect 属 LSR-04，不在 LSR-02 执行。旧 Note 与新对象通过强 FK ledger 和 QuestionSource 关联，不把 source URL 当关系。

### 2. 逐字段矩阵

矩阵中的 `target` 可为后续 schema target 或 ledger/provenance；`migration_notes` 保存规则、人工决定、未映射原因和 lossiness code。普通 Note/Blog 不进入矩阵的迁移执行队列。

| source field | target | type | normalization/default | provenance | disposition | lossiness | validation | rollback |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | ledger `source_note_id` FK | UUID→UUID | 原值 | ledger FK + snapshot | migrate (mistake only) | none | source exists, exact type | RESTRICT; retain ledger |
| `slug` | `QuestionSource.source_url=/notes/{slug}`; ledger `source_slug` | varchar(255)→URL/JSON | 原值；展示 URL encode 不改存档 | source_slug + hash | migrate/retain | none; never truncate | nonblank, route/URL check | source unchanged |
| `title` | Question/Mistake/draft title | varchar(500)→varchar(300) | preserve exact non-empty UTF-8; >300→manual（不截断） | raw snapshot | migrate/manual | length overflow retained only | target max length | atomic target rollback |
| `content` | immutable snapshot/`migration_notes`，不直接写正式学习字段 | text→archive | 原文保留；不把 content 猜作题干/解析 | snapshot_ref/hash | retain provenance | formal target 不承载正文 | archive read-back/hash | restore archive/source |
| `type` | ledger applicability；QuestionSource=`note` | string→enum | 必须 exact `mistake` | source metadata | migrate; note/blog ignore | none | allowlist | no ledger for note/blog |
| `status`,`hidden` | ledger source fields；公开判定 | string/bool→typed | 原值 | source metadata | retain/migrate | none | status allowlist/bool | source unchanged |
| `revision` | ledger `source_revision` | int→int | 原值；target version=1 | source metadata | provenance | no edit-history equivalence | `>0` | restore source/ledger |
| `created_at`,`updated_at` | snapshot/source metadata | naive datetime→JSON | 原值；target uses transaction time | snapshot | provenance | target history not recreated | parse/type | restore archive |
| `question` | Question `question_text` + `stem_md`; Mistake `question_text` | text→text | trim; blank→manual；不以 title/content 补齐 | source field/hash | migrate/manual | none when present | nonblank | atomic target rollback |
| `QuestionDraft.question_text` | deterministic QuestionDraft | text→text | exact normalized `question`; no title/content fallback | source field + source_hash + approval | draft prerequisite | draft is not fact until approval | draft status/version/source hash | rollback draft chain |
| no legacy `question_type`/`options` field | Question `question_type`/`options`/`answer_data` | absent→structured | no default type; only an explicit source/approval mapping may populate | mapping decision + raw answer | migrate/manual | absent structure is retained lossiness | current Question answer contract | no target until valid |
| `correct_answer` | Question `correct_answer` + `answer_data.value`; Mistake `correct_answer`; draft snapshot | text→text/JSON | trim；必须非空且题型/选项已明确；不推断题型 | source + mapping code | migrate/manual | unstructured answer retained; no guessed type | answer contract | atomic target rollback |
| `QuestionDraft.correct_answer` | QuestionDraft answer field | text→text/JSON | same deterministic answer mapping; no guessed type/options | source + draft approval | draft prerequisite | draft only; not formal answer | answer contract + hash | rollback draft chain |
| `analysis` | canonical Question `analysis_md`; mirror `explanation`; Mistake `analysis`; draft snapshot | text→text | trim；same normalized source；不生成解释 | duplicate-source note | migrate | mirror duplication; no semantic split claim | values/hash equal | atomic target rollback |
| `QuestionDraft.explanation` | QuestionDraft explanation field | text→text | exact normalized `analysis`; no generated explanation | source + draft approval | draft prerequisite | draft only | deterministic mirror rule | rollback draft chain |
| `MistakeDraft.question_text` | MistakeDraft question field | text→text | exact Question question text after Question conversion | Question target/source hash | draft prerequisite | copy is provenance-linked, not new fact | equals approved Question text | rollback draft chain |
| `MistakeDraft.correct_answer_snapshot` | MistakeDraft answer snapshot | text/JSON→text/JSON | exact approved Question answer snapshot | Question target + source hash | draft prerequisite | snapshot, not independent owner | equals Question deterministic answer | rollback draft chain |
| `MistakeDraft.explanation_snapshot` | MistakeDraft explanation snapshot | text→text | exact approved Question explanation mirror | Question target + source hash | draft prerequisite | snapshot, not independent owner | deterministic mirror function | rollback draft chain |
| `DraftItem.source_type` | Question/Mistake DraftItem | enum/string→enum | exact `legacy_note` | source metadata | draft prerequisite | none | allowlist includes `legacy_note` only for this adapter | rollback draft chain |
| `DraftItem.source_id` | Question/Mistake DraftItem | UUID→UUID | exact source Note UUID | source FK/hash | draft prerequisite | none | equals ledger source_note_id | rollback draft chain |
| `DraftItem.status`,`version` | DraftItem lifecycle | enum/int→typed | deterministic initial draft status; version=1 | draft audit | draft prerequisite | no legacy edit history | status/version checks | rollback draft chain |
| `DraftItem.approval` | DraftItem `approved_by/approved_at/conversion_sequence/source_hash` | mixed→typed | null until explicit approval; exact actor/time/hash/sequence | approval audit | draft prerequisite | no implicit approval | FK/time/order/hash | rollback draft chain |
| `DraftItem.target_question_id`,`target_mistake_id` | DraftItem final target links | UUID→UUID FK | Question DraftItem links Question; Mistake DraftItem links Mistake | target audit | draft/final | none when linked | strong FK and expected target kind | rollback draft chain |
| `QuestionDraft.subject_id`,`title` | QuestionDraft fields | FK/text→typed | exact approved Subject; title preserves source value/no invented value | source + approval | draft prerequisite | none if valid | Subject FK/length | rollback draft chain |
| `QuestionDraft.question_type`,`options`,`difficulty` | QuestionDraft answer metadata | enum/JSON/enum→typed | only explicit approved mapping; no default type | mapping decision + source hash | draft prerequisite/manual | unknown structure retained | answer/schema contract | rollback draft chain |
| `QuestionDraft.question_text`,`correct_answer`,`explanation` | QuestionDraft content | text→text/JSON | exact source-normalized values; no AI fill | source/hash/approval | draft prerequisite | draft not fact | nonblank/answer/mirror helper | rollback draft chain |
| `MistakeDraft.subject_id`,`title` | MistakeDraft fields | FK/text→typed | inherit approved Question Subject; title deterministic | Question/source audit | draft prerequisite | no independent subject | FK/equality | rollback draft chain |
| `MistakeDraft.reason_category`,`mistake_reason` | MistakeDraft reason | enum/text→typed | `unknown`/NULL only absent; no prose inference | raw analysis + mapping note | draft/manual | taxonomy lossiness explicit | enum/approval | rollback draft chain |
| `MistakeDraft.question_id`,`question_draft_id`,`attempt_id` | MistakeDraft source links | UUID FK→typed | before Question conversion: `question_id=NULL`, `question_draft_id=QuestionDraft.id`, `attempt_id=NULL`; after conversion exactly one question source | conversion sequence/source hash | draft→formal | source switch audited | exactly-one-of/FK | rollback draft chain |
| `MistakeDraft.question_text`,`correct_answer_snapshot`,`explanation_snapshot` | MistakeDraft snapshots | text/JSON→snapshot | exact approved Question mirrors; no second owner | Question ID + source hash | draft prerequisite | snapshot copy only | deterministic helper | rollback draft chain |
| no dedicated legacy `reason_category`/`mistake_reason` (analysis may be mixed) | Mistake `reason_category='unknown'`; `mistake_reason=NULL` unless explicitly mapped | absent→enum/text | deterministic unknown/NULL defaults; never parse/infer reason from prose | raw analysis + mapping note | migrate/manual | reason taxonomy unavailable | enum check; human mapping if required | atomic target rollback |
| `my_answer` | Mistake/draft `my_answer` | text→text | trim; blank→NULL | source field | migrate | none | nullable | atomic target rollback |
| `difficulty` | Question difficulty (`NULL→unspecified`); Mistake/draft null | enum/string→enum | exact allowlist; unknown non-null→manual | raw + decision | migrate/manual | null default explicit | target checks | atomic target rollback |
| `subject` | existing `Subject.id` | free text→int FK | trim + Unicode casefold exact match only；禁止 auto-create | raw label + chosen ID | migrate/manual | label retained | one exact Subject | no new Subject |
| `knowledge_points` | `QuestionKnowledgePoint` canonical rows；existing Mistake `KnowledgePointLink(target_type='mistake')` only derived projection | free text→int FK/projection | 不拆分/创建；仅批准的 exact label/path map；projection generated/checked from target Question QKP in same transaction | raw string + canonical IDs + projection evidence | migrate/manual | ambiguous labels not guessed | QKP subject, projection set equality, duplicate/orphan/cross-subject all zero | relation/projection rollback |
| conditional `chapter` snapshot field | existing KP path (`parent_id`) | free text→tree FK | no independent Chapter；exact existing path or human map | raw path + IDs | migrate/manual | no source chapter means N/A | same Subject/no cycle | relation rollback |
| `summary`,`category`,`cover`,`images`,`folder_id`,`sort_order` | snapshot/provenance only | mixed→JSON | raw; no category→KP/folder→Subject inference | snapshot | retain provenance | no formal equivalent | snapshot hash | restore source |
| `search_vector` (derived) | retained on old Note only; no Question/Mistake target | TSVECTOR→text/hash | never copy into private learning objects; hash as `CASE WHEN search_vector IS NULL THEN '<NULL>' ELSE '<VALUE>' || search_vector::text END` | source row + public-search parity evidence | retain/derived | no formal target equivalent | pre/post old-row/search-vector equality; rebuild only via existing public Note search mechanism with query parity | no source write; restore public-search artifact/snapshot |
| `tags` | stable tag manifest in snapshot | m:n→JSON | sort by tag ID/name；no KP creation | tag manifest | retain provenance | tag meaning not asserted | stable IDs/names | restore source |
| `ef` | ledger `legacy_ef FLOAT8` + `legacy_ef_bits CHAR(16)` + `legacy_review_json.ef` | float8→float8/bits/JSON | exact IEEE-754 value；`float8send` hex；no SM-2 conversion | typed + bit string + raw JSON | provenance only | no fixed-v1 equivalent | non-null finite value and bit replay equal; NULL is manual/failed before pending | ledger restore |
| `interval` | ReviewItem `interval_days` (active only) | int→int | exact nonnegative; no unit conversion | typed + raw JSON | active/paused | algorithm semantics not transferred | `>=0` | atomic ReviewItem rollback |
| `repetitions` | ReviewItem `repetitions` (active only) | int→int | exact nonnegative | typed + raw JSON | active/paused | no ReviewRecord history | `>=0` | atomic ReviewItem rollback |
| `next_review` | ReviewItem `next_review_at` (active only) | date→timestamptz | date-only requires declared source timezone; otherwise paused/manual | raw + timezone decision | active/paused | time-of-day not invented | valid date/UTC round trip | atomic target rollback |
| `last_reviewed` | ReviewItem `last_reviewed_at` (active only) | naive datetime→timestamptz | no declared timezone→paused/manual; null stays null | raw + timezone decision | active/paused | timezone uncertainty retained | valid instant/UTC round trip | atomic target rollback |
| `ai_metadata` | snapshot/provenance only | JSON→JSON | canonical JSON; no AI rerun | snapshot hash | provenance | AI output not verified fact | valid JSON/secret scan | restore archive |
| source/audit fields | ledger audit + QuestionSource | mixed→typed | exact source hash/version; approval only admin FK | ledger | provenance | none if present | FK/hash/approval order | state transition rollback |

矩阵的 `normalization/default` 列在下表拆开为显式 `default`，以避免把“清洗规则”和“缺省值”混为一谈：

| source field | default |
| --- | --- |
| identity/text/content/type/status/hidden/revision/timestamps | none; preserve source or route to manual |
| `title` | no default; blank is manual/rejected; no truncation |
| `question` | none; blank is manual |
| no legacy `question_type`/`options` | none; explicit mapping required |
| `correct_answer` | none; missing is manual |
| `analysis`,`my_answer` | NULL when blank |
| no dedicated reason fields | `reason_category='unknown'`; `mistake_reason=NULL` |
| `difficulty` | Question=`unspecified` only when source NULL; Mistake/draft=NULL |
| `subject`,`knowledge_points`,`chapter` | none; no auto-create |
| `summary`,`category`,`cover`,`images`,`folder_id`,`sort_order`,`tags`,`ai_metadata` | provenance-only; no formal target default |
| `search_vector` | derived/retained on old Note; no private-target default |
| `ef` | none; preserve exact value |
| `interval`,`repetitions` | none; active mapping requires valid nonnegative source |
| `next_review`,`last_reviewed` | none; missing/ambiguous means paused/manual |
| source/audit | `manual_review_required=TRUE`; state drives lifecycle |

#### Draft schema delta and source-switch contract (LSR-02 design, not current schema)

The migration adapter requires the following explicit delta; these are implementation inputs for LSR-03/G2 and must not be described as existing fields:

| object | required delta / field contract |
| --- | --- |
| `DraftItem` | `source_type` enum expands to include exact `legacy_note`; `source_id UUID` points to the legacy Note; `status` is frozen as `draft|approved|converted`, `version`, `approved_by UUID FK users.id`, `approved_at TIMESTAMPTZ`, `conversion_sequence INT CHECK (>0)`, `source_hash CHAR(64)` are typed/audited; `target_question_id` or `target_mistake_id` records the formal target according to draft kind, with exactly one expected target kind. |
| `QuestionDraft` | `subject_id`, `title`, `question_type`, `options`, `difficulty`, `question_text`, `correct_answer`, `explanation`; each value is the deterministic source mapping and remains editable draft data until approval. |
| `MistakeDraft` | `subject_id`, `title`, `reason_category`, `mistake_reason`, `question_id`, `question_draft_id`, `attempt_id`, `question_text`, `correct_answer_snapshot`, `explanation_snapshot`; `attempt_id` is NULL for this legacy import and snapshots are provenance-linked copies, not a second Question owner. |
| legacy dual-draft creation | `QuestionDraftItem.source_type='legacy_note'`, `MistakeDraftItem.source_type='legacy_note'`; both `source_id=source_note_id`, approval fields initially NULL; before formal Question conversion `MistakeDraft.question_draft_id=the corresponding QuestionDraft.id`, `question_id=NULL`, `attempt_id=NULL`. |
| post-Question conversion | in the same SERIALIZABLE transaction, after Question is created, set `MistakeDraft.question_id=target_question_id` and clear `MistakeDraft.question_draft_id`; the invariant is exactly-one-of(`question_id`,`question_draft_id`). Only after separate human Mistake approval may the adapter create Mistake and (active only) ReviewItem. |

The field matrix rows above are authoritative for normalization/provenance/lossiness; this table is the required schema delta and source-switch invariant. A paused row retains the two draft chains and formal Question/Mistake but never creates ReviewItem until a new approval event.
DraftItem is the canonical audit carrier for both Draft rows: its source/status/version/approval actor-time/sequence/hash and target FK must be present; QuestionDraft/MistakeDraft are reachable only through their DraftItem FK and cannot carry an unlinked approval or source identity.

`Question.question_text`/`stem_md`、`correct_answer`/`answer_data.value` 和 `analysis_md`/`explanation` 的复制是显式 compatibility mapping，不表示旧 Note 具有新版题型语义。正式 Question 只有在 `question_type/options/answer_data` 满足当前 schema contract 且人工/明确来源已确认时创建；否则 `manual_mapping`，不得以 `short_answer` 默认掩盖未知。`ReviewRecord` 禁止由本矩阵创建。

`essay`/长文本题型没有本合同认可的 deterministic mirror；adapter 对该题型固定返回 `ESSAY_MANUAL_REQUIRED`，进入 `manual_mapping`，不自动创建正式 Question/Mistake/ReviewItem。LSR-03 必须有 essay fixture 验证拒绝、零 target 和完整 source hash/audit 保留。

### 3. 隔离队列与判定

| queue/disposition | 必须满足 | target 结果 | 失败/人工信号 |
| --- | --- | --- | --- |
| `migrate active` / `migrated_active` | exact Subject/KP；question、answer、题型合法；source hash；schedule 字段齐全且 timezone 可证明；无 collision/cross-subject | Question DraftItem + QuestionDraft + Question + QuestionSource + QKP + Mistake DraftItem + MistakeDraft + Mistake + ReviewItem(active)；旧公开源仍只读 | 任一 invariant nonzero→rollback |
| `migrate paused` / `migrated_paused` | Question/Mistake 可正式建立，但 review 缺失/日期或 timezone ambiguous | Question DraftItem + QuestionDraft + Question + QSource + QKP + Mistake DraftItem + MistakeDraft + Mistake；不建 ReviewItem；manual flag | 人工补齐后同事务创建 ReviewItem；不生成 ReviewRecord |
| `retained_public_only` | 仅 published&&!hidden；正式 mapping 不可完成；批准保留公开源 | 无 target；只建 ledger | hidden/draft 不得用此状态；需新决定 |
| `manual_mapping` | missing question/answer/type/Subject/KP/chapter、超长、跨 Subject、invalid/ambiguous date、duplicate candidate | 不建正式 target；`pending_mapping` | 人工明确后新 approval；不使用 AI |
| `failed` | hash mismatch、FK/integrity error、UUID collision with different hash、archive/transaction error | target 全回滚，保留 failure ledger | only `failed→pending_mapping` retry；同错两次停下重查 |

缺 Question 不能用 title/content 补齐；缺 Subject/KP 不能自动创建；缺 answer/type/options 不建 Question；duplicate content 不自动去重，source UUID 不同则分别确认；slug 已由 source Notes unique 保护，但 target ref/URL 冲突即 failed；invalid date、无 timezone `last_reviewed`、date-only `next_review` 为 paused/manual；Note Subject 与 KP Subject 不一致为 manual/failed。普通 Note/Blog 是 `out_of_scope_retained`，zero ledger/target rows。

### 4. `QuestionSource.source_ref` 冲突方案

当前 `QuestionSource.source_ref` 是 `String(64)`、`QuestionSource.source_title` 是 `String(300)`，而 Note.title 可达 500。扩到 500 需额外 schema/index/rollback 变更；截断会丢 provenance；故选 bounded token：`source_ref='legacy-note:' || lower(source_note_id)`（<64），完整 slug/URL 在 ledger `source_slug`、snapshot 和 `source_url`。`source_type='note'`、`source_title=title`；超过 300 的 title 固定 `SOURCE_TITLE_TOO_LONG`，转 manual/failed，不截断。`source_note` 冻结为只含 provenance/mirror metadata 的 JSONB（source UUID/slug/title/URL/hash 与 deterministic `mirror_contract`，不含未经授权正文）。LSR-03 必须验证 token 长度、hash、URL、title 和 source ID 一致；扩列不能在迁移中隐式发生。

`QuestionSource.source_title` is `String(300)` while Note.title is `String(500)`; a title over 300 is `SOURCE_TITLE_TOO_LONG` and enters manual/failed, never truncation. The full title remains in ledger/snapshot provenance.

Title normalization is singular: the raw non-empty Note title is preserved
byte-for-byte as UTF-8 in the live binding, canonical payload, snapshot,
archive, ledger provenance, and rejection writer. No `trim`, blank-to-NULL
conversion, or truncation is permitted. `char_length(title) > 300` is only the
`QuestionSource VARCHAR(300)` migration gate. `btrim` may reject an
all-whitespace API argument, but never changes the stored title or its hash.

The owner `create_legacy_note_migration_pending` checks `p_source_title`, the
canonical payload title, and the locked live Note title with `char_length` before
any ledger INSERT or approval. A title over 300 raises the fixed
`SOURCE_TITLE_TOO_LONG` error. The adapter catches that error inside its
`SERIALIZABLE` source-lock transaction and writes an immutable
`legacy_note_migration_rejections` record through a separate owner-only rejection
writer (`source_note_id`, `mapping_version`, source hash, full title, snapshot
reference, reason=`SOURCE_TITLE_TOO_LONG`, disposition=`manual|failed`, all target IDs
NULL); it never calls the pending/approval path. The rejection is excluded from
final success and its independent fixture verifies no ready/retained target is
created. `transition(...,'ready',...)` repeats the ledger/live title check.

The rejection path is an explicit audit relation, not an implicit failed ledger:

```sql
CREATE TABLE public.legacy_note_migration_rejections (
  id UUID PRIMARY KEY, source_note_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE RESTRICT,
  mapping_version VARCHAR(64) NOT NULL, source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
  snapshot_ref VARCHAR(255) NOT NULL, source_title VARCHAR(500) NOT NULL,
  reason VARCHAR(64) NOT NULL CHECK (reason IN ('SOURCE_TITLE_TOO_LONG')),
  disposition VARCHAR(16) NOT NULL CHECK (disposition IN ('manual','failed')),
  migration_notes JSONB NOT NULL CHECK (jsonb_typeof(migration_notes)='array'),
  created_at TIMESTAMPTZ NOT NULL,
  idempotency_key VARCHAR(128) NOT NULL,
  actor_id UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  UNIQUE (source_note_id,mapping_version,idempotency_key),
  UNIQUE (source_note_id,mapping_version,source_hash,reason)
);
ALTER TABLE public.legacy_note_migration_rejections OWNER TO legacy_migration_owner;
REVOKE ALL ON public.legacy_note_migration_rejections FROM PUBLIC, app_role,
  legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
GRANT SELECT, INSERT ON public.legacy_note_migration_rejections TO legacy_migration_owner;

CREATE FUNCTION legacy_migration.guard_legacy_note_migration_rejection()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
SET search_path=pg_catalog,legacy_migration
AS $$
BEGIN
  IF TG_OP IN ('UPDATE','DELETE','TRUNCATE') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_IMMUTABLE';
  END IF;
  IF TG_OP='INSERT' AND
     (current_user IS DISTINCT FROM 'legacy_migration_owner'
      OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_DIRECT_INSERT_REJECTED';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER legacy_note_migration_rejections_immutable
  BEFORE INSERT OR UPDATE OR DELETE ON public.legacy_note_migration_rejections
  FOR EACH ROW EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_rejection();
CREATE TRIGGER legacy_note_migration_rejections_no_truncate
  BEFORE TRUNCATE ON public.legacy_note_migration_rejections
  FOR EACH STATEMENT EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_rejection();
REVOKE ALL ON FUNCTION legacy_migration.guard_legacy_note_migration_rejection()
  FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
ALTER FUNCTION legacy_migration.guard_legacy_note_migration_rejection()
  OWNER TO legacy_migration_owner;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON public.legacy_note_migration_rejections
  FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;

CREATE FUNCTION legacy_migration.record_legacy_note_migration_rejection(
  p_rejection_id UUID, p_source_note_id UUID, p_mapping_version TEXT,
  p_source_hash TEXT, p_source_title TEXT, p_disposition TEXT,
  p_reason TEXT, p_snapshot_ref TEXT, p_idempotency_key TEXT,
  p_actor_id UUID
) RETURNS public.legacy_note_migration_rejections
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE
  v_note public.notes%ROWTYPE;
  v_existing public.legacy_note_migration_rejections%ROWTYPE;
  v_live_payload JSONB;
  v_live_hash CHAR(64);
  v_hash CHAR(64);
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED';
  END IF;
  IF p_rejection_id IS NULL OR p_source_note_id IS NULL OR p_mapping_version IS NULL
     OR btrim(p_mapping_version)='' OR octet_length(p_mapping_version)>64
     OR p_source_title IS NULL OR char_length(p_source_title)>500
     OR p_disposition IS NULL OR p_reason IS NULL OR p_snapshot_ref IS NULL
     OR btrim(p_snapshot_ref)='' OR octet_length(p_snapshot_ref)>255
     OR p_idempotency_key IS NULL OR btrim(p_idempotency_key)=''
     OR octet_length(p_idempotency_key)>128 OR p_actor_id IS NULL THEN
    RAISE EXCEPTION 'INVALID_REASON_OR_REQUIRED_PARAMETER';
  END IF;
  IF p_source_hash IS NULL OR octet_length(p_source_hash) <> 64
     OR p_source_hash !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_HASH_INVALID';
  END IF;
  v_hash := p_source_hash::CHAR(64);
  IF p_snapshot_ref IS DISTINCT FROM ('sha256:' || lower(p_source_hash)) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SNAPSHOT_REF_INVALID';
  END IF;
  IF p_disposition NOT IN ('manual','failed') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_DISPOSITION_INVALID';
  END IF;
  IF p_reason <> 'SOURCE_TITLE_TOO_LONG' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_REASON_INVALID';
  END IF;
  SELECT * INTO v_note FROM public.notes WHERE id=p_source_note_id FOR UPDATE;
  IF NOT FOUND OR v_note.type IS DISTINCT FROM 'mistake' THEN
    RAISE EXCEPTION 'SOURCE_TYPE_NOT_MISTAKE';
  END IF;
  v_live_payload := legacy_migration.canonicalize_legacy_note(p_source_note_id);
  v_live_hash := pg_catalog.encode(pg_catalog.digest(
    pg_catalog.convert_to(v_live_payload::text,'UTF8'),'sha256'),'hex');
  IF v_live_hash IS DISTINCT FROM v_hash THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_DRIFT';
  END IF;
  IF p_snapshot_ref IS DISTINCT FROM ('sha256:' || lower(v_live_hash::text)) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SNAPSHOT_REF_INVALID';
  END IF;
  IF v_note.title IS NULL OR char_length(v_note.title) <= 300
     OR p_source_title IS DISTINCT FROM v_note.title THEN
    RAISE EXCEPTION 'SOURCE_TITLE_TOO_LONG';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM public.users u WHERE u.id=p_actor_id)
     OR NOT EXISTS (SELECT 1 FROM public.legacy_migration_approval_authorizations a
                    WHERE a.user_id=p_actor_id AND a.approval_kind='source' AND a.enabled=TRUE) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_ACTOR_NOT_AUTHORIZED';
  END IF;
  SELECT * INTO v_existing
    FROM public.legacy_note_migration_rejections
   WHERE source_note_id=p_source_note_id AND mapping_version=p_mapping_version
     AND idempotency_key=p_idempotency_key
   FOR UPDATE;
  IF FOUND THEN
    IF v_existing.source_hash IS DISTINCT FROM v_hash
       OR v_existing.source_title IS DISTINCT FROM p_source_title
       OR v_existing.disposition IS DISTINCT FROM p_disposition
       OR v_existing.reason IS DISTINCT FROM p_reason
       OR v_existing.snapshot_ref IS DISTINCT FROM p_snapshot_ref
       OR v_existing.actor_id IS DISTINCT FROM p_actor_id
       OR v_existing.id IS DISTINCT FROM p_rejection_id THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_IDEMPOTENCY_CONFLICT';
    END IF;
    RETURN v_existing;
  END IF;
  INSERT INTO public.legacy_note_migration_rejections
    (id,source_note_id,mapping_version,source_hash,snapshot_ref,source_title,
     reason,disposition,migration_notes,created_at,idempotency_key,actor_id)
  VALUES
    (p_rejection_id,p_source_note_id,p_mapping_version,v_hash,p_snapshot_ref,p_source_title,
     p_reason,p_disposition,'["SOURCE_TITLE_TOO_LONG"]'::jsonb,now(),p_idempotency_key,p_actor_id)
  RETURNING * INTO v_existing;
  RETURN v_existing;
EXCEPTION WHEN unique_violation THEN
  RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_IDEMPOTENCY_CONFLICT';
END;
$$;
REVOKE ALL ON FUNCTION legacy_migration.record_legacy_note_migration_rejection(
  UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID)
  FROM PUBLIC, app_role, legacy_note_verifier, legacy_note_adapter_runner;
GRANT EXECUTE ON FUNCTION legacy_migration.record_legacy_note_migration_rejection(
  UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID)
  TO legacy_note_adapter;
ALTER FUNCTION legacy_migration.record_legacy_note_migration_rejection(
  UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID)
  OWNER TO legacy_migration_owner;
```

The owner-only rejection writer validates the same source lock, calls the
shared live canonicalizer, recomputes the lowercase 64-hex hash from that
payload, and then validates the hash-derived snapshot reference, full title and
reason/disposition pair before one INSERT; it is the only permitted writer.
The rejection table intentionally permits only `SOURCE_TITLE_TOO_LONG`; null or
non-finite canonical fields are rejected by the pending owner path with their
closed error and are not fabricated as title-rejection rows. A title rejection therefore has a
durable manual/failed audit row even though no `legacy_note_migrations` row can
exist before the pending function's guarded INSERT.

The sixteen-key nonce marker registry is scoped only to guarded ledger,
migration-event, and rollback-audit DML. The rejection writer does not set or
consume that marker; it is protected by its SECURITY DEFINER owner/current-user
and adapter-session checks, exact-function ACL, table ACL, and append-only
rejection trigger. Direct rejection-table INSERT/UPDATE/DELETE/TRUNCATE is
forbidden even when a caller can set the marker GUC.

### 5. `legacy_note_migrations` DDL/state/provenance（设计，不是当前 schema）

QuestionSource provenance additionally carries the exact `mapping_version`; source-ref validation therefore binds source UUID, slug, URL, hash, and mapping version together.

采用冻结的 PostgreSQL typed enum，并以不可变 allowlist 表管理 transition；新增状态必须显式新 mapping version/DDL 评审，不得通过字符串或 direct UPDATE 绕过。核心 DDL：

```sql
CREATE TYPE public.legacy_note_migration_state AS ENUM
  ('pending_mapping','ready','migrated_active','migrated_paused',
   'retained_public_only','failed','rolled_back');

CREATE TABLE public.legacy_note_migrations (
  id UUID PRIMARY KEY,
  source_note_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE RESTRICT,
  source_slug VARCHAR(255) NOT NULL, source_title VARCHAR(500) NOT NULL, source_url VARCHAR(500) NOT NULL,
  source_status VARCHAR(20) NOT NULL,
  source_hidden BOOLEAN NOT NULL, source_revision INTEGER NOT NULL CHECK (source_revision > 0),
  source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
  snapshot_ref VARCHAR(255) NOT NULL, mapping_version VARCHAR(64) NOT NULL,
  idempotency_key VARCHAR(128) NOT NULL,
  target_question_id UUID NULL REFERENCES public.questions(id) ON DELETE RESTRICT,
  target_question_source_id UUID NULL REFERENCES public.question_sources(id) ON DELETE RESTRICT,
  target_qkp_ids INTEGER[] NULL,
  target_mistake_id UUID NULL REFERENCES public.mistakes(id) ON DELETE RESTRICT,
  target_projection_ids INTEGER[] NULL,
  target_review_item_id UUID NULL REFERENCES public.review_items(id) ON DELETE RESTRICT,
  target_question_draft_item_id UUID NULL REFERENCES public.draft_items(id) ON DELETE RESTRICT,
  target_question_draft_id UUID NULL REFERENCES public.question_drafts(id) ON DELETE RESTRICT,
  target_mistake_draft_item_id UUID NULL REFERENCES public.draft_items(id) ON DELETE RESTRICT,
  target_mistake_draft_id UUID NULL REFERENCES public.mistake_drafts(id) ON DELETE RESTRICT,
  state public.legacy_note_migration_state NOT NULL,
  target_bundle_hash CHAR(64) NULL CHECK (target_bundle_hash IS NULL OR target_bundle_hash ~ '^[0-9a-f]{64}$'),
  manual_review_required BOOLEAN NOT NULL DEFAULT TRUE,
  legacy_ef DOUBLE PRECISION NOT NULL CHECK (legacy_ef::text NOT IN ('NaN','Infinity','-Infinity')),
  legacy_ef_bits CHAR(16) NOT NULL CHECK (legacy_ef_bits ~ '^[0-9a-f]{16}$'),
  legacy_interval INTEGER NOT NULL CHECK (legacy_interval >= 0),
  legacy_repetitions INTEGER NOT NULL CHECK (legacy_repetitions >= 0),
  legacy_next_review DATE NULL, legacy_last_reviewed TIMESTAMP NULL,
  mapped_next_review_at TIMESTAMPTZ NULL,
  mapped_last_reviewed_at TIMESTAMPTZ NULL,
  legacy_review_json JSONB NOT NULL,
  migration_notes JSONB NOT NULL CHECK (jsonb_typeof(migration_notes) = 'array'),
  -- approval identities are intentionally separate; `approved_by/at` is the source-ledger alias only
  approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  approved_at TIMESTAMPTZ NULL,
  source_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  source_approved_at TIMESTAMPTZ NULL,
  source_approval_sequence INTEGER NULL CHECK (source_approval_sequence > 0),
  question_conversion_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  question_conversion_approved_at TIMESTAMPTZ NULL,
  question_conversion_sequence INTEGER NULL CHECK (question_conversion_sequence > 0),
  mistake_conversion_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  mistake_conversion_approved_at TIMESTAMPTZ NULL,
  mistake_conversion_sequence INTEGER NULL CHECK (mistake_conversion_sequence > 0),
  schedule_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  schedule_approved_at TIMESTAMPTZ NULL,
  schedule_approval_sequence INTEGER NULL CHECK (schedule_approval_sequence > 0),
  rollback_actor_id UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  rollback_reference CHAR(64) NULL CHECK (rollback_reference IS NULL OR rollback_reference ~ '^[0-9a-f]{64}$'),
  source_approval_event_id UUID NULL, question_approval_event_id UUID NULL,
  mistake_approval_event_id UUID NULL, schedule_approval_event_id UUID NULL,
  transition_event_id UUID NULL, rollback_event_id UUID NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source_note_id, mapping_version), UNIQUE (idempotency_key),
  UNIQUE (target_question_id), UNIQUE (target_question_source_id), UNIQUE (target_mistake_id), UNIQUE (target_review_item_id),
  UNIQUE (target_question_draft_item_id), UNIQUE (target_question_draft_id),
  UNIQUE (target_mistake_draft_item_id), UNIQUE (target_mistake_draft_id),
  CONSTRAINT legacy_note_migration_state_shape CHECK (
    (
      state IN ('pending_mapping','failed')
      AND target_question_id IS NULL AND target_question_source_id IS NULL
      AND target_qkp_ids IS NULL AND target_mistake_id IS NULL
      AND target_projection_ids IS NULL AND target_review_item_id IS NULL
      AND target_question_draft_item_id IS NULL AND target_question_draft_id IS NULL
      AND target_mistake_draft_item_id IS NULL AND target_mistake_draft_id IS NULL
      AND target_bundle_hash IS NULL AND rollback_reference IS NULL
      AND manual_review_required = TRUE
      AND mapped_next_review_at IS NULL
      AND approved_by IS NULL AND approved_at IS NULL
      AND source_approved_by IS NULL AND source_approved_at IS NULL
      AND source_approval_sequence IS NULL
      AND question_conversion_approved_by IS NULL AND question_conversion_approved_at IS NULL
      AND question_conversion_sequence IS NULL
      AND mistake_conversion_approved_by IS NULL AND mistake_conversion_approved_at IS NULL
      AND mistake_conversion_sequence IS NULL
      AND schedule_approved_by IS NULL AND schedule_approved_at IS NULL
      AND schedule_approval_sequence IS NULL AND rollback_actor_id IS NULL
      AND source_approval_event_id IS NULL AND question_approval_event_id IS NULL
      AND mistake_approval_event_id IS NULL AND schedule_approval_event_id IS NULL
      AND rollback_event_id IS NULL
    ) OR (
      state = 'ready'
      AND source_approved_by IS NOT NULL AND source_approved_at IS NOT NULL
      AND approved_by IS NOT DISTINCT FROM source_approved_by
      AND approved_at IS NOT DISTINCT FROM source_approved_at
      AND source_approval_event_id IS NOT NULL
      AND source_approval_sequence IS NOT NULL
      AND question_conversion_approved_by IS NULL AND question_conversion_approved_at IS NULL
      AND question_conversion_sequence IS NULL
      AND mistake_conversion_approved_by IS NULL AND mistake_conversion_approved_at IS NULL
      AND mistake_conversion_sequence IS NULL
      AND schedule_approved_by IS NULL AND schedule_approved_at IS NULL
      AND schedule_approval_sequence IS NULL
      AND rollback_actor_id IS NULL AND rollback_event_id IS NULL
      AND manual_review_required = TRUE AND mapped_next_review_at IS NULL
      AND target_question_id IS NULL AND target_question_source_id IS NULL
      AND target_qkp_ids IS NULL AND target_mistake_id IS NULL
      AND target_projection_ids IS NULL AND target_review_item_id IS NULL
      AND target_question_draft_item_id IS NULL AND target_question_draft_id IS NULL
      AND target_mistake_draft_item_id IS NULL AND target_mistake_draft_id IS NULL
      AND target_bundle_hash IS NULL AND rollback_reference IS NULL
    ) OR (
      state = 'migrated_active'
      AND source_approved_by IS NOT NULL AND source_approved_at IS NOT NULL
      AND question_conversion_approved_by IS NOT NULL AND question_conversion_approved_at IS NOT NULL
      AND mistake_conversion_approved_by IS NOT NULL AND mistake_conversion_approved_at IS NOT NULL
      AND schedule_approved_by IS NOT NULL AND schedule_approved_at IS NOT NULL
      AND question_conversion_sequence IS NOT NULL AND mistake_conversion_sequence IS NOT NULL
      AND schedule_approval_sequence IS NOT NULL
      AND source_approval_event_id IS NOT NULL AND question_approval_event_id IS NOT NULL
      AND source_approval_sequence IS NOT NULL
      AND mistake_approval_event_id IS NOT NULL AND schedule_approval_event_id IS NOT NULL
      AND manual_review_required = FALSE
      AND target_question_id IS NOT NULL AND target_question_source_id IS NOT NULL
      AND target_qkp_ids IS NOT NULL AND cardinality(target_qkp_ids) > 0
      AND target_mistake_id IS NOT NULL AND target_projection_ids IS NOT NULL
      AND cardinality(target_projection_ids) > 0 AND target_review_item_id IS NOT NULL
      AND target_question_draft_item_id IS NOT NULL AND target_question_draft_id IS NOT NULL
      AND target_mistake_draft_item_id IS NOT NULL AND target_mistake_draft_id IS NOT NULL
      AND target_bundle_hash IS NOT NULL AND mapped_next_review_at IS NOT NULL
      AND rollback_reference IS NULL
    ) OR (
      state = 'migrated_paused'
      AND source_approved_by IS NOT NULL AND source_approved_at IS NOT NULL
      AND question_conversion_approved_by IS NOT NULL AND question_conversion_approved_at IS NOT NULL
      AND mistake_conversion_approved_by IS NOT NULL AND mistake_conversion_approved_at IS NOT NULL
      AND question_conversion_sequence IS NOT NULL AND mistake_conversion_sequence IS NOT NULL
      AND source_approval_event_id IS NOT NULL AND question_approval_event_id IS NOT NULL
      AND source_approval_sequence IS NOT NULL
      AND mistake_approval_event_id IS NOT NULL
      AND manual_review_required = TRUE
      AND target_question_id IS NOT NULL AND target_question_source_id IS NOT NULL
      AND target_qkp_ids IS NOT NULL AND cardinality(target_qkp_ids) > 0
      AND target_mistake_id IS NOT NULL AND target_projection_ids IS NOT NULL
      AND cardinality(target_projection_ids) > 0 AND target_review_item_id IS NULL
      AND target_question_draft_item_id IS NOT NULL AND target_question_draft_id IS NOT NULL
      AND target_mistake_draft_item_id IS NOT NULL AND target_mistake_draft_id IS NOT NULL
      AND target_bundle_hash IS NOT NULL AND rollback_reference IS NULL
      AND mapped_next_review_at IS NULL
    ) OR (
      state = 'retained_public_only'
      AND source_status = 'published' AND source_hidden = FALSE
      AND source_approved_by IS NOT NULL AND source_approved_at IS NOT NULL
      AND approved_by IS NOT DISTINCT FROM source_approved_by
      AND approved_at IS NOT DISTINCT FROM source_approved_at
      AND source_approval_event_id IS NOT NULL
      AND source_approval_sequence IS NOT NULL
      AND question_conversion_approved_by IS NULL AND question_conversion_approved_at IS NULL
      AND question_conversion_sequence IS NULL
      AND mistake_conversion_approved_by IS NULL AND mistake_conversion_approved_at IS NULL
      AND mistake_conversion_sequence IS NULL
      AND schedule_approved_by IS NULL AND schedule_approved_at IS NULL
      AND schedule_approval_sequence IS NULL
      AND rollback_actor_id IS NULL AND rollback_event_id IS NULL
      AND manual_review_required = TRUE AND mapped_next_review_at IS NULL
      AND question_conversion_approved_by IS NULL AND question_conversion_approved_at IS NULL
      AND question_conversion_sequence IS NULL
      AND mistake_conversion_approved_by IS NULL AND mistake_conversion_approved_at IS NULL
      AND mistake_conversion_sequence IS NULL
      AND schedule_approved_by IS NULL AND schedule_approved_at IS NULL
      AND schedule_approval_sequence IS NULL
      AND rollback_actor_id IS NULL AND rollback_event_id IS NULL
      AND target_question_id IS NULL AND target_question_source_id IS NULL
      AND target_qkp_ids IS NULL AND target_mistake_id IS NULL
      AND target_projection_ids IS NULL AND target_review_item_id IS NULL
      AND target_question_draft_item_id IS NULL AND target_question_draft_id IS NULL
      AND target_mistake_draft_item_id IS NULL AND target_mistake_draft_id IS NULL
      AND target_bundle_hash IS NULL AND rollback_reference IS NULL
    ) OR (
      state = 'rolled_back'
      AND rollback_reference IS NOT NULL AND rollback_reference ~ '^[0-9a-f]{64}$'
      AND rollback_actor_id IS NOT NULL
      AND rollback_event_id IS NOT NULL
      AND approved_by IS NULL AND approved_at IS NULL
      AND source_approved_by IS NULL AND source_approved_at IS NULL
      AND source_approval_sequence IS NULL
      AND question_conversion_approved_by IS NULL AND question_conversion_approved_at IS NULL
      AND question_conversion_sequence IS NULL
      AND mistake_conversion_approved_by IS NULL AND mistake_conversion_approved_at IS NULL
      AND mistake_conversion_sequence IS NULL
      AND schedule_approved_by IS NULL AND schedule_approved_at IS NULL
      AND schedule_approval_sequence IS NULL
      AND source_approval_event_id IS NULL AND question_approval_event_id IS NULL
      AND mistake_approval_event_id IS NULL AND schedule_approval_event_id IS NULL
      AND target_question_id IS NULL AND target_question_source_id IS NULL
      AND target_qkp_ids IS NULL AND target_mistake_id IS NULL
      AND target_projection_ids IS NULL AND target_review_item_id IS NULL
      AND target_question_draft_item_id IS NULL AND target_question_draft_id IS NULL
      AND target_mistake_draft_item_id IS NULL AND target_mistake_draft_id IS NULL
      AND target_bundle_hash IS NULL
      AND manual_review_required = TRUE AND mapped_next_review_at IS NULL
    )
  )
);
CREATE INDEX idx_legacy_note_migrations_state ON public.legacy_note_migrations (state, updated_at);
CREATE INDEX idx_legacy_note_migrations_source_hash ON public.legacy_note_migrations (source_hash);
```

Clarification: pending creation writes every typed legacy review field from the locked canonical payload. It initializes `manual_review_required=TRUE`; date-only `next_review` yields `mapped_next_review_at=NULL`, while a canonical UTC `last_reviewed` may populate `mapped_last_reviewed_at`. `migrated_paused` keeps manual=true and no mapped next instant; it may carry a separately recorded schedule approval while it has no ReviewItem. Only the paused/ready→active transition may change manual TRUE→FALSE, and only with an explicit UTC mapped-next instant plus an active `ReviewItem` using `fixed_interval_v1`.

Checks: `ready` requires source approval (`source_approved_by/at`, mirrored by legacy `approved_by/at`), `manual_review_required=TRUE`, mapped-next NULL, and all target columns/arrays/hash NULL; `migrated_active` additionally requires distinct question/mistake conversion approvals and schedule approval with strictly positive sequences, active `ReviewItem.state='active'` + `algorithm='fixed_interval_v1'`, mapped-next non-NULL, and `manual_review_required=false`; `migrated_paused` requires source/question/mistake approvals and sequences, review NULL, mapped-next NULL, and manual=true; a schedule approval may be recorded while paused and is consumed by paused→active; `retained_public_only` requires all target columns/arrays/hash NULL, source published&&!hidden, source approval, manual=true and mapped-next NULL; `rolled_back` requires rollback reference plus an independently authorized rollback actor, manual=true and mapped-next NULL. `pending_mapping|failed` targets all NULL and retain manual=true. Allowed transitions only: `pending_mapping→ready|failed|retained_public_only`; `ready→migrated_active|migrated_paused|failed`; `migrated_paused→migrated_active|rolled_back`; `migrated_active→rolled_back`; `failed→pending_mapping`; retained/rolled_back terminal. Source hash/snapshot/source fields/mapping version and typed legacy values are immutable after pending creation; only the governed active transition may change manual/mapped schedule fields, and all other paths are rejected by the ledger guard. Every transition records its actor/time/reason/details and approval kind in append-only events, with later reasons only in event details.

`ReviewItem` successor contract is canonical `mistake_id UUID NOT NULL FK mistakes.id ON DELETE RESTRICT`, unique; current `target_type/target_id` is legacy and read-only during separately approved cutover. If LSR-03 finds the FK absent, it is schema `NOT_VERIFIED/TASK-BLOCK`; LSR-02 does not claim it exists. `QuestionKnowledgePoint` is the sole Question relation owner; generic `KnowledgePointLink` is not a second authority. Ledger transaction asserts `mistakes.question_id=target_question_id`, `review_items.mistake_id=target_mistake_id`, and Subject/KP agreement.

Attempt/Capture contract: existing `MistakeDraft.attempt_id` remains nullable unique FK `attempts.id ON DELETE RESTRICT`; non-null requires matching `attempt.question_id` and draft link. Capture dual-draft provenance must carry `source_capture_id`, source draft IDs, `source_hash`, `approved_by` (admin/user FK), `approved_at`, `conversion_sequence INT CHECK (>0)` and audit timestamps. Formal order is Capture→QuestionDraft + MistakeDraft (editable, not fact) → approved QuestionDraft→Question → separately approved MistakeDraft→Mistake→ReviewItem. These are future schema/service contracts, not current implementation evidence.

### 6. Idempotency, transactions and restore rollback

`idempotency_key = SHA256("legacy-note-migration|" + source_note_id + "|" + source_revision + "|" + source_hash + "|" + mapping_version)`. The runner canonicalizes/hash-checks source, locks `(source_note_id,mapping_version)`, returns existing targets for same hash/terminal state after target/draft hash verification, and fails closed on hash mismatch. It preflights all mapping/length/date/FK checks, then the dedicated `legacy_note_migration_adapter` atomically creates deterministic Question DraftItem+QuestionDraft and Mistake DraftItem+MistakeDraft, applies existing domain invariants and converts Question before Mistake, creates QuestionSource/QKP/ID-set projection and (active only) ReviewItem, asserts cross-entity invariants, updates ledger through the governed transition function and commits. No direct formal Mistake insert, unchanged-service bypass, generic Question link write, or `ON CONFLICT DO UPDATE` may overwrite provenance. Retry after rolled_back requires a new mapping version; retry after failed uses only explicit `failed→pending_mapping` with same immutable hash.

Preflight may separately commit pending/failed so errors remain auditable; successful targets plus ledger state commit together. Target failure rolls back all targets, then records failed in a separate transaction. Source Note is never deleted, hidden, rewritten or demoted by LSR-02. Logical rollback first writes external immutable rollback JSON/hash, then the governed transition function atomically marks the ledger `rolled_back` and NULLs all draft/final target FKs; only after that it deletes dependents in the fixed FK-safe order. An unexpected Capture/Attempt inbound reference makes this logical transaction fail and requires disaster snapshot restore. Disaster snapshot restore restores a fresh pre-migration DB and therefore has no attempted ledger row and is not called `rolled_back`. Existing 012/013/019/020 destructive downgrade is risk evidence only, never rollback.

### 7. LSR-03 executable inputs and fixtures (no scripts/DB created here)

LSR-03 input set is exactly this contract/hash, Alembic graph/head, empty isolated PostgreSQL, synthetic fixtures, source snapshot/hash manifest, mapping table, immutable pre-migration backup identity and recovery identity. Fixtures: valid complete schedule→`migrated_active`; same with published&&!hidden→active plus retained public source/private targets; independently public-but-unmappable→approved `retained_public_only`; valid content with null/ambiguous schedule→`migrated_paused` and no ReviewItem/Record; paused→active after explicit human approval/event; blank question/answer/unknown type→manual; unknown Subject→manual/no auto-create; unknown KP/chapter or cross-subject→manual/no auto-create; invalid date/negative interval/repetitions/NaN EF→manual/failed with raw typed evidence and EF bits; identical replay→same all draft/final/projection IDs/count/hash; changed hash→failed/no overwrite; UUID/ref collision→failed/atomic rollback; duplicate target→failed; due/overdue ReviewItem UTC; unchanged search_vector/parity; complete two-draft chain; chapters/019 three cases; illegal state/event transitions; note/blog→zero ledger/targets.

LSR-03 SQL must compare source/target counts, source_hash/key, FK/orphan, QKP uniqueness and Subject consistency, duplicate targets, ReviewItem due/id/UTC, absence of ReviewRecord for migrated source, new visibility private, old public visibility/slug, source revision/provenance, and before/after snapshot hashes. It must execute identical-key replay and restore verification; any unexpected nonzero is `FAIL`/rollback, not a waived note.

Historical query shorthand (retained only for audit context; **not executable** after the 2026-08-24 remediation). The only executable SQL contract is scoped section 8.10 below; every LSR-03 query must use its `:mapping_version` + final-state/target-ID scope, deterministic mirror function and NULL-safe guards. No query was run in LSR-02:

```sql
-- source coverage and ordinary-content exclusion
SELECT type, COUNT(*) FROM notes GROUP BY type;
SELECT COUNT(*) FROM legacy_note_migrations m JOIN notes n ON n.id=m.source_note_id
 WHERE n.type <> 'mistake';                         -- must be 0
-- target/source/hash and visibility
SELECT m.source_note_id, m.source_hash, q.id, q.visibility, x.visibility
 FROM legacy_note_migrations m
 JOIN questions q ON q.id=m.target_question_id
 JOIN mistakes x ON x.id=m.target_mistake_id;
-- orphan/cross-entity/cross-subject
SELECT m.id FROM legacy_note_migrations m
 LEFT JOIN questions q ON q.id=m.target_question_id
 LEFT JOIN mistakes x ON x.id=m.target_mistake_id
 WHERE m.state IN ('migrated_active','migrated_paused')
   AND (q.id IS NULL OR x.id IS NULL OR x.question_id <> q.id OR x.subject_id <> q.subject_id);
SELECT r.id FROM review_items r LEFT JOIN mistakes x ON x.id=r.mistake_id
 WHERE x.id IS NULL;                                  -- must be 0 after canonical FK
-- duplicates/ledger state/forbidden history
SELECT source_note_id, mapping_version, COUNT(*)
 FROM legacy_note_migrations GROUP BY source_note_id,mapping_version HAVING COUNT(*)>1;
SELECT m.id FROM legacy_note_migrations m JOIN review_records rr
 ON rr.review_item_id=m.target_review_item_id;        -- must be 0 for migrated sources
-- schedule/version/public assertions
SELECT m.id FROM legacy_note_migrations m JOIN questions q ON q.id=m.target_question_id
 JOIN mistakes x ON x.id=m.target_mistake_id
 WHERE q.visibility <> 'private' OR x.visibility <> 'private'
    OR q.version < 1 OR x.version < 1;
SELECT source_note_id, COUNT(*) FROM legacy_note_migrations
 GROUP BY source_note_id HAVING COUNT(*) > 1;          -- explain or fail by mapping-version policy
-- canonical QKP subject and Mistake projection set equality
SELECT qkp.question_id, qkp.knowledge_point_id
 FROM question_knowledge_points qkp
 JOIN questions q ON q.id=qkp.question_id
 JOIN knowledge_points kp ON kp.id=qkp.knowledge_point_id
 WHERE q.subject_id <> kp.subject_id;                 -- must be 0
SELECT m.id, kp.id FROM mistakes m
 JOIN question_knowledge_points qkp ON qkp.question_id=m.question_id
 JOIN knowledge_points kp ON kp.id=qkp.knowledge_point_id
 WHERE m.subject_id <> kp.subject_id;                 -- must be 0
WITH canonical AS (
  SELECT m.id, qkp.knowledge_point_id FROM mistakes m
  JOIN question_knowledge_points qkp ON qkp.question_id=m.question_id
), projection AS (
  SELECT l.target_id AS id, l.knowledge_point_id
  FROM knowledge_point_links l
  WHERE l.target_type='mistake' AND l.target_id ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
)
SELECT * FROM canonical EXCEPT SELECT * FROM projection
UNION ALL
SELECT * FROM projection EXCEPT SELECT * FROM canonical; -- set diff 0
SELECT l.id FROM knowledge_point_links l
 LEFT JOIN mistakes m ON l.target_type='mistake' AND l.target_id=m.id::text
 WHERE l.target_type='mistake' AND m.id IS NULL;       -- projection orphan 0
-- draft chain, source ref and Question mirror parity
SELECT m.id FROM legacy_note_migrations m
 LEFT JOIN draft_items qdi ON qdi.id=m.target_question_draft_item_id
 LEFT JOIN draft_items mdi ON mdi.id=m.target_mistake_draft_item_id
 LEFT JOIN question_drafts qd ON qd.draft_item_id=qdi.id
 LEFT JOIN mistake_drafts md ON md.draft_item_id=mdi.id
 WHERE m.state IN ('migrated_active','migrated_paused')
   AND (qdi.id IS NULL OR mdi.id IS NULL OR qd.id IS NULL OR md.id IS NULL);
SELECT qs.id FROM question_sources qs
 WHERE qs.source_type<>'note' OR qs.source_ref !~ '^legacy-note:[0-9a-f-]{36}$';
-- historical mirror shorthand retired; use the exact scoped helper call in 8.10 below.
-- bit-exact EF replay
SELECT m.id FROM legacy_note_migrations m
 WHERE m.legacy_ef_bits IS DISTINCT FROM
       pg_catalog.encode(pg_catalog.float8send(m.legacy_ef),'hex');
```

### 8. Reviewer/Verifier remediation addendum (current LSR-02 contract, 2026-08-24)

本 addendum 记录 Reviewer=`CHANGES_REQUIRED`、Verifier=`FAIL` 的逐项修订；它覆盖本节此前相冲突的简写，仍是设计合同，不是实现或 G2 证据。

#### 8.1 Derived search field and source concurrency

`Note.search_vector` 是旧 Note 的派生/retained 字段，不迁入任何 private Question/Mistake/MistakeDraft/ReviewItem。它必须进入 immutable source snapshot/hash，使用 NULL sentinel：`CASE WHEN search_vector IS NULL THEN '<NULL>' ELSE '<VALUE>' || search_vector::text END`；且 LSR-03 在迁移前/后逐行比较 old Note `id,slug,content,status,hidden,revision,search_vector`；LSR-02/LSR-03 的 writer 禁止更新旧 Note。若需重建 `search_vector`，只能通过现有公共 Note 搜索机制重建，并对相同 query/排序/过滤做 parity；不得把重建结果当作迁移完成证据。

每个 source migration transaction 使用 `REPEATABLE READ`（或全程 `SERIALIZABLE`）并执行：

```sql
SELECT * FROM notes WHERE id=:source_note_id FOR UPDATE;
```

锁定后重新 canonicalize/hash（包括 `search_vector` 文本和 EF bits），与 approved `source_hash` 比较；target 写入前和 commit 前再次读取/计算 `status,hidden,revision,search_vector,source_hash`。任一漂移、锁冲突无法安全重试或 hash 不一致均 `failed`，事务不产生任何 Question/Draft/Mistake/ReviewItem target。

#### 8.2 Canonical knowledge ownership and projection

`QuestionKnowledgePoint` 是 Question 唯一 canonical owner。迁移先在同一事务写/校验 Question QKP；现有 `KnowledgePointLink(target_type='mistake', target_id=...)` 只能是从 target Question QKP 派生的 projection，不能由旧 Note 字符串或 Mistake service 独立决定，也不能成为第二 owner。当前 schema 没有 projection 的 `role/sort_order`；projection 只投影 canonical QKP 的 `knowledge_point_id` ID set。role/order 只由 canonical QKP 保留，丢失到 Mistake projection 的语义必须以 lossiness code 追加到 `migration_notes`。重复执行必须幂等；Question QKP 更新时同事务重建 ID-set projection。

LSR-03 必须执行 QKP `subject_id` 一致性、canonical QKP PK 唯一、Mistake projection ID-set equality、projection duplicate/orphan、Question/Mistake/KP cross-subject queries；不得声称 projection 保留 role/order，也不对不存在的 projection role/order 做 SQL 断言；任一 nonzero `FAIL` 并回滚。

#### 8.3 Complete legacy import draft/audit chain

`ready` ledger 获批后，专用 `legacy_note_migration_adapter`（LSR-02 后续实现，G2=`NOT_IMPLEMENTED`）必须创建 deterministic `Question DraftItem + QuestionDraft` 与 `Mistake DraftItem + MistakeDraft`，并将它们的 IDs 写入 ledger 的 draft-item/draft 强 FK。adapter 不调用 unchanged existing service；它只复用既有 domain invariants，并负责 UUIDv5、`DraftItem.source_type='legacy_note'`、`QuestionSource.source_type='note'`、双 draft approval/conversion、QuestionSource `source_ref`、禁止 generic Question link、paused 不建 ReviewItem。两类草稿可在同一个 transaction 建立，但正式转换顺序不可变：

```text
approved ledger ready
  -> Question DraftItem + QuestionDraft (source/hash/audit)
  -> adapter applies existing domain invariants and converts QuestionDraft -> Question
  -> Mistake DraftItem + MistakeDraft, linked to Question
  -> adapter applies existing domain invariants and converts MistakeDraft -> Mistake
  -> ReviewItem only for migrated_active current schedule
```

Formal `Mistake` 禁止 direct insert/bypass adapter draft conversion；任何没有两枚 draft-item FK、draft version/status/target audit、approval actor/time/sequence/source hash 的 final target 都是 invalid。adapter 必须在一个可回滚 atomic boundary 内执行并记录 conversion sequence；不得依赖 existing service 的未核验副作用或签名。`migrated_paused` 仍有两枚 drafts 和正式 Question/Mistake，但没有 ReviewItem，直到显式人工 schedule approval；`ReviewRecord` 永不生成。Draft target IDs、final target IDs 和 idempotency key 对 `(source_note_id,mapping_version)` 唯一且不可变。

Adapter 冲突清单与 LSR-03 测试合同：现有 Question/Mistake service 若拥有不同 UUID、source type、approval、事务边界、generic-link 写入、隐式 ReviewItem 或重试副作用，均视为 adapter conflict；adapter 必须显式包住/拒绝这些行为，不得“原样调用后假设一致”。LSR-03 需以 synthetic fixtures 验证 adapter 的 method/signature 输入、domain invariant、Question-before-Mistake 顺序、两 DraftItem/FK、`DraftItem.source_type='legacy_note'`、`QuestionSource.source_type='note'`、无 generic Question link、paused no ReviewItem、相同 hash/idempotency replay 和 failure atomicity；实现及测试均为后续 `NOT_IMPLEMENTED`。

#### 8.3a `legacy_note_migration_adapter` exact interface

The only permitted migration entry point is this dedicated adapter; its implementation and tests remain `NOT_IMPLEMENTED`/future G2 input, but the interface is frozen:

```text
legacy_note_migration_adapter.migrate(
  session: SerializableSession,
  source_note_id: UUID,
  mapping_version: str,
  source_title: str,
  source_approved_by: UUID,
  source_approved_at: UTCDateTime,
  source_approval_sequence: int,
  question_conversion_approved_by: UUID,
  question_conversion_approved_at: UTCDateTime,
  mistake_conversion_approved_by: UUID,
  mistake_conversion_approved_at: UTCDateTime,
  schedule_approved_by: UUID | None,
  schedule_approved_at: UTCDateTime | None,
  question_conversion_sequence: int,
  mistake_conversion_sequence: int,
  schedule_approval_sequence: int | None,
  mapped_next_review_at: UTCDateTime | None,
  canonical_payload: JSONB,
  expected_source_hash: SHA256Hex,
  dry_run: bool
) -> LegacyNoteMigrationResult
```

The result additionally returns the complete approval/audit identity tuple for each independent approval: `source_approved_by`, `source_approved_at`, `source_approval_sequence`, `source_approval_event_id`, `question_conversion_approved_by`, `question_conversion_approved_at`, `question_conversion_sequence`, `question_approval_event_id`, `mistake_conversion_approved_by`, `mistake_conversion_approved_at`, `mistake_conversion_sequence`, `mistake_approval_event_id`, `schedule_approved_by`, `schedule_approved_at`, `schedule_approval_sequence`, `schedule_approval_event_id`, plus applicable `transition_event_id`, `rollback_actor_id`, `rollback_event_id`, and `rollback_reference`. These values are part of replay identity and are never replaced by a transition actor's event.

`LegacyNoteMigrationResult` returns `ledger_id`, `source_note_id`, `mapping_version`, `source_hash`, `state`, `idempotent_replay`, the complete approval/audit tuple listed above, `target_question_draft_item_id`, `target_question_draft_id`, `target_question_id`, `target_question_source_id`, `target_qkp_ids INTEGER[]`, `target_mistake_draft_item_id`, `target_mistake_draft_id`, `target_mistake_id`, `target_review_item_id` (NULL for paused), `target_projection_ids INTEGER[]`, and deterministic `target_bundle_hash`; the replay manifest uses these exact field names and types one-for-one. It never returns a fabricated ReviewRecord. Error enum is closed: `SOURCE_NOT_FOUND`, `SOURCE_TYPE_NOT_MISTAKE`, `SOURCE_HASH_MISMATCH`, `SOURCE_HASH_INVALID`, `SOURCE_DRIFT`, `SOURCE_TITLE_TOO_LONG`, `CANONICAL_PAYLOAD_INVALID`, `EF_NONFINITE`, `APPROVAL_REQUIRED`, `APPROVAL_KIND_INVALID`, `APPROVAL_ACTOR_NOT_AUTHORIZED`, `MAPPING_NOT_APPROVED`, `SUBJECT_UNMAPPED`, `KP_UNMAPPED_OR_AMBIGUOUS`, `QUESTION_INVALID`, `ANSWER_INVALID`, `ESSAY_MANUAL_REQUIRED`, `DATE_AMBIGUOUS`, `UUID_COLLISION`, `SOURCE_REF_COLLISION`, `TARGET_DUPLICATE`, `DRAFT_CHAIN_INVALID`, `DOMAIN_INVARIANT`, `INVALID_REASON_OR_REQUIRED_PARAMETER`, `STATE_TRANSITION_REJECTED`, `STALE_EXPECTED_STATE`, `STALE_EXPECTED_SEQUENCE`, `DUPLICATE_APPROVAL`, `UNEXPECTED_ROLLBACK_REFERENCE`, `ROLLBACK_HASH_INVALID`, `ACTIVE_TARGETS_REQUIRED`, `PAUSED_TARGET_SHAPE`, `PUBLIC_ONLY_TARGETS_NONNULL`, `UNEXPECTED_INBOUND_REFERENCE`, `UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED`, `ROLLBACK_HASH_MISMATCH`, `ROLLBACK_AUDIT_HASH_MISMATCH`, `RETRY_TARGETS_MUST_BE_NULL`, `ARCHIVE_INVALID`, `SERIALIZATION_RETRY_EXHAUSTED`, `ROLLBACK_REQUIRED`.
The rejection writer has its own fixed errors: `LEGACY_MIGRATION_REJECTION_DISPOSITION_INVALID`, `LEGACY_MIGRATION_REJECTION_REASON_INVALID`, `LEGACY_MIGRATION_REJECTION_IDEMPOTENCY_CONFLICT`, `LEGACY_MIGRATION_REJECTION_DIRECT_INSERT_REJECTED`, and `LEGACY_MIGRATION_REJECTION_IMMUTABLE`; none is converted into a positive migration disposition.

The adapter runs one `SERIALIZABLE` transaction, calls `create_legacy_note_migration_pending(...)` with the complete canonical payload (which inserts pending with all approval fields NULL), then calls `record_legacy_note_migration_approval(...,p_kind='source',...)`; it executes `SELECT ... FROM notes WHERE id=source_note_id FOR UPDATE`, re-canonicalizes/hash-checks the source before any target write and again before commit, derives all UUIDv5 IDs, creates the complete dual draft chain, records question/mistake/schedule approvals through separate `record_*` calls, switches `MistakeDraft.question_draft_id→question_id` only after formal Question conversion, and invokes the governed ledger transition function. `mapped_next_review_at` is an explicitly supplied, human-approved UTC instant; it is required together with the complete schedule approval tuple for `migrated_active`, and is passed unchanged to both `ReviewItem.next_review_at` and the governed transition. A date-only `next_review` never supplies this value or becomes an implicit midnight/current-time schedule. If the pre-insert title check raises `SOURCE_TITLE_TOO_LONG`, the pending transaction is rolled back completely; only then a new independent `SERIALIZABLE` transaction locks the same live Note, rechecks `type='mistake'`, exact full `source_title`, title length, source hash and hash-derived `snapshot_ref`, and calls `legacy_migration.record_legacy_note_migration_rejection(...,p_disposition='manual'|'failed',p_reason='SOURCE_TITLE_TOO_LONG',...)`. This rejection writer is the only path for a title failure, and its rejection row is outside `lsr02_all_dispositions`/positive counts. `dry_run=true` performs the same lock/hash/mapping checks but commits no target or ledger mutation. Same `(source_note_id,mapping_version,expected_source_hash)` returns the same IDs/state with `idempotent_replay=true`; any changed hash, mapping version collision, stale hash/state or sequence or different UUID content returns the closed error and creates no partial target.

#### 8.4 Bit-exact EF contract

`legacy_ef` is `FLOAT8` and `legacy_ef_bits CHAR(16)`, never a rounded decimal surrogate. The pending contract rejects a NULL or non-finite source before ledger INSERT; an accepted row stores `encode(float8send(source.ef),'hex')` and preserves the typed JSON representation/raw source value in `legacy_review_json`. LSR-03 replays and compares `legacy_ef_bits` byte-for-byte; converting through decimal or accepting equal-looking numeric text is not sufficient.

Non-finite EF is closed adapter error `EF_NONFINITE`; it cannot enter `ready`, `migrated_active`, or `migrated_paused` and must be isolated as manual/failed without targets.
The closed adapter error enum therefore includes `SOURCE_TITLE_TOO_LONG` and `EF_NONFINITE` in addition to the existing errors.

#### 8.5 Two rollback contracts

Controlled logical rollback and disaster snapshot restore are distinct:

1. **Controlled logical rollback** (synthetic/explicitly approved isolated target only): first write an external immutable rollback JSON containing code/route identity, ledger/source/mapping/hash, all draft/final/projection IDs, pre-state and post-state counts; load the matching `legacy_migration_rollback_audits` row whose canonical JSON digest equals the lowercase 64-hex `rollback_reference`. The sole `SECURITY DEFINER` transition function first locks the ledger and audit row and, in the same transaction, checks Capture/Attempt/MistakeDraft.attempt_id inbound references; any unexpected row raises `LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED` before clearing anything. If clear-safe, it atomically sets `state='rolled_back'`, writes the non-null `rollback_reference`, and clears **all** draft/final target columns (`target_question_draft_item_id`, `target_question_draft_id`, `target_mistake_draft_item_id`, `target_mistake_draft_id`, `target_question_source_id`, `target_qkp_ids`, `target_question_id`, `target_projection_ids`, `target_mistake_id`, `target_review_item_id`, `target_bundle_hash`). The trigger/allowlist explicitly permits this governed atomic transition, which releases `ON DELETE RESTRICT`; only then, in this order, delete ReviewItem → Mistake-derived KnowledgePointLink projection → Mistake → MistakeDraft → Mistake DraftItem → QSource/QKP/generic input links → Question → QuestionDraft → Question DraftItem. Legacy Note is never deleted. Legacy import creates no Capture. The standalone 8.10 inbound query is preflight only; the transition guard is the authoritative same-transaction defense.
Title rejection rows are immutable audit history: logical rollback never deletes them and positive disposition/count queries always exclude `legacy_note_migration_rejections`; snapshot restore preserves them only when present in the pre-migration snapshot, otherwise the external immutable rejection export/hash remains the audit reference.

2. **Snapshot disaster restore**: used only when logical rollback fails or the isolated DB is damaged. Restore the pre-migration custom-format snapshot into a fresh DB and associate its external immutable restore JSON/hash with the run. Because this is pre-migration state, the restored DB correctly has no `legacy_note_migrations` row for the attempted migration; do not claim the restored DB contains `state='rolled_back'`. Final audit is the external JSON/hash plus restore identity, not a fabricated post-restore ledger row.

Neither path uses destructive Alembic downgrade as rollback, and neither deletes the retained source Note.

#### 8.6 Chapters/Alembic 019 controlled fixtures

LSR-03 must include exactly three chapter fixtures: (a) `chapters` empty: empty replay through 019 is expected `PASS`; (b) non-empty chapters without an approved mapping manifest: migration must fail/stop before 019 and must not delete chapters; (c) non-empty chapters with an explicit approved `chapter_id→root KnowledgePoint` mapping manifest: run a controlled pre-019 transform, then 019, and verify chapter/KP counts, parent/order, status and provenance. Missing mapping manifest is fail-closed; no implicit chapter drop or guessed KP tree is allowed.

#### 8.7 Append-only transition audit and database enforcement

LSR-03 isolated replay has one explicit prerequisite, before any contract DDL:
`CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;`. The extension is a
new design dependency for `digest`, `float8send`, `gen_random_uuid`, and
`gen_random_bytes`; the replay must verify extension version/ownership, empty-DB
replay, permission denial to ordinary roles, and rollback behavior. No production
database may receive this extension under LSR-02.

The trusted execution boundary is explicit: `legacy_migration_owner` is `NOLOGIN`
and is the sole owner of the schema objects and `SECURITY DEFINER` functions; it
cannot be used as a session login. A separately provisioned adapter execution
login is the exact `session_user` `legacy_note_adapter_runner`, which is a member
of `legacy_note_adapter`; the guard checks that session identity and
`current_user='legacy_migration_owner'`. `app_role`
and `legacy_note_verifier` are never members of the adapter role and cannot become
the owner. Superuser/database-owner bypass of ordinary ACLs is outside the
application threat model and is audited only in an isolated LSR-03 fixture.
The controlled adapter worker enters the `legacy_note_adapter_runner→legacy_note_adapter`
role chain; only `legacy_note_adapter` may execute adapter/transition functions.
Nonce cleanup is a separate exact-signature function callable only by
`legacy_migration_maintenance_runner`; the adapter role and adapter login have
no cleanup EXECUTE privilege and cannot mutate unconsumed registry rows.

```sql
CREATE ROLE legacy_migration_owner NOLOGIN;
CREATE ROLE legacy_note_adapter NOLOGIN;
CREATE ROLE legacy_note_adapter_runner LOGIN;
CREATE ROLE legacy_migration_maintenance_runner LOGIN;
CREATE ROLE legacy_note_verifier NOLOGIN;
GRANT legacy_note_adapter TO legacy_note_adapter_runner;
-- The runner credential/network policy is provisioned outside this contract; no
-- password/credential is stored here.  It may not be app_role or verifier and
-- cannot SET ROLE to the owner.
REVOKE legacy_note_adapter FROM app_role, legacy_note_verifier;
REVOKE legacy_migration_owner FROM app_role, legacy_note_adapter,
  legacy_note_adapter_runner, legacy_migration_maintenance_runner, legacy_note_verifier;
CREATE SCHEMA legacy_migration AUTHORIZATION legacy_migration_owner;
REVOKE CREATE ON SCHEMA legacy_migration FROM PUBLIC;
GRANT USAGE ON SCHEMA legacy_migration TO legacy_note_adapter;
GRANT USAGE ON SCHEMA legacy_migration TO legacy_note_verifier;
GRANT USAGE ON SCHEMA legacy_migration TO legacy_migration_maintenance_runner;
GRANT USAGE ON SCHEMA public TO legacy_migration_owner;
-- SECURITY DEFINER owner functions do not rely on superuser/database-owner
-- inheritance: these are the minimum existing-table reads used by their source,
-- approval, target-bundle, QKP/projection, and rollback validations. Target
-- creation remains the separately governed adapter transaction; no broad target
-- write grant is implied here.
GRANT SELECT ON public.notes, public.users, public.tags, public.note_tags,
  public.draft_items, public.question_drafts, public.questions, public.question_sources,
  public.mistake_drafts, public.mistakes, public.review_items,
  public.question_knowledge_points, public.knowledge_point_links,
  public.capture_items, public.attempts TO legacy_migration_owner;
-- No sequence privilege is needed: governed UUIDs use pgcrypto; any future
-- sequence-backed target must receive an explicit per-sequence USAGE grant in
-- the isolated schema task, never an ALL SEQUENCES grant.
```

`legacy_migration_guard_nonces` rows are retained through the isolated run and
its immutable audit export so replay/second-use evidence remains inspectable.
An owner-only cleanup operation may delete only `consumed_at IS NOT NULL` rows
after the run is closed; its deletion and any rollback are transactional, and an
aborted target DML rolls back both registry insertion and consumption. No direct
app/adapter/verifier/owner-login DML or `TRUNCATE` can clean or rewrite the table;
the only cleanup path is the SECURITY DEFINER function above, called by the
authorized `legacy_migration_maintenance_runner` and limited to consumed rows.

The schema design must include a database trigger/function that rejects every state transition not in the allowlist and rejects direct target/state mutation that bypasses the governed service. The transition event ledger is append-only:

```sql
CREATE TYPE legacy_migration.legacy_note_migration_target_bundle AS (
  target_question_draft_item_id UUID,
  target_question_draft_id UUID,
  target_question_id UUID,
  target_question_source_id UUID,
  target_mistake_draft_item_id UUID,
  target_mistake_draft_id UUID,
  target_mistake_id UUID,
  target_review_item_id UUID,
  target_qkp_ids INTEGER[],
  target_projection_ids INTEGER[]
);
-- target_qkp_ids and target_projection_ids are sorted INTEGER arrays before hashing;
-- the bundle hash is therefore deterministic across replay.

CREATE TABLE public.allowed_legacy_note_migration_transitions (
  from_state public.legacy_note_migration_state NOT NULL,
  to_state public.legacy_note_migration_state NOT NULL,
  PRIMARY KEY (from_state, to_state)
);
-- Seed before application ACLs are revoked. ON CONFLICT is deliberately a
-- no-op only for the exact frozen pair; any pre-existing extra/missing pair
-- fails closed rather than silently drifting the transition contract.
INSERT INTO public.allowed_legacy_note_migration_transitions(from_state,to_state) VALUES
 ('pending_mapping','ready'),('pending_mapping','failed'),
 ('pending_mapping','retained_public_only'),
 ('ready','migrated_active'),('ready','migrated_paused'),('ready','failed'),
 ('migrated_paused','migrated_active'),('migrated_paused','rolled_back'),
 ('migrated_active','rolled_back'),('failed','pending_mapping')
ON CONFLICT (from_state,to_state) DO NOTHING;
DO $$
DECLARE v_actual INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_actual FROM public.allowed_legacy_note_migration_transitions;
  IF v_actual <> 10 OR EXISTS (
    SELECT 1 FROM public.allowed_legacy_note_migration_transitions t
    WHERE (t.from_state,t.to_state) NOT IN (
      ('pending_mapping','ready'),('pending_mapping','failed'),
      ('pending_mapping','retained_public_only'),
      ('ready','migrated_active'),('ready','migrated_paused'),('ready','failed'),
      ('migrated_paused','migrated_active'),('migrated_paused','rolled_back'),
      ('migrated_active','rolled_back'),('failed','pending_mapping')))
  THEN RAISE EXCEPTION 'LEGACY_MIGRATION_TRANSITION_SEED_DRIFT'; END IF;
END $$;

CREATE TABLE public.legacy_note_migration_events (
  id UUID PRIMARY KEY,
  ledger_id UUID NOT NULL REFERENCES public.legacy_note_migrations(id) ON DELETE RESTRICT,
  source_note_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE RESTRICT,
  from_state public.legacy_note_migration_state NOT NULL,
  to_state public.legacy_note_migration_state NOT NULL,
  actor_id UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  approval_kind VARCHAR(32) NOT NULL CHECK (approval_kind IN
    ('source','question_conversion','mistake_conversion','schedule','rollback','state_transition')),
  reason TEXT NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
  mapping_version VARCHAR(64) NOT NULL,
  target_bundle_hash CHAR(64) NULL CHECK (target_bundle_hash IS NULL OR target_bundle_hash ~ '^[0-9a-f]{64}$'),
  rollback_hash CHAR(64) NULL CHECK (
    (approval_kind='rollback' AND rollback_hash IS NOT NULL AND rollback_hash ~ '^[0-9a-f]{64}$') OR
    (approval_kind<>'rollback' AND rollback_hash IS NULL)),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT legacy_note_migration_event_real_transition CHECK
    (from_state <> to_state OR approval_kind <> 'state_transition')
);
-- trigger rejects UPDATE/DELETE on events; no service may mutate prior rows

CREATE TABLE public.legacy_migration_rollback_admins (
  user_id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE RESTRICT,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  granted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- A marker is not self-authenticating.  This owner-owned registry makes each
-- nonce a transactional capability that is inserted once, locked by the guard,
-- and consumed once.  It is never writable by an application/adapter/verifier;
-- the NOLOGIN owner can reach it only through the SECURITY DEFINER setter/guard.
CREATE TABLE legacy_migration.legacy_migration_guard_nonces (
  nonce TEXT PRIMARY KEY CHECK (nonce ~ '^[0-9a-f]{32}$'),
  txid BIGINT NOT NULL,
  "session_user" VARCHAR(128) NOT NULL,
  op VARCHAR(16) NOT NULL CHECK (op IN ('INSERT','UPDATE')),
  table_schema VARCHAR(128) NOT NULL,
  table_name VARCHAR(128) NOT NULL,
  ledger_id UUID NOT NULL,
  event_id UUID NULL,
  payload_hash CHAR(64) NOT NULL CHECK (payload_hash ~ '^[0-9a-f]{64}$'),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  consumed_at TIMESTAMPTZ NULL,
  UNIQUE (txid,nonce)
);
ALTER TABLE legacy_migration.legacy_migration_guard_nonces OWNER TO legacy_migration_owner;
REVOKE ALL ON legacy_migration.legacy_migration_guard_nonces
  FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner,
  legacy_migration_maintenance_runner, legacy_note_verifier;
REVOKE TRUNCATE ON legacy_migration.legacy_migration_guard_nonces
  FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier,
  legacy_migration_maintenance_runner, legacy_migration_owner;

CREATE FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(
  p_cutoff TIMESTAMPTZ, p_limit INTEGER
) RETURNS INTEGER
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE v_deleted INTEGER;
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_migration_maintenance_runner'
     OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit < 1 OR p_limit > 10000 THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_NONCE_CLEANUP_NOT_AUTHORIZED';
  END IF;
  WITH doomed AS (
    SELECT nonce
      FROM legacy_migration.legacy_migration_guard_nonces
     WHERE consumed_at IS NOT NULL AND consumed_at < p_cutoff
     ORDER BY consumed_at, nonce
     FOR UPDATE SKIP LOCKED
     LIMIT p_limit
  )
  DELETE FROM legacy_migration.legacy_migration_guard_nonces n
   USING doomed d
   WHERE n.nonce=d.nonce;
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RETURN v_deleted;
END;
$$;
REVOKE ALL ON FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)
  FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
GRANT EXECUTE ON FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)
  TO legacy_migration_maintenance_runner;
ALTER FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)
  OWNER TO legacy_migration_owner;
-- This allowlist is maintained outside the adapter and is read-only to app_role;
-- rollback actor identity is therefore not coupled to source/conversion approval.
CREATE TABLE public.legacy_migration_rollback_audits (
  ledger_id UUID PRIMARY KEY REFERENCES public.legacy_note_migrations(id) ON DELETE RESTRICT,
  source_note_id UUID NOT NULL,
  mapping_version VARCHAR(64) NOT NULL,
  source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
  rollback_reference CHAR(64) NOT NULL CHECK (rollback_reference ~ '^[0-9a-f]{64}$'),
  rollback_json JSONB NOT NULL CHECK (jsonb_typeof(rollback_json)='object'),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source_note_id,mapping_version),
  CONSTRAINT rollback_audit_binding CHECK (
    rollback_json->>'ledger_id'=ledger_id::text AND
    rollback_json->>'source_note_id'=source_note_id::text AND
    rollback_json->>'mapping_version'=mapping_version AND
    rollback_json->>'source_hash'=source_hash::text AND
    rollback_reference=pg_catalog.encode(public.digest(
      pg_catalog.convert_to(rollback_json::text,'UTF8'),'sha256'),'hex'))
);
-- The external immutable rollback JSON is loaded once by the owner; app/adapter/
-- verifier cannot write it. Its digest is recomputed by the transition function.
-- `guard_legacy_migration_rollback_audit()` rejects UPDATE/DELETE/TRUNCATE after
-- the owner load; the owner loader may INSERT exactly once for a ledger and the
-- transition function may only SELECT/lock/recompute it.
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON public.legacy_migration_rollback_audits
  FROM app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
GRANT SELECT ON public.legacy_migration_rollback_audits TO legacy_note_verifier, legacy_note_adapter;
CREATE TABLE public.legacy_migration_approval_authorizations (
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
  approval_kind VARCHAR(32) NOT NULL CHECK
    (approval_kind IN ('source','question_conversion','mistake_conversion','schedule')),
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, approval_kind)
);
ALTER TABLE public.legacy_note_migrations, public.legacy_note_migration_events,
  public.legacy_migration_rollback_audits,
  public.allowed_legacy_note_migration_transitions,
  public.legacy_migration_rollback_admins,
  public.legacy_migration_approval_authorizations OWNER TO legacy_migration_owner;
-- This independent allowlist is administered outside the adapter. Owner
-- functions must verify (actor_id,approval_kind,enabled) before recording an
-- approval; a caller cannot forge p_actor_id merely by naming another user.

-- The ledger event-ID columns are added after the event table exists; each is a
-- strong FK, so an approval/rollback ID cannot be fabricated or orphaned.
ALTER TABLE public.legacy_note_migrations
  ADD CONSTRAINT fk_lnm_source_approval_event FOREIGN KEY (source_approval_event_id)
    REFERENCES public.legacy_note_migration_events(id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT fk_lnm_question_approval_event FOREIGN KEY (question_approval_event_id)
    REFERENCES public.legacy_note_migration_events(id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT fk_lnm_mistake_approval_event FOREIGN KEY (mistake_approval_event_id)
    REFERENCES public.legacy_note_migration_events(id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT fk_lnm_schedule_approval_event FOREIGN KEY (schedule_approval_event_id)
    REFERENCES public.legacy_note_migration_events(id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT fk_lnm_rollback_event FOREIGN KEY (rollback_event_id)
    REFERENCES public.legacy_note_migration_events(id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT fk_lnm_transition_event FOREIGN KEY (transition_event_id)
    REFERENCES public.legacy_note_migration_events(id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

-- Every governed DML receives a fresh, exact-key JSONB marker immediately before
-- that one statement.  The trigger clears it after accepting the statement, so a
-- copied marker cannot authorize a second write.  The GUC is only a transport;
-- current_user/session_user, ACLs, locked-row values, and the nonce checks below
-- are the security boundary.
CREATE FUNCTION legacy_migration.set_legacy_transition_marker(
  p_op TEXT, p_table_schema TEXT, p_table_name TEXT, p_ledger_id UUID,
  p_source_note_id UUID, p_mapping_version VARCHAR(64),
  p_expected_source_hash TEXT, p_expected_from TEXT, p_expected_to TEXT,
  p_target_bundle_hash TEXT, p_event_id UUID, p_approval_kind TEXT,
  p_actor_id UUID, p_rollback_hash TEXT
) RETURNS VOID
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE v_nonce TEXT; v_marker JSONB; v_payload_hash CHAR(64);
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_CALLER_NOT_AUTHORIZED';
  END IF;
  IF p_op NOT IN ('INSERT','UPDATE') OR p_table_schema NOT IN ('public')
     OR p_table_name NOT IN ('legacy_note_migrations','legacy_note_migration_events','legacy_migration_rollback_audits')
     OR p_expected_source_hash IS NULL OR octet_length(p_expected_source_hash) <> 64
     OR p_expected_source_hash !~ '^[0-9a-f]{64}$'
     OR (p_target_bundle_hash IS NOT NULL AND (octet_length(p_target_bundle_hash) <> 64
         OR p_target_bundle_hash !~ '^[0-9a-f]{64}$'))
     OR (p_rollback_hash IS NOT NULL AND (octet_length(p_rollback_hash) <> 64
         OR p_rollback_hash !~ '^[0-9a-f]{64}$')) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_BINDING_INVALID';
  END IF;
  v_nonce := pg_catalog.encode(public.gen_random_bytes(16),'hex');
  v_marker := pg_catalog.jsonb_build_object(
      'nonce',v_nonce,'txid',pg_catalog.txid_current()::text,'op',p_op,
      'table_schema',p_table_schema,'table_name',p_table_name,
      'ledger_id',p_ledger_id::text,'source_note_id',p_source_note_id::text,
      'mapping_version',p_mapping_version,'expected_source_hash',p_expected_source_hash::text,
      'expected_from',p_expected_from,'expected_to',p_expected_to,
      'target_bundle_hash',p_target_bundle_hash,'event_id',p_event_id::text,
      'approval_kind',p_approval_kind,'actor_id',p_actor_id::text,
      'rollback_hash',p_rollback_hash);
  v_payload_hash := pg_catalog.encode(public.digest(
    pg_catalog.convert_to(v_marker::text,'UTF8'),'sha256'),'hex');
  INSERT INTO legacy_migration.legacy_migration_guard_nonces(
    nonce,txid,"session_user",op,table_schema,table_name,ledger_id,event_id,payload_hash)
  VALUES (v_nonce,pg_catalog.txid_current(),session_user,p_op,p_table_schema,p_table_name,
    p_ledger_id,p_event_id,v_payload_hash);
  PERFORM pg_catalog.set_config('app.legacy_transition_guard',
    v_marker::text, true);
END;
$$;

CREATE FUNCTION legacy_migration.validate_and_consume_transition_marker(
  p_marker JSONB, p_tg_op TEXT, p_tg_table_schema TEXT, p_tg_table_name TEXT
) RETURNS VOID
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE r legacy_migration.legacy_migration_guard_nonces%ROWTYPE;
  keys TEXT[] := ARRAY[
    'nonce','txid','op','table_schema','table_name','ledger_id','source_note_id',
    'mapping_version','expected_source_hash','expected_from','expected_to',
    'target_bundle_hash','event_id','approval_kind','actor_id','rollback_hash'];
  v_payload_hash CHAR(64);
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member')
     OR p_marker IS NULL OR jsonb_typeof(p_marker) IS DISTINCT FROM 'object'
     OR NOT (p_marker ?& keys)
     OR (SELECT count(*) FROM jsonb_object_keys(p_marker)) <> cardinality(keys)
     OR EXISTS (SELECT 1 FROM jsonb_object_keys(p_marker) k WHERE NOT (k = ANY(keys)))
     OR p_marker->>'txid' IS DISTINCT FROM pg_catalog.txid_current()::text
     OR p_marker->>'op' IS DISTINCT FROM p_tg_op
     OR p_marker->>'table_schema' IS DISTINCT FROM p_tg_table_schema
     OR p_marker->>'table_name' IS DISTINCT FROM p_tg_table_name THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_CONTEXT_REJECTED';
  END IF;
  v_payload_hash := pg_catalog.encode(public.digest(
    pg_catalog.convert_to(p_marker::text,'UTF8'),'sha256'),'hex');
  SELECT * INTO r
    FROM legacy_migration.legacy_migration_guard_nonces
   WHERE nonce=p_marker->>'nonce' FOR UPDATE;
  IF NOT FOUND OR r.consumed_at IS NOT NULL
     OR r.txid IS DISTINCT FROM pg_catalog.txid_current()
     OR r."session_user" IS DISTINCT FROM session_user
     OR r.op IS DISTINCT FROM p_tg_op
     OR r.table_schema IS DISTINCT FROM p_tg_table_schema
     OR r.table_name IS DISTINCT FROM p_tg_table_name
     OR r.ledger_id::text IS DISTINCT FROM p_marker->>'ledger_id'
     OR r.event_id::text IS DISTINCT FROM NULLIF(p_marker->>'event_id','')
     OR r.payload_hash IS DISTINCT FROM v_payload_hash THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_NONCE_REJECTED';
  END IF;
  UPDATE legacy_migration.legacy_migration_guard_nonces
     SET consumed_at=now()
   WHERE nonce=r.nonce AND consumed_at IS NULL;
  IF NOT FOUND THEN RAISE EXCEPTION 'LEGACY_MIGRATION_NONCE_REPLAY'; END IF;
END;
$$;

CREATE FUNCTION legacy_migration.guard_legacy_note_migration()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
DECLARE m JSONB; keys TEXT[] := ARRAY[
  'nonce','txid','op','table_schema','table_name','ledger_id','source_note_id',
  'mapping_version','expected_source_hash','expected_from','expected_to',
  'target_bundle_hash','event_id','approval_kind','actor_id','rollback_hash'];
BEGIN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_LEDGER_DELETE_REJECTED'; END IF;
  BEGIN m := pg_catalog.current_setting('app.legacy_transition_guard',true)::jsonb;
  EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_INVALID'; END;
  PERFORM legacy_migration.validate_and_consume_transition_marker(
    m,TG_OP,TG_TABLE_SCHEMA,TG_TABLE_NAME);
  IF TG_OP='INSERT' THEN
    IF NEW.state IS DISTINCT FROM 'pending_mapping'
       OR NEW.snapshot_ref IS DISTINCT FROM ('sha256:' || lower(NEW.source_hash::text))
       OR NEW.source_slug IS NULL OR NEW.source_title IS NULL OR NEW.source_url IS NULL
       OR NEW.legacy_review_json IS NULL OR jsonb_typeof(NEW.legacy_review_json) IS DISTINCT FROM 'object'
       OR NEW.migration_notes IS NULL OR jsonb_typeof(NEW.migration_notes) IS DISTINCT FROM 'array'
       OR NEW.target_question_id IS NOT NULL OR NEW.target_question_source_id IS NOT NULL
       OR NEW.target_qkp_ids IS NOT NULL OR NEW.target_mistake_id IS NOT NULL
       OR NEW.target_projection_ids IS NOT NULL OR NEW.target_review_item_id IS NOT NULL
       OR NEW.target_question_draft_item_id IS NOT NULL OR NEW.target_question_draft_id IS NOT NULL
       OR NEW.target_mistake_draft_item_id IS NOT NULL OR NEW.target_mistake_draft_id IS NOT NULL
       OR NEW.target_bundle_hash IS NOT NULL OR NEW.approved_by IS NOT NULL OR NEW.approved_at IS NOT NULL
       OR NEW.manual_review_required IS DISTINCT FROM TRUE
       OR NEW.mapped_next_review_at IS NOT NULL
       OR NEW.legacy_ef::text IN ('NaN','Infinity','-Infinity')
       OR NEW.legacy_ef_bits::text IS DISTINCT FROM pg_catalog.encode(pg_catalog.float8send(NEW.legacy_ef),'hex')
       OR NEW.legacy_interval < 0
       OR NEW.legacy_repetitions < 0
       OR NEW.source_approved_by IS NOT NULL OR NEW.source_approved_at IS NOT NULL
       OR NEW.source_approval_sequence IS NOT NULL OR NEW.question_conversion_approved_by IS NOT NULL
       OR NEW.question_conversion_approved_at IS NOT NULL OR NEW.question_conversion_sequence IS NOT NULL
       OR NEW.mistake_conversion_approved_by IS NOT NULL OR NEW.mistake_conversion_approved_at IS NOT NULL
       OR NEW.mistake_conversion_sequence IS NOT NULL OR NEW.schedule_approved_by IS NOT NULL
       OR NEW.schedule_approved_at IS NOT NULL OR NEW.schedule_approval_sequence IS NOT NULL
       OR NEW.rollback_actor_id IS NOT NULL OR NEW.rollback_reference IS NOT NULL
       OR NEW.source_approval_event_id IS NOT NULL OR NEW.question_approval_event_id IS NOT NULL
       OR NEW.mistake_approval_event_id IS NOT NULL OR NEW.schedule_approval_event_id IS NOT NULL
       OR NEW.transition_event_id IS NOT NULL OR NEW.rollback_event_id IS NOT NULL THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_PENDING_INSERT_BINDING_REJECTED';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM public.notes n
      WHERE n.id=NEW.source_note_id AND n.type='mistake'
        AND n.slug=NEW.source_slug AND n.title=NEW.source_title
        AND n.status=NEW.source_status AND n.hidden=NEW.source_hidden
        AND n.revision=NEW.source_revision) THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_PENDING_SOURCE_BINDING_REJECTED';
    END IF;
  END IF;
  IF TG_OP='UPDATE' THEN
    -- Immutable source/provenance binding: only the explicit approval/target/
    -- state/rollback columns below may differ on a governed UPDATE.
    IF NEW.id IS DISTINCT FROM OLD.id
       OR NEW.source_note_id IS DISTINCT FROM OLD.source_note_id
       OR NEW.source_slug IS DISTINCT FROM OLD.source_slug
       OR NEW.source_title IS DISTINCT FROM OLD.source_title
       OR NEW.source_url IS DISTINCT FROM OLD.source_url
       OR NEW.source_status IS DISTINCT FROM OLD.source_status
       OR NEW.source_hidden IS DISTINCT FROM OLD.source_hidden
       OR NEW.source_revision IS DISTINCT FROM OLD.source_revision
       OR NEW.source_hash IS DISTINCT FROM OLD.source_hash
       OR NEW.snapshot_ref IS DISTINCT FROM OLD.snapshot_ref
       OR NEW.mapping_version IS DISTINCT FROM OLD.mapping_version
       OR NEW.idempotency_key IS DISTINCT FROM OLD.idempotency_key
       OR NEW.legacy_ef IS DISTINCT FROM OLD.legacy_ef
       OR NEW.legacy_ef_bits IS DISTINCT FROM OLD.legacy_ef_bits
       OR NEW.legacy_interval IS DISTINCT FROM OLD.legacy_interval
       OR NEW.legacy_repetitions IS DISTINCT FROM OLD.legacy_repetitions
       OR NEW.legacy_next_review IS DISTINCT FROM OLD.legacy_next_review
       OR NEW.legacy_last_reviewed IS DISTINCT FROM OLD.legacy_last_reviewed
       OR NEW.legacy_review_json IS DISTINCT FROM OLD.legacy_review_json
       OR NEW.created_at IS DISTINCT FROM OLD.created_at THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_IMMUTABLE_PROVENANCE_CHANGED';
    END IF;
    IF m->>'approval_kind' IN ('source','question_conversion','mistake_conversion','schedule') THEN
      IF NEW.state IS DISTINCT FROM OLD.state
         OR NEW.migration_notes IS DISTINCT FROM OLD.migration_notes
         OR NEW.transition_event_id IS DISTINCT FROM OLD.transition_event_id
         OR NEW.rollback_event_id IS DISTINCT FROM OLD.rollback_event_id
         OR NEW.rollback_actor_id IS DISTINCT FROM OLD.rollback_actor_id
         OR NEW.rollback_reference IS DISTINCT FROM OLD.rollback_reference
         OR NEW.target_question_id IS DISTINCT FROM OLD.target_question_id
         OR NEW.target_question_source_id IS DISTINCT FROM OLD.target_question_source_id
         OR NEW.target_qkp_ids IS DISTINCT FROM OLD.target_qkp_ids
         OR NEW.target_mistake_id IS DISTINCT FROM OLD.target_mistake_id
         OR NEW.target_projection_ids IS DISTINCT FROM OLD.target_projection_ids
         OR NEW.target_review_item_id IS DISTINCT FROM OLD.target_review_item_id
         OR NEW.target_question_draft_item_id IS DISTINCT FROM OLD.target_question_draft_item_id
         OR NEW.target_question_draft_id IS DISTINCT FROM OLD.target_question_draft_id
         OR NEW.target_mistake_draft_item_id IS DISTINCT FROM OLD.target_mistake_draft_item_id
         OR NEW.target_mistake_draft_id IS DISTINCT FROM OLD.target_mistake_draft_id
         OR NEW.target_bundle_hash IS DISTINCT FROM OLD.target_bundle_hash
         OR NEW.manual_review_required IS DISTINCT FROM OLD.manual_review_required
         OR NEW.mapped_next_review_at IS DISTINCT FROM OLD.mapped_next_review_at
         OR NEW.mapped_last_reviewed_at IS DISTINCT FROM OLD.mapped_last_reviewed_at THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_SIDE_EFFECT_REJECTED';
      END IF;
      IF (m->>'approval_kind'='source' AND (
            NEW.question_conversion_approved_by IS DISTINCT FROM OLD.question_conversion_approved_by OR
            NEW.question_conversion_approved_at IS DISTINCT FROM OLD.question_conversion_approved_at OR
            NEW.question_conversion_sequence IS DISTINCT FROM OLD.question_conversion_sequence OR
            NEW.mistake_conversion_approved_by IS DISTINCT FROM OLD.mistake_conversion_approved_by OR
            NEW.mistake_conversion_approved_at IS DISTINCT FROM OLD.mistake_conversion_approved_at OR
            NEW.mistake_conversion_sequence IS DISTINCT FROM OLD.mistake_conversion_sequence OR
            NEW.schedule_approved_by IS DISTINCT FROM OLD.schedule_approved_by OR
            NEW.schedule_approved_at IS DISTINCT FROM OLD.schedule_approved_at OR
            NEW.schedule_approval_sequence IS DISTINCT FROM OLD.schedule_approval_sequence))
         OR (m->>'approval_kind'='question_conversion' AND (
            NEW.source_approved_by IS DISTINCT FROM OLD.source_approved_by OR
            NEW.source_approved_at IS DISTINCT FROM OLD.source_approved_at OR
            NEW.source_approval_sequence IS DISTINCT FROM OLD.source_approval_sequence OR
            NEW.mistake_conversion_approved_by IS DISTINCT FROM OLD.mistake_conversion_approved_by OR
            NEW.mistake_conversion_approved_at IS DISTINCT FROM OLD.mistake_conversion_approved_at OR
            NEW.mistake_conversion_sequence IS DISTINCT FROM OLD.mistake_conversion_sequence OR
            NEW.schedule_approved_by IS DISTINCT FROM OLD.schedule_approved_by OR
            NEW.schedule_approved_at IS DISTINCT FROM OLD.schedule_approved_at OR
            NEW.schedule_approval_sequence IS DISTINCT FROM OLD.schedule_approval_sequence))
         OR (m->>'approval_kind'='mistake_conversion' AND (
            NEW.source_approved_by IS DISTINCT FROM OLD.source_approved_by OR
            NEW.source_approved_at IS DISTINCT FROM OLD.source_approved_at OR
            NEW.source_approval_sequence IS DISTINCT FROM OLD.source_approval_sequence OR
            NEW.question_conversion_approved_by IS DISTINCT FROM OLD.question_conversion_approved_by OR
            NEW.question_conversion_approved_at IS DISTINCT FROM OLD.question_conversion_approved_at OR
            NEW.question_conversion_sequence IS DISTINCT FROM OLD.question_conversion_sequence OR
            NEW.schedule_approved_by IS DISTINCT FROM OLD.schedule_approved_by OR
            NEW.schedule_approved_at IS DISTINCT FROM OLD.schedule_approved_at OR
            NEW.schedule_approval_sequence IS DISTINCT FROM OLD.schedule_approval_sequence))
         OR (m->>'approval_kind'='schedule' AND (
            NEW.source_approved_by IS DISTINCT FROM OLD.source_approved_by OR
            NEW.source_approved_at IS DISTINCT FROM OLD.source_approved_at OR
            NEW.source_approval_sequence IS DISTINCT FROM OLD.source_approval_sequence OR
            NEW.question_conversion_approved_by IS DISTINCT FROM OLD.question_conversion_approved_by OR
            NEW.question_conversion_approved_at IS DISTINCT FROM OLD.question_conversion_approved_at OR
            NEW.question_conversion_sequence IS DISTINCT FROM OLD.question_conversion_sequence OR
            NEW.mistake_conversion_approved_by IS DISTINCT FROM OLD.mistake_conversion_approved_by OR
            NEW.mistake_conversion_approved_at IS DISTINCT FROM OLD.mistake_conversion_approved_at OR
            NEW.mistake_conversion_sequence IS DISTINCT FROM OLD.mistake_conversion_sequence)) THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_OTHER_APPROVAL_SLOT_CHANGED';
      END IF;
      IF m->>'approval_kind'='source' AND (
           NEW.source_approval_event_id::text IS DISTINCT FROM m->>'event_id'
           OR NEW.source_approved_by::text IS DISTINCT FROM m->>'actor_id'
           OR NEW.approved_by IS DISTINCT FROM NEW.source_approved_by
           OR NEW.source_approved_at IS NULL OR NEW.source_approval_sequence IS NULL
           OR NOT EXISTS (SELECT 1 FROM public.legacy_note_migration_events e
             WHERE e.id=NEW.source_approval_event_id AND e.ledger_id=NEW.id
               AND e.source_note_id=NEW.source_note_id
               AND e.mapping_version=NEW.mapping_version AND e.actor_id=NEW.source_approved_by
               AND e.approval_kind='source' AND e.source_hash=NEW.source_hash
               AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(NEW.source_approved_at)
               AND e.details->>'sequence' IS NOT DISTINCT FROM NEW.source_approval_sequence::text))
        OR m->>'approval_kind'='question_conversion' AND (
           NEW.question_approval_event_id::text IS DISTINCT FROM m->>'event_id'
           OR NEW.question_conversion_approved_by::text IS DISTINCT FROM m->>'actor_id'
           OR NEW.question_conversion_approved_at IS NULL OR NEW.question_conversion_sequence IS NULL
           OR NOT EXISTS (SELECT 1 FROM public.legacy_note_migration_events e
             WHERE e.id=NEW.question_approval_event_id AND e.ledger_id=NEW.id
               AND e.source_note_id=NEW.source_note_id
               AND e.mapping_version=NEW.mapping_version AND e.actor_id=NEW.question_conversion_approved_by
               AND e.approval_kind='question_conversion' AND e.source_hash=NEW.source_hash
               AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(NEW.question_conversion_approved_at)
               AND e.details->>'sequence' IS NOT DISTINCT FROM NEW.question_conversion_sequence::text))
        OR m->>'approval_kind'='mistake_conversion' AND (
           NEW.mistake_approval_event_id::text IS DISTINCT FROM m->>'event_id'
           OR NEW.mistake_conversion_approved_by::text IS DISTINCT FROM m->>'actor_id'
           OR NEW.mistake_conversion_approved_at IS NULL OR NEW.mistake_conversion_sequence IS NULL
           OR NOT EXISTS (SELECT 1 FROM public.legacy_note_migration_events e
             WHERE e.id=NEW.mistake_approval_event_id AND e.ledger_id=NEW.id
               AND e.source_note_id=NEW.source_note_id
               AND e.mapping_version=NEW.mapping_version AND e.actor_id=NEW.mistake_conversion_approved_by
               AND e.approval_kind='mistake_conversion' AND e.source_hash=NEW.source_hash
               AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(NEW.mistake_conversion_approved_at)
               AND e.details->>'sequence' IS NOT DISTINCT FROM NEW.mistake_conversion_sequence::text))
        OR m->>'approval_kind'='schedule' AND (
           NEW.schedule_approval_event_id::text IS DISTINCT FROM m->>'event_id'
           OR NEW.schedule_approved_by::text IS DISTINCT FROM m->>'actor_id'
           OR NEW.schedule_approved_at IS NULL OR NEW.schedule_approval_sequence IS NULL
           OR NOT EXISTS (SELECT 1 FROM public.legacy_note_migration_events e
             WHERE e.id=NEW.schedule_approval_event_id AND e.ledger_id=NEW.id
               AND e.source_note_id=NEW.source_note_id
               AND e.mapping_version=NEW.mapping_version AND e.actor_id=NEW.schedule_approved_by
               AND e.approval_kind='schedule' AND e.source_hash=NEW.source_hash
               AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(NEW.schedule_approved_at)
               AND e.details->>'sequence' IS NOT DISTINCT FROM NEW.schedule_approval_sequence::text)) THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_EVENT_BINDING_REJECTED';
      END IF;
    ELSIF m->>'approval_kind' IN ('state_transition','rollback') THEN
      IF m->>'approval_kind'='rollback' AND (
           NEW.rollback_event_id::text IS DISTINCT FROM m->>'event_id'
           OR NEW.rollback_actor_id::text IS DISTINCT FROM m->>'actor_id'
           OR NEW.rollback_reference::text IS DISTINCT FROM m->>'rollback_hash'
           OR NEW.transition_event_id IS NOT NULL
           OR NOT EXISTS (SELECT 1 FROM public.legacy_note_migration_events e
             WHERE e.id=NEW.rollback_event_id AND e.ledger_id=NEW.id
               AND e.source_note_id=NEW.source_note_id
               AND e.mapping_version=NEW.mapping_version
               AND e.from_state=OLD.state AND e.to_state=NEW.state
               AND e.actor_id=NEW.rollback_actor_id AND e.approval_kind='rollback'
               AND e.source_hash=NEW.source_hash AND e.rollback_hash=NEW.rollback_reference)) THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_EVENT_BINDING_REJECTED';
      ELSIF m->>'approval_kind'='state_transition' AND (
           NEW.transition_event_id::text IS DISTINCT FROM m->>'event_id'
           OR NEW.rollback_event_id IS DISTINCT FROM OLD.rollback_event_id
           OR NEW.rollback_actor_id IS DISTINCT FROM OLD.rollback_actor_id
           OR NEW.rollback_reference IS DISTINCT FROM OLD.rollback_reference
           OR NOT EXISTS (SELECT 1 FROM public.legacy_note_migration_events e
             WHERE e.id=NEW.transition_event_id AND e.ledger_id=NEW.id
               AND e.source_note_id=NEW.source_note_id
               AND e.mapping_version=NEW.mapping_version
               AND e.from_state=OLD.state AND e.to_state=NEW.state
               AND e.actor_id::text=m->>'actor_id'
               AND e.approval_kind='state_transition'
               AND e.source_hash=NEW.source_hash
               AND e.rollback_hash IS NULL)) THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_TRANSITION_EVENT_BINDING_REJECTED';
      END IF;
      IF m->>'approval_kind'='state_transition' AND m->>'expected_to'='migrated_active' THEN
        IF OLD.manual_review_required IS DISTINCT FROM TRUE
           OR NEW.manual_review_required IS DISTINCT FROM FALSE
           OR NEW.mapped_next_review_at IS NULL
           OR NOT EXISTS (SELECT 1 FROM public.review_items r
             WHERE r.id=NEW.target_review_item_id
               AND r.mistake_id=NEW.target_mistake_id
               AND r.state='active' AND r.algorithm='fixed_interval_v1'
               AND r.next_review_at IS NOT DISTINCT FROM NEW.mapped_next_review_at
               AND r.last_reviewed_at IS NOT DISTINCT FROM NEW.mapped_last_reviewed_at) THEN
          RAISE EXCEPTION 'LEGACY_MIGRATION_ACTIVE_SCHEDULE_DIFF_REJECTED';
        END IF;
      ELSIF m->>'approval_kind'='state_transition'
            AND m->>'expected_to' NOT IN ('rolled_back')
            AND (NEW.manual_review_required IS DISTINCT FROM OLD.manual_review_required
              OR NEW.mapped_next_review_at IS DISTINCT FROM OLD.mapped_next_review_at
              OR NEW.mapped_last_reviewed_at IS DISTINCT FROM OLD.mapped_last_reviewed_at) THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_SCHEDULE_SIDE_EFFECT_REJECTED';
      END IF;
      IF m->>'expected_to' NOT IN ('failed','pending_mapping','rolled_back')
         AND (NEW.migration_notes IS DISTINCT FROM OLD.migration_notes
           OR NEW.approved_by IS DISTINCT FROM OLD.approved_by
           OR NEW.source_approved_by IS DISTINCT FROM OLD.source_approved_by
           OR NEW.source_approved_at IS DISTINCT FROM OLD.source_approved_at
           OR NEW.source_approval_sequence IS DISTINCT FROM OLD.source_approval_sequence
           OR NEW.question_conversion_approved_by IS DISTINCT FROM OLD.question_conversion_approved_by
           OR NEW.question_conversion_approved_at IS DISTINCT FROM OLD.question_conversion_approved_at
           OR NEW.question_conversion_sequence IS DISTINCT FROM OLD.question_conversion_sequence
           OR NEW.mistake_conversion_approved_by IS DISTINCT FROM OLD.mistake_conversion_approved_by
           OR NEW.mistake_conversion_approved_at IS DISTINCT FROM OLD.mistake_conversion_approved_at
           OR NEW.mistake_conversion_sequence IS DISTINCT FROM OLD.mistake_conversion_sequence
           OR NEW.schedule_approved_by IS DISTINCT FROM OLD.schedule_approved_by
           OR NEW.schedule_approval_sequence IS DISTINCT FROM OLD.schedule_approval_sequence) THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_TRANSITION_APPROVAL_SIDE_EFFECT_REJECTED';
      END IF;
      IF m->>'approval_kind'='rollback' AND NEW.migration_notes IS DISTINCT FROM OLD.migration_notes THEN
        RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_NOTES_CHANGED';
      END IF;
    ELSE
      RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_KIND_REJECTED';
    END IF;
  END IF;
  IF TG_OP='UPDATE' AND NEW.state IN ('migrated_active','migrated_paused') AND (
       array_position(NEW.target_qkp_ids,NULL) IS NOT NULL
       OR NEW.target_qkp_ids IS DISTINCT FROM ARRAY(
         SELECT DISTINCT qkp.knowledge_point_id
           FROM public.question_knowledge_points qkp
          WHERE qkp.question_id=NEW.target_question_id
          ORDER BY qkp.knowledge_point_id)
       OR EXISTS (SELECT 1 FROM public.question_knowledge_points qkp
           WHERE qkp.question_id=NEW.target_question_id
           GROUP BY qkp.knowledge_point_id HAVING COUNT(*) > 1)
       OR array_position(NEW.target_projection_ids,NULL) IS NOT NULL
       OR NEW.target_projection_ids IS DISTINCT FROM ARRAY(
         SELECT DISTINCT l.id
           FROM public.knowledge_point_links l
          WHERE l.target_type='mistake' AND l.target_id=NEW.target_mistake_id::text
          ORDER BY l.id)
       OR EXISTS (SELECT 1 FROM public.knowledge_point_links l
           WHERE l.target_type='mistake' AND l.target_id=NEW.target_mistake_id::text
           GROUP BY l.id HAVING COUNT(*) > 1)) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_RELATION_SET_MISMATCH';
  END IF;
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member')
     OR jsonb_typeof(m) IS DISTINCT FROM 'object'
     OR NOT (m ?& keys) OR (SELECT count(*) FROM jsonb_object_keys(m)) <> cardinality(keys)
     OR EXISTS (SELECT 1 FROM jsonb_object_keys(m) k WHERE NOT (k = ANY(keys)))
     OR jsonb_typeof(m->'nonce') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'txid') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'op') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'table_schema') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'table_name') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'ledger_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'source_note_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'mapping_version') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'expected_source_hash') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'expected_from') NOT IN ('string','null')
     OR jsonb_typeof(m->'expected_to') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'target_bundle_hash') NOT IN ('string','null')
     OR jsonb_typeof(m->'event_id') NOT IN ('string','null')
     OR jsonb_typeof(m->'approval_kind') NOT IN ('string','null')
     OR jsonb_typeof(m->'actor_id') NOT IN ('string','null')
     OR jsonb_typeof(m->'rollback_hash') NOT IN ('string','null')
     OR m->>'txid' IS DISTINCT FROM pg_catalog.txid_current()::text
     OR m->>'op' IS DISTINCT FROM TG_OP
     OR m->>'table_schema' IS DISTINCT FROM TG_TABLE_SCHEMA
     OR m->>'table_name' IS DISTINCT FROM TG_TABLE_NAME
     OR m->>'ledger_id' IS DISTINCT FROM NEW.id::text
     OR m->>'source_note_id' IS DISTINCT FROM NEW.source_note_id::text
     OR m->>'mapping_version' IS DISTINCT FROM NEW.mapping_version
     OR m->>'expected_source_hash' IS DISTINCT FROM NEW.source_hash::text
     OR m->>'expected_to' IS DISTINCT FROM NEW.state::text
     OR (TG_OP='INSERT' AND m->>'expected_from' IS NOT NULL)
     OR (TG_OP='UPDATE' AND m->>'expected_from' IS DISTINCT FROM OLD.state::text)
     OR m->>'target_bundle_hash' IS DISTINCT FROM NEW.target_bundle_hash::text
     OR m->>'rollback_hash' IS DISTINCT FROM NEW.rollback_reference::text
     OR (NEW.target_bundle_hash IS NOT NULL AND NEW.target_bundle_hash IS DISTINCT FROM
       pg_catalog.encode(public.digest(pg_catalog.convert_to(
         pg_catalog.row_to_json(ROW(
           NEW.target_question_draft_item_id,NEW.target_question_draft_id,
           NEW.target_question_id,NEW.target_question_source_id,
           NEW.target_mistake_draft_item_id,NEW.target_mistake_draft_id,
           NEW.target_mistake_id,NEW.target_review_item_id,NEW.target_qkp_ids,
           NEW.target_projection_ids
         )::legacy_migration.legacy_note_migration_target_bundle)::text,'UTF8'),'sha256'),'hex')) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_DIRECT_LEDGER_MUTATION_REJECTED';
  END IF;
  -- A marker is one-use: consume it before returning from the accepted trigger.
  PERFORM pg_catalog.set_config('app.legacy_transition_guard','',true);
  RETURN NEW;
END;
$$;

CREATE FUNCTION legacy_migration.guard_legacy_note_migration_event()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
DECLARE m JSONB; keys TEXT[] := ARRAY[
  'nonce','txid','op','table_schema','table_name','ledger_id','source_note_id',
  'mapping_version','expected_source_hash','expected_from','expected_to',
  'target_bundle_hash','event_id','approval_kind','actor_id','rollback_hash'];
BEGIN
  IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_EVENT_APPEND_ONLY'; END IF;
  BEGIN m := pg_catalog.current_setting('app.legacy_transition_guard',true)::jsonb;
  EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_INVALID'; END;
  PERFORM legacy_migration.validate_and_consume_transition_marker(
    m,TG_OP,TG_TABLE_SCHEMA,TG_TABLE_NAME);
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member')
     OR jsonb_typeof(m) IS DISTINCT FROM 'object' OR NOT (m ?& keys)
     OR (SELECT count(*) FROM jsonb_object_keys(m)) <> cardinality(keys)
     OR EXISTS (SELECT 1 FROM jsonb_object_keys(m) k WHERE NOT (k = ANY(keys)))
     OR jsonb_typeof(m->'nonce') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'txid') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'op') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'table_schema') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'table_name') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'ledger_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'source_note_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'mapping_version') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'expected_source_hash') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'expected_from') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'expected_to') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'target_bundle_hash') NOT IN ('string','null')
     OR jsonb_typeof(m->'event_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'approval_kind') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'actor_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'rollback_hash') NOT IN ('string','null')
     OR m->>'txid' IS DISTINCT FROM pg_catalog.txid_current()::text
     OR m->>'op' IS DISTINCT FROM TG_OP OR m->>'table_schema' IS DISTINCT FROM TG_TABLE_SCHEMA
     OR m->>'table_name' IS DISTINCT FROM TG_TABLE_NAME
     OR m->>'event_id' IS DISTINCT FROM NEW.id::text
     OR m->>'ledger_id' IS DISTINCT FROM NEW.ledger_id::text
     OR m->>'source_note_id' IS DISTINCT FROM NEW.source_note_id::text
     OR NEW.source_note_id IS DISTINCT FROM (SELECT source_note_id FROM public.legacy_note_migrations WHERE id=NEW.ledger_id)
     OR m->>'mapping_version' IS DISTINCT FROM NEW.mapping_version
     OR m->>'expected_source_hash' IS DISTINCT FROM NEW.source_hash::text
     OR m->>'expected_from' IS DISTINCT FROM NEW.from_state::text
     OR m->>'expected_to' IS DISTINCT FROM NEW.to_state::text
     OR m->>'approval_kind' IS DISTINCT FROM NEW.approval_kind
     OR m->>'actor_id' IS DISTINCT FROM NEW.actor_id::text
     OR m->>'target_bundle_hash' IS DISTINCT FROM NEW.target_bundle_hash::text
     OR m->>'rollback_hash' IS DISTINCT FROM NEW.rollback_hash::text
     OR (NEW.approval_kind='rollback' AND NOT EXISTS (
       SELECT 1 FROM public.legacy_migration_rollback_audits a
        WHERE a.ledger_id=NEW.ledger_id
          AND a.rollback_reference=NEW.rollback_hash
          AND pg_catalog.encode(public.digest(pg_catalog.convert_to(a.rollback_json::text,'UTF8'),'sha256'),'hex')=NEW.rollback_hash))
     OR (NEW.approval_kind='rollback' AND NOT EXISTS (
       SELECT 1 FROM public.legacy_note_migrations l
        WHERE l.id=NEW.ledger_id
          AND ((l.state='rolled_back' AND l.rollback_reference=NEW.rollback_hash)
            OR (l.state=NEW.from_state AND NEW.to_state='rolled_back')))) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_FORGED_EVENT_REJECTED';
  END IF;
  PERFORM pg_catalog.set_config('app.legacy_transition_guard','',true);
  RETURN NEW;
END;
$$;

CREATE FUNCTION legacy_migration.guard_legacy_migration_rollback_audit()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
DECLARE m JSONB; keys TEXT[] := ARRAY[
  'nonce','txid','op','table_schema','table_name','ledger_id','source_note_id',
  'mapping_version','expected_source_hash','expected_from','expected_to',
  'target_bundle_hash','event_id','approval_kind','actor_id','rollback_hash'];
BEGIN
  IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_AUDIT_IMMUTABLE'; END IF;
  BEGIN m := pg_catalog.current_setting('app.legacy_transition_guard',true)::jsonb;
  EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_INVALID'; END;
  PERFORM legacy_migration.validate_and_consume_transition_marker(
    m,TG_OP,TG_TABLE_SCHEMA,TG_TABLE_NAME);
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member')
     OR jsonb_typeof(m) IS DISTINCT FROM 'object' OR NOT (m ?& keys)
     OR (SELECT count(*) FROM jsonb_object_keys(m)) <> cardinality(keys)
     OR EXISTS (SELECT 1 FROM jsonb_object_keys(m) k WHERE NOT (k = ANY(keys)))
     OR jsonb_typeof(m->'nonce') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'txid') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'op') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'table_schema') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'table_name') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'ledger_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'source_note_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'mapping_version') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'expected_source_hash') IS DISTINCT FROM 'string'
     OR jsonb_typeof(m->'expected_from') NOT IN ('string','null')
     OR jsonb_typeof(m->'expected_to') NOT IN ('string','null')
     OR jsonb_typeof(m->'target_bundle_hash') NOT IN ('string','null')
     OR jsonb_typeof(m->'event_id') NOT IN ('string','null')
     OR jsonb_typeof(m->'approval_kind') NOT IN ('string','null')
     OR jsonb_typeof(m->'actor_id') NOT IN ('string','null')
     OR jsonb_typeof(m->'rollback_hash') IS DISTINCT FROM 'string'
     OR m->>'txid' IS DISTINCT FROM pg_catalog.txid_current()::text
     OR m->>'op' IS DISTINCT FROM 'INSERT' OR m->>'table_schema' IS DISTINCT FROM TG_TABLE_SCHEMA
     OR m->>'table_name' IS DISTINCT FROM TG_TABLE_NAME OR m->>'ledger_id' IS DISTINCT FROM NEW.ledger_id::text
     OR m->>'source_note_id' IS DISTINCT FROM NEW.source_note_id::text
     OR m->>'mapping_version' IS DISTINCT FROM NEW.mapping_version
     OR m->>'expected_source_hash' IS DISTINCT FROM NEW.source_hash::text
     OR m->>'rollback_hash' IS DISTINCT FROM NEW.rollback_reference
     OR NEW.rollback_reference IS DISTINCT FROM pg_catalog.encode(public.digest(pg_catalog.convert_to(NEW.rollback_json::text,'UTF8'),'sha256'),'hex') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_AUDIT_MARKER_REJECTED';
  END IF;
  PERFORM pg_catalog.set_config('app.legacy_transition_guard','',true);
  RETURN NEW;
END;
$$;

CREATE FUNCTION legacy_migration.guard_legacy_note_migration_truncate()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
SET search_path=pg_catalog,legacy_migration
AS $$ BEGIN RAISE EXCEPTION 'LEGACY_MIGRATION_TRUNCATE_REJECTED'; END; $$;

CREATE TRIGGER trg_legacy_note_migration_guard
  BEFORE INSERT OR UPDATE OR DELETE ON public.legacy_note_migrations
  FOR EACH ROW EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration();
CREATE TRIGGER trg_legacy_note_migration_event_guard
  BEFORE INSERT OR UPDATE OR DELETE ON public.legacy_note_migration_events
  FOR EACH ROW EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_event();
CREATE TRIGGER trg_legacy_note_migration_event_truncate_guard
  BEFORE TRUNCATE ON public.legacy_note_migration_events
  FOR EACH STATEMENT EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_event();
CREATE TRIGGER trg_legacy_migration_rollback_audit_guard
  BEFORE INSERT OR UPDATE OR DELETE ON public.legacy_migration_rollback_audits
  FOR EACH ROW EXECUTE FUNCTION legacy_migration.guard_legacy_migration_rollback_audit();
CREATE TRIGGER trg_legacy_migration_rollback_audit_truncate_guard
  BEFORE TRUNCATE ON public.legacy_migration_rollback_audits
  FOR EACH STATEMENT EXECUTE FUNCTION legacy_migration.guard_legacy_migration_rollback_audit();
CREATE TRIGGER trg_legacy_note_migration_truncate_guard
  BEFORE TRUNCATE ON public.legacy_note_migrations
  FOR EACH STATEMENT EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_truncate();

REVOKE ALL ON FUNCTION legacy_migration.guard_legacy_note_migration() FROM PUBLIC, app_role;
REVOKE ALL ON FUNCTION legacy_migration.guard_legacy_note_migration_event() FROM PUBLIC, app_role;
REVOKE ALL ON FUNCTION legacy_migration.guard_legacy_migration_rollback_audit() FROM PUBLIC, app_role;
ALTER FUNCTION legacy_migration.guard_legacy_note_migration() OWNER TO legacy_migration_owner;
ALTER FUNCTION legacy_migration.guard_legacy_note_migration_event() OWNER TO legacy_migration_owner;
ALTER FUNCTION legacy_migration.guard_legacy_migration_rollback_audit() OWNER TO legacy_migration_owner;
ALTER FUNCTION legacy_migration.guard_legacy_note_migration_truncate() OWNER TO legacy_migration_owner;
REVOKE ALL ON FUNCTION legacy_migration.set_legacy_transition_marker(
  TEXT,TEXT,TEXT,UUID,UUID,VARCHAR,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,UUID,TEXT
) FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
ALTER FUNCTION legacy_migration.set_legacy_transition_marker(
  TEXT,TEXT,TEXT,UUID,UUID,VARCHAR,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,UUID,TEXT
) OWNER TO legacy_migration_owner;
REVOKE ALL ON FUNCTION legacy_migration.validate_and_consume_transition_marker(
  JSONB,TEXT,TEXT,TEXT
) FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
ALTER FUNCTION legacy_migration.validate_and_consume_transition_marker(
  JSONB,TEXT,TEXT,TEXT
) OWNER TO legacy_migration_owner;
REVOKE ALL ON FUNCTION legacy_migration.guard_legacy_note_migration_truncate() FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_verifier;
REVOKE TRUNCATE ON public.legacy_note_migrations, public.legacy_note_migration_events,
  public.legacy_migration_rollback_audits FROM PUBLIC, app_role, legacy_note_adapter,
  legacy_note_adapter_runner, legacy_note_verifier, legacy_migration_owner;

-- Rollback loader follows the same owner/session/structured-marker path as every
-- other governed write.  It cannot accept a self-consistent but wrong ledger:
-- the locked ledger row supplies source_note_id/mapping/source_hash and the
-- digest is recomputed inside this function before the single INSERT.
CREATE FUNCTION legacy_migration.load_legacy_migration_rollback_audit(
  p_ledger_id UUID, p_source_note_id UUID, p_mapping_version VARCHAR(64),
  p_source_hash TEXT, p_rollback_reference TEXT, p_rollback_json JSONB
) RETURNS public.legacy_migration_rollback_audits
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE v_ledger public.legacy_note_migrations%ROWTYPE;
        v_result public.legacy_migration_rollback_audits;
        v_digest CHAR(64); v_source_hash CHAR(64); v_rollback_reference CHAR(64);
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_LOADER_CALLER_NOT_AUTHORIZED';
  END IF;
  IF p_source_hash IS NULL OR octet_length(p_source_hash) <> 64 OR p_source_hash !~ '^[0-9a-f]{64}$'
     OR p_rollback_reference IS NULL OR octet_length(p_rollback_reference) <> 64
     OR p_rollback_reference !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_HASH_INVALID';
  END IF;
  v_source_hash := p_source_hash::char(64);
  v_rollback_reference := p_rollback_reference::char(64);
  SELECT * INTO v_ledger FROM public.legacy_note_migrations
   WHERE id=p_ledger_id FOR UPDATE;
  IF NOT FOUND OR v_ledger.source_note_id IS DISTINCT FROM p_source_note_id
     OR v_ledger.mapping_version IS DISTINCT FROM p_mapping_version
     OR v_ledger.source_hash IS DISTINCT FROM v_source_hash THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_SOURCE_BINDING_MISMATCH';
  END IF;
  v_digest := pg_catalog.encode(public.digest(
    pg_catalog.convert_to(p_rollback_json::text,'UTF8'),'sha256'),'hex');
  IF p_rollback_json IS NULL OR jsonb_typeof(p_rollback_json) IS DISTINCT FROM 'object'
     OR v_rollback_reference IS DISTINCT FROM v_digest
     OR p_rollback_json->>'ledger_id' IS DISTINCT FROM p_ledger_id::text
     OR p_rollback_json->>'source_note_id' IS DISTINCT FROM p_source_note_id::text
     OR p_rollback_json->>'mapping_version' IS DISTINCT FROM p_mapping_version
     OR p_rollback_json->>'source_hash' IS DISTINCT FROM v_source_hash::text THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_DIGEST_MISMATCH';
  END IF;
  PERFORM legacy_migration.set_legacy_transition_marker(
    'INSERT','public','legacy_migration_rollback_audits',p_ledger_id,p_source_note_id,
    p_mapping_version,v_source_hash::text,NULL,NULL,NULL,NULL,NULL,NULL,v_rollback_reference::text);
  INSERT INTO public.legacy_migration_rollback_audits
    (ledger_id,source_note_id,mapping_version,source_hash,rollback_reference,rollback_json)
  VALUES (p_ledger_id,p_source_note_id,p_mapping_version,v_source_hash,v_rollback_reference,p_rollback_json)
  RETURNING * INTO v_result;
  RETURN v_result;
EXCEPTION WHEN unique_violation THEN
  RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_AUDIT_ALREADY_LOADED';
END;
$$;
REVOKE ALL ON FUNCTION legacy_migration.load_legacy_migration_rollback_audit(
  UUID,UUID,VARCHAR,TEXT,TEXT,JSONB) FROM PUBLIC,app_role,legacy_note_verifier;
GRANT EXECUTE ON FUNCTION legacy_migration.load_legacy_migration_rollback_audit(
  UUID,UUID,VARCHAR,TEXT,TEXT,JSONB) TO legacy_note_adapter;
ALTER FUNCTION legacy_migration.load_legacy_migration_rollback_audit(
  UUID,UUID,VARCHAR,TEXT,TEXT,JSONB) OWNER TO legacy_migration_owner;
```

The state-shape CHECK above is mandatory, not descriptive shorthand. The executable
guard DDL above is the row-level trigger contract: `guard_legacy_note_migration()`
rejects `source_note_id`, source slug/status/hidden/revision/hash/snapshot,
`mapping_version`, `NEW.state`, every `target_*` column/array, `target_bundle_hash`,
all source/question-conversion/mistake-conversion/schedule approval fields,
`rollback_actor_id`, `rollback_reference`, or post-pending `migration_notes` change unless the
transaction-local marker contains the matching ledger id, expected-from/to enum,
source id/hash, target-bundle hash, and event id written by the appropriate SECURITY DEFINER
owner/transition function. A second `guard_legacy_note_migration_event()` trigger
rejects event `INSERT`, `UPDATE`, `DELETE`, and `TRUNCATE` unless that same
function marker is present; event `from_state`/`to_state` must be enum values and
`from_state <> to_state OR approval_kind <> 'state_transition'` (same-state approval events are valid). These triggers are required schema inputs for LSR-03;
direct SQL without the marker is a negative-test failure.

The application role is denied all writes to the transition table and event table; only the owner-controlled seed and approval/transition functions may seed/append them. It receives read-only access for verification:

```sql
REVOKE INSERT, UPDATE, DELETE, TRUNCATE
  ON public.allowed_legacy_note_migration_transitions, public.legacy_note_migration_events
  FROM app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON public.legacy_migration_rollback_admins
  FROM app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON public.legacy_migration_approval_authorizations
  FROM app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
GRANT SELECT ON public.legacy_migration_approval_authorizations,
  public.legacy_migration_rollback_admins TO legacy_note_verifier;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE
  ON public.allowed_legacy_note_migration_transitions FROM PUBLIC;
GRANT SELECT
  ON public.allowed_legacy_note_migration_transitions, public.legacy_note_migration_events
  TO app_role;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE
  ON public.legacy_note_migration_events FROM PUBLIC;
REVOKE UPDATE (state, target_question_draft_item_id, target_question_draft_id,
  target_mistake_draft_item_id, target_mistake_draft_id,
  target_question_source_id, target_qkp_ids, target_question_id,
  target_projection_ids, target_mistake_id, target_review_item_id,
  target_bundle_hash,
  rollback_reference, migration_notes)
  ON public.legacy_note_migrations
  FROM app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
REVOKE UPDATE ON public.legacy_note_migrations
  FROM app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
REVOKE INSERT, DELETE, TRUNCATE ON public.legacy_note_migrations
  FROM app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
GRANT SELECT ON public.legacy_note_migrations TO app_role;

-- Function ACL is applied immediately after its CREATE body below; helper ACL
-- and minimum SELECT grants are replayed after all helper CREATE statements.
```

The canonical live-source helper is the only owner-side source canonicalizer. It
does not apply the 300-character QuestionSource gate, so a title-overlength
source can still be hashed; migration/rejection policy applies that gate after
the helper returns. It locks the source before reading all fields and tags/KP
relations, and its timestamp expressions are the shared UTC-microsecond form:

```sql
CREATE FUNCTION legacy_migration.canonicalize_legacy_note(p_source_note_id UUID)
RETURNS JSONB LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE
  v_note public.notes%ROWTYPE;
  v_payload JSONB;
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED';
  END IF;
  SELECT * INTO v_note FROM public.notes WHERE id=p_source_note_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_NOT_FOUND'; END IF;
  IF v_note.ef IS NULL OR v_note.interval IS NULL OR v_note.repetitions IS NULL
     OR v_note.ef::text IN ('NaN','Infinity','-Infinity') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
  END IF;
  v_payload := jsonb_build_object(
    'id',v_note.id,'source_note_id',v_note.id,'slug',v_note.slug,
    'source_url','/notes/' || v_note.slug,'title',v_note.title,'content',v_note.content,
    'type',v_note.type,'status',v_note.status,'hidden',v_note.hidden,
    'created_at',to_char(v_note.created_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
    'updated_at',to_char(v_note.updated_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
    'summary',v_note.summary,'cover',v_note.cover,'category',v_note.category,
    'subject',v_note.subject,'difficulty',v_note.difficulty,'question',v_note.question,
    'answers',jsonb_build_object('my_answer',v_note.my_answer,'correct_answer',v_note.correct_answer),
    'analysis',v_note.analysis,
    'knowledge_points',COALESCE((SELECT jsonb_agg(trim(k.value) ORDER BY k.ordinality)
      FROM regexp_split_to_table(replace(replace(replace(replace(COALESCE(v_note.knowledge_points,''),'，',','),'、',','),E'\n',','),'；',','),',')
      WITH ORDINALITY AS k(value,ordinality) WHERE trim(k.value)<>''),'[]'::jsonb),
    'ef',v_note.ef,'legacy_ef_bits',pg_catalog.encode(pg_catalog.float8send(v_note.ef),'hex'),
    'interval',v_note.interval,'repetitions',v_note.repetitions,
    'next_review',to_char(v_note.next_review,'YYYY-MM-DD'),
    'last_reviewed',to_char(v_note.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
    'images',v_note.images,'ai_metadata',v_note.ai_metadata,'folder_id',v_note.folder_id,
    'sort_order',v_note.sort_order,'revision',v_note.revision,
    'tags',COALESCE((SELECT jsonb_agg(to_jsonb(t.name) ORDER BY t.id,t.name)
      FROM public.note_tags nt JOIN public.tags t ON t.id=nt.tag_id
      WHERE nt.note_id=v_note.id),'[]'::jsonb),
    'search_vector_token',CASE WHEN v_note.search_vector IS NULL THEN '<NULL>'
      ELSE '<VALUE>' || v_note.search_vector::text END,
    'legacy_review_json',jsonb_build_object(
      'ef',v_note.ef,'interval',v_note.interval,'repetitions',v_note.repetitions,
      'next_review',to_char(v_note.next_review,'YYYY-MM-DD'),
      'last_reviewed',to_char(v_note.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')));
  RETURN v_payload;
END;
$$;
REVOKE ALL ON FUNCTION legacy_migration.canonicalize_legacy_note(UUID)
  FROM PUBLIC,app_role,legacy_note_adapter,legacy_note_adapter_runner,legacy_note_verifier;
ALTER FUNCTION legacy_migration.canonicalize_legacy_note(UUID)
  OWNER TO legacy_migration_owner;
```

Required transition function signature and behavior (exact transition set; implementation deferred to LSR-03/schema task):

The adapter never writes the ledger with direct `INSERT`/`UPDATE` after ACL
revocation. Its exact owner-function path is:

```sql
CREATE FUNCTION legacy_migration.create_legacy_note_migration_pending(
  p_ledger_id UUID, p_source_note_id UUID, p_mapping_version VARCHAR(64),
  p_source_hash TEXT, p_source_slug VARCHAR(255), p_source_title VARCHAR(500),
  p_source_url VARCHAR(500), p_source_status VARCHAR(20), p_source_hidden BOOLEAN,
  p_source_revision INTEGER, p_snapshot_ref VARCHAR(255), p_idempotency_key VARCHAR(128),
  p_canonical_payload JSONB, p_legacy_review_json JSONB, p_migration_notes JSONB
) RETURNS public.legacy_note_migrations
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE
  v_note public.notes%ROWTYPE;
  v_existing public.legacy_note_migrations%ROWTYPE;
  v_result public.legacy_note_migrations;
  v_source_hash CHAR(64);
  v_legacy_ef DOUBLE PRECISION;
  v_legacy_ef_bits_text TEXT;
  v_legacy_ef_bits CHAR(16);
  v_legacy_interval INTEGER;
  v_legacy_repetitions INTEGER;
  v_legacy_next_review DATE;
  v_legacy_last_reviewed TIMESTAMP;
  v_mapped_last_reviewed_at TIMESTAMPTZ;
  v_live_payload JSONB;
  v_live_hash CHAR(64);
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED';
  END IF;
  IF p_source_hash IS NULL OR octet_length(p_source_hash) <> 64
     OR p_source_hash !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_HASH_INVALID';
  END IF;
  IF p_source_title IS NOT NULL AND char_length(p_source_title) > 300 THEN
    RAISE EXCEPTION 'SOURCE_TITLE_TOO_LONG';
  END IF;
  IF p_canonical_payload IS NULL OR jsonb_typeof(p_canonical_payload) IS DISTINCT FROM 'object'
     OR NOT (p_canonical_payload ?& ARRAY[
       'id','source_note_id','slug','source_url','title','content','type','status','hidden',
       'created_at','updated_at','summary','cover','category','subject','difficulty','question',
       'answers','analysis','knowledge_points','ef','legacy_ef_bits','interval','repetitions',
       'next_review','last_reviewed','images','ai_metadata','folder_id','sort_order','revision',
       'tags','search_vector_token','legacy_review_json']) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
  END IF;
  IF p_canonical_payload->>'title' IS NOT NULL
     AND char_length(p_canonical_payload->>'title') > 300 THEN
    RAISE EXCEPTION 'SOURCE_TITLE_TOO_LONG';
  END IF;
  -- Validate JSONB type/nullability, lexical formats, and bounded ranges before
  -- any typed cast.  This matrix is fail-closed: malformed input always emits
  -- the closed contract error, never PostgreSQL's native cast message.
  IF jsonb_typeof(p_canonical_payload->'id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'source_note_id') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'slug') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'source_url') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'title') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'content') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'type') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'status') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'hidden') IS DISTINCT FROM 'boolean'
     OR jsonb_typeof(p_canonical_payload->'created_at') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'updated_at') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'answers') IS DISTINCT FROM 'object'
     OR NOT (p_canonical_payload->'answers' ?& ARRAY['my_answer','correct_answer'])
     OR jsonb_typeof(p_canonical_payload->'answers'->'my_answer') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'answers'->'correct_answer') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'knowledge_points') IS DISTINCT FROM 'array'
     OR jsonb_typeof(p_canonical_payload->'tags') IS DISTINCT FROM 'array'
     OR jsonb_typeof(p_canonical_payload->'search_vector_token') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'legacy_review_json') IS DISTINCT FROM 'object'
     OR jsonb_typeof(p_canonical_payload->'summary') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'cover') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'category') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'subject') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'difficulty') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'question') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'analysis') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'images') NOT IN ('array','null')
     OR jsonb_typeof(p_canonical_payload->'ai_metadata') NOT IN ('object','null')
     OR jsonb_typeof(p_canonical_payload->'folder_id') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'sort_order') NOT IN ('number','null')
     OR jsonb_typeof(p_canonical_payload->'revision') IS DISTINCT FROM 'number'
     OR jsonb_typeof(p_canonical_payload->'ef') IS DISTINCT FROM 'number'
     OR jsonb_typeof(p_canonical_payload->'legacy_ef_bits') IS DISTINCT FROM 'string'
     OR jsonb_typeof(p_canonical_payload->'interval') IS DISTINCT FROM 'number'
     OR jsonb_typeof(p_canonical_payload->'repetitions') IS DISTINCT FROM 'number'
     OR jsonb_typeof(p_canonical_payload->'next_review') NOT IN ('string','null')
     OR jsonb_typeof(p_canonical_payload->'last_reviewed') NOT IN ('string','null')
     OR p_canonical_payload->>'id' !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
     OR p_canonical_payload->>'source_note_id' !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
     OR octet_length(p_canonical_payload->>'slug') NOT BETWEEN 1 AND 255
     OR octet_length(p_canonical_payload->>'source_url') NOT BETWEEN 1 AND 500
     OR octet_length(p_canonical_payload->>'title') NOT BETWEEN 1 AND 500
     OR p_canonical_payload->>'created_at' !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$'
     OR p_canonical_payload->>'updated_at' !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$'
     OR (p_canonical_payload->>'next_review' IS NOT NULL
         AND p_canonical_payload->>'next_review' !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
     OR (p_canonical_payload->>'last_reviewed' IS NOT NULL
         AND p_canonical_payload->>'last_reviewed' !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$')
     OR octet_length(p_canonical_payload->>'legacy_ef_bits') <> 16
     OR p_canonical_payload->>'legacy_ef_bits' !~ '^[0-9a-f]{16}$'
     OR p_canonical_payload->>'interval' !~ '^(0|[1-9][0-9]{0,9})$'
     OR p_canonical_payload->>'repetitions' !~ '^(0|[1-9][0-9]{0,9})$' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
  END IF;
  BEGIN
    -- Round-trip checks preserve microseconds and UTC; date-only values remain
    -- date-only and never become an implicit schedule instant.
    IF to_char((p_canonical_payload->>'created_at')::timestamptz AT TIME ZONE 'UTC',
               'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') IS DISTINCT FROM p_canonical_payload->>'created_at'
       OR to_char((p_canonical_payload->>'updated_at')::timestamptz AT TIME ZONE 'UTC',
               'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') IS DISTINCT FROM p_canonical_payload->>'updated_at'
       OR (p_canonical_payload->>'next_review' IS NOT NULL AND
           to_char((p_canonical_payload->>'next_review')::date,'YYYY-MM-DD') IS DISTINCT FROM p_canonical_payload->>'next_review')
       OR (p_canonical_payload->>'last_reviewed' IS NOT NULL AND
           to_char((p_canonical_payload->>'last_reviewed')::timestamptz AT TIME ZONE 'UTC',
             'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') IS DISTINCT FROM p_canonical_payload->>'last_reviewed') THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
    END IF;
    IF (p_canonical_payload->>'interval')::numeric > 2147483647
       OR (p_canonical_payload->>'repetitions')::numeric > 2147483647 THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
    END IF;
    v_legacy_ef_bits_text := p_canonical_payload->>'legacy_ef_bits';
    v_legacy_ef_bits := v_legacy_ef_bits_text::char(16);
    v_legacy_ef := (p_canonical_payload->>'ef')::double precision;
    v_legacy_interval := (p_canonical_payload->>'interval')::integer;
    v_legacy_repetitions := (p_canonical_payload->>'repetitions')::integer;
    v_legacy_next_review := CASE WHEN p_canonical_payload->>'next_review' IS NULL THEN NULL
                                 ELSE (p_canonical_payload->>'next_review')::date END;
    v_legacy_last_reviewed := CASE WHEN p_canonical_payload->>'last_reviewed' IS NULL THEN NULL
      ELSE ((p_canonical_payload->>'last_reviewed')::timestamptz AT TIME ZONE 'UTC') END;
    v_mapped_last_reviewed_at := CASE WHEN p_canonical_payload->>'last_reviewed' IS NULL THEN NULL
      ELSE (p_canonical_payload->>'last_reviewed')::timestamptz END;
  EXCEPTION WHEN others THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
  END;
  IF v_legacy_ef::text IN ('NaN','Infinity','-Infinity')
     OR v_legacy_ef_bits::text IS DISTINCT FROM pg_catalog.encode(pg_catalog.float8send(v_legacy_ef),'hex')
     OR v_legacy_interval < 0
     OR v_legacy_repetitions < 0 THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_EF_NONFINITE';
  END IF;
  -- Only structurally and lexically valid payloads reach live-source parity.
  -- This preserves the fixed error split: malformed payloads are
  -- CANONICAL_PAYLOAD_INVALID; valid payloads that differ from the locked Note
  -- are SOURCE_DRIFT.
  v_live_payload := legacy_migration.canonicalize_legacy_note(p_source_note_id);
  v_live_hash := pg_catalog.encode(pg_catalog.digest(
    pg_catalog.convert_to(v_live_payload::text,'UTF8'),'sha256'),'hex');
  IF v_live_hash IS DISTINCT FROM lower(p_source_hash)
     OR p_canonical_payload IS DISTINCT FROM v_live_payload THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_DRIFT';
  END IF;
  v_source_hash := pg_catalog.encode(public.digest(
    pg_catalog.convert_to(p_canonical_payload::text,'UTF8'),'sha256'),'hex');
  IF v_source_hash IS DISTINCT FROM lower(p_source_hash::text)
     OR p_canonical_payload->>'id' IS DISTINCT FROM p_source_note_id::text
     OR p_canonical_payload->>'source_note_id' IS DISTINCT FROM p_source_note_id::text
     OR p_canonical_payload->>'type' IS DISTINCT FROM 'mistake'
     OR p_canonical_payload->>'slug' IS DISTINCT FROM p_source_slug
     OR p_canonical_payload->>'source_url' IS DISTINCT FROM p_source_url
     OR jsonb_typeof(p_canonical_payload->'legacy_review_json') IS DISTINCT FROM 'object'
     OR p_canonical_payload->'legacy_review_json' IS DISTINCT FROM p_legacy_review_json THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_HASH_MISMATCH';
  END IF;
  IF jsonb_typeof(p_legacy_review_json) IS DISTINCT FROM 'object'
     OR p_migration_notes IS NULL OR jsonb_typeof(p_migration_notes) IS DISTINCT FROM 'array' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_PROVENANCE_INVALID';
  END IF;
  SELECT * INTO v_note FROM public.notes
   WHERE id=p_source_note_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_NOT_FOUND'; END IF;
  IF v_note.title IS NULL OR char_length(v_note.title) > 300 THEN
    RAISE EXCEPTION 'SOURCE_TITLE_TOO_LONG';
  END IF;
  IF v_note.ef IS NULL OR v_note.interval IS NULL OR v_note.repetitions IS NULL THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
  END IF;
  IF v_note.type IS DISTINCT FROM 'mistake'
     OR v_note.slug IS DISTINCT FROM p_source_slug
     OR v_note.title IS DISTINCT FROM p_source_title
     OR v_note.status IS DISTINCT FROM p_source_status
     OR v_note.hidden IS DISTINCT FROM p_source_hidden
     OR v_note.revision IS DISTINCT FROM p_source_revision THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_DRIFT';
  END IF;
  -- All field-level live binding (including tags, KP normalization, review
  -- JSON, EF bits and search-vector sentinel) is delegated to the shared
  -- helper above; this function only checks migration metadata and title gate.
  SELECT * INTO v_existing FROM public.legacy_note_migrations
   WHERE source_note_id=p_source_note_id AND mapping_version=p_mapping_version
   FOR UPDATE;
  IF FOUND THEN
    IF v_existing.source_hash IS DISTINCT FROM p_source_hash
       OR v_existing.id IS DISTINCT FROM p_ledger_id
       OR v_existing.idempotency_key IS DISTINCT FROM p_idempotency_key
       OR v_existing.snapshot_ref IS DISTINCT FROM p_snapshot_ref
       OR v_existing.source_url IS DISTINCT FROM p_source_url
       OR v_existing.source_slug IS DISTINCT FROM p_source_slug
       OR v_existing.source_title IS DISTINCT FROM p_source_title
       OR v_existing.source_status IS DISTINCT FROM p_source_status
       OR v_existing.source_hidden IS DISTINCT FROM p_source_hidden
       OR v_existing.source_revision IS DISTINCT FROM p_source_revision
       OR v_existing.legacy_ef IS DISTINCT FROM v_legacy_ef
       OR v_existing.legacy_ef_bits IS DISTINCT FROM v_legacy_ef_bits
       OR v_existing.legacy_interval IS DISTINCT FROM v_legacy_interval
       OR v_existing.legacy_repetitions IS DISTINCT FROM v_legacy_repetitions
       OR v_existing.legacy_next_review IS DISTINCT FROM v_legacy_next_review
       OR v_existing.legacy_last_reviewed IS DISTINCT FROM v_legacy_last_reviewed
       OR v_existing.mapped_next_review_at IS NOT NULL
       OR v_existing.mapped_last_reviewed_at IS DISTINCT FROM v_mapped_last_reviewed_at
       OR v_existing.manual_review_required IS DISTINCT FROM TRUE
       OR v_existing.legacy_review_json IS DISTINCT FROM p_legacy_review_json
       OR p_snapshot_ref IS DISTINCT FROM ('sha256:' || lower(p_source_hash::text)) THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_IDEMPOTENCY_CONFLICT';
    END IF;
    RETURN v_existing;
  END IF;
  IF p_snapshot_ref IS DISTINCT FROM ('sha256:' || lower(p_source_hash::text)) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SNAPSHOT_REF_INVALID';
  END IF;
  PERFORM legacy_migration.set_legacy_transition_marker(
    'INSERT','public','legacy_note_migrations',p_ledger_id,p_source_note_id,
    p_mapping_version,p_source_hash,NULL,'pending',NULL,NULL,NULL,NULL,NULL);
  INSERT INTO public.legacy_note_migrations(
    id,source_note_id,source_slug,source_title,source_url,source_status,source_hidden,
    source_revision,source_hash,snapshot_ref,mapping_version,idempotency_key,state,
    legacy_ef,legacy_ef_bits,legacy_interval,legacy_repetitions,legacy_next_review,
    legacy_last_reviewed,mapped_next_review_at,mapped_last_reviewed_at,manual_review_required,
    legacy_review_json,migration_notes)
  VALUES (
    p_ledger_id,p_source_note_id,p_source_slug,p_source_title,p_source_url,p_source_status,
    p_source_hidden,p_source_revision,p_source_hash,p_snapshot_ref,p_mapping_version,
    p_idempotency_key,'pending_mapping',v_legacy_ef,v_legacy_ef_bits,v_legacy_interval,
    v_legacy_repetitions,v_legacy_next_review,v_legacy_last_reviewed,NULL,v_mapped_last_reviewed_at,TRUE,
    p_legacy_review_json,p_migration_notes)
  RETURNING * INTO v_result;
  RETURN v_result;
EXCEPTION WHEN unique_violation THEN
  RAISE EXCEPTION 'LEGACY_MIGRATION_IDEMPOTENCY_CONFLICT';
END;
$$;

CREATE FUNCTION legacy_migration.record_legacy_note_migration_approval(
  p_ledger_id UUID, p_mapping_version TEXT, p_expected_source_hash TEXT,
  p_expected_state public.legacy_note_migration_state, p_kind VARCHAR(32),
  p_actor_id UUID, p_approved_at TIMESTAMPTZ, p_expected_sequence INTEGER,
  p_sequence INTEGER, p_reason TEXT,
  p_event_details JSONB
) RETURNS public.legacy_note_migrations
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,legacy_migration
AS $$
DECLARE
  v_ledger public.legacy_note_migrations%ROWTYPE;
  v_event_id UUID;
  v_current_sequence INTEGER;
  v_details JSONB;
  v_result public.legacy_note_migrations;
  v_expected_source_hash CHAR(64);
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED';
  END IF;
  IF p_expected_source_hash IS NULL OR octet_length(p_expected_source_hash) <> 64
     OR p_expected_source_hash !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_HASH_INVALID';
  END IF;
  v_expected_source_hash := p_expected_source_hash::char(64);
  IF p_kind NOT IN ('source','question_conversion','mistake_conversion','schedule')
     OR p_event_details IS NULL OR jsonb_typeof(p_event_details) IS DISTINCT FROM 'object'
     OR p_actor_id IS NULL OR p_approved_at IS NULL OR p_reason IS NULL
     OR btrim(p_reason)='' OR octet_length(p_reason)>2000
     OR p_expected_sequence IS NULL OR p_expected_sequence < 0
     OR p_sequence IS NULL OR p_sequence <= 0 THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_KIND_INVALID';
  END IF;
  SELECT * INTO v_ledger FROM public.legacy_note_migrations
   WHERE id=p_ledger_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'LEGACY_MIGRATION_LEDGER_NOT_FOUND'; END IF;
  IF v_ledger.mapping_version::text IS DISTINCT FROM p_mapping_version
     OR v_ledger.source_hash IS DISTINCT FROM v_expected_source_hash
     OR v_ledger.state IS DISTINCT FROM p_expected_state THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_STALE_EXPECTED_STATE';
  END IF;
  -- Explicit kind × state matrix; terminal dispositions and failed rows never
  -- accept a new approval, even if a later CHECK would also reject the shape.
  IF v_ledger.state IN ('retained_public_only','rolled_back','failed') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_TERMINAL_APPROVAL_FORBIDDEN';
  ELSIF p_kind='source' AND v_ledger.state <> 'pending_mapping' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_APPROVAL_STATE_INVALID';
  ELSIF p_kind IN ('question_conversion','mistake_conversion')
        AND v_ledger.state <> 'ready' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CONVERSION_APPROVAL_STATE_INVALID';
  ELSIF p_kind='schedule'
        AND v_ledger.state NOT IN ('ready','migrated_paused') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SCHEDULE_APPROVAL_STATE_INVALID';
  END IF;
  IF (p_kind='source' AND (v_ledger.state <> 'pending_mapping' OR v_ledger.source_approval_event_id IS NOT NULL))
     OR (p_kind='question_conversion' AND v_ledger.question_approval_event_id IS NOT NULL)
     OR (p_kind='mistake_conversion' AND v_ledger.mistake_approval_event_id IS NOT NULL)
     OR (p_kind='schedule' AND v_ledger.schedule_approval_event_id IS NOT NULL) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_DUPLICATE_APPROVAL';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM public.legacy_migration_approval_authorizations a
    WHERE a.user_id=p_actor_id AND a.approval_kind=p_kind AND a.enabled=TRUE
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_ACTOR_NOT_AUTHORIZED'; END IF;
  v_current_sequence := CASE p_kind
    WHEN 'question_conversion' THEN COALESCE(v_ledger.question_conversion_sequence,0)
    WHEN 'mistake_conversion' THEN COALESCE(v_ledger.mistake_conversion_sequence,0)
    WHEN 'schedule' THEN COALESCE(v_ledger.schedule_approval_sequence,0)
    ELSE CASE WHEN EXISTS (SELECT 1 FROM public.legacy_note_migration_events e
                           WHERE e.ledger_id=v_ledger.id AND e.approval_kind='source')
              THEN 1 ELSE 0 END
  END;
  IF p_expected_sequence IS DISTINCT FROM v_current_sequence
     OR p_sequence IS DISTINCT FROM v_current_sequence + 1 THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_STALE_EXPECTED_SEQUENCE';
  END IF;
  v_event_id := public.gen_random_uuid();
  v_details := p_event_details || jsonb_build_object('approved_at',p_approved_at,'sequence',p_sequence);
  PERFORM legacy_migration.set_legacy_transition_marker(
    'INSERT','public','legacy_note_migration_events',v_ledger.id,v_ledger.source_note_id,
    v_ledger.mapping_version,v_ledger.source_hash,v_ledger.state,v_ledger.state,
    v_ledger.target_bundle_hash,v_event_id,p_kind,p_actor_id,NULL);
  INSERT INTO public.legacy_note_migration_events
    (id,ledger_id,source_note_id,from_state,to_state,actor_id,approval_kind,reason,details,source_hash,mapping_version,target_bundle_hash,rollback_hash)
  VALUES (v_event_id,v_ledger.id,v_ledger.source_note_id,v_ledger.state,v_ledger.state,p_actor_id,p_kind,
          p_reason,v_details,v_ledger.source_hash,v_ledger.mapping_version,v_ledger.target_bundle_hash,NULL);
  IF p_kind='source' THEN
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',v_ledger.id,v_ledger.source_note_id,
      v_ledger.mapping_version,v_ledger.source_hash,v_ledger.state,v_ledger.state,
      v_ledger.target_bundle_hash,v_event_id,p_kind,p_actor_id,NULL);
    UPDATE public.legacy_note_migrations SET
      approved_by=p_actor_id,approved_at=p_approved_at,
      source_approved_by=p_actor_id,source_approved_at=p_approved_at,
      source_approval_sequence=p_sequence,source_approval_event_id=v_event_id,updated_at=now()
    WHERE id=v_ledger.id RETURNING * INTO v_result;
  ELSIF p_kind='question_conversion' THEN
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',v_ledger.id,v_ledger.source_note_id,
      v_ledger.mapping_version,v_ledger.source_hash,v_ledger.state,v_ledger.state,
      v_ledger.target_bundle_hash,v_event_id,p_kind,p_actor_id,NULL);
    UPDATE public.legacy_note_migrations SET
      question_conversion_approved_by=p_actor_id,question_conversion_approved_at=p_approved_at,
      question_conversion_sequence=p_sequence,question_approval_event_id=v_event_id,updated_at=now()
    WHERE id=v_ledger.id RETURNING * INTO v_result;
  ELSIF p_kind='mistake_conversion' THEN
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',v_ledger.id,v_ledger.source_note_id,
      v_ledger.mapping_version,v_ledger.source_hash,v_ledger.state,v_ledger.state,
      v_ledger.target_bundle_hash,v_event_id,p_kind,p_actor_id,NULL);
    UPDATE public.legacy_note_migrations SET
      mistake_conversion_approved_by=p_actor_id,mistake_conversion_approved_at=p_approved_at,
      mistake_conversion_sequence=p_sequence,mistake_approval_event_id=v_event_id,updated_at=now()
    WHERE id=v_ledger.id RETURNING * INTO v_result;
  ELSE
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',v_ledger.id,v_ledger.source_note_id,
      v_ledger.mapping_version,v_ledger.source_hash,v_ledger.state,v_ledger.state,
      v_ledger.target_bundle_hash,v_event_id,p_kind,p_actor_id,NULL);
    UPDATE public.legacy_note_migrations SET
      schedule_approved_by=p_actor_id,schedule_approved_at=p_approved_at,
      schedule_approval_sequence=p_sequence,schedule_approval_event_id=v_event_id,updated_at=now()
    WHERE id=v_ledger.id RETURNING * INTO v_result;
  END IF;
  RETURN v_result;
END;
$$;
```

`create_*` locks `(source_note_id,mapping_version)`, verifies the canonical source
hash and every canonical field of the locked live Note, and inserts only `pending_mapping` with every approval
column/event ID NULL. The adapter then calls `record_*` with `p_kind='source'` to
write the source approval event and stores `source_approved_by/at` (mirrored into
legacy `approved_by/at`) plus its exact `source_approval_event_id`; it is idempotent
only when every immutable provenance argument matches: source/mapping/idempotency,
snapshot reference derived from source hash, source URL/slug/title/status/hidden/
revision, canonical payload digest/source hash, and raw review JSON. `record_*` locks the ledger and
accepts `source|question_conversion|mistake_conversion|schedule`, verifies the caller's role and the
`(p_actor_id,p_kind,enabled)` authorization row, writes an
append-only event first, then updates the matching actor/time/sequence/event-id
columns. It rejects wrong state, duplicate sequence, stale hash, or a direct attempt
to approve another kind. Both are the only adapter write path and run SERIALIZABLE;
the transition function reads those exact event IDs and actor/time/sequence values.

```sql
REVOKE ALL ON FUNCTION legacy_migration.create_legacy_note_migration_pending(
  UUID,UUID,VARCHAR,TEXT,VARCHAR(255),VARCHAR(500),VARCHAR(500),VARCHAR(20),BOOLEAN,
  INTEGER,VARCHAR(255),VARCHAR(128),JSONB,JSONB,JSONB) FROM PUBLIC,app_role,legacy_note_verifier;
REVOKE ALL ON FUNCTION legacy_migration.record_legacy_note_migration_approval(
  UUID,TEXT,TEXT,public.legacy_note_migration_state,VARCHAR(32),UUID,TIMESTAMPTZ,INTEGER,INTEGER,TEXT,JSONB) FROM PUBLIC,app_role,legacy_note_verifier;
GRANT EXECUTE ON FUNCTION legacy_migration.create_legacy_note_migration_pending(
  UUID,UUID,VARCHAR,TEXT,VARCHAR(255),VARCHAR(500),VARCHAR(500),VARCHAR(20),BOOLEAN,
  INTEGER,VARCHAR(255),VARCHAR(128),JSONB,JSONB,JSONB) TO legacy_note_adapter;
GRANT EXECUTE ON FUNCTION legacy_migration.record_legacy_note_migration_approval(
  UUID,TEXT,TEXT,public.legacy_note_migration_state,VARCHAR(32),UUID,TIMESTAMPTZ,INTEGER,INTEGER,TEXT,JSONB) TO legacy_note_adapter;
ALTER FUNCTION legacy_migration.create_legacy_note_migration_pending(
  UUID,UUID,VARCHAR,TEXT,VARCHAR(255),VARCHAR(500),VARCHAR(500),VARCHAR(20),BOOLEAN,
  INTEGER,VARCHAR(255),VARCHAR(128),JSONB,JSONB,JSONB) OWNER TO legacy_migration_owner;
ALTER FUNCTION legacy_migration.record_legacy_note_migration_approval(
  UUID,TEXT,TEXT,public.legacy_note_migration_state,VARCHAR(32),UUID,TIMESTAMPTZ,INTEGER,INTEGER,TEXT,JSONB) OWNER TO legacy_migration_owner;
```

```sql
CREATE FUNCTION legacy_migration.transition_legacy_note_migration(
  p_ledger_id UUID,
  p_expected_from public.legacy_note_migration_state,
  p_to public.legacy_note_migration_state,
  p_actor_id UUID,
  p_reason TEXT,
  p_source_note_id UUID,
  p_mapping_version VARCHAR(64),
  p_expected_source_hash TEXT,
  p_target_bundle legacy_migration.legacy_note_migration_target_bundle,
  p_rollback_reference TEXT,
  p_expected_rollback_hash TEXT,
  p_mapped_next_review_at TIMESTAMPTZ,
  p_mapped_last_reviewed_at TIMESTAMPTZ,
  p_event_details JSONB
) RETURNS public.legacy_note_migrations
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, legacy_migration
AS $$

-- pseudo-PL/pgSQL body contract; all parameters are declared above
DECLARE
  v_ledger public.legacy_note_migrations%ROWTYPE;
  v_result public.legacy_note_migrations;
  v_event_id UUID;
  v_rollback_audit public.legacy_migration_rollback_audits%ROWTYPE;
  v_bundle_marker_hash CHAR(64);
  v_expected_source_hash CHAR(64);
  v_rollback_reference CHAR(64);
  v_expected_rollback_hash CHAR(64);
BEGIN
  IF current_user IS DISTINCT FROM 'legacy_migration_owner'
     OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
     OR NOT pg_has_role(session_user, 'legacy_note_adapter', 'member') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED';
  END IF;
  IF p_ledger_id IS NULL OR p_expected_from IS NULL OR p_to IS NULL
     OR p_actor_id IS NULL OR p_source_note_id IS NULL OR p_mapping_version IS NULL
     OR btrim(p_mapping_version)='' OR p_reason IS NULL OR btrim(p_reason)=''
     OR octet_length(p_reason)>2000 THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_INVALID_REASON_OR_REQUIRED_PARAMETER';
  END IF;
  IF p_expected_source_hash IS NULL OR octet_length(p_expected_source_hash) <> 64
     OR p_expected_source_hash !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_HASH_INVALID';
  END IF;
  v_expected_source_hash := p_expected_source_hash::char(64);
  IF p_rollback_reference IS NOT NULL AND (octet_length(p_rollback_reference) <> 64
     OR p_rollback_reference !~ '^[0-9a-f]{64}$') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_HASH_INVALID';
  END IF;
  IF p_expected_rollback_hash IS NOT NULL AND (octet_length(p_expected_rollback_hash) <> 64
     OR p_expected_rollback_hash !~ '^[0-9a-f]{64}$') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_HASH_INVALID';
  END IF;
  v_rollback_reference := p_rollback_reference::char(64);
  v_expected_rollback_hash := p_expected_rollback_hash::char(64);
  v_event_id := public.gen_random_uuid();
  SELECT * INTO v_ledger FROM public.legacy_note_migrations
   WHERE id=p_ledger_id FOR UPDATE;
  IF NOT FOUND OR v_ledger.state IS DISTINCT FROM p_expected_from THEN
  RAISE EXCEPTION 'LEGACY_MIGRATION_STALE_EXPECTED_STATE';
  END IF;
  PERFORM 1 FROM public.notes WHERE id=p_source_note_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_NOT_FOUND'; END IF;
  IF v_ledger.source_note_id IS DISTINCT FROM p_source_note_id
     OR v_ledger.mapping_version IS DISTINCT FROM p_mapping_version
     OR v_ledger.source_hash IS DISTINCT FROM v_expected_source_hash THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_IMMUTABLE_SOURCE';
  END IF;
  IF p_to='ready' AND (v_ledger.source_title IS NULL OR char_length(v_ledger.source_title) > 300
     OR EXISTS (SELECT 1 FROM public.notes n
                WHERE n.id=p_source_note_id
                  AND (n.title IS NULL OR char_length(n.title) > 300))) THEN
    RAISE EXCEPTION 'SOURCE_TITLE_TOO_LONG';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM public.users u WHERE u.id=p_actor_id) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ACTOR_NOT_FOUND';
  END IF;
  IF p_to IN ('ready','retained_public_only')
     AND p_actor_id IS DISTINCT FROM v_ledger.source_approved_by THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_APPROVAL_ACTOR_REQUIRED';
  END IF;
  IF p_to='migrated_active' AND p_actor_id IS DISTINCT FROM v_ledger.schedule_approved_by THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SCHEDULE_APPROVAL_ACTOR_REQUIRED';
  END IF;
  IF p_to='migrated_paused' AND p_actor_id IS DISTINCT FROM v_ledger.mistake_conversion_approved_by THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_MISTAKE_APPROVAL_ACTOR_REQUIRED';
  END IF;
  IF p_to='rolled_back' AND NOT EXISTS (
       SELECT 1 FROM public.legacy_migration_rollback_admins a
        WHERE a.user_id=p_actor_id AND a.enabled=TRUE) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_ACTOR_NOT_AUTHORIZED';
  END IF;
  IF p_to IN ('migrated_active','migrated_paused') AND
     (v_ledger.source_approval_event_id IS NULL OR v_ledger.question_approval_event_id IS NULL
      OR v_ledger.mistake_approval_event_id IS NULL) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_EVENTS_REQUIRED';
  END IF;
  IF p_to='migrated_active' AND v_ledger.schedule_approval_event_id IS NULL THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SCHEDULE_APPROVAL_EVENT_REQUIRED';
  END IF;
  IF p_to IN ('ready','retained_public_only','migrated_active','migrated_paused')
     AND NOT EXISTS (
       SELECT 1 FROM public.legacy_note_migration_events e
       WHERE e.id=v_ledger.source_approval_event_id AND e.ledger_id=v_ledger.id
         AND e.source_note_id=v_ledger.source_note_id
         AND e.mapping_version=v_ledger.mapping_version
         AND e.approval_kind='source' AND e.actor_id=v_ledger.source_approved_by
        AND e.source_hash=v_ledger.source_hash
         AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(v_ledger.source_approved_at)
         AND e.details->>'sequence' IS NOT DISTINCT FROM v_ledger.source_approval_sequence::text
     ) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_APPROVAL_EVENT_INVALID';
  END IF;
  IF NOT EXISTS (
  SELECT 1 FROM public.allowed_legacy_note_migration_transitions
   WHERE from_state=p_expected_from AND to_state=p_to
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_ILLEGAL_TRANSITION'; END IF;
  IF p_to='rolled_back' AND p_rollback_reference IS NULL THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_REFERENCE_REQUIRED';
  END IF;
  IF p_to='rolled_back' AND (p_expected_rollback_hash IS NULL
     OR p_rollback_reference IS DISTINCT FROM p_expected_rollback_hash
     OR p_rollback_reference !~ '^[0-9a-f]{64}$') THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_HASH_MISMATCH';
  END IF;
  IF p_to <> 'rolled_back' AND p_rollback_reference IS NOT NULL THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_UNEXPECTED_ROLLBACK_REFERENCE';
  END IF;
  IF p_to='migrated_active' AND (
       (p_target_bundle).target_question_draft_item_id IS NULL OR
       (p_target_bundle).target_mistake_draft_item_id IS NULL OR
       (p_target_bundle).target_question_draft_id IS NULL OR
       (p_target_bundle).target_mistake_draft_id IS NULL OR
       (p_target_bundle).target_question_source_id IS NULL OR
       (p_target_bundle).target_qkp_ids IS NULL OR
       (p_target_bundle).target_projection_ids IS NULL OR
       (p_target_bundle).target_question_id IS NULL OR
       (p_target_bundle).target_mistake_id IS NULL OR
       (p_target_bundle).target_review_item_id IS NULL) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ACTIVE_TARGETS_REQUIRED';
  END IF;
  IF p_to='migrated_active' AND (
       v_ledger.manual_review_required IS DISTINCT FROM TRUE
       OR p_mapped_next_review_at IS NULL) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_ACTIVE_SCHEDULE_REQUIRED';
  END IF;
  IF p_to='migrated_paused' AND (
       v_ledger.manual_review_required IS DISTINCT FROM TRUE
       OR p_mapped_next_review_at IS NOT NULL) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_PAUSED_SCHEDULE_SHAPE_INVALID';
  END IF;
  IF p_to IN ('migrated_active','migrated_paused') AND (
    EXISTS (SELECT 1 FROM public.draft_items qdi
      WHERE qdi.id=(p_target_bundle).target_question_draft_item_id
        AND qdi.approved_by IS DISTINCT FROM v_ledger.question_conversion_approved_by)
    OR EXISTS (SELECT 1 FROM public.draft_items mdi
      WHERE mdi.id=(p_target_bundle).target_mistake_draft_item_id
        AND mdi.approved_by IS DISTINCT FROM v_ledger.mistake_conversion_approved_by)
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_DRAFT_APPROVAL_ACTOR_MISMATCH'; END IF;
  IF p_to='migrated_paused' AND (
       (p_target_bundle).target_question_draft_item_id IS NULL OR
       (p_target_bundle).target_mistake_draft_item_id IS NULL OR
       (p_target_bundle).target_question_draft_id IS NULL OR
       (p_target_bundle).target_mistake_draft_id IS NULL OR
       (p_target_bundle).target_question_source_id IS NULL OR
       (p_target_bundle).target_qkp_ids IS NULL OR
       (p_target_bundle).target_projection_ids IS NULL OR
       (p_target_bundle).target_question_id IS NULL OR
       (p_target_bundle).target_mistake_id IS NULL OR
       (p_target_bundle).target_review_item_id IS NOT NULL) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_PAUSED_TARGET_SHAPE';
  END IF;
  IF p_to='retained_public_only' AND (
       (p_target_bundle).target_question_draft_item_id IS NOT NULL OR
       (p_target_bundle).target_question_draft_id IS NOT NULL OR
       (p_target_bundle).target_question_id IS NOT NULL OR
       (p_target_bundle).target_question_source_id IS NOT NULL OR
       (p_target_bundle).target_qkp_ids IS NOT NULL OR
       (p_target_bundle).target_mistake_draft_item_id IS NOT NULL OR
       (p_target_bundle).target_mistake_draft_id IS NOT NULL OR
       (p_target_bundle).target_mistake_id IS NOT NULL OR
       (p_target_bundle).target_review_item_id IS NOT NULL OR
       (p_target_bundle).target_projection_ids IS NOT NULL) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_PUBLIC_ONLY_TARGETS_NONNULL';
  END IF;
  IF p_to IN ('migrated_active','migrated_paused') AND NOT EXISTS (
    SELECT 1
    FROM public.draft_items qdi
    JOIN public.question_drafts qd ON qd.draft_item_id=qdi.id
    JOIN public.questions q ON q.id=(p_target_bundle).target_question_id
    JOIN public.question_sources qs ON qs.id=(p_target_bundle).target_question_source_id
    WHERE qdi.id=(p_target_bundle).target_question_draft_item_id
      AND qd.id=(p_target_bundle).target_question_draft_id
      AND qdi.draft_type='question' AND qdi.source_type='legacy_note'
      AND qdi.source_id=p_source_note_id AND qdi.source_hash=p_expected_source_hash
      AND qdi.status='converted' AND qdi.approved_by=v_ledger.question_conversion_approved_by
      AND qdi.approved_at IS NOT NULL AND qdi.conversion_sequence > 0
      AND qdi.target_question_id=(p_target_bundle).target_question_id
      AND qs.question_id=q.id AND qs.source_type='note'
      AND qs.source_ref=('legacy-note:' || lower(p_source_note_id::text))
      AND qs.source_url=v_ledger.source_url AND qs.source_title=v_ledger.source_title
      AND q.visibility='private'
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_TARGET_BUNDLE_UNAUTHORIZED'; END IF;
  IF p_to IN ('migrated_active','migrated_paused') AND NOT EXISTS (
    SELECT 1
    FROM public.draft_items mdi
    JOIN public.mistake_drafts md ON md.draft_item_id=mdi.id
    JOIN public.mistakes x ON x.id=(p_target_bundle).target_mistake_id
    WHERE mdi.id=(p_target_bundle).target_mistake_draft_item_id
      AND md.id=(p_target_bundle).target_mistake_draft_id
      AND mdi.draft_type='mistake' AND mdi.source_type='legacy_note'
      AND mdi.source_id=p_source_note_id AND mdi.source_hash=p_expected_source_hash
      AND mdi.status='converted' AND mdi.approved_by=v_ledger.mistake_conversion_approved_by
      AND mdi.approved_at IS NOT NULL AND mdi.conversion_sequence > 0
      AND mdi.target_mistake_id=(p_target_bundle).target_mistake_id
      AND x.question_id=(p_target_bundle).target_question_id
      AND x.visibility='private'
      AND md.question_id=(p_target_bundle).target_question_id
      AND md.question_draft_id IS NULL AND md.attempt_id IS NULL
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_TARGET_BUNDLE_UNAUTHORIZED'; END IF;
  IF p_to IN ('migrated_active','migrated_paused') AND EXISTS (
    SELECT 1 FROM unnest((p_target_bundle).target_qkp_ids) AS ids(knowledge_point_id)
    WHERE NOT EXISTS (
      SELECT 1 FROM public.question_knowledge_points qkp
      WHERE qkp.question_id=(p_target_bundle).target_question_id
        AND qkp.knowledge_point_id=ids.knowledge_point_id
    )
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_QKP_BUNDLE_UNAUTHORIZED'; END IF;
  IF p_to IN ('migrated_active','migrated_paused') AND EXISTS (
    SELECT 1 FROM unnest((p_target_bundle).target_projection_ids) AS ids(projection_id)
    WHERE NOT EXISTS (
      SELECT 1 FROM public.knowledge_point_links l
      WHERE l.id=ids.projection_id AND l.target_type='mistake'
        AND l.target_id=(p_target_bundle).target_mistake_id::text
    )
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_PROJECTION_BUNDLE_UNAUTHORIZED'; END IF;
  IF p_to IN ('migrated_active','migrated_paused') AND (
       array_position((p_target_bundle).target_qkp_ids,NULL) IS NOT NULL
       OR cardinality((p_target_bundle).target_qkp_ids) IS DISTINCT FROM
          (SELECT COUNT(DISTINCT qkp.knowledge_point_id)::integer
             FROM public.question_knowledge_points qkp
            WHERE qkp.question_id=(p_target_bundle).target_question_id)
       OR (p_target_bundle).target_qkp_ids IS DISTINCT FROM ARRAY(
          SELECT DISTINCT qkp.knowledge_point_id
            FROM public.question_knowledge_points qkp
           WHERE qkp.question_id=(p_target_bundle).target_question_id
           ORDER BY qkp.knowledge_point_id)
       OR EXISTS (SELECT 1 FROM public.question_knowledge_points qkp
           WHERE qkp.question_id=(p_target_bundle).target_question_id
           GROUP BY qkp.knowledge_point_id HAVING COUNT(*) > 1)
       OR array_position((p_target_bundle).target_projection_ids,NULL) IS NOT NULL
       OR cardinality((p_target_bundle).target_projection_ids) IS DISTINCT FROM
          (SELECT COUNT(DISTINCT l.id)::integer
             FROM public.knowledge_point_links l
            WHERE l.target_type='mistake'
              AND l.target_id=(p_target_bundle).target_mistake_id::text)
       OR (p_target_bundle).target_projection_ids IS DISTINCT FROM ARRAY(
          SELECT DISTINCT l.id
            FROM public.knowledge_point_links l
           WHERE l.target_type='mistake'
             AND l.target_id=(p_target_bundle).target_mistake_id::text
           ORDER BY l.id)
       OR EXISTS (SELECT 1 FROM public.knowledge_point_links l
           WHERE l.target_type='mistake'
             AND l.target_id=(p_target_bundle).target_mistake_id::text
           GROUP BY l.id HAVING COUNT(*) > 1)) THEN
    RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_RELATION_SET_MISMATCH';
  END IF;
  IF p_to='migrated_active' AND NOT EXISTS (
    SELECT 1 FROM public.review_items r
    WHERE r.id=(p_target_bundle).target_review_item_id
      AND r.mistake_id=(p_target_bundle).target_mistake_id
      AND r.state='active' AND r.algorithm='fixed_interval_v1'
      AND r.next_review_at IS NOT DISTINCT FROM p_mapped_next_review_at
      AND r.last_reviewed_at IS NOT DISTINCT FROM p_mapped_last_reviewed_at
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_REVIEW_BUNDLE_UNAUTHORIZED'; END IF;
  v_bundle_marker_hash := pg_catalog.encode(public.digest(
    pg_catalog.convert_to(row_to_json(p_target_bundle)::text,'UTF8'),'sha256'),'hex');
  -- Insert the transition event before the governed ledger UPDATE.  The ledger
  -- row guard then sees the exact event ID/ledger/from-to/hash already present;
  -- rollback event validation accepts the locked pre-state and the audit digest,
  -- while the following ledger UPDATE binds it to the rolled_back row.
  PERFORM legacy_migration.set_legacy_transition_marker(
    'INSERT','public','legacy_note_migration_events',p_ledger_id,p_source_note_id,
    p_mapping_version,p_expected_source_hash,p_expected_from::text,p_to::text,
    CASE WHEN p_to IN ('migrated_active','migrated_paused') THEN v_bundle_marker_hash ELSE NULL END,
    v_event_id,CASE WHEN p_to='rolled_back' THEN 'rollback' ELSE 'state_transition' END,
    p_actor_id,CASE WHEN p_to='rolled_back' THEN p_expected_rollback_hash ELSE NULL END);
  INSERT INTO public.legacy_note_migration_events
    (id,ledger_id,source_note_id,from_state,to_state,actor_id,approval_kind,reason,details,source_hash,mapping_version,target_bundle_hash,rollback_hash)
  VALUES
    (v_event_id,p_ledger_id,p_source_note_id,p_expected_from,p_to,p_actor_id,
     CASE WHEN p_to='rolled_back' THEN 'rollback' ELSE 'state_transition' END,
     p_reason,COALESCE(p_event_details,'{}'::jsonb),v_ledger.source_hash,p_mapping_version,
     CASE WHEN p_to IN ('migrated_active','migrated_paused') THEN v_bundle_marker_hash ELSE NULL END,
     CASE WHEN p_to='rolled_back' THEN p_expected_rollback_hash ELSE NULL END);
  -- Inline destination checks: active requires every draft/final ID and a ReviewItem;
  -- paused requires both draft chains, Question/Mistake and NULL ReviewItem;
  -- retained_public_only requires every target-bundle ID NULL plus source published/unhidden;
  -- rolled_back requires p_rollback_reference non-NULL and clears every ledger target FK.
  IF p_to='failed' THEN
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',p_ledger_id,p_source_note_id,
      p_mapping_version,p_expected_source_hash,p_expected_from::text,p_to::text,
      NULL,v_event_id,'state_transition',p_actor_id,NULL);
    UPDATE public.legacy_note_migrations SET
      state='failed', target_question_draft_item_id=NULL,
      target_mistake_draft_item_id=NULL, target_question_draft_id=NULL,
      target_mistake_draft_id=NULL, target_question_source_id=NULL,
      target_qkp_ids=NULL, target_question_id=NULL, target_projection_ids=NULL,
      target_mistake_id=NULL, target_review_item_id=NULL, target_bundle_hash=NULL,
      manual_review_required=TRUE, mapped_next_review_at=NULL,
      approved_by=NULL, approved_at=NULL, source_approved_by=NULL,
      source_approved_at=NULL, source_approval_sequence=NULL,
      question_conversion_approved_by=NULL, question_conversion_approved_at=NULL,
      question_conversion_sequence=NULL, mistake_conversion_approved_by=NULL,
      mistake_conversion_approved_at=NULL, mistake_conversion_sequence=NULL,
      schedule_approved_by=NULL, schedule_approved_at=NULL,
      schedule_approval_sequence=NULL, source_approval_event_id=NULL,
      question_approval_event_id=NULL, mistake_approval_event_id=NULL,
      schedule_approval_event_id=NULL, rollback_actor_id=NULL,
      transition_event_id=v_event_id, rollback_event_id=NULL, rollback_reference=NULL,
      migration_notes=jsonb_build_array(jsonb_build_object(
        'kind','failure','reason',p_reason,'details',COALESCE(p_event_details,'{}'::jsonb))),
      updated_at=now()
    WHERE id=p_ledger_id RETURNING * INTO v_result;
  ELSIF p_expected_from='failed' AND p_to='pending_mapping' THEN
    IF (p_target_bundle).target_question_draft_item_id IS NOT NULL
       OR (p_target_bundle).target_mistake_draft_item_id IS NOT NULL
       OR (p_target_bundle).target_question_draft_id IS NOT NULL
       OR (p_target_bundle).target_mistake_draft_id IS NOT NULL
       OR (p_target_bundle).target_question_source_id IS NOT NULL
       OR (p_target_bundle).target_qkp_ids IS NOT NULL
       OR (p_target_bundle).target_projection_ids IS NOT NULL
       OR (p_target_bundle).target_question_id IS NOT NULL
       OR (p_target_bundle).target_mistake_id IS NOT NULL
       OR (p_target_bundle).target_review_item_id IS NOT NULL THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_RETRY_TARGETS_MUST_BE_NULL';
    END IF;
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',p_ledger_id,p_source_note_id,
      p_mapping_version,p_expected_source_hash,p_expected_from::text,p_to::text,
      NULL,v_event_id,'state_transition',p_actor_id,NULL);
    UPDATE public.legacy_note_migrations SET
      state='pending_mapping', target_question_draft_item_id=NULL,
      target_mistake_draft_item_id=NULL, target_question_draft_id=NULL,
      target_mistake_draft_id=NULL, target_question_source_id=NULL,
      target_qkp_ids=NULL, target_question_id=NULL, target_projection_ids=NULL,
      target_mistake_id=NULL, target_review_item_id=NULL, target_bundle_hash=NULL,
      approved_by=NULL, approved_at=NULL, source_approved_by=NULL,
      source_approved_at=NULL, source_approval_sequence=NULL, question_conversion_approved_by=NULL,
      question_conversion_approved_at=NULL, question_conversion_sequence=NULL,
      mistake_conversion_approved_by=NULL, mistake_conversion_approved_at=NULL,
      mistake_conversion_sequence=NULL, schedule_approved_by=NULL,
      schedule_approved_at=NULL, schedule_approval_sequence=NULL,
      source_approval_event_id=NULL, question_approval_event_id=NULL,
      mistake_approval_event_id=NULL, schedule_approval_event_id=NULL,
      rollback_actor_id=NULL, rollback_event_id=NULL, transition_event_id=v_event_id, rollback_reference=NULL,
      manual_review_required=TRUE, mapped_next_review_at=NULL,
      migration_notes='[]'::jsonb, updated_at=now()
    WHERE id=p_ledger_id RETURNING * INTO v_result;
  ELSIF p_to='rolled_back' THEN
    SELECT * INTO v_rollback_audit
      FROM public.legacy_migration_rollback_audits
     WHERE ledger_id=p_ledger_id FOR SHARE;
    IF NOT FOUND OR v_rollback_audit.source_note_id IS DISTINCT FROM p_source_note_id
       OR v_rollback_audit.mapping_version IS DISTINCT FROM p_mapping_version
       OR v_rollback_audit.source_hash IS DISTINCT FROM p_expected_source_hash
       OR v_rollback_audit.rollback_reference IS DISTINCT FROM p_expected_rollback_hash
       OR pg_catalog.encode(public.digest(pg_catalog.convert_to(v_rollback_audit.rollback_json::text,'UTF8'),'sha256'),'hex')
            IS DISTINCT FROM p_expected_rollback_hash THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_AUDIT_HASH_MISMATCH';
    END IF;
    IF EXISTS (SELECT 1 FROM public.capture_items c
       WHERE c.mistake_draft_item_id=v_ledger.target_mistake_draft_item_id)
       OR EXISTS (SELECT 1 FROM public.attempts a
       WHERE a.mistake_draft_item_id=v_ledger.target_mistake_draft_item_id)
       OR EXISTS (SELECT 1 FROM public.mistake_drafts md
       WHERE md.id=v_ledger.target_mistake_draft_id AND md.attempt_id IS NOT NULL) THEN
      RAISE EXCEPTION 'LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED';
    END IF;
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',p_ledger_id,p_source_note_id,
      p_mapping_version,p_expected_source_hash,p_expected_from::text,p_to::text,
      NULL,v_event_id,'rollback',p_actor_id,p_expected_rollback_hash);
    UPDATE public.legacy_note_migrations SET
      state=p_to, rollback_reference=p_rollback_reference,
      rollback_actor_id=p_actor_id,
      rollback_event_id=v_event_id,
      transition_event_id=NULL,
      target_question_draft_item_id=NULL, target_mistake_draft_item_id=NULL,
      target_question_draft_id=NULL, target_mistake_draft_id=NULL,
      target_question_source_id=NULL, target_qkp_ids=NULL,
      target_question_id=NULL, target_projection_ids=NULL,
      target_mistake_id=NULL, target_review_item_id=NULL,
      target_bundle_hash=NULL,
      manual_review_required=TRUE, mapped_next_review_at=NULL,
      approved_by=NULL, approved_at=NULL, source_approved_by=NULL,
      source_approved_at=NULL, source_approval_sequence=NULL,
      question_conversion_approved_by=NULL, question_conversion_approved_at=NULL,
      question_conversion_sequence=NULL, mistake_conversion_approved_by=NULL,
      mistake_conversion_approved_at=NULL, mistake_conversion_sequence=NULL,
      schedule_approved_by=NULL, schedule_approved_at=NULL,
      schedule_approval_sequence=NULL, source_approval_event_id=NULL,
      question_approval_event_id=NULL, mistake_approval_event_id=NULL,
      schedule_approval_event_id=NULL,
      updated_at=now()
    WHERE id=p_ledger_id RETURNING * INTO v_result;
  ELSE
    PERFORM legacy_migration.set_legacy_transition_marker(
      'UPDATE','public','legacy_note_migrations',p_ledger_id,p_source_note_id,
      p_mapping_version,p_expected_source_hash,p_expected_from::text,p_to::text,
      CASE WHEN p_to IN ('migrated_active','migrated_paused') THEN v_bundle_marker_hash ELSE NULL END,
      v_event_id,'state_transition',p_actor_id,NULL);
    UPDATE public.legacy_note_migrations SET
      state=p_to,
      target_question_draft_item_id=(p_target_bundle).target_question_draft_item_id,
      target_mistake_draft_item_id=(p_target_bundle).target_mistake_draft_item_id,
      target_question_draft_id=(p_target_bundle).target_question_draft_id,
      target_mistake_draft_id=(p_target_bundle).target_mistake_draft_id,
      target_question_source_id=(p_target_bundle).target_question_source_id,
      target_qkp_ids=(p_target_bundle).target_qkp_ids,
      target_question_id=(p_target_bundle).target_question_id,
      target_projection_ids=(p_target_bundle).target_projection_ids,
      target_mistake_id=(p_target_bundle).target_mistake_id,
      target_review_item_id=(p_target_bundle).target_review_item_id,
      target_bundle_hash=CASE
        WHEN p_to IN ('migrated_active','migrated_paused')
        THEN pg_catalog.encode(public.digest(pg_catalog.convert_to(row_to_json(p_target_bundle)::text,'UTF8'),'sha256'),'hex')
        ELSE NULL
      END,
      manual_review_required=CASE WHEN p_to='migrated_active' THEN FALSE ELSE TRUE END,
      mapped_next_review_at=CASE WHEN p_to='migrated_active' THEN p_mapped_next_review_at ELSE NULL END,
      mapped_last_reviewed_at=CASE WHEN p_to='migrated_active' THEN p_mapped_last_reviewed_at ELSE v_ledger.mapped_last_reviewed_at END,
      transition_event_id=v_event_id,
      updated_at=now()
    WHERE id=p_ledger_id RETURNING * INTO v_result;
  END IF;
  -- create_* and record_* owner functions already wrote one append-only event
  -- per approval and stored its exact ID on the locked ledger.  Verify those
  -- IDs/actors/kinds/source hashes here; do not fabricate or duplicate an
  -- approval event under the transition actor.  This transition emits only
  -- the state/rollback event below.
  IF p_to IN ('migrated_paused','migrated_active') AND NOT EXISTS (
    SELECT 1 FROM public.legacy_note_migration_events e
    WHERE e.id=v_ledger.question_approval_event_id AND e.ledger_id=v_ledger.id
      AND e.source_note_id=v_ledger.source_note_id
      AND e.mapping_version=v_ledger.mapping_version
      AND e.approval_kind='question_conversion'
      AND e.actor_id=v_ledger.question_conversion_approved_by
      AND e.source_hash=v_ledger.source_hash
      AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(v_ledger.question_conversion_approved_at)
      AND e.details->>'sequence' IS NOT DISTINCT FROM v_ledger.question_conversion_sequence::text
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_QUESTION_APPROVAL_EVENT_INVALID'; END IF;
  IF p_to IN ('migrated_paused','migrated_active') AND NOT EXISTS (
    SELECT 1 FROM public.legacy_note_migration_events e
    WHERE e.id=v_ledger.mistake_approval_event_id AND e.ledger_id=v_ledger.id
      AND e.source_note_id=v_ledger.source_note_id
      AND e.mapping_version=v_ledger.mapping_version
      AND e.approval_kind='mistake_conversion'
      AND e.actor_id=v_ledger.mistake_conversion_approved_by
      AND e.source_hash=v_ledger.source_hash
      AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(v_ledger.mistake_conversion_approved_at)
      AND e.details->>'sequence' IS NOT DISTINCT FROM v_ledger.mistake_conversion_sequence::text
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_MISTAKE_APPROVAL_EVENT_INVALID'; END IF;
  IF p_to='migrated_active' AND NOT EXISTS (
    SELECT 1 FROM public.legacy_note_migration_events e
    WHERE e.id=v_ledger.schedule_approval_event_id AND e.ledger_id=v_ledger.id
      AND e.source_note_id=v_ledger.source_note_id
      AND e.mapping_version=v_ledger.mapping_version
      AND e.approval_kind='schedule'
      AND e.actor_id=v_ledger.schedule_approved_by
      AND e.source_hash=v_ledger.source_hash
      AND e.details->'approved_at' IS NOT DISTINCT FROM to_jsonb(v_ledger.schedule_approved_at)
      AND e.details->>'sequence' IS NOT DISTINCT FROM v_ledger.schedule_approval_sequence::text
  ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SCHEDULE_APPROVAL_EVENT_INVALID'; END IF;
  RETURN v_result;
END;
$$;
```

```sql
REVOKE ALL ON FUNCTION legacy_migration.transition_legacy_note_migration(
  UUID, public.legacy_note_migration_state, public.legacy_note_migration_state,
  UUID, TEXT, UUID, VARCHAR, TEXT,
  legacy_migration.legacy_note_migration_target_bundle, TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, JSONB
) FROM PUBLIC, app_role, legacy_note_adapter_runner, legacy_note_verifier;
GRANT EXECUTE ON FUNCTION legacy_migration.transition_legacy_note_migration(
  UUID, public.legacy_note_migration_state, public.legacy_note_migration_state,
  UUID, TEXT, UUID, VARCHAR, TEXT,
  legacy_migration.legacy_note_migration_target_bundle, TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, JSONB
) TO legacy_note_adapter;
ALTER FUNCTION legacy_migration.transition_legacy_note_migration(
  UUID, public.legacy_note_migration_state, public.legacy_note_migration_state,
  UUID, TEXT, UUID, VARCHAR, TEXT,
  legacy_migration.legacy_note_migration_target_bundle, TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, JSONB
) OWNER TO legacy_migration_owner;
```

Each owner approval function sets a fresh marker for its own approval event; the transition function validates the locked ledger approval-event IDs and actors, then sets a separate marker for the new state/rollback event. Approval events are never re-created under the transition actor.

The trigger family rejects `INSERT`, `UPDATE`, `DELETE`, and `TRUNCATE` unless the
owner function has set the exact structured JSONB marker immediately before that
single DML and its nonce is present/unconsumed in the owner-only
`legacy_migration_guard_nonces` registry. The marker has exactly these keys: `nonce`, `txid`, `op`,
`table_schema`, `table_name`, `ledger_id`, `source_note_id`, `mapping_version`,
`expected_source_hash`, `expected_from`, `expected_to`, `target_bundle_hash`,
`event_id`, `approval_kind`, `actor_id`, and `rollback_hash`. Each guard compares
every applicable key to `OLD`/`NEW` and `TG_OP/TG_TABLE_SCHEMA/TG_TABLE_NAME`,
including event id/ledger/from/to/actor/source hash/mapping/target hash and
rollback JSON digest; the registry stores the SHA-256 hash of this complete
16-key JSON payload. Missing, extra, malformed, wrong-type, wrong-row, wrong
nonce, wrong hash, cross-transaction, or replayed markers fail. The guard locks
and consumes the registry row after
one accepted row; a transition therefore sets one marker for ledger UPDATE and a
fresh marker for event INSERT. It also requires `current_user='legacy_migration_owner'`
and `session_user='legacy_note_adapter_runner'` with adapter-role membership;
custom-GUC injection alone is never trusted. The ledger/events/audit TRUNCATE
triggers unconditionally reject. LSR-03 must exercise legitimate paths, ordinary
role direct DML, forged/wrong/replayed/second-use markers, and every TRUNCATE path.

`migration_notes` is an append-only JSON contract (array of decision/error/event references); no update may replace prior history. LSR-03 must test illegal direct SQL transitions, illegal event UPDATE/DELETE, target mutation without valid event, missing approval for `ready`/`retained_public_only`, and invalid `migrated_active`/`migrated_paused` combinations; each must be rejected with zero committed target changes.

#### 8.8 Current route/mutation matrix (not historical addendum)

| route/surface | anonymous | admin | canonical owner/transition | rollback |
| --- | --- | --- | --- | --- |
| `/mistakes` | HTTP 308 permanent redirect `/notes` | same; no private write | Note/Public Content successor; aggregate navigation removed | restore route artifact + nav |
| `/mistakes/review` | HTTP 308 permanent redirect `/manage/review`, then current auth boundary | same successor | workspace ReviewItem owner | restore route artifact |
| `/notes/{slug}`, `/api/notes` | published&&!hidden old Note read-only; new private objects never exposed | Note/content admin only; legacy mistake single mutation forbidden | Note/Public Content read owner | restore source/route snapshot |
| legacy Note `POST/PUT/PATCH/DELETE/promote` where `type=mistake` | HTTP 410 JSON | HTTP 410 JSON; successor `/api/admin/captures` or mapped workspace object | governed capture/workspace only | restore pre-cutover route/client |
| legacy Note batch containing any `type=mistake` | HTTP 409 atomic no partial | HTTP 409 atomic no partial | no mixed mutation | restore batch artifact |
| `/write-mistake*` | HTTP 410 at cutover | HTTP 410; no Note write | workspace MistakeDraft/Mistake | restore old route artifact only during observation |
| `/api/review/*` | HTTP 410 JSON successor `/api/admin/review/items` | same; no read-only branch | ReviewItem API only | restore old writer from snapshot |

This table is the current LSR-02 input for LSR-04; implementation remains `NOT_VERIFIED`.

#### 8.9 Independent LSR-03 fixture matrix

In addition to the base fixtures, LSR-03 must independently include: a public, unmappable source that reaches approved `retained_public_only`; a paused source manually approved to active with a new ReviewItem and no ReviewRecord; source_ref collision; duplicate target IDs/content; due and overdue ReviewItem UTC values; unchanged search_vector with NULL/non-NULL sentinel cases; options `[]` for `short_answer`/`true_false`, illegal option objects with extra/non-string members, and exact `true_false` `True`/`False` versus manual-invalid values; complete `legacy_note_migration_adapter` draft-chain conversion; adapter conflict/side-effect/idempotency cases; failed→pending stale approval/event/target reuse; all three chapters/019 cases; illegal/stale state/event transitions; direct target/migration_notes writes; forged digest/gen-random ACL; and rollback FK order plus unexpected Capture/Attempt inbound reference. Each fixture must have expected ledger state, draft/final/projection IDs, count/hash assertions, and rollback result. No fixture may use real user content.

The title-error fixture additionally treats `legacy_note_migration_rejections` as a separate negative/manual relation: it verifies the pending transaction is rolled back before the writer's new source-lock transaction, the writer's immutable audit row/ACL/guard/idempotency behavior, and that neither rollback deletion order nor positive disposition/replay counts include rejection rows.

#### 8.9a Deterministic helper definitions

This is the helper-definition block of the single executable 8.10 bundle, not a
separate validation script or alternative SQL contract. The helpers used by the
executable SQL are frozen contracts, not optional names. `QuestionSource.source_note`
must be JSONB provenance metadata (never user正文) with `source_note_id`,
`source_slug`, `source_title`, `source_url`, `source_hash`, `mapping_version`, and a `mirror_contract` object
containing normalized `question_text`, `stem_md`, `question_type`, `options`,
`difficulty`, `correct_answer`, `answer_data`, `analysis_md`, `explanation`,
`title`, and `subject_id`.
Missing, malformed, NULL, unsupported data returns `FALSE`; `insufficient_privilege`
is re-raised so an ACL defect cannot be disguised as a parity miss. Helpers never
guess or raise a cast error for malformed UUID/data.

```sql
CREATE FUNCTION legacy_migration.legacy_question_source_matches(
  p_question_source_id UUID,
  p_source_note_id UUID,
  p_mapping_version VARCHAR(64),
  p_source_slug VARCHAR(255),
  p_source_title VARCHAR(500),
  p_source_url VARCHAR(500),
  p_source_hash TEXT
) RETURNS BOOLEAN
LANGUAGE plpgsql STABLE SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
DECLARE v_source RECORD; v_meta JSONB;
BEGIN
  IF p_question_source_id IS NULL OR p_source_note_id IS NULL OR p_mapping_version IS NULL
     OR p_source_slug IS NULL OR p_source_title IS NULL OR p_source_url IS NULL
     OR p_source_hash IS NULL OR octet_length(p_source_hash) <> 64
     OR p_source_hash !~ '^[0-9a-f]{64}$' THEN RETURN FALSE; END IF;
  SELECT id,source_type,source_ref,source_url,source_title,source_note,question_id INTO v_source
    FROM public.question_sources WHERE id=p_question_source_id;
  IF NOT FOUND OR v_source.source_type IS DISTINCT FROM 'note'
     OR v_source.source_ref IS DISTINCT FROM ('legacy-note:'||lower(p_source_note_id::text))
     OR v_source.source_url IS DISTINCT FROM p_source_url
     OR v_source.source_title IS DISTINCT FROM p_source_title THEN RETURN FALSE; END IF;
  IF NOT EXISTS (
    SELECT 1 FROM public.legacy_note_migrations m
    WHERE m.source_note_id=p_source_note_id AND m.mapping_version=p_mapping_version
      AND m.target_question_source_id=p_question_source_id AND m.source_hash=p_source_hash
  ) THEN RETURN FALSE; END IF;
  v_meta := v_source.source_note::jsonb;
  RETURN v_meta->>'source_note_id' IS NOT DISTINCT FROM p_source_note_id::text
     AND v_meta->>'source_slug' IS NOT DISTINCT FROM p_source_slug
     AND v_meta->>'source_title' IS NOT DISTINCT FROM p_source_title
     AND v_meta->>'source_url' IS NOT DISTINCT FROM p_source_url
     AND v_meta->>'source_hash' IS NOT DISTINCT FROM p_source_hash
     AND v_meta->>'mapping_version' IS NOT DISTINCT FROM p_mapping_version;
EXCEPTION WHEN insufficient_privilege THEN RAISE;
        WHEN others THEN RETURN FALSE;
END;
$$;

CREATE FUNCTION legacy_migration.legacy_question_mirror_matches(
  p_question_id UUID,
  p_question_source_id UUID,
  p_source_note_id UUID,
  p_mapping_version VARCHAR(64),
  p_source_hash TEXT
) RETURNS BOOLEAN
LANGUAGE plpgsql STABLE SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
DECLARE v_question RECORD; v_meta JSONB; v_source_note JSONB; v_expected_answer_data JSONB;
BEGIN
  IF p_question_id IS NULL OR p_question_source_id IS NULL OR p_source_note_id IS NULL
     OR p_mapping_version IS NULL OR p_source_hash IS NULL
     OR octet_length(p_source_hash) <> 64 OR p_source_hash !~ '^[0-9a-f]{64}$' THEN RETURN FALSE; END IF;
  SELECT id,subject_id,title,question_type,options,difficulty,question_text,stem_md,
         correct_answer,answer_data,analysis_md,explanation INTO v_question
    FROM public.questions WHERE id=p_question_id;
  SELECT qs.source_note::jsonb INTO v_source_note
    FROM public.question_sources qs
   WHERE qs.id=p_question_source_id AND qs.question_id=p_question_id AND qs.source_type='note';
  IF NOT FOUND OR NOT EXISTS (
       SELECT 1 FROM public.legacy_note_migrations m
       WHERE m.source_note_id=p_source_note_id AND m.mapping_version=p_mapping_version
         AND m.target_question_id=p_question_id AND m.target_question_source_id=p_question_source_id
         AND m.source_hash=p_source_hash
     ) OR v_source_note->>'source_note_id' IS DISTINCT FROM p_source_note_id::text
     OR v_source_note->>'mapping_version' IS DISTINCT FROM p_mapping_version
     OR v_source_note->>'source_hash' IS DISTINCT FROM p_source_hash
     OR jsonb_typeof(v_source_note->'mirror_contract') IS DISTINCT FROM 'object'
     OR v_question.question_type IS NULL
     OR v_question.question_type::text NOT IN ('short_answer','single_choice','multiple_choice','true_false') THEN RETURN FALSE; END IF;
  v_meta := v_source_note->'mirror_contract';
  v_expected_answer_data := legacy_migration.legacy_question_answer_data_expected(
    v_question.question_type::text,
    v_meta->>'correct_answer');
  IF v_expected_answer_data IS NULL THEN RETURN FALSE; END IF;
  RETURN v_question.subject_id::text IS NOT DISTINCT FROM v_meta->>'subject_id'
     AND v_question.title IS NOT DISTINCT FROM v_meta->>'title'
     AND v_question.question_text IS NOT DISTINCT FROM v_meta->>'question_text'
     AND v_question.stem_md IS NOT DISTINCT FROM v_meta->>'stem_md'
     AND v_question.question_type::text IS NOT DISTINCT FROM v_meta->>'question_type'
     AND to_jsonb(v_question.options) IS NOT DISTINCT FROM v_meta->'options'
     AND v_question.difficulty::text IS NOT DISTINCT FROM v_meta->>'difficulty'
     AND to_jsonb(v_question.correct_answer) IS NOT DISTINCT FROM v_meta->'correct_answer'
     AND to_jsonb(v_question.answer_data) IS NOT DISTINCT FROM v_expected_answer_data
     AND v_question.analysis_md IS NOT DISTINCT FROM v_meta->>'analysis_md'
     AND v_question.explanation IS NOT DISTINCT FROM v_meta->>'explanation';
EXCEPTION WHEN insufficient_privilege THEN RAISE;
        WHEN others THEN RETURN FALSE;
END;
$$;

CREATE FUNCTION legacy_migration.legacy_question_answer_data_expected(
  p_question_type TEXT, p_correct_answer TEXT
) RETURNS JSONB
LANGUAGE plpgsql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
BEGIN
  IF p_question_type='true_false' THEN
    IF p_correct_answer='True' THEN RETURN '{"kind":"true_false","value":true}'::jsonb; END IF;
    IF p_correct_answer='False' THEN RETURN '{"kind":"true_false","value":false}'::jsonb; END IF;
    RETURN NULL;
  ELSIF p_question_type IN ('single_choice','multiple_choice','single','multiple') THEN
    IF p_correct_answer IS NULL THEN RETURN NULL; END IF;
    RETURN jsonb_build_object(
      'kind',CASE WHEN p_question_type IN ('single','single_choice') THEN 'single_choice' ELSE 'multiple_choice' END,
      'value', COALESCE((SELECT jsonb_agg(trim(v.value) ORDER BY v.ordinality)
                         FROM regexp_split_to_table(p_correct_answer,',')
                         WITH ORDINALITY AS v(value,ordinality)
                         WHERE trim(v.value)<>''),'[]'::jsonb));
  ELSIF p_question_type IN ('short_answer','essay') THEN
    IF p_correct_answer IS NULL OR btrim(p_correct_answer)='' THEN RETURN NULL; END IF;
    RETURN jsonb_build_object('kind',p_question_type,'value', p_correct_answer);
  END IF;
  RETURN NULL;
END;
$$;

CREATE FUNCTION legacy_migration.legacy_question_options_normalize(p_options JSONB)
RETURNS JSONB
LANGUAGE plpgsql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
DECLARE v_result JSONB;
BEGIN
  IF p_options IS NULL OR jsonb_typeof(p_options) <> 'array' THEN RETURN NULL; END IF;
  IF jsonb_array_length(p_options)=0 THEN RETURN '[]'::jsonb; END IF;
  -- Current source-of-truth rule: QuestionDraft stores list[str]; conversion
  -- stores [{key: chr(65+ordinal), text: value}] in Question.options.
  SELECT jsonb_agg(
    CASE
      WHEN jsonb_typeof(e.value)='string' THEN
        jsonb_build_object('key',pg_catalog.chr(64+e.ordinality::integer),
                           'text',e.value #>> '{}')
      WHEN jsonb_typeof(e.value)='object'
       AND jsonb_object_length(e.value)=2
       AND e.value ? 'key' AND e.value ? 'text'
       AND jsonb_typeof(e.value->'key')='string'
       AND jsonb_typeof(e.value->'text')='string' THEN
        jsonb_build_object('key',e.value->>'key','text',e.value->>'text')
      ELSE NULL
    END ORDER BY e.ordinality)
    INTO v_result
  FROM jsonb_array_elements(p_options) WITH ORDINALITY AS e(value,ordinality);
  IF v_result IS NULL OR EXISTS (
    SELECT 1 FROM jsonb_array_elements(p_options) AS e(value)
    WHERE jsonb_typeof(e.value) NOT IN ('object','string')
       OR (jsonb_typeof(e.value)='object' AND
           (jsonb_object_length(e.value)<>2 OR NOT (e.value ? 'key' AND e.value ? 'text')
            OR jsonb_typeof(e.value->'key')<>'string'
            OR jsonb_typeof(e.value->'text')<>'string'))
  ) THEN RETURN NULL; END IF;
  RETURN v_result;
END;
$$;

CREATE FUNCTION legacy_migration.legacy_uuid_or_null(p_value TEXT) RETURNS UUID
LANGUAGE plpgsql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog, legacy_migration
AS $$
BEGIN
  IF p_value IS NULL OR p_value !~
     '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
  THEN RETURN NULL; END IF;
  RETURN p_value::uuid;
EXCEPTION WHEN others THEN RETURN NULL;
END;
$$;

REVOKE ALL ON FUNCTION legacy_migration.legacy_uuid_or_null(TEXT)
  FROM PUBLIC, app_role;
GRANT EXECUTE ON FUNCTION legacy_migration.legacy_uuid_or_null(TEXT)
  TO legacy_note_adapter, legacy_note_verifier;

-- These statements are replayed after CREATE FUNCTION so ACL order is executable.
REVOKE ALL ON FUNCTION legacy_migration.legacy_question_source_matches(
  UUID,UUID,VARCHAR,VARCHAR,VARCHAR,VARCHAR,TEXT) FROM PUBLIC, app_role;
REVOKE ALL ON FUNCTION legacy_migration.legacy_question_mirror_matches(
  UUID,UUID,UUID,VARCHAR,TEXT) FROM PUBLIC, app_role;
REVOKE ALL ON FUNCTION legacy_migration.legacy_question_options_normalize(JSONB)
  FROM PUBLIC, app_role;
REVOKE ALL ON FUNCTION legacy_migration.legacy_question_answer_data_expected(TEXT,TEXT)
  FROM PUBLIC, app_role;
GRANT EXECUTE ON FUNCTION legacy_migration.legacy_question_source_matches(
  UUID,UUID,VARCHAR,VARCHAR,VARCHAR,VARCHAR,TEXT) TO legacy_note_adapter,legacy_note_verifier;
GRANT EXECUTE ON FUNCTION legacy_migration.legacy_question_mirror_matches(
  UUID,UUID,UUID,VARCHAR,TEXT) TO legacy_note_adapter,legacy_note_verifier;
GRANT EXECUTE ON FUNCTION legacy_migration.legacy_question_options_normalize(JSONB)
  TO legacy_note_adapter,legacy_note_verifier;
GRANT EXECUTE ON FUNCTION legacy_migration.legacy_question_answer_data_expected(TEXT,TEXT)
  TO legacy_note_adapter,legacy_note_verifier;
-- SECURITY INVOKER helpers retain caller visibility: grant only columns read;
-- app_role receives neither these grants nor helper EXECUTE.
GRANT SELECT (id,source_type,source_ref,source_url,source_title,source_note,question_id)
  ON public.question_sources TO legacy_note_adapter, legacy_note_verifier;
GRANT SELECT (id,subject_id,title,question_type,options,difficulty,question_text,
  stem_md,correct_answer,answer_data,analysis_md,explanation)
  ON public.questions TO legacy_note_adapter, legacy_note_verifier;
GRANT SELECT (id,source_note_id,mapping_version,target_question_id,
  target_question_source_id,source_hash)
  ON public.legacy_note_migrations TO legacy_note_adapter, legacy_note_verifier;
-- Permission errors are intentionally re-raised by helpers, never converted to
-- a false parity result that hides an ACL defect.
```

#### 8.10 Scoped SQL contract, deterministic mirrors and rollback assertions

以下是 LSR-03 唯一可执行 SQL 口径，覆盖前文历史示例。`lsr02_all_dispositions` 是当前 mapping version 的所有最终 disposition（含 `failed`/`rolled_back`），只供 row/disposition、rollback、source-parity 与 ordinary Note/Blog 排除检查；`lsr02_final_migrations` 仅含 `migrated_active|migrated_paused`，只供 target、approval、relation/orphan、schedule 与 replay 检查；`lsr02_retained_public_only` 只供 retained 的公开性/target-null/hash parity 检查。任何 target/approval 查询不得扫描 failed/rolled_back；任何 disposition/rollback 查询不得漏掉它们；pending 只在 transition precondition 查询中显式点名。所有视图和查询均以 `:mapping_version` 约束，空 scope 或 mapping manifest 缺失/重复必须 FAIL：

```sql
-- Isolated replay prerequisite only; never run by LSR-02 against production.
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
REVOKE EXECUTE ON FUNCTION public.digest(bytea,text), public.gen_random_uuid(),
  public.gen_random_bytes(integer) FROM PUBLIC, app_role;
REVOKE EXECUTE ON FUNCTION public.gen_random_uuid(), public.gen_random_bytes(integer)
  FROM legacy_note_verifier;
GRANT EXECUTE ON FUNCTION public.digest(bytea,text)
  TO legacy_migration_owner, legacy_note_adapter, legacy_note_verifier;
GRANT EXECUTE ON FUNCTION public.gen_random_uuid(), public.gen_random_bytes(integer)
  TO legacy_migration_owner, legacy_note_adapter;
-- verifier receives digest only: it can recompute hashes but cannot write tables or
-- generate UUID/random values; permission errors must remain visible to the test.
CREATE TEMP TABLE lsr02_run_manifest (
  run_id UUID PRIMARY KEY,
  mapping_version VARCHAR(64) NOT NULL,
  evaluation_time_utc TIMESTAMPTZ NOT NULL,
  source_snapshot_version VARCHAR(64) NOT NULL,
  archive_rowcount INTEGER NOT NULL CHECK (archive_rowcount > 0),
  archive_hash CHAR(64) NOT NULL CHECK (archive_hash ~ '^[0-9a-f]{64}$')
);
DO $$
DECLARE v_manifest_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_manifest_count FROM lsr02_run_manifest
   WHERE mapping_version=:mapping_version;
  IF v_manifest_count <> 1 THEN
    RAISE EXCEPTION 'LSR02_MAPPING_MANIFEST_MISSING_OR_DUPLICATE';
  END IF;
END $$;
-- LSR-03 must first assert COUNT(*)=1 for :mapping_version; the table deliberately
-- permits two run rows so duplicate-run fixtures cannot be hidden by a PK.
SELECT CASE WHEN COUNT(*)=1 THEN 0 ELSE 1 END AS fail
FROM lsr02_run_manifest WHERE mapping_version=:mapping_version;
-- Independent immutable archive row payload. This is the archive data relation;
-- it is deliberately separate from the expected-hash manifest below.
CREATE TEMP TABLE lsr02_archive_rows (
  mapping_version VARCHAR(64) NOT NULL,
  source_note_id UUID NOT NULL,
  source_slug VARCHAR(255) NOT NULL,
  source_title VARCHAR(500) NOT NULL,
  source_url VARCHAR(500) NOT NULL,
  source_status VARCHAR(20) NOT NULL,
  source_hidden BOOLEAN NOT NULL,
  source_revision INTEGER NOT NULL,
  source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
  legacy_review_json JSONB NOT NULL CHECK (jsonb_typeof(legacy_review_json)='object'),
  canonical_payload JSONB NOT NULL CHECK (jsonb_typeof(canonical_payload)='object'),
  PRIMARY KEY (mapping_version,source_note_id)
);
-- The archive manifest is an independent expected identity/hash relation; it
-- contains no copied payload, so same-table double-counting is impossible.
CREATE TEMP TABLE lsr02_archive_manifest (
  mapping_version VARCHAR(64) NOT NULL,
  source_note_id UUID NOT NULL,
  expected_source_hash CHAR(64) NOT NULL CHECK (expected_source_hash ~ '^[0-9a-f]{64}$'),
  expected_payload_digest CHAR(64) NOT NULL CHECK (expected_payload_digest ~ '^[0-9a-f]{64}$'),
  PRIMARY KEY (mapping_version,source_note_id)
);
-- Each relation is loaded independently from the immutable archive package:
-- archive_rows carries canonical payload/raw fields; archive_manifest carries
-- the separately reviewed expected hash set. Both are bound to snapshot below.
CREATE TEMP TABLE lsr02_source_snapshot (
  mapping_version VARCHAR(64) NOT NULL,
  source_snapshot_version VARCHAR(64) NOT NULL,
  archive_hash CHAR(64) NOT NULL CHECK (archive_hash ~ '^[0-9a-f]{64}$'),
  source_note_id UUID NOT NULL,
  content TEXT NOT NULL,
  title VARCHAR(500) NOT NULL, source_url VARCHAR(500) NOT NULL, type VARCHAR(32) NOT NULL CHECK (type='mistake'), created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL,
  summary TEXT NULL, cover TEXT NULL, category TEXT NULL, subject TEXT NULL,
  difficulty TEXT NULL, question TEXT NULL, answers JSONB NOT NULL CHECK (jsonb_typeof(answers)='object'), analysis TEXT NULL,
  knowledge_points JSONB NOT NULL CHECK (jsonb_typeof(knowledge_points)='array'), legacy_ef DOUBLE PRECISION NOT NULL CHECK (
    legacy_ef::text NOT IN ('NaN','Infinity','-Infinity')),
  legacy_ef_bits CHAR(16) NOT NULL CHECK (legacy_ef_bits ~ '^[0-9a-f]{16}$'),
  interval_value INTEGER NOT NULL CHECK (interval_value >= 0), repetitions INTEGER NOT NULL CHECK (repetitions >= 0), next_review DATE NULL,
  last_reviewed TIMESTAMP NULL, images JSONB NULL, ai_metadata JSONB NULL,
  folder_id UUID NULL, sort_order INTEGER NULL, tags JSONB NOT NULL CHECK (jsonb_typeof(tags)='array'),
  legacy_review_json JSONB NOT NULL CHECK (jsonb_typeof(legacy_review_json)='object'),
  slug VARCHAR(255) NOT NULL,
  status VARCHAR(20) NOT NULL,
  hidden BOOLEAN NOT NULL,
  revision INTEGER NOT NULL CHECK (revision > 0),
  search_vector_token TEXT NOT NULL,
  canonical_payload JSONB NOT NULL CHECK (jsonb_typeof(canonical_payload) = 'object'),
  source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
  PRIMARY KEY (mapping_version, source_note_id),
  UNIQUE (mapping_version, source_note_id, source_hash)
);
-- The authorized LSR-03 loader uses the immutable archive bytes only, loading
-- archive_rows and archive_manifest independently, then loading snapshot from
-- the same immutable bytes for a third, typed projection:
-- COPY lsr02_source_snapshot(mapping_version,source_snapshot_version,archive_hash,
--   source_note_id,content,title,source_url,type,created_at,updated_at,summary,cover,category,
--   subject,difficulty,question,answers,analysis,knowledge_points,legacy_ef,legacy_ef_bits,
--   interval_value,repetitions,next_review,last_reviewed,images,ai_metadata,folder_id,
--   sort_order,tags,legacy_review_json,slug,status,hidden,revision,search_vector_token,canonical_payload,source_hash)
-- FROM STDIN WITH (FORMAT csv, HEADER true);
-- No live Note query populates this table; manifest hash/version/rowcount are checked below.
SELECT COUNT(*) FROM lsr02_source_snapshot
 WHERE mapping_version=:mapping_version;
SELECT COUNT(*) FROM lsr02_source_snapshot s
JOIN lsr02_run_manifest run ON run.mapping_version=s.mapping_version
 WHERE s.mapping_version=:mapping_version
   AND s.source_snapshot_version IS DISTINCT FROM run.source_snapshot_version;
SELECT COUNT(*) FROM lsr02_source_snapshot s
JOIN lsr02_run_manifest run ON run.mapping_version=s.mapping_version
 WHERE s.mapping_version=:mapping_version
   AND s.archive_hash IS DISTINCT FROM run.archive_hash;
SELECT COUNT(*) FROM lsr02_source_snapshot
 WHERE mapping_version=:mapping_version AND source_hash !~ '^[0-9a-f]{64}$';
SELECT s.source_note_id
FROM lsr02_source_snapshot s
WHERE s.mapping_version=:mapping_version
  AND pg_catalog.encode(public.digest(pg_catalog.convert_to(s.canonical_payload::text,'UTF8'),'sha256'),'hex')
      IS DISTINCT FROM s.source_hash;
SELECT s.source_note_id
FROM lsr02_source_snapshot s
JOIN lsr02_archive_rows a
  ON a.mapping_version=s.mapping_version AND a.source_note_id=s.source_note_id
WHERE s.mapping_version=:mapping_version
   AND (a.source_hash IS DISTINCT FROM s.source_hash
   OR a.legacy_review_json IS DISTINCT FROM s.legacy_review_json
   OR a.canonical_payload IS DISTINCT FROM s.canonical_payload
   OR a.canonical_payload->>'id' IS DISTINCT FROM a.source_note_id::text
   OR a.canonical_payload->>'source_note_id' IS DISTINCT FROM a.source_note_id::text);
SELECT s.source_note_id
FROM lsr02_source_snapshot s
JOIN lsr02_archive_manifest am
  ON am.mapping_version=s.mapping_version AND am.source_note_id=s.source_note_id
WHERE s.mapping_version=:mapping_version
  AND (am.expected_source_hash IS DISTINCT FROM s.source_hash
    OR am.expected_payload_digest IS DISTINCT FROM
       pg_catalog.encode(public.digest(pg_catalog.convert_to(s.canonical_payload::text,'UTF8'),'sha256'),'hex'));
SELECT a.source_note_id
FROM lsr02_archive_rows a
WHERE a.mapping_version=:mapping_version
  AND pg_catalog.encode(public.digest(pg_catalog.convert_to(a.canonical_payload::text,'UTF8'),'sha256'),'hex')
      IS DISTINCT FROM a.source_hash;
SELECT a.source_note_id
FROM lsr02_archive_rows a
JOIN lsr02_archive_manifest am
  ON am.mapping_version=a.mapping_version AND am.source_note_id=a.source_note_id
WHERE a.mapping_version=:mapping_version
  AND (am.expected_source_hash IS DISTINCT FROM a.source_hash
    OR am.expected_payload_digest IS DISTINCT FROM
       pg_catalog.encode(public.digest(pg_catalog.convert_to(a.canonical_payload::text,'UTF8'),'sha256'),'hex'));
SELECT s.source_note_id
FROM lsr02_source_snapshot s
LEFT JOIN lsr02_archive_rows a
  ON a.mapping_version=s.mapping_version AND a.source_note_id=s.source_note_id
WHERE s.mapping_version=:mapping_version AND a.source_note_id IS NULL;
SELECT a.source_note_id
FROM lsr02_archive_rows a
LEFT JOIN lsr02_source_snapshot s
  ON s.mapping_version=a.mapping_version AND s.source_note_id=a.source_note_id
WHERE a.mapping_version=:mapping_version AND s.source_note_id IS NULL;
SELECT am.source_note_id
FROM lsr02_archive_manifest am
LEFT JOIN lsr02_archive_rows a
  ON a.mapping_version=am.mapping_version AND a.source_note_id=am.source_note_id
WHERE am.mapping_version=:mapping_version AND a.source_note_id IS NULL;
SELECT source_note_id FROM lsr02_archive_rows WHERE mapping_version=:mapping_version
EXCEPT SELECT source_note_id FROM lsr02_source_snapshot WHERE mapping_version=:mapping_version;
SELECT source_note_id FROM lsr02_source_snapshot WHERE mapping_version=:mapping_version
EXCEPT SELECT source_note_id FROM lsr02_archive_rows WHERE mapping_version=:mapping_version;
SELECT source_note_id FROM lsr02_archive_manifest WHERE mapping_version=:mapping_version
EXCEPT SELECT source_note_id FROM lsr02_archive_rows WHERE mapping_version=:mapping_version;
SELECT source_note_id FROM lsr02_archive_rows WHERE mapping_version=:mapping_version
EXCEPT SELECT source_note_id FROM lsr02_archive_manifest WHERE mapping_version=:mapping_version;
CREATE TEMP TABLE lsr02_required_payload_keys (
  key TEXT PRIMARY KEY, expected_types TEXT[] NOT NULL
);
INSERT INTO lsr02_required_payload_keys VALUES
 ('id',ARRAY['string']),('source_note_id',ARRAY['string']),('slug',ARRAY['string']),('source_url',ARRAY['string']),('title',ARRAY['string']),
 ('content',ARRAY['string']),('type',ARRAY['string']),('status',ARRAY['string']),
 ('hidden',ARRAY['boolean']),('created_at',ARRAY['string']),('updated_at',ARRAY['string']),
 ('summary',ARRAY['string','null']),('cover',ARRAY['string','null']),('category',ARRAY['string','null']),
 ('subject',ARRAY['string','null']),('difficulty',ARRAY['string','null']),('question',ARRAY['string','null']),
 ('answers',ARRAY['object']),('analysis',ARRAY['string','null']),('knowledge_points',ARRAY['array']),
 ('ef',ARRAY['number']),('legacy_ef_bits',ARRAY['string']),('interval',ARRAY['number']),
 ('repetitions',ARRAY['number']),('next_review',ARRAY['string','null']),('last_reviewed',ARRAY['string','null']),
 ('images',ARRAY['array','null']),('ai_metadata',ARRAY['object','null']),('folder_id',ARRAY['string','null']),
 ('sort_order',ARRAY['number','null']),('revision',ARRAY['number']),('tags',ARRAY['array']),
 ('search_vector_token',ARRAY['string']),('legacy_review_json',ARRAY['object']);
SELECT s.source_note_id,k.key
FROM lsr02_source_snapshot s CROSS JOIN lsr02_required_payload_keys k
WHERE s.mapping_version=:mapping_version
  AND (NOT (s.canonical_payload ? k.key)
   OR NOT (jsonb_typeof(s.canonical_payload->k.key)=ANY(k.expected_types)));
-- Row binding is fail-closed: an internally self-consistent payload for another
-- Note is still invalid. The typed archive projection and locked live Note must
-- agree field-by-field, including the independent EF bit key and search sentinel.
SELECT s.source_note_id
FROM lsr02_source_snapshot s JOIN notes n ON n.id=s.source_note_id
WHERE s.mapping_version=:mapping_version
  AND (s.canonical_payload->>'id' IS DISTINCT FROM s.source_note_id::text
   OR s.canonical_payload->>'source_note_id' IS DISTINCT FROM s.source_note_id::text
   OR s.canonical_payload->>'type' IS DISTINCT FROM 'mistake'
   OR s.canonical_payload->>'slug' IS DISTINCT FROM s.slug
   OR s.canonical_payload->>'source_url' IS DISTINCT FROM s.source_url
   OR s.canonical_payload->>'title' IS DISTINCT FROM s.title
   OR s.canonical_payload->>'content' IS DISTINCT FROM s.content
   OR s.canonical_payload->>'status' IS DISTINCT FROM s.status
   OR s.canonical_payload->'hidden' IS DISTINCT FROM to_jsonb(s.hidden)
   OR s.canonical_payload->>'created_at' IS DISTINCT FROM to_char(s.created_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')
   OR s.canonical_payload->>'updated_at' IS DISTINCT FROM to_char(s.updated_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')
   OR s.canonical_payload->'answers' IS DISTINCT FROM s.answers
   OR s.canonical_payload->>'legacy_ef_bits' IS DISTINCT FROM s.legacy_ef_bits::text
   OR s.canonical_payload->>'search_vector_token' IS DISTINCT FROM s.search_vector_token
   OR n.slug IS DISTINCT FROM s.slug OR n.status IS DISTINCT FROM s.status
   OR n.hidden IS DISTINCT FROM s.hidden OR n.revision IS DISTINCT FROM s.revision);
-- The live source is locked before this comparison in the adapter/replay
-- transaction; all scalar Note columns below are bound, not inferred from slug.
SELECT n.id
FROM notes n JOIN lsr02_source_snapshot s ON s.source_note_id=n.id
WHERE s.mapping_version=:mapping_version
  AND (to_jsonb(n.id) IS DISTINCT FROM s.canonical_payload->'id'
   OR to_jsonb(n.id) IS DISTINCT FROM s.canonical_payload->'source_note_id'
   OR to_jsonb(n.slug) IS DISTINCT FROM s.canonical_payload->'slug'
   OR to_jsonb(n.title) IS DISTINCT FROM s.canonical_payload->'title'
   OR to_jsonb(n.content) IS DISTINCT FROM s.canonical_payload->'content'
   OR to_jsonb(n.type) IS DISTINCT FROM s.canonical_payload->'type'
   OR to_jsonb(n.status) IS DISTINCT FROM s.canonical_payload->'status'
   OR to_jsonb(n.hidden) IS DISTINCT FROM s.canonical_payload->'hidden'
   OR to_jsonb(to_char(n.created_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'))
      IS DISTINCT FROM s.canonical_payload->'created_at'
   OR to_jsonb(to_char(n.updated_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'))
      IS DISTINCT FROM s.canonical_payload->'updated_at'
   OR to_jsonb(n.summary) IS DISTINCT FROM s.canonical_payload->'summary'
   OR to_jsonb(n.cover) IS DISTINCT FROM s.canonical_payload->'cover'
   OR to_jsonb(n.category) IS DISTINCT FROM s.canonical_payload->'category'
   OR to_jsonb(n.subject) IS DISTINCT FROM s.canonical_payload->'subject'
   OR to_jsonb(n.difficulty) IS DISTINCT FROM s.canonical_payload->'difficulty'
   OR to_jsonb(n.question) IS DISTINCT FROM s.canonical_payload->'question'
   OR jsonb_build_object('my_answer',n.my_answer,'correct_answer',n.correct_answer)
      IS DISTINCT FROM s.canonical_payload->'answers'
   OR to_jsonb(n.analysis) IS DISTINCT FROM s.canonical_payload->'analysis'
   OR to_jsonb(n.ef) IS DISTINCT FROM s.canonical_payload->'ef'
   OR to_jsonb(n.interval) IS DISTINCT FROM s.canonical_payload->'interval'
   OR to_jsonb(n.repetitions) IS DISTINCT FROM s.canonical_payload->'repetitions'
   OR to_jsonb(n.next_review) IS DISTINCT FROM s.canonical_payload->'next_review'
   OR to_jsonb(to_char(n.last_reviewed AT TIME ZONE 'UTC',
                       'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'))
        IS DISTINCT FROM s.canonical_payload->'last_reviewed'
   OR to_jsonb(n.images) IS DISTINCT FROM s.canonical_payload->'images'
   OR to_jsonb(n.ai_metadata) IS DISTINCT FROM s.canonical_payload->'ai_metadata'
   OR to_jsonb(n.folder_id) IS DISTINCT FROM s.canonical_payload->'folder_id'
   OR to_jsonb(n.sort_order) IS DISTINCT FROM s.canonical_payload->'sort_order'
   OR to_jsonb(n.revision) IS DISTINCT FROM s.canonical_payload->'revision'
   OR s.canonical_payload->'knowledge_points' IS DISTINCT FROM COALESCE((
      SELECT jsonb_agg(trim(p.value) ORDER BY p.ordinality)
      FROM regexp_split_to_table(
        replace(replace(replace(replace(COALESCE(n.knowledge_points,''),'，',','),'、',','),E'\n',','),'；',','), ',')
        WITH ORDINALITY AS p(value,ordinality)
      WHERE trim(p.value) <> ''), '[]'::jsonb)
   OR s.canonical_payload->'tags' IS DISTINCT FROM COALESCE((
      SELECT jsonb_agg(to_jsonb(t.name) ORDER BY t.id,t.name)
      FROM note_tags nt JOIN tags t ON t.id=nt.tag_id WHERE nt.note_id=n.id), '[]'::jsonb));
SELECT s.source_note_id
FROM lsr02_source_snapshot s
WHERE s.mapping_version=:mapping_version
  AND s.canonical_payload IS DISTINCT FROM jsonb_build_object(
  'id',s.source_note_id,'source_note_id',s.source_note_id,'slug',s.slug,'source_url',s.source_url,'title',s.title,'content',s.content,'type',s.type,
  'status',s.status,'hidden',s.hidden,
  'created_at',to_char(s.created_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
  'updated_at',to_char(s.updated_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
  'summary',s.summary,'cover',s.cover,'category',s.category,'subject',s.subject,
  'difficulty',s.difficulty,'question',s.question,'answers',s.answers,'analysis',s.analysis,
  'knowledge_points',s.knowledge_points,'ef',s.legacy_ef,'legacy_ef_bits',s.legacy_ef_bits::text,
  'interval',s.interval_value,'repetitions',s.repetitions,
  'next_review',to_char(s.next_review,'YYYY-MM-DD'),
  'last_reviewed',to_char(s.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
  'images',s.images,'ai_metadata',s.ai_metadata,
  'folder_id',s.folder_id,'sort_order',s.sort_order,'revision',s.revision,'tags',s.tags,
  'search_vector_token',s.search_vector_token,'legacy_review_json',s.legacy_review_json);
-- Typed snapshot/archive/ledger review fields must expose the same canonical
-- UTC-microsecond text; no direct timestamp-to-JSON comparison is accepted.
SELECT s.source_note_id
FROM lsr02_source_snapshot s
WHERE s.mapping_version=:mapping_version
  AND s.canonical_payload->>'last_reviewed' IS DISTINCT FROM
      to_char(s.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"');
SELECT a.source_note_id
FROM lsr02_archive_rows a
WHERE a.mapping_version=:mapping_version
  AND a.canonical_payload->>'last_reviewed' IS DISTINCT FROM
      to_char((a.canonical_payload->>'last_reviewed')::timestamptz AT TIME ZONE 'UTC',
              'YYYY-MM-DD"T"HH24:MI:SS.US"Z"');
SELECT s.source_note_id
FROM lsr02_source_snapshot s
WHERE s.mapping_version=:mapping_version
  AND s.legacy_ef_bits IS DISTINCT FROM pg_catalog.encode(pg_catalog.float8send(s.legacy_ef),'hex');
SELECT s.source_note_id
FROM lsr02_source_snapshot s
WHERE s.mapping_version=:mapping_version
  AND s.legacy_ef::text IN ('NaN','Infinity','-Infinity');
SELECT m.id
FROM lsr02_all_dispositions m
WHERE m.state IN ('ready','migrated_active','migrated_paused')
  AND m.mapping_version=:mapping_version
  AND m.legacy_ef::text IN ('NaN','Infinity','-Infinity');
SELECT m.id
FROM lsr02_all_dispositions m
WHERE m.state IN ('ready','migrated_active','migrated_paused')
  AND m.mapping_version=:mapping_version
  AND length(m.source_title) > 300;
SELECT s.mapping_version
FROM lsr02_source_snapshot s
JOIN lsr02_run_manifest run ON run.mapping_version=s.mapping_version
WHERE s.mapping_version=:mapping_version
GROUP BY s.mapping_version, run.archive_rowcount
HAVING COUNT(*) IS DISTINCT FROM run.archive_rowcount;
SELECT run.mapping_version
FROM lsr02_run_manifest run
LEFT JOIN lsr02_source_snapshot s ON s.mapping_version=run.mapping_version
WHERE run.mapping_version=:mapping_version
GROUP BY run.mapping_version,run.archive_hash
HAVING pg_catalog.encode(public.digest(pg_catalog.convert_to(
  COALESCE(string_agg(s.source_hash,',' ORDER BY s.source_note_id::text),'')::text,'UTF8'),'sha256'),'hex')
  IS DISTINCT FROM run.archive_hash;
SELECT run.mapping_version
FROM lsr02_run_manifest run
LEFT JOIN lsr02_archive_rows a ON a.mapping_version=run.mapping_version
WHERE run.mapping_version=:mapping_version
GROUP BY run.mapping_version,run.archive_rowcount,run.archive_hash
HAVING COUNT(a.source_note_id) IS DISTINCT FROM run.archive_rowcount
    OR pg_catalog.encode(public.digest(pg_catalog.convert_to(
         COALESCE(string_agg(a.source_hash,',' ORDER BY a.source_note_id::text),'')::text,'UTF8'),'sha256'),'hex')
       IS DISTINCT FROM run.archive_hash;
SELECT run.mapping_version
FROM lsr02_run_manifest run
LEFT JOIN lsr02_archive_manifest am ON am.mapping_version=run.mapping_version
WHERE run.mapping_version=:mapping_version
GROUP BY run.mapping_version,run.archive_rowcount
HAVING COUNT(am.source_note_id) IS DISTINCT FROM run.archive_rowcount;
-- The rowcount mismatch query and all other validation counts must return zero.
CREATE TEMP TABLE lsr02_replay_manifest (
  mapping_version VARCHAR(64) NOT NULL,
  source_note_id UUID NOT NULL,
  source_hash CHAR(64) NOT NULL,
  ledger_id UUID NOT NULL,
  state public.legacy_note_migration_state NOT NULL,
  target_question_draft_item_id UUID NULL,
  target_question_draft_id UUID NULL,
  target_question_source_id UUID NULL,
  target_question_id UUID NULL,
  target_qkp_ids INTEGER[] NULL,
  target_mistake_draft_item_id UUID NULL,
  target_mistake_draft_id UUID NULL,
  target_mistake_id UUID NULL,
  target_projection_ids INTEGER[] NULL,
  target_review_item_id UUID NULL,
  source_approved_by UUID NULL,
  source_approved_at TIMESTAMPTZ NULL,
  source_approval_sequence INTEGER NULL,
  source_approval_event_id UUID NULL,
  question_conversion_approved_by UUID NULL,
  question_conversion_approved_at TIMESTAMPTZ NULL,
  question_conversion_sequence INTEGER NULL,
  question_approval_event_id UUID NULL,
  mistake_conversion_approved_by UUID NULL,
  mistake_conversion_approved_at TIMESTAMPTZ NULL,
  mistake_conversion_sequence INTEGER NULL,
  mistake_approval_event_id UUID NULL,
  schedule_approved_by UUID NULL,
  schedule_approved_at TIMESTAMPTZ NULL,
  schedule_approval_sequence INTEGER NULL,
  schedule_approval_event_id UUID NULL,
  transition_event_id UUID NULL,
  rollback_actor_id UUID NULL,
  rollback_event_id UUID NULL,
  rollback_reference CHAR(64) NULL,
  target_bundle_hash CHAR(64) NOT NULL,
  PRIMARY KEY (mapping_version, source_note_id)
);
-- Loader supplies the first successful replay identity; changed hash or any ID mismatch is FAIL.

-- Rollback replay is an independent negative/restore audit run.  It is not
-- filtered through the positive final replay: every rolled_back ledger row in
-- this mapping version must have one manifest row and one matching rollback
-- event plus immutable rollback-audit digest.
CREATE TEMP TABLE lsr02_rollback_replay_manifest (
  mapping_version VARCHAR(64) NOT NULL,
  source_note_id UUID NOT NULL,
  source_hash CHAR(64) NOT NULL,
  ledger_id UUID NOT NULL,
  state public.legacy_note_migration_state NOT NULL CHECK (state='rolled_back'),
  rollback_actor_id UUID NOT NULL,
  rollback_event_id UUID NOT NULL,
  rollback_reference CHAR(64) NOT NULL CHECK (rollback_reference ~ '^[0-9a-f]{64}$'),
  rollback_hash CHAR(64) NOT NULL CHECK (rollback_hash ~ '^[0-9a-f]{64}$'),
  transition_event_id UUID NULL,
  rollback_audit_digest CHAR(64) NOT NULL CHECK (rollback_audit_digest ~ '^[0-9a-f]{64}$'),
  PRIMARY KEY (mapping_version,source_note_id)
);
CREATE OR REPLACE TEMP VIEW lsr02_rollback_ledger AS
  SELECT m.mapping_version,m.source_note_id,m.source_hash,m.id AS ledger_id,m.state,
         m.rollback_actor_id,m.rollback_event_id,m.rollback_reference,
         m.transition_event_id,e.rollback_hash,
         a.rollback_reference AS rollback_audit_digest
    FROM public.legacy_note_migrations m
    LEFT JOIN public.legacy_note_migration_events e
      ON e.id=m.rollback_event_id AND e.ledger_id=m.id
     AND e.source_note_id=m.source_note_id AND e.mapping_version=m.mapping_version
     AND e.source_hash=m.source_hash AND e.approval_kind='rollback'
    LEFT JOIN public.legacy_migration_rollback_audits a
      ON a.ledger_id=m.id AND a.source_note_id=m.source_note_id
     AND a.mapping_version=m.mapping_version AND a.source_hash=m.source_hash
   WHERE m.mapping_version=:mapping_version AND m.state='rolled_back';
DO $$
DECLARE v_db_count INTEGER; v_replay_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_db_count FROM lsr02_rollback_ledger;
  SELECT COUNT(*) INTO v_replay_count FROM lsr02_rollback_replay_manifest
   WHERE mapping_version=:mapping_version;
  IF v_db_count <= 0 OR v_replay_count <= 0 OR v_db_count <> v_replay_count THEN
    RAISE EXCEPTION 'LSR02_ROLLBACK_REPLAY_EMPTY_OR_COUNT_MISMATCH';
  END IF;
END $$;
SELECT COALESCE(db.source_note_id,replay.source_note_id) AS source_note_id,
       COALESCE(db.mapping_version,replay.mapping_version) AS mapping_version
  FROM lsr02_rollback_ledger db
  FULL OUTER JOIN lsr02_rollback_replay_manifest replay
    ON replay.mapping_version=db.mapping_version
   AND replay.source_note_id=db.source_note_id
 WHERE db.source_note_id IS NULL OR replay.source_note_id IS NULL;
SELECT COALESCE(db.source_note_id,replay.source_note_id) AS source_note_id
  FROM lsr02_rollback_ledger db
  FULL OUTER JOIN lsr02_rollback_replay_manifest replay
    ON replay.mapping_version=db.mapping_version
   AND replay.source_note_id=db.source_note_id
 WHERE db.source_note_id IS NULL OR replay.source_note_id IS NULL
    OR db.source_hash IS DISTINCT FROM replay.source_hash
    OR db.ledger_id IS DISTINCT FROM replay.ledger_id
    OR db.state IS DISTINCT FROM replay.state
    OR db.rollback_actor_id IS DISTINCT FROM replay.rollback_actor_id
    OR db.rollback_event_id IS DISTINCT FROM replay.rollback_event_id
    OR db.rollback_reference IS DISTINCT FROM replay.rollback_reference
    OR db.rollback_hash IS DISTINCT FROM replay.rollback_hash
    OR db.transition_event_id IS DISTINCT FROM replay.transition_event_id
    OR db.rollback_audit_digest IS DISTINCT FROM replay.rollback_audit_digest
    OR db.mapping_version IS DISTINCT FROM replay.mapping_version;
-- Both directions are explicit; a missing/extra rolled_back source cannot
-- disappear behind an INNER JOIN or a positive-scope filter.
SELECT source_note_id FROM lsr02_rollback_ledger
EXCEPT SELECT source_note_id FROM lsr02_rollback_replay_manifest
 WHERE mapping_version=:mapping_version;
SELECT source_note_id FROM lsr02_rollback_replay_manifest
 WHERE mapping_version=:mapping_version
EXCEPT SELECT source_note_id FROM lsr02_rollback_ledger;

CREATE OR REPLACE TEMP VIEW lsr02_all_dispositions AS
  SELECT m.* FROM legacy_note_migrations m
  WHERE m.mapping_version = :mapping_version
    AND m.state IN ('migrated_active','migrated_paused','retained_public_only','failed','rolled_back');
CREATE OR REPLACE TEMP VIEW lsr02_final_migrations AS
  SELECT m.* FROM lsr02_all_dispositions m
  WHERE m.state IN ('migrated_active','migrated_paused');
CREATE OR REPLACE TEMP VIEW lsr02_retained_public_only AS
  SELECT m.* FROM lsr02_all_dispositions m
  WHERE m.state='retained_public_only';
SELECT m.source_note_id FROM lsr02_final_migrations m
LEFT JOIN lsr02_source_snapshot s
  ON s.mapping_version=m.mapping_version AND s.source_note_id=m.source_note_id
WHERE s.source_note_id IS NULL;
SELECT m.source_note_id
FROM lsr02_all_dispositions m
LEFT JOIN lsr02_source_snapshot s
  ON s.mapping_version=m.mapping_version AND s.source_note_id=m.source_note_id
WHERE s.source_note_id IS NULL;
SELECT m.id
FROM lsr02_final_migrations m
JOIN lsr02_source_snapshot s
  ON s.mapping_version=m.mapping_version AND s.source_note_id=m.source_note_id
WHERE m.source_hash IS DISTINCT FROM s.source_hash;
SELECT m.id
FROM lsr02_all_dispositions m
JOIN lsr02_source_snapshot s
  ON s.mapping_version=m.mapping_version AND s.source_note_id=m.source_note_id
WHERE m.source_slug IS DISTINCT FROM s.slug
   OR m.source_title IS DISTINCT FROM s.title
   OR m.source_url IS DISTINCT FROM s.source_url
   OR m.source_status IS DISTINCT FROM s.status
   OR m.source_hidden IS DISTINCT FROM s.hidden
   OR m.source_revision IS DISTINCT FROM s.revision
   OR m.legacy_interval IS DISTINCT FROM s.interval_value
   OR m.legacy_repetitions IS DISTINCT FROM s.repetitions
   OR m.legacy_next_review IS DISTINCT FROM s.next_review
   OR m.legacy_last_reviewed IS DISTINCT FROM s.last_reviewed
   OR m.legacy_ef IS DISTINCT FROM s.legacy_ef
   OR m.legacy_ef_bits::text IS DISTINCT FROM s.legacy_ef_bits::text
   OR m.legacy_review_json IS DISTINCT FROM s.legacy_review_json;
-- LSR-03 loads the immutable archive into this temp relation before running the assertions.
-- Required columns: source_note_id, content, slug, status, hidden, revision,
-- search_vector_token, canonical_payload, source_hash.
-- This live-source relation is loaded independently from public.notes; it is not
-- derived from a ledger/disposition or from the archive. The mapping-version
-- bind only labels this acceptance run, while Note.type supplies the source set.
CREATE OR REPLACE TEMP VIEW lsr02_live_source_scope AS
  SELECT :mapping_version::VARCHAR(64) AS mapping_version,
         n.id AS source_note_id, n.type, n.slug, n.status, n.hidden, n.revision
  FROM public.notes n
  WHERE n.type='mistake';
CREATE OR REPLACE TEMP VIEW lsr02_source_scope AS
  SELECT m.*, n.id AS live_source_note_id, n.content, n.slug, n.status, n.hidden, n.revision,
         n.search_vector,
         CASE WHEN n.search_vector IS NULL THEN '<NULL>'
              ELSE '<VALUE>' || n.search_vector::text END AS search_vector_token,
         s.content AS snapshot_content, s.slug AS snapshot_slug, s.status AS snapshot_status,
         s.hidden AS snapshot_hidden, s.revision AS snapshot_revision,
         s.source_url AS snapshot_source_url, s.legacy_review_json AS snapshot_legacy_review_json,
         s.search_vector_token AS snapshot_search_vector_token,
         s.canonical_payload AS snapshot_canonical_payload,
         s.source_hash AS snapshot_source_hash
  FROM lsr02_source_snapshot s
  JOIN notes n ON n.id=s.source_note_id AND n.type='mistake'
  LEFT JOIN lsr02_all_dispositions m
    ON m.mapping_version=s.mapping_version AND m.source_note_id=s.source_note_id
  WHERE s.mapping_version=:mapping_version;
DO $$
DECLARE v_run RECORD; v_snapshot_count INTEGER; v_archive_count INTEGER;
        v_archive_manifest_count INTEGER; v_disposition_count INTEGER;
        v_source_count INTEGER; v_failed_count INTEGER; v_nonfinal_count INTEGER;
BEGIN
  SELECT * INTO v_run FROM lsr02_run_manifest
   WHERE mapping_version=:mapping_version;
  IF NOT FOUND OR v_run.archive_rowcount <= 0 THEN
    RAISE EXCEPTION 'LSR02_ACCEPTANCE_RUN_EMPTY_OR_MANIFEST_INVALID';
  END IF;
  SELECT COUNT(*) INTO v_snapshot_count FROM lsr02_source_snapshot
   WHERE mapping_version=:mapping_version;
  SELECT COUNT(*) INTO v_archive_count FROM lsr02_archive_rows
   WHERE mapping_version=:mapping_version;
  SELECT COUNT(*) INTO v_archive_manifest_count FROM lsr02_archive_manifest
   WHERE mapping_version=:mapping_version;
  SELECT COUNT(*) INTO v_disposition_count FROM lsr02_all_dispositions
   WHERE mapping_version=:mapping_version;
  SELECT COUNT(*) INTO v_source_count FROM lsr02_live_source_scope
   WHERE mapping_version=:mapping_version;
  SELECT COUNT(*) INTO v_failed_count FROM lsr02_all_dispositions
   WHERE mapping_version=:mapping_version AND state='failed';
  SELECT COUNT(*) INTO v_nonfinal_count FROM lsr02_all_dispositions
   WHERE mapping_version=:mapping_version
     AND state NOT IN ('migrated_active','migrated_paused','retained_public_only');
  IF v_snapshot_count <= 0 OR v_archive_count <= 0
     OR v_archive_manifest_count <= 0 OR v_disposition_count <= 0 OR v_source_count <= 0
     OR v_snapshot_count <> v_run.archive_rowcount
     OR v_archive_count <> v_run.archive_rowcount
     OR v_archive_manifest_count <> v_run.archive_rowcount
     OR v_disposition_count <> v_run.archive_rowcount
     OR v_source_count <> v_run.archive_rowcount
     OR EXISTS (SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_all_dispositions
                WHERE mapping_version=:mapping_version)
     OR EXISTS (SELECT source_note_id FROM lsr02_all_dispositions
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version)
     OR EXISTS (SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_source_snapshot
                WHERE mapping_version=:mapping_version)
     OR EXISTS (SELECT source_note_id FROM lsr02_source_snapshot
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version)
     OR EXISTS (SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_archive_rows
                WHERE mapping_version=:mapping_version)
     OR EXISTS (SELECT source_note_id FROM lsr02_archive_rows
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version)
     OR EXISTS (SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_archive_manifest
                WHERE mapping_version=:mapping_version)
     OR EXISTS (SELECT source_note_id FROM lsr02_archive_manifest
                WHERE mapping_version=:mapping_version
                EXCEPT SELECT source_note_id FROM lsr02_live_source_scope
                WHERE mapping_version=:mapping_version) THEN
    RAISE EXCEPTION 'LSR02_ACCEPTANCE_SCOPE_EMPTY_OR_ROWCOUNT_MISMATCH';
  END IF;
  -- failed/rolled_back are legal all-dispositions records, but never a final
  -- success.  Keep them counted above, then fail the acceptance run explicitly
  -- instead of allowing a failed-only or rolled-back-only batch to masquerade
  -- as migrated_active/paused/retained success.
  IF v_failed_count > 0 OR v_nonfinal_count > 0 THEN
    RAISE EXCEPTION 'LSR02_ACCEPTANCE_NONFINAL_DISPOSITION';
  END IF;
END $$;
SELECT state, COUNT(*) FROM lsr02_final_migrations GROUP BY state;
SELECT m.source_note_id, COUNT(*) AS final_disposition_count
FROM lsr02_all_dispositions m
JOIN notes n ON n.id=m.source_note_id
WHERE n.type='mistake'
  AND m.state IN ('migrated_active','migrated_paused','retained_public_only','failed','rolled_back')
GROUP BY m.source_note_id
HAVING COUNT(*) <> 1;
SELECT 'source' AS kind, COUNT(*) FROM lsr02_live_source_scope
UNION ALL SELECT 'question', COUNT(*) FROM lsr02_final_migrations WHERE target_question_id IS NOT NULL
UNION ALL SELECT 'mistake', COUNT(*) FROM lsr02_final_migrations WHERE target_mistake_id IS NOT NULL
UNION ALL SELECT 'review', COUNT(*) FROM lsr02_final_migrations WHERE state='migrated_active' AND target_review_item_id IS NOT NULL
UNION ALL SELECT 'question_draft_item', COUNT(*) FROM lsr02_final_migrations WHERE target_question_draft_item_id IS NOT NULL
UNION ALL SELECT 'question_draft', COUNT(*) FROM lsr02_final_migrations WHERE target_question_draft_id IS NOT NULL
UNION ALL SELECT 'mistake_draft_item', COUNT(*) FROM lsr02_final_migrations WHERE target_mistake_draft_item_id IS NOT NULL
UNION ALL SELECT 'mistake_draft', COUNT(*) FROM lsr02_final_migrations WHERE target_mistake_draft_id IS NOT NULL
UNION ALL SELECT 'question_source', COUNT(*) FROM lsr02_final_migrations WHERE target_question_source_id IS NOT NULL
UNION ALL SELECT 'qkp', COALESCE(SUM(cardinality(target_qkp_ids)),0) FROM lsr02_final_migrations
UNION ALL SELECT 'mistake_projection', COALESCE(SUM(cardinality(target_projection_ids)),0) FROM lsr02_final_migrations;
-- Every aggregate above must equal the independently expected fixture count.
SELECT m.id FROM lsr02_all_dispositions m
JOIN notes n ON n.id=m.source_note_id
WHERE n.type IN ('note','blog'); -- ordinary Note/Blog ledger/target scope must be zero
SELECT m.id FROM lsr02_retained_public_only m
WHERE (m.source_status IS DISTINCT FROM 'published' OR m.source_hidden IS DISTINCT FROM FALSE
       OR m.target_question_draft_item_id IS NOT NULL OR m.target_question_draft_id IS NOT NULL
       OR m.target_mistake_draft_item_id IS NOT NULL OR m.target_mistake_draft_id IS NOT NULL
       OR m.target_question_id IS NOT NULL OR m.target_question_source_id IS NOT NULL
       OR m.target_qkp_ids IS NOT NULL OR m.target_mistake_id IS NOT NULL
       OR m.target_projection_ids IS NOT NULL OR m.target_review_item_id IS NOT NULL
       OR m.target_bundle_hash IS NOT NULL OR m.source_approved_by IS NULL OR m.source_approved_at IS NULL OR m.source_approval_sequence IS NULL
       OR m.approved_by IS DISTINCT FROM m.source_approved_by
       OR m.approved_at IS DISTINCT FROM m.source_approved_at);
SELECT s.source_note_id
FROM lsr02_source_scope s
 WHERE s.state='retained_public_only'
  AND (s.source_hash IS DISTINCT FROM s.snapshot_source_hash
       OR s.source_url IS DISTINCT FROM s.snapshot_source_url
       OR s.legacy_review_json IS DISTINCT FROM s.snapshot_legacy_review_json
       OR s.slug IS DISTINCT FROM s.snapshot_slug
       OR s.status IS DISTINCT FROM s.snapshot_status
       OR s.hidden IS DISTINCT FROM s.snapshot_hidden
       OR s.revision IS DISTINCT FROM s.snapshot_revision
       OR s.search_vector_token IS DISTINCT FROM s.snapshot_search_vector_token
       OR s.snapshot_canonical_payload->>'id' IS DISTINCT FROM s.source_note_id::text
       OR s.snapshot_canonical_payload->>'source_note_id' IS DISTINCT FROM s.source_note_id::text
       OR s.snapshot_canonical_payload->>'type' IS DISTINCT FROM 'mistake'
       OR s.snapshot_canonical_payload->>'source_url' IS DISTINCT FROM s.source_url
       OR s.target_question_id IS NOT NULL OR s.target_mistake_id IS NOT NULL);
SELECT m.id
FROM lsr02_all_dispositions m
WHERE m.state IN ('ready','migrated_active','migrated_paused','retained_public_only')
  AND (m.source_approved_by IS NULL OR m.source_approved_at IS NULL OR m.source_approval_sequence IS NULL OR m.source_approval_event_id IS NULL
   OR (m.state IN ('migrated_active','migrated_paused') AND
       (m.question_conversion_approved_by IS NULL OR m.question_conversion_approved_at IS NULL
        OR m.mistake_conversion_approved_by IS NULL OR m.mistake_conversion_approved_at IS NULL
        OR m.question_conversion_sequence IS NULL OR m.mistake_conversion_sequence IS NULL
        OR m.question_approval_event_id IS NULL OR m.mistake_approval_event_id IS NULL))
   OR (m.state='migrated_active' AND
       (m.schedule_approved_by IS NULL OR m.schedule_approved_at IS NULL OR m.schedule_approval_sequence IS NULL
        OR m.schedule_approval_event_id IS NULL))
   OR (m.state='rolled_back' AND m.rollback_actor_id IS NULL));
SELECT e.id
FROM public.legacy_note_migration_events e
JOIN lsr02_all_dispositions m ON m.id=e.ledger_id
WHERE e.mapping_version=:mapping_version
  AND (e.source_note_id IS DISTINCT FROM m.source_note_id
    OR e.mapping_version IS DISTINCT FROM m.mapping_version
    OR e.source_hash IS DISTINCT FROM m.source_hash
    OR e.ledger_id IS DISTINCT FROM m.id
    OR e.actor_id IS NULL
    OR (e.approval_kind='rollback' AND (e.rollback_hash IS NULL OR e.rollback_hash IS DISTINCT FROM m.rollback_reference))
    OR (e.approval_kind<>'rollback' AND e.rollback_hash IS NOT NULL));
SELECT m.id
FROM lsr02_final_migrations m
WHERE m.state='migrated_active'
  AND NOT EXISTS (
    SELECT 1 FROM public.legacy_note_migration_events e
     WHERE e.ledger_id=m.id AND e.source_note_id=m.source_note_id
       AND e.mapping_version=m.mapping_version AND e.source_hash=m.source_hash
       AND e.id=m.transition_event_id
       AND e.approval_kind='state_transition' AND e.to_state='migrated_active'
       AND e.from_state IN ('ready','migrated_paused'));
SELECT m.id FROM lsr02_final_migrations m
LEFT JOIN notes n ON n.id=m.source_note_id
WHERE n.id IS NULL; -- a missing source Note is an orphan, never a silently empty scope
SELECT m.id FROM lsr02_final_migrations m
JOIN questions q ON q.id=m.target_question_id
JOIN mistakes x ON x.id=m.target_mistake_id
WHERE q.visibility IS DISTINCT FROM 'private' OR x.visibility IS DISTINCT FROM 'private'
   OR q.version < 1 OR x.version < 1;
SELECT source_note_id, COUNT(*) FROM lsr02_final_migrations GROUP BY source_note_id HAVING COUNT(*) <> 1;
SELECT target_question_draft_item_id, COUNT(*) FROM lsr02_final_migrations GROUP BY target_question_draft_item_id HAVING COUNT(*) > 1;
SELECT target_mistake_draft_item_id, COUNT(*) FROM lsr02_final_migrations GROUP BY target_mistake_draft_item_id HAVING COUNT(*) > 1;
SELECT target_question_id, COUNT(*) FROM lsr02_final_migrations GROUP BY target_question_id HAVING COUNT(*) > 1;
SELECT target_mistake_id, COUNT(*) FROM lsr02_final_migrations GROUP BY target_mistake_id HAVING COUNT(*) > 1;
SELECT target_review_item_id, COUNT(*) FROM lsr02_final_migrations WHERE state='migrated_active'
 GROUP BY target_review_item_id HAVING COUNT(*) > 1;
SELECT m.id FROM lsr02_final_migrations m
LEFT JOIN draft_items qdi ON qdi.id=m.target_question_draft_item_id
LEFT JOIN question_drafts qd ON qd.draft_item_id=qdi.id
LEFT JOIN questions q ON q.id=m.target_question_id
LEFT JOIN question_sources qs ON qs.id=m.target_question_source_id
LEFT JOIN draft_items mdi ON mdi.id=m.target_mistake_draft_item_id
LEFT JOIN mistake_drafts md ON md.draft_item_id=mdi.id
LEFT JOIN users qactor ON qactor.id=qdi.approved_by
LEFT JOIN users mactor ON mactor.id=mdi.approved_by
LEFT JOIN mistakes x ON x.id=m.target_mistake_id
LEFT JOIN review_items r ON r.id=m.target_review_item_id
WHERE legacy_migration.legacy_question_options_normalize(to_jsonb(qd.options)) IS NULL
   OR legacy_migration.legacy_question_options_normalize(to_jsonb(q.options)) IS NULL;
SELECT m.id FROM lsr02_final_migrations m
LEFT JOIN draft_items qdi ON qdi.id=m.target_question_draft_item_id
LEFT JOIN question_drafts qd ON qd.draft_item_id=qdi.id
LEFT JOIN questions q ON q.id=m.target_question_id
LEFT JOIN question_sources qs ON qs.id=m.target_question_source_id
LEFT JOIN draft_items mdi ON mdi.id=m.target_mistake_draft_item_id
LEFT JOIN mistake_drafts md ON md.draft_item_id=mdi.id
LEFT JOIN users qactor ON qactor.id=qdi.approved_by
LEFT JOIN users mactor ON mactor.id=mdi.approved_by
LEFT JOIN mistakes x ON x.id=m.target_mistake_id
LEFT JOIN review_items r ON r.id=m.target_review_item_id
LEFT JOIN lsr02_source_snapshot ss
  ON ss.mapping_version=m.mapping_version AND ss.source_note_id=m.source_note_id
WHERE qdi.id IS NULL OR qd.id IS NULL OR q.id IS NULL OR qs.id IS NULL
   OR mdi.id IS NULL OR md.id IS NULL OR x.id IS NULL
   OR qdi.source_type IS DISTINCT FROM 'legacy_note'
   OR mdi.source_type IS DISTINCT FROM 'legacy_note'
   OR qdi.source_id IS DISTINCT FROM m.source_note_id
   OR mdi.source_id IS DISTINCT FROM m.source_note_id
   OR qdi.draft_type IS DISTINCT FROM 'question'
   OR mdi.draft_type IS DISTINCT FROM 'mistake'
   OR qdi.status IS DISTINCT FROM 'converted'
   OR mdi.status IS DISTINCT FROM 'converted'
   OR qdi.version < 1 OR mdi.version < 1
   OR qdi.approved_by IS NULL OR qactor.id IS NULL OR qdi.approved_at IS NULL
   OR mdi.approved_by IS NULL OR mactor.id IS NULL OR mdi.approved_at IS NULL
   OR qdi.approved_by IS DISTINCT FROM m.question_conversion_approved_by
   OR mdi.approved_by IS DISTINCT FROM m.mistake_conversion_approved_by
   OR qdi.conversion_sequence IS NULL OR qdi.conversion_sequence <= 0
   OR mdi.conversion_sequence IS NULL OR mdi.conversion_sequence <= 0
   OR mdi.conversion_sequence <= qdi.conversion_sequence
   OR qdi.source_hash IS DISTINCT FROM m.source_hash
   OR mdi.source_hash IS DISTINCT FROM m.source_hash
   OR qdi.target_question_id IS DISTINCT FROM m.target_question_id
   OR qdi.target_question_id IS NULL OR qdi.target_mistake_id IS NOT NULL
   OR mdi.target_mistake_id IS DISTINCT FROM m.target_mistake_id
   OR mdi.target_mistake_id IS NULL OR mdi.target_question_id IS NOT NULL
   OR m.target_question_draft_id IS DISTINCT FROM qd.id
   OR m.target_mistake_draft_id IS DISTINCT FROM md.id
   OR qs.question_id IS DISTINCT FROM q.id
   OR x.question_id IS DISTINCT FROM q.id
   OR md.question_id IS DISTINCT FROM q.id
   OR md.question_draft_id IS NOT NULL
   OR md.attempt_id IS NOT NULL
   OR qd.subject_id IS DISTINCT FROM q.subject_id
   OR qd.title IS DISTINCT FROM q.title
   OR qd.question_type::text IS DISTINCT FROM q.question_type::text
   OR legacy_migration.legacy_question_options_normalize(to_jsonb(qd.options)) IS DISTINCT FROM
      legacy_migration.legacy_question_options_normalize(to_jsonb(q.options))
   OR qd.difficulty::text IS DISTINCT FROM q.difficulty::text
   OR qd.question_text IS DISTINCT FROM q.question_text
   OR qd.question_text IS DISTINCT FROM q.stem_md
   OR legacy_migration.legacy_question_answer_data_expected(
        q.question_type::text,
        q.correct_answer) IS NULL
   OR to_jsonb(q.answer_data) IS DISTINCT FROM legacy_migration.legacy_question_answer_data_expected(
        q.question_type::text,
        q.correct_answer)
   OR to_jsonb(qd.correct_answer) IS DISTINCT FROM to_jsonb(q.correct_answer)
   OR qd.explanation IS DISTINCT FROM q.explanation
   OR qd.explanation IS DISTINCT FROM q.analysis_md
   OR md.subject_id IS DISTINCT FROM x.subject_id
   OR md.title IS DISTINCT FROM x.title
   OR md.reason_category::text IS DISTINCT FROM x.reason_category::text
   OR md.mistake_reason IS DISTINCT FROM x.mistake_reason
   OR md.question_text IS DISTINCT FROM q.question_text
   OR to_jsonb(md.correct_answer_snapshot) IS DISTINCT FROM to_jsonb(q.correct_answer)
   OR md.explanation_snapshot IS DISTINCT FROM q.explanation
   OR md.my_answer IS DISTINCT FROM x.my_answer
   OR md.difficulty::text IS DISTINCT FROM x.difficulty::text
   OR md.question_text IS DISTINCT FROM x.question_text
   OR md.my_answer IS DISTINCT FROM ss.canonical_payload->'answers'->>'my_answer'
   OR md.correct_answer_snapshot IS DISTINCT FROM ss.canonical_payload->'answers'->>'correct_answer'
   OR md.question_text IS DISTINCT FROM ss.canonical_payload->>'question'
   OR md.explanation_snapshot IS DISTINCT FROM ss.canonical_payload->>'analysis'
   OR qd.title IS DISTINCT FROM ss.canonical_payload->>'title'
   OR md.title IS DISTINCT FROM ss.canonical_payload->>'title'
   OR to_jsonb(md.correct_answer_snapshot) IS DISTINCT FROM to_jsonb(x.correct_answer)
   OR md.explanation_snapshot IS DISTINCT FROM x.analysis
   OR x.question_text IS DISTINCT FROM q.question_text
   OR to_jsonb(x.correct_answer) IS DISTINCT FROM to_jsonb(q.correct_answer)
   OR x.mistake_reason IS DISTINCT FROM md.mistake_reason
   OR (m.state='migrated_active' AND r.id IS NULL)
   OR (m.state='migrated_active' AND (r.state IS DISTINCT FROM 'active' OR r.algorithm IS DISTINCT FROM 'fixed_interval_v1'))
   OR (m.state='migrated_active' AND r.mistake_id IS DISTINCT FROM x.id)
   OR (m.state='migrated_paused' AND r.id IS NOT NULL);
SELECT m.id FROM lsr02_final_migrations m
JOIN questions q ON q.id=m.target_question_id
JOIN subjects qs ON qs.id=q.subject_id
JOIN mistakes x ON x.id=m.target_mistake_id
JOIN subjects xs ON xs.id=x.subject_id
JOIN question_knowledge_points qkp ON qkp.question_id=q.id
JOIN knowledge_points kp ON kp.id=qkp.knowledge_point_id
JOIN subjects ks ON ks.id=kp.subject_id
WHERE q.subject_id IS DISTINCT FROM qs.id
   OR x.subject_id IS DISTINCT FROM xs.id
   OR q.subject_id IS DISTINCT FROM x.subject_id
   OR q.subject_id IS DISTINCT FROM kp.subject_id
   OR kp.subject_id IS DISTINCT FROM ks.id;
SELECT qkp.question_id, qkp.knowledge_point_id, COUNT(*)
FROM question_knowledge_points qkp
JOIN lsr02_final_migrations m ON m.target_question_id=qkp.question_id
GROUP BY qkp.question_id,qkp.knowledge_point_id HAVING COUNT(*) > 1;
WITH declared AS (
  SELECT m.source_note_id, m.mapping_version, m.target_question_id,
         unnest(m.target_qkp_ids) AS knowledge_point_id
  FROM lsr02_final_migrations m
), actual AS (
  SELECT m.source_note_id, m.mapping_version, m.target_question_id,
         qkp.knowledge_point_id
  FROM lsr02_final_migrations m
  JOIN question_knowledge_points qkp ON qkp.question_id=m.target_question_id
)
SELECT COALESCE(d.source_note_id,a.source_note_id) AS source_note_id,
       COALESCE(d.mapping_version,a.mapping_version) AS mapping_version,
       COALESCE(d.target_question_id,a.target_question_id) AS question_id,
       COALESCE(d.knowledge_point_id,a.knowledge_point_id) AS knowledge_point_id
FROM declared d FULL OUTER JOIN actual a
  ON a.source_note_id=d.source_note_id AND a.mapping_version=d.mapping_version
 AND a.target_question_id=d.target_question_id
 AND a.knowledge_point_id=d.knowledge_point_id
WHERE d.knowledge_point_id IS NULL OR a.knowledge_point_id IS NULL;
SELECT m.source_note_id, m.mapping_version, qkp.knowledge_point_id, COUNT(*)
FROM lsr02_final_migrations m CROSS JOIN LATERAL unnest(m.target_qkp_ids) AS qkp(knowledge_point_id)
GROUP BY m.source_note_id,m.mapping_version,qkp.knowledge_point_id HAVING COUNT(*) > 1;
SELECT m.id
FROM lsr02_final_migrations m
WHERE array_position(m.target_qkp_ids,NULL) IS NOT NULL
   OR m.target_qkp_ids IS DISTINCT FROM ARRAY(
      SELECT DISTINCT qkp.knowledge_point_id
        FROM question_knowledge_points qkp
       WHERE qkp.question_id=m.target_question_id
       ORDER BY qkp.knowledge_point_id);
SELECT m.id
FROM lsr02_final_migrations m
WHERE array_position(m.target_projection_ids,NULL) IS NOT NULL
   OR m.target_projection_ids IS DISTINCT FROM ARRAY(
      SELECT DISTINCT l.id
        FROM knowledge_point_links l
       WHERE l.target_type='mistake' AND l.target_id=m.target_mistake_id::text
       ORDER BY l.id);
SELECT m.target_mistake_id, l.id, COUNT(*)
FROM lsr02_final_migrations m
JOIN knowledge_point_links l
  ON l.target_type='mistake' AND l.target_id=m.target_mistake_id::text
GROUP BY m.target_mistake_id,l.id HAVING COUNT(*) > 1;
SELECT m.id FROM lsr02_final_migrations m
LEFT JOIN review_records rr ON rr.review_item_id=m.target_review_item_id
WHERE rr.id IS NOT NULL;
DO $$
DECLARE v_replay_count INTEGER; v_final_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_replay_count FROM lsr02_replay_manifest
   WHERE mapping_version=:mapping_version;
  SELECT COUNT(*) INTO v_final_count FROM lsr02_final_migrations
   WHERE mapping_version=:mapping_version;
  IF v_replay_count <= 0 OR v_final_count <= 0 OR v_replay_count <> v_final_count THEN
    RAISE EXCEPTION 'LSR02_REPLAY_EMPTY_OR_COUNT_MISMATCH';
  END IF;
END $$;
-- FULL OUTER JOIN makes missing replay rows and extra replay rows visible; an
-- inner join is forbidden because it can turn an empty replay into zero errors.
SELECT COALESCE(m.source_note_id,replay.source_note_id) AS source_note_id,
       COALESCE(m.mapping_version,replay.mapping_version) AS mapping_version
FROM lsr02_final_migrations m
FULL OUTER JOIN lsr02_replay_manifest replay
  ON replay.mapping_version=m.mapping_version
 AND replay.source_note_id=m.source_note_id
WHERE m.source_note_id IS NULL OR replay.source_note_id IS NULL;
SELECT m.id FROM lsr02_final_migrations m
FULL OUTER JOIN lsr02_replay_manifest replay
  ON replay.mapping_version=m.mapping_version
 AND replay.source_note_id=m.source_note_id
WHERE m.source_note_id IS NULL OR replay.source_note_id IS NULL
   OR replay.source_hash IS DISTINCT FROM m.source_hash
   OR replay.ledger_id IS DISTINCT FROM m.id
   OR replay.state IS DISTINCT FROM m.state
   OR replay.target_question_draft_item_id IS DISTINCT FROM m.target_question_draft_item_id
   OR replay.target_question_draft_id IS DISTINCT FROM m.target_question_draft_id
   OR replay.target_question_source_id IS DISTINCT FROM m.target_question_source_id
   OR replay.target_question_id IS DISTINCT FROM m.target_question_id
   OR replay.target_qkp_ids IS DISTINCT FROM m.target_qkp_ids
   OR replay.target_mistake_draft_item_id IS DISTINCT FROM m.target_mistake_draft_item_id
   OR replay.target_mistake_draft_id IS DISTINCT FROM m.target_mistake_draft_id
   OR replay.target_mistake_id IS DISTINCT FROM m.target_mistake_id
   OR replay.target_projection_ids IS DISTINCT FROM m.target_projection_ids
   OR replay.target_review_item_id IS DISTINCT FROM m.target_review_item_id
   OR replay.source_approved_by IS DISTINCT FROM m.source_approved_by
   OR replay.source_approved_at IS DISTINCT FROM m.source_approved_at
   OR replay.source_approval_sequence IS DISTINCT FROM m.source_approval_sequence
   OR replay.source_approval_event_id IS DISTINCT FROM m.source_approval_event_id
   OR replay.question_conversion_approved_by IS DISTINCT FROM m.question_conversion_approved_by
   OR replay.question_conversion_approved_at IS DISTINCT FROM m.question_conversion_approved_at
   OR replay.question_conversion_sequence IS DISTINCT FROM m.question_conversion_sequence
   OR replay.question_approval_event_id IS DISTINCT FROM m.question_approval_event_id
   OR replay.mistake_conversion_approved_by IS DISTINCT FROM m.mistake_conversion_approved_by
   OR replay.mistake_conversion_approved_at IS DISTINCT FROM m.mistake_conversion_approved_at
   OR replay.mistake_conversion_sequence IS DISTINCT FROM m.mistake_conversion_sequence
   OR replay.mistake_approval_event_id IS DISTINCT FROM m.mistake_approval_event_id
   OR replay.schedule_approved_by IS DISTINCT FROM m.schedule_approved_by
   OR replay.schedule_approved_at IS DISTINCT FROM m.schedule_approved_at
   OR replay.schedule_approval_sequence IS DISTINCT FROM m.schedule_approval_sequence
   OR replay.schedule_approval_event_id IS DISTINCT FROM m.schedule_approval_event_id
   OR replay.transition_event_id IS DISTINCT FROM m.transition_event_id
   OR replay.rollback_actor_id IS DISTINCT FROM m.rollback_actor_id
   OR replay.rollback_event_id IS DISTINCT FROM m.rollback_event_id
   OR replay.rollback_reference IS DISTINCT FROM m.rollback_reference
   OR replay.target_bundle_hash IS DISTINCT FROM m.target_bundle_hash;
SELECT source_note_id FROM lsr02_final_migrations WHERE mapping_version=:mapping_version
EXCEPT SELECT source_note_id FROM lsr02_replay_manifest WHERE mapping_version=:mapping_version;
SELECT source_note_id FROM lsr02_replay_manifest WHERE mapping_version=:mapping_version
EXCEPT SELECT source_note_id FROM lsr02_final_migrations WHERE mapping_version=:mapping_version;
-- Old Note before/after snapshot is compared by source_note_id, including slug/status/hidden/hash/search_vector_token.
SELECT s.source_note_id FROM lsr02_source_scope s
 WHERE s.slug IS DISTINCT FROM s.snapshot_slug
    OR s.content IS DISTINCT FROM s.snapshot_content
    OR s.status IS DISTINCT FROM s.snapshot_status
    OR s.hidden IS DISTINCT FROM s.snapshot_hidden
    OR s.revision IS DISTINCT FROM s.snapshot_revision
    OR s.search_vector_token IS DISTINCT FROM s.snapshot_search_vector_token
    OR s.source_hash IS DISTINCT FROM s.snapshot_source_hash;
-- Legacy-note imports create no CaptureItem/Attempt. Any inbound reference makes
-- logical rollback unsafe and the result must be snapshot_restore_required=true.
-- LSR-03 relation contract (the only inbound columns used by this bundle):
-- capture_items.mistake_draft_item_id -> draft_items.id,
-- attempts.mistake_draft_item_id -> draft_items.id, and
-- mistake_drafts.attempt_id -> attempts.id; all are FK/RESTRICT in the isolated schema.
SELECT m.id AS ledger_id, 'capture' AS inbound_kind, c.id AS inbound_id,
       TRUE AS snapshot_restore_required
FROM lsr02_final_migrations m
JOIN capture_items c ON c.mistake_draft_item_id=m.target_mistake_draft_item_id
WHERE m.mapping_version=:mapping_version
UNION ALL
SELECT m.id, 'attempt', a.id, TRUE
FROM lsr02_final_migrations m
JOIN attempts a ON a.mistake_draft_item_id=m.target_mistake_draft_item_id
WHERE m.mapping_version=:mapping_version
UNION ALL
SELECT m.id, 'mistake_draft_attempt', md.attempt_id, TRUE
FROM lsr02_final_migrations m
JOIN mistake_drafts md ON md.id=m.target_mistake_draft_id
WHERE m.mapping_version=:mapping_version AND md.attempt_id IS NOT NULL;
```

The `lsr02_source_snapshot` temp relation is loaded only from the external immutable archive for the same `source_note_id`; missing archive rows or any nonzero result is `FAIL`. The source reference and URL/slug/hash binding is tested only within the same scope:

```sql
WITH final_migrations AS (
  SELECT m.* FROM legacy_note_migrations m
  WHERE m.mapping_version = :mapping_version
    AND m.state IN ('migrated_active','migrated_paused')
)
SELECT m.id, qs.id
FROM final_migrations m
JOIN question_sources qs ON qs.id=m.target_question_source_id
WHERE qs.source_type IS DISTINCT FROM 'note'
   OR qs.source_ref IS NULL
   OR qs.source_ref !~ '^legacy-note:[0-9a-f]{36}$'
   OR qs.source_ref <> ('legacy-note:' || lower(m.source_note_id::text))
   OR NOT legacy_migration.legacy_question_source_matches(
        qs.id, m.source_note_id, m.mapping_version, m.source_slug, m.source_title, m.source_url, m.source_hash);
```

`legacy_question_source_matches` 是 adapter 冻结的 deterministic rule：它锁定 ledger 的精确 `target_question_source_id`，逐项比较 QuestionSource 的 source URL、完整 slug、source UUID、mapping version 与 source hash。上面的 schema-qualified `CREATE FUNCTION` 是该 helper 的可执行定义；若实现环境缺少函数或对应 provenance，LSR-03 必须报告 `FAIL`，不能以只比较 `source_ref` 代替。

Question mirror parity is not defined as `answer_data->>'value'`. The `CREATE FUNCTION legacy_question_mirror_matches(p_question_id UUID,p_question_source_id UUID,p_source_note_id UUID,p_mapping_version VARCHAR(64),p_source_hash TEXT)` definition above is the required executable deterministic rule; it maps each approved `question_type`/answer shape to `question_text/stem_md`, `correct_answer/answer_data`, `analysis_md/explanation`, `title`, and `subject_id`. LSR-03 calls that function only with the ledger's exact target QuestionSource and `(source_note_id,mapping_version)` pair and fails on any false result or missing function. No SQL may assume a universal answer-data JSON path.

```sql
SELECT m.id
FROM lsr02_final_migrations m
JOIN questions q ON q.id=m.target_question_id
WHERE NOT legacy_migration.legacy_question_mirror_matches(
  q.id, m.target_question_source_id, m.source_note_id, m.mapping_version, m.source_hash);
```

Generic `KnowledgePointLink.target_id` is validated without unsafe casts, and only for scoped final Mistake IDs:

```sql
CREATE OR REPLACE TEMP VIEW lsr02_final_mistakes AS
  SELECT m.source_note_id, m.mapping_version, m.target_mistake_id AS mistake_id
  FROM lsr02_final_migrations m;
WITH declared AS (
  SELECT m.source_note_id, m.mapping_version, m.target_mistake_id,
         unnest(m.target_projection_ids) AS projection_id
  FROM lsr02_final_migrations m
)
SELECT d.source_note_id, d.mapping_version, d.projection_id
FROM declared d
JOIN lsr02_final_mistakes fm
  ON fm.source_note_id=d.source_note_id AND fm.mapping_version=d.mapping_version
LEFT JOIN knowledge_point_links l ON l.id=d.projection_id
WHERE l.id IS NULL OR l.target_type IS DISTINCT FROM 'mistake'
   OR l.target_id !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
   OR l.target_id <> fm.mistake_id::text;
SELECT m.source_note_id, m.mapping_version, p.projection_id, COUNT(*)
FROM lsr02_final_migrations m
CROSS JOIN LATERAL unnest(m.target_projection_ids) AS p(projection_id)
GROUP BY m.source_note_id,m.mapping_version,p.projection_id HAVING COUNT(*) > 1;
WITH projection AS (
  SELECT fm.source_note_id, fm.mapping_version, l.id,
         legacy_migration.legacy_uuid_or_null(l.target_id) AS target_mistake_id, l.knowledge_point_id
  FROM knowledge_point_links l JOIN lsr02_final_mistakes fm
   ON l.target_type='mistake'
   AND l.target_id ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
   AND l.target_id = fm.mistake_id::text
), canonical AS (
  SELECT fm.source_note_id, fm.mapping_version, m.id AS mistake_id, qkp.knowledge_point_id
  FROM lsr02_final_mistakes fm JOIN mistakes m ON m.id=fm.mistake_id
  JOIN question_knowledge_points qkp ON qkp.question_id=m.question_id
)
SELECT source_note_id, mapping_version, mistake_id, knowledge_point_id FROM canonical
EXCEPT SELECT source_note_id, mapping_version, target_mistake_id, knowledge_point_id FROM projection
UNION ALL
SELECT source_note_id, mapping_version, target_mistake_id, knowledge_point_id FROM projection
EXCEPT SELECT source_note_id, mapping_version, mistake_id, knowledge_point_id FROM canonical;
-- compare only knowledge_point_id sets; role/sort_order is not a projection claim.
SELECT l.target_id, l.knowledge_point_id, COUNT(*)
FROM knowledge_point_links l JOIN lsr02_final_mistakes fm
  ON l.target_type='mistake'
 AND l.target_id ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
 AND l.target_id=fm.mistake_id::text
GROUP BY l.target_id,l.knowledge_point_id HAVING COUNT(*) > 1;
```

Schedule and EF checks are also scoped and NULL-safe:

```sql
WITH final_migrations AS (
  SELECT m.* FROM legacy_note_migrations m
  WHERE m.mapping_version = :mapping_version
    AND m.state IN ('migrated_active','migrated_paused')
)
SELECT m.id FROM final_migrations m
JOIN review_items r ON r.id=m.target_review_item_id
JOIN lsr02_run_manifest run
  ON run.mapping_version=m.mapping_version
WHERE m.state='migrated_active'
  AND (m.manual_review_required IS DISTINCT FROM FALSE
    OR m.mapped_next_review_at IS NULL
    OR r.state IS DISTINCT FROM 'active'
    OR r.algorithm IS DISTINCT FROM 'fixed_interval_v1'
    OR r.interval_days IS DISTINCT FROM m.legacy_interval
    OR r.repetitions IS DISTINCT FROM m.legacy_repetitions
    OR r.next_review_at IS DISTINCT FROM m.mapped_next_review_at
    OR r.last_reviewed_at IS DISTINCT FROM m.mapped_last_reviewed_at
    OR ((r.next_review_at <= run.evaluation_time_utc) IS TRUE)
       IS DISTINCT FROM
       ((m.state='migrated_active' AND m.mapped_next_review_at <= run.evaluation_time_utc) IS TRUE));
WITH final_migrations AS (
  SELECT m.* FROM legacy_note_migrations m
  WHERE m.mapping_version = :mapping_version
    AND m.state IN ('migrated_active','migrated_paused')
)
SELECT m.id FROM final_migrations m
WHERE m.state='migrated_paused'
  AND (m.manual_review_required IS DISTINCT FROM TRUE
    OR m.mapped_next_review_at IS NOT NULL
    OR m.target_review_item_id IS NOT NULL);
WITH final_migrations AS (
  SELECT m.* FROM legacy_note_migrations m
  WHERE m.mapping_version = :mapping_version
    AND m.state IN ('migrated_active','migrated_paused')
)
SELECT m.id FROM final_migrations m
WHERE m.legacy_ef_bits IS DISTINCT FROM
  pg_catalog.encode(pg_catalog.float8send(m.legacy_ef),'hex');
```

Finally, identical replay must return the same ledger, all draft-item/draft, final, QSource, QKP/projection and active ReviewItem IDs plus hashes; the query compares those IDs keyed by `(source_note_id,mapping_version)`. A new mapping version must produce a new immutable ledger row and never mutate the previous scope. The rollback fixture must assert the governed atomic ledger transition first (state/rollback_reference/non-null→all target FK NULL), then the exact FK deletion order, zero legacy Note deletion, zero unexpected Capture/Attempt inbound reference, and snapshot-restore routing on any violation.

## 3. 阶段退出与切换合同

### 阶段一：迁移并移除旧结构

LSR-01 只读盘点所有旧/新对象、数据库表列、Alembic revision、API、service、前端 client/hook/page、导航、测试、静态内容和导出消费者；数据库内容查询只有在依赖满足且预先授权的隔离快照任务中允许。LSR-02 将 slug/UUID、科目、知识点、题干、答案、错因、难度、EF、interval、repetitions、next_review、last_reviewed、版本、来源、可见性和审计字段逐项映射，未知项 fail closed。LSR-03 只在隔离 PostgreSQL 从空库回放 Alembic、恢复合成/预先授权的本地快照、演练迁移和恢复；禁止连接日常/生产库。

LSR-03 不以 G2 `PASS` 为前置；它由 LSR-02 进入隔离 replay/计数/关系/幂等/恢复，生成 G2 证据，再由 Database Architect 与 Senior Data Engineer 独立对账。LSR-04 只依赖 LSR-03、G1 `PASS` 和 G2 `PASS`；它用权限负向、真实浏览器/网络证据生成 G3，必要时生成 G4，再由对应独立 Gate Worker 对账。LSR-05/06 才依赖相应 G3/G4 `PASS`。

只有新版等价性、权限负向、计数/关系/孤儿/重复/版本/可见性、回滚和独立复核均通过，才可按“API client/service → `/manage/*` 页面/导航 → 旧入口安全退出 → 旧 API/component/service/model consumer”顺序切换。删除只能发生在零消费者、数据已迁移且可恢复证据之后；普通 Note/Blog/公开内容永不因本任务整体删除。

### 阶段二：七个体系分别验收

Subject/KnowledgePoint、Question、Mistake、Review、Note、Capture、学习首页各自拥有独立 manifest、正常/空/错误/未登录/拒绝/重复提交证据和独立状态。任何 `FAIL`、`BLOCKED` 或 `NOT_VERIFIED` 禁止进入下一体系和阶段三。

### 阶段三：融合验收

在隔离 PostgreSQL、生产 frontend build、真实 FastAPI 路由和真实 Chromium 中完成 Capture→Question→Mistake→Review→Dashboard、Subject/KnowledgePoint 关联、Note 关联与公开/私有边界、刷新/重登持久性、归档/删除外键约束和旧请求零命中。记录 console、page error、failed request、unexpected navigation 和秘密扫描。

### 阶段四：收束

阶段四入口必须先有 G0、G1、G2、G3 `PASS`，实际触发 G4 时也必须 `PASS`；无生产范围时 G5 为 `NOT_AUTHORIZED`，不是非生产收束前置。随后完成旧入口/旧导入/旧迁移残留搜索、Alembic graph/空库 replay/恢复复核、目标 pytest/Vitest/typecheck/build/Chromium 验收、auth/session/公开可见性/秘密/端口/临时资源/worktree 清理。只有删除、迁移、七体系、融合、清理和独立审查均有当前证据，最终才可能 `PASS`。

## 4. G0-G5 触发、证据与独立对账

历史快照（已被最终当前结论取代）：LSR-01 只读完成后等待 G0/G1 对账，G1 尚未完成。最终当前结论为 G0=`PASS`、G1 Architect=`PASS`、Technical Reviewer=`PASS_WITH_NOTES`、combined G1=`PASS`；此段记录的是 LSR-02 Owner 交付前等待 QA/Data 的状态，不得把设计 PASS 误报为实现或 G2 PASS。当前 LSR-02 以本文件 addendum/validation manifest 为准，仍 `PARTIAL/[ ]`。

| Gate | 触发 | 必须对账的当前证据 | 独立决定者与 fail-closed 条件 |
| --- | --- | --- | --- |
| G0 REQUIREMENT_DOMAIN | 目标语义、保留/删除、可见性、复习规则或验收标准变化 | 新旧定义、边界案例、Note/Blog 保留规则、用户决定和可测试验收 | Product Architect + Senior Domain Analyst；语义冲突/未知即 `BLOCKED` |
| G1 ARCHITECTURE | 所有权切换、兼容 API、路由/服务边界或删除计划 | 当前调用图、持久化 owner、替代方案、兼容/回滚、切换顺序 | Principal Technical Reviewer；未证明 owner/兼容/回滚即 `BLOCKED` |
| G2 DATA_DATABASE | schema/model/Alembic、批量变更、字段映射、备份恢复、删除 | revision graph、不可变 manifest、隔离回放、计数/hash/关系/孤儿、幂等、恢复 | Database Architect + Senior Data Engineer；任何 drift/UNKNOWN/生产触达即 `BLOCKED` |
| G3 SECURITY_AUTH | admin/public owner、session、上传、AI、公开/私有过滤 | `admin_session`/`AdminSession`、`credentials: include`、`get_current_admin`、401/403、秘密/越权负向 | Senior Security Engineer + Senior QA / SDET；越权、泄露或合同变化即 `BLOCKED` |
| G4 RECOMMENDATION_AI | 采集识别、草稿转换、复习调度、推荐或 AI 持久化输出 | 来源链、人工确认、确定性规则、失败回退、审计、评估和不把 AI 当事实的证据 | Senior Recommendation Engineer + Senior AI / LLM Engineer；无来源/评估/回退即 `BLOCKED` |
| G5 RELEASE_PRODUCTION | 生产配置/数据、部署、公开切换、不可逆迁移、凭据、发布 | exact release identity、clean authorized scope、全部前置 Gate、监控/回滚、明确授权 | Senior DevOps / SRE + Senior QA / SDET；本工作流无生产范围时为 `NOT_AUTHORIZED` |

Gate 对账顺序固定为：Primary Owner 交付证据 → 独立 Reviewer 逐项质疑 → 独立 Verifier 重跑/抽样 → 对应 Gate Worker 写结论。Owner 不得自批；非生产任务权限已预先批准，但“任务权限”“技术 PASS”“部署资格”“实际部署”永不互相继承。

每个高风险任务必须在 `tasks.md` 明确列出 task-local Gate Worker，并写明“独立 Worker，排除 Primary Owner”。该 Gate Worker 不得采用任务 Owner 作为决定者；若默认领域 Gate Persona 与 Owner 冲突，必须使用任务中点名的独立替代 Persona。全局 Gate 表只定义领域规则，不授权 Owner 代行 Gate。

### Worker identity 规则

Persona 类型不是 identity。每个任务都使用唯一的 `worker_id_prefix`，并为 Primary Owner、每个 Reviewer、每个 Verifier 和每个 Gate Worker 分配不同的真实子代理 identity；即使 Persona 相同，也必须使用不同的 task-local `worker_id`。标准派生格式为 `<prefix>-owner`、`<prefix>-reviewer-<n>`、`<prefix>-verifier-<n>` 和 `<prefix>-g<gate>-<role>`。同一 task 内任何 worker_id 不得重复，Primary Owner 的 worker_id 不得出现在 Reviewer、Verifier 或 Gate Worker 集合中。

每个 Gate 的完整 Worker 组合固定为：G0=`Product Architect + Senior Domain Analyst`；G1=`Principal Software Architect + Principal Technical Reviewer`；G2=`Database Architect + Senior Data Engineer`；G3=`Senior Security Engineer + Senior QA / SDET`；G4=`Senior Recommendation Engineer + Senior AI / LLM Engineer`；G5=`Senior DevOps / SRE + Senior QA / SDET`，生产范围再按需追加 `Senior Security Engineer`/`Database Architect`。`tasks.md` 每项的 role matrix 必须列出其触发 Gate 的完整 worker_id+Persona。实际执行时这些 worker_id 必须绑定真实独立子代理；主代理只编排、汇总和对账，不代替任何 Worker。

## 5. Manifest 与回滚

每阶段唯一权威 manifest 作为 `validation.md` 中的版本化表格/JSON 摘要，至少含 `task_id`、时间、source/target identity（不含凭据）、revision、输入 hash、对象/表/路由覆盖、结果、证据 hash、Reviewer、Verifier、Gate 状态和清理状态。脚本、harness、原始输出、隔离附件只能放在该任务专属的仓库外临时目录；仓库只登记路径、hash、首次必要失败和清理结果。若确需把脚本或测试持久化进仓库，必须先在精确任务范围中扩展写入授权，不得偷跑。正常重试合并为一条，不新建本目录之外的 workflow artifact。

回滚优先级：取消当前任务 → 恢复上一版代码/路由配置（仅在该非生产任务精确写入范围内）→ 从隔离快照恢复数据库 → 重新跑完整性和权限负向 → 保留旧数据只读。不得以直接删除旧数据作为回滚，不得将隔离演练当成生产切换证据。

## 6. 固定的禁止事项

不读或连接日常/生产数据库；不接触真实凭据、session token、密码 hash、用户正文或私有附件；不改变 `admin_session`、`AdminSession`、`credentials: include`、`get_current_admin`；不私有化公开 Note/Blog；不执行生产迁移、公开路由删除、部署、commit、push、依赖升级、无关 UI 重构或 AI 扩展。任何一项成为必要条件，立即暂停并将任务标为 `NOT_AUTHORIZED` 或 `BLOCKED`。

### R8/R9 seed 与命令合同（2026-08-25）

R8 首错保留为历史：R6 seed 未持久化为 machine-readable helper，导致空 post-026 rehearsal 缺少 source Note。`lsr03_seed_rehearsal.py` 固定 synthetic users、approval authorization、rollback admin、taxonomy、source Note 与 paused baseline IDs，精确空集外 fail-closed，且仅在 guarded/private venv 后导入 DB 依赖。R9 必须按 validation.md 的唯一序列执行；`READY_FOR_R9=NO`，不改变 LSR-03/G2。
