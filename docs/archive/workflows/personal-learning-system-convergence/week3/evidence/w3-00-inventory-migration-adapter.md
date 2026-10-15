# W3-00 盘点 B — migration-026 适配器机制结论

- agent: W3-00-inv-inventory（profile=senior-backend-engineer，role=consulted/read-only）
- 日期: 2026-09-22
- 对象: `backend/app/services/legacy_note_migration_adapter.py`、`backend/alembic/versions/026_legacy_system_retirement.py`、`backend/app/services/review_item_service.py`、`backend/app/services/mistake_service.py`、migrations 028/029、相关测试
- 方法: source 阅读 + 文件级引用。未执行数据库命令、未跑写库测试。

---

## 1. ledger / 幂等机制如何工作

### 1.1 表结构（ledger 主表）

`public.legacy_note_migrations`，建于 `backend/alembic/versions/026_legacy_system_retirement.py:1109-1175`。

| 列 | 含义 | 引用 |
| --- | --- | --- |
| `id UUID PK` | ledger 行 id | `026:1110` |
| `source_note_id UUID NOT NULL` | 源 Note（`REFERENCES notes(id) ON DELETE RESTRICT`） | `026:1111` |
| `source_revision INTEGER NOT NULL CHECK (source_revision > 0)` | 源版本 | `026:1117` |
| `source_hash CHAR(64)` | 源内容 sha256 hex | `026:1118` |
| `mapping_version VARCHAR(64) NOT NULL` | **映射版本（一等公民列）** | `026:1120` |
| `idempotency_key VARCHAR(128) NOT NULL` | 幂等键 | `026:1121` |
| `target_*`（8 个 UUID + `target_qkp_ids`/`target_projection_ids` INTEGER[]） | 目标链: question-draft-item/draft/question/question-source、mistake-draft-item/draft/mistake、review-item | `026:1122-1131` |
| `state public.legacy_note_migration_state NOT NULL` | 状态机 | `026:1132`（enum 定义 `026:291-292,1019-1020`） |
| `legacy_ef/ef_bits/interval/repetitions/next_review/last_reviewed` + `mapped_next_review_at/mapped_last_reviewed_at` | 源 SM-2 快照与映射后调度 | `026:1135-1142` |
| `legacy_review_json`/`canonical_payload`/`migration_notes` JSONB | 不可变输入快照 | `026:1143-1145` |
| 4 组审批槽（source/question_conversion/mistake_conversion/schedule，各 `approved_by/at/sequence`）+ 对应 event_id | 三方独立审批 | `026:1146-1167` |

**唯一约束（幂等的骨架）** — `026:1170-1174`：

- `UNIQUE (source_note_id, mapping_version)` —— **同一源 Note 在同一 mapping version 下至多一行**；换 mapping version 则是另一行、另一套目标
- `UNIQUE (idempotency_key)` —— 幂等键全局唯一
- `UNIQUE` 于每个 `target_*` 标量列 —— 防止两个 ledger 行抢占同一目标

辅助表: `legacy_note_migration_events`（`026:705-720` 一带，含 `approval_kind IN ('source','question_conversion','mistake_conversion','schedule','rollback','state_transition')`）、`legacy_note_migration_rejections`（`026:748-759`，`UNIQUE (source_note_id,mapping_version,idempotency_key)` 与 `UNIQUE (source_note_id,mapping_version,source_hash,reason)`）、`legacy_migration_rollback_audits`（`026:736-743`，`UNIQUE (source_note_id,mapping_version)`）、`legacy_migration_guard_nonces`（16-key 防重放标记，`026:788-796,886`；测试 `backend/tests/test_legacy_note_migration_contract.py:185-209`）。

### 1.2 幂等键（idempotency key）如何表达 mapping version

`build_legacy_migration_idempotency_key` — `backend/app/services/legacy_note_migration_adapter.py:51-68`:

```
identity = f"legacy-note-migration|{source_uuid}|{source_revision}|{source_hash}|{mapping_version}"
key      = "legacy:" + sha256(identity).hexdigest()
```

