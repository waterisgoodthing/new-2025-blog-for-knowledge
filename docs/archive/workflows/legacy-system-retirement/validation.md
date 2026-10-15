# LSR 验证与证据账本

当前总状态（canonical）：LSR-01=`PASS`、`[x]`（仅静态 mapping 验收范围）；LSR-02=`PASS`、`[x]`（仅静态数据迁移合同）；LSR-03=`PARTIAL`、`[ ]`（当前 fresh isolated runtime Verifier=`PASS`，完整 G2 验收证据未闭合）；G0=`PASS`；G1 Architect=`PASS`、Technical Reviewer=`PASS_WITH_NOTES`、combined G1=`PASS`；G2 Database=`BLOCKED`、Data=`BLOCKED`、combined G2=`BLOCKED`；G3-G4=`NOT_VERIFIED`；G5=`NOT_AUTHORIZED`。LSR-04 未启动且禁止启动；5432 边界事故及早期失败/修订均保留为 superseded historical snapshots。

## LSR-03 当前 fresh isolated runtime / G2 Gate manifest（2026-08-25）

| field | value |
| --- | --- |
| current status | `PARTIAL/[ ]`; implementation/fixture revisions independently reviewed; current fresh Verifier=`PASS`; independent G2 Gate=`BLOCKED` |
| reached | 58 no-DB tests; fresh guard; `001→026`; 026 idempotent replay; seed/introspection; active/paused/retained/019/idempotent; 5 DB negative fixtures; logical rollback; three actual inbound zero-mutation paths; pre-026 schema restore |
| evidence/boundary | `/Users/limengyang/.codex/attachments/lsr03-g2-fresh-final-evidence-20260825-bootstrap-fixture-admin-cwd/`; SHA256SUMS 42 items PASS; 55432 stopped/no listener; no 5432 query; root worktree unchanged; no production/commit/push/deploy |
| open evidence | complete target parity/visibility/orphan/ReviewRecord assertions; actual `retained_public_only`; rollback replay/deletion-order/audit-digest proof; backup restore with synthetic source data |
| Gate | G2 Database=`BLOCKED`, Data=`BLOCKED`, combined=`BLOCKED`; LSR-03 remains `[ ]`; LSR-04 not started/prohibited |

### LSR-03 R9 runtime manifest（historical, superseded by current final G2 attempt）

| field | value |
| --- | --- |
| task/status | `LSR-03 runtime` / `PASS` / checkbox `[x]`; Final Reviewer=`PASS`, Independent Verifier R9=`PASS`; this does not equal G2; G2 Database=`BLOCKED`, Data=`FAIL`, combined=`FAIL`; LSR-04 prohibited |
| isolated identity | R9 fresh `lsr03_r9` at `127.0.0.1:55432`, explicit `postgresql+asyncpg://` URL; guarded runner/child used private `backend/.venv`, with non-recovery identity and no 5432/default DB |
| verified result | guarded `001→026` replay plus identical idempotent replay; deterministic seed; CaptureItem, Attempt, MistakeDraft.`attempt_id` each returned exact `SNAPSHOT_RESTORE_REQUIRED`; full ledger/relation/audit-event/attachment before-after unchanged and each cleanup=0 |
| superseded history | r2-r8 setup/runtime failures and revisions, including the 5432 boundary incident, remain retained historical evidence and are superseded by the R9 manifest; they do not negate the current R9 result |
| stable evidence | `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r9-verifier/`; R9 evidence and SHA manifest are distinct from and do not overwrite r2-r8 |
| historical evidence | `/tmp/lsr03-tdd-red.PYec4J/`, `/tmp/lsr03-final-*`, the earlier code-hash tables and r1 are superseded snapshots; they are not the current manifest and cannot promote this task |
| cleanup | stable r2 `fixture-cleanup.log` reports zero scoped rows and `cluster-stop.log` records shutdown; current no-listener check is performed separately; dirty worktree preserved; no commit/push/deploy |
| closure | R9 fresh evidence closes the previously missing actual-table path; no further LSR-03 rerun is implied. G2 is `FAIL` (Database=`BLOCKED`, Data=`FAIL`); LSR-04 remains prohibited. |

### LSR-03 重开前静态预检 manifest（2026-08-25，定向修订）

| field | value |
| --- | --- |
| scope/status | `PASS` / 仅无数据库源码与合同预检；R4 后独立 `lsr03_reviewer`=`REVIEW: PASS`、`lsr03_verifier`=`VERIFY: PASS`（静态修订）；不改变 LSR-03=`FAIL/[ ]`、Reviewer=`FAIL`、Verifier=`PARTIAL`、G2=`NOT_VERIFIED` |
| r2 inputs | `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r2/actual-inbound-fixture-status.md` SHA-256=`0d1a21fd1394535df60e655c4fbd01c9d9b4d3e171896d089a9e22ec91ffee39`; r2 `SHA256SUMS` read and retained as historical prior-run manifest; it does not cover this revision |
| static findings | 026 guard checks all three actual inbound edges and raises `SNAPSHOT_RESTORE_REQUIRED`; current helper setup uses `target_mistake_draft_item_id`, while MistakeDraft link checks use `target_mistake_draft_id`; full ledger/inbound/attachment/audit-event snapshots are compared |
| changes | `backend/tests/lsr03_rollback_rehearsal.py` now keeps baseline/setup/zero-mutation/cleanup on admin session, invokes rollback only through adapter-runner, checks explicit URL + read-only identity probe, and emits admin/adapter identity plus cleanup evidence; added structural/logic checks in `backend/tests/test_lsr03_rollback_static_contract.py`; no product/model/migration/adapter change |
| current hashes | rollback helper=`4c1343df4ee1cb85cc7a2ef939218b3db24a859412030cc18458a6a3d6fe5d6b`; static contract=`8954ec8488a95cc3f87d814e3380628dc9701cb6b661be6fb40a5fd80bb70614`; guarded runner=`0867324951d2a9489aee962746dd09339981910d376f7fa3f3bd1f5086aa4965`; guarded runner test=`237f64773ee21ae4cd0e17b8f7771b956722d6f89104222501b54125fb00bdb0`; 026=`0544f29060b0ca2f0fed8b4ced87c57cd3ccb7097dd44673e0608a2aca61e1cd`; adapter=`6ea489a98f64ba1f5e69d776c063e2a43f7d83a129ef91ace4e5d6d5a68b4bd4` |
| no-DB verification | `backend/.venv` `py_compile` PASS; static+guarded tests `24 passed`; no database-capable test, DB, service, or Alembic execution; fresh rehearsal remains blocked pending independent review |
| readiness | historical R4 readiness only; superseded by R9 Final Reviewer=`PASS` and Independent Verifier=`PASS`; G2 remains `NOT_VERIFIED` |

### LSR-03 r3 runtime recheck manifest (2026-08-25)

| field | value |
| --- | --- |
| runtime/status | `FAIL` / stopped after first runtime failure; LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED` |
| target | fresh `lsr03_r3` cluster, explicit `127.0.0.1:55432`; cluster stopped, no listener remains; no 5432/default DB connection |
| first failure | `backend/tests/lsr03_guarded_runner.py` import raised `ModuleNotFoundError: No module named 'sqlalchemy'`; URL parsing, identity probe, Alembic, SQL, paused baseline and all three actual-table inbound paths were not reached |
| stop rule | no repair, no retry, no migration/SQL/pytest execution after the first failure; rollback/zero-mutation/cleanup result is `NOT_RUN`, not PASS |
| evidence | `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r3/`; includes first-error log, runtime status, explicit cluster start/stop logs and `SHA256SUMS`; r2 remains untouched |
| next condition | resolve the missing runtime dependency through a separately reviewed action, then obtain fresh authorization if needed; any future run must use a new manifest and repeat all gates; this r3 failure does not self-approve LSR-03/G2 |

### LSR-03 r3 首错后的无数据库 runtime-contract 修订（2026-08-25）

| field | value |
| --- | --- |
| history/boundary | r3 首错与 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r3/` 保留且不覆盖；r2 保持不变；r4 未启动；未连接 DB、未启动服务、未执行 Alembic |
| guarded runtime contract | SQLAlchemy 改为延迟导入；probe/DB 动作前要求 `sys.prefix` 与项目 `backend/.venv` 一致；错误解释器固定 `LSR03_PYTHON_RUNTIME_REQUIRED`/exit 64；child 固定 `backend/.venv/bin/python`、`-m pytest`（unit）、`PYTHONPATH=.`、cwd=`backend` |
| no-DB changes | 仅 `backend/tests/lsr03_guarded_runner.py`、`backend/tests/test_lsr03_guarded_runner.py`；新增错误解释器 fail-before-probe/child 与正确私有 venv identity 覆盖；无产品/模型/迁移/adapter 修改 |
| current hashes | guarded runner=`20cb6ba76d1046b05cc0d5e994a62e49dae4f212f954748cc7fa1625829ed101`; guarded runner test=`46da9209df1ad194afc6cfb2238da84c92a0fff2807d0264a3de44b214bd4c00`; rollback helper=`4e479caa3e25f48440f322c3a5531bfbe33da89665facb939e9be20e2b26ee83`; static contract=`fdd6566a71ae4932ba5204059ea3c6a4ec3a197c4e801effd6a9a305971ac92f` |
| verification | `PYTHONPATH=. ../backend/.venv/bin/python -m pytest -q tests/test_lsr03_guarded_runner.py tests/test_lsr03_rollback_static_contract.py` from `backend`: `20 passed`; project-venv `py_compile=PASS`; `git diff --check=PASS` |
| readiness | `READY_FOR_R4=YES` only for a future fresh isolated runtime recheck; LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED`; no runtime approval is implied |

### LSR-03 R4 fresh isolated runtime manifest（2026-08-25）

| field | value |
| --- | --- |
| runtime/status | `FAIL` / stopped after first actual-table fixture failure; LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED` |
| identity/scope | fresh `lsr03_r4`, `127.0.0.1:55432`, explicit `LSR03_DATABASE_URL`=`DATABASE_URL`; runner and child used `/Users/limengyang/2025-blog-public/backend/.venv/bin/python`, cwd=`backend`, `PYTHONPATH=.`; no 5432/localhost/default DB |
| reached | guarded identity probe; guarded Alembic `001→026`; guarded paused seed/setup; guarded adapter paused baseline (`migrated_paused`) |
| first failure | `backend/tests/lsr03_rollback_rehearsal.py:_audit_event_snapshot` executed `SELECT * FROM public.legacy_migration_rollback_audits WHERE ledger_id=:id ORDER BY id`; PostgreSQL raised `UndefinedColumnError: column "id" does not exist` |
| not reached | capture-item, Attempt, MistakeDraft.`attempt_id` actual-table setup; rollback calls; exact `SNAPSHOT_RESTORE_REQUIRED`; full ledger/audit/event/relation/attachment zero-mutation; attachment rejection retention; fixture cleanup |
| stop/cleanup | no repair/retry; cluster stopped after first failure; `127.0.0.1:55432` listener-after=`NONE`; fixture cleanup=`NOT_RUN` because setup was not reached |
| evidence | `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r4/`; includes first-error log, runtime status, start/stop/listener logs, and code/evidence `SHA256SUMS`; r2/r3 untouched |
| code hashes | guarded runner=`20cb6ba76d1046b05cc0d5e994a62e49dae4f212f954748cc7fa1625829ed101`; rollback helper=`4e479caa3e25f48440f322c3a5531bfbe33da89665facb939e9be20e2b26ee83`; 026=`0544f29060b0ca2f0fed8b4ced87c57cd3ccb7097dd44673e0608a2aca61e1cd`; adapter=`6ea489a98f64ba1f5e69d776c063e2a43f7d83a129ef91ace4e5d6d5a68b4bd4` |
| conclusion | R4 runtime=`FAIL`; no actual-table rollback or zero-mutation evidence; no LSR-03/G2 approval is implied |

### LSR-03 R4 首错后的无数据库修订 manifest（2026-08-25）

| field | value |
| --- | --- |
| root cause | 026 DDL declares `public.legacy_migration_rollback_audits.ledger_id` as the primary key; helper previously used `ORDER BY id` |
| change | helper now uses `ORDER BY ledger_id`; structural test parses 026 DDL primary key and rejects rollback-audit SQL containing `ORDER BY id` |
| files/hashes | `backend/tests/lsr03_rollback_rehearsal.py`=`85f5507d1ee3061c8a147340cd47f1d505d0b98401775730c41640837c53b33f`; `backend/tests/test_lsr03_rollback_static_contract.py`=`c13dacf170454658974c99dd0c78a593002c97ce67c26997c2956a6a62d5aa4b` |
| verification | `PYTHONPATH=. ../backend/.venv/bin/python -m pytest -q tests/test_lsr03_guarded_runner.py tests/test_lsr03_rollback_static_contract.py` from `backend`: `21 passed`; project-venv `py_compile=PASS`; `diff-check=PASS` |
| boundaries | no DB, service, Alembic, r5, product/migration/adapter change; r4 evidence remains historical and untouched |
| readiness | `READY_FOR_R5=YES`; R4 后独立 Reviewer/Verifier 均为 `PASS`（静态修订）；LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED` |

### LSR-03 R5 fresh isolated runtime manifest（2026-08-25）

| field | value |
| --- | --- |
| runtime/status | `FAIL` / stopped after first zero-mutation assertion failure; LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED` |
| identity/scope | fresh `lsr03_r5`, `127.0.0.1:55432`, explicit `LSR03_DATABASE_URL`=`DATABASE_URL`; runner/child used `/Users/limengyang/2025-blog-public/backend/.venv/bin/python`, cwd=`backend`, `PYTHONPATH=.`; no 5432/localhost/default DB |
| reached | guarded identity probe; guarded Alembic `001→026`; guarded paused seed/setup; guarded adapter paused baseline; capture setup; capture rollback attempt; first zero-mutation assertion |
| first failure | `_assert_zero_mutation` compared the partial baseline selected by `run_inbound_fixtures` with `_ledger_snapshot` `SELECT *`; capture reported ledger columns as changed before completing verification |
| not reached | Attempt fixture; MistakeDraft.`attempt_id` fixture; complete exact `SNAPSHOT_RESTORE_REQUIRED` check; full ledger/audit/event/relation/attachment zero-mutation; attachment retention; cleanup |
| stop/cleanup | no repair/retry; cluster stopped after first failure; listener-after=`NONE` on `127.0.0.1:55432`; fixture cleanup=`NOT_RUN` because failure occurred during capture assertion |
| evidence | `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r5/`; includes first-error log, runtime status, cleanup status, start/stop/listener logs, and code/evidence `SHA256SUMS`; r2/r3/r4 untouched |
| conclusion | R5 runtime=`FAIL`; no complete actual-table rollback/zero-mutation evidence; no LSR-03/G2 approval is implied |

### LSR-03 R5 首错后的无数据库修订 manifest（2026-08-25）

| field | value |
| --- | --- |
| root cause | baseline was a partial mapping selected from `legacy_note_migrations`, while after used `_ledger_snapshot` `SELECT *` |
| change | locate only the paused ledger `id`, then set `baseline = await _ledger_snapshot(admin, baseline_id)`; zero-mutation after continues to call the same helper |
| structural contract | no-DB test proves baseline and after use `_ledger_snapshot` and forbids partial mapping row as baseline |
| files/hashes | `backend/tests/lsr03_rollback_rehearsal.py`=`4c1343df4ee1cb85cc7a2ef939218b3db24a859412030cc18458a6a3d6fe5d6b`; `backend/tests/test_lsr03_rollback_static_contract.py`=`8954ec8488a95cc3f87d814e3380628dc9701cb6b661be6fb40a5fd80bb70614` |
| verification | `PYTHONPATH=. ../backend/.venv/bin/python -m pytest -q tests/test_lsr03_guarded_runner.py tests/test_lsr03_rollback_static_contract.py` from `backend`: `22 passed`; project-venv `py_compile=PASS`; `diff-check=PASS` |
| boundaries | no DB, service, Alembic, r6, product/migration/adapter change; r5 evidence remains historical and untouched |
| readiness | `READY_FOR_R6=YES`; R5 后独立 Reviewer/Verifier 均为 `PASS`（静态修订）；LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED` |

### LSR-03 R6 fresh isolated runtime manifest（2026-08-25）

| field | value |
| --- | --- |
| runtime/status | `SUCCESS` for the three actual-table inbound rollback rehearsals; LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED`; no self-approval |
| identity/scope | fresh `lsr03_r6`, explicit `LSR03_DATABASE_URL`=`DATABASE_URL`, guard/admin/adapter all bound to `lsr03_r6` at `127.0.0.1:55432`; runner/child used backend `.venv`, cwd=`backend`, `PYTHONPATH=.`; no 5432/localhost/default DB |
| baseline | guarded 001→026 and paused baseline `state=migrated_paused`; complete baseline snapshot obtained through `_ledger_snapshot` |
| actual inbound results | CaptureItem=`SNAPSHOT_RESTORE_REQUIRED`, Attempt=`SNAPSHOT_RESTORE_REQUIRED`, MistakeDraft.`attempt_id`=`SNAPSHOT_RESTORE_REQUIRED`; exact code for each=`LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED` |
| zero mutation | each result: `ledger_unchanged=true`, `audit_event_unchanged=true`, `inbound_reference_retained=true`; capture attachment retained during rejection; all fixture cleanup counts=`0` |
| cleanup/stop | cleanup status records capture/attempt/mistake_draft_attempt_id=`cleanup_zero=true`; cluster stopped after success; listener-after=`NONE` on `127.0.0.1:55432` |
| evidence | `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r6/`; includes actual result JSON, exact error-code file, cleanup/status, start/stop/listener logs and code/evidence `SHA256SUMS`; r2-r5 untouched |
| conclusion | R6 runtime evidence complete for these three synthetic actual-table rejection paths; independent runtime Reviewer/Verifier still required; no LSR-03/G2 approval is implied |

### LSR-03 R7 首错后的无数据库 scheme 修订 manifest（2026-08-25）

| field | value |
| --- | --- |
| root cause | R7 accepted plain `postgresql://`; Alembic uses `settings.DATABASE_URL` and attempted the unavailable psycopg2 driver, while the isolated contract uses asyncpg |
| change | guarded runner now accepts only `postgresql+asyncpg://`; plain scheme fails before probe/child with `LSR03_DATABASE_URL_ASYNCPG_SCHEME_REQUIRED` and exit 64 |
| no-DB contract | venv test proves `asyncpg` is available and `psycopg2` is absent; plain scheme fail-before-probe/child; correct asyncpg URL remains accepted |
| current hashes | guarded runner=`0867324951d2a9489aee962746dd09339981910d376f7fa3f3bd1f5086aa4965`; guarded runner test=`237f64773ee21ae4cd0e17b8f7771b956722d6f89104222501b54125fb00bdb0`; rollback helper=`4c1343df4ee1cb85cc7a2ef939218b3db24a859412030cc18458a6a3d6fe5d6b`; static contract=`8954ec8488a95cc3f87d814e3380628dc9701cb6b661be6fb40a5fd80bb70614` |
| verification | `PYTHONPATH=. ../backend/.venv/bin/python -m pytest -q tests/test_lsr03_guarded_runner.py tests/test_lsr03_rollback_static_contract.py` from `backend`: `24 passed`; project-venv `py_compile=PASS`; `diff-check=PASS` |
| boundaries/readiness | no DB, service, Alembic, r8, product/migration/adapter change; R7 first-error evidence remains historical; R7 后独立 Reviewer/Verifier 均为 `PASS`（静态修订）；`READY_FOR_R8=YES`；LSR-03 remains `FAIL/[ ]`; G2 remains `NOT_VERIFIED` |

### LSR-03 boundary incident（历史）与最终独立结果

- Incident: Verifier supplied `LSR03_DATABASE_URL`, while Alembic reads `DATABASE_URL`; Alembic therefore connected to default `localhost:5432` and attempted `025→026`. The attempt failed on missing `CREATEROLE`; Verifier reports the transaction did not commit. No follow-up connection to 5432 was made by the primary agent. This is still an explicit scope violation and satisfies the task pause condition `误触日常库`.
- Historical pre-restart Reviewer/Verifier: `CHANGES_REQUIRED` / `FAIL`; those findings prompted the guarded restart and are superseded by the final r2 review.
- Final r2 Reviewer/Verifier: `FAIL` / `PARTIAL`. The decisive open path is actual-table inbound rollback, not the already-closed historical digest/five-way/nonce findings. TEMP predicate evidence cannot substitute for governed rollback against the real tables.
- Cleanup: primary agent stopped `/tmp/lsr03-tdd-red.PYec4J/data` on port 55432 with `pg_ctl ... stop -m fast`; no listener remains. Evidence directory is retained for audit. LSR-04 is not authorized to start from this result.

