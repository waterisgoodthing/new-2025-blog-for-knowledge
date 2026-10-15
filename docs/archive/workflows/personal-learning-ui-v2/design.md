# Design — UI V2 Full Implementation

## 1. 分层架构（沿用 Foundation，不推翻）

```text
Backend DTO (read-only，本轨不碰；经 src/lib/api/* 读取)
      ↓
Adapter  (src/adapters/ui-v2/*，纯函数映射 + source 标注；缺字段 → null + estimated)
      ↓
UI Contract (src/contracts/ui-v2/*，UI-facing types；禁止反向推导 backend schema)
      ↓
Hook (src/features/ui-v2/* co-located，fetch → adapter → UiPageModel；credentials: 'include' 经 apiFetch)
      ↓
UI Component (src/components/ui-v2/*，仅展示 + 状态；禁止 import raw backend DTO)
      ↓
Mock (src/mocks/ui-v2/*，source: 'mock'，六态：normal/empty/loading/error/partial/overdue)
```

`src/features/ui-v2/` 为业务组装位（domain section 组件 + hooks + tests 同目录内聚）。

## 2. IA 落地策略（不迁移路由）

目标 IA 见 Foundation `UI_V2_INFORMATION_ARCHITECTURE.md`。本轨不新增顶层路由、
不修改现有页面与 `layout.tsx`（脏文件只读）。IA 落地形式：

- `src/components/ui-v2/navigation.ts`：Current Route → Proposed Section 的只读映射配置
  （学习/知识/分析/资料/设置分组），供新 App Shell 组件渲染，不改 sidebar。
- 各 domain section 组件以 props 接收数据，可在未来路由迁移时直接挂载。

任何重大 IA 修改进入 Tracker Decision Ledger（G0）。

## 3. 合约扩展（本轮新增）

Foundation 已有：`ReviewTask`、`MasteryScore`、`PageState`/`UiPageModel`。

本轮新增（全部 UI-facing，`source` 必填）：

| Contract | 文件 | 说明 |
|---|---|---|
| `StudyTask` | `study-task.ts` | Today 统一任务：id/title/kind/dueAt/priority/status/subject/source；kind 仅描述展示意图，不发明调度语义 |
| `MistakeCardModel` | `mistake.ts` | 列表/筛选/状态/知识点/来源/复习入口所需展示字段；判定语义不由 UI 发明 |
| `QuestionCardModel` | `question.ts` | 列表/详情/作答态/结果态/错题与知识点关联展示字段；评分语义不由 UI 发明 |
| `KnowledgeNode` | `knowledge.ts` | Subject / KnowledgePoint / 学习状态 / 关联计数（counts 可为 null → “数据积累中”） |
| `NoteArtifact` | `note-artifact.ts` | 笔记作为 Learning Knowledge Artifact 的展示字段 + 关联位 |
| `TrendPoint` / `AnalyticsModel` | `analytics.ts` | 趋势点与分析展示模型；数值缺失 → null，不估算 |
| `ResourceItem` | `resource.ts` | 附件/资料展示字段（以现有 attachments 契约为准） |
| `LearningSettings` | `settings.ts` | 与学习直接相关的展示型设置项；Auth 不在内 |
| `NavSection` / `NavItem` | `navigation.ts` | 导航配置类型（非组件） |

## 4. Adapter 策略

- 稳定契约（DashboardSummary、Mistake、Question、NoteDetail、Taxonomy）：
  `from-backend.ts` 扩展纯函数，unknown → contract，缺字段 → null + estimated。
- 不稳定/缺失契约（Today 统一任务流、Mastery 数值、Weakness Top3、Review 六档）：
  adapter 只做“明确标注的降级”（estimated/null），不伪造；集成态保持 MOCK/BLOCKED。
- Component 禁止 import `src/lib/api/*` 的 DTO 类型；Hook 负责 fetch+adapt。

## 5. 组件策略

复用优先级：existing stable → ui-v2 foundation → extend → new domain。
本轮新增 domain 组件（确有领域语义才建）：
`AppShell`、`AppSidebar`、`AppHeader`、`PageLayout`、`Breadcrumb`、
`StudyTaskCard`、`MistakeCard`、`QuestionCard`、`KnowledgeCard`、`WeaknessCard`、
`MasteryIndicator`、`DueBadge`、`DifficultyBadge`、`SubjectBadge`、`LearningTrend`、
`PageStateView`（LOADING/EMPTY/ERROR/PARTIAL/SUCCESS/RETRY 统一渲染）、
`TodaySection`、`DashboardSection`、`ReviewSection`（mock 态）、
`AnalyticsSection`、`KnowledgeSection`、`NotesSection`、`ResourcesSection`、
`SettingsSection`。

禁止 `Button2`/`CardNew` 类重复组件；Foundation Button/Card/Badge/Skeleton/
Progress/SectionHeader/PageHeader/ErrorState 直接复用。

## 6. 状态覆盖

核心展示组件必须覆盖 LOADING / EMPTY / ERROR / PARTIAL / SUCCESS；
网络型 hook 增加 RETRY；mutation 型（仅 Settings/Notes entry 等展示型提交态）
考虑 SUBMITTING / SUCCESS / FAILURE（不接真实 mutation，除稳定契约外）。

## 7. Design System

沿用 `--uiv2-*` additive token（`src/components/ui-v2/tokens.css`，
按需扩展）；禁止页面级随机色/圆角/间距；全局 theme 零修改（改则先记 tasks.md）。
文字对比 ≥4.5:1；状态不唯颜色表达（badge 必须带文字）。

## 8. 测试策略

- 单元：adapters（state mapping 全覆盖）、contracts 不变量无测试必要。
- 组件：domain card + PageStateView 六态/error-retry/keyboard/a11y 属性。
- Hook：以 mock fetch 测 LOADING→SUCCESS/ERROR/RETRY 转移。
- 集成：adapter + mock 数据装配 section 组件冒烟。
- 路由冒烟：只读检查现有路由文件存在性与导出，不启动破坏性操作。
- jsdom 不作为真实浏览器行为证据；browser validation 以 build + 静态可访问性
  断言 + 响应式 CSS 契约为准，如实标注 NOT_VERIFIED 项。

## 9. 风险与 STOP

- Review 集成：BLOCKED_BY_WEEK2（PR-06/07/08 未 PASS）→ 只做 UI/Mock/Contract/Test。
- 脏文件/Week2 文件/后端文件需改 → STOP + Blocker + 继续独立任务。
- G3 触发内容 → STOP。关键路径全阻塞才整体 STOP。
