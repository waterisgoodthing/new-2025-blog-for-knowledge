# Week 3 架构与数据流专项审计

## 结论

**PARTIAL。** 当前源码包含 W3-00、PR-09～PR-13 的主要结构和业务实现，但 Week 3 尚不能作为已完整交付：旧 `Note(type='mistake')` 冻结有一个经事务回滚 probe 观察到的后端元数据写入口绕过；从题目错答生成的 draft/mistake 未继承 Question 的 KP，导致 attempt 指标与复习指标断链；练习/复答对多选答案的评分和输入语义不一致。PR-13 本身是**选题管线**，不要求建设独立练习会话；现有题目编辑页仍提供“作答验证”并能提交 practice Attempt。该结论不是 Week Gate 或总体完成率判断。

本专项按只读方式检查当前工作树，未执行数据库操作、测试或浏览器操作。工作树本来就有大量未提交更改；只写本报告。主 Agent 随后提供了本轮 fresh PG16 空库升级至 033、全后端 922 passed/9 skipped/47 subtests、前端 522 PASS、两套 tsc 与 Node 24 build PASS，以及 Playwright Chromium 5/5 的结果；这些是主 Agent 提供的本轮证据，不是本专项独立执行。5 个 E2E 覆盖登录/仪表盘进入、笔记创建、capture 草稿、review 再答与记录、公开笔记错误重试，不覆盖今日练习选择→作答及完整 Dashboard 数据逐值追溯。专项目录中的 probe 输出和截图按其记录作为主 Agent 提供的本轮观察证据；冻结 probe 使用覆写的 admin dependency 并回滚事务，不证明外部认证配置，也未持久化修改。历史 Week3 evidence、测试日志、截图和门禁声明不作为本轮验证。

## 任务矩阵

