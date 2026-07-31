# I 系列剩余任务设计与只读现状报告

事实截止：2026-07-28
执行属性：`READ-ONLY PLANNING BASELINE + AUTHORIZED EXECUTION`
实施状态：`C0-C12 AUTHORIZED / IN PROGRESS`

## 1. 证据方法与边界

本报告不采用 workflow 勾选作为运行时事实。结论来自当前工作树代码、显式只读 PostgreSQL 事务、备份内容/哈希、既有测试输出与浏览器资产。为维持只读边界，本轮没有重跑可能写库或生成缓存的测试，也没有启动应用；历史测试结果只作为带日期的既有证据，不升级为 2026-07-28 的新 PASS。

本轮允许写入的唯一位置是本 workspace 的规划文档。未修改 I10/I11/I12 既有验证记录。

### 1.1 本轮关键命令与输出

| 证据 | 只读命令 | 2026-07-28 输出摘要 |
|---|---|---|
| 源库身份/revision | `psql ... -Atc "BEGIN READ ONLY; ... SELECT version_num FROM alembic_version; COMMIT;"` | `blog_db|blog_user|5432|on`；`020` |
| Alembic current | `cd backend && env PYTHONPATH=. .venv/bin/alembic current` | `020` |
| 代码 head | `cd backend && .venv/bin/alembic heads` | `024 (head)` |
| migration 链 | `rg -n "revision:|down_revision:" backend/alembic/versions/02[0-4]*.py` | `020←021←022←023←024`，单链 |
| 12 类实体计数 | 源库 `BEGIN READ ONLY` 下逐表 `count(*)` | notes 13、questions 3、mistakes 3、review_items 3、review_records 4、attachments 1、attachment_links 1、capture_items 0、draft_items 6、ai_runs 32、ai_call_logs 47、users 8 |
| legacy/独立错题 | 源库只读 `notes.type` 与精确 question/answer join | notes: blog 1 / mistake 5 / note 7；独立 mistakes 3；精确 question 或 question+answer 候选均 0 |
| owner-like 字段 | `information_schema.columns` 与 FK 只读查询 | notes/questions/mistakes/review* 无 owner；attachments/draft_items 的 `created_by` 非空，但全部指向 non-admin user；ai_runs 32 条全部 `target_id IS NULL`；ai_call_logs 无 owner/target FK |
| 关系孤儿探针 | FK 与多态目标只读 left join | 当前已检查的 Mistake→Question/Draft、ReviewRecord→ReviewItem、ReviewItem→Mistake、AttachmentLink→Attachment/Mistake 均 0 orphan；这不替代未来全量 manifest |
| 备份 revision | `pg_restore --data-only --table=alembic_version --file=- .../database.dump` | dump 内 `020` |
| 数据库备份哈希 | `shasum -a 256 -c database.dump.sha256` | `database.dump: OK` |
| 附件备份/源哈希 | 在正确快照/源目录以两组 SHA-256 manifest 校验 | backend uploads 2/2 OK；兼容图片 10/10 OK；当前源文件与 2026-07-20 manifest 仍一致 |
| 浏览器资产 | `sips -g pixelWidth -g pixelHeight .../i12-final-closure/assets/*.png` 与人工查看 | 390×844、1280×800、1440×900 文件齐全；`prod-1280-manage.png` 仍显示“检查 Passkey 状态...”，390/1440 显示明确失败，完整失败态不成立 |
| 工作树 | `git status --short` | 大量既有 dirty 变更；021–024 migration 与 I10/I11/I12 目录均 untracked |
| 文本 diff 健康 | `git diff --check` | 无输出；仅说明当前 tracked diff 无 whitespace error，不是测试/发布资格 |

关键文件证据：

- `backend/main.py:17-35`：当前代码要求 revision `024` 并 fail closed。
- `backend/alembic/versions/021_add_attempt_learning_loop.py:13-67`：021 新建 attempts；存在数据时拒绝 downgrade。
- `backend/alembic/versions/022_add_admin_profiles.py:13-47`：022 新建 admin_profiles；存在数据时拒绝 downgrade。
- `backend/alembic/versions/023_add_file_workspace_metadata.py:19-40`：023 回填 attachment display_name；downgrade 删除新列。
- `backend/alembic/versions/024_add_markdown_versions_links_search.py:20-62`：024 回填 notes.revision、新建 versions/links、安装 pg_trgm；downgrade 删除表/列并 drop extension。
- `docs/workflows/i10-migration-dry-run/owner-coverage.md:24-73`：12 类 owner 覆盖与 gate 条件。
- `docs/workflows/i11-shadow-migration/tasks.md:3-6`、`docs/workflows/i12-final-closure/tasks.md:3-6`：未完成任务状态。
- `docs/workflows/i12-final-closure/validation.md:35-40`：管理员、恢复、完整失败态仍 NOT VERIFIED。
- `/Users/limengyang/Backups/2025-blog-public/20260720T164919/`：020 dump、SHA-256、source/restore facts 与附件快照。