- **mapping version 直接参与哈希**（`:67`）→ 同一源在不同 mapping version 下得到不同幂等键
- 校验: mapping_version 非空且 ≤64 bytes（`:59-60`）；source_revision 为正 int（`:61-62`）；source_hash 为 64 位小写 hex（`:63-66`），否则 `INVALID_IDEMPOTENCY_IDENTITY`
- DB 端独立重算并比对: `026_legacy_system_retirement.py:378-382`（`create_legacy_note_migration_pending` 内 `'legacy:'||encode(digest('legacy-note-migration|'||...))'`），不一致则拒绝 —— 应用端伪造键不可绕过
- 单元测试: `backend/tests/test_legacy_note_migration_adapter.py:177-187`（同输入同键；revision 变、hash 变 → 键变）
- 静态契约: `backend/tests/test_legacy_note_migration_static_contract.py:46-52`（026 内含 `p_idempotency_key IS DISTINCT FROM` 重算校验）

### 1.3 目标 ID 的确定性

`_stable_id` — `adapter.py:71-75`:

```python
_UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "legacy-note-migration")
_stable_id(source, mapping_version, kind) = uuid.uuid5(_UUID_NAMESPACE, f"{source}:{mapping_version}:{kind}")
```

`kind` ∈ {`question`,`question-draft-item`,`question-draft`,`question-source`,`mistake-draft-item`,`mistake-draft`,`mistake`,`review-item`}（`adapter.py:365-372`）。**源 + mapping_version + kind 决定目标 UUID** → 重放不产生重复目标；不同 mapping version 产生不同目标 UUID（正是新版本能并入同一 ledger 而不撞 `UNIQUE (target_*)` 的原因）。

### 1.4 状态机与审批

- 入口 `migrate()` — `adapter.py:555-713`：`SET TRANSACTION ISOLATION LEVEL SERIALIZABLE`（`:584`）、`_assert_runner` 要求 `current_user == session_user == 'legacy_note_adapter_runner'`（`:298-301`）
- 三方审批人必须互不相同（`:586-591` `APPROVAL_ACTORS_MUST_BE_INDEPENDENT`），schedule 审批人也独立（`:588-591`）
- owner 函数（026 安装，SECURITY DEFINER）: `create_legacy_note_migration_pending`（`026:311-414`）、`record_legacy_note_migration_approval`（`026:416-456`，kind ∈ source/question_conversion/mistake_conversion/schedule，重复审批抛 `LEGACY_MIGRATION_DUPLICATE_APPROVAL`，`026:430-432`）、`transition_legacy_note_migration`（`026:132-238`，期望态/源/hash/mapping 不符抛 `LEGACY_MIGRATION_STALE_EXPECTED_STATE`，`026:146`）、`record_legacy_note_migration_rejection`（`026:265-282`）、rollback 系列（`026:242-261` + `legacy_migration_rollback_audits`）
- 状态值: `pending_mapping → ready → migrated_active | migrated_paused`，旁路 `retained_public_only`、`rolled_back`、`failed`（adapter 中的终态判定 `adapter.py:608,632`；`should_retain_public_only` 分支 `:634-647`）
- 源漂移防护: `canonicalize_legacy_note`（`026:474+`）实时重算 canonical payload，与调用方传入不一致抛 `SOURCE_DRIFT`（`adapter.py:595-599`）；已有 ledger 行 hash/revision 不一致抛 `existing migration source hash mismatch`（`:606-607`）
- 幂等重放: 已有 ledger 行且状态 ∈ {`migrated_active`,`migrated_paused`,`retained_public_only`,`rolled_back`} → 直接返回 `_ledger(..., idempotent=True)`，不再写目标（`:604-609`、`:632-633`）
- dry-run: `migrate(..., dry_run=True)`（`:575`，`:630-631`）—— 走完 `create_legacy_note_migration_pending` 后**提前返回 ledger 快照**，不建目标、不迁移状态。注意 dry-run **会留下 `pending_mapping` ledger 行**（非无副作用），见 §5

### 1.5 mapping version 在现有夹具中的表达

现有 rehearsal 用字符串 mapping version 区分场景（同一源可多版本共存）:

- `backend/tests/lsr03_rehearsal.py:54` `mapping_version=f"v1-{label}"`；`:103-104` `"v1-active"`
- `backend/tests/lsr03_seed_rehearsal.py:157` `"v1-paused"`
- `backend/tests/lsr03_final_verifier_harness.py:25-28` `"v1-active"|"v1-paused"|"v1-retained"|"v1-chapter-019"`
- `backend/tests/lsr03_rollback_rehearsal.py:184,278` 按 `mapping_version='v1-paused'|'v1-active'` 选行