| ID | Expected | Actual（当前源码） | Evidence | Status | Risk |
|---|---|---|---|---|---|
| W3-00 | 锁定 030 基线、数据/接口合同、legacy 写读清单，提供 scratch-only runner | 合同/守卫代码和测试文件存在；当前 migration 源码链为 031→032→033。没有在本专项重跑 head/守卫，也没有核查其运行目标。 | B：`scripts/week3-scratch-guard.py`、`backend/tests/test_week3_contracts.py` 存在；C：migration 文件链。无本专项 A。 | IMPLEMENTED_UNVERIFIED | 中 |
| PR-09 | canonical 公共错题 allowlist；031 visibility；legacy mistake 写冻结；026 ledger 新映射可审计 | 公共 API 仅查询 active+public 并返回独立 DTO；管理端有 visibility 更新；031 downgrade 对 public 行 fail-closed；Wk3 migration runner 源码存在。notes/review 写入口有冻结，但 `/api/ai/suggestions/execute` 仍可改 legacy mistake Note 的 tags/folder。 | B：`backend/app/routers/public_mistakes.py:12-30`、`backend/app/services/mistake_service.py:195-215`、`backend/alembic/versions/031_mistake_visibility_public.py:51-102`、`backend/app/routers/notes.py:243-257,329-343,455-491`、`backend/app/routers/review.py:38-58`、`backend/app/routers/suggestions.py:32-78`。 | PARTIAL | 高（P1 冻结范围不完整） |
| PR-10 | service-owned KP 指标、稳定弱点排序、admin-only API、前后端 DTO 一致 | 单条聚合查询实现 attempt/wrong/review/due/lapse，按 PR-10 排序；API、Schema 与 TS client 均存在。`Attempt.is_correct` 为 NOT NULL，所以当前表不可能有 NULL 被计入正确数；但无“未判定”状态，practice essay 仍由上游裸字符串比较强行打 Boolean。详见下文“D7 口径”。 | B：`backend/app/services/kp_analytics_service.py:47-168`、`backend/app/models/attempt.py:11-27`、`backend/app/routers/knowledge_points.py:44-49`；主 Agent 提供后端测试结果为 A。 | COMPLETE_WITH_DEBT | 中（指标语义） |
| PR-11 | 单一 canonical Dashboard 答复今日复习、练习、最弱 Top3、最近掌握4及确定性优先动作 | Summary 汇总 ReviewItem、PR-10 Analytics、PR-13 Practice；页面通过 Dashboard client 展示。最近掌握查询使用 ReviewRecord 最新转换及当前 ReviewItem 状态。weak/recently-mastered 子查询失败会分别被吞成空数组，响应没有对应 unavailable 标志；并且零样本 KP 仍可能进入“最弱 Top3”。 | B：`backend/app/services/dashboard_service.py:119-203,257-327`、`backend/app/routers/dashboard.py:30-75`、`src/lib/api/dashboard.ts:39-88`、`src/app/manage/(workspace)/dashboard/dashboard-content.tsx:11-40`。主 Agent 提供代码测试/build 结果为 A；本专项未查真实浏览器。 | COMPLETE_WITH_DEBT | 中（看板可能把缺数据显示为空/弱点） |
| PR-12 | migration 032 建立 UUID Note↔INTEGER KP 外键关联，admin-only link/unlink 和 TS client | 联合主键、双 CASCADE FK、反向索引、service、admin router/client 均已实现。重复 link/unlink 是幂等 no-op；POST 重复时 router 仍返回 `linked=true`。新关系尚无页面消费者，也未接入 KP 分析/练习链。 | B：`backend/alembic/versions/032_note_knowledge_points.py:49-103`、`backend/app/services/note_knowledge_point_service.py:24-125`、`backend/app/routers/admin_notes.py:20-93`、`src/lib/api/notes.ts:194-221`。主 Agent 提供后端测试结果为 A。 | COMPLETE_WITH_DEBT | 中（新关系孤立于学习主链） |
| PR-13 | admin-only 确定性今日选题，过滤近期 practice/mastered，最多 10 个且无答案字段 | 服务调用 PR-10 排序、从 active Question↔active KP 生成候选、排除近 7 日 practice Attempt、返回理由/Empty metadata；router/schema/client 存在且选题 API 不创建 Attempt。候选≥3时固定返回 3（符合 task 细化约定）。practice 页面链接至 QuestionEditor；编辑页含“作答验证”，调用 `submitAttempt` 记录 practice Attempt，错答后导航到 MistakeDraft。`stable_order_fallback` 未翻译；编辑页加载失败是普通文本且无重试。归档正常路径会将关联 ReviewItem 置 paused，因此 mastered 排除未加 `Mistake.status` 谓词属防御性不足，未证实正常流可误排。 | B：`backend/app/services/practice_service.py:86-196`、`backend/app/routers/practice.py:9-20`、`src/app/manage/(workspace)/practice/practice-today.tsx:27-88`、`src/app/manage/(workspace)/questions/components/question-editor.tsx:25-33,125-153`、`src/lib/api/attempts.ts:15-20`、`backend/app/services/mistake_service.py:217-223`。主 Agent提供测试结果为 A；专项目录的 probe-learning、probe-multiple-choice 与截图为附加运行观察证据。 | COMPLETE_WITH_DEBT（选择管线）；独立 practice-session UX 未实现且在 PR-13 scope 外 | 中 |

## 当前数据流与权威边界

```text
Subject (PostgreSQL)
  └─ KnowledgePoint (subject_id FK, parent tree)
      ├─ QuestionKnowledgePoint ─ Question
      │    └─ Attempt(context_type='practice')
      │         └─ wrong → MistakeDraft (KP 未继承) → 人工确认/转换 → Mistake (KP 仍需手工补救) → ReviewItem
      └─ KnowledgePointLink(target_type='mistake', target_id)
           └─ Mistake → ReviewItem → ReviewRecord

ReviewRecord ── rating/state/schedule ──> ReviewItem
  ├─ PR-10 lifetime lapse/due/review aggregates
  ├─ PR-11 recent mastered + due count
  └─ PR-13 mastered exclusion

Note ── NoteKnowledgePoint ── KnowledgePoint   [新建的独立关联，未被以上统计消费]
```

