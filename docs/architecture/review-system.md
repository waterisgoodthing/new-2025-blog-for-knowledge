# Review System 复习系统

> 状态：目标架构待实现或待迁移。

## 职责

复习系统基于错题、知识点、题目和笔记安排复习，保存不可变复习记录并更新下一次
复习时间。

MVP 第一版只服务手工错题闭环，使用固定间隔或简单 SM-2。BKT、掌握度、Priority
Queue 和复杂容量控制属于后续目标；只有数据质量和独立批次验收通过后才可启用。
任何已启用算法的结果都必须可解释、可回放。

## 核心表

### MVP 第一版

- `review_items`
- `review_records`

### 后续候选

- `knowledge_mastery`
- `knowledge_mastery_events`
- `bkt_parameters`
- `question_drill_attempts`
- `review_settings`
- `subject_review_settings`

`review_items` 使用 `target_type/target_id` 引用复习对象。目标架构中的
`target_type` 可支持 `mistake`、`knowledge_point`、`question`、`note`；MVP 第一版
只启用 `mistake`。第一版不建立 `review_schedules`，当前调度时间统一保存在
`review_items.next_review_at`。

知识点复习对象引用正式 `knowledge_points`；题目、错题和笔记与知识点的归属通过 `knowledge_point_links` 表达，知识点之间的关系通过 `knowledge_relations` 表达。

## BKT 与掌握状态

> 后置能力：不属于 MVP 第一版。

默认参数建议：`P(L0)=0.30`、`P(T)=0.12`、`P(G)=0.20`、`P(S)=0.10`。参数必须版本化，事件记录保存计算前后值。

- `0.00–0.30`：weak
- `0.30–0.60`：learning
- `0.60–0.85`：stable
- `0.85–1.00`：mastered

`knowledge_mastery`、`knowledge_mastery_events`、`bkt_parameters` 是目标表，不属于第一批必做表。第一批代码实现只要求 `review_items`、`review_records` 和简单 SM-2；待作答分类、知识点关联和复习记录的数据质量通过验证后，再启用 BKT 写入与掌握度状态。

## 容量控制

> 后置能力：复杂容量控制不属于 MVP 第一版。

长期建议值可以是：每日 40 分钟、必做最多 15 项、最多 2 个知识点、最多 1 组强化
练习、每日新增 10 项、积压平滑 7 天、逾期分上限 7 天。只有实际使用数据证明需要
容量治理后，才设计全局与科目覆盖设置；这些数值不是 MVP 的默认实现要求。

## 规则

### MVP 提交规则

复习提交必须在一个事务中：

1. 写入不可变 `review_record`。
2. 使用固定间隔或简单 SM-2 计算下一次复习。
3. 更新 `review_item.next_review_at`。

MVP 不写 mastery event，也不依赖 `knowledge_mastery` 或 BKT。

### 后续算法规则

只有掌握度阶段另行设计、迁移和审批后，复习提交才可同时写 mastery event 并更新
掌握状态。AI 只能解释计划，不能静默修改 `next_review_at`、
`mastery_probability` 或 mastered 状态。

## 第一版范围

第一版只包含：

- active 错题对应的待复习项。
- 今日待复习列表。
- 一次复习提交。
- 不可变复习记录。
- 固定间隔或简单 SM-2。
- 更新 `review_item.next_review_at`。
- 管理员权限与必要操作审计。

知识点复习对象、强化练习、复杂容量控制、BKT 与掌握度事件全部后置。

## 暂缓范围

- BKT、掌握度概率与 mastery events。
- Priority Queue 与复杂容量控制。
- 知识点强化练习与题库抽题检测。
- AI 自动改计划。
- 多用户班级策略。
- 复杂自适应测验。
- 无需确认的自动 mastered。

MVP 总范围与批次门禁见 [MVP 第一版范围冻结](./mvp-scope.md)。
