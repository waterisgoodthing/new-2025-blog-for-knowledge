# I4 closure-fix 收口计划

## 目标

在不进入 I5 的前提下，补齐 I4 的最后四类证据与实现风险：Dashboard 各区块的独立查询/失败/empty 状态、SQL 异常后的事务回滚、真实 FastAPI dependency 生命周期，以及三种尺寸与键盘导航的可复核资产。

## 严格范围

- 影响架构线：`backend/` Dashboard 路由、服务与数据库依赖；`src/` 管理首页/导航测试与必要展示契约；本 workflow 的 `assets/`、`validation.md`、`README.md`、`tasks.md`、`incremental-plan.md`。
- 允许修改：Dashboard summary DTO/查询服务/路由、`get_db` 生命周期测试、Dashboard 前端状态与测试、导航证据采集。
- 不允许：I5 的资料/品牌/时区/偏好设置，新的领域模型、迁移、生产部署、源库写入、权威切换、旧系统停写、真实 AI 调用。

## 退出门槛

1. `learning`、`activity`、`storage` 能分别返回 ready、unavailable/unknown 或 empty，不以全局零值伪装失败。
2. 路由捕获 SQL 异常前显式 rollback；同一 dependency 生命周期中的后续查询可继续执行。
3. 使用真实 `get_db` dependency 的 TestClient/异步测试覆盖 commit、rollback、close 和异常后恢复，而非仅检查函数文本。
4. 测试覆盖 learning unavailable、activity unavailable、storage unknown、匿名 401、失效会话和 Dashboard 重试。
5. `assets/i4-closure-fix/` 保存 390×844、1280×800、1440×900 及键盘导航证据，validation 逐项链接。
6. 残余风险与 I4 归档决定已记录；I4 才可标记 `COMPLETE / PASS`，I5 仍保持单独审批。

## 收口结果（2026-07-22）

用户已批准 CF-01 至 CF-06，全部退出门槛通过，I4 已归档为 `COMPLETE / PASS`。本轮没有新增迁移、部署、源库写入或真实 AI 调用；`pls_v2_i4_target` 仅作为隔离验证目标继续保留。

残余风险：区块级降级当前针对 SQLAlchemy 异常，外部存储提供方或未来非数据库依赖异常仍需在对应增量单独建模；Dashboard 仍在一次请求内顺序执行多个查询，但每个区块已有独立状态，不再以全局零值伪装失败。当前仍是单管理员本地验证边界。

归档决定：冻结本 closure-fix 文档、测试与 `assets/i4-closure-fix/` 证据；I5 的资料/偏好/响应式产品化必须另建或复用经批准的任务清单，不能从本轮 PASS 自动推进。
