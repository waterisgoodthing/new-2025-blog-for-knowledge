# Phase B：Authentication Boundary Design

状态：设计完成，未修改认证配置。  
当前事实：后端主要使用 session cookie 与 `get_current_admin`；Phase A 记录 `ENABLE_REGISTRATION=True`，并存在 `AUTH_BYPASS` 与 `AUTH_BYPASS_ALLOW` 双开关。

## 四类身份

| 身份 | 可访问范围 | 默认不可做 | 认证/授权原则 |
|---|---|---|---|
| public | 已发布、未隐藏的公开内容和公开发布快照；公开详情只读 | 私有学习数据、复习、AI 操作、附件上传/下载、管理写入 | 后端公开 query 必须显式过滤 `status=published`、`hidden=false` 或发布快照状态；前端不把 401 当成公开页面错误 |
| authenticated user | 归属于自身的私有学习内容、采集、作答、复习和附件（目标态） | 他人数据、admin-only 治理、全局 settings、provider/retry/审计管理 | 需要有效 session/JWT 后再做 owner policy；当前实现主要是 admin session，不能把现状误写成已完成 user 隔离 |
| admin | 所授权 owner 范围内的管理页面、审核、AI Run、taxonomy、附件治理和内容写入 | 绕过 owner、绕过审计、把 AI 草稿直接当正式事实 | `get_current_admin` 是当前后端 admin seam；`/api/admin/**` 作为明确管理命名空间；每个 command 仍需 owner 校验 |
| worker | 受信异步任务的最小执行权限：OCR/AI/索引/导出/备份任务 | 直接接受浏览器身份、扩大 owner 范围、绕过 service、任意公开 | worker identity 仅用于调用 job handler；任务 payload 必须带 owner、object ID、幂等键；最终写入走 application service 和审计 |

## AUTH_BYPASS

当前语义是两个值同时为 true 才绕过：`AUTH_BYPASS=true` 且 `AUTH_BYPASS_ALLOW=true`。Phase B 的目标策略：

- 本地开发可保留机制，但测试必须覆盖 bypass 关闭、单开一个开关、双开三个矩阵，不得用 bypass 证明正常权限。
- 生产启动必须显式拒绝双 true 组合，并在启动日志/健康检查中留下可审计结果；本轮只记录设计，不改配置或启动代码。
- 任何设计、示例、runbook 和验收命令都不得建议生产启用 bypass。
- bypass 不改变对象 owner、公开过滤、审计或 worker 规则。

## ENABLE_REGISTRATION

当前配置为 `ENABLE_REGISTRATION=True`，这属于高风险现状，不在本轮修改。目标策略是按环境显式配置：个人生产环境默认关闭；若临时开启，必须限制入口、速率、审计和管理员批准，并在部署前验证最终生效配置。注册成功不等于 admin，admin 角色必须由独立受控流程授予。

## `/manage` 页面保护

`/manage` 及其子路由是 admin operation surface。目标行为：

1. 在根 layout 或等价 route seam 统一确认 admin session；未认证时不渲染管理数据骨架，转到既有登录入口。
2. 子页面仍按 API 失败处理，不能把父级 UI 保护当成后端安全边界。
3. 管理页面的流式 AI、附件内容、retry、decision、settings 和 jobs 均视为 admin command/query。
4. 未登录访问不应发起大量管理 API 请求；页面降级只显示登录入口或安全的空态。
5. `/mistakes`、`/notes`、公开博客与公开详情不纳入 `/manage` 强制保护；管理按钮按 session 隐藏或显示。

## `/api/admin` boundary

目标命名空间划分：

```text
/api/public/*       public query / published snapshot only
/api/me/*           authenticated owner-scoped query/command
/api/admin/*        admin query/command with get_current_admin
/api/worker/*       internal task seam, never browser-public
```

现有 `/api/notes`、`/api/review`、`/api/ai` 等混合 prefix 在迁移期保留兼容读，但新增写入必须归入明确 command seam；旧路径的每个 endpoint 要记录 owner、admin、public、worker 四种结果。所有 admin router 需保留后端依赖，不能因前端 AuthGate 或 `/manage` layout 已保护而移除。

## Worker 安全契约

worker 任务只接收已验证的 task ID、owner ID、目标类型/ID、schema 版本和幂等键。worker 通过 service 读取授权对象、写入状态和 `audit_log`/`AiRun`；失败只写安全错误码。任务 payload、重试和日志不得包含 token、cookie、authorization、API key、完整 prompt 或未经脱敏的个人内容。
