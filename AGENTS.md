# Agent Architecture Rules

This file is mandatory for all AI agents working in this repository. Read it before inspecting or editing code. If a user request conflicts with this file, ask for explicit confirmation before breaking these rules.

## Project Shape

This project has two active architectural lines:

1. Frontend and original static-blog system: Next.js App Router under `src/`.
2. Personal knowledge backend: FastAPI, PostgreSQL, JWT auth, notes, mistakes, review, AI, and GitHub sync under `backend/`.

Do not blur these lines accidentally. Every change must state which line it affects.

## Required First Steps

Before making code changes:

1. Check `git status --short`.
2. Identify the touched domain: `blog`, `notes`, `mistakes`, `review`, `auth`, `sync`, `home`, `share`, `manage`, or shared infrastructure.
3. Read the existing files in that domain before editing.
4. Prefer existing patterns over new abstractions.
5. Preserve user changes and generated content. Never revert unrelated dirty files.

## Task Workspace And Workflow Files

Every non-trivial task must follow the repository workflow below. Skills, external prompts, or agent habits do not override this workflow.

Required workflow order:

1. Create or reuse a task workspace folder.
2. Write or update `README.md`.
3. Write or update `design.md`.
4. Write or update `requirements.md`.
5. Write or update `tasks.md`.
6. Stop and request explicit user approval for `tasks.md`.
7. Only after approval, execute tasks one by one.
8. After each task item is completed, immediately update `tasks.md` and mark that exact item complete.
9. Record validation in `validation.md`.
10. Record handoff notes or external-agent prompts in `handoff-prompt.md` when needed.

Agents must not skip directly from discussion to implementation when a task requires workflow files. If the user asks to "start tasks", "implement", "push", or "continue" before approving `tasks.md`, the agent must first ask for approval of the task list.

Every non-trivial task must have a task workspace folder before design, requirements, task lists, audits, prompts, reports, screenshots, or handoff notes are created.

Use this structure:

```text
docs/workflows/<task-name>/
  README.md
  design.md
  requirements.md
  tasks.md
  diff-report.md
  audit.md
  validation.md
  handoff-prompt.md
  assets/
```

Rules:

- `<task-name>` must be a short, stable, kebab-case name that describes the user-visible task, for example `ai-mistake-navigation-upgrade` or `note-editor-ui-upgrade`.
- `README.md` is mandatory. It must state the task goal, touched domains, current status, and links to the main workflow files in that folder.
- `design.md`, `requirements.md`, and `tasks.md` are mandatory before implementation starts for any feature, UI change, architecture change, backend contract change, deployment change, or multi-step bugfix.
- `tasks.md` must use checkboxes for implementation items. Use `[ ]` for pending, `[x]` for completed, and clearly label blocked, skipped, or deferred items with a short reason.
- Starting implementation from `tasks.md` requires explicit user approval in the conversation. Approval must refer to the task list or phase being executed.
- After completing each individual task item, update `tasks.md` immediately in the same turn before starting the next task item. Do not batch all task-document updates at the end.
- If implementation changes the plan, update `design.md` or `requirements.md` first, then update `tasks.md`, then continue only if the change stays within the user-approved scope. If scope expands, request approval again.
- Put workflow-generated files in the task folder, not directly under `docs/`, unless the user explicitly asks for a top-level canonical document.
- Keep source code in its normal architectural location. Do not move implementation files into `docs/workflows/`.
- Put screenshots, pasted references, exported reports, and other supporting artifacts under `docs/workflows/<task-name>/assets/` when they should be kept in the repository.
- If continuing an existing task, reuse its existing task folder instead of creating a new parallel folder with a similar name.
- If a legacy workflow document already exists directly under `docs/`, do not move it casually. For new work on that topic, create or reuse a task folder and link back to the legacy document from `README.md`.
- Handoff prompts for Mimo or other agents must live in `handoff-prompt.md` inside the relevant task folder.
- Validation results must be recorded in `validation.md` or in a clearly named dated validation file inside the task folder.
- If the task is small enough that no workflow files are needed, do not create an empty folder just for ceremony. The folder rule applies once the task produces planning, audit, prompt, report, or multi-step validation artifacts.

