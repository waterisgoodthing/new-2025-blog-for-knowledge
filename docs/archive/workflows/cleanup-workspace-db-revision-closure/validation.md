# CLEANUP 验证记录

状态：`COMPLETE / PASS / NOT DEPLOYED`

## CLEANUP-01

结果：`PASS`

- `realpath` 与批准的绝对路径完全一致。
- `git status --short -- src/app/workspace` 仅返回未跟踪目录。
- `rg --files` 仅返回 `src/app/workspace/page.tsx`。
- SHA-256 已记录到 `audit.md`。
- 没有删除、迁移或数据库写入。

## CLEANUP-02

结果：`PASS`

- 删除前再次校验绝对路径、目录存在且仅含目标 `page.tsx`。
- `/usr/bin/trash` 成功返回。
- 删除后路径不存在。
- Git 未报告该路径下的 tracked 删除。
- `src/app` 路由清单不再包含 `/workspace`。

## CLEANUP-03

结果：`PASS`

| 门禁 | 结果 | 证据 |
| --- | --- | --- |
| 前端测试 | PASS | 23 个测试文件、64 个测试通过 |
| TypeScript | PASS | `npx next typegen` 清除 stale 路由类型后，`npx tsc --noEmit --pretty false` 退出码 0 |
| 生产构建 | PASS | Next.js 16.2.12 编译、类型检查及 40 个页面生成通过 |
| 路由表 | PASS | 构建输出不存在 `/workspace` |
| diff check | PASS | `git diff --check` 退出码 0 |

非阻塞观察：

- AI governance 相关测试仍输出既存 React `act(...)` 警告。
- Node 输出既存 `module.register()` deprecation warning。

## CLEANUP-04A

结果：`PASS（匿名阶段先通过，管理员阶段见 CLEANUP-04B）`

| 视口 | `/workspace` | 匿名 `/manage/dashboard` | 横向溢出 | 截图 |
| --- | --- | --- | --- | --- |
| 390×844 | 404、无旧原型文案 | 跳转 `/manage`、登录表单可见 | 无 | `assets/workspace-404-390x844.png`、`assets/manage-anonymous-390x844.png` |
| 1280×800 | 404、无旧原型文案 | 跳转 `/manage`、登录表单可见 | 无 | `assets/workspace-404-1280x800.png`、`assets/manage-anonymous-1280x800.png` |
| 1440×900 | 404、无旧原型文案 | 跳转 `/manage`、登录表单可见 | 无 | `assets/workspace-404-1440x900.png`、`assets/manage-anonymous-1440x900.png` |

- 真实浏览器页面 error 列表为空。
- console 的 dev HMR/React 信息不属于运行时错误；头像 LCP 建议作为低风险观察记录。
- 未向日常库创建管理员或执行其他写入。

## CLEANUP-04B

结果：`PASS`

| 视口 | clone 管理员 `/manage/dashboard` | 横向溢出 | 截图 |
| --- | --- | --- | --- |
| 390×844 | 保持目标 URL，管理员问候/学习管理首页/系统状态可见 | 无 | `assets/manage-admin-390x844.png` |
| 1280×800 | 保持目标 URL，管理员问候/学习管理首页/系统状态可见 | 无 | `assets/manage-admin-1280x800.png` |
| 1440×900 | 保持目标 URL，管理员问候/学习管理首页/系统状态可见 | 无 | `assets/manage-admin-1440x900.png` |

- 临时管理员只创建于 clone，未使用 AUTH_BYPASS。
- 验收后账号已禁用；已登录 session 重验后回到 `/manage` 登录态。
- 一次性凭据文件、浏览器 session、临时前后端服务均已清理。
- CLEANUP-04 总结：`PASS`。

## CLEANUP-05

结果：`PASS`

