# Personal Learning System — 受控收敛工程 Spec（30 天）

> 原计划续接（2026-10-09）：当前建议已在 [合并路线](../../ROADMAP.md)逐项映射原需求/PR、B返工与A/N问题；[当前状态](../../PROJECT_STATUS.md)区分历史验收和现版本。下文保留当期记录，不恢复历史实施授权。

> 文档治理（2026-10-09）：历史阶段账本保留，不把原 PASS/FAIL/未实施覆盖为本轮状态。当前见 PROJECT_STATUS；R 旧候选之后已有 B 本地返工 PARTIAL；UI V2 为独立组件轨，尚非主业务路由集成。 当前入口见 [文档索引](../../DOCUMENTATION_INDEX.md)。

> 版本 v1.0 ｜ 基线：`refactor/baseline` @ `4a954ea` ｜ 起草日期：2026-09-03
> 来源：综合审查（`PERSONAL_LEARNING_SYSTEM_AUDIT.md`、`IMPROVEMENT_BACKLOG.md`，均未跟踪、不纳入本 spec 变更）+ 外部工程实践。

## 1. 结论定位

本周期任务不是"重构整个系统"，而是一次**受控的收敛工程**：

```
Runtime → Authoring → Review → Re-answer → Canonical → Knowledge Feedback
```

30 天目标：从"双代并存、闭环不完整"推进到 **Canonical-first Personal Learning System**，稳定完成：

```
Dashboard → 今日复习/练习 → Question → Attempt（错）
→ MistakeDraft → 人工确认 → Mistake + ReviewItem
→ 到期 Re-answer → ReviewRecord → lapse / progression
→ mastered → KnowledgePoint 统计更新 → Dashboard 下一步建议
```

`Note → KnowledgePoint → Question → Attempt → Mistake → Review → Mastery` 逐渐成为唯一学习事实链。

## 2. 核心规则（唯一一条）

**优先修正确性和闭环；不新增架构层，不进行大规模 UI 重写，不引入新的基础设施。**

## 3. 工程原则

| 编号 | 原则 | 内容 |
| --- | --- | --- |
| P1 | Canonical First | 新增学习逻辑只能建立在 `Subject / KnowledgePoint / Question / Attempt / MistakeDraft / Mistake / ReviewItem / ReviewRecord` 之上；停止给 `Note.type='mistake'`、legacy SM-2、legacy weak-point 增加新能力 |
| P2 | Keep Architecture Boring | 保持 `Page → Hook → API Client → HTTP → Router → Schema → Service → SQLAlchemy → PostgreSQL`；明确不引入 Redis / Elasticsearch / Vector DB / Neo4j / Kafka / 微服务 / Background Job Platform / Repository Pattern |
| P3 | Migration 是 Schema 唯一所有者 | 空 PostgreSQL 经 `alembic upgrade head` 必须构造完整生产 Schema；不得依赖运行时 `create_all()` 补表；复杂业务数据迁移与 schema versioning 解耦（一次性可审计脚本），不扩展 migration 026 治理系统 |

## 4. 基线事实（已在 `4a954ea` 代码中逐条核实）

以下计划主张已对照当前代码验证，作为 spec 事实源：

| # | 事实 | 证据 |
| --- | --- | --- |
| F1 | 复习调度失败与成功均无条件 `repetitions += 1` | `backend/app/services/review_item_service.py:40` |
| F2 | 调度间隔表为 `INTERVALS={0:1, 1:1, 2:1, 3:3, 4:7, 5:14}`（按 rating、与历史无关） | `backend/app/services/review_item_service.py:11` |
| F3 | `ReviewItem.state` CHECK 仅 `('active','paused')`，无 `mastered` | `backend/app/models/review_item.py:33` |
| F4 | `ReviewRecord` 无 `previous_state / new_state` 列 | `backend/app/models/review_item.py:42-61` |
| F5 | `Attempt` 无 `context_type`（来源）字段 | `backend/app/models/attempt.py` |
| F6 | `guest_messages` 模型存在但 Alembic versions 中无任何 migration → fresh DB 缺表 | `backend/app/models/guest_message.py`；`backend/alembic/versions/` grep 无结果 |
| F7 | Alembic head 为 `026_legacy_system_retirement` | `backend/alembic/versions/026_legacy_system_retirement.py` |
| F8 | `/write`、`/write-note`、`/write-mistake` 旧编辑器仍在；`/manage/(workspace)` 无笔记写作路由 | `src/app/write*/`、`src/app/manage/(workspace)/` |
| F9 | 公共 `/mistakes` 页面读取 legacy `Note(type='mistake')` | `src/app/mistakes/page.tsx:28` |
| F10 | 提交复习已有乐观并发保护（`expected_next_review_at` + `with_for_update` + `ReviewConflict`） | `backend/app/services/review_item_service.py:29-35` |
| F11 | legacy `sm2.py` 服务仍存在于 services 层 | `backend/app/services/sm2.py` |
| F12 | 前端 API client 已有 `review-items.ts / attempts.ts / mistakes.ts / notes.ts` | `src/lib/api/` |
| F13 | `Mistake.visibility` 列已存在，但 CHECK 锁定 `= 'private'`；`questions.visibility` 同模式 | `backend/app/models/mistake.py:84,91`；`backend/app/models/question.py:173` |
| F14 | `build` = `next build`（纯 Next 构建）；OpenNext 构建为 `build:cf` = `opennextjs-cloudflare build` | `package.json` |
| F15 | passkey 存在三套内存 challenge store（registration/authentication/operator-registration），registration 用 `["current"]` 单键，operator-registration 按 `session_id` | `backend/app/services/passkey_service.py:14-16,55` |
| F16 | Note 以 unique `slug` 为标识；公开性由 `status`（默认 published）+ `hidden` 两字段表达；notes API 按 slug 读写 | `backend/app/models/note.py:36,40-41`；`backend/app/routers/notes.py:216,307` |
| F17 | polish 为流式预览调用（`polish_stream`），请求不带实体 `target_id`，结果仅随用户保存落库 | `backend/app/routers/ai_polish.py:33` |
| F18 | backend keep-alive 指向 `http://127.0.0.1:8000/api/health`（可作 smoke health 探针） | `backend/app/config.py:29` |

