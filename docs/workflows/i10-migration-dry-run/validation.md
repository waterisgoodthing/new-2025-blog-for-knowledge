# I10 验证

## 2026-07-31 Owner Gate 执行

### I10-06 执行输入

- 用户已明确批准执行 `tasks.md` I10-06 至 I10-10。
- C5 024 备份：
  `/Users/limengyang/Backups/2025-blog-public/20260728-c5-source-024/database.dump`，
  SHA-256=`5e1f967d0555d9e767955004b1703f25b1f4bfa9245b7a62e032df93c157138f`，
  与 `BACKUP.sha256` 一致；`pg_restore --list` 为 322 entries。
- Immutable owner manifest SHA-256=
  `a2d91fd48c96f4dfde15346c33b66e6ee58e581fb25dfa3258725dcd49dbbe4e6`；
  source_count/row_count=`121/121`，12 类计数完整，唯一 target owner 为
  `4c503215-b158-4162-b472-79df8289ed0a`。
- 日常库仅以 `BEGIN READ ONLY` 核验：database=`blog_db`、role=`blog_user`、
  `transaction_read_only=on`、revision=`024`、canonical owner count=`1`。
- 创建前 catalog 中 `i10_owner_backfill_%` 数据库数量为 0。
- 结论：I10-06 `PASS`；未创建隔离库，日常库无写入。

### I10-07 隔离 Owner Backfill Dry-Run

- TDD：`test_owner_backfill_dry_run.py` 依次以缺少接口确认 RED，再实现目标库
  拒绝、单 owner manifest 校验和 fail-closed audit；当前 3/3 PASS，
  `py_compile` PASS。
- 日常库 backfill 前只读基线为 revision 024、source_count=123、
  aggregate=`8a7773453f560d626583495d67730ce2cb6d6a4b22b00fad4d7a3abd90802d9d`。
  相对 immutable 121-row manifest 有 2 条新记录；本轮未吸收、覆盖或改写它们。
- 一次性目标 `i10_owner_backfill_20260731_approval` 创建前 catalog count=0；
  从 C5 024 backup 恢复后身份为该数据库、role=`blog_user`、
  `transaction_read_only=on`、revision=`024`。
- `owner_backfill_dry_run.py` 在隔离库创建
  `i10_dry_run.owner_backfill`，其 `owner_id` 为
  `NOT NULL REFERENCES users(id)`；从 immutable manifest 写入 121 条映射。
- 结果：source/manifest/sidecar=`121/121/121`；missing=0、extra=0、
  hash drift=0、owner conflict=0、owner FK orphan=0、七类关系 orphan=0，
  canonical owner count=1，`passed=true`。
- 证据：`assets/i10-owner-backfill-execution-20260731.json`。
- 结论：I10-07 `PASS`；写入仅发生在隔离数据库。

### I10-08 完整性审计与独立复核

- 当前代码 Alembic head 为 025；日常库和 C5 backup 为 024。首次在 024 clone
  执行 `alembic check` 返回 target not up to date，根因是缺少既有 migration
  025，不是 owner backfill drift。
- 按范围内计划校正，仅在隔离目标执行 024→025；随后
  `current=025 (head)`。基础 schema 在 sidecar 创建前 `alembic check` clean。
- 025 上重新执行 owner backfill：source/manifest/sidecar=`121/121/121`，
  missing/extra/hash drift/owner conflict/owner FK orphan/relationship orphan
  全为 0，`passed=true`。
- 独立 `psql` UNION/LEFT JOIN 查询未复用 Python verifier，结果为
  revision=025、source=121、sidecar=121、distinct owner=1、missing=0、
  extra=0、owner orphan=0；11 个非空 population 分组计数与 manifest 一致，
  `capture_items=0`。
- Alembic 会把 sidecar 正确识别为非迁移结构；证据采集后只在隔离库执行
  `DROP SCHEMA i10_dry_run CASCADE`，随后 `alembic check` 输出
  `No new upgrade operations detected`。