- **实际主链**：`Subject → KnowledgePoint → Question → Attempt → MistakeDraft → Mistake → ReviewItem → ReviewRecord`。错答先生成 Attempt 和 MistakeDraft，之后要经过 draft 转换才成为 canonical Mistake/ReviewItem；`attempt_service.create_mistake_draft_for_attempt` 没有将 Question 的 `knowledge_point_ids` 放进 `MistakeDraftCreate`，因此后续 KP review 聚合断链。见 `backend/app/services/attempt_service.py:23-70`、`backend/app/services/mistake_service.py:56-77,128-169`、`evidence/probe-learning.txt`。
- **复习反馈**：Review UI 先加载 ReviewItem/Mistake/Question，可选提交 review-context Attempt，再提交用户确认的 rating；Review service 持久化 ReviewRecord 并更新 ReviewItem interval/repetitions/state/next_due。`mastered` 是固定调度下连续成功计数（4 次且 rating≥4），不是独立掌握度模型。见 `src/app/manage/(workspace)/review/review-queue.tsx:108-159`、`backend/app/services/review_item_service.py:21-26,62-81`。
- **练习候选**：通过 `QuestionKnowledgePoint` 收集题目，按 PR-10 全量弱点顺序选一个最弱关联 KP，再排除近期 Attempt 和 mastered item。选题只返回题目 ID/KP ID/理由；页面把题目链接到编辑页，编辑页已有自由文本作答验证并提交 Attempt。这里没有独立 practice-session UX，但 PR-13 只承诺选题管线，不将此缺口算作 PR-13 未交付。作答仍有多选输入语义问题（见下文和前端专项）。
- **统计数据回流**：Attempt 统计沿 `QuestionKnowledgePoint`；ReviewRecord 统计沿 `KnowledgePointLink → Mistake → ReviewItem → ReviewRecord`；Practice 排序复用 PR-10；Dashboard 再汇总这两条。ReviewItem 同时保存 `mistake_id` FK 和 `target_id` 文本，两种读取方式并存，缺少数据库约束证明两值恒等。
- **存储 owner**：当前 Subject/KP/Question/Attempt/MistakeDraft/Mistake/ReviewItem/ReviewRecord/Note/NoteKnowledgePoint 均由 PostgreSQL/FastAPI 所有；Next.js 使用 API clients。PR-09 canonical 公共错题也从 PostgreSQL Mistake 读取。Legacy `Note(type='mistake')` 仍在同一 notes 表中由旧 API/SM-2/建议统计读取。public blog/note 与学习主链所有权不在本专项范围内，不推断其静态发布来源。

## 横向架构与质量

| 维度 | 判断 | 当前证据与缺口 |
|---|---|---|
| Architecture | PARTIAL | 已有 canonical 主链，但 KP 归属有 `QuestionKnowledgePoint`、多态 `KnowledgePointLink`、`NoteKnowledgePoint` 三种关系；其读写责任不同且部分复制。PR-12 新关系未替代或供给现有学习分析。 |
| Frontend | PARTIAL | Dashboard 使用 canonical summary；public 错题列表用 canonical `/api/public/mistakes`。但公开页管理员附带的 stats/plan 仍由旧 `/api/review` Note 查询供给；今日练习跳转到 QuestionEditor，而该页的多选答题入口没有多选交互；`stable_order_fallback` 理由直出英文枚举。具体交互审查见 `frontend-quality.md`。 |
| Backend | COMPLETE_WITH_DEBT | router→schema→service→ORM 边界基本清楚，核心 PR 服务存在；Dashboard 对 weak/mastered 子查询异常降级为空，Review due list 按 item 逐条取 Mistake。 |
| Database | PARTIAL | 031/032 源码约束/外键设计可读，主 Agent 报告 fresh PG16 链至 033；本专项未独立回放。032 是新表，没有把历史 Note.KP 字符串迁入新关联。 |
| API | COMPLETE_WITH_DEBT | 端点、Pydantic schema 和 TS client 存在；PR12 重复写返回幂等成功语义，和任务文档错误语义需主 Agent复核。公共 DTO 没有 `my_answer`。 |
| UX | PARTIAL | Review queue 有再答、人工评级、历史记录；PR-13 选题可通过 QuestionEditor 的“作答验证”写 practice Attempt，但它落在编辑表单内且当前选择题界面不能表达多选；错题公共列表与管理员旧 review 数字并列，可能产生双代口径混淆。 |
| Testing | PARTIAL | 主 Agent提供后端/前端/tsc/build 与 Chromium 5/5 当前结果；E2E 集合未包含今日练习选择→作答，也没有 Dashboard KPI 数据逐值追溯。专项目录另有主 Agent 提供的跨端 probe；本专项未重跑测试。 |
| Maintainability | PARTIAL | Analytics/Practice/Dashboard 复用关系较好；重复 KP 映射、ReviewItem 双 target ID、Legacy Note 仍供统计/复习、多个路由可写 Note 元数据增加后续切换成本。Review due 队列 N+1。 |

