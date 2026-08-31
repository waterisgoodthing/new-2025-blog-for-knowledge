# Legacy System Retirement

当前状态：LSR-01=`PASS/[x]`（静态 mapping）；LSR-02=`PASS/[x]`（静态迁移合同，Reviewer=`PASS_WITH_NOTES`、Verifier=`PASS`）；LSR-03=`PARTIAL/[ ]`（当前 fresh isolated runtime=`PASS`，独立 G2 Gate=`BLOCKED`，完整 target parity、`retained_public_only`、visibility/orphan/ReviewRecord、rollback replay/audit digest 与带数据 restore 证据尚未闭合）；G0/G1=`PASS`，G2 Database/Data/combined=`BLOCKED`，G3-G4=`NOT_VERIFIED`，G5=`NOT_AUTHORIZED`。LSR-04 及后续未启动且依赖未满足；本状态不授权生产、切换、删除、部署、commit 或 push。

历史快照：LSR-00 骨架状态曾为 `NOT_VERIFIED`；已被上述最终当前结论取代。

本工作流把用户提供的“旧体系退休、新体系收敛”目标冻结为唯一的后续串行合同。当前 LSR-01 静态盘点与 LSR-02 静态迁移合同均已完成独立复核；实现、迁移、切换、删除和 G2-G4 runtime 阶段均未完成。历史工作流的结论、资格或 dry-run 标记均不自动继承为本目标的当前状态。

## 权威范围与输入

- 目标输入：`/Users/limengyang/.codex/attachments/22aa1b29-c4eb-4468-81a6-0f9fccadf395/pasted-text-1.txt`。
- 本目录仅维护 [design](./design.md)、[requirements](./requirements.md)、[tasks](./tasks.md)、[validation](./validation.md) 和本 README 五个权威文件。
- 当前工作树已有用户改动；本次只允许新增本目录五个文件，不覆盖、暂存、提交、格式化或删除其它路径。
- `LSR-00` 是本次骨架建立任务；LSR-01 静态 mapping 已完成；LSR-02 静态合同已由独立 Reviewer/Verifier 收束通过。任务进度只用 `[x]`/`[ ]` checkbox 表示，不把文档合同误报为已执行审计；LSR-03 当前运行成功但任务验收仍为 `PARTIAL/[ ]`。

## LSR-03 当前 fresh isolated runtime 与 G2 对账（2026-08-25）

当前权威运行证据位于 `/Users/limengyang/.codex/attachments/lsr03-g2-fresh-final-evidence-20260825-bootstrap-fixture-admin-cwd/`。独立 Verifier=`PASS`：同一 fail-fast driver 完成 58 项 no-DB 测试、空库 `001→026`、026 二次幂等、active/paused/retained/019 与幂等路径、DB negative fixtures、logical rollback、三类 actual inbound zero-mutation 和 pre-026 restore；SHA256SUMS 42 项通过，55432 已停止，未查询 5432，root worktree 与基线一致。独立 Gate 最终裁决 G2=`BLOCKED`：当前日志尚不足以证明完整 target parity、真实 `retained_public_only`、visibility/orphan/ReviewRecord、rollback replay/audit digest 与带合成数据 restore。因此 LSR-03 仍为 `PARTIAL/[ ]`，下一任务仍属于 LSR-03，不得进入 LSR-04。

## LSR-03 重开前静态预检（2026-08-25）

本次仅完成无数据库预检，不改变 LSR-03 的 `FAIL/[ ]`、Reviewer=`FAIL`、Verifier=`PARTIAL`、G2=`NOT_VERIFIED` 或任何 Gate 结论。复核了 r2 的 `actual-inbound-fixture-status.md` 与 `SHA256SUMS`：两次失败分别为 adapter-runner 直接读取 ledger 被拒，以及夹具错绑 `target_question_draft_item_id`；r2 证据明确要求停线且未在修正后重跑。

当前源码静态结论：026 的 rollback guard 已对 `capture_items.mistake_draft_item_id`、`attempts.mistake_draft_item_id`、`mistake_drafts.attempt_id` 统一检查并返回 `SNAPSHOT_RESTORE_REQUIRED`；实际表夹具已使用 `target_mistake_draft_item_id`。本轮只增强 `backend/tests/lsr03_rollback_rehearsal.py` 的管理员 setup/cleanup、adapter-only rollback、连接 identity、zero-mutation 与 cleanup 证据接口，并新增纯源码合同测试；未改产品行为、模型、迁移或 adapter。

预检结论：`PASS`（仅静态/无数据库范围）；独立 `lsr03_reviewer`=`REVIEW: PASS`、`lsr03_verifier`=`VERIFY: PASS`；`READY_FOR_FRESH_REHEARSAL=YES`。本结论仅放行全新隔离 runtime recheck，不改变总体 LSR-03=`FAIL/[ ]` 或 G2=`NOT_VERIFIED`。

