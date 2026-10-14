# Validation

## 方法
- 定向：`tests/test_b05_ai_canonical.py`、`tests/test_ai_governance.py`、`tests/test_ai_run_service.py`（经 scratch 守卫）。
- 全量：`pytest tests/ -q`。
- 前端：`npm run test:typecheck`。

## 证据
```text
定向：30 passed
全量：950 passed, 9 skipped, 0 failed（A04 后基线 949；+1 用例）
前端 test:typecheck：exit 0
```
A01 redress 隔离性：`test_b05_ai_canonical.py` 的不一致场景只改 `user_error_reason`（题目 id/version、revision 均匹配），故 409 只能由新增 input_hash 校验触发。

## 独立审查（另一 agent，只读）— VERDICT: PASS
- A01：重算 input_hash 与生成一致（同一函数/归一），不一致 → 409；省略 `user_error_reason` → 必 409（安全默认）；校验在建实体之前。
- A02：快照与绑定同一事务写入；含完整确认载荷；不影响 replay/`_validate_run_for_confirmation`。
- A03：`get_ai_run_for_update` 为真实 `FOR UPDATE` + 刷新，`/decision` 已使用；与 confirm 的 `_lock_run` 锁同一行。
- 契约：新增字段可选，旧客户端仅 409 不崩溃；前端类型匹配。

### Findings 处置
- **F4（MEDIUM，覆盖缺口）**：未加"decision 并发 vs confirm"的跨路径并发测试；当前仅证明加锁读取刷新。**保留为已知缺口**，未在本轮补（需 HTTP 级双会话并发，另行安排）。
- **F5（LOW/MEDIUM，规格分歧）**：DR-B02/convergence REQ 还要求 `edited` 标记与把快照放到 MistakeDraft；本设计选择放 `AiRun.creation_context`（design.md 已记录）。**明确记录：本工作流以 AiRun 放置为准**；若 convergence REQ 具约束力，`edited` 与 draft 放置需另行立项。
- **F6（LOW）**：前端对 409 显示通用错误，未提示"输入已变更，请重新生成"；`difficulty` 名义类型差异（当前不可触发 422）。记为可选 UX 改进。
- **F7（LOW）**：本文档此前未更新 → **已更新**。
- F1/F2/F3/F8：核实通过 / 非活跃竞态，无动作。

## 提交受阻说明（重要）
A01–A03 改动所落的文件**本身是未提交的 B05 功能 WIP**：`HEAD` 中不存在 `ai-confirm`、`MistakeAiConfirmRequest`、`get_ai_run_for_update`。即整个 B05 尚未入库。
因此无法把 A01–A03 从既有 WIP 中干净剥离成"单独提交"（除 `routers/ai_runs.py` 的一行替换 + 新 helper 外）。
**处置（已执行）**：先做脏文件分离（基线），把 AI 确认相关文件作为**一个**功能提交 `92ab227 feat(ai): canonical AI confirmation with trusted source (B05, A01-A03)`；其余 WIP 按域分别提交为基线（`a899fa9` 后端 / `db702ec` 前端 / `fc871d5` docs+脚本）。工作区随后 **clean**。
附带说明：`admin_mistakes.py` 等文件同时含少量非 AI 的既有编辑（如 `update_mistake`/`MistakeOut`），随该文件一并进入 `92ab227`。
