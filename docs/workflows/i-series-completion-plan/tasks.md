# I 系列剩余任务执行清单

状态：`C0-C12 AUTHORIZED / IN PROGRESS`
规则：用户于 2026-07-28 明确授权连续执行全部增量。完成一项后立即勾选并记录验证，再直接进入下一项；技术 fail-closed 门槛、生产只读核查和不部署边界保持不变。

## 分阶段序列与技术关口

| 增量 | 唯一目标 | 前置 | 授权状态 | 验收证据 | 硬停止点 |
|---|---|---|---|---|---|
| C0 | 生效 owner/backfill 决策 D1–D8 | 本规划只读证据 | 2026-07-28 已授权默认决策；不涉及 DB 写入 | canonical owner、12 类规则、冲突/回滚政策 | 任一决策 UNKNOWN |
| C1 | 生成并独立复核逐行 mapping manifest，只读重判 Migration Gate | C0 PASS | 单独批准 C1 文档/只读审计任务 | 121 行全覆盖、hash、五类终态、双重复核、`DRY_RUN_READY=PASS` | missing/duplicate/owner conflict > 0 或任一 gate 非 PASS |
| C2 | 以获批 manifest 重跑最新隔离 dry-run | C1 PASS；`DRY_RUN_READY=PASS`；新鲜 source snapshot | **G2**：仅授权隔离 target 写入 | 020→024 clone、count/hash/关系/rollback/destroy；gate 持续 PASS | 任一 gate 退化；不得写 source |
| C3 | 冻结 021–024 upgrade artifact 与执行/回滚包 | C2 PASS | 单独批准 C3 只读/文档审查 | migration hash、SQL/锁/extension、维护/回滚 runbook | migration 仍 untracked/漂移或 rollback 不可验证 |
| C4 | 生成新鲜 020 备份并在隔离环境恢复/升级验收 | C3 PASS | 单独批准备份与隔离写入；不等于 source upgrade | DB+附件 hash、020 restore、clone 024 readiness | 备份不新鲜/不可读、restore/upgrade fail |
| C5 | 将源库从 020 升级到 024 | C4 PASS；维护窗口/停写 | **额外明确源库写入授权**；G2/G3 均不自动授权 | source 024、check、hash/关系、read/API smoke、024 恢复点 | 不能停写、任何 drift/权限/恢复失败 |
| C6 | 执行 E-05 shadow migration 与增量对账 | C5 PASS；owner manifest PASS | **G3：重新单独批准 E-05** | 隔离 target 全量+增量 count/hash、tombstone、至少 3 周期/24h、零未知 drift | target 服务流量、source 被写、任何未知 drift |
| C7 | 仅做 E-06 切换与回滚演练 | C6 PASS | G3 下新的“切换演练”批准 | 隔离 read/write switch、reverse delta、恢复/回切 | 回滚/权限/数据一致性任一不可证 |
| C8 | 实际权威切换并观察 | C7 PASS；新鲜 024 恢复点 | **G3：再次明确批准实际读写切换** | final zero drift、读/写 smoke、观察期指标 | 双主、回切失败、阈值超限 |
| C9 | 旧写停用与 Legacy 只读归档 | C8 观察期 PASS | **G3：再次明确批准停旧写/归档** | 只读证明、archive hash/runbook/route alias | 删除请求、archive 不可恢复、仍有旧写 |
| C10 | 完成 F-01 最终验证 | C9 PASS | 单独批准 I12-01 | 管理员/匿名/失效、024 恢复、失败矩阵、三尺寸、代码质量、交叉验证 | 任一 FAIL/UNKNOWN |
| C11 | F-02 部署资格审查（不部署） | C10 PASS | **G4** | fail-closed checklist、ELIGIBLE 或 DO NOT DEPLOY | 任一门槛非 PASS；不得部署 |
| C12 | F-03 最终报告与状态同步 | C11 有明确结论 | 单独批准报告/旧 workflow 同步 | 10 个状态维度及证据、残余风险、审批历史 | 任何维度被无证据升级；不得发布 |

## 待执行任务

