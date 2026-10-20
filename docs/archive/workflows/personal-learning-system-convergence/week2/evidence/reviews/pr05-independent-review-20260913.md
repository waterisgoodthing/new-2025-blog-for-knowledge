# PR-05 独立技术评审报告

评审员：独立 subagent（principal-technical-reviewer 角色，agentId agent_90e8192f-e9ae-4c57-b72d-9a9e5326be24），只读，无实现所有权，未修改任何文件。
评审日期：2026-09-13。派工说明：前两次派工因基础设施错误（Model request failed）未产出，本次为首次有效评审。

**总体结论：ACCEPT_WITH_CONCERNS**（七项核对 5 PASS + 2 PASS with MINOR/OBSERVATION；无 BLOCKER/MAJOR）

## 逐项结论

1. D1 契约跨层一致性 — PASS（migration 028 ↔ model ↔ Pydantic ↔ TS ↔ 测试五处一致；存量 UPDATE 与默认值正确）
2. D3 契约跨层一致性 — PASS（migration 029 ↔ model ↔ schema ↔ TS ↔ 测试一致；model 仅 server_default 是正确选择）
3. migration 质量 — PASS（形状断言有效、advisory lock 正确、有损性如实处理、028↔029 链完整）
4. 与 v1 service 共存 — PASS 无违约写入；F-1 MINOR（见下）
5. 测试充分性与安全性 — PASS；F-2/F-3 OBSERVATION（见下）
6. 回放证据充分性 — PASS；F-4 MINOR、F-5 OBSERVATION（见下）
7. router/DTO — PASS；F-6 OBSERVATION（TS target_type 收窄方向安全，无需行动）

## 发现与处置（Astra，code_acceptor）

| 编号 | 严重度 | 位置 | 问题 | 处置 |
| --- | --- | --- | --- | --- |
| F-1 | MINOR | review_item_service.py:11,40；028:111；review_item.py:23 | 窗口期行标 v2 实为 v1 调度；v1 失败虚增 repetitions 破坏 D2 streak 不变量，PR-06 后 mastery 可能提前误触发 | **转入 PR-06 必办项**：显式书面处置（重推导或接受偏差），见 pr-06.md |
| F-4 | MINOR | astra 回放日志 evidence note | "42 passed" 计数表述（实为两文件合计 35+7） | 已核实 35+7=42；说明已补记入回放日志；完整命令行在 evidence/tests/pr05-backend-targeted-20260912.log |
| F-2 | OBSERVATION | test_review_schema_v2.py:509 | assertRaises(Exception) 过宽 | **已修复**：收窄为 IntegrityError（sqlalchemy.exc），模块重跑 35 passed |
| F-3 | OBSERVATION | test_review_schema_v2.py 清理注册 | 中途失败遗留降级 head 与脏数据（仅 scratch） | 接受现状：动态测试开头 upgrade head 自愈；不阻塞 |
| F-5 | OBSERVATION | astra 回放日志 [4] | 降级列删除缺直接查询证据 | 接受：pytest 动态断言 + opencode 日志 [8] pg_attribute 核验已充分 |
| F-6 | OBSERVATION | review-items.ts:7 | TS target_type 窄于 Pydantic str | 无需行动（收窄方向安全） |

## 声明（评审员原文）

本次评审为只读独立评审，评审员无实现所有权，未修改、未暂存任何文件；评审范围仅限指定文件与两份回放日志，未做仓库全量扫描。
