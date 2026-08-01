# I11 任务清单

- [x] I11-01 影子迁移前置核验（I10 owner gate 2026-07-31 PASS）
- [x] I11-02A 批准 E-05 架构反转与执行边界
  - 来源需求：I11-R1
  - 涉及文件：I11 workflow、I-series 历史简化决策
  - 修改内容：确认恢复 shadow 路径，仅授权 E-05 隔离执行
  - 完成标准：批准明确覆盖 I11-02A 至 I11-02H
  - 验证方式：对话批准记录
  - 风险说明：不自动授权 E-06

- [x] I11-02B 锁定 source、v1 manifest 与 shadow 输入
  - 来源需求：I11-R2、I11-R3
  - 涉及文件：C5 backup、I10 manifest、当前 source 只读 fingerprint
  - 修改内容：确认 121-row v1 不变，识别当前 123-row 增量并生成输入 hash
  - 完成标准：source identity/revision/count、备份、manifest 均可验证
  - 验证方式：只读 SQL、SHA-256、`pg_restore --list`
  - 风险说明：不得把 snapshot 后新增行静默写回 v1

- [x] I11-02C TDD 实现 shadow/delta 安全工具
  - 来源需求：I11-R2、I11-R4
  - 涉及文件：`docs/workflows/i11-shadow-migration/assets/`
  - 修改内容：实现目标库拒绝、scan、ledger、delta 分类、幂等 replay、tombstone
  - 完成标准：工具拒绝 `blog_db`；fixture 覆盖 insert/update/delete/no-op
  - 验证方式：RED→GREEN 单元/集成测试、`py_compile`
  - 风险说明：不接入 runtime `DATABASE_URL`

- [x] I11-02D 创建并验证一次性 shadow target
  - 来源需求：I11-R2
  - 涉及文件：一次性 PostgreSQL target、仓库外临时 dump
  - 修改内容：source 只读 dump；restore 024；shadow-only upgrade 025
  - 完成标准：target identity 正确，current=head=025，基础 check clean
  - 验证方式：PostgreSQL catalog、Alembic、backup hash
  - 风险说明：所有写命令显式指向 `i11_shadow_` target

- [x] I11-02E 执行全量 shadow ledger 与 delta manifest
  - 来源需求：I11-R3
  - 涉及文件：shadow sidecar、delta manifest、全量报告
  - 修改内容：载入 v1 121 rows，为 snapshot 后行生成独立 delta mapping
  - 完成标准：source/current manifest/ledger 覆盖一致；owner conflict=0
  - 验证方式：PK/hash/owner/disposition 双重复核
  - 风险说明：密码 hash、正文和凭据不进入仓库证据

- [x] I11-02F 执行双扫描增量对账与幂等重放
  - 来源需求：I11-R4
  - 涉及文件：scan A/B、delta/tombstone/replay reports
  - 修改内容：分类并重放 delta；第二次 replay 必须 no-op
  - 完成标准：unmapped/duplicate/owner conflict/unexplained drift/orphan=0
  - 验证方式：主工具、独立 SQL、fixture mutation 演练
  - 风险说明：delete 仅记 tombstone，不自动删除业务行

- [x] I11-02G 完整性审计、回滚与销毁
  - 来源需求：I11-R5
  - 涉及文件：validation、audit、risk、JSON evidence
  - 修改内容：核对 schema/data/owner/关系；删除 sidecar 与 shadow target
  - 完成标准：基础 Alembic check clean，target catalog=0，source fingerprint 不变
  - 验证方式：独立进程复核
  - 风险说明：任一失败保持 E-05 BLOCKED

- [x] I11-02H 全量测试与 E-05 收口
  - 来源需求：I11-R5
  - 涉及文件：I11/I12/main workflow 状态
  - 修改内容：运行工具、后端隔离测试、前端/type/build；更新 E-05 状态
  - 完成标准：全部验收 PASS；E-06 仍 NOT AUTHORIZED
  - 验证方式：测试输出、diff/status、最终报告
  - 风险说明：测试必须显式连接隔离库

- [x] I11-03A 修复执行基线冲突：记录 2026-08-01 E-06 正式授权，校正
  source revision 024 陈旧项、I12 审计残句与 C10-C12 历史证据边界。
- [x] I11-03B 生成新鲜数据库与附件备份，验证 SHA-256、可读性，并在全新
  隔离目标完成联合恢复。
- [x] I11-03C 锁定 source/target/附件/运行配置身份，建立停写并构建 revision
  025 cutover target；验证 count、PK、hash、owner、关系与连接身份。
- [x] I11-03D 执行首次权威切换与观察期；使用真实管理员会话且
  `AUTH_BYPASS=false` 验证公开读取和管理员写入边界。
- [x] I11-03E 完成 source->target 增量对账与幂等重放；任一未知 delta 或
  drift 必须 fail closed。
- [x] I11-03F 完成 target->source reverse delta、回切与回切观察；验证回切
  后 source 可恢复服务且 target 停写。
- [x] I11-03G 完成最终重切、零增量复核与旧 source 只读归档；不得删除旧库、
  不得部署或 push。
- [x] I11-03H 清理临时恢复目标与临时附件，记录最终 authority、archive、
  backup 与 rollback 状态。
- [x] I11-04 主验证与独立交叉验证
