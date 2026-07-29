# 从现有结构迁移到目标结构

> 迁移尚未执行。当前架构与目标架构的差异统一视为待迁移或兼容旧系统。

## 学习系统新增迁移边界

1. 建立 Subject、Chapter、Knowledge Point 和 Question 基础关系。
2. 先引入私有 Attachment，再接 OCR 与 Capture；原文件始终保留。
3. 在任何 AI 自动化前建立 `draft_items` 与转换审计。
4. 从 `Note(type="mistake")` 双写/回填至独立 Mistake，并逐条对账一等错题字段。
5. 将旧 review 元数据迁移为 Review Item/Record/Mastery 事件，禁止伪造历史。
6. public/admin API 与管理路由逐调用方迁移，旧接口在无引用且验收通过前保留。
7. 最后启用 jobs、search index、metrics 和 settings；派生数据必须可重建。

任何阶段发现不一致，只记录、修正迁移器或回滚切流，不直接手改生产数据来掩盖问题。

## 已知起点

当前结构的主要迁移事实：

- `notes` 表同时承载 `blog`、`note`、`mistake`。
- 错题依靠 `type = "mistake"` 区分。
- `ef`、`interval`、`repetitions`、`next_review`、`last_reviewed` 等复习字段位于 `notes`。
- `ai_metadata` 是自由 JSON。
- `images` 是 URL JSON 数组。

迁移必须先用实际数据库盘点验证数量、空值、重复 slug、坏链接和 JSON 形状；本文不把代码模型等同于生产数据事实。

## 迁移通用护栏

- 每阶段独立 migration、脚本、指标、验收报告和回滚决策。
- 迁移脚本可重入，使用源 ID 到目标 ID 映射表或稳定映射规则。
- 切读前先校验记录数、内容哈希、关联数和抽样页面。
- 兼容期只允许明确的主写路径，避免无主双写。
- 删除旧字段是最后一步，并经过备份恢复演练。

## Phase 0：只读盘点，冻结语义

- **目标**：确认生产数据真实形态并冻结旧字段含义。
- **涉及数据**：`notes`、tags、subjects、复习字段、`ai_metadata`、`images`、现有用户/会话/审计。
- **风险**：把代码默认值误判为真实数据；遗漏异常 type、重复 slug 或非标准 JSON。
- **回滚方式**：全程只读，无数据回滚；撤销盘点结论并重新采样。
- **验收标准**：记录数按 type 对账；空值/异常值/JSON schema 分布、附件可达性、slug 冲突和数据所有权形成签字确认的基线。

## Phase 1：新增目标表，不切流量

- **目标**：建立目标表、约束、索引和映射设施，不改变现有读写。
- **涉及数据**：新增 `posts`、新语义 `notes`、`mistakes`、Review、AI、Attachment、Taxonomy、Auth 表；旧表保持不变。若表名冲突，先使用版本化临时表或 schema。
- **风险**：命名冲突、约束过严、迁移锁表、模型与 API 提前耦合。
- **回滚方式**：在确认无业务引用后回滚新增 migration；保留旧路径。
- **验收标准**：空表 migration 升降级通过；索引和外键检查通过；现有应用行为与基线一致。

## Phase 2：双写或后台迁移 posts / notes / questions / mistakes

- **目标**：按旧 `type` 拆分内容；每条旧错题先建立可复用 Question，再建立对应 Mistake，并保留 ID 映射。
- **涉及数据**：标题、slug、正文、摘要、状态、隐藏标记、学科、错题专属字段、标签。
- **风险**：双写漂移；同 slug 冲突；旧记录混合字段不完整；时间戳变化。
- **回滚方式**：读写仍指向旧表；停止双写，按 migration batch 删除或重建目标数据。
- **验收标准**：按类型记录数一致；每条旧错题均可追溯 Question 与 Mistake；关键字段哈希一致；重复/不完整记录全部进入异常清单；增量写入漂移为零。

旧数据没有 Practice Session 时，不强行伪造历史练习。`practice_session_id`、`practice_attempt_id` 可以为空并用 `source_type=legacy_migration` 保留来源；只有确有批次证据时才可创建明确标注的 `legacy_import_session`。`practice_sessions` 主要服务迁移后新增的练习导入。

## Phase 3：迁移复习字段到 review_items

- **目标**：把当前复习状态从 Mistake 内容中剥离。
- **涉及数据**：`ef`、`interval`、`repetitions`、`next_review`、`last_reviewed`，以及 Mistake ID 映射。
- **风险**：时区或 date/datetime 转换；`next_review = null` 的语义不清；算法版本未知。
- **回滚方式**：旧字段继续作为主数据；删除本批 Review Item/Schedule 后重跑。
- **验收标准**：每个应复习 Mistake 对应唯一 Review Item；due 队列与旧查询逐条一致；空值语义和算法版本有明确映射。

