# MVP 第一版范围冻结

> 状态：Batch 0 已冻结的实现边界。
> 本文定义 8 批 MVP 的执行上限，不表示候选页面、数据表或 API 已经实现。
> 长期目标架构继续保留，但不得覆盖本文的批次顺序与非目标。

## 1. 第一版目标

第一版只跑通可人工操作、可人工审核、可独立验证的学习闭环：

```text
科目
  ↓
知识点
  ↓
题目草稿
  ↓
人工审核
  ↓
正式题目
  ↓
错题草稿
  ↓
人工审核
  ↓
正式错题
  ↓
简单复习项
  ↓
复习记录
```

AI、OCR 和自动路由不能成为创建、审核、保存或复习的前置条件。所有核心步骤必须在
这些能力未启用时仍可完成。

## 2. 三种状态必须区分

### 当前实现

仓库当前同时存在 Next.js 公开内容系统与 FastAPI/PostgreSQL 个人知识后端。
错题当前仍是 `Note(type="mistake")`，使用 Note 模型与 `/api/notes` 合同；公开错题
详情当前复用 `/notes/[slug]`。不能假设已经存在独立 `mistakes` 表或
`/api/mistakes`。

### MVP 候选

本文列出的新页面、表和数据关系是对应批次的设计输入。只有在该批 workflow、
requirements、design、tasks 获用户批准并完成迁移与验证后，才能称为已实现。

### 长期目标

完整 AI、OCR、Capture Router、BKT、练习系统、任务队列、搜索、统计、对象存储和
云部署属于长期蓝图或后续迭代，不是本 MVP 的隐含交付项。

## 3. 固定批次顺序

```text
Batch 0：文档冻结与实现约束
  ↓
Batch 1：UI 壳层与首页轻量改造
  ↓
Batch 2：科目 / 知识点基础
  ↓
Batch 3：题目草稿 / 草稿审核 / 题库
  ↓
Batch 4：错题草稿 / 错题系统 / 简单复习
  ↓
Batch 5：附件基础系统
  ↓
Batch 6：AI / OCR 预留接口与占位
  ↓
Batch 7：体验收口、旧路由兼容、数据质量
```

禁止跳批、并行执行多批或把后续批次顺手并入当前批。当前批 checklist、handoff、
验证和用户确认全部完成后，才能进入下一批。

## 4. 各批实现边界

### Batch 0：文档冻结

只冻结范围、Review MVP、页面密度、候选模型和执行门禁，不改业务代码。

### Batch 1：UI 壳层

只建立公开首页轻入口与统一 `/manage` 壳层。使用静态占位，不接真实业务数据，
不改数据库。

### Batch 2：科目与知识点

设计并实现科目、章节、知识点的基础 CRUD 和选择器。知识图谱、AI 建议、BKT 与
复杂统计不属于本批。

### Batch 3：题目草稿与题库

设计并实现手工题目草稿、人工审核、正式题目与 manual 来源。AI 生成、OCR、自动
分流、批量审核、复杂去重和完整练习不属于本批。

独立 question 模型如何与当前 Note 架构共存或迁移，必须在 Batch 3 单独设计并审批。

### Batch 4：错题与简单复习

设计并实现错题草稿、人工确认、正式错题、简单复习项和复习记录。BKT、自动判错、
复杂容量控制、题库抽题检测和完整练习不属于本批。

独立 mistake 模型如何替代或兼容当前 `Note(type="mistake")`，必须在 Batch 4 单独
设计、迁移、回滚并审批；不得静默切换。

### Batch 5：附件基础

实现管理员本地上传、私有附件、元数据和通用关联。不做 OCR、PDF 自动解析、复杂
缩略图、对象存储、R2 或云部署。

### Batch 6：AI / OCR 占位

只提供清楚标注“第一版暂未启用”的管理端占位和附件 OCR 状态。不得接入真实模型、
OCR、Prompt 管理、调用持久化或任务队列。

### Batch 7：兼容与收口

处理旧入口、小范围状态收口、基础校验、危险操作确认、死链接和本地试运行说明。
不大规模重构公开站，不删除或自动迁移旧数据，不引入云部署。

## 5. 候选页面

### 公开层

- `/`
- `/mistakes`
- `/notes`
- `/notes/[slug]`
- `/blog`
- `/blog/[slug]`

