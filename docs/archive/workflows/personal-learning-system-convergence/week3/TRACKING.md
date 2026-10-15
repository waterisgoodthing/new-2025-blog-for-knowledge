# Week 3 跟踪文件 — CANONICAL LEARNING

> 本文件是 Week 3 执行期的唯一进度与背景跟踪入口。主 agent 只做任务制定、派工、验收与报告；实现、独立评审与验证均由真实子 agent 完成。

## 1. 背景信息（Background）

### 1.1 目标

Week 3 关闭 canonical learning 读路径，使私有 Dashboard 仅从 canonical entities 回答三问：

1. 今天该复习什么？（review today）
2. 今天该练什么？（practise today）
3. 哪些知识点最弱？（weakest KP）

同时把公共 mistake 列表切到显式发布的 canonical `Mistake` 行，并落地后续学习功能所需的 Note↔KnowledgePoint canonical 关联。

### 1.2 计划与决策权威

- 执行计划（含 W3-D01～D05 决策、各工作包验收标准、Week 3 Gate 矩阵）：[README.md](README.md)
- 父工作流需求/任务/Gate：[../requirements.md](../requirements.md)、[../tasks.md](../tasks.md)、[../validation.md](../validation.md)
- 编排/权限/Gate 规则：`agents/orchestration.md`、`agents/permissions.md`、`agents/gates.md`

### 1.3c 主 agent 定版（2026-09-22，回应 PR-09 验证 U-1）

| 决策 | 内容 |
| --- | --- |
| W3-D10 | **源变更冲突语义**：迁移后 source note 内容漂移（title/revision/content hash 变化）不得静默 no-op。重放时须将该 source 记入对账报告 `rejected`（reason=`source_drift`）或独立 `conflicts` 区，并使 `checks.provenance_match=false` 或新增 `checks.source_stable=false`。**禁止**用新内容覆盖既有 canonical 目标（AI/解析内容不得静默覆写可信结构化数据）。status/hidden 变化仍走 W3-D07 visibility 对账路径。 |

### 1.3 已锁定决策（摘要，细节以 week3/README.md 为准）

| 决策 | 内容 |
| --- | --- |
| W3-D01 | 串行：W3-00 → PR-09 → PR-10 → PR-12 → PR-13 → PR-11 → Gate；逐项验收 PASS 才开下一项 |
| W3-D02 | PR-09 fail-closed 切换顺序：prepare → freeze legacy writes → migrate in scratch → reconcile → enable canonical public read → verify |
| W3-D03 | 公共 DTO 是 allowlist（`id,title,question_text,correct_answer,analysis,reason_category,mistake_reason,difficulty,knowledge_point_ids,created_at,updated_at`）；排除 `my_answer` 等私有字段；仅 `active+public` |
| W3-D04 | migration 032：`note_id` UUID、`knowledge_point_id` INTEGER；PK/Unique；FK `ON DELETE CASCADE` |
| W3-D05 | analytics/practice 确定性语义（practice-only attempts、非零分母、lapse 终身计数、稳定排序、0..10 题、无 AI） |

### 1.3b 主 agent 执行期定版（2026-09-22，回应 W3-00 盘点 unresolved）

| 决策 | 内容 |
| --- | --- |
| W3-D06 | legacy Note → canonical Mistake 映射矩阵：`status='published' AND hidden=false` → `status='active'` + `visibility='public'`；其余三格（published×hidden、unpublished×visible、unpublished×hidden）→ `status='active'` + `visibility='private'`。canonical `status` 表学习生命周期（active/archived），legacy `status` 表发布态，不得混用导致误归档。 |
| W3-D07 | 新 mapping version 命名 `wk3-mistake-visibility-v1`（≤64B）。既有 `v1-*` ledger 行与产物**原样保留**（治理记录不删）。新 mapping 运行两类动作：(a) 未迁移 legacy note → 按 W3-D06 创建 canonical 链（含 ReviewItem v2）；(b) 已迁移（`v1-*` 目标）→ **仅 UPDATE `mistakes.visibility`** 至映射值（幂等），事件记入对账报告而非新 ledger 目标行（目标 UNIQUE 不允许重复指向）。 |
| W3-D08 | ReviewItem 创建用 `fixed_interval_v2`。**禁止**把 legacy SM-2 的 ef/interval/repetitions 当作 v2 streak/ladder 写入。初始化取 v2 默认调度；`next_review` 存在时映射为 `next_due`（保留用户既定到期日）；无法映射字段进对账报告 unmapped 区。LSR03 校验器/测试中 `fixed_interval_v1`/`v1-*` 断言随 PR-09 改写。 |
| W3-D09 | legacy mistake 冻结范围 = **全部写入**（F-1～F-9）：create（含写型）、update-type（进/出 mistake）、promote、legacy writer UI 两表单、write-note 对 mistake 行的内容写入、SM-2 提交、通用字段更新、delete/batch-delete。依据 W3-D02 "freeze all new legacy mistake writes" fail-closed。兼容**读**全部保留（K-1～K-12）；`search_notes` 收窄与 `manage/notes` 对 mistake 行的读展示延后（记录 deferred，PR-18 处置）；UI 对 type='mistake' 行不得提供任何写操作入口。 |

