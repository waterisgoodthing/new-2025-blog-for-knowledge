# Phase A A-02 路由、API 与权限审计

## Summary

审计确认：前端同时存在公开内容路由、管理员管理路由、旧写作路由和学习复习路由；后端主要使用 session cookie + `get_current_admin`，不是 JWT API Bearer 实现。`/mistakes/review`、`/write-note`、`/write-mistake` 已发现 `AuthGate`，但大多数 `/manage/**` 页面文件本身没有直接出现 `AuthGate`，需要继续确认其父级 layout 是否承担保护。

后端 router 的认证形式并不完全统一：部分 router 在 `APIRouter(dependencies=[Depends(get_current_admin)])` 级别保护，部分在函数参数保护，部分公开 GET 与管理员写入共用同一 prefix。以下报告把“源码已看见的保护”与“需要运行验证的行为”分开记录。

## Evidence

### Frontend Route Matrix

| Route | 类型 | 登录要求 | 写操作 | API 调用 | AuthGate | 直接 fetch | 风险 |
|---|---|---|---|---|---|---|---|
| `/`、`/blog`、`/blog/[id]` | Public | 否 | 否 | content/静态内容 | 否 | 未发现核心直接 fetch | 需确认只读内容过滤 |
| `/notes`、`/notes/[id]` | Public | 否 | 否 | `/api/notes` | 否 | 通过 API client | 后端公开过滤需运行确认 |
| `/mistakes` | Public | 否 | 否 | notes/mistake 数据 | 否 | 需逐组件确认 | 公开错题与私有复习边界 |
| `/mistakes/review` | Private User/Admin | 是 | 是 | `/api/review/*` | 是，`src/app/mistakes/review/page.tsx:12-31` | 通过 API client | 复习 API 仍是 admin 语义 |
| `/write-note` | Admin | 是 | 是 | `/api/notes` | 是 | 通过 API client | 后端 notes router 需逐端点核验 |
| `/write-note/[slug]` | Admin | 是 | 是 | `/api/notes/{slug}` | 是 | 通过 API client | 公开详情和编辑写入共用 notes API |
| `/write-mistake` | Admin | 是 | 是 | notes/AI/staged APIs | 是 | 通过 API client | AI 辅助接口与保存边界需核验 |
| `/write-mistake/[slug]` | Admin | 是 | 是 | `/api/notes/{slug}` | 是 | 通过 API client | 旧 Note 错题模型与独立 Mistake 并存 |
| `/write`、`/write/[slug]` | Admin/Unknown | `/write` 有 AuthGate；详情页未见 | 是 | content/旧写入 API | 部分 | 需确认 | 旧写作入口可能绕过 V2 内容链 |
| `/manage`、`/manage/dashboard` | Admin | layout 保护待确认 | 可能 | 管理 API | 页面未直接出现 | API client | 父级 layout 保护需浏览器验证 |
| `/manage/capture` | Admin | layout 保护待确认 | 是 | `/api/admin/captures` | 页面未直接出现 | API client | 采集为后台写入，需确认父级保护 |
| `/manage/drafts/**` | Admin | layout 保护待确认 | 是 | `/api/admin/drafts` | 页面未直接出现 | API client | 草稿审核链权限需端到端验证 |
| `/manage/questions/**` | Admin | layout 保护待确认 | 是 | `/api/admin/questions` | 页面未直接出现 | API client | 正式题库 admin router |
| `/manage/mistakes/**` | Admin | layout 保护待确认 | 是 | `/api/admin/mistakes` | 页面未直接出现 | API client | 独立 Mistake 与公开 Note 错题共存 |
| `/manage/review` | Admin | layout 保护待确认 | 是 | `/api/admin/review/items` | 页面未直接出现 | API client | 复习私有数据不得公开 |
| `/manage/ai`、`/manage/ai/runs` | Admin | layout 保护待确认 | 是/重试/审核 | `/api/ai/*`、`/api/admin/ai/runs` | 页面未直接出现 | API client 与流式 fetch | AI 输入、输出和治理日志敏感 |
| `/manage/attachments/**` | Admin | layout 保护待确认 | 是 | `/api/admin/attachments` | 页面未直接出现 | API client | 附件内容和 URL 泄露风险 |
| `/manage/subjects/**`、`knowledge-points/**` | Admin | layout 保护待确认 | 是 | `/api/subjects`、`/api/knowledge-points` | 页面未直接出现 | API client | taxonomy 写操作需 admin |
| `/manage/settings`、`jobs` | Admin | layout 保护待确认 | 是/治理 | settings/jobs 相关 API | 页面未直接出现 | API client | Jobs 当前是否真实队列需确认 |
| `/projects`、`/share`、`/snippets`、`/pictures` | Public/Unknown | 否 | 可能 | content/静态 JSON | 否 | 组件级 API | 公开与管理内容共用 managed content |

