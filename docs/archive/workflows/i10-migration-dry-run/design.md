# I10 设计

## 决策与边界

E-01～E-04 分离来源清单、SHA-256、字段映射、重复/冲突规则与门槛判断。
用户于 2026-07-31 选择单管理员 backfill：全部 legacy 实体映射到 canonical
owner `4c503215-b158-4162-b472-79df8289ed0a`。该决定只解除 owner 决策
UNKNOWN，不授权生产写入、部署、推送或 E-05/E-06。

## 执行架构

```text
已验证 024 备份
  -> 新建一次性隔离 PostgreSQL 数据库
  -> 恢复 12 类、121 条 source rows
  -> 隔离目标升级到当前代码 head 025
  -> 校验 revision/head/check 与 manifest source hash
  -> 创建隔离 sidecar owner_backfill 表
  -> 写入 manifest 的 121 条 source PK -> canonical owner 映射
  -> 校验覆盖、唯一性、owner FK、业务关系 orphan、hash drift
  -> 运行测试与独立复核
  -> 导出不含个人正文的 JSON/Markdown 证据
  -> 删除隔离数据库并确认 catalog 中不存在
```

日常 `blog_db` 不是恢复目标，也不执行任何 DDL/DML。隔离数据库名必须带
本轮时间戳并在创建前确认不存在；所有写入命令必须显式指定该数据库名。

## Backfill 表

隔离库临时 sidecar 表至少包含：

- `source_table`
- `source_id`
- `owner_id UUID NOT NULL REFERENCES users(id)`
- `source_row_hash`
- `disposition`
- `approval_reference`
- `rollback_source`

`(source_table, source_id)` 为主键。导入必须来自获批 manifest，不允许按
`is_admin`、`created_by`、slug、路径或关联对象临时推断 owner。每条映射都
必须等于 canonical owner。

## 完整性审计

1. manifest、source、sidecar 都必须为 121 条，12 类逐表计数一致。
2. missing、extra、duplicate、hash drift、owner conflict 均为 0。
3. sidecar `owner_id` FK orphan 为 0，canonical owner 恰好存在一条。
4. 既有七类 FK/多态关系 orphan 均为 0。
5. 从 024 备份恢复后仅在隔离目标升级到当前代码 head 025；
   `current=head=025` 且移除临时 sidecar 后 `alembic check` clean。
6. 任一 UNKNOWN 或非零 drift/orphan 均 fail closed。

## 回滚与清理

本轮回滚不是修改日常库，而是销毁一次性隔离数据库。无论成功或失败都要
终止隔离连接、删除目标并以 `pg_database` 复核为 0。备份、原 manifest 和
日常库保持只读/不变；证据只保存计数、hash、revision、owner ID 和检查结果。
