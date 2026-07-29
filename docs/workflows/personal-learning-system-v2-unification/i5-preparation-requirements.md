# I5 需求与验收基线（已通过）

## 目标

在不破坏公开读取边界的前提下，为单管理员提供可保存、可恢复、可验证的私有资料、时区和首页偏好；同时明确公开站点品牌配置与私有设置的契约分离。

## 需求

| 编号 | 需求 | 验收基线 |
| --- | --- | --- |
| I5-01 | 私有资料真实存储 | 管理员可读取/更新 display name、identity title、signature、welcome message；数据不写入公开 site-settings；首次无记录有安全默认值。 |
| I5-02 | 时区安全 | 只接受 IANA timezone；无效值返回 422；Dashboard 的动态问候/时间按保存时区计算；不保存易漂移的当前问候文本。 |
| I5-03 | 首页偏好受约束 | section order/hidden sections 使用显式枚举、去重和上限校验；不能隐藏所有安全行动入口；保存后刷新仍一致。 |
| I5-04 | 后端权限 | 匿名和失效会话访问 profile 为 401；非管理员为 403；所有写入依赖 `get_current_admin`；不启用 `AUTH_BYPASS` 验收。 |
| I5-05 | 公开/私有隔离 | 匿名公开首页只请求 `site-settings` 等公开接口；网络与 DOM 不出现私有 profile 字段；公开页面不因 profile 401/403 报错。 |
| I5-06 | 设置页状态 | `/manage/settings` 覆盖 loading、默认/empty、saving、saved、validation error、network error/retry 和未保存离开提示。 |
| I5-07 | Dashboard 降级 | profile unavailable 时 I4 Dashboard 的学习、活动、存储区块仍可用，欢迎区域明确 unavailable，不泄露内部异常。 |
| I5-08 | 响应式与键盘 | 设置页与 Dashboard 在 390×844、1280×800、1440×900 无横向溢出；键盘可到达字段、保存、重置、重试和导航，焦点可见。 |
| I5-09 | 数据与恢复 | 若批准新增 schema/migration，必须在 `pls_v2_i4_target` 的隔离副本验证 upgrade/downgrade、默认值、回滚和重新查询；不触碰源库。 |
| I5-10 | 代码质量 | router 保持薄，业务逻辑进 service，schema/client 同步，补齐定向测试、TypeScript、Python 编译、Alembic check 和 diff 检查。 |

## 通过门槛

I5 只有在 I5-01 至 I5-10 全部有代码、API、权限、浏览器和必要恢复证据时才能标记 `COMPLETE / PASS`。任何 schema authority、公开/私有边界或生产操作不明确，均保持 `BLOCKED`，不得进入 I6。

## I5 实施结论

I5-01 至 I5-10 均已满足：私有 profile 使用受保护 API 与 `admin_profiles` revision `022`，公开首页未请求或暴露私有字段，设置页与 Dashboard 覆盖默认/失败/重试状态，前后端定向测试与三尺寸/键盘证据已归档。I6 仍需新的任务清单与明确批准。
