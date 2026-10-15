# CLEANUP 审计基线

状态：`COMPLETE / PASS / NOT DEPLOYED`

## 删除目标

- `src/app/workspace/` 当前仅含未跟踪 `page.tsx`。
- 原型引用不存在的 `ReviewStats.total_notes`，且使用未配置的 Dayjs `fromNow`。
- 原型内部链接还指向不存在的 `/workspace/review`、`/workspace/create`、`/workspace/capture`。
- canonical 工作区为 `/manage/dashboard`。

## CLEANUP-01 删除目标确认

- 绝对路径：`/Users/limengyang/2025-blog-public/src/app/workspace`
- Git 状态：仅 `?? src/app/workspace/`，目录中没有 tracked 文件。
- 文件清单：仅 `src/app/workspace/page.tsx`。
- SHA-256：
  `588df0c66955733e40cb523c3fc27ff77940ddf5ad94222219ba20aebe11c054`
- canonical 依据：现有管理入口与 R1 设计均指向 `/manage/dashboard`；R1 明确不新增 `/workspace` redirect。
- 结论：目标与批准范围一致，允许进入 CLEANUP-02。

## CLEANUP-02 可恢复删除

- 使用 `/usr/bin/trash` 移除精确绝对路径。
- 删除后 `src/app/workspace` 不存在。
- `git ls-files --deleted -- src/app/workspace` 无输出，未产生 tracked 删除。
- `src/app` 中不再存在 `/workspace` 路由文件。
- 未创建 redirect，未修改 `next.config.ts`。
- 恢复方式：可从 macOS 废纸篓恢复删除前记录的单文件原型。

## CLEANUP-03 主工作区门禁

- `npm test -- --run`：23 files / 64 tests passed。
- 首次 `npx tsc --noEmit --pretty false` 命中删除路由后的 stale
  `.next/types/validator.ts` 引用；运行 `npx next typegen` 刷新生成类型后，
  同一 `tsc` 命令通过。
- `npm run build`：PASS，40 个页面生成完成；构建路由表不含 `/workspace`。
- `git diff --check`：PASS。
- `.next` 无 tracked 或 untracked 工作树变化。

## 执行期计划校正：浏览器管理员身份

- 发现原设计的“源库只读”与“在项目 CLI 创建临时管理员”存在写入冲突。
- 采用更严格边界：日常库不创建/禁用管理员。
- 匿名与 404 验收先执行；管理员验收在 025 临时 clone 上执行。
- 本调整不改变页面、认证架构、migration 或源库，仅改变安全的验证环境。

## CLEANUP-04A 三尺寸匿名浏览器验收

- 验证 origin：`http://localhost:3000`（项目既有 CORS allowlist）。
- 390×844、1280×800、1440×900 的 `/workspace`：
  - DOM 显示 `404 / This page could not be found.`；
  - 不含旧“学习工作区”文案；
  - `scrollWidth === innerWidth`。
- 同三尺寸匿名打开 `/manage/dashboard`：
  - 最终 URL 为 `/manage`；
  - DOM 含用户名、密码与密码登录入口；
  - `scrollWidth === innerWidth`。
- 页面 error 列表为空。console 仅有 dev HMR/React 信息及既有头像 LCP 建议。
- 管理员矩阵留待 025 clone，CLEANUP-04 暂不关闭。

## CLEANUP-04B clone 管理员浏览器验收

- 数据库：`blog_db_clone` revision 025，端口 55432。
- 后端：临时 `127.0.0.1:8001`，`AUTH_BYPASS=false`。
- 前端：临时 `http://localhost:3000`，API 指向 8001。
- 临时管理员通过项目 CLI 仅创建于 clone；一次性凭据只存在于权限
  `0600` 的临时文件，未输出到仓库或对话。
- 390×844、1280×800、1440×900：
  - URL 保持 `/manage/dashboard`；
  - DOM 包含管理员问候、`学习管理首页` 与 `系统状态`；
  - `scrollWidth === innerWidth`；
  - 页面 error 列表为空。
- 验收后项目 CLI 已将 clone 临时账号设为 `is_admin=false`、密码 disabled。
- 原登录 session 再访问 Dashboard 后回到 `/manage` 登录表单。
- 凭据文件已移入废纸篓；浏览器与临时 8001/3000 服务均已关闭。

## 日常数据库只读快照

```text
database=blog_db
user=blog_user
host=::1/128
port=5432
revision=024
```

025 涉及的 NOT NULL 列升级前 NULL 计数均为 0：

```text
categories.sort_order
music_items.sort_order
music_items.is_active
music_items.created_at
notes.hidden
notes.created_at
notes.updated_at
notes.ef
notes.interval
notes.repetitions
recommendations.created_at
users.created_at
```

本快照通过 `BEGIN READ ONLY` 获取；没有执行 DDL、DML、migration 或 dump。

## CLEANUP-05 源库只读 manifest 与 dump

- 源 transaction：`transaction_read_only=on`
- 源 revision：`024`
- PostgreSQL / pg_dump：`16.14`
- 临时根：`/private/tmp/2025-blog-cleanup.AVNuO9`，权限 `0700`
- dump：`source-024.dump`，custom format v1.15
- dump SHA-256：
  `270de9062187235af945df02fed51456b671b0f8f4b2dccfdf367bc21a635aac`
