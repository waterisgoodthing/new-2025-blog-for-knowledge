# UI V2 Information Architecture（F2，2026-09-13）

本轮只输出映射，不迁移路由。

## 目标 IA

```text
首页 (/)
学习
├── 今日任务
├── 题库
├── 错题
└── 复习
知识
├── 科目
├── 知识点
└── 笔记
分析
├── 掌握度
├── 薄弱点
└── 学习趋势
资料（附件/采集/图片工具）
设置
```

## Current → Proposed → Status

| Current Route | Proposed | Status | 备注 |
|---|---|---|---|
| `/` | 首页 | KEEP | — |
| `/manage/dashboard` | 学习/今日任务 + 分析摘要入口 | REFACTOR | 整页重写本轮禁止，仅 IA 占位 |
| `/manage/questions` | 学习/题库 | KEEP | — |
| `/mistakes` + `/manage/mistakes` | 学习/错题 | REFACTOR | 公共读 visibility cutover 归 Week3 PR-09，本轨不动 |
| `/manage/review` | 学习/复习 | MIGRATE_LATER | 等 Week2 PR-08 Review 切片批准 |
| `/manage/subjects` | 知识/科目 | KEEP | — |
| `/manage/knowledge-points` | 知识/知识点 | KEEP | — |
| `/notes` + `/manage/notes` | 知识/笔记 | REFACTOR | 双入口收敛候选，需批准 |
| `/manage/analytics` | 分析/掌握度·薄弱点·趋势 | MIGRATE_LATER | 等 Week3 PR-10/11 canonical 数据 |
| `/manage/search` | 全局搜索 | KEEP | — |
| `/manage/attachments` + `/manage/capture` + `/image-toolbox` | 资料 | KEEP | Capture 失败路径 UI 归 PR-14，本轨不动 |
| `/manage/ai` | 资料/AI（治理后） | MIGRATE_LATER | 等 PR-19 AI 纪律 |
| `/manage/jobs` | 系统/任务 | KEEP | — |
| `/manage/settings` | 设置 | KEEP | — |
| `/manage/drafts` | 知识/草稿 | KEEP | — |
| `/write*` 三编辑器 | 统一创建（refactor-plan 方向） | MIGRATE_LATER | 大规模迁移不在本轮 |
| `/blog*` | 内容/博客（公共） | LEGACY | 静态源为空，迁移归后端轨 |
| `/guestbook` | UNKNOWN | UNKNOWN | 待确认归属 |
| `/music`, `/pictures`, `/discover` 等内容页 | KEEP | KEEP | 非学习域，不纳入 V2 首版 |

## 本轮决议

- 不新增路由，不改 `middleware`/守卫，不动 public/private ownership。
- `MIGRATE_LATER` 项进入 `UI_V2_BACKEND_GAPS.md` 跟踪，不在本轮实施。
