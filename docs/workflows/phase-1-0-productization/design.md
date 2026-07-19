# Design: Phase 1.0 Productization

## 1. Overall Architecture

```text
Phase 0 baseline
      |
Phase 0.5 Runtime Recovery
      |
      +-----------------------------+
      |                             |
Phase 1.0A UI/Product Polish   Phase 1.0B Production Hardening
      |                             |
      +---------------+-------------+
                      |
               Phase 1.0 RC Gate
                      |
          Personal Learning System v1.0
                      |
Phase 1.0C separate approval
```

前端仍使用 Next.js App Router；后端仍使用 FastAPI、PostgreSQL 和既有 admin auth。UI 收口不得改变领域事实源；Production Hardening 不引入新学习能力。

## 1.1 Remaining-Gate Decision Architecture

```text
Gate B COMPLETE / CONDITIONAL PASS
               |
               v
Schema Authority decision (user selects final knowledge-point contract)
               |
               +-- no-DDL metadata alignment OR approved DDL/migration path
               |
               v
Alembic current / heads / check agree at one final revision
               |
               v
RC Gate (separately approved runtime + restore + browser evidence)
               |
               v
Gate C design, then separately approved Learning Feedback implementation
```

Schema Authority had no implicit default. The documented candidates were mutually exclusive until the user selected SA-A on 2026-07-19:

| Candidate | Final authority | Possible work | Approval boundary |
|---|---|---|---|
| SA-A | **SELECTED:** existing database index/unique contract | Make lifecycle metadata match the accepted physical contract; prove no DDL is needed | Decision and SA-P0-01 are approved; source/test task approval remains required; no migration authorization is implied |
| SA-B | Current ORM sibling-name contract | Create and review an exact migration plan after duplicate-data and query compatibility preflight | Requires explicit decision plus separate DDL/migration approval |
| SA-C | A defined compatibility contract | Document final index/constraint set and change only the approved layers | Requires explicit decision; DDL/migration remains separately approved if needed |

SA-A final taxonomy contract is defined in `schema-authority-compatibility-matrix.md`: two case-insensitive partial unique indexes distinguish roots from children, and all three existing query indexes remain present. The current single ORM sibling-name constraint is not compatible because PostgreSQL unique constraints treat multiple `NULL` parent IDs differently and do not apply `lower(name)`. Metadata alignment must therefore model the existing partial-index semantics, not replace them with a constraint.

All candidates retain Alembic as the schema lifecycle authority and startup as read-only readiness validation. The lifecycle metadata inclusion/exclusion list must be explicit; historical guest-message provenance remains excluded unless separately governed. Existing dirty source that appears to move toward this architecture is treated as unaccepted worktree state, not completion evidence.

RC runs against exactly one accepted final revision. If Schema Authority changes the revision or restore boundary, it must use a fresh backup and an isolated restore; source database and attachment storage remain untouched. Gate C begins only after RC PASS and must first freeze a narrow feedback contract before implementation.

## 2. Phase 0 Baseline Design

项目级 canonical artifact：`docs/releases/v1.0-baseline.md`。

内容必须包括：

- Git branch、HEAD、worktree 精确状态。
- Alembic current/heads/history 摘要。
- 核心表 counts 与抽样标识；UUID 聚合需转为 text。
- 当前公开/管理路由和 Demo 主链路。
- `LT-ISSUE-002` 等历史问题的当前状态，而不是复制旧摘要中的过期描述。
- AI infrastructure、Capture、真实 OCR、BKT、Analytics 的分层状态。
- 桌面和移动截图；管理登录后截图如无真实会话则标 `BLOCKED`，不得启用 bypass。
- 历史 revision 018 restore 证据与当前 revision 020 证据之间的差异。

## 2.5 Phase 0.5 Runtime Recovery Design

```text
read-only runtime audit
        ↓
confirmed project process + failure layer
        ↓
quarantine generated .next output
        ↓
clean production build (exit 0)
        ↓
start newly built frontend runtime
        ↓
desktop/mobile browser + network verification
        ↓
asset validation + DB/revision comparison
        ↓
strict PASS or FAIL
```

