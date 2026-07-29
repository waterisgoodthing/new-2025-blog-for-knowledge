# I4 closure-fix 现状发现

日期：2026-07-22

- 当前 `get_dashboard_summary` 将 counts、题目/错题/复习活动放在同一个服务调用中，`sections.learning` 与 `sections.activity` 目前固定为 `ready`。
- 当前路由捕获 `SQLAlchemyError` 后直接返回 unavailable 摘要，但没有在捕获前调用 `await db.rollback()`；若 `get_db` 依赖随后提交，失败事务可能污染该 dependency 生命周期。
- `backend/app/database.py:get_db` 已有正常路径 commit、异常路径 rollback，但现有测试主要是单元/服务级或路由依赖存在性检查，缺少真实 dependency 生命周期的 commit/rollback/close 证据。
- 前端已有整体 error/retry 与局部 sections 展示；需要补齐 learning/activity/storage 三类状态的真实 fixture 与重试断言。
- I4 浏览器已在前一轮取得尺寸结果，但 closure-fix 要求将截图/键盘操作证据落到 `assets/i4-closure-fix/` 并从 validation 逐项引用。
- 用户指定的隔离目标为 `postgresql+asyncpg://127.0.0.1:55435/pls_v2_i4_target`，当前 revision 为 `021`；它不属于源库。

## 收口后结论（2026-07-22）

上述缺口已在 closure-fix 中关闭：三类区块现在分别查询并返回状态；SQL 异常分支先 rollback；真实 `get_db` 生命周期、失败/权限/重试测试均已通过；浏览器资产已归档至 `assets/i4-closure-fix/`。本发现记录保留为实施前基线，最终验收以 [validation.md](./validation.md) 为准。
