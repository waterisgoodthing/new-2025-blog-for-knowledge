# P0-AUTH 需求文档

## 背景

R1 浏览器验收发现：临时管理员被降权后，访问 `/manage/dashboard` 会回退到 `/manage`，而旧 `/manage` 仍显示管理界面。前端把有效普通会话误当成管理权限，页面边界与后端管理员边界不一致。

## 角色

- 匿名访客：没有有效 session cookie。
- 管理员：`/api/auth/me` 返回 `is_admin: true`。
- 降权用户：session 仍有效，但当前用户 `is_admin: false`。
- 失效会话：cookie 不存在于会话表、被撤销或已过期。

## 功能需求

### REQ-AUTH-01 严格管理员判定

- 输入：受保护页面加载及当前 session。
- 处理：以当前 `/api/auth/me` 响应中的 `is_admin === true` 作为页面放行条件，不把旧缓存或“请求成功”当作管理员证明。
- 输出：管理员看到子页面；其他角色进入明确登录态。
- 失败：网络/401/403/无效 payload 均 fail closed，不渲染管理子页面。

### REQ-AUTH-02 `/manage` 登录入口收口

- 输入：四类角色访问 `/manage`。
- 处理：只有真实管理员可以看到旧管理面板；匿名、降权和失效会话都显示登录页。
- 输出：登录页与管理员面板状态互斥。
- 失败：鉴权请求失败时显示登录态，不泄露内容列表、编辑或删除操作。

### REQ-AUTH-03 `/manage/dashboard` 收口

- 输入：四类角色访问 `/manage/dashboard`。
- 处理：真实管理员进入工作区；其他角色回到 `/manage` 登录态。
- 输出：不得闪现 Dashboard 或旧管理面板。
- 失败：鉴权不确定时保留“验证中”，结束后 fail closed。

### REQ-AUTH-04 后端写权限契约

- 输入：当前 FastAPI 注册的管理型 POST/PUT/PATCH/DELETE 路由。
- 处理：逐路由验证依赖树含 `get_current_admin` 或已有、更严格的 `get_passkey_admin`。
- 输出：生成完整、可复现的受保护路由集合。
- 失败：发现任何非 allowlist 管理写路由缺少管理员依赖时测试失败并列出 method/path。

明确 allowlist：

- 登录、登出、注册等认证入口；
- 公开留言创建；
- 其他公开写入只有在当前源码和权限规则明确证明为公开契约后才能加入。

### REQ-AUTH-05 运行时 create/update/delete 权限

- 对代表核心内容写入的 create/update/delete 路由验证：
  - 匿名和失效 cookie 返回 401；
  - 降权用户返回 403；
  - 管理员仍可通过既有成功测试或受控 fixture。
- 测试不得实际修改生产或日常数据库。

### REQ-AUTH-06 公开读取不回归

- `/blog`、`/notes`、`/mistakes` 保持匿名可访问。
- 不增加页面级 `AuthGate`。
- 公开 API 继续只返回允许公开的数据。
- 管理员状态检查失败不得让公开页面出现管理接口错误态。

## 非功能需求

- 安全：默认拒绝；后端仍是真实安全边界。
- 一致性：`/manage` 与共享 `AuthGate` 使用同一管理员判定语义。
- 可测试性：前端覆盖 loading/admin/non-admin/error；后端覆盖完整路由依赖集合和运行时 401/403。
- 可访问性：登录态、验证态和管理态有明确可读文本；不依赖颜色表达权限结果。
- 可维护性：不重构认证架构，不新增第二种管理员状态源。

## 边界

- 不修改 AUTH_BYPASS。
- 不修改 JWT、Passkey 流程、session schema 或认证架构。
- 不修改 `/workspace` 原型。
- 不删除旧 `/manage`、旧编辑器或路由。
- 不迁移数据库、不部署、不推送、不写生产数据。

## 验收标准

1. 匿名/管理员/降权用户/失效 cookie × 390×844、1280×800、1440×900 的浏览器矩阵完成；每个单元格检查 `/manage` 与 `/manage/dashboard`。
2. 全部管理写路由依赖审计通过，create/update/delete 运行时 401/403 测试通过。
3. `/blog`、`/notes`、`/mistakes` 匿名浏览器与静态兼容性测试通过。
4. 前端完整测试通过。
5. R1 scoped source 加上 P0-AUTH diff 的 TypeScript 与生产构建通过。
6. 主工作区 TypeScript/构建也必须记录；若仍仅被排除范围的未跟踪 `/workspace` 原型阻断，结论只能是 `PARTIAL`，不得伪报 `PASS`。