### 1.4 起点事实（Verified starting point，2026-09-22）

- Week 2 Gate `PASS`（2026-09-21）。当前 dirty worktree 含 Week 2 实现与 migrations 028–030，必须作为 Week 3 基线保护，不得当作干净分支。
- source migration head = `030`（`030_reanswer_audit.py`，`down_revision="029"`）；031/032 不存在。
- 公共 `/mistakes` 仍经 `useNoteIndex` 读 legacy `Note(type='mistake')`。
- canonical `Mistake.visibility` 契约为 private-only；admin DTO/client 亦收窄为 `private`。
- Dashboard 摘要已用 canonical Question/Mistake/ReviewItem/ReviewRecord，但未暴露 daily practice、weak KP、recently mastered。
- `QuestionKnowledgePoint.knowledge_point_id` 与 `KnowledgePoint.id` 为 `INTEGER`（旧 D8 UUID 草图过期，不得驱动 032）。
- 现有 `MistakeOut` 含私有字段（含 `my_answer`），不得复用为公共 DTO。
- migration-026 适配器创建 canonical mistakes 时 `visibility='private'`；PR-09 须复用同一 ledger/幂等机制，不得另建平行迁移脚本。

### 1.5 授权状态

| 事项 | 状态 | 依据 |
| --- | --- | --- |
| Week 3 实现（W3-00～PR-11 代码、scratch 数据库、真实浏览器、文档） | **AUTHORIZED / COMPLETED** | 用户 2026-09-22 指令；Gate PASS（用户裁决） |
| scratch 数据库（`astra_week3_*` allowlist）、隔离迁移回放 | **AUTHORIZED / CLEANED UP** | 随 Week 3 实现授权；已清理 |
| 生产数据检查/写入、真实迁移执行、部署、cutover | **NOT_AUTHORIZED** | week3/README.md §7、§8；`blog_db` 未触及 |
| stage/commit/push/merge/release | **NOT_AUTHORIZED** | 同上 |
| Week 4（PR-14+）、候选 PR-20～26、AI 每日推荐 | **NOT_AUTHORIZED** | 同上 |
| `blog_v2` 残留处置（保持 032、不清理） | **USER_DECIDED（2026-09-22）** | INC-01/INC-02 已决流程记录 |

### 1.6 执行纪律（主 agent 自我约束）

1. 主 agent 只做：任务制定（write_scope/验收/止损）、派工、证据裁决、返工指派、最终 code accept、报告。不亲自实现产品代码、不亲自跑实现性测试写入。
2. 每个工作包：`implementer`（限定写范围）→ 独立只读 `reviewer`（无实现所有权）→ 必要 `verifier`/gate reviewer → 主 agent 验收。
3. HIGH 风险包保持实现、独立评审、验证、命名 gate 决策分别指派。
4. 下一项未开工，直到当前项验收为 `PASS`。
5. 只清理 Week 3 自建 scratch 资源；常驻服务与无关 dirty 文件受保护。

## 2. 当前进行程度（Progress）

更新时间：2026-09-22（持续更新，每次派工/验收后立即回写）

### 2.1 总状态

