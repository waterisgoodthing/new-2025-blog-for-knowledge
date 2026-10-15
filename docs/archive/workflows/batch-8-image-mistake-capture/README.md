# Batch 8：图片错题采集与 AI 错因草稿

## 任务目标

在 Batch 0–7 与 MVP 本地试运行链路之上，规划一条适合日常高频使用的图片错题采集闭环：

```text
图片上传
→ private attachment
→ capture_item
→ OCR / 多模态识别
→ AI 生成可编辑草稿
→ mistake_draft
→ 人工确认
→ mistake
→ review_item
```

Batch 8 解决“手工录入步骤过多”的真实使用问题，但不推翻现有题目、错题、复习和附件模型。

## 触及领域

- `attachments`、`attachment_links`：保存并关联原图，始终保持 private。
- `mistakes`、`review`：复用 `mistake_drafts → mistakes → review_items`。
- `subjects`、`knowledge_points`：提供人工选择与 AI 建议目标。
- `manage`：候选入口为 `/manage/capture` 或 `/manage/mistakes/capture`。
- `ai/ocr`：只规划 Batch 8 所需的最小调用边界和运行状态。
- `public compatibility`：公开页面不得读取或展示 capture、OCR、AI 草稿。

## 必须复用的既有系统

- `attachments`
- `attachment_links`
- `mistake_drafts`
- `mistakes`
- `review_items`
- `subjects`
- `knowledge_points`
- `/manage/mistakes`
- `/manage/attachments`

其中 `capture_items` 只负责采集过程状态与草稿输出，不成为第二套正式错题事实源。

## 当前状态

**Batch 8 P0-01 至 P0-09 已完成并关闭。真实 AI/OCR：not verified，作为后置补证项记录，不阻塞 Batch 8 关闭。**

- P0-01 至 P0-07：已完成（审计、模型、adapter、schema、转换流程、管理端页面、权限验证）。
- P0-08：14 项验证全部执行（14 passed、Alembic 015、schema/约束/索引、TSC、build、匿名拒绝、禁止项搜索）。
- P0-09：已完成（handoff、risks、范围 diff、禁止项交叉审查）。
- 真实 AI/OCR：not verified（deepseek API 模型名称过期，回退供应商超时），已转入后置补证/真实 provider 可用性 backlog。
- Batch 9 已作为后续独立批次完成，本文件不再作为进入 Batch 9 的审批门。

## 工作流文件

- [需求](requirements.md)
- [设计](design.md)
- [任务清单](tasks.md)
- [审批检查表](checklist.md)
- [风险](risks.md)
- [移交说明](handoff.md)

## 核心原则

1. AI/OCR 输出只能进入草稿，不得直接写正式 `mistakes`。
2. `capture_item` 失败不得污染 `mistake_drafts`、`mistakes` 或 `review_items`。
3. 原图必须保留为 private `attachment`。
4. AI 生成内容必须允许人工编辑。
5. `mistake_draft` 必须人工确认后才能成为正式 `mistake`。
6. `review_item` 仍然只由正式 `mistake` 生成。
7. 公开页面不得展示 capture、AI、OCR 结果。
8. Batch 8 只做最小实用闭环，不做完整 AI Gateway。
9. Batch 8 为 Batch 9–12 留稳定接口，但不提前实现其治理能力。

## 后续分阶段路线

| 批次 | 目标 |
| --- | --- |
| Batch 8 | 图片错题采集 MVP |
| Batch 9 | AI Gateway 最小内核 |
| Batch 10 | Task / Prompt / Validator 管理 |
| Batch 11 | AI Run 审计与人工流转 |
| Batch 12 | 多供应商、路由、成本与稳定性治理 |

Batch 8 先打通真实高频场景。Batch 9 之后再逐步治理 AI 调用；不得把完整 AI Gateway、
多供应商、模型路由、成本统计或完整审计系统塞入 Batch 8。

## 明确不做

完整 AI Gateway、多供应商管理、模型路由、Prompt 管理后台、成本统计、完整 AI 审计事件系统、
BKT、完整练习系统、批量 OCR、PDF 多页拆题、公开展示 AI 结果、旧 `Note(type="mistake")`
迁移、对象存储、云部署、生产级任务队列。
