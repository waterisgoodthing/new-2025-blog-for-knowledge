# Phase B：Source of Truth

状态：设计完成，未执行迁移。  
基线：Phase A A-01/A-02/A-03；当前数据库 Alembic 版本为 `018 (head)`。  
范围：个人学习后端线与其公开内容/导出 seam；本文件不改变任何事实来源。

## 决策摘要

目标运行态采用 PostgreSQL 作为正式业务事实来源。静态 Markdown/JSON、GitHub 文件、AI 输入输出快照和附件文件系统不能继续作为同一对象的并行写入来源；它们分别承担公开构建输入、导出/归档、可审计运行证据和 blob 存储职责。

迁移策略含义：

- `preserve`：保留现有表/对象作为目标事实来源，先补齐验证与权限，不做无必要的重建。
- `migrate`：把旧来源逐对象映射到目标对象，使用稳定键、内容哈希、人工冲突队列和可回滚批次。
- `archive`：停止其作为在线事实来源，保留不可变只读副本和索引。
- `compatibility-read`：在切换窗口内只读旧来源，禁止新写入，用于旧 URL、旧 API 或历史导出兼容。

## 实体矩阵

| 实体 | 当前事实来源（Phase A 事实） | 目标事实来源 | 迁移策略 | 设计约束 |
|---|---|---|---|---|
| notes | `notes`；同一表承载 `note`、`blog`、`mistake`，并含旧错题/SM-2 字段；公开静态内容还存在 `public/` 与 Markdown | 按 `type` 拆入统一 `ContentItem/ContentRevision`；错题语义进入 `MistakeCase`；公开输出进入发布快照 | `migrate` + `compatibility-read` | 旧 `Note` 不立即删除；迁移前按 slug、type、正文哈希和公开状态去重；旧 `/api/notes` 只保留兼容读/明确 command seam |
| questions | `questions`；题目/题目来源和草稿链由 migration 012 建立 | `Question` 继续作为题目本体事实来源；作答事件单独归属 Practice/Attempt | `preserve` | Question 不承载某次作答、复习调度或 AI 审核最终状态；草稿转换必须幂等 |
| mistakes | 独立 `mistakes`（migration 013）与 `Note(type='mistake')` 并存；另有 `mistake_drafts` | `MistakeCase`（正式错题）作为唯一正式错题事实；Question 作为题目来源；ReviewItem 作为复习事实 | `migrate` + `compatibility-read` | 独立 `mistakes` 优先保留并对齐目标；旧 Note 错题逐条映射；冲突不自动覆盖；旧错题 API 只读兼容 |
| review_items | `review_items`/`review_records` 与 `notes.next_review/last_reviewed/ef/interval/repetitions` 并存 | `ReviewItem` + `ReviewRecord`（目标名称可由后续 schema 设计确定）作为唯一复习事实 | `migrate` + `compatibility-read` | 调度状态不再写回 Note 或 Mistake 正文；旧 Note 复习字段只作为迁移输入和兼容读，不再接受新写入 |
| knowledge_points | `knowledge_points` + `knowledge_point_links`；另有字符串 `Note.knowledge_points` | `KnowledgeNode`、alias、edge 和 typed content links | `migrate` + `compatibility-read` | 旧 taxonomy ID/name 保留映射表；字符串知识点先进入待确认队列；节点不拥有复习、发布、项目或 AI 状态 |
| managed_content_entries | `managed_content_entries(key,data)`；另有 `src/app/*/list.json`、公开 Markdown/JSON 和 GitHub push 流 | 结构化 managed/published content registry；学习内容仍归 Content bounded context，不与站点配置混表 | `preserve` + `compatibility-read` | `about`、`shares`、`projects`、`pictures`、`snippets`、`bloggers`、`site-settings` 等 key 先保持独立；后续仅按 key 建立版本/发布快照，不把静态页面数据静默当私有学习数据 |
| attachments | `attachments` 元数据 + `attachment_links`；`storage_provider='local'`，文件候选在 `backend/uploads/` | Attachment metadata/link 仍为附件事实；文件 blob 由明确 storage adapter 管理；业务对象只持有 attachment ID | `preserve` | 不在本阶段搬运文件；先建立 dump 与文件副本的同一批次校验；link 的 `target_type/target_id` 必须逐对象可验证；缺失 blob 标记 `missing`，不伪造成功 |
| AI runs | `ai_runs`（migration 018）记录业务 Run；`ai_call_logs` 记录 provider 调用粒度；部分旧 `Note.ai_metadata` 仍存在 | `AiRun` 作为业务运行、校验与人工审核事实；`AiCallLog` 作为调用明细；正式对象只引用已审核结果 | `preserve` + `compatibility-read` | `replay_input`、`output_data`、`input_summary` 按敏感字段策略过滤；旧 `ai_metadata` 只读兼容；AI 不直接成为正式内容写入源 |

## 写入方向

```text
UI / API command / worker
  -> application service
  -> PostgreSQL target owner
  -> audit event / export / public snapshot
```

GitHub/Markdown 只允许作为导出、归档、构建输入或恢复副本；公开构建失败不能反向覆盖 PostgreSQL。附件 blob 与元数据必须以 checksum、storage key 和备份批次关联。AI provider 输出先进入 `AiRun`/draft，人工接受后才能产生领域 command。

## 切换前置条件

在 `source-of-truth` 从设计变为执行前，必须完成：对象映射和哈希报告、owner 补齐方案、匿名/管理员权限测试、Alembic-only schema 方案、数据库与附件恢复演练、Migration 018 恢复验证，以及旧读路径的兼容窗口和删除条件。未满足时状态保持 `BLOCKED`，不执行切写或删除。
