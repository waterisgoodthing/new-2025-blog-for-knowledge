# Owner Mapping Readiness

日期：2026-07-13  
判定规则：`owner_id` 才是显式 owner contract；`created_by`、admin session、reviewer、worker 或 target 关系均不是 owner 的默认替代。当前报告只评估迁移准备条件，不写入 owner、不生成映射表。

## 总结

- 指定的 10 个实体中，当前没有实体拥有明确的非空 `owner_id`。
- `attachments.created_by` 是 nullable，语义是创建/操作审计字段；不能直接迁移为 owner。
- `mistake_drafts`、`questions` 的草稿链可提供关联证据，但关联对象也没有 owner，因此只能作为 inferred evidence。
- `review_items`、`ai_runs`、多态 link 的 target 关系可以辅助推断，但不能仅凭字符串 ID 授权或归属。
- 所有无法由稳定、显式证据确认的行必须进入 `pending_owner_review`，不得默认归给 admin、默认公开或自动删除。

## Entity readiness matrix

| entity | current_owner_field | available_identity | confidence | migration_action | risk |
|---|---|---|---|---|---|
| `notes` | 无。表内没有 `owner_id` 或 `created_by` | `slug`、`type`、`status`、`hidden`、内容/时间；当前写入路由使用 `get_current_admin`，只能证明操作者/管理边界 | low | 人工确认；按 slug/type/content hash 建立来源记录，禁止 admin=session 直接转 owner | 同一表混合 note/blog/mistake，且公开状态不等于归属；旧错题与独立 mistakes 可能冲突 |
| `questions` | 无 `owner_id`、无 `created_by` | `subject_id`、题目内容、状态/版本、created_at；由 admin router 保护 | low | 人工确认或从已确认的来源对象映射；保留 admin 操作者为审计字段 | admin 保护不提供多用户隔离；subject 不是 owner；可能被多个错题/草稿引用 |
| `mistakes` | 无 `owner_id`、无 `created_by` | `source_draft_item_id`、`question_id`、`subject_id`、内容、时间；admin router 保护 | low | 映射到已确认 Question/draft owner；冲突进入人工队列 | 独立 mistakes 与 `Note(type='mistake')` 双事实来源；关联对象当前也无 owner |
| `mistake_drafts` | 无 `owner_id`、无 `created_by` | `draft_item_id`、`question_id`/`question_draft_id`、`subject_id`、时间；草稿 router 保护 | low | 仅在 Draft Item、Question 或 QuestionDraft owner 已确认且一致时映射，否则人工确认 | 多态/可选来源链不能单独证明 owner；转换前 owner 一致性未被 schema 强制 |
| `review_items` | 无 `owner_id` | `target_type='mistake'`、`target_id`、复习时间；review router/admin router 使用 admin 保护 | low | 通过已确认 Mistake owner 继承，但每行保留 `owner_evidence=derived_from_target`；target 不存在则人工确认 | `target_id` 是字符串且无 FK；当前 Note 复习字段并存，可能造成双重事实 |
| `review_records` | 无 `owner_id` | `review_item_id`、rating、reviewed_at；可沿 ReviewItem → Mistake 追溯 | low | 通过已确认 ReviewItem 继承，或选择直接 owner contract 后再迁移；不从 reviewer/admin 推断 | 历史记录无直接 owner；ReviewItem target 漂移会污染整条复习历史 |
| `knowledge_points` | 无 `owner_id` | `subject_id`、`chapter_id`、name；taxonomy admin API 保护 | low | 先区分公共 taxonomy 与个人节点；无法区分时人工确认 | subject/chapter 是分类关系，不是数据主体；全表默认为公共会造成越权/错误共享 |
| `attachments` | `created_by` nullable，非 owner | `created_by`（若非空）、storage key、checksum、attachment links、创建时间 | low | `created_by` 仅作为 inferred evidence；结合 link target owner、文件 checksum 逐行确认 | 文件可恢复不等于数据归属可恢复；storage key/target 是多态；缺失 owner 或 checksum 必须阻断 |
| `ai_runs` | 无 `owner_id`、无 worker owner 字段 | `target_type`/`target_id`、task/provider/model、review 状态、时间；admin AI run router 保护 | low | 只有在 target owner 已确认且授权链闭合时派生映射；否则人工确认 | 输入/输出字段敏感；target 不一定存在；admin 角色不能自动成为业务 owner |
| `ai_call_logs` | 无 owner、无 `ai_run_id` | task/provider/model、attempts、input_summary、created_at；可按时间/task 与 AI 运行做候选关联 | low | 保留为调用审计；只有建立不可歧义的 run/owner 关联后才能映射，否则人工确认/仅归档 | 调用日志粒度与业务 run 不同；无法安全从时间或 provider 反推 owner；敏感摘要需脱敏 |

## Explicit vs inferred owner

### Explicit owner

当前核心实体中未发现可直接作为 owner 的字段。`attachments.created_by` 和任何路由依赖的 admin identity 都不满足 explicit owner 定义。

### Inferred owner candidates

- `attachments.created_by`：只能表示创建者/操作者候选，必须与业务 target、权限和审计证据交叉核对。
- `mistake_drafts -> draft_items -> question_drafts/questions`：只能在整条关系链的 owner 均已确认且一致时作为派生证据。
- `review_records -> review_items -> mistakes`：只能作为继承候选，不能把 review item 的 admin 操作身份当 owner。
- `ai_runs -> target`：只能在 target 类型、存在性、owner 和运行授权均验证后派生。
- `ai_call_logs`：目前没有不可歧义的业务 run 关联，不能从时间窗口、provider 或 task type 自动推断。

## Required migration input per row

后续真正迁移前，每行至少需要：旧表/旧 ID、候选 owner、`owner_evidence`（explicit 或 inferred）、证据来源 ID、内容/业务哈希、关系完整性、冲突状态、人工确认人和确认时间。候选 owner 为空或证据冲突时必须写入 `pending_owner_review`，不执行自动归属。

结论：owner migration readiness 不通过；此项仍是 Migration Gate 阻断条件。
