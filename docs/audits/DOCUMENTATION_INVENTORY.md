# 全量技术文档有效性清单

基线日期：2026-10-09；设计评估补充：2026-10-12。机械盘点Git追踪及非忽略未追踪的非public Markdown，包含隐藏目录（排除Git忽略内容、node_modules/venv、公开文章；.agents内5份忽略Markdown不在此清单）。每份文件读取路径、标题、内容哈希、复选框与分类。分类不是逐段准确性或整项产品验收。A/B/C核代码；D语义审查49份优先文档，Lead审查当前/高风险入口。未逐行审阅其余历史段落。

有效性：CURRENT=本轮/现行入口；RULE_REFERENCE=Agent规则；TARGET_OR_STAGE_SPEC=目标或阶段设计；HISTORICAL_SNAPSHOT=当时记录；LOGICALLY_ARCHIVED=旧当前路线/边界；REFERENCE_RECHECK=维护参考，执行前复核。框数统计口径为行首可含空白的 `- [x]` / `- [X]` / `- [ ]` 列表标记；不计正文、表格或编号列表中的同形字符，不解析代码围栏。此为文本统计，**不得推导完成率**。

当前清单：1220份 Markdown（2026-10-11新增设计评估；10/09复查1219份）；前两阶段1218为默认rg漏隐藏PR模板的当时结果，保留于原证据，不再称完整口径。102个workflow目录（101含Markdown，另1仅artifact）。

