# Design — 个人学习系统受控收敛工程

> 事实源：README.md 第 4 节 F1–F12（已在 `4a954ea` 代码核实）。所有 schema 变更跨层 reconcile：model → migration → schema → service → router → frontend API client → tests。

## D1 — ReviewItem 状态机迁移（R01）

**现状**（F3）：`review_items.state` CHECK 约束 `('active','paused')`，`server_default='active'`。

**变更**（migration 028）
- `state` CHECK 扩展为 `('active','mastered','paused')`。
- `algorithm` CHECK 由 `= 'fixed_interval_v1'` 扩展为 `IN ('fixed_interval_v1','fixed_interval_v2')`，并将存量行 `UPDATE ... SET algorithm='fixed_interval_v2'`（语义全局切换为 D2；行数量极小、可审计、可回放）。Model `__table_args__` 同步。
- 新增 `last_rating SMALLINT NULL`（D2 mastery 判定依据；存量行置 NULL）。
- Pydantic schema 枚举同步；前端 `src/lib/api/review-items.ts` 类型同步。
- 存量 state 无需回填：现有行只有 `active/paused`，与新枚举兼容；`mastered` 只能由新调度逻辑产生。
- due queue 排除 mastered：现有 `idx_review_items_due(state, next_review_at)` 已覆盖 `state='active'` 查询，`list_due_items` 现有 `state=="active"` 过滤不变（`review_item_service.py:15`）。

**不引入**：learning / relearning / young / mature / graduated 状态（避免 Anki clone）。

## D2 — 调度语义 v2（R01，替代现状 F1/F2）

**现状事实源**：`INTERVALS={0:1,1:1,2:1,3:3,4:7,5:14}`（`review_item_service.py:11`）；失败与成功都 `repetitions+=1`（`:40`）。

**v2 规则**（在 `review_item_service.py` 内实现为 `fixed_interval_v2`；定版如下，不再留"二选一"）：

| 输入 | 动作 |
| --- | --- |
| 失败 rating ∈ {0,1} | `repetitions=0`，`interval=1d`，`state=active`，`last_rating=rating`（lapse） |
| 失败 rating = 2 | `repetitions=0`，`interval=2d`，`state=active`，`last_rating=rating`（温和 lapse 档，定版） |
| 成功 rating ∈ {3,4,5} | `repetitions += 1`；interval 按"连续成功次数"取阶梯：1→3d，2→7d，3→14d，4→30d；`repetitions > 4` 后维持 30d |
| Mastery | 每次成功提交后立即评估：`repetitions >= 4 AND last_rating >= 4` → `state='mastered'` |

**streak / lapse 语义定版**
- v2 下 `repetitions` 恒等于"自上次 lapse 以来的连续成功次数"（失败归零、成功 +1），因此 **"当前 streak 无 lapse"由 `repetitions >= 4` 自动蕴含**，不再作为独立判定项（保留为语义说明）。
- 连续成功次数 = 提交时 `repetitions + 1`（自增后查阶梯），阶梯查询 `min(自增后 repetitions, 4)`。
- rating=5 不跳级：只影响 mastery 判定（`last_rating >= 4`），不影响阶梯进度。
- `ReviewItem` 新增 `last_rating SMALLINT NULL` 列（migration 028），提交时更新；mastery 判定无需扫描 ReviewRecord。存量行 `last_rating` 置 NULL，仅影响 mastery 时机（需再一次成功提交 ≥4 才可能 mastered），可接受并记录。

## D3 — ReviewRecord 状态转换记录（R01）

**现状**（F4）：`ReviewRecord` 有 `rating / previous_interval_days / next_interval_days / previous_next_review_at / next_review_at`。

**变更**：新 migration 增加两列，均为 NOT NULL（带 server_default 回填 `'active'`）：

```
previous_state VARCHAR(20) NOT NULL DEFAULT 'active'
new_state      VARCHAR(20) NOT NULL DEFAULT 'active'
```

