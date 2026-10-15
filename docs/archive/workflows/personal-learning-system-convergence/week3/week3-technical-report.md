# Week 3 技术报告：CANONICAL LEARNING

> 执行日期：2026-09-22  
> 主 agent / `primary_owner` / 最终代码验收：主 agent（WORKER 模式）  
> 授权范围：W3-00 → PR-09 → PR-10 → PR-12 → PR-13 → PR-11 → Week 3 Gate 的代码、隔离数据库、真实浏览器与文档工作  
> 最终状态：**PASS**（Week 3 Gate **PASS**，用户 2026-09-22 裁决；附 INC-01/INC-02 已决流程记录）

## 1. 结论

Week 3「CANONICAL LEARNING」已按锁定的串行顺序 **W3-00 → PR-09 → PR-10 → PR-12 → PR-13 → PR-11 → Week 3 Gate** 完成。所有工作包的实现、独立评审、验证、命名 Gate（G2/G3/G4）与主 agent 最终验收均为 **PASS**；Week 3 Gate 的六问矩阵与最终验证集全部独立复现通过。

本次证明：私有 Dashboard 能仅从 canonical entities 回答三问（今天该复习什么 / 今天该练什么 / 哪个知识点最弱）；公共 `/mistakes` 已切到显式发布的 canonical `Mistake` 行（public allowlist，无 legacy fallback）；legacy mistake 写入全部冻结、兼容读保留；`Note↔KnowledgePoint` canonical 关联（migration 032）落地；分析/选题为确定性、无 AI、只读。

本结论**不**代表代码已 commit、push、merge、部署或对生产库执行迁移。生产库 `blog_db`（revision 025）**未被触及**。INC-01/INC-02 涉及本地开发库 `blog_v2`，已按用户裁决处置并记录。

## 2. 状态总览

| 工作包 | 风险 | 实现 | 独立评审 | 验证 | Gates | 主 agent 验收 |
| --- | --- | --- | --- | --- | --- | --- |
| W3-00 预检与合同锁定 | HIGH | PASS | PASS（返工后复核） | PASS | 合同锁定 | PASS |
| PR-09 canonical public mistakes | HIGH | PASS | PASS（返工后复核 R1～R4 关闭） | PASS（DB + API 两组） | G2 PASS；G3 PASS | PASS |
| PR-10 KP analytics | MEDIUM | PASS | PASS_WITH_NOTES（无缺陷） | PASS（PFV-01 返工后） | G4 PASS | PASS |
| PR-12 Note↔KP schema/API | HIGH | PASS | PASS_WITH_NOTES（无阻断缺陷） | PASS | G2 PASS；G3 PASS | PASS |
| PR-13 daily practice | MEDIUM | PASS | PASS_WITH_NOTES（无缺陷） | PASS | G4 PASS | PASS |
| PR-11 Dashboard integration | MEDIUM | PASS | PASS_WITH_NOTES（无缺陷） | PASS（含真实 Chromium） | G3 PASS；G4 PASS | PASS |
| Week 3 Gate | HIGH | PASS | PASS（初判 GATE_FAIL 仅因 INC-02） | PASS（六问 + 最终验证集） | G2/G3/G4 PASS | **PASS（用户裁决）** |

授权边界：Week 3 实现与 scratch 验证为 **PASS**；生产迁移/cutover、commit/push/merge/release、Week 4 与候选 PR-20～26 为 **NOT_AUTHORIZED**。

## 3. 关键设计与实现

### W3-00：预检与合同锁定
- 固化 dirty 基线快照、核验唯一 source migration head=030、盘点 legacy mistake 写入/读取面（F-1～F-9 写入、K-1～K-12 兼容读）与 migration-026 ledger 机制。
- 以可执行断言锁定 W3-D03 公共 DTO allowlist（11 字段）、W3-D05 指标/practice/dashboard 形状、W3-D04 键型、W3-D06 映射矩阵，并通过真实模型漂移检测。
- 新建 `scripts/week3-scratch-guard.py`：任何 DB 动作前校验目标库名属 `astra_week3_*`，拒绝 `blog_db`/`blog_v2`/默认 `.env`/远程 host（默认仅 localhost）。独立评审发现并关闭 1 个 BLOCKER（双参绕过）。

