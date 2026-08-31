# I11 验证

## I11-03B E-06 新鲜备份与隔离恢复（2026-08-01）

- Source 只读身份：`blog_db/blog_user@localhost:5432`、revision 024、其他 session=0；
  12 类记录 123 行，aggregate=`8a777345...02d9d`。
- 仓库外恢复点：`/Users/limengyang/Backups/2025-blog-public/20260801-i11-e06-source-024`。
  custom dump、两份附件 tar、两份逐文件清单 5/5 SHA-256 PASS；dump TOC 322；
  backend uploads 2/2、兼容 pictures 10/10。
- 全新隔离库从 dump 恢复为 024；与 source 的 count、PK、规范 hash 全等。
  隔离库升级 024→025 后 business aggregate 不变，owner manifest 121+2、唯一
  canonical owner、duplicate PK=0，关系 orphan=0；current=head=025、
  `alembic check` 与 readiness PASS，`AUTH_BYPASS=false`。
- 第一次总清单校验因并行生成清单与总 hash 的竞态出现 1/5 失败；按依赖顺序
  重建总清单后 5/5 PASS。首次 Alembic 命令因重渲染 URL 引入 `%` 插值而在连接
  前失败，改为保留原始凭据文本仅替换数据库名后 PASS。两次均未写 source。
- 隔离数据库已删除且 catalog=0；临时附件移入系统废纸篓；长期备份清理后
  再次 5/5 PASS。机器证据：
  `assets/e06-backup-restore-verification-20260801.json`。

结论：I11-03B `PASS`，允许进入停写与 target 构建。

## I11-03C 停写、source 025 与 Cutover Target（2026-08-01）

- 发现 LaunchAgent `com.blog.backend` 在 source 达到 readiness 025 后自动启动；
  source 当时已默认只读。精确卸载该 agent 后 `:8000` listener=0、其他 source
  session=0，停写重新成立。
- 首次尝试用 `PGOPTIONS` 为 asyncpg Alembic 连接覆盖只读失败，025 DDL 在事务内
  回滚，source 仍 024/on/0 sessions。随后使用 `finally` 保护的短维护窗口关闭默认
  只读、执行 024→025、立即恢复默认只读；业务 123-row PK/hash aggregate 零漂移。
- 在无公网 listener 的维护窗口创建 admin/non-admin 一次性身份，loopback
  `:18001` 真实登录得到 cookie session；admin dashboard=200、non-admin=403、
  anonymous/invalid=401，`AUTH_BYPASS=false`。凭据仅在 `/private/tmp` mode 600。
- 冻结点 source 为 revision 025、125 rows（含两个一次性 user），aggregate
  `1013a457...5c095`。cutover dump SHA-256=`db141143...5b32`、TOC=322。
- 稳定 target `blog_v2` 与仓库外附件 authority 已建立。source/target 125/125、
  inserted/updated/deleted=0、aggregate match；两端临时 user/session/login audit
  均为 2；关系 orphan=0。target current=head=025、check/readiness PASS。
- Source `blog_db` 默认只读；target `blog_v2` 默认可写；本阶段结束时所有 backend
  listener=0。机器证据：`assets/e06-cutover-target-verification-20260801.json`。

结论：I11-03C `PASS`，允许首次 authority 切换与观察。

## I11-03D 首次 Authority 切换与观察（2026-08-01）

- 使用测试通过的 authority rewriter 精确更新 ignored `backend/.env`：database
  `blog_db`→`blog_v2`，新增仓库外 `UPLOAD_ROOT`；JWT/AI/DB 凭据文本不输出、
  不进入 Git，原 `.env` mode-600 副本保存在新鲜备份目录。
- 切换后 Settings 只读复核：host/port/user 不变，database=`blog_v2`，密码存在，
  upload root 为新 authority，`AUTH_BYPASS=false`、allow=false。source 025/on，
  target 025/off。
- Loopback `:18002` 运行三轮观察，每轮 health/public notes=200，匿名/失效
  admin=401，真实 admin me/dashboard=200，真实 non-admin dashboard=403，
  missing note=404，管理员附件列表与实际附件内容=200。无 AUTH_BYPASS。
- 观察结束 backend 已停止。机器证据：
  `assets/e06-first-switch-observation-20260801.json`。

结论：I11-03D `PASS`，允许增量对账与幂等重放。

## I11-03E Forward Delta 与幂等重放（2026-08-01）

- 观察后重新采集 source、target scan A、target scan B。source 冻结点自身
  revision/count/PK/hash 不变。
- 第一次 source→target replay：125/125，insert/update/delete=0，aggregate
  match。第二次 replay 与 target A→B 均为同一零 delta/no-op 结果。
- 两端临时 user/session/login audit 均为 2，其他 session=0；target 关系
  orphan=0；target attachments 2/2 SHA-256 PASS。