- `submit_review` 写入转换前后的 state（含 `mastered` 转换时刻），回答"这道题什么时候真正掌握的"。
- 现有 CHECK `rating BETWEEN 0 AND 5` 不变；新增 CHECK `state IN (...)` 与 D1 一致。

## D4 — Attempt 来源字段（R02）

**现状**（F5）：`Attempt(question_id, submitted_answer, is_correct, mistake_draft_item_id UNIQUE, created_by, submitted_at)`。

**变更**：新 migration 增加一列：

```
context_type VARCHAR(20) NOT NULL DEFAULT 'practice'
```

- 枚举：`practice / review / editor_check`（CHECK 约束）。
- 同一 migration（执行序 030）同时为 `review_records` 增加 `attempt_id` 审计关联，见 D5。
- Re-answer 复用 Attempt，不建 Review-only Answer 表；不新增多个 Attempt 模型。
- 可选索引：`idx_attempts_context_submitted(context_type, submitted_at)` 服务 review 统计查询。
- KP analytics（D7）按 `context_type` 过滤，避免 review 复答污染 practice 统计。

## D5 — Re-answer 判定策略（R02）

Review 页面流程：`Mistake → Re-answer → Evaluation → Rating Recommendation → User Confirm → ReviewRecord`。

| 题型 | 判定 | 说明 |
| --- | --- | --- |
| `single_choice / multiple_choice / true_false` | 自动 | 归一化选项集合比较；multiple_choice 要求集合完全一致 |
| `numeric / short_answer` | 半自动 | normalized answer / tolerance，**仅当**题目带明确机器判定规则 |
| `essay / proof / open-ended` | 人工确认 | 展示参考答案，用户自评 rating |

- 服务端输出 `evaluation: { verdict: 'correct' | 'incorrect' | 'needs_human', recommendation: 0–5 }`，用户可确认或修正后提交 → Attempt（`context_type='review'`）→ R01 调度。
- **Re-answer ↔ ReviewRecord 审计关联**（migration 030）：`review_records` 新增 `attempt_id UUID NULL REFERENCES attempts(id) ON DELETE RESTRICT`。`submit_review` 扩展为接收可选 `attempt_id`：
  - 提交 re-answer 流程时必填 `attempt_id`，服务端验证：attempt 存在、`context_type='review'`；若 `Mistake.question_id` 非空，则 `attempt.question_id == mistake.question_id`；
  - `Mistake.question_id` 为 NULL（question_draft 来源，`mistake.py:18-19`）时无对应 Question 可作答 → 仅走人工确认路径，提交不携带 `attempt_id`（合法取值），ReviewRecord 只记录 rating 与状态转换；
  - 直接在 review 页打分（无 re-answer）同样允许无 `attempt_id`。
  - 该取舍明确记录：**无 re-answer 的纯评分记录不含来源 Attempt，属合法**；有 re-answer 的记录必须可追溯。
- 禁止裸字符串等值判定跨题型使用。
- 判定逻辑置于 service 层（纯函数可单测），router 保持 thin。

## D6 — Legacy Mistake Read Cutover（R04）

**现状**（F9）：公共 `/mistakes/page.tsx` 以 `type:'mistake'` 读 legacy Note。
**现状修正**（F13）：`Mistake.visibility` 列**已存在**（`mistake.py:84`，`String(20) DEFAULT 'private'`），但 CHECK 约束锁定 `visibility = 'private'`（`mistake.py:91`）；`questions` 表同模式（`question.py:173`）。Note 公开性由 `status`（default `'published'`）+ `hidden`（boolean）两个独立字段表达（`note.py:40-41`），**不存在单一 public 字段**。

