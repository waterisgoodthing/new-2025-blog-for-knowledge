# Job Queue System 后台任务系统

> 文档治理（2026-10-09）：此文保留目标设计/阶段起点，不是当前实现或执行授权。canonical Question/Mistake/Review 已有实现；阶段号、未实现表名、JWT/Redis及旧 Note 起点按原设计时点解读，认证以现行有状态会话为准。当前事实见 [ARCHITECTURE_CURRENT](ARCHITECTURE_CURRENT.md)。 当前入口见 [文档索引](../DOCUMENTATION_INDEX.md)。

> 状态：第一版建议使用数据库 jobs 表与简单 worker。

## 职责

管理附件处理、缩略图、PDF 拆页、OCR、Capture Router、AI 识别、练习导入、错题文档导入、复习计划刷新和学习报告生成等耗时、可重试、可追踪任务。

## 核心表

- `jobs`：任务类型、目标、状态、优先级、可运行时间、尝试次数、幂等键、进度和错误摘要。
- `job_steps`：步骤顺序、输入输出引用、状态、尝试和耗时。
- `job_logs`：结构化事件、级别、时间和安全处理后的上下文。

状态建议：`queued`、`running`、`succeeded`、`failed`、`retry_wait`、`cancelled`、`dead`。

## 第一版机制

Worker 使用数据库锁或 `SKIP LOCKED` 领取任务；设置租约与心跳；指数退避；幂等 handler；有限重试后进入 dead；管理端可查看、取消或重试。任务载荷只存业务 ID，不内嵌密钥或大文件。

## 第一版范围

数据库 jobs 表、单一简单 worker、进度与步骤、有限重试、失败查看、人工重试和基础任务日志。

## 演进边界

第一版不强制 Celery、Redis Queue、Dramatiq 或 Arq。只有吞吐、调度或隔离证据表明数据库 worker 不足时，才迁移队列执行层，业务 job 契约保持稳定。

## 暂缓范围

复杂分布式编排、跨区域 worker、实时流处理和无限自动重试。
