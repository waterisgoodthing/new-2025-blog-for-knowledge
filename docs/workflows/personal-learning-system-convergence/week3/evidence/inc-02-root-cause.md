# INC-02 — `blog_v2.notes` Week 3 夹具数据泄漏（read-only root cause）

- agent_id: `INC-02-investigate` · profile: `senior-qa-sdet` · role: `verifier`
- Mode: **strictly read-only**. No DML/DDL; 所有 SQL 均为 SELECT / information_schema 元数据。
- Target (redacted): `backend/.env` 中 `DATABASE_URL=***@localhost:5432/blog_v2`（user=blog_user，无明文输出）。

## 1. 默认 DB 目标（确认）

- `backend/.env` 将 `DATABASE_URL` 指向 `blog_v2`；`backend/app/config.py:8` 默认值仅为模板 `blog_db`，被 `.env` 覆盖。
- `backend/app/database.py:7-11` 在模块 import 时 `get_settings().DATABASE_URL` 构建全局 `engine`/`async_session`。
- pydantic `env_file=".env"` 是 **CWD 相对路径**：从 `backend/` 运行 pytest 时加载 `.env` → `blog_v2`；从仓库根目录运行时找不到 `.env` → 落回 `blog_db` 模板（连接会失败）。
- **仓库内不存在任何 `conftest.py`**（`find . -name conftest.py` 为空）→ 无全局 DB 守卫、无自动 fixture、无 pytest 级 fail-closed 机制。
- 各 DB 测试获得连接串的方式分两类：
  - `from app.database import async_session, engine`（读 config 默认值，**隐式**）→ 直接命中 `blog_v2`。
  - `create_async_engine(os.environ["DATABASE_URL"])`（读裸环境变量，**显式**）→ 未设置时 `KeyError` 报错，不静默落 `blog_v2`。

## 2. 触发路径（确认）

- `scripts/week3-scratch-guard.py` 是 **CLI 包装器**（`:258-284`），仅在被显式调用时把已校验的 scratch DSN 注入子进程 `DATABASE_URL`；它不是 pytest 运行时强制机制。
- `test_pr09_wk3_runner.py` / `test_pr09_rework.py` 的 DB 类 `asyncSetUp` 以 `SELECT 1 FROM public.notes LIMIT 1` 连通性判定 `_db_ready`，**只测连通、不验库名**；`blog_v2` 本地可达 → self-skip 永不触发。
- 直写路径：未用 guard 直接 `pytest` 运行（从 `backend/`）→ engine 绑定 `blog_v2` → `_insert_legacy_mistake_note`（slug `wk3-<hex>`）或 `_seed_migratable_note`（slug `pr09rw-<hex>`）INSERT+commit。
- 残留成因：`run_wk3_migration` 依赖的 ledger 表（`legacy_note_migrations` 等）在 `blog_v2` **不存在** → 迁移抛错（wk3_runner 中该异常未被捕获 / rework 中被 `except … skipTest` 吞掉），发生在 seed-commit 与 cleanup-DELETE 之间 → 夹具 note 遗留；rework 的 `_setup_infra` 还会遗留 `subjects`/`knowledge_points` 行。

## 3. 受影响测试清单（有 guard / 无 guard）

| 类别 | 测试文件 | 守卫情况 |
|------|----------|----------|
| 直写（无 guard）| `test_pr09_wk3_runner.py`、`test_pr09_rework.py` | 仅连通性 self-skip；读 config → 默认落 `blog_v2`。**实害源** |
| 直写（无 guard，且无 self-skip）| `test_pr10_kp_analytics_service.py`、`test_pr10_verify_matrix.py`、`test_pr11_dashboard_service.py`、`test_pr12_note_knowledge_points_service.py`（3 commit）、`test_pr13_practice_service.py`、`test_pr13_verify_practice.py` | 读 config → 默认落 `blog_v2`；多数不 commit（事务回滚，不产残留但仍在 blog_v2 上执行写）。高风险 |
| 显式 env（KeyError 兜底）| `test_pr09_verify_api_contract.py`、`test_pr09_verify_http.py`、`test_pr10_*_http.py`、`test_pr10_verify_contract.py`、`test_pr11_dashboard_http.py`、`test_pr12_*_http.py`、`test_pr12_verify_api.py`、`test_pr12_verify_concurrency.py`、`test_pr13_practice_http.py` | 必须显式 `DATABASE_URL`；未设即报错。若 shell 恰导出 blog_v2 仍可直写 |
| 无 DB | `test_pr09_migration.py`、`test_pr09_permissions.py`、`test_pr09_routes.py`、`test_pr09_legacy_mistake_freeze.py`、`test_pr09_verify_api_contract`（纯部分）、`test_pr10_kp_analytics_contract.py`、`test_pr11_dashboard_service`（部分）、`test_week3_contracts.py`、`week3_contracts_support.py` | 无 DB 访问，不受影响 |
| 支持脚本 | `_pr09_evidence_seed.py`、`_pr09_evidence_constraint.py`、`_pr10_n1_evidence.py`、`_pr13_attempt_count_evidence.py` | 用 `app.database` 且 commit；无 guard，同样高风险 |

## 4. 现存痕迹（确认，只读）

