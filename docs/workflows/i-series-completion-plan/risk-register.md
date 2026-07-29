# I 系列完成风险登记

事实日期：2026-07-29
状态：`CLOSED FOR I-SERIES / RESIDUAL RISKS RETAINED`

| 风险编号 | 优先级 | 风险 | 当前证据 | 处置与退出门槛 |
|---|---|---|---|---|
| I-RISK-P0-01 | P0 | source schema `020` 与候选 runtime `EXPECTED_ALEMBIC_REVISION=024` mismatch | `psql`/Alembic current=`020`；代码 head=`024` | C3 固定 artifact，C4 备份恢复，C5 020→024 后 current=head/check 全 PASS |
| I-RISK-P0-02 | P0 | 021-024 与 I3-I10 modified/untracked runtime、contracts、tests 纠缠 | `git status --short` 与 import/reference 扫描见 `design.md` 2.4 | 同一个 hash manifest 冻结完整闭包；Phase 1.0 无关 dirty 切分；C5 前逐文件 hash相等 |
| I-RISK-P0-03 | P0 | 已部署前端可能经活 backend 连接 source DB | OpenNext 前端指向 public API tunnel；当前 localhost:8000 无监听，public health=502 | C5 窗口重查 process/version/expected revision/tunnel/DB sessions；发现活 backend 必须先停写，否则 BLOCKED |
| I-RISK-P0-04 | P0 | owner/backfill 错归属 | 12 类当前记录缺统一 owner | D1-D8 固化、121 行逐行 manifest、双独立 hash/count 复核 |
| I-RISK-P0-05 | P0 | 020→024 后的 024 恢复能力尚待实证 | C4 已证明 020 restore；C5 已生成 024 restore point | C7 将 C5 024 backup 恢复到全新隔离 DB，并验证 manifest/readiness/check 后清理 |
| I-RISK-P0-06 | P0 | legacy Note mistakes 与独立 mistakes 错误合并 | 5 与 3 精确 question/answer 匹配为 0 | 默认分别 MIGRATED；只有逐字段严格等价才 MERGED |
| I-RISK-P0-07 | P0 | C6-E-05 目标权威基础设施不存在 | 仅一个 `DATABASE_URL`/`blog_db`；系统规模为 121 manifest rows | `RESOLVED - C6-C9 改为简化验证，不实现 shadow target`：2026-07-29 批准单一 source 架构，以 C6 完整性审计和 C7 024 恢复验证取代 shadow/cutover |
| I-RISK-P0-08 | P0 | live source 已是 024，但产生该 schema 的 021-024 migration 曾为 Git-untracked | 2026-07-29 `git ls-files` 确认 021-024 已由 local commit `2c7adcc` 跟踪；single head/current/check PASS | `RESOLVED`：C3 83-file 闭包与 workflow 已精确提交；未 push/deploy |
| I-RISK-P0-09 | P0 | C1 verify 固定要求 source=020，无法在升级后的 live 024 原样复核 | 2026-07-29 已用显式 024→020 投影完成 live 只读复核：121/121、drift/conflict/orphan=0、aggregate 不变 | `RESOLVED`：manifest 保持 020 不变；unsupported revision pair fail closed；证据 `assets/c1-post-upgrade-verification.json` |
| I-RISK-P1-01 | P1 | shadow 增量扫描需要额外 tombstone/时间戳合同 | 多表无可靠统一 `updated_at` | `RESOLVED BY SCOPE DECISION`：不实现 shadow delta；C6 对唯一 source 做全量只读 PK/hash 审计 |
| I-RISK-P1-02 | P1 | 权威切换可能形成双主 | 当前 source 是唯一实际 DB | `RESOLVED BY SCOPE DECISION`：C8/C9 SKIPPED，不创建或切换第二权威 |
| I-RISK-P1-03 | P1 | 权限或失败态未完整验证 | 既有 F-01 为 PARTIAL | 真实隔离 admin，匿名/失效/非 admin，全失败矩阵，三尺寸/键盘与独立交叉验证 |
| I-RISK-P2-01 | P2 | 工作树仍有本范围外 dirty/untracked | migration/runtime authority 已由 `2c7adcc` 固定；Phase 1.0、其他 workflow/评审资产仍未提交 | 本次不混入无关用户改动；F-02 继续把全工作树与测试状态作为生产资格限制 |
| I-RISK-P2-02 | P2 | 测试与浏览器存在非阻塞 warnings | frontend AI-runs `act()`、backend AI gateway AsyncMock、avatar LCP 建议；最终 suites/build 均 PASS | 下一轮 test/performance hygiene；实际部署前重新评估 warning baseline |
| I-RISK-P1-04 | P1 | production backend runtime 未启用 | public tunnel 无 localhost:8000 listener；本轮禁止部署 | 实际部署前单独授权并完成 exact-commit config/secret/health/rollback gates |
| I-RISK-P1-05 | P1 | 真实 AI/OCR provider 成功路径未验证 | C10 使用空 provider keys；governed adapters/failure tests PASS | provider integration 作为未来独立验收，不影响本次治理范围完成状态 |

任何 P0/P1 门槛出现 UNKNOWN/FAIL 都不得由“数据不重要”豁免。失败必须进入 `validation.md`，同一失败无新证据重复两次则停止该增量并诊断。