### Authorized read-only incident audit and restart condition

- User authorized one read-only audit of `localhost:5432`. Auditor forced `transaction_read_only=on`, verified `blog_v2`, `blog_user`, `127.0.0.1:5432`, and found Alembic `025` with no persistent 026/legacy schema, tables, functions, triggers, roles or related active sessions. The transaction was rolled back and disconnected; no further 5432 access is authorized.
- Evidence: `/tmp/lsr03-incident-audit.i6qoKD`; raw output SHA-256 `7b55e7e65b2f853ec222638248345f7aee394e672985d150ad14c32c9b1b23fc`. Limitation: current catalog absence cannot prove historical absence of any uncovered change.
- Restart condition: every Alembic/test/SQL command must pass through a task-specific fail-closed runner that requires an explicit dedicated URL, rejects missing or conflicting environment variables, and verifies exact `127.0.0.1:55432`, database name prefix `lsr03_`, non-recovery identity before any operation. Direct Alembic invocation is forbidden for the resumed rehearsal.

本轮 final code manifest（当前源码/测试/helper）：026=`sha256:92a9ca83c81210bfc7ac4e1333d170b23b0f1a0f9e5ec32ec32d3a03be904347`；adapter=`sha256:067cf7da79af23245e96931ecd69aefd26da82a6aff6a8ca70a77c51fd2a6b9b`；contract test=`sha256:99e28b07b89a0f37f5bd8bfac736bed9bb7066e8ab6a0e758e339cfa0ada9641`；adapter test=`sha256:c410d673dda795a1dd04115d3f746894a662488a80838f89450a819cd68b6da8`；validation helper=`sha256:162b229dd13cf1fcadfb772419c41d4121546cac3e778b59ee8e2fc0418cc6a6`。历史首个失败证据：`reviewer-red-ledger.log`、`reviewer-red-adapter.log`；最终日志不覆盖历史失败文件。

最终状态为 `FAIL`：Owner-side isolated evidence 仅证明局部路径；独立 Reviewer/Verifier 已重审并确认 active/retained、chapters/019、Capture/Attempt inbound negative、完整 duplicate/collision、真实五方 manifest、pre-migration restore 与 ACL 仍未闭环，且发生默认 5432 边界事故。G2 保持 `NOT_VERIFIED`。

### LSR-03 historical TASK_BLOCK details (superseded after explicit reauthorization)

- Block Type: `TASK_BLOCK`; Severity: `HIGH`.
- Problem: current source contains no executable `legacy_note_migrations` schema/table, canonicalizer, adapter, transition functions, ACL roles, or migration tests; LSR-02 calls them `NOT_IMPLEMENTED`.
- Evidence: the zero-hit implementation search and isolated catalog output above; baseline Alembic only reaches current head `025`.
- Impact: only the current app schema can be replayed. No safe way exists to load the frozen 8.10 temporary snapshot/manifest, synthesize Note→Question/Mistake/ReviewItem rows, or prove rollback and G2 invariants.
- Required Action: separately authorize and implement the frozen contract in non-production Alembic/app/test scope, then restart LSR-03 with a fresh isolated cluster and independent Reviewer/Verifier.
- Recheck Condition: implementation and fixtures are present; the same identity-bound replay produces non-empty count/hash/FK/visibility/version, idempotency, rollback/restore, and ACL-negative evidence with zero unexplained rows.

本账本是本工作流唯一的阶段 manifest 容器。它不会把历史 workflow 的结论转换为当前结论，也不会把文档骨架当成迁移、切换、删除或生产就绪证据。

## LSR-00 骨架验证（本次实际完成）

结论：`PASS`（仅指文档骨架范围）。

- 已先运行 `git status --short`；工作树存在大量用户修改和未跟踪文件，已保留，未覆盖、暂存、提交或格式化。
- 已读取 `AGENTS.md`、`agents/orchestration.md`、`agents/permissions.md`、`agents/gates.md`、`agents/task-template.md`、`agents/report-template.md` 和 `agents/workers/principal-software-architect.md`。
- 已读取用户粘贴目标文件，以及 route ownership、editor convergence、frontend foundation、route cutover、i10/i11/i12、i-series completion、personal-learning-system-v2-unification 的 README/design/requirements/tasks/validation 相关输入。
- 写入范围仅为本目录五个文件；写入前确认 `docs/workflows/legacy-system-retirement/` 不存在。没有创建 `audit.md`、`assets/` 或其它文件。
- 已冻结四阶段串行合同、LSR-00 已勾选、LSR-01 为唯一下一项、其余任务未勾选、G0-G5 独立对账、隔离 PostgreSQL/真实 Chromium、Note/Blog/公开内容保留、`admin_session` 合同和生产/部署/commit/push 禁止边界。

## Reviewer findings、修复与最终独立结论（仅 LSR-00 骨架）

以下 `PASS_WITH_NOTES` 是 LSR-00 历史骨架闭环结论，仅适用于五文件的流程骨架、角色矩阵和链接完整性；不得与当前 LSR-01 的独立 Reviewer=`PASS_WITH_NOTES`、QA=`PASS`、Data=`PASS` 混淆。其后关于 LSR-01=`PARTIAL`/`[ ]` 的文字均为历史快照；当前 LSR-01 状态以本文件顶部 canonical status 和文末收束记录为准，为静态 mapping 范围内 `PASS`、`[x]`。

独立 Reviewer 在五轮审查中先后给出 `CHANGES_REQUIRED`，Owner 按 findings 定向修订且 Reviewer 未参与修改。LSR-00 最终复审结论为 `PASS_WITH_NOTES`：五文件骨架没有剩余 actionable finding；残余风险是后续每个 task-local `worker_id` 仍须绑定真实独立子代理，并重新产生当前源码、数据库、运行时和浏览器证据。本历史骨架结论不把任何业务 Gate 或 LSR-01 改为 `PASS`。

- 角色已统一为仓库 `agents/workers/` 中的精确 Persona 显示名；复合 Reviewer/Verifier 已明确为多个真实独立 Worker。
- 已同步授权合同：LSR-01 及既定非生产任务预先获执行授权；Gate 仍须当前独立验证；生产数据库/服务、真实凭据或用户数据、公开路由生产切换、不可逆操作、部署、commit/push 保持 `NOT_AUTHORIZED`。
- 任务进度改为仅使用 `[x]`/`[ ]`；每项补齐 `depends_on`，移除不存在的中间编号，冻结完整串行链；LSR-01 先只读、结论 `NOT_VERIFIED`，再独立对账 G0/G1。
- LSR-20～23 已逐条登记阶段三八条链路及原始证据路径/hash 要求；阶段四入口改为 G0-G3 `PASS`，适用时 G4 `PASS`，无生产范围时 G5 `NOT_AUTHORIZED`。
- 已统一五文件仓库边界：脚本、harness、原始输出、隔离附件仅在任务专属仓库外临时目录；仓库只登记路径/hash/首次失败/清理；持久化脚本或测试须先扩展精确任务写入范围。

第二轮独立复审仍要求修改；本轮已修正 LSR-03/LSR-04 的 Gate 依赖循环、阶段四入口和 G2 当前状态，Reviewer 状态继续保持 `NOT_VERIFIED`，等待下一轮复审。

第三轮独立复审聚焦高风险 Owner/Gate 自审重叠；本轮已为全量任务补充 task-local Gate Worker，并逐项写明排除 Primary Owner。LSR-03/23/31 改由 Senior Data Engineer 执行、Database Architect 对账 G2；LSR-06 的 G1 由不参与实施的 Principal Software Architect 对账；LSR-13 的 G4 由 Senior AI / LLM Engineer 对账；LSR-15 的 G4 由 Senior Recommendation Engineer 对账；LSR-22 改由 Senior Backend Engineer 执行、Senior Security Engineer 对账 G3；LSR-34 的 G1 由 Principal Software Architect 对账。Reviewer 状态仍为 `NOT_VERIFIED`，未改为 `PASS`。

第五轮复审的唯一 P2 已修复：LSR-21 仅覆盖认证/公开私有融合，role matrix 与触发 Gates 统一为 G3/G5，移除不适用的 G4；LSR-00 最终 Reviewer 复核确认无 actionable finding，结论为 `PASS_WITH_NOTES`，仅限骨架。

本轮角色 identity 修订：每个任务已增加唯一 `worker_id_prefix` 派生的 role matrix；同一 Persona 的 Owner/Verifier/Gate 也使用不同 worker_id。机械检查规则为：每个 `### LSR-*` 必须有一行 `role matrix`；`owner`、所有 `reviewer`、`verifier`、触发 Gate 的全部 worker_id 必须非空且互不重复；owner worker_id 不得出现在其它集合；每个 Gate 必须展开 design.md 规定的完整 Persona 组合；不同任务的 worker_id 不得复用。实际执行时必须将这些 id 绑定不同真实子代理，主代理只编排/汇总/对账；当前没有执行 Worker identity 证据，因此相关 manifest 仍为 `NOT_VERIFIED`。

独立 Senior QA / SDET Verifier 结论为 `PASS`（仅限工作流文档合同）：确认目录恰好包含五个文件，14 个 Markdown 链接均存在，23 项任务/依赖/role matrix 完整，仅 LSR-00 勾选，worker_id 唯一且角色互斥，各 Gate 组合完整，限定 whitespace 检查无错误，staged paths 为空。Verifier 未运行产品测试、数据库、服务或 Chromium；因缺少任务开始前的独立 Git 基线，只能确认当前目标目录未与其它 dirty 路径重叠，不能反推所有历史 dirty 文件的归属。

### LSR-00 manifest

| 字段 | 值 |
| --- | --- |
| task_id | LSR-00 |
| owner/reviewer/verifier | `lsr00-owner` Principal Software Architect / `lsr00-reviewer` Principal Technical Reviewer / `lsr00-verifier` Senior QA / SDET（真实独立子代理） |
| source | AGENTS、治理文件、粘贴目标、既有 workflow 输入 |
| target | `docs/workflows/legacy-system-retirement/` 五文件 |
| source/DB/runtime mutation | none；未连接 DB、未启动服务、未运行 Chromium |
| status | `PASS`（骨架范围） |
| next | LSR-01；depends_on=LSR-00；依赖满足后的第一项 |
| independent conclusions | Reviewer `PASS_WITH_NOTES`；Verifier `PASS`；仅覆盖五文件合同与仓库边界 |
| evidence | 本文件、`git status --short`、staged-path 空检查、23 项依赖/角色矩阵检查、14 个链接目标检查、五文件限定 whitespace 检查 |

## 当前 Gate 对账（不继承历史状态）

| Gate | 当前状态 | 当前依据 | 可进入的下一步 |
| --- | --- | --- | --- |
| G0 | `PASS` | 用户三项合同已书面化并消除残余矛盾；`lsr01-g0-product` 与 `lsr01-g0-domain` 最终独立复核均为 `PASS` | 允许执行 G1；不代表实现、数据库、权限或 LSR-02 已通过 |
| G1 | `PASS` | 最终机械合同已冻结；`lsr01-g1-architect=PASS`、`lsr01-g1-reviewer=PASS_WITH_NOTES` | 仅允许完成 LSR-01 并进入 LSR-02 合同设计；实现、G2/G3/G4 不继承 |
| G2 | `BLOCKED` | Database=`BLOCKED`、Data=`BLOCKED`、combined=`BLOCKED`。当前 fresh runtime Verifier=`PASS`，但 target parity/retained/visibility/orphan/ReviewRecord、rollback replay/audit digest 与带数据 restore 证据不足；LSR-03=`PARTIAL/[ ]` | LSR-04 禁止启动；必须先在 LSR-03 补齐针对性 fixture/断言并重新独立对账 |
| G3 | `NOT_VERIFIED` | `admin_session`/`AdminSession`/`get_current_admin` 只被冻结为边界，未执行负向验收 | 需独立 Security/QA 证据 |
| G4 | `NOT_VERIFIED` | Capture/Review/AI 来源链仅定义合同，未做当前评估 | 依赖满足后由 Senior Recommendation Engineer + Senior AI / LLM Engineer 独立验证 |
| G5 | `NOT_AUTHORIZED` | 本次无生产范围；生产数据库/服务、真实凭据或用户数据、公开路由生产切换、不可逆操作、部署、commit/push 均禁止 | 任何生产意图必须取得新的明确授权并重新建 Gate 证据 |

## 阶段 manifest 状态

| 阶段 | 权威 manifest 位置 | 状态 | 进入条件 | 当前阻塞 |
| --- | --- | --- | --- | --- |
| 一：迁移/退休 | 本文件“阶段一 manifest”区（含 LSR-01/02 当前 manifest） | `BLOCKED` | LSR-01→06 串行；LSR-03 当前为 `PARTIAL/[ ]`；LSR-04 生成 G3/适用 G4 后独立对账，LSR-05/06 才依赖相应 Gate | LSR-01/02 静态范围已 `PASS`；LSR-03 runtime PASS 但完整 G2 证据不足；G2 Database/Data/combined=`BLOCKED`；LSR-04 禁止启动 |
| 二：七体系 | 本文件“阶段二 manifest”区（尚未执行） | `NOT_VERIFIED` | 阶段一完成且 G0-G3 PASS | 未开始 |
| 三：融合 | 本文件“阶段三 manifest”区（尚未执行） | `NOT_VERIFIED` | 阶段二七项逐项 PASS | 未开始 |
| 四：收束 | 本文件“阶段四 manifest”区（尚未执行） | `NOT_VERIFIED` | 融合独立审查通过 | 未开始 |

## 阶段一 manifest（占位，不是结果）

LSR-01 已产生静态 mapping 范围内 `PASS` 只读 manifest；LSR-02 已产生静态迁移合同范围内 `PASS` manifest。LSR-03 当前 fresh isolated runtime 为 `PASS`，但任务状态为 `PARTIAL/[ ]`，因为完整 G2 数据等价、rollback replay 与带数据 restore 证据尚未闭合。G2 独立对账为 `BLOCKED`；LSR-04、LSR-05、LSR-06 仍未启动且 LSR-04 禁止启动。不得用 i10/i11/i12、R9 或其它历史 `/tmp` 快照替代当前权威证据目录。

## 阶段二 manifest（占位，不是结果）

Subject/KnowledgePoint、Question、Mistake、Review、Note、Capture、学习首页七项均为 `NOT_VERIFIED`；没有任何一项可批量继承 personal-learning-system-v2-unification 或其它 workflow 的历史状态。

## 阶段三 manifest（占位，不是结果）

隔离 PostgreSQL、生产 frontend build、真实 FastAPI、真实 Chromium、E2E 数据链、权限负向、SQL 完整性、旧请求零命中、console/page error/failed request/secret scan 均为 `NOT_VERIFIED`；本次没有启动服务或浏览器。

## 阶段四 manifest（占位，不是结果）

旧残留搜索、Alembic graph/replay/recovery、pytest/Vitest/typecheck/build、auth/visibility/secret/port/process/worktree 清理、独立报告和最终 Gate 均为 `NOT_VERIFIED`；本次没有删除任何数据或资源。

## 证据政策与后续更新规则

每阶段只保留本文件一份 manifest、必要的首次原始失败证据和一份最终汇总；脚本、harness、原始输出、隔离附件只位于任务专属仓库外临时目录，仓库登记精简摘要、路径、hash、首次失败和清理结果。若脚本或测试需持久化进仓库，必须先在精确任务范围扩展写入授权，不得偷跑。不得为正常重试复制整套日志，不得新增本目录五文件之外的 workflow artifact。每个任务完成后立即更新 checkbox、当前证据、Reviewer/Verifier、Gate 对账和清理结果；任何 UNKNOWN、不一致、失败或未授权均保持 fail closed。

## 本次限定验证命令

本次重开前预检只执行：本目录五文件的 `rg`/Markdown 链接目标存在性检查、限定路径 `git diff --check`、`git status --short`、限定路径 diff、Python 语法编译和不读取环境数据库 URL 的五项源码合同检查。未运行产品 pytest（环境无 pytest 且 DB-capable tests 禁止运行）、build、服务、数据库、浏览器或 Git 写操作。

## LSR-01 当前源码/迁移/消费者盘点 manifest（2026-08-23）

结论：`PASS`；`LSR-01` checkbox 为 `[x]`，仅限静态 mapping 验收范围。只读覆盖了当前模型、schema、service、router/注册、Alembic 文件图、前端 client/hook/page/navigation、测试、静态文件和导出/导入线索；没有数据库内容、隔离快照或运行时证据，因此不代表完成迁移、切换、删除或允许后续 runtime Gate。

### 执行边界与可重算证据（历史快照，已被最终结论取代）

| 字段 | 值 |
| --- | --- |
| task_id / worker_id | `LSR-01` / `lsr01-owner`（Primary Owner，Principal Software Architect） |
| reviewer / verifier | `lsr01-reviewer`（Principal Technical Reviewer）；`lsr01-verifier-qa`（Senior QA / SDET）；`lsr01-verifier-data`（Senior Data Engineer）；本轮未执行独立 Reviewer/Verifier 对账 |
| source identity | 当前工作树 `/Users/limengyang/2025-blog-public`；当前源码与测试优先，历史 workflow 仅作线索 |
| target identity | 仅本文件与 `tasks.md`；未改产品代码、测试、迁移、路由或运行时 |
| commands | `git status --short`；`rg --files`/`rg -n`；`sed`；`find`；Python3 AST import 计数；Python3 Alembic revision-header 读取；均只读 |
| runtime/DB | 未启动服务、测试、build、浏览器；未连接或查询日常/生产/隔离 PostgreSQL；数据库内容状态 `NOT_AUTHORIZED`/未执行 |
| dirty boundary | 起始已有 `AGENTS.md`、auth、package、多个 `src/` 文件及大量未跟踪 workflow/测试/PoC；均保留，未暂存/提交/push |
| graph result | 文件图单一 head 为 `025`；`003` 的 `down_revision` 为 `1119bee5a419`，该 revision 再接 `0ec85724afb9`→`002`，不是按文件名排序即可推断 |
| cleanup | 仅生成的 `/tmp/lsr01-backend-files.txt`、`/tmp/lsr01-frontend-files.txt` 为只读临时索引，盘点结束后删除；无仓库外持久化 artifact/hash |

### 新版对象与支持对象映射

以下 disposition 只使用合同允许的 `迁移/保留/替换/删除/未知`；`删除` 从未表示本轮执行删除。字段来自当前 `backend/app/models/*` 与对应 `backend/app/schemas/*`，表/约束/index 来自模型 metadata 与列出的 Alembic revision 文件。

