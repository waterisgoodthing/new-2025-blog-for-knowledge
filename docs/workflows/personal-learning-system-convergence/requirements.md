# Requirements — 个人学习系统受控收敛工程

> 基线事实编号（F1–F12）见 [README.md](README.md) 第 4 节。每条需求包含：背景、需求、验收标准。
> 验收状态只允许 `PASS / PARTIAL / FAIL / BLOCKED / NOT_VERIFIED / NOT_AUTHORIZED`。
> 涉及界面、交互、动效、响应式与无障碍的实现同时受 [ui-design.md](ui-design.md) 约束；该文件是目标态 UI 合同，不扩大本 30 天计划已批准的实施范围。

---

## Week 1 — 运行可信度（M1: TRUSTED RUNTIME）

### R31 — Production Artifact Integrity（第一优先级）

**背景**：审查观察到 16 个引用资产中 8 × 200、8 × 404。build 成功不能证明 production 正常。

**需求**
1. 生产构建路径修正（F14）：`npm run build` = `next build`（纯 Next 构建）；OpenNext 产物为 `npm run build:cf`。Production runtime 验证必须使用 `build:cf` 产物 + 实际 production 启动方式（不得用 `next dev` 代替）。
2. 提供 smoke 检查：`GET /` → 解析 HTML 中 `<script src>` / `<link href>` → 逐个请求并要求 HTTP 200。
3. Gate：`referenced = successful`，`404 = 0`，才允许发布。
4. `HTML_n ↔ Assets_n` 同源（禁止混合窗口）定性为 **deployment/release gate，不属于 smoke 能证明的范围**：smoke 只证明"某次响应引用的资源可访问"。实现方式 = 整 artifact 部署 + 流量切换 + **post-deploy smoke**（对生产 URL 重跑同一脚本）；若现有部署机制无法保证原子切换，如实记录为 `PARTIAL` 并禁止宣称满足，本周期不为此构建新部署平台。
5. 运行拓扑（backend/PG/前端启动命令、`/api/health` 探针、seed fixture）在 Phase 0 T-00b 定版并留证据（D12）。

**验收**
- 本地复现 production 启动（`build:cf` 产物）+ smoke 脚本，输出引用资产计数与 404 计数。
- smoke 脚本可退出码非零阻断发布；post-deploy smoke 写入发布 runbook。
- smoke 纳入 CI Job 3（T-00b 拓扑定版后）。

### R03 — 恢复写作（Note / Blog authoring）

**背景**：`Dashboard → /write-note → Dashboard` 自循环（F8）。

**需求**
1. 建立路由：`/manage/notes`、`/manage/notes/new`、`/manage/notes/[slug]`（标识符定版为 slug，沿用现有 notes API 语义，F16；PR-02 不改 API）。
2. Blog 共用 Note 模型：`/manage/notes/new?type=note` 与 `?type=blog`。
3. 编辑器收敛：只保留一个 `ContentEditor`，不新建 BlogEditor/NoteEditor/ArticleEditor 三个系统。
4. `/write`、`/write-note` 旧实现按三阶段迁移：① redirect 到新编辑器 → ② 内部链接全部迁移 → ③ 删除旧实现（本周期至少完成 ①②；③ 需单独批准）。redirect 必须保留，避免旧 Bookmark 404。
5. 不得继续同时维护旧编辑器与 Workspace 两套页面。

**验收**：新建 Note PASS、编辑 Note PASS、新建 Blog PASS、旧 `/write*` 路由 redirect 到新编辑器且不 404。

### R32 — Fresh DB Guestbook 表

**背景**：`guest_messages` 无 Alembic migration（F6），`alembic upgrade head` 的空库缺 Guestbook 表。

**需求**：新增 migration，使空 PostgreSQL 经 `alembic upgrade head` 后包含 Guestbook 表；不依赖运行时 `create_all()`。

**验收**：空库 `alembic upgrade head` → 应用启动 → Guestbook 表存在且可读写。

### R03b — Loading / Empty / Error 状态整改

**背景**：当前 `API Failed → "暂无内容"` 是错误产品语义。

**需求**
1. 使用 Next.js App Router 原生 `loading.tsx` / `error.tsx`，不自建框架。
2. 建立单一组件 `AsyncStatePanel`，支持 `loading / empty / error / retry` 四态。
3. 涉整改的页面必须区分三态；API 失败不得显示为"暂无内容"。

**验收**：目标页面 API 失败显示 Error 且 Retry 可执行；空数据显示 Empty；加载显示 Loading。

