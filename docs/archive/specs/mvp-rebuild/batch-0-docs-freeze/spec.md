# Batch 0：文档冻结与实现约束

## 目标

在任何 MVP 业务代码开始前，冻结第一版范围、信息密度原则、数据边界和后续 7 批
执行边界。

## 背景

现有架构文档覆盖 AI、OCR、BKT、练习、附件等长期能力，容易被误读为第一版必须
全量实现。本批只修订和冻结文档，不写代码。

## 任务范围

1. 新增或确认 `docs/architecture/mvp-scope.md`。
2. 修正 `docs/architecture/review-system.md` 中 BKT 的后置表述。
3. 明确第一版不做 AI、OCR、BKT 和完整练习系统。
4. 明确公开首页低密度、`/manage` 高密度。
5. 明确第一批数据表、页面和验收标准。
6. 明确 Batch 1 至 Batch 7 的边界。
7. 对未来独立 question、mistake 等模型与当前 `Note` 模型的关系标注“待确认”，
   不在文档冻结阶段擅自决定迁移。

## 允许修改范围

- 本批对应的 `docs/workflows/<task-name>/`。
- `docs/architecture/mvp-scope.md`。
- `docs/architecture/review-system.md`。
- 为保持架构索引一致而确有必要的 `docs/architecture/README.md`。
- 本批 `checklist.md` 与 `handoff.md`。

## 禁止事项

- 不改业务代码、样式或配置。
- 不建表、不写 API、不写数据库迁移。
- 不改 UI。
- 不提前执行 Batch 1 至 Batch 7。

## 涉及页面

仅在文档中定义 `/` 与 `/manage` 的信息密度原则，不修改任何页面。

## 涉及数据表

不修改数据表。只在 `mvp-scope.md` 中记录第一版候选表和与现有模型的待确认关系。

## 验收标准

1. `mvp-scope.md` 存在。
2. 第一版目标明确为手工学习闭环。
3. 暂缓清单清楚。
4. `review-system.md` 明确 BKT 后置。
5. 首页低密度、`/manage` 高密度原则明确。
6. 后续批次不会被误解为一次性全量实现。
7. 与现有架构冲突的模型项被明确标记，未暗示已经完成迁移。

## 非目标

任何业务实现、数据迁移、页面原型、API 合同落地或依赖调整。

## 完成后 handoff 要求

列出修订文档、冻结结论、待确认的模型冲突、未完成项、风险以及 Batch 1 的前置条件，
并等待用户明确确认。