### 1.2 未完成任务的精确状态

| 任务 | 当前状态 | 已有证据 | 仍缺证据/阻塞 |
|---|---|---|---|
| I10-02 / E-02 | `PARTIAL` | 技术字段映射、duplicate slug=0、关系探针与 8 表 hash 见 `i10-migration-dry-run/validation.md:9-14` | canonical owner、12 类逐行 manifest、legacy/独立错题终态、冲突批准 |
| I10-03 / E-03 | `PASS` | 2026-07-31 121-row owner sidecar、双重复核、FK/关系、销毁与基线恢复 PASS | 不授权 source/shadow 写入 |
| I10-04 / E-04 | `TECHNICAL PASS / OWNER PASS` | clone replay 与最新 024→025 隔离 backfill/check 均有证据 | 不授权 source/shadow 写入 |
| I10-05 | `PARTIAL` | 历史主验证/独立进程技术复核存在 | owner 决策后的新鲜 source snapshot 与独立 manifest 复核 |
| I11-01 | `PASS for historical approval check` | `i11-shadow-migration/tasks.md:3`、`validation.md:3` 记录 2026-07-26 单一 owner 模式与“批准并继续” | 该批准早于本报告确认的 mismatch/新执行拆分，不自动授权 C5–C9 |
| I11-02 / E-05 | `READY / NOT AUTHORIZED` | Owner gate PASS；没有 shadow target 或本轮执行授权 | 新授权、shadow count/hash、增量/tombstone/零 drift |
| I11-03 / E-06 | `READY / NOT AUTHORIZED` | Owner gate PASS；未执行 E-05 | E-05 PASS、切换/停旧写/归档分别批准、观察期、reverse delta、回切/恢复 |
| I11-04 | `BLOCKED / NOT EXECUTED` | 无 E-05/E-06 主验证可复核 | 与主验证不同进程/fixture 的独立交叉验证 |
| I12-01 / F-01 | `PARTIAL` | 2026-07-26 匿名三尺寸、键盘、失效 session、隔离测试/build 记录；本轮确认资产存在 | 真实管理员、024 恢复/回切、全失败态；1280 Passkey 资产仍 loading |
| I12-02 / F-02 | `NOT STARTED / BLOCKED` | fail-closed 设计只有一句原则 | I10/I11/F-01 全部关闭、固定 artifact、完整 predeploy checklist 与 G4 |
| I12-03 / F-03 | `NOT STARTED / BLOCKED` | 最终状态维度尚未形成正式报告 | 各维度带日期/环境/artifact/revision 的证据与 I10/I11 终态 |
| I12-04 | `PARTIAL / BLOCKED` | 匿名/隔离的局部独立复核见 `i12-final-closure/validation.md:6-40` | 管理员、恢复、切换、完整失败态和 F-02/F-03 的交叉验证 |

## 2. Migration mismatch

### 2.1 确切事实

源库 revision 为 `020`；代码 head 为 `024`。源物理 schema 未出现 attempts、admin_profiles、note_versions、note_links，也未出现 023/024 的目标列。当前代码的 readiness 明确要求 024，因此 020 源库不能作为当前后端的合格启动目标。

缺失的四个 migration 是：

| Revision | 主要变化 | 写入/回滚风险 |
|---|---|---|
| 021 | attempts、mistake_drafts.attempt_id 与约束 | 有 attempt 数据后 downgrade 被代码拒绝 |
| 022 | admin_profiles | 有 profile 数据后 downgrade 被代码拒绝 |
| 023 | attachments workspace 字段与 display_name 数据回填 | downgrade 删除列；`trashed` 状态需先处置 |
| 024 | notes.revision 回填、note_versions、note_links、pg_trgm | downgrade 删除版本/链接/列并 drop extension，可能影响同库其他消费者 |

此外 021–024 当前为 Git untracked。任何执行前必须先形成可审计、不可漂移的候选代码版本；本规划不提交它们。

### 2.2 I11 前置关系

顺序必须是：owner 决策与 manifest → 只读重判 Migration Gate 为 `DRY_RUN_READY=PASS` → G2 → 最新隔离 dry-run → 新鲜 020 备份/恢复演练 → 用户单独授权源库 020→024 写入 → 024 验证 → G3 后执行 E-05。不得在 gate 非 PASS 时写隔离 target，不得在 020 源库上直接开始 E-05，也不得把既有 I11-01 历史批准当成源库 upgrade 授权。

