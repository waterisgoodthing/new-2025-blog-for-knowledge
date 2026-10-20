# Handoff Prompt

## Target

Implementation agent

## Task Type

Implement an operator-only `blog.limengyang.me` passkey registration tool for `manage-auth-hardening` Phase 7.

## Prompt

你现在接手 `/Users/limengyang/2025-blog-public` 仓库中 `docs/workflows/manage-auth-hardening/` 的一个补洞任务：

- 不是继续排查部署；
- 不是重做 `/manage` 登录页；
- 而是补一个 **operator-only 的公网域名 passkey 注册工具**，让当前机器可以为 `blog.limengyang.me` 真实注册并替换管理员 passkey。

先读这些文件：

- `docs/workflows/manage-auth-hardening/README.md`
- `docs/workflows/manage-auth-hardening/requirements.md`
- `docs/workflows/manage-auth-hardening/tasks.md`
- `docs/workflows/manage-auth-hardening/validation.md`
- `backend/app/cli.py`
- `backend/app/services/passkey_service.py`
- `backend/app/routers/auth.py`
- `backend/app/models/session.py`

---

## 一、你要先接受的事实边界

当前系统状态已经核实：

1. 线上 RP/origin 已经是：
   - `WEBAUTHN_RP_ID=blog.limengyang.me`
   - `WEBAUTHN_ORIGIN=https://blog.limengyang.me`
2. 数据库里已有一条 `PasskeyCredential`，但它没有在当前公网 RP 迁移后成功用于登录。
3. 当前没有 `AdminPassword`，所以不能走“先密码登录，再进安全页重绑”的恢复路径。
4. 当前公网只提供：
   - `GET /api/auth/passkey/reg-options`
   - `GET /api/auth/passkey/auth-options`
   - `GET /api/auth/passkey/status`
   - `POST /api/auth/login-passkey`
5. 当前没有公网 passkey 注册 verify/store 入口。
6. 现有 `backend/app/cli.py register-passkey` 仍然是 `localhost` origin 注册流，不足以闭合 `https://blog.limengyang.me` 的真实 passkey 注册。

所以本任务的核心不是“修登录”，而是：

**增加一个只给 operator 使用、但能对 `blog.limengyang.me` 这个公网 RP 生效的注册工具。**

---

## 二、目标产物

请实现一个 **operator-only** 工具，满足下面目标：

1. 可以由本机 operator 明确触发，不面向普通匿名用户暴露。
2. 注册出来的 credential 必须真实绑定到：
   - RP ID: `blog.limengyang.me`
   - Origin: `https://blog.limengyang.me`
3. 工具必须能把新 credential 写入当前数据库，并替换旧 credential。
4. 工具完成后，应能用这台机器在 `https://blog.limengyang.me/manage` 上通过 passkey 登录。

---

## 三、推荐实现方向

优先实现一个 **operator-only backend registration flow**，而不是继续依赖 `localhost` CLI 页面。

推荐方案：

1. 在后端增加一组仅供 operator 使用的 passkey 注册端点。
2. 这组端点必须能：
   - 生成 `blog.limengyang.me` 的 registration options
   - 接收 attestation
   - verify registration
   - 原子替换旧 `PasskeyCredential`
3. 入口必须是 operator-only，而不是公开匿名可用。

推荐做法二选一，优先选 A：

### 方案 A：operator key / CLI token 保护的 HTTP 注册接口

例如新增单独的 operator 注册 router 或 auth router 下的 operator-only 端点：

- `POST /api/auth/passkey/operator/reg-options`
- `POST /api/auth/passkey/operator/register`

保护方式建议：

- 使用单独环境变量，如 `OPERATOR_REGISTRATION_KEY`
- 通过 header 传递，例如 `X-Operator-Registration-Key`
- 必须 fail-closed
- 不依赖现有普通 admin session

这样 operator 可以在真实公网 origin 页面中完成 `navigator.credentials.create(...)`，再把 attestation 发回后端。

### 方案 B：增强 CLI，但必须支持公网域名注册

只有在你能证明 A 不合适时才选。

如果沿用 CLI，必须满足：

- 不再默认只生成 `localhost` origin
- 能明确指定公网 RP/origin
- 能在真实 `https://blog.limengyang.me` 上完成注册，而不是伪装 localhost 成功

如果你只是把现有 CLI 稍微改一下 host/port，但注册 origin 仍不是公网域名，这不算完成任务。

---