**Week 1 Gate（全部满足才进入 Week 2）**

| 验收 | 标准 |
| --- | --- |
| Fresh build | PASS |
| Static assets | 100% HTTP 200 |
| /notes | 可读取 |
| 新建 Note / 编辑 Note / 新建 Blog | PASS |
| API failure | 显示 Error |
| Retry | 可执行 |
| Fresh DB | Guestbook tables 存在 |
| Existing tests | 无回归 |

---

## Week 2 — 关闭复习闭环（M2: CLOSED REVIEW LOOP）

### R01 — ReviewItem 状态机与调度语义

**背景**：`rating=0 → repetitions+1` 违反"repetition 表示学习推进"（F1/F2）。

**需求**（语义定版见 design D2，不在此重复讨论间隔取值）
1. `ReviewItem.state` 从 `active / paused` 扩展为 `active / mastered / paused`（migration + model + CHECK 约束 + schema + client 同步，见 F3）。
2. 失败（rating 0/1/2）：`repetitions = 0`，`state = active`，即 **lapse**；rating=0/1 → 1d，rating=2 → 2d（定版，无"二选一"）。
3. 成功（rating ≥ 3）：`repetitions += 1`，按连续成功次数取阶梯 3d/7d/14d/30d（定版于 D2）。
4. Mastery 触发时点定版：每次成功提交后立即评估 `repetitions >= 4 AND last_rating >= 4` → `state='mastered'`；`ReviewItem` 新增 `last_rating` 列承载判定依据；"当前 streak 无 lapse"由 v2 的 repetitions 语义自动蕴含（D2）。
5. `ReviewRecord` 增加 `previous_state / new_state` 列（F4），回答"这道题什么时候真正掌握的"。
6. 保留既有乐观并发（F10），Case D 并发测试必须继续通过。

**验收（状态机边界测试，property-style）**
- Case A：rating=1 → `repetitions=0`、`state=active`、interval 缩短。
- Case B：4→4→5→4 成功序列 → `state=mastered`。
- Case C：mastered item 不出现在 due queue。
- Case D：并发提交 → 乐观并发仍正常拒绝。

### R02 — Re-answer

**需求**
1. Review 流程改为：`Mistake → Re-answer → Evaluation → Rating Recommendation → User Confirm → ReviewRecord`。
2. 题型判定策略：
   - 自动：`single_choice / multiple_choice / true_false`；
   - 半自动：`numeric / short_answer`（normalized answer / tolerance，仅当题目有明确机器判定规则）；
   - 人工确认：`essay / proof / open-ended`。
   - 禁止裸 `submitted_answer == correct_answer` 作为唯一判定。
3. Re-answer 复用 `Attempt`，不新建 Review-only Answer 表；`Attempt` 增加 `context_type`（`practice / review / editor_check`），不新增多个 Attempt 模型。
4. **Re-answer ↔ ReviewRecord 可审计关联**：`ReviewRecord` 新增 `attempt_id`（nullable FK），re-answer 流程提交必填并验证归属（attempt 存在、`context_type='review'`、与 `Mistake.question_id` 匹配（非空时））；纯评分（无 re-answer）与 question_draft 来源 mistake（无对应 Question）允许空 `attempt_id`——取舍明确记录（D5）。
5. Re-answer 结果直接驱动 R01 状态机（lapse / progression / mastered）。

**Week 2 Gate（整个 30 天最重要的验收流程，须人工完整走通）**

```
Question → wrong Attempt → MistakeDraft → Mistake → ReviewItem
→ re-answer → wrong → lapse → 再次到期 → correct × N → mastered
```

---

## Week 3 — Single Source of Truth（M3: CANONICAL LEARNING）

### R04 — Legacy Mistake Cutover

**背景**：公共 `/mistakes` 现读 legacy `Note(type='mistake')`（F9）。

