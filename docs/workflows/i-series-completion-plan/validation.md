# I 系列完成执行验证

事实日期：2026-07-28
执行环境：`/Users/limengyang/2025-blog-public`，本机 PostgreSQL `blog_db:5432`

## 执行前规划缺陷补正

- 目标：补齐候选 artifact 纠缠切分与已部署前端/source DB mismatch 两个 P0 缺陷。
- 范围：仅 `docs/workflows/i-series-completion-plan/` 文档；读取 Git、代码引用、进程、端口、Cloudflare ingress、生产 HTTP 和 DB revision。
- 不做：未改源码，未写数据库，未启动/停止服务，未改生产配置。
- 前置：`git status --short` 已保存；dirty/untracked 用户改动保持原样。
- 执行证据：`design.md` 2.4 列出 migration/runtime/contracts/tests 完整冻结集合；2.5 记录 OpenNext 前端、public API→localhost:8000 tunnel、无 8000 listener/Uvicorn、public health 502、candidate expected=024、source=020；`risk-register.md` I-RISK-P0-02/03。
- 退出：`PASS`。
- 本轮实际改动摘要：文件仅为本 workflow 的 `README.md`、`design.md`、`requirements.md`、`tasks.md`、`risk-register.md`、`validation.md`；数据库无改动；源库无写入；Git 未 stage/commit/push。

## C0 Owner/Backfill 决策

- 目标：确定 D1-D8，解除 owner 决策 UNKNOWN。
- 范围：只读 users 查询与 workflow 决策记录。
- 不做：不生成 C1 manifest，不写 source/target DB，不迁移 password hash。
- 前置：2026-07-28 用户明确授权 D1-D8 默认决策与 C0-C12 连续执行。
- 执行证据：只读事务返回 8 users/4 admins；`WHERE is_admin IS TRUE ORDER BY id LIMIT 1` 得到 `4c503215-b158-4162-b472-79df8289ed0a|i5-profile-fe846c85`。D1 为 source→target 同 UUID；D2 row-level manifest；D3 其余 7 identities ARCHIVED/password hash excluded；D4 QUARANTINED；D5 strict-equivalence-only MERGED；D6 AI logs owner-controlled read-only ARCHIVED；D7 quarantine+inverse map+snapshot；D8 两组错题分别 MIGRATED。
- 退出：`PASS`；D1-D8 无 UNKNOWN。`DRY_RUN_READY` 仍待 C1 双重复核，不在 C0 提前升级。
- 本轮实际改动摘要：仅 workflow 文档；数据库无改动；源库只读；Git 未 stage/commit/push。

## C1 Row-Level Manifest 与独立复核

- 目标：只读生成覆盖 12 类当前 source records 的逐行 manifest，并由不同进程/查询独立复核后重判 `DRY_RUN_READY`。
- 范围：source `blog_db:5432` revision 020 只读；workflow `assets/` 下生成器、测试、manifest 与验证报告。
- 不做：不写 source DB，不创建 target DB，不迁移 password hash，不保存原始行/用户名/内容到 manifest。
- 前置：C0 PASS；canonical owner=`4c503215-b158-4162-b472-79df8289ed0a`；D1-D8 已生效。
- 执行证据：`python3 -m unittest -v test_manifest_tool.py` 为 2/2 PASS；`py_compile` PASS。进程一 `manifest_tool.py generate` 逐表只读查询得到 source_count=121，ARCHIVED=86，MIGRATED=35，12 类 counts=`13/3/3/3/4/1/1/0/6/32/47/8`，source aggregate SHA-256=`b40b109a0a1a7eca9b633a11503f8327c8c051fa0b4f05fb0efa04a79089adb6`，manifest payload SHA-256=`c98bdfa3a560ea47ab1768215a3600aa19b3d190f42ac13d4ebfcb51a80be3b5`。进程二 `verify` 使用单 UNION 查询与独立关系 SQL，结果 missing=0、extra=0、duplicate=0、hash_drift=0、owner_conflict=0、disposition_rule_conflict=0、orphan=0、source aggregate match=true；见 `assets/c1-independent-verification.json`。
- 退出：`PASS`；`DRY_RUN_READY=PASS`。
- 本轮实际改动摘要：新增 `assets/manifest_tool.py`、`test_manifest_tool.py`、`owner-mapping-manifest-v1.json`、`c1-independent-verification.json` 并更新 workflow 文档；源库只读；无 target DB；Git 未 stage/commit/push。