### 2.3 源库 upgrade 策略

这一步是未来的不可忽略源库写入，必须单独授权；G2/G3 本身都不自动授权。

前置：

1. 固定候选代码/迁移哈希，确认单 head 与 `alembic check`；审查 021–024 upgrade/downgrade SQL、锁、extension 权限和预计时间。
2. 在维护窗口开始前生成新鲜 020 custom dump、附件快照、全 12 类 row count/hash、FK/多态关系清单与 owner manifest hash；备份在仓库外，权限最小化。
3. 将新鲜备份恢复到新隔离目标，验证 020 可启动历史兼容版本；再在 clone 执行 020→024，核对数据回填、约束、head/check、应用 readiness 与核心只读 API。
4. 在源库 upgrade 期间停止正式写入口。若不能确认停写，硬停止。

执行后验收：revision/head/check 均为 024；旧字段的逐行 hash 不变；新列回填符合规则；新表/索引/extension 存在；附件引用/hash 不变；公开读取与管理员鉴权 smoke 通过；生成一次 024 后备份。

回滚：首选“恢复新鲜 020 备份到并行数据库并切回经验证的 020 兼容应用”，而不是对已承接新写入的库直接 `alembic downgrade 020`。在重新开放写入前 upgrade 失败，可以恢复 020 快照；重新开放写入后若要回退，必须先有经演练的 024→020 业务 delta 导出/重放方案，否则回滚会丢失新写入并硬停止。021/022 的拒绝降级与 023/024 的删除行为使直接 downgrade 不是默认回滚路径。

### 2.4 C3 候选 artifact 与 I3-I10 纠缠代码切分（P0）

2026-07-28 的 `git status --short` 与 import/reference 闭包证明 021-024 不是四个可单独搬运的 migration 文件：当前 ORM registry、FastAPI router 注册、schemas/services、API clients 和 I6-I9 验证共同依赖新列/新表。C3 必须把以下集合冻结为同一个可审计候选 artifact，并证明 Alembic 单 head、`alembic check` 干净：

- migrations：`backend/alembic/versions/021_add_attempt_learning_loop.py`、`022_add_admin_profiles.py`、`023_add_file_workspace_metadata.py`、`024_add_markdown_versions_links_search.py`。
- models/registry：`backend/app/models/{__init__,registry,note,mistake,attachment,attempt,admin_profile,knowledge_markdown}.py`。
- routers/runtime：`backend/main.py`、`backend/app/routers/{attempts,admin_profile,file_workspace,governance,search,dashboard,notes}.py`。
- schemas：`backend/app/schemas/{attempt,admin_profile,file_workspace,governance,search,attachment,capture,dashboard,mistake,note}.py`。
- services：`backend/app/services/{attempt_service,admin_profile_service,file_workspace_service,governance_service,knowledge_markdown_service,attachment_service,dashboard_service,mistake_service}.py`。
- backend acceptance tests：`backend/tests/{test_attempt_service,test_admin_profile_routes,test_i6_capture_failure_matrix,test_i6_capture_http,test_i6_draft_chain,test_i7_file_workspace,test_i7_file_workspace_routes,test_i8_markdown_search,test_i8_search_routes,test_i9_governance_routes,test_dashboard_dependency_lifecycle,test_dashboard_routes}.py`。
- frontend contract/consumer closure：`src/lib/api/{attempts,admin-profile,admin-profile.test,governance,governance.test,search,search.test,dashboard,notes}.ts`，以及当前引用这些契约的 `src/app/manage/(workspace)/{capture,search,settings,dashboard,ai,analytics,jobs}/**`、`src/app/manage/(workspace)/questions/components/question-editor.tsx`、`src/app/manage/(workspace)/governance-overview.tsx`、`src/app/manage/components/manage-sidebar.test.tsx`、`src/app/notes/[id]/note-detail-content.tsx`、`src/app/write-note/[slug]/page.tsx`、`src/layout/head.tsx` 与对应测试。

上述集合以 C3 生成的逐文件 SHA-256 manifest 为准；列表中任何文件在 C5 前漂移都使 artifact gate 失败。与 Phase 1.0 产品化有关但不在该引用闭包中的 dirty 文档、截图和其他改动不得混入候选 artifact。由于当前工作树未提交，C3 的“冻结”是仓库外只读 bundle + hash manifest，不是 commit、push 或部署。

**C5 硬门槛：**执行 source migration 的代码目录必须与 C3 冻结 artifact 的逐文件 hash 完全相等；不允许只复制 021-024 migration 后使用另一版 ORM/runtime。任何 mismatch 都立即停止 C5。