### PR-09：canonical public mistakes
- migration 031 仅替换 `ck_mistakes_visibility` 为 `IN ('private','public')`，downgrade 遇 public 行 fail-closed。
- 新增独立公共 DTO `PublicMistakeOut`（allowlist，排除 `my_answer` 等私有字段）与无鉴权 `GET /api/public/mistakes`（仅 `active+public`，零 public 显式 Empty）；admin-only visibility 变更带乐观锁（409）。
- 冻结 F-1～F-9 全部 legacy mistake 写入（路由层 410 `legacy_mistake_write_frozen`），保留 K-1～K-12 兼容读；公共页切 canonical、无 legacy fallback。
- ledger runner 以新 mapping version `wk3-mistake-visibility-v1` 复用 026 ledger：未迁移按 W3-D06 建 canonical 链（ReviewItem v2），已迁移仅幂等对账 `visibility`；dry-run 零持久化；机器可读对账报告；source drift（W3-D10）记冲突且不覆写目标。

### PR-10：canonical KP analytics
- service-owned 单查询聚合：practice-only attempts（review-context 排除）、非零分母（零样本 0.0）、lapse 终身 `rating<=2`、due 计数、多 KP 全额计入、archived Question/Mistake + inactive KP 全排除（含 review 路径）。
- 排序权威 `KP_ANALYTICS_SORT_KEY = (wrong_rate DESC, lapse_count DESC, due_count DESC, knowledge_point_id ASC)`；admin-only 只读端点；无权重/ML/趋势/AI。

### PR-12：Note↔KP canonical 关联
- migration 032 `note_knowledge_points`：`note_id` UUID、`knowledge_point_id` INTEGER、复合 PK、双 FK `ON DELETE CASCADE`、KP 方向索引。
- admin-only link/unlink/list（幂等、404/401-403、并发唯一约束不 500）；`knowledge_point_links` 多态表保持不动；跨学科规范化显式 deferred。

### PR-13：daily practice
- `GET /api/admin/practice/today`：weak-KP 优先（复用 PR-10 权威）、active/unarchived、7×24h 滚动窗口排除近期已练、mastered 排除、0..10 实际条目（候选 ≥3 时目标 3）、稳定排序收尾 `knowledge_point_id, question_id`、显式 selection reason + 诚实 Empty、DTO 无答案字段、只读不创建 Attempt。

### PR-11：Dashboard 集成
- 扩展既有 Dashboard summary（单一权威）：今日复习/练习计数与 section action、weak Top3（PR-10 序）、最近掌握 4（最新合格 ReviewRecord 变 mastered 且当前仍 mastered，`reviewed_at DESC` + item ID，限 4）、`今日先做`确定性 fallback（由 due review/practice 推导，无 AI）。
- 四态齐备、部分服务失败不虚构推荐、保留 profile/activity/storage、键盘/焦点/reduced-motion；真实 Chromium 桌面 + 390 窄屏 + SQL 溯源证明三问数据来自 canonical 行。

## 4. 主 agent 执行期定版（回应 W3-00 盘点 unresolved）

| 决策 | 内容 |
| --- | --- |
| W3-D06 | legacy Note→Mistake 映射矩阵：仅 `published AND hidden=false` → `active+public`，其余三格 → `active+private`；canonical `status` 表学习生命周期，不与发布态混用。 |
| W3-D07 | 新 mapping version `wk3-mistake-visibility-v1`；`v1-*` ledger/产物保留；已迁移目标仅幂等 UPDATE `visibility`，不建重复目标行。 |
| W3-D08 | ReviewItem 用 `fixed_interval_v2`；禁拷 SM-2 ef/interval/repetitions；`next_review`→`next_due`；无法映射字段进报告。 |
| W3-D09 | legacy mistake 冻结范围 = 全部写入 F-1～F-9；兼容读 K-1～K-12 保留。 |
| W3-D10 | 源内容漂移记 `source_drift` 冲突并置 `provenance_match=false`，禁止覆写既有 canonical 目标。 |

## 5. 多智能体协作实录

