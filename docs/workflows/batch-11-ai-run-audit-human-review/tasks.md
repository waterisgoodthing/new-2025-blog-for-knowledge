# Tasks：Batch 11 AI Run 审计与人工流转

> 状态：**全部完成，用户验收通过并关闭**
>
> 关联：[requirements.md](./requirements.md) · [design.md](./design.md)
>
> 执行规则：批准后严格按编号执行；每完成一项立即更新 checkbox。不得进入 Batch 12。

## 批准硬约束

1. `ai_runs` 是业务审计记录，`ai_call_logs` 是技术调用日志，保持双轨。
2. 不删除、rename、drop 或重建 `ai_call_logs`。
3. AI 输出与人工接受均不得直接写正式 Question、Mistake 或 Review Item。
4. 人工接受最多进入 draft/staged artifact，本批只记录决定，不自动 apply。
5. 决策使用 revision 并发控制，冲突返回 409。
6. 列表 DTO 不含完整 output、replay input、敏感原文或 storage key。
7. 详情 DTO 只返回受控 output，不返回凭据、绝对路径、storage key 或完整敏感输入。
8. Retry 不从 input summary 猜测输入；无 replay input 返回 409。
9. Gateway 方法签名与旧 AI endpoint response schema 保持兼容。
10. stream 生命周期缺口单独记录，不宣称完整流式审计。
11. 旧 call-log endpoint/table 仅兼容保留，不删除。
12. 不新增 Prompt 后台、A/B、热更新、成本统计或多供应商路由。
13. 不改变公开 API，不向匿名用户暴露 Run。
14. mock 测试不得表述为真实 provider 端到端验证。

## P0-01 实施前合同审计

任务编号：P0-01
任务名称：冻结现行 Gateway、validator、call-log 与 API 合同
优先级：P0
来源需求：R1、R3、N3
涉及文件：本 workflow 的 `audit.md`，只读检查现有实现
修改内容：记录现行 schema、端点、权限、日志字段、stream 缺口和兼容约束。
完成标准：明确哪些调用接入 Run、哪些旧端点保留、哪些数据禁止持久化。
验证方式：源码和 migration 证据表。
风险说明：若发现现行实现与本设计冲突且会扩大范围，先更新设计/tasks 并重新审批。

- [x] 完成 P0-01。现行合同、双轨边界、stream 缺口、敏感数据禁区与 14 条批准约束已冻结在 `audit.md`。

## P0-02 AiRun 模型与 migration

任务编号：P0-02
任务名称：建立最小 AI Run 持久化
优先级：P0
来源需求：R2、R3
涉及文件：model、models init、Alembic migration、model/migration tests
修改内容：创建 `ai_runs`、约束和索引；安全复制历史 call logs；保留旧表。
完成标准：upgrade/downgrade 可执行，历史映射符合设计，不新增 Batch 12 字段。
验证方式：Alembic 与数据库结构测试。
风险说明：不得 drop/rename `ai_call_logs`，不得存储完整敏感输入。

- [x] 完成 P0-02。新增独立 `ai_runs` 模型与 018 migration；未读取、修改或重建 `ai_call_logs`；模型测试 2 passed，Alembic head 为 018。

## P0-03 Run schema 与安全 DTO

任务编号：P0-03
任务名称：定义列表、详情、重试和决策合同
优先级：P0
来源需求：R4、R5、R6、N1
涉及文件：`backend/app/schemas/ai_run.py`、schema tests
修改内容：列表不含 output/replay input；详情含受控 output；请求定义 revision 与 note 长度。
完成标准：敏感字段不会进入列表 DTO，枚举和非法输入有测试。
验证方式：Pydantic 单元测试。
风险说明：不得改变现有 AI 业务 endpoint response schema。

- [x] 完成 P0-03。新增列表/详情/决策 DTO；列表排除 output/replay/input summary，详情递归清理凭据、绝对路径、data URL 与 storage key；schema 测试 3 passed。

## P0-04 Run lifecycle service