### 2.5 已部署前端与源库关系只读核查（P0）

2026-07-28 只读核查结论：`blog.limengyang.me` 返回 Cloudflare OpenNext/Next.js 预渲染页面，`/api/health` 在该域名为 Next 404；生产前端 artifact 的 `.open-next/cloudflare/next-env.mjs` 指向 `https://public-api.limengyang.me`。本机 cloudflared ingress 将该域名转发到 `http://localhost:8000`，但 `lsof` 无 8000 listener、`ps` 无 Uvicorn/Gunicorn，公网 health 返回 502。因此当前没有活 backend 进程，backend version、运行时 `EXPECTED_ALEMBIC_REVISION` 与运行时 DB connection 均为 N/A；候选源码要求 `024`，本地 source DB 为 `blog_db:5432` revision `020`。

该证据满足“公开站为已部署前端、无活 backend 连本源库”的 C5 前置分支。C5 开始前仍须在同一维护窗口重复 `ps/lsof`、public health、cloudflared ingress 和 `pg_stat_activity` 只读核查；若出现活 backend 或除执行会话外的应用连接，必须先停写，否则 C5 保持 BLOCKED。

### 2.6 C0-C5 Git 权威收口与 revision-aware C1 复核（P0）

2026-07-29 复查确认 source `blog_db:5432` 已由 C5 升至 revision 024，但当时 `021`-`024` 仍为 Git untracked。C3 的仓库外 bundle 能证明执行时 artifact 未漂移，却不能让干净 checkout 重建当前 schema，因此本轮把 C3 `candidate-files.txt` 的 83-file 闭包作为一个不可拆分的本地 commit 收口。暂存范围由该清单与本 workflow 目录白名单共同决定；Phase 1.0、temp-admin、project assessment、UI review 和其他 workflow dirty 明确排除。该收口已由 local commit `2c7adcc` 完成，四个 migration 现为 tracked。

C1 manifest 继续表示 revision 020 的 121-row 时点快照，其 payload 与 source aggregate 不变。升级后不重新生成 manifest；verifier 在读取当前 database revision 后选择显式 revision pair：

| manifest revision | database revision | 读取合同 | 结果 |
|---|---|---|---|
| 020 | 020 | 12 表完整行 | 支持；无投影 |
| 020 | 024 | `notes - revision`；`attachments - display_name/folder_id/trashed_at`；其余完整行 | 支持；投影到 020 合同 |
| 其他组合 | 任意 | 无隐式猜测 | `BLOCKED` |

投影在 SQL 查询侧完成，避免先读取 024-only 字段再以字符串方式删改 JSON。验证报告同时保留 manifest/source database/projection 三个 revision 事实，并继续执行 canonical owner、关系 orphan、121-row 与 aggregate gate。该复核只能证明“024 中保留的 020 字段未漂移”，不能把 C1 manifest 解释为 024 新表/新列的快照；024 schema/backfill 仍由 C5 独立证据负责。

## 3. I10 Owner/Backfill 决策方案

### 3.1 Owner 决策状态

12 类实体全部 `pending_owner_review`。当前 8 users 为 4 admin/4 non-admin；唯一 attachment 和 6 个 draft_items 的 `created_by` 都指向 non-admin user，且是同一 source user。该事实只说明 provenance 一致，不证明该 user 或任一 admin 是 target owner。32 个 ai_runs 全部无 target，47 个 ai_call_logs 无 owner/target 关系。

用户于 2026-07-28 明确授权使用确定性默认选择。只读查询 `SELECT ... FROM users WHERE is_admin IS TRUE ORDER BY id LIMIT 1` 选定 admin UUID 升序最小者 `4c503215-b158-4162-b472-79df8289ed0a`（username=`i5-profile-fe846c85`）作为 canonical source/target owner；source→target 为同 UUID 1:1。`created_by`、folder/path/slug 和关联对象仍不作为 fallback owner。

### 3.2 已生效的 D1-D8 决策

| 决策 | 生效选择 | 执行规则 |
|---|---|---|
| D1 canonical owner | A | source/target 均为 `4c503215-b158-4162-b472-79df8289ed0a`；依据为 admin UUID 升序最小，不使用用户名语义 |
| D2 行级覆盖 | A | 每行 `source_table + source_id + source_hash → target_owner_id`，逐行可逆 |
| D3 非 canonical users | A | 其余 7 users 为 ARCHIVED identity map；不迁移 password hash |
| D4 ambiguous/orphaned | A | QUARANTINED，不进入 active authority，保留原因/hash/source snapshot |
| D5 duplicates/conflicts | A | 仅全字段严格等价才 MERGED，否则 QUARANTINED；当前不预设任何 merge |
| D6 AI operational data | A | ai_runs/ai_call_logs 进入 canonical owner 控制的只读 ARCHIVED 区，不活跃化 |
| D7 quarantine/rollback | A | 独立 quarantine + target→source 逆映射 + source snapshot |
| D8 两套错题 | A | 5 条 Note mistakes 与 3 条独立 Mistakes 分别 MIGRATED；仅严格等价时 MERGED |

