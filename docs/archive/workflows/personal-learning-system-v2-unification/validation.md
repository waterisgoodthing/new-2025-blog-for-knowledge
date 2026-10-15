# 文档细化校验

日期：2026-07-20
范围：`personal-learning-system-v2-unification` 工作区中的规划文档。

## 2026-07-30 `docs/refactor-plan` 重新审查

- 已重新读取 `docs/refactor-plan/` 当前文件清单和新增的 `00-CORRECTED-PHASED-PLAN.md`。
- 已以当前源码核对 canonical workspace、AuthGate、博客读写链、静态博客基线、AUTH_BYPASS 生产保护、Alembic readiness 与前后端测试入口。
- 已确认原方案关于“当前没有毛玻璃”“博客尚未进入数据库”“生产 AUTH_BYPASS 尚未阻断”“应用启动仍由 create_all 管理 schema”等前提与当前源码不符或已过期。
- 已将有效目标提取为 R1 管理工作区入口与视觉收敛，并放入现有统一大方案工作区，避免创建平行 master plan。
- 本轮仅新增/更新 workflow 文档；未修改 `docs/refactor-plan/`、`src/app/workspace/` 或任何业务代码、数据库、schema、migration、配置和部署。
- 规划当时 R1 状态为 `APPROVAL REQUIRED`；该历史门禁随后已由用户明确批准并完成执行。

## 2026-07-30 R1 管理工作区入口与视觉收敛

状态：`CLOSED / PASS BY P0-AUTH + CLEANUP`

- 用户已明确批准 R1-01 至 R1-10；十项任务均已按序执行。
- Dashboard 新增四个真实快捷行动：`/write-note`、`/write`、`/manage/capture`、`/manage/review`；未创建 `/workspace/*` 平行路由。
- 完整前端测试 21 个文件、59 项通过；R1 隔离源状态的 TypeScript 与生产构建通过，构建生成 40/40 页面。
- 主工作区 TypeScript 与生产构建被保留的未跟踪 `src/app/workspace/page.tsx` 两个类型错误阻断；R1-02 禁止本轮覆盖该原型。
- 真实浏览器在 390×844、1280×800、1440×900 验证快捷行动、无横向溢出和键盘焦点；管理员 Dashboard 控制台无 error/warning。
- 失效/降权管理员会话访问 `/manage/dashboard` 会回退到仍展示管理界面的旧 `/manage`，已记录为独立权限风险；未扩大为后端越权结论。
- 一次性临时管理员已禁用，浏览器会话已退出，一次性凭据文件、临时前端和隔离 worktree 已清理。
- 详细证据见 [R1 验收记录](./r1-acceptance.md)、[最终审查](./r1-audit.md)、[风险](./r1-risks.md) 与 [后续需求](./r1-next-requirements.md)。
- 后续 P0-AUTH 已关闭失效/降权会话回退缺口；CLEANUP 已删除原型并在主工作区通过 64 项前端测试、TypeScript、40 页生产构建与三尺寸浏览器。原 R1 `PARTIAL` 已解除。

## I4 规划校验

- 已基于 I3 完成证据重新编号递进计划：I4 对应 C-04/C-05，I5 才进入资料/偏好与响应式验收。
- 已记录 Dashboard 聚合状态与侧栏能力标识的现状；没有将现状发现误写为 I4 功能完成。
- 已创建 I4 设计、范围、不做事项、停止条件和可验证任务清单；在用户明确批准前未修改业务源码、API、数据库、迁移、部署或生产数据。

## I4 实施中验证（2026-07-20）

- Dashboard 不可用状态与 Capture 导航事实定向测试共 7 项通过；`npx tsc --noEmit --pretty false`、`git diff --check` 与 Dashboard router Python 编译通过。
- 已核验旧 `/manage` 保留为受保护登录入口，`/manage/dashboard` 为规范工作区入口；桌面/移动导航、焦点隔离和键盘行为相关定向测试累计 9 项通过。
- 已在恢复 revision `021` 的隔离 PostgreSQL 与独立生产构建中验证：匿名管理工作区显示登录入口；管理员正常会话可读取 Dashboard summary，桌面导航显示 Capture 为可用且其他未实现模块仍标“后续”。Dashboard 后端测试在该隔离库通过。
- 已补做真实浏览器尺寸验证：390×844 管理员页打开移动导航抽屉并显示 Capture；1280×800 与 1440×900 管理员 Dashboard 正常渲染摘要和导航。临时前后端与浏览器已停止，用户指定的 `pls_v2_i4_target` 数据库保持运行。C-04、C-05 可标记完成。

