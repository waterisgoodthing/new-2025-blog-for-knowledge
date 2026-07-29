# MVP Rebuild Batch 6：AI / OCR 占位与依赖隔离

## 任务目标

在不接入真实模型、OCR、Capture Router 或后台队列的前提下，为未来 AI/OCR/Jobs/Settings
留下诚实、无副作用的管理端入口，并验证当前题目、错题、附件、复习主流程不依赖这些占位能力。

## 涉及领域

- manage：`/manage/ai`、`/manage/jobs`、`/manage/settings`
- attachments：`/manage/attachments/[id]` 显示“OCR 第一版暂未启用”
- navigation：管理工作区导航与必要 dashboard 入口
- ai/ocr/jobs/settings：仅占位文案与静态结构，不新增后端合同或持久化表
- public compatibility：不改变公开页面，不开放访客 AI/OCR 操作

## 当前状态

**Batch 6 已由用户确认通过。**

Batch 6 已按批准的 [`tasks.md`](./tasks.md) 执行至 P0-09。用户已于 2026-07-03 确认通过，
并允许进入 Batch 7 workflow 准备阶段；Batch 7 代码实现仍需单独审批其 `tasks.md`。

## 工作流文件

- [设计](./design.md)
- [需求](./requirements.md)
- [任务清单](./tasks.md)
- [审查记录](./audit.md)
- [验证记录](./validation.md)

## 已确认起点

- Batch 5 已由用户确认关闭，可以进入 Batch 6 workflow 准备。
- 附件基础可提供详情页，但 OCR 状态仍应明确未启用。
- 本仓库已有历史 AI 路由和旧管理页组件；本批不得扩大或包装成新 MVP 已启用能力。
- `/manage/(workspace)` 由 AuthGate 保护，Batch 6 页面应继续落在该 workspace 下。

## 核心边界

- 不新增 AI/OCR/job/settings 数据表、迁移、真实 API、依赖或外部服务配置。
- 不加入“开始识别”“生成分析”“重新生成”等可触发真实调用的按钮。
- 占位页面必须明确“第一版暂未启用”，不能虚构模型、prompt、调用记录或成功结果。
- 验证主流程没有新增 AI/OCR 请求依赖。
