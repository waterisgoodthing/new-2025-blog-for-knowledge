# Analytics / Report System 学习统计与报告系统

> 状态：拟新增。统计系统计算事实，AI 只解释已提供指标。

## 职责与模型

报告类型：`daily`、`weekly`、`monthly`、`subject`、`knowledge_point`、`review`、`ai_quality`、`ocr_quality`。

核心表：`learning_metrics_daily`、`learning_metrics_weekly`、`subject_metric_snapshots`、`knowledge_metric_snapshots`、`learning_reports`。

指标应由 SQL 或确定性规则计算，并记录统计窗口、口径版本、源数据截止时间和重算状态。AI 只能依据 `provided_metrics` 写摘要、解释和建议，不得编造数值，也不得因报告自动修改复习计划。

## 第一版指标

练习数量与正确率、错题新增/确认数、复习完成率与逾期数、学习时长、科目分布、知识点掌握变化、OCR/AI 成功率和草稿采纳率。

## 第一版范围

日/周聚合、科目与知识点快照、基础周报、后台重算和数据口径说明。

## 暂缓范围

复杂数据大屏、预测排名、跨用户比较、AI 自主决策和对外公开个人学习报告。
