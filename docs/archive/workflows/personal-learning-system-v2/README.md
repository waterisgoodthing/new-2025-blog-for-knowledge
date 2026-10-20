# Personal Learning System V2

## 任务目标

将“个人学习系统整体重构设计方案”固化为新的最高层架构目标，并建立一套可审查、可迁移、可分阶段验收的后续开发流程。

本任务组的核心结果不是立即重写代码，而是让后续所有学习系统开发都围绕同一条主链推进：

```text
采集 -> 整理 -> 知识关系 -> 学习与练习 -> 错误 -> 复习 -> 总结 -> 选择性发布
```

## 涉及领域

- `home` / `manage`
- `notes` / `mistakes` / `review`
- `auth` / `sync` / `share`
- `AI`、OCR、附件、搜索、后台任务、统计和共享基础设施

前端原始静态博客线与 FastAPI/PostgreSQL 个人知识后端线都在影响范围内，但本轮只更新架构与流程文档，不修改 `src/`、`backend/`、配置或迁移文件。

## 当前状态

文档基线已建立；实现任务清单等待用户明确批准。未批准前不得开始数据库、API、路由、组件或部署改造。

## 文档

- [个人学习系统 V2 目标架构](../../architecture/personal-learning-system-v2.md)：本任务组的最高层设计依据
- [design.md](./design.md)：任务组设计、边界和流程结构
- [ui-design.md](./ui-design.md)：全局壳层、页面线框、交互状态与响应式规范
- [requirements.md](./requirements.md)：可验证需求与验收条件
- [tasks.md](./tasks.md)：分阶段任务清单与审批门
- [source-of-truth.md](./source-of-truth.md)：实体事实来源与迁移策略
- [owner-coverage-matrix.md](./owner-coverage-matrix.md)：私有实体 owner 覆盖矩阵
- [auth-boundary-design.md](./auth-boundary-design.md)：public/user/admin/worker 认证边界
- [schema-ownership.md](./schema-ownership.md)：Alembic 与 `create_all` 的 schema authority 决策
- [backup-validation-plan.md](./backup-validation-plan.md)：备份、恢复、附件与 Migration 018 验证计划
- [validation.md](./validation.md)：本阶段文档验证与禁止项记录

## 后续闭环

```text
现状审计
-> 任务清单批准
-> 基础安全与数据源收敛
-> 统一内容与知识模型
-> 今日工作台与采集
-> WikiLink 与知识关系
-> 错题复习闭环
-> AI 建议与发布快照
-> 数据迁移切换
-> 验收报告 / 剩余风险 / 下一轮需求
```
