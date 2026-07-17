# Dependency And Runtime Risk Cleanup

## 目标

清理当前公网前端已确认的依赖漏洞、Next.js/OpenNext 版本契约不匹配，以及部署构建警告，并用隔离构建和公网回归证据确认风险收敛。

## 影响架构线

- 主要影响：`src/` Next.js 前端与 Cloudflare OpenNext 部署链路。
- 次要影响：前端构建依赖审计。
- 不影响：`backend/` 业务代码、数据库 schema、Alembic、现有数据。

## 当前状态

依赖清理、本地回归和公网发布已完成；下一轮方案演进已登记，尚未开始实现。当前未执行数据库修改。

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
