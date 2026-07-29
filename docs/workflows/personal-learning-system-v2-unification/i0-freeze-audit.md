# I0 冻结审查与来源索引

日期：2026-07-20
状态：`PARTIAL / USER APPROVAL PENDING`

## 范围与结论

本次只读审查完成了 I0 的事实来源分层和术语/边界核对，未执行代码、数据库、迁移、备份恢复、浏览器验收、部署或旧系统切换。

结论：A-05 已完成；A-01～A-03 需要用户确认，A-04 依赖这些确认。因此 I0 不能标记为 `PASS`，但可以安全地停在“决策待确认”状态。

## 来源索引

| 来源 | 类型 | 截至/观察日期 | 可用于证明 | 不可用于证明 | 后续动作 |
|---|---|---:|---|---|---|
| [统一主方案](./master-plan.md) | 待批准目标设计 | 2026-07-20 | 目标产品、目标边界、阶段意图 | 当前代码、数据、API 已实现 | 等待 A-01～A-03 批准 |
| [设计边界](./design.md) | 待批准目标设计 | 2026-07-20 | 领域归属、API 过渡、文件状态机 | 当前数据库已具备对应实体 | 用于后续设计/实施审批 |
| [需求与验收](./requirements.md) | 待批准验收基线 | 2026-07-20 | 每阶段应出具的验收证据 | 任一需求已经 PASS | 随每个增量更新证据 |
| [递进执行计划](./incremental-plan.md) | 待批准执行顺序 | 2026-07-20 | I0–I11 的批准与停止顺序 | 任何增量已经获批 | 逐增量重新批准 |
| [V2 最高层架构](../../architecture/personal-learning-system-v2.md) | 既有目标架构 | 未标注现状快照 | PostgreSQL 主数据、领域拆分的历史目标 | 当前路由、表、迁移或运行状态 | A-04 后列为被统一方案引用的目标依据 |
| [MVP 范围冻结](../../architecture/mvp-scope.md) | 既有 MVP 范围基线 | 未标注现状快照 | 旧 `Note(type="mistake")` 兼容约束、Batch 范围 | 独立错题迁移已经完成 | A-04 后保留为 legacy MVP 基线 |
| [历史 Migration Gate 审计](../personal-learning-system-v2/audit/migration-gate.md) | 历史只读审计 | 文档记录为 revision 018 | 当时备份、恢复和 schema 风险 | 当前 revision、当前恢复能力或 Gate 已解除 | I1 的 B-04～B-06 重新验证 |
| `backend/main.py` | 当前代码观察 | 2026-07-20 | 启动要求 revision `020`、readiness 检查只读、生产 bypass 拒绝 | 数据库实际已在 020、恢复已成功 | I1 读取实际数据库与备份证据 |
| `backend/app/routers/notes.py` | 当前代码观察 | 2026-07-20 | `/api/notes` 公开读取与 `published + hidden=false` 过滤 | 目标 `/api/public/**` 已存在 | I1 建立 API 兼容矩阵 |
| `backend/app/models/{question,mistake,review_item}.py` 与管理路由 | 当前代码观察 | 2026-07-20 | 独立 Question/Mistake/Review 模型及管理员路由已并存 | 旧 Note 数据已经全量迁移或新模型是唯一权威 | I1/I2 以数据和浏览器证据确认 |

## 已冻结的术语与解释

| 术语 | I0 解释 | 当前状态 |
|---|---|---|
| 正式主数据 | 目标上由 PostgreSQL 承担；GitHub Markdown 只作导出、归档、公开构建输入和恢复副本 | 目标已定义，实际写入方向待 I1 核验 |
| 当前实现事实 | 仅由带日期的代码、数据库只读审计、API/浏览器验证和恢复记录证明 | 已采用 |
| 历史审计 | 仅证明其执行日期的发现；不自动继承为当前运行时事实 | 已采用 |
| 旧 Note 错题 | `Note(type="mistake")` 的公开/兼容合同 | 仍需保留兼容决策，不能假定已迁移 |
| 新错题链路 | Question、Mistake、Review Item 等独立模型及管理端路由 | 已观察到代码并存，数据权威状态未知 |
| Migration Gate | 备份、联合恢复、schema authority、映射和路由矩阵的 fail-closed 门槛 | `BLOCKED`，仅可在 I1 重验证后改变 |
| dry-run | 已达到 `DRY_RUN_READY` 后，只向可销毁的隔离目标写入的迁移演练 | 未获授权、未执行 |

