# 个人学习系统目标架构

## 项目重新定义

2025 Blog 的目标产品定义是：**公开内容系统 + 私有个人学习管理系统**。

公开内容系统负责博客、公开笔记和公开文章展示。私有学习管理系统负责科目、知识点、题库、练习、错题、复习、附件、OCR、AI 识别、草稿审核、后台任务、搜索、统计和设置。博客只是 Content Publishing 域的一种公开输出，不应继续充当全部数据与交互的中心。

目标架构以清晰的领域边界代替 `notes.type` 对多种业务语义的复用：

1. **Content Publishing**：公开文章的撰写、发布和展示。
2. **Knowledge Notes**：个人知识笔记的沉淀、关联和选择性公开。
3. **Question Bank**：题目本体、来源、去重信息和复用关系。
4. **Practice System**：一次练习、逐题作答、练习导入和练习报告。
5. **Mistake System**：需要复盘的错题、错因、解析和确认流程。
6. **Review System**：学习项目、调度状态、复习记录和统计。
7. **AI Assistant**：可追踪、可重试的识别、批改、分析和报告任务。
8. **Capture / OCR**：上传材料、文字版面识别和内容类型路由。
9. **Draft Review**：AI、OCR 和 Capture 输出进入正式系统前的人工确认闸门。
10. **Media / Attachments**：文件存储、元数据和业务实体关联。
11. **Taxonomy / Subjects**：科目、章节、知识点、标签及知识关系。
12. **Jobs / Search / Analytics / Settings**：异步处理、统一检索、统计报告和参数治理。
13. **Auth / Admin**：管理通行密钥、会话、授权和审计。

## 架构原则

- `posts`、`notes`、`questions`、`practice_sessions`、`mistakes` 是职责不同的业务实体，不依赖通用 `type` 字段区分。
- 多题导入不再属于错题系统；它升级为练习导入，保存题目、作答、错题草稿与练习报告。
- 科目是一级学习维度，知识点是题库、错题、复习和 BKT 掌握度的核心单位。
- AI、OCR 和 Capture Router 输出只能进入草稿、建议、报告或分析，必须经过结构化校验和人工确认。
- 公开读取与管理员操作使用不同路由和 API 命名空间。
- 复习系统拥有学习状态和历史，不拥有错题内容。
- AI 是辅助能力；业务实体可以没有 AI 运行记录而正常创建、编辑和发布。
- 附件是独立资源，不把文件列表永久嵌入业务实体 JSON。
- 分类关系可查询、可约束，不以逗号分隔文本或自由 JSON 代替。
- 前端保护负责体验，后端鉴权才是安全边界。
- 迁移采取可验证、可回滚的分阶段切换，不进行大爆炸式重构。

## 文档导航

- [MVP 第一版范围冻结](./mvp-scope.md)
- [学习系统总流程](./learning-system-flow.md)
- [功能域边界](./domains.md)
- [目标数据模型](./data-model.md)
- [科目系统](./subject-system.md)
- [知识组织系统](./taxonomy-system.md)
- [题库系统设计](./question-bank-system.md)
- [练习系统设计](./practice-system.md)
- [错题系统](./mistake-system.md)
- [复习系统](./review-system.md)
- [附件系统](./attachment-system.md)
- [OCR 系统](./ocr-system.md)
- [Capture Router](./capture-router.md)
- [AI 系统](./ai-system.md)
- [AI 管理台](./ai-admin-console.md)
- [草稿审核系统](./draft-review-system.md)
- [后台任务系统](./job-queue-system.md)
- [搜索系统](./search-system.md)
- [统计与报告系统](./analytics-report-system.md)
- [设置系统](./settings-system.md)
- [UI 重构方向](./ui-redesign.md)
- [目标路由](./routes.md)
- [目标 API](./api-design.md)
- [权限模型](./permissions.md)
- [迁移计划](./migration-plan.md)
- [实现阶段](./implementation-phases.md)
- [技术栈基线](./tech-stack.md)
- [前端结构规范](./frontend-structure.md)
- [后端结构规范](./backend-structure.md)
- [渲染系统规范](./rendering-system.md)
- [图标系统规范](./icon-system.md)
- [思维导图系统规范](./mindmap-system.md)

## 本轮范围

本轮仅输出目标架构与技术落地蓝图。它不是现有实现的补丁，也不表示已批准数据库、API、页面、组件或数据迁移改造。本轮不修改 `src/`、`backend/`、配置文件或数据库迁移；后续每个实现阶段都必须单独设计、审批和验收。

## 第一版统一范围

第一版代码实现上限由 [MVP 第一版范围冻结](./mvp-scope.md) 统一定义，并严格按
Batch 0 至 Batch 7 顺序推进。核心目标是手工学习闭环：科目、知识点、题目草稿、
人工审核、正式题目、错题草稿、人工审核、正式错题、简单复习项和复习记录。

第一版核心闭环不依赖 AI、OCR、Capture Router、BKT 或完整练习系统。附件基础属于
Batch 5；AI/OCR 在 Batch 6 只提供明确标注“第一版暂未启用”的占位。Review 第一版
只使用 `review_items`、`review_records`、固定间隔或简单 SM-2，以及
`review_items.next_review_at`。

暂缓完整 AI、真实 OCR、Capture Router 自动分流、BKT 与掌握度事件、完整练习系统、
后台任务真实队列、搜索索引、统计报告、对象存储、云部署、向量库、RAG、全自动
知识图谱、无确认自动入库、AI 自动修改复习计划、多用户权限分级和大规模批审。

## 学习系统主链路

```text
subjects
↓
knowledge_points
↓
question_drafts
↓
人工审核
↓
questions
↓
mistake_drafts
↓
人工审核
↓
mistakes
↓
review_items
↓
review_records
```

这是 MVP 候选目标链路，不表示独立 question/mistake 表已经存在。当前错题仍可能使用
`Note(type="mistake")`；独立模型的共存、迁移和回滚方案必须在对应批次单独审批。
长期完整上传、AI、练习与审核链路见 [学习系统总流程](./learning-system-flow.md)。

## 现状与目标状态

本文档集描述目标架构，统一使用“拟新增”“待实现”“待迁移”或“兼容旧系统”。当前 `Note(type="mistake")`、`/api/notes`、旧写作/复习路由与静态 GitHub 文件工作流仍可能存在；它们不等于目标架构已经落地，必须通过 [迁移计划](./migration-plan.md) 分阶段切换。
