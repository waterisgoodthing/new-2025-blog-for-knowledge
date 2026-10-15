# I1 边界与恢复审计

日期：2026-07-20
状态：`IN PROGRESS`

## 范围

本文件记录 I1 的 B-01～B-06。允许静态代码审计、只读数据库/备份证据核验和隔离恢复验证；不允许迁移、权威切换、部署、生产数据写入或旧系统停写。

## B-01 权限矩阵

| 领域 | 当前入口/证据 | 匿名预期 | 管理员预期 | 失效会话/不可见资源预期 | 状态 |
|---|---|---|---|---|---|
| 公开 Note/博客/旧错题读取 | `GET /api/notes`、`GET /api/notes/{slug}` | 仅 `status=published` 且 `hidden=false` | 可读取管理范围内容 | 失效会话按匿名处理；草稿/隐藏内容为 404 | 静态代码已核对 |
| Note 写入与图片上传 | `POST/PUT/DELETE /api/notes`、`POST /api/notes/upload-image` | 401/403，不能写入 | `get_current_admin` 后可操作 | 无有效管理员身份不得写入 | 静态代码已核对 |
| 管理学习实体 | `/api/admin/questions`、`/api/admin/mistakes`、`/api/admin/review/items`、`/api/admin/drafts` | 401/403 | 路由级 `get_current_admin` | 非管理员不得枚举或读取 | 静态代码已核对 |
| 旧复习接口 | `/api/review/*` | 401/403 | `get_current_admin` 后可读取/提交 | 未认证不得访问队列、统计、计划或提交 | 静态代码已核对 |
| 私有附件 | `/api/admin/attachments`、`/api/admin/attachment-links` | 401/403，不能读写或取内容 | 路由级 `get_current_admin` | 已删除/不存在资源按服务契约失败，不得泄露文件 | 静态代码已核对 |
| 治理与 AI | `/api/admin/dashboard`、`/api/admin/drafts`、`/api/admin/captures`、AI 管理路由 | 401/403 | 管理员专用 | 失效会话不得重试管理员操作 | 静态代码已核对 |
| 管理页面 | `/manage/(workspace)/*` | `AuthGate` 拦截/跳转 | 可进入工作区 | 失效会话回到既有登录入口 | 静态代码已核对 |

### B-01 观察与限制

1. `AUTH_BYPASS` 仅在两个开关同时为 `true` 时生效；生产启动代码拒绝该组合。此为源码观察，未在生产环境执行验证。
2. 本矩阵是当前路由/页面声明的基线，不替代匿名、管理员、失效会话和资源不可见性的运行时 API/浏览器测试。
3. 目标 `/api/public/**` 尚未作为现状前提；其过渡矩阵在 B-03 建立。

## B-02 所有权与稳定 ID 冻结

| 领域 | 正式聚合与稳定身份 | 所有权冻结规则 | 现状观察 | 后续限制 |
|---|---|---|---|---|
| Content | 既有 `Note.id` UUID；`slug` 仅为公开兼容标识 | 新私有内容必须关联管理员 owner；legacy Note 在单管理员过渡期由管理 API 防护 | Note 没有统一 `owner_id` 字段 | 不把 slug、文件夹路径或 GitHub 路径当作主键 |
| Knowledge | `Subject.id`、`KnowledgePoint.id` 与链接表主键 | 当前为单管理员共享学习分类；若引入多 owner，必须单独设计 owner 迁移 | taxonomy 使用整数主键和外键 | 不复制知识点以表示用户状态；掌握度/复习属于其他领域 |
| Question/Draft | `DraftItem.id`、`QuestionDraft.id`、`Question.id` UUID | `created_by` 是创建审计，不代替 owner 策略；新私有写入经管理员边界 | 已有 draft/source/target 稳定引用 | 关联只能使用类型化 ID，不得依赖展示路径 |
| Mistake | `MistakeDraft.id`、`Mistake.id` UUID；与 Question/DraftItem 外键 | 新错题链路保持私有管理员数据；旧 `Note(type="mistake")` 在兼容期仍受既有规则保护 | 新旧模型并存 | 不以“模型存在”推断旧数据已迁移 |
| Review | `ReviewItem.id`、`ReviewRecord.id` UUID；目标使用 `target_type + target_id` | 复习队列、提交与历史只允许管理员 | 管理路由已受保护 | 目标类型须有固定命名空间与外键/约束设计，不能仅依赖自由文本 |
| Attachment | `Attachment.id`、`AttachmentLink.id` UUID；`storage_key` 唯一 | 默认私有；`created_by` 记录创建者；公开必须有未来显式发布关系 | 当前约束只允许 private 和本地存储 | 不用 URL、原始文件名或物理路径作业务身份 |
| Folder/workspace node | 当前 `Folder.id` UUID；目标 `workspace_node` 尚未实现 | 当前 Folder 作为 legacy 组织能力；未来 workspace node 必须由资源引用连接领域实体 | Folder 无 owner 字段，且只关联 Note | 未批准前不得新增 workspace schema 或将业务状态搬入节点 |