|路径|标题|有效性|核验深度|勾选/未勾（非验收）|
|---|---|---|---|---|
|[.github/pull_request_template.md](<../../.github/pull_request_template.md>)|PR模板|RULE_REFERENCE|隐藏非忽略文档；机械盘点|0/11|
|[docs/architecture/DESIGN_RATIONALE_REVIEW.md](<../architecture/DESIGN_RATIONALE_REVIEW.md>)|整体设计合理性：领域边界与体验质量|TARGET_OR_STAGE_SPEC|Lead源码抽查/专项证据/视觉阻断；未实施|0/0|
|[AGENTS.md](<../../AGENTS.md>)|Repository Agent Rules|CURRENT|当前基线/受治理入口|0/0|
|[CODEX-OUTCOME-REVIEW.md](<../../CODEX-OUTCOME-REVIEW.md>)|Codex 成果审核报告|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[CODEX-TECHNICAL-AUDIT-REPORT-20260801.md](<../../CODEX-TECHNICAL-AUDIT-REPORT-20260801.md>)|Codex 任务组技术审计报告|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[CONTRIBUTING.md](<../../CONTRIBUTING.md>)|贡献指南|CURRENT|当前基线/受治理入口|0/0|
|[I-SERIES-CODEX-TECHNICAL-AUDIT-REPORT.md](<../../I-SERIES-CODEX-TECHNICAL-AUDIT-REPORT.md>)|I系列Codex技术审查报告|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[IMPROVEMENT_BACKLOG.md](<../../IMPROVEMENT_BACKLOG.md>)|IMPROVEMENT BACKLOG — Personal Learning System|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[NEXT-STEPS-RECOMMENDATIONS.md](<../../NEXT-STEPS-RECOMMENDATIONS.md>)|下一步行动建议|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/8|
|[NOTEBOOK_SYSTEM_FULL_CHAIN_USABILITY_AUDIT.md](<../../NOTEBOOK_SYSTEM_FULL_CHAIN_USABILITY_AUDIT.md>)|个人笔记本系统全链路可用性审查报告|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[PERSONAL_LEARNING_SYSTEM_AUDIT.md](<../../PERSONAL_LEARNING_SYSTEM_AUDIT.md>)|PERSONAL LEARNING SYSTEM AUDIT|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[Personal_Learning_System_Week_Completion_Quality_Audit.md](<../../Personal_Learning_System_Week_Completion_Quality_Audit.md>)|个人学习系统全 Week 完成质量技术审计|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[README.md](<../../README.md>)|2025 Blog|CURRENT|当前基线/受治理入口|0/0|
|[SECURITY.md](<../../SECURITY.md>)|安全策略|CURRENT|当前基线/受治理入口|0/0|
|[SYSTEM_AUDIT_REPORT.md](<../../SYSTEM_AUDIT_REPORT.md>)|SYSTEM_AUDIT_REPORT.md|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[SYSTEM_MAP.md](<../../SYSTEM_MAP.md>)|SYSTEM_MAP.md|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[agents/README.md](<../../agents/README.md>)|Agent Team|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/gates.md](<../../agents/gates.md>)|Decision Gates|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/orchestration.md](<../../agents/orchestration.md>)|Worker Orchestration|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/permissions.md](<../../agents/permissions.md>)|Persona Worker Permissions|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/report-template.md](<../../agents/report-template.md>)|Result Report Template|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/task-template.md](<../../agents/task-template.md>)|Task Assignment Template|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/api-contract-reviewer.md](<../../agents/workers/api-contract-reviewer.md>)|API Contract Reviewer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/compatibility-retirement-engineer.md](<../../agents/workers/compatibility-retirement-engineer.md>)|Compatibility / Retirement Engineer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/database-architect.md](<../../agents/workers/database-architect.md>)|Database Architect|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/learning-workflow-reviewer.md](<../../agents/workers/learning-workflow-reviewer.md>)|Learning Workflow Reviewer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/principal-software-architect.md](<../../agents/workers/principal-software-architect.md>)|Principal Software Architect|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/principal-technical-reviewer.md](<../../agents/workers/principal-technical-reviewer.md>)|Principal Technical Reviewer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/product-architect.md](<../../agents/workers/product-architect.md>)|Product Architect|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-ai-llm-engineer.md](<../../agents/workers/senior-ai-llm-engineer.md>)|Senior AI / LLM Engineer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-backend-engineer.md](<../../agents/workers/senior-backend-engineer.md>)|Senior Backend Engineer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-data-engineer.md](<../../agents/workers/senior-data-engineer.md>)|Senior Data Engineer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-devops-sre.md](<../../agents/workers/senior-devops-sre.md>)|Senior DevOps / SRE|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-domain-analyst.md](<../../agents/workers/senior-domain-analyst.md>)|Senior Domain Analyst|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-frontend-engineer.md](<../../agents/workers/senior-frontend-engineer.md>)|Senior Frontend Engineer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-qa-sdet.md](<../../agents/workers/senior-qa-sdet.md>)|Senior QA / SDET|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-recommendation-engineer.md](<../../agents/workers/senior-recommendation-engineer.md>)|Senior Recommendation Engineer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-security-engineer.md](<../../agents/workers/senior-security-engineer.md>)|Senior Security Engineer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[agents/workers/senior-ux-interaction-designer.md](<../../agents/workers/senior-ux-interaction-designer.md>)|Senior UX / Interaction Designer|RULE_REFERENCE|机械盘点；内容需按任务复核|0/0|
|[design-process-keepalive.md](<../../design-process-keepalive.md>)|进程保活与公网连接稳定性设计文档|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/45|
|[design.md](<../../design.md>)|个人笔记本与博客系统闭环与安全修复设计文档 (Revised Edition)|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/DOCUMENTATION_INDEX.md](<../DOCUMENTATION_INDEX.md>)|文档索引与有效性|CURRENT|当前基线/受治理入口|0/0|
|[docs/GitHub开源项目实现方案与技术选型报告.md](<../GitHub开源项目实现方案与技术选型报告.md>)|GitHub 开源项目实现方案与技术选型报告|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/PROJECT_OVERVIEW.md](<../PROJECT_OVERVIEW.md>)|个人学习系统项目概览|CURRENT|当前基线/受治理入口|0/0|
|[docs/PROJECT_STATUS.md](<../PROJECT_STATUS.md>)|当前开发状态|CURRENT|当前基线/受治理入口|0/0|
|[docs/ROADMAP.md](<../ROADMAP.md>)|下一阶段开发建议：原计划续接|CURRENT|当前基线/受治理入口|0/0|
|[docs/adr/ADR-001-postgresql-source-of-truth.md](<../adr/ADR-001-postgresql-source-of-truth.md>)|ADR-001：PostgreSQL 是唯一事实来源|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/adr/ADR-002-knowledge-node-relational-storage.md](<../adr/ADR-002-knowledge-node-relational-storage.md>)|ADR-002：KnowledgeNode 使用关系模型，不以 GraphDB 作为事实存储|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/adr/ADR-003-today-orchestrator.md](<../adr/ADR-003-today-orchestrator.md>)|ADR-003：Today 是统一入口与 Dashboard Orchestrator|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/adr/ADR-004-ai-human-review.md](<../adr/ADR-004-ai-human-review.md>)|ADR-004：AI 输出必须经过人工审核|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/adr/README.md](<../adr/README.md>)|Architecture Decision Records|CURRENT|当前基线/受治理入口|0/0|
|[docs/ai-mistake-navigation-upgrade-plan.md](<../ai-mistake-navigation-upgrade-plan.md>)|AI 配置、错题工作流与导航体验升级方案|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/architecture/ARCHITECTURE_CURRENT.md](<../architecture/ARCHITECTURE_CURRENT.md>)|当前真实架构|CURRENT|当前基线/受治理入口|0/0|
|[docs/architecture/README.md](<../architecture/README.md>)|架构文档入口与目标设计|CURRENT|当前基线/受治理入口|0/0|
|[docs/architecture/ai-admin-console.md](<../architecture/ai-admin-console.md>)|AI Admin Console|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/ai-governance.md](<../architecture/ai-governance.md>)|AI 治理：当前 Run 来源与确认契约|CURRENT|当前基线/受治理入口|0/0|
|[docs/architecture/ai-system.md](<../architecture/ai-system.md>)|AI System|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/analytics-report-system.md](<../architecture/analytics-report-system.md>)|Analytics / Report System 学习统计与报告系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/api-design.md](<../architecture/api-design.md>)|目标 API 设计|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/attachment-system.md](<../architecture/attachment-system.md>)|Attachment System 附件系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/backend-structure.md](<../architecture/backend-structure.md>)|后端结构规范|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/capture-router.md](<../architecture/capture-router.md>)|Capture Router 上传识别路由器|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/data-model.md](<../architecture/data-model.md>)|目标数据模型|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/domains.md](<../architecture/domains.md>)|功能域边界|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/draft-review-system.md](<../architecture/draft-review-system.md>)|Draft Review System 草稿审核系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/frontend-structure.md](<../architecture/frontend-structure.md>)|前端结构规范|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/icon-system.md](<../architecture/icon-system.md>)|图标系统规范|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/implementation-phases.md](<../architecture/implementation-phases.md>)|实施阶段与第一版收口|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/job-queue-system.md](<../architecture/job-queue-system.md>)|Job Queue System 后台任务系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/learning-system-flow.md](<../architecture/learning-system-flow.md>)|学习系统总流程|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/migration-plan.md](<../architecture/migration-plan.md>)|从现有结构迁移到目标结构|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/mindmap-system.md](<../architecture/mindmap-system.md>)|思维导图系统规范|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/mistake-system.md](<../architecture/mistake-system.md>)|Mistake System 错题系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/mvp-scope.md](<../architecture/mvp-scope.md>)|MVP 第一版范围冻结|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/ocr-system.md](<../architecture/ocr-system.md>)|OCR System|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/permissions.md](<../architecture/permissions.md>)|目标权限模型|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/personal-learning-system-v2.md](<../architecture/personal-learning-system-v2.md>)|个人学习系统 V2 最高层架构|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/practice-system.md](<../architecture/practice-system.md>)|练习系统设计|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/question-bank-system.md](<../architecture/question-bank-system.md>)|题库系统设计|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/rendering-system.md](<../architecture/rendering-system.md>)|渲染系统规范|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/review-system.md](<../architecture/review-system.md>)|Review System 复习系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/routes.md](<../architecture/routes.md>)|目标路由|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/search-system.md](<../architecture/search-system.md>)|Search System 搜索系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/settings-system.md](<../architecture/settings-system.md>)|Settings System 设置系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/subject-system.md](<../architecture/subject-system.md>)|Subject System 科目系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/taxonomy-system.md](<../architecture/taxonomy-system.md>)|Taxonomy System 知识组织系统|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/tech-stack.md](<../architecture/tech-stack.md>)|技术栈基线|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/architecture/ui-redesign.md](<../architecture/ui-redesign.md>)|UI 重构方向|TARGET_OR_STAGE_SPEC|治理标识/优先入口；非全段验收|0/0|
|[docs/audits/ARCHITECTURE_AUDIT.md](<ARCHITECTURE_AUDIT.md>)|架构审查与偏移清单|CURRENT|当前基线/受治理入口|0/0|
|[docs/audits/CURRENT_REVIEW_EVIDENCE.md](<CURRENT_REVIEW_EVIDENCE.md>)|本轮执行与验证证据|CURRENT|当前基线/受治理入口|0/0|
|[docs/audits/CURRENT_REVIEW_TRACKER.md](<CURRENT_REVIEW_TRACKER.md>)|当前架构审查跟踪记录|CURRENT|当前基线/受治理入口|0/0|
|[docs/audits/CURRENT_SOURCE_MAP.md](<CURRENT_SOURCE_MAP.md>)|当前源码覆盖地图|CURRENT|当前基线/受治理入口|0/0|
|[docs/audits/DOCUMENTATION_INVENTORY.md](<DOCUMENTATION_INVENTORY.md>)|全量技术文档有效性清单|CURRENT|当前基线/受治理入口|0/0|
|[docs/audits/archive/AI_GOVERNANCE_PRE_2026-10-09.md](<archive/AI_GOVERNANCE_PRE_2026-10-09.md>)|AI Governance — Run Target Linkage|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/backup-restore.md](<../backup-restore.md>)|数据备份与恢复流程|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/5|
|[docs/batch1-handoff.md](<../batch1-handoff.md>)|Batch 1 Handoff|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/batch1-route-current-state.md](<../batch1-route-current-state.md>)|Batch 1 Route Current State|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/batch1-ui-shell-design.md](<../batch1-ui-shell-design.md>)|Batch 1 UI Shell Design|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/batch1-ui-shell-validation.md](<../batch1-ui-shell-validation.md>)|Batch 1 UI Shell Validation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ci-local-reproduction.md](<../ci-local-reproduction.md>)|CI Local Reproduction (PR-17 / W4-D06)|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/final-backlog.md](<../final-backlog.md>)|Final Backlog|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/final-handoff.md](<../final-handoff.md>)|Final Handoff|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/final-system-boundary.md](<../final-system-boundary.md>)|Final System Boundary|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/note-editor-design.md](<../note-editor-design.md>)|笔记编辑器多维度扩展 — 设计文档|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/4|
|[docs/note-editor-remaining-risks-tasks.md](<../note-editor-remaining-risks-tasks.md>)|笔记编辑器剩余风险修复 — 任务清单|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/60|
|[docs/note-editor-remaining-risks.md](<../note-editor-remaining-risks.md>)|笔记编辑器修复后剩余风险设计文档|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/note-editor-requirements.md](<../note-editor-requirements.md>)|笔记编辑器多维度扩展 — 需求文档|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/note-editor-tasks.md](<../note-editor-tasks.md>)|笔记编辑器多维度扩展 — 任务清单|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/150|
|[docs/personal-knowledge-system-design.md](<../personal-knowledge-system-design.md>)|个人知识与博客系统整体演进设计|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/personal-knowledge-system-p0-audit.md](<../personal-knowledge-system-p0-audit.md>)|个人知识与博客系统 P0 验收记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/personal-knowledge-system-p1-audit.md](<../personal-knowledge-system-p1-audit.md>)|个人知识与博客系统 P1 验收记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/personal-knowledge-system-requirements.md](<../personal-knowledge-system-requirements.md>)|个人知识与博客系统整体演进 — 需求文档|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/personal-knowledge-system-tasks.md](<../personal-knowledge-system-tasks.md>)|个人知识与博客系统整体演进 — 任务清单|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|60/151|
|[docs/phase-c10-context-evidence.md](<../phase-c10-context-evidence.md>)|Phase C+10 Context Evidence|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-contract-evidence.md](<../phase-c10-contract-evidence.md>)|Phase C+10 Contract Evidence|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-execution-report.md](<../phase-c10-execution-report.md>)|Phase C+10 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-guest-evidence.md](<../phase-c10-guest-evidence.md>)|Phase C+10 Guest Schema Evidence|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-index-evidence.md](<../phase-c10-index-evidence.md>)|Phase C+10 Index Evidence|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-integrity-check.md](<../phase-c10-integrity-check.md>)|Phase C+10 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-operational-evidence.md](<../phase-c10-operational-evidence.md>)|Phase C+10 Operational Evidence|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-owner-evidence.md](<../phase-c10-owner-evidence.md>)|Phase C+10 Owner Evidence|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c10-readiness-decision.md](<../phase-c10-readiness-decision.md>)|Phase C+10 Readiness Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-blocker-closure-decision.md](<../phase-c11-blocker-closure-decision.md>)|Phase C+11 Blocker Closure Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-context-resolution-result.md](<../phase-c11-context-resolution-result.md>)|Phase C+11 Context Resolution Result|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-contract-resolution.md](<../phase-c11-contract-resolution.md>)|Phase C+11 Contract Resolution|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-evidence-resolution-matrix.md](<../phase-c11-evidence-resolution-matrix.md>)|Phase C+11 Evidence Resolution Matrix|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-execution-report.md](<../phase-c11-execution-report.md>)|Phase C+11 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-guest-resolution.md](<../phase-c11-guest-resolution.md>)|Phase C+11 Guest Schema Resolution|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-index-resolution.md](<../phase-c11-index-resolution.md>)|Phase C+11 Index Resolution|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-integrity-check.md](<../phase-c11-integrity-check.md>)|Phase C+11 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-operational-resolution.md](<../phase-c11-operational-resolution.md>)|Phase C+11 Operational Evidence Resolution|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c11-owner-confirmation.md](<../phase-c11-owner-confirmation.md>)|Phase C+11 Owner Confirmation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c12-blocker-summary.md](<../phase-c12-blocker-summary.md>)|Phase C+12 Blocker Summary|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c12-closure-criteria.md](<../phase-c12-closure-criteria.md>)|Phase C+12 Closure Criteria|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c12-decision-matrix.md](<../phase-c12-decision-matrix.md>)|Phase C+12 Decision Matrix|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c12-decision-request.md](<../phase-c12-decision-request.md>)|Phase C+12 Governance Decision Request|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c12-execution-report.md](<../phase-c12-execution-report.md>)|Phase C+12 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c12-integrity-check.md](<../phase-c12-integrity-check.md>)|Phase C+12 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c12-risk-acceptance-template.md](<../phase-c12-risk-acceptance-template.md>)|Phase C+12 Risk Acceptance Template|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-context-resolution.md](<../phase-c13-context-resolution.md>)|Phase C+13 Context Authority Resolution|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-execution-report.md](<../phase-c13-execution-report.md>)|Phase C+13 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-final-governance-decision.md](<../phase-c13-final-governance-decision.md>)|Phase C+13 Final Governance Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-guest-schema-decision.md](<../phase-c13-guest-schema-decision.md>)|Phase C+13 Guest Schema Final Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-index-policy-approval.md](<../phase-c13-index-policy-approval.md>)|Phase C+13 Index Policy Approval|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-integrity-check.md](<../phase-c13-integrity-check.md>)|Phase C+13 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-migration-scope-approval.md](<../phase-c13-migration-scope-approval.md>)|Phase C+13 Migration Scope Approval|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-nullable-contract-approval.md](<../phase-c13-nullable-contract-approval.md>)|Phase C+13 Nullable Contract Approval|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-owner-approval-record.md](<../phase-c13-owner-approval-record.md>)|Phase C+13 Owner Approval Record|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-phase-d-authorization-draft.md](<../phase-c13-phase-d-authorization-draft.md>)|Phase C+13 Phase D Authorization Draft|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c13-phase-d-readiness.md](<../phase-c13-phase-d-readiness.md>)|Phase C+13 Phase D Authorization Readiness|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c6-approval-checklist.md](<../phase-c6-approval-checklist.md>)|Phase C+6 Approval Checklist|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/22|
|[docs/phase-c6-decision-matrix.md](<../phase-c6-decision-matrix.md>)|Phase C+6 Decision Matrix|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c6-execution-report.md](<../phase-c6-execution-report.md>)|Phase C+6 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c6-integrity-check.md](<../phase-c6-integrity-check.md>)|Phase C+6 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c7-context-completeness.md](<../phase-c7-context-completeness.md>)|Phase C+7 Context Completeness Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c7-execution-report.md](<../phase-c7-execution-report.md>)|Phase C+7 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c7-final-decision.md](<../phase-c7-final-decision.md>)|Phase C+7 Final Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c7-implementation-decision.md](<../phase-c7-implementation-decision.md>)|Phase C+7 Implementation Authorization Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c7-integrity-check.md](<../phase-c7-integrity-check.md>)|Phase C+7 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c7-preimplementation-validation.md](<../phase-c7-preimplementation-validation.md>)|Phase C+7 Pre-Implementation Validation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-authorization-decision.md](<../phase-c8-authorization-decision.md>)|Phase C+8 Authorization Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-context-governance-decision.md](<../phase-c8-context-governance-decision.md>)|Phase C+8 Context Governance Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-execution-report.md](<../phase-c8-execution-report.md>)|Phase C+8 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-guest-schema-decision.md](<../phase-c8-guest-schema-decision.md>)|Phase C+8 Guest Schema Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-index-policy-decision.md](<../phase-c8-index-policy-decision.md>)|Phase C+8 Index Policy Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-integrity-check.md](<../phase-c8-integrity-check.md>)|Phase C+8 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-nullable-contract-decision.md](<../phase-c8-nullable-contract-decision.md>)|Phase C+8 Nullable Contract Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c8-operational-readiness.md](<../phase-c8-operational-readiness.md>)|Phase C+8 Operational Readiness|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c9-context-resolution.md](<../phase-c9-context-resolution.md>)|Phase C+9 Context Resolution|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c9-execution-report.md](<../phase-c9-execution-report.md>)|Phase C+9 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c9-final-authorization-record.md](<../phase-c9-final-authorization-record.md>)|Phase C+9 Final Authorization Record|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c9-integrity-check.md](<../phase-c9-integrity-check.md>)|Phase C+9 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c9-migration-scope-decision.md](<../phase-c9-migration-scope-decision.md>)|Phase C+9 Migration Scope Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c9-operational-approval.md](<../phase-c9-operational-approval.md>)|Phase C+9 Operational Approval|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-c9-owner-assignment.md](<../phase-c9-owner-assignment.md>)|Phase C+9 Owner Assignment|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-approval-report.md](<../phase-d-approval-report.md>)|Phase D Approval Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-backup-rollback-plan.md](<../phase-d-backup-rollback-plan.md>)|Phase D Backup and Rollback Plan|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-execution-authorization.md](<../phase-d-execution-authorization.md>)|Phase D Execution Authorization|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-execution-scope.md](<../phase-d-execution-scope.md>)|Phase D Execution Scope|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-implementation-authorization-draft.md](<../phase-d-implementation-authorization-draft.md>)|Phase D Implementation Authorization Draft|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-implementation-plan.md](<../phase-d-implementation-plan.md>)|Phase D Implementation Plan|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-migration-final-draft.md](<../phase-d-migration-final-draft.md>)|Phase D Migration Final Draft Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-migration-readiness-analysis.md](<../phase-d-migration-readiness-analysis.md>)|Phase D Migration Readiness Analysis|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-migration-readiness-integrity.md](<../phase-d-migration-readiness-integrity.md>)|Phase D Migration Readiness Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-migration-readiness-report.md](<../phase-d-migration-readiness-report.md>)|Phase D Migration Readiness Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-nullable-drift-analysis.md](<../phase-d-nullable-drift-analysis.md>)|Phase D Nullable Drift Analysis|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-pre-execution-integrity-check.md](<../phase-d-pre-execution-integrity-check.md>)|Phase D Pre-Execution Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-stop-condition.md](<../phase-d-stop-condition.md>)|Phase D Stop Conditions|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d-validation-plan.md](<../phase-d-validation-plan.md>)|Phase D Validation Plan|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-code-change-review.md](<../phase-d1-code-change-review.md>)|Phase D-1 Code Change Draft Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-draft-decision.md](<../phase-d1-draft-decision.md>)|Phase D-1 Migration Draft Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-execution-report.md](<../phase-d1-execution-report.md>)|Phase D-1 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-integrity-check.md](<../phase-d1-integrity-check.md>)|Phase D-1 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-migration-draft-review.md](<../phase-d1-migration-draft-review.md>)|Phase D-1 Migration Draft Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-pre-draft-analysis.md](<../phase-d1-pre-draft-analysis.md>)|Phase D-1 Pre-Draft Analysis|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-scope-validation.md](<../phase-d1-scope-validation.md>)|Phase D-1 Scope Validation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d1-sql-review.md](<../phase-d1-sql-review.md>)|Phase D-1 SQL Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d2-code-change-review.md](<../phase-d2-code-change-review.md>)|Phase D-2 Code Change Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d2-execution-report.md](<../phase-d2-execution-report.md>)|Phase D-2 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d2-integrity-check.md](<../phase-d2-integrity-check.md>)|Phase D-2 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d2-model-registry-audit.md](<../phase-d2-model-registry-audit.md>)|Phase D-2 Model Registry Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-alembic-validation.md](<../phase-d3-alembic-validation.md>)|Phase D-3 Alembic Validation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-backup-validation.md](<../phase-d3-backup-validation.md>)|Phase D-3 Backup Evidence Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-environment-confirmation.md](<../phase-d3-environment-confirmation.md>)|Phase D-3 Environment Confirmation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-execution-readiness-decision.md](<../phase-d3-execution-readiness-decision.md>)|Phase D-3 Final Execution Readiness Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-execution-report.md](<../phase-d3-execution-report.md>)|Phase D-3 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-integrity-check.md](<../phase-d3-integrity-check.md>)|Phase D-3 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-restore-validation.md](<../phase-d3-restore-validation.md>)|Phase D-3 Restore Verification Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-schema-drift-review.md](<../phase-d3-schema-drift-review.md>)|Phase D-3 Schema Drift Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d3-validation-report.md](<../phase-d3-validation-report.md>)|Phase D-3 Validation Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-alembic-final-state.md](<../phase-d4-alembic-final-state.md>)|Phase D-4 Alembic Final State|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-backup-completed.md](<../phase-d4-backup-completed.md>)|Phase D-4 Backup Completed|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-backup-record.md](<../phase-d4-backup-record.md>)|Phase D-4 Backup Record|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-backup-restore-integrity.md](<../phase-d4-backup-restore-integrity.md>)|Phase D-4 Backup Restore Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-backup-restore-report.md](<../phase-d4-backup-restore-report.md>)|Phase D-4 Backup Restore Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-backup-validation-result.md](<../phase-d4-backup-validation-result.md>)|Phase D-4 Backup Validation Result|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-code-validation.md](<../phase-d4-code-validation.md>)|Phase D-4 Code Validation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-environment-confirmation.md](<../phase-d4-environment-confirmation.md>)|Phase D-4 Environment Confirmation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-execution-report.md](<../phase-d4-execution-report.md>)|Phase D-4 Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-final-execution-approval.md](<../phase-d4-final-execution-approval.md>)|Phase D-4 Final Execution Approval|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-final-scope-freeze.md](<../phase-d4-final-scope-freeze.md>)|Phase D-4 Final Scope Freeze|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-integrity-check.md](<../phase-d4-integrity-check.md>)|Phase D-4 Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-restore-completed.md](<../phase-d4-restore-completed.md>)|Phase D-4 Restore Completed|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-restore-validation-result.md](<../phase-d4-restore-validation-result.md>)|Phase D-4 Restore Validation Result|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-d4-restore-verification.md](<../phase-d4-restore-verification.md>)|Phase D-4 Restore Verification|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-alembic-runtime-check.md](<../phase-e-alembic-runtime-check.md>)|Phase E Alembic Runtime Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-api-smoke-test.md](<../phase-e-api-smoke-test.md>)|Phase E API Smoke Test|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-database-safety-check.md](<../phase-e-database-safety-check.md>)|Phase E Database Safety Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-execution-report.md](<../phase-e-execution-report.md>)|Phase E Execution Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-git-release-review.md](<../phase-e-git-release-review.md>)|Phase E Git Release Review|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-integrity-check.md](<../phase-e-integrity-check.md>)|Phase E Integrity Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-regression-check.md](<../phase-e-regression-check.md>)|Phase E Runtime Regression Check|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-release-decision.md](<../phase-e-release-decision.md>)|Phase E Release Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-runtime-startup-validation.md](<../phase-e-runtime-startup-validation.md>)|Phase E Runtime Startup Validation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/phase-e-static-validation.md](<../phase-e-static-validation.md>)|Phase E Static Validation|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/project-assessment/mvp-gap-analysis.md](<../project-assessment/mvp-gap-analysis.md>)|MVP Goal Gap Analysis|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/public-deploy-runbook.md](<../public-deploy-runbook.md>)|Public Deploy Runbook|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/refactor-executive-summary.md](<../refactor-executive-summary.md>)|前端重构技术选型 - 执行摘要|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/refactor-github-opensource-report.md](<../refactor-github-opensource-report.md>)|GitHub 开源项目实现方案与技术选型报告|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/refactor-plan/00-CORRECTED-PHASED-PLAN.md](<../refactor-plan/00-CORRECTED-PHASED-PLAN.md>)|学习系统重构方案 - 冲突校正与分阶段实施|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/29|
|[docs/refactor-plan/01-PORTABILITY-SCALABILITY-AUDIT.md](<../refactor-plan/01-PORTABILITY-SCALABILITY-AUDIT.md>)|系统可迁移性、可扩展性与伪实现审查报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/refactor-plan/02-UI-DESIGN-SYSTEM-BLUE-WHITE.md](<../refactor-plan/02-UI-DESIGN-SYSTEM-BLUE-WHITE.md>)|学习系统 UI 设计规范 v2.0（蓝白配色版）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md](<../refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md>)|学习系统重构实施方案（保留视觉风格版）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/35|
|[docs/refactor-plan/04-DESIGN-REFACTOR-PROPOSAL.md](<../refactor-plan/04-DESIGN-REFACTOR-PROPOSAL.md>)|学习系统设计重构方案|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/refactor-plan/README.md](<../refactor-plan/README.md>)|学习系统重构计划文档|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/refactor-plan/UI-DESIGN-SYSTEM-V2.md](<../refactor-plan/UI-DESIGN-SYSTEM-V2.md>)|学习系统 UI 设计规范 v2.0|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/refactor-plan-2026-08-02.md](<../refactor-plan-2026-08-02.md>)|前端重构计划 - 2026-08-02|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/16|
|[docs/releases/v1.0-baseline.md](<../releases/v1.0-baseline.md>)|v1.0 Baseline|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/roadmap-2026-09.md](<../roadmap-2026-09.md>)|历史路线图 2026-09|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/roadmap-design.md](<../roadmap-design.md>)|个人知识系统演进路线 — 设计文档|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/0|
|[docs/roadmap-tasks.md](<../roadmap-tasks.md>)|个人知识系统演进路线 — 任务清单|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|203/91|
|[docs/specs/mvp-rebuild/README.md](<../specs/mvp-rebuild/README.md>)|MVP Rebuild Specs|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-0-docs-freeze/checklist.md](<../specs/mvp-rebuild/batch-0-docs-freeze/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|10/0|
|[docs/specs/mvp-rebuild/batch-0-docs-freeze/handoff.md](<../specs/mvp-rebuild/batch-0-docs-freeze/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|1/0|
|[docs/specs/mvp-rebuild/batch-0-docs-freeze/spec.md](<../specs/mvp-rebuild/batch-0-docs-freeze/spec.md>)|Batch 0：文档冻结与实现约束|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-1-ui-shell/checklist.md](<../specs/mvp-rebuild/batch-1-ui-shell/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|11/0|
|[docs/specs/mvp-rebuild/batch-1-ui-shell/handoff.md](<../specs/mvp-rebuild/batch-1-ui-shell/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|1/0|
|[docs/specs/mvp-rebuild/batch-1-ui-shell/spec.md](<../specs/mvp-rebuild/batch-1-ui-shell/spec.md>)|Batch 1：UI 壳层与首页轻量改造|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-2-subject-taxonomy/checklist.md](<../specs/mvp-rebuild/batch-2-subject-taxonomy/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|12/0|
|[docs/specs/mvp-rebuild/batch-2-subject-taxonomy/handoff.md](<../specs/mvp-rebuild/batch-2-subject-taxonomy/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|1/0|
|[docs/specs/mvp-rebuild/batch-2-subject-taxonomy/spec.md](<../specs/mvp-rebuild/batch-2-subject-taxonomy/spec.md>)|Batch 2：科目 / 知识点基础|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-3-drafts-question-bank/checklist.md](<../specs/mvp-rebuild/batch-3-drafts-question-bank/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|12/0|
|[docs/specs/mvp-rebuild/batch-3-drafts-question-bank/handoff.md](<../specs/mvp-rebuild/batch-3-drafts-question-bank/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|1/0|
|[docs/specs/mvp-rebuild/batch-3-drafts-question-bank/spec.md](<../specs/mvp-rebuild/batch-3-drafts-question-bank/spec.md>)|Batch 3：题目草稿 / 草稿审核 / 题库|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-4-mistakes-review/checklist.md](<../specs/mvp-rebuild/batch-4-mistakes-review/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|13/0|
|[docs/specs/mvp-rebuild/batch-4-mistakes-review/handoff.md](<../specs/mvp-rebuild/batch-4-mistakes-review/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|1/0|
|[docs/specs/mvp-rebuild/batch-4-mistakes-review/spec.md](<../specs/mvp-rebuild/batch-4-mistakes-review/spec.md>)|Batch 4：错题草稿 / 错题系统 / 简单复习|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-5-attachments/checklist.md](<../specs/mvp-rebuild/batch-5-attachments/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|12/0|
|[docs/specs/mvp-rebuild/batch-5-attachments/handoff.md](<../specs/mvp-rebuild/batch-5-attachments/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|1/0|
|[docs/specs/mvp-rebuild/batch-5-attachments/spec.md](<../specs/mvp-rebuild/batch-5-attachments/spec.md>)|Batch 5：附件基础系统|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-6-ai-ocr-placeholders/checklist.md](<../specs/mvp-rebuild/batch-6-ai-ocr-placeholders/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|12/0|
|[docs/specs/mvp-rebuild/batch-6-ai-ocr-placeholders/handoff.md](<../specs/mvp-rebuild/batch-6-ai-ocr-placeholders/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|1/0|
|[docs/specs/mvp-rebuild/batch-6-ai-ocr-placeholders/spec.md](<../specs/mvp-rebuild/batch-6-ai-ocr-placeholders/spec.md>)|Batch 6：AI / OCR 预留接口与占位|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/batch-7-polish-compatibility/checklist.md](<../specs/mvp-rebuild/batch-7-polish-compatibility/checklist.md>)|Checklist|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|12/0|
|[docs/specs/mvp-rebuild/batch-7-polish-compatibility/handoff.md](<../specs/mvp-rebuild/batch-7-polish-compatibility/handoff.md>)|Handoff|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/1|
|[docs/specs/mvp-rebuild/batch-7-polish-compatibility/spec.md](<../specs/mvp-rebuild/batch-7-polish-compatibility/spec.md>)|Batch 7：体验收口、旧路由兼容、数据质量|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/specs/mvp-rebuild/execution-rules.md](<../specs/mvp-rebuild/execution-rules.md>)|MVP Rebuild 执行规则|TARGET_OR_STAGE_SPEC|机械盘点；内容需按任务复核|0/0|
|[docs/suggestions-2026-08-29.md](<../suggestions-2026-08-29.md>)|建议汇总（2026-08-29 全天对话）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-review/issue-inventory.md](<../ui-review/issue-inventory.md>)|UI Issue Inventory|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-review/page-inventory.md](<../ui-review/page-inventory.md>)|UI Page Inventory|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-review/screenshot-index.md](<../ui-review/screenshot-index.md>)|Screenshot Index|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-review/ui-review-report.md](<../ui-review/ui-review-report.md>)|UI Browser Review Report|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/8|
|[docs/ui-upgrade-design.md](<../ui-upgrade-design.md>)|UI 升级设计文档 — 日常使用体验修正|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-upgrade-diff-report.md](<../ui-upgrade-diff-report.md>)|UI 升级 — 差异化报告|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-upgrade-requirements.md](<../ui-upgrade-requirements.md>)|UI 升级 — 需求文档 v2.0|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-upgrade-tasks.md](<../ui-upgrade-tasks.md>)|UI 升级 — 任务清单 v2.2|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|67/12|
|[docs/ui-v2/UI_V2_ARCHITECTURE.md](<../ui-v2/UI_V2_ARCHITECTURE.md>)|UI V2 Architecture — Repository UI Audit（F0，2026-09-13）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-v2/UI_V2_BACKEND_GAPS.md](<../ui-v2/UI_V2_BACKEND_GAPS.md>)|UI V2 Backend Gaps（F4 起，递增编号；只记录，不修后端）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-v2/UI_V2_COMPONENT_INVENTORY.md](<../ui-v2/UI_V2_COMPONENT_INVENTORY.md>)|UI V2 Component Inventory（F1，2026-09-13）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-v2/UI_V2_CONTRACT_TODAY_TASKS.md](<../ui-v2/UI_V2_CONTRACT_TODAY_TASKS.md>)|GAP-001 Contract — 今日任务统一列表（B2，2026-09-20）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-v2/UI_V2_DESIGN_SYSTEM.md](<../ui-v2/UI_V2_DESIGN_SYSTEM.md>)|UI V2 Design System Foundation（F3，2026-09-13）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-v2/UI_V2_INFORMATION_ARCHITECTURE.md](<../ui-v2/UI_V2_INFORMATION_ARCHITECTURE.md>)|UI V2 Information Architecture（F2，2026-09-13）|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[docs/ui-v2/UI_V2_PROGRESS.md](<../ui-v2/UI_V2_PROGRESS.md>)|UI V2 Progress（第一阶段 F0–F5）|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|8/1|
|[docs/workflows/admin-contract-organization-music-upgrade/README.md](<../workflows/admin-contract-organization-music-upgrade/README.md>)|Admin Contract Organization Music Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/admin-contract-organization-music-upgrade/audit.md](<../workflows/admin-contract-organization-music-upgrade/audit.md>)|Planning Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/admin-contract-organization-music-upgrade/design.md](<../workflows/admin-contract-organization-music-upgrade/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/admin-contract-organization-music-upgrade/handoff-prompt.md](<../workflows/admin-contract-organization-music-upgrade/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/admin-contract-organization-music-upgrade/requirements.md](<../workflows/admin-contract-organization-music-upgrade/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/admin-contract-organization-music-upgrade/tasks.md](<../workflows/admin-contract-organization-music-upgrade/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|36/0|
|[docs/workflows/admin-contract-organization-music-upgrade/validation.md](<../workflows/admin-contract-organization-music-upgrade/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/README.md](<../workflows/ai-mistake-navigation-upgrade/README.md>)|AI 配置、错题工作流与导航体验升级 — P1|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/design.md](<../workflows/ai-mistake-navigation-upgrade/design.md>)|Design: AI 错题导航升级 — P1 UI 与路由体验实现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/diff-report.md](<../workflows/ai-mistake-navigation-upgrade/diff-report.md>)|Diff Report: AI 错题导航升级 — P1|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/findings.md](<../workflows/ai-mistake-navigation-upgrade/findings.md>)|Findings & Decisions|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/progress.md](<../workflows/ai-mistake-navigation-upgrade/progress.md>)|Progress Log|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/report.md](<../workflows/ai-mistake-navigation-upgrade/report.md>)|最终验证报告: AI 错题导航升级 — P1|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/requirements.md](<../workflows/ai-mistake-navigation-upgrade/requirements.md>)|Requirements: AI 错题导航升级 — P1 UI 与路由体验实现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-mistake-navigation-upgrade/task_plan.md](<../workflows/ai-mistake-navigation-upgrade/task_plan.md>)|Task Plan: AI 错题导航升级 — P1 UI 与路由体验实现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|36/0|
|[docs/workflows/ai-mistake-navigation-upgrade/tasks.md](<../workflows/ai-mistake-navigation-upgrade/tasks.md>)|Tasks: AI 错题导航升级 — P1 UI 与路由体验实现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|23/0|
|[docs/workflows/ai-mistake-navigation-upgrade/validation.md](<../workflows/ai-mistake-navigation-upgrade/validation.md>)|Validation: AI 错题导航升级 — P1|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-skill-pipeline/README.md](<../workflows/ai-skill-pipeline/README.md>)|AI Skill Pipeline Knowledge Base|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-skill-pipeline/design.md](<../workflows/ai-skill-pipeline/design.md>)|Design: AI Skill Pipeline Knowledge Base|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-skill-pipeline/handoff-prompt.md](<../workflows/ai-skill-pipeline/handoff-prompt.md>)|Handoff Prompt: AI Skill Pipeline Knowledge Base|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-skill-pipeline/report.md](<../workflows/ai-skill-pipeline/report.md>)|AI Skill Pipeline Knowledge Base 完备报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-skill-pipeline/requirements.md](<../workflows/ai-skill-pipeline/requirements.md>)|Requirements: AI Skill Pipeline Knowledge Base|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ai-skill-pipeline/tasks.md](<../workflows/ai-skill-pipeline/tasks.md>)|Tasks: AI Skill Pipeline Knowledge Base|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|29/0|
|[docs/workflows/ai-skill-pipeline/validation.md](<../workflows/ai-skill-pipeline/validation.md>)|Validation: AI Skill Pipeline Knowledge Base|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|70/0|
|[docs/workflows/batch-10-1-prompt-registry-runtime-integration/README.md](<../workflows/batch-10-1-prompt-registry-runtime-integration/README.md>)|Batch 10.1：Prompt Registry Runtime Integration|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-1-prompt-registry-runtime-integration/design.md](<../workflows/batch-10-1-prompt-registry-runtime-integration/design.md>)|Design：Batch 10.1 Prompt Registry Runtime Integration|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-1-prompt-registry-runtime-integration/handoff.md](<../workflows/batch-10-1-prompt-registry-runtime-integration/handoff.md>)|Handoff：Batch 10.1 Prompt Registry Runtime Integration|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-1-prompt-registry-runtime-integration/requirements.md](<../workflows/batch-10-1-prompt-registry-runtime-integration/requirements.md>)|Requirements：Batch 10.1 Prompt Registry Runtime Integration|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-1-prompt-registry-runtime-integration/tasks.md](<../workflows/batch-10-1-prompt-registry-runtime-integration/tasks.md>)|Tasks：Batch 10.1 Prompt Registry Runtime Integration|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|102/0|
|[docs/workflows/batch-10-1-prompt-registry-runtime-integration/validation.md](<../workflows/batch-10-1-prompt-registry-runtime-integration/validation.md>)|Validation：Batch 10.1 Prompt Registry Runtime Integration|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-2-prompt-engineering-standardization/README.md](<../workflows/batch-10-2-prompt-engineering-standardization/README.md>)|Batch 10.2：Prompt Engineering Standardization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-2-prompt-engineering-standardization/audit.md](<../workflows/batch-10-2-prompt-engineering-standardization/audit.md>)|Audit：Batch 10.2 剩余风险与归档决定|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-2-prompt-engineering-standardization/design.md](<../workflows/batch-10-2-prompt-engineering-standardization/design.md>)|Design：Batch 10.2 Prompt Engineering Standardization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-2-prompt-engineering-standardization/requirements.md](<../workflows/batch-10-2-prompt-engineering-standardization/requirements.md>)|Requirements：Batch 10.2 Prompt Engineering Standardization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-2-prompt-engineering-standardization/tasks.md](<../workflows/batch-10-2-prompt-engineering-standardization/tasks.md>)|Tasks：Batch 10.2 Prompt Engineering Standardization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|9/0|
|[docs/workflows/batch-10-2-prompt-engineering-standardization/validation.md](<../workflows/batch-10-2-prompt-engineering-standardization/validation.md>)|Validation：Batch 10.2 Prompt Engineering Standardization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-task-prompt-validator/README.md](<../workflows/batch-10-task-prompt-validator/README.md>)|Batch 10：Task / Prompt / Validator 管理|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-task-prompt-validator/design.md](<../workflows/batch-10-task-prompt-validator/design.md>)|Design：Batch 10 Task / Prompt / Validator 管理|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-10-task-prompt-validator/requirements.md](<../workflows/batch-10-task-prompt-validator/requirements.md>)|Requirements：Batch 10 Task / Prompt / Validator 管理|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/10|
|[docs/workflows/batch-10-task-prompt-validator/tasks.md](<../workflows/batch-10-task-prompt-validator/tasks.md>)|Tasks：Batch 10 Task / Prompt / Validator 管理|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|104/1|
|[docs/workflows/batch-10-task-prompt-validator/validation.md](<../workflows/batch-10-task-prompt-validator/validation.md>)|Validation：Batch 10 Task / Prompt / Validator 管理|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/README.md](<../workflows/batch-11-ai-run-audit-human-review/README.md>)|Batch 11：AI Run 审计与人工流转|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/audit.md](<../workflows/batch-11-ai-run-audit-human-review/audit.md>)|Audit：Batch 11 最终审计与关闭|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/design.md](<../workflows/batch-11-ai-run-audit-human-review/design.md>)|Design：Batch 11 AI Run 审计与人工流转|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/handoff-prompt.md](<../workflows/batch-11-ai-run-audit-human-review/handoff-prompt.md>)|Handoff：Batch 11 关闭后的可选补证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/handoff.md](<../workflows/batch-11-ai-run-audit-human-review/handoff.md>)|Handoff：Batch 11 Browser Verification Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/requirements.md](<../workflows/batch-11-ai-run-audit-human-review/requirements.md>)|Requirements：Batch 11 AI Run 审计与人工流转|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/tasks.md](<../workflows/batch-11-ai-run-audit-human-review/tasks.md>)|Tasks：Batch 11 AI Run 审计与人工流转|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|13/0|
|[docs/workflows/batch-11-ai-run-audit-human-review/validation.md](<../workflows/batch-11-ai-run-audit-human-review/validation.md>)|Validation：Batch 11 AI Run 审计与人工流转|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/README.md](<../workflows/batch-12-ai-provider-routing-cost-stability/README.md>)|Batch 12 — AI Provider Routing / Cost / Stability|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/audit.md](<../workflows/batch-12-ai-provider-routing-cost-stability/audit.md>)|Audit — Batch 12 Design Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/checklist.md](<../workflows/batch-12-ai-provider-routing-cost-stability/checklist.md>)|Checklist|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|38/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/design.md](<../workflows/batch-12-ai-provider-routing-cost-stability/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/handoff.md](<../workflows/batch-12-ai-provider-routing-cost-stability/handoff.md>)|Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/requirements.md](<../workflows/batch-12-ai-provider-routing-cost-stability/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/risks.md](<../workflows/batch-12-ai-provider-routing-cost-stability/risks.md>)|Risks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/tasks.md](<../workflows/batch-12-ai-provider-routing-cost-stability/tasks.md>)|Tasks — Batch 12 Provider Routing / Cost / Stability Closure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|32/0|
|[docs/workflows/batch-12-ai-provider-routing-cost-stability/validation.md](<../workflows/batch-12-ai-provider-routing-cost-stability/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/README.md](<../workflows/batch-2-subject-knowledge-point/README.md>)|Batch 2 - Subject / Knowledge Point Domain Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/api-contract.md](<../workflows/batch-2-subject-knowledge-point/api-contract.md>)|API Contract|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/audit.md](<../workflows/batch-2-subject-knowledge-point/audit.md>)|Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/decisions.md](<../workflows/batch-2-subject-knowledge-point/decisions.md>)|Decisions|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/domain-design.md](<../workflows/batch-2-subject-knowledge-point/domain-design.md>)|Domain Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/migration-strategy.md](<../workflows/batch-2-subject-knowledge-point/migration-strategy.md>)|Migration Strategy|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/requirements.md](<../workflows/batch-2-subject-knowledge-point/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/route-design.md](<../workflows/batch-2-subject-knowledge-point/route-design.md>)|Route Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/schema-design.md](<../workflows/batch-2-subject-knowledge-point/schema-design.md>)|Schema Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-2-subject-knowledge-point/tasks.md](<../workflows/batch-2-subject-knowledge-point/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|18/5|
|[docs/workflows/batch-2-subject-knowledge-point/validation.md](<../workflows/batch-2-subject-knowledge-point/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/README.md](<../workflows/batch-3-question-system/README.md>)|Batch 3 Question System|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/api-contract.md](<../workflows/batch-3-question-system/api-contract.md>)|API Contract|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/audit.md](<../workflows/batch-3-question-system/audit.md>)|Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/design.md](<../workflows/batch-3-question-system/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/domain-design.md](<../workflows/batch-3-question-system/domain-design.md>)|Domain Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/handoff-prompt.md](<../workflows/batch-3-question-system/handoff-prompt.md>)|Batch 3 Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/implementation-plan.md](<../workflows/batch-3-question-system/implementation-plan.md>)|Implementation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/requirements.md](<../workflows/batch-3-question-system/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/schema-design.md](<../workflows/batch-3-question-system/schema-design.md>)|Schema Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/tasks.md](<../workflows/batch-3-question-system/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|27/0|
|[docs/workflows/batch-3-question-system/validation-plan.md](<../workflows/batch-3-question-system/validation-plan.md>)|Validation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-3-question-system/validation.md](<../workflows/batch-3-question-system/validation.md>)|Batch 3 Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/README.md](<../workflows/batch-4-mistake-review/README.md>)|Batch 4 Mistake And Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/api-contract.md](<../workflows/batch-4-mistake-review/api-contract.md>)|API Contract|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/audit.md](<../workflows/batch-4-mistake-review/audit.md>)|Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/design.md](<../workflows/batch-4-mistake-review/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/handoff-prompt.md](<../workflows/batch-4-mistake-review/handoff-prompt.md>)|Batch 4 Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/requirements.md](<../workflows/batch-4-mistake-review/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/schema-design.md](<../workflows/batch-4-mistake-review/schema-design.md>)|Schema Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/tasks.md](<../workflows/batch-4-mistake-review/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|24/0|
|[docs/workflows/batch-4-mistake-review/validation-plan.md](<../workflows/batch-4-mistake-review/validation-plan.md>)|Validation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-4-mistake-review/validation.md](<../workflows/batch-4-mistake-review/validation.md>)|Batch 4 Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/README.md](<../workflows/batch-5-attachments/README.md>)|Batch 5 Attachments|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/api-contract.md](<../workflows/batch-5-attachments/api-contract.md>)|API Contract|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/audit.md](<../workflows/batch-5-attachments/audit.md>)|Current-State Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/design.md](<../workflows/batch-5-attachments/design.md>)|Domain And UI Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/handoff-prompt.md](<../workflows/batch-5-attachments/handoff-prompt.md>)|Batch 5 Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/requirements.md](<../workflows/batch-5-attachments/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/schema-design.md](<../workflows/batch-5-attachments/schema-design.md>)|Schema Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/tasks.md](<../workflows/batch-5-attachments/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|20/0|
|[docs/workflows/batch-5-attachments/validation-plan.md](<../workflows/batch-5-attachments/validation-plan.md>)|Validation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-5-attachments/validation.md](<../workflows/batch-5-attachments/validation.md>)|Batch 5 Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/README.md](<../workflows/batch-6-ai-ocr-placeholders/README.md>)|Batch 6 AI And OCR Placeholders|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/api-contract.md](<../workflows/batch-6-ai-ocr-placeholders/api-contract.md>)|Reserved API Contract|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/audit.md](<../workflows/batch-6-ai-ocr-placeholders/audit.md>)|Current-State Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/design.md](<../workflows/batch-6-ai-ocr-placeholders/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/handoff-prompt.md](<../workflows/batch-6-ai-ocr-placeholders/handoff-prompt.md>)|Batch 6 Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/requirements.md](<../workflows/batch-6-ai-ocr-placeholders/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/tasks.md](<../workflows/batch-6-ai-ocr-placeholders/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|15/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/validation-plan.md](<../workflows/batch-6-ai-ocr-placeholders/validation-plan.md>)|Validation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-6-ai-ocr-placeholders/validation.md](<../workflows/batch-6-ai-ocr-placeholders/validation.md>)|Batch 6 Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-7-compatibility-closure/README.md](<../workflows/batch-7-compatibility-closure/README.md>)|Batch 7 Compatibility And Closure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-7-compatibility-closure/audit.md](<../workflows/batch-7-compatibility-closure/audit.md>)|Current-State Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-7-compatibility-closure/design.md](<../workflows/batch-7-compatibility-closure/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-7-compatibility-closure/handoff-prompt.md](<../workflows/batch-7-compatibility-closure/handoff-prompt.md>)|Batch 7 Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-7-compatibility-closure/requirements.md](<../workflows/batch-7-compatibility-closure/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-7-compatibility-closure/tasks.md](<../workflows/batch-7-compatibility-closure/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|16/0|
|[docs/workflows/batch-7-compatibility-closure/validation-plan.md](<../workflows/batch-7-compatibility-closure/validation-plan.md>)|Validation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-7-compatibility-closure/validation.md](<../workflows/batch-7-compatibility-closure/validation.md>)|Batch 7 Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-8-image-mistake-capture/README.md](<../workflows/batch-8-image-mistake-capture/README.md>)|Batch 8：图片错题采集与 AI 错因草稿|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-8-image-mistake-capture/checklist.md](<../workflows/batch-8-image-mistake-capture/checklist.md>)|Batch 8 审批与验收检查表|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|43/0|
|[docs/workflows/batch-8-image-mistake-capture/design.md](<../workflows/batch-8-image-mistake-capture/design.md>)|设计文档：Batch 8 图片错题采集与 AI 错因草稿|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-8-image-mistake-capture/handoff.md](<../workflows/batch-8-image-mistake-capture/handoff.md>)|Batch 8 移交说明|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-8-image-mistake-capture/requirements.md](<../workflows/batch-8-image-mistake-capture/requirements.md>)|需求文档：Batch 8 图片错题采集与 AI 错因草稿|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-8-image-mistake-capture/risks.md](<../workflows/batch-8-image-mistake-capture/risks.md>)|Batch 8 剩余风险清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-8-image-mistake-capture/tasks.md](<../workflows/batch-8-image-mistake-capture/tasks.md>)|任务清单：Batch 8 图片错题采集与 AI 错因草稿|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/0|
|[docs/workflows/batch-8-image-mistake-capture/validation.md](<../workflows/batch-8-image-mistake-capture/validation.md>)|Batch 8 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-9-ai-gateway-kernel/README.md](<../workflows/batch-9-ai-gateway-kernel/README.md>)|Batch 9：AI Gateway 最小内核|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-9-ai-gateway-kernel/design.md](<../workflows/batch-9-ai-gateway-kernel/design.md>)|Design：Batch 9 AI Gateway 最小内核|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-9-ai-gateway-kernel/requirements.md](<../workflows/batch-9-ai-gateway-kernel/requirements.md>)|Requirements：Batch 9 AI Gateway 最小内核|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-9-ai-gateway-kernel/risks.md](<../workflows/batch-9-ai-gateway-kernel/risks.md>)|Risks：Batch 9 AI Gateway 最小内核|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/batch-9-ai-gateway-kernel/tasks.md](<../workflows/batch-9-ai-gateway-kernel/tasks.md>)|Tasks：Batch 9 AI Gateway 最小内核|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|72/0|
|[docs/workflows/batch-9-ai-gateway-kernel/validation.md](<../workflows/batch-9-ai-gateway-kernel/validation.md>)|Validation：Batch 9 AI Gateway 最小内核|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/15|
|[docs/workflows/blog-cover-save-fix/README.md](<../workflows/blog-cover-save-fix/README.md>)|Blog Cover Save Fix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/blog-cover-save-fix/design.md](<../workflows/blog-cover-save-fix/design.md>)|Blog Cover Save Fix Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/blog-cover-save-fix/handoff-prompt.md](<../workflows/blog-cover-save-fix/handoff-prompt.md>)|Blog Cover Save Fix Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/blog-cover-save-fix/requirements.md](<../workflows/blog-cover-save-fix/requirements.md>)|Blog Cover Save Fix Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/blog-cover-save-fix/tasks.md](<../workflows/blog-cover-save-fix/tasks.md>)|Blog Cover Save Fix Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|15/0|
|[docs/workflows/blog-cover-save-fix/validation.md](<../workflows/blog-cover-save-fix/validation.md>)|Blog Cover Save Fix Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ci-clean-checks-fix/README.md](<../workflows/ci-clean-checks-fix/README.md>)|CI Clean Checkout Fix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ci-clean-checks-fix/design.md](<../workflows/ci-clean-checks-fix/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ci-clean-checks-fix/requirements.md](<../workflows/ci-clean-checks-fix/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ci-clean-checks-fix/tasks.md](<../workflows/ci-clean-checks-fix/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|4/0|
|[docs/workflows/ci-clean-checks-fix/validation.md](<../workflows/ci-clean-checks-fix/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/README.md](<../workflows/cleanup-workspace-db-revision-closure/README.md>)|CLEANUP 工作区与 DB Revision 收口|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/acceptance.md](<../workflows/cleanup-workspace-db-revision-closure/acceptance.md>)|CLEANUP 验收报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/audit.md](<../workflows/cleanup-workspace-db-revision-closure/audit.md>)|CLEANUP 审计基线|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/design.md](<../workflows/cleanup-workspace-db-revision-closure/design.md>)|CLEANUP 设计文档|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/diff-report.md](<../workflows/cleanup-workspace-db-revision-closure/diff-report.md>)|CLEANUP Diff 报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/handoff-prompt.md](<../workflows/cleanup-workspace-db-revision-closure/handoff-prompt.md>)|CLEANUP 交接提示|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/next-requirements.md](<../workflows/cleanup-workspace-db-revision-closure/next-requirements.md>)|CLEANUP 下一轮需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/requirements.md](<../workflows/cleanup-workspace-db-revision-closure/requirements.md>)|CLEANUP 需求文档|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/risks.md](<../workflows/cleanup-workspace-db-revision-closure/risks.md>)|CLEANUP 剩余风险清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/tasks.md](<../workflows/cleanup-workspace-db-revision-closure/tasks.md>)|CLEANUP 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/0|
|[docs/workflows/cleanup-workspace-db-revision-closure/validation.md](<../workflows/cleanup-workspace-db-revision-closure/validation.md>)|CLEANUP 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cloudflare-release-2026-08-02/README.md](<../workflows/cloudflare-release-2026-08-02/README.md>)|Cloudflare Release 2026-08-02|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cloudflare-release-2026-08-02/design.md](<../workflows/cloudflare-release-2026-08-02/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cloudflare-release-2026-08-02/requirements.md](<../workflows/cloudflare-release-2026-08-02/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/cloudflare-release-2026-08-02/tasks.md](<../workflows/cloudflare-release-2026-08-02/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|4/0|
|[docs/workflows/cloudflare-release-2026-08-02/validation.md](<../workflows/cloudflare-release-2026-08-02/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/current-architecture-review-2026-10-09/README.md](<../workflows/current-architecture-review-2026-10-09/README.md>)|当前架构与文档基线审查|CURRENT|当前基线/受治理入口|0/0|
|[docs/workflows/current-architecture-review-2026-10-09/design.md](<../workflows/current-architecture-review-2026-10-09/design.md>)|审查方法|CURRENT|当前基线/受治理入口|0/0|
|[docs/workflows/current-architecture-review-2026-10-09/requirements.md](<../workflows/current-architecture-review-2026-10-09/requirements.md>)|交付要求|CURRENT|当前基线/受治理入口|0/0|
|[docs/workflows/current-architecture-review-2026-10-09/tasks.md](<../workflows/current-architecture-review-2026-10-09/tasks.md>)|执行清单|CURRENT|当前基线/受治理入口|16/0|
|[docs/workflows/current-architecture-review-2026-10-09/validation.md](<../workflows/current-architecture-review-2026-10-09/validation.md>)|验证记录|CURRENT|当前基线/受治理入口|0/0|
|[docs/workflows/dependency-runtime-governance/README.md](<../workflows/dependency-runtime-governance/README.md>)|Dependency Runtime Governance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-governance/design.md](<../workflows/dependency-runtime-governance/design.md>)|设计文档：Dependency Runtime Governance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-governance/next-requirements.md](<../workflows/dependency-runtime-governance/next-requirements.md>)|下一轮需求文档：Dependency Runtime Governance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-governance/requirements.md](<../workflows/dependency-runtime-governance/requirements.md>)|需求文档：Dependency Runtime Governance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-governance/risks.md](<../workflows/dependency-runtime-governance/risks.md>)|剩余风险清单：Dependency Runtime Governance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-governance/tasks.md](<../workflows/dependency-runtime-governance/tasks.md>)|任务清单：Dependency Runtime Governance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|6/0|
|[docs/workflows/dependency-runtime-governance/validation.md](<../workflows/dependency-runtime-governance/validation.md>)|验证报告：Dependency Runtime Governance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-risk-cleanup/README.md](<../workflows/dependency-runtime-risk-cleanup/README.md>)|Dependency And Runtime Risk Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-risk-cleanup/design.md](<../workflows/dependency-runtime-risk-cleanup/design.md>)|设计文档：Dependency And Runtime Risk Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-risk-cleanup/next-requirements.md](<../workflows/dependency-runtime-risk-cleanup/next-requirements.md>)|下一轮需求文档：Dependency And Runtime Risk Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-risk-cleanup/requirements.md](<../workflows/dependency-runtime-risk-cleanup/requirements.md>)|需求文档：Dependency And Runtime Risk Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-risk-cleanup/risks.md](<../workflows/dependency-runtime-risk-cleanup/risks.md>)|剩余风险清单：Dependency And Runtime Risk Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/dependency-runtime-risk-cleanup/tasks.md](<../workflows/dependency-runtime-risk-cleanup/tasks.md>)|任务清单：Dependency And Runtime Risk Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|13/0|
|[docs/workflows/dependency-runtime-risk-cleanup/validation.md](<../workflows/dependency-runtime-risk-cleanup/validation.md>)|验证报告：Dependency And Runtime Risk Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/editor-convergence/README.md](<../workflows/editor-convergence/README.md>)|Editor Convergence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/editor-convergence/audit.md](<../workflows/editor-convergence/audit.md>)|Editor Convergence Source Inventory|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/editor-convergence/design.md](<../workflows/editor-convergence/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/editor-convergence/implementation-tasks.md](<../workflows/editor-convergence/implementation-tasks.md>)|Option A Editor Convergence Implementation Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/10|
|[docs/workflows/editor-convergence/requirements.md](<../workflows/editor-convergence/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/editor-convergence/tasks.md](<../workflows/editor-convergence/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|7/0|
|[docs/workflows/editor-convergence/validation.md](<../workflows/editor-convergence/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/README.md](<../workflows/folder-note-assignment-fix/README.md>)|Folder Note Assignment Fix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/audit.md](<../workflows/folder-note-assignment-fix/audit.md>)|Closure Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/design.md](<../workflows/folder-note-assignment-fix/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/diff-report.md](<../workflows/folder-note-assignment-fix/diff-report.md>)|Diff Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/handoff-prompt.md](<../workflows/folder-note-assignment-fix/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/next-iteration.md](<../workflows/folder-note-assignment-fix/next-iteration.md>)|Next Iteration Decision|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/requirements.md](<../workflows/folder-note-assignment-fix/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/residual-risks.md](<../workflows/folder-note-assignment-fix/residual-risks.md>)|Residual Risks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/folder-note-assignment-fix/tasks.md](<../workflows/folder-note-assignment-fix/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|6/0|
|[docs/workflows/folder-note-assignment-fix/validation.md](<../workflows/folder-note-assignment-fix/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-foundation-and-quality/README.md](<../workflows/frontend-foundation-and-quality/README.md>)|前端技术基座与质量保障：F4 前总工作夹|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-foundation-and-quality/audit.md](<../workflows/frontend-foundation-and-quality/audit.md>)|现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-foundation-and-quality/design.md](<../workflows/frontend-foundation-and-quality/design.md>)|设计：F4 前总工作夹|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-foundation-and-quality/f4-input-package.md](<../workflows/frontend-foundation-and-quality/f4-input-package.md>)|F4 输入包（已就绪，等待单独审批；禁止自行执行）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-foundation-and-quality/handoff-prompt.md](<../workflows/frontend-foundation-and-quality/handoff-prompt.md>)|F4 前总工作夹执行 Goal|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-foundation-and-quality/requirements.md](<../workflows/frontend-foundation-and-quality/requirements.md>)|需求：F4 前总工作夹|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-foundation-and-quality/tasks.md](<../workflows/frontend-foundation-and-quality/tasks.md>)|任务清单：F4 前总工作夹|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|49/0|
|[docs/workflows/frontend-foundation-and-quality/validation.md](<../workflows/frontend-foundation-and-quality/validation.md>)|验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-refactor-alignment/README.md](<../workflows/frontend-refactor-alignment/README.md>)|Frontend Refactor Alignment|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-refactor-alignment/audit.md](<../workflows/frontend-refactor-alignment/audit.md>)|Initial Differential Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-refactor-alignment/design.md](<../workflows/frontend-refactor-alignment/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-refactor-alignment/requirements.md](<../workflows/frontend-refactor-alignment/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/frontend-refactor-alignment/tasks.md](<../workflows/frontend-refactor-alignment/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|14/0|
|[docs/workflows/frontend-refactor-alignment/validation.md](<../workflows/frontend-refactor-alignment/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/full-audit-2025-06-23/README.md](<../workflows/full-audit-2025-06-23/README.md>)|Full Audit 2025-06-23|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/full-audit-2025-06-23/audit-report.md](<../workflows/full-audit-2025-06-23/audit-report.md>)|全量审查报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/git-cleanup-public-push/README.md](<../workflows/git-cleanup-public-push/README.md>)|Git Cleanup And Public Push|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/git-cleanup-public-push/design.md](<../workflows/git-cleanup-public-push/design.md>)|Design — Git Cleanup And Public Push|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/git-cleanup-public-push/diff-report.md](<../workflows/git-cleanup-public-push/diff-report.md>)|Diff Report — Git Cleanup And Public Push|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/git-cleanup-public-push/handoff-prompt.md](<../workflows/git-cleanup-public-push/handoff-prompt.md>)|Handoff Prompt — Git Cleanup And Public Push|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/git-cleanup-public-push/requirements.md](<../workflows/git-cleanup-public-push/requirements.md>)|Requirements — Git Cleanup And Public Push|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/git-cleanup-public-push/tasks.md](<../workflows/git-cleanup-public-push/tasks.md>)|Tasks — Git Cleanup And Public Push|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|59/0|
|[docs/workflows/git-cleanup-public-push/validation.md](<../workflows/git-cleanup-public-push/validation.md>)|Validation — Git Cleanup And Public Push|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/github-open-source-selection-report/README.md](<../workflows/github-open-source-selection-report/README.md>)|GitHub Open-Source Selection Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/github-open-source-selection-report/design.md](<../workflows/github-open-source-selection-report/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/github-open-source-selection-report/requirements.md](<../workflows/github-open-source-selection-report/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/github-open-source-selection-report/tasks.md](<../workflows/github-open-source-selection-report/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|8/0|
|[docs/workflows/github-open-source-selection-report/validation.md](<../workflows/github-open-source-selection-report/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/home-music-local-playback-fix/README.md](<../workflows/home-music-local-playback-fix/README.md>)|Home Music Local Playback Fix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/home-music-local-playback-fix/design.md](<../workflows/home-music-local-playback-fix/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/home-music-local-playback-fix/handoff-prompt.md](<../workflows/home-music-local-playback-fix/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/home-music-local-playback-fix/requirements.md](<../workflows/home-music-local-playback-fix/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/home-music-local-playback-fix/tasks.md](<../workflows/home-music-local-playback-fix/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|4/0|
|[docs/workflows/home-music-local-playback-fix/validation.md](<../workflows/home-music-local-playback-fix/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/C6-C12-REVIEW-REPORT.md](<../workflows/i-series-completion-plan/C6-C12-REVIEW-REPORT.md>)|C6-C12 简化路径完成审查报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/NEXT-STEPS.md](<../workflows/i-series-completion-plan/NEXT-STEPS.md>)|I 系列剩余任务：简化路径执行指令|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/2|
|[docs/workflows/i-series-completion-plan/README.md](<../workflows/i-series-completion-plan/README.md>)|I 系列剩余任务完成规划|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/assets/c10-browser-testing.md](<../workflows/i-series-completion-plan/assets/c10-browser-testing.md>)|C10 Browser Testing|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/assets/c10-quality-testing.md](<../workflows/i-series-completion-plan/assets/c10-quality-testing.md>)|C10 Quality Testing|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/assets/c3-artifact-review.md](<../workflows/i-series-completion-plan/assets/c3-artifact-review.md>)|C3 Candidate Artifact 与 Migration Runbook|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/design.md](<../workflows/i-series-completion-plan/design.md>)|I 系列剩余任务设计与只读现状报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/f02-deployment-eligibility.md](<../workflows/i-series-completion-plan/f02-deployment-eligibility.md>)|F-02 Deployment Eligibility Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/f03-final-status-report.md](<../workflows/i-series-completion-plan/f03-final-status-report.md>)|F-03 Personal Learning System V2 最终状态报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/requirements.md](<../workflows/i-series-completion-plan/requirements.md>)|I 系列剩余任务需求与验收门槛|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/risk-register.md](<../workflows/i-series-completion-plan/risk-register.md>)|I 系列完成风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i-series-completion-plan/tasks.md](<../workflows/i-series-completion-plan/tasks.md>)|I 系列剩余任务执行清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|24/0|
|[docs/workflows/i-series-completion-plan/validation.md](<../workflows/i-series-completion-plan/validation.md>)|I 系列完成执行验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/README.md](<../workflows/i10-migration-dry-run/README.md>)|I10 迁移准备与隔离 dry-run|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/assets/dry-run-report.md](<../workflows/i10-migration-dry-run/assets/dry-run-report.md>)|I10 隔离 dry-run 报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/audit.md](<../workflows/i10-migration-dry-run/audit.md>)|I10 只读现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/design.md](<../workflows/i10-migration-dry-run/design.md>)|I10 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/diff-report.md](<../workflows/i10-migration-dry-run/diff-report.md>)|I10 差异报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/next-requirements.md](<../workflows/i10-migration-dry-run/next-requirements.md>)|I10 下一步|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/owner-coverage.md](<../workflows/i10-migration-dry-run/owner-coverage.md>)|I10 Owner Coverage and Conflict Queue|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/owner-decision-proposal.md](<../workflows/i10-migration-dry-run/owner-decision-proposal.md>)|I10 Owner / Backfill Decision Proposal|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/requirements.md](<../workflows/i10-migration-dry-run/requirements.md>)|I10 需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/risk-register.md](<../workflows/i10-migration-dry-run/risk-register.md>)|I10 风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i10-migration-dry-run/tasks.md](<../workflows/i10-migration-dry-run/tasks.md>)|I10 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/0|
|[docs/workflows/i10-migration-dry-run/validation.md](<../workflows/i10-migration-dry-run/validation.md>)|I10 验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/README.md](<../workflows/i11-shadow-migration/README.md>)|I11 影子迁移与切换|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/audit.md](<../workflows/i11-shadow-migration/audit.md>)|I11 现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/design.md](<../workflows/i11-shadow-migration/design.md>)|I11 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/diff-report.md](<../workflows/i11-shadow-migration/diff-report.md>)|I11 差异报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/next-requirements.md](<../workflows/i11-shadow-migration/next-requirements.md>)|I11 下一步|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/requirements.md](<../workflows/i11-shadow-migration/requirements.md>)|I11 需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/risk-register.md](<../workflows/i11-shadow-migration/risk-register.md>)|I11 风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i11-shadow-migration/tasks.md](<../workflows/i11-shadow-migration/tasks.md>)|I11 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|18/0|
|[docs/workflows/i11-shadow-migration/validation.md](<../workflows/i11-shadow-migration/validation.md>)|I11 验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/README.md](<../workflows/i12-final-closure/README.md>)|I12 最终收口|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/audit.md](<../workflows/i12-final-closure/audit.md>)|I12 现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/design.md](<../workflows/i12-final-closure/design.md>)|I12 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/diff-report.md](<../workflows/i12-final-closure/diff-report.md>)|I12 差异报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/next-requirements.md](<../workflows/i12-final-closure/next-requirements.md>)|I12 下一步|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/requirements.md](<../workflows/i12-final-closure/requirements.md>)|I12 需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/risk-register.md](<../workflows/i12-final-closure/risk-register.md>)|I12 风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i12-final-closure/tasks.md](<../workflows/i12-final-closure/tasks.md>)|I12 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|4/0|
|[docs/workflows/i12-final-closure/validation.md](<../workflows/i12-final-closure/validation.md>)|I12 验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-final-fix/README.md](<../workflows/i4-i5-closure-final-fix/README.md>)|I4-I5 closure-final-fix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-final-fix/audit.md](<../workflows/i4-i5-closure-final-fix/audit.md>)|现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-final-fix/design.md](<../workflows/i4-i5-closure-final-fix/design.md>)|设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-final-fix/requirements.md](<../workflows/i4-i5-closure-final-fix/requirements.md>)|需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-final-fix/tasks.md](<../workflows/i4-i5-closure-final-fix/tasks.md>)|任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|7/0|
|[docs/workflows/i4-i5-closure-final-fix/validation.md](<../workflows/i4-i5-closure-final-fix/validation.md>)|验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-fix-2/README.md](<../workflows/i4-i5-closure-fix-2/README.md>)|I4-I5 closure-fix-2|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-fix-2/audit.md](<../workflows/i4-i5-closure-fix-2/audit.md>)|现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-fix-2/design.md](<../workflows/i4-i5-closure-fix-2/design.md>)|设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-fix-2/requirements.md](<../workflows/i4-i5-closure-fix-2/requirements.md>)|需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i4-i5-closure-fix-2/tasks.md](<../workflows/i4-i5-closure-fix-2/tasks.md>)|任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|8/0|
|[docs/workflows/i4-i5-closure-fix-2/validation.md](<../workflows/i4-i5-closure-fix-2/validation.md>)|验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i6-capture-draft-chain/README.md](<../workflows/i6-capture-draft-chain/README.md>)|I6 采集到草稿深化链路|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i6-capture-draft-chain/audit.md](<../workflows/i6-capture-draft-chain/audit.md>)|I6 现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i6-capture-draft-chain/design.md](<../workflows/i6-capture-draft-chain/design.md>)|I6 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i6-capture-draft-chain/next-requirements.md](<../workflows/i6-capture-draft-chain/next-requirements.md>)|I6 下一轮需求入口|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i6-capture-draft-chain/requirements.md](<../workflows/i6-capture-draft-chain/requirements.md>)|I6 需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i6-capture-draft-chain/risk-register.md](<../workflows/i6-capture-draft-chain/risk-register.md>)|I6 剩余风险清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i6-capture-draft-chain/tasks.md](<../workflows/i6-capture-draft-chain/tasks.md>)|I6 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|8/0|
|[docs/workflows/i6-capture-draft-chain/validation.md](<../workflows/i6-capture-draft-chain/validation.md>)|I6 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/README.md](<../workflows/i7-file-workspace/README.md>)|I7 文件工作区首个切片|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/audit.md](<../workflows/i7-file-workspace/audit.md>)|I7 独立审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/design.md](<../workflows/i7-file-workspace/design.md>)|I7 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/diff-report.md](<../workflows/i7-file-workspace/diff-report.md>)|I7 变更报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/next-requirements.md](<../workflows/i7-file-workspace/next-requirements.md>)|I7 下一步|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/requirements.md](<../workflows/i7-file-workspace/requirements.md>)|I7 需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/risk-register.md](<../workflows/i7-file-workspace/risk-register.md>)|I7 风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i7-file-workspace/tasks.md](<../workflows/i7-file-workspace/tasks.md>)|I7 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|5/0|
|[docs/workflows/i7-file-workspace/validation.md](<../workflows/i7-file-workspace/validation.md>)|I7 验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/README.md](<../workflows/i8-markdown-search/README.md>)|I8 Markdown 与权限搜索|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/audit.md](<../workflows/i8-markdown-search/audit.md>)|I8 独立审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/design.md](<../workflows/i8-markdown-search/design.md>)|I8 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/diff-report.md](<../workflows/i8-markdown-search/diff-report.md>)|I8 变更报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/next-requirements.md](<../workflows/i8-markdown-search/next-requirements.md>)|I8 下一步|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/requirements.md](<../workflows/i8-markdown-search/requirements.md>)|I8 需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/risk-register.md](<../workflows/i8-markdown-search/risk-register.md>)|I8 风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i8-markdown-search/tasks.md](<../workflows/i8-markdown-search/tasks.md>)|I8 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|5/0|
|[docs/workflows/i8-markdown-search/validation.md](<../workflows/i8-markdown-search/validation.md>)|I8 验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/README.md](<../workflows/i9-governance-analytics/README.md>)|I9 治理与统计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/audit.md](<../workflows/i9-governance-analytics/audit.md>)|I9 现状审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/design.md](<../workflows/i9-governance-analytics/design.md>)|I9 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/diff-report.md](<../workflows/i9-governance-analytics/diff-report.md>)|I9 差异报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/next-requirements.md](<../workflows/i9-governance-analytics/next-requirements.md>)|I9 下一步|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/requirements.md](<../workflows/i9-governance-analytics/requirements.md>)|I9 需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/risk-register.md](<../workflows/i9-governance-analytics/risk-register.md>)|I9 风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/i9-governance-analytics/tasks.md](<../workflows/i9-governance-analytics/tasks.md>)|I9 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|4/0|
|[docs/workflows/i9-governance-analytics/validation.md](<../workflows/i9-governance-analytics/validation.md>)|I9 验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/legacy-system-retirement/README.md](<../workflows/legacy-system-retirement/README.md>)|Legacy System Retirement|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/legacy-system-retirement/design.md](<../workflows/legacy-system-retirement/design.md>)|LSR-02 数据迁移合同与可逆规则（含 LSR-00/01 历史设计）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/legacy-system-retirement/requirements.md](<../workflows/legacy-system-retirement/requirements.md>)|LSR 需求与验收合同|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/legacy-system-retirement/tasks.md](<../workflows/legacy-system-retirement/tasks.md>)|LSR 串行任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|3/20|
|[docs/workflows/legacy-system-retirement/validation.md](<../workflows/legacy-system-retirement/validation.md>)|LSR 验证与证据账本|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/local-single-music-source/README.md](<../workflows/local-single-music-source/README.md>)|Local Single Music Source|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/local-single-music-source/design.md](<../workflows/local-single-music-source/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/local-single-music-source/handoff-prompt.md](<../workflows/local-single-music-source/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/local-single-music-source/requirements.md](<../workflows/local-single-music-source/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/local-single-music-source/tasks.md](<../workflows/local-single-music-source/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|13/0|
|[docs/workflows/local-single-music-source/validation.md](<../workflows/local-single-music-source/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-auth-hardening/README.md](<../workflows/manage-auth-hardening/README.md>)|Manage Auth Hardening|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-auth-hardening/audit.md](<../workflows/manage-auth-hardening/audit.md>)|Planning Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-auth-hardening/design.md](<../workflows/manage-auth-hardening/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-auth-hardening/handoff-prompt.md](<../workflows/manage-auth-hardening/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-auth-hardening/requirements.md](<../workflows/manage-auth-hardening/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-auth-hardening/tasks.md](<../workflows/manage-auth-hardening/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|26/0|
|[docs/workflows/manage-auth-hardening/validation.md](<../workflows/manage-auth-hardening/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-ui-consolidation/README.md](<../workflows/manage-ui-consolidation/README.md>)|Manage UI Consolidation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-ui-consolidation/design.md](<../workflows/manage-ui-consolidation/design.md>)|Manage UI Consolidation Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-ui-consolidation/handoff.md](<../workflows/manage-ui-consolidation/handoff.md>)|Manage UI Consolidation Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|9/0|
|[docs/workflows/manage-ui-consolidation/requirements.md](<../workflows/manage-ui-consolidation/requirements.md>)|Manage UI Consolidation Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-ui-consolidation/tasks.md](<../workflows/manage-ui-consolidation/tasks.md>)|Manage UI Consolidation Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/manage-ui-consolidation/validation.md](<../workflows/manage-ui-consolidation/validation.md>)|Manage UI Consolidation Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-rendering-security-poc/README.md](<../workflows/markdown-rendering-security-poc/README.md>)|Markdown Rendering Security PoC|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-rendering-security-poc/audit.md](<../workflows/markdown-rendering-security-poc/audit.md>)|Current Renderer Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-rendering-security-poc/design.md](<../workflows/markdown-rendering-security-poc/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-rendering-security-poc/handoff-prompt.md](<../workflows/markdown-rendering-security-poc/handoff-prompt.md>)|Codex Goal Prompt：受控扩展完成 M6|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-rendering-security-poc/requirements.md](<../workflows/markdown-rendering-security-poc/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-rendering-security-poc/tasks.md](<../workflows/markdown-rendering-security-poc/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|32/1|
|[docs/workflows/markdown-rendering-security-poc/validation.md](<../workflows/markdown-rendering-security-poc/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/README.md](<../workflows/markdown-special-adapter-enablement/README.md>)|Markdown 特殊适配器安全启用|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/assets/chart-01-first-failure.md](<../workflows/markdown-special-adapter-enablement/assets/chart-01-first-failure.md>)|Chart-01 first failing evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/assets/markmap-01-first-failure.md](<../workflows/markdown-special-adapter-enablement/assets/markmap-01-first-failure.md>)|Markmap-01 first failing evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/assets/mermaid-01-first-failure.md](<../workflows/markdown-special-adapter-enablement/assets/mermaid-01-first-failure.md>)|Mermaid-01 first structural failure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/assets/mermaid-02-first-failure.md](<../workflows/markdown-special-adapter-enablement/assets/mermaid-02-first-failure.md>)|Mermaid-02 first browser failure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/audit.md](<../workflows/markdown-special-adapter-enablement/audit.md>)|审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/design.md](<../workflows/markdown-special-adapter-enablement/design.md>)|设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/handoff-prompt.md](<../workflows/markdown-special-adapter-enablement/handoff-prompt.md>)|交接 Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/requirements.md](<../workflows/markdown-special-adapter-enablement/requirements.md>)|需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/markdown-special-adapter-enablement/tasks.md](<../workflows/markdown-special-adapter-enablement/tasks.md>)|任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|15/2|
|[docs/workflows/markdown-special-adapter-enablement/validation.md](<../workflows/markdown-special-adapter-enablement/validation.md>)|验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-ai-image-personalization-fix/README.md](<../workflows/mistake-ai-image-personalization-fix/README.md>)|AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-ai-image-personalization-fix/audit.md](<../workflows/mistake-ai-image-personalization-fix/audit.md>)|Audit: AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-ai-image-personalization-fix/design.md](<../workflows/mistake-ai-image-personalization-fix/design.md>)|Design: AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-ai-image-personalization-fix/diff-report.md](<../workflows/mistake-ai-image-personalization-fix/diff-report.md>)|Diff Report: AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-ai-image-personalization-fix/handoff-prompt.md](<../workflows/mistake-ai-image-personalization-fix/handoff-prompt.md>)|Handoff Prompt: AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-ai-image-personalization-fix/requirements.md](<../workflows/mistake-ai-image-personalization-fix/requirements.md>)|Requirements: AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-ai-image-personalization-fix/tasks.md](<../workflows/mistake-ai-image-personalization-fix/tasks.md>)|Tasks: AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|34/0|
|[docs/workflows/mistake-ai-image-personalization-fix/validation.md](<../workflows/mistake-ai-image-personalization-fix/validation.md>)|Validation: AI Mistake And Prompt Management Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-editor-simplification/README.md](<../workflows/mistake-editor-simplification/README.md>)|Mistake Editor Simplification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-editor-simplification/design.md](<../workflows/mistake-editor-simplification/design.md>)|Design: Mistake Editor Simplification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-editor-simplification/requirements.md](<../workflows/mistake-editor-simplification/requirements.md>)|Requirements: Mistake Editor Simplification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-editor-simplification/tasks.md](<../workflows/mistake-editor-simplification/tasks.md>)|Tasks: Mistake Editor Simplification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/17|
|[docs/workflows/mistake-editor-simplification/validation.md](<../workflows/mistake-editor-simplification/validation.md>)|Validation: Mistake Editor Simplification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-learning-reliability-upgrade/README.md](<../workflows/mistake-learning-reliability-upgrade/README.md>)|Mistake Learning Reliability Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-learning-reliability-upgrade/audit.md](<../workflows/mistake-learning-reliability-upgrade/audit.md>)|Audit: Mistake Learning Reliability Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-learning-reliability-upgrade/design.md](<../workflows/mistake-learning-reliability-upgrade/design.md>)|Design: Mistake Learning Reliability Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-learning-reliability-upgrade/diff-report.md](<../workflows/mistake-learning-reliability-upgrade/diff-report.md>)|Diff Report: Expected Implementation Scope|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-learning-reliability-upgrade/handoff-prompt.md](<../workflows/mistake-learning-reliability-upgrade/handoff-prompt.md>)|Implementation Agent Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-learning-reliability-upgrade/requirements.md](<../workflows/mistake-learning-reliability-upgrade/requirements.md>)|Requirements: Mistake Learning Reliability Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-learning-reliability-upgrade/tasks.md](<../workflows/mistake-learning-reliability-upgrade/tasks.md>)|Tasks: Mistake Learning Reliability Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|22/0|
|[docs/workflows/mistake-learning-reliability-upgrade/validation.md](<../workflows/mistake-learning-reliability-upgrade/validation.md>)|Validation: Mistake Learning Reliability Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-staged-error-diagram-generation/README.md](<../workflows/mistake-staged-error-diagram-generation/README.md>)|Mistake Staged Error Diagram Generation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-staged-error-diagram-generation/audit.md](<../workflows/mistake-staged-error-diagram-generation/audit.md>)|Front-Back Closure Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-staged-error-diagram-generation/design.md](<../workflows/mistake-staged-error-diagram-generation/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-staged-error-diagram-generation/handoff-prompt.md](<../workflows/mistake-staged-error-diagram-generation/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-staged-error-diagram-generation/requirements.md](<../workflows/mistake-staged-error-diagram-generation/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mistake-staged-error-diagram-generation/tasks.md](<../workflows/mistake-staged-error-diagram-generation/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|40/2|
|[docs/workflows/mistake-staged-error-diagram-generation/validation.md](<../workflows/mistake-staged-error-diagram-generation/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-auto-deploy-script/README.md](<../workflows/music-auto-deploy-script/README.md>)|Music Auto Deploy Script|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-auto-deploy-script/design.md](<../workflows/music-auto-deploy-script/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-auto-deploy-script/handoff-prompt.md](<../workflows/music-auto-deploy-script/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-auto-deploy-script/requirements.md](<../workflows/music-auto-deploy-script/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-auto-deploy-script/tasks.md](<../workflows/music-auto-deploy-script/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|5/0|
|[docs/workflows/music-auto-deploy-script/validation.md](<../workflows/music-auto-deploy-script/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-selection-auto-deploy/README.md](<../workflows/music-selection-auto-deploy/README.md>)|Music Selection Auto Deploy|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-selection-auto-deploy/design.md](<../workflows/music-selection-auto-deploy/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-selection-auto-deploy/handoff-prompt.md](<../workflows/music-selection-auto-deploy/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-selection-auto-deploy/requirements.md](<../workflows/music-selection-auto-deploy/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/music-selection-auto-deploy/tasks.md](<../workflows/music-selection-auto-deploy/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|7/0|
|[docs/workflows/music-selection-auto-deploy/validation.md](<../workflows/music-selection-auto-deploy/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-goal-gap-analysis/README.md](<../workflows/mvp-goal-gap-analysis/README.md>)|MVP Goal Gap Analysis|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-goal-gap-analysis/audit.md](<../workflows/mvp-goal-gap-analysis/audit.md>)|Audit Record|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-goal-gap-analysis/design.md](<../workflows/mvp-goal-gap-analysis/design.md>)|Design: MVP Goal Gap Analysis|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-goal-gap-analysis/requirements.md](<../workflows/mvp-goal-gap-analysis/requirements.md>)|Requirements: MVP Goal Gap Analysis|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-goal-gap-analysis/tasks.md](<../workflows/mvp-goal-gap-analysis/tasks.md>)|Tasks: MVP Goal Gap Analysis|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|6/0|
|[docs/workflows/mvp-goal-gap-analysis/validation.md](<../workflows/mvp-goal-gap-analysis/validation.md>)|Validation: MVP Goal Gap Analysis|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/README.md](<../workflows/mvp-local-trial-acceptance/README.md>)|MVP 本地试运行验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/acceptance-summary.md](<../workflows/mvp-local-trial-acceptance/acceptance-summary.md>)|MVP 第一阶段项目验收摘要|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/checklist.md](<../workflows/mvp-local-trial-acceptance/checklist.md>)|本地试运行 Checklist|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|56/1|
|[docs/workflows/mvp-local-trial-acceptance/demo-record.md](<../workflows/mvp-local-trial-acceptance/demo-record.md>)|P0-15 现场演示记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/demo-script.md](<../workflows/mvp-local-trial-acceptance/demo-script.md>)|MVP 第一阶段演示脚本|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/11|
|[docs/workflows/mvp-local-trial-acceptance/design.md](<../workflows/mvp-local-trial-acceptance/design.md>)|设计文档：MVP 本地试运行验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/issues.md](<../workflows/mvp-local-trial-acceptance/issues.md>)|Issues|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|14/28|
|[docs/workflows/mvp-local-trial-acceptance/next-requirements.md](<../workflows/mvp-local-trial-acceptance/next-requirements.md>)|下一轮需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/requirements.md](<../workflows/mvp-local-trial-acceptance/requirements.md>)|需求文档：MVP 本地试运行验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/risks.md](<../workflows/mvp-local-trial-acceptance/risks.md>)|剩余风险清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/sample-data-plan.md](<../workflows/mvp-local-trial-acceptance/sample-data-plan.md>)|Sample Data Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/tasks.md](<../workflows/mvp-local-trial-acceptance/tasks.md>)|任务清单：MVP 本地试运行验收与演示准备|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|65/1|
|[docs/workflows/mvp-local-trial-acceptance/trial-record.md](<../workflows/mvp-local-trial-acceptance/trial-record.md>)|MVP 本地试运行记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-local-trial-acceptance/validation.md](<../workflows/mvp-local-trial-acceptance/validation.md>)|MVP 本地试运行验收报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-public-deployment/README.md](<../workflows/mvp-public-deployment/README.md>)|MVP Rebuild 公网部署|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-public-deployment/design.md](<../workflows/mvp-public-deployment/design.md>)|设计文档：MVP Rebuild 公网部署|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-public-deployment/next-requirements.md](<../workflows/mvp-public-deployment/next-requirements.md>)|下一轮需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-public-deployment/requirements.md](<../workflows/mvp-public-deployment/requirements.md>)|需求文档：MVP Rebuild 公网部署|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-public-deployment/risks.md](<../workflows/mvp-public-deployment/risks.md>)|剩余风险|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-public-deployment/tasks.md](<../workflows/mvp-public-deployment/tasks.md>)|任务清单：MVP Rebuild 公网部署|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|17/0|
|[docs/workflows/mvp-public-deployment/validation.md](<../workflows/mvp-public-deployment/validation.md>)|MVP Rebuild 公网部署验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-0-docs-freeze/README.md](<../workflows/mvp-rebuild-batch-0-docs-freeze/README.md>)|MVP Rebuild Batch 0：文档冻结与实现约束|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-0-docs-freeze/audit.md](<../workflows/mvp-rebuild-batch-0-docs-freeze/audit.md>)|Batch 0 文档一致性审查|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-0-docs-freeze/design.md](<../workflows/mvp-rebuild-batch-0-docs-freeze/design.md>)|设计文档：Batch 0 文档冻结|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-0-docs-freeze/requirements.md](<../workflows/mvp-rebuild-batch-0-docs-freeze/requirements.md>)|需求文档：Batch 0 文档冻结|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-0-docs-freeze/tasks.md](<../workflows/mvp-rebuild-batch-0-docs-freeze/tasks.md>)|任务清单：Batch 0 文档冻结与实现约束|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|9/0|
|[docs/workflows/mvp-rebuild-batch-0-docs-freeze/validation.md](<../workflows/mvp-rebuild-batch-0-docs-freeze/validation.md>)|Batch 0 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-1-ui-shell/README.md](<../workflows/mvp-rebuild-batch-1-ui-shell/README.md>)|MVP Rebuild Batch 1：UI 壳层与首页轻量改造|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-1-ui-shell/audit.md](<../workflows/mvp-rebuild-batch-1-ui-shell/audit.md>)|Batch 1 实现审查|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-1-ui-shell/design.md](<../workflows/mvp-rebuild-batch-1-ui-shell/design.md>)|设计文档：Batch 1 UI 壳层|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-1-ui-shell/requirements.md](<../workflows/mvp-rebuild-batch-1-ui-shell/requirements.md>)|需求文档：Batch 1 UI 壳层|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-1-ui-shell/tasks.md](<../workflows/mvp-rebuild-batch-1-ui-shell/tasks.md>)|任务清单：Batch 1 UI 壳层与首页轻量改造|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|9/0|
|[docs/workflows/mvp-rebuild-batch-1-ui-shell/validation.md](<../workflows/mvp-rebuild-batch-1-ui-shell/validation.md>)|Batch 1 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/README.md](<../workflows/mvp-rebuild-batch-2-subject-taxonomy/README.md>)|MVP Rebuild Batch 2：科目 / 知识点基础|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/audit.md](<../workflows/mvp-rebuild-batch-2-subject-taxonomy/audit.md>)|Batch 2 审查记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/design.md](<../workflows/mvp-rebuild-batch-2-subject-taxonomy/design.md>)|设计文档：Batch 2 科目 / 知识点基础|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/requirements.md](<../workflows/mvp-rebuild-batch-2-subject-taxonomy/requirements.md>)|需求文档：Batch 2 科目 / 知识点基础|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/tasks.md](<../workflows/mvp-rebuild-batch-2-subject-taxonomy/tasks.md>)|任务清单：Batch 2 科目 / 知识点基础|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|13/0|
|[docs/workflows/mvp-rebuild-batch-2-subject-taxonomy/validation.md](<../workflows/mvp-rebuild-batch-2-subject-taxonomy/validation.md>)|Batch 2 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/README.md](<../workflows/mvp-rebuild-batch-3-drafts-question-bank/README.md>)|MVP Rebuild Batch 3：题目草稿 / 审核 / 题库|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/audit.md](<../workflows/mvp-rebuild-batch-3-drafts-question-bank/audit.md>)|Batch 3 审查与剩余风险|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/design.md](<../workflows/mvp-rebuild-batch-3-drafts-question-bank/design.md>)|设计文档：Batch 3 题目草稿 / 审核 / 题库|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/requirements.md](<../workflows/mvp-rebuild-batch-3-drafts-question-bank/requirements.md>)|需求文档：Batch 3 题目草稿 / 审核 / 题库|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/tasks.md](<../workflows/mvp-rebuild-batch-3-drafts-question-bank/tasks.md>)|任务清单：Batch 3 题目草稿 / 审核 / 题库|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|13/0|
|[docs/workflows/mvp-rebuild-batch-3-drafts-question-bank/validation.md](<../workflows/mvp-rebuild-batch-3-drafts-question-bank/validation.md>)|Batch 3 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-4-mistakes-review/README.md](<../workflows/mvp-rebuild-batch-4-mistakes-review/README.md>)|MVP Rebuild Batch 4：错题草稿 / 错题 / 简单复习|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-4-mistakes-review/audit.md](<../workflows/mvp-rebuild-batch-4-mistakes-review/audit.md>)|Batch 4 审查记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-4-mistakes-review/design.md](<../workflows/mvp-rebuild-batch-4-mistakes-review/design.md>)|设计文档：Batch 4 错题与简单复习|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-4-mistakes-review/requirements.md](<../workflows/mvp-rebuild-batch-4-mistakes-review/requirements.md>)|需求文档：Batch 4 错题与简单复习|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-4-mistakes-review/tasks.md](<../workflows/mvp-rebuild-batch-4-mistakes-review/tasks.md>)|任务清单：Batch 4 错题与简单复习|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|11/0|
|[docs/workflows/mvp-rebuild-batch-4-mistakes-review/validation.md](<../workflows/mvp-rebuild-batch-4-mistakes-review/validation.md>)|Batch 4 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-5-attachments/README.md](<../workflows/mvp-rebuild-batch-5-attachments/README.md>)|MVP Rebuild Batch 5：附件基础系统|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-5-attachments/audit.md](<../workflows/mvp-rebuild-batch-5-attachments/audit.md>)|Batch 5 审查记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-5-attachments/design.md](<../workflows/mvp-rebuild-batch-5-attachments/design.md>)|设计文档：Batch 5 附件基础系统|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-5-attachments/requirements.md](<../workflows/mvp-rebuild-batch-5-attachments/requirements.md>)|需求文档：Batch 5 附件基础系统|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-5-attachments/tasks.md](<../workflows/mvp-rebuild-batch-5-attachments/tasks.md>)|任务清单：Batch 5 附件基础系统|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|11/0|
|[docs/workflows/mvp-rebuild-batch-5-attachments/validation.md](<../workflows/mvp-rebuild-batch-5-attachments/validation.md>)|Batch 5 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/README.md](<../workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/README.md>)|MVP Rebuild Batch 6：AI / OCR 占位与依赖隔离|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/audit.md](<../workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/audit.md>)|Batch 6 审查记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/design.md](<../workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/design.md>)|设计文档：Batch 6 AI / OCR 占位与依赖隔离|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/requirements.md](<../workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/requirements.md>)|需求文档：Batch 6 AI / OCR 占位与依赖隔离|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/tasks.md](<../workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/tasks.md>)|任务清单：Batch 6 AI / OCR 占位与依赖隔离|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|11/0|
|[docs/workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/validation.md](<../workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/validation.md>)|Batch 6 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/README.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/README.md>)|MVP Rebuild Batch 7：体验收口、旧路由兼容、数据质量|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/audit.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/audit.md>)|Batch 7 审查记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/data-quality-report.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/data-quality-report.md>)|Batch 7 数据质量只读报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/design.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/design.md>)|设计文档：Batch 7 体验收口、旧路由兼容、数据质量|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/local-runbook.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/local-runbook.md>)|Batch 7 本地试运行说明|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/requirements.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/requirements.md>)|需求文档：Batch 7 体验收口、旧路由兼容、数据质量|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/tasks.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/tasks.md>)|任务清单：Batch 7 体验收口、旧路由兼容、数据质量|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/0|
|[docs/workflows/mvp-rebuild-batch-7-polish-compatibility/validation.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/validation.md>)|Batch 7 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-spec-planning/README.md](<../workflows/mvp-rebuild-spec-planning/README.md>)|MVP 重构 Spec 规划工作区|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-spec-planning/design.md](<../workflows/mvp-rebuild-spec-planning/design.md>)|设计文档：MVP 重构 Spec 任务夹|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-spec-planning/requirements.md](<../workflows/mvp-rebuild-spec-planning/requirements.md>)|需求文档：MVP 重构 Spec 任务夹|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/mvp-rebuild-spec-planning/tasks.md](<../workflows/mvp-rebuild-spec-planning/tasks.md>)|任务清单：创建 8 批 MVP 重构 Spec|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/0|
|[docs/workflows/mvp-rebuild-spec-planning/validation.md](<../workflows/mvp-rebuild-spec-planning/validation.md>)|验证记录：MVP 重构 Spec 任务夹|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/note-edit-409-conflict/README.md](<../workflows/note-edit-409-conflict/README.md>)|Note Edit 409 Conflict|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/note-edit-409-conflict/design.md](<../workflows/note-edit-409-conflict/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/note-edit-409-conflict/handoff-prompt.md](<../workflows/note-edit-409-conflict/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/note-edit-409-conflict/requirements.md](<../workflows/note-edit-409-conflict/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/note-edit-409-conflict/tasks.md](<../workflows/note-edit-409-conflict/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/4|
|[docs/workflows/note-edit-409-conflict/validation.md](<../workflows/note-edit-409-conflict/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/notes-workspace-ux-upgrade/README.md](<../workflows/notes-workspace-ux-upgrade/README.md>)|Notes Workspace UX Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/notes-workspace-ux-upgrade/audit.md](<../workflows/notes-workspace-ux-upgrade/audit.md>)|Documentation Completeness Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/notes-workspace-ux-upgrade/design.md](<../workflows/notes-workspace-ux-upgrade/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/notes-workspace-ux-upgrade/diff-report.md](<../workflows/notes-workspace-ux-upgrade/diff-report.md>)|Diff Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/notes-workspace-ux-upgrade/handoff-prompt.md](<../workflows/notes-workspace-ux-upgrade/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/notes-workspace-ux-upgrade/requirements.md](<../workflows/notes-workspace-ux-upgrade/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/notes-workspace-ux-upgrade/tasks.md](<../workflows/notes-workspace-ux-upgrade/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|33/2|
|[docs/workflows/notes-workspace-ux-upgrade/validation.md](<../workflows/notes-workspace-ux-upgrade/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/open-source-closure/README.md](<../workflows/open-source-closure/README.md>)|Open Source Closure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/open-source-closure/audit.md](<../workflows/open-source-closure/audit.md>)|Open-Source Structure Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/open-source-closure/design.md](<../workflows/open-source-closure/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/open-source-closure/requirements.md](<../workflows/open-source-closure/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/open-source-closure/tasks.md](<../workflows/open-source-closure/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|32/0|
|[docs/workflows/open-source-closure/validation.md](<../workflows/open-source-closure/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/README.md](<../workflows/p0-auth-manage-access-closure/README.md>)|P0-AUTH 管理权限回退收口修复|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/acceptance.md](<../workflows/p0-auth-manage-access-closure/acceptance.md>)|P0-AUTH 验收报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/audit.md](<../workflows/p0-auth-manage-access-closure/audit.md>)|P0-AUTH 审计记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/design.md](<../workflows/p0-auth-manage-access-closure/design.md>)|P0-AUTH 设计文档|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/diff-report.md](<../workflows/p0-auth-manage-access-closure/diff-report.md>)|P0-AUTH Diff 报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/handoff-prompt.md](<../workflows/p0-auth-manage-access-closure/handoff-prompt.md>)|P0-AUTH 交接提示|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/next-requirements.md](<../workflows/p0-auth-manage-access-closure/next-requirements.md>)|P0-AUTH 下一轮需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/requirements.md](<../workflows/p0-auth-manage-access-closure/requirements.md>)|P0-AUTH 需求文档|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/risks.md](<../workflows/p0-auth-manage-access-closure/risks.md>)|P0-AUTH 剩余风险|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-auth-manage-access-closure/tasks.md](<../workflows/p0-auth-manage-access-closure/tasks.md>)|P0-AUTH 任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|9/0|
|[docs/workflows/p0-auth-manage-access-closure/validation.md](<../workflows/p0-auth-manage-access-closure/validation.md>)|P0-AUTH 验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-closure-precheck/README.md](<../workflows/p0-closure-precheck/README.md>)|P0 Closure Precheck|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-closure-precheck/audit.md](<../workflows/p0-closure-precheck/audit.md>)|P0 Precheck Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-closure-precheck/design.md](<../workflows/p0-closure-precheck/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-closure-precheck/requirements.md](<../workflows/p0-closure-precheck/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p0-closure-precheck/tasks.md](<../workflows/p0-closure-precheck/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|5/0|
|[docs/workflows/p0-closure-precheck/validation.md](<../workflows/p0-closure-precheck/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p1-acceptance-cleanup-patch/README.md](<../workflows/p1-acceptance-cleanup-patch/README.md>)|P1 Acceptance Cleanup Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p1-acceptance-cleanup-patch/design.md](<../workflows/p1-acceptance-cleanup-patch/design.md>)|Design — P1 Acceptance Cleanup Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p1-acceptance-cleanup-patch/diff-report.md](<../workflows/p1-acceptance-cleanup-patch/diff-report.md>)|Diff Report — P1 Acceptance Cleanup Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p1-acceptance-cleanup-patch/handoff-prompt.md](<../workflows/p1-acceptance-cleanup-patch/handoff-prompt.md>)|Handoff Prompt — P1 Acceptance Cleanup Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p1-acceptance-cleanup-patch/requirements.md](<../workflows/p1-acceptance-cleanup-patch/requirements.md>)|Requirements — P1 Acceptance Cleanup Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p1-acceptance-cleanup-patch/tasks.md](<../workflows/p1-acceptance-cleanup-patch/tasks.md>)|Tasks — P1 Acceptance Cleanup Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|21/0|
|[docs/workflows/p1-acceptance-cleanup-patch/validation.md](<../workflows/p1-acceptance-cleanup-patch/validation.md>)|Validation — P1 Acceptance Cleanup Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p2-test-performance-tuning/README.md](<../workflows/p2-test-performance-tuning/README.md>)|P2 Test Quality And Performance Tuning|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p2-test-performance-tuning/design.md](<../workflows/p2-test-performance-tuning/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p2-test-performance-tuning/diff-report.md](<../workflows/p2-test-performance-tuning/diff-report.md>)|Diff Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p2-test-performance-tuning/requirements.md](<../workflows/p2-test-performance-tuning/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/p2-test-performance-tuning/tasks.md](<../workflows/p2-test-performance-tuning/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|5/0|
|[docs/workflows/p2-test-performance-tuning/validation.md](<../workflows/p2-test-performance-tuning/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/README.md](<../workflows/page-render-timing-validation/README.md>)|页面渲染时效验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/acceptance.md](<../workflows/page-render-timing-validation/acceptance.md>)|页面渲染时效验证验收报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/audit.md](<../workflows/page-render-timing-validation/audit.md>)|预执行审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/design.md](<../workflows/page-render-timing-validation/design.md>)|页面渲染时效验证设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/next-requirements.md](<../workflows/page-render-timing-validation/next-requirements.md>)|下一轮需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/requirements.md](<../workflows/page-render-timing-validation/requirements.md>)|页面渲染时效验证要求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/risks.md](<../workflows/page-render-timing-validation/risks.md>)|残余风险|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/page-render-timing-validation/tasks.md](<../workflows/page-render-timing-validation/tasks.md>)|页面渲染时效验证任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|6/0|
|[docs/workflows/page-render-timing-validation/validation.md](<../workflows/page-render-timing-validation/validation.md>)|页面渲染时效验证记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/README.md](<../workflows/personal-learning-system-convergence/README.md>)|Personal Learning System — 受控收敛工程 Spec（30 天）|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[docs/workflows/personal-learning-system-convergence/design.md](<../workflows/personal-learning-system-convergence/design.md>)|Design — 个人学习系统受控收敛工程|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/phase-0-evidence.md](<../workflows/personal-learning-system-convergence/phase-0-evidence.md>)|Phase 0 — 工程 Gate 实测证据（T-00 / T-00b）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/requirements.md](<../workflows/personal-learning-system-convergence/requirements.md>)|Requirements — 个人学习系统受控收敛工程|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/tasks.md](<../workflows/personal-learning-system-convergence/tasks.md>)|Tasks — PR 切分与串行执行计划|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[docs/workflows/personal-learning-system-convergence/ui-design.md](<../workflows/personal-learning-system-convergence/ui-design.md>)|Personal Learning System Convergence UI 设计规范|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/validation.md](<../workflows/personal-learning-system-convergence/validation.md>)|Validation — 验证策略与验收矩阵|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week1/README.md](<../workflows/personal-learning-system-convergence/week1/README.md>)|Week 1 — TRUSTED RUNTIME（M1）执行记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week1/evidence/README.md](<../workflows/personal-learning-system-convergence/week1/evidence/README.md>)|Week 1 证据索引|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week1/pr-01.md](<../workflows/personal-learning-system-convergence/week1/pr-01.md>)|PR-01 — Runtime Smoke（R31 / D12）设计与证据|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week1/pr-02.md](<../workflows/personal-learning-system-convergence/week1/pr-02.md>)|PR-02 — Authoring 路由收敛（R03 / D10）设计与证据|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week1/pr-03.md](<../workflows/personal-learning-system-convergence/week1/pr-03.md>)|PR-03 — AsyncStatePanel 与主要异步面板证据|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week1/pr-04.md](<../workflows/personal-learning-system-convergence/week1/pr-04.md>)|PR-04 — Guestbook migration 027 与 G2 证据|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week1/week1-technical-report.md](<../workflows/personal-learning-system-convergence/week1/week1-technical-report.md>)|Week 1 技术报告：TRUSTED RUNTIME|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week2/README.md](<../workflows/personal-learning-system-convergence/week2/README.md>)|Week 2 — CLOSED REVIEW LOOP|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week2/evidence/reviews/pr05-independent-review-20260913.md](<../workflows/personal-learning-system-convergence/week2/evidence/reviews/pr05-independent-review-20260913.md>)|PR-05 独立技术评审报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week2/pr-05.md](<../workflows/personal-learning-system-convergence/week2/pr-05.md>)|PR-05|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week2/pr-06.md](<../workflows/personal-learning-system-convergence/week2/pr-06.md>)|PR-06|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week2/pr-07.md](<../workflows/personal-learning-system-convergence/week2/pr-07.md>)|PR-07|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week2/pr-08.md](<../workflows/personal-learning-system-convergence/week2/pr-08.md>)|PR-08|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/README.md](<../workflows/personal-learning-system-convergence/week3/README.md>)|Week 3 — CANONICAL LEARNING execution plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/TRACKING.md](<../workflows/personal-learning-system-convergence/week3/TRACKING.md>)|Week 3 跟踪文件 — CANONICAL LEARNING|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/browser/pr-09-api-scenarios.md](<../workflows/personal-learning-system-convergence/week3/evidence/browser/pr-09-api-scenarios.md>)|PR-09-C real-browser scenarios (agent-browser / Chromium)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/inc-01-blog-v2-assessment.md](<../workflows/personal-learning-system-convergence/week3/evidence/inc-01-blog-v2-assessment.md>)|INC-01 — `blog_v2` at revision 032 (read-only assessment)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/inc-02-root-cause.md](<../workflows/personal-learning-system-convergence/week3/evidence/inc-02-root-cause.md>)|INC-02 — `blog_v2.notes` Week 3 夹具数据泄漏（read-only root cause）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/migrations/README-stale.md](<../workflows/personal-learning-system-convergence/week3/evidence/migrations/README-stale.md>)|Stale migration evidence (PR-09 R1-R4 rework)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/pr-10-rework-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/pr-10-rework-self-evidence.md>)|PR-10 rework — PFV-01 (MEDIUM) + PFV-02 (LOW)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/pr-10-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/pr-10-self-evidence.md>)|PR-10 — Canonical KP analytics — self evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/pr-10-verify-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/pr-10-verify-summary.md>)|PR-10 independent verification — summary|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/pr-12-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/pr-12-self-evidence.md>)|PR-12 — Canonical Note ↔ KnowledgePoint relation — self evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/pr-12-verify-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/pr-12-verify-summary.md>)|PR-12 verification summary — PR-12-verify (independent)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/pr-13-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/pr-13-self-evidence.md>)|PR-13 self-evidence — daily practice|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-09-api-findings.md](<../workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-09-api-findings.md>)|PR-09-verify-api findings (HTTP contract / permissions / freeze / source / browser)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-09-db-findings.md](<../workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-09-db-findings.md>)|PR-09 DB/Migration/Ledger Independent Verification Findings|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-10-findings.md](<../workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-10-findings.md>)|PR-10 independent verification — findings|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-12-findings.md](<../workflows/personal-learning-system-convergence/week3/evidence/reviews/pr-12-findings.md>)|PR-12 findings — independent verification (PR-12-verify)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/browser/pr-11-verify-browser-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/browser/pr-11-verify-browser-summary.md>)|PR-11-verify B: Real-Chromium verification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/browser/gate-browser-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/browser/gate-browser-summary.md>)|Week 3 Gate — real Chromium walkthrough evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/gate-findings.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/gate-findings.md>)|Week 3 Gate — findings|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/gate-matrix.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/gate-matrix.md>)|Week 3 Gate matrix — evidence record|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/migrations/gate-migration-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/migrations/gate-migration-summary.md>)|Week 3 Gate — migration replay evidence (030→032)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/tests/gate-backend-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/tests/gate-backend-summary.md>)|Week 3 Gate — backend test evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/tests/gate-frontend-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/gate/tests/gate-frontend-summary.md>)|Week 3 Gate — frontend test evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/pr-11-frontend-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/pr-11-frontend-self-evidence.md>)|PR-11 frontend self-evidence (Dashboard three-question integration)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/pr-11-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/pr-11-self-evidence.md>)|PR-11 backend self-evidence (dashboard summary delta)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/pr-13-verify-summary.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/pr-13-verify-summary.md>)|PR-13 independent verification summary|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/reviews/pr-11-findings.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/reviews/pr-11-findings.md>)|PR-11 findings (independent verification)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/reviews/pr-13-findings.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/reviews/pr-13-findings.md>)|PR-13 verification findings (agent PR-13-verify, senior-qa-sdet)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/tests/pr-11-verify-test-matrix.md](<../workflows/personal-learning-system-convergence/week3/evidence/root-week3-relocated/tests/pr-11-verify-test-matrix.md>)|PR-11-verify A: component/contract test matrix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/tests/pr-09-rework-2-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/tests/pr-09-rework-2-self-evidence.md>)|pr-09-rework-2-self-evidence.md|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/tests/pr-09-rework-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/tests/pr-09-rework-self-evidence.md>)|pr-09-rework-self-evidence.md|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/tests/pr-09-self-evidence.md](<../workflows/personal-learning-system-convergence/week3/evidence/tests/pr-09-self-evidence.md>)|PR-09 Evidence — canonical public mistakes (backend slice)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/w3-00-contracts-and-guard.md](<../workflows/personal-learning-system-convergence/week3/evidence/w3-00-contracts-and-guard.md>)|W3-00 实现报告 — 合同固化与 scratch 守卫 runner|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/w3-00-inventory-legacy-mistake.md](<../workflows/personal-learning-system-convergence/week3/evidence/w3-00-inventory-legacy-mistake.md>)|W3-00 盘点 A — legacy mistake 写入方 / 读取方全量清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/w3-00-inventory-migration-adapter.md](<../workflows/personal-learning-system-convergence/week3/evidence/w3-00-inventory-migration-adapter.md>)|W3-00 盘点 B — migration-026 适配器机制结论|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/w3-00-inventory-runtime-contracts.md](<../workflows/personal-learning-system-convergence/week3/evidence/w3-00-inventory-runtime-contracts.md>)|W3-00 — Runtime & canonical contract inventory (read-only)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/evidence/w3-00-rework.md](<../workflows/personal-learning-system-convergence/week3/evidence/w3-00-rework.md>)|W3-00 Rework Report (agent: W3-00-rework)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/README.md](<../workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/README.md>)|Week 3 复核及事故防复发（2026-09-26）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/design.md](<../workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/design.md>)|根因与设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/requirements.md](<../workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/requirements.md>)|范围与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/review.md](<../workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/review.md>)|独立评审记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/tasks.md](<../workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/tasks.md>)|串行任务|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/validation.md](<../workflows/personal-learning-system-convergence/week3/incident-followup-2026-09-26/validation.md>)|证据与结果|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/tasks/pr-09.md](<../workflows/personal-learning-system-convergence/week3/tasks/pr-09.md>)|PR-09 — Canonical public mistakes|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/tasks/pr-10.md](<../workflows/personal-learning-system-convergence/week3/tasks/pr-10.md>)|PR-10 — Canonical KP analytics|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/tasks/pr-11.md](<../workflows/personal-learning-system-convergence/week3/tasks/pr-11.md>)|PR-11 — Dashboard integration|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/tasks/pr-12.md](<../workflows/personal-learning-system-convergence/week3/tasks/pr-12.md>)|PR-12 — Canonical Note↔KnowledgePoint relation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/tasks/pr-13.md](<../workflows/personal-learning-system-convergence/week3/tasks/pr-13.md>)|PR-13 — Daily practice|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/tasks/w3-00.md](<../workflows/personal-learning-system-convergence/week3/tasks/w3-00.md>)|W3-00 — Preflight and contract lock|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/tasks/week3-gate.md](<../workflows/personal-learning-system-convergence/week3/tasks/week3-gate.md>)|Week 3 Gate — CANONICAL LEARNING|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week3/week3-technical-report.md](<../workflows/personal-learning-system-convergence/week3/week3-technical-report.md>)|Week 3 技术报告：CANONICAL LEARNING|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/README.md](<../workflows/personal-learning-system-convergence/week4/README.md>)|Week 4 — RELEASE GATE execution plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/TRACKING.md](<../workflows/personal-learning-system-convergence/week4/TRACKING.md>)|Week 4 TRACKING — RELEASE GATE (M4)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/fix-F02-F03-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/fix-F02-F03-review.md>)|Independent Review — Week 4 fixes F02 (CLI cross-event-loop) + F03 (WebAuthn challenge matching)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/fix-F05-F07-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/fix-F05-F07-review.md>)|Independent Review — Week 4 F07 (full-chain error sanitization) + F05 (structured cross-layer OCR er|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/fix-F06-F01-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/fix-F06-F01-review.md>)|Independent Review — Week 4 fixes F06 (bounded throttle state) + F01 (CI DB config vs guards)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/fix-rework-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/fix-rework-review.md>)|Independent Review — Week 4 Rework (F05 draft path, CI deselect debt removal, pr09 idempotency)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/gate/gate-final-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/gate/gate-final-review.md>)|Week 4 Gate — Final Independent Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/gate/reassessment-verification.md](<../workflows/personal-learning-system-convergence/week4/evidence/gate/reassessment-verification.md>)|Week 4 Gate — Independent Recheck of `quality-reassessment.md`|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/gate/week4-gate-matrix.md](<../workflows/personal-learning-system-convergence/week4/evidence/gate/week4-gate-matrix.md>)|Week 4 Gate Matrix — RELEASE GATE (M4)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/gate/week4-gate-summary.md](<../workflows/personal-learning-system-convergence/week4/evidence/gate/week4-gate-summary.md>)|Week 4 Gate Summary — RELEASE GATE (M4)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-14-ocr-baseline-report.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-14-ocr-baseline-report.md>)|PR-14 — OCR Baseline Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-14-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-14-review.md>)|PR-14 — Independent Review / Verification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-15-design-deviation.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-15-design-deviation.md>)|PR-15 design deviation — W4-E08: raw WebAuthn challenge retained|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-15-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-15-review.md>)|PR-15 Independent Review — WebAuthn Challenge Persistence (migration 033)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-16-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-16-review.md>)|PR-16 — Independent Review: Login Throttling|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-17-e2e-business.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-17-e2e-business.md>)|PR-17 / F04 — Restored R22b business E2E (E2E-03, E2E-04)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-17-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-17-review.md>)|PR-17 (W4-D06) — CI four jobs: independent review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-18-cleanup-components.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-18-cleanup-components.md>)|PR-18 Evidence — SAFE_TO_DELETE Legacy Cleanup (3 components + music/list + dead import)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-18-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-18-review.md>)|PR-18 Independent Review — Week 4 Legacy Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-18-summary.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-18-summary.md>)|PR-18 Summary — Week 4 Legacy Cleanup (SAFE_TO_DELETE only)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-19-ai-call-audit.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-19-ai-call-audit.md>)|pr-19-ai-call-audit.md|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/pr-19-review.md](<../workflows/personal-learning-system-convergence/week4/evidence/pr-19-review.md>)|PR-19 Independent Review — AI Governance (Run target linkage)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/reassessment-2026-09-26/backend-SUMMARY.md](<../workflows/personal-learning-system-convergence/week4/evidence/reassessment-2026-09-26/backend-SUMMARY.md>)|Week 4 independent backend verification — 2026-09-26|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/w4-00-cleanup-candidates.md](<../workflows/personal-learning-system-convergence/week4/evidence/w4-00-cleanup-candidates.md>)|W4-00 Evidence — Legacy Cleanup Candidate Classification (PR-18 preflight)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/w4-00-decisions.md](<../workflows/personal-learning-system-convergence/week4/evidence/w4-00-decisions.md>)|W4-00 — Locked Decisions (executable + plan deltas)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/w4-00-ocr-inventory.md](<../workflows/personal-learning-system-convergence/week4/evidence/w4-00-ocr-inventory.md>)|W4-00 — OCR / Capture Recognition Flow Inventory|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/evidence/w4-00-webauthn-inventory.md](<../workflows/personal-learning-system-convergence/week4/evidence/w4-00-webauthn-inventory.md>)|W4-00 WebAuthn / Login Auth Inventory (READ-ONLY evidence)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/quality-reassessment.md](<../workflows/personal-learning-system-convergence/week4/quality-reassessment.md>)|Week 4 代码质量与功能复验|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/pr-14.md](<../workflows/personal-learning-system-convergence/week4/tasks/pr-14.md>)|PR-14 — OCR Diagnostic and UI|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/44|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/pr-15.md](<../workflows/personal-learning-system-convergence/week4/tasks/pr-15.md>)|PR-15 — WebAuthn Challenge Table|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/62|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/pr-16.md](<../workflows/personal-learning-system-convergence/week4/tasks/pr-16.md>)|PR-16 — Login Throttling|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/54|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/pr-17.md](<../workflows/personal-learning-system-convergence/week4/tasks/pr-17.md>)|PR-17 — CI Four Jobs|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/51|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/pr-18.md](<../workflows/personal-learning-system-convergence/week4/tasks/pr-18.md>)|PR-18 — Legacy Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/44|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/pr-19.md](<../workflows/personal-learning-system-convergence/week4/tasks/pr-19.md>)|PR-19 — AI Governance Closure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/43|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/w4-00.md](<../workflows/personal-learning-system-convergence/week4/tasks/w4-00.md>)|W4-00 — Preflight and Scope Lock|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/41|
|[docs/workflows/personal-learning-system-convergence/week4/tasks/week4-gate.md](<../workflows/personal-learning-system-convergence/week4/tasks/week4-gate.md>)|Week 4 Gate — Final Verification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/35|
|[docs/workflows/personal-learning-system-convergence/week4/week4-summary.md](<../workflows/personal-learning-system-convergence/week4/week4-summary.md>)|Week 4 — RELEASE GATE 执行计划摘要|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-convergence/week4/week4-technical-report.md](<../workflows/personal-learning-system-convergence/week4/week4-technical-report.md>)|Week 4 技术报告：RELEASE GATE (M4)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/README.md](<../workflows/personal-learning-system-v2/README.md>)|Personal Learning System V2|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/audit/access-matrix.md](<../workflows/personal-learning-system-v2/audit/access-matrix.md>)|Phase A A-02 路由、API 与权限审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/audit/data-inventory.md](<../workflows/personal-learning-system-v2/audit/data-inventory.md>)|Phase A A-01 数据源与实体盘点|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/audit/migration-gate.md](<../workflows/personal-learning-system-v2/audit/migration-gate.md>)|Phase A A-03 备份、恢复与迁移门槛审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/audit/risk-register.md](<../workflows/personal-learning-system-v2/audit/risk-register.md>)|Phase A 风险登记|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/auth-boundary-design.md](<../workflows/personal-learning-system-v2/auth-boundary-design.md>)|Phase B：Authentication Boundary Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/backup-validation-plan.md](<../workflows/personal-learning-system-v2/backup-validation-plan.md>)|Phase B：Backup Validation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/design.md](<../workflows/personal-learning-system-v2/design.md>)|Personal Learning System V2 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/owner-coverage-matrix.md](<../workflows/personal-learning-system-v2/owner-coverage-matrix.md>)|Phase B：Owner Coverage Matrix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/requirements.md](<../workflows/personal-learning-system-v2/requirements.md>)|Personal Learning System V2 需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/schema-ownership.md](<../workflows/personal-learning-system-v2/schema-ownership.md>)|Phase B：Schema Ownership|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/source-of-truth.md](<../workflows/personal-learning-system-v2/source-of-truth.md>)|Phase B：Source of Truth|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/tasks.md](<../workflows/personal-learning-system-v2/tasks.md>)|Personal Learning System V2 详细任务组|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/ui-design.md](<../workflows/personal-learning-system-v2/ui-design.md>)|Personal Learning System V2 UI 设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2/validation.md](<../workflows/personal-learning-system-v2/validation.md>)|Phase B Design Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/README.md](<../workflows/personal-learning-system-v2-unification/README.md>)|Personal Learning System V2 统一大方案|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/design.md](<../workflows/personal-learning-system-v2-unification/design.md>)|统一大方案设计边界|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i0-freeze-audit.md](<../workflows/personal-learning-system-v2-unification/i0-freeze-audit.md>)|I0 冻结审查与来源索引|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i1-boundary-recovery-audit.md](<../workflows/personal-learning-system-v2-unification/i1-boundary-recovery-audit.md>)|I1 边界与恢复审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i2-learning-loop-validation.md](<../workflows/personal-learning-system-v2-unification/i2-learning-loop-validation.md>)|I2 最小学习闭环浏览器验证|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i3-attempt-capture-findings.md](<../workflows/personal-learning-system-v2-unification/i3-attempt-capture-findings.md>)|I3 现状发现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i3-attempt-capture-plan.md](<../workflows/personal-learning-system-v2-unification/i3-attempt-capture-plan.md>)|I3 计划：Attempt、错题转换与采集手工回退|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i3-attempt-capture-progress.md](<../workflows/personal-learning-system-v2-unification/i3-attempt-capture-progress.md>)|I3 进度|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i4-closure-fix-findings.md](<../workflows/personal-learning-system-v2-unification/i4-closure-fix-findings.md>)|I4 closure-fix 现状发现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i4-closure-fix-plan.md](<../workflows/personal-learning-system-v2-unification/i4-closure-fix-plan.md>)|I4 closure-fix 收口计划|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i4-closure-fix-progress.md](<../workflows/personal-learning-system-v2-unification/i4-closure-fix-progress.md>)|I4 closure-fix 进度|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i4-dashboard-navigation-findings.md](<../workflows/personal-learning-system-v2-unification/i4-dashboard-navigation-findings.md>)|I4 现状发现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i4-dashboard-navigation-plan.md](<../workflows/personal-learning-system-v2-unification/i4-dashboard-navigation-plan.md>)|I4 计划：学习首页状态与统一导航收口|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i4-dashboard-navigation-progress.md](<../workflows/personal-learning-system-v2-unification/i4-dashboard-navigation-progress.md>)|I4 进度|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i5-preparation-design.md](<../workflows/personal-learning-system-v2-unification/i5-preparation-design.md>)|I5 设计：私有资料、首页偏好与响应式验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i5-preparation-findings.md](<../workflows/personal-learning-system-v2-unification/i5-preparation-findings.md>)|I5 准备现状发现|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i5-preparation-plan.md](<../workflows/personal-learning-system-v2-unification/i5-preparation-plan.md>)|I5 准备计划：私有资料、首页偏好与响应式验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i5-preparation-progress.md](<../workflows/personal-learning-system-v2-unification/i5-preparation-progress.md>)|I5 准备进度|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i5-preparation-requirements.md](<../workflows/personal-learning-system-v2-unification/i5-preparation-requirements.md>)|I5 需求与验收基线（已通过）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/i5-preparation-tasks.md](<../workflows/personal-learning-system-v2-unification/i5-preparation-tasks.md>)|I5 准备任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/0|
|[docs/workflows/personal-learning-system-v2-unification/i5-profile-settings-adr.md](<../workflows/personal-learning-system-v2-unification/i5-profile-settings-adr.md>)|ADR-I5-01：公开站点设置与管理员私有资料分离|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/incremental-plan.md](<../workflows/personal-learning-system-v2-unification/incremental-plan.md>)|Personal Learning System V2 递进执行计划|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/master-plan.md](<../workflows/personal-learning-system-v2-unification/master-plan.md>)|Personal Learning System V2 统一大方案|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-acceptance.md](<../workflows/personal-learning-system-v2-unification/r1-acceptance.md>)|R1 验收记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-audit.md](<../workflows/personal-learning-system-v2-unification/r1-audit.md>)|R1 最终审查|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-content-editor-capability-matrix.md](<../workflows/personal-learning-system-v2-unification/r1-content-editor-capability-matrix.md>)|R1 内容创建与编辑能力矩阵|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-diff-report.md](<../workflows/personal-learning-system-v2-unification/r1-diff-report.md>)|R1 Diff 报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-entry-permission-matrix.md](<../workflows/personal-learning-system-v2-unification/r1-entry-permission-matrix.md>)|R1 入口、调用方与权限矩阵|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-next-requirements.md](<../workflows/personal-learning-system-v2-unification/r1-next-requirements.md>)|R1 后续需求建议|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-risks.md](<../workflows/personal-learning-system-v2-unification/r1-risks.md>)|R1 风险与阻断项|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-visual-baseline.md](<../workflows/personal-learning-system-v2-unification/r1-visual-baseline.md>)|R1 管理工作区视觉基线|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-workspace-entry-visual-convergence-design.md](<../workflows/personal-learning-system-v2-unification/r1-workspace-entry-visual-convergence-design.md>)|R1 管理工作区入口与视觉收敛设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-workspace-entry-visual-convergence-requirements.md](<../workflows/personal-learning-system-v2-unification/r1-workspace-entry-visual-convergence-requirements.md>)|R1 管理工作区入口与视觉收敛需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/r1-workspace-entry-visual-convergence-tasks.md](<../workflows/personal-learning-system-v2-unification/r1-workspace-entry-visual-convergence-tasks.md>)|R1 管理工作区入口与视觉收敛任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/0|
|[docs/workflows/personal-learning-system-v2-unification/refactor-plan-audit-2026-07-30.md](<../workflows/personal-learning-system-v2-unification/refactor-plan-audit-2026-07-30.md>)|`docs/refactor-plan` 重新审查报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/requirements.md](<../workflows/personal-learning-system-v2-unification/requirements.md>)|统一大方案需求与验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-system-v2-unification/tasks.md](<../workflows/personal-learning-system-v2-unification/tasks.md>)|统一大方案任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|71/0|
|[docs/workflows/personal-learning-system-v2-unification/validation.md](<../workflows/personal-learning-system-v2-unification/validation.md>)|文档细化校验|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-ui-foundation/README.md](<../workflows/personal-learning-ui-foundation/README.md>)|UI Foundation Track — personal-learning-ui-foundation|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[docs/workflows/personal-learning-ui-foundation/design.md](<../workflows/personal-learning-ui-foundation/design.md>)|Design — UI Foundation Track|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-ui-foundation/requirements.md](<../workflows/personal-learning-ui-foundation/requirements.md>)|Requirements — UI Foundation Track 第一阶段（F0–F5）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-ui-foundation/tasks.md](<../workflows/personal-learning-ui-foundation/tasks.md>)|Tasks — F0–F5（串行，F5 后停止）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|2/15|
|[docs/workflows/personal-learning-ui-foundation/validation.md](<../workflows/personal-learning-ui-foundation/validation.md>)|Validation — UI Foundation Track（F5 填写，状态词仅限 PASS / PARTIAL / FAIL / NOT_APPLICABLE）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-ui-v2/README.md](<../workflows/personal-learning-ui-v2/README.md>)|UI V2 Full Implementation Track — personal-learning-ui-v2|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[docs/workflows/personal-learning-ui-v2/UI_V2_MASTER_TRACKER.md](<../workflows/personal-learning-ui-v2/UI_V2_MASTER_TRACKER.md>)|Personal Learning System — UI V2 Master Tracker|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[docs/workflows/personal-learning-ui-v2/design.md](<../workflows/personal-learning-ui-v2/design.md>)|Design — UI V2 Full Implementation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-ui-v2/requirements.md](<../workflows/personal-learning-ui-v2/requirements.md>)|Requirements — UI V2 Full Implementation（U1–U16）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/personal-learning-ui-v2/tasks.md](<../workflows/personal-learning-ui-v2/tasks.md>)|Tasks — UI V2 Full Implementation（串行为主，独立任务可并行；共享文件单写者）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/36|
|[docs/workflows/personal-learning-ui-v2/validation.md](<../workflows/personal-learning-ui-v2/validation.md>)|Validation — UI V2 Full Implementation（状态词仅限 PASS / PARTIAL / FAIL / NOT_APPLICABLE）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/README.md](<../workflows/phase-1-0-productization/README.md>)|Phase 1.0 Productization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/audit.md](<../workflows/phase-1-0-productization/audit.md>)|Current-State Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/design.md](<../workflows/phase-1-0-productization/design.md>)|Design: Phase 1.0 Productization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/handoff-prompt.md](<../workflows/phase-1-0-productization/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/next-requirements.md](<../workflows/phase-1-0-productization/next-requirements.md>)|Next Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/phase-0-5-runtime-recovery-gate.md](<../workflows/phase-1-0-productization/phase-0-5-runtime-recovery-gate.md>)|Phase 0.5 Runtime Recovery Gate|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/recovery-runbook.md](<../workflows/phase-1-0-productization/recovery-runbook.md>)|v1.0 Recovery Runbook|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/requirements.md](<../workflows/phase-1-0-productization/requirements.md>)|Requirements: Phase 1.0 Productization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/risks.md](<../workflows/phase-1-0-productization/risks.md>)|Residual Risks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/schema-authority-compatibility-matrix.md](<../workflows/phase-1-0-productization/schema-authority-compatibility-matrix.md>)|Schema Authority Compatibility Matrix — SA-A|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-1-0-productization/tasks.md](<../workflows/phase-1-0-productization/tasks.md>)|Tasks: Phase 1.0 Productization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|59/4|
|[docs/workflows/phase-1-0-productization/validation.md](<../workflows/phase-1-0-productization/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/README.md](<../workflows/phase-c-execution-preparation/README.md>)|Phase C：Execution Preparation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/alembic-metadata-coverage.md](<../workflows/phase-c-execution-preparation/alembic-metadata-coverage.md>)|Alembic Metadata Coverage Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/auth-integration-test-plan.md](<../workflows/phase-c-execution-preparation/auth-integration-test-plan.md>)|Permission Integration Test Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/auth-test-matrix.md](<../workflows/phase-c-execution-preparation/auth-test-matrix.md>)|Authentication Boundary Test Matrix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/backup-restore-validation-plan.md](<../workflows/phase-c-execution-preparation/backup-restore-validation-plan.md>)|Backup and Restore Validation Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/column-drift-ownership-report.md](<../workflows/phase-c-execution-preparation/column-drift-ownership-report.md>)|Column Drift Ownership Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/data-baseline.md](<../workflows/phase-c-execution-preparation/data-baseline.md>)|Data Baseline|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/design.md](<../workflows/phase-c-execution-preparation/design.md>)|Phase C Execution Preparation：设计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/guest-table-origin-report.md](<../workflows/phase-c-execution-preparation/guest-table-origin-report.md>)|Guest Table Origin Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/index-drift-report.md](<../workflows/phase-c-execution-preparation/index-drift-report.md>)|Index Drift Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/migration-baseline.md](<../workflows/phase-c-execution-preparation/migration-baseline.md>)|Database Migration Baseline|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/migration-gate-closure-checklist.md](<../workflows/phase-c-execution-preparation/migration-gate-closure-checklist.md>)|Migration Gate Closure Checklist|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/migration-provenance-inventory.md](<../workflows/phase-c-execution-preparation/migration-provenance-inventory.md>)|Migration Provenance Inventory|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/owner-mapping-readiness.md](<../workflows/phase-c-execution-preparation/owner-mapping-readiness.md>)|Owner Mapping Readiness|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/owner-migration-design.md](<../workflows/phase-c-execution-preparation/owner-migration-design.md>)|Owner Migration Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/phase-c-gate-checklist.md](<../workflows/phase-c-execution-preparation/phase-c-gate-checklist.md>)|Phase C Migration Gate Checklist|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|10/12|
|[docs/workflows/phase-c-execution-preparation/requirements.md](<../workflows/phase-c-execution-preparation/requirements.md>)|Phase C Execution Preparation：需求|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-authority-audit.md](<../workflows/phase-c-execution-preparation/schema-authority-audit.md>)|Schema Authority Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-authority-convergence-plan.md](<../workflows/phase-c-execution-preparation/schema-authority-convergence-plan.md>)|Schema Authority Convergence Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-authority-decision.md](<../workflows/phase-c-execution-preparation/schema-authority-decision.md>)|Schema Authority Decision|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-authority-validation.md](<../workflows/phase-c-execution-preparation/schema-authority-validation.md>)|Schema Authority Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-coverage-final-matrix.md](<../workflows/phase-c-execution-preparation/schema-coverage-final-matrix.md>)|Schema Coverage Final Matrix|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-entrypoints.md](<../workflows/phase-c-execution-preparation/schema-entrypoints.md>)|Schema Entry Points Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-inventory.md](<../workflows/phase-c-execution-preparation/schema-inventory.md>)|Schema Inventory|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-provenance-validation.md](<../workflows/phase-c-execution-preparation/schema-provenance-validation.md>)|Schema Provenance Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/schema-three-way-drift-report.md](<../workflows/phase-c-execution-preparation/schema-three-way-drift-report.md>)|Schema Three-Way Drift Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/phase-c-execution-preparation/tasks.md](<../workflows/phase-c-execution-preparation/tasks.md>)|Phase C Execution Preparation：任务清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|17/0|
|[docs/workflows/phase-c-execution-preparation/validation.md](<../workflows/phase-c-execution-preparation/validation.md>)|Phase C Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-auth-cors-cleanup/README.md](<../workflows/production-auth-cors-cleanup/README.md>)|Production Auth/CORS Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-auth-cors-cleanup/design.md](<../workflows/production-auth-cors-cleanup/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-auth-cors-cleanup/handoff-prompt.md](<../workflows/production-auth-cors-cleanup/handoff-prompt.md>)|Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-auth-cors-cleanup/requirements.md](<../workflows/production-auth-cors-cleanup/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-auth-cors-cleanup/tasks.md](<../workflows/production-auth-cors-cleanup/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|21/0|
|[docs/workflows/production-auth-cors-cleanup/validation.md](<../workflows/production-auth-cors-cleanup/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/README.md](<../workflows/production-render-readiness-acceptance/README.md>)|Production Render Readiness Acceptance|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/assets/pra07-raw-aggregation-20260822.md](<../workflows/production-render-readiness-acceptance/assets/pra07-raw-aggregation-20260822.md>)|PRA-07 Raw-only aggregation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/audit.md](<../workflows/production-render-readiness-acceptance/audit.md>)|F4 Input Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/design.md](<../workflows/production-render-readiness-acceptance/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/next-requirements.md](<../workflows/production-render-readiness-acceptance/next-requirements.md>)|Next Iteration Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/requirements.md](<../workflows/production-render-readiness-acceptance/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/risks.md](<../workflows/production-render-readiness-acceptance/risks.md>)|Residual Risks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/production-render-readiness-acceptance/tasks.md](<../workflows/production-render-readiness-acceptance/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|22/0|
|[docs/workflows/production-render-readiness-acceptance/validation.md](<../workflows/production-render-readiness-acceptance/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-deployment-config-restore/README.md](<../workflows/public-deployment-config-restore/README.md>)|Public Deployment Config Restore|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-deployment-config-restore/design.md](<../workflows/public-deployment-config-restore/design.md>)|Design — Public Deployment Config Restore|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-deployment-config-restore/diff-report.md](<../workflows/public-deployment-config-restore/diff-report.md>)|Diff Report — Public Deployment Config Restore|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-deployment-config-restore/handoff-prompt.md](<../workflows/public-deployment-config-restore/handoff-prompt.md>)|Handoff Prompt — Public Deployment Config Restore|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-deployment-config-restore/requirements.md](<../workflows/public-deployment-config-restore/requirements.md>)|Requirements — Public Deployment Config Restore|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-deployment-config-restore/tasks.md](<../workflows/public-deployment-config-restore/tasks.md>)|Tasks — Public Deployment Config Restore|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|25/0|
|[docs/workflows/public-deployment-config-restore/validation.md](<../workflows/public-deployment-config-restore/validation.md>)|Validation — Public Deployment Config Restore|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-mistake-review-api-gate/README.md](<../workflows/public-mistake-review-api-gate/README.md>)|Public Mistake Review API Gate|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-mistake-review-api-gate/design.md](<../workflows/public-mistake-review-api-gate/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-mistake-review-api-gate/handoff-prompt.md](<../workflows/public-mistake-review-api-gate/handoff-prompt.md>)|Handoff|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-mistake-review-api-gate/requirements.md](<../workflows/public-mistake-review-api-gate/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-mistake-review-api-gate/tasks.md](<../workflows/public-mistake-review-api-gate/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|12/0|
|[docs/workflows/public-mistake-review-api-gate/validation.md](<../workflows/public-mistake-review-api-gate/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/README.md](<../workflows/public-session-state-optimization/README.md>)|Public Session State Optimization|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-02-first-failure.md](<../workflows/public-session-state-optimization/assets/pss-02-first-failure.md>)|PSS-02 first failing evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-03-final-pass.md](<../workflows/public-session-state-optimization/assets/pss-03-final-pass.md>)|PSS-03 final pass evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-04-final-pass.md](<../workflows/public-session-state-optimization/assets/pss-04-final-pass.md>)|PSS-04 final pass evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-04-first-failure.md](<../workflows/public-session-state-optimization/assets/pss-04-first-failure.md>)|PSS-04 first failing evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-05-final-pass.md](<../workflows/public-session-state-optimization/assets/pss-05-final-pass.md>)|PSS-05 final pass evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-05-first-failure.md](<../workflows/public-session-state-optimization/assets/pss-05-first-failure.md>)|PSS-05 first failing evidence|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-06-final-pass.md](<../workflows/public-session-state-optimization/assets/pss-06-final-pass.md>)|PSS-06 final isolated-browser pass|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-06-first-failure.md](<../workflows/public-session-state-optimization/assets/pss-06-first-failure.md>)|PSS-06 first browser failure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/assets/pss-06-second-failure.md](<../workflows/public-session-state-optimization/assets/pss-06-second-failure.md>)|PSS-06 second browser failure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/audit.md](<../workflows/public-session-state-optimization/audit.md>)|PSS-01 Contract and Consumer Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/design.md](<../workflows/public-session-state-optimization/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/requirements.md](<../workflows/public-session-state-optimization/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-session-state-optimization/tasks.md](<../workflows/public-session-state-optimization/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|11/0|
|[docs/workflows/public-session-state-optimization/validation.md](<../workflows/public-session-state-optimization/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-site-closure-upgrade/README.md](<../workflows/public-site-closure-upgrade/README.md>)|Public Site Closure Upgrade|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-site-closure-upgrade/design.md](<../workflows/public-site-closure-upgrade/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-site-closure-upgrade/requirements.md](<../workflows/public-site-closure-upgrade/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/public-site-closure-upgrade/tasks.md](<../workflows/public-site-closure-upgrade/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|30/0|
|[docs/workflows/public-site-closure-upgrade/validation.md](<../workflows/public-site-closure-upgrade/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-cutover-after-batch-8/README.md](<../workflows/route-cutover-after-batch-8/README.md>)|Route Cutover Sprint：新旧路由束口与旧入口下线|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-cutover-after-batch-8/checklist.md](<../workflows/route-cutover-after-batch-8/checklist.md>)|Checklist：Route Cutover Sprint 验收清单|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/38|
|[docs/workflows/route-cutover-after-batch-8/design.md](<../workflows/route-cutover-after-batch-8/design.md>)|Design：Route Cutover Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-cutover-after-batch-8/handoff.md](<../workflows/route-cutover-after-batch-8/handoff.md>)|Handoff：Route Cutover Sprint 交接说明|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-cutover-after-batch-8/requirements.md](<../workflows/route-cutover-after-batch-8/requirements.md>)|需求：Route Cutover Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-cutover-after-batch-8/risks.md](<../workflows/route-cutover-after-batch-8/risks.md>)|Risks：Route Cutover Sprint 风险记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-cutover-after-batch-8/tasks.md](<../workflows/route-cutover-after-batch-8/tasks.md>)|Tasks：Route Cutover Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|40/1|
|[docs/workflows/route-cutover-after-batch-8/validation.md](<../workflows/route-cutover-after-batch-8/validation.md>)|Validation：Route Cutover Sprint 验证方案与记录模板|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|5/0|
|[docs/workflows/route-ownership-alignment/README.md](<../workflows/route-ownership-alignment/README.md>)|Route Ownership Alignment|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-ownership-alignment/audit.md](<../workflows/route-ownership-alignment/audit.md>)|Route and navigation audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-ownership-alignment/design.md](<../workflows/route-ownership-alignment/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-ownership-alignment/requirements.md](<../workflows/route-ownership-alignment/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/route-ownership-alignment/tasks.md](<../workflows/route-ownership-alignment/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|7/0|
|[docs/workflows/route-ownership-alignment/validation.md](<../workflows/route-ownership-alignment/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/README.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/README.md>)|Phase C+3 Schema Authority Closure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/alembic-authority-implementation-design.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/alembic-authority-implementation-design.md>)|Alembic Authority Implementation Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/alembic-only-transition-plan.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/alembic-only-transition-plan.md>)|Alembic-only Transition Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/code-change-plan.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/code-change-plan.md>)|Code Change Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/design.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/design.md>)|C+3 Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/guest-schema-authority-decision.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/guest-schema-authority-decision.md>)|Guest Schema Authority Decision|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/guest-schema-final-decision.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/guest-schema-final-decision.md>)|Guest Schema Final Decision Preparation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/guest-schema-ownership-decision.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/guest-schema-ownership-decision.md>)|Guest Schema Ownership Decision|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/implementation-scope-freeze.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/implementation-scope-freeze.md>)|Implementation Scope Freeze|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/index-metadata-policy.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/index-metadata-policy.md>)|Index Metadata Policy|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/migration-execution-plan.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/migration-execution-plan.md>)|Migration Execution Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/nullable-contract-decision.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/nullable-contract-decision.md>)|Nullable Contract Decision|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/phase-c3-execution-report.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/phase-c3-execution-report.md>)|Phase C+3 Execution Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/phase-c4-execution-report.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/phase-c4-execution-report.md>)|Phase C+4 Execution Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/phase-c5-readiness-report.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/phase-c5-readiness-report.md>)|Phase C+5 Readiness Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/requirements.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/requirements.md>)|C+3 Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-authority-closure-decision.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-authority-closure-decision.md>)|Schema Authority Closure Decision|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-authority-closure-validation.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-authority-closure-validation.md>)|Schema Authority Closure Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-drift-decision-package.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-drift-decision-package.md>)|Schema Drift Decision Package|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-drift-resolution-plan.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-drift-resolution-plan.md>)|Schema Drift Resolution Plan|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-remediation-approval-package.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/schema-remediation-approval-package.md>)|Schema Remediation Approval Package|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/tasks.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/tasks.md>)|C+3 Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|19/1|
|[docs/workflows/scoped-git-commit-2026-07-17/README.md](<../workflows/scoped-git-commit-2026-07-17/README.md>)|Scoped Git Commit Task Group|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/scoped-git-commit-2026-07-17/audit.md](<../workflows/scoped-git-commit-2026-07-17/audit.md>)|Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/scoped-git-commit-2026-07-17/design.md](<../workflows/scoped-git-commit-2026-07-17/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/scoped-git-commit-2026-07-17/diff-report.md](<../workflows/scoped-git-commit-2026-07-17/diff-report.md>)|Diff Report|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/scoped-git-commit-2026-07-17/requirements.md](<../workflows/scoped-git-commit-2026-07-17/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/scoped-git-commit-2026-07-17/tasks.md](<../workflows/scoped-git-commit-2026-07-17/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|8/1|
|[docs/workflows/scoped-git-commit-2026-07-17/validation.md](<../workflows/scoped-git-commit-2026-07-17/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/security-findings-remediation/README.md](<../workflows/security-findings-remediation/README.md>)|Security Findings Remediation (2026-08-29)|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/security-findings-remediation/design.md](<../workflows/security-findings-remediation/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/security-findings-remediation/requirements.md](<../workflows/security-findings-remediation/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/security-findings-remediation/tasks.md](<../workflows/security-findings-remediation/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/security-findings-remediation/validation.md](<../workflows/security-findings-remediation/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stability-fixes/README.md](<../workflows/stability-fixes/README.md>)|稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stability-fixes/design.md](<../workflows/stability-fixes/design.md>)|Design: 稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stability-fixes/requirements.md](<../workflows/stability-fixes/requirements.md>)|Requirements: 稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stability-fixes/tasks.md](<../workflows/stability-fixes/tasks.md>)|Tasks: 稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|25/0|
|[docs/workflows/stability-fixes/validation.md](<../workflows/stability-fixes/validation.md>)|交叉验证报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stream-run-lifecycle-design-review/README.md](<../workflows/stream-run-lifecycle-design-review/README.md>)|RISK-B11-003 Stream Lifecycle Design Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stream-run-lifecycle-design-review/audit.md](<../workflows/stream-run-lifecycle-design-review/audit.md>)|Audit — RISK-B11-003|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stream-run-lifecycle-design-review/checklist.md](<../workflows/stream-run-lifecycle-design-review/checklist.md>)|Design Review Checklist|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|34/0|
|[docs/workflows/stream-run-lifecycle-design-review/design.md](<../workflows/stream-run-lifecycle-design-review/design.md>)|Design Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stream-run-lifecycle-design-review/handoff.md](<../workflows/stream-run-lifecycle-design-review/handoff.md>)|Handoff — B11-003 Stream Endpoint Simplification Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stream-run-lifecycle-design-review/requirements.md](<../workflows/stream-run-lifecycle-design-review/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stream-run-lifecycle-design-review/risks.md](<../workflows/stream-run-lifecycle-design-review/risks.md>)|Residual Risks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/stream-run-lifecycle-design-review/tasks.md](<../workflows/stream-run-lifecycle-design-review/tasks.md>)|Tasks — Stream Endpoint Simplification Closure|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|9/4|
|[docs/workflows/stream-run-lifecycle-design-review/validation.md](<../workflows/stream-run-lifecycle-design-review/validation.md>)|Validation — B11-003 Stream Endpoint Simplification Patch|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/system-freeze-acceptance-sprint/README.md](<../workflows/system-freeze-acceptance-sprint/README.md>)|System Freeze & Acceptance Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/system-freeze-acceptance-sprint/audit.md](<../workflows/system-freeze-acceptance-sprint/audit.md>)|Audit — Codex Quality Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/system-freeze-acceptance-sprint/design.md](<../workflows/system-freeze-acceptance-sprint/design.md>)|Design — System Freeze & Acceptance Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/system-freeze-acceptance-sprint/diff-report.md](<../workflows/system-freeze-acceptance-sprint/diff-report.md>)|Diff Report — SFA-01 Workflow Status Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/system-freeze-acceptance-sprint/final-decision.md](<../workflows/system-freeze-acceptance-sprint/final-decision.md>)|Final Daily-Use Decision|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/system-freeze-acceptance-sprint/requirements.md](<../workflows/system-freeze-acceptance-sprint/requirements.md>)|Requirements — System Freeze & Acceptance Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/system-freeze-acceptance-sprint/tasks.md](<../workflows/system-freeze-acceptance-sprint/tasks.md>)|Tasks — System Freeze & Acceptance Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|38/0|
|[docs/workflows/system-freeze-acceptance-sprint/validation.md](<../workflows/system-freeze-acceptance-sprint/validation.md>)|Validation — System Freeze & Acceptance Sprint|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/temp-admin-bootstrap/README.md](<../workflows/temp-admin-bootstrap/README.md>)|Temporary Admin Bootstrap|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/temp-admin-bootstrap/design.md](<../workflows/temp-admin-bootstrap/design.md>)|Temporary Admin Bootstrap Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/temp-admin-bootstrap/handoff-prompt.md](<../workflows/temp-admin-bootstrap/handoff-prompt.md>)|Temporary Admin Bootstrap Handoff Prompt|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/temp-admin-bootstrap/requirements.md](<../workflows/temp-admin-bootstrap/requirements.md>)|Temporary Admin Bootstrap Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/temp-admin-bootstrap/tasks.md](<../workflows/temp-admin-bootstrap/tasks.md>)|Temporary Admin Bootstrap Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|5/0|
|[docs/workflows/temp-admin-bootstrap/validation.md](<../workflows/temp-admin-bootstrap/validation.md>)|Temporary Admin Bootstrap Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/test-teardown-cleanup/README.md](<../workflows/test-teardown-cleanup/README.md>)|Test Teardown Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/test-teardown-cleanup/design.md](<../workflows/test-teardown-cleanup/design.md>)|Design：Test Teardown Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/test-teardown-cleanup/requirements.md](<../workflows/test-teardown-cleanup/requirements.md>)|Requirements：Test Teardown Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/test-teardown-cleanup/tasks.md](<../workflows/test-teardown-cleanup/tasks.md>)|Tasks：Test Teardown Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|24/0|
|[docs/workflows/test-teardown-cleanup/validation.md](<../workflows/test-teardown-cleanup/validation.md>)|Validation：Test Teardown Cleanup|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ui-browser-review/README.md](<../workflows/ui-browser-review/README.md>)|UI Browser Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ui-browser-review/design.md](<../workflows/ui-browser-review/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ui-browser-review/requirements.md](<../workflows/ui-browser-review/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/ui-browser-review/tasks.md](<../workflows/ui-browser-review/tasks.md>)|Task List|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|7/0|
|[docs/workflows/ui-browser-review/validation.md](<../workflows/ui-browser-review/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/updated-business-plan-audit/README.md](<../workflows/updated-business-plan-audit/README.md>)|Updated Business Plan Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/updated-business-plan-audit/audit.md](<../workflows/updated-business-plan-audit/audit.md>)|更新版计划书只读审查报告|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/updated-business-plan-audit/design.md](<../workflows/updated-business-plan-audit/design.md>)|Audit Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/updated-business-plan-audit/requirements.md](<../workflows/updated-business-plan-audit/requirements.md>)|Audit Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/updated-business-plan-audit/tasks.md](<../workflows/updated-business-plan-audit/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|9/0|
|[docs/workflows/updated-business-plan-audit/validation.md](<../workflows/updated-business-plan-audit/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/visual-system-consolidation/README.md](<../workflows/visual-system-consolidation/README.md>)|Visual System Consolidation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/visual-system-consolidation/design.md](<../workflows/visual-system-consolidation/design.md>)|Design|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/visual-system-consolidation/navigation-overlay-context-actions.md](<../workflows/visual-system-consolidation/navigation-overlay-context-actions.md>)|Navigation, Overlay, and Context Action Specification|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/visual-system-consolidation/requirements.md](<../workflows/visual-system-consolidation/requirements.md>)|Requirements|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/visual-system-consolidation/tasks.md](<../workflows/visual-system-consolidation/tasks.md>)|Tasks|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/17|
|[docs/workflows/visual-system-consolidation/validation.md](<../workflows/visual-system-consolidation/validation.md>)|Validation|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/README.md](<../workflows/week-completion-quality-audit-2026-09-27/README.md>)|全 Week 完成质量审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/completion-checklist.md](<../workflows/week-completion-quality-audit-2026-09-27/completion-checklist.md>)|按原Prompt验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/design.md](<../workflows/week-completion-quality-audit-2026-09-27/design.md>)|审计方法|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/requirements.md](<../workflows/week-completion-quality-audit-2026-09-27/requirements.md>)|验收|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/tasks.md](<../workflows/week-completion-quality-audit-2026-09-27/tasks.md>)|执行记录|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/validation.md](<../workflows/week-completion-quality-audit-2026-09-27/validation.md>)|当前运行证据|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/workers/baseline-week12.md](<../workflows/week-completion-quality-audit-2026-09-27/workers/baseline-week12.md>)|基线与 convergence Week 1–2 审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/workers/frontend-quality.md](<../workflows/week-completion-quality-audit-2026-09-27/workers/frontend-quality.md>)|前端质量专项审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/workers/independent-review.md](<../workflows/week-completion-quality-audit-2026-09-27/workers/independent-review.md>)|主审计报告独立技术审查|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/workers/testing-engineering.md](<../workflows/week-completion-quality-audit-2026-09-27/workers/testing-engineering.md>)|Testing and Engineering Quality Review|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/workers/week3-architecture.md](<../workflows/week-completion-quality-audit-2026-09-27/workers/week3-architecture.md>)|Week 3 架构与数据流专项审计|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-quality-audit-2026-09-27/workers/week4-backend.md](<../workflows/week-completion-quality-audit-2026-09-27/workers/week4-backend.md>)|Week 4 Backend and Database Audit|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/README.md](<../workflows/week-completion-remediation-2026-09-27/README.md>)|全 Week 审计修复方案|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/design.md](<../workflows/week-completion-remediation-2026-09-27/design.md>)|修复设计与决策|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/execution-verification/README.md](<../workflows/week-completion-remediation-2026-09-27/execution-verification/README.md>)|修复方案执行情况独立核验|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/requirements.md](<../workflows/week-completion-remediation-2026-09-27/requirements.md>)|需求与范围|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/rework-evidence/README.md](<../workflows/week-completion-remediation-2026-09-27/rework-evidence/README.md>)|返工证据账本（B00–B07，本地隔离）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/rework-evidence/STATUS.md](<../workflows/week-completion-remediation-2026-09-27/rework-evidence/STATUS.md>)|本次返工执行状态（2026-09-27）|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/rework-evidence/b05a-canonical-ai-creation.md](<../workflows/week-completion-remediation-2026-09-27/rework-evidence/b05a-canonical-ai-creation.md>)|B05a — Canonical AI-creation contract and incremental schema|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/rework-plan.md](<../workflows/week-completion-remediation-2026-09-27/rework-plan.md>)|执行核验后的返工方案|HISTORICAL_SNAPSHOT|治理标识/优先入口；非全段验收|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/tasks.md](<../workflows/week-completion-remediation-2026-09-27/tasks.md>)|串行执行任务书|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[docs/workflows/week-completion-remediation-2026-09-27/validation.md](<../workflows/week-completion-remediation-2026-09-27/validation.md>)|验证计划与证据状态|HISTORICAL_SNAPSHOT|机械盘点；内容需按任务复核|0/0|
|[src/features/ui-v2/README.md](<../../src/features/ui-v2/README.md>)|UI V2 原型组装层|CURRENT|当前基线/受治理入口|0/0|
|[src/lib/markdown-poc/__tests__/browser-candidate-review.md](<../../src/lib/markdown-poc/__tests__/browser-candidate-review.md>)|Browser Test Runner — Deferred Decision|REFERENCE_RECHECK|机械盘点；内容需按任务复核|0/0|
|[tasks-process-keepalive.md](<../../tasks-process-keepalive.md>)|进程保活与公网连接稳定性任务清单|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|8/51|
|[tasks.md](<../../tasks.md>)|闭环修复任务清单|LOGICALLY_ARCHIVED|治理标识/优先入口；非全段验收|0/156|