| 工作包 | 任务制定 | 实现 | 独立评审 | 验证 | Gates | 主 agent 验收 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W3-00 预检与合同锁定 | DONE | PASS | PASS（返工后复核） | PASS（实现者自证 + 评审复测） | 合同锁定 G0 依据就绪 | **PASS** | 1 BLOCKER 已关闭；见 [tasks/w3-00.md](tasks/w3-00.md) |
| PR-09 canonical public mistakes | DONE | PASS | PASS（返工后复核 R1～R4 全关闭） | PASS（db + api 两组） | G2 PASS；G3 PASS | **PASS** | 2 HIGH + 2 MEDIUM 已关闭；见 [tasks/pr-09.md](tasks/pr-09.md) |
| PR-10 KP analytics | DONE | PASS | PASS（PASS_WITH_NOTES，无缺陷） | PASS（PASS，PFV-01 返工后） | G4 PASS | **PASS** | PFV-01 归档题排除已修；见 [tasks/pr-10.md](tasks/pr-10.md) |
| PR-12 Note↔KP schema/API | DONE | PASS | PASS（PASS_WITH_NOTES，无阻断缺陷） | PASS（PASS，无产品缺陷） | G2 PASS；G3 PASS | **PASS** | INC-01 越权写已记录并升级用户裁决；见 [tasks/pr-12.md](tasks/pr-12.md) |
| PR-13 daily practice | DONE | PASS | PASS（PASS_WITH_NOTES，无缺陷） | PASS（PASS，无缺陷） | G4 PASS | **PASS** | LOW/INFO 记注；见 [tasks/pr-13.md](tasks/pr-13.md) |
| PR-11 Dashboard integration | DONE | PASS | PASS（PASS_WITH_NOTES，无缺陷） | PASS（PASS，含真实 Chromium） | G3 PASS；G4 PASS | **PASS** | R11-01/02 LOW 记注；见 [tasks/pr-11.md](tasks/pr-11.md) |
| Week 3 Gate | DONE（判据） | PASS | PASS（最终独立评审：产品不变量全过；初判 GATE_FAIL 仅因 INC-02） | PASS（六问矩阵 + 最终验证集） | G2 PASS；G3 PASS；G4 PASS | **PASS（用户 2026-09-22 裁决）** | INC-01/02 记为已决流程事件；见 [tasks/week3-gate.md](tasks/week3-gate.md) |

图例：DONE / 进行中 / 阻塞 / PASS / FAIL / NOT_VERIFIED / NOT_AUTHORIZED / —

### 2.2 派工日志（实际身份，planned ≠ executed）

