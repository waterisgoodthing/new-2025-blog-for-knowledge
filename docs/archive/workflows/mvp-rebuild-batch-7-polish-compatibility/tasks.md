# 任务清单：Batch 7 体验收口、旧路由兼容、数据质量

> 状态：用户已批准，按 P0-01 至 P0-09 顺序执行。

## P0-01 基线审计与禁止项确认

- [x] 审计 Batch 7 相关旧入口、公开页、管理页、API client、数据表与禁止能力。
- 来源需求：REQ-B7-01 至 REQ-B7-07
- 涉及文件：本 workflow `validation.md`、相关源码只读检查。
- 修改内容：只读审计，不实现。
- 完成标准：列出旧入口当前行为、公开/管理 API 边界、候选修复文件、禁止能力未触碰清单。
- 验证方式：`rg`、route scan、目录检查、现有文档交叉检查。
- 风险说明：若发现需要 AI、OCR、BKT、完整练习、对象存储、云部署或大型重构才能解决，停止并记录为后续需求。
- 完成记录（2026-07-04）：完成旧入口、公开页、管理页状态、首页链接和禁止项只读审计；
  确认本批不新增后端域/表/迁移/大型功能。主要候选修复为旧动态编辑入口 AuthGate、
  `/write-mistake` 迁移提示、管理端确认/空状态补强、死链检查和数据质量只读记录。

## P0-02 旧入口兼容小范围处理

- [x] 处理 `/write-mistake` 与必要旧写作入口的兼容提示、跳转或保留策略。
- 来源需求：REQ-B7-01、REQ-B7-02
- 涉及文件：待 P0-01 审计后精确列出，候选包括 `src/app/write-mistake/**`、`src/app/write-note/**`。
- 修改内容：仅限轻量兼容；`/write-note` 默认保持可用，`/write-mistake` 不得引入复杂兼容层。
- 完成标准：旧入口行为清楚；不会封闭公开读取；不会破坏原写作流；未审批文件不修改。
- 验证方式：TSC、build、browser、route table。
- 风险说明：不得删除旧内容、自动迁移旧错题或把权限重构和编辑器重构混成大 diff。
- 完成记录（2026-07-04）：`/write-mistake` 保留旧表单并新增兼容模式提示，指向
  `/manage/mistakes`；`/write-mistake/[slug]` 与 `/write-note/[slug]` 新增页面级
  `AuthGate`。未删除旧数据、未迁移旧错题、未破坏 `/write-note` 新建入口。`npx tsc --noEmit`
  通过。

## P0-03 公开读取边界收口

- [x] 检查并修正公开 `/mistakes`、`/notes`、`/notes/[slug]`、`/blog`、`/blog/[slug]` 的管理端污染。
- 来源需求：REQ-B7-02
- 涉及文件：待 P0-01 审计后精确列出，候选包括 `src/app/mistakes/**`、`src/app/notes/**`、`src/app/blog/**`、相关 hooks/API。
- 修改内容：隐藏或条件加载管理操作；避免匿名公开页因 admin API 401/403 出现明显错误。
- 完成标准：公开页不加 `AuthGate`，不展示编辑/删除/AI/上传/复习提交操作，匿名访问稳定。
- 验证方式：browser 匿名访问、console/network、TSC、build。
- 风险说明：不得误伤公开博客、公开笔记、公开错题读取。
- 完成记录（2026-07-04）：公开 `/mistakes` 对未登录访客隐藏个人复习元数据
  （复习次数、EF、下次复习），保留公开错题读取；`/mistakes` 未加 AuthGate。`/notes`、`/blog`
  管理操作维持 `isAdmin` 条件展示。`npx tsc --noEmit` 通过。

## P0-04 管理端 empty/loading/error state 收口

- [x] 为已完成 MVP 管理页补齐明显缺失的 empty、loading、error state。
- 来源需求：REQ-B7-03
- 涉及文件：待 P0-01 审计后精确列出，候选包括 `src/app/manage/(workspace)/**`。
- 修改内容：小范围文案、状态块、错误显示、重试/返回路径；不新增状态库或大组件框架。
- 完成标准：无数据、加载、失败状态可读，不用假数据伪装成功。
- 验证方式：browser、TSC、必要 API failure 模拟或源码检查。
- 风险说明：不得顺手改业务模型或扩展新流程。
- 完成记录（2026-07-04）：为题目草稿创建补充“没有可用科目”空状态说明；为错题草稿创建补充
  “没有 active 正式题目”空状态说明。未新增状态库、未使用假数据。`npx tsc --noEmit` 通过。

## P0-05 表单校验与危险操作确认

