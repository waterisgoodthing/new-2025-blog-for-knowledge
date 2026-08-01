# I11 需求与验收

## I11-R1 执行授权与架构反转

- 输入：2026-07-29 单 source 简化决策、2026-07-31 E-05 新任务清单。
- 处理：明确批准是否恢复 shadow target 路径。
- 输出：E-05 执行授权记录。
- 失败：含糊的“继续”不自动授权 E-06 或生产切换。
- 验收：批准明确指向 I11-02A 至 I11-02H。

## I11-R2 Source 只读与 Shadow 隔离

- 输入：日常 source、全新 `i11_shadow_` target 名称。
- 处理：source 只读 dump/scan；所有 DDL/DML 只作用于 shadow。
- 输出：source 前后 fingerprint、target identity 与清理证据。
- 失败：目标名或连接身份不符立即停止。
- 验收：source revision/count/aggregate 前后不变；target catalog 最终为 0。

## I11-R3 全量与 Owner/Delta Manifest

- 输入：immutable v1 121 rows、当前 source 增量。
- 处理：保留 v1，生成独立 delta manifest；建立 shadow ledger。
- 输出：全量 source PK 恰好一个 owner/disposition/rollback mapping。
- 失败：missing、duplicate、owner conflict、hash drift 或 unknown disposition。
- 验收：source=current manifest coverage；canonical owner count=1；所有差异有原因。

## I11-R4 增量与 Tombstone 合同

- 输入：scan A、scan B。
- 处理：分类 unchanged/inserted/updated/deleted，幂等重放 insert/update；
  delete 生成 tombstone 并 fail closed。
- 输出：delta report 与 replay report。
- 失败：重放产生重复、业务关系破坏或自动删除 source/shadow 业务数据。
- 验收：第二次重放为 no-op；tombstone 数量明确；未解释 drift=0。

## I11-R5 完整性、恢复与退出

- 输入：shadow business schema、ledger、delta/tombstone report。
- 处理：主验证与独立 SQL/进程复核；清理 sidecar 与 target。
- 输出：validation/audit/risk/next-requirements。
- 失败：任何 UNKNOWN 或非零 orphan 阻断 E-05 PASS。
- 验收：current=head=025、基础 schema check clean、关系 orphan=0、
  target 已删除、source 未写。

## 边界

- 允许：E-05 工具；2026-08-01 E-06 所需的新鲜备份、隔离恢复、精确 source
  停写、cutover target、runtime authority 值切换、观察、reverse delta、回切和
  旧 source 只读归档。
- 禁止：应用部署、Git push、Cloudflare/公网流量修改、广泛删除、产品重构、
  immutable v1 manifest 改写、凭据或私人内容入库。

## I11-R6 E-06 备份与恢复门槛

- DB custom dump 与附件快照必须新鲜、仓库外、SHA-256 可复核。
- DB 必须通过 `pg_restore --list` 并恢复到全新隔离库；附件恢复须逐文件 hash。
- 隔离恢复必须与 source 的 revision/count/PK/hash/owner/关系一致，完成后清理。

## I11-R7 停写、切换与观察

- 切换前确认没有 backend listener、没有其他 source session，并将 source 默认
  事务设为只读。
- authority 只通过精确 `.env` 数据库/附件值切换；凭据不输出、不写 workflow。
- 观察使用 loopback backend、真实密码管理员、`AUTH_BYPASS=false`；公开页面
  保持公开，管理写接口继续由 `get_current_admin` 保护。

## I11-R8 Delta、Reverse Delta 与回切

- source->target 和 target->source 均比较 12 类记录的 count、PK、规范 hash、
  owner 与七类关系。
- replay 必须幂等；预期零 delta。任何非零 delta/unknown schema 均停止自动写入。
- 回切必须恢复 source 写能力、将 target 停写并通过相同观察矩阵。

## I11-R9 最终权威与只读归档

- 最终 target revision=head=025，runtime authority 指向 target。
- 旧 source 保留、默认只读、可连接恢复，不得删除或覆盖。
- 最终报告必须分别声明 DB authority、附件 authority、应用部署与公网流量状态。

## I11-R10 交叉验证

- 主验证后使用不同 Python 进程或独立 SQL 重新采集连接身份、revision、count、
  PK/hash、owner、关系、默认只读与数据库 catalog。
- 交叉验证不得读取主报告后原样回写结论；任一差异阻断 I11-04。