## LSR-03 r3 runtime recheck（2026-08-25）

结果：`FAIL`，首个 guarded runtime 步骤即因运行环境缺少 `sqlalchemy`，在导入 `backend/tests/lsr03_guarded_runner.py` 时 `ModuleNotFoundError`；尚未进入 URL 解析、identity probe、Alembic 或 SQL。按合同立即停止，不修复、不重跑。全新集群已停止且 `127.0.0.1:55432` 无监听；首错与 SHA manifest 保存在 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r3/`，不得覆盖 r2。LSR-03 保持 `FAIL/[ ]`，G2 保持 `NOT_VERIFIED`，不产生任何 rollback/zero-mutation/cleanup 通过证据。

## r3 首错后的运行时合同修订（2026-08-25）

r3 首错作为历史首错保留，r3 evidence/r2 未覆盖，r4 未启动。仅在 guarded runner/tests 中做 task-specific 无数据库修订：移除顶层 SQLAlchemy 导入，任何 probe/DB 动作前机械要求 `backend/.venv`（固定 `LSR03_PYTHON_RUNTIME_REQUIRED`、exit 64）；所有 child 命令固定为 `backend/.venv/bin/python -m pytest`、`PYTHONPATH=.`、cwd=`backend`。新增无 DB subprocess 覆盖错误解释器在 probe/child 前 fail-closed，以及正确私有 venv identity；未改产品、模型、迁移或 adapter。

本轮只用 `backend/.venv` 完成 targeted guarded/static tests=`20 passed`、`py_compile=PASS`、`git diff --check=PASS`；`READY_FOR_R4=YES` 仅表示允许未来一次全新隔离 runtime recheck，不改变 LSR-03=`FAIL/[ ]` 或 G2=`NOT_VERIFIED`。

## LSR-03 R4 fresh runtime recheck（2026-08-25）

结果：`FAIL`，首个 actual-table fixture 命令在 `_audit_event_snapshot` 查询 `legacy_migration_rollback_audits ORDER BY id` 时收到 `UndefinedColumnError`（该表无 `id` 列）；尚未进入 capture/Attempt/MistakeDraft.attempt_id setup、rollback、zero-mutation 或 fixture cleanup。按首错规则立即停止，不修复、不重跑。全新 `lsr03_r4` 集群已停止，`127.0.0.1:55432` 无监听；精简日志、代码/证据 SHA256 manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r4/`，r2/r3 未覆盖。cluster stop 已证明，fixture cleanup=`NOT_RUN`；LSR-03 仍 `FAIL/[ ]`，G2 仍 `NOT_VERIFIED`。

## R4 首错后的无数据库定向修订（2026-08-25）

根据 R4 的 026 DDL 证据，`legacy_migration_rollback_audits` 的主键为 `ledger_id`，helper 已将 audit snapshot 改为 `ORDER BY ledger_id`，并新增无数据库结构合同测试，禁止该表使用 `ORDER BY id`。仅修改 LSR-03 helper/test；未连接 DB、未启动服务、未执行 Alembic/r5。`backend/.venv` targeted tests=`21 passed`，`py_compile=PASS`，`diff-check=PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R5=YES` 仅放行未来 fresh runtime，不改变 LSR-03=`FAIL/[ ]` 或 G2=`NOT_VERIFIED`。

## LSR-03 R5 fresh runtime recheck（2026-08-25）

