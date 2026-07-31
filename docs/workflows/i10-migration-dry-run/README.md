# I10 迁移准备与隔离 dry-run

状态：`COMPLETE / DRY_RUN_READY PASS`。

## 目标

用户于 2026-07-31 批准解除 I10 owner gate，并确认单管理员
backfill 策略：全部 121 条 legacy 实体统一归属 canonical owner
`4c503215-b158-4162-b472-79df8289ed0a`。本轮只允许在由已验证备份恢复的
隔离数据库执行 owner mapping backfill、完整性审计和销毁；不得写日常库、
生产库，不得部署、推送或实际执行 E-05/E-06。

## 涉及领域

- 架构线：`backend/` shared infrastructure。
- 领域：auth、notes、mistakes、review、sync、manage 的迁移归属证据。
- 数据边界：现有业务表没有统一 `owner_id`；本轮在隔离库建立 sidecar
  owner mapping 表进行 dry-run，不把临时结构带入日常库。

## 当前状态

- 决策：PASS，单管理员策略与 canonical owner 已明确。
- 本轮隔离执行：121/121、owner FK orphan=0、关系 orphan=0、销毁均 PASS。
- 测试：前端、类型、构建、workflow 与 025 隔离后端均 PASS。
- 日常库保护：首次测试残留的两条记录已按用户精确授权删除，最终指纹恢复
  到执行前 123 条与原 aggregate。
- E-03：PASS。
- E-05/E-06：`READY / NOT AUTHORIZED`，本轮未执行。

## 工作流文件

[设计](./design.md) · [需求](./requirements.md) ·
[任务](./tasks.md) · [验证](./validation.md) · [审计](./audit.md) ·
[风险](./risk-register.md) · [下一步](./next-requirements.md) ·
[差异报告](./diff-report.md) · [Owner 覆盖](./owner-coverage.md)
