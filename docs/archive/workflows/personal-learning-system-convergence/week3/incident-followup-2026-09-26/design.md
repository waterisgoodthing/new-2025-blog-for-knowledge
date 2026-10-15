# 根因与设计

INC-01：外置 CLI guard 可被直接 Alembic 跳过。INC-02：默认 .env 指向 blog_v2；现 conftest 在 collection 后才按源码正则检查，文件/marker 豁免还可放行生产或远程库，手动脚本不受 pytest 保护。

最小修复：新增 `backend/app/utils/scratch_db_safety.py`；conftest 加载即注册 Engine `do_connect` 监听，检查最终 DBAPI 参数，不再按文件/marker 豁免。sync/async 普通 SQLAlchemy 路径在驱动调用前拒绝非 scratch/非本地和 libpq 重定向。纯 in-memory SQLite 允许。

四个活动 `_pr09_evidence_*`、`_pr10_n1_evidence.py`、`_pr13_attempt_count_evidence.py` 在导入 app.database 前校验 Settings URL。Alembic 在线 engine 创建前校验 URL。非 scratch 的 `BLOG_APPROVED_MIGRATION_TARGET=host:port/database` 只作为本次调用目标确认，不是用户授权，不能写入 .env；本轮未设置或使用此确认。

迁移文件/schema无变化，G2 schema replay不触发；认证不变，G3 auth变更不触发；无迁移执行/生产行为，G5执行不授权。独立技术评审检查连接隔离与绕过。

回归拒绝 URL query 重定向、connect_args host/dbname/hostaddr、PGHOSTADDR/PGSERVICE/PGSERVICEFILE/PGOPTIONS。应用启动不安装监听，不影响常驻 web engine。
