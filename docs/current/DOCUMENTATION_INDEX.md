# 文档索引与有效性

基线日期：2026-10-09；设计评估补充：2026-10-12。当前代码基线统一由以下入口解释；历史审计保留原裁定，目标设计不当作实现。当前盘点1220份（2026-10-11新增一份设计评估；10/09复查为1219份）Git追踪及非忽略未追踪的非public Markdown（包含隐藏PR模板），排除Git忽略文件如.agents内5份Markdown；不解析公开文章、PDF或图片每个内容页，也不验证外部URL。前两阶段1218计数保留其扫描时点。

## 当前入口及职责

|入口|职责|
|---|---|
|[PROJECT_OVERVIEW](PROJECT_OVERVIEW.md)|项目定位、成熟度、阅读入口|
|[DESIGN_RATIONALE_REVIEW](architecture/DESIGN_RATIONALE_REVIEW.md)|整体设计取舍、后端最小边界与前端八维质量目标；提案，非实现/视觉验收|
|[ARCHITECTURE_CURRENT](architecture/ARCHITECTURE_CURRENT.md)|源码真实目录/模型/API/链路与未实现目标|
|[ARCHITECTURE_AUDIT](audits/ARCHITECTURE_AUDIT.md)|问题证据、严重度、影响和裁决|
|[PROJECT_STATUS](PROJECT_STATUS.md)|历史验收、现有实现、本轮验证分开；Week/PR/B/I/UI状态|
|[ROADMAP](ROADMAP.md)|原M1–M4/PR、B返工与A/N映射、第二阶段/UI/September边界；不授权实现|
|[CURRENT_REVIEW_TRACKER](audits/CURRENT_REVIEW_TRACKER.md)|本轮Lead过程记录及最终验收|
|[CURRENT_REVIEW_EVIDENCE](audits/CURRENT_REVIEW_EVIDENCE.md)|实际命令/结果、审查分工、保护与链接验证|
|[CURRENT_SOURCE_MAP](audits/CURRENT_SOURCE_MAP.md)|42表声明/197router decorators/53page文件静态地图|
|[DOCUMENTATION_INVENTORY](audits/DOCUMENTATION_INVENTORY.md)|全部技术Markdown逐文件分类、所有workflow目录和重复文本组|
|[UI技术规格](ui-technical-specification/04-execution/refactoring-roadmap.md)|UI重构现状/目标/差距/路线；Phase 1视觉路线已确认（2026-10-17），后续Phase需单独授权|
|[光标修复记录](cursor-hotspot-fix.md)|自定义光标与导航hover偏移修复及遗留项|
|[AI governance](architecture/ai-governance.md)|现行candidate/confirm合同、退役loose绑定与未闭合事项|
|[AGENTS](../AGENTS.md)、[agents](../agents/README.md)|现行工作规则与授权边界；本轮未改Agent规则|
|[README](../README.md)、[CONTRIBUTING](../CONTRIBUTING.md)、[SECURITY](../SECURITY.md)|项目使用/贡献/安全入口；操作前验证环境/目标|

## 保留目标与ADR

`docs/architecture`原33份分域设计加1份架构入口共34份已标目标/阶段起点；当前架构与AI治理是现行例外。`mvp-scope`、`migration-plan`对Note错题的“当前”只属于Batch0设计起点；canonical表已有代码。V2长期Redis/monorepo/content_items/KnowledgeNode/StudyPlan等未实现；JWT目标已更正为现行会话。Phase0–6、Batch0–7、I/Week/U编号属于不同轨，不可拼成一条完成声明。

[ADR索引](adr/README.md)的Accepted是决策接受，不证明TodayOrchestrator或新模型已经落地。新架构改变仍需具体设计/授权，而非依据本次标记执行。

## 逻辑归档与时间谱系

- `docs/roadmap-design.md`、`roadmap-tasks.md`、`roadmap-2026-09.md`、root `design.md/tasks.md`、refactor旧报告、`final-system-boundary/backlog/handoff`、旧编辑器/知识系统/UI任务入口：保留路径与正文，顶部标历史并导向当前索引。旧JWT/Bearer、恢复bypass、机械先删除等条款不得直接执行。
- 根目录SYSTEM_MAP、各审计/质量报告与IMPROVEMENT_BACKLOG：保留当时证据，添加历史标识。历史PDF保持原字节，不重写其当时结论；新的当前状态在本轮Markdown入口。
- Week Gate/原R核验/最新B返工：原FAIL与后续PARTIAL时间不同。历史原文件不互相覆盖；现行比较在PROJECT_STATUS。
- UI Foundation/Full UI V2：保留旧REQUESTED/validation/progress快照，以最新UI_V2_MASTER_TRACKER的Final Gate GRANTED及Review依赖解除解释历史组件验收；当前主路由/Today任务流未完成集成，不把组件交付当整产品通过。
- `ai-governance.md`原文本因内部旧绑定/未接入矛盾，完整副本保存为 [历史AI治理](audits/archive/AI_GOVERNANCE_PRE_2026-10-09.md)，现行文件已重写。没有物理移动或删除历史文件。

## 完整覆盖与边界

全量清单逐文件给出有效性、标题与复查深度；所有workflow家族均登记。D对49份优先入口做语义审查，Lead针对当前与高风险文档/代码整合，不声称其余上千份历史记录每个段落均准确。其余维护参考在执行前需核对源码、环境与授权。

本轮当前入口与新增证据链接须为有效本地文件。全库历史失效引用（临时外部路径、旧文件）在 [本轮证据](audits/CURRENT_REVIEW_EVIDENCE.md) 列出，不以删除历史内容隐藏缺链。不检查外部URL、示例语法或章节anchor；存在性验证不等于内容正确。

## 治理原则

ARCHITECTURE_CURRENT是当前事实总览，AI治理等现行分域说明和概览需与其一致；PROJECT_STATUS统一解释当前状态，ROADMAP统一解释下一阶段。审查报告写问题与证据；历史快照不滚动改判，新增状态用当前入口引用。以后代码变化应同步相关契约/状态/索引及验证日期；没有当前运行证据时保留UNVERIFIED。目录/文档任务框数和测试总数均不是发布资格。