### B-02 跨领域规则

1. UUID/数据库主键是稳定身份；slug、标题、文件名、显示路径、`storage_key` 和 GitHub 路径均不是可迁移主键。
2. 每个多态引用必须同时保存受限 `target_type` 与稳定 `target_id`，并在对应 schema/数据库约束中限定允许类型。
3. `created_by`、审计 actor 与 owner 是不同概念：前两者记录操作来源，owner 定义资源访问边界。
4. 在当前单管理员过渡期，缺少逐行 owner 的 legacy 数据不得开放给匿名写入，也不得被误标为已完成 owner backfill。
5. 新 `workspace_node`、公开发布关系或多用户 owner 模型都属于后续批准的 schema/API 工作，I1 只冻结规则，不创建它们。

## B-03 API、页面、旧写入口与导出方向矩阵

| 能力 | 当前调用方/页面 | 当前 API 或写入方向 | 目标方向 | 兼容/退役条件 | 本轮结论 |
|---|---|---|---|---|---|
| 公开笔记、博客、legacy 错题 | `/notes`、`/notes/[slug]` 等公开页面 | `GET /api/notes`、`GET /api/notes/{slug}` → PostgreSQL Note；匿名过滤 `published + hidden=false` | 未来可引入 `/api/public/**` 读模型 | 字段映射、匿名/管理员/隐藏/草稿契约测试、调用方迁移、观测窗口与批准的退役记录 | 旧读端点继续保留 |
| Legacy Note 写入 | write-note/write-mistake 和管理编辑流 | `POST/PUT/DELETE /api/notes` → PostgreSQL Note，管理员保护 | 迁移期继续兼容；新学习实体走 `/api/admin/**` | 旧数据映射、公开别名与回滚证据完成前不得停写或删除 | 仍是有效兼容写入口 |
| 新学习实体 | `/manage/(workspace)/questions`、`mistakes`、`review`、`drafts` | `src/lib/api/*` → `/api/admin/questions`、`mistakes`、`review/items`、`drafts` → PostgreSQL | 保持管理员 API 分层 | I2 浏览器闭环、权限和数据权威证据 | 当前管理链路已观察到 |
| 复习兼容接口 | legacy review 页面/API 客户端 | `/api/review/*` → legacy Note 型复习，管理员保护 | 后续以独立 Review Item/Record 为主时需保持兼容 | 队列、提交、统计、链接与公开入口逐项契约验证 | 双轨并存，不得假定已切换 |
| 附件与目录 | `/manage/(workspace)/attachments`、题目/错题编辑、legacy folders | `/api/admin/attachments`、`/api/folders` → PostgreSQL + 本地附件存储 | 未来 workspace 资源引用与显式发布关系 | 私有读取、恢复、冲突、审计和路径兼容验证 | 当前仅私有附件模型已观察到 |
| 可编辑静态内容 | 管理内容页面与 `src/lib/api/content.ts` | `/api/content/*` → `managed_content_entries`/本地受控资源 | PostgreSQL 仍为正式写入来源 | 逐页面调用链、公开构建输入和导出恢复策略待验证 | 代码观察为 backend-native |
| GitHub/Markdown 导出 | 文档和旧架构描述 | 当前活动调用链未在 `src/`/`backend/` 静态搜索中确认 | 只作导出、归档、公开构建输入或恢复副本 | 需在 I1 后续只读调用链与运行环境核验；不得引入双写 | `UNKNOWN`，历史文档存在相互矛盾表述 |

