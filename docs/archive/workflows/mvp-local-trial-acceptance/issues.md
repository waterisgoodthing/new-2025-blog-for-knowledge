# Issues

## 使用规则

- 本文件只记录本地试运行发现的问题。
- 不在本轮自动修复问题。
- 不因为发现问题而新增功能、脚本、迁移、AI/OCR/BKT、对象存储或云部署。
- 若需要修复，必须由用户另行批准，并单独进入对应 workflow。

## 严重程度

- P0：阻塞本地 MVP 主链路继续执行，或造成公开泄露、权限绕过、数据无法保存/读取。
- P1：影响核心体验或数据一致性，但可以通过替代步骤继续试运行。
- P2：文案、展示、轻微交互、日志噪音或后续优化项。

## 状态

- `open`
- `confirmed`
- `needs-info`
- `deferred`
- `approved-for-fix`
- `fixed-in-separate-workflow`
- `wont-fix`

## 问题总览

| ID | 标题 | 严重程度 | 链路节点 | 状态 | 是否阻塞验收 | 关联样例 |
| --- | --- | --- | --- | --- | --- | --- |
| LT-ISSUE-001 | 本地 Passkey RP 配置与 localhost 运行域名不匹配 | P2 | non-target compatibility | wont-fix | 否 | 全部 |
| LT-ISSUE-002 | 禁用临时管理员后密码登录返回 500 | P1 | auth cleanup | fixed-in-separate-workflow | 否（已修复） | 全部 |
| DEMO-ISSUE-001 | 匿名 `/mistakes` 被重定向到管理工作区 | P0 | public boundary / route compatibility | fixed-in-separate-workflow | 否（已复验） | 现场演示 |

## 问题模板

复制以下模板新增问题。

### LT-ISSUE-XXX：`<标题>`

| 字段 | 内容 |
| --- | --- |
| 严重程度 | P0 / P1 / P2 |
| 状态 | open |
| 发现日期 |  |
| 发现人 |  |
| 关联样例 |  |
| 链路节点 | subject / knowledge point / question draft / question / mistake draft / mistake / review item / review record / attachment upload / attachment link / attachment read / public boundary / environment |
| 是否阻塞本地 MVP 验收 | 是 / 否 / 待确认 |
| 是否已获准修复 | 否 |

#### 现象

-

#### 复现步骤

1.
2.
3.

#### 预期结果

-

#### 实际结果

-

#### 证据

- 页面：
- 对象 ID：
- 截图路径：
- 日志摘要：
- API 响应摘要：

#### 影响范围

-

#### 临时处理

-

#### 建议归属

- [ ] 本地环境问题
- [ ] 权限 / AuthGate
- [ ] subject / knowledge point
- [ ] question draft / question
- [ ] mistake draft / mistake
- [ ] review item / review record
- [ ] attachment
- [ ] 公开边界
- [ ] 后续独立迁移 / 统一模型
- [ ] 其他：

#### 下一步

- [ ] 仅记录，等待用户判断。
- [ ] 需要补充信息。
- [ ] 需要用户批准后单独开修复 workflow。
- [ ] 不进入下一轮需求。

### LT-ISSUE-002：禁用临时管理员后密码登录返回 500

| 字段 | 内容 |
| --- | --- |
| 严重程度 | P1 |
| 状态 | fixed-in-separate-workflow |
| 发现日期 | 2026-07-04 |
| 发现人 | Codex |
| 关联样例 | 全部 |
| 链路节点 | auth cleanup |
| 是否阻塞本地 MVP 验收 | 否 |
| 是否已获准修复 | 是 |

#### 现象

- `disable-temp-admin` 成功后，使用原一次性密码重新调用 `/api/auth/login` 返回 HTTP 500 和 `Internal Server Error`。
- 禁用前建立的旧 cookie 会话访问 `/api/subjects` 返回 403，说明管理员权限已被撤销。

#### 复现步骤

1. 使用既有 CLI 创建 `temp-admin` 并完成一次密码登录。
2. 运行既有 `disable-temp-admin --username temp-admin`。
3. 使用禁用前的一次性密码再次调用 `/api/auth/login`。

#### 预期结果

- 登录失败并返回 401，不泄露内部异常。

#### 实际结果

- 登录返回 500；旧管理员会话返回 403。

#### 影响范围

- 不阻塞主链路和权限撤销，但会产生认证错误噪音，并可能暴露未处理的密码哈希边界。

#### 临时处理

- 账号保持禁用；临时密码文件和 cookie jar 已删除。

#### 下一步

- [x] 修复前作为“有条件通过”的唯一条件项保留。
- [x] 已进入并完成独立的 Auth Error Handling Cleanup。

#### 修复结果（2026-07-17）

- [x] 在 `backend/app/utils/auth.py` 的 `verify_password()` 边界捕获 `TypeError` / `ValueError`，将 malformed/disabled hash 视为不匹配。
- [x] 禁用账号密码登录回归测试返回 401 `Invalid credentials`。
- [x] 认证与全量后端测试通过；未修改 schema、migration 或数据。
- [x] LT-ISSUE-002 关闭。

### DEMO-ISSUE-001：匿名 `/mistakes` 被重定向到管理工作区

