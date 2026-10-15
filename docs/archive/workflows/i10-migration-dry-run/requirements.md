# I10 需求与验收

## I10-R1 单管理员 Owner 决策

- 输入：获批 canonical owner 与 revision-020 immutable manifest。
- 处理：全部 121 条 legacy entity 使用同一个明确 owner；不得从
  `is_admin`、`created_by`、路径、slug 或关系临时推断。
- 输出：每条 manifest row 都有非空且一致的 `target_owner_id`。
- 失败：owner 不存在、出现多个 owner 或 manifest drift 时停止。
- 验收：manifest=121/121、owner conflict=0、canonical owner count=1。

## I10-R2 隔离 Backfill Dry-Run

- 输入：已验证的 024 备份、当前代码 head 025、获批 manifest。
- 处理：恢复到全新隔离数据库，仅在隔离目标升级 024→025，再在 sidecar
  owner mapping 表写入 121 条映射。
- 输出：可机器读取的执行报告，不包含个人正文或凭据。
- 失败：恢复、revision、schema、导入或唯一性检查失败时销毁隔离目标。
- 验收：source=manifest=sidecar=121，逐表计数一致，duplicate/missing/extra=0。

## I10-R3 完整性与日常库保护

- 输入：隔离 target 和执行前后日常库只读指纹。
- 处理：检查 owner FK、七类业务关系、row hash、revision/head/check；临时
  sidecar 会被 Alembic 识别为非迁移结构，因此先采集 backfill 证据，再删除
  sidecar，最后要求基础 schema 的 `alembic check` clean。
- 输出：完整性审计报告与清理证据。
- 失败：任何 orphan/drift/UNKNOWN 使 E-03 保持 BLOCKED。
- 验收：owner FK orphan=0、业务关系 orphan=0、hash drift=0；隔离库删除后
  catalog count=0；日常库未发生写入。

## I10-R4 Readiness 更新

- 输入：R1-R3 与测试结果。
- 处理：只有全部 PASS 才把 E-03 更新为 `PASS`，并把 E-05/E-06 标记为
  `READY / NOT AUTHORIZED`。
- 输出：README、tasks、validation、audit、diff-report、risk-register 和上层
  workflow 状态一致。
- 失败：任一测试或审计失败时记录风险，不提前解除后续 gate。
- 验收：所有工作流文档无相互矛盾状态；没有实际执行 E-05/E-06。

## 非功能与边界

- 安全：不输出密码 hash、token、正文、附件内容或数据库凭据。
- 可审计：报告包含命令类别、时间、数据库角色、revision、计数和 SHA-256。
- 可恢复：隔离库可销毁；原备份和 immutable manifest 不被改写。
- 禁止：生产/日常库写入、部署、推送、权限切换、归档和 E-05/E-06 执行。