→ **结论: mapping version 就是 ledger 的 `mapping_version VARCHAR(64)` 列 + 幂等键与稳定 ID 的组成要素。PR-09 只需引入新字符串（如 `v3-week3-public`，≤64 bytes），即自动获得独立 ledger 行、独立幂等键、独立目标 ID，无需新表、无需平行脚本。**

---

## 2. 现有映射如何决定 canonical mistake 的 visibility

**恒为 `'private'`，无任何条件分支。**

| 插入点 | 位置 | 写死值 |
| --- | --- | --- |
| `_create_targets`（`include_mistake=True` 路径） | `backend/app/services/legacy_note_migration_adapter.py:453-458` | `INSERT INTO public.mistakes (... status,visibility,version) VALUES (...,'active','private',1)` |
| `_finish_mistake_targets`（migrate 主路径实际调用者） | `adapter.py:528-533` | 同样 `...'active','private',1` |

- 两处均**不读**源 Note 的 `status` / `hidden`，也无 visibility 参数
- `should_retain_public_only`（`adapter.py:282-295`）只判断「公开源 + 确定性映射失败 → `retained_public_only`（不建目标）」，与已建 mistake 的 visibility 无关
- 源 `status`/`hidden` 仅被记录进 ledger（`026:1115-1116` 列 `source_status`/`source_hidden`；`adapter.py:614,623` 传入 pending 函数）与 `canonical_payload`（`026:493` `'status',n.status,'hidden',n.hidden`）—— 只做 provenance，不参与 visibility 映射
- 与已定映射规则冲突: 源 `status=='published' AND hidden==false` → `visibility='public'`，否则 `'private'`（`docs/workflows/personal-learning-system-convergence/design.md:99`、`requirements.md:126`、week3/README.md:111）
- 上游已标注须 reconcile: week3/README.md:29、TRACKING.md:42

**结论: 现有适配器 visibility 恒为 private；PR-09 必须在新 mapping version 中实现上述条件映射，而不是另起迁移脚本。**

---

## 3. ReviewItem 创建用的是 v1 还是 v2 算法

### 3.1 适配器 = **v1（历史默认，硬编码）**

| 位置 | 证据 |
| --- | --- |
| `adapter.py:464-470` | `INSERT INTO public.review_items (...,algorithm,...) VALUES (...,'fixed_interval_v1',:interval,:repetitions,:next_review,:last,:mistake)` |
| `adapter.py:538-545` | `_finish_mistake_targets` 内同样 `'fixed_interval_v1'` |

- 同时把 legacy SM-2 的 `interval/repetitions/next_review/last_reviewed` 直接拷入 `interval_days/repetitions/next_review_at/last_reviewed_at`（`:468-470,543-545`）
- 对照 LSR03 校验器也断言 v1: `backend/tests/lsr03_final_verifier_harness.py:453` `t.ri_algorithm IS DISTINCT FROM 'fixed_interval_v1'` 视为不一致

### 3.2 已验收的 v2 算法（Week 2）

| 组件 | 位置 | 内容 |
| --- | --- | --- |
| 调度语义 | `backend/app/services/review_item_service.py:13-26` | `fixed_interval_v2`（design D2，**no v1/v2 selection**）: `LAPSE_INTERVALS={0:1,1:1,2:2}`、`SUCCESS_LADDER={1:3,2:7,3:14,4:30}`、`MASTERY_REPETITIONS=4`、`MASTERY_MIN_RATING=4`；`schedule_v2(rating,repetitions)` |
| 提交路径 | `review_item_service.py:62-81` | `submit_review` 只走 `schedule_v2`（`:70`），写 `ReviewRecord.previous_state/new_state`（`:73-77`） |
| 模型默认 | `backend/app/models/review_item.py:23` | `algorithm` default/server_default `'fixed_interval_v2'`；`last_rating` 可空（`:28`） |
| CHECK | `review_item.py:35` | `algorithm IN ('fixed_interval_v1','fixed_interval_v2')` |
| schema | `backend/app/schemas/review_item.py:19` | `Literal["fixed_interval_v1","fixed_interval_v2"]` |
| migration 028 | `backend/alembic/versions/028_review_items_v2.py:104-112` | 加 `last_rating`、CHECK 放宽到 v1\|v2、**存量行与 DEFAULT 全切 `'fixed_interval_v2'`**；downgrade 有损回 v1（`:123-126`） |
| migration 029 | `backend/alembic/versions/029_review_record_states.py:66-80,94-97` | `review_records` 加 `previous_state`/`new_state` + 双 CHECK（v2 状态机所需） |
| canonical 转换路径 | `backend/app/services/mistake_service.py:168` | `ReviewItem(target_type="mistake",...,state="active")` **不传 algorithm** → 落库为默认 `fixed_interval_v2` |
| 测试 | `backend/tests/test_review_scheduling_v2.py`、`test_review_schema_v2.py:86-103,471-501`、`test_mistake_review_service.py:179` | v2 语义/schema/默认值契约 |

