# Requirements: Phase 1.0 Productization

## 1. Background

核心 MVP 已具备 Subject、Knowledge Point、Question Draft、Question、Mistake Draft、Mistake、Review Item、Review Record 与私有 Attachment 主链路，但用户看到的管理 Dashboard、导航、移动首页、状态文案和部分占位路由未与当前能力同步。生产侧已有历史 Auth/CORS 和 revision 018 备份恢复证据，但 v1.0 需要基于当前 revision 重新建立可复核证据。

## 2. User Roles

### Anonymous visitor

- 阅读公开 Blog、Notes、Mistakes。
- 使用移动端公开导航。
- 不看到管理、写入、复习提交、附件、AI 或系统状态数据。

### Personal administrator / learner

- 通过既有认证进入管理工作区。
- 理解并完成 `Capture → Draft → Question → Mistake → Review` 主流程。
- 查看真实 Dashboard 摘要，不接收 mock 或过期状态。
- 在故障后能够依据备份恢复证据恢复数据库与附件。

## 3. Functional Requirements

### REQ-P10-001 v1.0 baseline

- 输入：当前 Git、数据库、文档、路由和运行页面状态。
- 处理：只读采集 commit、branch、worktree、Alembic revision、核心数据量、已知问题、延期项、截图和 Demo 路径。
- 输出：`docs/releases/v1.0-baseline.md` 与 workflow `assets/` 中的截图。
- 失败处理：不可验证项必须标为 `UNKNOWN` / `NOT VERIFIED`；不得猜测或自动修复。
- 验收：每个事实都能追溯到命令、数据库只读查询、源码、浏览器或既有文档。

### REQ-P10-002 Dashboard 真实状态

- 输入：当前 Question、Mistake、Knowledge Point、Attachment、Review 数据。
- 处理：优先评估复用既有只读 API；只有无法形成一致快照时，才在批准后设计 admin-only summary API。
- 输出：学习概览、今日任务、内容统计、最近活动和安全的系统状态。
- 失败处理：部分请求失败时显示局部 Error/Retry，不把未知值显示为 0。
- 验收：不出现 `Coming Soon`、`No API connected`、`Static shell`；所有数字来自真实数据。

### REQ-P10-003 管理导航闭环

- 输入：当前管理路由与实际学习流程。
- 处理：将 Dashboard、Drafts、Questions、Mistakes、Review、Attachments、Capture、AI、Settings 按产品语义分组。
- 输出：桌面与移动管理导航都能发现完整主流程。
- 失败处理：延期页面必须诚实标注，不与已启用能力混为一谈。
- 验收：`Capture → Draft → Question → Mistake → Review` 每一节点都有清晰入口。

### REQ-P10-004 移动首页导航

- 输入：移动端公开首页与可选管理员会话状态。
- 处理：匿名展示首页、博客、笔记、错题；管理员会话确认后追加管理入口。
- 输出：390px 宽度下存在可见、可点击、可访问的主要导航。
- 失败处理：会话未知或失败时保持公开导航，不产生明显 401/403 噪音。
- 验收：无横向溢出；匿名不会看到管理入口；管理员可进入 `/manage`。

### REQ-P10-005 状态组件统一

- 输入：列表、详情和 Dashboard 的 loading、empty、error、future capability 状态。
- 处理：建立受控共享组件并逐页替换纯文本 `加载中...` 和不一致占位。
- 输出：Loading Skeleton、Empty、Error/Retry、Deferred 四类明确状态。
- 失败处理：不得以 skeleton 隐藏长期失败；错误状态必须可恢复或说明下一步。
- 验收：选定核心页面状态在桌面和移动端均通过浏览器验证。

### REQ-P10-006 产品语言统一

