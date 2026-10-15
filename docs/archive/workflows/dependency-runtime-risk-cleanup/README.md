# Dependency And Runtime Risk Cleanup

## 目标

清理当前公网前端已确认的依赖漏洞、Next.js/OpenNext 版本契约不匹配，以及部署构建警告，并用隔离构建和公网回归证据确认风险收敛。

## 影响架构线

- 主要影响：`src/` Next.js 前端与 Cloudflare OpenNext 部署链路。
- 次要影响：前端构建依赖审计。
- 不影响：`backend/` 业务代码、数据库 schema、Alembic、现有数据。

## 当前状态

2026-07-29 第二轮依赖修复已默认批准并开始。此前阶段已完成；
本轮由 Git 公网发布门禁新发现的 10 个 high 风险触发，目标是在不降级
OpenNext、不使用 `npm audit fix --force` 的前提下恢复 fail-closed 发布资格。
当前未执行数据库修改。

本轮基线：

- `next@16.2.10`
- `@opennextjs/cloudflare@1.20.1`
- `npm audit --omit=dev`: 10 high、0 critical
- 最新稳定候选：Next `16.2.12`、OpenNext Cloudflare `1.20.2`
- 明确拒绝 npm 建议的 OpenNext `0.2.1` 大版本降级

## 当前基线

- `next`: `16.0.10`
- `@opennextjs/cloudflare`: `1.20.1`
- `npm audit`: 2 high、3 moderate
- `npm audit --omit=dev`: 2 high、2 moderate
- `wrangler.toml` compatibility date：`2025-03-25`
- 当前公网版本仍可访问，但依赖安全风险未关闭。

## 工作流文件

- [requirements.md](requirements.md)
- [design.md](design.md)
- [tasks.md](tasks.md)
- [risks.md](risks.md)
- [next-requirements.md](next-requirements.md)

## 硬边界

- 不执行 `npm audit fix --force`。
- 不修改数据库 schema，不创建 migration，不迁移或删除数据。
- 不实现 AI/OCR/Capture/Search/Analytics/Practice/BKT。
- 不在未通过验证和审批前重新部署公网。