## 5. 范围

### In Scope（主链，顺序锁定）

```
R31 Runtime Integrity → R03 Authoring → R01 Review Semantics
→ R02 Re-answer → R04 Canonical Migration → R05 KP Analytics
→ R06 Note↔KP → R09 Daily Practice
```

横向工程线（与主开发同步）：**Schema / Security / CI**。

### Out of Scope（本周期明确禁止，BLOCK 清单）

FSRS、Vector Search、Vector DB、Knowledge Graph、Graph Visualization、Elasticsearch、Redis、微服务、新 Repository 层、新 Article Model、大型设计系统重写、大型 Analytics 重建、自动文章生成。

任何 BLOCK 项要进入 Sprint，必须先证明它能解决当前 P0 闭环问题。

### Day 30 之后才重新评估

FSRS 调度、Trend Analytics、AI Knowledge Summary、Citation Persistence。前提：Attempt / ReviewRecord 显著且稳定增长、Mastered 数据可信、KP accuracy 有真实样本、系统连续稳定使用。

## 6. 里程碑

| 里程碑 | 名称 | 内容 | 对应周期 |
| --- | --- | --- | --- |
| M1 | TRUSTED RUNTIME | Production 稳定启动；写作可用；fresh DB 可用；错误状态诚实 | Week 1 |
| M2 | CLOSED REVIEW LOOP | Attempt → Mistake → Re-answer → Lapse/Progress → Mastered 全链打通 | Week 2 |
| M3 | CANONICAL LEARNING | Legacy 学习读取退役；KP 分析 canonical；Note↔KP；Daily Practice | Week 3 |
| M4 | RELEASE GATE | OCR 已诊断；认证加固；CI 完整；关键 E2E 完成；legacy 收缩 | Week 4 |

**周 Gate 硬性规则**：Week 1 未通过 → 暂停进入 Review 算法整改。

## 7. UI 设计路线

UI 路线独立列示，并以核心工程能力为前置：

1. 已完成：Authoring（PR-02）→ Foundation 子集（PR-03），状态均为 `PASS`。
2. 周内 UI：Review（PR-08）→ Today 基础（PR-11）→ Capture 失败路径（PR-14），随对应周授权和 Gate 执行。
3. 扩展 UI：Authentication（PR-20）、Today 本地工作台（PR-21）、OCR 候选确认（PR-22）。
4. 契约型扩展：跨设备布局同步（PR-23 路线占位）、ReviewRecord 真实撤销（PR-24）、UTC+8 每日 AI 推荐（PR-25）、OCR 后台状态查询（PR-26）。

PR-20～26 均为 `NOT_AUTHORIZED`，不进入 Week 1–4 Gate。其依赖关系、解除条件和完整顺序见 [tasks.md](tasks.md#ui-设计路线独立于-m1m4-gate)；交互与浏览器验收合同见 [ui-design.md](ui-design.md#17-ui-设计路线)。

## 8. 风险与审批

- 本 spec 覆盖 schema 迁移、认证、CI、生产运行时 → 多数 PR 为 **HIGH** 风险（见 tasks.md 逐项标注）。
- 本 spec 的创建即为已授权任务；**每个 Phase（周）开始执行前需单独明确批准**，批准不跨阶段传递，绝不自动携带到 commit / push / migration / 部署。
- 生产数据操作（R04 legacy 迁移、WebAuthn challenge 表、任何 destructive 操作）执行前另行走 `agents/gates.md` 审批。
- 认证契约不变：HttpOnly `admin_session` 会话 + `get_current_admin` 后端授权边界；`AuthGate` 仅是导航保护。公共读路由不得因整改被意外私有化。

## 9. 文档索引

| 文件 | 内容 |
| --- | --- |
| [requirements.md](requirements.md) | 按需求编号（R31–R34 等）的完整需求与验收标准 |
| [design.md](design.md) | 设计决策（schema 变更、调度语义、路由收敛、CI、安全） |
| [ui-design.md](ui-design.md) | UI 目标规范（分散模块、登录、工作台、编辑器、复习、OCR、动效、响应式与无障碍） |
| [tasks.md](tasks.md) | PR-01 … PR-19 核心路线、PR-20 … PR-26 UI 候选路线、风险等级与 gate |
| [validation.md](validation.md) | 验证命令、周 gate 表、30 天最终验收矩阵、证据规则 |