- 输入：管理与公开页面现有中英文、难度和日期格式。
- 处理：面向中文用户统一核心导航、领域名词、难度和日期展示。
- 输出：用户界面不再混用 `Workspace/Subject/Question/medium` 等主要产品词。
- 失败处理：API enum 和内部代码字段保持稳定，只转换展示层。
- 验收：抽查核心页面无未批准的中英文混排；日期按统一规则输出。

### REQ-P10-007 Auth 当前版本回归

- 输入：匿名、有效管理员、禁用管理员、过期/撤销会话。
- 处理：验证既有认证、session、token、middleware 和错误处理。
- 输出：禁用或无效凭据稳定返回 401；权限撤销后管理 API 返回 401/403；公开读取不受影响。
- 失败处理：仅在复现当前缺陷且任务获批后修改代码。
- 验收：LT-ISSUE-002 按当前版本重新验证；历史“已修复”不等于当前自动通过。

### REQ-P10-008 数据与附件恢复能力

- 输入：当前 PostgreSQL revision 和本地附件目录。
- 处理：生成当前版本 backup，并只在隔离 PostgreSQL + 临时附件目录中 restore。
- 输出：backup hash、restore revision、核心 counts、抽样 ID、附件 checksum 和应用连接证据。
- 失败处理：任何 restore 失败都停止，不触碰原数据库；记录 blocker。
- 验收：`backup → isolated restore → app start/import → data check → cleanup` 全链路通过。

### REQ-P10-009 最小 Monitoring

- 输入：已有 health、应用异常和安全上下文。
- 处理：评估 DB、Storage、Auth 检查与安全错误记录的最小实现。
- 输出：可判断服务、数据库和附件存储是否可用；错误日志不包含 secret、token、密码或敏感正文。
- 失败处理：监控自身失败不得阻断核心读写；状态必须明确 unknown。
- 验收：健康项与错误记录有测试和运行证据。

### REQ-P10-010 Learning Analytics Lite

- 状态：`DEFERRED / NOT AUTHORIZED`。
- 原因：属于新增业务能力，可能需要新查询口径、表或 migration。
- 进入条件：1.0A、1.0B 和 RC Gate 全部完成，并重新提交 requirements/design/tasks 获取批准。

### REQ-P10-011 Schema Authority Closure

- 状态：`COMPLETE / PASS`。
- 背景：当前 `alembic current` 与 `heads` 均为 `020 (head)`，但 `alembic check` 仍检测到三个数据库 knowledge-point 索引未出现在 ORM lifecycle metadata 中，以及 ORM 提议新增 `uq_knowledge_points_sibling_name`。
- 决策输入：现有数据库索引、现有 ORM `KnowledgePoint` 合同、Alembic revision 链、现有数据兼容性与查询/写入语义。
- 已选口径（2026-07-19）：**SA-A**。现有数据库 index/constraint contract 是权威：保留 `idx_knowledge_points_parent`、`idx_knowledge_points_subject_parent_sort`、`idx_knowledge_points_subject_sort`，以及 root/child 分流、`lower(name)` 比较的两个 partial unique indexes。当前 ORM 的单一、大小写敏感 `uq_knowledge_points_sibling_name` 不是最终合同。
- 兼容性事实：只读 preflight 记录 root duplicate groups `0`、child duplicate groups `0`、总 rows `3`；此结果不替代未来写入/查询回归测试。
- 约束：不得从 SA-A 决定、`020 (head)`、现有 dirty source、`create_all` 已移除或历史报告推断 metadata/source task 已批准。下一步必须先获批，且只可使 ORM lifecycle metadata 精确描述 SA-A；不得执行 DDL、migration 或改变公开读取 + 管理员写入权限模型、数据语义或 API 合同。
- 验收：PASS — `alembic current`、`heads` 均为 `020 (head)`，`check` 无 upgrade operations；启动仍为只读 readiness；lifecycle metadata 不含治理排除的 guest tables；10 个 taxonomy tests 通过，且只读 count 为 `3`。DDL/migration 是否不需要仍由 SA-P0-03 记录。

