# Batch 2 验证记录

## 当前状态

执行与验证完成；用户已确认 Batch 2 通过并允许开始 Batch 3 规划。

## P0-01：TDD 与迁移门禁

### Alembic 基线

```text
代码 head：010
本地数据库 current：005
待执行：006、007、008、009、010
```

使用正确的后端模块路径执行：

```text
cd backend
PYTHONPATH=. .venv/bin/alembic current
PYTHONPATH=. .venv/bin/alembic history --verbose
```

直接运行 `.venv/bin/alembic current` 会因找不到 `app` 模块失败；这不是数据库迁移
失败，后续命令必须显式设置 `PYTHONPATH=.`。

### 006–010 审查

- 006：新增 admin session、passkey、admin password；依赖既有 users。
- 007：将 folders parent FK 从 CASCADE 改为 SET NULL；依赖 005 已存在约束。
- 008：新增 audit logs；依赖 006 admin sessions。
- 009：新增音乐每日同步表。
- 010：新增 managed content entries。

迁移链连续，没有分叉。不得 stamp 或跳过任何版本。

### 恢复路径

已在仓库外创建权限为 600 的临时 PostgreSQL custom-format 备份：

```text
/tmp/blog-db-pre-batch2.dump
```

`pg_restore --list` 完整性检查通过。备份不进入 Git，Batch 2 数据库验证完成后删除。

### TDD RED

第一条行为测试：

```text
SubjectCreate / SubjectUpdate 必须 trim 名称，并拒绝纯空白名称。
```

测试文件：`backend/tests/test_taxonomy_service.py`。

预期 RED 原因：`app.schemas.taxonomy` 尚未实现。

实际结果：

```text
ModuleNotFoundError: No module named 'app.schemas.taxonomy'
1 error during collection
```

RED 与预期一致。

## P0-02：迁移漂移阻塞

首次执行：

```text
PYTHONPATH=. .venv/bin/alembic upgrade 010
```

在 005 → 006 失败：

```text
DuplicateTableError: relation "admin_sessions" already exists
```

事务回滚后 `alembic current` 仍为 005。

### 根因证据

数据库中 006–010 的目标表均已存在，但 Alembic 版本仍为 005。现有数据量：

```text
admin_sessions=16
passkey_credentials=1
audit_logs=81
netease_api_configs=1
music_source_rules=11
managed_content_entries=5
```

另外：

- `folders_parent_id_fkey` 仍为 `ON DELETE CASCADE`，说明 007 未执行。
- `passkey_credentials.public_key` 当前为 BYTEA，与当前 SQLAlchemy 模型一致，但历史
  006 migration 写的是 VARCHAR。

结论：后端 lifespan 的 `Base.metadata.create_all` 在 Alembic 之外提前建表，导致
schema 与版本链分离；不能删表重建，也不能在未验证结构时 stamp。

### 当前门禁

原批准 tasks 未包含修改历史 006–010 migration。已更新 design 与 tasks，等待用户
追加批准“数据保留型可重放迁移”后才能继续 P0-02。

### 追加批准与修复结果

用户于 2026-07-03 明确批准扩大范围，仅用于数据保留型修复 006–010，并重申禁止
stamp、删表、丢数据、跳过 007 或使用 `create_all` 代替迁移。

修复策略：

- 006、008、009、010：先 inspect 表、列、索引与约束；存在时验证并只补缺失索引，
  不存在时才创建。
- 006：新库 `public_key` 改用当前模型的 BYTEA；若旧库类型不符且已有数据则主动
  失败，禁止猜测转换格式。
- 007：inspect 实际 folder parent FK；仅当不是 SET NULL 时按真实约束名安全替换。
- 所有迁移沿正常 Alembic 链执行，不修改版本表。

执行结果：

```text
005 -> 006 -> 007 -> 008 -> 009 -> 010
alembic current: 010
重复 alembic upgrade head: 通过
```

数据保全对比：

```text
admin_sessions: 16 -> 16
passkey_credentials: 1 -> 1
audit_logs: 81 -> 81
netease_api_configs: 1 -> 1
music_source_rules: 11 -> 11
managed_content_entries: 5 -> 5
```

007 验证：

```text
folders_parent_id_fkey ... ON DELETE SET NULL
```

类型验证：

```text
passkey_credentials.public_key = bytea
```

### 011 taxonomy migration

新增并执行 `011_add_subject_taxonomy.py`：

```text
010 -> 011
alembic current: 011 (head)
重复 alembic upgrade head: 通过
```

Schema 检查：

```text
taxonomy_tables=3
subject_new_columns=5
```

历史表数据行数在 011 后仍与修复前一致。
## P0-03 taxonomy API 与 service

- 实现：Subject、Chapter、KnowledgePoint CRUD；router 仅做 HTTP 编排，service
  负责重复冲突、父级存在性、章节/科目一致性和有关联时拒绝删除。
- 权限：`/api/subjects`、`/api/chapters`、`/api/knowledge-points` 的全部路由
  均通过 router 级 `Depends(get_current_admin)` 保护，包括 GET。
- 测试：`cd backend && .venv/bin/python -m pytest tests/test_taxonomy_service.py -q`
  → `4 passed`。
