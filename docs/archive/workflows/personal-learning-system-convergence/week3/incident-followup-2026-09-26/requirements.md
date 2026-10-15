# 范围与验收

- 只读核对 Week 3 源码、任务和保存证据，保留历史 PASS 与当前复核状态的区别。
- 防止 pytest（包括 collection 期间）和四个活动证据脚本误连默认/受保护库；默认仅接受本地 `astra_week3_*`。
- 直接 Alembic 在线执行不再自动信任 .env；非 scratch 必须显式确认精确目标，且实际迁移仍需另行用户授权。
- 验证拒绝发生在 DBAPI/网络之前；允许本地 scratch 参数通过（mock），纯单元测试可运行。
- 不连接或改动 blog_v2/blog_db，不清理残留，不迁移，不更改应用认证/业务/schema，不 stage/commit/push/deploy。
- 当前源码测试中的普通 SQLAlchemy engine 路径是技术保护范围；raw driver、自定义 creator、归档证据脚本不属于通用防火墙保护。归档脚本仅作材料，执行须重新审查并加入口守卫。
