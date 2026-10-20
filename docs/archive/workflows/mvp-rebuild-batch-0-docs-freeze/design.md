# 设计文档：Batch 0 文档冻结

## 1. 设计目标

建立一个明确区分“当前实现”“MVP 批次目标”“长期目标架构”的范围文档，避免后续
Codex 将长期蓝图一次性实现。

## 2. 当前差异

### 架构首页范围偏大

`docs/architecture/README.md` 当前把以下内容写入“第一版统一范围”：

- 图片与单个 PDF 上传。
- 单文件 OCR/Capture。
- 不依赖 AI 的练习—错题—复习闭环。
- 简单 SM-2 与容量上限。

Batch 0 的已批准 spec 则要求 MVP 第一版不做完整 AI、OCR、BKT、完整练习系统；
附件、AI/OCR 还分别被安排到 Batch 5 和 Batch 6。架构首页必须改为与 8 批顺序一致，
并避免把长期蓝图写成当前承诺。

### Review 规则仍混合长期能力

`review-system.md` 已写“BKT 与掌握度事件明确后置”，但同时存在：

- 职责段将 BKT、SM-2、优先队列、容量控制并列为建议方案。
- 提交规则要求每次写 mastery event。
- 第一版范围仍包含容量控制。

冻结后应将 MVP 复习限定为：

```text
active 错题 → review_item → 简单间隔 / 简单 SM-2
           → review_record → 更新 next_review_at
```

不得要求 `knowledge_mastery`、mastery event、BKT 或复杂容量控制。

## 3. `mvp-scope.md` 结构

新文档应包含：

1. 文档状态和权威性。
2. 第一版手工学习闭环。
3. 当前实现与目标模型的区别。
4. Batch 0 至 Batch 7 的范围和依赖。
5. 第一版候选页面。
6. 第一版候选表及其“候选、待设计、待迁移”状态。
7. 公开首页低密度、`/manage` 高密度原则。
8. 明确暂缓清单。
9. 权限底线。
10. 验收与变更控制。

## 4. 数据边界设计

候选表只表达后续批次可能采用的目标结构，不代表已经存在或已经批准迁移：

- Batch 2：`subjects`、`chapters`、`knowledge_points`、
  `knowledge_point_links`
- Batch 3：`draft_items`、`question_drafts`、`questions`、
  `question_sources`
- Batch 4：`mistake_drafts`、`mistakes`、`review_items`、
  `review_records`
- Batch 5：`attachments`、`attachment_links`

必须醒目标注：当前错题仍是 `Note(type="mistake")`，读取与写入仍走现有 Note 合同；
独立 question/mistake 模型要在对应批次单独完成架构设计、迁移设计和用户审批。

## 5. 页面密度设计

- `/`：公开、青春柔和、浅蓝绿色、玻璃卡片、低密度；只提供轻入口和少量状态。
- `/manage`：管理员保护的高密度工作台；承载 CRUD、审核、复习、附件等操作。
- 公开博客、笔记和错题读取不能因管理工作台建设而封闭。

## 6. Review 冻结设计

将文档分为 MVP 与长期目标：

- MVP：`review_items`、`review_records`、简单固定间隔或简单 SM-2、
  `next_review_at`。
- 后置：BKT、掌握度表与事件、知识点强化、复杂容量控制、题库抽题检测、
  AI 改计划。

复习提交的 MVP 事务只要求写 review record 并更新 review item；mastery event
仅在未来 BKT/掌握度阶段启用。

## 7. 索引同步

`docs/architecture/README.md` 只做两类修改：

1. 增加 `mvp-scope.md` 导航入口。
2. 将“第一版统一范围”和主链路同步到冻结后的手工 MVP。

长期目标架构内容继续保留，但必须明确不等于当前批次承诺。

## 8. 验证设计

- 检查必需章节、8 批顺序、候选表和页面。
- 检查 AI、OCR、BKT、完整练习均明确后置。
- 检查 Review MVP 不再强制 mastery event 或复杂容量控制。
- 检查当前 `Note(type="mistake")` 事实和待迁移标记。
- 检查 Git diff 只落在本批允许范围。
- 不运行代码构建、服务、迁移或浏览器验收。
