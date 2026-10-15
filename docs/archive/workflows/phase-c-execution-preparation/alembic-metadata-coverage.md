# Alembic Metadata Coverage Audit

日期：2026-07-14  
范围：Phase C+1.2；模型注册、Alembic target metadata 与 migration history 的覆盖关系。

## Coverage Chain

```text
SQLAlchemy Models
        |
        v
Base.metadata
        |
        v
Alembic target_metadata
        |
        v
Migration history
```

### Observed behavior

- `backend/alembic/env.py` 显式导入 `note`、`music`、`recommendation`、`taxonomy`、`question`、`mistake`、`review_item`、`attachment` 模块。
- 这些模块的首次导入会先执行 `app.models` package 的 `__init__.py`；该文件又导入 content、folder、session、audit、music_daily、guest_message、AI、capture 等模块。
- 在干净 Python 进程中仅导入 `app.models.note` 后，`Base.metadata` 观察到 37 张表。由此可见，当前运行时覆盖是完整的，但依赖 package import side effect，而非 `env.py` 的显式、可审计注册。
- Alembic `target_metadata = Base.metadata`，所以当前运行时 Alembic target 也观察到 37 张表。
- 对 migration 文件进行静态 history inventory 后，发现 35 张表有 `op.create_table` 记录；`guest_messages`、`guest_message_bans` 在模型/当前数据库存在，但未发现 migration `create_table` 记录。

## Model Coverage Matrix

`Imported` 分为 `direct`（env.py 直接导入的模块）和 `indirect`（经 models package 初始化间接导入）。`Alembic visible` 是当前运行时 target metadata 观察结果；`Migration history` 是 migration 文件静态 inventory，不等同于数据库当前存在。

| Model | Imported | In `Base.metadata` | Alembic visible | Status |
|---|---|---:|---:|---|
| `Note` / `note_tags` | direct | yes | yes | REVIEW：model index drift remains |
| `Tag` / `Subject` / `Category` / `User` | direct | yes | yes | PASS at runtime; history covered |
| `MusicItem` | direct | yes | yes | PASS at runtime; history covered |
| `DailyRecommendation` | direct | yes | yes | PASS at runtime; history covered |
| `Chapter` / `KnowledgePoint` / `KnowledgePointLink` | direct | yes | yes | PASS at runtime; history covered |
| `DraftItem` / `QuestionDraft` / `Question` / `QuestionSource` | direct | yes | yes | PASS at runtime; history covered |
| `MistakeDraft` / `Mistake` | direct | yes | yes | PASS at runtime; history covered |
| `ReviewItem` / `ReviewRecord` | direct | yes | yes | PASS at runtime; history covered |
| `Attachment` / `AttachmentLink` | direct | yes | yes | PASS at runtime; history covered |
| `ManagedContentEntry` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration |
| `Folder` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration; nullable drift |
| `AdminSession` / `PasskeyCredential` / `AdminPassword` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration |
| `AuditLog` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration |
| `MusicSourceRule` / `MusicCandidate` / `DailySong` / `MusicSyncLog` / `NetEaseApiConfig` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration |
| `GuestMessage` | indirect via `models/__init__.py` | yes | yes | BLOCKED：no migration create record found |
| `GuestMessageBan` | indirect via `models/__init__.py` | yes | yes | BLOCKED：no migration create record found |
| `AiCallLog` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration; history covered |
| `AiRun` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration; history covered |
| `CaptureItem` | indirect via `models/__init__.py` | yes | yes | REVIEW：implicit registration; history covered |

## Coverage Conclusion

运行时 `Base.metadata` 与 Alembic `target_metadata` 当前覆盖 37 张模型表，但覆盖方式不够显式；migration history 只覆盖 35 张模型表。`guest_messages` 与 `guest_message_bans` 的当前来源无法在本阶段安全归因，分类为 `unknown`，候选风险为 migration omission 或 create_all/外部 schema provisioning 产生的非版本化表。

在显式注册、migration history provenance 与 guest message 表来源闭合前，Alembic metadata coverage 不得标记 READY。

