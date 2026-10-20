# Batch 0 文档一致性审查

## 审查范围

- `docs/specs/mvp-rebuild/batch-0-docs-freeze/spec.md`
- `AGENTS.md` 中的架构、权限和 workflow 规则
- `docs/architecture/mvp-scope.md`
- `docs/architecture/README.md`
- `docs/architecture/review-system.md`

本审查只判断文档范围是否一致，不判断后续页面、API、表或迁移是否已经实现。

## 结论

**通过，Batch 0 的文档冻结目标已达到。**

三份架构文档现在一致地把第一版定义为手工学习闭环；AI、OCR、Capture Router、
BKT、完整练习、复杂容量控制等均不再被写成第一版核心要求。候选独立 question /
mistake 模型明确处于待设计、待迁移状态。

## 逐项核对

| 冻结项 | 结果 | 证据 |
| --- | --- | --- |
| `mvp-scope.md` 存在 | 通过 | 已建立权威范围入口 |
| 手工学习闭环 | 通过 | 范围文档和架构首页链路一致 |
| AI / OCR 后置 | 通过 | 核心流程不依赖；Batch 6 仅占位 |
| BKT 后置 | 通过 | Review 文档单列后置能力 |
| 完整练习后置 | 通过 | MVP 主链路不含 practice session / attempt |
| 首页低密度 | 通过 | 范围文档明确公开首页职责 |
| `/manage` 高密度 | 通过 | 范围文档明确管理工作台职责 |
| 候选页面 | 通过 | 公开层与管理层分别列出 |
| 候选数据表 | 通过 | 按 Batch 2 至 Batch 5 列出并标注待设计 |
| 8 批顺序 | 通过 | Batch 0 至 Batch 7 固定顺序和门禁清楚 |
| 当前错题模型 | 通过 | 明确仍为 `Note(type="mistake")` |
| 公开读取权限 | 通过 | 公开博客、笔记、错题不封闭 |
| 管理操作权限 | 通过 | 前端保护与后端安全边界分离 |

## 审查中发现并修正

### 1. 架构首页第一版范围过大

原文把单文件 OCR/Capture、练习闭环和容量上限写入第一版。已改为：

- 核心闭环完全手工。
- 附件属于 Batch 5。
- AI/OCR 在 Batch 6 只占位。
- Review 只使用简单间隔或简单 SM-2。

### 2. Review 提交混入 mastery event

原文要求每次提交同时写 mastery event，与 BKT 后置冲突。现已拆为：

- MVP 事务：写 `review_record`、计算简单间隔、更新 `next_review_at`。
- 后续事务：只有掌握度阶段获批后才写 mastery event。

### 3. Review 第一版混入复杂容量控制

原文把容量控制列入第一版。现已改为长期建议值，不再是 MVP 默认实现要求。

### 4. Review 目标类型范围含糊

目标架构允许 mistake、knowledge point、question、note，但 MVP 只需要 active mistake。
现已明确：第一版只启用 `mistake`，其他目标类型后置。

## 待确认但不阻塞 Batch 0

### RISK-B0-01：独立 question 模型

- 状态：待 Batch 3 设计。
- 原因：当前系统以 Note 为中心，独立 question 模型尚未完成共存、迁移和回滚设计。
- 约束：不得因为架构文档列出 `questions` 就假设表和 API 已存在。

### RISK-B0-02：独立 mistake 模型

- 状态：待 Batch 4 设计。
- 原因：当前错题仍是 `Note(type="mistake")`，公开详情复用 `/notes/[slug]`。
- 约束：不得假设已有 `mistakes` 表或 `/api/mistakes`，不得破坏公开读取。

### RISK-B0-03：候选表最终命名与关系

- 状态：待 Batch 2 至 Batch 5 各自设计。
- 原因：Batch 0 只冻结职责和顺序，不批准具体 schema、外键、索引或迁移。
- 约束：每批必须保持前端类型、后端 schema、模型和迁移同步。

### RISK-B0-04：既有长期架构文档仍描述全量蓝图

- 状态：已缓解。
- 原因：其他架构文档仍会提到 AI、OCR、练习和 BKT。
- 缓解：架构首页已声明 MVP 以 `mvp-scope.md` 为权威；后续批次不能仅凭长期文档扩大范围。

## 是否允许进入验收

允许。上述待确认项属于后续批次的设计输入，不阻塞 Batch 0 文档冻结。
进入 Batch 1 仍需完成本批 validation、handoff，并由用户明确确认 Batch 0 通过。
