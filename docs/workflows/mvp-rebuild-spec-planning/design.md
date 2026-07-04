# 设计文档：MVP 重构 Spec 任务夹

## 1. 设计目标

用一套可审查、可顺序推进的文档结构约束后续 MVP 重构，避免跨批实现、
顺手修复和一次性改造全量系统。

## 2. 文档架构

```text
docs/specs/mvp-rebuild/
  README.md
  execution-rules.md
  batch-0-docs-freeze/
  batch-1-ui-shell/
  batch-2-subject-taxonomy/
  batch-3-drafts-question-bank/
  batch-4-mistakes-review/
  batch-5-attachments/
  batch-6-ai-ocr-placeholders/
  batch-7-polish-compatibility/
```

每个批次目录固定包含：

```text
spec.md
checklist.md
handoff.md
```

## 3. 执行状态设计

批次状态只按以下顺序推进：

```text
未开始 -> 执行中 -> 待验收 -> 用户已确认 -> 下一批
```

进入下一批必须同时满足：

1. 当前批目标完成。
2. checklist 全部完成或明确标记阻塞、跳过、延期及原因。
3. handoff 填写完成内容、修改文件、未完成事项、风险和下一批前置条件。
4. 用户在对话中明确确认当前批通过。

## 4. 内容设计

### 全局 README

说明 MVP 手工学习闭环、8 批总览、依赖关系、工作方式和用户确认机制。

### execution-rules

定义禁止跳批、禁止跨批、问题只记录不顺手修复，以及第一版明确不做的能力。

### spec

每批固定包含目标、背景、任务范围、允许修改范围、禁止事项、页面、数据表、
验收标准、非目标和 handoff 要求。

### checklist

将 spec 的任务与验收条件转换为可逐项勾选的执行清单，不预先宣称完成。

### handoff

使用空白模板记录实际执行证据；默认“用户已确认”保持未勾选。

## 5. 架构边界

本轮只生成任务治理文档，不实现任何页面、API、模型、迁移、权限或数据流。
Batch 0 中提到的 `mvp-scope.md` 与 `review-system.md` 修订，是未来执行内容，
不在本轮创建 spec 时提前修改。

## 6. 冲突处理

若附件内容与仓库当前架构不一致，只在对应 spec 中标注“待确认”“后续批次处理”
或“不属于本批”，不以本轮文档创建为理由修改代码或架构实现。

## 7. 验证设计

完成后仅做静态文档验证：

- 核对目录与文件数量。
- 核对 8 批顺序及命名。
- 核对每个文件的必需章节。
- 核对每批边界、禁止事项和验收标准。
- 核对 Git diff 仅落在批准目录，且无业务代码变化。

不运行安装、迁移、服务、构建或全项目格式化。
