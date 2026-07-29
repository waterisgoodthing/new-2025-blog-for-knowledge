# I9 现状审计

审计基线：2026-07-24，隔离数据库 `pls_v2_i4_target`，代码 revision 024。

- `ai_runs` 36、`ai_call_logs` 51、`attempts` 0、`mistakes` 3、`review_items` 3、`notes` 13、`admin_profiles` 2、`audit_logs` 136（只读 SQL）。
- `/manage/ai`、`/manage/ai/runs`、`/manage/analytics`、`/manage/jobs` 原先分别为占位或后续能力页面；已有 AI 运行 API 和设置 API。
- 没有持久化后台任务模型；I9 不伪造任务主数据，改为明确 `unavailable`。
