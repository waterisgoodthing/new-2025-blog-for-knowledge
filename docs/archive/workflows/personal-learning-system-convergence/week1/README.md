# Week 1 — TRUSTED RUNTIME（M1）执行记录

> 批准：用户于 2026-09-08 批准 Week 1（PR-01…PR-04）任务清单（tasks.md 对应 Phase）。
> 执行纪律：串行推进；每 PR 走 设计 → 开发 → 测试 → 验证 → 独立评审；状态与证据如实记录；批准不自动携带到 commit / push / migration / 部署。

## 用户决策记录（2026-09-08）

| # | 决策 | 结论 |
| --- | --- | --- |
| D-W1-1 | PR-04 验证范围 | **仅 scratch 库取证**（空库回放 + 模拟存量环境回放 + downgrade 回放）；blog_db 的 026/027 升级另行授权执行 |
| D-W1-2 | 启动 pin | PR-04 将 `main.py` `EXPECTED_ALEMBIC_REVISION` 由 `"026"` 更新为 `"027"`，LSR03 契约测试断言同步 |
| D-W1-3 | PR-02 编辑器 | 新建单一 `ContentEditor`（manage/(workspace)/notes/components/）；`useNoteEditor` 迁至 `src/hooks/`，旧路径留 re-export shim，无逻辑副本 |
| D-W1-4 | 侧边栏入口 | PR-02 在 manage 侧边栏新增"笔记写作"入口指向 `/manage/notes` |
| D-W1-5 | 技术文档 | 最终交付 `week1-technical-report.md`（本目录，中文） |

## 上次执行的现场记录（历史证据，本次接续不视为重新验证）

- **blog_db `alembic_version = 025`**：migration 026 从未应用于 blog_db（与 phase-0-evidence §2 的 scratch 回放路径无关）。42 张 public 表，含**已存在**的 `guest_messages`（8 行）与 `guest_message_bans`（历史上手工建表，非 migration 产物）。
- 因此"现有环境"语义分层：① 全新库（000→027 全链）；② 已应用 026 且 guest 表已预建的库（027 guarded no-op）；③ blog_db 实际状态（025 + guest 表在场）——第 ③ 类的 026+027 升级属生产数据操作，按 D-W1-1 另行授权。
- `:8000` 常驻 backend 为旧代码进程；当前 HEAD 代码（pin=026）对 blog_db@025 重启本就会 fail-closed 失败，属既有状况，非 Week 1 引入。

## PR 状态总览

| PR | 设计 | 开发 | 测试 | 验证 | 独立评审 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| PR-01 | [pr-01.md](pr-01.md) | PASS | PASS（15/15） | PASS（Gate 重跑 exit 0/1） | PASS | **PASS** |
| PR-02 | [pr-02.md](pr-02.md) | PASS | PASS | PASS（Chromium 19/19 + scratch 行验证） | PASS | **PASS** |
| PR-03 | [pr-03.md](pr-03.md) | PASS | PASS | PASS（Chromium 9/9） | PASS | **PASS** |
| PR-04 | [pr-04.md](pr-04.md) | PASS | PASS | PASS（scratch 双向回放 + runtime） | PASS（G2） | **PASS** |

证据文件：[pr-01.md](pr-01.md) ｜ [pr-02.md](pr-02.md) ｜ [pr-03.md](pr-03.md) ｜ [pr-04.md](pr-04.md)

## Astra 接续与完成记录（2026-09-08—09）

- 执行模式 WORKER；Astra 是唯一 primary_owner 和最终代码验收负责人。用户本次明确授权 PR-02 → PR-03 → PR-04 → Week 1 Gate 与本目录技术报告，五项决策继续有效。
- 初始 `git status --short` 未发现 PR-02 源码遗留修改；Agent 规则、runbook、package.json、PR-01 脚本和未跟踪工作流为既有改动，保留。基线记录暂存 `/tmp/astra-week1-20260908/baseline-status.txt` 与 `baseline.diff`。
- CLI 当前核实并实际使用：OpenCode 的 `opencode-go/omen-alpha` 两次未产出可用实现，改用 `opencode-go/gpt-5.6-luna` 完成限定实现；`opencode-go/qwen3.7-max` 独立复核 PR-02/03。agy 的 `gemini-3.1-pro-high` 完成 PR-02 设计审查，`gemini-3.8-flash-low` 完成 PR-04 与 Week 1 Gate 独立评审。模型输出均由 Astra 结合代码、测试和运行证据裁决。
- 本次只核实 8000 为 PID 898 常驻服务占用，未重启、未访问其数据库。上方 blog_db 版本与行数是上次记录，本次未重验。
- 使用现有 initdb/pg_ctl 建立独立临时 PostgreSQL 集群（55439），不修改共享集群角色。PR-02/03 浏览器写入只指向 `astra_week1_authoring`；PR-04 分别使用 fresh、simulated-existing、partial 三类 scratch 库完成 027 upgrade/downgrade、数据保持、fail-closed 与 Guestbook runtime 取证。
- Week 1 Gate：fresh `build:cf` PASS；workerd production preview 正向 smoke exit 0（assets 20/20，checks 23/23），失效 API 负向 smoke exit 1；前端 43 files / 395 tests PASS，backend 显式 scratch@027 为 416 passed / 7 skipped；Gemini 最终独立评审 PASS、0 blocker。
- **Week 1 Gate：PASS（2026-09-09）**；Astra 主 agent 最终代码验收：**PASS**。完整说明见 [week1-technical-report.md](week1-technical-report.md)。
- commit / push / merge / 部署 / 真实 blog_db 升级 / Week 2+：NOT_AUTHORIZED。
