# Owner Migration Design

日期：2026-07-13  
状态：设计完成；当前不写入 owner、不创建映射表、不执行迁移。

## 1. Owner Contract Definition

### Explicit owner

由实体自身的非空、受约束 `owner_id` 明确表达数据主体，并能关联到已验证的用户身份。当前 Phase C 证据显示 10 个指定实体均没有此类字段；`attachments.created_by` 不是 explicit owner。

### Inferred owner

由可审计关系链、已确认的上游 owner、内容/关系 hash 和一致的授权证据推导的候选 owner。inferred owner 只能作为候选，不能在无冲突时自动等同于 explicit owner。

### Unknown owner

没有足够证据、证据冲突、target 不存在/多态关系无法验证、或只能依赖 admin session/worker/reviewer/时间窗口/provider 的归属。unknown 必须进入 `pending_owner_review`，不可默认归属、公开、删除或迁移。

## 2. Entity Mapping Strategy

| Entity | 当前身份字段/证据 | 风险 | 推荐策略 |
|---|---|---|---|
| `notes` | 无 owner；slug/type/status/hidden/content/time；admin route 只证明操作者边界 | note/blog/mistake 混合；公开状态不等于归属；与旧错题事实来源可能冲突 | 用 slug/type/content hash 建候选；人工确认；保留 admin 为审计字段 |
| `questions` | 无 owner；subject、内容、状态/版本、时间；admin router | subject 不是 owner；可能被多个草稿/错题引用 | 仅从已确认来源对象派生；否则人工确认 |
| `mistakes` | 无 owner；draft/question/subject 关系、内容、时间 | 关联对象也无 owner；独立 mistakes 与 legacy Note mistake 双事实来源 | 仅在 Question/Draft owner 已确认且一致时派生；冲突人工处理 |
| `mistake_drafts` | 无 owner；draft item、question/question draft、subject 关系 | 可选/多态来源链不能单独证明 owner | 仅在整条链 owner 一致时候选映射，否则 pending |
| `review_items` | 无 owner；`target_type`/`target_id`、复习状态/时间 | 多态 target 无 FK；可能与 Note 复习字段形成双事实 | 从已确认 target owner 继承并记录 derived evidence；target 不存在则阻断 |
| `review_records` | 无 owner；review item、rating、时间 | 历史记录依赖 review item；target 漂移会污染链路 | 从已确认 ReviewItem 继承，不能从 reviewer/admin 推断 |
| `knowledge_points` | 无 owner；subject/chapter/name；taxonomy admin API | 可能是公共 taxonomy 或个人节点，当前未区分 | 先做公共/个人分类；无法区分时人工确认 |
| `attachments` | nullable `created_by`；storage key/checksum/link/time | created_by 可能是操作者；多态 link 和 blob 归属不确定 | created_by 仅 inferred；与 target owner、checksum、link 逐行交叉验证 |
| `ai_runs` | 无 owner；target、task/provider/model、review state/time | target 可能不存在；输入/输出敏感；admin 不是 owner | target owner 与授权链闭合后派生；否则人工确认 |
| `ai_call_logs` | 无 owner、无 `ai_run_id`；task/provider/model/attempts/input_summary/time | 不能从时间/provider/task 安全关联 run；敏感摘要 | 默认仅作审计归档；只有不可歧义的 run/owner 关联才候选映射，否则 pending/仅归档 |

## 3. Mapping Table Design

设计表 `owner_mapping`，用于迁移前 dry run 与人工审核队列。该表本身只在后续获批执行阶段创建；本阶段不创建。

| Field | Purpose | Required rule |
|---|---|---|
| `id` | mapping row identity | stable unique identifier |
| `source_table` | source entity | allowlisted table name |
| `source_id` | source primary key | original ID preserved |
| `candidate_owner_id` | proposed owner | nullable until confirmed |
| `evidence_type` | `explicit` / `inferred` / `unknown` | never infer explicit from admin identity |
| `evidence_source` | source row/relationship/audit reference | concrete IDs, not free-form assertion only |
| `content_hash` | content identity/dedup evidence | algorithm and canonicalization documented |
| `relation_hash` | relationship snapshot evidence | includes relevant polymorphic links |
| `confidence` | numeric or enum confidence | low is not auto-approval |
| `conflict_status` | `none` / `conflict` / `missing` / `target_missing` | conflict blocks automatic migration |
| `review_status` | `pending` / `approved` / `rejected` / `deferred` | only approved rows eligible later |
| `reviewer` | human reviewer identity | required for approved/rejected |
| `review_time` | decision timestamp | required for approved/rejected |

Recommended additional fields: `source_snapshot_id`, `canonical_key`, `owner_policy_version`, `created_at`, `updated_at`, and a redaction-safe review note. Exact types, indexes, FK behavior and retention are UNKNOWN until the owner contract is approved.

### Row-level rule

每条源数据至少要有 source table/ID、candidate owner、evidence type/source、content hash、relation hash、confidence、conflict/review state。candidate owner 为空或证据冲突时只能进入 `pending_owner_review`。

## 4. Conflict Handling

### Automatic approval conditions

Automatic approval is allowed only if all are true:

1. An explicit owner exists, or an inferred owner is derived from a fully confirmed owner chain approved by policy.
2. All relevant targets exist and their types match.
3. Candidate evidence sources agree; no competing owner candidate exists.
4. Content and relation hashes are reproducible and match the frozen baseline.
5. The mapping is not based solely on `created_by`, admin, session, worker, reviewer, time window, provider or public visibility.
6. Sensitive objects (`attachments`, `ai_runs`, `ai_call_logs`) pass redaction and authorization review.

当前没有任何实体满足已证实的 automatic approval 条件；这不是“全部拒绝”，而是当前状态 UNKNOWN/待审核。

### Human review conditions

必须人工审核：只有 inferred evidence、多个候选 owner、legacy Note 与独立 mistake 冲突、公共/个人 taxonomy 不明、attachment target/checksum 不完整、polymorphic target 不存在或类型不匹配、AI run/log 关联不确定。

### Migration-prohibited conditions

禁止迁移：owner 为空、冲突未解决、source row 无法稳定定位、hash 不一致、target 不存在、敏感字段无法按策略保护、review status 未 approved、或 reviewer/review time 缺失。

