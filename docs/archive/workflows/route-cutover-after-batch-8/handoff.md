# Handoff：Route Cutover Sprint 交接说明

> 关联：[README.md](./README.md) | [tasks.md](./tasks.md) | [risks.md](./risks.md)
> 阶段：**实施完成**。D-0=方案 B，P0-01~P0-11 全部完成并通过验证。

## 一、当前状态

- Route Cutover Sprint **已实施完成**。
- 用户已确认 D-0 = 方案 B（关闭公开错题入口），并批准执行 P0-01~P0-11。
- P0-01~P0-10 全部完成并通过验证（tsc、build、HTTP 重定向、浏览器回归）。
- P0-11 收口文档已完成（tasks.md 勾选、validation.md 记录、本文件回填）。
- 改动文件限于：`next.config.ts`、`src/lib/content-routes.ts`、`src/components/nav-card.tsx`、`src/components/empty-state.tsx`、`src/app/(home)/*`、`src/app/manage/page.tsx`、`src/app/manage/(workspace)/mistakes/page.tsx`、`src/app/manage/(workspace)/capture/page.tsx`、`src/app/mistakes/*`、`src/app/notes/*`、`src/app/blog/[id]/*`。
- **未触碰**：后端代码、数据库模型、migration、Batch 8 业务逻辑。

## 二、新增文件清单

| 文件 | 用途 |
| --- | --- |
| `README.md` | 任务目标、路由现状、用户确认、本轮边界、主线文件索引 |
| `requirements.md` | 路由策略、数据流、权限、公开页策略、验收要求 |
| `design.md` | 路由收束设计、页面减负、导航统一、渲染减负方案 |
| `tasks.md` | P0-01 ~ P0-11 实施勾选项 + 前置决策 D-0 |
| `checklist.md` | 验收清单（十节） |
| `risks.md` | R-1 ~ R-9 风险记录（含用户已确认不阻塞项） |
| `validation.md` | 验证方案与记录模板 |
| `handoff.md` | 本文件 |

# 三、路由变更总览（已实施）

### 保留路由

- 公开（只读）：`/`、`/blog`、`/blog/[id]`、`/notes`、`/notes/[id]`
- 管理主线（AuthGate 保护）：`/manage/{dashboard,capture,subjects,drafts,questions,mistakes,review,attachments,ai,jobs,settings}` 及其 `[id]`

### 重定向路由（`next.config.ts` redirects，全部 307 临时重定向）

| 旧路由 | 重定向目标 | 验证 |
| --- | --- | --- |
| `/write-mistake` | `/manage/capture` | ✅ |
| `/write-mistake/:slug` | `/manage/mistakes` | ✅ |
| `/write-note` | `/manage/dashboard` | ✅ |
| `/write-note/:slug` | `/manage/dashboard` | ✅ |
| `/write` | `/manage/dashboard` | ✅ |
| `/write/:slug` | `/manage/dashboard` | ✅ |
| `/mistakes/review` | `/manage/review` | ✅ |
| `/mistakes` | `/manage/mistakes` | ✅ |

### 提示页路由

- 无独立提示页。旧路由统一重定向到对应 `/manage/*` 主线，重定向目标页含主线文案。

### 下线说明

- 旧 `write-*` 不再作为新内容主入口，不再写旧 `Note(type="mistake")`。
- 旧 `Note(type="mistake")` 不自动迁移。
- `/mistakes` 公开入口已关闭（方案 B）：公开导航移除"错题"项，`/mistakes` 重定向到 `/manage/mistakes`，未登录经 AuthGate 跳转 `/manage` 登录页。

## 四、用户已确认事项

1. **D-0**：`/mistakes` 公开策略 = **方案 B**（关闭公开错题入口）。已实施。
2. **tasks.md 审批**：用户已明确批准执行 P0-01~P0-11。已完成。
3. **旧数据丢失不阻塞**：旧路由下线导致的旧编辑能力丢失、旧书签失效、旧 Note 不再作为新主线，均不作为阻塞风险。

## 五、用户已确认的不阻塞项

- 旧路由下线导致的数据丢失 / 旧编辑能力丢失，不作为阻塞风险（见 [risks.md](./risks.md) R-1、R-2）。
- 本轮不做旧 `Note(type="mistake")` 到新 `mistakes` 的自动迁移，也不保留复杂兼容层。

## 六、剩余风险摘要

- **R-3 旧书签失效**：已用 307 重定向缓解，旧书签自动跳转新主线。
- **R-4 / R-5 公开错题策略变更与 SEO**：方案 B 下 `/mistakes` 重定向到私有管理页，公开错题列表不再可索引。这是用户确认的取舍。
- **R-6 无限"验证中"**：已解决。redirects 在 `next.config.ts` 层生效（渲染前），AuthGate 检测未登录后 `router.replace('/manage')` 跳转，不会无限停留。浏览器验证确认。
- **R-7 公开页 admin API 噪音**：已解决。浏览器验证首页与 /notes 均为 0 个 401/403。首页 `useAdminAuth` 仅一次 session check（httpOnly cookie 架构限制，SWR 60s dedup 全局共享，非噪音）。
- **R-8 旧 `/manage` 依赖未清**：已加降级提示条 + 跳转 `/manage/dashboard` 按钮。旧管理面板保留历史内容维护，未强重定向。
- **R-9 `/mistakes` 决策**：已确认方案 B，无未决风险。

## 七、实施发现（非阻塞，记录供后续）

1. **本地生产构建 CORS 阻断**：`next start` 使用 `.env.production` 的 `NEXT_PUBLIC_API_BASE_URL=https://public-api.limengyang.me`，本地 localhost 访问被 CORS 阻止。这是本地验证环境限制，非 Route Cutover 引入。生产部署同域无此问题。
2. **`GET /api/folders` 无 admin 权限保护**：`backend/app/routers/folders.py` 第 78-84 行 `list_folders` 无 `Depends(get_current_admin)`，匿名可调用并返回全部文件夹树（含文件夹名）。这是既有安全债务，非 Route Cutover 范围。建议后续任务收紧为 admin-only 或按公开/私有过滤。
3. **httpOnly cookie session check 架构限制**：前端无法无请求判断登录态，`useAdminAuth` 需一次 `getMe` 请求。401 由 try/catch 静默捕获，SWR 60s dedup 全局共享，不构成"噪音"。此为架构固有，非 Route Cutover 引入。

## 八、后续建议

1. 先确认 D-0，再审批 `tasks.md`。
2. 按 `tasks.md` 推荐执行顺序实施：Link scan → D-0 → `/write-mistake` → `/mistakes/review` → `/write-note`/`/write` → 首页清理 → Sidebar/Dashboard 统一 → 公开页减负 → 文案 → 浏览器回归 → 收口。
3. 实施时每完成一个 task 项立即回填 `tasks.md` 勾选状态，验证结果记入 `validation.md`。
4. 旧 `/manage` 第二步重定向建议在确认无依赖后再做，不要在首轮直接强重定向。
5. 旧 `Note(type="mistake")` 迁移作为独立后续任务，不在本任务组内。

## 九、给后续执行者（Codex / GLM / 人工）的边界提醒

- 不得在本任务组内：改数据库模型、新增 migration、删数据、自动迁移旧 Note、改 Batch 8 业务逻辑、接 AI Gateway、全量重写 notes 系统、全站 UI 重构。
- 公开页改动遵循「职责归位」而非「大重写」。
- 后端权限校验是真实安全边界，前端 `AuthGate` 仅做路由体验，不替代后端校验。