### 3.3 结论

- **适配器创建的 ReviewItem 用 v1（`fixed_interval_v1`）**；**Week 2 已验收、模型默认、canonical 转换路径用 v2（`fixed_interval_v2`）**。
- 二者并存于 CHECK（028 放宽为 v1|v2），但 v2 是当前权威语义（`review_item_service.py:13` "design D2, final — no v1/v2 selection"）。
- PR-09 要求「ReviewItem 创建切到已验收 v2 算法」（week3/README.md:94、tasks/pr-09.md:36）→ 新 mapping version 必须写 `algorithm='fixed_interval_v2'`，并配套 v2 的 `interval_days/repetitions/next_review_at` 语义（见 §6 U-2 的 legacy SM-2 → v2 调度值映射未决项）。

---

## 4. PR-09 复用方案结论

### 4.1 以「新 mapping version」并入同一 ledger（而非平行脚本）

1. **新 mapping_version 字符串**（≤64 bytes，形如 `v3-week3-public` / `week3-public-v2`，由主 agent 定名），写入现有 `migrate(..., mapping_version=<new>)`（`adapter.py:555-576`）:
   - 自动获得独立 ledger 行（`UNIQUE (source_note_id, mapping_version)`，`026:1170`）
   - 自动获得独立幂等键（mapping_version 参与哈希，`adapter.py:67`；DB 端重算校验 `026:378-382`）
   - 自动获得独立目标 UUID（`_stable_id` 含 mapping_version，`adapter.py:74-75`）→ 不与 `v1-*` 目标撞 `UNIQUE (target_*)`（`026:1171-1174`）
   - **不修改 migration 026 的数据库治理结构**（requirements.md:126 硬约束）—— 只是 `mapping_version` 的新取值 + 适配器映射逻辑变化
2. **复用同一套 owner 函数与审批流**: `create_legacy_note_migration_pending` → `record_legacy_note_migration_approval`（source / question_conversion / mistake_conversion / schedule，三方独立 actor，`adapter.py:586-591`）→ `transition_legacy_note_migration`。provenance / 冲突检测 / SERIALIZABLE / runner 角色约束全部保留（`adapter.py:584-585,298-301`）
3. **visibility 映射改造**: 在 `_create_targets` / `_finish_mistake_targets` 的 `INSERT INTO public.mistakes` 两处（`adapter.py:458,533`）把写死的 `'private'` 改为按源 `status=='published' AND hidden==false` 计算（数据源即 `canonical_payload["status"]`/`["hidden"]`，`026:493` 已产出；或 `payload["status"]`/`payload["hidden"]`，`adapter.py:284` 已用同名键）。建议以参数/纯函数 `map_visibility(status, hidden)` 注入，保持可测
4. **ReviewItem 切 v2**: `adapter.py:467,542` 的 `'fixed_interval_v1'` 改为 `'fixed_interval_v2'`，并按 v2 语义填 `interval_days/repetitions/next_review_at/last_reviewed_at`（对齐 `review_item_service.schedule_v2` 与 `mistake_service.convert_mistake_draft` 的 `ReviewItem(...)` 形状，`mistake_service.py:168`）。`last_rating` 留空（028 允许 NULL，`review_item.py:28`）
5. **不平行建脚本**: 不新建独立 5 行迁移脚本（week3/README.md:94 明令 "not a parallel five-row script"）；所有写入仍走 `_create_targets`/`_finish_mistake_targets` + owner 函数单事务
6. **源集冻结为前置**（W3-D02 fail-closed 顺序）: 先冻结 legacy mistake 写入（清单 A §4），再在 scratch 跑新 mapping version —— 否则 `SOURCE_DRIFT`（`adapter.py:598-599`）与 hash mismatch（`:607`）会阻断迁移