### REQ-P10-012 RC Evidence Closure

- 状态：`NOT AUTHORIZED`；前置为 REQ-P10-011 的批准与通过。
- 处理：以同一最终 revision 为基准，重新执行全量 checks、真实 frontend/backend 运行时、匿名与真实管理员权限、Dashboard、Question → Mistake → Review、Attachment、Health 与 admin diagnostics 验收。
- 数据纪律：测试数据只能以精确 ID 标记、清理并复核最终 counts；不得使用 `AUTH_BYPASS`、mock 或生产数据。若 schema 或恢复边界改变，必须生成当前 revision backup 并仅在隔离 PostgreSQL / 临时 storage 中证明 restore。
- 验收：所有命令、hash、revision、counts、截图、warning 与风险写入 workflow evidence；任一失败保留为 FAIL/BLOCKED，不以其他通过项替代。

### REQ-P10-013 Learning Feedback Gate C

- 状态：`DESIGNED / AUTHORIZED FOR MINIMAL NO-SCHEMA IMPLEMENTATION`；RC 已于 2026-07-19 PASS，用户的“批准所有内容直至目标完成”授权适用于本工作流中定义的最小 Gate C task list。DDL/migration、Analytics Lite、BKT、推荐、多用户与 AI 扩展仍不在授权范围。
- 用户问题：管理员打开学习管理首页时，需要知道今天最值得进行的下一步，而不是自行从多个计数和列表推断。
- 输入：既有管理员专用 `DashboardSummary.counts` 的 `due_reviews`、`mistakes`、`questions`；不读取正文、不调用 AI、不触发写操作。
- 输出：一个确定性、中文、可访问的“学习反馈”卡片，输出单一下一步、理由和到对应管理路由的行动链接。优先级固定为到期复习、已有错题整理、已有题目回顾、从题目开始。
- 权限与保留：仅作为 `/manage/dashboard` 的管理员 UI 派生内容；沿用 summary 的 `get_current_admin` 后端边界。无新增 API、表、字段、日志、cookie、持久化或保留期。
- API/UI 合同：复用既有 `GET /api/admin/dashboard/summary`，不得改变其 JSON contract；UI 不得把推断呈现为掌握度、诊断、AI 建议或推荐。
- schema need：`NO`。因此不生成 migration，不重做 backup/restore；最终仍须复核 `current`/`heads`/`check`。
- 验收：四种输入分支有测试；管理员运行时展示对应行动；匿名不新增请求或入口；全量前端/后端/TS/build/browser 回归通过。

### REQ-P10-014 Production Startup Security Hardening

- 状态：`AUTHORIZED`；用户已明确要求直接启动本项修改。
- 输入：`ENV`、`JWT_SECRET_KEY`、`ALLOWED_ORIGINS`、`AUTH_BYPASS`、`AUTH_BYPASS_ALLOW`。
- 处理：仅当 `ENV == "production"` 时，默认 JWT 密钥、空/通配 CORS、以及两个 bypass 开关同时为真必须拒绝启动；拒绝统一抛出 `RuntimeError`，保留安全且不含配置值的错误信息。
- 兼容：非生产环境保留现有双开关开发语义；diagnostics 的 warning 保留为运行时可观察性，不替代生产启动阻断。
- 验收：覆盖三条生产拒绝路径、非生产不触发阻断、以及异常类型；不启动真实生产服务，不读取凭证，不执行 DDL 或数据写入。

### REQ-P10-015 Recommendation Read Semantics and Release Safety

