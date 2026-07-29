# 后端结构规范

> 目标结构，均为待实现或待迁移，不表示当前后端已经具有这些模块。

相关文档：[功能域](./domains.md)、[数据模型](./data-model.md)、[API](./api-design.md)、[权限](./permissions.md)、[技术栈](./tech-stack.md)。

## 1. 后端分层原则

FastAPI 后端按 HTTP、业务服务、ORM、请求响应契约和依赖注入分层。依赖方向为 `router -> schema/dependency -> service -> model/database`；下层不得反向依赖 router。

## 2. 目标目录结构

```text
backend/app/
├── routers/
│   ├── public_posts.py
│   ├── public_notes.py
│   ├── public_mistakes.py
│   ├── admin_posts.py
│   ├── admin_notes.py
│   ├── admin_questions.py
│   ├── admin_practice.py
│   ├── admin_practice_imports.py
│   ├── admin_mistakes.py
│   ├── review.py
│   ├── ai_runs.py
│   ├── attachments.py
│   ├── taxonomy.py
│   ├── subjects.py
│   ├── ocr.py
│   ├── capture.py
│   ├── drafts.py
│   ├── jobs.py
│   ├── search.py
│   ├── analytics.py
│   ├── reports.py
│   ├── settings.py
│   └── auth.py
├── models/
│   ├── post.py
│   ├── note.py
│   ├── question.py
│   ├── practice.py
│   ├── mistake_draft.py
│   ├── mistake.py
│   ├── review.py
│   ├── ai_run.py
│   ├── attachment.py
│   ├── taxonomy.py
│   └── session.py
├── schemas/
│   ├── post.py
│   ├── note.py
│   ├── question.py
│   ├── practice.py
│   ├── mistake_draft.py
│   ├── mistake.py
│   ├── review.py
│   ├── ai_run.py
│   ├── attachment.py
│   └── taxonomy.py
├── services/
│   ├── post_service.py
│   ├── note_service.py
│   ├── question_service.py
│   ├── practice_service.py
│   ├── practice_import_service.py
│   ├── mistake_draft_service.py
│   ├── mistake_service.py
│   ├── review_service.py
│   ├── ai_service.py
│   ├── ai_run_service.py
│   ├── attachment_service.py
│   ├── taxonomy_service.py
│   ├── ocr_service.py
│   ├── capture_service.py
│   ├── draft_service.py
│   ├── job_service.py
│   ├── search_service.py
│   ├── analytics_service.py
│   └── settings_service.py
├── dependencies/
│   ├── auth.py
│   └── database.py
└── database.py
```

这是目标组织方式，不表示本轮移动或创建后端代码。

OCR Service 只保存识别结果；Capture Service 只分类并产生草稿；Draft Service 是转换正式数据的唯一审核入口；Job Service 管理异步生命周期。三者均不得绕过业务 Service 直接写正式学习表。

## 3. routers 层职责

Router 只处理 HTTP 输入输出：路径与查询参数、schema 校验、依赖注入、状态码、响应 schema 和异常映射。Router 不直接实现发布规则、复习算法、AI 生命周期、附件清理或复杂查询。

## 4. services 层职责

Service 表达用例和业务规则，协调模型、事务与外部服务。它负责权限后的资源校验、状态转换、幂等、并发冲突、审计载荷及领域间编排。Service 不依赖 FastAPI Request/Response，也不返回 HTTPException 作为领域结果。

学习域服务必须保持以下所有权：

- `question_service` 管理题目本体、来源、去重候选和复用关系。
- `practice_service` 管理练习、逐题作答、汇总和报告的业务状态。
- `practice_import_service` 编排上传文件、AI 识别、题目拆分、Question/Practice Attempt 生成和 Mistake Draft 生成。
- `mistake_draft_service` 管理草稿修正、拒绝和经用户确认的幂等转换。
- `mistake_service` 只管理正式错题，不拥有完整练习导入。
- `review_service` 只管理复习规划、队列、记录和算法状态。
- `ai_service` 只负责模型调用及结构化结果，不直接写正式业务数据。

## 5. models 层职责

Model 只表达 SQLAlchemy ORM 表、字段、关系、数据库约束与索引。Post、Note、Question、Practice、Mistake Draft、Mistake 保持独立模型；Review、AI Run、Attachment 和 Taxonomy 按各自所有权建模。Model 不负责序列化、HTTP 状态或界面文案。

## 6. schemas 层职责

Schema 只表达请求与响应结构及字段级校验。Public 与 Admin 响应必须显式分开；创建、更新和读取 schema 也应按语义区分。Schema 不执行数据库查询，不把 ORM model 直接无筛选地暴露给客户端。

## 7. dependencies 层职责

Dependencies 提供数据库 session、`get_current_admin`、请求上下文等横切依赖。认证依赖解析并验证 `admin_session`，返回明确管理员身份；数据库依赖负责 session 生命周期，但不隐式提交任意业务事务。

## 8. 数据库事务边界

- 一个业务用例由 service 建立清晰事务边界。
- 创建/更新实体及其审计记录应原子完成。
- 复习提交必须原子写 Record、更新 Item、消费旧 Schedule 并生成新 Schedule。
- AI 外部调用不应长时间占用数据库事务；先记录 Run 状态，再在短事务中落结果。
- 附件元数据与对象存储操作需设计补偿和可重试状态，不能假装跨系统原子。
- Router 和深层 helper 不得随意 `commit`，异常必须回滚并映射为稳定错误。

## 9. Public API 与 Admin API 分离

`/api/public/**` 只读公开内容，在查询层强制 published、public、未删除过滤，并使用 public schema。Question 与 Practice 默认不提供 public API。`/api/admin/**` 负责草稿读取、创建、编辑、删除、题库、练习、练习导入、复习、AI、上传和分类管理；所有 admin 端点必须依赖 `get_current_admin`。

两套 API 可以复用 service 的受控查询能力，但不能复用会泄露内部字段的响应 schema。完整契约见 [目标 API](./api-design.md)。

## 10. 禁止事项

- 不在 router 中堆积业务逻辑或直接到处操作 ORM。
- 不在 model 中加入 HTTP、序列化或外部 AI 调用。
- 不以通用 `type` 重新合并 Post、Note、Mistake。
- 不由前端过滤敏感字段或替代 `get_current_admin`。
- 不让 public API 先读取全部数据再在 Python 中过滤。
- 不在缺少 migration 时改变持久化模型。
- 不把外部网络调用包在长事务中。
- 不让 Practice Import 直接调用 ORM 静默生成正式 Mistake 或 Review Item。
