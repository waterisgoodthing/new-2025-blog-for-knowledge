# Backup and Restore Validation Plan

日期：2026-07-13  
状态：设计完成；未执行 `pg_dump`、`pg_restore`、数据库写入或附件复制。

## Current Evidence Boundary

Phase C 只有只读 row counts、PK 范围和时间范围。当前没有 pg_dump evidence、restore rehearsal 或 attachment checksum validation。因此本计划定义未来验证，不把设计写成恢复已成功。

## Backup Scope

### PostgreSQL

- schema、Alembic revision metadata、tables、indexes、constraints、foreign keys、polymorphic target fields；
- all migration-relevant rows, including notes, questions, mistakes, mistake drafts, review items/records, knowledge points/links, attachments metadata, AI runs/call logs;
- audit/session metadata only within approved retention and redaction policy；敏感字段备份范围与加密策略当前 UNKNOWN。

### Attachment metadata

- attachment ID、storage key、size、content type、created time、checksum（若存在）；
- attachment links、target type/ID、link integrity；
- metadata 与 blob 必须使用同一 snapshot identifier。

### Attachment storage

- every referenced blob；
- storage key to blob mapping；
- byte size and cryptographic checksum；
- missing/unreadable/duplicate key 状态。

当前附件存储介质、完整 key 清单和已有 checksum 覆盖率未由证据证明，标记 UNKNOWN。

## Restore Procedure

仅允许在隔离临时环境执行，不能对共享/生产数据库执行：

```text
snapshot
  ↓
temporary database
  ↓
restore
  ↓
schema verification
  ↓
data verification
  ↓
business smoke test
```

1. 固定 source snapshot ID、数据库 revision、附件 snapshot ID 与工具版本。
2. 创建临时数据库/临时 storage namespace；不得复用生产写入口。
3. 恢复 PostgreSQL backup；记录成功/失败、日志摘要和最终 revision。
4. 恢复附件到隔离 namespace；禁止覆盖生产对象。
5. 执行 schema、数据、关系、附件和业务校验。
6. 保存 machine-readable result、命令边界、失败项与清理结果。
7. 若任一 P0 校验失败，标记 restore rehearsal BLOCKED，不进入 Migration Gate。

## Verification Items

### Database

| Check | Expected evidence |
|---|---|
| table count | source snapshot 与 restored DB 按 allowlist 一致；差异需解释 |
| row count | 13 个核心表逐表一致；忽略项必须有批准记录 |
| primary key range | 每表 min/max 与 collision/duplicate report |
| foreign key consistency | orphan、违反 RESTRICT/CASCADE/SET NULL 语义的记录为 0 或有批准解释 |
| polymorphic integrity | review/attachment/knowledge/AI target 存在、类型匹配、owner policy 可验证 |
| schema/revision | expected revision、columns/indexes/constraints 与 baseline/approved target 一致 |

### Attachments

| Check | Expected evidence |
|---|---|
| checksum | 每个 referenced blob 的 checksum 与 source snapshot 一致 |
| size | metadata size 与 restored blob byte size 一致 |
| storage key | 每个 key 可解析到唯一 blob；无越权路径或临时路径泄露 |
| link coverage | 每个 attachment link 的 target 存在且类型正确 |

### Business smoke tests

- note read：公开可见 note 仍可读，hidden/unpublished 不被 public 读取；
- question query：已恢复题目按预期状态/subject 查询；
- mistake review：已授权 owner 的 review queue/read/submit 流程可验证，跨 owner 被拒绝；
- AI run audit：authorized admin/owner 可按策略读取安全审计字段，sensitive input/output 不泄露，replay/decision 未被恢复后意外放宽。

Smoke test 的具体 endpoint、fixture IDs 和预期状态码需在执行阶段根据已批准 permission contract 固定；当前为 UNKNOWN。

## Pass/Fail and Gate Rule

通过条件：backup 可读取、restore 完整、schema/revision 对齐、数据/关系一致、附件逐项 checksum/size/key 一致、业务 smoke 通过、日志可审计。任何缺失 backup evidence、附件 checksum、owner mapping 或权限结果都保持 BLOCKED。

