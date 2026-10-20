# I 系列剩余任务完成规划

状态：`C0-C12 REVISION-024 HISTORICAL BASELINE / E-06 PASS / F-01 PASS /
F-02 TECHNICALLY ELIGIBLE BUT CURRENT DIRTY WORKTREE DO NOT DEPLOY /
F-03 COMPLETE / I12-04 PASS / NOT DEPLOYED`

2026-07-31 状态补充：新的 I10 owner backfill dry-run 再次通过 121/121、owner
FK/关系完整性和隔离销毁。原简化路径中的 E-05/E-06 `SKIPPED` 是 2026-07-29
历史决策；当前 E-05 已在一次性隔离 shadow 中执行并 `PASS`。2026-08-01
用户已正式批准 E-06；因此原 C10-C12/F-01～F-03 仅保留为 revision-024 历史
基线。2026-08-01 已在 revision 025 最终 authority 上完成 I11-04、F-01 和
F-02 刷新，F-03 正在统一终态。

## 目标

为 Personal Learning System V2 Unification 的 I10 收尾、I11 与 I12 提供可回滚、可验收的连续执行与最终收口。C0-C5 已完成；用户于 2026-07-29 批准以最终只读完整性审计和 024 灾难恢复演练替代原 C6-C9 影子迁移/切换路径。范围明确不包含 push、生产部署或生产配置修改。

## 涉及领域与架构线

- 后端线 `backend/`：shared infrastructure、notes、mistakes、review、auth、sync、manage；重点是 Alembic/PostgreSQL、owner/backfill、只读完整性、权限与恢复。
- 前端线 `src/`：只规划 I12 的公开读取、管理员会话、失败态与三尺寸浏览器验收；不把前端 `AuthGate` 当成后端安全边界。
- 当前模型边界：公开/legacy 错题仍由 `Note(type="mistake")` 路径服务；同一源库又有独立 `mistakes` 表。2026-07-28 只读计数为 `notes=13`，其中 `type=mistake` 为 5；独立 `mistakes=3`，两组按 question/answer 精确匹配为 0。两套错题数据并存是迁移决策对象，不能假设其中一套不存在或已自动合并。

## 当前结论

1. 历史 source `localhost:5432/blog_db` 已由 020→024→025；最终 runtime
   authority 为 `blog_v2` revision 025，Legacy `blog_db` revision 025 默认只读。
   021-024 与 C3 闭包已由本地 commit `2c7adcc` 跟踪，025 为当前单 head。
2. C0/C1 已 PASS：canonical target owner 为 `4c503215-b158-4162-b472-79df8289ed0a`；121 行 mapping manifest 覆盖 12 类，独立复核 missing/duplicate/hash drift/owner conflict/orphan 均为 0，`DRY_RUN_READY=PASS`。升级后的 live 024 又通过显式 024→020 旧字段投影复核，aggregate 保持 `b40b109a...89adb6`。
3. 2026-07-29 的 C8/C9 `SKIPPED` 是历史简化决策；2026-08-01 E-06 的新明确
   授权有限反转该决策，并已完成 target、切换/观察、reverse delta、回切、最终
   重切和 Legacy 只读归档。
4. E-06/I11-04/F-01 均 PASS：清理后 123/123、零 delta、独立全行 hash、owner、
   关系与附件一致；frontend=64/64、backend=307/307、type/build/compile/Alembic、
   权限和三尺寸浏览器全部有证据。
5. F-02 的技术/recovery candidate 具备未来单独授权部署资格；当前 dirty
   worktree 被 clean-artifact 门禁阻断。F-03 十维报告已刷新；本轮未 push、未
   应用部署、未改 Cloudflare 配置。

## 文件

- [设计与现状证据](./design.md)
- [需求与验收门槛](./requirements.md)
- [执行任务](./tasks.md)
- [风险登记](./risk-register.md)
- [执行验证](./validation.md)

## 授权边界

2026-07-29 用户已明确批准 [tasks.md](./tasks.md) 的 C6-C12 简化路径。count/hash、owner、single head、`alembic check`、恢复、权限与 source 只读边界仍是不可弱化的技术关口。F-02 仅做资格审查；无论结论如何均不 push、不部署、不改生产配置。