| 对象 | 当前模型/schema 字段与持久化约束 | 当前 API/service/消费者 | 表、revision、disposition |
| --- | --- | --- | --- |
| `DraftItem` | `id` UUID、`draft_type`、`source_type/source_id`、`status`、`version`、`validation_errors`、`target_type/target_id`、`created_by`、时间；类型/来源/状态/转换目标/version checks；`status+updated_at`、`draft_type+status` indexes | `draft_service.py`；`drafts.py` `/api/admin/drafts`；`mistake_service.py`、`capture_service.py`、`attachment_service.py`、`question_service.py`；前端 `src/lib/api/drafts.ts` 与 manage drafts/capture | `draft_items`；012 创建，013 扩展 `draft_type/source/target`，020/021 间接使用；`保留` |
| `QuestionDraft` | `id`、唯一 `draft_item_id`、`subject_id`、`title`、`question_text`、`question_type`、`options`、`correct_answer`、`explanation`、`difficulty`、时间；subject RESTRICT、类型/难度 checks、subject index | `question.py` model/schema；`draft_service.py`；`drafts.py` list/create/get/update/reject/convert；capture、mistake staged、AI validator；manage drafts and capture components | `question_drafts`；012 创建；`保留` |
| `Question` | UUID `id`、`subject_id`、`title`、`stem_md/question_text`、`question_type`、`options`、`answer_data/correct_answer`、`analysis_md/explanation`、`difficulty`、`status`、固定 `visibility=private`、`version`、时间；subject RESTRICT、状态/类型/难度/version checks、subject/status+updated indexes | `question_service.py`；`questions.py` `/api/admin/questions` GET/POST/GET-id/PUT/PATCH/DELETE；`attempt_service.py`、dashboard、capture、mistake；前端 `src/lib/api/questions.ts`、manage questions/capture/drafts | `questions`；012 初始字段，020 canonical fields/constraints；`保留` |
| `QuestionSource` | UUID、`question_id`、`source_type`、`source_name/title/ref/url/note`、created；source type check，question CASCADE，question index | `question_service.py`/question schemas；question client/editor/list | `question_sources`；012 创建，020 扩展 source 字段并放宽 ref；`保留` |
| `QuestionKnowledgePoint` | 复合 PK `question_id+knowledge_point_id`，`role`、`sort_order`、created；两端 CASCADE、role check、两个 indexes | `question_service.py`、`draft_service.py`；`questions.py` create/update；question schemas/client/editor/form | `question_knowledge_points`；020 从通用 links 迁入并建立；`保留` |
| `MistakeDraft` | UUID、唯一 `draft_item_id`；question/question_draft/attempt source 三选一；subject、题面、`my_answer`、answer/explanation snapshot、reason、mistake_reason、difficulty、时间；source/reason/difficulty checks，subject RESTRICT | `mistake_service.py`、`mistake_staged_service.py`；`mistake_drafts.py` `/api/admin/mistake-drafts` CRUD/reject/convert；capture/attempt；manage capture/drafts/mistakes | `mistake_drafts`；013 创建，021 增加 attempt source；`保留` |
| `Mistake` | UUID、唯一 `source_draft_item_id`、`question_id`、`subject_id`、题面、`my_answer`、`correct_answer`、`analysis`、reason、difficulty、`status`、固定 private visibility、version、时间；draft/question/subject RESTRICT，状态/visibility/version checks | `mistake_service.py`；`admin_mistakes.py` `/api/admin/mistakes`；`review_item_service.py`、dashboard、knowledge；manage mistakes/detail/review | `mistakes`；013 创建；`保留` |
| `ReviewItem` | UUID、`target_type='mistake'`、string `target_id`、state、fixed interval algorithm、`interval_days`、`repetitions`、next/last review、时间；target/state/algorithm/count checks、target unique、due index；target_id 无 SQL FK | `review_item_service.py`；`review_items.py` `/api/admin/review/items` queue/records/submit；dashboard；manage `review-queue.tsx` + `src/lib/api/review-items.ts` | `review_items`；013 创建；`保留`，需后续隔离完整性验证 |
| `ReviewRecord` | UUID、`review_item_id` RESTRICT、rating 0–5、review time、previous/next interval、previous/next date、created；rating/interval checks、item/time index | `review_item_service.py` submit/list；dashboard；manage review client/page | `review_records`；013 创建；`保留` |
| `Subject` | int PK、unique name、description、`status`、sort_order、created/updated；status `active/archived` 当前约束 | `taxonomy_service.py`、`subjects.py` `/api/admin/subjects` CRUD/tree；question/mistake/capture/dashboard；manage subjects/knowledge/question forms；旧 Note schema 另有 `SubjectOut` | `subjects`；001 创建，011 加 taxonomy，019 `is_active`→status；`保留` |
| `KnowledgePoint` | int PK、subject、self `parent_id` RESTRICT、name/description、sort/status/time；subject/parent/sort indexes、root/child lower-name unique partial indexes | `taxonomy_service.py`、`knowledge_points.py` `/api/admin/knowledge-points` CRUD/archive；question/draft/mistake/capture/dashboard；manage taxonomy/select/forms | `knowledge_points`；011 创建，019 chapters→parent tree；`保留` |
| `KnowledgePointLink` | int PK、`knowledge_point_id` CASCADE、generic `target_type/target_id`、created；target unique/index，无 target FK | `taxonomy_service.py`、`draft_service.py`、`question_service.py`、mistake service；generic Note/旧 mistake/draft links仍被读取；020 从 question links 复制 canonical Question 关系 | `knowledge_point_links`；011 创建，019 保留，020 迁移 question links；`保留`（不能按名称删除） |
| `CaptureItem`（合同称 Capture） | UUID、source attachment、status lifecycle、recognized/user context、question/analysis/error drafts、subject、KP suggestions、model version、attempt/last stage/error safe fields、timestamps、optional mistake draft target/creator；status/conversion/stage/count checks、两 indexes | `capture_service.py`、recognition/AI draft adapters；`captures.py` `/api/admin/captures` list/create/get/patch/recognize/draft/convert；manage capture workspace/manual/mistake entry；capture tests | `capture_items`；015 创建；`保留` |
| `Attempt`（支持对象） | UUID、question、submitted answer/correctness、unique optional mistake draft item、creator、submitted_at；nonblank check、question index | `attempt_service.py`、`attempts.py` `/api/admin/attempts`；question editor/capture→mistake draft；`test_attempt_service.py` | `attempts`；021 创建；`保留` |
| `Attachment/AttachmentLink`（Capture 来源/下游） | private local attachment metadata；link target only question_draft/question/mistake，purpose/unique checks | attachment service/router，capture service，manage attachments/capture | `attachments`/`attachment_links`；014、023；`保留` |
| `Note` | UUID `id`、unique `slug`、title/content/type/status/hidden、summary/cover/category、legacy mistake fields `subject/difficulty/question/my_answer/correct_answer/analysis/knowledge_points/ef/interval/repetitions/next_review/last_reviewed`、images/ai_metadata、folder/sort/revision/search_vector、tags | `notes.py` public GET + protected mutations/versions/backlinks; blog/note pages and editors; `review.py`, `review_planner.py`, knowledge retrieval/relations/assistant, recommendation, suggestions; public `/notes`, `/blog`, `/mistakes` | `notes` + `note_tags`；001 initial, 002/003 status, 004 ai metadata, 005 folder, 024 revision/versions/links, 1119 images, 025 fresh-install null defaults；`保留` for Note/Blog/public; `迁移` only for the `type=mistake` subset and legacy review fields, pending LSR-02 |

### Alembic 文件图与迁移消费者

静态 revision-header 读取结果（未加载 Alembic、未连接 DB）：`001→002→0ec85724afb9→1119bee5a419→003→004→005→006→007→008→009→010→011→012→013→014→015→016→017→018→019→020→021→022→023→024→025`，当前文件 head `025`。对象相关 revision 为：`001` notes/subjects；`002/003/004/005/1119/024/025` Note schema；`011/019` Subject/KnowledgePoint/KnowledgePointLink；`012` DraftItem/QuestionDraft/Question/QuestionSource；`013` MistakeDraft/Mistake/ReviewItem/ReviewRecord；`014` Attachment；`015` Capture；`020` canonical Question fields and QuestionKnowledgePoint；`021` Attempt and MistakeDraft attempt source。`backend/app/models/registry.py` 将上述模型注册进 schema lifecycle metadata。

关键运行时迁移风险已记录但未执行：`019` 会检查/删除非空 chapters；`020` 会读取并复制 `knowledge_point_links`，并拒绝跨 subject links；`025` 会更新多个表的 NULL 默认并操作 session indexes。它们不是当前 DB 状态证明，后续只能在隔离 replay 中验证。

### FastAPI 路由注册与调用图

`backend/main.py` 当前注册 34 个 router；相关注册在 86–119 行。新版私有链为：

- `/api/admin/subjects` → `taxonomy_service`；`/api/admin/knowledge-points` → 同服务。
- `/api/admin/drafts` → `draft_service`；`/api/admin/questions` → `question_service`；`/api/admin/attempts` → `attempt_service`。
- `/api/admin/mistake-drafts`、`/api/admin/mistakes` → `mistake_service`。
- `/api/admin/review/items` → `review_item_service`；`/api/admin/captures` → `capture_service`。
- `/api/admin/dashboard/summary` → `dashboard_service`；该服务查询 Question/Mistake/KnowledgePoint/ReviewItem/ReviewRecord。

这些 router 均在模块级依赖 `get_current_admin`（`notes.py` 的公开 GET 为 optional session，写入为 admin）。当前 auth 证据仍是 `admin_session` HttpOnly cookie backed by `AdminSession`、前端 `credentials: 'include'`、后端 `get_current_admin`；本轮未改变或验证运行时 auth。

### 旧候选与当前消费者

| 旧候选 | 当前证据 | disposition |
| --- | --- | --- |
| `Note(type='mistake')` 题面/答案/错因/知识点字段 | `Note` schema/model；`notes.py` 创建时 type=mistake 初始化 `next_review`；公开 `/api/notes?type=mistake` 和 `/mistakes` 页面仍读取；knowledge/recommendation/assistant 仍按 `Note.type` 查询 | `迁移`（仅候选子集；Note 模型本体 `保留`） |
| Note 复习字段 `ef/interval/repetitions/next_review/last_reviewed` | `/api/review` queue/stats/plan/submit、`review_planner.py`、`sm2.py` 仍直接读写；`src/lib/api/review.ts` 和 `use-note-index.ts` 仍调用 | `替换` |
| 旧 `/api/review` 链 | `backend/main.py` 仍 include `review.router`；`review.py` 仍提供 `/queue`、`/{slug}`、`/stats`、`/plan`，全部以 Note mistake 为源；compatibility test 明确断言这些私有路由 | `替换`（不是删除证据） |
| `/mistakes/review` | Next page 仍存在且直接用旧 review client；`next.config.ts` 仅 redirect 到 `/manage/review`；`batch7-compatibility.test.ts` 要求旧 page 存在和 redirect 存在 | `替换` |
| `/write-mistake`、`/write-mistake/:slug` | page/components 仍存在；slug page 读取 `/api/notes/{slug}`，兼容表单仍写 Note；Next redirects 指向 manage capture/mistakes；compatibility test 要求文件存在 | `替换` |
| `/write-note`、`/write` 及其写作服务 | Next redirects 指向 manage dashboard，但页面/服务仍存在；Blog/Note 写入仍通过 `src/lib/api/notes.ts`，不能误删普通 Note/Blog | `替换`（范围需单独确认） |
| `src/lib/api/review.ts`、`use-note-index` 的 review hooks、旧 review page | 当前命中并由 public mistakes/dashboard-ish surfaces 使用；不是孤立文件 | `替换` |
| `src/lib/api/questions.ts:updateLegacyQuestion` 与 `question-editor.tsx` PUT 调用 | 当前兼容 client 仍被 manage question editor 使用；后端 `/api/admin/questions/{id}` 同时保留 PUT/PATCH 形态 | `替换`（需新版 patch 合同稳定后再退休） |
| `review_planner.py`、`sm2.py`、`schemas/note.py` 中 ReviewPlan/ReviewRequest/ReviewStats | 仍是旧 API/service 的运行时依赖；不能在 LSR-01 删除 | `替换` |
| 通用 `KnowledgePointLink` relation | 旧/新 target 共同使用；Note/旧 mistake 与 question-draft 仍有 generic links，Question canonical table 仅部分替代 | `保留` |
| `Note` 普通笔记、Blog、公开读取、版本、tags/folders/backlinks | `notes.py`、`src/lib/api/notes.ts`、blog/note pages、`public/blogs/index.json`/`categories.json`、`load-blog.ts`、Blog services | `保留` |

### 前端 client、hook、page、navigation 与测试交叉审计

新版 client 为 `src/lib/api/questions.ts`、`drafts.ts`、`mistakes.ts`、`review-items.ts`、`taxonomy.ts`、`captures.ts`、`attempts.ts`、`dashboard.ts`；核心 manage 页面为 `manage/(workspace)/{drafts,questions,mistakes,review,subjects,knowledge-points,capture,dashboard}` 及其 components。`manage-sidebar.tsx` 当前导航将草稿/题目/错题、科目/知识点、复习、采集列为工作区入口；这些页面的 API imports 与后端路由逐项存在。

新版后端测试引用分布（AST/import 或 rg，只读文件计数，不代表测试已执行）：Question 相关 `test_question_domain.py`、`test_question_draft_service.py`、`test_question_routes.py`、`test_i6_draft_chain.py`；Mistake/Review 相关 `test_mistake_review_service.py`、`test_mistake_routes.py`、`test_mistake_staged_workflow.py`；Capture 相关 `test_capture_service.py`、`test_i6_capture_failure_matrix.py`、`test_i6_capture_http.py`、`test_i6_draft_chain.py`、`test_anon_capture_access.py`；taxonomy `test_taxonomy_service.py`；dashboard/attachment/attempt/AI tests 还交叉消费上述对象。前端相关测试包括 manage draft/dashboard/capture、sidebar/mobile navigation、`batch7-compatibility.test.ts` 与 `use-note-index.test.ts`。

旧消费者仍可重算：`/api/review` 文本命中 18（backend/src/next config 范围）；`/write-mistake` 命中 2 个配置/源引用，`/mistakes/review` 命中 3 个配置/测试/源引用；精确路径审计确认旧 page、redirect、旧 client、旧 service 和 compatibility test 均存在。文档命中未计为运行时消费者。

### 静态数据、公开内容与导出/导入审计

- `public/blogs/index.json` 与 `public/blogs/categories.json` 是当前静态 Blog 索引/分类消费者；`src/lib/load-blog.ts` 从 `/blogs/{slug}/config.json`、`index.md` 加载静态博客；当前 `public/blogs` 根下没有 slug 子目录文件（`find` 只发现两个 JSON），故不能假设静态导出完整。
- Blog 写入/删除服务 `src/app/write/services/{push-blog,delete-blog}.ts` 与 `src/app/blog/services/{save-blog-edits,batch-delete-blogs}.ts` 通过 `/api/notes` 操作 `Note(type=blog)`；这是保留职责，不是旧错题删除授权。
- 全仓源码脚本未发现当前运行时的 Note→新对象导出/导入器、批量迁移器或已登记数据快照；`rg --files` 只发现 `docs/backup-restore.md`、历史 workflow 和静态 fixtures 等文档/测试线索。现有 GitHub/static export owner=`现有 Note/Blog GitHub/export integration boundary`，仅处理 Note/Blog、排除 private Question/Mistake；新 structured import owner=`未来 LSR-02 governed migration service/tool + legacy_note_migrations ledger`（design-only/`NOT_IMPLEMENTED`），任何其它 external consumer 即 `TASK-BLOCK`。

### Blocker / decision-needed（历史快照，已被最终结论取代；仍保留风险证据）

1. **旧 Review 运行时未退出**：旧 `/api/review` 与 Note SM-2 字段仍被当前 router/service/client/page/test 消费；需要后续验证新版当前调度语义等价、切换观察期和旧链安全退出顺序。历史 `ReviewRecord` 不恢复、不伪造；旧字段只进入 provenance/`migration_notes`，当前 `替换`，不是 `删除`。
2. **Note 责任边界待按当前合同实现/验证**：普通 Note、Blog、公开 `/notes`/`/blog` 读取、版本/标签/文件夹/反向链接仍活跃；旧 published&&!hidden Note mistake 应只读公开并保留原 `/notes/{slug}`，`/mistakes` 聚合入口应关闭；不能删除整个 Note 或公开内容。当前代码仍有 `/mistakes` 消费者，尚未证明已切换。
3. **旧入口仍有真实文件与兼容断言**：`/write-mistake`、`/mistakes/review`、`/write-note`、`/write` 有 redirect，但 compatibility tests 要求文件存在，且 `/write-mistake/[slug]` 仍读取 Note；不能宣称旧入口零消费者。
4. **通用关系/字符串目标未证明可替换**：`KnowledgePointLink.target_id` 与 `ReviewItem.target_id` 无数据库目标 FK；需隔离数据完整性查询确认孤儿、重复、跨 subject 和 target_type 分布，当前为 `未知`。
5. **数据内容与迁移映射未执行**：本任务禁止 DB 内容查询；Note slug/UUID、subject/KP、答案/错因/难度、EF/interval/repetitions/日期、版本/来源/可见性和审计字段的逐行映射仍属 LSR-02，任何不可无损项必须进入 migration_notes。
6. **导出/导入边界（历史快照已收束）**：当前 runtime importer/exporter 零实现/零注册；现有 GitHub/static export owner=`现有 Note/Blog GitHub/export integration boundary`，仅处理 Note/Blog，明确排除 private Question/Mistake。新 legacy Note→structured import owner=`未来 LSR-02 governed migration service/tool + legacy_note_migrations ledger`（design-only/`NOT_IMPLEMENTED`）；任何其它 external consumer 发现即 `TASK-BLOCK`。
7. **当前 graph 只由文件读取得到**：head `025` 已识别，但没有 Alembic replay、数据库 `alembic_version` 或 schema introspection；G2 仍 `NOT_VERIFIED`。

### Gate 与后续状态（历史快照，已被文末 canonical status 取代）

| Gate/任务 | 当前状态 | 原因 |
| --- | --- | --- |
| LSR-01 | `PASS`；checkbox `[x]` | 静态 mapping、消费者 owner/disposition 与当前边界已由 Reviewer/QA/Data 复核；数据库/runtime/G2 仍未执行 |
| G0 | `PASS` | `lsr01-g0-product` 与 `lsr01-g0-domain` 已针对当前用户合同独立复核通过 |
| G1 | `PASS` | 最终机械合同已由 `lsr01-g1-architect=PASS`、`lsr01-g1-reviewer=PASS_WITH_NOTES` 独立复核；仅设计层，不继承实现/G2 |
| G2 | `NOT_VERIFIED` | 本轮不读 DB；需 LSR-02/03 隔离 replay、映射、计数/关系/幂等/恢复 |
| G3 | `NOT_VERIFIED` | 只确认源码中 session/admin dependency 形态；未执行 401/403/公开可见性负向 |
| G4 | `NOT_VERIFIED` | Capture/AI/Review 来源链未运行验证 |
| G5 | `NOT_AUTHORIZED` | 无生产数据库、服务、凭据、部署、commit/push 范围 |

建议下一步：G0 已由两名独立 Worker 针对 2026-08-23 当前用户合同复核为 `PASS`；当前执行 G1 最小架构修订与独立复核。在 G0/G1 均 `PASS` 前不触发 LSR-02。LSR-02 需要单独冻结 Note mistake→Question/Mistake/ReviewItem/ReviewRecord/Subject/KnowledgePoint 的无损字段映射、来源/版本/审计、幂等键、备份/恢复和 blocker；本轮不触发 LSR-02。

## LSR-01 修订 addendum（历史快照，已被最终当前结论取代；Reviewer/Verifier findings，2026-08-23）

本节为历史快照，只补当时当前源码证据，不改变最终任务结论：当时记录 `LSR-01=PARTIAL`、checkbox `[ ]`、G1=`BLOCKED` 并等待复核；实际早期反馈为 Principal Technical Reviewer=`PASS_WITH_NOTES`、Senior QA / SDET=`PARTIAL`、Senior Data Engineer=`PASS`。该状态已由最终 Reviewer=`PASS_WITH_NOTES`、QA=`PASS`、Data=`PASS` 取代，Owner 不把历史反馈当作当前 Gate 结论。

历史快照（已被最终 QA/Data 收束取代）：本轮曾记录 Reviewer=`CHANGES_REQUIRED`、QA/Data=`PARTIAL`；其修订内容已纳入最终合同。当时 QA=`BLOCKED`、Data=`PARTIAL`，等待最终复核；当前 QA=`PASS`、Data=`PASS`。

### 迁移字段与 revision 风险补全

