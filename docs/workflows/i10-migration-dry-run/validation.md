# I10 验证

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
