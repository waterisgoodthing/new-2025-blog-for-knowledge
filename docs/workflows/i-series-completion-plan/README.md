# I 系列剩余任务完成规划

状态：`EXECUTION AUTHORIZED / C0-C12 IN PROGRESS`

## 目标

为 Personal Learning System V2 Unification 的 I10 收尾、I11 与 I12 提供可回滚、可验收的连续执行与最终收口。用户于 2026-07-28 明确批准 C0-C12，包括源库 020→024、影子迁移、实际权威切换、停旧写与 Legacy 只读归档；技术 fail-closed 门槛仍逐项生效。范围明确不包含 push、生产部署或生产配置修改。

## 涉及领域与架构线

- 后端线 `backend/`：shared infrastructure、notes、mistakes、review、auth、sync、manage；重点是 Alembic/PostgreSQL、owner/backfill、影子迁移、权限与恢复。
- 前端线 `src/`：只规划 I12 的公开读取、管理员会话、失败态与三尺寸浏览器验收；不把前端 `AuthGate` 当成后端安全边界。
- 当前模型边界：公开/legacy 错题仍由 `Note(type="mistake")` 路径服务；同一源库又有独立 `mistakes` 表。2026-07-28 只读计数为 `notes=13`，其中 `type=mistake` 为 5；独立 `mistakes=3`，两组按 question/answer 精确匹配为 0。两套错题数据并存是迁移决策对象，不能假设其中一套不存在或已自动合并。

## 当前结论

1. 源库 `localhost:5432/blog_db` 已在 C5 从 `020` 升至 `024`，工作树代码单 head/readiness 同为 `024`；但产生该 schema 的 021、022、023、024 四个 migration 在 2026-07-29 提交前仍为 Git untracked，因此 clean checkout 可复现性是当前 P0 收口项。
2. C0/C1 已 PASS：canonical target owner 为 `4c503215-b158-4162-b472-79df8289ed0a`；121 行 mapping manifest 覆盖 12 类，独立复核 missing/duplicate/hash drift/owner conflict/orphan 均为 0，`DRY_RUN_READY=PASS`。升级后的 live 024 又通过显式 024→020 旧字段投影复核，aggregate 保持 `b40b109a...89adb6`。
3. 用户已授权 C0-C12 连续执行；I11-02、I11-03、I11-04 仍须按技术 gate 顺序完成，不因授权而提前升级状态。
4. I12-01 为 PARTIAL；管理员真实会话、024 恢复、权威切换回滚和完整失败态未验证。I12-02、I12-03 未完成，I12-04 仅有局部交叉证据。
5. C4 的新鲜 020 备份与 C5 的 024 恢复点均保存在仓库外并通过 hash/restore 前置验证；C7/C10 尚未完成 024 故障恢复、reverse delta 和权威回切，因此不能直接覆盖 I11/I12。

## 文件

- [设计与现状证据](./design.md)
- [需求与验收门槛](./requirements.md)
- [执行任务](./tasks.md)
- [风险登记](./risk-register.md)
- [执行验证](./validation.md)

## 授权边界

本次用户授权覆盖 [tasks.md](./tasks.md) 的 C0-C12 连续执行，不再把增量间人工批准作为关口。count/hash、owner、single head、`alembic check`、恢复/回切、权限与生产只读核查仍是不可弱化的技术关口。F-02 仅做资格审查；无论结论如何均不 push、不部署、不改生产配置。
