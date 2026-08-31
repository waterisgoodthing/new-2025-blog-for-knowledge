# I11 影子迁移与切换

状态：`E-05 PASS / E-06 PASS / I11-04 PASS / FINAL AUTHORITY blog_v2`。

用户于 2026-07-31 要求继续推进。I10 owner gate 已通过，但仓库不存在可执行的
shadow/delta/tombstone 工具，且 2026-07-29 曾批准单一 source 简化路径。新版
E-05 计划把这项历史简化决策视为有限反转；用户已明确批准
[tasks.md](./tasks.md) I11-02A 至 I11-02H。

I11-02A 至 I11-02H 已完成：source `blog_db` 全程保持只读，一次性 shadow
完成 123-row ledger/delta 对账、单 owner 与关系完整性复核、幂等重放、基础
schema 回滚和可验证销毁。2026-08-01 用户已正式批准 E-06 的最小 live 写入、
停写、切换、观察、reverse delta、回切与只读归档；部署和推送仍不授权。

文档：[audit](./audit.md) ·
[design](./design.md) · [requirements](./requirements.md) ·
[tasks](./tasks.md) · [validation](./validation.md) ·
[risk-register](./risk-register.md) · [next-requirements](./next-requirements.md)