完整前端 route 文件清单来自 `find src/app -name page.tsx`；未列出的娱乐、音乐、guestbook、工具页面暂归 Public/Unknown，不属于个人学习主链，但其 API 权限仍需在后续全量 matrix 中保留。

### Backend API Matrix：认证与职责分组

| API 前缀 | 主要方法/端点 | Router 文件 | Service | Auth 源码证据 | 写入 | 风险 |
|---|---|---|---|---|---|---|
| `/api/notes` | GET list/detail；POST/PUT/DELETE；upload/promote | `routers/notes.py` | 直接 DB + note logic | `get_current_user/get_optional_user/get_current_admin` 混用 | 是 | 公开读取与管理员写入共 prefix；存在旧 Note 事实 |
| `/api/admin/questions` | GET/PUT/DELETE | `routers/questions.py` | `question_service` | router-level `get_current_admin` | 是 | admin 边界清晰，需 owner/审计确认 |
| `/api/admin/drafts` | GET/POST/PUT/reject/convert | `routers/drafts.py` | `draft_service` | router-level `get_current_admin` | 是 | 草稿转换为正式题目需幂等 |
| `/api/admin/mistake-drafts` | GET/POST/PUT/reject/convert | `routers/mistake_drafts.py` | `mistake_service` | router-level `get_current_admin` | 是 | 与 `Note(type=mistake)` 并存 |
| `/api/admin/mistakes` | GET/PUT/DELETE | `routers/admin_mistakes.py` | `mistake_service` | router-level `get_current_admin` | 是 | 独立错题 admin API |
| `/api/review` | queue/submit/stats/plan | `routers/review.py` | `review_planner`, `sm2` | function-level `get_current_admin` | 是 | 旧 Note 复习逻辑与独立 ReviewItem 并存 |
| `/api/admin/review/items` | list/records/submit | `routers/review_items.py` | `review_item_service` | router-level `get_current_admin` | 是 | 两套 Review API 并存 |
| `/api/admin/captures` | list/create/get/patch/recognize/draft/convert | `routers/captures.py` | `capture_service` | router-level `get_current_admin` | 是 | Capture 当前数据库数量为 0 |
| `/api/admin/attachments` | list/upload/get/content/delete | `routers/attachments.py` | `attachment_service` | router-level `get_current_admin` | 是 | 私有附件访问、storage key 和删除关联 |
| `/api/admin/ai/runs` | list/detail/retry/decision | `routers/ai_runs.py` | `ai_run_service` | router-level `get_current_admin` | 是 | AI 审核状态需与正式对象写入分离 |
| `/api/ai` | analyze、stream、draft、interpretation、diagram、logs、provider | `routers/ai.py` | 多个 AI service | router/function 需逐端点核验 | 是/只读混合 | router 包含较多编排，敏感日志和真实 provider 状态需审计 |
| `/api/ai/suggestions` | list/execute/weekly summary | `routers/suggestions.py` | `knowledge_assistant` | function-level `get_current_admin` | 是 | execute 可能改变正式 Note，需明确人工审核状态 |
| `/api/knowledge` | context-pack/weak-points | `routers/knowledge.py` | retrieval/relations | function-level `get_current_admin` | 只读 | 当前知识点与目标 KnowledgeNode 尚未统一 |
| `/api/knowledge-points` | CRUD | `routers/knowledge_points.py` | `taxonomy_service` | router-level `get_current_admin` | 是 | 当前 taxonomy 是独立事实 |
| `/api/subjects`、`/api/chapters` | CRUD | `routers/subjects.py`、`chapters.py` | `taxonomy_service` | router-level `get_current_admin` | 是 | 学科/章节 owner 和删除策略需确认 |
| `/api/auth` | login/register/passkey/session/me | `routers/auth.py` | auth helpers + direct DB | endpoint-specific | 是 | `ENABLE_REGISTRATION=True`；存在 AUTH_BYPASS 双开关 |
| `/api/content` | public GET + admin PUT/upload/delete | `routers/content.py` | `content_store` | mixed `get_current_admin/get_passkey_admin` | 是 | managed JSON 内容与 PostgreSQL 学习内容分开 |
| `/api/folders`、`/api/tags`、`/api/categories` | CRUD/merge/reorder | corresponding routers | 部分直接 DB | function-level admin | 是 | router/service 分层不一致 |
| `/api/guest-messages` | public create/list + moderation | `routers/guest_messages.py` | direct DB | optional user/admin | 是 | 非学习域，但匿名写入是公开 guestbook 设计 |
| `/api/music*` | playlist/items/manage/sync/public | `routers/music.py`, `music_manage.py` | music/netease/local services | mixed | 是 | 非学习域，不能混入学习数据审计结论 |

