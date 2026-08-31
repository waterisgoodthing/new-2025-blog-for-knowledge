# CLEANUP 任务清单

状态：`CLEANUP-01～10 COMPLETE / PASS / NOT DEPLOYED`

> 用户已于 2026-07-30 明确批准执行 CLEANUP-01 至 CLEANUP-10。批准不包含日常库 migration、部署、推送、认证重构、`/manage` strict 附加项或 `/workspace` redirect。

## CLEANUP-01 删除目标最终确认

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-01
- 涉及文件：`src/app/workspace/`、`audit.md`
- 修改内容：重新确认目录只含未跟踪 `page.tsx`，记录 SHA-256、Git 状态和 canonical `/manage/dashboard` 依据。
- 完成标准：删除目标精确且无新增/已跟踪用户内容。
- 验证方式：`git status`、`rg --files`、`shasum -a 256`。
- 风险说明：事实不符立即停止，不删除。

## CLEANUP-02 可恢复删除 `/workspace` 原型

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-01
- 涉及文件：`src/app/workspace/`
- 修改内容：使用系统废纸篓删除精确目录；不创建 redirect。
- 完成标准：目录不存在，Git 状态没有意外删除。
- 验证方式：路径检查、`git status --short`、路由文件清单。
- 风险说明：这是已授权的破坏性操作；完成后报告可从废纸篓恢复。

## CLEANUP-03 主工作区自动化与构建

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-02
- 涉及文件：当前主工作区
- 修改内容：运行完整前端测试、TypeScript、生产构建与 diff check。
- 完成标准：全部在主工作区直接通过。
- 验证方式：`npm test -- --run`、`npx tsc --noEmit --pretty false`、`npm run build`、`git diff --check`。
- 风险说明：不得用 scoped worktree 或忽略配置替代。

## CLEANUP-04 三尺寸路由浏览器验收

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-03
- 涉及文件：`assets/`、`validation.md`
- 修改内容：先三尺寸验证 `/workspace` 404 与匿名 `/manage/dashboard`；管理员三尺寸验证在 CLEANUP-07 的 025 clone 上完成后再关闭本项。
- 完成标准：404/canonical/权限/无溢出均符合设计。
- 验证方式：真实浏览器 DOM、URL、console 和截图。
- 风险说明：临时管理员只能写入 clone，必须清理；不使用 AUTH_BYPASS。

## CLEANUP-05 源库只读 manifest 与 dump

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-04
- 涉及文件：临时目录、`audit.md`
- 修改内容：BEGIN READ ONLY manifest；custom-format pg_dump；SHA-256 与 dump list。
- 完成标准：源库 revision 024，dump 可读，源库未写入。
- 验证方式：SQL manifest、`pg_dump`、`shasum`、`pg_restore --list`。
- 风险说明：任何源库写入迹象立即停止。

## CLEANUP-06 临时 cluster 恢复 revision 024

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-05
- 涉及文件：`mktemp` 临时 cluster
- 修改内容：initdb、独立端口启动、createdb、pg_restore。
- 完成标准：clone current=024，关键计数/哈希等于源 manifest。
- 验证方式：`alembic current`、SQL manifest。
- 风险说明：端口不得为 5432，DATABASE_URL 必须显式指向 clone。

## CLEANUP-07 clone 024→025 升级与检查

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-05
- 涉及文件：隔离 clone、migration 025
- 修改内容：upgrade 025，验证索引/约束/NOT NULL，运行 alembic check、readiness 和后端权限组合。
- 完成标准：所有 schema、revision、应用检查通过。
- 验证方式：Alembic、PostgreSQL catalog、pytest。
- 风险说明：失败只记录，不修日常库或擅改 migration。

## CLEANUP-08 clone 025→024→025 回滚重放

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-06
- 涉及文件：隔离 clone
- 修改内容：downgrade 024、校验旧形态、re-upgrade 025、最终对账。
- 完成标准：最终 025，计数/哈希无未解释漂移，alembic check clean。
- 验证方式：revision/schema/data manifests。
- 风险说明：任一步失败则 CLEANUP 不得 PASS。

## CLEANUP-09 临时资源销毁与源库复核

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：REQ-CLEANUP-07
- 涉及文件：临时 cluster/dump
- 修改内容：停止服务、trash 临时根、复核端口关闭和源库仍为 024。
- 完成标准：临时资源不存在，工作树无敏感导出，源库 manifest 未变。
- 验证方式：进程/端口/路径/Git/只读 SQL 检查。
- 风险说明：删除仅限解析后的临时根目录。

## CLEANUP-10 最终审查与风险收口

- [x] 已完成（2026-07-30）
- 优先级：P0
- 来源需求：全部
- 涉及文件：`validation.md`、`audit.md`、`diff-report.md`、P0-AUTH/R1 风险台账
- 修改内容：汇总删除、构建、浏览器、clone、回滚、清理和边界证据。
- 完成标准：所有门禁通过才解除 PARTIAL 并标 PASS。
- 验证方式：命令输出、截图、checksum、revision 和 Git 状态。
- 风险说明：不自动部署、推送或迁移日常库。

## 顺序

```text
CLEANUP-01 → 02 → 03 → 04A（匿名）→ 05 → 06 → 07
→ 04B（clone 管理员）→ 08 → 09 → 10
```

每项完成后立即更新本清单、`validation.md` 和风险台账。