### 3.3 12 类实体的确定性规则候选

以下规则已由 D1-D8 授权生效。所有规则均以 immutable source primary key 与 source row hash 验证；任何规则无法唯一解析时进入 QUARANTINED，不回退到 admin/created_by/folder 默认。

| 源实体 | 建议确定性 owner/backfill 规则 | ambiguous/orphaned 规则 |
|---|---|---|
| notes (13；含 5 legacy mistakes) | manifest 逐 `notes.id` 指向 D1 owner；普通 note/blog 与 legacy mistake 分开计数和 hash | 不与独立 mistake 自动 merge；字段冲突或 owner 未确认则 QUARANTINED |
| questions (3) | manifest 逐 `questions.id` 指向 D1 owner；subject 只作关系校验 | subject 缺失/冲突或 manifest 缺行则 QUARANTINED |
| mistakes (3) | manifest 逐 `mistakes.id` 指向 D1 owner；同时要求 Question、DraftItem、Subject 关系解析到相同 owner | 任一关系 orphan/跨 owner 或与 legacy Note 疑似重复未裁决则 QUARANTINED |
| review_items (3) | 先按 `target_type+target_id` 解析已终态 Mistake，再继承其已批准 owner，并在 manifest 固化 | target 非 MIGRATED/MERGED、缺失或跨 owner则 QUARANTINED |
| review_records (4) | 仅从已终态 review_item 继承 owner，记录 `review_record.id→review_item.id` | review_item 非 active terminal mapping 则 QUARANTINED |
| attachments (1) | 逐 `attachments.id` manifest；`created_by`、checksum、storage_key 只作 provenance/完整性证据 | creator 与 D1 owner 不一致时不得覆盖；用户未明确批准则 QUARANTINED |
| attachment_links (1) | attachment 与 `target_type+target_id` 都终态且 owner 相同才继承，并保留 link source ID | attachment/target 任一 orphan、跨 owner 或终态不一致则 ARCHIVED link 或 QUARANTINED，由 D4/D7 决定 |
| capture_items (0) | 批准未来规则：source attachment 已归 owner、`created_by` 仅佐证、逐 ID manifest | 空表不代表规则通过；未来新行解析失败则 QUARANTINED |
| draft_items (6) | 逐 `draft_items.id` manifest；source/target 链与 D1 owner 一致才迁移；`created_by` 仅佐证 | creator 为 non-admin 不自动 merge；链冲突/缺失则 QUARANTINED |
| ai_runs (32) | 因当前 32 条均 targetless，逐 `ai_runs.id` 明确 ARCHIVED 或 MIGRATED，并绑定 D1 custodian owner | 不从 task_type/parent 推断；parent chain 冲突则 QUARANTINED |
| ai_call_logs (47) | 逐 `ai_call_logs.id` 以 D6 保留策略映射到 owner-controlled archive；保留 source hash/时间/状态 | 无 owner/target FK，任何 active migration 都需显式逐行 manifest；缺行则 QUARANTINED |
| users (8) | D1 指定的 source user 1:1 MIGRATED；其余 7 逐 ID 选择 ARCHIVED/MERGED/REJECTED_WITH_REASON | role 不是 owner；重复身份或凭据处置不明则 QUARANTINED，绝不迁移 password hash 到新权威而无单独安全审批 |

### 3.4 Manifest 合同

每条源记录必须恰好一个终态：

- `MIGRATED`：一条源记录对应一条 active target，字段/关系验收通过。
- `MERGED`：多源合并为一 target；manifest 保留全部 source IDs、hash、等价规则和用户批准引用。
- `ARCHIVED`：只读保留，不进入 active authority。
- `QUARANTINED`：隔离保留且不服务流量；记录缺口/冲突与后续决策。
- `REJECTED_WITH_REASON`：明确不迁移；保留不可变原因、source hash 与批准引用，不等同删除源。

manifest 每行至少包含 `manifest_version`、`source_revision`、`source_table`、`source_id`、`source_row_hash`、`source_owner_evidence`、`target_owner_id`、`target_type`、`target_id`、`disposition`、`rule_id`、`conflict_code`、`approved_at`、`approval_reference`、`rollback_source`。全表需证明 `source_count = 五类终态计数之和`，且 source primary key 无遗漏/重复。