- 证据：`assets/i10-owner-backfill-integrity-audit-20260731.json`。
- 结论：I10-08 `PASS`；owner FK orphan=0，七类关系 orphan=0。

### I10-09 隔离环境销毁与日常库保护

- 销毁前确认隔离库中 `i10_dry_run` schema count=0，目标无活动连接。
- 显式删除 `i10_owner_backfill_20260731_approval` 后，以 `pg_database` 复核
  count=0。
- 日常库前后均以同一 `manifest_tool.py verify` 只读执行：
  revision=`024`、source_count=`123`、aggregate=
  `8a7773453f560d626583495d67730ce2cb6d6a4b22b00fad4d7a3abd90802d9d`、
  extra/hash drift/owner conflict/orphan=`0`，相对 121-row snapshot 的
  missing=`2` 前后不变。
- 最终只读身份为 database=`blog_db`、role=`blog_user`、
  `transaction_read_only=on`、revision=`024`。
- 结论：I10-09 `PASS`；隔离环境已销毁，日常库未写入。

### I10-10 测试与恢复收口

- 前端 Vitest：23 files、64 tests 全部 PASS。
- TypeScript：`npx tsc --noEmit` PASS。
- Next production build：PASS，40/40 static pages generated。
- Workflow：I10 3/3、C1/C6 5/5，合计 8/8 PASS；`py_compile` PASS。
- 后端第一次未覆盖 `DATABASE_URL`，默认连接日常 revision 024；结果为
  288 passed / 19 failed，首个根因为 runtime 要求 revision 025。该运行在
  12:04 留下两条失败 `capture_recognition` 测试记录：
  - `ai_runs.id=5577ec86-8d50-4c31-9256-b7168267565f`
  - `ai_call_logs.id=cc6f2a37-bbda-4053-8b91-f6785234f3f5`
- 只读复核确认两条记录各存在 1 行，AI run 没有 child run。日常 manifest
  从执行前 123 条变为 125 条，aggregate 从
  `8a777345...02d9d` 变为 `f4d2ae0a...7ce31`。
- 随后从同一备份创建 025 隔离测试库，在 `AUTH_BYPASS=false`、
  `AUTH_BYPASS_ALLOW=false` 下完整后端为 307/307 PASS；测试库已删除，
  两个 I10 隔离数据库 catalog count=0。
- 用户随后明确批准精确删除上述两条测试残留。删除前只读复核确认各 1 行、
  task_type=`capture_recognition`、run status=`failed`、log success=false，
  且 run child count=0。
- 恢复事务按 ID、task_type 和失败状态限定删除，每类影响行数必须恰好为 1，
  否则抛错回滚；事务成功提交。
- 最终只读 verifier：两个 ID count=`0/0`，日常库 revision=`024`、
  source_count=`123`、aggregate=
  `8a7773453f560d626583495d67730ce2cb6d6a4b22b00fad4d7a3abd90802d9d`，
  与执行前基线完全一致；关系 orphan=0。I10 隔离数据库 catalog count=0。
- 结论：I10-10 `PASS`；E-03=`DRY_RUN_READY PASS`。E-05/E-06 更新为
  `READY / NOT AUTHORIZED`，未实际执行。

## 结果

