# P0-AUTH 任务清单

状态：`P0-AUTH-01～09 COMPLETE / PASS / CLEANUP CLOSED WORKSPACE GATE`

> 用户批准本清单前，不得修改业务代码。批准 P0-AUTH 不授权 AUTH_BYPASS、JWT、Passkey、session schema、数据库、migration、`/workspace` 原型、部署或推送。

## P0-AUTH-01 根因复现与权限基线冻结

- [x] 已完成

- 优先级：P0
- 来源需求：REQ-AUTH-01～06
- 涉及文件：本 workflow 的 `audit.md`、现有 AuthGate/manage/auth 路由与测试（只读）
- 修改内容：记录 `/manage` 的会话成功误判、AuthGate 缓存风险、当前写路由依赖清单和公开页面基线。
- 完成标准：根因、受影响入口、写路由 allowlist 和验证数据库边界均可复现。
- 验证方式：源码追踪、FastAPI 路由注册表枚举、现有测试盘点。
- 风险说明：不得把历史测试或静态依赖声明当作本轮浏览器验收。

## P0-AUTH-02 `/manage` 非管理员行为 RED→GREEN

- [x] 已完成：非管理员初始会话测试取得 RED，最小修复后连同非管理员密码登录回调与管理员正常状态共 3 项通过。

- 优先级：P0
- 来源需求：REQ-AUTH-02
- 涉及文件：`src/app/manage/page.tsx`、新增或就近 manage 页面测试
- 修改内容：先建立 RED，覆盖 `getMe()` 返回 `is_admin=false` 时只显示登录态；再做最小修复，使初始检查和登录回调都严格检查管理员。
- 完成标准：普通/降权用户不渲染管理面板、内容列表或管理操作；管理员行为保持。
- 验证方式：Vitest + Testing Library 行为测试。
- 风险说明：不得重构整个 legacy manage 页面。

## P0-AUTH-03 `AuthGate` 当前管理员核验 RED→GREEN

- [x] 已完成：新受保护入口会重新核验；已建立 focus 返回后的降权 RED，并以 strict hook key、focus/reconnect revalidation 和最小 dedupe 修复，AuthGate/legacy manage/mobile-nav 组合 7 项通过。

- 优先级：P0
- 来源需求：REQ-AUTH-01、REQ-AUTH-03
- 涉及文件：`src/components/auth-gate.tsx`、`src/hooks/use-admin-auth.ts`、对应测试
- 修改内容：先复现旧缓存/降权仍被放行，再最小调整严格 gate 核验；普通公开展示调用方不被批量重构。
- 完成标准：loading 不闪现 children；admin 放行；non-admin/401/403/error 均 fail closed 并回到 `/manage`。
- 验证方式：组件测试模拟管理员、降权、失效和请求失败。
- 风险说明：必须保持 Hook 顺序稳定，避免公共页面产生重复 401 噪音。

## P0-AUTH-04 全部管理写路由依赖契约

- [x] 已完成：动态枚举全部 FastAPI POST/PUT/PATCH/DELETE；除显式认证/公开留言 allowlist 外，所有写路由均含 `get_current_admin` 或更严格的 `get_passkey_admin`。

- 优先级：P0
- 来源需求：REQ-AUTH-04
- 涉及文件：`backend/tests/test_manage_write_permissions.py`，仅在发现真实缺口时涉及对应 router
- 修改内容：动态枚举全部管理型 POST/PUT/PATCH/DELETE，要求 `get_current_admin` 或 `get_passkey_admin`；显式维护最小公开/auth allowlist。
- 完成标准：任何新增未保护管理写路由都会使测试列出 method/path 并失败。
- 验证方式：从 `backend/` 运行定向 pytest。
- 风险说明：不得把未理解的写路由随意加入 allowlist。

## P0-AUTH-05 create/update/delete 运行时权限测试

- [x] 已完成：Note create/update/delete 对匿名、失效 session 均为 401，对非管理员 session 均为 403；与完整写路由契约合计 7 项通过且未进入业务写入。

- 优先级：P0
- 来源需求：REQ-AUTH-05
- 涉及文件：`backend/tests/test_manage_write_permissions.py`
- 修改内容：对 Note create/update/delete 验证匿名、失效 cookie 为 401，非管理员为 403；保留既有管理员成功行为证据。
- 完成标准：鉴权在任何业务写入前拒绝请求，测试不污染数据库。
- 验证方式：TestClient、受控 resolver/dependency 和测试清理。
- 风险说明：不使用 AUTH_BYPASS，不向日常/生产数据库写入。

## P0-AUTH-06 公开读取回归

- [x] 已完成：Batch 7 静态契约确认 `/blog`、`/notes`、`/mistakes` 无页面级 AuthGate；与 AuthGate、legacy manage、mobile-nav 组合 4 文件 11 项通过，真实匿名浏览器回归纳入 P0-AUTH-08。

