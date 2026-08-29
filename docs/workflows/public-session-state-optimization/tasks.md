# Tasks

## Approval State

Status: `COMPLETE — PSS-01～06 HISTORICAL COMPLETE; FIX-01/G3 PASS; FIX-03～05 COMPLETE; F4 INPUT READY FOR SEPARATE APPROVAL; F4 NOT EXECUTED`

PSS-01～06 的 2026-08-16 列表页、严格会话和权限证据保留为历史通过记录。FIX-01 已补足公开详情和真实挂载共享移动导航的隔离浏览器证据；G3 现为 `PASS`，但 FIX-02～05 与独立 F4 审批仍未完成。

The user explicitly approved the reorganized `frontend-foundation-and-quality/tasks.md` and this Goal's PSS sequence. Execute PSS-01 through PSS-06 exactly one item at a time and immediately synchronize parent/child task, audit, and validation records. G2 is PASS for F3 evidence only; it never authorizes a Markdown production migration.

## PSS-01

- [x] 状态：COMPLETE（2026-08-16）

- 任务名称：冻结会话状态合同与消费者矩阵
- 优先级：P1
- 来源需求：PSS-REQ-01、PSS-REQ-04
- 涉及文件：本 workflow 文档、现有 auth hook 消费者
- 修改内容：确认可选响应字段、错误语义、SWR key、optional/strict 模式及每个消费者归属
- 完成标准：不存在未分类的当前 `useAdminAuth` 消费者；合同不包含私有资料
- 验证方式：源文件矩阵与文档交叉检查
- 风险说明：若消费者职责不明确，标记 BLOCKED，不做批量替换

结论：冻结为当前 HttpOnly `admin_session` / `AdminSession` 机制，不采用 JWT/Bearer。可选端点的最小成功体为 `{ authenticated: boolean, is_admin: boolean }`；无 Cookie、无效、过期、撤销或缺失用户均为 200 anonymous boolean state，数据库/基础设施异常必须继续显式失败。14 个 hook 调用点和 2 个直接严格调用均已分类，无未分类运行时消费者；完整矩阵见 `audit.md`，命令与计数见 `validation.md`。PSS-02 是唯一下一项。

## PSS-02

- [x] 状态：COMPLETE（2026-08-16）

- 任务名称：先建立后端可选会话状态测试
- 优先级：P1
- 来源需求：PSS-REQ-01、PSS-REQ-02
- 涉及文件：`backend/tests/` 下目标 auth 测试
- 修改内容：覆盖匿名 200、有效管理员 200、失效会话降级、真实后端错误不被吞掉，以及 `/api/auth/me` 严格语义不变
- 完成标准：新增测试在实现前能证明缺口，实现后全部通过
- 验证方式：目标 pytest
- 风险说明：不得依赖 `AUTH_BYPASS` 或真实管理员

首个失败已保留在 `assets/pss-02-first-failure.md`：`tests/test_optional_session_state.py` 为 `4 failed, 1 passed, 3 warnings`，失败原因为 endpoint 尚不存在的 404；严格匿名 `/api/auth/me` 已绿。PSS-03 的最小 schema/route 使该合同最终为 `5 passed`，cookie test-harness warning 已清零；最终 artifact 为 `assets/pss-03-final-pass.md`。

## PSS-03

- [x] 状态：COMPLETE（2026-08-16）

- 任务名称：实现最小后端可选会话状态
- 优先级：P1
- 来源需求：PSS-REQ-01、PSS-REQ-02
- 涉及文件：`backend/app/schemas/auth.py`、`backend/app/routers/auth.py`、既有 auth 工具/服务
- 修改内容：增加最小响应与可选会话读取，复用既有 cookie/session 校验
- 完成标准：匿名不产生 401；严格身份、所有写入和管理员依赖无变化
- 验证方式：PSS-02 目标测试与现有权限回归测试
- 风险说明：错误地吞掉数据库异常会伪装故障，必须 fail visibly

`SessionStateOut` 只含 `authenticated` / `is_admin`；`GET /api/auth/session-state` 直接复用 `_resolve_session_user`，没有 catch database/resolver error，也没有改动 `/api/auth/me`、`get_current_admin` 或任何写入依赖。PSS-02 目标 `5 passed`、现有 auth/write 回归 `9 passed`；PSS-04 是唯一下一项。

## PSS-04

- [x] 状态：COMPLETE（2026-08-16）

- 任务名称：拆分前端 optional/strict 会话模式
- 优先级：P1
- 来源需求：PSS-REQ-03
- 涉及文件：`src/lib/api/auth.ts`、`src/hooks/use-admin-auth.ts`、相关 hook 测试
- 修改内容：增加类型化可选状态请求、共享缓存 key、严格模式保留及登录/注销缓存失效
- 完成标准：匿名 public hook 不调用 `/api/auth/me`；`AuthGate` 仍严格校验
- 验证方式：Vitest hook/AuthGate 测试与 TypeScript 检查
- 风险说明：缓存未失效会造成管理员按钮显示滞后

`src/lib/api/auth.test.ts`、`src/hooks/use-admin-auth.test.tsx` 与 `src/app/manage/manage-auth.test.tsx` 的首次联合运行是 `5 failed, 3 passed`；artifact 为 `assets/pss-04-first-failure.md`。最小实现后，API/hook/manage/AuthGate/Batch 7 联合回归为 `14 passed`，`npx tsc --noEmit` PASS；final artifact 为 `assets/pss-04-final-pass.md`。PSS-05 才迁移公开消费者。

