# Requirements — UI V2 Full Implementation（U1–U16）

状态词：TODO / READY / IN_PROGRESS / BLOCKED / IMPLEMENTED / REVIEWING /
CHANGES_REQUESTED / VERIFIED / PASS / FAIL / NOT_APPLICABLE。

## REQ-U1 App Shell

- R-U1-1：交付 presentational 的 Sidebar / Header / Navigation / Page Layout /
  Content Container / Breadcrumb / Mobile Navigation（`src/components/ui-v2/`），
  用户能知道“我在哪里 / 能做什么 / 主要操作在哪里”。
- R-U1-2：导航配置 `navigation.ts` 映射现有路由 → 学习/知识/分析/资料/设置分组，
  不改现有 sidebar/layout 文件。
- R-U1-3：desktop / tablet / mobile / keyboard 可用（语义 HTML + focus-visible）。

## REQ-U2 Dashboard

- R-U2-1：首页围绕 Today / Review / Weakness / Recent Learning / Learning Trend /
  Next Action；禁止以笔记数/标签数/博客数为核心。
- R-U2-2：覆盖 loading / empty / error / partial / success（含 retry）。
- R-U2-3：数据经 adapter 来自 DashboardSummary 或 mock，`source` 明确标注。

## REQ-U3 Today

- R-U3-1：实现“今天学什么”入口 UI + adapter；后端无统一任务流（GAP-001）
  → 真实集成保持 BLOCKED，UI 明确标注数据来源（REAL / PARTIAL / MOCK / BLOCKED）。
- R-U3-2：不得把 Mock 伪装成真实功能。

## REQ-U4 Mistakes

- R-U4-1：canonical Mistake UX：列表 / 筛选 / 状态 / 知识点 / 来源 / 最近错误 /
  复习入口 / 空状态 / 错误状态。
- R-U4-2：基于 canonical Mistake DTO（`src/lib/api/mistakes.ts`，稳定契约）适配；
  不得破坏现有 canonical 数据（只读展示，不写 mutation）。

## REQ-U5 Review（高风险）

- R-U5-1：实施前已复核 Week2 状态（PR-06/07/08 NOT_VERIFIED）。
- R-U5-2：本轮只做 layout / component / mock / contract / test；
  真实 integration = BLOCKED_BY_WEEK2；Week2 Gate 后重新审计契约再接入。
- R-U5-3：六档评分等语义不得由 UI 发明；mock 评分展示必须标注 `source: 'mock'`。

## REQ-U6 Questions

- R-U6-1：Question List / Detail / Practice Entry / Answer State / Result State /
  Mistake Relation / Knowledge Relation 展示。
- R-U6-2：attempt / practice 后端能力缺失 → 记 Backend Gap，不自行改 backend。

## REQ-U7 Knowledge

- R-U7-1：围绕 Subject / KnowledgePoint / Learning State / Related Questions /
  Related Mistakes / Related Notes 组织；不只做树状目录。
- R-U7-2：统计缺失时显示“暂无足够数据 / 数据积累中”。

## REQ-U8 Notes

- R-U8-1：Notes 定位为 Learning Knowledge Artifact：list / detail / editor entry /
  knowledge relation / subject relation 展示。
- R-U8-2：editor 脏文件/ownership 冲突 → Blocker，不覆盖已有工作。

## REQ-U9 Analytics

- R-U9-1：只展示有真实数据依据的分析（Trend / Review Completion / Mistake Trend /
  Weakness Distribution / Mastery Presentation）。
- R-U9-2：Mastery / Weakness / Recommendation 算法不得由 UI 创造；缺数据 → 诚实空态。

## REQ-U10 Resources

- R-U10-1：按现有 attachments 资源模型实施展示；无 canonical resource domain
  → 只做合理 UI + Gap，不创造 backend domain。

## REQ-U11 Settings

- R-U11-1：整合与学习系统直接相关的展示型设置；不得重构 Auth。

## REQ-U12 Responsive

- R-U12-1：375 / 768 / 1024 / 1440 四断点检查 navigation / sidebar / tables /
  cards / forms / dialogs / overflow / touch target / content density。

## REQ-U13 Accessibility

- R-U13-1：keyboard navigation / focus-visible / semantic HTML / label /
  aria-label / dialog focus / contrast / disabled / loading / error；
  状态不只通过颜色表达。

## REQ-U14 Integration

- R-U14-1：稳定契约模块逐步 Mock → API → Adapter → UI Contract → Component。
- R-U14-2：严禁 Component → raw backend DTO；Mock 可识别、可移除。

## REQ-U15 Final QA

- R-U15-1：route smoke / critical interaction / loading / empty / error / retry /
  responsive / keyboard / API failure / unauthorized behavior / regression。
- R-U15-2：admin/private route 按 `agents/gates.md` 触发 Security/QA Gate（只读验证）。

## REQ-U16 Final Gate

- R-U16-1：全部授权 scope IMPLEMENTED + REVIEWED + VERIFIED + VALIDATED 后申请；
  Final Gate 不自行批准。

## 非目标（本轮禁止）

commit/push/deploy、backend/schema/migration 改动、auth 策略改动、Review/Mastery/
Weakness/Recommendation 算法、现有路由迁移、现有页面重写、Week2 文件修改、
脏文件修改、生产写入。