## Frontend Boundaries

Use these ownership rules:

- `src/app/<route>/page.tsx`: route-level UI and page composition only.
- `src/app/<route>/components/`: route-specific UI components.
- `src/app/<route>/services/`: client-side services tied to that route only.
- `src/app/<route>/hooks/`: route-specific hooks only.
- `src/components/`: shared UI used by more than one route.
- `src/hooks/`: shared hooks used by more than one route.
- `src/lib/api/`: typed API clients and request DTOs only. No React.
- `src/lib/`: shared pure utilities, markdown rendering, auth helpers, and client helpers.
- `src/config/`: static JSON configuration. Do not rely on JSON inference for public types.
- `public/`: static assets and static generated content only.

Do not put API calls directly in components when an API wrapper already exists or should exist in `src/lib/api/`.

Do not create a new top-level route for a domain if an existing domain route should own it.

## Backend Boundaries

Use these ownership rules:

- `backend/app/models/`: SQLAlchemy database models only.
- `backend/app/schemas/`: Pydantic request and response contracts only.
- `backend/app/routers/`: HTTP routing, dependency wiring, status codes, and thin orchestration.
- `backend/app/services/`: business logic such as SM-2 review, AI analysis, GitHub sync, import/export, and domain operations.
- `backend/app/utils/`: small framework-independent helpers.
- `backend/app/config.py`: settings only.
- `backend/alembic/versions/`: database migrations.

Routers must stay thin. If a route grows complex, move logic into `services/`.

Model changes require matching schema, API client, and migration changes unless there is a documented reason.

## Domain Model Rules

The current knowledge model is centered on `Note` with these content types:

- `note`: ordinary notes.
- `blog`: blog-like long-form entries.
- `mistake`: wrong-question records with review metadata.

If adding podcast records, do not overload `music` or `blog` silently. Add an explicit `podcast` content type and update all of these together:

- Backend enum/schema/model.
- Frontend API types in `src/lib/api/`.
- List filters and labels.
- Create/edit UI.
- Detail UI.
- Management UI.
- GitHub sync/export.
- Tests or verification notes.

Mistake records must preserve these fields as first-class data, not only markdown text:

- `subject`
- `difficulty`
- `question`
- `my_answer`
- `correct_answer`
- `analysis`
- `knowledge_points`
- `ef`
- `interval`
- `repetitions`
- `next_review`
- `last_reviewed`

## Data Flow Rules

Frontend pages must use this flow:

`page/component -> hook or local action -> src/lib/api/* -> backend API`

Backend APIs must use this flow:

`router -> schema validation -> service/model -> response schema`

Do not introduce a second data source for the same domain unless the architecture decision is documented in this file or in a dedicated architecture note.

The original GitHub-file workflow and the new backend workflow are both present. When changing persistence, be explicit about whether data lives in:

- static files under `public/`
- PostgreSQL through the backend
- GitHub export/sync generated from backend data

## Type And Contract Rules

Do not trust inferred JSON types for mutable configuration. Define explicit TypeScript types when arrays may start empty, especially:

- `siteContent.artImages`
- `siteContent.socialButtons`
- background images
- route config arrays

Keep frontend TypeScript types in sync with backend Pydantic schemas.

Do not hide contract failures by adding `any` unless the code is integrating an untyped external boundary and the unsafe part is isolated.

Do not add new fields in only one layer.

## Auth And Security Rules

There are two auth concepts:

1. Original GitHub App private-key auth for static content updates.
2. Backend JWT auth for notes, mistakes, review, and management APIs.

Do not mix these casually. A feature must clearly use one path.

For backend-protected mutations, use JWT auth through `Authorization: Bearer <token>`.

Do not expose broad registration, wildcard CORS, or persistent secrets in production without calling it out as a security risk.

Never commit real `.env`, private keys, tokens, database dumps, or personal content not intentionally public.

