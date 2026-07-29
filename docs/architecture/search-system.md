# Search System 搜索系统

> 状态：拟新增；第一版以 PostgreSQL 为主。

## 职责

统一检索笔记、题目、错题、知识点、练习、附件、草稿和 AI 运行记录，同时严格隔离公开与私有结果。

## 第一版设计

使用结构化筛选、`ILIKE`、`pg_trgm` 和统一 `search_index`。索引建议保存 `entity_type`、`entity_id`、标题、规范化文本、subject、visibility、status、更新时间和可选 tsvector；原始私有内容仍由源表拥有。

页面：`/manage/search`。API：`GET /api/public/search` 与 `GET /api/admin/search`。

Public search 只返回 `visibility=public AND status=published`，且使用 public DTO；Admin search 才能检索私有学习数据、OCR、草稿与 AI runs。索引和结果都必须执行同等权限过滤。

## 第一版范围

关键词、实体类型、科目、知识点、状态、日期筛选；分页与高亮；异步索引更新和可重建机制。

## 暂缓范围

向量检索、RAG、自然语言查询、Elasticsearch、Meilisearch 和复杂搜索 DSL。