| 字段 | 内容 |
| --- | --- |
| 严重程度 | P0 |
| 状态 | fixed-in-separate-workflow |
| 发现日期 | 2026-07-16 |
| 发现人 | Codex |
| 关联样例 | 无；只读现场演示 |
| 链路节点 | public boundary / route compatibility |
| 是否阻塞项目验收 | 否（已复验） |
| 是否已获准修复 | 是 |

#### 现象

- 匿名访问 `http://localhost:2025/mistakes` 时，浏览器最终进入 `/manage` 或 `/manage/mistakes`，无法看到公开错题列表。
- 直接 HTTP 检查返回 `307 Location: /manage/mistakes`。

#### 复现步骤

1. 在未登录状态打开 `http://localhost:2025/mistakes`。
2. 等待客户端导航完成。
3. 检查浏览器 URL 和页面内容。

#### 预期结果

- 匿名用户留在 `/mistakes`，可以读取已发布、未隐藏的公开错题。
- 页面不调用管理员复习、附件、AI 或 Capture API。

#### 实际结果

- 服务端返回 307，目标为 `/manage/mistakes`。
- 浏览器进入管理侧，未登录时显示登录保护，因此公开错题列表不可达。

#### 证据

- HTTP：`curl -I http://localhost:2025/mistakes` → `307 Location: /manage/mistakes`。
- 浏览器：最终 URL 为 `http://localhost:2025/manage` 或 `http://localhost:2025/manage/mistakes`。
- 代码定位：`next.config.ts` 存在 `/mistakes` → `/manage/mistakes` redirect 规则。

#### 影响范围

- 匿名公开错题列表不可访问。
- 与 Batch 7 public read contract 冲突，阻塞项目验收的无条件通过结论。
- 未观察到私有数据泄露或未授权写入。

#### 临时处理

- 本次只记录，不修改 redirect、不修改页面、不重启服务。

#### 建议归属

- [x] 权限 / AuthGate / public route compatibility
- [ ] subject / knowledge point
- [ ] question / mistake / review
- [ ] attachment
- [ ] 后续独立修复 workflow

#### 下一步

- [x] P0-16 删除错误 redirect。
- [x] P0-17 只读浏览器复验通过。
- [x] 保留 `/mistakes/review` 私有重定向并复验通过。

## 当前记录

### LT-ISSUE-001：本地 Passkey RP 配置与 localhost 运行域名不匹配

| 字段 | 内容 |
| --- | --- |
| 严重程度 | P2 |
| 状态 | wont-fix |
| 发现日期 | 2026-07-04 |
| 发现人 | Codex |
| 关联样例 | two-sum、valid-parentheses、tree-level-order |
| 链路节点 | environment |
| 是否阻塞本地 MVP 验收 | 否；localhost 不再是主要目标访问环境 |
| 是否已获准修复 | 否 |

#### 现象

- 本地 `/manage` 可显示登录页，但在 `http://localhost:2025` 点击“使用 Passkey 登录”后，浏览器拒绝 WebAuthn 请求。
- 页面错误为：`The relying party ID is not a registrable domain suffix of, nor equal to the current domain.`

#### 复现步骤

1. 确认前端运行于 `http://localhost:2025`、后端运行于 `http://127.0.0.1:8000`。
2. 未登录打开 `http://localhost:2025/manage`。
3. 点击“使用 Passkey 登录”。

#### 预期结果

- 本地 Passkey 验证可完成并建立管理员会话，且不依赖 `AUTH_BYPASS`。

#### 实际结果

- `backend/.env` 的 `WEBAUTHN_RP_ID` 为 `blog.limengyang.me`，`WEBAUTHN_ORIGIN` 为 `https://blog.limengyang.me`。
- 当前运行域名为 `localhost`，浏览器在 WebAuthn RP 校验阶段拒绝请求，管理员会话未建立。
- 密码凭据未读取或输出；未创建、轮换临时管理员；未改配置。

#### 证据

- 页面：`http://localhost:2025/manage`
- 环境：数据库迁移 `014 (head)`；后端健康检查 `200 {"status":"ok","db":"ok"}`；前端 `200`。
- 权限：未登录 `GET /api/subjects`、`GET /api/admin/drafts`、`GET /api/admin/attachments` 均返回 `401 {"detail":"Not authenticated"}`。
- 配置摘要：`AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false`。

#### 影响范围

- 仅影响 localhost 下的 Passkey 登录兼容性。
- localhost 不再是主要目标访问环境，因此不影响当前日常试用结论。

#### 临时处理

- 不处理。该项按非目标环境兼容问题归档，不启动专项。

#### 建议归属

- [x] 本地环境问题
- [x] 权限 / AuthGate
- [ ] subject / knowledge point
- [ ] question draft / question
- [ ] mistake draft / mistake
- [ ] review item / review record
- [ ] attachment
- [ ] 公开边界
- [ ] 后续独立迁移 / 统一模型
- [ ] 其他：

#### 下一步

- [x] 仅作为非目标环境兼容记录归档。
- [ ] 需要补充信息。
- [ ] 需要用户批准后单独开修复 workflow。
- [x] 不进入下一轮需求。