| 时间 | 工作包 | agent_id（实际） | 角色 | 范围 | 结果 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-22 | W3-00 | W3-00-inv-inventory | consulted（只读盘点） | week3/evidence/ 两份 md | PASS：legacy 写/读清单 F-1～F-9、K-1～K-12；适配器 ledger/幂等/v1 ReviewItem 结论；12 项 unresolved 已裁决 |
| 2026-09-22 | W3-00 | W3-00-inv-runtime | consulted（只读盘点） | week3/evidence/ 一份 md | PASS：alembic 单头 030；visibility CHECK、键型、MistakeOut、Dashboard/公共读链、乐观锁、API client 风格核对完成 |
| 2026-09-22 | W3-00 | W3-00-impl-contracts | implementer | backend/tests/test_week3_contracts*、scripts/week3-scratch-guard* | PASS 自评：32 合同测试 + 13 守卫测试 |
| 2026-09-22 | W3-00 | W3-00-review | reviewer（只读） | 同上 4 文件 | CHANGES_REQUIRED：W3R-01 BLOCKER（双参绕过）、W3R-02 MEDIUM、W3R-03/04 LOW |
| 2026-09-22 | W3-00 | W3-00-rework | implementer（返工） | 同上 4 文件 | PASS 自评：W3R-01/02/03/04 全修，51 合同测试 + 36 守卫测试 |
| 2026-09-22 | W3-00 | W3-00-review-recheck | reviewer（只读复核） | 同上 4 文件 | PASS：四项全关闭，A/B/D 复现消除，回归与范围 OK |
| 2026-09-22 | W3-00 | main-agent | 验收 | — | **PASS**（W3F-11 live alembic current 钉扎移交 PR-09 首个 scratch 动作） |
| 2026-09-22 | PR-09 | PR-09-impl-backend | implementer | backend 031+schemas+routers+services+tests+runner | PASS 自评：160 passed；迁移矩阵+dry-run 零持久+对账报告 |
| 2026-09-22 | PR-09 | PR-09-impl-frontend | implementer | src/app、src/lib/api、components | PASS 自评：15/15 vitest、tsc 0 err；公共页切 canonical、UI 冻结、admin toggle |
| 2026-09-22 | PR-09 | PR-09-verify-db | verifier | week3/evidence migrations/sql/reviews | PARTIAL：迁移 A1-A6 全 PASS；ledger B1-B5 多 PASS 但 F-1 HIGH（next_due 丢弃源值）、F-2/F-3 MEDIUM |
| 2026-09-22 | PR-09 | PR-09-verify-api | verifier | week3/evidence api/browser/tests/screenshots | PARTIAL：A/B 多 PASS、浏览器 C.1/C.3/C.4 PASS；FINDING-01 HIGH（admin 写路径 500 MissingGreenlet）、C.2 FAIL |
| 2026-09-22 | PR-09 | PR-09-rework | implementer（返工） | backend services/routers/tests/scripts | PASS：PR9F-01/02/03/06 + W3-D10 + 小项全修 |
| 2026-09-22 | PR-09 | PR-09-verify-rework | verifier（复验） | week3/evidence | PARTIAL：两项 HIGH 复现 PASS、W3-D10 PASS；7 测试骨架红 |
| 2026-09-22 | PR-09 | PR-09-testfix | implementer（测试修复） | 2 测试文件 | PASS：7 项全绿；全量 10F→2F |
| 2026-09-22 | PR-09 | PR-09-review | reviewer（只读） | PR-09 全量改动 | CHANGES_REQUIRED：R1 HIGH（dry-run 非零持久）、R2/R3 MEDIUM、R4 LOW |
| 2026-09-22 | PR-09 | PR-09-gate-security | gate-reviewer（G3） | 安全边界 | **G3 PASS**（附风险注记非 block） |
| 2026-09-22 | PR-09 | PR-09-gate-db | gate-reviewer（G2） | 迁移/ledger/v2 | **G2 PASS**（附风险注记非 block） |
| 2026-09-22 | PR-09 | PR-09-rework-2 | implementer（返工） | 迁移 service + 测试 | PASS：R1～R4 修复 + R8 标注 |
| 2026-09-22 | PR-09 | PR-09-review-recheck2 | reviewer（定点复核） | 迁移 service | **PASS**：R1～R4 全关闭，独立 SQL 快照验证 |
| 2026-09-22 | PR-09 | main-agent | 验收 | — | **PASS**（R5/R7 风险注记；R6 出范围；R8 归档） |
| 2026-09-22 | PR-10 | PR-10-impl | implementer | service/schema/router/tests | PASS 自评：17 passed、单查询无 N+1 |
| 2026-09-22 | PR-10 | PR-10-impl-client | implementer | src/lib/api/knowledge-points.ts | PASS：tsc 0、vitest 3/3 |
| 2026-09-22 | PR-10 | PR-10-verify | verifier | week3/evidence | PASS（PFV-01 MEDIUM 语义待裁） |
| 2026-09-22 | PR-10 | PR-10-rework | implementer（返工） | kp_analytics_service.py | PASS：PFV-01 修复（3/1/2→0/0/0）、PFV-02 顺带 |
| 2026-09-22 | PR-10 | PR-10-review | reviewer（只读） | PR-10 全量 | PASS_WITH_NOTES：无缺陷，仅证据簿记/偏好 |
| 2026-09-22 | PR-10 | PR-10-gate-rec | gate-reviewer（G4） | 排序/确定性/provenance | **G4 PASS** |
| 2026-09-22 | PR-10 | PR-10-evidence-fix | implementer（文档） | 3 证据文件 | PASS：PFV 状态回写 CLOSED |
| 2026-09-22 | PR-10 | main-agent | 验收 | — | **PASS** |
| 2026-09-22 | PR-12 | PR-12-impl | implementer | 032+model+schema+service+router+tests | PASS 自评：43 passed、迁移矩阵全 PASS |
| 2026-09-22 | PR-12 | PR-12-impl-client | implementer | src/lib/api/notes.ts | PASS：tsc 0、vitest 6/6 |
| 2026-09-22 | PR-12 | PR-12-verify | verifier | week3/evidence | PASS：迁移矩阵/API/权限/回归全过，无产品缺陷 |
| 2026-09-22 | PR-12 | PR-12-fix | implementer（LOW 修复） | 证据路径 + notes.ts 类型 | PASS |
| 2026-09-22 | PR-12 | PR-12-review | reviewer（只读） | PR-12 全量 | PASS_WITH_NOTES：F-01～F-05 全 LOW/INFO；**自报 INC-01** |
| 2026-09-22 | PR-12 | PR-12-gate | gate-reviewer（G2+G3） | DB + 安全 | **G2 PASS；G3 PASS** |
| 2026-09-22 | PR-12 | INC-01-assess | verifier（只读事故评估） | blog_v2 只读诊断 | 完成：无数据丢失；推荐保持 032；需用户裁决 |
| 2026-09-22 | PR-12 | main-agent | 验收 | — | **PASS**（F-01～03 LOW 记注；INC-01 升级用户裁决） |
| 2026-09-22 | PR-13 | PR-13-impl | implementer | practice service/schema/router/tests | PASS 自评：17 passed；main.py 2 行注册 |
| 2026-09-22 | PR-13 | PR-13-impl-client | implementer | src/lib/api/practice.ts | PASS：tsc 0、vitest 5/5 |
| 2026-09-22 | PR-13 | PR-13-verify | verifier | week3/evidence | PASS：A-E 全过，无 BLOCKER/HIGH/MEDIUM |
| 2026-09-22 | PR-13 | PR-13-review | reviewer（只读） | PR-13 全量 | PASS_WITH_NOTES：F1-F2 LOW、F3-F6 INFO |
| 2026-09-22 | PR-13 | PR-13-gate-rec | gate-reviewer（G4） | 确定性/provenance/只读 | **G4 PASS** |
| 2026-09-22 | PR-13 | main-agent | 验收 | — | **PASS**（LOW/INFO 记注） |
| 2026-09-22 | PR-11 | PR-11-impl-backend | implementer | dashboard service/schema/router/tests | PASS 自评：W3R-05 合同锁定 |
| 2026-09-22 | PR-11 | PR-11-impl-frontend | implementer | dashboard/practice UI + client | PASS：tsc 0、97 vitest |
| 2026-09-22 | PR-11 | PR-11-verify | verifier | week3/evidence browser/sql/api | PASS：真实 Chromium 双视口 + SQL 溯源 |
| 2026-09-22 | PR-11 | PR-11-review | reviewer（只读） | PR-11 全量 | PASS_WITH_NOTES：R11-01/02 LOW/INFO |
| 2026-09-22 | PR-11 | PR-11-gate-security | gate-reviewer（G3） | 私有边界/泄漏/auth | **G3 PASS** |
| 2026-09-22 | PR-11 | PR-11-gate-rec | gate-reviewer（G4） | 确定性 fallback/provenance | **G4 PASS** |
| 2026-09-22 | PR-11 | main-agent | 验收 | — | **PASS**（偏好记注） |
| 2026-09-22 | Gate | GATE-seed-verify | verifier | week3/evidence/gate/** | GATE_PASS：六问全 PASS、最终验证集绿（4 既有失败如实记录） |
| 2026-09-22 | Gate | GATE-final-review | reviewer（只读） | Gate 全量 | 初判 **GATE_FAIL**：六问/验证集 PASS，但发现未记录 HIGH（INC-02） |
| 2026-09-22 | Gate | GATE-gate-db | gate-reviewer（G2） | 迁移/schema/完整性 | **G2 PASS** |
| 2026-09-22 | Gate | GATE-gate-security | gate-reviewer（G3） | 边界/泄漏/auth | **G3 PASS** |
| 2026-09-22 | INC-02 | INC-02-investigate | verifier（只读） | blog_v2 + 测试连接语义 | 根因：`.env`→blog_v2、无 conftest；9+2 行残留确认 |
| 2026-09-22 | INC-02 | INC-02-fix | implementer | backend/tests/conftest.py | PASS：fail-closed 守卫，无 env 拦截 8 测试、显式 scratch 零回归 |
| 2026-09-22 | Gate | user（Project Lead） | 授权裁决 | — | blog_v2 保持 032 + 不清理残留；Gate 定级 **PASS**（附 INC-01/02 已决记录） |
| 2026-09-22 | Gate | main-agent | 验收 | — | **PASS**（用户裁决；产品不变量全过） |
| 2026-09-22 | PR-11 | PR-11-impl-backend | implementer | dashboard service/schema/router/tests | PASS 自评：101 passed；W3R-05 合同锁定 |
| 2026-09-22 | PR-11 | PR-11-impl-frontend | implementer | dashboard/practice UI + client | PASS 自评：tsc 0、97 vitest；四态齐备 |
| 2026-09-22 | PR-11 | PR-11-verify | verifier | week3/evidence + 真实 Chromium | PASS：A-D 全过，浏览器 9 截图，SQL 溯源一致 |
| 2026-09-22 | PR-11 | PR-11-review | reviewer（只读） | PR-11 全量 | PASS_WITH_NOTES：R11-01/02 LOW 偏好、R11-03 记注 |
| 2026-09-22 | PR-11 | PR-11-gate-security | gate-reviewer（G3） | 私有边界/公共路由/无泄漏 | **G3 PASS** |
| 2026-09-22 | PR-11 | PR-11-gate-rec | gate-reviewer（G4） | 确定性 fallback/provenance | **G4 PASS** |
| 2026-09-22 | PR-11 | main-agent | 验收 | — | **PASS**（R11-01/02 记注；R11-03 采纳） |

### 2.3 发现与返工日志

> **事故 INC-01（2026-09-22）**：PR-12 评审员（agent_id PR-12-review）在未通过 `scripts/week3-scratch-guard.py` 的情况下对本地 `blog_v2` 执行 `alembic upgrade head`，使其 revision 由 026 变为 032（027～032 六个迁移被应用）。评审员自报：仅 additive 迁移、无数据删除、之后未再写入。已按止损条件处理：冻结对 `blog_v2` 的任何进一步写入，派只读评估（INC-01-assess）确认影响与安全恢复选项，由主 agent/用户裁决恢复方式。生产库 `blog_db` 未触及。

> **事故 INC-02（2026-09-22 发现 / 2026-09-23-24 发生）**：Gate 最终独立评审员（GATE-final-review）发现 `blog_v2.notes` 存在 9 行 Week 3 测试夹具数据（slug `wk3-<hex>` ×8、`pr09rw-<hex>` ×1，title `pr09-rework-note`，type='mistake'），created_at 2026-09-23 14:26 → 2026-09-24 16:54，**晚于 INC-01 冻结声明**。slug 模式对应 `test_pr09_wk3_runner.py` 与 `test_pr09_rework.py`；`.env` DATABASE_URL 默认即 blog_v2，守卫拒收该库 → 这些是**未经 guard 的 pytest 直写**。无 schema 变更、无数据丢失、blog_db 未触及、无安全泄漏。INC-01 评估「no post-migration writes」结论被推翻。处置：主 agent 记录为 HIGH（流程/授权）未决，冻结后续写入，派调查根因 + 加测试级防直写守卫；是否清理 9 行夹具数据交用户裁决。

| 编号 | 来源 | 严重度 | 问题 | 处置 | 状态 |
| --- | --- | --- | --- | --- | --- |
| W3F-01 | inv-inventory | MEDIUM | 冻结范围歧义（F-7～F-9 是否纳入） | W3-D09：全冻结 F-1～F-9 | CLOSED |
| W3F-02 | inv-inventory | MEDIUM | promote 无 UI 调用方但 API 开放 | 路由层冻结（并入 W3-D09） | CLOSED |
| W3F-03 | inv-inventory | LOW | search_notes 不按 type 过滤 | 延后收窄，PR-18 处置；本期只读兼容 | DEFERRED |
| W3F-04 | inv-inventory | LOW | manage/notes 读 mistake 后前端丢弃 | 读可保留；写入口必须冻结 | CLOSED |
| W3F-05 | inv-adapter | HIGH | 新 mapping 与 v1-* 产物关系未定 | W3-D07：v1 保留 + visibility 就地对账 | CLOSED |
| W3F-06 | inv-adapter | HIGH | SM-2 → v2 调度映射未定 | W3-D08：v2 默认 + next_review→next_due | CLOSED |
| W3F-07 | inv-adapter | MEDIUM | dry-run 留 pending 行 | PR-09 须回滚或零持久化 dry-run | OPEN→PR-09 |
| W3F-08 | inv-adapter | MEDIUM | 对账报告 schema 未定 | 见 pr-09.md 报告 schema | CLOSED |
| W3F-09 | inv-adapter | MEDIUM | LSR03 断言 v1 与 v2 目标冲突 | PR-09 测试改写清单 | OPEN→PR-09 |
| W3R-01 | W3-00-review | BLOCKER | 守卫双参绕过：URL 指向 production_db 时仍 PASS 并注入子进程 | 返工修复：以有效连接串解析库名；双参不一致 FAIL | CLOSED（复核 PASS） |
| W3R-02 | W3-00-review | MEDIUM | host 无白名单，远程 host 可用合法库名通过 | 返工加固：默认仅 localhost/127.0.0.1/::1，远程需 `--allow-remote-host` | CLOSED（复核 PASS） |
| W3R-03 | W3-00-review | LOW | `hidden is False` 身份比较 | 返工改为 `not bool(hidden)` 语义 | CLOSED |
| W3R-04 | W3-00-review | LOW | 比率越界静默返回 | 返工 raise ValueError + 边界测试 | CLOSED |
| W3R-05 | W3-00-review | LOW | dashboard/empty_metadata 形状完备性可能缺 per-section action | 主 agent 裁决：转 PR-11 实现时定版再回写合同 | DEFERRED→PR-11 |
| W3F-10 | inv-runtime | LOW | 031 须只替换 ck_mistakes_visibility | 写入 pr-09 约束 | CLOSED |
| W3F-11 | inv-runtime | LOW | 未做 live alembic current 钉扎 | 移交 PR-09 首个 scratch 动作经 runner 复核 | OPEN→PR-09 |
| PR9F-01 | pr-09-db | HIGH | `next_due` 恒 `_now_utc()`，源 `next_review` 被丢弃（违 W3-D08） | 返工：映射源值，报告如实计数 | OPEN→返工 |
| PR9F-02 | pr-09-db | MEDIUM | 对账报告 match 字段硬编码 True | 返工：真实计算，可失败 | OPEN→返工 |
| PR9F-03 | pr-09-db | MEDIUM | dry-run 短路致 `created_v2` 恒 0，报告不忠实 | 返工：dry-run 输出计划值 | OPEN→返工 |
| PR9F-04 | pr-09-db | LOW | 首次 dry-run 报 `replay_noop=false` | 随返工顺带修正 | OPEN→返工 |
| PR9F-05 | pr-09-db | LOW | published×visible 映射失败记 skipped 而非 rejected | 随返工顺带修正 | OPEN→返工 |
| PR9U-01 | pr-09-db | MEDIUM | 源变更静默 no-op（U-1） | W3-D10 定版：记 source_drift 冲突，禁覆写 | OPEN→返工 |
| PR9F-06 | pr-09-api | HIGH | admin 写路径 500 MissingGreenlet（PATCH 成功/PUT/DELETE） | 返工：修复序列化过期字段 | OPEN→返工 |
| PR9F-07 | pr-09-api | LOW | 验证测试重复+EventLoop 隐患 | 返工整理 | CLOSED |
| PR9R-01 | pr-09-review | HIGH | dry-run 非零持久化（reconcile UPDATE + commit） | 返工-2：dry_run 分支只比较不写 | CLOSED（定点复核 PASS，独立快照） |
| PR9R-02 | pr-09-review | MEDIUM | `_ensure_approval_actors` dry-run 落库 | 返工-2：dry_run 提前返回 | CLOSED |
| PR9R-03 | pr-09-review | MEDIUM | `_count_match` 不含 would_* | 返工-2：dry_run 并入 would_* | CLOSED |
| PR9R-04 | pr-09-review | LOW | dry-run 双计 visibility_reconciled | 返工-2：只增 would_reconcile | CLOSED |
| PR9R-05 | pr-09-review | LOW | adapter 对任意 mapping_version 写 v2 调度（v1-* 重放语义静默改变） | 风险注记；v1-* 未被改写（W3-D07 合规） | ACCEPTED_RISK |
| PR9R-06 | pr-09-review | LOW | `test_legacy_note_migration_contract.py` revision 断言 026→027 与他包不一致 | 出 PR-09 写范围；记录 | DEFERRED |
| PR9R-07 | pr-09-review | LOW | cleanup 用 `session_replication_role=replica` 可掩盖 delete 顺序 FK 回归 | 评估注记；断言期真实 FK 已由 verify-8 抓到 | ACCEPTED_NOTE |
| PR9R-08 | pr-09-review | LOW | 旧返工前证据 JSON 与新材料并存易误读 | 返工-2 已加 `README-stale.md` 标注 | CLOSED |
| PR10F-01 | pr-10-verify | MEDIUM | review 路径未排除 archived Question（违 W3-D05） | 返工修复：review JOIN Question 过滤 active | CLOSED（复现 3/1/2→0/0/0） |
| PR10F-02 | pr-10-verify | LOW | review 子查询单 SQL 内重复两次 | 返工 `.cte()` 单 WITH | CLOSED |
| PR10F-03 | pr-10-verify | INFO | ui-v2 预存在 tsc 错误 | 出范围 | DEFERRED |
| PR10R-01 | pr-10-review | LOW | 证据文档仍标 PFV-01/02 OPEN | 证据回写 CLOSED + STALE 标注 | CLOSED |
| PR10R-02 | pr-10-review | LOW | /analytics 无分页/上限 | 个人规模可接受，后续优化 | ACCEPTED_RISK |
| PR10R-03 | pr-10-review | INFO | 客户端 vitest 字段断言为同文件字面量 | 真口径另有 verify_contract 正则比对 | ACCEPTED_NOTE |
| PR12F-01 | pr-12-review | LOW | 并发删父 Note/KP 时 link 返回 409 而非 404 | 边缘语义；幂等/无 500 已保证 | ACCEPTED_NOTE |
| PR12F-02 | pr-12-review | LOW | link 返回 `linked:true` 无信息量 | 幂等契约文档化 | ACCEPTED_NOTE |
| PR12F-03 | pr-12-review | LOW | unlink 无 savepoint，并发可能 SAWarning | 非 500；观察 | ACCEPTED_NOTE |
| PR12F-04 | pr-12-review | INFO | PR12V-02 已不可复现（client 已为 string） | 已随 PR-12-fix 修正 | CLOSED |
| PR12F-05 | pr-12-review | INFO | client 函数暂无 UI 消费 | 符合 excluded src/app | ACCEPTED_NOTE |
| INC-01 | PR-12-review | HIGH（流程） | 未经 guard 对 `blog_v2` 执行 upgrade（026→032） | 只读评估：无数据丢失；用户裁决保持 032，不清理 | CLOSED（USER_DECIDED） |
| INC-02 | GATE-final-review | HIGH（流程） | 未经 guard 的 pytest 直写 blog_v2（9 行夹具 + 2 行 taxonomy，晚于 INC-01 冻结） | 根因调查 + conftest fail-closed 守卫 + 记录；用户裁决保持 032 不清理 | CLOSED（USER_DECIDED） |
| INC-02-FIX | INC-02-fix | — | 测试防直写守卫 | `backend/tests/conftest.py` fail-closed；无 env 拦截 8 测试，显式 scratch 零回归 | CLOSED（用户授权保持 032 + 不清理残留） |
| PR13F-01 | pr-13-verify/review | LOW | 无 KP 的 active 题被静默丢弃，未计入 raw_candidate_count | 确定性不受影响；W3-D05 以 KP 为模型 | ACCEPTED_NOTE |
| PR13F-02 | pr-13-verify/review | LOW | mastered 排除未过滤 Mistake.status（与 PR-10 active-only 不对称） | 符合任务字面「任一关联 canonical Mistake」 | ACCEPTED_NOTE |
| PR13F-03 | pr-13-review | INFO | PRACTICE_MAX_ITEMS=10 实际不可达 | 上界仅形式成立 | ACCEPTED_NOTE |
| PR13F-04 | pr-13-review | INFO | selection_reason 为 KP 级、含内部术语 | 不伪造弱项 | ACCEPTED_NOTE |
| PR13F-05 | pr-13-review | INFO | analytics 查询失败整请求 500（fail-closed） | 无部分/伪造推荐 | ACCEPTED_NOTE |
| PR13F-06 | pr-13-review | INFO | main.py 越声明 write globs（2 行注册） | 主 agent 接受为必要 | CLOSED |
| PR11F-01 | pr-11-verify | LOW | 服务测试假设空 scratch DB | 测试隔离；干净库 101 全过 | ACCEPTED_NOTE |
| PR11F-02 | pr-11-verify/review/g4 | LOW | weak_top3 含零指标 KP（PR-10 继承语义） | 权威锁定行为，未重排 | ACCEPTED_NOTE |
| PR11F-03 | pr-11-verify | INFO | 后端全停时 AuthGate 先重定向 | error+retry 用 endpoint abort 验证 | ACCEPTED_NOTE |
| PR11F-04 | pr-11-verify | INFO | scratch DB/预览仍在跑 | Gate 资源清理阶段处理 | OPEN→Gate |
| R11-01 | pr-11-review | LOW | review 数据不可用但仍渲染「没有到期复习」文案 | 无 CTA、不虚构入口；偏好 | ACCEPTED_NOTE |
| R11-02 | pr-11-review | INFO | 子查询失败降级为空列表（无法区分真空/失败） | 不渲染伪造推荐 | ACCEPTED_NOTE |

### 2.4 证据索引

- `evidence/tests/` 测试输出
- `evidence/migrations/` 迁移回放
- `evidence/sql/` 完整性/对账 SQL 结果
- `evidence/api/` API 契约与负测证据
- `evidence/browser/` 真实 Chromium 证据
- `evidence/reviews/` 独立评审结论
- `evidence/screenshots/` 截图

### 2.5 明确未执行（与授权边界一致）

- 生产 migration/cutover、生产数据检查（生产 `blog_db` 未触及）
- commit/stage/push/merge/release
- legacy 表/端点删除、migration-026 治理记录删除
- AI 每日推荐、AI KP 自动关联、FSRS、加权/ML、趋势图表
- PR-14+、PR-20～26

### 2.6 收尾状态

- Week 3 Gate：**PASS**（用户 2026-09-22 裁决；产品/数据/安全不变量全过，INC-01/02 记为已决流程事件）
- 最终技术报告：[week3-technical-report.md](week3-technical-report.md)
- scratch 资源清理：**PASS**（34 个 `astra_week3_*` 库、2 个临时 PG 实例、验证进程；常驻 `:8000` 与 `blog_v2` 未动）
- 生产/版本控制写操作：**NOT_AUTHORIZED**（未执行）


### 2026-09-26 后续复核

历史 Gate PASS 保留；本次证据完整性复核 PARTIAL。事故防复发补强与独立评审见 [后续记录](incident-followup-2026-09-26/README.md)，不执行数据库恢复/清理。
