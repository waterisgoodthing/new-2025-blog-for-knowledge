# UI Technical Specification

**项目**：2025-blog-public  
**版本基线**：Git HEAD `700f345` (2026-10-15)  
**审计日期**：2026-10-15  
**文档目标**：为 UI 系统重构（visual-system-consolidation）提供完整现状、目标规范、差距分析和执行路线图

---

## 核心发现摘要

### 关键指标

| 维度 | 现状 | 目标 | 状态 |
|------|------|------|------|
| **页面数量** | 53 页 | - | ✅ 已盘点 |
| **组件总数** | 约 120+ | - | ✅ 已盘点 |
| **UI V2 组件** | 15 个（完整实现） | - | ⚠️ 零接入 |
| **Token 系统** | 3 套并存 | 1 套统一 | ❌ 需合并 |
| **Navigation** | VerticalNav + MobileNav | Glass + Sidebar + Drawer | ❌ 需重构 |
| **Overlay 系统** | Modal + Drawer + ContextMenu（独立实现） | 统一 accessibility 系统 | ❌ 需标准化 |
| **响应式覆盖** | 部分组件 | 全覆盖 | ⚠️ 需补充 |

### 优先级 P0 问题

1. **Token 系统分裂**（P0）
   - Legacy（`site-content.json`，8 个变量）
   - theme.css（10 个 Tailwind token）
   - UI V2（`ui-v2/tokens.css`，完整系统）
   - **影响**：样式维护成本高，设计一致性无法保证

2. **UI V2 零接入**（P0）
   - 15 个组件已实现（Card/Button/Badge/AppShell/PageHeader...）
   - 测试覆盖完整（2 个测试文件）
   - **但路由使用率 = 0**
   - **影响**：前期投入未释放价值，组件系统化受阻

3. **Navigation 架构不符合设计目标**（P0）
   - 现状：Desktop 用 VerticalNav（左侧悬浮，展开/收缩）
   - 目标：Public 用 glass topbar，Admin 用 collapsible sidebar
   - **差距**：需完全重构 navigation 系统

4. **Overlay 职责模糊**（P0）
   - Modal、Drawer、ContextMenu 各自实现
   - 无统一焦点管理和键盘导航
   - **影响**：无障碍问题、交互不一致

---

## 文档结构

```
ui-technical-specification/
├── README.md ························ 本文件（总览）
├── 00-meta/ ························· 元数据层
│   ├── evidence-baseline.md ········· 证据等级和验证方法
│   ├── version-baseline.md ·········· Git/依赖版本基线
│   └── glossary.md ·················· 术语表
├── 01-as-is/ ························ 现状层（As-Is）
│   ├── tech-stack.md ················ 技术栈清单
│   ├── ui-inventory.md ·············· UI 资产全量清单
│   ├── token-systems.md ············· 3 套 Token 系统对比
│   ├── dependency-graph.md ·········· 组件/页面/API 依赖图
│   └── technical-debt.md ············ 技术债务清单
├── 02-to-be/ ························ 规范层（To-Be）
│   ├── design-foundations.md ········ 设计基础规范
│   ├── component-system.md ·········· 组件系统规范
│   ├── navigation-system.md ········· Navigation 规范
│   ├── overlay-system.md ············ Overlay 规范
│   ├── responsive-system.md ········· 响应式规范
│   ├── accessibility.md ············· 无障碍基线
│   └── engineering-standards.md ····· 前端工程规范
├── 03-gap-analysis/ ················· 差距层（Gap）
│   └── as-is-vs-to-be.md ············ 现状与目标对照表
└── 04-execution/ ···················· 执行层（Execution）
    ├── refactoring-roadmap.md ······· 重构路线图
    ├── task-registry.md ············· 任务清单（17 任务）
    ├── acceptance-criteria.md ······· 验收标准
    └── governance.md ················ 变更治理流程
```

---

## 阅读指南

### 如果你是...

**产品/设计**：先读 `02-to-be/design-foundations.md`，了解视觉目标  
**前端开发**：先读 `01-as-is/ui-inventory.md` + `03-gap-analysis/as-is-vs-to-be.md`  
**技术负责人**：先读本文件 + `04-execution/refactoring-roadmap.md`  
**AI Agent**：先读 `04-execution/task-registry.md`，选择可执行任务

### 推荐路径

1. **理解现状**：`01-as-is/*`（技术栈、资产清单、Token 对比、依赖图、技术债务）
2. **明确目标**：`02-to-be/*`（设计基础、组件规范、Navigation、Overlay、响应式、无障碍）
3. **分析差距**：`03-gap-analysis/as-is-vs-to-be.md`
4. **执行重构**：`04-execution/*`（路线图、任务清单、验收标准）

---

## 证据等级说明

本文档所有现状事实均标注证据等级：

| 等级 | 说明 | 示例 |
|------|------|------|
| **L1 — Verified** | 代码扫描 + 人工核实 | 页面数量 = 53（`find src/app -name "page.tsx"`） |
| **L2 — Static** | 静态分析，未运行时验证 | 组件依赖图（import 关系） |
| **L3 — Inferred** | 从代码推断，需运行时验证 | 响应式覆盖情况 |
| **L4 — Pending** | 待核实，标注来源 | 某些 API 契约（需后端确认） |

所有 L3/L4 事实会在对应章节标注 `[需验证]`。

---

## 快速决策

### 最优执行路径

**Phase 1（本轮，2-4 天）**：
1. VSC-02：Token 系统冻结（合并 3 套 → 1 套统一双表面系统）
2. VSC-02 验证：Demo 页验证（`/dev/tokens`）

**Phase 2（下轮，5-7 天）**：
1. VSC-03-05：Overlay 加固（统一 Modal/Drawer/ContextMenu）
2. VSC-06-08：Context Actions（ContextMenu 规范化）
3. 试点接入：选 1-2 页接入 UI V2（Dashboard 或 Notes）

**Phase 3（后续）**：
1. VSC-09-13：Navigation 重构（glass topbar + collapsible sidebar + drawer）
2. 扩展接入：剩余页面逐步迁移
3. VSC-14-17：最终验收

---

## 相关文档

- **设计目标**：`docs/current/workflows/visual-system-consolidation/design.md`
- **任务规格**：`docs/current/workflows/visual-system-consolidation/tasks.md`
- **参考图**：`docs/current/workflows/visual-system-consolidation/assets/*.png`
- **AGENTS.md**：`/AGENTS.md`（工程约束和门禁）

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-10-15 | 1.0.0 | 初始版本（基于 Git HEAD 700f345 审计） |

---

**下一步**：阅读 `01-as-is/ui-inventory.md` 了解完整资产清单。