## 四、强约束

### 安全约束

1. 绝不能把 passkey 注册入口直接开放给匿名公网用户。
2. 绝不能因为要补工具，就顺手把 `/manage/security` 改成匿名可访问。
3. 绝不能复活 `AUTH_BYPASS` 作为公网注册手段。
4. 绝不能让 operator 工具变成一个长期裸露、无强保护的后门。

### 架构约束

1. 遵守现有 backend 分层：
   - router 薄
   - passkey 逻辑进 `services`
   - request/response contract 进 `schemas`
2. 不要把复杂 WebAuthn 流程硬塞进 router。
3. 如果新增配置项，要同步：
   - `backend/app/config.py`
   - `backend/.env.example`
4. 如果新增模型字段或持久化变化，补 migration。

### 产品约束

1. 这是 operator-only 工具，不要求做成对普通用户可见的完整产品 UI。
2. 但操作路径必须可验证、可重复，不要做成一次性手工 hack。
3. 最终应该让 Phase 7 可以真的闭环，而不是只留下“理论上可行”。

---

## 五、建议落地形态

下面是我建议你优先实现的最小形态：

### 后端

1. 新增 operator registration schema
   - reg-options request
   - register verify request
   - success/error response

2. 新增 operator-only registration endpoints
   - 通过 `X-Operator-Registration-Key` 校验
   - `reg-options` 固定产出 `blog.limengyang.me` 对应注册参数，或从受控 config 读取
   - `register` 调 `verify_registration(...)`
   - 成功后先删旧 credential，再写入新 credential

3. 记录最少必要审计信息
   - 谁触发：operator path
   - 结果：success/failure
   - device_name
   - 不要记录敏感原始 attestation 全量到日志

### Operator 侧

二选一即可：

1. 一个受控 HTML/operator page，只给 operator 用
2. 或一个 CLI 命令，负责打开真实公网注册页并调用新接口

关键不是形式，而是：

- 浏览器中的 `navigator.credentials.create(...)` 必须发生在真实可接受的公网 origin 上
- 后端 verify/store 路径必须受 operator key 保护

---

## 六、必须回答的问题

在实现前，你必须自己先回答并在文档里落实：

1. operator-only 入口放哪一层最合适？
   - auth router 子路径
   - 单独 operator router
   - CLI + backend endpoint 混合

2. operator key 如何配置与校验？
   - env 名称是什么
   - 缺失时是否 fail-closed

3. 替换旧 credential 的策略是什么？
   - 先 reset 再 register
   - 还是事务内替换
   - 失败时如何避免把唯一 credential 删掉却没写回

4. 设备名怎么传？
   - 前端输入
   - CLI 参数
   - 默认值

5. 注册完成后，如何验证这台机器能真实登录？

---

## 七、验证标准

这次不能只做代码验证，必须有至少一轮真实执行证据。

最少要验证：

1. `npx tsc --noEmit`
2. `python -c "from main import app"` 或等效 import check
3. operator-only `reg-options` 在未带 operator key 时拒绝访问
4. operator-only `reg-options` 在带正确 key 时返回可用 registration options
5. operator-only `register` 能成功写入新 credential
6. `PasskeyCredential` 被替换后，`last_used_at` 在真实登录后更新
7. `https://blog.limengyang.me/manage` 这台机器可成功 passkey 登录
8. passkey-only action 仍然只允许 `auth_level == "passkey"`

所有未实际验证到的内容必须明确标注“未验证”。

---

## 八、你要更新的 workflow 文档

请不要跳过仓库 workflow。

至少更新：

- `docs/workflows/manage-auth-hardening/design.md`
- `docs/workflows/manage-auth-hardening/requirements.md`
- `docs/workflows/manage-auth-hardening/tasks.md`
- `docs/workflows/manage-auth-hardening/validation.md`

如果你改变了实现策略，也要把策略变化写清楚，不要只改代码不改文档。

---

## 九、完成定义

只有同时满足下面条件，才算这轮 operator-only 工具完成：

1. 不是 `localhost` 假注册，而是真正对 `blog.limengyang.me` 生效。
2. 注册入口不是匿名裸露，而是 operator-only。
3. 新 credential 已写入数据库并替换旧值。
4. 这台机器已通过新 credential 在公网 `/manage` 登录成功。
5. 文档里留下了完整证据链。

如果只能做到“代码看起来对”，但没有真实注册与真实登录证据，请明确写“未验证”，不要报完成。