### 分层审计

- 已确认存在 service 层：`capture_service`、`question_service`、`mistake_service`、`review_item_service`、`taxonomy_service`、`ai_run_service`、`attachment_service` 等。
- 已确认部分 router 直接 import model 并执行查询/修改，例如 `routers/notes.py`、`routers/content.py`、`routers/suggestions.py`、`routers/guest_messages.py`。
- 这只能证明“存在直接 DB 访问”，不能单独判定为缺陷；是否违反当前边界需结合该路由是否只是简单查询和现有 workflow 约束审查。
- 前端 `src/lib/api/client.ts` 提供 `apiFetch`，但 `src/lib/api/ai.ts`、`auth.ts`、`ai-polish.ts` 等仍存在直接 `fetch`，主要用于流式或 passkey 场景，需区分合理例外与绕过统一 client。

### Permission Boundary Map

```text
Anonymous
  已确认：公开 notes/blog/content GET 和 guest message create 等入口存在
  未确认：所有公开 GET 是否都过滤 status/hidden
  禁止：管理写入、AI 操作、附件上传、复习提交

Authenticated User
  当前实现主要表现为 admin session user
  owner 级别隔离未在所有业务表统一存在
  不能把“已登录”自动等同为“可访问所有私有学习数据”

Admin
  get_current_admin 保护题目、草稿、错题、复习项、附件、AI Run、taxonomy 等多组 API
  管理页面父级 layout 的真实保护需要浏览器/网络请求验证

Worker / Background
  当前仓库未发现独立 worker app 的完整任务入口
  OCR/AI/同步多由 service 或请求路径触发
  是否存在绕过 service 的后台写入，需要后续运行与调用链审计
```

## Risk

| ID | 风险 | 严重程度 | 影响 | 建议 |
|---|---|---|---|---|
| A02-ACCESS-001 | 当前前端存在多个旧写作和管理入口 | 高 | 用户可能走不同写入链，难以迁移 | Phase B 建立 route ownership 和唯一写入口 |
| A02-ACCESS-002 | `/api/notes` 同时承担公开读取与管理员写入 | 高 | 公开过滤和写入权限容易互相影响 | 分离公开 query 与 admin command，迁移前保持兼容 |
| A02-ACCESS-003 | 管理页面文件未直接出现 AuthGate | 高 | 父级保护若失效则页面可进入并发起请求 | 只读浏览器验证 layout、401 和网络请求 |
| A02-ACCESS-004 | `AUTH_BYPASS` 与 `AUTH_BYPASS_ALLOW` 存在双开关组合 | 高 | 生产环境可能绕过认证 | Phase B 增加生产启动阻断，当前只记录不修复 |
| A02-ACCESS-005 | `notes`、`mistakes`、`review` 有两套事实路径 | 高 | 越权、复习状态漂移和审计缺口 | 统一权限矩阵和对象映射 |
| A02-ACCESS-006 | 部分 router 直接使用 model/session | 中 | 业务逻辑和权限检查可能分散 | Phase B 按 Context 逐路由重构，不在 Phase A 修改 |
| A02-ACCESS-007 | 前端存在直接 `fetch` | 中 | 统一错误/认证/重试策略可能不一致 | 逐项区分流式/passkey 合理例外与绕过 |
| A02-ACCESS-008 | 后端注册配置 `ENABLE_REGISTRATION=True` | 高 | 个人系统可能暴露开放注册 | 生产配置和 auth policy 单独审计 |

## Next Step

1. 以本矩阵为基线，执行 Phase B 权限和数据源收敛设计。
2. 不在 Phase A 修复任何路由或认证问题。
3. 所有 `High` 风险先转为 Phase B 需求或明确接受，不得直接进入迁移切换。