- 状态：`PLANNED / AWAITING TASK APPROVAL`。
- 问题：公开 `GET /api/recommendations/today` 在无当日记录时会调用 AI 并写入 recommendation、AI run 与 call log，违反 GET 只读语义；管理端重新生成流程依赖该隐式写入。公开 history 还需要按个人学习数据边界复核。
- 目标合同：公开 GET 仅返回已存在、可公开展示的当日 recommendation；无记录时返回明确的无内容结果，不调用 AI、不写数据库。任何生成、删除或 history 读取均为管理员操作；生成使用显式的受保护 mutation。
- 兼容：公开首页在 recommendation 缺失时继续显示既有随机分享 fallback；管理端改为显式生成并对无结果显示空状态。不得把 private `raw_context` 暴露给公开读取。
- 生产安全评审：复核 production startup guard、CORS、认证 bypass、公开/管理 API 分层、secret-safe error/logging、依赖审计与可部署性；不读取真实凭证或生产配置值。
- 部署前验证：形成可复跑、fail-closed 的本地 pre-deploy matrix，至少覆盖前端 tests/typecheck/Cloudflare build、后端 full pytest、Alembic current/heads/check、API-contract tests、diff hygiene 和 clean-worktree gate。不得执行 deploy/push。
- schema need：预期 `NO`；若实现证据显示需要表/字段/迁移，立即暂停并请求独立 migration/DDL 批准。
- 验收：公开 GET 不产生 AI/database 写；管理员显式生成有真实鉴权；公开 history 不泄露私人上下文；预部署矩阵对失败明确阻断；测试数据精确清理。

### REQ-P10-016 Deployment Readiness and Authorized Release

- 状态：`PARTIALLY AUTHORIZED`。用户已批准 production registration disabled、Cloudflare Workers Logs 1% sampling with platform short retention、以及前后端 release-gate split and frontend-only release path。该批准不授权 backend target access, backend deployment, migration/DDL, restore, credential read or production data access.
- 发布边界：Cloudflare/OpenNext frontend 与 FastAPI/PostgreSQL/Attachment Storage 是独立运行边界。每一边的 target、变更范围、回滚责任与验证方式必须分别明确；不得将 frontend 发布成功表述为 backend 已发布或反之。
- 工作树：当前工作树是已知 dirty 状态。发布只能从经用户明确批准、可审计且内容已冻结的干净 worktree/commit 进行；不得清理、暂存、提交或丢弃现有用户改动来满足该条件。
- 安全与隐私决策：已决定 production registration disabled；Cloudflare invocation logs 保持启用但 `head_sampling_rate=0.01`，采用平台短期 retention（不将 Workers Logs 作为长期审计库）。提高采样率必须走独立、短期批准并在结束后恢复 1%。决策必须以不泄露配置值的方式可验证。
- 数据库与恢复：若 backend target 连接到生产或准生产，需单独授权。执行前只允许按既有恢复边界核对 revision、备份适用性和只读 Alembic authority checks；任何 migration、DDL、restore 或数据写入仍需独立批准。
- 发布门禁：拆分为 frontend-only 与 backend gate。frontend gate 在批准的 clean scope 内运行 clean-worktree、dependency audit、peer tree、frontend tests/typecheck/Cloudflare build 与 diff hygiene，不需要 target DB。backend gate 使用隔离 test database 运行 pytest，并使用与 test database 不同的已授权 target database 运行 Alembic `current`/`heads`/`check`。full gate 组合两者；任何缺失变量、相同 URL、测试失败、metadata drift、审计高/critical 或 dirty worktree 都必须阻断。
- 发布后验收：仅在发布命令获得单独批准后，按公开读取/管理员写入边界验证 frontend document、JS/CSS、hydration、console、Health、公开 API、管理员 API、附件读取和 diagnostics；不得使用 `AUTH_BYPASS`，不得记录凭证、Cookie、私有正文、数据库 URL 或 storage key。
- 回滚：部署前必须记录可回退的 frontend release identity 与 backend release identity；若任一发布后健康或权限验收失败，停止扩展验证并按获批的对应平台回滚步骤执行。不得用数据库 restore 作为常规 frontend rollback。
- 验收：任务清单必须把 policy decision、clean release scope、target authorization、predeploy、deployment、post-deploy smoke、rollback decision 与最终 readiness verdict 分开；每项完成即更新 tasks 与 evidence。

