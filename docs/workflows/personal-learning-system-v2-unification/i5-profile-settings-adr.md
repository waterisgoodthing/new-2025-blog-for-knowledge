# ADR-I5-01：公开站点设置与管理员私有资料分离

日期：2026-07-22
状态：`ACCEPTED FOR I5 IMPLEMENTATION`

## 背景

现有 `ManagedContentEntry(key="site-settings")` 服务公开首页，`GET /api/content/site-settings` 无需管理员身份，前端 `SiteSettingsLoader` 会将其注入公开页面。现有 `User` 模型没有 profile、timezone 或首页偏好字段；`/manage/settings` 仍是占位页。

如果把管理员欢迎语、时区或首页偏好继续写入 `site-settings`，匿名页面会间接读取私有数据，并且全局配置无法表达用户所有权。

## 决定

1. 公开品牌/主题/公开头像/背景/社交链接继续留在现有 `site-settings` 契约；不向其加入私有 profile 字段。
2. I5 新增独立 `admin_profiles` 表，一行对应一个 `users.id`，`user_id` 唯一、级联删除；首版仅支持当前单管理员产品边界，不引入 RBAC 或共享空间。
3. `admin_profiles` 通过受保护的 `GET/PUT /api/admin/profile` 访问，读取和写入均依赖 `get_current_admin`；匿名和失效会话返回 401。
4. profile 初始不存在时由 service 返回稳定默认值；首次保存才创建记录。时区必须是可由 Python `zoneinfo` 解析的 IANA 名称。
5. Dashboard 只在管理员工作区消费 profile；公开首页不请求该接口。

## Schema / migration 计划

拟新增 `admin_profiles`：

- `id` UUID 主键
- `user_id` UUID 外键 `users.id`、唯一、`ON DELETE CASCADE`
- `display_name`、`identity_title`、`signature`、`welcome_message` 字符串字段
- `timezone` 字符串，默认 `Asia/Shanghai`
- `home_preferences` JSONB，仅存受 schema 校验后的对象
- `created_at`、`updated_at`

迁移必须从当前隔离目标 revision `021` 产生，完成 `021 → 022 → 021 → 022`、`alembic check`、默认值/回滚/后续查询恢复；不得对源库或生产库执行。

## 后果

- 公开与私有边界清晰，未来可按 `user_id` 扩展而不改变公开站点契约。
- I5 需要一个新 migration 和对应模型/schema/client/service/测试，不能只改前端占位页。
- 首版单管理员仍有产品边界限制；多用户/RBAC 留在后续阶段。