## I0 现状发现

1. 目标 `/api/public/**` 分层与现有 `/api/notes` 合同不相同。当前匿名读取显式过滤 `hidden=false` 与 `status=published`；因此任何目标路由迁移都必须先建立字段/调用方/退役矩阵。
2. 旧 MVP 基线把错题描述为 `Note(type="mistake")`，但当前代码已有 `questions`、`mistakes`、`review_items` 等独立模型和 `/api/admin/*` 路由。它们的真实数据覆盖、权威来源和公开兼容性尚未由数据库或浏览器证据证明。
3. 历史 migration-gate 审计记录 revision 018 和 `Base.metadata.create_all` 风险；当前启动代码要求 revision 020，且代码注释表明 readiness 检查不创建 schema。历史发现应保留，但不得作为当前 Gate 结论的唯一证据。
4. 生产环境对 `AUTH_BYPASS` 双开关已有启动拒绝代码；本轮未启动应用，故只标记为代码观察，未标记为运行时验证。

## 待用户确认的冻结决策

| ID | 决策 | 建议冻结内容 | 影响 |
|---|---|---|---|
| I0-DEC-01 | 产品与导航边界 | 采用“今日、采集、学习、复习、知识库、项目、发布”七项主导航；管理工作区不进入日常主导航；公开内容继续公开读取 | **APPROVED 2026-07-20**；固定后续 UI/路由范围 |
| I0-DEC-02 | MVP 边界 | MVP 只要求人工 Question → Attempt → Mistake → Review 闭环、私有附件基础、公开/管理权限边界和今日摘要；文件工作区、WikiLink、统计、复杂 AI/搜索与迁移切换后置 | **APPROVED 2026-07-20**；限制 I2～I8 的范围 |
| I0-DEC-03 | 阶段与停止规则 | 采用 I0–I11 顺序；I1 未通过不得进入 I2；I9/I10 需额外 Gate 与逐项批准；任何失败门槛阻断发布 | **APPROVED 2026-07-20**；建立唯一执行顺序 |

## I0 退出条件

- A-05：`PASS`，来源索引与术语已建立。
- A-01：`PASS`，I0-DEC-01 已于 2026-07-20 获用户批准。
- A-02：`PASS`，I0-DEC-02 已于 2026-07-20 获用户批准。
- A-03：`PASS`，I0-DEC-03 已于 2026-07-20 获用户批准。

## 已批准的唯一引用关系

自 2026-07-20 起，以下关系生效：

1. `master-plan.md` 是本任务组经 I0 批准的产品愿景、信息架构和阶段意图的唯一入口。
2. `design.md` 是领域、权限、API 过渡和文件工作区边界的唯一设计依据；`requirements.md` 是对应验收依据；`tasks.md` 与 `incremental-plan.md` 是唯一执行顺序与批准门依据。
3. `docs/architecture/personal-learning-system-v2.md` 保留为被引用的长期目标架构，不以其实体名称证明当前实现。
4. `docs/architecture/mvp-scope.md` 保留为 legacy MVP 范围与兼容约束依据；其中对 `Note(type="mistake")` 的描述不等于当前数据迁移结论。
5. `docs/workflows/personal-learning-system-v2/audit/migration-gate.md` 保留为历史风险依据；其 revision 与恢复结论必须在 I1 重验证，不能直接作为当前 Gate 状态证据。
6. 当前实现事实仍只由带日期的代码、数据库只读审计、API/浏览器验证和恢复记录证明；本 I0 决策不授权 I1 及后续实现、迁移或部署。

- A-04：`PASS`，上述唯一引用关系已冻结。
- I0 总体：`PASS / IMPLEMENTATION NOT AUTHORIZED`。下一增量 I1 需单独批准。