| 当前证据 | 具体风险 / disposition |
| --- | --- |
| `011_add_subject_taxonomy.py` 创建 `chapters(subject_id,name,description,sort_order,is_active,created_at,updated_at)`，并给 `subjects` 加 `description/is_active/sort_order/created_at/updated_at`；`019_align_subject_knowledge_tree.py` 在升级前查询 `SELECT count(*) FROM chapters`，非空即抛错，随后把 `subjects.is_active` 转为 `subjects.status`、把 `knowledge_points.is_active` 转为 `status`，新增 `knowledge_points.parent_id`，删除 `knowledge_points.chapter_id/is_active` 与 `chapters`。 | `chapters` 为旧 taxonomy 候选 `迁移`，但非空拒绝、章节→parent 映射、跨 subject/排序/名称冲突均未知；`subjects.is_active`、`knowledge_points.is_active`、`knowledge_points.chapter_id` 的当前数据映射为 `未知` blocker，不能称 019 可逆。`Subject.status`/`KnowledgePoint.status` 与 parent tree `保留`。 |
| `Question` 同时持有 `stem_md` 与 `question_text`、`analysis_md` 与 `explanation`、`answer_data` 与 `correct_answer`；`question_service.create_question` 双写 canonical+legacy。实际 PUT router 调用 `question_service.update_question()`：该路径只更新 generic `KnowledgePointLink`，不删除/重建 canonical `QuestionKnowledgePoint`；读取优先 canonical，因此 PUT 后可能返回陈旧 canonical 关系。 | 双写一致性、历史 NULL/格式、choice answer 编码及 PUT 后关系陈旧风险为 `未知`；canonical `Question` 保留，legacy mirror 字段迁移/未知；不得任选一侧为唯一事实源。 |
| `Question` service create/update 写入 `QuestionKnowledgePoint` **和** generic `KnowledgePointLink`（但 PUT 更新路径只维护 generic link）；读取优先 canonical，空时 fallback generic。`020` 检查跨 subject generic links，复制到 canonical 表 `ON CONFLICT DO NOTHING`；同时去除 `question_sources` 的 `uq_question_sources_ref`，放宽 `source_ref` nullable。 | canonical/generic 双写一致性、PUT 陈旧 canonical、复制丢重复、跨 subject 拒绝、去唯一约束后的重复 source 风险均为 `未知`；两张关系表保留至等价性验证。 |
| `QuestionSource` schema `source_ref` `max_length=500`，但 012 初始 DB 为 `String(64)`；020 仅 `nullable=True`，没有扩容。 | schema/DB 长度契约冲突为 `BLOCKER`，disposition=`未知`；必须由 LSR-02 决定截断/扩容/拒绝，禁止静默截断。 |
| `MistakeDraftCreate` schema 暴露 `attempt_id`，但 `mistake_drafts.py:create_mistake_draft` 调 `mistake_service.create_mistake_draft(...created_by=admin.id)` 未传 `attempt_id`；前端 `src/lib/api/mistakes.ts` 的 `MistakeDraftCreate` 也未定义该字段。 | Attempt-backed path 当前不可从 HTTP 创建，来源 provenance 断裂；`MistakeDraft`/`Attempt` 均 `保留`，该链为 `未知` blocker，需后续修复/验证任务，不在 LSR-01 修改。 |
| 012 downgrade 删除 generic question links 后 drop tables；013 downgrade 删除 mistake/mistake_draft generic links 后 drop；019 downgrade 重建 chapters 并删除 parent/status；020 downgrade 拒绝存在 canonical rows 后才 drop canonical。 | downgrade 并非无损回滚，且 019/020 有数据条件/不可逆风险；状态 `未知`/G2 blocker，不能将历史 downgrade 代码当作恢复证明。 |

### 旧具体消费者路径（当前源码）

| 路径 | 当前行为与对象 | disposition |
| --- | --- | --- |
| `backend/app/services/knowledge_retrieval.py` | `select(Note)`；按 `Note.subject/type/difficulty/knowledge_points`、`note_tags`、`next_review` due/overdue/upcoming 过滤；构造 `related_mistakes`/`SourceRef`，直接读取 `analysis/question/content` | `迁移`/`替换`候选；当前消费者 |
| `backend/app/services/knowledge_assistant.py` | recent/untagged/unfoldered 查询 Note；`aggregate_weaknesses` 按 `Note.type='mistake'`、subject、knowledge_points 聚合 | `迁移`/`替换`候选；当前消费者 |
| `backend/app/services/knowledge_relations.py` | Note↔Note 候选关系，按 tags/subject/knowledge_points 计算 relation；不读取 canonical Question/Mistake | `替换`候选；当前 Note graph 消费者 |
| `backend/app/services/recommendation.py` | 收集非隐藏 Note、`type='mistake'`、`next_review` 到期、knowledge_points；生成 DailyRecommendation 上下文 | `替换`候选；当前消费者 |
| `backend/app/routers/suggestions.py` | `/api/ai/suggestions*` 读取/写入 Note、Tag、Folder；weekly summary 统计 Note 非 mistake、mistake、`last_reviewed`、subject、knowledge_points，并写 `Note(type='note')` 周报 | `保留` Note/普通内容职责；错题统计部分 `迁移`候选 |
| `src/app/mistakes/page.tsx` | `useNoteIndex({type:'mistake',status:'published'})`；匿名/可选 admin 展示 Note 统计/复习计划，链接 `/manage/review`、`/manage/capture` | `替换`候选；公开旧错题链当前消费者 |
| `src/app/mistakes/review/page.tsx` | 直接 import `getReviewQueue/submitReview/getReviewStats/getReviewPlan` from `src/lib/api/review.ts`，提交 slug+quality，展示 Note fields | `替换`候选；旧页面仍实际调用 |
| `src/app/notes/[id]/note-detail-content.tsx` | `getNote('/api/notes/{id}')`；展示 question/my_answer/correct_answer/knowledge_points/analysis/ai_metadata；公开详情按 Note visibility 返回；admin 才读 backlinks/delete | `保留` Note/公开详情；其中旧错题展示 `迁移`候选 |
| `src/app/manage/page.tsx` | 根 `/manage` 旧管理壳，`useNoteIndex` + `deleteNote/batchDeleteNotes` 管理普通 Note/Blog/mistake；嵌入 KnowledgeSidebar、SuggestionCard、SiteSettingsPanel、AI/Recommendation tabs | 根管理入口 `替换`候选；Note/Blog/content 子功能 `保留` |
| `src/app/notes/components/weekly-summary-card.tsx` | `getWeeklySummary` from knowledge-assistant；用 `getNote/updateNote/createNote` 保存周报 Note，并创建/list folders | Note/周报 `保留`；错题来源部分 `迁移`候选 |
| `src/hooks/use-note-index.ts` + `src/lib/api/review.ts` | Note index 与旧 review stats/plan SWR keys `/api/review/stats|plan` | `替换`候选；当前 hook 消费者 |
| `backend/app/routers/review.py` + `review_planner.py` + `sm2.py` | `/api/review/{queue,slug,stats,plan}` 全部 Note mistake/SM-2 字段 | `替换`；不得删除 |
| `src/app/manage/page.tsx` → `src/app/write-note/page.tsx` / `src/app/write/[slug]/page.tsx` 等 | 根 `/manage` 的旧内容管理/编辑链接由 `getContentEditHref`、旧 tab/组件继续指向 write surface；`next.config.ts` redirects `/write-note*`/`/write*` 到 `/manage/dashboard` | redirect 只改变导航，不证明 page、client、service 或 API consumer 删除；根 `/manage`=`替换`候选，旧写页/API/service=`替换`候选 |

### 两个 `/manage` 入口与新旧 API 边界

- 根 `src/app/manage/page.tsx` 是旧的内容/设置/guestbook 管理壳，直接消费 `/api/notes`、auth、content、suggestions、guest messages 等。
- `src/app/manage/(workspace)/layout.tsx` 是新版 `/manage/(workspace)` route group 的私有工作区壳，导航由 `manage-sidebar.tsx` 提供，消费 `/api/admin/drafts|questions|mistake-drafts|mistakes|review/items|subjects|knowledge-points|captures|dashboard`。
- App Router route group `(workspace)` 不出现在 URL，因此根 `/manage` 与新版 `/manage/dashboard` 是两个实际页面入口；不能把 redirect 或同一视觉导航误当作 owner 已收敛。
- `/write-note*`、`/write*`、`/write-mistake*` 的 redirect 只改变请求导航目标；源 page、旧 client、旧 Note API/service 与 compatibility tests 仍是消费者，全部 `替换`候选而非 `删除`。

### 公开错题可见性冲突（G0/G3 blocker）

`backend/app/routers/notes.py` 的匿名 GET `/api/notes` 只过滤 `hidden=False`、`status='published'`，没有排除 `type='mistake'`；GET `/api/notes/{slug}` 对匿名用户同样只检查 hidden/status。因此 published&&!hidden 的旧 Note mistake 可由匿名列表/详情返回。`src/app/mistakes/page.tsx` 明确公开 Note mistake 列表；`src/app/notes/[id]/note-detail-content.tsx` 公开展示 question/correct_answer/analysis/knowledge_points 等字段（my_answer 部分仅 admin）。新版 `Question`、`Mistake` schema/model 固定 `visibility='private'`。

这形成已确认合同与当前实现之间的待验证冲突：旧 published&&!hidden Note mistake 应只读公开并保留原 `/notes/{slug}`，而新版 `Question/Mistake` 应始终私有，`/mistakes` 聚合入口应关闭。标记为 **G0/G3 decision-needed blocker（任务层阻塞事项）**；G0 既有状态仍为 `BLOCKED`，须针对当前合同重查，G3 仍为 `NOT_VERIFIED`。任务层 blocker 不等于 Gate=`BLOCKED`，本 Owner 不擅自声称实现或 Gate PASS。

### AI、认证与静态/导出边界补全

- `AiCallLog` (`ai_call_logs`) 由 016 初建，017 才增加 `prompt_version`；字段包括 task/provider/model/latency/success/error/fallback/attempts/input_summary/prompt_version/created，模型注释明确不保存完整 prompt/output。字段静态存在不等于 AI service 始终写入，也不等于与 `AiRun` 有可靠关联；写入覆盖率、correlation 和运行时 provenance 均为 `未知`。
- `AiRun` (`ai_runs`) 由 018 创建，包含 task/`target_type`/`target_id`/provider/model/prompt_version/status、validation_status、input_summary/replay_input/output_data/warnings/error、attempt、parent_run、review_status/revision/note、latency/start/finish/time；状态 checks 与 created/task/status/review indexes。`ai_runs.py` 注册 `/api/admin/ai/runs` list/detail/retry/decision；client `src/lib/api/ai-runs.ts`；页面 `src/app/manage/(workspace)/ai/runs/page.tsx` 与 AI run tests/AI services 消费。`target_type/target_id` 为无 FK 多态目标：invalid target、目标删除后的 orphan、type/object mismatch、retry/parent 与原目标 provenance 均为 `未知`；`AiCallLog` 也无到 `AiRun` 的 FK/correlation，关联完整性为 `未知`。两者均 `保留`，G4=`NOT_VERIFIED`。
- Note supporting constraints：`folders.parent_id` 由 005 的 self-FK `CASCADE` 漂移为 007 `SET NULL`；`note_versions` 有 `(note_id,version)` unique、`note_id` CASCADE、`created_by` SET NULL；`note_links` 有 `source_note_id` CASCADE、`target_note_id` SET NULL、`(source_note_id,raw_link)` unique；`note_tags` 为复合 PK 且两端 CASCADE；`notes.folder_id` 为 SET NULL。当前只读确认文件定义，实际数据 orphan/重复/级联结果仍为隔离 DB unknown。
- `AdminSession`、`PasskeyCredential`、`AdminPassword` (`admin_sessions`/`passkey_credentials`/`admin_passwords`) 由 006 创建，025 调整 session indexes/unique token hash；session fields 是 user/token_hash/auth_level/expiry/revoked/ip/user_agent/time，passkey 是 credential/public_key/sign_count/device/time，password 是 username/password_hash/update/session FK。它们是当前 `admin_session` HttpOnly、`AdminSession`、`credentials: 'include'`、`get_current_admin` 合同的 retained auth support；不得描述 JWT/Bearer 为当前合同，disposition=`保留`，G3 仍未运行验证。
`backend/app/services/content_store.py`、`backend/app/routers/content.py` `/api/content/{about,shares,projects,pictures,snippets,bloggers,site-settings,upload-image,delete-image}` 与 `ManagedContentEntry` 表承担静态/站点内容；`src/app/(home)/services/push-site-content.ts`、about/projects/pictures/share/bloggers/snippets services 及 `src/config/site-content.json` 消费。它们与 Note/Blog retirement 无关，owner=`Note/Public Content integration boundary`，disposition=`保留`/`超出 LSR-01 旧错题范围`；不得删除或纳入 private Question/Mistake。

### 多态关系、字段和数据验证 unknown 清单

以下均为后续隔离 DB/迁移验证项，本轮未查询：

- 旧 `notes(type='mistake')` 与新版 `mistakes` 数量/唯一来源/字段映射是否匹配；slug/UUID、subject/KP、题干/答案/错因/难度、EF/interval/repetitions/next/last review、visibility/status/version/source/audit 是否可无损迁移。
- `KnowledgePointLink(target_type,target_id)`、`ReviewItem(target_type,target_id)`、`AttachmentLink(target_type,target_id)`、`DraftItem.target_id` 的 invalid UUID/int、unknown target type、orphan、duplicate、cross-subject；canonical `QuestionKnowledgePoint` 与 generic links 一致性。
- `ReviewItem` 是否一对一指向真实 Mistake、重复 target、ReviewRecord orphan/并发重复；`Mistake`↔DraftItem/Question/Subject/ReviewItem 关系。
- `Attachment`↔AttachmentLink↔QuestionDraft/Question/Mistake、`Attempt`↔Question/MistakeDraft 的关系；特别是 HTTP attempt_id 未传 service 的实际影响。
- Note tags/folders/note_versions/note_links 的数据完整性、版本重复、source/target backlinks、SET NULL/CASCADE 结果；公开/隐藏/草稿过滤与旧错题详情暴露。
- live Alembic `alembic_version`、实际 schema/index/constraint 与文件 head `025` 的 drift；012/013 downgrade、019 chapters conversion/drop、020 import/ON CONFLICT/drop-unique 的 replay/rollback。
- import/export owner、format、scale、静态 `public/blogs` 与 managed content 的来源/导出目标：现有 GitHub/static export owner=`Note/Blog GitHub/export integration boundary`，仅 Note/Blog；runtime importer/exporter 零实现/零注册；structured import owner=`未来 LSR-02 governed migration service/tool + ledger`（design-only/`NOT_IMPLEMENTED`）；其它 external consumer 即 `TASK-BLOCK`。

### 可重算证据标识（不含用户正文/秘密）

按命令 `python3` 读取并排序以下输入集合的路径与每个文件 SHA-256（不保存正文、不连接 DB）：`backend/app`、`backend/alembic`、`backend/tests`、`src/app`、`src/hooks`、`src/lib`、`src/components`、`public`、`next.config.ts`。当时扫描计数为 1119 个文件；仅保留路径+内容 hash 的 aggregate 摘要和命令提示，逐文件 manifest 与过滤后成员集合未持久化，因此 hash 不能独立证明当时成员集合，只能作为可重算线索。

| 标识 | 值 |
| --- | --- |
| input file-path+content-hash manifest | `e7cf4da8f1697fce2059a13543332eaf5a8620a5c6594ab27003053062883918` |
| evidence summary hash | `ebc3bd89c3fcf8b2003b50f42d63a3f48389cdba1d209aff317e8f39b41ebedf` |
| summary input | `files=1119;head=025;backend_include_router=34;old_review_hits=18;db=NOT_AUTHORIZED;runtime=NOT_VERIFIED` |
| evidence status | aggregate hash 可重算但成员集合未持久化；不是运行时/数据库证明，历史数字未继承；仅作当时输入摘要线索 |

### 修订后的审查状态

| 角色 | 当前结论 | 处理 |
| --- | --- | --- |
| Independent Principal Technical Reviewer | `PASS_WITH_NOTES` | 最终复审无 actionable finding；可交独立 G0/G1 Worker 对账，但不代表 Gate PASS |
| Independent Senior QA / SDET | `PARTIAL` | 静态路径、计数、hash 与串行状态复核一致；未运行产品测试/DB/runtime/browser，LSR-01 仍为 `PARTIAL` |
| Independent Senior Data Engineer | `PASS` | 仅指第二轮静态修订事实已闭环；未连接 DB，G2 与所有数据分布/完整性仍为 `NOT_VERIFIED` |
| Primary Owner | 不自批 | 只维护 manifest 与任务证据，不改变 G0/G1 结论 |

主代理在 G0 Worker 执行前的状态对账：公开错题段落当时写的是“G0/G3 任务层 decision-needed blocker”，并明确 `blocker != Gate BLOCKED`；当时全局 G0/G3 仍为 `NOT_VERIFIED`。随后只有 G0 经两名独立 Gate Worker 正式裁决为 `BLOCKED`；G3 仍为 `NOT_VERIFIED`。

### LSR-01 G0 独立 Gate 对账（历史快照，已被最终 G0 结论取代）

`lsr01-g0-product`（Product Architect）与 `lsr01-g0-domain`（Senior Domain Analyst）均给出 `BLOCKED`。这是 G0 独立裁决后的当前 Gate 状态；它取代上文 Owner 审计阶段的 `NOT_VERIFIED`，但不把 G3 一并判为 `BLOCKED`。G1 尚未执行，LSR-02 不得开始。

### 2026-08-23 当前用户合同（历史重查输入，已被最终 G0 结论取代）

用户原话：`以上三项同意`。这三项决定覆盖相冲突的历史决定/未决项，但仅是当前领域合同，不代表实现或 Gate PASS：

1. 已发布且未隐藏的旧 `Note(type='mistake')` 保留为只读公开 Note，保留原 `/notes/{slug}` URL；关闭 `/mistakes` 聚合入口；新版 `Question/Mistake` 始终私有；旧公开 Note 与新版私有学习对象以 source/provenance 关联。普通 Note/Blog 保持。
2. 旧复习只迁移当前调度状态到 `ReviewItem`；原 `ef/interval/repetitions/next_review/last_reviewed` 保存到 provenance/`migration_notes`；不生成/伪造历史 `ReviewRecord`；语义不明或空值设为 `paused`，等待人工确认。
3. Capture 允许同一操作同时生成 `QuestionDraft` 与 `MistakeDraft`；正式转换严格先 `QuestionDraft→Question`，再人工确认 `MistakeDraft→Mistake→ReviewItem`；两类草稿均不得绕过人工确认。

G0 重查条件当时已满足“用户合同已书面化、可测试验收与 LSR-02 映射输入已登记”；在两个独立 G0 Worker 完成复核前，历史状态仍保持 `BLOCKED`。该历史过程保留为审计轨迹。

最终重查结果：Owner 修正新版复习字段/旧字段 provenance、把 Review 等价性收窄为当前调度语义，并明确 Capture 草稿创建与正式转换的区别；`lsr01-g0-product=PASS`、`lsr01-g0-domain=PASS`。当前 G0=`PASS`，允许进入 G1，但不继承到 G1-G4 或任何实现状态。

### G0 历史明确决定审计

两名 G0 Worker 独立复查现有 workflow 中明确归属用户的历史决定，结论仍为 `BLOCKED`，但以下边界可复用且不继承历史 Gate 状态：

- 普通 Note、Blog 和公开内容职责继续保留；新版 Question/Mistake/Review 学习数据保持私有。
- Subject 是私有学习命名空间，KnowledgePoint 使用 `parent_id` 树；Chapter-like 节点归入 KnowledgePoint 语义，不恢复独立 Chapter 域。
- 数据库 UUID/主键是稳定身份，slug 仅作公开兼容标识；缺失或矛盾 provenance 进入人工复核，不静默补全。
- Capture/AI/OCR 只能生成可编辑草稿，人工确认后才能产生正式 Mistake；ReviewItem 只从正式 Mistake 产生。
- 新版复习规则已确定为 `fixed_interval_v1` 与 0–5 评分；这些事实不定义旧 SM-2 历史的迁移方式。

历史 D-0 曾决定关闭公开 `/mistakes` 且不自动迁移旧 Note；当前用户合同现已在上述范围覆盖该历史决定：旧 published&&!hidden Note mistake 只读公开并保留原 URL，关闭 `/mistakes` 聚合入口；复习仅迁移当前调度状态且不伪造 ReviewRecord；Capture 允许双草稿但正式转换严格按 Question 后 Mistake/ReviewItem 且均需人工确认。普通 Note/Blog 保持。当前源码仍可能与合同不一致，不能将合同记录当作实现证据。

### 当前合同的可测试验收与 LSR-02 映射输入

| 合同 | LSR-01/后续可测试验收 | LSR-02 映射输入/禁止事项 |
| --- | --- | --- |
| 公开旧 Note | 匿名只读 `/api/notes` 与 `/notes/{slug}` 对 published&&!hidden `type=mistake` 保持可读；原 slug URL 保持；`/mistakes` 聚合入口关闭；新版 Question/Mistake 匿名不可读；旧 Note 与新对象存在可审计 source/provenance 关联 | 旧 Note→新对象 source/provenance、slug/UUID、visibility/status、只读 disposition；不得把普通 Note/Blog 或公开 URL 删除/私有化，不得假设当前代码已切换 |
| 复习迁移 | 只验证当前调度状态映射到 ReviewItem；旧字段完整进入 provenance/`migration_notes`；不新增历史 ReviewRecord；语义不明/空值为 paused 并产生人工确认项 | `ef/interval/repetitions/next_review/last_reviewed` 原值、空值/时区/语义和 migration_notes 字段；禁止伪造历史 ReviewRecord 或猜补值 |
| Capture 双草稿 | 同一操作可产生 QuestionDraft 与 MistakeDraft；正式路径必须先 QuestionDraft→Question，再人工确认 MistakeDraft→Mistake→ReviewItem；两类草稿未经人工确认不得正式转换 | draft source/approval/audit/order/idempotency；禁止绕过人工确认、并行伪造正式对象或把 AI 输出当事实 |