任务编号：P0-04
任务名称：创建、完成、失败与查询生命周期
优先级：P0
来源需求：R1、R2、N2
涉及文件：`backend/app/services/ai_run_service.py`、service tests
修改内容：实现状态转换、validation、错误安全化、输入 allowlist 与输出记录。
完成标准：成功、失败、异常、非法转换和敏感输入拒绝均有测试。
验证方式：service 单元/数据库测试。
风险说明：审计写入失败不能伪造成功状态。

- [x] 完成 P0-04。实现 start/complete/fail 生命周期、replay allowlist 与 output 清理；非法重复转换被拒绝，service 测试 4 passed。

## P0-05 Gateway 接入 Run 生命周期

任务编号：P0-05
任务名称：AI Gateway 运行记录接入
优先级：P0
来源需求：R1、R3、N3
涉及文件：`ai_gateway.py`、调用适配层、现有 Gateway tests
修改内容：调用前 start，结束 complete/fail；保持四个 Gateway 方法和外部 API response 兼容。
完成标准：已接入调用均产生 Run；原 Gateway 与 AI endpoint 回归通过。
验证方式：Gateway/endpoint 测试，不调用真实 provider。
风险说明：stream 生命周期缺口需单独测试；不能靠双写长期掩盖迁移问题。

- [x] 完成 P0-05。四个 Gateway 方法签名保持不变，注册任务独立写业务 Run 且继续写技术 call log；Gateway 测试 12 passed。真实 stream endpoint 缺口已单独记录，未宣称完整流式审计。

## P0-06 重试链

任务编号：P0-06
任务名称：安全重试与父子 Run 链
优先级：P0
来源需求：R5
涉及文件：run service、router、tests
修改内容：校验 replay input、创建新 attempt、保持父 Run 不变、处理重复请求。
完成标准：新 ID、parent、attempt、409 缺输入路径均有测试。
验证方式：service/API 测试。
风险说明：不得从 input summary 猜测可重放输入。

- [x] 完成 P0-06。retry 仅复制安全 `replay_input` 创建新 child/attempt，父 Run 不变；无 replay 或 running 状态抛冲突，service 测试 6 passed。

## P0-07 人工接受/拒绝

任务编号：P0-07
任务名称：带 revision 的人工决策与审计
优先级：P0
来源需求：R6、N2
涉及文件：run service、audit service 调用、API tests
修改内容：pending -> accepted/rejected；同决定幂等；冲突 409；写 `audit_logs`。
完成标准：接受、拒绝、重复、冲突、非法状态、未认证均有测试。
验证方式：service/API/audit 测试。
风险说明：接受动作不得调用正式实体写入 service。

- [x] 完成 P0-07。人工接受/拒绝使用 revision、同决定幂等、相反决定与过期 revision 冲突；审计只记录状态/revision/note_present，不含 output/note 正文；service 测试 8 passed。

## P1-01 Admin Run API

任务编号：P1-01
任务名称：私有 Run 列表与详情 API
优先级：P1
来源需求：R4
涉及文件：`backend/app/routers/ai_runs.py`、`backend/main.py`、API tests
修改内容：新增 canonical admin API；筛选、分页、404、权限和 DTO 分层。
完成标准：列表/详情合同与权限测试通过。
验证方式：route tests。
风险说明：不得向公开 API 或匿名用户泄露 Run。

- [x] 完成 P1-01。新增 `/api/admin/ai/runs` 列表、详情、retry、decision 私有路由，列表/详情 DTO 分层并统一 404/409；route/schema/service 组合测试 14 passed，匿名请求 401。

## P1-02 前端 API 与管理页

任务编号：P1-02
任务名称：Run 列表、详情、重试与决策界面
优先级：P1
来源需求：R7
涉及文件：`src/lib/api/ai-runs.ts`、`/manage/ai` route components/hooks
修改内容：接入新 API，展示 lifecycle/validation/review，提供受控操作和状态反馈。
完成标准：空/错/加载/冲突状态完整；接受提示不直接写正式内容；可访问性合格。
验证方式：TSC、build、浏览器验收。
风险说明：不得把完整 output 放入列表请求或公开页面。

