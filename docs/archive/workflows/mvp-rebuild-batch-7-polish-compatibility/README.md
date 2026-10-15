# MVP Rebuild Batch 7：体验收口、旧路由兼容、数据质量

## 任务目标

在不新增大型能力、不重构公开站、不删除或自动迁移旧数据的前提下，为第一版 MVP 做最后一轮
体验收口、旧入口兼容、明显死链检查、本地试运行说明与数据质量审计。

## 涉及领域

- home：首页学习轻卡入口与状态文案
- manage：已完成 `/manage/*` MVP 页面的 empty/loading/error、表单校验、危险操作确认与本地可用性
- mistakes：公开 `/mistakes` 读取边界、旧 `/write-mistake` 兼容策略
- notes/write：保留旧 `/write-note`，不破坏原流程
- public compatibility：公开博客、笔记、错题读取能力不能被封闭或污染
- data quality：只检查和记录 Batch 2–5 数据完整性，不自动迁移或删除旧数据

## 当前状态

**实现侧收口完成，等待用户验收。**

用户已于 2026-07-04 批准执行 [`tasks.md`](./tasks.md)。Batch 7 已执行至 P0-09；
本批不自动宣称整个项目闭环，仍需用户验收。

## 工作流文件

- [需求](./requirements.md)
- [设计](./design.md)
- [任务清单](./tasks.md)
- [验证记录](./validation.md)
- [审查记录](./audit.md)
- [数据质量只读报告](./data-quality-report.md)
- [本地试运行说明](./local-runbook.md)

## 已确认起点

- Batch 6 已由用户确认通过，可以进入 Batch 7 workflow 准备阶段。
- Batch 7 只做体验收口、旧路由兼容、数据质量，不做新业务扩展。
- 任何实现任务必须等用户确认 Batch 7 `tasks.md` 后才能执行。

## 核心边界

- 不新增 AI、OCR、BKT、完整练习系统、对象存储、云部署或新的大型功能。
- 不大规模重构旧公开页，不封闭公开读取页面。
- 不删除旧数据，不自动迁移旧错题、旧笔记或公开内容。
- 不引入复杂兼容层；旧入口处理应优先使用明确提示、轻量跳转或文档化保留策略。
- 不把 Batch 7 做成“顺手修所有历史债”的大 diff。
