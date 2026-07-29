# I 系列完成风险登记

事实日期：2026-07-28
状态：`ACTIVE`

| 风险编号 | 优先级 | 风险 | 当前证据 | 处置与退出门槛 |
|---|---|---|---|---|
| I-RISK-P0-01 | P0 | source schema `020` 与候选 runtime `EXPECTED_ALEMBIC_REVISION=024` mismatch | `psql`/Alembic current=`020`；代码 head=`024` | C3 固定 artifact，C4 备份恢复，C5 020→024 后 current=head/check 全 PASS |
| I-RISK-P0-02 | P0 | 021-024 与 I3-I10 modified/untracked runtime、contracts、tests 纠缠 | `git status --short` 与 import/reference 扫描见 `design.md` 2.4 | 同一个 hash manifest 冻结完整闭包；Phase 1.0 无关 dirty 切分；C5 前逐文件 hash相等 |
| I-RISK-P0-03 | P0 | 已部署前端可能经活 backend 连接 source DB | OpenNext 前端指向 public API tunnel；当前 localhost:8000 无监听，public health=502 | C5 窗口重查 process/version/expected revision/tunnel/DB sessions；发现活 backend 必须先停写，否则 BLOCKED |
| I-RISK-P0-04 | P0 | owner/backfill 错归属 | 12 类当前记录缺统一 owner | D1-D8 固化、121 行逐行 manifest、双独立 hash/count 复核 |
| I-RISK-P0-05 | P0 | 020→024 或切换后恢复失败 | 历史只证明 020 restore；021/022 有数据时拒绝 downgrade | C4 新鲜 020 restore rehearsal；C5 024 restore point；C7/C10 restore/reverse delta/回切 |
| I-RISK-P0-06 | P0 | legacy Note mistakes 与独立 mistakes 错误合并 | 5 与 3 精确 question/answer 匹配为 0 | 默认分别 MIGRATED；只有逐字段严格等价才 MERGED |
| I-RISK-P0-07 | P0 | C6-E-05 目标权威基础设施不存在 | 仅一个 `DATABASE_URL`/`blog_db`；无 shadow/quarantine/archive/tombstone/identity-map tables，无 upsert/delta/cutover tool | 需独立新增 target schema、迁移执行器、delta/tombstone 和 authority switch contract；在显式范围批准前 C6-C12 BLOCKED |
| I-RISK-P0-08 | P0 | live source 已是 024，但产生该 schema 的 021-024 migration 仍 Git-untracked | C3 只冻结仓库外 bundle；clean checkout 会丢迁移链 | C3 83-file 闭包与本 workflow 进入精确 local commit；校验 migration staged/tracked、single head/current/check；不 push/deploy |
| I-RISK-P0-09 | P0 | C1 verify 固定要求 source=020，无法在升级后的 live 024 原样复核 | 2026-07-29 已用显式 024→020 投影完成 live 只读复核：121/121、drift/conflict/orphan=0、aggregate 不变 | `RESOLVED`：manifest 保持 020 不变；unsupported revision pair fail closed；证据 `assets/c1-post-upgrade-verification.json` |
| I-RISK-P1-01 | P1 | 增量扫描漏 delete 或无时间戳变更 | 多表无可靠统一 `updated_at` | 小数据全量 PK/hash 三周期，显式 tombstone，zero unknown drift |
| I-RISK-P1-02 | P1 | 权威切换形成双主 | 当前 source 是唯一实际 DB | 隔离演练、final zero drift、读切/写切分离、旧写显式只读、回切验证 |
| I-RISK-P1-03 | P1 | 权限或失败态未完整验证 | 既有 F-01 为 PARTIAL | 真实隔离 admin，匿名/失效/非 admin，全失败矩阵，三尺寸/键盘与独立交叉验证 |
| I-RISK-P2-01 | P2 | 工作树 dirty/untracked 使证据不可复现 | 当前大量 I-series 与 Phase 1.0 变更并存 | 候选 bundle/hash 而非提交；F-02 明确 dirty tree 对生产资格的影响 |

任何 P0/P1 门槛出现 UNKNOWN/FAIL 都不得由“数据不重要”豁免。失败必须进入 `validation.md`，同一失败无新证据重复两次则停止该增量并诊断。