Recovery boundaries:

1. P05-01 is read-only and must identify process ownership before any stop action.
2. P05-02 may change only ephemeral runtime state and generated `.next` output after approval. Generated output is quarantined with a timestamp, not immediately deleted; the production build must exit 0 before browser verification.
3. Source/config/dependency/lockfile edits are an exception path requiring a task-scope amendment and new approval.
4. Browser verification uses a fresh anonymous session and no request mocking.
5. The database is guarded by before/after `020 (head)` and core-count snapshots; no DDL/DML/migration is authorized.

Browser acceptance contract:

| Route | Desktop | Mobile | Document | JS/CSS | Hydration | Console |
|---|---|---|---|---|---|---|
| `/` | required | required | 200 | 200 | success | 0 errors |
| `/blog` | required | required | 200 | 200 | success | 0 errors |
| `/notes` | required | required | 200 | 200 | success | 0 errors |
| `/mistakes` | required | required | 200 | 200 | success | 0 errors |
| `/manage` | required | required | 200 | 200 | success | 0 errors |

Hydration success requires rendered route content, working navigation or controls appropriate to the anonymous state, no hydration exception, and no indefinite loading/blank screen. HTTP document 200 alone is insufficient.

Asset validation is limited to requests actually exercised by target routes. First-party 200 or valid cache 304 is required. External font/analytics availability is recorded separately and cannot trigger source changes in this Gate.

Gate PASS resolves only the frontend-runtime blocker. Alembic metadata drift remains assigned to Production Hardening.

## 6. Gate C — Minimal Learning Feedback Design

### 6.1 Product boundary

This Gate C is deliberately a deterministic **next-step feedback** surface, not Analytics Lite, mastery scoring, recommendation storage, BKT, AI advice or a second learning data source. It answers one narrow administrator question: “What should I do next today?”

The card is rendered only inside the already protected `/manage/dashboard` after `DashboardContent` has loaded the existing admin-only summary. It adds no public route, no public API request and no management mutation.

### 6.2 Decision table

| Priority | Existing summary predicate | Feedback | Action |
|---|---|---|---|
| 1 | `due_reviews > 0` | complete due reviews first | `/manage/review` |
| 2 | no due reviews and `mistakes > 0` | organize an existing mistake | `/manage/mistakes` |
| 3 | no due reviews/mistakes and `questions > 0` | review or turn a question into a learning record | `/manage/questions` |
| 4 | otherwise | start by adding a question | `/manage/questions` |

The feedback names only observable counts and a route. It must not claim mastery, weakness, cause, progress percentage, learning effectiveness or a generated recommendation.

### 6.3 Data, permission and lifecycle

```text
admin Dashboard page
  -> existing DashboardContent / DashboardSummary request
  -> pure feedback derivation from counts
  -> rendered card + action link
```

`GET /api/admin/dashboard/summary` remains the sole API boundary and remains protected by `get_current_admin`. The derivation is a pure frontend function; it stores nothing and never reads question/mistake text. No schema change, migration, backup refresh, restore, telemetry, recommendation row, AI call or retention policy is introduced.

### 6.4 Acceptance design

Test-first coverage freezes all four branches in the decision table. Browser acceptance uses a real admin session, confirms the card and action are visible, verifies anonymous access remains redirected, and repeats TypeScript/build/full regression checks. Any need for extra fields, persistence, metrics or a public endpoint is an out-of-scope change that requires a new approval.

## 7. Production Startup Security Follow-up

The startup guard remains a pure pre-readiness validation inside the existing FastAPI lifespan. It evaluates only configuration booleans and must run before database readiness or keep-alive startup.

```text
ENV != production -> retain existing development behavior
ENV == production -> reject insecure JWT OR wildcard/empty CORS OR (AUTH_BYPASS && AUTH_BYPASS_ALLOW)
                  -> raise RuntimeError with a fixed safe message
                  -> do not reach database readiness, keep-alive or serve requests
```