- [x] 完成 P1-02。`/manage/ai` 新增业务 Run 列表/详情/筛选/retry/decision，明确接受不写正式实体；技术 call-log 区域保留，前端 DTO 不含 replay input，`npx tsc --noEmit` 通过。

## P1-03 旧 call-log 兼容

任务编号：P1-03
任务名称：冻结或适配旧日志端点
优先级：P1
来源需求：R3
涉及文件：旧 API/service/tests、兼容说明
修改内容：基于 P0-01 决定保持历史冻结或映射新 Run；用合同测试证明旧响应不变。
完成标准：现有管理客户端迁移后，旧端点不再是新事实源；旧合同不被静默破坏。
验证方式：API contract tests。
风险说明：不在本批删除旧端点或旧表。

- [x] 完成 P1-03。兼容测试固定 `ai_runs`/`ai_call_logs` 双表、旧 call-log 端点与响应字段；018 无 drop/rename 旧表，兼容与 route 测试 6 passed。

## P1-04 全量验证

任务编号：P1-04
任务名称：Batch 11 综合验收
优先级：P1
来源需求：N1–N4
涉及文件：`validation.md`、`assets/`（如有截图）
修改内容：运行 migration、pytest、TSC、build、浏览器、权限和禁止项检查。
完成标准：关键结论均有命令/截图/响应证据；失败转入 audit 风险。
验证方式：

```text
PYTHONPATH=. .venv/bin/alembic upgrade head
PYTHONPATH=. .venv/bin/alembic downgrade -1
PYTHONPATH=. .venv/bin/alembic upgrade head
.venv/bin/python -m pytest tests/ -ra
npx tsc --noEmit
npm run build
git diff --check
```

风险说明：不以 build 代替权限、数据库和浏览器验收。

- [x] 完成 P1-04。Alembic 往返与 head、207 项 pytest、TSC、build、diff、匿名权限和禁止项检查通过；已登录 UI、真实 provider 与真实 stream 完整性明确记为未验证风险。

## P1-05 文档收口

任务编号：P1-05
任务名称：验收、风险与移交收口
优先级：P1
来源需求：仓库 workflow 规则
涉及文件：README、tasks、validation、audit、handoff-prompt（需要时）
修改内容：更新状态、证据、偏差、回滚与下一轮边界。
完成标准：所有完成声明可追溯；未解决项有风险归属；明确不自动进入 Batch 12。
验证方式：交叉链接和 checkbox 核对。
风险说明：不得把 mock 验证写成真实 provider 端到端通过。

- [x] 完成 P1-05。README、validation、audit 与 handoff 已收口；用户确认三项未验证风险不阻塞验收，Batch 11 已通过并关闭，未进入 Batch 12。

## 执行顺序

```text
P0-01 -> P0-02 -> P0-03 -> P0-04 -> P0-05 -> P0-06 -> P0-07
      -> P1-01 -> P1-02 -> P1-03 -> P1-04 -> P1-05
```

## 关闭后补证

### P1-06 RISK-B11-004 真实 provider 端到端补证

任务编号：P1-06
任务名称：受控真实同步 provider 双轨落库审计
优先级：P1
来源需求：RISK-B11-004、用户 2026-07-06 补证指令
涉及文件：`README.md`、`tasks.md`、`validation.md`、`audit.md`
修改内容：使用无个人数据的最小同步任务调用真实 provider，并核对同一时间窗内
`ai_runs` 与 `ai_call_logs` 的新增记录和公共元数据。
完成标准：单次真实调用新增一个 Run 和一个 call log；两者 task、provider、model、
Prompt 版本、延迟与成功状态一致；不记录密钥或模型正文。
验证方式：真实 Gateway 调用前后计数差、唯一 input marker 查询、数据库元数据交叉核对。
风险说明：只补证同步 Gateway 双轨落库；不验证 SSE，不进入 Batch 12。

- [x] 完成 P1-06。受控 `netease_reason` 真实调用经 DeepSeek 尝试后 fallback 到
  `qwen_general/qwen3.7-plus` 成功；新增 1 个 Run 与 1 个 call log，公共元数据一致，
  RISK-B11-004 已关闭。
