# Validation — 验证策略与验收矩阵

> 状态词只有六个：`PASS / PARTIAL / FAIL / BLOCKED / NOT_VERIFIED / NOT_AUTHORIZED`。
> 禁止以"页面做出来了"作为 Done；禁止用 jsdom 作为真实浏览器行为的证明；禁止以被忽略的 type/build 错误作为健康证明。

## 1. 固定验证命令（每个 PR 必须全绿）

| 层 | 命令 | 说明 |
| --- | --- | --- |
| Frontend 类型 | `npx tsc --noEmit` | 不允许新增被忽略错误 |
| Frontend 测试 | `npm run test:typecheck`、`npm test`（vitest） | |
| Backend 测试 | `pytest`（`backend/`，需要时 `PYTHONPATH=.`） | |
| 构建 | `npm run build` | build 敏感改动必跑 |
| Migration | 空库 `alembic upgrade head` → 应用启动 → 全表存在；涉改 migration 另跑 downgrade 回放；创建新 migration 前以 `alembic heads` 确认 down_revision（D 迁移清单） | 涉 schema PR 必跑 |
| Runtime | `scripts/runtime-smoke`（D12；production 产物用 `build:cf`，F14） | PR-01 起纳入 |
| E2E | Playwright E2E-01…05 | PR-17 起纳入 |

## 2. 分层验证要求

- **TypeScript**：targeted tests + tsc + build（build 敏感时）。
- **UI**：涉及布局/交互/导航/真实浏览器行为时，提供真实浏览器证据（截图/agent-browser 流程记录）。
- **UI 目标合同**：纳入 [ui-design.md](ui-design.md) 的对应切片时，按其第 16 节验证视口、状态、动效中断/反向、reduced-motion、焦点与安全区；未纳入的切片保持 `NOT_AUTHORIZED`，不得因规范已存在而宣称实现。
- **Python**：targeted tests。
- **API 契约**：frontend client（`src/lib/api/*`）与 backend schema（`backend/app/schemas/*`）成对核对。
- **Database**：migration 图、空库隔离回放、完整性查询、rollback 证据（按风险）。
- **文档**：链接/文件存在性、内部一致性、`git diff --check`。

## 3. Week Gates（逐周阻断）

### Week 1（M1）

| 验收 | 标准 | 证据形式 |
| --- | --- | --- |
| Fresh build | PASS（production runtime 用 `build:cf` 产物，T-00b 定版拓扑） | build 日志 |
| Static assets | 100% HTTP 200 | pre-deploy smoke 输出（referenced/failed 计数）+ post-deploy smoke 记录（runbook） |
| /notes | 可读取 | 浏览器证据 |
| 新建 Note / 编辑 Note / 新建 Blog | PASS | 浏览器证据 + DB 行验证 |
| API failure | 显示 Error | 浏览器证据（断网/错误注入） |
| Retry | 可执行 | 浏览器证据 |
| Fresh DB | Guestbook tables 存在 | 空库 upgrade 日志 + `\dt` |
| Existing tests | 无回归 | 全量测试输出 |

**未通过 → 暂停进入 Review 算法整改（硬性规则）。**

**执行结果（2026-09-09）：PASS。** Fresh `build:cf`、workerd production runtime、20/20 引用资产、`/notes`、Note/Blog 新建编辑与 scratch 持久化、Error+Retry、fresh DB Guestbook、前端 395 项和 backend scratch 416 项测试均通过；失效 API 负向 smoke 按预期 exit 1。原始证据与边界见 [week1/week1-technical-report.md](week1/week1-technical-report.md)。

### Week 2（M2）

人工全链走通并核对持久化 DB 状态：

```
Question → wrong Attempt → MistakeDraft → Mistake → ReviewItem
→ re-answer(wrong) → lapse（repetitions=0, interval 短）
→ 再次到期 → correct × N → mastered（state 转换记录在 review_records）
```

状态机测试 Case A–D 全 PASS；Case D 并发提交验证乐观并发未破坏；re-answer 驱动的 ReviewRecord 抽查 `attempt_id` 可追溯（无 re-answer 的纯评分允许为空，D5）。

### Week 3（M3）

PR-09～PR-13 均须先独立验收为 PASS。Dashboard 三问（复习什么 / 练什么 / 最弱知识点）全部可答，且数据来源经 SQL 抽查确认来自 canonical entities（非 legacy Note 文本）。legacy mistake 的 create/update-type/promote/旧 UI 写入已冻结；迁移前后数量、provenance 与 visibility 映射核对一致；匿名公共 `/mistakes` 仅返回 active+public allowlist，私有字段不泄漏，无 public mistake 时为显式 Empty。Daily practice 覆盖 0/1/2/3/10/>10、weak/recent/mastered 过滤与答案隐藏。migration 032 的 UUID/INTEGER FK、Unique、关联/解除、权限负测和 downgrade/re-upgrade 均通过。完整 Gate 与证据矩阵见 [week3/README.md](week3/README.md#5-week-3-gate)。

### Week 4（M4）

OCR 分类报告 + 10 样本结果；WebAuthn 四 case（并发/过期/已消费/跨 purpose 不串用）+ operator registration 语义保持；throttling 递增延迟单测；CI 四 Job 全绿截图/日志（Job 3/4 以 T-00b 拓扑为准）。

## 4. 30 天最终验收矩阵

| 能力 | 当前（基线评估） | Day 30 目标 |
| --- | --- | --- |
| Production asset integrity | 风险 | PASS |
| Note authoring | BROKEN | PASS |
| Blog authoring | BROKEN | PASS |
| Attempt | Weak | ACTIVE |
| MistakeDraft | PASS | PASS |
| Mistake | PASS | PASS |
| Review | Partial | PASS |
| Re-answer | Missing | PASS |
| Lapse | Missing | PASS |
| Mastery | Missing | PASS |
| Note↔KP | Missing | PASS |
| KP weakness | Legacy | Canonical |
| Daily Practice | Missing | Minimal PASS |
| OCR | 0/31 | Diagnosed + usable or explicitly disabled |
| Guestbook migration | Drift | PASS |
| Vitest CI | Missing | PASS |
| Runtime Smoke | Missing | PASS |
| Critical Playwright | Missing CI | PASS |

> "当前"列来自计划评估，执行 PR-01 等验证时须以实测为准修订（如 smoke 实测 404 数）。

## 5. 证据与记录规则

- 每个 PR 在本目录或 PR 描述中记录：改动范围、验证命令输出结论、gate 结果、遗留风险。
- 完成状态与验证状态分开表述；未执行的项标记 `NOT_VERIFIED`，未获批准的项标记 `NOT_AUTHORIZED`，绝不声称未做过的验证。
- 涉学习流程的验收必须包含持久化 DB 状态证据（SQL 查询输出），UI 可见不等于已持久化。
- 无法运行或因既有原因失败的验证，如实说明失败原因并标记状态。

## 6. 阻断与止损

以下任一情况 STOP 并报告（证据、影响、选项、建议）：

- Week Gate 未通过；
- smoke 发现新的 404 资产或回归；
- migration 空库回放失败或 downgrade 不可逆；
- 公共读路由被意外私有化 / 认证边界被削弱；
- 验证发现严重回归；
- scope 扩展超出本 spec（如出现 BLOCK 清单需求）。
