# Batch 7 审查记录

## 审查结论

Batch 7 已完成实现侧收口，当前状态为：**等待用户验收，不自动宣称整个项目闭环**。

本批只做体验收口、旧路由兼容、公开读取边界、数据质量只读检查和本地试运行说明。未新增
AI、OCR、BKT、完整练习系统、对象存储、云部署、新表、迁移或大型功能。

## 影响范围

- old write routes：`/write-mistake`、`/write-mistake/[slug]`、`/write-note/[slug]`
- public mistakes：`/mistakes`
- manage workspace：
  - drafts
  - questions
  - mistakes
- workflow/spec：Batch 7 workflow 与 specs 文档

## 实现侧变更

- `/write-mistake` 保留旧表单，新增兼容模式提示，指向 `/manage/mistakes`。
- `/write-mistake/[slug]` 与 `/write-note/[slug]` 增加页面级 `AuthGate`。
- `/mistakes` 对未登录访客隐藏个人复习元数据：复习次数、EF、下次复习。
- 题目草稿创建在没有可用科目时显示明确空状态。
- 错题草稿创建在没有 active 正式题目时显示明确空状态。
- 单选/多选草稿与正式题目至少需要两个选项。
- 错题草稿确认入正式错题前增加确认，说明会同时创建复习项。
- 新增数据质量只读报告与本地试运行说明。

## 权限边界

- `/mistakes` 保持公开读取，没有添加 `AuthGate`。
- `/write-mistake/[slug]`、`/write-note/[slug]` 属于编辑入口，现由 `AuthGate` 页面级保护。
- `/manage/*` 继续继承工作区 `AuthGate`。
- 本次未依赖 `AUTH_BYPASS` 作为权限验收。
- 后端写入、上传、复习、管理 API 权限未放宽。

## 数据质量

数据质量检查只读执行：

- Batch 2–5 新表存在，但当前本地数据为空。
- legacy `notes(type='mistake')` 共 5 条，且均为公开 `published`、`hidden=false`。
- 孤儿关联检查为 0。
- 附件 `storage_key` 类路径泄露检查为 0。

详见 `data-quality-report.md`。

## 验证证据

- `git diff --check`：通过。
- `npx tsc --noEmit`：通过。
- `npm run build`：通过；route table 包含 Batch 7 关注路由。
- 后端导入检查：`cd backend && .venv/bin/python -c "from main import app"` 通过。
- 后端健康检查：`curl http://localhost:8000/api/health` 返回 `{"status":"ok","db":"ok"}`。
- 浏览器匿名验收：
  - `/mistakes` 可访问，未出现复习元数据、编辑、删除、上传、AI 分析、重新生成等管理噪音。
  - `/write-note/[slug]` 导向 `/manage` 登录入口。
  - `/write-mistake/[slug]` 导向 `/manage` 登录入口。
  - `/manage/dashboard` 导向 `/manage` 登录入口。

## 非阻塞警告

- build 输出提示 `baseline-browser-mapping` 数据超过两个月。
- build 输出提示 Node `[DEP0205] module.register()` deprecation warning。
- 应用内浏览器日志出现 `SiteSettingsLoader` 访问 `http://localhost:8000` 失败；同轮 shell 健康检查显示
  后端与数据库均为 ok。该噪音记录为浏览器/全站环境待查项，不是 Batch 7 新增 API。

## 剩余风险

### RISK-B7-001

- 风险类型：数据 / 体验
- 风险描述：Batch 2–5 新表当前为空，因此本批无法证明有真实新 MVP 数据时的全部体验路径。
- 影响范围：manage drafts/questions/mistakes/review/attachments
- 严重程度：中
- 当前状态：部分处理
- 建议措施：用户验收时按 `local-runbook.md` 创建一组本地样例数据再试跑。
- 是否进入下一轮需求：否，作为用户验收步骤保留。

### RISK-B7-002

- 风险类型：架构 / 数据迁移
- 风险描述：legacy `Note(type='mistake')` 与新 `mistakes` 模型并存；本批未迁移旧数据。
- 影响范围：公开 `/mistakes` 与管理 `/manage/mistakes`
- 严重程度：中
- 当前状态：未处理
- 建议措施：若要统一数据模型，单独开需求、设计迁移、回滚和验收。
- 是否进入下一轮需求：是，若用户后续决定统一旧错题与新错题模型。

### RISK-B7-003

- 风险类型：环境 / 噪音
- 风险描述：应用内浏览器里出现 `SiteSettingsLoader` API 连接失败日志，但 shell 健康检查显示后端 ok。
- 影响范围：浏览器验收日志清洁度
- 严重程度：低
- 当前状态：未处理
- 建议措施：如需彻底清理，单独排查 in-app browser 网络、旧日志或全站 settings loader。
- 是否进入下一轮需求：否，除非用户要求清理验收噪音。

## 下一轮需求建议

- 如需真正闭环第一版，应由用户用管理员会话按 `local-runbook.md` 创建样例数据并验收。
- 如需统一旧错题与新 `mistakes` 模型，应单独进入数据迁移 workflow。
- 不应把 build 成功等同于整个项目闭环。
