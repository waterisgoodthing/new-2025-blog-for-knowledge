# 目标权限模型

> 目标模型采用管理通行密钥保护私有学习面；本轮不扩展复杂登录、角色、Passkey 或多用户 RBAC。

## 角色

目标首期只有两种角色：

| 角色 | 定义 |
|---|---|
| 访客 | 未建立管理员会话的公开访问者 |
| 管理员 | 通过脚本生成的管理通行密钥建立有效、未撤销、未过期会话的站点所有者 |

第一版是单管理员通行密钥模型，不设计 `admin_users`、`password_hash`、`passkeys` 或多用户 RBAC。通行密钥本体只存在于服务端安全配置；数据库仅保存会话 token hash 与审计记录。

未来若增加编辑者或只读协作者，应另做权限设计，不在代码中提前埋入模糊角色判断。

## 权限矩阵

| 能力 | 访客 | 管理员 |
|---|---:|---:|
| 阅读公开、已发布 Post/Note/Mistake | 允许 | 允许 |
| 阅读草稿、私有或隐藏内容 | 禁止 | 允许 |
| 查看或管理默认私有题库 | 禁止 | 允许 |
| 查看练习、作答、导入任务与练习报告 | 禁止 | 允许 |
| 创建、编辑、删除内容 | 禁止 | 允许 |
| 进入 `/manage/**` | 禁止 | 允许 |
| 查看/提交复习、统计与计划 | 禁止 | 允许 |
| 创建、查看、重试 AI Run | 禁止 | 允许 |
| 上传、关联、删除附件 | 禁止 | 允许 |
| 管理标签、学科、知识点 | 禁止 | 允许 |
| 查看安全审计 | 禁止 | 允许 |

## 页面规则

- `/`、`/blog/**`、`/notes/**`、`/mistakes/**` 为公开页面。
- `/manage/**` 必须管理员访问。
- `/manage/questions`、`/manage/practice/**`、`/manage/mistakes/**`、`/manage/review/**` 全部属于管理员私有页面。
- 未登录时，公开页面不显示编辑、删除、AI、复习提交和上传操作。
- 公开页面不得调用管理员接口来探测数据；需要管理员增强 UI 时，先确认会话，再按需加载。
- 前端 `AuthGate` 或等价路由保护只改善体验、避免界面闪烁和无效请求，不构成安全边界。

## API 规则

- 公开 API 使用 `/api/public/**`，只返回 `visibility=public AND status=published`。
- 管理 API 使用 `/api/admin/**`，必须通过 `get_current_admin` 或等价服务端鉴权。
- Public 与 Admin 使用不同响应 schema，不得由前端从 Admin DTO 删除敏感字段来模拟公开响应。

- Public API 只允许 GET，并在数据库查询层强制 `status = published`、`visibility = public` 且未删除。
- Public API 对不可见资源返回 404，不泄露草稿存在性。
- Admin API 每个端点都由后端统一校验管理员会话；不能因为页面使用 AuthGate 而省略。
- 创建、编辑、删除、上传、复习和 AI 全部属于管理员能力。
- Question 与 Practice 对应 API 全部依赖 `get_current_admin`；练习导入、报告、Mistake Draft 转换也不得例外。
- 写操作执行资源校验、并发控制和审计，禁止只靠前端隐藏按钮。

## 会话与凭据

- 会话 token 只以哈希存储；cookie 使用 `HttpOnly`、`Secure`、合适的 `SameSite`。
- 管理通行密钥验证后创建可撤销、可过期的服务端 session。
- 通行密钥不应持久化在浏览器可读存储或普通日志中。
- 退出、密钥轮换或安全事件应撤销相关 session。
- 生产环境启动时显式拒绝认证绕过组合；绕过不得成为正常权限测试路径。

## 审计要求

以下操作至少记录 actor、session、action、entity、结果、时间、IP、user agent 和安全脱敏后的前后值：

- 通行密钥验证成功/失败、退出、密钥轮换与会话撤销。
- Post、Note、Mistake 的创建、发布、编辑、删除。
- 复习提交和人工改期。
- AI Run 创建、失败、重试及结果采纳。
- 附件上传、关联、公开性变更和删除。
- Taxonomy 结构调整。
- Question 创建、合并、删除，Practice 导入、分析、确认，以及 Mistake Draft 转换或拒绝。

## 学习数据可见性

- `practice_sessions`、`practice_attempts`、`practice_reports` 默认是私有学习数据，不提供 public API。
- `questions` 默认属于私有题库；除非未来经过单独发布流程显式公开，否则访客不可读取。
- `mistakes` 可由 `visibility` 与发布状态决定是否出现在公开 `/mistakes`。
- `review_items`、`review_records` 永远是私有数据；第一版不使用 `review_schedules`。
- `knowledge_mastery`、`ai_runs`、`ocr_jobs`、`ocr_results`、`capture_jobs`、`draft_items` 和 job logs 永远私有。
- 附件默认私有；练习截图、错题照片、试卷/讲义 PDF、OCR 原文和 AI 来源图永远私有。
- 公开页面只读取已发布、未隐藏的数据；不得因管理员增强功能失败而出现 401/403 噪音。

## 自动化与通行密钥边界

所有 `/manage/**` 页面必须验证管理通行密钥会话；前端保护只改善体验，后端鉴权才是真实边界。所有写入、上传、OCR、Capture、AI、草稿转换、复习、私有统计和设置操作均需管理员身份。

AI/OCR/Capture 只能产生草稿、建议、报告或分析，不能直接写正式学习表。生产环境必须显式拒绝 `AUTH_BYPASS=true` 且 `AUTH_BYPASS_ALLOW=true`；不得依赖 bypass 完成正常权限验收。

## 失败行为

- 未认证 admin API：401。
- 已认证但权限不足：403。
- public 请求不可见资源：404。
- 会话过期：后端拒绝；前端清除会话视图并引导登录。
- 公开页的管理员增强模块失败：局部隐藏或提示，不影响公开正文。
