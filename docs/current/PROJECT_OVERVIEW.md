# 个人学习系统项目概览

基线日期：2026-10-09（Asia/Shanghai）。对象：`refactor/baseline` 工作区，HEAD `4a954eaa92952fcc5a6b18a2e15d2e824b094e41`，包含既有未提交开发成果。

## 定位与成熟度

当前产品是公开内容站点与私有个人学习工作区共存的单仓库系统。源码具备**MVP能力骨架与部分学习闭环实现**，当前完整运行可用性尚未验证；整体状态 `PARTIAL`。本轮文档交付与产品发布验收分开记录：单测通过并不证明最新业务链、生产数据或部署完整。

优势是已有正式 Question/Mistake/Review 模型、服务端会话授权、人审草稿闸门、复习记录、确定性练习推荐以及双 schema 漂移门禁。主要问题集中在兼容写法分叉、AI 输入来源与确认审计、生命周期/统计口径、完整浏览器验收和文档多重权威。暂不需要服务拆分、目录大迁移或新增队列平台。

## 当前产品范围

|能力|当前范围|边界|
|---|---|---|
|公开内容|blog、notes、canonical public mistakes、内容展示与辅助工具|后端过滤发布/可见性；不同辅助页面有各自权限|
|知识组织|Subjects、KP、Note-KP、WikiLink/反链、版本、文件夹/标签|不等于长期 KnowledgeNode/Graph 目标全部落地|
|题库/错题|正式题目、草稿审核、练习 Attempt、错答草稿、正式 Mistake|legacy Note 错题写冻结，兼容读仍在|
|复习|ReviewItem v2、再答、0–5评分、ReviewRecord、mastered|mastered 是单项复习状态，不是连续 KP 掌握度|
|反馈/今日练习|KP统计、Dashboard、实时选题|无持久 StudyPlan/StudyTask 完成状态|
|采集/AI|附件、Capture 人工录入、可选 AI 候选、Run审查/治理摘要|OCR默认关闭；canonical AI确认仍有已确认合同缺口|
|运行交付|Next/OpenNext、FastAPI/PostgreSQL、CI配置、smoke脚本|构建、完整浏览器业务流、数据库、远端CI及生产未验；10/11–12只有加载阻断观察|

## 阅读顺序与唯一当前入口

1. [当前真实架构](architecture/ARCHITECTURE_CURRENT.md)：目录、实体、API、链路与未实现目标。
2. [架构审查](audits/ARCHITECTURE_AUDIT.md)：证据、分类、影响和主智能体裁决。
3. [开发状态](PROJECT_STATUS.md)：Week/PR、返工与其他计划家族的三层状态。
4. [下一阶段路线](ROADMAP.md)：优先级、依赖和可验收退出条件；仅建议，不是实施授权。
5. [文档索引](DOCUMENTATION_INDEX.md)：当前、目标、历史、失效条款及完整清单。
6. [设计合理性评估](architecture/DESIGN_RATIONALE_REVIEW.md)：后端边界与前端八维目标；建议，非已实施/视觉验收。
7. [执行跟踪](audits/CURRENT_REVIEW_TRACKER.md)与[本轮验证](audits/CURRENT_REVIEW_EVIDENCE.md)。

## 数据和权限

正式内容及学习事实由 FastAPI/PostgreSQL 管理；附件字节和公开图片仍有文件系统存储，不能把所有资源都称为数据库真源。私有附件与公开图片必须分开。静态配置、展示素材、种子和旧导出残留并不构成另一条已支持的内容写主线。

管理员身份使用 HttpOnly `admin_session` 随机 token 与数据库 `AdminSession`，后端 `get_current_admin` 是实际授权边界。GitHub 历史集成、JWT 配置残留和前端 AuthGate 均不能替代该合同。

本轮仅修改技术文档。没有业务修复、数据库/迁移、真实 provider、生产、commit/push/部署。所有后续实现与发布需按对应范围另行授权。