## 4. 2026-07-29 简化路径决策（取代原 E-05/E-06）

原 C6-C9 的 shadow target、增量同步、权威切换和 Legacy 归档设计不再执行。系统当前只有 121 条 manifest 记录，source `blog_db` 024 已是唯一 schema/data authority；为该规模新增双库、tombstone、reverse delta 和 cutover contract 会引入超过其收益的双主与恢复复杂度。

简化后的 C6 使用独立只读审计脚本，通过 C1 revision-020 manifest 的 024→020 投影、七类关系 orphan、024 backfill、12 表计数、extension 和 owner/user facts 证明 live source 完整性。所有 SQL 由 `BEGIN READ ONLY` 包裹，报告只包含计数、hash 和标识符，不包含内容正文或凭据。

简化后的 C7 把 C5 custom dump 恢复到时间戳隔离数据库，使用可配置 DB URL 的 verifier/readiness 重新验证 revision、121-row aggregate、关系和 backfill，并执行 `alembic check`。附件压缩包只解压到临时目录验证可读性，随后移动到废纸篓；隔离 DB 无论成功或失败均需删除并复核不存在。

C8/C9 记录为 `SKIPPED`：不存在 target 可切换，也不存在与当前唯一 source 分离的 Legacy authority。该决策不授权删除、部署、生产流量切换或生产配置修改。

## 4.1 历史 E-05 影子迁移计划（已取代，不执行）

目标：源系统保持唯一读写权威，迁移写入完全隔离、不可见的 024 target；证明全量与增量收敛，不切流量、不停旧写、不归档。

范围：12 类 owner manifest、legacy Note mistakes 与独立 Mistakes、附件、关系、全表 count/hash、增量变化与删除检测。前端不改权威来源；后端仅使用批准的迁移工具/隔离连接。

不做：生产读切换、生产写切换、旧系统停写/删除、公开 route 退役、部署。

前置：I10 manifest 获批并复核；G2 最新隔离 dry-run PASS；新鲜 020 备份恢复 PASS；源库经单独授权升级并验证为 024；新的 G3 E-05 明确批准。历史 I11-01 不自动满足新的批准。

执行设计：

1. 源事务使用 `REPEATABLE READ READ ONLY`；对仅 121 行的 12 类数据每周期做全量 primary-key/hash 快照，不依赖不完整的 `updated_at`。
2. target upsert 使用 `(source_table, source_id, manifest_version)` 幂等键；删除通过前后快照缺失显式生成 tombstone，不静默遗忘。
3. 首次全量影子写后，按每类 count、逐行 hash、终态分布、FK/多态关系、owner 覆盖、附件 checksum/path 映射对账。
4. 增量周期必须至少在隔离 clone 证明 create/update/delete/retry 幂等；真实源观察推荐连续 24 小时、至少 3 个周期零未知 drift。该时长需用户在执行前确认。
5. 任一周期 source 有新行时，必须先生成/批准对应 manifest 行；不得用默认 owner 自动吸收。

退出条件：12 类 `unmapped=0`、`duplicate_manifest=0`、未解释 count/hash drift=0、关系 orphan=0、owner conflict=0、重试无重复 target、quarantine/rejected/archived 全部有原因，且 target 从未服务正式流量。否则 E-05 为 BLOCKED/PARTIAL，不能进入 E-06。

## 5. 历史 E-06 权威切换计划（已取代，不执行）

目标：在 E-05 完整通过后，分开完成读权威切换、写权威切换、观察期、旧系统只读归档与回滚演练。

批准关口：

1. G3 的 E-05 批准不自动授权 E-06。
2. E-06 开始前需新的“切换演练”批准。
3. 实际读/写权威切换需再次明确批准；它是生产/源系统状态变化。
4. 旧写停用与 Legacy 只读归档需在观察期后再次明确批准；不删除旧数据。

切换顺序：

1. 在隔离环境演练最终增量、read switch、write switch、reverse delta 与回切。
2. 新鲜 024 数据库+附件备份；记录 manifest、配置、镜像/commit、schema、route 与健康基线。
3. 维护窗口冻结旧写，完成 final delta，要求全类 zero drift。
4. 先切读并执行公开/管理员权限 smoke；再切写并执行最小 create/edit/review/attachment 流程。任一步失败立即 fail closed，不继续。
5. 观察期内 target 为权威，旧系统保持可回切但禁止写；推荐至少 7 日且覆盖 3 个真实管理员会话及四类最小写流程，以较晚者为准。时长/活动门槛由用户批准。
6. 只有观察期、reverse delta、恢复和回切演练均 PASS 后，才请求旧系统只读归档批准。归档保留 schema/revision、dump/hash、附件、manifest、route alias 与恢复 runbook。