## Phase 4：迁移复习历史到 review_records

- **目标**：建立不可变复习历史；对旧系统不存在的历史不伪造。
- **涉及数据**：现有审计、日志或可验证复习事件；仅有 `last_reviewed` 时作为明确标注的 legacy snapshot，而非完整历史。
- **风险**：现有结构可能没有完整历史；从当前状态反推事件会制造虚假数据。
- **回滚方式**：按 `source=legacy_migration` 删除导入记录；保留 Review Item 当前状态。
- **验收标准**：每条 Record 有来源证据；无法恢复的历史被记录为数据缺口；统计不会把 snapshot 当普通复习次数。

## Phase 5：迁移 ai_metadata 到 ai_runs

- **目标**：把自由 JSON 拆为可追踪 AI 运行及可选的已采纳业务字段。
- **涉及数据**：`ai_metadata` 的各类 shape、模型结果、图解、错误理解与最终解析。
- **风险**：缺少模型、prompt、时间和执行状态；不同版本 JSON 语义冲突；敏感内容被复制。
- **回滚方式**：旧 JSON 保留；删除按 migration 标识生成的 AI Run；不覆盖已确认业务字段。
- **验收标准**：所有非空 JSON 被分类为“成功迁移、保留原样、人工处理”；输出可从 Run 读取；未知元数据无静默丢失。

## Phase 6：迁移 images 到 attachments

- **目标**：为 JSON URL 建立 Attachment 记录与业务关联。
- **涉及数据**：`images` 数组、cover、AI 生成图、现有 public 文件或外链。
- **风险**：文件缺失、重复 URL、外链不可控、路径泄露、同文件多实体共享。
- **回滚方式**：业务继续读旧数组；删除导入的 Attachment 关系，不删除原始文件。
- **验收标准**：每个 URL 有成功、缺失、外链或重复分类；可访问文件 checksum 对账；顺序和用途保持一致。

## 新学习结构迁移映射

| 旧数据 | 目标数据 | 原则 |
|---|---|---|
| `notes(type="mistake")` 的题目本体 | `questions` | 每条旧错题先建立 Question，后续再做经确认的去重 |
| `notes(type="mistake")` 的错题特有字段 | `mistakes` | 引用对应 Question，保留旧 ID/slug 来源 |
| `ef`、`interval`、`repetitions`、`next_review`、`last_reviewed` | `review_items`（含 `next_review_at`） | 第一版不建立 `review_schedules`，不继续保存在 Mistake |
| `ai_metadata` | `ai_runs` | 未知结构不静默丢失，已采纳结果与原始运行分离 |
| `images` | `attachments` | 保留顺序、用途和来源 |

多题导入能力不从旧 Mistake API 延伸；应在目标 Question 与 Practice 模型确认后，以新的 Practice Import 路径实现。

## Phase 7：切换读取路径

- **目标**：public/admin API 和前端逐域读取目标表。
- **涉及数据**：Posts、Notes、Mistakes、Review、AI、Attachments 及其关系。
- **风险**：公开过滤差异、N+1 查询、缓存污染、旧新 DTO 不兼容。
- **回滚方式**：按域 feature flag 切回旧读路径；目标写入保留用于分析。
- **验收标准**：每个域单独通过 API 契约、权限、数据对账、性能和真实浏览器验收；错误率与延迟在阈值内。

## Phase 8：保留旧字段兼容窗口

- **目标**：让旧消费者有固定期限迁移，同时监测是否仍有旧读写。
- **涉及数据**：旧 `notes.type`、复习字段、`ai_metadata`、`images` 和旧 API。
- **风险**：无限期双写；旧字段再次成为事实来源；修复只落一侧。
- **回滚方式**：窗口内可按域切回旧路径；若漂移则暂停下线倒计时并重新对账。
- **验收标准**：兼容截止日期、owner 和移除条件明确；旧路径调用量归零；双写一致性持续满足阈值。

## Phase 9：删除旧字段或归档旧表

- **目标**：在兼容完成后移除旧结构，目标表成为唯一事实来源。
- **涉及数据**：旧多态内容、复习列、JSON 字段、兼容 API 与映射表。
- **风险**：隐藏消费者、不可逆丢失、回滚时间过长。
- **回滚方式**：执行前创建加密备份和恢复点；若需回滚，通过已演练的恢复脚本重建旧 schema，而非临时手工 SQL。
- **验收标准**：完整备份与恢复演练通过；零旧流量持续一个约定周期；删除 migration 升级通过；关键业务和数据对账再次通过。