## 全部开发工作流登记

每个目录均已登记；当前运行整项状态默认UNVERIFIED，主要Week/B/I/UI家族的语义核验以 [PROJECT_STATUS](../PROJECT_STATUS.md) 为准。不会把历史checkbox或gate自动升级为当前完成。

|Workflow家族|Markdown数量|复查入口|
|---|---|---|
|`admin-contract-organization-music-upgrade`|7|[README.md](<../workflows/admin-contract-organization-music-upgrade/README.md>)|
|`ai-mistake-navigation-upgrade`|10|[README.md](<../workflows/ai-mistake-navigation-upgrade/README.md>)|
|`ai-skill-pipeline`|7|[README.md](<../workflows/ai-skill-pipeline/README.md>)|
|`batch-10-1-prompt-registry-runtime-integration`|6|[README.md](<../workflows/batch-10-1-prompt-registry-runtime-integration/README.md>)|
|`batch-10-2-prompt-engineering-standardization`|6|[README.md](<../workflows/batch-10-2-prompt-engineering-standardization/README.md>)|
|`batch-10-task-prompt-validator`|5|[README.md](<../workflows/batch-10-task-prompt-validator/README.md>)|
|`batch-11-ai-run-audit-human-review`|8|[README.md](<../workflows/batch-11-ai-run-audit-human-review/README.md>)|
|`batch-12-ai-provider-routing-cost-stability`|9|[README.md](<../workflows/batch-12-ai-provider-routing-cost-stability/README.md>)|
|`batch-2-subject-knowledge-point`|11|[README.md](<../workflows/batch-2-subject-knowledge-point/README.md>)|
|`batch-3-question-system`|12|[README.md](<../workflows/batch-3-question-system/README.md>)|
|`batch-4-mistake-review`|10|[README.md](<../workflows/batch-4-mistake-review/README.md>)|
|`batch-5-attachments`|10|[README.md](<../workflows/batch-5-attachments/README.md>)|
|`batch-6-ai-ocr-placeholders`|9|[README.md](<../workflows/batch-6-ai-ocr-placeholders/README.md>)|
|`batch-7-compatibility-closure`|8|[README.md](<../workflows/batch-7-compatibility-closure/README.md>)|
|`batch-8-image-mistake-capture`|8|[README.md](<../workflows/batch-8-image-mistake-capture/README.md>)|
|`batch-9-ai-gateway-kernel`|6|[README.md](<../workflows/batch-9-ai-gateway-kernel/README.md>)|
|`blog-cover-save-fix`|6|[README.md](<../workflows/blog-cover-save-fix/README.md>)|
|`ci-clean-checks-fix`|5|[README.md](<../workflows/ci-clean-checks-fix/README.md>)|
|`cleanup-workspace-db-revision-closure`|11|[README.md](<../workflows/cleanup-workspace-db-revision-closure/README.md>)|
|`cloudflare-release-2026-08-02`|5|[README.md](<../workflows/cloudflare-release-2026-08-02/README.md>)|
|`current-architecture-review-2026-10-09`|5|[README.md](<../workflows/current-architecture-review-2026-10-09/README.md>)|
|`dependency-runtime-governance`|7|[README.md](<../workflows/dependency-runtime-governance/README.md>)|
|`dependency-runtime-risk-cleanup`|7|[README.md](<../workflows/dependency-runtime-risk-cleanup/README.md>)|
|`editor-convergence`|7|[README.md](<../workflows/editor-convergence/README.md>)|
|`folder-note-assignment-fix`|10|[README.md](<../workflows/folder-note-assignment-fix/README.md>)|
|`frontend-foundation-and-quality`|8|[README.md](<../workflows/frontend-foundation-and-quality/README.md>)|
|`frontend-refactor-alignment`|6|[README.md](<../workflows/frontend-refactor-alignment/README.md>)|
|`full-audit-2025-06-23`|2|[README.md](<../workflows/full-audit-2025-06-23/README.md>)|
|`git-cleanup-public-push`|7|[README.md](<../workflows/git-cleanup-public-push/README.md>)|
|`github-open-source-selection-report`|5|[README.md](<../workflows/github-open-source-selection-report/README.md>)|
|`home-music-local-playback-fix`|6|[README.md](<../workflows/home-music-local-playback-fix/README.md>)|
|`i-series-completion-plan`|13|[README.md](<../workflows/i-series-completion-plan/README.md>)|
|`i10-migration-dry-run`|12|[README.md](<../workflows/i10-migration-dry-run/README.md>)|
|`i11-shadow-migration`|9|[README.md](<../workflows/i11-shadow-migration/README.md>)|
|`i12-final-closure`|9|[README.md](<../workflows/i12-final-closure/README.md>)|
|`i4-i5-closure-final-fix`|6|[README.md](<../workflows/i4-i5-closure-final-fix/README.md>)|
|`i4-i5-closure-fix-2`|6|[README.md](<../workflows/i4-i5-closure-fix-2/README.md>)|
|`i6-capture-draft-chain`|8|[README.md](<../workflows/i6-capture-draft-chain/README.md>)|
|`i7-file-workspace`|9|[README.md](<../workflows/i7-file-workspace/README.md>)|
|`i8-markdown-search`|9|[README.md](<../workflows/i8-markdown-search/README.md>)|
|`i9-governance-analytics`|9|[README.md](<../workflows/i9-governance-analytics/README.md>)|
|`legacy-system-retirement`|5|[README.md](<../workflows/legacy-system-retirement/README.md>)|
|`local-single-music-source`|6|[README.md](<../workflows/local-single-music-source/README.md>)|
|`manage-auth-hardening`|7|[README.md](<../workflows/manage-auth-hardening/README.md>)|
|`manage-ui-consolidation`|6|[README.md](<../workflows/manage-ui-consolidation/README.md>)|
|`markdown-rendering-security-poc`|7|[README.md](<../workflows/markdown-rendering-security-poc/README.md>)|
|`markdown-special-adapter-enablement`|11|[README.md](<../workflows/markdown-special-adapter-enablement/README.md>)|
|`mistake-ai-image-personalization-fix`|8|[README.md](<../workflows/mistake-ai-image-personalization-fix/README.md>)|
|`mistake-editor-simplification`|5|[README.md](<../workflows/mistake-editor-simplification/README.md>)|
|`mistake-learning-reliability-upgrade`|8|[README.md](<../workflows/mistake-learning-reliability-upgrade/README.md>)|
|`mistake-staged-error-diagram-generation`|7|[README.md](<../workflows/mistake-staged-error-diagram-generation/README.md>)|
|`music-auto-deploy-script`|6|[README.md](<../workflows/music-auto-deploy-script/README.md>)|
|`music-selection-auto-deploy`|6|[README.md](<../workflows/music-selection-auto-deploy/README.md>)|
|`mvp-goal-gap-analysis`|6|[README.md](<../workflows/mvp-goal-gap-analysis/README.md>)|
|`mvp-local-trial-acceptance`|14|[README.md](<../workflows/mvp-local-trial-acceptance/README.md>)|
|`mvp-public-deployment`|7|[README.md](<../workflows/mvp-public-deployment/README.md>)|
|`mvp-rebuild-batch-0-docs-freeze`|6|[README.md](<../workflows/mvp-rebuild-batch-0-docs-freeze/README.md>)|
|`mvp-rebuild-batch-1-ui-shell`|6|[README.md](<../workflows/mvp-rebuild-batch-1-ui-shell/README.md>)|
|`mvp-rebuild-batch-2-subject-taxonomy`|6|[README.md](<../workflows/mvp-rebuild-batch-2-subject-taxonomy/README.md>)|
|`mvp-rebuild-batch-3-drafts-question-bank`|6|[README.md](<../workflows/mvp-rebuild-batch-3-drafts-question-bank/README.md>)|
|`mvp-rebuild-batch-4-mistakes-review`|6|[README.md](<../workflows/mvp-rebuild-batch-4-mistakes-review/README.md>)|
|`mvp-rebuild-batch-5-attachments`|6|[README.md](<../workflows/mvp-rebuild-batch-5-attachments/README.md>)|
|`mvp-rebuild-batch-6-ai-ocr-placeholders`|6|[README.md](<../workflows/mvp-rebuild-batch-6-ai-ocr-placeholders/README.md>)|
|`mvp-rebuild-batch-7-polish-compatibility`|8|[README.md](<../workflows/mvp-rebuild-batch-7-polish-compatibility/README.md>)|
|`mvp-rebuild-spec-planning`|5|[README.md](<../workflows/mvp-rebuild-spec-planning/README.md>)|
|`note-edit-409-conflict`|6|[README.md](<../workflows/note-edit-409-conflict/README.md>)|
|`notes-workspace-ux-upgrade`|8|[README.md](<../workflows/notes-workspace-ux-upgrade/README.md>)|
|`open-source-closure`|6|[README.md](<../workflows/open-source-closure/README.md>)|
|`p0-auth-manage-access-closure`|11|[README.md](<../workflows/p0-auth-manage-access-closure/README.md>)|
|`p0-closure-precheck`|6|[README.md](<../workflows/p0-closure-precheck/README.md>)|
|`p1-acceptance-cleanup-patch`|7|[README.md](<../workflows/p1-acceptance-cleanup-patch/README.md>)|
|`p2-test-performance-tuning`|6|[README.md](<../workflows/p2-test-performance-tuning/README.md>)|
|`page-render-timing-validation`|9|[README.md](<../workflows/page-render-timing-validation/README.md>)|
|`personal-learning-system-convergence`|109|[README.md](<../workflows/personal-learning-system-convergence/README.md>)|
|`personal-learning-system-v2`|15|[README.md](<../workflows/personal-learning-system-v2/README.md>)|
|`personal-learning-system-v2-unification`|38|[README.md](<../workflows/personal-learning-system-v2-unification/README.md>)|
|`personal-learning-ui-foundation`|5|[README.md](<../workflows/personal-learning-ui-foundation/README.md>)|
|`personal-learning-ui-v2`|6|[README.md](<../workflows/personal-learning-ui-v2/README.md>)|
|`phase-1-0-productization`|12|[README.md](<../workflows/phase-1-0-productization/README.md>)|
|`phase-c-execution-preparation`|28|[README.md](<../workflows/phase-c-execution-preparation/README.md>)|
|`production-auth-cors-cleanup`|6|[README.md](<../workflows/production-auth-cors-cleanup/README.md>)|
|`production-render-readiness-acceptance`|9|[README.md](<../workflows/production-render-readiness-acceptance/README.md>)|
|`public-deployment-config-restore`|7|[README.md](<../workflows/public-deployment-config-restore/README.md>)|
|`public-mistake-review-api-gate`|6|[README.md](<../workflows/public-mistake-review-api-gate/README.md>)|
|`public-session-state-optimization`|15|[README.md](<../workflows/public-session-state-optimization/README.md>)|
|`public-site-closure-upgrade`|5|[README.md](<../workflows/public-site-closure-upgrade/README.md>)|
|`route-cutover-after-batch-8`|8|[README.md](<../workflows/route-cutover-after-batch-8/README.md>)|
|`route-ownership-alignment`|6|[README.md](<../workflows/route-ownership-alignment/README.md>)|
|`schema-provenance-drift-closure`|22|[README.md](<../workflows/schema-provenance-drift-closure/phase-c3-schema-authority-closure/README.md>)|
|`scoped-git-commit-2026-07-17`|7|[README.md](<../workflows/scoped-git-commit-2026-07-17/README.md>)|
|`security-findings-remediation`|5|[README.md](<../workflows/security-findings-remediation/README.md>)|
|`stability-fixes`|5|[README.md](<../workflows/stability-fixes/README.md>)|
|`stream-run-lifecycle-design-review`|9|[README.md](<../workflows/stream-run-lifecycle-design-review/README.md>)|
|`system-freeze-acceptance-sprint`|8|[README.md](<../workflows/system-freeze-acceptance-sprint/README.md>)|
|`temp-admin-bootstrap`|6|[README.md](<../workflows/temp-admin-bootstrap/README.md>)|
|`test-teardown-cleanup`|5|[README.md](<../workflows/test-teardown-cleanup/README.md>)|
|`ui-browser-review`|5|[README.md](<../workflows/ui-browser-review/README.md>)|
|`updated-business-plan-audit`|6|[README.md](<../workflows/updated-business-plan-audit/README.md>)|
|`visual-system-consolidation`|6|[README.md](<../workflows/visual-system-consolidation/README.md>)|
|`week-completion-quality-audit-2026-09-27`|12|[README.md](<../workflows/week-completion-quality-audit-2026-09-27/README.md>)|
|`week-completion-remediation-2026-09-27`|10|[README.md](<../workflows/week-completion-remediation-2026-09-27/README.md>)|

## 完全相同文本的组

哈希相同仅表示相同文字，不自动删除；原任务trace可能需要各自路径。
无完全相同文本组。

## 仅artifact的workflow目录

`docs/workflows/agent-governance-refresh/` 存在但无Markdown，作为第102个workflow目录登记；只做存在性盘点，不推导完成。`.DS_Store`不是workflow。

