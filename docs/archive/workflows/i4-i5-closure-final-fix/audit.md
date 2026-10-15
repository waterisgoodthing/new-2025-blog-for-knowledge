# 现状审计

日期：2026-07-24

## 已复现事实

1. `backend/.env` 当前连接 `blog_db`；只读查询显示 `alembic_version=020`，应用 `backend/main.py` 要求 `022`。
2. 四文件组合为 `test_attempt_service.py`、`test_admin_profile_routes.py`、`test_dashboard_dependency_lifecycle.py`、`test_dashboard_routes.py`；当前环境因 schema 未升级产生多项 `UndefinedTable/UndefinedColumn`，并伴随事务污染/异步资源警告，不能把本次输出等同于审查中的 15/2 结果。
3. `test_dashboard_dependency_lifecycle.py` 使用多个 `asyncio.run()`，并通过全局 `app.database.engine`、`async_session` 和 `TestClient` 混合测试。
4. `src/layout/head.tsx` 的 viewport 含 `maximum-scale=1.0, user-scalable=no`，违反仓库的用户缩放规则。
5. `test_summary_preserves_independent_failures_and_maps_empty_storage_to_healthy` 同时注入 learning 与 activity 失败，缺少三个独立故障场景的持久化回归覆盖。

## 需要分离的证据层

- 代码修复证据：可在当前环境先完成并用不依赖 022 的单元/模拟测试验证。
- 真实后端证据：必须指向已确认 `022 (head)` 的隔离数据库，并记录数据库名、current/heads 和组合测试输出。
- 浏览器证据：必须使用生产构建和无禁缩放 viewport，在真实 022 后端会话或明确标注的受控环境中采集。