### P1、SURFACE_COMPLETE、NOT_IMPLEMENTED

- **P1：Legacy freeze 仍可绕过。** `backend/app/routers/suggestions.py:32-78` 对 `Note` 执行 `add_tag` 和 `move_to_folder` 时没有调用 freeze guard，目标可为 `type='mistake'`。`evidence/probe-freeze.txt` 记录了真实 handler/service/PG 的 folder metadata mutation 成功，但覆写了 admin dependency 并回滚事务；它证明该写入路径可达，不证明外部认证配置，也没有持久化修改。冻结 guard 源码调用点未覆盖此 router；需主 Agent核对冻结合同是否包含标签/文件夹元数据并按合同裁定 PR-09。
- **P1：错答未保留 Question 的 KP 身份。** `attempt_service.create_mistake_draft_for_attempt` 创建 Draft 时未传 KP IDs；probe 直接观察到 Question KP=1、Draft/Mistake KP 均为空。Practice attempt/wrong 增加，但该错题后续的 ReviewRecord 无法进入该 KP 的 review/lapse/due 指标；MistakeDetail 的 KP 选择器是手工补救，不是自动回填。这影响跨周弱点/复习闭环，建议列为数据关联修复优先项。
- **P1：多选答案 UI 和 scorer 不一致。** ReviewQueue 的选项按钮每次只把 `answer` 替换为一个 key。主 Agent提供的浏览器 probe 点击 A、C 后只有 C 的 `aria-pressed=true`，提交值为 `C`，并得到 incorrect；同目录 probe 还显示 practice 对 `"A C"`、`"a,c"` 均返回 false，而 re-answer 对两种格式都返回 correct。选择 UI、两个 scorer 的契约不一致，错误会产生不准确的 attempt/wrong 和 draft。需按产品规则统一多选选择/序列化/评分。
- **闭环范围澄清：今日练习选择页面。** PR-13 选题端点只返回题目候选，这是其声明范围；界面链接到 QuestionEditor，那里已有自由文本“作答验证”、`submitAttempt` 及错答转 Draft。因此不能将 PR-13 标为 `SURFACE_COMPLETE` 或声称完全没有 practice Attempt 路径。独立、面向练习的 session UX 仍未实现，但属于后续 UX 范围，不是 PR-13 验收失败。
- **NOT_IMPLEMENTED：Note↔KP 消费端。** 关系表及 API 已实现，但除 service/router/client 和 API 单测外，当前没有笔记编辑/详情消费者；KP analytics、practice、Dashboard 也不读这张表。PR-12 的 API/client 目标已达，关系到学习决策的产品用途仍未实现。
- **无 P0 可由本次源码检查确认。** 这不构成数据库一致性或安全门禁通过声明。

## D7 attempt/graded 口径裁定（供主 Agent复核）

**NULL 不是当前 Attempt 表的可达状态。** `Attempt.is_correct` 在 ORM 为 `nullable=False`，migration 021 创建列也设为 `nullable=False`。因此 PR-10 `COUNT(Attempt.id)` 不会把 NULL 当“正确”；按当前表约束它把所有 practice Attempt 当分母，并把 `is_correct=false` 计为错。代码实现了 task 中 `attempt_count=practice attempts` 与 `wrong_count=false` 的定义。