The bypass predicate uses the same case-insensitive string semantics as the authentication router. No configuration value, token or secret is included in the exception. Diagnostics may still report a runtime warning if it observes an active bypass, but production cannot reach that state through normal startup.

## 8. Release Safety Follow-up Design

### 8.1 Recommendation API boundary

```text
public ShareCard
  -> GET /api/recommendations/today
  -> existing public-safe record OR explicit missing response
  -> never AI, never DB write

admin management
  -> GET /api/recommendations/today (read existing)
  -> POST /api/recommendations/today/generate (explicit AI/write)
  -> DELETE /api/recommendations/today (explicit admin delete)
  -> GET /api/recommendations/history (admin-only, bounded safe DTO)
```

The public-safe DTO excludes `raw_context`. Existing history is treated as private because it contains personal learning-derived information. The generation mutation must use `get_current_admin`; it invokes the existing generation service only after authorization. Missing public content uses a bounded missing response that callers can degrade to the existing random-share fallback; it does not synthesize or persist a fallback row.

### 8.2 Release review and pre-deploy boundary

The review is source/config-template/test based. It does not read deployed settings, invoke external providers, deploy, push, or contact production systems. The deployment gate remains fail-closed:

```text
clean worktree
  -> dependency audit and peer tree
  -> frontend test/typecheck/Cloudflare build
  -> backend full pytest
  -> Alembic current/heads/check
  -> production-startup security tests
  -> recommendation public/admin contract tests
  -> diff hygiene
  -> eligible for separately authorized deployment
```

The current dirty worktree is expected to block an actual predeploy invocation. This task can only prove the checker correctly identifies that block; it must not clean, stage, commit, deploy or alter user files.

### 8.3 Deployment-readiness execution boundary

Deployment is a separately approved release sequence, not the final command of local validation:

```text
policy decisions approved
  -> approved release scope in isolated clean worktree
  -> separately authorized target / backend boundary
  -> fail-closed predeploy matrix
  -> separately authorized frontend and/or backend deployment
  -> public and administrator post-deploy smoke
  -> explicit rollback-or-accept decision
```

The frontend Cloudflare/OpenNext release and FastAPI/PostgreSQL/Attachment Storage release are independent. The task list therefore names them separately and forbids inferring one deployment from the other. The existing `predeploy:check` requires a clean worktree, an isolated test database for pytest and a distinct target database for read-only Alembic authority checks. It does not itself authorize target access or deployment.

The approved production policy is: disable public registration; retain Workers invocation logs at 1% head sampling with platform short retention; treat any higher sampling as separately approved, temporary incident work. The frontend-only gate does not touch a target database. The backend gate is separately authorized only when a target database boundary is approved. Evidence records only pass/fail assertions and release identities; it never copies credentials, configuration values, cookies, private content, database URLs or storage paths. A failed predeploy, health, authorization, asset, hydration or console check stops the sequence. Rollback is platform-specific and must use the pre-recorded release identity; no migration, restore or destructive cleanup is implied.

## 3. UI/Product Polish Design

### 3.1 Dashboard

页面结构：

```text
学习管理首页
├── 今日任务
│   ├── 待复习
│   └── 最近错题
├── 内容统计
│   ├── 题目
│   ├── 错题
│   ├── 知识点
│   └── 附件
├── 最近活动
│   ├── 最近题目
│   └── 最近复习记录
└── 系统状态
    ├── 服务
    ├── 数据库
    └── Storage
```

数据策略：

1. 先审计已有 admin list/queue/health API 是否能在可接受请求数内组成页面。
2. 如果多个 API 会产生不一致快照、过度请求或客户端聚合，设计 `GET /api/admin/dashboard/summary`。
3. summary API 只读、admin-only、薄 router，聚合逻辑进入 service。
4. unknown/null 必须与 0 区分；健康信息不泄露连接串、路径、provider secret。