## C2 带 Manifest 的隔离 Dry-Run

- 目标：在可销毁隔离 target 重跑 source clone 的 `020→024`，证明 manifest、数据、schema、rollback/replay 与销毁门槛持续 PASS。
- 范围：source `blog_db:5432` 仅由 `pg_dump` 读取；临时 DB `i_series_c2_20260728` 写入；仓库外临时目录 `/tmp/i-series-c2.a6nliO`。
- 不做：不写 source DB，不服务任何正式流量，不改生产配置，不部署。
- 前置：C1 `DRY_RUN_READY=PASS`；Alembic heads=`024 (head)`，source current=`020`；目标 DB 预检查不存在，source 除检查会话外连接数=0。
- 执行证据：source custom dump SHA-256=`23da88c184597fc49f0b2358be578e1e05f3e752f1f1fbd81147c6a68d134eab`；restore current=020。第一次 `createdb` 以 `blog_user` 因缺少 CREATEDB 权限失败且未创建目标，随后由本机管理角色创建、owner=`blog_user`，根因已闭合。clone 执行 `020→021→022→023→024` 后 current=head=024，`alembic check`=`No new upgrade operations detected`；manifest 020 字段投影 121/121、missing/extra/duplicate/hash drift/owner conflict=0；notes revision 与 attachment workspace 回填 bad=0；新表初始 rows=0；pg_trgm=1；关系 orphan=0。随后 `024→020`，原始 121 行 manifest 再验 PASS；再次 `020→024`，head/check/manifest/backfill 全 PASS。
- 回滚/销毁证据：rollback replay 已实跑；临时 DB drop 后 `pg_database` count=0。工具层拒绝 `rm -rf`，未执行该命令；临时 dump 目录改为可恢复地移动到 `/Users/limengyang/.Trash/i-series-c2.a6nliO-20260728`，原 `/tmp` 路径不存在。
- 退出：`PASS`；`DRY_RUN_READY` 持续 PASS。
- 本轮实际改动摘要：隔离 DB 创建、迁移、降级、重放后已删除；源库只读；临时 dump 在废纸篓可恢复；仓库仅更新 workflow 文档；Git 未 stage/commit/push。

## C3 候选 Artifact 冻结与 Runbook 审查

- 目标：把 021-024 与 I3-I10 纠缠 runtime/contracts/tests 冻结为同一个可审计候选，并审查 SQL、锁、extension、数据影响与回滚。
- 范围：当前 Git base、全部 dirty/untracked `backend/`/`src/` 纠缠文件、owner manifest、离线 upgrade SQL、恢复 runbook；仓库外路径 `/Users/limengyang/Backups/2025-blog-public/i-series-artifacts/20260728-c3-candidate/`。
- 不做：不 commit/stage/push，不部署，不改 source DB，不混入 Phase 1.0 文档/截图 dirty。
- 前置：C2 PASS；Alembic `020→021→022→023→024` 单 head；C2 同代码 024 `alembic check` clean。
- 执行证据：Git base=`cc05ef5b4b3fa0504d3ebbc07105ed260397cb71`；候选文件 83，复制后 `shasum -c` 83/83 OK。file hash manifest SHA-256=`2a70223b11d7d456ad3cceaccba01304e5219261ab65e7286b7b6e1a38abcfb8`；bundle=`de60d2ec8f56ef742b2f06633fe17be5bf96bb84b004ba614b56a1e072defa70`；tracked patch=`4aad86dfa9f25897867185dd643e1a089e5958132d001a0f39d455aece0ff782`；upgrade SQL=`e12f0e09afeaeb2d12c222aef295c35196e5ad65466d71cb6983d978184299b1`；顶层 `ARTIFACT.sha256` 11/11 OK，自身 hash=`c88ddad22d2d39f1f92a5a6145a06532ff10c50370215c8e9e65e399fcfa9e40`。
- 审查结论：021/023/024 ALTER 对 `mistake_drafts`/attachments/notes 需要强锁，C5 必须无应用连接；source 仅 1 attachment/13 notes，C2 实跑回填 bad=0。source 020 无 pg_trgm，clone 由 `blog_user` 创建成功。离线 upgrade SQL 完整；离线 downgrade 因 022 的在线数据保护查询无 bind 只能生成 partial，故主回滚固定为并行 020 restore/switch，不能依赖静态 downgrade。详见 `assets/c3-artifact-review.md`。
- 退出：`PASS`；C5 前必须逐文件 83/83 与 file-list hash 相等，否则硬停止。
- 本轮实际改动摘要：仓库新增 C3 审查文档并更新 workflow；仓库外新增可审计候选 bundle；数据库无改动；Git 未 stage/commit/push。

