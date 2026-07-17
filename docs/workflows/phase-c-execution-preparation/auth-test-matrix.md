# Authentication Boundary Test Matrix

日期：2026-07-13  
身份范围：`public`、`authenticated user`、`admin`、`worker`。  
对象范围：`notes`、`questions`、`mistakes`、`review_items`、`attachments`、`ai_runs`。

## 判定口径

- `allow` 是目标态允许，不代表当前实现已完成。
- `deny` 是目标态必须拒绝。
- 当前后端主要是 admin session + `get_current_admin`，当前实现不能被描述为已完成 authenticated-user owner isolation 或 worker API boundary。
- `/api/notes` 是特殊混合路径：public 读已按 `status='published'`、`hidden=false` 过滤；admin 可读全量并执行写操作。独立 `mistakes` 使用 `/api/admin/mistakes`，公开错题列表仍可能读取 `Note(type='mistake')`，不能混淆。

## Matrix

| object | public | authenticated user | admin | worker | 当前实现状态 / 缺失测试 |
|---|---|---|---|---|---|
| `notes` | allow：仅 published + not hidden 的只读列表/详情；deny 写入、复习、AI、管理字段 | target allow：仅 own notes；deny 他人 notes 与 admin command；current：`get_optional_user` 存在，但非 admin 用户没有 owner filter，owner model 也不存在 | allow：管理读写；current：写路由使用 `get_current_admin`，读路由按 admin 状态放宽过滤 | deny 浏览器直达；target 仅通过受信 service/job seam | 已有公开过滤逻辑；缺失非 admin authenticated 的 own/cross-owner 测试、public hidden/draft 回归、worker 误用测试 |
| `questions` | deny 私有题目与所有管理写入 | target allow own read/write；deny other owner；current：没有 owner 字段，router 为 `/api/admin/questions` 全部 admin-only | allow admin management；current：router 级 `get_current_admin` 已存在 | deny browser/public；target worker 只能执行带 owner 的受信任务 | 已有 admin dependency/匿名拒绝路由测试；缺失 authenticated user、跨 owner、worker 任务授权测试 |
| `mistakes` | deny 独立 `mistakes`（当前 visibility private）；公开 `/api/notes?type=mistake` 属于旧 Note seam，只能返回 published/not hidden | target allow own private mistake；deny others；current：独立 mistakes 无 owner，admin-only | allow admin management；current：`/api/admin/mistakes` 及 drafts 有 admin dependency | deny browser/public；target service 代表 owner 执行 | 已有 admin dependency/匿名拒绝；缺失独立 mistakes vs legacy Note 分界、owner isolation、公开误泄露测试 |
| `review_items` | deny review queue、records、submit、stats、plan | target allow own review items/records/submit；deny others；current：review endpoints admin-only且无 owner | allow admin review operations；current：`/api/review` 与 `/api/admin/review/items` 使用 admin seam | deny browser/public；target worker 只能代表已验证 owner 更新 | 已有匿名拒绝和路由依赖测试；缺失 cross-owner target、ReviewItem→Mistake owner 一致性、worker replay 测试 |
| `attachments` | deny private metadata/content/upload/delete | target allow own attachment metadata/content；deny others；current：`/api/admin/attachments` 全部 admin-only，`created_by` 不是 owner | allow admin attachment governance；current：router 级 admin dependency 已存在 | deny browser/public；target worker 仅经 attachment service、带 owner 与 checksum | 已有匿名拒绝和 dependency tests；缺失 owner-scoped download、link target authorization、missing/checksum 与 worker 测试 |
| `ai_runs` | deny list/detail/retry/decision、输入输出和审计字段 | target allow own safe run detail；deny other owner、replay/retry unless explicitly authorized；current：无 owner，admin-only | allow authorized admin query/decision/retry，不得绕过 owner；current：`/api/admin/ai/runs` admin dependency 已存在 | deny browser/public；target worker only for trusted task handler and original owner | 已有 admin dependency/anonymous rejection；缺失 sensitive-field redaction, cross-owner, replay decision, worker identity and `ai_call_logs` correlation tests |

## Identity-specific expected assertions

### public

- `GET /api/notes` 和 `GET /api/notes/{slug}` 只能看到 `status='published' AND hidden=false`。
- public 对独立 private questions/mistakes/review/attachments/ai_runs 返回 401/403 或不暴露对象；不能把 admin 失败渲染为公开页面错误噪音。
- 所有 POST/PUT/PATCH/DELETE、上传、复习提交、AI retry/decision 必须拒绝。

### authenticated user

- 需要正式 owner contract 后，读写仅限自身 owner；跨 owner 的 ID、target、link、replay 均拒绝。
- 当前 session 体系主要是 admin session；不能把“带 session”当作 owner isolation 已完成的证据。

### admin

- 保留后端 `get_current_admin` 作为实际管理边界；前端 AuthGate 不能替代。
- admin 权限仍应受 object owner/policy 约束；admin identity 不自动等于每条业务数据的 owner。

### worker

- 当前没有向浏览器公开的 worker API contract。目标态必须使用受信 task identity、owner/object ID、schema version 与 idempotency key，并通过 service 授权。
- 不得以 `AUTH_BYPASS`、admin session 或任意浏览器 header 模拟 worker。

## Missing test set before Migration Gate

1. public filtering：published/hidden/private/legacy Note mistake 四种样本。
2. authenticated user：own vs other owner 的读写、复习、附件、AI detail/replay。
3. admin：authorized owner scope vs unrelated owner scope；不能仅测 401。
4. worker：无浏览器身份、非法 owner、target mismatch、重复任务幂等。
5. polymorphic target：review/attachment/AI target 不存在、类型错配、跨 owner。
6. sensitive data：`replay_input`、`output_data`、`input_summary`、storage key 与日志脱敏。
7. `AUTH_BYPASS`：关闭、单开、双开矩阵；不得用 bypass 证明正常权限。

结论：当前已有部分 admin/anonymous route tests，但 owner-scoped permission integration evidence 缺失；权限 Gate 未通过。