**变更（四步，顺序不可颠倒）**
1. **Schema/API 准备**：
   - migration 031 将 `ck_mistakes_visibility` 由 `= 'private'` **替换**为 `IN ('private','public')`（列本身不动）；model `__table_args__` 同步；
   - 公共 API 使用独立 allowlist DTO，仅返回 `status='active' AND visibility='public'`；管理 API（`get_current_admin` 边界）返回全部；
   - **公开写入/发布入口**：manage mistakes 编辑页增加 visibility 开关（admin-only），持久化时写入 `visibility`；不建 publication workflow；
   - `src/lib/api/mistakes.ts` DTO 与后端 schema 同步。
2. **Freeze 写入**：所有可令 Note 成为 `type='mistake'` 的入口停止，包括 create、update 改 type、promote 和旧写入 UI（后端 fail-closed，保留兼容读取）。
3. **数据迁移与核验**：执行时动态盘点 legacy mistakes，通过现有 migration-026 ledger/idempotency 管道的新 mapping version 迁移到 canonical Mistake；先 dry-run，后写入，幂等可重放，并产出 `source_total / eligible / migrated / retained / rejected / drifted` 对账报告。**公开映射规则定版**：来源 Note 满足 `status == 'published' AND hidden == false` → `visibility='public'`；否则 `'private'`。不修改 migration 026 的数据库治理结构；未决公开来源不为零时禁止 cutover。
4. **Read Cutover**：迁移对账通过后，公共 `/mistakes` 才改读 canonical Mistake；不回退 legacy 数据源。生产迁移和公开切换仍需单独授权与回滚 runbook。

**诚实空态**：若迁移后无任何 `visibility='public'` 的 mistake（例如全部 legacy note 均非公开状态），公共 `/mistakes` 返回显式 Empty 状态——这是正确行为，不回退到 legacy 数据源凑数；公开化由 admin 通过发布入口主动完成。

**兼容约束**（AGENTS.md）：不删除 legacy 读兼容路径，仅在证据齐全并单独授权后按 Legacy Cleanup 顺序退役。`mistake_id` → `review_items` 既有 FK（`ondelete=RESTRICT`）不受影响。

## D7 — KP Analytics（R05）

**最小指标**（聚合自 canonical 表）：

```
attempt_count = COUNT(attempts WHERE context_type='practice' AND question → kp)
wrong_count   = COUNT(... context_type='practice' AND is_correct = false)
review_count  = COUNT(review_records → review_items → mistakes → kp)
due_count     = COUNT(review_items state='active' AND next_review_at <= now → kp)
```

派生：`accuracy = correct / graded`；`wrong_rate = wrong / attempts`（分母为 0 时定义 0，且有单测）。

**Weakness 第一版采用排序规则**（不引入加权分数/ML）：

```
wrong_rate DESC → lapse_count DESC → due_count DESC
```

`lapse_count` = 该 KP 关联错题的 canonical `ReviewRecord.rating <= 2` lifetime 计数。多 KP 题对每个关联 KP 各记一次完整观测；不做分数拆分。Archived Question/Mistake 与 inactive KP 不参与第一版统计；最终排序以 `knowledge_point_id` 稳定收口。

- 实现置于 `backend/app/services/`（KP analytics service），router 暴露只读端点；Dashboard 经既有 hook → API client 链路消费。
- 复杂权重方案（W = 0.5·WrongRate + 0.3·DuePressure + 0.2·LapseRate）保留为文档备选，第一版不实现。

## D8 — Note ↔ KnowledgePoint 关联（R06）

**新表**

```
note_knowledge_points
  note_id            UUID FK notes.id ON DELETE CASCADE
  knowledge_point_id INTEGER FK knowledge_points.id ON DELETE CASCADE
  UNIQUE (note_id, knowledge_point_id)
```

- 明确 FK 关联表承载核心 domain relationship；不复用 polymorphic `KnowledgePointLink.target_id VARCHAR`。
- 关联的建立入口：note 保存/编辑时由用户或 AI 建议确认（AI 建议仍走 Human Confirm，不自动落库）。
- Model + migration + schema + router（关联/解除端点）+ `src/lib/api/notes.ts` 同步。

## D9 — Daily Practice（R09）

