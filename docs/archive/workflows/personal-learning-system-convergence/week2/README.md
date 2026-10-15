# Week 2 — CLOSED REVIEW LOOP

执行模式 WORKER；Astra 为唯一 primary_owner 与 code_acceptor。

用户授权：PASS。2026-09-09 目标附件明确批准 PR-05→PR-06→PR-07→PR-08→Gate 的代码、隔离数据库、真实浏览器和文档工作。2026-09-12 用户再次确认本授权继续有效并下发执行指令。生产写入、stage/commit/push/merge/deploy、Week 3+、PR-24：NOT_AUTHORIZED。

## 当前证据

- 初始 dirty 工作区已保存于 `/tmp/astra-week2-20260909/baseline-status.txt`、`baseline.diff`；所有既有改动保留，重叠文件先读 diff。
- 隔离 PostgreSQL（astra 会话实例）：127.0.0.1:62466，数据库 astra_week2_main，PID 58289，data_directory `/tmp/astra-week2-20260909/pgdata`。每个数据库相关命令经 `/tmp/astra-week2-20260909/run-scratch.py` 校验名称、端口、实例 PID、data_directory 和实际 SQL 目标后执行。2026-09-12 核验：实例存活、校验全过；`astra_week2_main` 当前 revision 027。
- PR-05 迁移回放证据（2026-09-09）产生于上一会话的隔离实例 opencode :65432（`opencode_week2_20260909_replay_*` 一次性空库），日志归档 `evidence/migrations/pr05-scratch-replay.log`（10 步全过，REPLAY DONE）。2026-09-12 PR-05 收尾将在 astra 实例上重放确认可复现（见 pr-05.md）。
- `backend/tests/test_review_schema_v2.py` 的 scratch 守卫与 alembic 子进程路径原硬编码 opencode 会话环境；2026-09-12 修正为同时接受 `astra_week2_`/`opencode_week2_` 前缀并继承 wrapper 导出的 DATABASE_URL，使动态测试在授权实例上真实执行。
- 运行拓扑（T-00b 定版）：backend uvicorn :8001（8000 常驻占用）、production preview workerd :8787。
- 模型发现（2026-09-09 记录）：opencode-go/omen-alpha 可用；agy Gemini 3.8 Flash 与 3.1 Pro 可用。2026-09-12 会话实际可用 subagent 以当次派工记录为准。

## 串行状态

| PR | implementation | independent review | verification | G0/G2 | Astra acceptance |
| --- | --- | --- | --- | --- | --- |
| [PR-05](pr-05.md) | PASS（2026-09-09 实现落地；2026-09-12 修正测试 scratch 守卫与 main.py revision 钉定） | PASS（2026-09-13，ACCEPT_WITH_CONCERNS，F-1 转入 PR-06） | PASS（2026-09-12/13，六项固定命令 + 双实例空库回放） | PASS（G0 2026-09-13；G2 2026-09-13） | PASS（2026-09-13） |
| [PR-06](pr-06.md) | PASS（2026-09-20：D2 实现确认 + 9 状态机测试 + 回归 51 passed） | PASS（2026-09-20，ACCEPT_WITH_CONCERNS，无 BLOCKER） | PASS（2026-09-20，隔离 scratch + 029 单链回放） | PASS（G0 2026-09-20；G2 2026-09-20） | PASS（2026-09-20） |
| [PR-07](pr-07.md) | PASS（2026-09-20：migration 030 + 判定 service + 17 测试） | PASS（2026-09-20，ACCEPT_WITH_CONCERNS，无 BLOCKER/HIGH） | PASS（2026-09-20，030 升级/降级回放 + 后端全量） | PASS（G0 2026-09-20；G2 2026-09-20） | PASS（2026-09-20） |
| [PR-08](pr-08.md) | PASS（2026-09-20：六档+键盘+再答编排+无撤销） | PASS（2026-09-20，ACCEPT_WITH_CONCERNS，动效/人工链为记录递延） | PASS（2026-09-20，组件+全链自动化；人工 walkthrough 2026-09-21 用户完成） | PASS（G0 2026-09-20；G3 2026-09-20） | PASS（2026-09-21，人工链关闭） |

Week 2 Gate：**PASS（2026-09-21）**——自动化全链（真实 PG 持久化）+ 用户人工浏览器全链。
最终综合独立评审：**PASS（2026-09-21，真子 agent：GATE_PASS，零 BLOCKER/HIGH）**。
资源清理：**PASS（2026-09-21：三 scratch 库零连接确认后删除；:2026 dev 已关；:2025 非本轨实例未动）**。