## I4 closure-fix 验收（2026-07-22）

状态：`PASS`。用户已批准 CF-01 至 CF-06；本轮仅收口 I4，不进入 I5。

### 契约与失败隔离

- `DashboardSections` 已将 `learning`、`activity`、`storage` 分别建模为 ready/unavailable/empty 或 ready/unknown/empty；服务对三类查询分别捕获 SQLAlchemy 异常、rollback 并保留其他区块结果。
- learning unavailable、activity unavailable、storage unknown 的前端 fixture 与展示断言已覆盖；局部失败仍保留安全行动入口，empty 不再被零值伪装成正常数据。
- SQL 异常 fallback 在 `backend/app/routers/dashboard.py` 显式 `await db.rollback()`；服务级异常分支同步 rollback。

### 生命周期、权限与重试

- `backend/tests/test_dashboard_dependency_lifecycle.py` 的真实 `get_db` 生命周期测试验证：正常 commit、异常 rollback、依赖 close、异常后新查询可恢复，以及 HTTP 路由 SQL 异常返回安全摘要；后端定向测试 `4 passed`。
- Dashboard/导航前端定向测试 `17 passed`，覆盖局部失败、storage unknown、重试、Capture active、移动导航和可访问名称；`npx tsc --noEmit --pretty false` 通过。
- 未带会话访问 Dashboard API 返回 `401 Not authenticated`；带 `admin_session=invalid-i4-session` 返回 `401 Not authenticated`。管理员使用正常密码会话读取独立测试数据库摘要，未启用 `AUTH_BYPASS`。
- 隔离目标 `postgresql+asyncpg://127.0.0.1:55435/pls_v2_i4_target` 当前 revision `021`；`alembic check` 无待生成升级，Python 编译和 `git diff --check` 通过。

### 浏览器与资产

- [匿名 390×844 登录/401 入口](./assets/i4-closure-fix/390x844-anonymous-login.png)
- [管理员 390×844 Dashboard](./assets/i4-closure-fix/390x844-admin-dashboard.png)
- [390×844 移动端导航（Capture 为 active，AI/后续能力保留后续标识）](./assets/i4-closure-fix/390x844-mobile-navigation.png)
- [1280×800 Dashboard](./assets/i4-closure-fix/1280x800-dashboard.png)
- [1440×900 Dashboard](./assets/i4-closure-fix/1440x900-dashboard.png)
- [Tab 键盘导航焦点证据](./assets/i4-closure-fix/keyboard-navigation.png)

### 残余风险与归档

- 本轮只覆盖 SQLAlchemy 异常和当前 Dashboard 查询；外部存储 provider 异常、未来多用户 owner 隔离和 I5 资料/偏好能力仍未实现。
- 未执行生产部署、源库迁移、权威切换、旧系统停写或真实 AI 成功调用；这些均保持未授权。
- I4 closure-fix 证据已冻结并归档，I4 标记 `COMPLETE / PASS`；I5 必须单独审批后再建立实施任务。

## I5 准备记录（2026-07-22）

- 已完成 I5 现状盘点：公开 `site-settings`、legacy 页面设置、当前 `/manage/settings` 占位页、用户模型和认证边界已记录。
- 已确认当前 `users` 模型没有 profile/timezone/preferences 字段；若实施 I5，需先审批独立 profile 存储或模型扩展方案，当前未创建 migration。
- 已建立 [I5 准备计划](./i5-preparation-plan.md)、[现状发现](./i5-preparation-findings.md)、[设计](./i5-preparation-design.md)、[需求](./i5-preparation-requirements.md) 和 [任务清单](./i5-preparation-tasks.md)。
- 本节不是 I5 实施验收：未修改 I5 业务代码、schema、migration、数据库、生产配置或部署；I5 仍等待用户对任务清单的明确批准。

## I5 实施进度（2026-07-22）

