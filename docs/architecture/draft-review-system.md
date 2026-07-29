# Draft Review System 草稿审核系统

> 状态：拟新增；AI/OCR/Capture 输出进入正式系统的统一安全闸门。

## 核心表与状态

统一表 `draft_items` 保存草稿类型、来源、状态、版本、验证结果和目标引用；细分表包括 `question_drafts`、`mistake_drafts`、`practice_attempt_drafts`、`knowledge_point_suggestions`、`note_ai_suggestions`。

上述五类细分草稿表都必须包含非空且唯一的 `draft_item_id`。`draft_items` 是统一审核索引，细分表保存类型化字段；不得把所有类型字段堆进通用 payload。

完整状态：`pending`、`needs_fix`、`approved`、`rejected`、`converted`、`archived`、`failed`。第一版可只实现 `pending`、`needs_fix`、`rejected`、`converted`；确认并转换应作为一个幂等动作，避免中间 `approved` 长期漂移。

## 审核流程

```text
AI / OCR / Capture 输出
  → validator
  → draft_items
  → 带 draft_item_id 的类型化草稿
  → 管理员查看来源与差异
  → 修正 / 拒绝 / 确认转换
  → 正式表 + 审计记录
```

页面：`/manage/drafts`、`/manage/drafts/[id]`。转换必须校验草稿版本、来源仍有效、必填字段和目标重复；转换后保留草稿与正式实体映射。

AI、OCR、Capture 的候选输出在进入 Question、Mistake、Practice Attempt、Knowledge Point 或 Note 正式表前，必须先进入 `draft_items`。

## 第一版范围

统一队列、按类型筛选、来源预览、字段校验、人工修正、拒绝、幂等转换和审计。

## 暂缓范围

大规模批审、多人审批、AI 自动批准、复杂工作流编排和跨用户协作。
