# Handoff

## 本批完成内容

- 旧 `/write-mistake` 保留旧表单并新增兼容模式提示，指向 `/manage/mistakes`。
- `/write-mistake/[slug]` 与 `/write-note/[slug]` 增加页面级 `AuthGate`。
- `/mistakes` 公共页对未登录访客隐藏个人复习元数据。
- 管理端草稿/错题创建补齐无科目、无 active 正式题目的解释性空状态。
- 单选/多选题目补齐至少两个选项校验。
- 错题草稿确认入正式错题前增加确认提示。
- 完成明显死链静态检查。
- 完成数据质量只读报告。
- 完成本地试运行说明。
- 完成全量验证与审查记录。

## 修改文件

- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/README.md`
- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/requirements.md`
- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/design.md`
- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/tasks.md`
- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/validation.md`
- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/audit.md`
- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/data-quality-report.md`
- `docs/workflows/mvp-rebuild-batch-7-polish-compatibility/local-runbook.md`
- `docs/specs/mvp-rebuild/batch-7-polish-compatibility/checklist.md`
- `docs/specs/mvp-rebuild/batch-7-polish-compatibility/handoff.md`
- `src/app/write-mistake/page.tsx`
- `src/app/write-mistake/[slug]/page.tsx`
- `src/app/write-note/[slug]/page.tsx`
- `src/app/mistakes/page.tsx`
- `src/app/manage/(workspace)/drafts/components/draft-workspace.tsx`
- `src/app/manage/(workspace)/drafts/components/draft-editor.tsx`
- `src/app/manage/(workspace)/questions/components/question-editor.tsx`
- `src/app/manage/(workspace)/mistakes/components/mistake-workspace.tsx`
- `src/app/manage/(workspace)/mistakes/components/mistake-detail.tsx`

## 未完成事项

- 用户尚未完成管理员会话下的完整样例数据试跑。
- legacy `Note(type='mistake')` 与新 `mistakes` 模型仍并存；本批未迁移旧数据。
- 应用内浏览器存在 `SiteSettingsLoader` API 连接失败噪音，shell 健康检查显示后端 ok，未在本批处理。

## 风险点

- Batch 2–5 新表当前为空，真实数据下的体验仍需用户按 runbook 创建样例后验收。
- 旧错题 Note 与新 mistakes 模型并存，未来统一需要独立迁移 workflow。
- 不得把本批收口结果等同于整个项目闭环；仍需用户明确验收。

## 下一批前置条件

本批没有后续 MVP 批次。完成验收后，应根据失败项与剩余风险建立下一轮需求，
或明确归档决定；不得把“构建成功”等同于整个项目闭环。

当前 Batch 7 已是最后一个 MVP 批次。验收后应根据失败项与剩余风险建立下一轮需求，
或由用户明确归档；不得把“构建成功”等同于整个项目闭环。

## 用户确认

- [ ] 用户已确认 Batch 7 验收通过