#### Frozen dashboard contract (A-P0-02)

Existing domain list APIs return complete arrays, expose no aggregate totals, and provide review records only per review item. Building the dashboard from them would require multiple full-list requests plus an N+1 review-record path. Gate A therefore uses one new read-only, admin-only endpoint:

```text
GET /api/admin/dashboard/summary
Authorization: existing get_current_admin dependency
```

Response:

```ts
type DashboardSummary = {
  generated_at: string
  counts: {
    questions: number
    mistakes: number
    knowledge_points: number
    attachments: number
    due_reviews: number
  }
  recent_questions: Array<{
    id: string
    title: string | null
    question_text: string
    updated_at: string
  }>
  recent_mistakes: Array<{
    id: string
    title: string | null
    question_text: string
    reason_category: string
    updated_at: string
  }>
  recent_reviews: Array<{
    id: string
    review_item_id: string
    rating: number
    reviewed_at: string
    question_text: string
  }>
  system: {
    service: 'ok'
    database: 'ok'
    storage: 'ok' | 'unknown'
  }
}
```

Counts include active questions, active mistakes, active knowledge points and active attachments. `due_reviews` includes active items whose `next_review_at` is not later than the response time. Recent arrays are limited to five rows and sorted newest first. A successful response proves service/database availability; storage is `ok` only when the configured root exists as a directory, otherwise `unknown`. The endpoint does not expose paths, credentials or provider state and creates no schema or migration.

### 3.2 Manage navigation

```text
学习空间
└── Dashboard

内容管理
├── Drafts
├── Questions
└── Mistakes

学习计划
└── Review

资料管理
└── Attachments

工具
├── Capture
└── AI

系统
└── Settings
```

Search、Analytics、Jobs 若仍延期，不应占据与核心流程相同的一级权重；可移入“后续能力”分组或暂不展示。

### 3.3 Mobile public navigation

- 使用固定底部导航或现有 `MobileNav` 模式。
- 匿名固定展示：首页、博客、笔记、错题。
- 只有已确认管理员会话才追加管理。
- 为内容底部增加 safe-area padding，避免最后一张卡片被导航遮挡。
- 390×844、横屏和较长中文标题都需验证。

### 3.4 Shared state components

如果仅管理页使用，优先放在 `src/app/manage/components/`；只有公开页与管理页都复用时，才放在 `src/components/ui/`。

建议最小合同：

```ts
type FeatureState =
  | { kind: 'loading'; rows?: number }
  | { kind: 'empty'; title: string; description?: string; action?: Action }
  | { kind: 'error'; title: string; description?: string; retry?: () => void }
  | { kind: 'deferred'; title: string; description: string }
```

禁止把 `deferred` 当成 empty，也禁止用 Skeleton 永久掩盖 API 失败。

### 3.5 Language and display normalization

- 展示层统一中文，API enum 不改名。
- 建立 difficulty/date label helpers，避免页面各自硬编码。
- 推荐完整日期：`2026年6月23日`；紧凑列表允许 `6月23日`，但同一页面只使用一种格式。
- “AI”“OCR”“API”等通用缩写可保留英文。

实现采用 `src/lib/manage-display.ts` 作为管理端展示边界：API 继续传输既有英文 enum，组件只在渲染时转换题型、难度、状态、附件可见性/关联类型/用途。完整日期统一为 `yyyy年M月d日`，含时间时统一为 `yyyy年M月d日 HH:mm`，并固定按 `Asia/Shanghai` 展示。

## 4. Production Hardening Design

### 4.1 Auth regression first

`LT-ISSUE-002` 当前文档状态为 `fixed-in-separate-workflow`，所以 PROD-01 首先是回归验证，不默认修改。只有禁用账号仍返回 500 或会话边界失败时，才进入最小修复。

### 4.2 Backup and restore

