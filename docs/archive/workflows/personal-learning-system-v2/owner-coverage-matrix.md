# Phase B：Owner Coverage Matrix

状态：设计完成，当前仅记录现状，不执行 schema 修改。  
判定规则：`owner_id` 是直接、非空或可审计归属字段；`created_by` 只表示操作者/创建者，不等价于 owner。多态 `target_id` 不能单独证明权限边界。

## 私有实体覆盖

| 实体 | 当前 owner_id | 当前权限边界 | 是否需要迁移 | 目标 owner 设计 | 当前结论 |
|---|---|---|---|---|---|
| notes | 否 | `/api/notes` 混合公开 GET 与管理员写入；公开过滤依赖 `status/hidden`；没有 owner 隔离 | 是 | `content_items.owner_id` 非空；公开内容以 visibility/status 过滤；owner/admin command 分开 | 高风险；旧 Note 必须先建立归属映射 |
| questions | 否；有 `created_by` 但不是 owner contract | `/api/admin/questions` 有 admin router 级保护；不能证明多用户隔离 | 是 | `questions.owner_id` 或统一 Content owner seam；`created_by` 保留为审计操作者 | 需要补齐 owner 与跨对象授权检查 |
| question drafts / draft items | 否；部分有 `created_by` | admin API 保护；多态 `target_type/target_id` 约束转换链 | 是 | draft owner 与目标 owner 一致性；转换 command 校验幂等和同 owner | 先迁移归属，再允许转换 |
| mistakes | 否 | `/api/admin/mistakes` admin 保护；模型 visibility 当前为 private；旧 Note 错题路径另存 | 是 | `mistake_cases.owner_id`；owner/admin 可读写；公开展示需显式发布快照而非 private bypass | 高风险；两套错题事实必须映射到一个 owner |
| mistake drafts | 否 | admin router 保护；通过 question/question_draft 关联 | 是 | draft owner；引用的 Question owner 必须一致 | 不能从关联对象隐式推断而不记录 |
| review_items | 否 | `/api/review` 与 `/api/admin/review/items` admin 保护；目标是多态错题 ID | 是 | `review_items.owner_id`，并校验 target owner；`review_records` 继承同一 owner 事务 | 高风险；不得继续依赖 Note 的复习字段 |
| review_records | 否 | 依赖 review_item API；无直接 owner | 是 | 直接 owner 或强制通过 owner-scoped ReviewItem 查询 | 选择一种可审计的继承策略并固定 |
| knowledge_points | 否 | taxonomy admin API 保护；公开/私有边界未统一 | 是 | `knowledge_nodes.owner_id`；个人节点 owner-scoped；公共 taxonomy 另有 explicit visibility | 旧 `subject_id/name` 需映射，不可把全表视为公共 |
| knowledge_point_links | 否 | 多态 target；当前只靠调用方权限 | 是 | link 归属于 source owner，且 source/target 均做授权验证 | 多态 link 是越权高风险 seam |
| attachments | 否；有 nullable `created_by` | `/api/admin/attachments` admin router 保护；visibility 当前 private；storage key 可能泄露存储边界 | 是 | `attachments.owner_id` 非空；`created_by` 仅审计；下载、link 和删除均 owner-scoped/admin | 必须与文件副本和 checksum 一起迁移/恢复验证 |
| attachment_links | 否 | 依赖 attachment API；`target_type/target_id` 无真实 FK | 是 | owner 由 attachment 与 target 双向校验决定；孤立 link 进入冲突队列 | 不得只按字符串 target 放行 |
| AI runs | 否 | `/api/admin/ai/runs` admin router 保护；当前是个人 admin 语义，不是 owner 语义 | 是 | `ai_runs.owner_id` 非空；worker 只能代表受信任务身份；详情和 replay 均 owner/admin scoped | 高敏感；run、target、输入输出的授权要一致 |
| AI call logs | 未确认 owner；与 run 关联粒度不同 | AI router 端点保护不完全统一；日志字段需脱敏 | 是 | `ai_call_logs.owner_id` 或不可绕过的 `ai_run_id -> owner` 关系；敏感字段最小化 | 必须先完成字段与 run 关联审计 |
| managed_content_entries | 否 | `/api/content` public GET 与 admin PUT 混合；key/data 无 owner/版本 | 条件性是 | 站点级公开内容显式 `scope=site`；私有 managed content 另建 owner 归属；不与学习私有数据混用 | 不能把 admin 身份当作 owner；先分类 key |

## 归属原则

1. `owner_id` 表达数据主体，`created_by`、`reviewed_by`、`worker_id` 表达执行者，三者不能互换。
2. 公开对象也保留 owner；公开只是 visibility/publish policy，不代表 owner 为空。
3. 管理员是权限角色，不是所有实体的默认数据 owner。迁移时若历史数据只有管理员账户可推断归属，必须记录 `owner_inference=explicit/admin-default` 和证据。
4. worker 不拥有个人学习数据；任务以受信 worker identity 执行，但写入必须携带原始 owner，并由 service 重新授权。
5. 多态 link、review target、AI target 必须同时校验 owner、对象类型、对象状态，不能以字符串 ID 命中即授权。

## 迁移判定与停止条件

迁移前为每行生成：旧表/旧 ID、目标 owner、归属证据、内容哈希、关联完整性、冲突状态。无法确认 owner 的行进入 `pending_owner_review`，不得默认公开、默认共享或自动删除。出现 owner 冲突、target 不存在、附件 checksum 不匹配或 AI 敏感字段无法过滤时，批次停止并保持只读兼容。
