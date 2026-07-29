# Mistake System 错题系统

> 状态：目标模型待迁移。当前实现仍以 `Note(type="mistake")` 兼容运行。

## 职责与边界

错题系统记录用户做错或需要复盘的题。来源可以是练习、题库抽题、手动录入或错题文档上传。题目本体归题库，某次作答归练习，调度归复习。

错题默认 `private`。只有确认且状态为 `active` 的错题才能创建 `review_item`。

## 核心表

- `mistakes`：正式错题，关联 `question_id`、来源作答、科目、错因、解析、状态和可见性。
- `mistake_drafts`：待人工确认的错题候选。
- `mistake_import_jobs` / `mistake_import_files`：错题文档导入任务与来源文件。

正式错题应保留 `question`、`my_answer`、`correct_answer`、`analysis`、`knowledge_points` 等业务信息或稳定引用，迁移不得丢失现有一等字段。

正式 Mistake 与知识点通过 `knowledge_point_links` 关联；知识点之间的先修、相关或易混关系只使用 `knowledge_relations`。`mistake_drafts` 必须通过 `draft_item_id` 一对一追溯统一审核索引。

`mistake_drafts` 优先引用正式 `question_id`，若题目仍在审核则引用 `question_draft_id`；两者至少存在一个。`question_text` 仅作 snapshot，不能成为唯一题目来源。草稿建议保存 `correct_answer_snapshot`、`explanation_snapshot` 和结构化 `reason_category`。

## 状态

| 状态 | 含义 | 进入复习 |
|---|---|---:|
| `unconfirmed` | 尚未确认 | 否 |
| `needs_fix` | 信息缺失或冲突 | 否 |
| `active` | 已确认并可复盘 | 是 |
| `archived` | 已归档 | 否 |

## 第一版范围

手工录入、练习转入、草稿确认、状态管理、知识点关联、私有详情和显式加入复习。

## 暂缓范围

公开题库化、无确认自动入库、大规模批审、AI 自动归档和多用户协作。
