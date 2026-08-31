# I11 设计

## 当前事实与决策

- Final authority：`localhost:5432/blog_v2` revision 025、默认可写；Legacy
  `blog_db` revision 025、默认只读；当前代码 head 025。
- I10 immutable snapshot：121 rows；当前 source 为 123 rows，新增 2 个 user
  是 snapshot 之后的合法增量，不得改写 v1 manifest。
- Canonical owner：
  `4c503215-b158-4162-b472-79df8289ed0a`。
- 2026-07-29 简化路径决定不实现 shadow target；执行 E-05 前必须由新版任务
  批准明确反转该决定。
- 当前代码只有一个 `DATABASE_URL`，没有 shadow runtime、ledger、delta、
  tombstone、cutover 或 reverse-sync contract。

## E-05 目标

创建一个绝不服务正式流量的一次性 PostgreSQL shadow target，证明：

1. 从 source 只读快照恢复 024 并升级到当前 head 025。
2. v1 121-row manifest 保持不可变；生成独立 delta manifest 覆盖当前新增行。
3. shadow ledger 对 source 全量记录建立
   `(source_table, source_id, source_hash, owner_id, disposition)` 唯一映射。
4. 第二次 source 只读扫描可产生 insert/update/delete delta；insert/update
   幂等，delete 只生成 tombstone 并 fail closed，不静默丢失。
5. source、shadow business rows、ledger 与 manifest/delta 在 count、PK、hash、
   owner、关系上零未解释 drift。
6. shadow target、临时 dump 和凭据完成可恢复清理。

## 数据流

```text
source 024 (BEGIN READ ONLY)
  -> fresh custom dump + scan A
  -> isolated shadow restore
  -> shadow-only upgrade 024 -> 025
  -> i11_shadow.migration_ledger / tombstones
  -> full reconcile
  -> source scan B (READ ONLY)
  -> delta classify: inserted / updated / deleted / unchanged
  -> idempotent replay on shadow
  -> independent reconcile
  -> drop shadow target
```

## Shadow Sidecar Contract

`i11_shadow.migration_ledger`：

- `source_table text`
- `source_id text`
- `source_revision text`
- `source_row_hash text`
- `owner_id uuid REFERENCES public.users(id)`
- `disposition text`
- `manifest_version text`
- `applied_at timestamptz`
- 主键：`(source_table, source_id)`

`i11_shadow.tombstones`：

- `source_table text`
- `source_id text`
- `last_source_row_hash text`
- `detected_at timestamptz`
- `reason text`
- 主键：`(source_table, source_id)`

Sidecar 仅属于 shadow target，不加入正式 Alembic schema。对账完成后先采集证据，
再删除 sidecar 并要求基础 schema `alembic check` clean。

## 增量规则

- v1 manifest 的 121 行不可重生成或修改。
- 新增 source row 进入 delta manifest；单管理员规则仍映射 canonical owner。
- 非 canonical user 的 disposition 为 `ARCHIVED`，不迁移 password hash。
- 相同 PK、相同 hash：`UNCHANGED`。
- 相同 PK、不同 hash：`UPDATED`，必须保留 before/after hash。
- scan A 存在、scan B 缺失：`TOMBSTONED`，本轮不得自动删除 shadow 业务行。
- 任一 unknown table、重复 PK、owner conflict、orphan 或 unsupported schema
  立即停止。

## E-06 Cutover Contract（2026-08-01 已授权）

E-06 将新鲜 source 快照恢复到稳定 cutover target，并只在本机精确运行配置中
切换数据库权威。当前没有 backend listener，因此停写门槛由“无 backend 进程、
无其他 DB session、source database 默认只读”共同证明。应用部署、Git push、
Cloudflare 或其他生产流量配置不在本轮范围。

执行序列：

1. 对 source database 与附件根目录生成仓库外新鲜备份，校验 SHA-256、
   `pg_restore --list`、逐文件 hash，并恢复到全新隔离数据库/附件目录。
2. 锁定 source revision/count/PK/hash/owner/关系和连接身份，设置 source 默认
   只读后复核没有写连接。
3. 从同一备份构建 revision 025 cutover target；应用 runtime `.env` 只改
   `DATABASE_URL`/`UPLOAD_ROOT` 的精确 authority 值，凭据不进入仓库。
4. 启动 loopback backend 观察公开读取与真实密码管理员权限；禁止
   `AUTH_BYPASS`。
5. source->target delta 与第二次幂等 replay 必须为零未解释差异。
6. 将 target 设为默认只读，验证 target->source reverse delta 后恢复 source
   写权限并回切；再次观察。
7. 最终将 source 停写、重切 target，确认零 delta 后保持 source 默认只读作为
   Legacy archive。旧库不删除；附件旧根保留只读语义，备份保留在仓库外。

因为观察窗口内不制造业务数据，reverse delta 预期为空；空 reverse delta 仍须
用独立 PK/hash 比较证明，不得仅凭“没有操作”推断。若出现任何业务 delta，必须
停止、保留双端只读并记录唯一差异，不能自动覆盖。

## 安全与回滚

- 每个写命令必须显式使用 `i11_shadow_` 前缀目标；工具拒绝 `blog_db`。
- Source 查询必须包装在 `BEGIN READ ONLY`；不得依赖测试默认 `DATABASE_URL`。
- Shadow target 不配置到应用、Cloudflare、systemd、Docker 或正式环境变量。
- 回滚等于终止 shadow 会话并删除精确目标；source 无需数据回滚。
- E-05 PASS 只证明影子复制/对账能力；E-06 已由 2026-08-01 用户指令单独授权。
- E-06 回切通过恢复 `.env` authority、解除 source 默认只读并重新验证 source；
  任一备份、身份、hash、权限或连接门槛失败时保持两端只读。