## G1 最小架构修订合同与补漏 manifest（历史快照，已被最终机械合同取代）

本节记录当时 G1 Architect/Reviewer 的共同 findings 与 Owner 修订输入；不代表当前 G1 状态、实现或 LSR-02 授权。最终当前状态见文末 canonical status。

### 补漏消费者 manifest

| 当前路径/消费者 | 当前对象与行为 | owner/disposition |
| --- | --- | --- |
| `backend/app/routers/search.py` → `services/knowledge_markdown_service.py` | `search_notes` 查询 published&&!hidden `Note` title/content/summary/category；普通 Note/Blog 与旧公开 mistake 都可能进入搜索 | 普通 Note/Blog=`保留`；旧 mistake 搜索需按当前公开合同验证/调整，当前=`未知`，不得删除 |
| `src/app/manage/(workspace)/search/page.tsx`、`src/lib/api/search.ts`、`backend/tests/test_i8_search_routes.py`、`test_i8_markdown_search.py`、`src/lib/api/search.test.ts` | 管理搜索 client/page 与后端 Note 搜索测试；当前不搜索新版私有学习对象 | owner=`retained Note/Public Content admin search`；private learning search 不属于 LSR-01，新增须独立 G1/G3/G4 |
| `src/app/discover/page.tsx` | `getBloggers/getShares` content API + `listNotes(type=note,featured=true)`；页面仍链接 `/mistakes`、`/guestbook` | Blog/content/普通 Note=`保留`；`/mistakes` 链接=`替换`（永久 `/notes` redirect 合同待实现验证） |
| `src/app/rss.xml/route.ts`、`src/app/sitemap.ts`、`src/app/(home)/aritcle-card.tsx`、`src/hooks/use-blog-index.ts`、`public/blogs/index.json/categories.json` | RSS/sitemap/home article card 消费 Blog 静态索引/公开 Blog | Blog/static index=`保留`；不纳入旧 mistake 删除；owner=`Blog/static content` |
| `src/lib/content-routes.ts` | `note/blog/mistake` 三类编辑/公开 href；mistake 当前指向 `/manage/mistakes` 或 `/mistakes` | note/blog=`保留`；mistake route=`替换`，按新 `/notes` public 与 `/manage/*` private owner 矩阵收敛 |
| `src/components/mobile-nav.tsx`、`src/components/vertical-nav.tsx`、`src/app/manage/components/manage-mobile-nav.tsx`、相关 nav tests | public/mobile nav 仍有 `/mistakes`，manage nav 指向 workspace | public `/mistakes`=`替换`为永久 `/notes`；workspace private nav=`保留`；导航测试需验证 rollback |
| `src/app/guestbook/page.tsx`、`src/lib/api/guest-messages.ts` | guestbook type=`mistake` 链接可指向 `/notes/{slug}` 或 `/mistakes`；留言职责独立 | guestbook=`保留`；mistake link=`替换`为 `/notes/{slug}`，不可因退休删除留言/公开 Note |
| `src/app/mistakes/page.tsx`、`src/app/mistakes/components/{weak-points-panel,weak-point-diagnosis}.tsx`、`src/app/mistakes/review/page.tsx`、相关 mistake tests | 旧公开错题聚合、弱点/AI diagnosis、旧 review client；读写/统计仍基于 Note/旧 review | private Question/Mistake/Review services owner，具体实现 LSR-04/LSR-16/适用 G4 / `替换`；只读 Note detail=`保留`；不留未指定 owner |
| `src/app/notes/[id]/components/related-knowledge-panel.tsx` | 展示 related_notes 与 related_mistakes，来源为 Note detail/knowledge relations | `Note/Public Content owner`；Note backlinks/related content=`保留`；旧 mistake projection=`替换`为 private Question/Mistake/Review service 只读关联 |
| `backend/app/services/knowledge_relations.py`、`knowledge_retrieval.py`、`knowledge_assistant.py`、`recommendation.py`、`routers/suggestions.py` | Note tags/subject/knowledge_points、旧 mistake、复习字段、周报与推荐仍被运行时消费 | 普通 Note/Blog/周报=`Note/Public Content owner`/`保留`；旧 mistake/review=`Question/Mistake/Review services owner`/`替换`，具体 LSR-04/LSR-16/适用 G4 |
| `backend/app/services/knowledge_markdown_service.py` | NoteVersion/NoteLink、wikilinks/backlinks、Note 搜索；并非新版 Question/Mistake owner | `Note/Public Content owner`/`保留`；新 legacy Note→structured import 由未来 LSR-02 governed migration service/tool + ledger owner，design-only/`NOT_IMPLEMENTED` |

### 保守 route matrix（历史快照，已被最终冻结 route matrix 取代）

| surface | anonymous | admin | URL/navigation | API owner | rollback |
| --- | --- | --- | --- | --- | --- |
| `/mistakes` aggregate | 永久 redirect `/notes`，不再聚合 | 同上；私有错题在 workspace | old URL successor=`/notes` | public Note read owner；private Mistake=`/api/admin/mistakes` | 恢复旧 page/router 与 redirect config |
| `/api/notes`、`/notes/{slug}` | published&&!hidden Note 只读公开，含旧 mistake；无写 | admin 可按 Note contract 管理普通 Note/Blog/content；旧 mistake 不增加公开写 | 原 slug URL 保留 | `notes.py` + Note service | 恢复旧 Note router/client，从备份恢复 |
| 根 `/manage` | 不可用/按现有 auth | 普通 Note/Blog/content 管理 | root entry retained | legacy Note/content APIs | 恢复 root manage shell |
| `/manage/*` workspace | 401/不可写 | 新 Question/Mistake/Review/Capture 私有写入唯一 owner | workspace nav retained | `/api/admin/*` | 恢复上一版本 workspace client/router |
| `/mistakes/review`、`/write-mistake*` | `/mistakes/review` 308 `/manage/review`；C 阶段 `/write-mistake*` 410 | 不作为私有学习 writer | old URL 进入观察/rollback | C 阶段 old `/api/review/*` 全端点 410 successor；恢复旧 client/router，旧 Note read state |
| `/guestbook`、RSS/sitemap/home Blog | 公开读取 | admin 按原 content/guestbook owner 管理 | 保留 | guest/content/blog services | 恢复对应 content/static index |

### Review cutover 状态机（禁止双写）

| state | source of truth | read/write owner | entry/exit 与指标 |
| --- | --- | --- | --- |
| A `LEGACY_SINGLE_WRITER` | Note SM-2 fields | legacy client/router/service 唯一 writer | entry=当前基线；exit=隔离 snapshot/hash 与消费者清单齐备；指标=旧写请求、错误、队列一致性 |
| B `ISOLATED_SHADOW` | runtime 仍 legacy；shadow 仅隔离 | legacy runtime writer；backfill/shadow 不写 runtime | entry=授权隔离 DB；exit=计数/当前调度语义/关系/权限一致，失败阈值为任一 mismatch、orphan、未知 owner 或错误率回归 |
| C `FREEZE_AND_CUTOVER` | 新 ReviewItem 当前调度状态 | 短停写后新 client/page/API 唯一 writer；旧 API 明确只读或 410 successor | entry=观察窗口、备份与 rollback identity 齐备；exit=观察期内旧写=0、重复/丢失=0、权限失败=0；任一阈值失败立即 rollback |

Rollback：恢复代码/路由版本与旧 client/router，从已验证 Note/隔离 snapshot 恢复并重跑完整性与权限查询；不依赖破坏性 012/013/019/020 downgrade，不双写补偿。

### Provenance / migration ledger 推荐架构（设计输入，未授权实现）

推荐 `legacy_note_migrations` 强 FK ledger：`source_note_id → notes.id`；`target_question_id → questions.id`、`target_mistake_id → mistakes.id`、`target_review_item_id → review_items.id` 明确 FK；另存 source version/hash、disposition、legacy review JSON/typed fields、`migration_notes`、idempotency key、status、created/updated/approved_by/approved_at。禁止用无约束字符串替代稳定关系。旧复习为空/语义不明时 ledger=`paused_pending_review`，不创建 ReviewItem；人工确认后才创建合法非空 `next_review_at`。schema、FK、G2 replay 尚未授权。

### 关系 owner、Attempt 与恢复合同

- `QuestionKnowledgePoint` 是 Question canonical 唯一 owner；generic `KnowledgePointLink` 不再作为 Question 权威。迁移需验证 generic→canonical、一致性、回滚；`question_service` update/get 必须共享该 owner 合同。设计合同已冻结；当前实现缺口属于后续 `NOT_VERIFIED`，不作为本轮 G1 blocker。
- Attempt 来源要求 router/client/service 一致传 `attempt_id`；Draft/Capture 必须记录 source、approval actor、approval timestamp、conversion order 和 audit provenance。当前 HTTP 缺口已登记，未修改实现。
- 恢复 identity 至少包括代码/路由版本、不可变输入 hash、隔离 DB snapshot/restore identity、完整性查询结果、恢复后 401/403/公开过滤检查；历史 downgrade 仅作风险证据，不作主 rollback。

### G1 recheck evidence / decision needed

本轮新增证据为上述当前路径 manifest、route matrix、无双写状态机、ledger/owner/Attempt/recovery 合同；均为文档设计输入，未执行 runtime/DB。G1 Architect/Reviewer 仍 `BLOCKED`，需两个独立 Worker 复核：消费者 owner/disposition 是否完整、永久 redirect 与只读公开边界是否可实现、cutover 失败阈值/rollback 是否可执行、ledger FK 是否覆盖 provenance、Question canonical owner 与 Attempt 链是否一致。G0=`PASS` 不继承到 G1；LSR-02 继续不启动。

## G1 第二轮冻结架构合同（历史快照，已被最终 G1 结论取代；单一机械方案，2026-08-23）

本节覆盖上一节方向性方案，作为 G1 recheck 的唯一合同。G1 只评“设计是否可进入 LSR-02”；当前产品实现、隔离 DB、G2/runtime/browser 证据均不在本轮判断内，仍为后续 `NOT_VERIFIED`。当前状态：LSR-01=`PARTIAL`/`[ ]`，G0=`PASS`，G1=`BLOCKED`，LSR-02 未启动。

### Consumer owner/disposition 清零

| consumer set | exact current paths/evidence | frozen owner/disposition |
| --- | --- | --- |
| public search/markdown | `backend/app/routers/search.py`; `backend/app/services/knowledge_markdown_service.py`; `src/lib/api/search.ts`; `src/lib/api/search.test.ts`; `backend/tests/test_i8_search_routes.py`; `backend/tests/test_i8_markdown_search.py` | `Note/Public Content owner` / `保留`；旧 mistake 公开结果按只读 Note route contract，聚合/私有学习替换另行执行 |
| RSS/sitemap/discover/home cards/static | `src/app/rss.xml/route.ts`; `src/app/sitemap.ts`; `src/app/discover/page.tsx`; `src/app/(home)/aritcle-card.tsx`; `src/hooks/use-blog-index.ts`; `public/blogs/index.json`; `public/blogs/categories.json` | `Note/Public Content owner` / `保留`（Blog/static index）；不迁移为私有 learning owner |
| content routes/nav | `src/lib/content-routes.ts`; `src/components/mobile-nav.tsx`; `src/components/vertical-nav.tsx`; `src/app/manage/components/manage-mobile-nav.tsx`及 nav tests | `Note/Public Content owner` / 普通 Note/Blog retained；mistake aggregate entry `replace` by route contract，移除 nav item |
| guestbook | `src/app/guestbook/page.tsx`; `src/lib/api/guest-messages.ts`；mistake links | `Guestbook + Note/Public Content owner` / 留言保留；mistake link replace 为 `/notes/{slug}`，不删除 guestbook |
| related public Note | `src/app/notes/[id]/components/related-knowledge-panel.tsx`; `knowledge_relations.py`; Note detail tests/clients | `Note/Public Content owner` / Note related/backlinks 保留；旧 mistake projection replace 为新 private Question/Mistake/Review services 的只读关联 |
| old mistake aggregate/components | `src/app/mistakes/page.tsx`; `src/app/mistakes/review/page.tsx`; `src/app/mistakes/components/weak-points-panel.tsx`; `weak-point-diagnosis.tsx`; `backend/app/services/recommendation.py`; `backend/app/routers/suggestions.py`; knowledge assistant/retrieval | `Question/Mistake/Review services owner` / `替换`；具体实现任务 LSR-04/LSR-16/适用 G4；不得由根 `/manage` 或 public aggregate 继续拥有 private writes |
| workspace search | `src/app/manage/(workspace)/search/page.tsx`、`src/lib/api/search.ts`、`/api/admin/search`；当前运行时是 Note 搜索 | `retained Note/Public Content admin search`；不得搜索/暴露 private Question/Mistake；未来 learning search 超出 LSR-01，新增须独立 G1/G3/G4 |
| import/export | 当前源码 runtime 零实现/零注册；外部 GitHub/export boundary 仅保留职责与历史线索 | `External GitHub/export boundary` / `保留`；任何新 runtime importer/exporter 发现立即 `TASK-BLOCK` |

### Exact route matrix（冻结）

| route | anonymous | admin | owner/transition | rollback |
| --- | --- | --- | --- | --- |
| `/mistakes` | HTTP 308 permanent redirect `/notes` | 同上；不提供 private write | `Note/Public Content` successor；nav 移除 aggregate | 恢复同版本 route artifact 与 nav，仅在回滚观察期 |
| `/notes/{slug}`、`/api/notes` | published&&!hidden 旧 Note read-only；新版 Question/Mistake 不匿名暴露 | 根 `/manage` 仅普通 Note/Blog/content admin | `Note/Public Content` read owner；旧 mistake 不可写 | 恢复旧 client/router 与 pre-cutover snapshot |
| `/manage` exact root | auth required | 仅普通 Note/Blog/content admin，绝不拥有 learning writes | legacy content owner | 恢复 root manage artifact |
| `/manage/<workspace route>` | 401/不可写 | private Question/Mistake/Review/Capture 唯一 write owner | `/api/admin/*` + workspace clients | 恢复 workspace artifact，再完整 auth check |
| `/write-mistake*` | C 阶段 HTTP 410 Gone | C 阶段 HTTP 410 Gone；不得写 Note | old route replace；successor 为 workspace flow | 仅按 rollback artifact 恢复，不继续双写 |
| `/api/review/*` | C 阶段 HTTP 410 Gone | C 阶段 HTTP 410 Gone | every endpoint returns `410` JSON `{code:"LEGACY_REVIEW_GONE",successor:"/api/admin/review/items"}`；禁止只读分支 | rollback 恢复旧 router/client，旧 Note 为唯一 writer |

public/mobile/vertical nav 统一移除 `/mistakes` aggregate；普通 Blog/RSS/sitemap/guestbook routes retained。

### Review cutover state machine（禁止双写）

| state | source-of-truth | read/write owner | exact entry/exit |
| --- | --- | --- | --- |
| A `LEGACY_SINGLE_WRITER` | Note SM-2 fields | legacy client/router/service 唯一 writer | entry=current baseline；exit=source archive/hash、route matrix、backup identity 齐备 |
| B `ISOLATED_SHADOW` | runtime 仍 Note；shadow 仅隔离 | legacy runtime writer；shadow/backfill zero runtime writes | entry=一次性隔离 DB；exit=3 independent cold-start cycles、每个关键操作≥20 synthetic samples、逐行 due/id/next_review_at UTC一致；不达标 rollback/不进入 C |
| C `FREEZE_AND_CUTOVER` | ReviewItem 当前调度 | 短停写后 new client/page/API 唯一 writer；旧 `/api/review/*` 全端点 410 | 观察窗口全程写冻结，仅可回滚 synthetic transactions；匿名401/non-admin403 单列预期 PASS；unexpected4xx/5xx=0、旧写请求=0、duplicate/orphan/hash drift=0、queue due/id/next_review_at UTC逐行 mismatch=0、console/page/request异常=0；任一非零立即 rollback |

Rollback 固定：停服务→恢复 code/route artifact→restore pre-cutover snapshot→重跑 count/PK/hash/FK/orphan/visibility/session negative→确认旧 writer 唯一。不得依赖 012/013/019/020 downgrade；生产真实写/delta 另需 G5。

### Ledger DDL/state-machine contract（设计冻结，未授权 schema 实现）

推荐唯一表 `legacy_note_migrations`：

| column | frozen type/constraint |
| --- | --- |
| `id` | UUID PK |
| `source_note_id` | UUID NOT NULL FK `notes.id` ON DELETE RESTRICT |
| `source_slug` / `source_url` | source slug plus bounded URL retained without truncation; `QuestionSource.source_ref='legacy-note:'||lower(source_note_id::text)` must bind exactly to source UUID/slug/url/hash |
| `target_question_id` | UUID NULL FK `questions.id` ON DELETE RESTRICT |
| `target_question_source_id` | UUID NULL FK `question_sources.id` ON DELETE RESTRICT |
| `target_qkp_ids` / `target_projection_ids` | INTEGER[] NULL; canonical QKP/projection ID sets, no projection role/order claim |
| `target_mistake_id` | UUID NULL FK `mistakes.id` ON DELETE RESTRICT |
| `target_review_item_id` | UUID NULL FK `review_items.id` ON DELETE RESTRICT |
| `target_question_draft_item_id` / `target_question_draft_id` | UUID NULL FK `draft_items.id` / `question_drafts.id` ON DELETE RESTRICT; active and paused both require both IDs plus their QuestionDraft row |
| `target_mistake_draft_item_id` / `target_mistake_draft_id` | UUID NULL FK `draft_items.id` / `mistake_drafts.id` ON DELETE RESTRICT; active and paused both require both IDs plus their MistakeDraft row |
| target bundle | composite `legacy_note_migration_target_bundle` carries all draft/final/QSource/QKP/projection IDs; QKP/projection arrays are sorted before hashing; `target_bundle_hash` CHAR(64) is immutable and cleared only by governed rollback |
| `target_question_draft_item_id` | UUID NULL FK `draft_items.id` ON DELETE RESTRICT; unique |
| `target_mistake_draft_item_id` | UUID NULL FK `draft_items.id` ON DELETE RESTRICT; unique |
| `source_hash` / `mapping_version` / `idempotency_key` | NOT NULL; unique `(source_note_id,mapping_version)`、unique `idempotency_key` |
| `state` | single state allowlist: `pending_mapping,ready,migrated_active,migrated_paused,retained_public_only,failed,rolled_back`；禁止 status/disposition 双义 |
| `manual_review_required` | `BOOLEAN NOT NULL DEFAULT TRUE`; state is the sole lifecycle column |
| legacy review | typed columns/JSON preserving `ef,interval,repetitions,next_review,last_reviewed` exactly; `migration_notes` JSON NOT NULL |
| mapped schedule | `mapped_next_review_at TIMESTAMPTZ`, `mapped_last_reviewed_at TIMESTAMPTZ`; due evaluated only as active state + next timestamp <= run-manifest `evaluation_time_utc`; no assumed `ReviewItem.due` |
| audit | `approved_by` UUID NULL FK admin identity, `approved_at`, `created_at`, `updated_at` timestamps |
| transition/events ACL | app role only `SELECT` on immutable allowlist/events; `INSERT/UPDATE/DELETE/TRUNCATE` revoked; event INSERT only through the SECURITY DEFINER transition function |

CHECK/transition rules（当前 addendum supersedes this historical wording）：`migrated_active` requires both draft-item and all three final targets non-null；`migrated_paused` requires both draft-item plus question+mistake non-null, review null, `manual_review_required=true`；`retained_public_only` requires all targets null, published&&!hidden and approval; `rolled_back` requires all targets null plus immutable rollback reference；allowlist transitions为 `pending_mapping→ready|failed|retained_public_only`、`ready→migrated_active|migrated_paused|failed`、`migrated_paused→migrated_active|rolled_back`、`migrated_active→rolled_back`、`failed→pending_mapping`，DB trigger/function rejects其它 transition and event UPDATE/DELETE。`review_items` canonical contract为 `mistake_id UUID NOT NULL FK mistakes.id`；旧 `target_type/target_id` 仅过渡只读、不再写。

### Canonical owners / approval provenance / recovery inputs

