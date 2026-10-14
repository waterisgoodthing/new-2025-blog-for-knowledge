# Tasks — PR 切分与串行执行计划

> 原计划续接（2026-10-09）：当前建议已在 [合并路线](../../ROADMAP.md)逐项映射原需求/PR、B返工与A/N问题；[当前状态](../../PROJECT_STATUS.md)区分历史验收和现版本。下文保留当期记录，不恢复历史实施授权。

> 文档治理（2026-10-09）：历史阶段账本保留，不把原 PASS/FAIL/未实施覆盖为本轮状态。当前见 PROJECT_STATUS；R 旧候选之后已有 B 本地返工 PARTIAL；UI V2 为独立组件轨，尚非主业务路由集成。 当前入口见 [文档索引](../../DOCUMENTATION_INDEX.md)。

> 每个 PR：one concern + tests + migration（如需）+ acceptance criteria。
> 执行纪律：串行推进；每个 Phase（周）开工前需用户对该 Phase 的任务清单**单独批准**；批准不跨阶段传递。任何 HIGH gate 未满足即 STOP 并报告（AGENTS.md 止损条件）。

## Phase 0 — 工程 Gate（Day 1，不开发产品功能）

| 任务 | 内容 | 风险 | 状态（2026-09-04 实测） |
| --- | --- | --- | --- |
| T-00 | 固定命令基线并实测记录当前状态：`npx tsc --noEmit`、`npm run test:typecheck`、`npm test`、`pytest`、`npm run build`、`alembic upgrade head`（空库） | LOW | **PASS**（5 项 PASS；空库 alembic = PARTIAL：migration 026 在 PG15+ 全新库需两项集群前置，已定因并定版 CI superuser 契约，见 [phase-0-evidence.md](phase-0-evidence.md) §2） |
| T-00b | 定版 runtime/CI 契约并留证据（D12/D13）：`build:cf` 产物的本地 production 启动方式与端口；backend 启动命令 + PostgreSQL + `alembic upgrade head` 时点；环境变量集（无真实 secrets）；smoke health 探针（`/api/health`）；seed fixture（≥1 note、≥1 public mistake）；post-deploy smoke 写入发布 runbook | MEDIUM | **PASS**（preview=workerd :8787；backend=uvicorn :8001（8000 常驻占用）；upgrade 先于启动（main.py lifespan 校验 026）；seed=1 note + 1 legacy mistake 实测可读；post-deploy smoke 已入 [runbook](../../public-deploy-runbook.md)，见 [phase-0-evidence.md](phase-0-evidence.md) §3） |

**Gate**：命令清单全部可执行并记录基线结果（PASS/FAIL 如实）；T-00b 拓扑定版是 PR-01 与 CI Job 3/4 的前置条件。→ **Phase 0 Gate：PASS（2026-09-04）**。

## Week 1 — TRUSTED RUNTIME（M1）

| PR | 需求 | Scope | 风险 | 关键 gate |
| --- | --- | --- | --- | --- |
| PR-01 | R31 | runtime smoke 脚本（D12，依赖 T-00b 拓扑）+ pre-deploy 本地验证报告 + post-deploy smoke 纳入发布 runbook | MEDIUM | smoke 可阻断发布；拿到当前 404 实测数据 |
| PR-02 | R03 | `/manage/notes{,/new,[slug]}` 路由 + ContentEditor 接入（D10；slug 标识，不改 API）；UI 按 [ui-design.md](ui-design.md) §8 Authoring 切片（构图/保存状态/属性/发布确认） | MEDIUM | 新建/编辑 Note、Blog 手动流程 PASS；UI 证据按 §16 |
| PR-03 | R03b | `AsyncStatePanel`（D11）+ `/notes`、Dashboard 主要面板 loading/empty/error/retry；含 [ui-design.md](ui-design.md) §13 异步状态 + Foundation 子集（reduced-motion、焦点） | LOW | API 失败显示 Error 且 Retry 可执行 |
| PR-04 | R32 | guestbook Alembic migration（执行序 027） | HIGH | 空库 upgrade → 表存在；现有环境不回归 |

