# 任务清单：Batch 0 文档冻结与实现约束

> 状态：等待用户明确批准本任务清单。批准前不得修改架构正文。

## P0-01 创建 MVP 权威范围文档

- [x] 创建 `docs/architecture/mvp-scope.md`。
- 来源需求：REQ-B0-01、REQ-B0-03、REQ-B0-04、REQ-B0-05
- 涉及文件：`docs/architecture/mvp-scope.md`
- 修改内容：写入手工学习闭环、8 批顺序、候选页面、候选表、UI 密度、暂缓清单、
  权限底线、当前实现差异和变更门禁。
- 完成标准：文档明确区分当前实现、MVP 候选和长期目标。
- 验证方式：章节、关键词、顺序和冲突标记检查。
- 风险说明：候选表不能被写成已存在或已批准迁移。

## P0-02 冻结 Review MVP

- [x] 修订 `docs/architecture/review-system.md`。
- 来源需求：REQ-B0-02
- 涉及文件：`docs/architecture/review-system.md`
- 修改内容：将简单复习与 BKT、mastery events、复杂容量控制彻底分层；修正 MVP
  提交事务要求。
- 完成标准：MVP 只依赖 review item、review record 和 `next_review_at`，不强制
  BKT 或 mastery event。
- 验证方式：对 BKT、mastery、容量控制和第一版范围做语义检查。
- 风险说明：不得删除长期目标，只需明确其后置状态。

## P0-03 同步架构入口与第一版摘要

- [x] 更新 `docs/architecture/README.md`。
- 来源需求：REQ-B0-01、REQ-B0-03、REQ-B0-05
- 涉及文件：`docs/architecture/README.md`
- 修改内容：增加 MVP 范围导航；将第一版摘要和主链路同步为手工闭环；保留长期蓝图。
- 完成标准：首页不再将 OCR/Capture、完整练习或 BKT 写成第一版承诺。
- 验证方式：链接、第一版摘要、主链路和长期状态说明检查。
- 风险说明：只做范围同步，不重写其他架构文档。

## P0-04 审核冻结文档一致性

- [x] 创建本 workflow 的 `audit.md`。
- 来源需求：REQ-B0-01 至 REQ-B0-05
- 涉及文件：本批三个架构文档与 `audit.md`
- 修改内容：交叉检查范围、批次、页面、表、权限和后置能力是否一致。
- 完成标准：所有冲突有结论；无法确认项明确进入后续批次。
- 验证方式：逐项对照 Batch 0 spec 和 AGENTS 权限规则。
- 风险说明：审查结论必须区分“已冻结”和“待确认”。

## P0-05 验证并完成 Batch 0 移交

- [x] 创建本 workflow 的 `validation.md`。
- [x] 更新 Batch 0 `checklist.md`。
- [x] 填写 Batch 0 `handoff.md`，但不代替用户勾选确认项。
- [x] 核对本轮补丁只包含本批允许文档；既存未跟踪目录的 Git 基线限制已记录。
- 来源需求：全部
- 涉及文件：workflow 验证文件、Batch 0 checklist 与 handoff
- 修改内容：记录静态验证、修改文件、未完成事项、风险和 Batch 1 前置条件。
- 完成标准：Batch 0 进入“待用户验收”，不自行进入 Batch 1。
- 验证方式：`rg`、`git diff --check`、`git status --short` 与文件清单。
- 风险说明：工作树已有大量用户改动，必须与本批修改严格区分。

## 执行顺序

严格按 P0-01 → P0-02 → P0-03 → P0-04 → P0-05 执行。每完成一项立即更新本文件，
不得最后批量回填。

## 审批记录

- [x] 用户已明确批准执行本任务清单（2026-07-02）。