- `QuestionKnowledgePoint` 是 Question 唯一 read/write owner；update 必须 transactionally replace canonical rows；generic Question links 只读迁移输入，完成一致性 query 后停止写并按 G2 结果删除/回滚。当前实现未做该变更，属于后续 `NOT_VERIFIED`，不是本轮 G1 blocker。
- `MistakeDraftCreate` 的 client/router/service 必须全链传 `attempt_id`，并由 FK 校验；Capture/Draft provenance 唯一记录 source_hash、approval actor_id、approved_at、conversion_sequence、audit timestamps；正式转换顺序固定 QuestionDraft→Question→人工批准 MistakeDraft→Mistake→ReviewItem。
- 本轮 Draft schema delta 冻结 `DraftItem.source_type=legacy_note`、source/status/version/approval/target 字段，以及 QuestionDraft/MistakeDraft 内容、subject、reason、snapshot、`question_draft_id→question_id` exactly-one-of source switch；legacy import 的 `attempt_id` 始终 NULL，以上仍为后续实现/G2 `NOT_IMPLEMENTED`。
- Recovery input manifest 必须包含 source archive hash、route-matrix hash、DB custom-format snapshot identity、attachment manifest、Alembic head、code/route identity；restore 到明确一次性 DB 后运行 count/PK/hash/FK/orphan/visibility/session negative。C 冻结窗口 synthetic IDs 全记录；生产真实写/delta 另需 G5，当前不授权。

### G1 recheck matrix

| design question | frozen answer | evidence status |
| --- | --- | --- |
| all consumer owners | listed above; no `未知` disposition remains；not-present/import-export rules fail closed | contract frozen；runtime NOT_VERIFIED |
| route ownership | exact 308/410/root/workspace matrix above | contract frozen；implementation NOT_VERIFIED |
| review cutover | A/B/C, no dual-write, exact 3×20 thresholds, rollback sequence | contract frozen；isolated evidence NOT_VERIFIED |
| provenance/ReviewItem schema | DDL/FK/check/allowlist above；no downgrade rollback | design frozen；schema/G2 NOT_VERIFIED |
| canonical knowledge/Attempt | QuestionKnowledgePoint and Attempt chains above | design frozen；implementation/G2 NOT_VERIFIED |

本表为最终复核前快照：当时 G1 保持 `BLOCKED` 等待两个独立 Worker；该历史状态已由下文最终 G1 对账取代。

## G1 第三轮 tight blockers：最终机械冻结 addendum（历史快照，已被最终 G1 结论取代）

本节为 G1 recheck 的最终单一合同；当时 G1 仍待复核。其设计内容已被最终 G1 结论取代/确认，当前 canonical status 见文末；实现/DB/G2/runtime/browser 仍为 `NOT_VERIFIED`。

### Route、搜索与旧 Note mutation

- `/mistakes` 固定 HTTP `308` permanent redirect `/notes`；`/mistakes/review` 固定 HTTP `308` permanent redirect `/manage/review`，anonymous 随后由现有 auth boundary 处理，rollback 恢复旧 route artifact。
- `src/app/manage/(workspace)/search/page.tsx` + `src/lib/api/search.ts` + `/api/admin/search` 是当前 Note runtime search，owner=`retained Note/Public Content admin search`；不得搜索/暴露 private Question/Mistake。未来 learning search 不属于 LSR-01，新增须独立 G1/G3/G4。import/export runtime 继续以当前零实现/零注册的静态证据边界登记，外部 GitHub/export retained；新发现即 `TASK-BLOCK`。
- C 及之后，旧 Note 单条 `POST/PUT/PATCH/DELETE/promote` 且 `type=mistake` 统一 `410` JSON：创建 successor=`/api/admin/captures`，已有迁移对象 successor 指向对应 `/manage/*`/`/api/admin/*`；GET published&&!hidden 继续只读公开。batch 若含任一 legacy mistake，整批 `409` JSON、atomic no partial。根 `/manage` 不得绕过该矩阵。

### Review 观察操作与零阈值

C 的观察操作集合固定为：due queue read、stats read、0/1/2/3/4/5 各评分提交、duplicate rejection、concurrent conflict rejection、logout 后 401、non-admin 403、refresh/relogin consistency。每项每 cycle 至少 20 个 synthetic samples；3 个独立 cold cycles，每 cycle 重启 backend/frontend/browser 并重置 fixture；冻结持续到全部完成，30 分钟 hard timeout 即 rollback。expected 401/403/409 conflict 单列为成功，不计 unexpected error。unexpected 4xx/5xx、旧写请求、重复/孤儿/hash drift、queue due/id/`next_review_at` UTC 逐行不一致、console/page/request 异常均必须为 0；任一非零立即 rollback。仅允许可回滚 synthetic IDs，生产真实写/delta 另需 G5。

### Ledger 单一 state DDL 合同

唯一表名 `legacy_note_migrations`，唯一状态列 `state`（禁止 `status/disposition` 双义）。这是 LSR-02+G2 NEW DESIGN，`NOT_IMPLEMENTED`，不是当前 schema；仅当 `source Note.type='mistake'` 时建立 row，ordinary Note/Blog 永不进入 ledger。

| column | exact type / FK / constraint |
| --- | --- |
| `id` | UUID PK |
| `source_note_id` | UUID NOT NULL FK `notes.id` ON DELETE RESTRICT |
| `target_question_id` | UUID NULL FK `questions.id` ON DELETE RESTRICT |
| `target_mistake_id` | UUID NULL FK `mistakes.id` ON DELETE RESTRICT |
| `target_review_item_id` | UUID NULL FK `review_items.id` ON DELETE RESTRICT |
| `state` | frozen PostgreSQL typed enum `legacy_note_migration_state` with `pending_mapping,ready,migrated_active,migrated_paused,retained_public_only,failed,rolled_back` |
| `source_hash` | CHAR(64) NOT NULL |
| `mapping_version` | VARCHAR(64) NOT NULL |
| `idempotency_key` | VARCHAR(128) NOT NULL; unique with `source_note_id,mapping_version` and unique `idempotency_key` |
| legacy review fields | `legacy_ef FLOAT8`, `legacy_ef_bits CHAR(16)` from `encode(float8send(ef),'hex')`, typed interval/repetitions/next/last plus `legacy_review_json JSONB`; values/bits preserved exactly |
| `migration_notes` | JSONB NOT NULL |
| `approved_by` / `approved_at` | UUID NULL FK `users.id` ON DELETE RESTRICT / TIMESTAMPTZ NULL |
| `manual_review_required` | BOOLEAN NOT NULL DEFAULT TRUE |
| `rollback_reference` | CHAR(64) NULL |
| audit | `created_at`,`updated_at` TIMESTAMPTZ NOT NULL; append-only `legacy_note_migration_events` records every transition, including immutable `mapping_version`, nullable `target_bundle_hash`, and rollback-only `rollback_hash` digest binding |

Exact CHECK rules：`pending_mapping|ready|retained_public_only|failed|rolled_back` targets (including both draft-item targets) all NULL；`ready` requires source approval and all non-applicable conversion/schedule/rollback slots NULL；`retained_public_only` requires published&&!hidden plus `approved_by`+`approved_at`, while conversion/schedule/rollback slots and event IDs are NULL；`failed` and `rolled_back` clear every current approval slot/event ID (history remains only in append-only events), with rolled_back additionally requiring non-null immutable `rollback_reference`; `migrated_active` requires both draft-item/draft chains and Question/Mistake/ReviewItem final targets non-NULL, `manual_review_required=FALSE`, `rollback_reference IS NULL`; `migrated_paused` requires both draft-item/draft chains, question+mistake non-NULL, review NULL, `manual_review_required=TRUE`, rollback NULL；all other states require rollback NULL. Transition allowlist：`pending_mapping→ready|failed|retained_public_only`、`ready→migrated_active|migrated_paused|failed`、`migrated_paused→migrated_active|rolled_back`（人工确认后同事务创建合法 ReviewItem）、`migrated_active→rolled_back`、`failed→pending_mapping`；immutable `allowed_transition` table is exact-seeded before ACL revoke and sole SECURITY DEFINER function rejects all other transitions, stale expected state, direct target/state/migration_notes update, and event UPDATE/DELETE。

Applicability：published 旧 mistake 若成功迁移，原 Note 仍只读公开，ledger state=`migrated_active` 或 `migrated_paused`；`retained_public_only` 仅用于不可迁移但经批准继续公开的旧 mistake，targets 全 NULL 且 `approved_by/approved_at` 非空。每行保留 source_hash/source version/mapping_version；ordinary Note/Blog 不建立 row。

### Cross-entity invariant 与 canonical owner

`ReviewItem` 新增 canonical `mistake_id UUID NOT NULL FK mistakes.id ON DELETE RESTRICT`，停止写旧 `target_type/target_id`（仅过渡只读）。该字段是 LSR-02+G2 NEW DESIGN，`NOT_IMPLEMENTED`，不是当前 schema。Ledger service 必须在单事务 assert `mistakes.question_id = target_question_id` 且 `review_items.mistake_id = target_mistake_id`；数据库单列 FK 不能证明该跨表语义。完整性 query 必须检查 mismatch、missing target、orphan、duplicate 与 cross-subject，任何 nonzero 立即 rollback。`QuestionKnowledgePoint` 是 Question 唯一读写 owner；update transactional replace canonical，generic Question links 只读迁移输入后停止写。

Transition audit addendum (current LSR-02): `legacy_note_migration_events(id,ledger_id,source_note_id,from_state,to_state,actor_id,approval_kind,reason,details,source_hash,mapping_version,target_bundle_hash,rollback_hash,created_at)` uses the typed enum, non-null source/ledger/actor FKs, separate source/question-conversion/mistake-conversion/schedule/rollback approval semantics, append-only details/reason/hash/time, `rollback_hash` non-null only for rollback events and equal to the immutable rollback-audit digest, and DB trigger/function rejects event INSERT/UPDATE/DELETE/TRUNCATE except inside the SECURITY DEFINER function. The ledger also stores `transition_event_id` for non-rollback transitions and `rollback_event_id` for rollback; each is bound to the corresponding append-only event with source_note_id/mapping_version/source_hash/kind/actor. The sole `SECURITY DEFINER transition_legacy_note_migration(p_ledger_id,p_expected_from,p_to,p_actor_id,p_reason,p_source_note_id,p_mapping_version,p_expected_source_hash,p_target_bundle,p_rollback_reference,p_expected_rollback_hash,p_mapped_next_review_at,p_mapped_last_reviewed_at,p_event_details)` locks the row, checks expected state + immutable allowlist + target-state-specific approval actor/time/sequence + typed schedule fields + state CHECK, and for rollback recomputes the immutable audit JSON digest and checks inbound Capture/Attempt references before any clear. Active transition must change `manual_review_required` TRUE→FALSE only with a non-NULL mapped UTC next instant and active `ReviewItem.state='active'`/`algorithm='fixed_interval_v1'`; paused keeps TRUE and mapped-next NULL. For rollback it sets state/reference/rollback actor and NULLs all target columns/arrays/hash in one UPDATE before dependency deletion; any unexpected inbound reference raises `SNAPSHOT_RESTORE_REQUIRED` and leaves targets untouched. `migration_notes` may change only while state remains `pending_mapping`; after that it is immutable and later reasons go in event details. LSR-03 must include direct-SQL negative tests for forged event INSERT, transition-table mutation, stale expected state, event UPDATE/DELETE/TRUNCATE, missing approval and target mutation bypass; every expected rejection must leave zero committed target changes.

第十轮 guard 安全闭环（**supersedes the earlier prose in this subsection**）：`legacy_migration_owner` 为 `NOLOGIN` 且仅拥有对象/`SECURITY DEFINER` 函数；`session_user` 必须是精确 `legacy_note_adapter_runner`，并由其成员资格进入 `legacy_note_adapter`，普通 app/verifier 不可成为 owner。所有 owner DML 在紧邻单条语句前写入恰好 16 个 JSONB marker keys：`nonce,txid,op,table_schema,table_name,ledger_id,source_note_id,mapping_version,expected_source_hash,expected_from,expected_to,target_bundle_hash,event_id,approval_kind,actor_id,rollback_hash`。三类 guard 对每个适用 key 与 `OLD/NEW/TG_OP/TG_TABLE_SCHEMA/TG_TABLE_NAME`、事件 actor/from/to、rollback digest 做严格比对；缺失、额外、类型错误、错行、错 hash、伪造 GUC、nonce 重放或二次使用均拒绝，成功后清空 marker。ledger/events/rollback-audit 另有无条件 `BEFORE TRUNCATE` 拒绝。LSR-03 fixture 必须覆盖合法 create/approval/transition/rollback-loader PASS，以及普通 role direct DML、forged marker、wrong ledger/event/hash/nonce、replay/second-use 和三表 TRUNCATE FAIL。

第十一次补充：`legacy_migration_guard_nonces` 是 owner-owned registry，记录
nonce/txid/session/op/table/ledger/event/payload hash/created/consumed；setter
仅 owner 内部可执行，guard 在同事务 `SELECT FOR UPDATE` 并原子消费。Ledger
UPDATE 逐项拒绝 immutable provenance 或非本 approval/transition/rollback 允许的
列 diff；event 增加 `rollback_hash`，rollback event 必须等于 audit digest，其他
event 必须为 NULL。registry 与三张审计表均禁止 TRUNCATE/普通 role 直写。

### Attempt/Capture provenance 字段合同

`MistakeDraft.attempt_id` 为 `UUID NULL FK attempts.id ON DELETE RESTRICT` 且 unique（one attempt→at most one draft）。client optional 字段、router、service 原样传递，service 事务校验 `attempt.question_id` 与 draft source。Capture→Draft 记录 `source_capture_id`、source draft IDs；approval 字段为 `approved_by UUID FK users.id`、`approved_at TIMESTAMPTZ`、`conversion_sequence INT CHECK (>0, strictly increasing)`、`source_hash CHAR(64)`。正式转换前 approval 字段必须非空且顺序递增。上述 attempt/approval 字段均为 LSR-02+G2 NEW DESIGN，`NOT_IMPLEMENTED`；若当前表缺字段，不得写成当前 schema。

### Recovery runbook freeze

输入固定包含 source archive hash、route matrix hash、DB custom-format snapshot identity、attachment manifest hash（逐文件验证）、Alembic head、code/route identity。先写仓库外 immutable rollback JSON/hash；logical rollback 由唯一 transition function 在同一事务设置 `rolled_back` + `rollback_reference` 并原子 NULL 全部 draft/final/source/projection target columns/arrays/hash，然后严格删除 ReviewItem→Mistake projection→Mistake→MistakeDraft→Mistake DraftItem→QSource/QKP/generic links→Question→QuestionDraft→Question DraftItem；legacy Note 不删。若发现 legacy import 不应生成的 Capture/Attempt inbound reference 或任一 RESTRICT 失败，事务必须 fail 并改走 snapshot restore。restore 到明确一次性 DB；验证 count/PK/hash/FK/orphan/visibility/session negative、ledger state/targets、attachments、Question/Mistake/Review relations。C 冻结仅 synthetic IDs 且逐项清除；当前 LSR-02 区分 logical rollback（ledger 可审计为 `rolled_back`）与 disaster snapshot restore（恢复 pre-migration DB，ledger 行不存在，不能声称 `rolled_back`）；不得依赖 downgrade。生产 delta 另需 G5，当前不授权。

### G1 recheck matrix（最终）

| item | frozen design answer | current evidence state |
| --- | --- | --- |
| consumer/search owner | all listed consumers have retained/replaced/out-of-scope owner; Note workspace search retained admin search；import/export zero runtime implementation/registration | contract frozen；runtime NOT_VERIFIED |
| route/mutation | exact 308/410/GET-read-only/batch-409 matrix | contract frozen；implementation NOT_VERIFIED |
| review observation | exact operation set, 3×20 cold cycles, hard timeout, zero thresholds, rollback | contract frozen；isolated evidence NOT_VERIFIED |
| ledger/cross-entity | single `state`, exact FK/CHECK/allowlist, transactional assertions and SQL query | contract frozen；schema/G2 NOT_VERIFIED |
| Attempt/provenance/recovery | exact fields, FK, approval ordering, attachment/hash restore runbook | contract frozen；implementation/G2 NOT_VERIFIED |

最终独立复核：`lsr01-g1-architect=PASS`；`lsr01-g1-reviewer=PASS_WITH_NOTES`。当前 G1=`PASS`，仅表示机械架构合同足以进入 LSR-02 设计；当前源码、schema、数据库、runtime、G2/G3/G4 仍为 `NOT_VERIFIED`。本历史段记录的是 LSR-02 Owner 交付前状态；当前 LSR-02 manifest 在下方，仍为 `PARTIAL/[ ]`。

以上验收尚未运行；当前实现是否满足仍为 `NOT_VERIFIED`/后续任务输入。

### 最终 QA/Data 收束记录（当前，待复核）

- QA=`PASS`：确认文档一致性、owner 细节与静态 mapping 验收满足；未运行产品测试、DB、runtime、browser。
- Data=`PASS`：确认 ledger applicability、ordinary Note 排除、source hash/version 与强 FK 设计边界满足静态 mapping；仍未执行 schema/G2/数据完整性验证。
- Primary Owner 不自批；LSR-01 已勾选、`PASS`，仅限静态 mapping 范围。Reviewer=`PASS_WITH_NOTES`；G0=`PASS`；G1 Architect=`PASS`、Technical Reviewer=`PASS_WITH_NOTES`、combined G1=`PASS`；G2-G4=`NOT_VERIFIED`；G5=`NOT_AUTHORIZED`。本段为 LSR-01 历史收束；当前 LSR-02 见下方 manifest，仍 `PARTIAL/[ ]`。

## LSR-02 最终静态 manifest

本节是 LSR-02 最终静态 manifest。其合同范围已由独立 Reviewer=`PASS_WITH_NOTES`、Verifier=`PASS` 收束为 `PASS/[x]`；这不表示迁移、schema、DB、runtime、browser 或 G2 已通过。
本节及 `design.md` 的 LSR-02 当前冻结合同 supersede 前文标注的 LSR-00/LSR-01 历史建议；历史数字、旧 status/disposition wording 和旧 Gate 状态不得覆盖当前静态 `PASS` 与运行时 `NOT_VERIFIED` 边界。

| field | value |
| --- | --- |
| task_id / worker_id | `LSR-02` / `lsr02-owner` (`Senior Data Engineer`, Primary Owner) |
| reviewer / verifier | `lsr02-reviewer` (`Principal Software Architect`) = `PASS_WITH_NOTES`; `lsr02-verifier` (`Senior QA / SDET`) = `PASS`; scope is static contract only, DB/G2 remain `NOT_VERIFIED` |
| source identity | LSR-01 final static manifest; current `backend/app/models`, schemas, services/routers, Alembic files; user three-item contract; pasted goal |
| target identity | only this workflow's five files; design/requirements/tasks/validation updated |
| source snapshot/DB | no source data snapshot; no DB connection/query; no service/browser |
| implementation | no product/schema/Alembic/migration/test/script changes |
| contract coverage | Note fields + derived `search_vector`; Question/QuestionSource/QKP/Mistake/ReviewItem; canonical KP projection; ledger + draft-item FK chain + events; Subject/KP/chapter/019; Attempt/Capture provenance; queues; source_ref; EF bits; concurrency; logical/snapshot rollback; current routes; idempotency; exhaustive SQL/fixtures/restore |
| status | `PASS`; checkbox `[x]`; scope is static migration contract only |
| LSR-03 | `[ ]` `FAIL`; see the current manifest and boundary incident at the top of this file |
| G0/G1 | existing `PASS`/`PASS_WITH_NOTES` design-layer decisions not re-approved by Owner |
| G2/G3/G4/G5 | `NOT_VERIFIED` / `NOT_VERIFIED` / `NOT_VERIFIED` / `NOT_AUTHORIZED` |
| cleanup | no external artifacts created; dirty worktree preserved; no staged/commit/push |

### LSR-02 Reviewer/Verifier findings and remediation ledger