- I5-01/I5-02 已完成：公开 `site-settings` 与私有 `admin_profiles` 边界已由 [ADR-I5-01](./i5-profile-settings-adr.md) 冻结；隔离目标已升级到 revision `022`。
- I5-03 已完成：`AdminProfile` model、schema、service、`/api/admin/profile` GET/PUT、默认值、IANA timezone 校验和前端 API client 已实现；匿名请求 401、无效时区 422、管理员 round-trip 200，后端 profile 定向测试 `4 passed`。
- I5-04 已完成：`/manage/settings` 已替换占位页，覆盖默认值、保存成功、loading、network retry 和可访问字段；组件测试 `3 passed`。
- I5-05 已完成：Dashboard 接入管理员欢迎语、UTC/保存时区格式化及 profile unavailable 降级，保持 I4 摘要可用；overview 测试 `9 passed`。
- I5-06 至 I5-10 已在下方完成收口并通过；本节历史进度记录保留，不作为最终状态覆盖。

## I5 验收（2026-07-22）

状态：`COMPLETE / PASS`。用户已批准 I5-01 至 I5-10；本轮仅完成私有资料、首页偏好、公开隔离与响应式验收，不进入 I6、生产部署、源库写入或权威切换。

### 边界、契约与权限

- [ADR-I5-01](./i5-profile-settings-adr.md) 冻结了两条数据流：公开首页继续读取 `GET /api/content/site-settings`，管理员私有资料/偏好使用 `GET/PUT /api/admin/profile`。
- 新增 `admin_profiles` 一对一模型、schema、service、管理员路由和前端 API client；默认资料、IANA timezone、section order/hidden sections 约束均已实现。
- 匿名 profile 请求返回 `401 Not authenticated`；失效 cookie 返回 `401`；非管理员返回 `403`；无效时区和重复区块返回 `422`；管理员 GET/PUT round-trip 返回 `200`。未启用 `AUTH_BYPASS`。
- 公开 `site-settings` payload 不含 `display_name`、`identity_title`、`welcome_message`、`signature`、`timezone` 或 `home_preferences`。

### 页面与失败隔离

- `/manage/settings` 已替换占位页，覆盖 loading、默认/empty、saving、saved、validation error、network retry、未保存提示和可访问名称。
- `/manage/dashboard` 接入管理员欢迎语与保存时区；profile unavailable 时保留 I4 learning/activity/storage 摘要并显示明确降级和重试入口。
- 匿名公开首页网络证据仅包含 `/api/auth/me`（401）、公开 notes/site-settings 等请求；未请求 `/api/admin/profile`，无私有字段泄露或管理员接口错误噪音。

### 测试、迁移与代码质量

- 前端定向套件：6 个文件、22 项通过；覆盖设置保存/重试/loading、Dashboard 欢迎/UTC/降级、I4 状态与导航。
- 后端定向套件：11 项通过；覆盖 profile 路由/服务/权限/公开隔离，以及 Dashboard 生命周期、Attempt 和既有 Dashboard 行为。
- `npx tsc --noEmit --pretty false`、`python3 -m py_compile`、`alembic check` 和 `git diff --check` 均通过。
- 隔离目标 `postgresql+asyncpg://127.0.0.1:55435/pls_v2_i4_target` 完成 `021 → 022 → 021 → 022`；最终 revision `022`，`admin_profiles` 表存在，回滚后重新查询恢复。未写入源库或生产数据库。

### 浏览器与资产

- 公开匿名 390×844：[public anonymous](./assets/i5-preparation/390x844-public-anonymous.png)
- 管理端匿名 390×844：[login entry](./assets/i5-preparation/390x844-manage-anonymous-login.png)
- 设置页 390×844：[saved state](./assets/i5-preparation/390x844-settings-final.png)
- 设置页桌面：[1280×800](./assets/i5-preparation/1280x800-settings.png)、[1440×900](./assets/i5-preparation/1440x900-settings.png)
- Dashboard 桌面：[1280×800](./assets/i5-preparation/1280x800-dashboard-profile.png)、[1440×900](./assets/i5-preparation/1440x900-dashboard-profile-final.png)
- 键盘焦点：[settings keyboard](./assets/i5-preparation/keyboard-settings.png)

### 残余风险与归档决定

- 当前仍是单管理员 profile；未实现多用户/RBAC、私有头像存储、共享空间或公开个人资料。
- 公开品牌仍由既有 `site-settings` 契约提供；本轮未重构 Passkey 写入、GitHub 同步或 legacy 配置。
- I5 不包含 OCR、文件工作区、搜索、AI provider、任务/分析主数据、生产迁移、部署或权威切换。
- I5 证据与代码已冻结归档，标记 `COMPLETE / PASS`；当时记录的“I6 必须新建/审批独立任务组”已由本轮 `i6-capture-draft-chain` workflow 完成。

## I0 冻结审查