### 4.2 与 `v1-*` 已有 ledger 行的关系（策略未定，见 §6 U-1）

- 新 mapping version 会为同一源再建一行 ledger 与一套新目标 UUID（含第二个 canonical mistake）。若 scratch/生产已有 `v1-*` 迁移产物，「并入同一 ledger」不等于「复用同一行」。
- 候选策略（需主 agent 定版）:
  - (a) 只对**尚无任何 `migrated_*` ledger 行**的源跑新 mapping version；已有 v1 产物的源走 reconcile/补 visibility 的单独处置（但这又接近"平行"，须谨慎）
  - (b) 全量跑新 mapping version，把 `v1-*` 行视为历史 rehearsal 痕迹（LSR03 是 rehearsal，见 `backend/tests/lsr03_rehearsal.py`），scratch 起点干净则无冲突
  - (c) 对已迁移源禁止新 mapping version（`UNIQUE (source_note_id)` 级策略，需应用层守卫）
- week3/README.md:111 只说 "reused with a new Week 3 mapping version"，未指定 (a)/(b)/(c)。

---

## 5. dry-run / 幂等重放 / 机器可读对账报告的挂钩点

### 5.1 dry-run

| 挂钩点 | 位置 | 现状 | PR-09 动作 |
| --- | --- | --- | --- |
| `migrate(..., dry_run=True)` | `adapter.py:575,630-631` | 已存在: pending 建行后返回 ledger，不建目标、不迁移 | 直接复用 |
| 副作用 | `adapter.py:621-625`（`create_legacy_note_migration_pending` 仍写 `pending_mapping` 行） | dry-run **非无副作用** | runner 侧二选一: (i) dry-run 事务整体 ROLLBACK；(ii) 报告中显式声明 dry-run 会留 pending 行。建议 (i) 以满足 "先 dry-run 后写入" 的可重入性 |
| 调用面 | 目前无测试调用 `dry_run`（`backend/tests` 内 grep 无 `dry_run`） | 缺覆盖 | PR-09 fixture 矩阵补 dry-run 正/负例（tasks/pr-09.md:24） |

### 5.2 幂等重放

| 挂钩点 | 位置 | 现状 | PR-09 动作 |
| --- | --- | --- | --- |
| 终态短路 | `adapter.py:604-609,632-633` | 已有终态行 → `idempotent=True`，零目标写入 | 重放断言 `result.idempotent is True` 且 target_* 不变 |
| 幂等键唯一 | `026:1170`（`UNIQUE (idempotency_key)`）+ `026:392-396` 旧键不一致拒绝 | 已有 | 同 mapping version 同源重放走同一键 |
| 稳定目标 ID | `adapter.py:71-75` | 已有 | 重放不产生新 UUID |
| 目标 UNIQUE | `026:1171-1174` | 已有 | 双写会被 DB 拒绝（兜底） |
| 现有重放证据 | `backend/tests/lsr03_rehearsal.py:93,113`（打印 `result.idempotent`）、`test_legacy_note_migration_adapter.py:177-187` | 部分 | PR-09 补「rerun 幂等」fixture（tasks/pr-09.md:24 "重跑幂等"） |

### 5.3 机器可读对账报告（JSON 或 CSV，tasks/pr-09.md:124）

**现状: 无内置报告**（adapter/026 均无 reconciliation 输出；`backend/tests` 无 dry_run/对账报告代码）。应在 runner 层挂钩:

| 报告字段（design.md:99 定名） | 取数点 |
| --- | --- |
| `source_total` | 迁移前快照: `count(*) FROM notes WHERE type='mistake'`（冻结后源集稳定） |
| `eligible` | 通过 `validate_legacy_mapping_payload`（`adapter.py:121-202`）且非 `should_retain_public_only`（`:282-295`）的源数 |
| `migrated` | `SELECT count(*) FROM public.legacy_note_migrations WHERE mapping_version=<new> AND state IN ('migrated_active','migrated_paused')`（`:608,632` 状态集） |
| `retained` | 同上 `state='retained_public_only'`（`:634-647`） |
| `rejected` | `SELECT ... FROM public.legacy_note_migration_rejections WHERE mapping_version=<new>`（`026:748-759`；写入 `record_legacy_note_migration_rejection`，`026:265-282`） |
| `drifted` | runner 捕获 `SOURCE_DRIFT`（`adapter.py:598-599`）与 `existing migration source hash mismatch`（`:607`）per-source 计数 |
| provenance | `legacy_note_migration_events`（`026:705-720`）+ `legacy_migration_rollback_audits`（`026:736-743`）按 ledger_id 关联 |
| visibility 映射核对 | `count(*) FROM mistakes m JOIN legacy_note_migrations l ON l.target_mistake_id=m.id WHERE l.mapping_version=<new>` 按 `m.visibility` 分组，对照源 `l.source_status`/`l.source_hidden` 的 2×2 矩阵（design.md:99 映射规则） |
| 数量核对 | `source_total == migrated + retained + rejected + drifted + 未处理`；`migrated == count(target_mistake_id NOT NULL)` |