**Week 1 Gate**（requirements.md 表格）：Fresh build / assets 100% 200 / /notes 可读 / Note·Blog 新建编辑 / Error+Retry / Fresh DB Guestbook / tests 无回归。**未通过 → 停止，不进入 Week 2。**

**执行结果（2026-09-09）**：PR-01、PR-02、PR-03、PR-04 与 Week 1 Gate 均为 **PASS**；证据见 [week1/README.md](week1/README.md) 与 [week1/week1-technical-report.md](week1/week1-technical-report.md)。该结果不授权或表示 Week 2 已开始。

## Week 2 — CLOSED REVIEW LOOP（M2）

| PR | 需求 | Scope | 风险 | 关键 gate |
| --- | --- | --- | --- | --- |
| PR-05 | R01 | migration 028/029 + model/schema 同步：state 枚举、algorithm v2（含存量 UPDATE）、`last_rating`、ReviewRecord state 记录（D1/D2/D3） | HIGH | 空库回放；现有 review tests 无回归 |
| PR-06 | R01 | 调度语义 v2（D2 定版表）：lapse reset、成功阶梯、mastery 触发；Case A–D 状态机测试 | HIGH | Case A–D 全 PASS（含并发 Case D） |
| PR-07 | R02 | Re-answer API：判定 service（D5）+ migration 030（`attempts.context_type` + `review_records.attempt_id`）+ schema/router/client 同步 | HIGH | 自动/半自动/人工三档判定有测试；attempt 归属验证有测试；DTO 跨层一致 |
| PR-08 | R02 | Re-answer UI：Review 页 `Mistake → Re-answer → Evaluation → Recommendation → Confirm → ReviewRecord`；UI 按 [ui-design.md](ui-design.md) §7 Review 切片（六档评分 0–5、动效编排）；撤销 API 契约批准前**只显示普通成功 Toast，不出现"撤销"控件**（不设虚假操作入口）；真实撤销 NOT_AUTHORIZED（见 UI 切片表） | MEDIUM | Week 2 Gate 人工全链走通；六档评分不丢失业务值 |

**Week 2 Gate**（最重要验收流程）：

```
Question → wrong Attempt → MistakeDraft → Mistake → ReviewItem
→ re-answer(wrong) → lapse → 再次到期 → correct × N → mastered
```

须实际持久化 DB 状态验证（非仅 UI 可见）。

## Week 3 — CANONICAL LEARNING（M3）

计划状态：`IMPLEMENTATION_DONE / WEEK3_GATE_PASS`（2026-09-22，用户裁决；详见 [week3/TRACKING.md](week3/TRACKING.md) 与 [week3/week3-technical-report.md](week3/week3-technical-report.md)）。为满足真实依赖与逐项验收，执行顺序为 **W3-00 → PR-09 → PR-10 → PR-12 → PR-13 → PR-11 → Week 3 Gate**；PR 编号不变。

| PR | 需求 | Scope | 风险 | 关键 gate |
| --- | --- | --- | --- | --- |
| PR-09 | R04 | legacy mistake 写入冻结 + migration 031（visibility CHECK 替换）+ admin 发布入口 + 公共 `/mistakes` read cutover（D6）+ 基于现有 ledger 的可审计迁移 runner（执行时动态盘点，映射规则定版） | HIGH | 迁移前后数量与 visibility 映射核对；公共读按 active+public 过滤；无 public 时显式 Empty；legacy 读兼容保留 |
| PR-10 | R05 | KP analytics service + 四指标/派生/weakness 排序（D7）+ 只读端点 | MEDIUM | 指标单测含除零样本 |
| PR-11 | R05b | Dashboard 第一版：今日复习/练习、薄弱 Top3、最近掌握 4 个；UI 按 [ui-design.md](ui-design.md) §6.1 `今日先做`（仅确定性 fallback，AI 推荐 NOT_AUTHORIZED） | MEDIUM | 数据全部来自 canonical entities |
| PR-12 | R06 | `note_knowledge_points`（migration 032）+ 关联/解除 API（D8） | HIGH | Unique 冲突拒绝；fresh DB 回放 |
| PR-13 | R09 | `GET /api/admin/practice/today` 选题管线（D9；候选不足时实际数量 + Empty） | MEDIUM | 充足样本 3–10、不足样本实际数量 + Empty；weak 优先；mastered 排除有测试 |

