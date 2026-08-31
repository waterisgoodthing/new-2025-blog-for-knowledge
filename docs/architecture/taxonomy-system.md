# Taxonomy System 知识组织系统

> 状态：拟新增；第一版建议。

## 职责

管理章节、知识点、知识点别名、标签和知识关系。知识点是 BKT 掌握度、题库抽题、错题归因和复习调度的核心单位；标签只用于辅助筛选，不能代替知识点。

## 概念边界

- `subject`：哪一科。
- `chapter`：科目内部章节或模块。
- `knowledge_point`：具体学习点或考点。
- `tag`：辅助筛选标签。
- `knowledge_link`：知识点之间的先修、相关、包含或易混关系。

## 核心表

- `chapters`：`id`、`subject_id`、`parent_id`、`name`、`slug`、`sort_order`、状态和时间戳。
- `knowledge_points`：`id`、`subject_id`、`chapter_id`、`name`、`slug`、`description`、状态和时间戳。
- `knowledge_aliases`：知识点别名及来源。
- `knowledge_point_links`：业务对象与知识点的关联；使用 `knowledge_point_id + target_type + target_id`。可选 `source_type/source_id` 只追踪建议或导入来源。
- `knowledge_relations`：知识点与知识点之间的有向关系。
- `tags` / `taggings`：标签及多态关联。
- `knowledge_point_suggestions`：AI 或规则产生的新增、合并、别名及关系建议。

## 安全规则

AI 可以建议知识点、别名和 `knowledge_relations`，但不得静默创建、合并、移动或删除正式知识点。业务对象关联只写 `knowledge_point_links`；知识点之间不得使用该表。合并必须保留重定向、来源和审计。

## 第一版范围

章节树、知识点 CRUD、别名、基础关系、标签、人工审核建议和按科目筛选。

## 暂缓范围

全自动知识图谱、复杂本体、向量聚类、跨用户共建和 AI 自动合并。