- 源库身份：`blog_db` / `blog_user` / `::1:5432`。
- manifest transaction 明确返回 `transaction_read_only=on`。
- revision=`024`；8 张相关表计数及稳定哈希已写入 `audit.md`。
- 025 的 12 个 NOT NULL 目标列 NULL 计数均为 0。
- custom-format dump 非空，`file` 可识别，`pg_restore --list` 返回 322 行。
- dump SHA-256：`270de9062187235af945df02fed51456b671b0f8f4b2dccfdf367bc21a635aac`。
- dump 后只读复核源 revision 仍为 `024`。

## CLEANUP-06

结果：`PASS`

- `initdb` 成功创建独立 UTF-8 / C locale cluster。
- clone 仅监听 `127.0.0.1:55432`，`pg_isready` 通过。
- `pg_restore --exit-on-error` 退出码 0。
- `blog_db_clone` revision=`024`。
- 8 张相关表的行数与稳定哈希与源 manifest 完全一致。
- 未对 5432 执行 create/restore/migration。

## CLEANUP-07

结果：`PASS`

| 验证 | 结果 |
| --- | --- |
| Alembic `024→025` | PASS，revision=`025` |
| 4 个目标索引 | PASS，两个要求的索引为 UNIQUE |
| 2 个旧 unique constraint | PASS，均已移除 |
| 12 个 NOT NULL | PASS，`is_nullable=NO` 且 NULL=0 |
| 数据 manifest | PASS，8 表行数/稳定哈希无漂移 |
| `alembic check` | PASS，no new operations |
| readiness | PASS |
| 后端权限组合 | PASS，10 tests |
| auth bypass | 明确为 false / false |

## CLEANUP-08

结果：`PASS`

| 阶段 | revision | schema | canonical 数据 |
| --- | --- | --- | --- |
| 起点 | 025 | 025 索引 / NOT NULL 形态 | 与源一致 |
| downgrade | 024 | legacy constraints/index 恢复，12 列 nullable | 与源一致 |
| re-upgrade | 025 | 4 新索引、0 legacy constraint、12 NOT NULL | 与源一致 |

- clone 浏览器验收产生 `+1 user / +1 admin_session`；测试账号已 disabled。
- 对账显式排除该命名测试账号及其 session，排除后的 8 表行数和稳定哈希逐项等于源 manifest。
- 最终 `alembic check` 与 readiness 均再次 PASS。

## CLEANUP-09

结果：`PASS`

- 55432 cluster 已正常停止，端口与 readiness 均确认关闭。
- 临时根已整体移入废纸篓。
- 3000/8001 临时服务已关闭。
- 工作区不存在 dump、PostgreSQL data marker 或一次性凭据。
- 日常库保持 `5432 / revision 024 / transaction_read_only=on`。
- 日常库 8 表最终 manifest 与备份前完全一致。

## CLEANUP-10

结果：`PASS`

- 需求、设计、任务、执行、验收、剩余风险和下一轮需求闭环完整。
- 最终 TypeScript 与 diff check 通过。
- 9 张三尺寸浏览器截图存在且像素尺寸正确。
- P0-AUTH/R1 的 workspace gate 状态与风险台账已同步。
- 2025 日常前端恢复为健康 dev 编译，页面资源全部 200；8000 后端匿名鉴权返回预期 401。
- 两项低风险观察已路由到下一轮需求，不阻断本轮 PASS。
- 未部署、提交、推送或迁移日常库。

## 已完成的规划期只读验证

- 确认删除目标当前为单个未跟踪文件。
- 确认 migration 025 的 down revision 为 024。
- 确认日常库当前 revision 024，025 触及的 NOT NULL 列均无 NULL。
- 确认本机具备独立 backup/restore cluster 工具链。

## 最终边界

- 已执行批准范围内的 dump、clone restore、upgrade/downgrade/re-upgrade。
- 日常库未执行 migration、DDL、DML 或管理员创建。
- 未部署、提交或推送。
- 未修改认证架构、AUTH_BYPASS、JWT、Passkey 或 `/manage` 业务实现。
