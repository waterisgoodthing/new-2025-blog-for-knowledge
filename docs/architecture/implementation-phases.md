# 实施阶段与第一版收口

> 以下均为待实现规划，不构成本轮代码、数据库迁移、依赖或部署批准。Phase 0–6 是唯一主线，不再维护另一套“第一阶段至第十三阶段”编号。

## 总体原则

每个 Phase 都必须单独形成需求、设计、经批准任务清单、验证证据、剩余风险和回滚方案。上一 Phase 未验收，不进入下一 Phase。实现应按最小纵向切片推进，不把全部系统一次性上线。

## Phase 0：安全、术语与边界收口

目标：让后续实现建立在唯一契约上。

- 固定脚本生成通行密钥与单管理员会话，不引入密码、Passkey 或多用户 RBAC。
- 分离 `/api/public/**` 与 `/api/admin/**`；盘点旧路由/API 兼容矩阵。
- 固定 `knowledge_point_links`、`knowledge_relations`、`attachment_links` 和 Review target 模型。
- 固定 AI/OCR/Capture 必须先进入 `draft_items` 的安全闸门。
- 验收：术语全文一致，公开读取不泄露私有学习数据，生产绕过组合被列为实施阻断项。

## Phase 1：最小学习基础

目标：先建立一个可手工维护的学习骨架。

- 第一批只实现 Subject、Chapter、Knowledge Point、Question 及来源。
- 使用 `knowledge_point_links` 关联题目与知识点；`knowledge_relations` 首批只支持人工维护。
- 提供最小管理列表、详情、创建与编辑，不同时实现搜索、统计或 AI。
- 验收：无需 AI 即可完成科目、知识点和题目的基本管理。

## Phase 2：私有附件与单文件 OCR

目标：打通最小上传识别链路。

- 实现 `attachments`、`attachment_links` 和私有访问。
- 首批只支持图片及单个 PDF；OCR 保存 job/result/block。
- Capture Router 首批只输出 `question_only`、`mistake_candidate` 或 `unknown`。
- 暂不实现多文件练习导入、复杂衍生文件和云端多引擎自动切换。
- 验收：原文件可追溯，OCR/Capture 不写正式业务表。

## Phase 3：统一草稿审核

目标：建立自动化输出到正式数据之间的唯一闸门。

- 实现 `draft_items`、`question_drafts` 和 `mistake_drafts`。
- 第一批只支持列表、详情、修正、拒绝和幂等转换。
- `practice_attempt_drafts`、知识点建议和 Note 建议可在相同契约下后续补充。
- 验收：所有已接入 AI/OCR/Capture 输出都能追溯 Draft Item，未经确认不进入正式表。

## Phase 4：最小练习、错题与复习闭环

目标：完成一条可用的手工学习闭环。

- 实现 Practice Session、Practice Attempt、Mistake、Review Item 和 Review Record。
- Practice Attempt 使用 `result_type`；首批支持手工创建练习和确认错题。
- Review 使用 `target_type/target_id` 和 `review_items.next_review_at`，不建立 `review_schedules`。
- 第一批可先使用 SM-2 与容量上限；BKT Mastery 事件在数据质量可验证后启用。
- 验收：做题、判错、确认错题、加入复习、提交复习均可在 AI 失败时完成。

## Phase 5：AI 管理与简单后台任务

目标：让已证明有价值的自动化可配置、可观察、可重试。

- 实现最小 `ai_model_profiles`、`ai_routing_rules`、`ai_prompt_templates`、`ai_runs`。
- 目标路径统一为 `/manage/ai/runs` 和 `/api/admin/ai/runs`。
- 首批使用数据库 jobs 表与单 worker，只承载 OCR、Capture 和已批准 AI 任务。
- 暂不实现复杂成本中心、多供应商自动优化或分布式队列。
- 验收：每次 Run 可追溯模型、路由、Prompt、校验、token、成本、时延和错误。

## Phase 6：按证据补齐搜索、统计与设置

目标：只为已经产生的真实数据增加管理效率。

- 先实现管理搜索和 Review/Upload/AI 的必要设置。
- 再实现基础日/周指标与周报；统计先由 SQL/规则计算，AI 只解释。
- 复杂索引、设置中心和报告类型按使用证据逐项增加。
- 验收：公开搜索只返回 public + published，私有指标不泄露，设置有类型和变更审计。

## 第一版代码实现上限

第一版建议只交付 Phase 0、Phase 1、Phase 2 的单文件路径、Phase 3 的 Question/Mistake 草稿，以及 Phase 4 的手工最小闭环。Phase 5–6 保留架构接口但不要求与第一版同时上线。

明确暂缓：多文件练习批导、全量 BKT、自适应出题、复杂 AI 路由、分布式队列、统一搜索索引、复杂统计大屏、完整设置中心、RAG、向量库、公开题库和多用户权限。

## 每阶段最小交付物

1. 当前 Phase 的需求、设计和经批准任务清单。
2. 明确的实现上限与不做事项。
3. 数据迁移、兼容与回滚方案。
4. API、权限、数据和浏览器验收证据。
5. 剩余风险及是否进入下一 Phase 的明确结论。