- 导入检查：`cd backend && .venv/bin/python -m compileall -q app main.py` → 通过。
- 路由检查：导入 `main.app` 后确认三组 list/detail/create/update/delete 路由均已注册。
- 测试夹具说明：首次运行多用例时，`IsolatedAsyncioTestCase` 与全局 asyncpg
  连接池跨事件循环复用，首条失败为
  `RuntimeError: ... Future ... attached to a different loop`；在每个测试 teardown
  中 dispose engine 后通过。这不是 taxonomy 业务失败。
- 命令更正：第一次误用 `../.venv/bin/python`，首条输出为
  `no such file or directory: ../.venv/bin/python`；改用实际
  `backend/.venv/bin/python` 后通过。

## P0-04 前端合同与选择器

- 新增 `src/lib/api/taxonomy.ts`，显式定义 Subject、Chapter、KnowledgePoint
  及其 create/update DTO 和完整 CRUD。
- `src/lib/api/meta.ts` 的旧 `listSubjects()`、`createSubject(name)`、
  `deleteSubject(id)` 调用签名保持兼容，并委托给 taxonomy 客户端。
- `KnowledgePointSelect` 仅加载 `is_active=true` 的正式知识点，可按 subject
  过滤；包含 loading、empty、error 和 disabled 状态。
- 验证：`npx tsc --noEmit --pretty false` → 通过，无 TypeScript 错误。

## P0-05 管理页面真实浏览器验收

- 隔离运行：本机已有用户进程占用 8000/2025，未终止；本批使用后端 8001、
  前端 2026，并仅通过进程环境临时允许 2026 CORS，未改仓库配置。
- 使用一次性 `temp-admin` 登录旧 `/manage` 后，直接进入受 AuthGate 保护的
  `/manage/subjects`。
- 真实完成：创建科目 → 创建章节 → 创建知识点 → 打开知识点详情 → 更新说明 →
  刷新确认说明仍为 `Batch 2 浏览器验收`。
- 冲突验证：知识点仍关联章节时删除章节，页面显示
  `Chapter still has knowledge points`，对应 HTTP 409。
- 响应式：默认桌面视口页面正常；390×844 视口下
  `documentElement.scrollWidth === clientWidth === 390`，无横向页面溢出。
- 清理：按知识点 → 章节 → 科目顺序调用真实 API，三次均返回 204；同名验收科目
  剩余数量为 0；临时会话 logout 返回 200。
- 临时账号：第一次非交互执行 `disable-temp-admin` 的首条失败为
  `EOFError: EOF when reading a line`，未改变账号；随后输入 CLI 要求的 `yes`，
  输出 `Temporary admin account disabled: temp-admin`。

## P0-06 权限、兼容、迁移与公开页面回归

- 未登录 `GET /api/subjects` → 401；三组 taxonomy 路由的 GET 与写操作都保持
  管理员边界。
- Alembic：修复后再次执行 `alembic current` → `011 (head)`；
  `alembic upgrade head` 可重复执行，再次 current 仍为 `011 (head)`。
- 历史数据保留复核：
  - `admin_sessions=18`（修复前 16；本轮登录新增会话）
  - `passkey_credentials=1`（修复前 1）
  - `audit_logs=84`（修复前 81；本轮登录/操作新增审计）
  - `netease_api_configs=1`（修复前 1）
  - `music_source_rules=11`（修复前 11）
  - `managed_content_entries=5`（修复前 5）
- Schema：`notes_folder_id_fkey` delete rule 为 `SET NULL`；`public_key` 为
  `bytea`；3 个 taxonomy 新表均存在。
- 后端：taxonomy + temp-admin 定向测试 → `7 passed`。
- 前端：`npx tsc --noEmit --pretty false` → 通过。
- 构建：`npm run build` → 通过；32/32 静态页面生成成功，新详情路由被识别为动态
  路由。仅出现既有 `baseline-browser-mapping` 数据过期和 Node deprecation warning。
- 公开页面：禁用临时管理员后，真实浏览器未登录访问 `/notes` 与 `/mistakes`
  均正常，两个页面 console error 数均为 0。后端日志仍可观察到 `/mistakes`
  对既有管理员 review/weak-points API 的 403 请求噪音；这是 `AGENTS.md` 已登记的
  P1 权限问题，不由 Batch 2 修改，且未导致公开页面错误状态。
- 兼容：旧 `meta.ts` Subject 函数签名继续通过 TypeScript；`Note.subject` 与
  `Note.knowledge_points` 字符串字段未迁移、未修改。

## P0-07 最终审查

- 审查时补充 `SubjectUpdate(name=None)` 回归测试，先得到
  `AssertionError: ValidationError not raised`，随后让三类 update schema 对显式
  `name: null` 在请求校验层拒绝；最终定向测试仍为 `7 passed`。
- `git diff --check` → 通过。
- `src/app/manage/page.tsx` diff → 0；旧管理登录入口和业务面板未改。
- 本批隔离前后端验收进程已停止，未终止原有 8000/2025 用户进程。
- 最终数据库复核：`temp-admin.is_admin=false` 且密码散列为禁用哨兵；
  `alembic current` 仍为 `011 (head)`。
- `/tmp/blog-db-pre-batch2.dump` 在迁移、schema、数据保全与重复 upgrade 全部通过后
  已删除，未进入仓库。
- 审查结论见 `audit.md`；handoff 已填写，状态停留在等待用户确认。