### B-03 冻结规则

1. 当前 `/api/notes` 和 `/api/review/*` 是兼容合同，I1 不改名、不删除、不停写。
2. `/api/public/**` 是未来目标，不是当前路由；任何新增端点必须先并行并通过权限/可见性契约验证。
3. 管理写入以 `src/lib/api/* → FastAPI → PostgreSQL` 为当前代码观察；GitHub 不得被假定为现行主写入来源，也不得在无证据时宣布已完全退役。
4. 所有旧写入口、导出方向和公开别名只有在 I9/I10 的映射、对账、回滚和单独批准后才可变更。

## B-04 备份可读性证据

| 所需证据 | 本轮观察 | 结论 |
|---|---|---|
| 当前 revision 的数据库 dump | 未在工作区发现 dump、位置、时间戳或可读性校验记录 | `BLOCKED` |
| 当前附件副本 | 仅发现 `backend/uploads/.gitkeep` 与附件实现代码；未发现副本、清单或哈希 | `BLOCKED` |
| 数据库与附件对应关系 | 历史文档指出该关系未证明；本轮未发现更新证据 | `BLOCKED` |
| 恢复说明 | `docs/backup-restore.md` 时间为 2026-06-03，历史恢复演练对应旧 revision | 历史参考，不能证明当前 revision |

结论：没有当前 revision 的新鲜、可读、可定位的数据库与附件备份证据。Migration Gate 保持 `BLOCKED`。

### B-04 自主查找范围与结果

已在项目、Documents、Downloads、Desktop、已挂载卷、本机容器/卷、用户级备份调度、用户 crontab 与 Time Machine 元数据中进行只读查找。

- 未找到项目数据库 dump、附件副本、哈希清单或恢复快照。
- 未发现本机容器或容器卷。
- 未发现外部备份卷或备份调度；Time Machine 未配置目的地。
- 本机存在 `pg_dump` 与 `pg_restore` 工具，但工具本身不构成备份或恢复证据。
- 未读取环境变量、凭据、数据库内容或候选业务数据文件。

### B-04/B-05 已批准执行方案

用户已授权在 2026-07-20 设计并执行新的“数据库 + 附件”备份与隔离恢复验证。执行边界如下：

1. 只脱敏确认数据库主机、端口、数据库名和附件目录；不在记录或终端输出凭据。
2. 备份产物存放在仓库外的时间戳目录，避免将业务数据纳入 Git 工作树。
3. 数据库通过一致性 `pg_dump` 备份；附件通过只读复制、清单和 SHA-256 核验备份。
4. 恢复只写入新建的隔离临时数据库和临时附件目录；不得连接应用到生产写入目标。
5. 验证包含 dump 可读性、恢复后的 revision、表/附件清单和哈希核对；不运行 Alembic upgrade/downgrade。
6. 临时恢复环境仅在验证完成且结果已记录后清理；原始备份保留，清理动作不影响源数据库或源附件。

### B-04 当前备份证据（2026-07-20）

| 项目 | 结果 |
|---|---|
| 备份位置 | `/Users/limengyang/Backups/2025-blog-public/20260720T164919/`，在仓库外，不纳入 Git 工作树 |
| 数据库 | custom-format `database.dump`，206,881 bytes；已生成 SHA-256 文件并通过 `pg_restore --list` 可读性检查 |
| 源 revision | `020` |
| 源关键计数 | 38 public tables、1 attachment、13 notes、3 questions、3 mistakes、3 review items |
| 附件快照 | `backend/uploads` 2 个文件；`public/images/pictures` 10 个兼容图片；两类均生成源/备份 SHA-256 清单并逐项一致 |
| 源数据安全 | 使用 `pg_dump` 和只读文件复制；未执行源库 DDL/DML、迁移、downgrade 或删除 |

结论更新：B-04 `PASS`。此前缺失的当前 revision 数据库与附件备份证据已补齐。

## B-05 隔离恢复

状态：`BLOCKED / NOT RUN`。