| finding | current remediation in five-file contract | evidence state |
| --- | --- | --- |
| Reviewer `CHANGES_REQUIRED`: search_vector omitted from source invariants | `design.md` hashes `CASE WHEN search_vector IS NULL THEN '<NULL>' ELSE '<VALUE>' || search_vector::text END`, marks it derived/retained, forbids private target copy, requires old-row/search parity | design-only; DB/search `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: Mistake KP ownership ambiguous | `QuestionKnowledgePoint` is sole canonical owner; Mistake `KnowledgePointLink` is derived ID-set projection only; role/order lossiness is explicit and SQL does not claim projection role/order | schema/runtime `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: import could bypass drafts | dedicated `legacy_note_migration_adapter` (not unchanged services) owns UUIDv5, source_type, dual draft approvals/conversion, QuestionSource and paused semantics; direct Mistake insert/generic Question link forbidden | adapter/schema `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: EF numeric loses bits | `legacy_ef FLOAT8` + `legacy_ef_bits CHAR(16)` using `float8send`; replay compares bits | DB replay `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: rollback conflated restore/order | external audit first; governed transition atomically sets rolled_back + rollback_reference + all target FKs NULL, then fixed FK deletion order; unexpected Capture/Attempt routes to snapshot restore; restored pre-migration DB has no rolled_back ledger row | restore `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: source concurrency absent | `REPEATABLE READ/SERIALIZABLE`, source `FOR UPDATE`, post-lock hash and commit-time drift check | runtime `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: chapters/019 cases absent | three explicit empty/nonempty-unmapped/nonempty-approved-transform fixtures | Alembic replay `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: SQL/fixture coverage incomplete | exhaustive checklist covers ledger cardinality, hashes/bits, QSource, mirrors, QKP/projection, drafts, schedule, Note/search_vector, replay/mapping versions and all independent fixtures | SQL execution `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: state transitions not DB-enforced | typed enum, immutable allowed-transition table, sole SECURITY DEFINER transition function, app-role revoke, actor/details events, pending-only migration_notes, negative direct-SQL tests | schema/negative tests `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: retained_public_only approval absent | canonical DDL requires `approved_by` + `approved_at` and public source predicate | schema `NOT_VERIFIED` |
| Reviewer `CHANGES_REQUIRED`: route matrix only historical | current design addendum promotes 308/410/409 matrix to LSR-02 input | implementation `NOT_VERIFIED` |
| Historical Verifier `FAIL` | Earlier findings were design-only remediation; final bounded recheck later closed the remaining static issues | superseded by LSR-02 Reviewer=`PASS_WITH_NOTES`, Verifier=`PASS`; G2/G3/G4 remain `NOT_VERIFIED` |

| Second-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | Exact rollback atomic-clear order, full draft/final queue targets, dedicated adapter, ID-set-only projection, NULL-sentinel hash, scoped SQL/mirror/EF/replay checks, typed enum/transition function/events and adapter/rollback fixtures added in 2026-08-24 addendum | design-only; independent re-review pending |
| Third-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | 8.10 now defines mapped schedule/evaluation time, complete scoped SQL cardinality/FK/visibility/approval/QKP/ReviewRecord/replay checks; Draft schema/source switch; exact adapter signature/errors; composite target bundle and full ACL/SECURITY DEFINER transition; executable helper signatures and TEMP snapshot/run-manifest schema | design-only; independent re-review pending |
| Fourth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | INTEGER[] target ID unification; canonical_payload typed source snapshot with independent UTF-8 SHA-256 recomputation; exact provenance mirror targets and essay refusal; strict/safe malformed-ID handling; complete Draft→final/cross-entity assertions; schema-qualified SECURITY DEFINER + role/ACL/nonce guard; explicit pgcrypto isolated prerequisite; expanded negative fixtures | design-only; independent re-review pending |
| Fifth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | canonical_payload required-key/type and row/archive/live-Note binding including top-level `legacy_ef_bits` and wrong-note rejection; invoker helper least-privilege ACL with re-raised permission errors; complete MistakeDraft/Mistake mirror and reverse target-kind nulls; separate source/conversion/schedule/rollback approval identities; active ReviewItem state+`fixed_interval_v1`; manifest exact-one fail-closed assertion; retained source/hash parity | design-only; independent re-review pending |
| Sixth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | owner-only pending/approval execution path with independent actors/event IDs; source-code exact options normalization and stem/analysis mirrors; Note TEXT knowledge-point/tag normalization; bidirectional archive/ledger raw JSON and full field binding; explicit mapping scope; source_title helper; executable inbound Capture/Attempt rollback guard; microsecond UTC canonicalization; finite EF checks; pgcrypto PUBLIC/app ACL | design-only; independent re-review pending |
| Seventh-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | approval owner functions now write independent source/question/mistake/schedule event IDs and transition only validates locked IDs/actors; transition target checks compare qdi/mdi to their own approval actors and MistakeDraft question FK to target Question; source-accurate option objects/answer_data/stem/analysis/mistake mirrors; archive↔snapshot↔live Note row/hash/raw-review JSON binding; source URL/title and mapping-version fail-closed scope; executable Capture/Attempt rollback guard and microsecond/finite EF/pgcrypto contracts | design-only; independent re-review pending |
| Eighth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | complete executable owner-function bodies/signatures/ACL and stale state/hash/sequence locks; empty/invalid options and exact `true_false` answer-data helper; failed→pending clears approvals/events/targets/notes and requires new source approval; explicit all-dispositions/final/retained SQL scopes with one-row manifest fail-closed; rollback audit JSON canonical digest plus atomic inbound Capture/Attempt guard; one normative canonical-key set including source_note_id/source_url/legacy_review_json/legacy_ef_bits; verifier digest-only pgcrypto grant | design-only; independent re-review pending |
| Ninth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | retained query syntax; explicit approval kind/state matrix and terminal rejection; full pending idempotency/provenance comparison and hash-derived snapshot_ref; owner-side complete live Note canonical binding; ready→failed and rolled_back approval-slot clearing; executable transition seed and three schema-qualified guard functions/triggers with ACL | design-only; independent re-review pending |
| Tenth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | explicit threat/role model with NOLOGIN owner and exact adapter session; structured 16-key marker with OLD/NEW/TG_* binding and strict type/key checks; owner create/approval/transition/rollback-loader markers immediately before each DML; one-use nonce consumption; rollback hash binding; unconditional ledger/events/audit TRUNCATE guards and ACLs; legitimate and forged/wrong/replay/second-use/truncate fixtures | design-only; independent re-review pending |
| Eleventh-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | owner-only nonce registry with payload hash, row lock and atomic consumption; private setter ACL; executable ledger immutable/provenance diff and approval-kind/event binding; `transition_event_id`; event `rollback_hash` CHECK and digest binding; registry cleanup/rollback semantics and replay/wrong-payload fixtures | design-only; independent re-review pending |
| Twelfth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | pending INSERT now projects all typed legacy/schedule fields from the locked canonical payload; active transition enforces manual TRUE→FALSE only with mapped UTC next instant and active fixed-interval ReviewItem; QKP/projection arrays are non-null-free, deduplicated, strictly ascending canonical relation sets; approval/transition/rollback event checks bind ledger/source/mapping/hash; owner-only consumed-nonce cleanup and explicit minimum owner SELECT ACL; manifest/archive/all-dispositions/source scopes reject empty acceptance runs | design-only; independent re-review pending |
| Thirteenth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | pending canonical JSON validates every required key's type/nullability, UUID/date/RFC3339-microsecond-UTC/array/object shape and integer range before any cast; `legacy_ef_bits` is TEXT-validated at exact 16 lowercase hex bytes before CHAR(16) storage; every public hash input is TEXT with exact lowercase-hex validation; transition reason/required parameters use fixed errors; cleanup is maintenance-runner-only; replay requires five-way count equality and bidirectional source-note set equality, with failed/rolled_back never accepted as final success | design-only; independent re-review pending |
| Fourteenth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | pending/approval 前以 `char_length`（QuestionSource `VARCHAR(300)` 字符语义）同时校验参数、canonical 与锁定 live Note title，超长固定 `SOURCE_TITLE_TOO_LONG` 并由独立 rejection 记录路径落入 manual/failed；`ready` 防御复检；`lsr02_source_snapshot`、独立 `lsr02_archive_rows`、独立 `lsr02_archive_manifest`、all-dispositions 与 live source 五方分别计数/hash/set 绑定；replay 先显式非空/等数，再用 FULL OUTER JOIN 与双向 EXCEPT 检出 missing/extra 并逐行比较 IDs/hash；统一 Note 非空/可空/type 矩阵贯穿 owner/live/snapshot/archive/replay，规范化 knowledge_points/tags 为非空数组 | design-only; independent re-review pending |
| Fifteenth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | executable owner-only rejection writer with exact TEXT hash boundary, source lock, title/type/hash/snapshot/idempotency/actor checks, `manual|failed` disposition, immutable table and append-only/ACL guards; pending rollback then independent SERIALIZABLE rejection transaction; rejection excluded from positive scope; replay manifest/result now carries and compares every source/question/mistake/schedule approval actor/time/sequence/event plus transition/rollback identity; nullable EF/interval/repetitions acceptance branches removed | design-only; independent re-review pending |
| Sixteenth-round Reviewer `CHANGES_REQUIRED` / Verifier `FAIL` | rejection writer now calls the shared owner-only live canonicalizer and recomputes the source hash before title acceptance; `legacy_note_migration_rejections.reason` is closed to `SOURCE_TITLE_TOO_LONG`; rolled_back replay has an independent manifest/count/FULL OUTER/set audit for rollback actor/event/reference/hash, transition event, and immutable audit digest; last_reviewed uses UTC microsecond text throughout; title is exact raw UTF-8 with no trim/truncation; the 16-key nonce marker is explicitly limited to ledger/events/rollback-audit while rejection uses separate owner/session/ACL/append-only enforcement | design-only; independent re-review pending |
| Final bounded recheck | payload validation now precedes live canonicalization/parity, preserving fixed `CANONICAL_PAYLOAD_INVALID` versus `SOURCE_DRIFT`; `legacy_uuid_or_null(TEXT)` explicitly revokes `PUBLIC/app_role` and grants only adapter/verifier; Reviewer=`PASS_WITH_NOTES`, Verifier=`PASS` | LSR-02 static contract `PASS`; LSR-03 DB/G2 `NOT_VERIFIED` |

No finding is represented as a product fix or runtime result. Independent Reviewer/Verifier must re-run and may keep this task `PARTIAL`, return `FAIL/BLOCKED`, or require another bounded revision.

### LSR-03 SQL/fixture checklist frozen by LSR-02

Every row below is a required isolated-DB assertion; `nonzero/unexplained` means `FAIL` and rollback. No item was executed in LSR-02.

| check group | required contract |
| --- | --- |
| source/disposition cardinality | every `type='mistake'` source has exactly one final ledger disposition row for a mapping version; ordinary Note/Blog has zero rows; aggregate source/target/draft counts and duplicate source/target IDs |
| run/snapshot scope | executable `lsr02_run_manifest(run_id,mapping_version,evaluation_time_utc,source_snapshot_version,archive_rowcount,archive_hash)` first asserts exactly one current mapping row (0 or 2 is FAIL, never empty-JOIN PASS), `archive_rowcount>0`, and five independent nonzero counts—`lsr02_source_snapshot`, `lsr02_archive_rows`, `lsr02_archive_manifest`, all-dispositions, live source—each equal the manifest; an empty batch is `NOT_RUN`, never PASS; `source_note_id` sets are checked both directions across live source/dispositions and snapshot/archive rows/manifest; failed/rolled_back remain counted dispositions but cause explicit non-final acceptance failure and never enter final target success; every archive/source/canonical/live query explicitly filters `:mapping_version`; `lsr02_source_snapshot` has PK/unique/hash/rowcount/version checks; canonical required keys/types, typed projection, `id/source_note_id/type='mistake'/slug`, every exact field, source URL, raw `legacy_review_json`, `legacy_ef_bits`, archive→snapshot and snapshot→archive per-row binding plus aggregate rowcount/hash and locked live-Note parity are checked; wrong-note self-consistent payload fails; loader hash is never trusted |
| typed/hash boundary | pending owner function checks every required JSONB key's type/nullability and UUID/date/RFC3339-microsecond-UTC/array/object/range shape before casts; date/timestamp round-trips preserve exact text; interval/repetitions are bounded nonnegative integers; `legacy_ef_bits` is TEXT-checked for exact 16 lowercase hex bytes before `CHAR(16)` conversion; all callable source/expected/rollback/bundle hash inputs are TEXT, exact 64 lowercase hex checked before explicit `CHAR(64)` storage; malformed values map only to closed `CANONICAL_PAYLOAD_INVALID`, `EF_NONFINITE`, `SOURCE_HASH_INVALID`, `ROLLBACK_HASH_INVALID` or `INVALID_REASON_OR_REQUIRED_PARAMETER` errors |
| immutable source | source hash, `legacy_ef` FLOAT8 and `legacy_ef_bits`, all typed legacy review values + raw `legacy_review_json`, source URL/title/revision/status/hidden/version are equal bidirectionally to snapshot; source `content/slug/status/hidden/revision/search_vector` unchanged; knowledge_points TEXT and tags relation use exact current-source normalization |
| source concurrency | `REPEATABLE READ`/`SERIALIZABLE`, source `FOR UPDATE`, post-lock hash and commit-time status/hidden/version/search_vector recheck; drift produces failed row and zero targets |
| QuestionSource | scoped `source_ref IS NULL OR regex-fail` and exact `source_ref='legacy-note:'||lower(source_note_id::text)` checks; source_url/slug/type/title/hash binding exact; malformed generic IDs never cast; collision is zero |
| retained/ordinary | `retained_public_only` has published/unhidden source, separate source approval actor/time, every target column/array/hash NULL, and the same snapshot/source-hash/canonical-payload/slug/status/hidden/revision/search-vector parity; ordinary Note/Blog has zero scoped ledger/target rows |
| helper definitions | schema-qualified invoker helpers have exact provenance signatures including `source_title`, no arbitrary source/LIMIT, explicit TEXT-vs-JSONB comparisons and least-privilege SELECT+EXECUTE grants; insufficient privilege is re-raised (not swallowed), malformed/unsupported data is false; options normalization follows current `draft_service` list[str]→`[{key:chr(65+ordinal),text:value}]` conversion for single/multiple choice; essay is `ESSAY_MANUAL_REQUIRED` |
| Question mirrors | deterministic adapter mirror function/rule validates title/subject/question text/answer/explanation/options/type/difficulty for each approved question type; no universal `answer_data.value` assumption; visibility private, version valid |
| taxonomy | QKP canonical subject consistency, PK uniqueness, INTEGER ID-set arrays with no NULL/duplicates and strict ascending order, exact bidirectional `ARRAY(SELECT DISTINCT ... ORDER BY id)` equality for QuestionKnowledgePoint and Mistake projection links, strict UUID validation for legacy string targets via safe helper, projection duplicate/orphan/cross-subject zero; role/order remain canonical-QKP-only and lossiness is recorded |
| draft chain | active and paused each have Question DraftItem+QuestionDraft IDs, Mistake DraftItem+MistakeDraft IDs, Question and Mistake; active additionally has exactly one current ReviewItem, paused has none; `draft_type=question|mistake`, source/status/version/approval actor-time/sequence/hash and target FK chain valid; qdi has question target only and mdi mistake target only; qdi approval actor equals question-conversion approval and mdi approval actor equals mistake-conversion approval; every QuestionDraft→Question mirror includes stem_md/question_text, analysis_md/explanation, options normalization, answer/type/difficulty; MistakeDraft→Mistake mirror includes `my_answer`, difficulty, reason/category, question relation and final `question_text/correct_answer/analysis` from the corresponding distinct draft fields (analysis is not mistake_reason); `mistakes.question_id=target_question_id` and `review_items.mistake_id=target_mistake_id`; adapter Question conversion precedes Mistake conversion; no direct final Mistake |
| Review | active ReviewItem exact `state='active'`, `algorithm='fixed_interval_v1'`, interval/repetitions/next/last UTC and ID; due is derived from active state + mapped next timestamp <= run-manifest evaluation_time_utc, never from assumed `ReviewItem.due`; paused has no ReviewItem; migrated source has no ReviewRecord; paused→active requires a distinct schedule approval event |
| approval execution | owner-only executable `create_legacy_note_migration_pending` inserts pending with all approval fields NULL and every typed legacy/schedule field populated from the locked canonical payload; owner-only `record_legacy_note_migration_approval` separately writes source/question/mistake/schedule approval events and exact actor/time/sequence/event IDs; every event EXISTS check binds `ledger_id`, source Note through the ledger, mapping version, source hash, kind, actor and event ID; qdi/mdi approval actors must match their corresponding ledger actors; active transition actor is only schedule actor and changes manual TRUE→FALSE only with mapped UTC next + fixed-interval ReviewItem; paused remains manual TRUE with mapped-next NULL; rollback actor is independent authorized admin; app_role/ordinary adapter direct INSERT/UPDATE is rejected; failed→pending clears all prior approval/event/target/note fields and requires a new source event/hash |
| rollback inbound references | scoped SQL checks CaptureItem, Attempt, and MistakeDraft.attempt_id inbound references; any row returns `snapshot_restore_required=true` and logical rollback is forbidden |
| EF finite | ready/active/paused legacy EF must be finite and non-null under the current matrix; executable `legacy_ef::text IN ('NaN','Infinity','-Infinity')` or `legacy_ef_bits IS DISTINCT FROM encode(float8send(legacy_ef),'hex')` checks are nonzero failures, and NULL/nonfinite fixtures route to manual/failed before acceptance |
| replay/mapping versions | `lsr02_replay_manifest` and final acceptance scope are both explicitly counted and must be >0 and equal; FULL OUTER JOIN plus both-direction `(source_note_id,mapping_version)` EXCEPT detects missing/extra rows before per-row comparison; each matched row returns exactly the same ledger, all draft-item/draft/final/QSource/QKP/projection/ReviewItem IDs and hashes, and source/question/mistake/schedule approval actor/time/sequence/event IDs plus transition/rollback identity; an empty/partial/extra replay is FAIL and its negative fixture uses isolated temp relations, never mutating positive acceptance; same mapping version permits one immutable row; next mapping version requires explicit new row and leaves previous immutable |
| rollback replay (independent scope) | `lsr02_rollback_replay_manifest` is a separate negative/restore run, not a positive-final JOIN; rolled_back ledger count and replay count are each >0 and equal, FULL OUTER plus both-direction source/mapping EXCEPT catches missing/extra rows, and each row compares source_hash, ledger/state, rollback_actor_id/event_id/reference/hash, transition_event_id, and rollback-audit digest. Wrong-ledger/source/mapping/hash, event, reference, actor, or audit digest is nonzero FAIL; a rollback-only run never makes positive acceptance PASS |
| search/public | old Note row/search_vector unchanged using NULL sentinel token; public query result parity if a rebuild is explicitly exercised; old public source remains read-only, new objects private |
| chapters/019 | empty replay PASS; non-empty without mapping fails before 019; non-empty explicit pre-019 transform then 019 preserves count/order/status/provenance |
| state/audit/rollback | typed enum + executable exact seed of immutable allowlist + schema-qualified sole SECURITY DEFINER transition function (`SET search_path=pg_catalog,legacy_migration`); separate source/question/mistake/schedule/rollback actor/time/sequence fields and event kinds are checked; explicit kind×state approval matrix rejects terminal/failed approvals; app direct UPDATE/function call rejected by `guard_legacy_note_migration()` trigger; immutable source/provenance diff and approval/event time/sequence binding are executable; every approval/transition/rollback event binds `ledger_id`, `source_note_id`, `mapping_version`, `source_hash`, kind, actor and event ID; `transition_event_id` binds non-rollback transitions; active manual TRUE→FALSE and mapped schedule fields are transition-only; QKP/projection arrays are exact canonical relation sets; `guard_legacy_note_migration_event()` rejects forged INSERT and UPDATE/DELETE/TRUNCATE and enforces rollback-only `rollback_hash`; `guard_legacy_migration_rollback_audit()` enforces immutable audit rows; owner-only nonce registry is row-locked and atomically consumed; cleanup can delete only consumed rows before cutoff; event UPDATE/DELETE and stale expected state rejected; legitimate adapter transition must PASS; logical rollback first atomically clears all approval slots/target FKs and marks rolled_back, then deletes in fixed FK order; unexpected Capture/Attempt routes to snapshot restore |
| forged writes | direct event/ledger/registry INSERT/UPDATE/DELETE/TRUNCATE, forged marker, wrong payload hash/ledger/event/session/txid, replayed or second-use nonce, direct function call by `app_role`, event UPDATE/DELETE/TRUNCATE, transition-table INSERT/UPDATE/DELETE/TRUNCATE, direct ledger typed-field/state/target/migration_notes UPDATE and stale expected transition all rejected with zero committed changes |
| extension/roles | isolated replay first verifies `public.pgcrypto` prerequisite, extension ownership/version and rollback; `legacy_migration_owner`/`legacy_note_adapter` are NOLOGIN, exact `session_user=legacy_note_adapter_runner` is the separately provisioned adapter execution login, `legacy_migration_maintenance_runner` is the only cleanup login and the only role with cleanup schema USAGE/EXECUTE, while adapter/adapter-runner/verifier have cleanup EXECUTE revoked; ordinary app/verifier has no EXECUTE or membership; owner has explicit minimum SELECT on every existing validation table; cleanup deletes only consumed rows before cutoff; `legacy_note_verifier` receives only `public.digest(bytea,text)` EXECUTE plus minimum SELECT, never gen_random_* or writes |

Required independent fixtures: manifest missing/duplicate mapping rows (0/2 fail closed), archive rowcount=0, empty source snapshot/all-dispositions/source scope and mismatched manifest rowcount all FAIL (not PASS/NOT_RUN); archive-manifest count mismatch and source-note set missing/extra in either EXCEPT direction FAIL; failed-only/rolled_back-only disposition is counted in all-dispositions but fails final acceptance; approved `retained_public_only` public-but-unmappable source with snapshot/hash/payload parity; owner-function pending creation with every typed legacy field and manual schedule shape; canonical payload wrong JSON type/nullability, malformed UUID, invalid RFC3339/microsecond or date round-trip, wrong array/object shape, integer overflow/negative range and native-cast shielding all return fixed `CANONICAL_PAYLOAD_INVALID`; `legacy_ef_bits` NULL/empty/uppercase/prefix/15-or-17-byte and EF nonfinite fixtures fail closed; public hash TEXT inputs NULL/uppercase/short/long/prefix fail before storage/cast; pending replay with each immutable provenance mismatch (snapshot_ref/canonical hash/source URL/raw review/idempotency) rejected; distinct question/mistake approval actors and event IDs plus cross-ledger event reference rejection; each approval kind on allowed and forbidden states including terminal/failed; ready→failed clears all approval slots/events/targets and failed→pending requires fresh source approval; deterministic paused→active and ready→active with manual TRUE→FALSE, mapped UTC next and fixed-interval ReviewItem; paused schedule/date ambiguity remains manual TRUE/mapped-next NULL; qdi/mdi approval-actor mismatch; source_ref/source_title collision; duplicate target; due/overdue UTC plus active state/algorithm; helper PASS as verifier plus app-role permission denial; verifier `digest(bytea,text)` PASS but `gen_random_uuid/gen_random_bytes` and any INSERT/UPDATE/DELETE FAIL; unchanged search_vector with NULL and non-NULL sentinel cases; full dual-draft chain through `legacy_note_migration_adapter`; exact source Note knowledge_points/tags normalization; essay→`ESSAY_MANUAL_REQUIRED`; empty options for short/true-false, extra-key/non-string option object and true_false invalid-answer manual route; failed→pending stale approval/event/target reuse; exact Question/Mistake/Draft/Review cross-entity mirror including stem/analysis, reverse target-kind nulls and list→option-object shape; QKP/projection NULL/duplicate/permutation/subset/superset arrays all FAIL and exact canonical arrays PASS; malformed legacy target ID; chapters three-case; illegal state/event transitions; stale expected state; forged marker; direct function call; forged event INSERT; cross-ledger event ID; transition-table mutation; direct typed-field/target/migration_notes/nonce-registry update; wrong marker payload hash/ledger/event/session/txid, nonce replay/second-use/cross-transaction; rollback event wrong/null hash and audit digest mismatch; executable Capture/Attempt inbound rollback guard; rollback audit wrong digest/reference and FK order; unexpected Capture/Attempt inbound reference; cleanup attempts on unconsumed/new rows, wrong session and over-limit cutoff, adapter/adapter-runner cleanup EXECUTE denial, plus consumed-before-cutoff deletion PASS; each of the three guard trigger direct-mutation paths; owner-only consumed-nonce cleanup and aborted-transaction restoration. All are synthetic only.

Fourteenth-round fixture additions are independent runs: parameter/canonical/live title length 301 fails with `SOURCE_TITLE_TOO_LONG` before ledger INSERT or approval, and its separate rejection record is manual/failed with no ready/retained target; transition-to-ready repeats the same check. `lsr02_archive_rows` is loaded from immutable archive rows while `lsr02_archive_manifest` is loaded from an independent expected-hash manifest; snapshot/archive-row/archive-manifest/disposition/live-source count and two-way source-set mismatches each fail. Replay empty, one missing, and one extra rows fail through explicit count/FULL OUTER checks; these negative temp relations are discarded and cannot contaminate the positive acceptance run. Null/wrong-type fixtures for every normative required field fail before cast; `knowledge_points` and `tags` use normalized non-null arrays with explicit empty semantics, while nullable fields retain their single frozen type. All are synthetic only.

Fifteenth-round fixtures additionally call the exact rejection writer through the authorized adapter role and assert deterministic ID on identical input; direct table INSERT, UPDATE, DELETE, TRUNCATE, forged marker/session, wrong actor, wrong source type, title ≤300, title/hash/snapshot/idempotency mismatch, invalid disposition/reason and duplicate conflicting input all fail with zero committed rows. The positive title-error path proves the original pending transaction rolled back, then the independent SERIALIZABLE writer transaction re-locks the live Note and creates only `disposition=manual|failed`; rejection rows are absent from `lsr02_all_dispositions`, final target counts and positive replay. Replay negative fixtures independently alter each approval actor, approved_at, sequence, event ID, transition event, rollback actor/event/reference and assert the FULL OUTER row returns nonzero. All are synthetic only.

Sixteenth-round fixtures additionally mutate the locked live Note after producing an expected hash, call the rejection writer, and require `LEGACY_MIGRATION_SOURCE_DRIFT`; a wrong-note but self-consistent payload, stale hash, or digest-derived snapshot mismatch likewise returns zero rows. A title-overlength fixture calls the shared canonicalizer successfully before the title gate, then records only `SOURCE_TITLE_TOO_LONG`; attempts to insert `CANONICAL_PAYLOAD_INVALID` or `EF_NONFINITE` rejection reasons fail the table CHECK and do not enter the negative writer path. Separate rollback replay fixtures cover empty, missing, extra, wrong-ledger, wrong-source/mapping/hash, rollback actor/event/reference/hash, transition-event, and audit-digest drift with independent FULL OUTER/set failures. Timestamp fixtures compare live/helper/snapshot/archive/replay `last_reviewed` as `YYYY-MM-DD"T"HH24:MI:SS.US"Z"`; title fixtures prove exact Unicode title preservation and that btrim cannot alter hash. Legitimate rejection writer calls pass through owner/session/table ACLs without marker state; direct insert, forged role, marker-only, update/delete/truncate all fail. All are synthetic only.

Approval-specific negative fixtures additionally remove/disable each `(user_id,approval_kind)` authorization row, call the owner function with a forged actor or wrong kind, and attempt a direct adapter-role write; each must fail before any ledger/event mutation. A legitimate source→question→mistake→schedule chain with distinct authorized actors must pass its corresponding event-ID and transition checks.

### Current LSR-02 route/mutation matrix (design input; implementation `NOT_VERIFIED`)

| surface | anonymous | admin | owner/rollback |
| --- | --- | --- | --- |
| `/mistakes` | `308 → /notes` | same | Note/Public Content successor; restore route artifact |
| `/mistakes/review` | `308 → /manage/review` then auth | same | workspace ReviewItem owner; restore artifact |
| `/notes/{slug}`, `/api/notes` | published&&!hidden old Note read-only; new private objects never exposed | content admin only | Note owner; restore source snapshot |
| old Note mistake single mutation | `410` | `410`, successor captures/workspace | no old writer; restore pre-cutover client |
| old Note batch containing mistake | `409`, atomic no partial | `409`, atomic no partial | no mixed mutation |
| `/write-mistake*`, `/api/review/*` | `410` with successor | `410`, no read-only branch | workspace/API successor; rollback only from immutable artifact |

### LSR-02 Owner self-check (限定只读/文档命令)

Owner self-check only covered the allowed boundary: `rg`/`sed` over current source and five files; five-file link/heading/contract searches; limited `git diff --check`; `git status --short`; limited diff review. It did not run tests, build, migration, database, service, browser or user-data query. The self-check confirms:

- ordinary Note/Blog exclusion and current public Note contract are stated in design/requirements/validation;
- every requested legacy Note field and every requested target has a row or explicit out-of-scope/provenance disposition;
- null/ambiguous review state is paused; no ReviewRecord is synthesized; active schedule mapping is explicitly conditional;
- source_ref 64-vs-500 conflict has compared alternatives and selected bounded UUID token without truncation;
- search_vector is explicitly derived/retained, included in source hash, excluded from private targets, with old-row/search parity and no-source-write rules;
- EF uses FLOAT8 plus bit-exact `legacy_ef_bits`, while typed and JSON legacy review values remain preserved;
- the import chain creates both deterministic draft-item/draft pairs through the dedicated `legacy_note_migration_adapter` (existing services are not assumed unchanged), applies Question-before-Mistake domain invariants, and records strong draft FKs/approval/audit;
- logical rollback first uses the governed atomic clear/transition and then fixed FK deletion order; unexpected Capture/Attempt references route to snapshot restore; source locking/drift checks and chapters/019 three-case fixtures are explicit;
- the fourth-round addendum freezes INTEGER[] QKP/projection IDs, complete canonical_payload/hash recomputation and pgcrypto prerequisite, exact provenance mirror signatures/essay refusal, strict malformed-ID handling, Draft→final cross-entity mirrors, schema-qualified SECURITY DEFINER/role/ACL/nonce guard, and expanded negative fixtures;
- current route/mutation matrix and exhaustive SQL/fixture/illegal-transition requirements are in the current addendum;
- ledger state/check/transition/FK/on-delete/index/idempotency/hash/mapping/approval/audit/migration_notes/rollback are cross-referenced;
- QuestionKnowledgePoint canonical ownership, ReviewItem `mistake_id` successor, Attempt/Capture approval chain and strict Capture order are marked future/not-current where implementation is absent;
- LSR-03 fixtures and SQL/restore input contract are listed without creating scripts/tests/DB.

Self-check does not prove source data completeness, schema correctness, migration execution, relation integrity, rollback success, public/private runtime behavior or Gate status. Any independent Reviewer/Verifier finding must update this manifest and may keep LSR-02 `PARTIAL` or return `FAIL/BLOCKED`; Owner cannot promote it to `PASS`.

### Historical controlled LSR-03 owner evidence (2026-08-25; superseded by r2 final review)

This historical owner snapshot was `LSR-03=PARTIAL/[ ]`, `G2=NOT_VERIFIED`; it is superseded by the final R9 `LSR-03=PASS/[x]` manifest. The isolated PostgreSQL cluster was `/tmp/lsr03-final-cluster.3GsaS6`, bound to `127.0.0.1:55432`, and every Alembic/pytest/SQL command passed through the fail-closed guarded runner. It was stopped after evidence capture; no 5432 connection occurred in this run.

| check | result | raw evidence / SHA-256 |
| --- | --- | --- |
| empty replay + idempotent replay | PASS | `/tmp/lsr03-final-replay-2.log` `5d5d8311dfe079ec99e2f531a234478a0baf5feee353108d401b3583f72b363f`; idempotent `d68447b9ec59a526a538b0ecdd291cd1eac106440f8c35a32da1f8c06b0f76e2` |
| adapter synthetic paths | PASS | `/tmp/lsr03-final-rehearsal-2.log` `2501bca47afbd5227c95317e4c3b61b3776d3f641c72a18ad2dac6850f8c75ec` |
| five independent scopes + EXCEPT/FULL OUTER | PASS | `/tmp/lsr03-final-validation.log` `bb221c86498da5719f195960510f5b48661f96d849df566a6d1dd9d384dece0f5`; counts 4/4/4/4/4; mismatches 0 |
| targeted tests | PASS | 16 passed through guard |
| digest ACL + direct ledger negative | PASS | ACL `/tmp/lsr03-final-acl-2.log` `61bd57a63eab2e82e018190a30f5b48661f96d849df566a6d1dd9d384dece0f5`; marker `/tmp/lsr03-final-marker-negative-2.log` `d164cb3f0df9ed173830b3c48bc4f9e2be5dc64eb0f3b8ee32d2a2f7ffb5d54e` |
| logical rollback | PASS | `/tmp/lsr03-final-rollback-2.log` `ed8f12f8e0f3d94340502224ac6260a6c26b1250c2afd93eb64701e04bd71bbb`; state `rolled_back`, targets NULL |
| pre-migration custom dump/restore | PASS | dump `/tmp/lsr03-pre-migration.dump` `45ff916d1a9d1becc13f12e607a0db0df758acb601014fb4ee6f9244a6322917`; restore check `/tmp/lsr03-final-restore-check.log` `93762361955b64388ccb312646be7a5b55bcc72e0ddef1b236089d1661847284`; `legacy_note_migrations` absent |

Historical code hashes (superseded; not current): `026=0544f29060b0ca2f0fed8b4ced87c57cd3ccb7097dd44673e0608a2aca61e1cd`; adapter=`f725675911e79b8c38d34d4748b2743acff82727e122c5378f859caa89507bab`; guarded runner=`dfa7c559095e3ea1ec2c02a9c0961719a3b070aeffdb63ab5a6dfce05f36cead`; rehearsal=`3410455140b03402a5a8d59d0dba08831606a99cb301b47ab899c5256c3f905a`; rollback helper=`946ab39c91671bffdca654857e1f39cb9f903b2b9f7a9a5db95777054f8e81`; validation helper=`3e716e3d322555e65489fa4a57bffd99590e1e2fcc1b1722b21fc2f822957d61`. Current hashes are exclusively the r2 `SHA256SUMS` manifest.

Not closed: full inbound Capture/Attempt/MistakeDraft fixture, exhaustive wrong/replay/second-use nonce and duplicate/collision/search sentinel fixture matrix, independent Reviewer/Verifier and G2. Historical failure logs remain separate from final evidence.

Subsequent bounded adapter fix: frozen legacy `options: list[str]` is normalized to keyed objects (`A`, `B`, …); option dictionaries remain exact `key/text` with string values and true/false answers remain strict. Guarded unit result after this fix: `16 passed`. Current adapter code hash is recomputed at handoff; the earlier hash above is historical and must not be treated as current.

### LSR-03 fixture-QA evidence (2026-08-25; independent fixture implementer)

Historical final status was `LSR-03=FAIL/[ ]`, Reviewer=`FAIL`, Verifier=`PARTIAL`, G2=`NOT_VERIFIED`; this fixture work was superseded by the R9 Final Reviewer/Independent Verifier `PASS` and did not self-approve any Gate. All database commands below were launched through `backend/tests/lsr03_guarded_runner.py` against `127.0.0.1:55432/lsr03_final`; no `5432` connection was made.

| check | result | evidence |
| --- | --- | --- |
| independent archive NDJSON + separate expected-hash manifest | PASS | `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r2/archive.ndjson`, `archive-expected-hashes.ndjson`, `run-manifest.json` |
| five-source count/hash/set replay | PASS | 4/4/4/4/4; bidirectional `EXCEPT=0`; archive/live `FULL OUTER=0`; independent manifest mismatch `0` |
| tamper/missing/extra negative replay | PASS | `archive-validation.log`: all three detected |
| inbound CaptureItem/Attempt/MistakeDraft.attempt_id predicate fixture | PASS | `fixture-matrix.log`: nonempty synthetic relations and `SNAPSHOT_RESTORE_REQUIRED` predicate |
| inbound actual-table rollback call | NOT_VERIFIED | stopped after two consecutive capture/attempt fixture failures per contract; details in `actual-inbound-fixture-status.md`; no third retry |
| wrong marker, nonce replay/second-use/cross-transaction, collision, search sentinel | PASS | `fixture-matrix.log` |
| chapters empty / unmapped pre-019 / explicit mapping | PASS | `fixture-matrix.log`; TEMP pre-019 transform preserves order/status/provenance |
| guarded pytest fixture/helper checks | PASS | `pytest-lsr03.log`: 13 passed |
| stable artifact and code hashes | PASS | `SHA256SUMS`; `r1` was not overwritten |

The actual-table fixture's two failures were isolated to fixture setup/binding (adapter direct ledger SELECT privilege, then wrong draft-item target); the corrected binding was not rerun after the mandatory stop condition. This evidence therefore cannot promote LSR-03 or G2.

### LSR-03 R8 首错后的 deterministic seed 修订 manifest（2026-08-25）

| field | value |
| --- | --- |
| historical failure | R8 Verifier 在空 post-026 数据库执行 rehearsal；R6 Owner evidence 未持久化 machine-readable synthetic seed，source Note 缺失。R8 evidence 保留、不覆盖。 |
| change | 新增 `backend/tests/lsr03_seed_rehearsal.py`；固定 R6 synthetic users、approval authorization、rollback admin、taxonomy、source Note 与 paused baseline IDs；精确空集外 fail-closed；guard/private-venv 后才导入 SQLAlchemy/adapter；输出结构化 identity/count/IDs；static contract 绑定 seed→baseline→rollback。 |
| current hashes | seed=`a8a8ec5bea636a20a17eb6b04f468f6e767374d15b65243aa00768ffbd5d3283`; static=`2991edc1e01bb74e092a3cfb8dce3967f48dc2c2ad58b774125d30192009c389`; rollback=`4c1343df4ee1cb85cc7a2ef939218b3db24a859412030cc18458a6a3d6fe5d6b`; runner=`0867324951d2a9489aee962746dd09339981910d376f7fa3f3bd1f5086aa4965`; 026=`0544f29060b0ca2f0fed8b4ced87c57cd3ccb7097dd44673e0608a2aca61e1cd`; adapter=`6ea489a98f64ba1f5e69d776c063e2a43f7d83a129ef91ace4e5d6d5a68b4bd4`; runner-test=`237f64773ee21ae4cd0e17b8f7771b956722d6f89104222501b54125fb00bdb0` |
| exact R9 sequence | From `backend`, set `R9_URL=postgresql+asyncpg://fixture_admin:secret@127.0.0.1:55432/lsr03_r9`. For every command set `LSR03_DATABASE_URL="$R9_URL" DATABASE_URL="$R9_URL" PYTHONPATH=.` and invoke `/Users/limengyang/2025-blog-public/backend/.venv/bin/python tests/lsr03_guarded_runner.py -- /Users/limengyang/2025-blog-public/backend/.venv/bin/python ...`: (1) `-m alembic upgrade 026` for empty `001→026`; (2) repeat `-m alembic upgrade 026` for idempotent replay; (3) `tests/lsr03_seed_rehearsal.py`; (4) `tests/lsr03_rollback_rehearsal.py --inbound-fixtures`. |
| no-DB verification | `backend/.venv` targeted guarded/static tests=`26 passed`; project-venv `py_compile=PASS`; `diff-check=PASS`; no DB/service/Alembic command is executed in this turn. |
| readiness | historical `READY_FOR_R9=NO` is superseded by R9 Final Reviewer=`PASS` and Independent Verifier=`PASS`; current LSR-03 runtime=`PASS/[x]`; current G2 decision is `FAIL` (Database=`BLOCKED`, Data=`FAIL`). |

### LSR-03 R9 final independent runtime manifest (2026-08-25)

| field | value |
| --- | --- |
| target/evidence | fresh `lsr03_r9`, `postgresql+asyncpg://fixture_admin:secret@127.0.0.1:55432/lsr03_r9`; `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r9-verifier/`; prior r2-r8 evidence untouched |
| sequence | guarded identity → Alembic `001→026` → identical idempotent replay → deterministic seed → actual-table inbound rollback |
| identity | guard/admin=`fixture_admin`; adapter=`legacy_note_adapter_runner`; `127.0.0.1:55432`; non-recovery |
| rollback result | CaptureItem, Attempt, and MistakeDraft.`attempt_id` each returned exact `LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED`; full ledger/relation/audit-event/attachment before-after snapshots unchanged; each inbound reference retained |
| cleanup/stop | all three cases cleanup=0; cluster stopped; listener-after=`NONE` |
| conclusion | Final Reviewer=`PASS`; Independent Verifier R9=`PASS`; LSR-03 runtime evidence=`PASS`; this does not equal G2, whose current combined decision is `FAIL` (Database=`BLOCKED`, Data=`FAIL`) |

### G2 最终独立对账（2026-08-25）

| decision | status |
| --- | --- |
| Database | `BLOCKED` |
| Data | `FAIL` |
| combined G2 | `FAIL` |
| decisive implementation-contract drift | options 空值、idempotency key、mirror/provenance、retained predicate |
| decisive current-evidence gaps | active/retained/019 实际 parity、logical rollback/pre-026 restore、R9 原始日志 hash |
| boundary | LSR-03 runtime remains `PASS/[x]`, but that runtime result is not G2 approval; LSR-04 is not started and is prohibited |