结果：`FAIL`，全新 `lsr03_r5` 已完成 guarded identity、001→026、paused baseline、capture setup 与 capture rollback attempt；首个 zero-mutation 断言将部分列 baseline 与 `SELECT *` 全 ledger 快照直接比较，报告大量 ledger 字段“变更”。按首错规则立即停止，不修复、不重跑；Attempt/MistakeDraft.attempt_id 两条 fixture、精确 `SNAPSHOT_RESTORE_REQUIRED`、完整 zero-mutation 与 cleanup 均未完成。集群已停止且 `127.0.0.1:55432` 无监听；fixture cleanup=`NOT_RUN`。证据与 SHA256 manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r5/`，不覆盖 r2/r3/r4；LSR-03 保持 `FAIL/[ ]`，G2 保持 `NOT_VERIFIED`。

## R5 首错后的无数据库定向修订（2026-08-25）

R5 根因已最小修订：先只定位唯一 `migrated_paused` ledger `id`，再通过 `_ledger_snapshot(admin, baseline_id)` 获取完整 baseline；zero-mutation after 继续使用同一 `_ledger_snapshot` helper，禁止 partial mapping 直接作为 baseline。新增无数据库结构测试覆盖该合同。仅修改 LSR-03 helper/test；`backend/.venv` targeted tests=`22 passed`，`py_compile=PASS`，`diff-check=PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R6=YES` 仅放行未来 fresh runtime，不改变 LSR-03=`FAIL/[ ]` 或 G2=`NOT_VERIFIED`。

## LSR-03 R6 fresh runtime recheck（2026-08-25）

R6 三条 actual-table inbound rollback 全部完成：CaptureItem、Attempt、MistakeDraft.`attempt_id` 均精确返回 `LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED`；全 ledger、audit/event、relation、attachment zero-mutation 与 inbound retention 均为 true，每条 cleanup=0。guard/admin/adapter identity 均绑定全新 `lsr03_r6` 与 `127.0.0.1:55432`；集群已停止且无监听。证据与 SHA256 manifest 位于 `/Users/limengyang/.codex/attachments/lsr03-final-evidence-20260825-r6/`，不覆盖 r2-r5。该 runtime 证据不自批 LSR-03 或 G2；总体状态仍 `FAIL/[ ]`、`NOT_VERIFIED`，等待独立 runtime Reviewer/Verifier。

## R7 首错后的无数据库运行时合同修订（2026-08-25）

R7 首错根因是 plain `postgresql://` 被 guard 接受后，Alembic 按 `settings.DATABASE_URL` 尝试缺失的 psycopg2；R6 使用 `postgresql+asyncpg://` 成功。guard 现仅接受 `postgresql+asyncpg://`，plain scheme 在 probe/child 前固定 `LSR03_DATABASE_URL_ASYNCPG_SCHEME_REQUIRED`、exit 64；无 DB 测试覆盖 asyncpg 可用、psycopg2 不可用、plain scheme fail-before-probe/child 与正确 scheme 接受。仅修改 LSR-03 guard/test；`backend/.venv` targeted tests=`24 passed`，`py_compile=PASS`，`diff-check=PASS`。独立 Reviewer=`PASS`、Verifier=`PASS`（静态修订）；`READY_FOR_R8=YES` 仅放行未来 fresh runtime，不改变 LSR-03/G2。

## 为什么既有工作流不能单独承载本目标

既有资料是有价值的历史/输入证据，但不是本目标的单一权威载体：

1. `route-ownership-alignment` 只解决路由归属与兼容共存，明确把切换和删除留给另行审批；它没有对象、字段、迁移、数据完整性或全链路清单。
2. `editor-convergence` 只比较 Note/Blog/Mistake 编辑能力，选择了未来的最小共享原语方向；它不证明旧数据迁移、旧 API 退休或复习链等价。
3. `frontend-foundation-and-quality` 聚合前端质量与若干子工作流，存在 F4 输入、G2/G3/G4 分域状态；它不是旧体系退休、数据库迁移或公开/私有切换合同。
4. `route-cutover-after-batch-8` 描述过路由目标和旧 Note 错题冻结，但其方案、公开 `/mistakes` 策略和旧入口处置仍需当前源码与数据证据逐项重审。
5. `i10-migration-dry-run`、`i11-shadow-migration`、`i12-final-closure` 及 `i-series-completion-plan` 关注另一组 revision、owner backfill、恢复或部署资格；它们的 dated manifest、数据库快照、权限边界和授权条件不能替代本目标的对象映射与退休证明。
6. `personal-learning-system-v2-unification` 记录了从规划到历史验收的多条增量线，包含已完成、阻塞、跳过和仅隔离证据；它没有在当前工作树上提供覆盖“旧对象零消费者→迁移→切换→删除→四阶段融合”的一份当前 manifest。

因此，本目录的 `validation.md` 只记录可重算的当前证据和独立对账；历史状态保留为引用来源，不能改写为当前 PASS。

## 冻结的领域合同

新版候选权威体系为：`Question / QuestionDraft / DraftItem`（结构化题目）、`Mistake / MistakeDraft`（结构化错题）、`ReviewItem / ReviewRecord`（正式复习）、`Subject / KnowledgePoint / QuestionKnowledgePoint / KnowledgePointLink`（知识组织）、`Capture`（经过草稿、人工确认、正式转换的采集入口）和受保护的 `/manage/*` 学习工作区。

旧体系候选必须由 LSR-01 依据当前源代码、迁移、路由、客户端、测试和获批隔离快照确认，不能仅凭名称删除：`Note(type=mistake)` 及其复习字段、旧 `/api/review` 链、`/write-mistake`、`/mistakes/review`、重复私有写作入口，以及经引用审计证明已被新版完全替代的兼容客户端、组件、服务、模型消费者和测试。

