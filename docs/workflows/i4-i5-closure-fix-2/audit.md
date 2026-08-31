# 现状审计

日期：2026-07-23

## 已核对事实

1. `backend/app/schemas/admin_profile.py` 已校验 section 枚举、去重、完整排序集合和“至少一个区块可见”，但未校验至少一个学习行动区块可见。
2. `src/app/manage/(workspace)/settings/admin-profile-settings.tsx` 仅以 `sections.length - 1` 限制隐藏数量，未与后端共享“学习行动区块”规则。
3. `DashboardOverview` 当前按固定 JSX 顺序渲染“今日任务/内容统计/最近活动/系统状态”，未读取 `profile.home_preferences.section_order` 或 `hidden_sections`。
4. `dashboard_service.py` 在 `storage` 为空时将 section 标记为 `empty`，但 system storage 只在 `ready` 时标记 `ok`，因此 empty 被误映射为 `unknown`。
5. 当前 Dashboard 测试已覆盖部分 unavailable/unknown 与 profile retry，但没有覆盖偏好保存后的重新读取、真实排序/隐藏渲染、empty 健康映射及完整正常 commit 证据。

## 保留边界

- 不重置或整理当前脏工作树。
- 不把 I5 的 profile 设计重新扩大为新的设置功能；只消费已存在的偏好契约。
- 不把局部失败、empty 或浏览器证据写成 PASS，除非执行后有实际日志/截图/测试输出。
