# I 系列剩余任务需求与验收门槛

状态：`APPROVED FOR C6-C12 SIMPLIFIED EXECUTION`

## 1. 总体要求

1. 用户于 2026-07-29 批准 C6-C12 简化路径；一次只执行、验收一个增量，完成后立即更新 `tasks.md` 与 `validation.md`。
2. 当前事实必须由同一执行窗口的代码版本、只读源审计、数据库/附件证据、测试和浏览器证据共同支持；历史 workflow 勾选不能单独证明当前状态。
3. `src/` 与 `backend/` 分开验收。前端 `AuthGate` 只表达页面边界，后端 `get_current_admin` 才是写入、AI、上传、复习的真实安全边界。
4. 公开 `/mistakes`、`/notes`、`/notes/[slug]`、`/blog`、`/blog/[slug]` 保持匿名读取；管理创建/编辑、复习、AI、上传必须受保护。
5. legacy 错题 `Note(type="mistake")` 与独立 `mistakes` 表均作为真实源；不得假设 `/api/mistakes` 取代 `/api/notes`，也不得无证据 merge。
6. 任一 UNKNOWN、owner 冲突、hash/count drift、恢复失败或权限失败均 fail closed。live source 在 C6/C7/C10 只允许只读查询。

## 2. I10 owner gate 验收

- D1-D8 使用用户在 2026-07-28 指定的默认决策；canonical target owner 由只读查询在 admin 中按 UUID 升序确定。
- manifest 覆盖 12 类全部 121 条当前源记录；capture_items=0 仍有未来确定性规则。
- 每条 source PK 恰好一个 MIGRATED/MERGED/ARCHIVED/QUARANTINED/REJECTED_WITH_REASON 终态。
- `sum(disposition counts)=source count`，source PK/hash 无遗漏/重复；MERGED 保留多源逆向映射。
- ambiguous/orphaned/duplicate/cross-owner 均有 conflict code、原因、批准引用和 rollback source。
- admin、created_by、folder/path/slug 不作为 fallback owner；created_by 只作 provenance。
- 主验证与独立复核使用不同进程/查询实现，结果一致后才可将 `DRY_RUN_READY` 改为 PASS。

## 3. 020→024 upgrade 验收

- 021–024 候选文件已纳入固定、可审计 artifact，链为单 head；SQL/锁/extension/downgrade 风险已评审。
- 源库写入已由 2026-07-28 授权覆盖，但写入前仍须完成生产 backend/source DB 关系的只读核查并通过 C3/C4 技术门槛。
- 同一维护窗口的新鲜 020 DB+附件备份、SHA-256、12 类 count/hash、manifest hash 可读，并在隔离目标恢复成功。
- clone 上 020→024 后 `current=head=024`、`alembic check` 无差异；旧字段 hash/关系不变，新字段回填正确。
- 源 upgrade 期间旧写停用；失败时可恢复并切回 020 兼容应用。开放 024 写入前生成 024 恢复点。
- 直接 downgrade 不是默认回滚；若 reverse delta 未演练，禁止在开放新写后声称可回滚。

### 3.1 C0-C5 Git 权威与升级后 C1 复核收口

- 产生当前 revision 024 schema 的 `021`-`024` migration 必须与 C3 识别的 83-file runtime/contracts/tests 闭包进入同一个本地 Git commit；不得只提交 migration，也不得混入 Phase 1.0、UI review、临时管理员或其他无关 dirty 改动。
- 暂存后必须证明四个 migration 均为 Git added/tracked、Alembic 保持 single head 024、`alembic current=head=024` 且 `alembic check` 无差异。
- C1 manifest 是 revision 020 的不可变时点契约，不得从 revision 024 重新生成或改写其 source hash。
- C1 verifier 可对明确支持的 revision pair 应用旧字段投影；当前唯一跨 revision 支持为 database 024 投影到 manifest 020：`notes` 排除 `revision`，`attachments` 排除 `display_name`、`folder_id`、`trashed_at`，其余 12 类记录保持完整行。
- 升级后报告必须同时写出 `manifest_source_revision=020`、`database_revision_actual=024`、`projection_revision=020`、`projection_applied=true`；不支持的 revision pair 必须 fail closed。
- live 024 只读复核必须继续满足 121 行、missing/extra/duplicate/hash drift/owner conflict/orphan 全为 0，aggregate 仍为 `b40b109a0a1a7eca9b633a11503f8327c8c051fa0b4f05fb0efa04a79089adb6`。
- 本收口仅允许本地 commit；不 push、不部署、不改生产配置、不写数据库。

## 4. C6 最终数据完整性审计

- 在 live source 024 上只执行显式只读事务；不得创建 target、迁移表或写入 source。
- 重用不可变 C1 revision-020 manifest 和既有 024→020 投影，继续满足 121/121、aggregate 不变。
- 七类 FK/多态关系 orphan 均为 0；`notes.revision >= 1`；`attachments.display_name` 非空且等于 `filename`；`folder_id` 允许 NULL。
- 报告 12 表计数、revision、extensions、用户/admin/canonical owner 事实；任何 drift 或 UNKNOWN 均失败。

## 5. C7 恢复与 C8/C9 简化决策验收

- C7 从 C5 024 backup 恢复到全新时间戳隔离 DB，校验 backup SHA-256、revision/head/check、12 表计数、121-row manifest aggregate、关系、backfill 和 candidate runtime readiness。
- 临时附件只解压到临时目录；完成后移入 `~/.Trash/`。隔离 DB 必须删除并用 `pg_database` 复核不存在；C5 backup 保持不变。
- C8 `SKIPPED`：单一 source 架构不存在实际权威切换对象。
- C9 `SKIPPED`：source 即唯一权威，不存在 Legacy 数据库可归档。跳过不等于删除或部署。

## 6. F-01/F-02/F-03 验收

F-01：真实管理员会话、匿名/非管理员/失效会话、公开与管理路径、C7 恢复证据、完整失败矩阵、三尺寸/键盘、测试/type/build/compile/alembic 全部有主验证与独立交叉验证。AUTH_BYPASS 不得用于正常权限证明；不得通过修改生产配置取得证据。

F-02：只有所有门槛 PASS 才可写 `ELIGIBLE`；任一 UNKNOWN/FAIL/BLOCKED 写 `NOT ELIGIBLE / DO NOT DEPLOY`。G4 只授权审查，不授权部署。

F-03：最终报告分别声明 MVP、产品化、知识工作区、AI-OCR 治理、备份恢复、migration dry-run、权威切换、Legacy 归档、生产资格、实际部署；状态必须带日期/环境/artifact/revision/证据，不能互相推断。

## 7. 完成与暂停

完成条件：I10 owner gate、020→024、C6 完整性、C7 恢复、C8/C9 简化决策、F-01、F-02、F-03 均有对应证据与明确结论；生产部署仍保持独立授权。

暂停条件：live source 写入、schema 扩大、部署、删除源数据、不可恢复 downgrade，任一技术 gate 失败，或同一失败重复两次而无新证据来源。暂停时记录 BLOCKED/PARTIAL，不弱化门槛。
