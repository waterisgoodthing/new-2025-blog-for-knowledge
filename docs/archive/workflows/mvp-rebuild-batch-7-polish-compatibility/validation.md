# Batch 7 验证记录

## 当前状态

执行中；中间证据不代表 Batch 7 已验收。

## P0-01 基线审计与禁止项确认

- 用户于 2026-07-04 明确批准执行 Batch 7 tasks。
- 工作区基线：
  - 当前 worktree 已有大量 Batch 0–6 与其他用户/代理改动，Batch 7 只在批准范围内做增量。
  - 本批涉及 domain：home、manage、mistakes、notes/write、public compatibility、data quality。
- 旧入口审计：
  - `/write-mistake` 已有 `AuthGate`，当前直接进入旧 `StagedMistakeForm`。
  - `/write-mistake/[slug]` 缺少页面级 `AuthGate`，但属于编辑入口，应纳入 P0-02。
  - `/write-note` 已有 `AuthGate`，应保持可用。
  - `/write-note/[slug]` 缺少页面级 `AuthGate`，但属于编辑入口，应纳入 P0-02。
- 公开读取边界审计：
  - `/mistakes` 使用 public `GET /api/notes?type=mistake&status=published`；复习统计、计划、弱点诊断和“添加错题”入口均按 `isAdmin` 条件展示。
  - `/notes` 使用 public `GET /api/notes`；管理操作按 `isAdmin` 条件展示。
  - `/notes` 会匿名读取 `/api/folders` 作为公开筛选树；该接口当前 GET 未强制管理员，写操作仍受管理员保护。
  - `/blog` 的编辑模式按 `isAdmin` 条件启用；详情页走动态 client 内容。
- 管理端状态与危险操作审计：
  - drafts/questions/mistakes/review/attachments/subjects 已有基础 loading/empty/error。
  - 错题草稿“确认入错题”缺少确认；复习提交评分缺少确认但属于高频操作，暂不强制弹窗。
  - 部分创建表单在无科目、无来源题目时只禁用按钮，说明不够清楚。
- 首页与链接审计：
  - `LearningSpaceCard` 已链接 `/manage/drafts`、`/manage/review`、`/manage/dashboard`、`/manage/attachments`。
  - 后续需用 build route table 或静态 route scan 确认可达。
- 禁止项审计：
  - 既有旧 `/api/ai*`、AI service、旧 AI tab 属于历史系统，不纳入 Batch 7 新增能力。
  - Batch 7 不新增 AI、OCR、BKT、完整练习系统、对象存储、云部署、大型功能、新表或迁移。
- P0-01 结论：
  - 可进入小范围实现：旧动态编辑入口加 AuthGate、旧 `/write-mistake` 增加迁移提示、公开页匿名噪音/管理入口检查、管理端少量状态和确认补强、死链检查、本地 runbook 和数据质量只读记录。

## P0-02 旧入口兼容小范围处理

- 修改范围：
  - `src/app/write-mistake/page.tsx`
  - `src/app/write-mistake/[slug]/page.tsx`
  - `src/app/write-note/[slug]/page.tsx`
- 结果：
  - `/write-mistake` 保留旧 `StagedMistakeForm`，新增“旧错题入口已进入兼容模式”提示，并指向 `/manage/mistakes`。
  - `/write-mistake/[slug]` 新增页面级 `AuthGate`。
  - `/write-note/[slug]` 新增页面级 `AuthGate`。
  - `/write-note` 新建入口保持原状。
- 验证：
  - `npx tsc --noEmit`：通过。
- 边界：
  - 未删除旧数据。
  - 未自动迁移旧错题。
  - 未新增复杂兼容层。

## P0-03 公开读取边界收口

- 修改范围：
  - `src/app/mistakes/page.tsx`
- 结果：
  - 匿名公开错题列表仍可读取已发布未隐藏错题。
  - 个人复习元数据（复习次数、EF、下次复习）仅在 `isAdmin` 为 true 时展示。
  - `/mistakes` 未加 `AuthGate`。
  - `/notes` 与 `/blog` 的管理操作仍按 `isAdmin` 条件展示，未纳入额外改动。
- 验证：
  - `npx tsc --noEmit`：通过。
- 边界：
  - 未封闭 `/mistakes`、`/notes`、`/notes/[slug]`、`/blog`、`/blog/[slug]`。
  - 未新增 AI、上传或复习提交公开操作。

## P0-04 管理端 empty/loading/error state 收口

- 修改范围：
  - `src/app/manage/(workspace)/drafts/components/draft-workspace.tsx`
  - `src/app/manage/(workspace)/mistakes/components/mistake-workspace.tsx`
- 结果：
  - 没有可用科目时，题目草稿创建表单显示明确说明，引导先创建并启用科目。
  - 没有 active 正式题目时，错题草稿创建表单显示明确说明，引导先确认题目入库。
- 验证：
  - `npx tsc --noEmit`：通过。
- 边界：
  - 未新增状态库。
  - 未新增假数据或假成功状态。

## P0-05 表单校验与危险操作确认

- 修改范围：
  - `src/app/manage/(workspace)/drafts/components/draft-workspace.tsx`
  - `src/app/manage/(workspace)/drafts/components/draft-editor.tsx`
  - `src/app/manage/(workspace)/questions/components/question-editor.tsx`
  - `src/app/manage/(workspace)/mistakes/components/mistake-detail.tsx`