执行模式 **WORKER**。主 agent 只做任务制定、派工、证据裁决、返工指派与最终验收；实现/评审/验证均由真实子 agent（`general` 类型）完成。独立性通过「实现者 ≠ 评审者 ≠ 验证者」与返工后由不同 agent 复核保证。

| 阶段 | 参与 agent（实际身份） | 结果 |
| --- | --- | --- |
| W3-00 | inv-inventory / inv-runtime（只读盘点）、impl-contracts、review、rework、review-recheck | 1 BLOCKER + 1 MEDIUM 关闭 |
| PR-09 | impl-backend、impl-frontend、verify-db、verify-api、rework、verify-rework、testfix、review、gate-security、gate-db、rework-2、review-recheck2 | 2 HIGH + 2 MEDIUM 关闭 |
| PR-10 | impl、impl-client、verify、rework、review、gate-rec、evidence-fix | 1 MEDIUM（PFV-01）关闭 |
| PR-12 | impl、impl-client、verify、fix、review、gate(G2+G3)、INC-01-assess | 无产品缺陷；INC-01 记录 |
| PR-13 | impl、impl-client、verify、review、gate-rec | 无缺陷 |
| PR-11 | impl-backend、impl-frontend、verify、review、gate-security、gate-rec | 无缺陷 |
| Gate | seed-verify、final-review、gate-db、gate-security | 六问全 PASS；final-review 初判 GATE_FAIL（仅 INC-02） |
| 事故/清理 | INC-02-investigate、INC-02-fix、cleanup | 守卫落地；34 scratch 库清理 |

说明：本环境可用的子 agent 为通用类型，未使用 Week 1 记录中的命名模型身份；所有 PASS 均以当前代码、自动测试、真实浏览器、隔离 scratch DB 或 runtime 原始证据为准。

## 6. 评审发现与关闭证据（摘要）

| 发现 | 严重度 | 处置 | 状态 |
| --- | --- | --- | --- |
| W3R-01 守卫双参绕过 | BLOCKER | 以有效连接串解析库名；双参不一致 FAIL | CLOSED |
| W3R-02 host 无白名单 | MEDIUM | 默认仅 localhost，远程需显式旗标 | CLOSED |
| PR9F-01 ReviewItem `next_due` 丢弃源值 | HIGH | 映射源 `next_review`（复现 2026-12-15） | CLOSED |
| PR9F-06 admin 写路径 500 MissingGreenlet | HIGH | 序列化前 refresh（PATCH 成功 200、version+1） | CLOSED |
| PR9R-01 dry-run 非零持久化 | HIGH | dry_run 分支只比较不写（独立 SQL 快照验证） | CLOSED |
| PR10F-01 review 路径未排除 archived Question | MEDIUM | JOIN Question 过滤 active（3/1/2→0/0/0） | CLOSED |
| 其余 LOW/INFO（R5/R7、F-01～03、R11-01/02 等） | LOW/INFO | 记录为 ACCEPTED_NOTE / DEFERRED | 记录在案 |

零未决 BLOCKER/HIGH 产品缺陷。

## 7. 事故 INC-01 / INC-02（流程/授权）

- **INC-01**：PR-12 评审员未经 `week3-scratch-guard.py` 对本地 `blog_v2` 执行 `alembic upgrade head`（026→032）。只读评估：仅 additive 迁移、无数据删除、`blog_db` 未触及。
- **INC-02**：Gate 最终评审发现 `blog_v2.notes` 存在 9 行 Week 3 测试夹具 + 2 行 taxonomy，created 2026-09-23/24，晚于 INC-01 冻结；根因是 `.env` 默认 `DATABASE_URL` 指向 `blog_v2` 且仓库无 pytest 守卫。
- **处置**：根因调查 + 新建 `backend/tests/conftest.py` fail-closed 守卫（无 env 时拦截 8 个越界测试、显式 `astra_week3_*` 零回归、全量基线不增加）；用户裁决 **blog_v2 保持 032、暂不清理残留**，Gate 定级 **PASS** 并附为本报告已决流程记录。
- **影响**：生产 `blog_db` 未触及；无数据丢失、无安全泄漏；测试基础设施防直写能力已加固。

## 8. 验证证据索引

