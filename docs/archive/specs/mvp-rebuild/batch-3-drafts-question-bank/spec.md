# Batch 3：题目草稿 / 草稿审核 / 题库

## 目标

跑通“题目草稿 → 人工审核 → 正式题目”的核心链路。

## 背景

MVP 需要先保证人工录入与审核可靠，再考虑 AI、OCR、自动分流或批量处理。
附件提出的独立题目模型尚需与当前以 `Note` 为中心的系统做正式架构确认。

## 任务范围

1. 在本批设计阶段确认 `draft_items`、`question_drafts`、`questions`、
   `question_sources` 与现有 `Note` 模型的迁移或共存方案。
2. 经批准后新增题目草稿基础结构和手动创建入口。
3. 新增 `/manage/drafts` 列表与 `/manage/drafts/[id]` 详情。
4. 支持编辑、人工确认题目草稿。
5. 确认后生成正式题目，并将草稿状态更新为 `converted`。
6. 正式题目支持科目和知识点绑定。
7. 题目来源支持 `manual`。
8. 未确认草稿不能进入正式题库。

## 允许修改范围

- 本批对应 workflow 与架构决策文档。
- 经批准的模型、schema、service、thin router、migration 和测试。
- 对应 `src/lib/api/` 客户端。
- `/manage/drafts`、`/manage/questions` 路由及专属组件。
- 必要导航、共享选择器和本批验证材料。

最终文件范围必须写入本批 tasks 并获用户批准。

## 禁止事项

- 不做 AI 自动生成题目。
- 不做 OCR 自动识别。
- 不做 Capture Router。
- 不做批量审核或复杂去重。
- 不做完整练习系统。
- 不绕过当前 `Note` 架构直接假设独立模型已经存在。

## 涉及页面

- `/manage/drafts`
- `/manage/drafts/[id]`
- `/manage/questions`
- `/manage/questions/[id]`

## 涉及数据表

候选表：

- `draft_items`
- `question_drafts`
- `questions`
- `question_sources`
- Batch 2 的 `knowledge_point_links`

这些表是本批待设计范围，不代表当前仓库已经存在或已批准迁移。

## 验收标准

1. 可以手动创建并编辑题目草稿。
2. 可以人工审核并转换为正式题目。
3. 正式题目可绑定科目和知识点。
4. 来源可记录为 `manual`。
5. 未确认草稿不会进入正式题库。
6. 转换操作具有一致性保护，不会重复生成正式题目。
7. 管理员权限、前后端合同、迁移和异常路径均有验证证据。

## 非目标

AI/OCR、自动分流、批量审核、完整练习系统、高级去重和搜索。

## 完成后 handoff 要求

记录最终架构决定、数据迁移、API、页面、转换一致性证据、未完成项、风险和 Batch 4
前置条件，并等待用户确认。