这些页面保持公开读取。未登录用户只能读取已发布、未隐藏内容，不能看到编辑、删除、
AI、上传或复习提交操作。

### 管理层

- `/manage`
- `/manage/dashboard`
- `/manage/drafts`
- `/manage/drafts/[id]`
- `/manage/questions`
- `/manage/questions/[id]`
- `/manage/mistakes`
- `/manage/mistakes/[id]`
- `/manage/review`
- `/manage/attachments`
- `/manage/attachments/[id]`
- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/knowledge-points/[id]`
- `/manage/ai`
- `/manage/jobs`
- `/manage/settings`

管理页面必须使用 `AuthGate` 或等价的页面级保护；真实写入、上传、AI 和复习安全边界
必须继续由后端管理员鉴权提供。

## 6. 页面信息密度

### 公开首页 `/`

- 青春柔和、浅蓝绿色、玻璃卡片、低密度。
- 继续承担公开展示与轻导航，不改造成 Dashboard。
- 学习相关只提供待复习、待审核、进入学习空间、上传资料等轻入口。
- 不展示高密度表格、复杂统计图或完整管理表单。

### 管理台 `/manage`

- 高密度但可读的管理员工作台。
- 使用统一 Sidebar、Topbar 和 PageHeader。
- CRUD、审核、复习、附件等操作只在管理层承载。
- 公开首页与管理台不得共享会泄露管理员操作的默认状态。

具体视觉和组件实现属于 Batch 1。

## 7. 候选数据表

以下均为候选目标结构，不表示当前存在：

| 批次 | 候选表 | 状态与限制 |
| --- | --- | --- |
| Batch 2 | `subjects`、`chapters`、`knowledge_points`、`knowledge_point_links` | 待设计、待迁移 |
| Batch 3 | `draft_items`、`question_drafts`、`questions`、`question_sources` | 待确认与 Note 的共存或迁移 |
| Batch 4 | `mistake_drafts`、`mistakes`、`review_items`、`review_records` | 待确认与 `Note(type="mistake")` 的兼容 |
| Batch 5 | `attachments`、`attachment_links` | 待设计；附件默认 private |

可选 `tags`、`taggings` 不自动进入第一版；只有 Batch 2 证明为核心闭环必需并重新获批
后才能纳入。

本 MVP 不建立：

- `knowledge_mastery`
- `knowledge_mastery_events`
- `bkt_parameters`
- 完整 `ai_model_profiles`
- `ai_runs`
- `ocr_jobs`
- 搜索索引、统计仓库或对象存储专用表

## 8. Review MVP 冻结

第一版复习只要求：

```text
active mistake
  ↓
review_item
  ↓
固定间隔或简单 SM-2
  ↓
review_record
  ↓
更新 review_item.next_review_at
```

第一版不要求 BKT、掌握度状态、mastery events、复杂容量控制、强化练习或 AI 调度。
详细边界见 [Review System](./review-system.md)。

## 9. 明确暂缓

- 完整 AI 与真实模型接入。
- 完整 OCR 与 PDF 自动解析。
- Capture Router 自动分流。
- BKT 与掌握度事件。
- 完整练习、自动判错、抽题和练习报告。
- 后台任务真实队列。
- 搜索索引。
- 统计与报告。
- 对象存储与 Cloudflare R2。
- 云部署。
- 复杂知识图谱。
- 多用户权限分级。
- 大规模批审或无人工确认自动入库。

## 10. 权限底线

1. 公开博客、笔记与错题读取不能被管理重构封闭。
2. 创建、编辑、删除、上传、AI 和复习操作必须使用后端管理员鉴权。
3. `AuthGate` 只负责页面体验，不能替代后端安全边界。
4. 公开页面不得反复请求管理员接口产生 401/403 噪音。
5. 生产环境不得启用 `AUTH_BYPASS=true` 与 `AUTH_BYPASS_ALLOW=true` 的组合。

## 11. 变更与验收

每批必须：

1. 建立或复用独立 workflow。
2. 完成 requirements、design 和 tasks。
3. 获得用户对 tasks 的明确批准。
4. 只执行当前批范围。
5. 逐项更新 checklist。
6. 记录验证、失败、风险和 handoff。
7. 获得用户对当前批的明确验收。

如实现发现范围或模型必须变化，先更新本文件或对应设计与任务清单；若范围扩大，
必须重新请求用户批准。
