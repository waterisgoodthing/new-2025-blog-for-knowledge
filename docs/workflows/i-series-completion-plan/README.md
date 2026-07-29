# I 系列剩余任务完成规划

状态：`C0-C12 COMPLETE VIA SIMPLIFIED PATH / ELIGIBLE / NOT DEPLOYED`

## 目标

为 Personal Learning System V2 Unification 的 I10 收尾、I11 与 I12 提供可回滚、可验收的连续执行与最终收口。C0-C5 已完成；用户于 2026-07-29 批准以最终只读完整性审计和 024 灾难恢复演练替代原 C6-C9 影子迁移/切换路径。范围明确不包含 push、生产部署或生产配置修改。

## 涉及领域与架构线

- 后端线 `backend/`：shared infrastructure、notes、mistakes、review、auth、sync、manage；重点是 Alembic/PostgreSQL、owner/backfill、只读完整性、权限与恢复。
- 前端线 `src/`：只规划 I12 的公开读取、管理员会话、失败态与三尺寸浏览器验收；不把前端 `AuthGate` 当成后端安全边界。
- 当前模型边界：公开/legacy 错题仍由 `Note(type="mistake")` 路径服务；同一源库又有独立 `mistakes` 表。2026-07-28 只读计数为 `notes=13`，其中 `type=mistake` 为 5；独立 `mistakes=3`，两组按 question/answer 精确匹配为 0。两套错题数据并存是迁移决策对象，不能假设其中一套不存在或已自动合并。

## 当前结论

1. 源库 `localhost:5432/blog_db` 已在 C5 从 `020` 升至 `024`，工作树代码单 head/readiness 同为 `024`；产生该 schema 的 021、022、023、024 与 C3 83-file 闭包已进入本地 commit `2c7adcc`，clean checkout 丢失 migration 的 P0 风险已解除。
2. C0/C1 已 PASS：canonical target owner 为 `4c503215-b158-4162-b472-79df8289ed0a`；121 行 mapping manifest 覆盖 12 类，独立复核 missing/duplicate/hash drift/owner conflict/orphan 均为 0，`DRY_RUN_READY=PASS`。升级后的 live 024 又通过显式 024→020 旧字段投影复核，aggregate 保持 `b40b109a...89adb6`。
3. 2026-07-29 的简化决策明确 source `blog_db` 024 为唯一权威；不创建 shadow target，不执行权威切换或 Legacy 归档。C8/C9 将以该架构决策标记为 `SKIPPED`。
4. C6 integrity、C7 024 restore、C10 F-01 均 PASS；C8/C9 按单一 source 决策 SKIPPED。frontend=58/58、backend=300/300、type/build/compile/Alembic/browser/cross verification 全部有证据。
5. F-02 结论为 `ELIGIBLE (NOT DEPLOYED; PRODUCTION RUNTIME ENABLEMENT REQUIRED)`；F-03 已完成十维报告。当前无 production 8000 listener，本轮未 push/部署/改生产配置。

## 文件

- [设计与现状证据](./design.md)
- [需求与验收门槛](./requirements.md)
- [执行任务](./tasks.md)
- [风险登记](./risk-register.md)
- [执行验证](./validation.md)

## 授权边界

2026-07-29 用户已明确批准 [tasks.md](./tasks.md) 的 C6-C12 简化路径。count/hash、owner、single head、`alembic check`、恢复、权限与 source 只读边界仍是不可弱化的技术关口。F-02 仅做资格审查；无论结论如何均不 push、不部署、不改生产配置。