**需求**
1. 顺序：`Prepare Schema/API/Tooling → Freeze Legacy Writes → Dry-run/迁移 → Verify → Read Cutover → Observe → 后续另行退役旧读路径`。不直接删旧表；生产迁移与公开切换需要单独授权。
2. Step A：准备 migration 031、新 public/admin API 与 dry-run 工具，但不切换公共读取。
3. Step B：停止所有可令 Note 成为 `type='mistake'` 的写路径，包括 create、update 改 type、promote 和旧写入 UI；保留兼容读取。
4. Step C：通过现有 migration-026 ledger/idempotency 管道的新 mapping version 迁移执行时盘点出的 legacy mistakes；先 dry-run，再写入，再对账。**公开映射规则定版**：来源 Note `status='published' AND hidden=false` → `'public'`，否则 `'private'`（Note 无单一 public 字段，F16）。不修改 migration 026 的数据库治理结构，也不得绕过其 provenance/冲突检测。
5. Step D：对账通过且无未决公开来源后，公共 `/mistakes` 才改读 canonical `Mistake`。`visibility` 列已存在但 CHECK 锁定 `'private'`（F13）——migration 必须**替换**该 CHECK 为 `IN ('private','public')`（F13），并增加 admin-only 发布入口；不做完整 publication workflow。公共读仅返回 `status='active' AND visibility='public'`，使用独立 public allowlist DTO，遵守现有会话契约。
6. 前端 API client（`src/lib/api/mistakes.ts`）与后端 schema 同步（DTO 变更跨层 reconcile，见 AGENTS.md 契约纪律）。

**验收**：公共 `/mistakes` 数据来自 canonical Mistake；迁移脚本可重放且幂等；迁移前后数量与 visibility 映射核对一致；若无 public mistake，页面为显式 Empty（正确行为，不回退 legacy 数据源）；legacy 读路径观察到读取切换。

### R05 — KnowledgePoint Analytics

**需求**
1. 最少四指标：`attempt_count / wrong_count / review_count / due_count`。
2. 派生：`accuracy = correct_attempts / graded_attempts`；`wrong_rate = wrong / attempts`。
3. Weakness 第一版采用**排序规则**（而非加权分数）：`wrong_rate DESC → lapse_count DESC → due_count DESC`；排序规则易于解释、测试、维护。

**验收**：指标计算有单测覆盖（含除零/无 attempt 样本）；Dashboard 薄弱知识点来自 canonical 数据。

### R05b — Dashboard 第一版

**需求**：不做复杂 ECharts。只显示：今日复习 N、今日练习 N、薄弱知识点 Top3、最近掌握 4 个。目标：10 秒钟知道下一步做什么。数据全部来自 canonical entities，不是 legacy Note 文本。

**验收（Week 3 Gate）**：Dashboard 真实回答三问——今天复习什么？今天练什么？最弱知识点是什么？

### R06 — Note ↔ KnowledgePoint 正式关联

**需求**
1. 新建关联表 `NoteKnowledgePoint(note_id, knowledge_point_id)`，Unique `(note_id, knowledge_point_id)`，明确 FK。
2. 不复用 polymorphic `KnowledgePointLink.target_id VARCHAR` 承载此核心 domain relationship。
3. Model / migration / schema / API client 跨层同步。

**验收**：fresh DB 建表 PASS；重复关联被 Unique 约束拒绝；关联/解除关联 API 有测试。

### R09 — Daily Practice

**需求**
1. 第一版只做 admin-only `GET /api/admin/practice/today`：候选充足时返回 3–10 题；候选不足时返回实际数量（可为 0）+ 显式 empty 语义。上限 10 硬性；`3` 不是无条件下限。
2. 选题主链：weak KP → unarchived Question → recently not attempted；排除 already mastered mistake targets。
3. 不做练习平台。比例策略（如 50/30/20）为可选增强，第一版 "weak KP first" 已足够。

**验收**：候选充足样本返回 3–10 区间；候选不足样本返回实际数量且前端呈现 Empty；weak KP 优先级有测试；mastered 排除有测试。

---

## Week 4 — Reliability Gate（M4: RELEASE GATE）

### R10 — OCR 诊断（先诊断，不先重写）

**背景**：当前 31/31 failed。

**需求**
1. 失败分类：`provider_auth / provider_timeout / invalid_model / invalid_response / schema_validation / image_fetch / image_format / unknown`。
2. 统计 `capture_recognition success_rate` 并可观测。
3. 10 个受控样本 ≥ 8 次成功 pipeline completion；失败必须 **visible / retryable / diagnosable**。
4. 若仍失败：禁用入口或明确标识不可用——不允许 0/31 模块继续作为主要学习入口而不标示。

**验收**：失败分类报告 + 10 样本结果记录；入口状态明确（可用 / 显式禁用）。

### R11 — AI Governance

