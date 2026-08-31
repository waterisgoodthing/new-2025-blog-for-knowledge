# R1 内容创建与编辑能力矩阵

日期：2026-07-30
状态：`AUDITED / NO EDITOR MERGE`

## 当前能力

| 能力 | 普通笔记 | 博客 | 错题 |
|---|---|---|---|
| 主要创建入口 | `/write-note` | `/write`；`/write-note` 也可选择 blog | `/manage/capture` 与兼容 `/write-mistake` |
| 页面保护 | `AuthGate` | `AuthGate` | 管理 route-group 或页面 `AuthGate` |
| 持久化 | Note API，`type=note` | Note API，`type=blog` | 正式学习域 + 兼容 Note mistake 路径 |
| Markdown 编辑/预览 | 有 | 有，独立 Store/预览 | 结构化表单与生成内容 |
| 图片 | Note upload | 封面、本地占位符替换、正文图片 | 证据图片、Capture attachment |
| 元数据 | title、slug、tags、category、folder、sort | title、slug、tags、summary、category、cover、hidden | subject、difficulty、question、answers、analysis、knowledge points、review metadata |
| AI | 对话辅助、标签建议 | 不作为 R1 统一目标 | OCR/错因/最终分析/图解，带人工确认边界 |
| 保存后去向 | `/notes/[slug]` | `/blog/[slug]` | 草稿审核、正式错题与复习链 |
| 主要风险 | 文件夹上下文和标签提醒 | 两个可创建 blog 的 UI 能力重叠 | 不能降级为通用 Markdown |

## R1 决策

1. Dashboard “写笔记”进入 `/write-note`。
2. Dashboard “写博客”进入功能更完整的 `/write`。
3. Dashboard “图片采集”进入 `/manage/capture`，这是新学习闭环的首选错题入口。
4. `/write-mistake` 继续作为历史兼容入口，不从 R1 Dashboard 主推。
5. R1 不合并 Store、DTO、字段、上传逻辑或 AI 流程。

## 后续独立任务建议

建议任务名：`R2 内容创建入口适配与编辑器能力去重`。

开始前必须重新审批，并至少完成：

- 决定 `/write-note` 中 `type=blog` 与 `/write` 的唯一职责。
- 为 note/blog/mistake 定义显式 DTO，不使用通用 `any`。
- 保留博客封面/图片处理、笔记 folder context 和错题一等字段。
- 建立创建、编辑、失败保留输入、返回上下文和权限测试。
- 在能力等价前不删除任何旧路由。

R2 不由 R1 自动授权。
