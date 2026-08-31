# Schema Authority Decision

日期：2026-07-14  
决策状态：设计结论；未执行任何 required change。

## Current State

当前谁可以改变 schema：

```text
Application startup Base.metadata.create_all
                         +
Alembic migration chain
                         =
multiple schema authority
```

证据：`backend/main.py` 的 lifespan 在应用启动时调用 `Base.metadata.create_all`；`backend/alembic/env.py` 通过 `target_metadata = Base.metadata` 提供版本化 migration chain。当前 Alembic 为 `018 (head)`，但 `alembic check` 仍报告 4 个 nullable drift 与 1 个 index drift。

另有 coverage 证据：运行时 target metadata 包含 37 张模型表，但 migration history 的静态 create-table inventory 只有 35 张；`guest_messages` 与 `guest_message_bans` 的 schema provenance 尚未闭合。

## Target State

目标架构：

```text
Alembic Migration
        |
        v
Database Schema
```

Application startup 只做 revision/readiness/health checks，不承担 schema provisioning。`Base.metadata` 仍是 Alembic 对照的 model metadata，但模型注册必须显式、可审计，并与 migration history 逐表对账。

## Required Changes (Design Only)

### `create_all` 处理建议

在后续获批实施阶段，将生产 application lifespan 中的 `create_all` 移出 schema provisioning 路径；启动流程改为只读 revision/readiness 检查。对本地开发与测试建立显式隔离数据库/fixture 策略，不以生产启动行为补齐 schema。

### Migration authority 建议

将 Alembic 定义为唯一 schema change authority。任何 upgrade、downgrade、新 migration 或旧表删除必须作为独立批准的执行动作，且先有 backup/restore、owner、权限和 drift closure evidence。

### Metadata import 修正建议

不要依赖 `app.models` package import side effect 作为 coverage 保障。后续设计应形成显式 model registry 或等价的审计清单，使 `env.py` 的 target metadata coverage 能逐表验证。实施前需确认不会重复注册、改变表定义或引入意外 import side effect。

### Drift closure strategy

对 `folders.sort_order`、`folders.created_at`、`folders.updated_at`、`notes.sort_order` 和 `idx_notes_folder_id` 先完成 database/model/migration 三方 read-only reconciliation：

1. 核对 exact DDL、defaults、nullable 与现有 NULL 数据影响；
2. 核对 migration 005/007 的历史意图和模型当前声明；
3. 对每项归类为 `database drift`、`model drift`、`migration omission`、`metadata registration issue` 或 `unknown`；
4. 只有分类、风险与执行方案获批后，才可在后续阶段设计 migration；
5. 以 clean `alembic check` 作为 schema authority closure 的必要证据。

## Decision

```text
Current authority: Application create_all + Alembic (not converged)
Target authority: Alembic-only
Current decision: DESIGNED, not implemented
Migration Gate: BLOCKED
```

