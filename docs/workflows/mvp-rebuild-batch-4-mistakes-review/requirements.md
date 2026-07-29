# 需求文档：Batch 4 错题与简单复习

## 背景与角色

Batch 3 已建立稳定 Question。个人管理员需要将值得复盘的 Question 转为错题草稿，
人工确认后进入私有错题和简单复习。未登录访客仍只能读取旧系统中已发布、未隐藏的
Note 错题，不能看到新私有学习数据。

## 功能需求

### REQ-B4-01 独立模型与旧 Note 共存

- 输入：Alembic 012、Question、DraftItem、旧 `Note(type="mistake")` 真实数据。
- 处理：新增 MistakeDraft、Mistake、ReviewItem、ReviewRecord；扩展 DraftItem 允许
  mistake 类型及 question/question_draft 来源。
- 输出：新私有错题闭环可用，旧 Note 数量、字段、API 与公开页面不变。
- 失败：目标表提前存在、版本漂移或约束无法安全变更时停止并申请范围扩大。
- 验收：013 正常升级；无旧 Note 回填、迁移、双写或删除。

### REQ-B4-02 创建与编辑错题草稿

- 输入：正式 question_id 或 question_draft_id（二选一）、我的答案、错因、可选解析、
  难度与知识点。
- 处理：复制题目/答案/解析快照，创建统一 DraftItem 与 MistakeDraft。
- 输出：pending 私有草稿，可在管理端修正。
- 失败：来源不存在、两种来源同时为空/同时存在、跨科目知识点或非法字段返回稳定错误。
- 验收：管理员可从正式 Question 创建，也能保留 QuestionDraft 引用合同。

### REQ-B4-03 人工拒绝与幂等确认

- 输入：草稿 ID 与 version。
- 处理：拒绝变 rejected；确认时锁定草稿、验证来源与字段，原子创建 Mistake、
  knowledge links、唯一 ReviewItem，并把 DraftItem 更新为 converted target。
- 输出：一个 active/private Mistake 与一个 active ReviewItem。
- 失败：旧 version、rejected 状态或无效来源返回 409/400；任一步失败整体回滚。
- 验收：重复确认返回同一 Mistake/ReviewItem，未确认草稿不进入复习。

### REQ-B4-04 私有错题管理

- 输入：列表筛选、详情更新或归档命令。
- 处理：支持 active/archived 管理；更新使用 version；归档同时暂停对应 ReviewItem。
- 输出：管理端错题列表/详情、Question 来源与知识点。
- 失败：version 冲突、无效 taxonomy 或不存在返回稳定错误。
- 验收：新 Mistake 无 public endpoint，管理员可编辑与归档。

### REQ-B4-05 简单复习队列与提交

- 输入：到期 ReviewItem 与 rating `0..5`。
- 处理：一个事务写入不可变 ReviewRecord，并按固定规则更新 item：
  `0..2 → 1天`、`3 → 3天`、`4 → 7天`、`5 → 14天`；更新 repetitions、
  interval_days、last_reviewed_at、next_review_at。
- 输出：新的 next_review_at 与历史记录。
- 失败：非 active/未到期/目标不存在/重复请求返回稳定错误，不产生半条记录。
- 验收：提交一次只新增一条记录；记录写入后没有 update/delete API。

### REQ-B4-06 管理页面体验

- 输入：真实 API 的 loading、empty、success、validation、conflict、network 状态。
- 处理：`/manage/mistakes` 提供草稿入口与正式列表；详情审核/编辑；
  `/manage/review` 展示今日到期项并提交 rating。
- 输出：桌面与移动端可完成完整闭环，错误不丢表单。
- 验收：真实浏览器完成草稿、确认、错题详情、复习提交与刷新持久化。

### REQ-B4-07 权限与公开兼容

- 输入：匿名、一次性管理员、旧公开错题页面。
- 处理：全部新 API 使用 `get_current_admin`；workspace 使用 AuthGate；旧公开 Note
  过滤与路由不变；公开页面不得请求新 admin API。
- 输出：新学习数据私有，旧公开错题继续可读。
- 失败：任何匿名 2xx、新 public Mistake API、旧公开页面回归或 Note 数据变化均阻塞。
- 验收：401/404、公开浏览器、DB 对账、临时账号清理与旧 `/manage` 零 diff均有证据。

## 非功能需求

- 一致性：确认与复习提交均为单事务；使用行锁、version 和唯一约束。
- 安全：新 Mistake/Review 固定 private/admin-only；不使用 AUTH_BYPASS 验收。
- 审计：保留草稿 target、Question 来源、ReviewRecord 前后状态与时间。
- 兼容：旧 Note 与旧 review 字段不改、不迁、不双写。
- 可维护：router thin，service 管理状态机，DTO 显式且无 `any`。

## 明确不做

- 旧 Note 错题迁移或公开数据源切换。
- 旧错题编辑器大型重构。
- 完整练习、自动判错、题库抽题。
- BKT、mastery、复杂容量、优先队列、AI/OCR、附件。
- ReviewRecord 更新/删除、公开新错题 API。

## 总体验收

无需 AI 或练习系统，管理员可从 Question 完成错题确认与一次固定间隔复习；未确认数据
不会进入复习；新数据保持私有；旧公开错题与旧 Note 事实源完全不受影响。