- [x] 补齐 MVP 范围内明显缺失的必填校验、格式校验和删除/归档/拒绝/解除关联确认。
- 来源需求：REQ-B7-04
- 涉及文件：待 P0-01 审计后精确列出，候选包括 drafts/questions/mistakes/review/attachments/subjects 管理组件。
- 修改内容：最小校验、禁用态、错误提示、确认文案；后端权限不变。
- 完成标准：明显无效输入有反馈；危险操作确认说明对象和后果。
- 验证方式：browser、TSC、定向后端测试或 API 检查。
- 风险说明：不得新增完整练习系统、统计系统或复杂工作流。
- 完成记录（2026-07-04）：题目草稿创建、草稿编辑/确认、正式题目编辑为选择题时增加至少两个选项校验；
  错题草稿确认入正式错题前增加明确确认，说明会同时创建复习项。`npx tsc --noEmit` 通过。

## P0-06 首页入口与明显死链检查

- [x] 检查首页学习轻卡、管理侧栏、dashboard 与 MVP 主链路明显死链，并做小范围修正。
- 来源需求：REQ-B7-05
- 涉及文件：待 P0-01 审计后精确列出，候选包括 `src/app/(home)/**`、`src/app/manage/components/manage-sidebar.tsx`、dashboard。
- 修改内容：首页轻卡指向已批准管理入口；修正明显 404 或误导性链接。
- 完成标准：MVP 范围主入口没有明显死链；不新增营销页或大型导航。
- 验证方式：route scan、build route table、browser 点击验证。
- 风险说明：不得把公开站做大规模视觉重构。
- 完成记录（2026-07-04）：静态扫描首页学习轻卡、管理侧栏、dashboard、公开/旧写作入口与
  `src/app` route 文件；未发现 MVP 主入口明显死链。本项无代码改动，后续 build route table
  在 P0-09 统一记录。

## P0-07 数据质量只读检查

- [x] 对 Batch 2–5 相关表与 legacy mistake note 进行只读数据质量检查并记录。
- 来源需求：REQ-B7-06
- 涉及文件：本 workflow `validation.md` 或数据质量报告；数据库只读查询。
- 修改内容：只记录，不写入、不删除、不迁移。
- 完成标准：列出检查范围、异常样本、影响、建议措施、是否进入下一轮需求。
- 验证方式：只读 SQL/API inspection、schema/relationship checks。
- 风险说明：不得自动修复、自动合并、自动迁移或删除旧数据。
- 完成记录（2026-07-04）：完成 PostgreSQL 只读 schema/count/orphan 检查并写入
  `data-quality-report.md`。Batch 2–5 新表存在但当前为空；legacy `notes(type='mistake')`
  有 5 条且均为公开；孤儿关联与附件 `storage_key` 路径泄露检查为 0。未写入、未迁移、未删除。

## P0-08 本地试运行说明

- [x] 编写并核对第一版 MVP 本地试运行说明。
- 来源需求：REQ-B7-07
- 涉及文件：候选 `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/local-runbook.md` 或 README 链接。
- 修改内容：依赖、环境、迁移、启动、登录、核心链路、常见失败排查。
- 完成标准：步骤可复现；不包含生产认证绕过、云部署或对象存储指引。
- 验证方式：命令核对、浏览器/API 试跑记录。
- 风险说明：不得把本地试运行说明扩展为生产部署方案。
- 完成记录（2026-07-04）：新增 `local-runbook.md`，覆盖前置检查、初始化、迁移、管理员凭据、
  启动、公开读取、管理主链路、附件、Batch 6 占位和常见失败；未包含云部署、对象存储或生产认证绕过。

## P0-09 全量验证、审查与移交

- [x] 创建 audit/validation，更新 checklist，填写 handoff，明确剩余风险和下一轮需求。
- 来源需求：全部
- 涉及文件：本 workflow 文档与 Batch 7 spec checklist/handoff。
- 修改内容：记录兼容改动、状态收口、数据质量、本地试运行、权限、合同、浏览器证据和剩余风险。
- 完成标准：Batch 7 仅进入等待用户验收；不得由代理自行宣称整个项目闭环。
- 验证方式：`git diff --check`、`npx tsc --noEmit`、`npm run build`、必要后端测试、browser、数据质量只读证据。
- 风险说明：任何新增 AI/OCR/BKT/完整练习/对象存储/云部署/大型功能或旧数据自动迁移都阻塞验收。
- 完成记录（2026-07-04）：补齐 `audit.md`、更新 `validation.md`、Batch 7 checklist 与
  handoff；`git diff --check`、`npx tsc --noEmit`、`npm run build`、后端导入检查通过；
  后端 `/api/health` 返回 ok；浏览器匿名验收确认公开 `/mistakes` 无管理噪音，旧动态编辑入口与
  `/manage/dashboard` 被 AuthGate 导向登录入口。Batch 7 进入等待用户验收，不自动宣称项目闭环。

## 执行顺序

严格按 P0-01 → P0-09；每完成一项立即更新本文件。

## 审批记录

- [x] 用户已于 2026-07-04 明确批准执行 Batch 7 tasks。
