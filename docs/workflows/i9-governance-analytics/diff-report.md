# I9 差异报告

- 新增 `/api/admin/governance/summary`，管理员保护，返回生成时间、来源、计数和 `ready/empty/unavailable` 状态。
- AI 页面读取现有 `ai_runs`；分析与任务页面读取治理汇总；设置继续读取 `admin_profiles`。
- 保留 AI 草稿/人工确认闸门，不调用真实 provider，不写入正式学习对象。
- 运行时验证中发现并修正了构建注入与陈旧后端进程问题；未修改生产配置、源库或生产数据。