**端点**：`GET /api/admin/practice/today`（后端 router → service），返回 0–10 个实际候选；候选充足时返回 3–10 题。

**选题管线（顺序过滤）**

```
weak KP（D7 排序头部）
→ 该 KP 下 unarchived Question
→ 排除 recently attempted（配置化 rolling window，默认前 7×24 小时）
→ 排除存在任一 mastered canonical Mistake/ReviewItem 的 Question
→ 过滤后按优先级取题：候选足够时取 3–10 题；候选不足时返回实际数量（可为 0）
```

**数量语义定版**：`3–10` 是"候选充足时"的区间，不是无条件下限；候选不足（或为 0）时返回实际数量并由前端渲染显式 Empty 状态。上限 10 硬性；下限仅在候选充足时成立。gate 与测试按此口径。

- 第一版只实现 "weak KP first"；50/30/20 比例策略为后续可选增强。
- 纯读、admin-only 端点，无 mutation；记入 `attempt` 仍走既有提交流（`context_type='practice'`）。列表 DTO 不返回 `answer_data`、`correct_answer`、`analysis` 或 `explanation`，最终排序以 `knowledge_point_id`、`question_id` 收口。

## D10 — Authoring 路由收敛（R03）

**目标路由**

```
/manage/notes            列表
/manage/notes/new        新建（?type=note | ?type=blog）
/manage/notes/[slug]     编辑
```

**标识符定版**：编辑路由采用 **slug**（F16：`notes.slug` unique、现有 notes API 按 slug 读写，`notes.py:216,307`），不引入 id 路由、不改 API 语义——PR-02 只做路由与 UI 收敛。

- Blog 共用 Note 模型，仅 `type` 区分；单一 `ContentEditor` 组件，`type` 只影响元数据字段（cover/tags/publish）与默认模板。
- 页面 → hook → `src/lib/api/notes.ts` 链路；不在 page 里直连 fetch。
- **旧路由三阶段**：
  1. `/write`、`/write-note`（`/write-mistake` 由 R04 一并处理）改为 server-side `redirect()` 到 `/manage/notes/new` 或 `[slug]`；
  2. 内部链接（Dashboard 快捷入口、菜单、旧测试）全部改指新路由；
  3. 删除旧实现目录（`src/app/write*/`），单独 PR + 删除证据。
- 旧 redirect 保留至第三阶段，避免 Bookmark 404。

## D11 — AsyncStatePanel（R03b）

```
components/AsyncStatePanel
  props: status: 'loading' | 'empty' | 'error', error?, onRetry?, emptyHint?
```

- 机制：App Router 原生 `loading.tsx`（Suspense）+ `error.tsx`（route-level boundary，含 reset）；`AsyncStatePanel` 只做数据面板级三态渲染，不自建框架。
- 采用范围：Week 1 覆盖 `/notes` 与 Dashboard 主要数据面板；后续 PR 触及的页面顺带整改，不发起全局大改。
- 语义规则：API 失败 ≠ 空数据；error 必须可 retry。

## D12 — Runtime Smoke 脚本（R31）

```
scripts/runtime-smoke.mjs（或等价）
1. GET <baseUrl>/           → 200
2. 解析 HTML：<script src>、<link href>（含 next/_next 资产）
3. 逐个 GET，要求 200
4. GET <baseUrl>/notes      → 200
5. GET <apiHealthUrl>       → 200（默认 http://127.0.0.1:8000/api/health，config.py:29 keep-alive 同源）
6. 汇总：referenced N / failed M；M > 0 → exit 1
```

**命令事实源**（F14）：`package.json` 中 `build` = `next build`（纯 Next 构建），`build:cf` = `opennextjs-cloudflare build`（OpenNext 产物）。Production runtime 验证必须使用 `build:cf` 产物，绝不以 `next dev` 或未部署的 `next build` 冒充。