`Note` 仍保留普通笔记、Blog 和公开内容职责；不得把整个 Note 模型、公开读取路由、历史公开内容或未迁移的用户历史数据归为可删除旧体系。当前认证合同保持 stateful HttpOnly `admin_session`、`AdminSession`、前端受保护请求的 `credentials: 'include'` 和后端 `get_current_admin`；不得借退休任务迁移到 Bearer/JWT、放宽权限或启用 bypass。

## 串行阶段与状态

```text
LSR-00 骨架冻结
   -> [LSR-01 后独立 G0/G1 对账] 阶段一：映射、迁移、隔离演练、切换/退出、删除、独立复核
   -> [G0-G3 全部 PASS] 阶段二：七个体系逐项主链验证
   -> [G0-G3 全部 PASS] 阶段三：隔离生产构建 + FastAPI + PostgreSQL + Chromium 融合验证
   -> [G0-G3 全部 PASS，适用时 G4 PASS；无生产范围 G5=NOT_AUTHORIZED] 阶段四：残留清理、恢复复核、最终报告
```

每次只执行依赖满足后的第一项；完成一个任务后立即在 `tasks.md` 和 `validation.md` 更新 checkbox 与证据。非生产范围的 LSR-01 及后续既定任务权限已预先批准，但批准不等于 Gate PASS；Gate 仍必须由当前独立 Reviewer/Verifier 对账。生产数据库/服务、真实凭据或用户数据、公开路由生产切换、不可逆操作、部署、commit/push 仍为 `NOT_AUTHORIZED`。

## 证据、角色与硬边界

每阶段只保留一份嵌入 `validation.md` 的权威 manifest、必要的原始失败证据（优先保存在隔离临时目录并以 hash/路径登记）和一份最终汇总；不创建 `audit.md`、`assets/` 或重复正常重试日志。实施 Worker、独立 Reviewer、Verifier 和 task-local Gate Worker 必须由真实独立子代理 identity 承担，统一使用用户指定的 luna/high；主代理只编排、汇总和对账，不代替任何 Worker，Primary Owner 不得批准自己的高风险结果。

本次 LSR-00 只建立文档，不读取或连接日常/生产数据库、不读取真实凭据或用户正文、不启动服务、不修改产品代码/测试/迁移/运行时、不执行真实 Chromium、不部署、不 commit、不 push。已预先批准的非生产任务可以在其依赖满足后按精确任务范围实施，并优先使用隔离 PostgreSQL、合成数据、真实 Chromium 与可回滚证据；生产数据库/服务、真实凭据或用户数据、公开路由生产切换、不可逆操作、部署、commit/push 仍必须停止并保持 `NOT_AUTHORIZED`。

## 参考输入工作流

- [route-ownership-alignment](../route-ownership-alignment/README.md)
- [editor-convergence](../editor-convergence/README.md)
- [frontend-foundation-and-quality](../frontend-foundation-and-quality/README.md)
- [route-cutover-after-batch-8](../route-cutover-after-batch-8/README.md)
- [i10-migration-dry-run](../i10-migration-dry-run/README.md)、[i11-shadow-migration](../i11-shadow-migration/README.md)、[i12-final-closure](../i12-final-closure/README.md)、[i-series-completion-plan](../i-series-completion-plan/README.md)
- [personal-learning-system-v2-unification](../personal-learning-system-v2-unification/README.md)

历史快照（已被最终当前结论取代）：LSR-00 依赖满足后执行 LSR-01、其结论保持 `NOT_VERIFIED` 并等待 G0/G1 对账。当前 G0/G1 已完成设计层对账；LSR-02 在 Owner 交付前曾因最终 QA/Data 复核未完成而未启动，当前状态以五文件顶部和 validation manifest 为准。

## R8 首错后的 deterministic seed 修订（2026-08-25）

R8 首错与 evidence 保留为历史：R6 Owner evidence 未持久化 machine-readable synthetic seed，Verifier 在空 post-026 数据库执行 rehearsal，source Note 缺失。新增 `backend/tests/lsr03_seed_rehearsal.py`，固定 R6 synthetic users、approval authorization、rollback admin、taxonomy、source Note 与 paused baseline IDs；仅接受 guarded/private-venv invocation，目标非精确空集时 fail-closed，并输出结构化 identity/count/IDs。未改产品、model、migration 或 adapter；总体 LSR-03=`FAIL/[ ]`、G2=`NOT_VERIFIED`。

R9 唯一顺序与完整 command/hash manifest 见 `validation.md`：guard/private-venv Alembic `001→026`、重复同一 Alembic 命令验证 idempotent、guard/private-venv seed、guard/private-venv `lsr03_rollback_rehearsal.py --inbound-fixtures`。`READY_FOR_R9=NO`，等待独立 Reviewer/Verifier。