## C4 新鲜 020 备份、恢复与升级演练

- 目标：生成 C5 可恢复输入，验证最新 020 DB+附件备份可以恢复并升级至 024。
- 范围：source `blog_db:5432` 只读 dump/文件读取；长期仓库外备份 `/Users/limengyang/Backups/2025-blog-public/20260728-c4-source-020/`；隔离 restore DB `i_series_c4_restore_20260728`。
- 不做：不写 source，不改生产配置，不部署；不删除长期 020 备份。
- 前置：C3 artifact 83/83 SHA-256 仍 OK；C1 manifest fresh verify PASS、source revision=020、source 无其他连接。
- 执行证据：`database.dump` custom-format 206,185 bytes、`pg_restore --list` 289 entries；DB/两份附件 tar/owner manifest/source facts 的 `BACKUP.sha256` 8/8 OK，根 hash=`f34deee9b54e75a54efffb892b1f26cc25ba91b8779b5fd9a34c853ec71abca2`。附件恢复到临时路径后 backend uploads 2/2、兼容 pictures 10/10 SHA-256 OK。restore 020 的 121-row manifest 精确复核 PASS；升级后 current=head=024、`alembic check` clean、024 投影 hash PASS、backfill bad=0、pg_trgm=1；候选 runtime `validate_database_readiness()` 在 `AUTH_BYPASS=false` 下输出 `readiness=PASS expected=024`。
- 回滚/清理证据：C4 long-lived source 020 backup 保留。restore target 前无连接，drop 后 `pg_database` count=0；临时附件解压目录移至 `/Users/limengyang/.Trash/i-series-c4-attachments.fp1AFr-20260728`，没有删除备份。
- 退出：`PASS`；C5 使用此备份作为失败时并行恢复的输入。
- 本轮实际改动摘要：新增仓库外 C4 backup 与 SHA-256 evidence；隔离 DB 写入/迁移后已删除；source 仅只读；仓库更新 workflow 文档和 `c4-prebackup-source-verification.json`；Git 未 stage/commit/push。

## C5 Source 020→024 Upgrade 与 024 Restore Point

- 目标：在 fail-closed maintenance window 内将 source `blog_db:5432` 从 020 升至 024，并生成可验证的 024 恢复点。
- 范围：C5 前只读 production/tunnel/source/artifact/backup/manifest preflight；唯一 source 写入为 Alembic 020→024；后续只读验证和 024 dump。
- 不做：不部署、不 push、不改生产配置、不使用 AUTH_BYPASS、不执行 authority switch 或 Legacy 删除。
- 前置：C1/C2/C3/C4 PASS；C3 candidate 83/83 OK、C4 backup 8/8 OK；source fresh manifest PASS、revision=020、无非自身 DB session；无 Uvicorn/Gunicorn/8000 listener；Cloudflare tunnel 将 public API 指向 localhost:8000，`blog` health=404、public API health=502，确认不存在活 backend 连 source。
- 执行证据：`alembic upgrade head` 依次运行 020→021→022→023→024。后验：current=head=024，`alembic check`=`No new upgrade operations detected`；121-row old-field projection manifest missing/extra/duplicate/hash drift/owner conflict=0；backfill bad=0、new tables=`0,0,0,0`、pg_trgm=1、orphan=0；`validate_database_readiness()` 在 `AUTH_BYPASS=false` 下 PASS。FastAPI TestClient 公开 smoke：`/api/health`=200、`/api/notes`=200/total=13、`/api/notes/{slug}`=200。首个 smoke 对 list 形状作了错误假设而失败，实际 200 response 是分页 `{items,total,page,size}`；改为现有契约后重跑 PASS，未写数据。
- 恢复点：`/Users/limengyang/Backups/2025-blog-public/20260728-c5-source-024/`；custom dump 322 entries，DB/attachments/manifest/facts `BACKUP.sha256` 8/8 OK，root hash=`28c79256820523965aca3d223dae866044c43748ae8d292cf8224cd49b258135`。
- 退出：`PASS`；source schema authority=024。C4 020 backup 保留为 upgrade-failure parallel restore 输入，C5 024 backup 保留为 post-upgrade restore 输入。
- 本轮实际改动摘要：**source DB schema 写入** 020→024；新 024 backup 写入仓库外；仓库仅更新 workflow、`c5-preflight-source-verification.json`；未 stage/commit/push/部署。