**Week 3 Gate**：PR-09～PR-13 各自验收均为 PASS；Dashboard 真实回答三问（复习什么 / 练什么 / 最弱知识点）且来源为 canonical；公共 `/mistakes` 仅暴露 active+public allowlist；legacy 写入已冻结；Note↔KP 的 migration 032、关联/解除、Unique/FK 与权限负测全部通过。完整矩阵见 [week3/README.md](week3/README.md#5-week-3-gate)。

## Week 4 — RELEASE GATE（M4）

| PR | 需求 | Scope | 风险 | 关键 gate |
| --- | --- | --- | --- | --- |
| PR-14 | R10 | OCR 失败分类诊断 + 10 受控样本报告 + 入口可见性处置（D16）；UI 按 [ui-design.md](ui-design.md) §9 **仅限失败可见/重试/入口处置**；§9.3 候选确认与类型推荐属产品功能扩展，拆候选 PR-22（见 UI 切片表） | MEDIUM | 分类报告 + ≥8/10 或显式禁用；失败 UI 可见可重试可诊断 |
| PR-15 | R33 | `webauthn_challenges`（migration 033）+ generate/store/verify/consume（D14；覆盖三类 ceremony 含 operator registration） | HIGH | 并发/过期/已消费/跨 purpose 四 case 测试；operator registration 语义保持 |
| PR-19 | R11 | polish 分类决策记录（D17）+ 产出持久化数据调用点的 AiRun `target_type/target_id` 纪律 | MEDIUM | 分类决策在案；创建型"确认后回填"口径抽查 |
| PR-16 | R34 | login throttling（D15）+ 配置项 + 单测 | HIGH | 递增延迟可观测；配置可调 |
| PR-17 | R22 | CI 四 Job（D13）+ Playwright E2E-01…05（workers=1） | MEDIUM | 四 Job 全绿 |
| PR-18 | Legacy | 按证据删除候选（旧 review client / SM-2 caller / WIP components / broken tests / duplicate surfaces / unused endpoints） | MEDIUM | 每项删除三证据（grep/tests/logs）记录 |

**Week 4 Gate**：M4 达成 = OCR 已知、Auth 加固、AI target 纪律（PR-19）落地、CI 完整、E2E 完整、legacy 收缩。

## UI 规范切片整合（[ui-design.md](ui-design.md) §17）

> 原则：UI 规范是目标态合同，**不扩大已批准范围**（requirements.md 首注）。
> **阻塞规则**：已纳入 PR 的 UI 切片，其验收失败**必须阻塞该 PR**，并因此阻塞所属周 Gate（Week 1 的 Error/Retry、写作流程等 gate 本身含 UI 验收）；**候选 PR-20～26 不阻塞 Week 1–4 Gate**——它们只有在独立批准后才形成实施任务。
> 2026-09-22 状态更新：Week 1 与 Week 2 Gate 已完成验收；Authoring、Foundation 和 Review 对应子集为 `PASS`。Week 3 实现、Week 4+ 与候选切片仍为 `NOT_AUTHORIZED`。此前 `NOT_VERIFIED` 或未批准措辞属于当时的历史状态。

| 切片（ui-design §17） | 计划归属 | 授权状态（当前） | 解除条件 |
| --- | --- | --- | --- |
| Foundation（token/异步状态/焦点/reduced-motion 子集） | 随 PR-03 及各 PR 触及页面顺带应用；不发起全局设计系统重写（BLOCK 清单） | PASS | Week 1 PR-03 子集已验证；其他 PR 随各自批准生效 |
| Authoring（§8：ContentEditor/保存状态/属性/发布确认） | PR-02 | PASS | Week 1 + PR-02 已验证 |
| Review（§7：Re-answer 编排、六档评分 0–5） | PR-08 | PASS | Week 2 + PR-08 已验证；**真实撤销无随 PR 解除路径**——需撤销 API 契约任务立项并批准（§18），此前仅普通成功 Toast、无撤销控件 |
| Today（§6.1 `今日先做` 确定性 fallback） | PR-11 | PASS | Week 3 + PR-11 已验证；**每日 AI 推荐无随 PR 解除路径**——需 UTC+8 幂等契约 + R11 治理另行批准（§18） |
| Authentication（§5：会话查询、登录模块、成功展开） | 候选 PR-20 | NOT_AUTHORIZED | PR-20 单独立项批准；不改认证语义（§5.1） |
| Capture 失败状态 UI（§9.1/9.4：失败可见/重试/入口处置） | PR-14 | NOT_AUTHORIZED | Week 4 + PR-14 批准；"后台继续"另需 NOT_VERIFIED 项定版（§18） |
| Capture 候选确认（§9.3：多字段候选、类型推荐） | 候选 PR-22 | NOT_AUTHORIZED | R10 gate 通过后单独立项批准；属产品功能扩展，不属 R10"先诊断"范围 |
| Today 工作台（模块库、本地布局保存） | 候选 PR-21 | NOT_AUTHORIZED | PR-21 单独立项批准；跨设备同步见下行 |
| Account Sync（§4.2–4.3 跨设备同步） | PR-23 路线占位 | NOT_AUTHORIZED | PR-21 后定版 layout revision + 冲突 API，再单独批准 |
| Review Undo（§7.4 ReviewRecord 真实撤销） | PR-24 路线占位 | NOT_AUTHORIZED | PR-08 后定版撤销 API + 审计语义，再单独批准 |
| Daily AI（§6.1 每日推荐生成） | PR-25 路线占位 | NOT_AUTHORIZED | PR-11/13/19 后定版 UTC+8 幂等、缓存和 fallback，再单独批准 |
| Capture Background（§9 OCR 离开页面继续运行） | PR-26 路线占位 | NOT_AUTHORIZED | PR-14 后定版任务状态和生命周期 API，再单独批准 |

## UI 设计路线（独立于 M1–M4 Gate）

UI 路线与核心工程路线共享后端前置，但不改变周 Gate。每个候选只有在前置满足并获得独立批准后才可实施；路线占位不等于实现授权。

| 顺序 | UI 切片 | 承载项 | 依赖 | 当前状态 |
| --- | --- | --- | --- | --- |
| UI-01 | Authoring：ContentEditor、保存状态、属性、发布确认 | PR-02 | Week 1 | PASS |
| UI-02 | Foundation：异步状态、焦点、Overlay、reduced-motion 子集 | PR-03 | Week 1；作为后续 UI 的公共基础 | PASS |
| UI-03 | Review：Re-answer 编排、六档评分、完成反馈 | PR-08 | PR-05～07 | PASS |
| UI-04 | Today 基础：`今日先做`、确定性 fallback | PR-11 | PR-09 + PR-10 + PR-13 | PASS |
| UI-05 | Capture 失败路径：状态可见、重试、入口处置 | PR-14 | Week 3 Gate | NOT_AUTHORIZED |
| UI-06 | Authentication UI：会话查询、Passkey/密码登录、失败与成功状态 | PR-20 | PR-15 WebAuthn + PR-16 throttling | NOT_AUTHORIZED |
| UI-07 | Today 可定制工作台：模块库、独立方框、本地布局保存 | PR-21 | PR-11；明确仅本地保存 | NOT_AUTHORIZED |
| UI-08 | OCR 候选确认：多字段候选框、类型推荐、用户确认后转换 | PR-22 | PR-14 的 R10 gate | NOT_AUTHORIZED |
| UI-09 | 跨设备布局同步 | PR-23 路线占位 | PR-21 + layout revision/冲突 API 契约 | NOT_AUTHORIZED |
| UI-10 | ReviewRecord 真实撤销 | PR-24 路线占位 | PR-08 + 撤销 API/审计语义 | NOT_AUTHORIZED |
| UI-11 | UTC+8 每日 AI 推荐 | PR-25 路线占位 | PR-11 + PR-13 + PR-19 + 幂等/缓存/fallback 契约 | NOT_AUTHORIZED |
| UI-12 | OCR 离开页面后的后台状态查询 | PR-26 路线占位 | PR-14 + 后台任务状态 API 契约 | NOT_AUTHORIZED |

### 候选 PR 说明

| 候选 | 内容 | Gate 关系 |
| --- | --- | --- |
| PR-20 | Authentication UI 切片 | 不进入 Week 1–4 Gate；PR-15/16 后单独批准 |
| PR-21 | Today 可定制工作台，仅本地布局保存 | 不进入 Week 1–4 Gate；PR-11 后单独批准 |
| PR-22 | OCR 候选确认和类型推荐 | 不进入 Week 1–4 Gate；R10 gate 后单独批准 |
| PR-23 | 跨设备布局同步 | 不进入 Week 1–4 Gate；先定版 revision 和冲突 API |
| PR-24 | ReviewRecord 真实撤销 | 不进入 Week 1–4 Gate；先定版撤销 API 和审计语义 |
| PR-25 | UTC+8 每日 AI 推荐 | 不进入 Week 1–4 Gate；先定版幂等、缓存、fallback 和 AiRun 治理 |
| PR-26 | OCR 后台状态查询 | 不进入 Week 1–4 Gate；先定版任务状态和生命周期 API |

`PR-23～26` 仅是路线编号，尚未形成获批任务包。UI 视觉前置中的品牌渐变、字体资产和自动性能降级阈值仍为 `NOT_VERIFIED`，应在首次实际依赖它们的 PR 设计阶段定版。

## 串行依赖关系

```
PR-01 ─┐
PR-02 ─┼─ Week1 Gate ─→ PR-05 → PR-06 → PR-07 → PR-08 ─ Week2 Gate
PR-03 ─┤                                            │
PR-04 ─┘                                            ▼
                            W3-00 → PR-09 → PR-10 → PR-12 → PR-13 → PR-11 ─ Week3 Gate
                                                                    │
                                                    PR-14 → PR-15 → PR-16 → PR-17 → PR-18 ─┐
                                                    PR-19（可并行，MEDIUM）──────────────────┴─ Week4 Gate

UI 非阻断支线：
PR-15 + PR-16 ─→ PR-20 Authentication UI
PR-11 ─────────→ PR-21 Today 本地工作台 ─→ PR-23 跨设备布局同步
PR-14 / R10 ───→ PR-22 OCR 候选确认 ─────→ PR-26 OCR 后台状态查询
PR-08 ─────────→ PR-24 ReviewRecord 真实撤销
PR-11 + PR-13 + PR-19 ───────────────────→ PR-25 UTC+8 每日 AI 推荐
```

- 同 Phase 内通常允许低风险并行（如 PR-01 与 PR-02），HIGH migration（PR-05/09/12/15）串行且不与其他 migration 并行。**Week 3 由 W3-D01 覆盖本通用规则，W3-00、PR-09、PR-10、PR-12、PR-13、PR-11 与 Gate 必须逐项串行验收。**
- Phase 间必须过 Gate；Gate 失败即停（Week 1 硬性规则）。

## 每 PR Definition of Done

- Code complete + tests complete
- 涉数据结构：空库 `alembic upgrade head` PASS（+ downgrade 回放）
- 涉 UI：loading / empty / error / success 四态齐备；按 [ui-design.md](ui-design.md) §16 为所涉切片提供真实浏览器证据（视口/动效/焦点/reduced-motion）
- 涉学习流程：实际持久化 DB 状态验证（非仅 UI）
- API 契约：frontend client 与 backend schema 同步核对
- 行为变化：相关 docs 更新
- UI 切片范围：仅限 UI 切片表中已有明确"计划归属"的项（候选 PR 项除外）；越界实施视为 scope 扩张，STOP 并报告
- 验证命令全绿（validation.md），结果如实记录为 PASS/PARTIAL/FAIL

## 明确不做（BLOCK，见 README 第 5 节）

FSRS / Vector Search / Vector DB / Knowledge Graph / Graph Visualization / Elasticsearch / Redis / 微服务 / 新 Repository 层 / 新 Article Model / 设计系统重写 / Analytics 重建 / 自动文章生成。提出者须证明其解决当前 P0 闭环问题，否则拒绝进入 Sprint。