- 已创建 `i0-freeze-audit.md`，完成目标设计、历史审计、既有基线和当前代码观察的来源分层。
- 已确认：目标 `/api/public/**` 与当前 `/api/notes` 不是同一契约；当前公开 Note 读取使用 `published + hidden=false`。
- 已确认：独立 Question/Mistake/Review 模型与旧 `Note(type="mistake")` 基线并存，未据此推断数据已迁移或权威已切换。
- 已确认：历史 Migration Gate 文档记录 revision 018；当前启动代码要求 revision 020。因此 Gate 保持 `BLOCKED`，待 I1 重新验证。
- I0 审查初始结论：A-05 已完成；A-01～A-04 曾因需要用户决策或其依赖而保持 `BLOCKED`。
- 用户已于 2026-07-20 批准 I0-DEC-01～I0-DEC-03；A-01～A-04 已依次完成，I0 状态更新为 `PASS / IMPLEMENTATION NOT AUTHORIZED`。

## I1 边界与恢复审计

- B-01 已完成静态权限矩阵：公开 Note 读取、管理员写入、学习管理、复习、附件、AI/治理与管理页面均记录了匿名、管理员和失效会话预期。
- 本轮未进行运行时匿名/API/浏览器测试；静态路由声明不被误报为端到端权限验收。
- B-02 已冻结跨领域所有权与稳定 ID 规则；明确 legacy 单管理员实体与未来逐行 owner 的过渡边界，未修改 schema。
- B-03 已建立 API/页面/旧写入口/导出方向矩阵；将当前 `/api/notes`、legacy review 与目标 `/api/public/**` 的过渡明确分开，GitHub 活动导出链路保持 `UNKNOWN`。
- B-04 初始审计结果为 `BLOCKED`：未发现当前 revision 的数据库 dump、附件副本、哈希或可读性记录；历史恢复说明不能替代当前证据。
- B-04 初始阶段已完成项目目录、常用用户目录、挂载卷、容器/卷、备份调度、crontab 与 Time Machine 的只读自主查找，未发现额外恢复输入。
- B-04 已于 2026-07-20 执行新的数据库与附件备份：custom-format dump 可读，`backend/uploads` 2 个文件与兼容图片 10 个文件均完成 SHA-256 一致性核验。
- B-05 初始状态为 `BLOCKED / NOT RUN`：当时没有可恢复输入，未执行 `pg_restore`、临时库创建、附件写入或应用恢复验证。
- B-05 已于 2026-07-20 通过独立 PostgreSQL 16 临时 cluster 完成隔离恢复；revision、表数、关键实体计数和附件 SHA-256 清单均与源快照一致，临时服务已停止、临时目录已移入废纸篓。
- B-06 初始静态审计与修复计划确认：本地 Alembic 单一 head 为 `020`，启动使用只读 readiness，registry 显式管理 metadata 并排除 guest schema；当时当前数据库漂移状态仍为 `NOT VERIFIED`。
- B-06 已在确认的 localhost 源库复核 `020 (head)`，`alembic check` 未发现新的 upgrade operations。
- I1 已完成：B-01～B-06 均有记录证据；下一增量 I2 仍需单独批准。

## 已完成的只读依据核对

- 已核对既有公开 Note 读取契约：当前路径为 `/api/notes`，匿名可见性由 `published` 与 `hidden=false` 控制。
- 已核对应用启动的当前 schema readiness 检查与历史 migration-gate 文档中的旧 revision/风险记录不应混同。
- 已核对既有目标架构、MVP 范围与本工作区之间存在“目标设计、历史审计、现状实现”三种不同证据层级。

## 本轮文档变更验证

- 统一方案已明确：目标 API 分层不等于当前端点已迁移。
- 统一方案已明确：`DRY_RUN_READY`、隔离 dry-run、影子迁移与权威切换的授权和写入边界不同。
- 文件工作区已补充最小状态机、冲突、恢复、审计和公开发布边界。
- 任务清单已拆分大粒度的恢复、学习闭环、文件工作区和迁移事项。
- 已将任务映射为 I0～I11 单增量执行序列，并为每个增量定义完成证据和停止条件。

## 未执行项

未执行业务代码修改、迁移、dry-run、影子迁移、生产部署或旧系统切换。已执行一次授权的 localhost 数据库 + 附件备份与隔离恢复验证；I1 状态为 `PASS / I2 APPROVAL REQUIRED`。
# I2 暂停验证记录（2026-07-20）