**未判定答案语义仍存在合同空档。** `requirements.md:98-102` 与 `design.md:68-85` 明确 Re-answer 对 essay/proof/open-ended 应人工确认、禁止跨题型裸字符串相等；该段以 Review 的 re-answer 流程为上下文，而普通 practice endpoint 调用 `attempt_service._is_correct`，对非 bool/list 一律 `submitted == expected`，然后写入 NOT NULL Boolean 并在 false 时自动建 mistake draft。故：

1. 这不是“NULL 被 analytics 当成正确”的实现错误；当前 schema 禁止 NULL。
2. PR-10 自身的 D7 聚合公式符合其 `COUNT practice attempts` 与 `wrong/attempts` 口径；任务正文同时写“accuracy/wrong_rate 用 graded denominator”，但数据模型没有 `graded` 或 `needs_human` 状态，设计文本对分母也一处写 graded、一处写 attempts，属于 **B：Planned but Insufficient** 的合同与模型不足。
3. 普通 practice 是否必须遵守 D5 的 essay 人工判定仍需主 Agent确认领域适用范围。若适用，则 `_is_correct` 对 essay 是实现违约；若 D5 只约束复答，仍建议限制 practice 题型或扩展 grading state，避免把主观答案塞入统计分母。

## P1/P2 风险与 Future Work 分类

| 类别 | 发现 | 建议方向 |
|---|---|---|
| A — Planned but Unfinished | PR-09 冻结覆盖不完整（suggestions 元数据 mutation）；当前 assignment 未取得本轮真实 Chromium 的 public/admin 与 Dashboard 数据行追溯证据。 | 先完成冻结入口审查/修正与定向验证；主 Agent核实其 fresh DB/UI验证记录是否覆盖任务 acceptance。 |
| B — Planned but Insufficient | `graded` 概念与 Attempt 的必填 Boolean 冲突；essay 普通 practice 自动裸字符串判断；三个 KP 关联体系无统一 owner；Dashboard 可把零样本 KP 显示为最弱项。 | 明确机器评分资格与未判定状态；限制 weak Top3 至有证据样本或显式标“暂无作答样本”；建立关联迁移/一致性策略。 |
| C — Newly Recommended Future Work | 若产品要提供独立练习体验，可把候选链接接到不暴露题目编辑字段的练习页，复用既有 Attempt 提交/错答 Draft 路径并明确 feedback；另可评估将 ReviewItem 的 target 文本副本收敛为 `mistake_id` 权威引用。 | 作为 PR-13 之外的 UX work item；先明确具体场景和评分规则。 |

P2 维护风险：`review_item_service.list_due_items` 先读 due items 后逐行 `session.get(Mistake, ...)`，队列会产生 N+1；practice `stable_order_fallback` UI 显示原始枚举；PR-09 public list 每行独立查 KP link（另一个 N+1）。这些不是当前 Week Gate 的已证实阻断项。

## 主 Agent复核清单

1. 核对 `/api/ai/suggestions/execute` 是否纳入 F-1～F-9 冻结范围，并据此裁定 PR-09；probe 仅证明受覆写 admin dependency 的 handler 路径可写。
2. 优先裁定并修复 Question KP → MistakeDraft/Mistake 的数据关联保留，否则 Attempt 与复习弱点指标无法对齐。
3. 统一多选题选择 UI 和 practice/re-answer scorer 的接受格式；区分 D5 essay 人工判定是否适用于普通 practice。
4. 按 archive 正常状态转移复核 Practice mastered 谓词：archive 已把 item 置 paused，因此当前漏掉 Mistake.status 条件是防御性不足，未证实正常流程可达错误排除。
5. 主 Agent的 Chromium 5/5 未覆盖今日练习，也未追踪 Dashboard KPI 行值；需定向补证 PR-09/PR-11 实际页面显示和数据来源。历史 Week3 screenshots 不替代本轮证据。
6. 决定 PR-12 Note↔KP 暂时作为独立关联 API 保留，还是未来要接入笔记 UI/知识点参考内容流。不得把该表描述为已供给 KP mastery/weakness 统计。