- 优先级：P0
- 来源需求：REQ-AUTH-06
- 涉及文件：`src/app/batch7-compatibility.test.ts`、必要的公开页面测试
- 修改内容：保持 `/blog`、`/notes`、`/mistakes` 无页面级 AuthGate，并验证匿名页面不被管理鉴权失败影响。
- 完成标准：三条公开路由仍可匿名渲染，不请求或展示管理操作。
- 验证方式：静态兼容性测试、前端行为测试、真实浏览器。
- 风险说明：不得为修复管理入口而封闭公开页面。

## P0-AUTH-07 自动化、TypeScript 与生产构建

- [x] 已完成（scoped PASS / main workspace BLOCKED）：完整前端 23 文件 64 项通过，后端 P0-AUTH+Batch 7 组合 10 项通过，`git diff --check` 通过；隔离 R1+P0-AUTH source 的 TypeScript 与 40/40 生产构建通过。主工作区仍仅被明确排除的未跟踪 `/workspace` 原型两个既有类型错误阻断，因此总状态不得标全仓 PASS。

- 优先级：P0
- 来源需求：全部
- 涉及文件：`validation.md`
- 修改内容：运行前后端定向权限测试、完整前端测试、TypeScript、生产构建和 `git diff --check`。
- 完成标准：P0-AUTH scoped source 全部通过；主工作区结果单独记录。
- 验证方式：
  - `npm test -- --run`
  - `npx tsc --noEmit --pretty false`
  - `npm run build`
  - `PYTHONPATH=. .venv/bin/pytest ...`
  - `git diff --check`
- 风险说明：若主工作区仍被排除范围的 `/workspace` 原型阻断，只能记 `PARTIAL`；不得修改原型、tsconfig 或隐藏失败。

## P0-AUTH-08 真实浏览器 4×3 权限矩阵

- [x] 已完成：匿名/管理员/降权/失效 cookie × 390×844、1280×800、1440×900 全部符合 `/manage` 与 `/manage/dashboard` 预期且无横向溢出；匿名 `/blog`、`/notes`、`/mistakes` 在三尺寸均保持公开。12 张角色矩阵截图已归档。

- 优先级：P0
- 来源需求：REQ-AUTH-01～03、REQ-AUTH-06
- 涉及文件：`assets/`、`validation.md`
- 修改内容：匿名/管理员/降权/失效 cookie × 三种尺寸，逐格验证 `/manage` 和 `/manage/dashboard`；同时抽查公开三页。
- 完成标准：12 个角色×尺寸单元全部符合设计矩阵，无管理内容闪现、无横向溢出、无新增 console error。
- 验证方式：真实浏览器 DOM snapshot、URL、可访问名称、console 和截图。
- 风险说明：本地临时管理员必须在验收后禁用，一次性凭据和临时环境必须清理。

## P0-AUTH-09 最终安全与代码质量审查

- [x] 已完成：diff、权限、Hook 稳定性、公开边界、死链、测试、浏览器、临时资源和残余风险均已复核；权限功能 PASS，范围外主工作区构建和默认数据库 revision 阻断使总状态保持 PARTIAL。

- 优先级：P0
- 来源需求：全部
- 涉及文件：`diff-report.md`、`audit.md`、`validation.md`
- 修改内容：复核 diff、权限、Hook 稳定性、公开边界、死链、测试质量、残余风险和清理状态。
- 完成标准：每项有 `PASS/PARTIAL/FAIL` 与证据；失败项不被标完成。
- 验证方式：源码 diff、命令结果、浏览器证据和临时资源清单。
- 风险说明：不自动进入认证重构、原型修复、部署或推送。

## 执行顺序与硬门禁

```text
P0-AUTH-01
  → P0-AUTH-02
  → P0-AUTH-03
  → P0-AUTH-04
  → P0-AUTH-05
  → P0-AUTH-06
  → P0-AUTH-07
  → P0-AUTH-08
  → P0-AUTH-09
```

- 每项完成后立即勾选，不得批量回填。
- 每个行为按单一 RED→GREEN 垂直切片执行。
- 任一权限回归、公开读取回归或后端缺保护：立即停止。
- P0-AUTH-07 或 P0-AUTH-08 未全部满足时，最终不得标 `PASS`。

## 后续 CLEANUP 收口

- 2026-07-30：用户另行批准 CLEANUP-01 至 CLEANUP-10。
- 未跟踪 `/workspace` 原型已按方案 A 删除；主工作区 23 files / 64 tests、
  TypeScript、40 页生产构建和三尺寸浏览器均通过。
- revision 025 已在临时 clone 完成 `024→025→024→025`，日常库保持 024。
- P0-AUTH 原 workspace gate 从 `PARTIAL` 更新为 `PASS`。