历史 Phase D-4 在 revision 018 已验证：custom-format `pg_dump` + 隔离 PostgreSQL restore。v1.0 应复用同一安全模式，但必须针对当前 revision 和当前附件目录重新生成证据。

```text
read-only source
  ├── pg_dump --format=custom
  └── attachment archive + manifest + checksums
             |
             v
isolated PostgreSQL + temporary attachment root
             |
             v
revision / schema / counts / IDs / checksums / app import
             |
             v
cleanup temporary environment
```

### 4.3 Monitoring

- `/health` 保留轻量公开语义，不暴露内部详情。
- 详细 DB/Storage/Auth 状态放到 admin-only diagnostics 或运行日志。
- 错误记录只保存 safe route、timestamp、request/correlation id、匿名化 user id、error class 和安全摘要。
- 不记录 Authorization、cookie、password、token、完整 AI input 或私人正文。

Gate B 现状审计确认：`/api/health` 当前公开返回 DB 项；Dashboard 的 system 字段虽然受管理员保护，但 DB 固定为 `ok`、Storage 只判断目录存在，且没有 Auth 项。应用也没有统一 request/correlation id 或安全的未处理异常记录。因此 B-P1-02 采用以下最小合同，不增加数据库表或第三方监控依赖：

```text
GET /api/health
  -> public, 仅返回整体 service status

GET /api/admin/diagnostics
  -> get_current_admin
  -> service / database / storage / auth
  -> generated_at + overall status
  -> 不返回路径、用户、配置值或 secret

request middleware
  -> 每请求生成 server-owned UUID request id
  -> 正常与错误响应均返回 X-Request-ID
  -> 仅对未处理异常记录 route、UTC timestamp、request id、匿名 actor、异常类和固定安全摘要
  -> 不记录异常 message、headers、cookies、body 或 query string
```

诊断状态只使用 `ok / warning / error / unknown`。DB 通过 `SELECT 1`；Storage 只读检查目录存在且当前进程可读写，不创建探针文件；Auth 在管理员依赖已通过且 bypass 未激活时为 `ok`，双 bypass 激活时为 `warning`。诊断检查自身失败转为对应状态，不向客户端抛出内部细节。

## 5. Permission Design

- Public：只能读取已发布、未隐藏内容。
- Admin UI：AuthGate 提供页面体验保护。
- Admin API：继续由 `get_current_admin` 提供真实安全边界。
- Dashboard、backup status、diagnostics：全部 admin-only。
- Mobile public nav：不得因为 admin session probe 失败而影响公开页面。

## 6. Exception Design

- Partial Dashboard failure：分区显示 error，不清空其他成功分区。
- Empty data：显示下一步行动，不显示虚构示例。
- Auth unknown：显示公开 UI；管理入口延迟出现或不出现。
- Backup failure：停止 restore chain，保留日志和 artifact hash，不触碰原 DB。
- Attachment mismatch：RC Gate BLOCKED，不能以 DB restore 通过代替完整恢复。
- Browser auth unavailable：管理截图标 `BLOCKED`，等待真实用户会话，不启用 bypass。

## 7. Validation Strategy

- Docs/data baseline：Git、Alembic、read-only SQL、route inventory。
- Frontend：Vitest、`npx tsc --noEmit`、`npm run build`。
- Backend：定向测试 + full pytest；记录 warning。
- UI：桌面 1280×720、移动 390×844；公开匿名与真实管理员会话分开验证。
- Auth：匿名、有效管理员、禁用管理员、撤销/过期会话。
- Restore：隔离 PostgreSQL + 临时 storage root；原数据库零 mutation。
- RC：`git diff --check`、scope diff、全链路浏览器验收、剩余风险与回滚说明。

## 8. Rollback Boundaries

- UI 修改按任务文件级回滚，不删除用户数据。
- Dashboard API 如新增，必须为纯新增只读合同；撤回前端后不影响既有领域 API。
- Auth 修改需有回归测试后才能合入。
- Backup/restore 工具不得修改原数据，因此无需原库回滚；失败时删除临时环境即可。
