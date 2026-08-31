# I10 任务清单

- [x] I10-01 E-01 旧系统只读盘点、哈希、来源基线（PASS：源 `blog_db:5432` revision 020 与静态索引均已核对）
- [x] I10-02 E-02 字段映射、重复、冲突、legacy alias（2026-07-26 为
  PARTIAL；2026-07-31 owner 决策与 manifest 验证后 PASS）
- [x] I10-03 E-03 `DRY_RUN_READY` 门槛（2026-07-26 历史结论为 BLOCKED；
  2026-07-31 单 owner backfill、双重复核与恢复完成后更新为 PASS）
- [x] I10-04 E-04 隔离 dry-run、对账、回滚、销毁（TECHNICAL PASS；不授权源库写入或切换）
- [x] I10-05 主验证与独立交叉验证（2026-07-26 为 PARTIAL；
  2026-07-31 owner backfill 主验证与独立 SQL 均 PASS）

## 2026-07-31 Owner Gate 解除执行

> 用户已批准单管理员 backfill 决策及以下任务；I10-06 至 I10-10 已完成。
> E-05/E-06 始终不在本轮执行范围。

- [x] I10-06 固化批准与执行输入
  - 来源需求：I10-R1、I10-R2
  - 涉及文件：本 workflow 文档、C1 immutable manifest、C5 024 backup
  - 修改内容：记录 2026-07-31 批准、canonical owner、备份与 manifest hash；
    确认日常库与隔离目标的名称和身份不会混淆
  - 完成标准：所有输入存在、hash 校验通过、目标创建前不存在
  - 验证方式：只读文件 hash、`pg_restore --list`、PostgreSQL catalog 查询
  - 风险说明：任一输入漂移即停止，不重生成 immutable manifest

- [x] I10-07 在隔离数据库执行 owner backfill dry-run
  - 来源需求：I10-R1、I10-R2
  - 涉及文件：`assets/` 下 dry-run 工具、测试与执行报告
  - 修改内容：恢复 024 备份并仅在隔离目标升级到当前 head 025；创建 FK
    约束的 sidecar mapping 表；从 manifest 写入 121 条 source PK、owner、
    hash、disposition 和 rollback evidence
  - 完成标准：source=manifest=sidecar=121；12 类计数一致；全部 owner 等于
    canonical owner；duplicate/missing/extra=0
  - 验证方式：工具单元测试、隔离 DB SQL、机器可读 JSON 报告
  - 风险说明：所有写命令必须显式指向隔离 DB；禁止使用日常 `blog_db`

- [x] I10-08 执行完整性审计与独立复核
  - 来源需求：I10-R3
  - 涉及文件：`assets/` 审计报告、`audit.md`、`validation.md`
  - 修改内容：核对 owner FK、七类业务关系、manifest row hash、revision/head、
    Alembic check、日常库只读保护证据
  - 完成标准：FK orphan=0、owner orphan=0、hash drift=0、revision/head/check PASS
  - 验证方式：主工具与独立 SQL/进程双重复核
  - 风险说明：任一 UNKNOWN/non-zero 使 E-03 保持 BLOCKED

- [x] I10-09 销毁隔离环境并验证无日常库写入
  - 来源需求：I10-R3
  - 涉及文件：`validation.md`、执行报告
  - 修改内容：终止隔离连接、删除一次性数据库、复核 catalog；比较日常库执行
    前后 revision/count/aggregate 指纹
  - 完成标准：隔离 database count=0；日常库指纹不变
  - 验证方式：`pg_database`、只读 manifest verifier
  - 风险说明：不删除备份，不对日常库执行 DDL/DML

- [x] I10-10 运行测试并更新 E-03/E-05/E-06 状态
  - 来源需求：I10-R4
  - 涉及文件：I10、I11、I12 与主 unification workflow 状态文档
  - 修改内容：运行 owner 工具测试和仓库全量测试；证据全部 PASS 后把 E-03
    更新为 PASS，把 E-05/E-06 更新为 `READY / NOT AUTHORIZED`
  - 完成标准：所有测试 PASS；文档完整且状态一致；未执行 E-05/E-06
  - 验证方式：前端、后端、type/build/compile、Git diff/status 审计
  - 风险说明：若出现既有测试失败，必须记录首个相关失败且不得宣称全 PASS