## C6 E-05 Shadow Target 与增量对账

- 目标：创建仅隔离写入的 shadow target，按 C1 manifest 执行全量/增量、tombstone 和 zero-drift 对账。
- 范围：C5 后的只读代码/config/schema/DB inventory 审计。
- 不做：不创建伪 target clone，不写 source/target/Legacy，不执行 C7-C12。
- 前置：C5 PASS；owner manifest PASS。
- 执行证据：全仓 `rg` 仅发现一个 `Settings.DATABASE_URL` 和 `create_async_engine(settings.DATABASE_URL)`；`backend/app/cli.py` 只有 passkey/password/temp-admin CLI，无 export/import/shadow/delta/cutover 命令。`information_schema` 未发现 shadow/quarantine/archive/tombstone/identity-map/migration ledger 表或 `owner_id/source_table/source_id/disposition/archived_at/quarantined_at/tombstoned_at` 列；唯一相关字段为既有 `draft_items.source_id`。PostgreSQL 仅有 `blog_db`、`postgres` 和无关 acceptance DB；I11 docs 也只有设计性描述，没有实现 artifact。
- 退出：`BLOCKED`。没有可审计 target 及 upsert/tombstone/authority contract，无法证明 `unmapped=duplicate_manifest=owner_conflict=unexplained_drift=orphan=0`，更不能进入 C7 演练或 C8 实际切换。创建这些能力会扩大 C3 冻结后的候选 artifact 与数据模型，需要独立范围批准。
- 本轮实际改动摘要：仅 workflow/risk 文档；source/target/Legacy DB 无写入；Git 未 stage/commit/push/部署。

## C11/C12 提前 Fail-Closed 状态输出

- 目标：在 C6 blocker 已证实后，不部署地给出资格和十维状态结论。
- 范围：workflow evidence 汇总；不运行部署、push、生产配置或数据库写入。
- 执行证据：`f02-deployment-eligibility.md`=NOT ELIGIBLE/DO NOT DEPLOY；`f03-final-status-report.md` 逐项列 MVP、产品化、知识工作区、AI-OCR、备份恢复、dry-run、权威切换、Legacy、资格、部署，并明确 C6-C10 未完成。
- 退出：C11=`BLOCKED / early DO NOT DEPLOY`；C12=`BLOCKED / status report published, no completion claim`。
- 本轮实际改动摘要：仅 workflow 文档；没有 source/target/Legacy/prod 写入，没有 Git stage/commit/push/deploy。

## C0-C5 Git 权威收口：C1 升级后复核

- 目标：在 live source 已为 revision 024 后，继续用不可变 revision-020 manifest 证明 020 旧字段未漂移，并为 021-024 进入 Git 做 fail-closed 前置验证。
- 范围：`assets/manifest_tool.py`、`test_manifest_tool.py` 与 live `blog_db:5432` 的只读 SQL；新证据 `assets/c1-post-upgrade-verification.json`。
- 不做：不重新生成/改写 `owner-mapping-manifest-v1.json`，不写数据库，不 push、不部署、不改生产配置。
- 前置：C5 source current=024；C1 manifest source revision=020、aggregate=`b40b109a0a1a7eca9b633a11503f8327c8c051fa0b4f05fb0efa04a79089adb6`。
- 执行证据：TDD RED 为 `ImportError: cannot import name 'project_row_to_manifest_revision'`；实现后 `python3 -m unittest -v test_manifest_tool.py` 为 4/4 PASS，`python3 -m py_compile manifest_tool.py test_manifest_tool.py` PASS。verifier 只支持 020→020 与 database 024→manifest 020；其他 revision pair 抛出 `RuntimeError`。live 只读 UNION 查询在 024→020 投影下返回 source/manifest=121、missing=0、extra=0、duplicate=0、hash_drift=0、owner_conflict=0、invalid/rule conflict=0、orphan=0；canonical owner 不变；aggregate match=true 且仍为 `b40b109a...89adb6`。报告明确为 `manifest_source_revision=020`、`database_revision_actual=024`、`projection_revision=020`、`projection_applied=true`、`DRY_RUN_READY=PASS`。
- 退出：`PASS`。该结果只证明 020 旧字段在 024 中未漂移，不把 C1 manifest 升级为 024 新字段/新表快照。
- 本轮实际改动摘要：workflow/verifier/tests/JSON evidence；source DB 只读，数据库无写入；Git 尚未 stage/commit/push；无部署。

