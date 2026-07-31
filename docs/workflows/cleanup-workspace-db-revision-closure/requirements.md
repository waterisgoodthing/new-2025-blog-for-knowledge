# CLEANUP 需求文档

## 背景

P0-AUTH 权限功能已通过，但工作区仍因未跟踪 `/workspace` 原型的两个类型错误而无法通过主工作区 TypeScript/生产构建；默认日常数据库仍为 revision 024，而当前源码期望 025。

用户选择：

- `/workspace`：方案 A，删除原型。
- DB：授权在隔离 clone 验证 024→025，并回滚重放。
- 未选择附加 `/manage` strict 重验，不得扩展该项。

## 功能需求

### REQ-CLEANUP-01 删除原型

- 输入：精确目录 `/Users/limengyang/2025-blog-public/src/app/workspace/`。
- 处理：确认目录仍只包含已盘点的未跟踪原型后，以系统废纸篓执行可恢复删除。
- 输出：仓库中不再存在 `/workspace` route source。
- 失败：若目录出现新的文件、已跟踪内容或用户新改动，停止并重新确认。

### REQ-CLEANUP-02 主工作区门禁

- 删除后运行完整前端测试、TypeScript、生产构建与 `git diff --check`。
- 不通过 tsconfig exclude、`.gitignore` 或忽略错误绕过。
- 必须在当前主工作区直接通过，不能再以 scoped worktree 替代。

### REQ-CLEANUP-03 路由行为

- `/workspace` 删除后应成为无业务页面的 404，不创建 redirect。
- canonical `/manage/dashboard` 仍保持管理员工作区。
- 在 390×844、1280×800、1440×900 验证 `/workspace` 404 和 `/manage/dashboard` 权限入口。
- 管理员验收必须连接隔离 clone；不得为浏览器验收写入日常库。

### REQ-CLEANUP-04 日常库只读备份

- 仅从 `localhost:5432/blog_db` 执行 custom-format `pg_dump`。
- 记录 dump SHA-256、源 revision、源身份和关键表计数/哈希。
- 日常库只允许 `BEGIN READ ONLY` 查询，不允许 migration、DDL、DML、创建数据库或修改 revision。

### REQ-CLEANUP-05 隔离升级

- 使用临时目录和独立 TCP 端口初始化临时 PostgreSQL cluster。
- 将 dump 恢复为 revision 024 clone。
- 在 clone 执行 `alembic upgrade 025` 和 `alembic check`。
- 验证 025 的索引、约束、NOT NULL、revision、应用 readiness 和权限测试。

### REQ-CLEANUP-06 回滚重放

- 在 clone 执行 `025 → 024 → 025`。
- 每一步记录 revision、关键计数/哈希和 025 管理的索引/约束状态。
- 最终 clone 必须回到 025，数据计数/哈希不得出现未解释漂移。

### REQ-CLEANUP-07 销毁与闭环

- 停止临时 PostgreSQL。
- 使用系统废纸篓清理临时 cluster、socket、dump 和凭据临时文件。
- 只保留不含个人内容的 checksum、计数、schema 和命令结果文档。
- 更新 P0-AUTH/R1 风险台账。

## 非功能需求

- 安全：源库 fail closed，只读事务与 pg_dump。
- 可恢复：删除原型进入系统废纸篓；临时数据库销毁前完成证据记录。
- 隐私：数据库 dump、日志中的个人内容和连接密码不得进入 Git。
- 可审计：命令、revision、端口、checksum、计数、首个失败和清理状态均记录。
- 一致性：最终 PASS 必须同时满足主工作区、隔离 migration、浏览器三条证据链。

## 边界

- 不修改日常库 `localhost:5432`。
- 不部署、不推送、不提交。
- 不改认证架构、AUTH_BYPASS、JWT、Passkey。
- 不执行 `/manage` strict 附加项。
- 不新增 `/workspace` redirect 或替代页面。
- 不执行生产 migration 或 authority switch。

## 验收标准

1. `src/app/workspace/` 不存在，且删除记录可审计。
2. 主工作区完整前端测试、`npx tsc --noEmit`、`npm run build`、`git diff --check` 通过。
3. 三尺寸浏览器确认 `/workspace` 404、canonical 管理入口正常且无横向溢出。
4. 源库 revision 在任务前后均为 024，关键只读 manifest 不变。
5. 隔离 clone 完成 024→025→024→025、`alembic check`、schema/readiness 和数据一致性验证。
6. 临时 clone/dump 已销毁，无敏感文件进入工作树。
