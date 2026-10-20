# 全 Week 审计修复方案

> 原计划续接（2026-10-09）：当前建议已在 [合并路线](../../ROADMAP.md)逐项映射原需求/PR、B返工与A/N问题；[当前状态](../../PROJECT_STATUS.md)区分历史验收和现版本。下文保留当期记录，不恢复历史实施授权。

> 文档治理（2026-10-09）：历史阶段账本保留，不把原 PASS/FAIL/未实施覆盖为本轮状态。当前见 PROJECT_STATUS；R 旧候选之后已有 B 本地返工 PARTIAL；UI V2 为独立组件轨，尚非主业务路由集成。 当前入口见 [文档索引](../../DOCUMENTATION_INDEX.md)。

日期：2026-09-27。状态：方案文档 PASS。R00–R07 本地实现与隔离验证已执行（见文末「实施结果」）；本地回归 PASS，远端 CI、真实 OCR provider、生产迁移/发布仍 **NOT_VERIFIED / NOT_AUTHORIZED**。

目标：先修复现有合法输入和学习事实传递，关闭 F01–F05、D06、D12，再补核心体验与工程债。依据 [质量审计](../../../Personal_Learning_System_Week_Completion_Quality_Audit.md)，不将测试数量或完成度百分比作为放行条件。

本次授权仅为制定方案。采用 WORKER：主 Agent 为 primary_owner、文档作者和最终验收人；独立 plan_review 只读检查。实际写入仅本目录；原报告、产品源码、既有脏文件不改。未运行数据库迁移、真实 provider、远端 CI，也未提交、推送或部署。

## 现状与推荐顺序

HEAD：`4a954eaa92952fcc5a6b18a2e15d2e824b094e41`，工作树有大量跨周未提交改动；HEAD 不能代表当前实现。`baseline-files.json` 记录本次写方案前的 tracked/untracked 非忽略文件 SHA-256；仅作本地身份核对，不含文件正文，不是发布清单或备份。

本轮源码复核支持：多选 UI 仍覆盖单值、自动错答草稿未传 KP、suggestions 修改未调用 freeze guard、schema ownership 缺口及 AiRun helper 未接生产确认入口。报告的运行计数属于该审计的已有证据，本轮未重跑。9 月 26 日的 CI 库名、CLI loop、latest challenge、E2E 外壳结论已被新报告替代，不列为当前待修缺陷，但保留回归。

建议串行执行：

`R00 合同/基线 → R01 多选 → R02 KP传递 → R03 完整冻结 → R04 schema authority → R05 AI追踪 → R06 OCR入口决策 → R07 综合验收`

R04 是任何新增迁移生成/执行的前置；若前面步骤发现必须改 schema，先停下并提前完成 R04，不能绕过。每步达到退出条件、记录独立复核后进入下一步。D12 穿链测试随各项修复落地，不等最后再补。

## 交付导航

- [需求与缺陷映射](requirements.md)：本轮必须关闭、后续改进及不包含范围。
- [设计与数据合同](design.md)：推荐解法、兼容、失败和回退策略。
- [串行任务与门禁](tasks.md)：修改候选、依赖、验收、角色与授权。
- [验证方案与本轮检查](validation.md)：反例、持久化断言、证据和验收状态。

完成第一阶段只代表修复候选可验收。远端 CI 必须对应同一提交/构建，生产还需要目标环境、迁移/恢复与发布批准。不得用本地通过替代这些证据。

## 实施结果（本地隔离，2026-09-27）

顺序 `R00→R07` 已按计划执行。R04 先于 R05 的任何 schema 触碰完成；本轮未新增迁移（纯 metadata 对齐 + 精确 SQL-owner allowlist）。

| 步骤 | 结果 | 关键证据 |
|---|---|---|
| R00 | PASS | `baseline-files.json` 2872 项复算：0 缺失、27 项变化，全部为本轮有意修改的新增文件（见 diff） |
| R01 | PASS | 多选集合 UI + 编辑清除旧评分；`review-queue.test.tsx` 新增 2 例，前端 525 passed |
| R02 | PASS | 自动草稿继承 Question KP 快照；`test_attempt_service.py` 4 passed（含 attempt→draft→mistake KP） |
| R03 | PASS | suggestions/folders/tags/Note↔KP 冻结 + 批量预检；`test_f03_freeze_coverage.py` 1 passed（真实 ASGI+PG） |
| R04 | PASS | SQL-owner manifest + 033 索引入模型；`alembic check` 在新/旧库均「No new upgrade operations detected」，`test_f04_schema_ownership.py` 4 passed（含删索引反例） |
| R05 | PASS | gateway `run_id` + `bind_run_to_entity` + canonical MistakeDraft 保存 `source_run_id`；`test_ai_governance.py` 20 passed |
| R06 | PASS（禁用策略） | 自动 OCR 默认关闭（服务端 fail-closed + UI 隐藏识别按钮 + 手工路径），真实 provider 评估 **NOT_VERIFIED** |
| R07 | PASS（本地） | 后端 940 passed/9 skipped（fresh `astra_week4_r00r07_full`）；前端 `tsc`/`test:typecheck`/`npm test`/`build`/`build:cf` 全 0；D12 穿链见 validation.md |

未执行且未授权：远端 CI、真实 provider 外发、历史/生产回填、生产迁移、commit/push/部署。这些不得由本地结果替代。
