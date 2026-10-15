# Batch 7 数据质量只读报告

## 范围

本报告只读检查 Batch 2–5 相关数据与 legacy mistake note，不写入、不迁移、不删除。

检查范围：

- subjects / chapters / knowledge_points / knowledge_point_links
- question_drafts / questions
- mistake_drafts / mistakes
- review_items / review_records
- attachments / attachment_links
- legacy `notes(type='mistake')`

## 表存在性与计数

| 表 | 状态 | 行数 |
|---|---:|---:|
| subjects | exists | 0 |
| chapters | exists | 0 |
| knowledge_points | exists | 0 |
| knowledge_point_links | exists | 0 |
| question_drafts | exists | 0 |
| questions | exists | 0 |
| mistake_drafts | exists | 0 |
| mistakes | exists | 0 |
| review_items | exists | 0 |
| review_records | exists | 0 |
| attachments | exists | 0 |
| attachment_links | exists | 0 |
| notes | exists | 13 |

## 完整性检查

| 检查项 | 结果 |
|---|---:|
| questions 缺失 subject | 0 |
| question_drafts 缺失 subject | 0 |
| mistakes 缺失 question | 0 |
| mistake_drafts 缺失 question | 0 |
| review_items(type=mistake) 缺失 target mistake | 0 |
| review_records 缺失 review_item | 0 |
| attachment_links 缺失 attachment | 0 |
| attachment_links 缺失 question_draft target | 0 |
| attachment_links 缺失 question target | 0 |
| attachment_links 缺失 mistake target | 0 |
| attachments storage_key 类路径泄露 | 0 |

## Legacy mistake note

| 检查项 | 结果 |
|---|---:|
| notes(type='mistake') | 5 |
| published 且 hidden=false 的 legacy mistake notes | 5 |

## 结论

- Batch 2–5 新表已存在，但当前本地数据为空；没有发现孤儿关联。
- legacy `Note(type='mistake')` 仍是当前公开 `/mistakes` 的主要数据来源，共 5 条公开记录。
- 附件表没有发现 `storage_key` 以 `/` 开头或包含 `..` 的路径泄露模式。

## 剩余风险

- 当前本地新 MVP 表为空，因此本次不能证明“有真实业务数据时”的体验质量，只能证明 schema 与空数据路径没有明显孤儿关系。
- legacy mistake note 与新 `mistakes` 模型并存；本批不自动迁移，后续若要统一数据模型必须单独开需求、设计迁移和回滚。