## C0-C5 Git 权威收口：提交前验证

- 目标：证明待提交的 C3 83-file 闭包未漂移、migration schema 权威一致，并记录前后端质量门槛。
- 范围：C3 SHA manifest、一次性 C5-024 restore、live Alembic 只读检查、frontend test/type/build 与 Git whitespace；后端测试只写隔离 DB。
- 不做：不写 live source，不使用 AUTH_BYPASS，不改生产配置，不 push/部署；不为通过测试而改动 C3 runtime artifact。
- 前置：C1 升级后只读复核 PASS；C5 024 backup 可恢复；candidate list 固定为 83 files。
- 执行证据：从仓库根目录执行 C3 `candidate-files.sha256` 为 83/83 OK，证明 migration/runtime/contracts/tests 与 C5 执行 artifact 未漂移。manifest unit 4/4 PASS、`py_compile` PASS、backend `compileall` PASS。后端测试从 C5 024 dump 恢复到一次性隔离库，显式 `AUTH_BYPASS=false/AUTH_BYPASS_ALLOW=false`；首次 collection 因命令遗漏 `PYTHONPATH=.` 未运行测试，修正后发现两个 HTTP case 共用的固定 admin UUID 不在 C5 快照，profile=404/upload FK=500；在新的隔离 restore 显式 seed 该测试身份后 35/35 PASS，临时库由 trap 删除，live source 未写。Alembic `heads=024`、`current=024`、`check=No new upgrade operations detected`。`npx tsc --noEmit` PASS；`npm run build` PASS（40 static pages）。frontend `npm test` 为 57/58：唯一失败 `static-placeholders.test.tsx` 的 Capture case 未挂载 Next App Router，抛出 `invariant expected app router to be mounted`；其余 20 files/57 tests PASS。该既有测试夹具失败不影响 migration/C1 hash correctness，但继续阻止 F-02 ELIGIBLE。
- 退出：Git/schema authority 收口验证 `PASS`；全量 frontend test 门槛 `PARTIAL (57/58)`；生产资格保持 `NOT ELIGIBLE / DO NOT DEPLOY`。
- 本轮实际改动摘要：source DB 只读；三个一次性验证 DB 均已删除；构建仅产生 ignored cache/output；Git 尚未 commit/push；无部署。

## C0-C5 Git 权威收口：精确暂存

- 目标：把产生 live 024 schema 的 migration 与其 runtime/contracts/tests 闭包纳入可审计 Git authority，同时隔离无关 dirty。
- 范围：C3 `candidate-files.txt` 的 83 files，加 `docs/workflows/i-series-completion-plan/` 的 16 files，共 99 files。
- 不做：不暂存 Phase 1.0、temp-admin、project assessment、UI review、其他 workflow/截图；不暂存 `.env`、dump、private key；不 push/deploy。
- 执行证据：`git add --pathspec-from-file=.../candidate-files.txt` 加 workflow 白名单；expected/actual sorted file set 的 `comm -3` 无输出；021-024 均为 `A`；`git diff --cached --check` 无输出；敏感/备份文件名筛查无命中。C5 执行前和本轮规范化前，C3 SHA manifest 为 83/83 OK；为满足 cached whitespace gate，最终 staged tree 仅 `backend/tests/test_i7_file_workspace.py` 与 `test_i8_markdown_search.py` 各移除一个 EOF 空行，因此 81/83 与 C3 byte-identical、2/83 为 test-only whitespace 差异；四个 migration 与全部 36 runtime model/router/schema/service/main 文件仍与 C3 hash 相同。
- 退出：`PASS`。暂存集合完整且无越界；migration 已进入待提交 Git tree。
- 本轮实际改动摘要：Git index 写入 99 files；working tree 的无关 dirty 保留且未暂存；数据库无写入；尚未 commit/push/deploy。