硬停止：任何 unmapped/unknown、权限泄露、公开内容 404/错误过滤、写入双主、reverse delta 不可验证、备份不可读、恢复超时超门槛、error rate/latency 超批准阈值、旧系统仍接受写入。切换不得以“观察起来正常”代替门槛。

## 6. I12 最终收口计划

### 6.1 F-01 缺失验证

管理员端：使用隔离 024 环境中的真实管理员账号与真实 JWT/session，不使用 AUTH_BYPASS；验证 dashboard、notes、5 条 legacy Note mistakes、3 条独立 Mistakes、questions、drafts、review、attachments、search、AI/governance 的可见性与最小安全流程。匿名、失效 session、非 admin 逐 API/页面验证 401/403/404 与不泄露。

恢复：使用 C5 024 DB+附件备份恢复到全新隔离目标，核对 revision/head/check、12 类 count/hash、owner manifest、附件可读性与 candidate runtime readiness。简化架构不存在 target authority，因此不虚构回切/reverse delta 证据。2026-07-20 的 020 恢复证据只作前置历史证据。

完整失败态：至少覆盖 backend/API unavailable、局部区块失败、Passkey 失败/超时、失效 session、静态 chunk 失败、上传格式/大小失败、附件 missing、409 version conflict、AI provider unavailable 并可人工回退、空队列/空搜索、迁移 drift。三尺寸均不得无限 loading、假成功或公开页 401/403 噪音；现有 1280 Passkey loading 资产必须重验。

浏览器与可访问性：390×844、1280×800、1440×900 的匿名与管理员各自新 session；截图、网络记录、console、scrollWidth、键盘焦点、Escape/focus trap、accessible name、文本不重叠。交叉验证不得复用主验证进程/fixture/结论。

代码/契约：前端 targeted tests、`npx tsc --noEmit`、`npm run build`；后端 targeted/full relevant pytest、compileall；`alembic current/heads/check`；API contract 与前后端类型；Git diff/check 与可复现构建。所有命令需在批准执行时从 package/CI 配置重新确认。

### 6.2 F-02 fail-closed 部署资格（G4，仅审查，不部署）

以下任一项 UNKNOWN/FAIL/BLOCKED 即 `NOT ELIGIBLE / DO NOT DEPLOY`：

- owner manifest 或 I10/I11 终态未闭合；source/target revision mismatch；migration 文件未进入可审计候选版本。
- 最新数据库/附件备份不可读，024 恢复或切换回滚未演练。
- 任何匿名/管理员/失效 session 权限矩阵失败，AUTH_BYPASS 双 true，默认 JWT secret、wildcard CORS 或开放注册。
- 前端测试/type/build、后端测试/compile、alembic check、浏览器主验证或独立交叉验证失败。
- 双数据源同时可写、legacy route 无兼容/归档方案、监控/日志/回滚 owner 未指定。
- 生产配置/secret、部署 artifact、migration 顺序、维护窗口、容量、健康检查和回退 runbook 不可复现。

G4 只授权资格审查；`ELIGIBLE` 也不授权部署、发布或 migration。

### 6.3 F-03 最终报告结构

最终报告必须带事实日期、环境、commit/artifact、revision、证据链接，并分别声明：

| 维度 | 允许状态 |
|---|---|
| MVP | COMPLETE / PARTIAL / BLOCKED |
| 产品化 | COMPLETE / PARTIAL / BLOCKED |
| 知识工作区 | COMPLETE / PARTIAL / BLOCKED |
| AI-OCR 治理 | COMPLETE / PARTIAL / BLOCKED；真实 provider 成功路径未执行时必须单列 |
| 备份恢复 | 020 HISTORICAL / 024 VERIFIED / BLOCKED |
| 迁移 dry-run | TECHNICAL PASS / DRY_RUN_READY PASS/BLOCKED |
| 权威切换 | NOT AUTHORIZED / PARTIAL / COMPLETE / ROLLED BACK |
| Legacy 归档 | NOT AUTHORIZED / READ-ONLY ARCHIVED / BLOCKED |
| 生产资格 | NOT REVIEWED / NOT ELIGIBLE / ELIGIBLE |
| 实际部署 | NOT DEPLOYED / DEPLOYED；不得由 ELIGIBLE 推断 |

## 7. 风险登记

