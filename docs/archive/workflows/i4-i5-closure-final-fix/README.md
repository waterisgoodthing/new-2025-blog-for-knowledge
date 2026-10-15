# I4-I5 closure-final-fix

## 目标

完成 closure-fix-2 的最终收口：修复后端 asyncpg/事件循环隔离，固化 learning、activity、storage 三类独立故障回归，移除全局禁用用户缩放的 viewport 参数，并在真实 Alembic `022` 隔离目标上重跑后端组合套件、前端测试、构建和移动端验收，同步 closure-fix-2 文档。

## 影响架构线与边界

- Personal learning backend：测试生命周期、Dashboard 服务测试、profile/attempt 测试环境。
- 管理工作区前端：HTML viewport 元数据和移动端验收。
- 文档：本工作区与 `docs/workflows/i4-i5-closure-fix-2/` 的状态、数量、证据同步。
- 不包含：生产部署、推送、源库权威切换、真实 AI 调用、业务 schema 设计变更。

## 当前状态

`COMPLETE / PASS / FINAL-FIX-VERIFIED (2026-07-24)`。已使用既有 `127.0.0.1:55435/pls_v2_i4_target` 隔离目标只读验证 Alembic `022`，未执行迁移；默认 `blog_db` 的 020 仅保留为历史运行时说明。现有脏工作树和其他 workflow 改动均保留，未回滚。

## 文件

- [audit.md](./audit.md)
- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
