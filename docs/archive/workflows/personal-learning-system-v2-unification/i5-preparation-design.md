# I5 设计：私有资料、首页偏好与响应式验收

## 1. 设计决策（I5 已批准并实施）

I5 将公开站点配置与管理员私有设置分成两条数据流：

```text
公开首页 -> GET /api/content/site-settings -> 公开站点品牌/主题/公开头像
管理工作区 -> GET/PUT /api/admin/profile -> 管理员私有资料/时区/首页偏好
```

不得把私有资料追加到 `SiteSettingsPayload`，也不得让匿名公开页面请求 `/api/admin/profile`。

采用独立的 `admin_profiles` 一对一表（`user_id` 唯一外键），而不是继续扩张 `users` 或把私有值写进全局 `ManagedContentEntry`。对应 migration 为 `022`，仅在隔离测试目标完成升级/回滚验证。

## 2. 最小私有资料契约

建议 `GET/PUT /api/admin/profile` 使用同一受保护 DTO：

- `display_name`：管理员在工作区显示的名称，长度上限 100。
- `identity_title`：身份/角色标题，长度上限 100，可为空。
- `signature`：工作区欢迎区域签名，长度上限 300，可为空。
- `welcome_message`：可选固定欢迎语，长度上限 300；动态问候由时区计算，不保存当前日期。
- `timezone`：IANA 时区名称，默认 `Asia/Shanghai`，必须使用 `zoneinfo` 校验。
- `home_preferences`：受 schema 限制的首页偏好对象，而不是自由 JSON。

最小 `home_preferences`：

- `show_welcome`：是否显示欢迎区域。
- `section_order`：固定允许区块的排序，去重且不能包含未知区块。
- `hidden_sections`：固定允许区块的隐藏列表，不能隐藏全部安全行动入口。

推荐初始值必须能在没有 profile row 时安全生成，避免首次访问出现 500 或空白页面。

## 3. 公开站点配置边界

现有 `GET /api/content/site-settings` 继续服务公开首页，包含站点标题、副标题、主题颜色、公开头像、背景和社交链接。现有 `PUT /api/content/site-settings` 继续沿用 Passkey 管理员边界；I5 不改变其 API，不向其中加入 `welcome_message`、`timezone` 或私有首页偏好。

若 I5 需要调整公开品牌字段，只能作为现有站点设置表单的显式字段审查项，不得借机重构图片上传、GitHub 同步或 legacy 管理页。

## 4. 前端数据流

- `/manage/settings` 从占位页升级为私有设置表单；页面级沿用 workspace `AuthGate`，API 仍由 `get_current_admin` 保护。
- Dashboard 读取私有 profile 后，仅在管理员会话中显示欢迎语、显示名称和按时区格式化的时间；profile 失败时保留 I4 的安全 Dashboard 和明确的 unavailable 状态。
- 公开首页只继续读取公开 `site-settings`；401/403 的管理员接口不得进入公开页面加载链路。
- 表单必须有 loading、empty/default、保存中、成功、失败可重试和未保存变更提示；按钮和输入均有可访问名称。

## 5. 响应式验收范围

I5 浏览器验收不重复宣称 I4 已完成的导航证据，重点覆盖：

- `/manage/settings`：390×844、1280×800、1440×900；字段可见、无横向溢出、保存与错误状态可读。
- `/manage/dashboard`：私有欢迎语/时区显示与 profile unavailable/empty 降级。
- 公开首页：匿名浏览不请求私有 profile，不暴露私有字段。
- 键盘：从页面入口到所有字段、保存、重置、重试和导航操作均可到达，焦点可见，Escape 不丢失未保存数据。

## 6. 不做

不做多用户/RBAC、共享空间、公开个人资料、头像私有存储、文件工作区、OCR/AI、搜索、任务/分析主数据、迁移切换、生产部署或旧系统停写。

## 7. 实施结果

I5 设计已按上述边界落地：私有 profile 使用 `GET/PUT /api/admin/profile`，公开首页继续使用 `GET /api/content/site-settings`；设置页和 Dashboard 均明确 loading、unavailable、retry 与安全默认态。响应式和键盘证据见 [validation](./validation.md)。