- `pg_restore --list`：322 行，可正常读取

025 触及表的源 manifest：

| 表 | 行数 | 稳定 MD5 |
| --- | ---: | --- |
| admin_sessions | 43 | `4171e9e4f4b005dc43aea353926bebde` |
| categories | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| daily_songs | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| music_candidates | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| music_items | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| notes | 13 | `70c5b00dd7eebb0a603eb8a9401abaa1` |
| recommendations | 29 | `33b66cbd94428e0f09c3b3ffb3e64569` |
| users | 10 | `c4e2554b8695a4c4dae99ebd30dd0acf` |

- 12 个 025 NOT NULL 目标列的 NULL 计数全部为 0。
- dump 后再次以只读 transaction 查询，源 revision 仍为 `024`。

## CLEANUP-06 临时 clone 恢复

- data directory：`/private/tmp/2025-blog-cleanup.AVNuO9/data`
- socket directory：`/private/tmp/2025-blog-cleanup.AVNuO9/socket`
- TCP：`127.0.0.1:55432`（明确非 5432）
- clone database：`blog_db_clone`
- restore：`pg_restore --exit-on-error --no-owner --no-acl`，退出码 0
- clone revision：`024`
- clone transaction manifest：`transaction_read_only=on`
- 8 张相关表的行数与稳定 MD5 全部逐项等于 CLEANUP-05 源 manifest。

## CLEANUP-07 clone 024→025

- Alembic：`Running upgrade 024 -> 025`，最终 revision=`025`。
- 目标索引：
  - `ix_admin_sessions_token_hash`：UNIQUE
  - `ix_admin_sessions_user_id`
  - `ix_daily_songs_date`：UNIQUE
  - `ix_music_candidates_netease_id`
- 旧 `admin_sessions_token_hash_key`、`daily_songs_date_key` constraint 均不存在。
- 12 个目标列 `is_nullable=NO` 且 NULL 计数均为 0。
- 8 张相关表的行数与稳定 MD5 均与 024 源 manifest 相同。
- `alembic check`：`No new upgrade operations detected.`
- `validate_database_readiness()`：PASS。
- `AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false` 下：
  `test_manage_write_permissions.py` + `test_batch7_compatibility.py` 共 10 项通过。

## CLEANUP-08 025→024→025 回滚重放

浏览器测试工件：

- clone 原始 `users=11`、`admin_sessions=44`。
- 排除明确的 `cleanup-admin-20260730` 及其 session 后，
  canonical `users=10`、`admin_sessions=43`，哈希与源库一致。
- 该差异来自授权的 clone 浏览器登录，不计为 migration 漂移。

降级到 024：

- revision=`024`。
- `admin_sessions_token_hash_key`、`daily_songs_date_key` unique constraint 恢复。
- `idx_admin_sessions_user_id` 恢复。
- 4 个 025 新索引不存在。
- 12 个目标列全部恢复 `is_nullable=YES`。
- canonical 8 表计数/哈希与源 manifest 一致。

重新升级到 025：

- revision=`025`。
- 4 个目标索引存在且两个要求项为 UNIQUE。
- legacy constraint 数量为 0。
- 12 个目标列 `NOT NULL=12`、unexpected nullable=0。
- canonical 8 表计数/哈希仍与源 manifest 一致。
- `alembic check` 无新 operations；readiness PASS。

## CLEANUP-09 临时资源销毁与源库复核

- `pg_ctl status` 在删除前确认目标 PID/目录/端口均属于临时 cluster。
- `pg_ctl stop -m fast` 成功，55432 不再监听且 `pg_isready` 不可连接。
- 精确临时根 `/private/tmp/2025-blog-cleanup.AVNuO9` 已整体移入废纸篓。
- 本轮临时 3000/8001 服务均不再监听。
- 工作区未发现 `.dump`、`PG_VERSION` 或 `temp-admin.txt`。
- 日常库最终 `BEGIN READ ONLY` 复核：
  - database=`blog_db`
  - port=`5432`
  - transaction_read_only=`on`
  - revision=`024`
  - 8 张相关表的行数和稳定 MD5 与 CLEANUP-05 源 manifest 完全相同。

## CLEANUP-10 最终审查

- CLEANUP-01 至 CLEANUP-10 全部有执行与验证记录。
- `npx tsc --noEmit --pretty false` 最终复核 PASS。
- `git diff --check` 最终复核 PASS。
- 9 张截图尺寸与命名完整。
- `/workspace` 路径不存在；未建立 redirect。
- P0-AUTH workspace gate 与 R1 历史 PARTIAL 已更新为 PASS。
- 两项低风险 warning 已进入 `next-requirements.md`，没有删除或隐藏。
- 生产构建曾使长期运行的 2025 dev server 出现 stale chunk；旧进程停止后由
  既有守护器自动拉起 Next 16.2.12，新浏览器确认登录页正常、所有 Next
  chunk 200、页面 error 为空。
- 日常 2025 前端返回 200；日常 8000 后端匿名 `/api/auth/me` 返回预期 401。
- 未部署、未提交、未推送、未迁移日常库。

最终结论：`PASS / NOT DEPLOYED`。
