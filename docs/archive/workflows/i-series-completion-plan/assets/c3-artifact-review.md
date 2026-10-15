# C3 Candidate Artifact 与 Migration Runbook

事实日期：2026-07-28
候选路径：`/Users/limengyang/Backups/2025-blog-public/i-series-artifacts/20260728-c3-candidate/`
Git base：`cc05ef5b4b3fa0504d3ebbc07105ed260397cb71`（branch `notes-workspace-ux-upgrade`）

## 冻结身份

- 完整纠缠文件数：83；来源是 C3 时刻 `git status --short` 中全部 `backend/`、`src/` modified/untracked 文件。
- `candidate-files.sha256` SHA-256：`2a70223b11d7d456ad3cceaccba01304e5219261ab65e7286b7b6e1a38abcfb8`。
- `candidate-files.tar.gz` SHA-256：`de60d2ec8f56ef742b2f06633fe17be5bf96bb84b004ba614b56a1e072defa70`。
- tracked patch SHA-256：`4aad86dfa9f25897867185dd643e1a089e5958132d001a0f39d455aece0ff782`。
- offline upgrade SQL SHA-256：`e12f0e09afeaeb2d12c222aef295c35196e5ad65466d71cb6983d978184299b1`。
- 复制后从 `files/` 执行 `shasum -a 256 -c ../candidate-files.sha256`：83/83 OK。
- Alembic chain：`020→021→022→023→024 (head)`，单 head。C2 使用同一文件内容在 024 clone 上 `alembic check` 为 `No new upgrade operations detected`。
- manifest：`owner-mapping-manifest-v1.json` payload SHA-256=`c98bdfa3a560ea47ab1768215a3600aa19b3d190f42ac13d4ebfcb51a80be3b5`。

该冻结是“Git base + tracked binary patch + untracked/modified 83 文件完整副本 + hash manifest”，不是 commit。Phase 1.0 文档/截图等非 `backend/`、`src/` dirty 未进入 artifact。

## SQL、锁与数据影响审查

| Revision | DDL/DML | 锁/时延风险 | 当前数据影响与 gate |
|---|---|---|---|
| 021 | create attempts/index；alter `mistake_drafts` add FK/unique/check | ALTER TABLE 需要强表锁；新 FK/unique 需扫描现有行 | source `mistake_drafts` 小表；C2 实跑 PASS；升级窗口必须无应用会话 |
| 022 | create `admin_profiles` 与 FK/unique | catalog/table create locks；不改旧行 | 新表 0 rows；C2 PASS |
| 023 | `attachments` add 3 columns；回填 `display_name`；NOT NULL/FK/check/index | 多次 ALTER 需 ACCESS EXCLUSIVE；UPDATE/NOT NULL/index 扫描表 | source 1 row，backfill bad=0；C2 PASS |
| 024 | `notes.revision` 回填/NOT NULL；create versions/links/index；`CREATE EXTENSION pg_trgm` | notes ALTER/UPDATE 锁；extension catalog lock且要求 CREATE privilege | source 13 notes，backfill bad=0；`blog_user` 在 clone 可创建 extension；C2 PASS |

C2 完整 `upgrade + current + heads + check` 墙钟约 1.2 秒；这只是本机 121-row 观察值，不是生产 SLA。C5 前要求 source 无应用连接，迁移期间保持停写；任一非执行连接、新 hash drift 或 artifact drift 硬停止。

## Extension 审查

source 020 当前只有 `plpgsql`，无 `pg_trgm`；024 在独立 target 创建 `pg_trgm` 成功。024 downgrade 中的 `DROP EXTENSION IF EXISTS pg_trgm` 可能影响同库未来消费者，因此不作为 source 主回滚。若 C5 upgrade 失败，事务型 PostgreSQL DDL 应回滚；仍以并行 020 restore/switch 验证为最终恢复门槛。

## 回滚 Runbook

1. C4 先创建新鲜 020 DB+附件备份，恢复到新的并行 DB 并验证 020→024；备份不可读则不进 C5。
2. C5 preflight 重跑 artifact `shasum -c`、source manifest/hash、production backend/tunnel/`pg_stat_activity`；任何 drift 停止。
3. 停写后运行 Alembic `upgrade head`。未开放 024 写入前失败时，保持 source 不服务应用，并恢复 C4 的 020 dump 到并行 DB；核对 revision/count/hash/附件后才允许选择 020 兼容连接。
4. 成功升级后先做 current=head/check、旧字段投影 hash、新字段 backfill、关系、read/API smoke，再创建 024 restore point；此前不开放写入。
5. 已产生 024 新写后禁止直接 `downgrade 020`。只能使用 C7 验证的 reverse delta + 并行 restore/switch 回切。

离线 `upgrade 020:024 --sql` 可完整生成。离线 `downgrade 024:020 --sql` 在 022 的数据保护查询因无 bind 而停止，只生成到 023→022 的 partial SQL；这证明 downgrade 必须在线读取数据状态。C2 的在线 `024→020→024` 已 PASS，但只适用于新表无数据的隔离 clone，不能扩大为 source 主回滚保证。

## C5 Artifact Equality Gate

在 C5 同一窗口，必须对当前 repo 从候选目录运行：

```text
shasum -a 256 -c /Users/limengyang/Backups/2025-blog-public/i-series-artifacts/20260728-c3-candidate/candidate-files.sha256
```

必须 83/83 OK；同时 candidate file list hash 必须仍为 `535257ae402d7055d8a9e8271c081109361849acd4ae6b829f1fb314c78b00a9`，Alembic heads 必须唯一为 024。任一失败即 C5 BLOCKED。
