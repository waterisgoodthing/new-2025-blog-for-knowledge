# ADR-004：AI 输出必须经过人工审核

- 状态：Accepted
- 日期：2026-07-13
- 范围：AI、Ingestion、Content、Knowledge、Mistake、Review、Publish

## 决策

AI 输出只能进入 `generated -> pending_review -> accepted / rejected` 状态流。AI 不直接覆盖正式正文、知识节点、题目、错题、复习计划或发布快照。

## 原因

学习内容需要可追溯、可解释、可撤销；OCR 和生成式模型都可能产生结构错误或事实错误。

## 后果

每个结果必须记录 AI Run、Prompt/模型版本、依据、引用、置信度和人工操作。低风险元数据可以自动建议，但仍必须满足可审计和可撤销要求。

