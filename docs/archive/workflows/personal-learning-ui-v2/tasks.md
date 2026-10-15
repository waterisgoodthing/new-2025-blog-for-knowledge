# Tasks — UI V2 Full Implementation（串行为主，独立任务可并行；共享文件单写者）

> 白名单外现有文件默认 READ-ONLY。任一任务触发 STOP 条件即停该项，
> 记 Blocker 后继续独立任务；仅关键路径全阻塞才整体 STOP。

## U1 — App Shell

- [ ] T-U1-1 `src/components/ui-v2/navigation.ts`：NavSection/NavItem 类型 + 现有路由映射配置（只读映射，不改路由）。
- [ ] T-U1-2 `AppShell` / `PageLayout` / `AppHeader` / `AppSidebar` / `Breadcrumb` / `MobileNav` presentational 组件（复用 tokens，语义 HTML，keyboard 可达）。
- [ ] T-U1-3 U1 tests（导航配置完整性 + 组件渲染 + keyboard/focus 属性断言）。

## U2 — Dashboard

- [ ] T-U2-1 `src/contracts/ui-v2/dashboard.ts`：DashboardModel（today/review/weakness/recent/trend/nextAction，各段 source 标注）。
- [ ] T-U2-2 adapter `adaptDashboardSummary(DashboardSummary) → DashboardModel`（partial 降级：缺段 → null + estimated）。
- [ ] T-U2-3 mocks `dashboard-v2.ts` 六态；`DashboardSection` + `NextActionCard` 组件（六态覆盖）。
- [ ] T-U2-4 hook `useDashboardModel`（fetch → adapt → UiPageModel + retry）+ tests。

## U3 — Today

- [ ] T-U3-1 contract `study-task.ts` + mock `today.ts`（source: mock，六态）。
- [ ] T-U3-2 adapter（DashboardSummary/ReviewPlan → StudyTask[]，PARTIAL 标注）+ `TodaySection` 组件。
- [ ] T-U3-3 真实统一任务流集成 → BLOCKED（GAP-001），hook 默认 mock 源并明确标注。

## U4 — Mistakes

- [ ] T-U4-1 contract `mistake.ts` + adapter（canonical Mistake DTO → MistakeCardModel）+ tests。
- [ ] T-U4-2 `MistakeCard` + `MistakeFilter`（状态/知识点/来源/最近错误/复习入口）+ 空/错态。
- [ ] T-U4-3 `useMistakesModel`（listMistakes → adapt + retry）+ section 装配 + tests。

## U5 — Review（集成 BLOCKED_BY_WEEK2）

- [ ] T-U5-1 Review 展示 contract 扩展（queue item 复用 ReviewTask；评分展示仅 mock 标注）+ mock。
- [ ] T-U5-2 `ReviewSection` 组件（layout/queue/empty/error/partial）+ tests。
- [ ] T-U5-3 真实 ReviewItem 契约集成 → BLOCKED（DEPENDENCY-001），Week2 Gate 后重审。

## U6 — Questions

- [ ] T-U6-1 contract `question.ts` + adapter（Question DTO → QuestionCardModel，含 options/answer/result 展示态）+ tests。
- [ ] T-U6-2 `QuestionCard`（List/Detail/Practice Entry/Answer/Result/关联位）+ mock + tests。
- [ ] T-U6-3 attempt/practice 缺口 → GAP-006（只读展示，不建 mutation）。

## U7 — Knowledge

- [ ] T-U7-1 contract `knowledge.ts` + adapter（taxonomy/subjects/KP → KnowledgeNode，counts 可 null）+ tests。
- [ ] T-U7-2 `KnowledgeCard`（Subject/KP/学习状态/关联 Questions/Mistakes/Notes 位）+ mock + tests。

## U8 — Notes

- [ ] T-U8-1 contract `note-artifact.ts` + adapter（NoteDetail → NoteArtifact）+ tests。
- [ ] T-U8-2 `NotesSection`（list/detail/entry/relation 展示）+ mock + tests；editor 本体不动（Blocker 候选）。

## U9 — Analytics

- [ ] T-U9-1 contract `analytics.ts` + mock（含全 null “数据积累中”态）。
- [ ] T-U9-2 `AnalyticsSection` + `LearningTrend` + `MasteryIndicator`（null → 诚实空态）+ tests。

## U10 — Resources

- [ ] T-U10-1 contract `resource.ts` + adapter（attachments DTO → ResourceItem）+ `ResourcesSection` + mock + tests；缺 canonical domain → GAP-007。

## U11 — Settings

- [ ] T-U11-1 contract `settings.ts` + `SettingsSection`（学习相关展示型设置）+ mock + tests；Auth 不碰。

## U12 — Responsive

- [ ] T-U12-1 四断点（375/768/1024/1440）检查：navigation/sidebar/tables/cards/forms/dialogs/overflow/touch target/density；修复仅限 ui-v2 文件。
- [ ] T-U12-2 记录 Responsive 结果矩阵（PASS/PARTIAL + 证据）。

## U13 — Accessibility

- [ ] T-U13-1 全量 a11y 检查：keyboard/focus-visible/semantics/labels/dialog focus/contrast/disabled/loading/error；状态非唯颜色。
- [ ] T-U13-2 记录 Accessibility 结果矩阵。

## U14 — Integration

- [ ] T-U14-1 稳定契约 hooks 接线复核（dashboard/mistakes/questions/notes/knowledge）：API → Adapter → Contract → Component 链路断言；Mock 可识别可移除。
- [ ] T-U14-2 不稳定契约保持 MOCK/BLOCKED 标注复核。

## U15 — Final QA

- [ ] T-U15-1 route smoke（只读）/ critical interaction / states / retry / responsive / keyboard / API failure / unauthorized behavior / regression 清单执行。
- [ ] T-U15-2 admin/private 只读验证（G3 相关行为不断言 bypass，不触 Auth）。

## U16 — Final Gate

- [ ] T-U16-1 汇总 IMPLEMENTED/REVIEWED/VERIFIED/VALIDATED 证据，申请 Final Gate（不自批）。