- `blog_v2.notes` 匹配夹具：**9 行**（slug `wk3-%` 或 `pr09rw-%` 或 title=`pr09-rework-note`）。
  - `wk3-<hex12>` ×8，title=`'t'`，type=`mistake`，status=`published`
  - `pr09rw-94a674944fc4` ×1，title=`'pr09-rework-note'`，type=`mistake`，status=`published`
  - created 窗口：2026-09-23 14:26:58 → 2026-09-24 16:54:12。
- **无级联**：ledger 表（`legacy_note_migrations/_events/_rejections`、`legacy_migration_approval_authorizations`）在 blog_v2 **不存在**；窗口内 `mistakes`/`review_items`/`review_records`/`knowledge_point_links` created 计数均 **0**；`mistakes` 无 `pr09%`/`original-title` 标题。→ 仅 notes 残留，无 mistakes/review_items/attempts 级联。
- **额外残留**：`subjects` `pr09-rework-subj` ×1、`knowledge_points` `pr09-rework-kp` ×1（rework `_setup_infra` 遗留）。
- 对照：`notes` 全库 published+type=mistake 共 14 行，其中 9 行为夹具 → 其余 5 行为真实内容，不得误删。

## 5. 修复方案（建议，未实施）

**推荐：conftest 全局 fail-closed 守卫。**
- 新建 `backend/tests/conftest.py`：在**收集期**（pytest 最早钩子）解析将用的 `DATABASE_URL`（pydantic `get_settings()`），校验库名：
  - Week 3 DB 测试默认仅允许 `^astra_week3_[a-z0-9_]+$`；
  - 命中 `blog_v2`/`blog_db` 时 `pytest.exit(…, returncode=2)` 并输出错误（含触发文件定位）；
  - 提供显式 marker/夹具（如 `@pytest.mark.db("legacy-local")` 或环境变量白名单）放行确实需要本地 dev 库的既有测试。
- **影响评估（既有测试）**：Week 1/2 及遗留测试（`test_attempt_service.py`、`test_dashboard_routes.py`、`test_mistake_review_service.py`、`test_taxonomy_service.py` 等约 20+ 文件）同样 `from app.database import …` 且依赖本地 `blog_v2`（0 commit、靠回滚）→ 裸 fail-closed 会整批 break；须按 marker 白名单放行，或为其改用独立 dev 库（非 `blog_v2`）后再守卫。
- 注意：`os.environ["DATABASE_URL"]` 类测试不受 conftest 影响（读裸 env），无需改动。

**备选：把 config 默认 `DATABASE_URL` 改为无效/占位值，强制显式传入。**
- 影响面：`blog_db` 模板默认（config.py:8）与 `.env` 均被改成占位后，任何未显式设 URL 的运行（含本地 app 启动、遗留测试）都会立即失败——是“fail-fast”而非“fail-closed”，运维摩擦更大；仍挡不住“显式导出 blog_v2 的 shell”。仅作兜底配合推荐方案。

**推荐组合：conftest fail-closed（主）+ 保持 guard 脚本职责不变 + 可选把 config 默认改为占位（防裸跑）**。仅靠现有 guard 文档说明不构成防护。

## 6. 清理建议（建议，未实施）

- 9 行 notes 夹具（按 `slug LIKE 'wk3-%' OR slug LIKE 'pr09rw-%'` 且 created ∈ [2026-09-23, 2026-09-25)）可安全删除：与真实内容（其余 5 行 published mistake 型 notes）无交集、无 FK 引用（无 ledger 表、无级联行）。
- 另删 `subjects.name='pr09-rework-subj'`、`knowledge_points.name='pr09-rework-kp'`（孤立，无引用）。
- **授权**：删除属 DML + 生产/dev 数据写操作，需 owner 显式授权（per AGENTS.md 变更纪律）；建议由 blog_v2 数据 owner 一次性批准。
- **执行方式**：单条事务内 `DELETE FROM notes WHERE slug LIKE 'wk3-%' OR slug LIKE 'pr09rw-%' AND created_at BETWEEN '2026-09-23' AND '2026-09-25'`（先 `SELECT count(*)=9` 双校验再删），随后删两个 taxonomy 行；删除前先 `pg_dump` 或记录 9 个 uuid（上文已列出 2 个，其余见 SELECT 结果）以可回滚。不触碰 `pr09-rework-subj` 之外任何 subjects/kp。
- 仅清除数据不足以防复发 → 必须同时落地 §5 守卫。

## 7. 证据路径

- SQL 证据（只读脚本，SELECT/information_schema only）：`/var/folders/…/T/opencode/inc02_readonly_check.py`（临时，本会话内）。
- 关键 SELECT 输出（见上）：9 notes（含 id/slug/title/type/status/created）、4 张 ledger 表 ABSENT、窗口级联计数 0、subjects/kp 残留 1/1。
- 源码证据：`backend/.env`、`backend/app/config.py:8,44`、`backend/app/database.py:7-11`、`scripts/week3-scratch-guard.py:53-57,258-284`、`test_pr09_wk3_runner.py:137-207`、`test_pr09_rework.py:173-324`、无 `conftest.py`（全仓 find 为空）。

## 8. 状态

`PASS`（只读调查完成）。未实施任何修复/清理/写入。