B-04 未提供可恢复的当前数据库与附件副本，因而不存在可安全使用的输入。未执行 `pg_restore`、未创建临时数据库、未写入附件、未启动恢复后的应用，也未删除任何资源。

### B-05 当前隔离恢复验证（2026-07-20）

| 验证项 | 结果 |
|---|---|
| 隔离数据库 | 新建独立 PostgreSQL 16 临时 cluster，仅监听临时 Unix socket；未使用源库的创建数据库权限 |
| 数据库恢复 | `pg_restore --exit-on-error --no-owner --no-privileges` 成功完成 |
| 数据核对 | restore revision 为 020；38 public tables、1 attachment、13 notes、3 questions、3 mistakes、3 review items，与源快照逐项一致 |
| 附件恢复 | 数据库附件与兼容图片快照均恢复到独立临时目录；SHA-256 清单逐项一致 |
| 生命周期 | 临时 PostgreSQL 服务已停止；临时 cluster 和附件目录已移入系统废纸篓，可恢复；正式备份保留在仓库外 |
| 排除项 | 未执行 Alembic upgrade/downgrade、未连接恢复应用、未改源数据库或源附件 |

结论更新：B-05 `PASS`。当前 revision 的数据库与附件联合恢复已在隔离环境验证。

## B-06 Schema Authority 与启动行为审计

| 检查项 | 观察 | 结论 |
|---|---|---|
| 本地 Alembic head | `alembic heads` 输出单一 `020 (head)` | 代码库 migration 链在本地为单 head |
| 应用启动 | `EXPECTED_ALEMBIC_REVISION = "020"`；启动前只读取 `alembic_version` | 启动代码不再调用 `Base.metadata.create_all`，符合 fail-closed readiness 方向 |
| Alembic metadata | `backend/alembic/env.py` 使用 `SCHEMA_LIFECYCLE_METADATA` | schema lifecycle 明确从 registry 取得，而非隐式导入 |
| Registry 范围 | registry 显式列出正式模型，排除 `guest_messages`、`guest_message_bans` | guest schema 是已记录的治理例外，不得被 autogenerate 静默纳入 |
| 当前数据库与 metadata 漂移 | 对已确认的 localhost 源库运行 `alembic current` 得到 `020 (head)`；`alembic check` 输出无新 upgrade operations | `PASS` |
| migration 风险 | 020 含数据更新、约束/表变更；历史 downgrade 含 drop/删除路径 | 任何 upgrade/downgrade 必须由备份、隔离恢复、SQL 审查和单独批准保护 |

### B-06 修复与验证计划

1. 在 B-04/B-05 通过后，仅对已确认的隔离数据库运行 `alembic current`、`alembic history`、`alembic heads` 与 `alembic check`。
2. 若 `alembic check` 产生差异，先将每项分为“registry 例外、既有物理 schema、ORM 漏登记、未批准模型变更”四类；不得直接 autogenerate 或执行 migration。
3. guest 表继续保持显式排除，直到其来源、owner、保留策略和 Alembic 管理决策获单独批准。
4. 生产环境禁止以 `create_all`、直接 downgrade 或手工 DDL 修复 schema；任何修复先写设计、任务、回滚和验证记录，再请求批准。

结论更新：B-06 `PASS`。静态审计、修复计划与已确认 localhost 源库的 revision/drift 检查均完成；guest schema 仍是明确治理例外，而非自动纳管对象。

## I1 退出状态

- B-01：`PASS`，静态权限矩阵已建立。
- B-02：`PASS`，所有权与稳定 ID 规则已冻结。
- B-03：`PASS`，API、页面、旧写入口和导出方向矩阵已建立。
- B-04：`PASS`，当前 revision 的数据库与附件备份、清单和可读性证据已生成。
- B-05：`PASS`，隔离 PostgreSQL cluster 与临时附件目录恢复及核对已完成。
- B-06：`PASS`，静态 schema authority 审计、源库 `020 (head)` 与无新升级操作检查已完成。

I1 总体：`PASS / I2 APPROVAL REQUIRED`。Migration Gate 的备份、恢复与 schema authority 前置证据已补齐；这不授权 I2、迁移、切换、部署或任何新的 schema 操作。I2 仍需单独批准。