- 结果：
  - 新建题目草稿时，单选/多选至少需要两个选项。
  - 编辑题目草稿并保存或确认入库时，单选/多选至少需要两个选项。
  - 编辑正式题目时，单选/多选至少需要两个选项。
  - 错题草稿确认入正式错题前增加确认，说明会同时创建复习项。
- 验证：
  - `npx tsc --noEmit`：通过。
- 边界：
  - 未新增完整练习系统。
  - 未新增统计系统。
  - 未修改后端权限边界。

## P0-06 首页入口与明显死链检查

- 静态扫描范围：
  - `src/app/(home)/learning-space-card.tsx`
  - `src/app/manage/components/manage-sidebar.tsx`
  - `src/app/manage/(workspace)/dashboard/page.tsx`
  - `src/app/mistakes`
  - `src/app/notes`
  - `src/app/manage`
- 关键入口：
  - `/manage/review`
  - `/manage/drafts`
  - `/manage/dashboard`
  - `/manage/attachments`
  - `/manage/questions`
  - `/manage/mistakes`
  - `/manage/subjects`
  - `/manage/ai`
  - `/manage/jobs`
  - `/manage/settings`
  - `/write`
  - `/write-note`
  - `/write-mistake`
  - `/mistakes/review`
- 结论：
  - 以上静态入口均有对应 App Router 页面或动态路由。
  - 本项未发现需要代码修正的明显死链。
  - build route table 将在 P0-09 统一记录。

## P0-07 数据质量只读检查

- 检查方式：
  - 使用后端配置建立数据库连接。
  - 只读查询表存在性、行数、孤儿关联与附件 storage key 路径模式。
  - 未输出数据库连接串。
- 报告：
  - `data-quality-report.md`
- 关键结果：
  - Batch 2–5 新表存在但当前为空：subjects、chapters、knowledge_points、question_drafts、questions、
    mistake_drafts、mistakes、review_items、review_records、attachments、attachment_links 均为 0 行。
  - `notes` 共 13 行。
  - legacy `notes(type='mistake')` 共 5 行，且 5 行均为 `published` 与 `hidden=false`。
  - questions/question_drafts/mistakes/mistake_drafts/review_items/review_records/attachment_links 孤儿检查为 0。
  - attachments `storage_key` 类路径泄露检查为 0。
- 边界：
  - 未写入。
  - 未删除。
  - 未自动迁移 legacy mistake notes。

## P0-08 本地试运行说明

- 新增文档：
  - `local-runbook.md`
- 覆盖内容：
  - 前置条件。
  - `npm run check`、`npm run init`、`npm run setup`。
  - 手动依赖安装。
  - Alembic 迁移。
  - 管理员密码与可选 Passkey。
  - FastAPI 与 Next.js 本地启动。
  - 公开读取、管理登录、科目/知识点、草稿到题库、错题与复习、附件、Batch 6 占位试跑。
  - 常见 API 连接、迁移、权限、端口问题。
- 边界：
  - 不包含云部署。
  - 不包含对象存储。
  - 不建议生产认证绕过。

## P0-09 全量验证、审查与移交

- `git diff --check`：通过。
- `npx tsc --noEmit`：通过。
- `npm run build`：通过；route table 包含：
  - `/`
  - `/manage`
  - `/manage/dashboard`
  - `/manage/drafts`
  - `/manage/questions`
  - `/manage/mistakes`
  - `/manage/review`
  - `/manage/attachments`
  - `/manage/ai`
  - `/manage/jobs`
  - `/manage/settings`
  - `/mistakes`
  - `/mistakes/review`
  - `/notes`
  - `/notes/[id]`
  - `/blog`
  - `/blog/[id]`
  - `/write`
  - `/write-mistake`
  - `/write-mistake/[slug]`
  - `/write-note`
  - `/write-note/[slug]`
- 后端导入检查：
  - `cd backend && .venv/bin/python -c "from main import app; print('backend import ok')"`：通过。
- 后端健康检查：
  - `curl http://localhost:8000/api/health`：`{"status":"ok","db":"ok"}`。
- 浏览器匿名验收：
  - 使用临时 dev server `http://localhost:3025`；未杀已有 `localhost:2025` 进程。
  - `/mistakes` 可访问，页面文本未出现 EF、下次复习、添加错题、编辑、删除、上传、AI 分析、重新生成等管理噪音。
  - `/write-note/some-slug` 导向 `/manage` 登录入口。
  - `/write-mistake/some-slug` 导向 `/manage` 登录入口。
  - `/manage/dashboard` 导向 `/manage` 登录入口。
- 非阻塞警告：
  - build 输出 `baseline-browser-mapping` 数据超过两个月。
  - build 输出 Node `[DEP0205] module.register()` deprecation warning。
  - 浏览器日志出现 `SiteSettingsLoader` API 连接失败；同轮 shell 健康检查显示后端和 DB ok，记录为环境/全站噪音。
- 审查记录：
  - 已补充 `audit.md`，列明影响范围、权限边界、数据质量、验证证据、剩余风险和下一轮建议。

## 总结

Batch 7 实现侧收口完成，状态为等待用户验收；不得由代理自行宣称整个项目闭环。