- 已在隔离恢复数据库（Alembic revision `020`）启动临时后端，附件根目录为临时目录；未向现有数据库或附件目录写入。
- 真实浏览器访问独立前端端口的 `/manage`：`GET /api/auth/me` 返回预期匿名 `401 Not authenticated`。
- 页面五秒后仍显示“验证中…”，未渲染密码登录表单；浏览器控制台未见页面错误。
- 只读诊断排除了后端、数据库 readiness 与 CORS：同源页面上下文的直接请求可立即获得匿名 `401`，但新浏览器会话中的管理页没有触发其自身会话请求，指向前端水合/副作用状态流。
- C-01、C-02、C-03 未执行，I2 未通过；本轮不修改源代码。
- 已停止隔离服务并将临时恢复目录移入系统废纸篓；现有 `2025` / `8000` 日常服务未受影响。

## I2 重试验证（2026-07-20）

- 先前管理页无限加载仅在临时开发服务器环境中出现；独立 worktree 的生产构建通过完整 TypeScript 阶段，匿名 401 后正常渲染登录表单，密码管理员登录可进入工作区。
- 浏览器通过独立隔离后端新建科目、知识点与关联题目，并在题目详情确认关系回显。
- 浏览器对既有隔离错题提交复习结果；`POST /api/admin/review/items/{id}/submit` 返回 200，验证 Mistake 至 Review Record 的既有链路。
- 未发现 Attempt 模型/API/UI；`/manage/capture` 显示“当前版本未启用”。C-01、C-02、C-03 因此分别保留为 BLOCKED，未作完整通过声明。
- 已停止独立生产前端、隔离后端、临时 PostgreSQL 与自动化浏览器，并将临时 worktree、数据库、附件根目录和测试管理员移入系统废纸篓；日常 `2025` / `8000` 服务未受影响。

## I3 Attempt、错题转换与采集手工回退验证（2026-07-20）

- 数据库来自 I1 custom-format 备份恢复；隔离 PostgreSQL 上完成 `020 → 021 → 020 → 021`，`021 (head)`，并通过 `alembic check`（无待生成 upgrade）。应用 schema readiness 已同步为 `021`。
- 未登录 `POST /api/admin/attempts` 返回 `401 Not authenticated`；管理员通过正常密码会话访问独立生产构建，未设置 `AUTH_BYPASS`。
- 浏览器新建隔离科目和正式 Question；错误答案 `5` 创建 Attempt 并跳转到 pending Mistake Draft。确认后创建正式 Mistake 和 Review Item；对该项提交 5 分复习结果后，其从今日到期队列消失，形成 Review Record。
- Capture 上传隔离图片后，在 `AI_API_KEY`、`DASHSCOPE_API_KEY`、`DASHSCOPE_IMAGE_API_KEY`、`DEEPSEEK_API_KEY` 都显式为空的后端中返回“无可用 provider”的识别失败；随后切换“手工录入题目”，创建 Question Draft 并进入审核页。未调用真实 AI 成功路径。
- `tests.test_attempt_service` 与 `tests.test_capture_service` 共 14 项通过；失败路径断言没有污染正式对象。根目录 `npx tsc --noEmit --pretty false` 通过，`git diff --check` 通过。
- 代码审查：新路由只做鉴权、DTO 与错误映射；Attempt/Draft 的唯一约束和服务级重入检查共同保证单个 Attempt 最多关联一个 Draft。已知范围限制：本增量只支持单管理员学习事件；简答题使用规范化后的精确文本判定，未引入语义判题或题目版本快照。
- 已完成 I3-10：临时后端、独立生产前端、隔离 PostgreSQL 与自动化浏览器均已停止；`/private/tmp/pls-v2-i3-db-bD75Ot` 与 `/private/tmp/pls-v2-i3-frontend-275QeG` 已移入系统废纸篓。日常 `2025` / `8000` 服务未受影响。上述结论仅针对恢复出的隔离副本，不代表源库或生产已迁移、发布或切换。

## I6 采集到草稿深化链路验证（2026-07-24）