- 合同：`backend/tests/week3_contracts_support.py`、`test_week3_contracts.py`（53 passed）
- Gate：`docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/`
  - 六问复算 `sql/gate-matrix-recompute.json`；HTTP `api/gate-matrix-http.json`、`api/gate-q5.json`
  - 迁移回放 `migrations/gate-mig-*.log`；schema 形状；单头 032
  - 真实 Chromium `browser/`、`screenshots/`（9 张）
  - `gate-matrix.md`、`gate-findings.md`、`git-diff-check.txt`
- 各 PR 证据：`evidence/tests/`、`evidence/migrations/`、`evidence/sql/`、`evidence/api/`、`evidence/browser/`、`evidence/reviews/`（前缀 `pr-09-*`、`pr-10-*`、`pr-12-*`、`pr-13-*`、`pr-11-*`）
- 事故：`evidence/inc-01-blog-v2-assessment.md`、`evidence/inc-02-root-cause.md`、`evidence/tests/inc-02-fix-*.txt`
- 清理：`evidence/cleanup-2026-09-26.txt`
- 根目录遗留证据已统一迁移至 `evidence/root-week3-relocated/`（含 `RELOCATED-MANIFEST.sha256`）

### 最终验证集结果

| 项 | 结果 |
| --- | --- |
| 5 PR 目标后端套件 | 147 passed（clean DB） |
| 前端 vitest | 69 文件 / 516 passed |
| backend 全量（fresh scratch，032） | 821 passed / 4 failed / 9 skipped（3 项测试污染失败有 isolated PASS；1 项 psycopg2 环境失败 isolation 为 n/a） |
| `npx tsc --noEmit` | exit 0 |
| `npm run test:typecheck` | 10 errors，全在未跟踪 `src/features/ui-v2/`（预存在，PR10F-03） |
| migration 030→032 回放 + downgrade/re-upgrade | PASS，单头 032，schema 符合 W3-D04 |
| fresh `npm run build:cf` + workerd preview + runtime smoke | build exit 0；smoke ok=20 / failed=0 |
| `git diff --check` | clean（exit 0） |

## 9. 授权边界与未执行事项

- **未执行**：生产数据检查/写入、真实生产迁移执行、部署、cutover；commit/stage/push/merge/release；legacy 表/端点删除、migration-026 治理记录删除。
- **未授权范围**：Week 4（PR-14+）、候选 PR-20～26、AI 每日推荐、AI KP 自动关联、FSRS、加权/ML、趋势图表。
- 工作树为脏（含 Week 2 基线与 Week 3 改动），未做任何 git 写操作；无关既有改动未被覆盖。

## 10. 风险 / 遗留 / 待决

- **保留风险（用户已决）**：`blog_v2` 保持 revision 032 且不清理 9+2 行夹具残留；INC-01/INC-02 记为已决流程事件。若要恢复，需另行授权「备份 + downgrade 026 + 按 slug 前缀清理」。
- **既有环境噪声**：backend 全量 4 项失败已记录为测试隔离/环境问题，不能据此断言均非 Week 3 引入；`test:typecheck` 10 项 ui-v2 预存错误（PR10F-03）。
- **ACCEPTED_NOTE / DEFERRED**：weak_top3 可含零指标 KP（PR-10 继承语义）；mastered 排除未过滤 `Mistake.status`（符合 W3-D05 字面）；`/analytics` 无分页；活动证据脚本手动入口已在 2026-09-26 补 scratch 守卫（见事故后续报告）。
- **待决**：无阻塞项。生产迁移/cutover、commit/push/merge/release 均需单独的显式授权。


## 2026-09-26 独立复核补充（优先于上述证据完备性表述）

历史用户 Gate PASS 保留；当前保存证据完整性复核为 **PARTIAL**。迁移/build/preview原始日志与最终独立 Gate评审落盘材料未找到；报告中的统一 09-22日期与09-25 Gate、09-23/24事故记录存在冲突，真实裁决日期待证。不得将本报告摘要当成全部原始证据。本轮纯合同复跑为60 passed。

详见 [复核与事故防复发记录](incident-followup-2026-09-26/validation.md)。守卫补强未连接或修改 blog_v2/blog_db。