### REQ-P05-001 Frontend runtime audit

- 输入：当前 frontend process、port、working directory、Node/npm/Next 版本、generated build/cache 和一次可复现 chunk 500。
- 处理：只读确认进程归属、运行命令、构建输出一致性、环境变量存在性和失败层级。
- 输出：可证伪的根因判断与最小恢复路径。
- 失败处理：无法证明进程归属或需要源代码修改时停止，不终止进程、不猜测修复。
- 验收：审计记录足以区分 stale runtime/cache、build mismatch、asset failure 与 source/config defect。

### REQ-P05-002 Clean build recovery

- 输入：P05-01 确认的项目进程与恢复路径。
- 处理：只停止确认属于本项目的前端进程；隔离而非直接删除 `.next`；使用权威 package manager 执行 clean production build，再启动新构建。
- 输出：稳定监听的本地 Next.js runtime。
- 失败处理：如需要修改 source/config/dependency/lockfile，停止并请求扩展批准。
- 验收：production build exit 0；目标 document 与首次加载的 JS/CSS 不再返回 500。

### REQ-P05-003 Browser runtime verification

- 输入：clean runtime、匿名桌面与移动浏览器。
- 处理：检查 `/`、`/blog`、`/notes`、`/mistakes`、`/manage` 的 network、DOM、hydration、console 与截图。
- 输出：逐页面、逐 viewport 的浏览器证据。
- 失败处理：任一页面 blank/loading、hydration failure 或 console error 均判 Gate FAIL。
- 验收：documents/JS/CSS 200，hydration success，console error 0。

### REQ-P05-004 First-party asset loading

- 输入：目标页面实际请求的 favicon/avatar/cursor/route imagery/Next image optimizer resources。
- 处理：验证 first-party status、content type 和可视结果；第三方请求独立分类。
- 输出：asset manifest 与失败清单。
- 失败处理：critical first-party 4xx/5xx 阻塞；第三方失败不得伪装成 first-party PASS。
- 验收：critical first-party assets 返回 200 或有效 304，页面无 broken-image 状态。

### REQ-P05-005 Environment closure

- 输入：恢复前后 Git、database counts、Alembic revision、process/port 和 browser evidence。
- 处理：进行前后对比，关闭临时浏览器会话，记录 quarantined cache 和精确 changed scope。
- 输出：Phase 0.5 PASS/FAIL 与 baseline 更新。
- 失败处理：database counts 或 revision 变化立即 FAIL；不得用恢复成功掩盖数据变化。
- 验收：database unchanged，Alembic `020 (head)` unchanged，证据与风险均已归档。

## 4. Non-functional Requirements

- 安全：后端管理员鉴权保持真实边界；公开页面不得调用管理 API。
- 数据：任何 backup/restore 都不得写入原数据库；附件与 DB 必须成对验证。
- 性能：Dashboard 不得形成无界 N+1；移动首页不得因管理员探测阻塞公开导航。
- 兼容：保留公开 `/blog`、`/notes`、`/mistakes` 与既有 legacy 路由。
- 可访问：图标按钮有 accessible name；抽屉、焦点和键盘路径保持可用。
- 一致性：不显示 mock、假成功、伪健康或把 unknown 显示为 0。
- 可审计：每项完成后立即更新 `tasks.md`，证据写入 `validation.md`。

## 5. Explicit Non-goals

- AI 新功能、Prompt 编辑、AI 自动决策。
- 真实 OCR 扩展、PDF/批量导入。
- BKT、完整 Practice、多用户、推荐系统。
- Note/Mistake 数据迁移或旧路由清理。
- Analytics Lite 实施。
- 未经批准的 schema、migration、部署和生产配置改动。
- 未经范围扩展批准的 source、dependency、lockfile 或持久配置修改。