**需求**
1. **先分类再治理**：polish 现为流式预览（F17），结果仅随用户保存落库 → 定版为 **transient preview**，不强制 governance 链与 `target_id`；该决策记录在案，未来 polish 直接持久化时必须先入链。强制链路 `Prompt Registry → Gateway → AiRun → Validation → Human Confirm` 适用于**产出持久化学习数据**的生成（如 capture→recognition/draft/question）；Diagram 若仅视觉辅助可后处理。
2. AiRun 审计补全：凡基于已有实体（Note / Question / Mistake / Capture）生成，必须记录 `target_type / target_id`；**创建型生成**在 Human Confirm 创建实体后回填，未创建（建议被放弃）留空为合法状态；不为此建立 event sourcing。

**验收**：polish 分类决策已记录；产出持久化数据的新增调用点 AiRun `target_id` 非空（创建型以"确认后回填"口径抽查）。

### R33 — WebAuthn Challenge 修复

**背景**：W3C WebAuthn Level 3 要求 challenge 由可信环境随机产生、严格匹配、临时保存、生命周期接近 ceremony timeout。当前如存在 `global_dict["current"]` 共享 challenge 则必须替换。

**需求**
1. 新表 `WebAuthnChallenge(id, challenge_hash, purpose, session_id, user_id, created_at, expires_at, consumed_at)`，其中 `purpose` 必须覆盖现有**三类** ceremony（F15）：`registration / authentication / operator_registration`；operator-registration 保持按 `session_id` 取 challenge 的现有语义。
2. 流程：`generate → store → verify → consume`；challenge 单次消费（原子 consume）、按 purpose + 绑定键双重隔离、过期清理。
3. `passkey_service.py` 三套全局 dict store（含 `["current"]` 单键）全部替换为该表，不复用任何全局字典；验证时严格比对 challenge。

**验收**：并发两次同类 ceremony 第二个 challenge 不覆盖第一个；跨 purpose/绑定键不串用；过期 challenge 被拒绝；已消费 challenge 被拒绝；三类 ceremony（含 operator registration）现有流程语义保持。

### R34 — Login Throttling

**背景**：OWASP 建议对认证失败做 throttling；账户维度比 IP 更重要，自动化攻击应账户+IP 双维度。

**需求**
1. 双维度：`account failures` + `IP failures`。
2. 递增延迟而非永久锁定，示意：1–3 → 正常；4 → 2s；5 → 5s；6 → 15s。
3. 阈值与延迟必须是配置项（`backend/app/config.py`），单用户项目不做复杂防欺诈。

**验收**：连续失败触发延迟且延迟递增；成功登录后计数按设计重置；配置可调；有单测。

### R22 — CI 最终 Gate

**需求**：四个 Job：

| Job | 内容 |
| --- | --- |
| 1 Frontend | `npm ci → tsc → test:typecheck → vitest → next build` |
| 2 Backend | install → PostgreSQL service → `alembic upgrade head` → `pytest` |
| 3 Runtime Smoke | 按 T-00b 定版拓扑：`build:cf` → production start（前端 + backend + PG）→ `GET /` verify chunks → `GET /notes` → API health |
| 4 Critical E2E | 3–5 条 Playwright，`workers = 1`（CI 稳定性与可复现性优先） |

> Job 3/4 的启动命令、端口、环境变量、seed fixture 以 Phase 0 T-00b 实测证据为准；T-00b 未定版前 Job 3/4 不进入 CI（D13）。

**验收**：四个 Job 全绿；Job 2 在空库上验证 migration；Job 3 复用 R31 smoke（pre-deploy 段）。

### R22b — 关键 E2E（只保留五条）

| ID | 流程 |
| --- | --- |
| E2E-01 | login → dashboard |
| E2E-02 | create note → edit → save |
| E2E-03 | question → wrong attempt → mistake draft |
| E2E-04 | mistake → review → re-answer → review record |
| E2E-05 | API failure → error state → retry |

### Legacy Cleanup

**需求**
1. 顺序（绝不一次大清理 PR）：`Stop write → Switch read → Observe → Remove frontend → Remove endpoint → Remove service → Remove DB columns/table later`。
2. 适用：legacy review、legacy weak point、legacy mistake、`/write*`、旧 `/manage`。
3. 删除候选（本周期内）：旧 Review API Client、旧 SM-2 caller（F11）、无调用 WIP Components、Dashboard broken quick-action tests、Jobs/Analytics duplicate surfaces、unused API endpoints。
4. 删除前必须以 grep/static reference + tests + 可用 runtime logs 三类证据确认无引用。

**验收**：每个删除项有证据记录；删除后全部 CI Job 绿。