- 机器证据：`assets/e06-forward-delta-idempotency-20260801.json`。

结论：I11-03E `PASS`，允许 reverse delta 与回切。

## I11-03F Reverse Delta 与回切（2026-08-01）

- 先将 `blog_v2` 默认只读，target→source 独立 snapshot 对账 125/125、
  insert/update/delete=0、aggregate match；reverse replay 为 no-op。
- 使用同一 tested rewriter 将 runtime database/upload authority 回到
  `blog_db` 与旧 upload root；source 恢复默认可写，target 保持默认只读。
- Loopback `:18003` 两轮回切观察：health/public=200，匿名/失效=401，
  admin me/dashboard=200，non-admin=403；`AUTH_BYPASS=false`。
- 观察后 source 冻结点仍零漂移，target→source 仍零 delta；所有临时 backend
  listener=0。机器证据：`assets/e06-reverse-delta-rollback-20260801.json`。

结论：I11-03F `PASS`，回切路径可用，允许最终重切与只读归档。

## I11-03G 最终重切与只读归档（2026-08-01）

- 最终停写 source 后，source/target 125/125、zero delta、aggregate match；runtime
  database/upload authority 重切到 `blog_v2` 与仓库外 target upload root。
- `blog_v2` 025 默认可写；Legacy `blog_db` 025 默认只读且未删除；旧 upload
  root 的目录与文件权限已设只读，target uploads 保持可写。
- 最终 loopback smoke 权限矩阵 PASS。恢复维护前既有 LaunchAgent
  `com.blog.backend` 后，`:8000` health/public notes=200；`pg_stat_activity` 仅
  `blog_v2` 有应用连接，`blog_db` 为 0。
- 这一步只恢复既有 runtime service，不构建/发布/部署新应用，不 push、不改
  Cloudflare。两个一次性验收身份将在 F-01 浏览器验收后精确清理。
- 机器证据：`assets/e06-final-switch-archive-20260801.json`。

结论：I11-03G `PASS`；final authority 已切换，I11-03H 等待验收身份与临时凭据
清理后的最终 123-row 复核。

## I11-03H 最终清理与 123-row 收口（2026-08-01）

- F-01 浏览器验收完成后，先关闭两份隔离浏览器会话，再停止既有
  `com.blog.backend` LaunchAgent。按用户名精确锁定两个临时身份；目标库仅有
  5 个从属 session、5 条对应 audit 和 1 条临时 admin profile，Legacy 仅有
  2 个从属 session、2 条对应 audit，所有内容型 `created_by` 引用均为 0。
- 两库分别在单事务内删除上述精确依赖和 2 个临时用户；Legacy 只在该维护事务
  短暂关闭数据库级默认只读，并在退出保护中恢复为只读。删除后两个用户名、
  session、对应 audit/profile 均为 0。
- 清理后只读 source/target 快照均为 revision 025、123 rows，PK 与规范 row hash
  全等；insert/update/delete/delta 均为 0，aggregate SHA-256 相同。机器证据：
  `assets/e06-final-source-post-cleanup-20260801.json`、
  `assets/e06-final-target-post-cleanup-20260801.json`、
  `assets/e06-final-post-cleanup-reconciliation-20260801.json`。
- 最终 runtime authority 为 `blog_v2` 与仓库外 target upload root；目标数据库和
  附件可写。Legacy `blog_db` 默认只读，旧 `backend/uploads` 为文件系统只读；
  LaunchAgent 恢复后 health/public notes=200，`pg_stat_activity` 仅显示应用连接
  `blog_v2`。有效设置 `AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false`。
- 新鲜 revision-024 备份及其 5/5 hash/read/隔离恢复证据继续作为 rollback
  基线；target→source reverse delta 与实际回切观察由 I11-03F 证明可用。隔离
  前端树、临时凭据/会话文件和生成缓存已可恢复地移入系统废纸篓，未写入 Git。

结论：I11-03H `PASS`；E-06 执行面完成，进入 I11-04 主验证与独立交叉验证。

## I11-04 主验证与独立交叉验证（2026-08-01）

- 独立 Python 进程分别通过 `psql` 的只读事务读取 12 个业务表的主键与
  `md5(to_jsonb(row))`，再在进程外计算 SHA-256 聚合；source/target 均为
  revision 025、123 rows、表计数相同、主键重复=0、聚合哈希相同。
- 独立 SQL 关系审计的七类 orphan（mistake/question、mistake/draft、review
  target、review record、attachment link attachment/target、capture attachment）
  两库均为 0；canonical owner 存在且两库临时验证身份均为 0。immutable v1
  manifest 仍为 121 rows，SHA-256=`a2d91fd48c96f4dfde15346c33b66e6ee58e581fb25dfa3258725dcd49dbbe4e`，
  与既有 2-row E05 delta 合计 123 rows、source key 重复=0。