输出格式建议 JSON（一行一源 + 汇总块）落 `week3/evidence/`（w3-00.md:104 证据命名前缀 `w3-00-`；PR-09 阶段用 `pr-09-`）。

**挂钩位置建议**: 新 scratch runner（W3-00 交付的 `scripts/week3-scratch-guard.*` 之上）在 per-source `migrate()` 循环内收集 `LegacyNoteMigrationResult`（`adapter.py:21-39`，含 `state`/`idempotent`/`target_*`/`manual_review_required`），循环后一次性 SELECT ledger/rejections/events 汇总成报告。

---

## 6. unresolved_issues

| # | 问题 | 影响 | 建议 |
| --- | --- | --- | --- |
| U-1 | **新 mapping version 与既有 `v1-*` ledger/产物的关系未定**（§4.2 (a)/(b)/(c)） | 决定 scratch/生产源集与是否产生重复 canonical mistake | 主 agent 定版后再开工迁移 runner；scratch 排练产物按 (b) 处理最简，生产另议 |
| U-2 | **legacy SM-2 调度值 → v2 调度字段的映射规则未定**。适配器现拷 `interval/repetitions/next_review/last_reviewed` 到 v1 语义列（`adapter.py:468-470,543-545`）；v2 的 `repetitions` 是 streak、`interval_days` 走 `SUCCESS_LADDER`（`review_item_service.py:16-26`），二者语义不等价 | 直接切 v2 字面值会导致 due/mastered 语义漂移 | 需定版: 建议新 mapping version 对未复习源用 v2 初值（repetitions=0、interval_days=0 或按 `schedule_v2` 首评推导），把 legacy SM-2 快照留在 ledger `legacy_*` 列（`026:1135-1143`）作 provenance，不复刻进 v2 状态 |
| U-3 | **dry-run 的副作用语义未定**（`adapter.py:630-631` 会留 `pending_mapping` 行） | 影响 "先 dry-run 后写入" 的可重入性与对账计数 | 建议 runner 在 dry-run 事务 ROLLBACK；或报告显式计数 dry-run pending 行 |
| U-4 | 对账报告 schema 未定（design.md:99 仅给字段名 `source_total/eligible/migrated/retained/rejected/drifted`） | 实现者自由度大，评审无合同 | 建议 W3-00 合同固化阶段把报告 JSON schema 写入 `backend/tests/` 或 `src/contracts/` fixture（tasks/w3-00.md:99） |
| U-5 | 新 mapping_version 具体命名未定（约束: ≤64 bytes，`adapter.py:59`） | 低 | 主 agent 定名（如 `week3-public-v1`） |
| U-6 | `include_mistake=False` 分支（`adapter.py:420-432`）与 `_finish_mistake_targets` 双路径均含 v1 ReviewItem INSERT，改造须两处一致（`adapter.py:467,542`） | 漏改一处会残留 v1 | 实现时双路径 + LSR03 校验器（`lsr03_final_verifier_harness.py:453` 断言 v1）一并更新；该校验器当前断言 `ri_algorithm='fixed_interval_v1'`，与 v2 目标冲突，须同步改写 |
| U-7 | LSR03 系列测试/校验器硬编码 `v1-active`/`v1-paused` 与 `fixed_interval_v1`（`lsr03_final_verifier_harness.py:25-28,453`、`test_lsr03_rollback_static_contract.py:103-116`） | 新 mapping version / v2 落地后这些契约测试会与目标态冲突 | 属 PR-09 实现范围的测试改写清单，不在本次只读盘点内改动 |