## PSS-05

- [x] 状态：COMPLETE（2026-08-16）

- 任务名称：按职责迁移公开消费者
- 优先级：P1
- 来源需求：PSS-REQ-04
- 涉及文件：PSS-01 矩阵确认的公开页面、详情组件与共享导航
- 修改内容：公开消费者切到 optional；保护页保持 strict；不修改业务操作条件
- 完成标准：公开内容始终可读，匿名隐藏管理控件，管理员保留控件
- 验证方式：目标组件测试、`npx tsc --noEmit`
- 风险说明：不得给 `/notes`、`/blog`、`/mistakes` 或公开详情添加 AuthGate

首次 static consumer contract 为 `14 failed`：12 public、1 shared navigation 未显式 optional，`use-blog-index` 仍使用 strict `/api/auth/me`。artifact 为 `assets/pss-05-first-failure.md`。最终 7 files / 30 tests PASS、source TypeScript PASS；final artifact 为 `assets/pss-05-final-pass.md`。PSS-05 只将矩阵内的 display-state probes 改到 optional，未改变其业务 handler、AuthGate 或后端写权限。

## PSS-06

- [x] 状态：COMPLETE（2026-08-16）

- 任务名称：真实浏览器权限与网络验收
- 优先级：P1
- 来源需求：全部
- 涉及文件：`validation.md` 与 `assets/`
- 修改内容：隔离数据库下验证匿名/管理员公开页面、`/manage`、登出、过期会话和请求清单
- 完成标准：匿名公开页无 `/api/auth/me` 401、无管理员专用 API 噪音；管理员与严格页面闭环正常；临时账户和进程已清理
- 验证方式：真实浏览器网络记录、DOM 断言、截图、后端日志
- 风险说明：缺少隔离环境或清理证据时不得标记完成

历史快照：首次 Playwright 为 `1 failed, 2 did not run`：匿名 `/notes`/`/mistakes` 没有 strict `/api/auth/me`，但产生六个 `/api/folders` 管理数据请求。失败 screenshot/trace/error-context 已留在 `assets/playwright-test-results/`，摘要见 `assets/pss-06-first-failure.md`。最小 public folder-load guard、shared optional SWR key 收敛和非个人合成 settings 后，历史隔离矩阵为 `3 passed (7.8s)`。FIX-01 的当前完整矩阵及 G3 结论见下方。

## G3

- [x] 状态：`PASS — FIX-01 COMPLETE`（2026-08-16；F4 仍未授权）

- Gate 名称：公开会话状态权限与浏览器闭环
- 依据：PSS-01～06 的 Cookie-session 合同、failing-first 后端测试、strict auth/write 回归、公开消费者静态合同、Batch 7 与隔离 Playwright 矩阵
- PASS 条件：匿名公开页没有 strict `/api/auth/me` 或管理员 API 噪音；管理员 display state、logout、expired Cookie、strict `/manage` 都有实浏览器证据；`/api/auth/me` 仍为 strict 401；`get_current_admin` 与写入保护没有变化
- 当前结论：`PASS / GO FOR F4 INPUT REPAIR ONLY`。当前隔离 Playwright `5 passed (12.6s)` 同时覆盖匿名 `/blog`、`/notes`、`/mistakes` 列表，公开博客详情、公开笔记详情和 390px 视口下页面真实挂载的共享移动导航；所有匿名场景均断言无 strict `/api/auth/me`、folders/review/admin/AI/attachments 请求、管理入口、page error、意外 5xx、就绪后导航、对话框或下载。历史 browser `3 passed (7.8s)`、后端 `14 passed`、frontend/Batch 7 `31 passed` 与 source TypeScript PASS 仍是历史证据；后续完整回归由 FIX-05 重新计数。
- Gate 范围：仅放行父工作夹 F3 的 E1 只读证据任务；不放行生产 Markdown 迁移、JWT/Bearer、CORS、路由/视觉改造、F4、Git 或部署。

## F4 前质量审查修复（已批准；严格顺序执行）

- [x] FIX-01. **COMPLETE (2026-08-16):** `public-session-state.browser.spec.ts` 以确定性公开博客/笔记详情 fixture 和内存会话完成真实 Chromium 验收。当前完整命令为 `5 passed (12.6s)`；详见 `validation.md` 的 FIX-01 记录。未改生产业务逻辑、认证、路由或生产数据。
- [x] FIX-03-PSS. **COMPLETE (2026-08-16):** README/tasks/audit/validation 已区分既有三场景为历史范围，记录 FIX-01 当前浏览器 `5 passed (12.6s)`、G3 PASS 与 FIX-04 下一任务；F4 仍未授权。
- [x] FIX-04-PSS. **COMPLETE (2026-08-16):** PSS browser test 与本轮触及 workflow 文档通过 Prettier、尾随空白和 `git diff --check`；未修改 harness/config 语义，也未格式化既有或生成的无关文件。
- [x] FIX-05-PSS. **COMPLETE (2026-08-16):** 已记录最终 PSS Playwright 精确命令、5 个场景、warnings、合成边界、端口清理、相关未跟踪文件与残余风险，供父级交付审计引用；F4 未执行。

## Stop Conditions

- 需要放宽 `get_current_admin`、让严格 `/me` 匿名返回管理员资料、启用 `AUTH_BYPASS` 或扩大 CORS。
- 需要把权限重构与编辑器、路由删除、Markdown 或视觉重构合并。