- 独立附件树比较：Legacy 与 target 均 2 个可读文件，逐文件相对路径与 SHA-256
  完全一致；Legacy 目录权限只读，target 目录可写。
- 运行配置独立解析为 database=`blog_v2`、target upload root、有效
  `AUTH_BYPASS=false`/`AUTH_BYPASS_ALLOW=false`；LaunchAgent 正常运行，
  `pg_stat_activity` 仅有 `blog_v2|blog_user` 应用连接，`blog_db` 为 0。
- 机器证据：`assets/e06-independent-cross-validation-20260801.json`。

结论：I11-04 `PASS`；I11/E-06 的 live authority、回切、只读归档和独立复核
均已证据闭合，进入 I12-01/F-01。

## 2026-07-31 E-05 隔离执行

### I11-02A 授权

- 用户明确批准 `tasks.md` I11-02A 至 I11-02H，仅授权 E-05 隔离执行。
- 该批准有限反转 2026-07-29 “不实现 shadow”简化决策，不授权 E-06、
  source 写入、正式流量、停写、归档、部署或推送。
- 结论：I11-02A `PASS`。

### I11-02B Source 与输入锁定

- Source 只读身份：database=`blog_db`、role=`blog_user`、
  `transaction_read_only=on`、revision=`024`。
- 当前 12 类 source count=`123`；aggregate=
  `8a7773453f560d626583495d67730ce2cb6d6a4b22b00fad4d7a3abd90802d9d`。
- Immutable v1 manifest count=`121`，SHA-256=
  `a2d91fd48c96f4dfde15346c33b66e6ee58e581fb25dfa3258725dcd49dbbe4e`；
  v1 既有行 hash drift=0、owner conflict=0、关系 orphan=0。
- Snapshot 后增量恰好为两个 `users`：
  `3f37d7e5-3bcc-49af-8d08-987d089bc9b8` 与
  `ecbbc83f-df65-43bf-b9a1-18e5e15db8f3`，均按规则 `ARCHIVED`。
- C5 dump SHA-256=`5e1f967d...157138f`，`BACKUP.sha256` 8/8 PASS，
  `pg_restore --list` 322 entries；现有 `i11_shadow_%` target count=0。
- 证据：`assets/e05-input-preflight-20260731.json`。
- 结论：I11-02B `PASS`；v1 不改写，两个新增 user 进入 delta manifest。

### I11-02C Shadow/Delta 工具

- TDD 依次验证并实现：
  1. 写目标拒绝 `blog_db`，只允许 `i11_shadow_` 前缀。
  2. scan A/B 分类 unchanged/inserted/updated/deleted。
  3. v1 immutable hash fail closed；新增非 canonical user 为 `ARCHIVED`。
  4. insert/update/tombstone replay 幂等，第二次 applied_count=0。
- `test_shadow_delta_tool.py` 4/4 PASS；`py_compile` PASS。
- 真实 `snapshot` 子命令仅以 `BEGIN READ ONLY` 读取 source，输出 123 rows、
  aggregate=`8a777345...02d9d`，不包含正文或密码 hash。
- 证据：`assets/shadow_delta_tool.py`、`test_shadow_delta_tool.py`、
  `e05-source-scan-a.json`。
- 结论：I11-02C `PASS`。

### I11-02D 一次性 Shadow Target

- 创建前 `i11_shadow_e05_20260731` catalog count=0。
- Fresh source custom dump 位于仓库外
  `/tmp/i11-e05-shadow.T16eJE/source-024.dump`，SHA-256=
  `297099089acababcb54ac2fd25d19e538c5090061761d197fa624157222d109b`，
  `pg_restore --list` 322 entries。
- Restore 身份为 target=`i11_shadow_e05_20260731`、role=`blog_user`、
  revision=`024`；仅在 target 执行 024→025。
- 后验：`current=025 (head)`，`alembic check` clean。Target snapshot
  123 rows、aggregate=`8a777345...02d9d`，与 source scan A 完全一致。
- 证据：`assets/e05-shadow-preledger-snapshot.json`。
- 结论：I11-02D `PASS`；source 未执行 DDL/DML。

### I11-02E 全量 Ledger 与 Delta Manifest

- `initialize` 在 shadow-only schema 创建 ledger/tombstones。
- v1 manifest 保持 121 rows 与原 hash；delta manifest 仅包含两个 snapshot 后
  user，均映射 canonical owner 且 disposition=`ARCHIVED`。
- Source snapshot=123、v1=121、delta=2、ledger=123。
- owner conflict=0、owner FK orphan=0、七类关系 orphan=0、tombstone=0，
  shadow business hash 与 source scan A 一致。
