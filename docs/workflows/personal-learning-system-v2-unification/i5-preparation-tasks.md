# I5 准备任务清单

状态：`I5 COMPLETE / PASS / I6 APPROVAL REQUIRED`

以下清单已获用户批准；按顺序执行，每项完成后立即更新本清单与 validation。

- [x] I5-01 冻结公开 `site-settings` 与私有 profile/preferences 的字段、所有权和 API 边界；形成最终 ADR/决策记录。见 [ADR-I5-01](./i5-profile-settings-adr.md)。
- [x] I5-02 确认 schema authority，选择独立 `admin_profiles` 表或已有模型扩展；补充 migration/回滚计划。采用独立 `admin_profiles`，`021 → 022 → 021 → 022` 已完成验证。
- [x] I5-03 新增私有 profile/preferences 的 schema、service、管理员路由与前端 API client；实现默认值、IANA 时区校验、枚举/排序约束。后端/前端契约已同步，profile 定向测试已通过。
- [x] I5-04 将 `/manage/settings` 占位页升级为受保护设置表单；实现 loading、empty/default、保存、失败重试、未保存提示和可访问名称。设置组件测试 3 项通过。
- [x] I5-05 将管理员私有 profile 接入 Dashboard 欢迎区域与时区格式化；profile unavailable 时保留 I4 安全摘要和明确降级。Dashboard profile unavailable/retry 与 UTC greeting 定向测试通过。
- [x] I5-06 验证公开首页只消费公开 site-settings；匿名/失效 profile 请求为 401，浏览器无私有字段请求或泄露，公开 payload 不含 profile 字段。
- [x] I5-07 完成后端/前端定向测试：权限、默认值、422、保存刷新、失败恢复、公开隔离、Dashboard 降级与重试；前端 22 项、后端 11 项通过。
- [x] I5-08 在隔离目标完成 `021 → 022 → 021 → 022` upgrade/downgrade、回滚和后续查询恢复；最终 revision `022`，未写源库/生产。
- [x] I5-09 已采集 `/manage/settings`、`/manage/dashboard` 和公开首页的 390×844、1280×800、1440×900 与键盘证据，保存并链接于 `assets/i5-preparation/`。
- [x] I5-10 已完成残余风险、归档决定及 README/tasks/validation/incremental-plan 状态统一；I5 标记 `COMPLETE / PASS`，I6 保持单独审批。

## 不授权

本清单不授权生产部署、源库/生产数据写入、权威切换、旧系统停写、真实 AI provider 调用、多用户/RBAC、文件工作区或 I6 以后能力。