## UI And Product Rules

The project is a personal knowledge/blog system, not a generic demo. Core user workflows are:

- write and read notes
- record and review mistakes
- write blog posts
- optionally add podcast records if the domain type is introduced
- manage content safely

Do not add landing-page marketing screens for these workflows.

For operational pages such as notes, mistakes, review, and manage, prefer dense but readable interfaces over decorative hero sections.

Every public icon-only button must have an accessible name.

Every image that conveys meaning must have `alt`.

Do not disable user zoom.

## Static Assets And Content Rules

Static content references must point to files that exist under `public/`.

If removing imported public content, update all indexes and references in the same change.

If a UI uses `/music/*`, `/images/share/*`, `/images/art/*`, `/images/blogger/*`, or `/blogs/*`, verify the referenced files exist.

Do not commit generated caches:

- `.next/`
- `.open-next/`
- `.output/`
- `node_modules/`
- `backend/.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `*.pyc`

## Validation Rules

Choose validation based on touched files:

- Frontend TypeScript changes: run `npx tsc --noEmit`.
- Frontend build-sensitive changes: run `npm run build`.
- Frontend UI changes: run the dev server and inspect the relevant route in a browser.
- Backend Python changes: run targeted tests if present, or at least import/start checks for FastAPI.
- API contract changes: verify both frontend client types and backend schemas.
- Database model changes: add or update Alembic migrations.

If validation fails because of pre-existing issues, report that clearly and include the first relevant failure.

Do not rely on `next.config.ts` `ignoreBuildErrors` as proof that the project is healthy.

## Package And Tooling Rules

Prefer the package manager already chosen by the repository. If both `pnpm-lock.yaml` and `package-lock.json` exist, do not update both casually. Ask or document which one is authoritative before changing dependencies.

Do not add large dependencies for small utilities.

Do not introduce a new state library; the project already uses Zustand and SWR.

## Change Discipline

Keep changes small and domain-scoped.

Do not refactor unrelated old blog features while implementing notes, mistakes, or podcast records.

Do not move files only for tidiness unless the user asked for architecture cleanup.

When creating a new domain feature, include:

- route
- API client
- backend schema/router/service/model updates
- navigation entry if user-facing
- empty state
- create/edit/read flow
- validation notes

## Current Known Architecture Debt

Agents must be aware of these known issues and avoid deepening them:

- TypeScript checking currently fails because JSON empty arrays infer as `never[]`.
- `next.config.ts` ignores build type errors.
- Static assets referenced by the UI may be missing after upstream content removal.
- Backend and original GitHub App persistence models are not fully unified.
- Backend registration and CORS are suitable for local prototype use, not production.
- Podcast records are not a first-class domain yet.

When working near these areas, either fix the debt in scope or explicitly avoid making it worse.

# 权限分层规则

## 1. 项目权限模型总则

本项目采用“公开读取 + 管理员写入”的权限模型。

前端页面是否使用 `AuthGate`，应根据页面职责判断。后端 API 权限必须作为真实安全边界，前端 `AuthGate` 只承担路由体验、访问边界表达和减少无效请求的作用。

任何重构都不得把公开内容页面错误地封闭，也不得把私有编辑、复习、AI 操作暴露为公开页面。

---

## 2. 公开读取层

以下页面允许未登录访客访问：

```text
/mistakes
/notes/[slug]
/blog
/blog/[slug]
/notes
```

公开读取层的规则：

1. 可以展示已发布、未隐藏内容。
2. 不应强制要求管理员登录。
3. 不应显示编辑、删除、AI 分析、复习提交等管理操作。
4. 如果页面中存在管理员专用模块，应在未登录时隐藏、折叠或优雅降级。
5. 公开页面不应因为管理员接口返回 `401` 或 `403` 而出现明显错误状态。

后端公开读取 API 包括：

```text
GET /api/notes
GET /api/notes/{slug}
```

未登录访问时，后端只能返回：

```text
status === "published"
hidden === false
```

的数据。

---

## 3. 管理员编辑层

以下页面必须使用 `AuthGate` 或等价的前端访问保护：

```text
/write-note
/write-note/[slug]
/write-mistake
/write-mistake/[slug]
```

管理员编辑层的规则：

1. 未登录用户访问时应跳转到 `/manage` 或项目既有登录入口。
2. 页面加载前应先确认管理员会话，避免展示编辑界面骨架。
3. 不能只隐藏保存按钮来替代页面级访问保护。
4. 编辑页必须依赖后端权限校验完成真实写入保护。
5. 前端 `AuthGate` 不得被视为唯一安全边界。

相关后端写入 API 必须受 `get_current_admin` 保护：

```text
POST /api/notes
PUT /api/notes/{slug}
DELETE /api/notes/{slug}
```

---

## 4. 管理员学习与复习层

以下页面必须使用 `AuthGate`：

```text
/mistakes/review
```

复习相关功能属于站点所有者的私有学习数据，不应作为公开页面暴露。

复习相关 API 必须受 `get_current_admin` 保护，包括但不限于：

```text
复习队列
复习提交
复习统计
复习计划
薄弱点诊断
```

规则：

1. 未登录用户不能进入复习页面。
2. 公开 `/mistakes` 页面可以提供轻量复习入口，但点击后必须进入受保护的 `/mistakes/review`。
3. `/mistakes` 页面中如果需要展示复习统计，应仅在管理员已登录时加载。
4. 未登录时不要反复请求管理员复习接口，避免控制台出现大量 `401` 或 `403`。

---

## 5. AI 操作层

AI 分析、图片识别、错因理解、最终解析、图解生成等能力属于管理员操作层。

以下接口或同类接口必须受 `get_current_admin` 保护：

```text
POST /api/ai/analyze
POST /api/ai/analyze-text
POST /api/ai/analyze-stream
POST /api/ai/analyze-text-stream