- 证据：`assets/e05-delta-manifest-20260731.json`、
  `e05-shadow-initialize-20260731.json`。
- 结论：I11-02E `PASS`。

### I11-02F 双扫描增量对账与幂等重放

- Source scan A/B 均为 123 rows，aggregate 均为
  `8a7773453f560d626583495d67730ce2cb6d6a4b22b00fad4d7a3abd90802d9d`；
  两次只读扫描完全一致。
- 分类结果：unchanged=123、inserted=0、updated=0、deleted=0；
  没有未映射增量、重复映射、owner conflict 或 unexplained drift。
- 第一次 replay applied=0；第二次 replay applied=0，验证当前 snapshot 的
  no-op 幂等路径。
- Shadow business rows=123、ledger=123、tombstones=0；source scan、
  business hash 与 ledger hash 全部匹配。
- 证据：`assets/e05-source-scan-a.json`、`e05-source-scan-b.json`、
  `e05-delta-reconcile-first.json`、`e05-delta-reconcile-second.json`。
- 结论：I11-02F `PASS`。

### I11-02G 完整性审计、回滚与销毁

- 独立只读 SQL 验证：business=123、ledger=123、missing ledger=0、
  extra ledger=0、distinct owner=1；唯一 owner 为
  `4c503215-b158-4162-b472-79df8289ed0a`。
- owner FK orphan=0；mistake/question、mistake/draft、review target、
  review record、attachment 与 capture 共七类关系 orphan 全部为 0；
  tombstone=0。
- 删除 shadow-only `i11_shadow` sidecar 后，以显式隔离
  `DATABASE_URL` 运行 `alembic check`，结果
  `No new upgrade operations detected`。
- 精确销毁 `i11_shadow_e05_20260731`，销毁后 PostgreSQL catalog count=0。
  仓库外临时 dump 目录 `/tmp/i11-e05-shadow.T16eJE` 已移入
  `/Users/limengyang/.Trash/i11-e05-shadow.T16eJE`，未不可恢复删除。
- 销毁后 source 只读复扫仍为 database=`blog_db`、revision=`024`、
  123 rows、aggregate=
  `8a7773453f560d626583495d67730ce2cb6d6a4b22b00fad4d7a3abd90802d9d`；
  与 scan A 逐行完全一致。
- 证据：`assets/e05-independent-integrity-20260731.json`、
  `e05-source-scan-post-destroy.json`。
- 结论：I11-02G `PASS`；source 未写入，shadow 已完成可验证销毁。

### I11-02H 全量测试与 E-05 收口

- Shadow/workflow 工具：4/4 tests PASS；`py_compile` PASS。
- Backend：新建独立 `i11_test_e05_20260731`，从空库升级至
  `025 (head)`；显式 `DATABASE_URL` 下 307/307 tests PASS，
  `compileall` PASS，`alembic check` clean。两条既有 AI Gateway
  `AsyncMock` RuntimeWarning 保留为非阻塞测试债务。
- Frontend：23 files、64/64 tests PASS；`npx tsc --noEmit` PASS；
  `npm run build` PASS，40/40 static pages generated。
- 隔离测试库已销毁；shadow/test 两个精确数据库名最终均不存在。
- 所有 E-05 JSON evidence 均通过 `jq empty`；生成的 `__pycache__` 已移入
  废纸篓；`git diff --check` PASS。
- 最终 source 只读复扫仍为 revision 024、123 rows、aggregate
  `8a7773453f560d626583495d67730ce2cb6d6a4b22b00fad4d7a3abd90802d9d`，
  与执行前 scan A 逐行一致。
- 证据：`assets/e05-source-scan-final.json` 及本节命令结果。
- 结论：I11-02H `PASS`；E-05=`PASS`。该结论只证明隔离 shadow/delta
  能力，不授权 E-06、生产切换、部署、推送、停写或归档。

## 历史门槛记录

2026-07-26 时点已收到用户“批准并继续”，I11-01 批准核验为 PASS。项目同时
确认采用单一 owner 模式。当时 E-05/E-06 尚未执行，因为 I10
`DRY_RUN_READY=BLOCKED`：canonical owner identifier、逐类 owner/backfill、
冲突处置和回滚映射尚未明确。当时结论为
`APPROVED / BLOCKED BY OWNER GATE`，不是 E-05/E-06 PASS。

2026-07-31 E-05 获批前，I10 通过 121-row 单 owner 隔离 backfill、owner FK/关系
完整性、双重复核、025 schema check、隔离销毁和日常库基线恢复，E-03=
`DRY_RUN_READY PASS`。在该时点 E-05/E-06 更新为
`READY / NOT AUTHORIZED`，尚未执行 shadow、delta、switch、停写或归档；
后续 E-05 执行终态以本文顶部 I11-02A 至 I11-02H 记录为准。