**进程拓扑在 Phase 0 T-00b 定版并以证据记录**（本 spec 不预设未验证细节）：
- 前端 production 启动方式（OpenNext 本地 preview / 本地 Cloudflare 模拟 / `next start` 差异）与端口；
- backend 启动命令、PostgreSQL service/容器、`alembic upgrade head` 时点、环境变量集（不含真实 secrets）；
- 认证态注入方式（smoke 仅需公共页，默认匿名；`/notes` 公共读）与 seed fixture（最小：至少 1 条 note / 1 条 public mistake，由脚本自建或 fixture 注入）；
- smoke 的两段执行：**pre-deploy**（本地拓扑，CI Job 3）与 **post-deploy**（生产 URL，发布 runbook 步骤）。

- 脚本同时被本地验收与 CI Job 3 复用；输出结构化计数便于 gate 判定。

## D13 — CI 结构（R22）

```yaml
jobs:
  frontend:   npm ci → tsc --noEmit → npm run test:typecheck → npm test → npm run build
  backend:    setup → postgres service → alembic upgrade head（空库）→ pytest
  smoke:      按 T-00b 定版拓扑：build:cf → production start（前端+backend+PG）→ runtime-smoke（D12）
  e2e:        3–5 条 Playwright，workers=1，webServer 复用同拓扑
```

- Job 3/4 的具体启动命令、端口、环境变量、seed fixture **以 Phase 0 T-00b 的实测证据为准**；T-00b 未定版前，Job 3/4 不进入 CI（避免虚构可运行契约）。
- 任何 Job 失败 → DO NOT DEPLOY。
- Playwright 只保留 E2E-01…05（见 requirements R22b），不追求覆盖数量。

## D14 — WebAuthnChallenge（R33）

**现状修正**（F15）：`passkey_service.py:14-16` 存在**三套**内存 challenge store（registration / authentication / operator-registration），且 registration 用 `["current"]` 单键（`:55`）——并发 ceremony 互相覆盖；operator-registration 按 `session_id` 取 challenge。替换设计必须覆盖全部三类 ceremony，不能只覆盖登录。

**新表**（migration 033）

```
webauthn_challenges
  id             UUID PK
  challenge_hash CHAR(64) HEX    （SHA-256，不存明文 challenge）
  purpose        VARCHAR(30)     CHECK IN ('registration','authentication','operator_registration')
  session_id     VARCHAR(64) NULL（operator_registration 必填；其余可为 NULL，Indexed）
  user_id        UUID NULL FK users.id（authentication/operator_registration 已知用户时绑定）
  created_at     TIMESTAMPTZ
  expires_at     TIMESTAMPTZ     （≈ ceremony timeout，2–5 min，配置化）
  consumed_at    TIMESTAMPTZ NULL
  INDEX (challenge_hash)、INDEX (session_id)
```

**现有三类 store → 新表映射**

| 现有 store（passkey_service.py） | purpose | 绑定键 |
| --- | --- | --- |
| `_reg_challenge_store["current"]` | `registration` | challenge_hash（并发由多行天然隔离，废除 `["current"]` 单键） |
| `_auth_challenge_store` | `authentication` | challenge_hash（+ 可选 user_id 绑定） |
| `_operator_reg_challenge_store`（按 session_id） | `operator_registration` | `session_id`（保持现有"按 session 取 challenge"语义不变） |

**协议**：`generate（secrets.token_bytes 随机）→ store（一行/ceremony，写入 purpose+绑定键+expires_at）→ verify（按 challenge_hash+purpose+绑定键查行，严格比对、未过期、未消费）→ consume（原子 `UPDATE ... SET consumed_at=now() WHERE id=... AND consumed_at IS NULL`，0 行更新即拒绝）`。

- 替换后删除三套全局 dict；并发两个 ceremony 互不覆盖、互不串用（purpose + 绑定键双重隔离）。
- 过期行由认证时惰性清理，不建后台任务平台。
- 请求/响应协议不变：各 ceremony begin 端点仍返回 challenge，verify 端点仍接收断言——仅存储与校验实现替换。

