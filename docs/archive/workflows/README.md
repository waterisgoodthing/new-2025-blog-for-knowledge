# docs/workflows/ — 历史与流程记录

> **2026-10-15 顶层说明：本目录是历史/流程快照，不作当前事实或执行授权。**

本目录下的各子目录记录历史上不同阶段的**工作流、审计、验收、证据与计划**。它们保留当时的结论与计数，**不滚动改判**。

## 阅读约定
- 本目录内容**不代表当前实现或当前运行状态**；一条"PASS/完成"是该时点的记录，不等于现在仍然成立。
- 需要判断"当前是否这样"时，以现行入口为准：
  - 当前架构：`docs/architecture/ARCHITECTURE_CURRENT.md`
  - 当前状态：`docs/PROJECT_STATUS.md`
  - 当前路线：`docs/ROADMAP.md`
  - 缺陷证据：`docs/audits/ARCHITECTURE_AUDIT.md`
  - 文档索引：`docs/DOCUMENTATION_INDEX.md`
- 测试计数（如 530、121）为**历史时点**数值；当前数值以后端 `pytest` 与前端 `vitest` 实跑为准。
- 计划类内容（tasks/requirements/design）通常**不是实施授权**；执行需按 `AGENTS.md` 与 `agents/gates.md` 单独批准。

## 权威层级（一句话）
**现行入口（`docs/` 顶层 + `docs/architecture` 的 CURRENT + `docs/audits`）> 目标/阶段设计（已标注） > 本目录的历史工作流。**