- [x] C0：D1-D8 已按 2026-07-28 授权生效；canonical source/target owner=`4c503215-b158-4162-b472-79df8289ed0a`，其余决策与证据见 `design.md` 3.2、`validation.md` C0。
- [x] C1：已生成 121 行 `owner-mapping-manifest-v1.json`；独立 UNION 查询复核 missing/duplicate/hash/owner/orphan 全为 0，`DRY_RUN_READY=PASS`，见 `validation.md` C1。
- [x] C2：隔离 clone 已完成带 manifest 的 `020→024→020→024`、三次逐行 hash/count 验证、关系/回填/check 验证并销毁；gate 持续 PASS，见 `validation.md` C2。
- [x] C3：已在仓库外冻结 Git base + 83 个纠缠文件 + patch/bundle/hash/SQL/manifest，并完成锁、extension、数据影响与 restore-first 回滚 runbook 审查，见 `assets/c3-artifact-review.md`。
- [x] C4：已生成新鲜 020 DB+附件备份，恢复至隔离 DB 并完成 020→024/readiness 验证；备份保留、restore target 销毁，见 `validation.md` C4。
- [x] C5：在 production-backend/source DB 只读核查 PASS 且停写窗口确认后，source `blog_db:5432` 已实际 `020→024`；current=head/check、旧字段 hash/关系/backfill/readiness/API smoke 均 PASS，024 恢复点已生成，见 `validation.md` C5。
- [ ] C6：`BLOCKED`。C5 后只读审计确认没有 target schema、owner/quarantine/tombstone/identity-map ledger、source→target upsert/delta 工具或 authority switch config；仅 clone 024 DB 不满足 E-05。见 `validation.md` C6。
- [ ] C7：单独批准并完成 E-06 隔离切换、reverse delta、恢复与回切演练。
- [ ] C8：再次批准实际读/写权威切换；执行 final delta、分步切换与观察期，任何异常 fail closed。
- [ ] C9：观察期 PASS 后再次批准旧写停用与 Legacy 只读归档；保留可恢复快照，不删除。
- [ ] C10：批准并完成 I12-01/F-01 管理员、恢复、权限、完整失败态、浏览器、质量与独立交叉验证。
- [ ] C11：`BLOCKED`，但已提前形成 fail-closed `NOT ELIGIBLE / DO NOT DEPLOY` 结论；完整 F-02 仍等待 C6-C10，见 `f02-deployment-eligibility.md`。
- [ ] C12：`BLOCKED`；已发布 `f03-final-status-report.md`，明确为 NOT COMPLETE 而非最终完成报告，等待 C6-C11 实证。

## C0-C5 Git 权威收口（2026-07-29 已授权）

- [x] GIT-C0：复核 `git status --short`、C3 83-file 清单与无关 dirty 边界；确认 021-024 为 untracked，live source revision=024。
- [x] GIT-C1：先增加失败测试，覆盖 024 row 投影为 020 contract 及 unsupported revision pair fail closed；RED 为缺少接口的 ImportError，随后 4/4 PASS。
- [x] GIT-C2：实现 revision-aware verifier；manifest 本体不变，只支持 020→020 与 database 024→manifest 020。
- [x] GIT-C3：对 live 024 只读执行 C1 投影复核；121/121、全部 drift/conflict/orphan=0、aggregate 保持 `b40b109a...89adb6`，证据为 `assets/c1-post-upgrade-verification.json`。
- [x] GIT-C4：manifest 4/4、隔离 024 backend 35/35、compile/tsc/build/Alembic/Git whitespace PASS；frontend Vitest 57/58，唯一失败为既有 Capture App Router fixture，故不升级生产资格。
- [x] GIT-C5：仅暂存 C3 83-file 闭包和 `i-series-completion-plan` 共 99 files；expected/actual 集合差=0，四个 migration 均为 `A`，cached whitespace check PASS，无无关 dirty/secret/backup 混入。
- [x] GIT-C6：已创建本地 artifact commit `2c7adcc`；四个 migration 由 `git ls-files` 确认为 tracked。未 push/部署/改生产配置；剩余 dirty 均在本次白名单外。

## 当前授权记录

2026-07-28 用户已批准 C0-C12 连续执行及 D1-D8 默认决策。该授权不包含 push、生产部署或生产配置修改，也不覆盖任何技术 gate 的豁免。