| 优先级 | 风险与证据 | 影响 | 计划处置 |
|---|---|---|---|
| P0 | migration mismatch（已解除）：源曾为 `020`，代码 head/readiness 为 `024` | 当时后端无法把源库视为合格 schema | C5 已升级 source 至 024；current=head/check PASS |
| P0 | C5 后 Git/schema 权威分裂（已解除）：live source 024，而 021-024 曾 untracked | clean checkout 当时无法重建或审计 live schema | local commit `2c7adcc` 已提交 C3 闭包与 migration；tracked/single-head/current/check PASS；未 push/deploy |
| P0 | C1 独立 verify 是 source=020 时点快照，live source 已为 024 | 原 verifier revision equality 会阻止升级后复核；若直接读 024 全行又会产生预期 hash drift | manifest 保持 020 不变；仅允许显式 024→020 SQL 投影并对 unsupported pair fail closed |
| P0 | 候选 artifact 与 I3-I10 代码纠缠：021-024 与 modified/untracked models、routers、schemas、services、clients/tests 共同构成运行时合同 | 只冻结 migration 会让 ORM/runtime 与 schema 不一致，C5 后无法复现 | C3 冻结完整引用闭包及 SHA-256；切分 Phase 1.0 无关 dirty；C5 前逐文件 hash 必须相等 |
| P0 | 已部署前端与 source DB mismatch：前端指向 public API tunnel；当前 tunnel 后端 8000 无监听、public health 502 | 若未来出现活 backend 连接 `blog_db:5432`，C5 停写/升级可能误伤公开读取或产生并发写 | C5 窗口重复只读核查 backend process/version、`EXPECTED_ALEMBIC_REVISION`、tunnel ingress、`pg_stat_activity`；有活连接则先停写，否则 BLOCKED |
| P0 | owner gate：12 类全 pending，无 canonical owner/manifest | E-05 可能错误归属私有数据，DRY_RUN_READY 必须 BLOCKED | D1–D8 用户决策、逐行 manifest 与独立复核 |
| P0 | 备份恢复适用性：现有可读 dump/恢复仅 revision 020 | 不能证明 024 故障恢复或切换后回退 | upgrade 前新鲜 020 备份；upgrade 后 024 备份；两种恢复/回切演练 |
| P0 | 权威切换不可逆性：021/022 有数据时拒绝 downgrade，023/024 downgrade 删除数据结构/extension | 直接 downgrade 可能失败或丢数据 | 并行 restore/switch 为主回滚；reverse delta 未验证即不切 |
| P0 | 双数据源共存：5 个 Note mistakes 与 3 个独立 Mistakes，精确匹配 0 | 自动替代/merge 会丢错题或重复服务 | 两组独立 manifest，默认分别迁移，merge 必须证据+批准 |
| P1 | attachment 与 6 drafts 的 creator 是同一 non-admin；created_by 不是 owner | admin/creator 默认会错误归属 | created_by 仅 provenance；逐行用户决定 |
| P1 | 32 ai_runs 全 targetless、47 ai_call_logs 无 owner/target FK | 无法继承 owner，可能迁入敏感/无价值日志 | 默认推荐 owner-controlled archive，逐行终态 |
| P1 | E-05 共存期若依赖 updated_at 会漏 delete/无时间戳表 | target drift 或双写分叉 | 小数据全量 PK/hash 周期、tombstone、zero-drift 门槛 |
| P1 | I12 管理员、恢复、失败态未验证；1280 asset 仍 loading | F-01/F-02 不能关闭 | 真实隔离管理员、024 restore、三尺寸失败矩阵与独立交叉验证 |
| P1 | 本范围外 dirty/untracked 工作树及 frontend 57/58 | 整体仓库尚无部署资格 | migration/runtime 由 `2c7adcc` 固定；完整 F-01/F-02 前清理其余范围并修复 App Router test fixture |
| P2 | `incremental-plan.md` 状态头仍停在 I7 approval，而正文已到 I12 | 人员可能误读当前阶段 | 仅在后续获批收口同步，不在本轮改旧记录 |
| P2 | 历史 `:2025` chunk 500 与 1280 Passkey loading | 浏览器证据存在环境/时序不一致 | 新 production process、全新 sessions、network/console 证据 |

## 8. I0–I12 之外

以下不在本规划范围，必须独立立项、重新设计/requirements/tasks 并批准：独立 `/today` TodayOrchestrator 与七项主导航、统一 `content_items/content_revisions`、`knowledge_nodes/knowledge_edges` 与 `/graph`、`publish_snapshots`、`/projects`、Redis 队列+Worker、真实 AI/OCR provider 成功路径、BKT/掌握度/自适应出题、monorepo 重构。本计划不得把它们作为 I12 完成条件或顺带实现。
