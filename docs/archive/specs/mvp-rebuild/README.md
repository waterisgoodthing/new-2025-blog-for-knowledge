# MVP Rebuild Specs

## 用途

本任务夹把 MVP 重构锁定为 8 个可独立执行、验收和移交的批次。后续 Codex
只能执行当前已获用户批准的批次，不得跨批实现或顺手修复。

## MVP 目标

第一版只跑通手工学习闭环：

```text
科目
  ↓
知识点
  ↓
题目草稿
  ↓
人工审核
  ↓
正式题库
  ↓
错题草稿
  ↓
正式错题
  ↓
简单复习项
  ↓
复习记录
```

第一版不实现完整 AI、完整 OCR、Capture Router 自动分流、BKT、完整练习系统、
真实后台任务队列、统计报告、搜索索引、对象存储或云部署。

## 8 批总览

| 批次 | 核心目标 | 前置条件 |
| --- | --- | --- |
| Batch 0 | 文档冻结与实现约束 | 本任务夹获批准 |
| Batch 1 | UI 壳层与首页轻量改造 | Batch 0 验收通过 |
| Batch 2 | 科目 / 知识点基础 | Batch 1 验收通过 |
| Batch 3 | 题目草稿 / 草稿审核 / 题库 | Batch 2 验收通过 |
| Batch 4 | 错题草稿 / 错题系统 / 简单复习 | Batch 3 验收通过 |
| Batch 5 | 附件基础系统 | Batch 4 验收通过 |
| Batch 6 | AI / OCR 预留接口与占位 | Batch 5 验收通过 |
| Batch 7 | 体验收口、旧路由兼容、数据质量 | Batch 6 验收通过 |

依赖链固定为：

```text
Batch 0 → Batch 1 → Batch 2 → Batch 3
        → Batch 4 → Batch 5 → Batch 6 → Batch 7
```

## 后续工作方式

1. 只打开当前批次的 `spec.md`、`checklist.md` 和 `handoff.md`。
2. 实现前按仓库 `AGENTS.md` 建立或复用对应 workflow，并获得 tasks 明确批准。
3. 只修改 `spec.md` 允许的范围。
4. 每完成一项立即更新该批 `checklist.md`。
5. 发现跨批问题只写入 `handoff.md`，不顺手修复。
6. 完成验证并填写 handoff 后，等待用户验收。

## 用户确认机制

用户必须在对话中明确确认当前批通过。仅完成代码、构建成功、清单勾选或代理自评，
均不等于用户确认。没有用户确认不得打开下一批实施范围。

完整门禁见 [execution-rules.md](./execution-rules.md)。