## D15 — Login Throttling（R34）

**模型**：双维度失败计数（account + IP），达到阈值施加**递增延迟**而非锁定：

```
failures 1–3 → 无延迟
4 → 2s；5 → 5s；6+ → 15s（封顶）
```

- 计数窗口/阈值/延迟表全部进 `backend/app/config.py` 配置项。
- 存储复用 PostgreSQL（小表或复用 audit/session 存储），不引入 Redis。
- 成功登录重置该账户计数；IP 计数按窗口滑动衰减。
- 校验、错误信息与现有会话认证契约（HttpOnly `admin_session`）一致，不改变成功路径行为。

## D16 — OCR 诊断（R10）

- 失败分类枚举落库/落日志：`provider_auth / provider_timeout / invalid_model / invalid_response / schema_validation / image_fetch / image_format / unknown`。
- 对存量 31 条失败逐条归类产出报告；统计 `capture_recognition success_rate`。
- 受控样本测试：10 个固定样本 → 记录成功/失败与分类；验收 ≥ 8 成功。
- 失败 UI 必须可见、可重试、可诊断（错误分类透出到 manage capture 页）；若无法达标，入口显式禁用或标注不可用。

## D17 — AiRun target 纪律与 polish 分类（R11）

**现状**（F17）：`ai_polish.py` 的 polish 是流式预览调用（`polish_stream`），请求本身不带实体 `target_id`；polish 结果仅当用户保存 Note 时才落库，保存动作即 Human Confirm。

**polish 分类定版**：polish = **transient preview（临时预览辅助）**，不是直接持久化学习数据的生成。
- 因此 polish **不强制** `AiRun.target_type/target_id` 与完整 governance 链（Prompt Registry → Gateway → AiRun → Validation → Human Confirm）；
- 但该分类必须作为明确决策记录在案；**若未来 polish 结果被直接持久化为学习内容（不经用户保存动作），必须先入链再上线**。

**强制纪律（适用于产出持久化学习数据的生成，如 capture→recognition/draft/question）**
- 基于已有实体（Note / Question / Mistake / Capture）的生成，必须写 `target_type + target_id`。
- **创建型生成**（确认后才创建实体，提交时尚无 ID）：Human Confirm 创建实体后**回填** `target_id`；未确认创建则 AiRun 留空是**合法**状态（含义：建议被放弃）。
- 新增调用点强制；存量 NULL 不回填（除非单独授权）。
- 不建 event sourcing；仅字段纪律 + 新增调用点抽查。

## 迁移清单汇总（按 PR 执行顺序编号，全部从空库可重放）

> 当前源码 head 为 `030`（单链；027–030 仍位于当前 dirty/untracked Week 1/2 基线中）。**migration 必须按 PR 执行顺序创建**：每个新 migration 的 `down_revision` 指向创建时的实际 head，文件名序号连续递增；创建前用 `alembic history`/`alembic heads` 确认，禁止按下方"内容序号"跳跃创建或从 Git HEAD 的旧 026 基线重建。

| 序（执行顺序） | 内容 | 涉及 PR |
| --- | --- | --- |
| 027 | guestbook 表 | PR-04 |
| 028 | `review_items`：state CHECK 扩展（mastered）、algorithm CHECK 扩展（v2）+ 存量行 UPDATE 置 v2、新增 `last_rating` 列 | PR-05 |
| 029 | `review_records.previous_state / new_state` | PR-05 |
| 030 | `attempts.context_type` + `review_records.attempt_id`（FK → attempts.id） | PR-07 |
| 031 | `mistakes`：visibility CHECK 由 `= 'private'` 替换为 `IN ('private','public')` | PR-09 |
| 032 | `note_knowledge_points` | PR-12 |
| 033 | `webauthn_challenges` | PR-15 |

> 每个migration必须通过空库 `alembic upgrade head` 与 downgrade 回放验证；同一 PR 内多个 migration 按上表顺序串行。
