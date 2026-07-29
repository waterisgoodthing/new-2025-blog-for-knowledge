# Subject System 科目系统

> 状态：拟新增；第一版建议。

## 职责与边界

科目是私有学习系统的一级维度，连接知识点、题目、练习、错题、复习、统计、相关笔记和 AI 报告。科目不保存具体题目内容，也不直接执行复习算法。

科目详情页应聚合本科目的知识点、题目、练习记录、错题、复习计划、掌握度、相关笔记和报告；聚合数据仍由各分系统拥有。

## 核心表

### `subjects`

`id`、`name`、`slug`、`parent_id`、`description`、`current_phase`、`exam_weight`、`daily_budget_minutes`、`weekly_budget_minutes`、`is_active`、`sort_order`、`created_at`、`updated_at`。

约束建议：同一父级下 `slug` 唯一；`parent_id` 不得形成环；预算非负。

### `subject_review_settings`

`id`、`subject_id`、`daily_budget_minutes`、`weekly_budget_minutes`、`max_items_per_day`、`max_knowledge_points_per_day`、`priority_weight`、`is_enabled`、`created_at`、`updated_at`。

每个科目最多一条有效配置；未配置时继承全局复习设置。

## 第一版范围

科目 CRUD、启停与排序；科目详情聚合；科目级复习预算；与章节、知识点、题目及统计的关系。

## 暂缓范围

多用户共享科目、复杂课程体系、自动课程规划、AI 自动调整预算和跨科目依赖推断。