- `git status --short` 已在本轮开始执行。
- 静态来源读取与哈希：PASS；`public/blogs` 两个索引均为空，manifest 已保存。
- 源库只读连接：PASS，`blog_db:5432`、角色 `blog_user`、revision `020`；源事务 `transaction_read_only=on`。
- 静态清单和数据库 manifest：PASS，未写入源库或提交个人正文/dump。
- 临时 clone：`pg_dump --no-owner --no-acl` 与 `pg_restore` 成功；020→024 upgrade 成功，`alembic current=head=024`，`alembic check` 无新操作。
- 主对账：8 个核心表共同字段 count/hash 全等；notes 13、mistakes 3、questions 3、attachments 1、ai_runs 32、ai_call_logs 47、audit_logs 105、review_items 3。
- 关系/冲突：duplicate slug=0；3/3 Mistake→Question；3/3 ReviewItem→Mistake；公开 notes 全部 `published,false`。
- 回滚重放：024→020→024 成功；独立新进程重新执行 source read-only、revision、count/hash、关系复核，均 PASS。
- 销毁：`DROP DATABASE pls_v2_i10_source_dryrun_20260726` 成功，catalog 复核确认临时库不存在。
- 独立 owner 复核：第一次同步 engine 探针因项目 `asyncpg` URL 误用产生 `MissingGreenlet`，未触碰数据库；随后以新进程和项目异步 engine 重跑，`transaction_read_only=on`、身份、revision、逐表计数和 owner-like 字段结果与报告一致；另以只读查询确认 `attachments.created_by` 存在、用户角色为 4 admin / 4 non-admin。

结论：技术 E-04=PASS；总体 `DRY_RUN_READY=BLOCKED`，阻塞原因是 owner/backfill 责任与逐行归属尚未明确，不能进入 I11。

## I10 continuation recheck (2026-07-26)

- 重新执行 `git status --short`、AGENTS/workflow 读取和 package/backend 入口核对；dirty worktree 中的既有变更未被覆盖。
- 隔离目标以 `cd backend; PYTHONPATH=.; alembic` 入口核验为 `current=024`、`heads=024`，`alembic check` 输出 `No new upgrade operations detected`。
- 源库以同一正确入口只做 `current` 查询为 `020`；新进程异步只读探针确认 `transaction_read_only=on`、身份 `blog_db/blog_user:5432`，计数仍为 notes 13、questions 3、mistakes 3、review_items 3、review_records 4、attachments 1、attachment_links 1、ai_runs 32、ai_call_logs 47。
- 本次探针的两个命令问题已记录：根目录 Alembic 会找错脚本路径；backend 目录需要 `PYTHONPATH=.`；系统 PATH 没有 `python`，最终使用项目 `.venv/bin/python` 成功完成只读复核。上述失败均未连接写入或迁移数据库。
- owner 覆盖报告、I10 task 状态与主 workflow 状态保持一致；I11/I12 未被误标为完成。
- owner 覆盖补查发现源库 `capture_items=0`、`draft_items=6`，两者均只有 nullable `created_by` 或空人口，已纳入 [owner-coverage.md](owner-coverage.md)；这不改变 owner gate 的 `BLOCKED` 结论。

## Single-owner governance update (2026-07-26)

- 用户确认这是个人项目，采用单一 owner 模式：同一项目 owner 负责 owner
  决策、冲突处置、审计证据和回滚决定；不再要求另设负责人或独立审批人。
- 本次仅更新 workflow 决策文档，没有写入源库、隔离数据库、生产库或业务代码。
- canonical target owner identifier、逐类 mapping manifest 和剩余冲突处置仍未提供，故 `DRY_RUN_READY` 继续为 `BLOCKED`；该文档政策调整不授权 E-05/E-06。

## Fresh owner-gate recheck (2026-07-26)

- 新的只读事务再次确认 source `blog_db/blog_user:5432`、`transaction_read_only=on`、Alembic revision `020`；逐表计数仍为 `notes=13, questions=3, mistakes=3, review_items=3, review_records=4, attachments=1, attachment_links=1, capture_items=0, draft_items=6, ai_runs=32, ai_call_logs=47, users=8`，用户角色仍为 `4 admin / 4 non-admin`。
- 静态来源 `public/blogs/categories.json` 与 `public/blogs/index.json` 仍为空；本次只读 SHA-256 为 `9a88878a8ef9046d3e889eaafb299e6a213529266b1f8618856698c2e253079b` 与 `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`。
- 隔离目标仍为 `024 (head)`，未发现 owner manifest、冲突裁决或回滚责任的新外部输入；`DRY_RUN_READY` 继续为 `BLOCKED`，I11 E-05/E-06 不执行。