POST /api/ai/mistake/question-draft
POST /api/ai/mistake/question-draft/confirm
POST /api/ai/mistake/error-interpretation
POST /api/ai/mistake/error-interpretation/reject
POST /api/ai/mistake/final-analysis
POST /api/ai/mistake/diagram
```

规则：

1. AI 操作不应对未登录访客开放。
2. 公开详情页可以展示已经生成并保存的 AI 解析内容。
3. 公开详情页不得提供“重新生成”“继续分析”“生成图解”等管理按钮。
4. 新建或编辑错题时，AI 只能作为辅助能力，不应成为保存错题的强制前置步骤。

---

## 6. 图片上传层

图片上传属于管理员写入行为，必须受 `get_current_admin` 保护。

规则：

1. 未登录用户不能上传图片。
2. 公开页面可以读取和展示已保存图片。
3. 上传接口不得因为前端隐藏入口而取消后端权限校验。
4. 图片 URL 展示应避免泄露本地路径、临时路径或内部存储细节。

---

## 7. 错题系统的特殊权限规则

当前错题不是独立模型，而是：

```text
Note(type="mistake")
```

因此权限判断应沿用 Note 权限模型。

实际接口是：

```text
GET    /api/notes?type=mistake
GET    /api/notes/{slug}
POST   /api/notes
PUT    /api/notes/{slug}
DELETE /api/notes/{slug}
```

禁止在权限规则中假设存在：

```text
mistakes 表
/api/mistakes
/api/mistakes/{slug}
```

错题权限规则：

1. `/mistakes` 是公开错题列表页，可以展示已发布、未隐藏错题。
2. `/write-mistake` 是管理员新建错题页，必须使用 `AuthGate`。
3. `/write-mistake/[slug]` 是管理员编辑错题页，必须使用 `AuthGate`。
4. `/mistakes/review` 是管理员复习页，必须使用 `AuthGate`。
5. 错题详情当前复用 `/notes/[slug]`，按公开详情页处理。
6. 登录态下可以显示错题编辑入口，未登录时必须隐藏编辑入口。

---

## 8. AuthGate 使用原则

`AuthGate` 适用于页面级保护，不适合替代后端权限校验。

应该使用 `AuthGate` 的场景：

```text
内容创建页
内容编辑页
错题复习页
后台管理页
需要管理员身份才能操作的工具页
```

不应该机械使用 `AuthGate` 的场景：

```text
公开博客列表
公开博客详情
公开笔记详情
公开错题列表
公开错题详情
```

页面级规则：

1. 私有页面进入前先鉴权。
2. 公开页面保持可访问。
3. 公开页面中的管理按钮根据登录态条件展示。
4. 页面是否公开，不能改变后端 API 的权限约束。

---

## 9. 后端权限原则

真实安全边界必须在后端。

后端规则：

1. 所有创建、更新、删除接口必须依赖 `get_current_admin`。
2. 所有 AI 写操作或分析操作必须依赖 `get_current_admin`。
3. 所有复习提交、复习统计、复习计划接口必须依赖 `get_current_admin`。
4. 公开读取接口必须过滤 `status` 与 `hidden`。
5. 不得因为前端已经使用 `AuthGate` 而移除后端权限校验。

---

## 10. AUTH_BYPASS 规则

项目中存在开发绕过开关：

```text
AUTH_BYPASS
AUTH_BYPASS_ALLOW
```

当前语义为两个值同时为 true 时才允许绕过：

```text
return bypass and allow
```

规则：

1. 本地开发可以保留该机制。
2. 生产环境不应允许 `AUTH_BYPASS=true` 且 `AUTH_BYPASS_ALLOW=true`。
3. 如后续修改后端配置，建议在生产环境启动时显式拒绝该组合。
4. 不得在文档、测试或示例中建议生产启用认证绕过。
5. 不得依赖 `AUTH_BYPASS` 通过正常权限测试。

---

## 11. 修改权限相关代码前的检查清单

在修改权限相关代码前，必须检查：

```text
1. 该页面是公开内容页，还是管理员操作页？
2. 是否涉及创建、编辑、删除、上传、AI、复习？
3. 后端接口是否已有 get_current_admin？
4. 前端是否需要 AuthGate？
5. 未登录用户访问时应该跳转、隐藏模块，还是优雅降级？
6. 是否会误伤公开博客、公开笔记、公开错题列表？
7. 是否会导致公开页面出现 401/403 错误噪音？
8. 是否涉及 AUTH_BYPASS？
```

---

## 12. 当前已知权限问题

当前已知需要后续修复的问题：

```text
/write-mistake/[slug] 缺少 AuthGate
/write-note/[slug] 缺少 AuthGate
/mistakes/review 缺少 AuthGate
/mistakes 公开页可能调用管理员专用复习接口
生产环境缺少对 AUTH_BYPASS=true 且 AUTH_BYPASS_ALLOW=true 的显式启动拒绝
```

这些问题应分批处理，避免与错题编辑器重构混在一个大 diff 中。

推荐优先级：

```text
P0：
- /write-mistake/[slug] 加 AuthGate
- /write-note/[slug] 加 AuthGate
- /mistakes/review 加 AuthGate

P1：
- /mistakes 公开页中的管理员接口优雅降级
- 登录态下显示编辑入口，未登录隐藏

P2：
- 生产环境显式禁止 AUTH_BYPASS 双 true
```

---

## 13. 禁止事项

权限相关修改中禁止：

1. 不要给 `/mistakes` 强制加 `AuthGate`。
2. 不要给 `/notes/[slug]` 强制加 `AuthGate`。
3. 不要破坏公开博客、公开笔记、公开错题的读取能力。
4. 不要只依赖前端隐藏按钮保护写操作。
5. 不要移除后端 `get_current_admin`。
6. 不要新增不存在的 `/api/mistakes` 权限规则。
7. 不要假设错题有独立表。
8. 不要在生产环境启用认证绕过。
9. 不要让公开页面因为管理员接口失败而出现大面积错误。
10. 不要把权限重构和错题编辑器重构合并成一个不可审查的大改动。