- 既有 `127.0.0.1:55435/pls_v2_i4_target` 只读确认 Alembic `current=heads=022`；未执行迁移、源库写入、部署或推送。
- 后端 I6 组合 51 项通过：私有上传/Capture HTTP、识别与草稿失败矩阵、人工修正、Draft 状态/版本、来源链和幂等转换均有证据。
- 前端 9 个定向测试文件、33 项通过；`npx tsc --noEmit`、`npm run build`（40/40 页面）、Python compileall、`git diff --check` 通过。
- 独立生产构建浏览器以受控管理员 API fixture 验证 390×844、1280×800、1440×900 的失败提示、人工修正后“待确认”、无横向溢出、标准 viewport 和键盘焦点；真实 AI provider 成功质量不在 I6 验收范围。
- I6 状态：`COMPLETE / PASS`；下一项 I7 仍需单独批准。

## I10 迁移 dry-run 验证（2026-07-26）

- 源库通过默认实例 `localhost:5432/blog_db` 只读事务核验，revision `020`，核心计数与哈希写入 I10 manifest。
- `pg_dump --no-owner --no-acl` 恢复至临时隔离 clone，020→024 upgrade、`alembic current=head=024` 和 `alembic check` 通过。
- 8 个核心表共同字段 count/hash 全等；duplicate slug=0；Mistake→Question 与 ReviewItem→Mistake 关系完整；临时 clone 完成 024→020→024 回滚重放并销毁。
- owner/backfill 责任未收敛，`DRY_RUN_READY` 总门槛保持 `BLOCKED`；未执行源库写入、权威切换、旧系统停写或 I11。

## I10 Owner Gate 最终验证（2026-07-31）

- 用户批准 canonical single-owner backfill；immutable manifest 121/121。
- 024 backup 恢复到隔离目标并升级 025；sidecar owner FK backfill、
  missing/extra/hash/owner conflict、七类关系 orphan 均为 0。
- 独立 SQL 与主工具结果一致；sidecar 移除后 Alembic check clean，隔离库销毁。
- 前端 64/64、后端 025 隔离库 307/307、workflow 8/8、TypeScript 和 build PASS。
- 首次测试残留按用户精确授权恢复后，日常库最终 123-row aggregate 与执行前
  完全一致，两个残留 ID 均不存在。
- 当前结论：E-03=`DRY_RUN_READY PASS`；E-05=`PASS`，已完成 123/123
  隔离 shadow/delta、单 owner、零 orphan、幂等 replay、独立 SQL、销毁和
  source 不变验证；E-06=`READY / NOT AUTHORIZED`，未执行。

## I9/I10 current independent recheck (2026-07-26)

- 隔离目标 `024 (head)`、`alembic check` clean；源库只读 identity/revision 为 `blog_db/blog_user:5432`、`020`，计数与 owner 覆盖证据一致。
- 后端 I7/I8/I9 组合 10 passed；前端治理/AI/设置/仪表盘/API 组合 20 tests passed。复核发现并同步了 I9 中陈旧的 AI capability 断言；该同步不改变运行时代码。
- `npx tsc --noEmit`、`npm run build`（40/40）、Python `compileall` 和 `git diff --check` 通过。
- 本次未重新取得浏览器截图：`agent-browser`/Playwright/Puppeteer 不在当前环境；既有 I9 三尺寸浏览器证据继续保留为既有证据，当前复核不扩大浏览器覆盖声明。

## I11/I12 最终收口（2026-08-01）

- E-06/I11：新鲜 DB+附件备份、5/5 hash、dump 可读、隔离 024 restore→025、
  source/target count/PK/hash/owner/关系/附件一致；首次 authority 切换与观察、
  forward delta/幂等、reverse delta、实际回切、最终重切和 Legacy 只读归档均
  PASS。清理临时身份后两库 123/123、零 delta；I11-04 独立 SQL/hash 复核 PASS。
- F-01：真实管理员/非管理员与匿名/失效矩阵在 `AUTH_BYPASS=false` 下为
  200/403/401；公开读取保持 200。390×844、1280×800、1440×900 无溢出，
  键盘可达，浏览器错误为空。Frontend 23 files/64 tests、backend 307 tests、
  tsc、Next build 40/40、compileall、Alembic current/heads/check 和 diff check PASS。
- F-02：npm production audit=0 vulnerabilities、依赖树和 OpenNext build PASS；
  `predeploy:check` 因当前 worktree 非 clean 按设计阻断。技术候选具备未来单独授权
  部署资格，但 current dirty worktree=`DO NOT DEPLOY`。
- F-03：十维最终报告已同步。代码完成与隔离验证 PASS；本机 authority 已切换；
  Legacy 只读保留；实际应用部署=`NOT DEPLOYED`，Git push=`NOT PERFORMED`。
