# I5 准备现状发现

日期：2026-07-22

## 已确认事实

- I4 已归档为 `COMPLETE / PASS`；I5 必须重新获得增量级批准，不能沿用 I4 批准。
- 当前已有公开 `GET /api/content/site-settings`，以及对应的 `PUT /api/content/site-settings`；这套内容包含站点品牌、背景、社交按钮等公开内容配置，不能直接当作管理员私有资料。
- 当前首页存在站点设置加载器与站点设置编辑组件；管理工作区已有 `/manage/settings`，但需要进一步核对它的实际数据来源、写入权限和是否覆盖 I5 的用户资料/偏好需求。
- 当前后端用户/会话采用管理员会话边界；I5 的私有设置写入必须继续依赖 `get_current_admin`，不能使用前端隐藏按钮代替后端保护。
- 当前工作区已知规则要求：公开页面不得因管理员接口 401/403 报错；私有资料不能由匿名页面读取。
- `backend/app/models/note.py:User` 当前只有 `id`、`username`、`password_hash`、`is_admin`、`created_at`，没有 profile、timezone 或首页偏好字段。
- `backend/app/routers/content.py` 的公开 `GET /api/content/site-settings` 不需要管理员身份；更新使用 `get_passkey_admin`。因此该入口不能承载管理员私有 profile。
- `backend/app/services/content_store.py` 将 `site-settings` 存在全局 `ManagedContentEntry`，默认值来自 `src/config/site-content.json` 与 `card-styles.json`；这套数据会被 `SiteSettingsLoader` 注入公开首页。
- 旧 `/manage?tab=settings` 复用 `SiteSettingsPanel` 编辑公开站点品牌/主题/图片；规范工作区 `/manage/settings` 目前仍是无保存动作的 `FutureCapabilityPage` 占位页。

## 待核对问题

1. `site-settings` 的完整 schema、存储键和公开字段清单是什么？是否存在敏感字段混入风险？
2. `/manage/settings` 当前可编辑哪些字段？哪些只是 legacy 配置或占位页？
3. 用户模型是否已有 profile/timezone/preference 字段；若没有，最小 I5 是否需要新表/迁移？
4. 欢迎语、品牌、时区和首页偏好分别应归属用户私有设置还是公开站点设置？需要形成明确 ADR/决策记录。
5. 前端哪些页面消费这些值：公开首页、管理首页、导航、日期格式化和复习摘要？
6. I5 的三尺寸与键盘证据应覆盖哪些页面，如何避免重复 I4 已归档的 Dashboard 导航证据？

## 暂定边界判断

- 公开品牌/背景/社交链接继续属于 `site-settings`，但管理员个人显示名、欢迎语、时区和 Dashboard 偏好应优先按私有设置设计。
- 在确认用户模型和 schema authority 前，不授权直接新增字段或 migration；准备阶段只记录选项、影响和待决策点。

## 关键决策待批准

- 是否采用独立 `admin_profiles` 一对一表承载私有资料与首页偏好（推荐），而不是扩展 `users` 或复用全局 `ManagedContentEntry`。
- 公开 avatar/站点名称/副标题/主题是否继续留在既有 `site-settings`，管理员 display name/welcome/timezone 是否只在私有 profile 中展示。
- I5 首版是否只支持当前单管理员；多用户/RBAC 明确留在后续阶段。
