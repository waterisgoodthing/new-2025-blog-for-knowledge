# 目标路由

> 全部为目标路由规划；尚未存在的页面均为待实现，旧路由在迁移期兼容保留。

## 路由原则

- 公开阅读与管理操作使用明确分离的 URL 空间。
- 公开页面只调用 public API；不得先请求 admin API 再依靠 401/403 降级。
- `/manage/**` 在页面级使用管理员会话保护，但真实安全边界仍在后端。
- 路由中的 `[slug]` 是人类可读公开标识；管理 API 的更新和删除优先使用稳定 `id`。

## 公开路由

| 路由 | 所属功能域 | 是否公开 | 数据来源 | 管理员权限 |
|---|---|---:|---|---:|
| `/` | Content Publishing / 聚合 | 是 | public posts、notes、mistakes 的精选摘要 | 否 |
| `/blog` | Content Publishing | 是 | `GET /api/public/posts` | 否 |
| `/blog/[slug]` | Content Publishing | 是 | `GET /api/public/posts/{slug}` | 否 |
| `/notes` | Knowledge Notes | 是 | `GET /api/public/notes` | 否 |
| `/notes/[slug]` | Knowledge Notes | 是 | `GET /api/public/notes/{slug}` | 否 |
| `/mistakes` | Mistake System | 是 | `GET /api/public/mistakes` | 否 |
| `/mistakes/[slug]` | Mistake System | 是 | `GET /api/public/mistakes/{slug}` | 否 |

公开路由只展示 `published + public + 未删除` 的资源。管理按钮根据已确认的管理员会话条件展示，但不得改变公共数据响应。

## 管理路由

| 路由 | 所属功能域 | 是否公开 | 数据来源 | 管理员权限 |
|---|---|---:|---|---:|
| `/manage` | Auth / Admin | 否 | session、管理概览 admin API | 是 |
| `/manage/subjects` | Subject | 否 | subjects admin API | 是 |
| `/manage/subjects/[id]` | Subject | 否 | subject 聚合详情 | 是 |
| `/manage/subjects/[id]/taxonomy` | Taxonomy | 否 | 章节与知识点 admin API | 是 |
| `/manage/taxonomy` | Taxonomy | 否 | taxonomy admin API | 是 |
| `/manage/knowledge-points/[id]` | Taxonomy | 否 | knowledge point admin API | 是 |
| `/manage/posts` | Content Publishing | 否 | `GET /api/admin/posts` | 是 |
| `/manage/posts/new` | Content Publishing | 否 | `POST /api/admin/posts` | 是 |
| `/manage/posts/[slug]/edit` | Content Publishing | 否 | admin post detail/update API | 是 |
| `/manage/notes` | Knowledge Notes | 否 | `GET /api/admin/notes` | 是 |
| `/manage/notes/new` | Knowledge Notes | 否 | `POST /api/admin/notes` | 是 |
| `/manage/notes/[slug]/edit` | Knowledge Notes | 否 | admin note detail/update API | 是 |
| `/manage/questions` | Question Bank | 否 | `GET /api/admin/questions` | 是 |
| `/manage/questions/[id]` | Question Bank | 否 | admin question detail/update API | 是 |
| `/manage/practice` | Practice System | 否 | `GET /api/admin/practice-sessions` | 是 |
| `/manage/practice/import` | Practice System | 否 | practice import admin API | 是 |
| `/manage/practice/[sessionId]` | Practice System | 否 | session、attempts、report admin API | 是 |
| `/manage/practice/[sessionId]/review` | Practice System | 否 | session result confirmation admin API | 是 |
| `/manage/mistakes` | Mistake System | 否 | `GET /api/admin/mistakes` | 是 |
| `/manage/mistakes/import/document` | Mistake System | 否 | mistake document import API | 是 |
| `/manage/mistakes/new` | Mistake System | 否 | `POST /api/admin/mistakes` | 是 |
| `/manage/mistakes/[slug]/edit` | Mistake System | 否 | admin mistake detail/update API | 是 |
| `/manage/review` | Review System | 否 | queue、records、stats admin API | 是 |
| `/manage/ai-runs` | AI Assistant 旧兼容路径 | 否 | 重定向 `/manage/ai/runs` | 是 |
| `/manage/attachments` | Media / Attachments | 否 | `/api/admin/attachments` | 是 |
| `/manage/attachments/[id]` | Media / Attachments | 否 | attachment detail API | 是 |
| `/manage/ai` | AI | 否 | AI 管理概览 | 是 |
| `/manage/ai/models` | AI | 否 | model profiles | 是 |
| `/manage/ai/routing` | AI | 否 | routing rules | 是 |
| `/manage/ai/prompts` | AI | 否 | prompt templates | 是 |
| `/manage/ai/playground` | AI | 否 | task playground | 是 |
| `/manage/ai/runs` | AI | 否 | AI runs | 是 |
| `/manage/ai/validators` | AI | 否 | validators | 是 |
| `/manage/ai/costs` | AI | 否 | cost metrics | 是 |
| `/manage/drafts`、`/manage/drafts/[id]` | Draft Review | 否 | drafts admin API | 是 |
| `/manage/jobs`、`/manage/jobs/[id]` | Job Queue | 否 | jobs admin API | 是 |
| `/manage/search` | Search | 否 | admin search | 是 |
| `/manage/analytics` | Analytics | 否 | analytics API | 是 |
| `/manage/reports`、`/manage/reports/[id]` | Reports | 否 | reports API | 是 |
| `/manage/settings` | Settings | 否 | settings API | 是 |
| `/manage/settings/review` | Settings | 否 | review settings | 是 |
| `/manage/settings/ai` | Settings | 否 | AI settings | 是 |
| `/manage/settings/ocr` | Settings | 否 | OCR settings | 是 |
| `/manage/settings/upload` | Settings | 否 | upload settings | 是 |
| `/manage/settings/drafts` | Settings | 否 | draft settings | 是 |
| `/manage/settings/jobs` | Settings | 否 | job settings | 是 |
| `/manage/settings/privacy` | Settings | 否 | privacy settings | 是 |

`/manage/questions` 管理题库，`/manage/practice` 管理练习记录，`/manage/practice/import` 是多题上传与批量识别的主入口，`/manage/practice/[sessionId]` 展示一次练习的作答结果和分析报告。`/manage/mistakes` 只管理需要复盘的正式错题，`/manage/review` 只管理复习规划、队列与记录。

若迁移期保留 `/manage/mistakes/import`，它不得继续作为多题导入主入口，只能重定向或引导至 `/manage/practice/import`。练习导入不等于错题导入。

旧 `/write-note`、`/write-note/[slug]`、`/write-mistake`、`/write-mistake/[slug]` 和 `/mistakes/review` 在对应管理页迁移完成前属于兼容旧系统；它们仍须遵守现有 AuthGate 与后端鉴权规则。

AI 运行页面的唯一目标主路径是 `/manage/ai/runs`；`/manage/ai-runs` 只能作为迁移期重定向，不得继续承载新页面。

## 导航与异常约定

- 未登录访问 `/manage/**`：跳转 `/manage` 的登录状态；若当前就是 `/manage`，显示登录界面。
- 会话过期：清理本地会话状态并返回登录界面，不展示残留编辑表单。
- public API 的未发布资源：返回 404，避免泄露存在性。
- admin API 的未认证请求：返回 401；已认证但能力不足返回 403。
- 后端失败：公开路由展示局部错误或空状态；管理路由保留未提交表单并提供重试。
- 旧 `/write*` 与 `/mistakes/review` 路由仅在迁移兼容期重定向；何时启用重定向由对应前端迁移阶段决定。
