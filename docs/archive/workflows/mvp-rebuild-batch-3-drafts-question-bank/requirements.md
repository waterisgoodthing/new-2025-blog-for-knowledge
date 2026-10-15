# 需求文档：Batch 3 题目草稿 / 审核 / 题库

## 背景

Batch 2 已提供稳定的科目与知识点 ID。下一步需要先建立完全人工可用、可审核、
可追溯的题目入库链路，才能安全承接后续错题与复习。当前 Note 模型不能被直接当作
独立 Question，且旧错题数据迁移属于后续兼容设计，不应混入本批。

## 用户角色

- 个人管理员：创建、修正、拒绝、转换草稿，并维护私有正式题目。
- 未登录访客：不能读取草稿、题库或执行任何题目操作。

## 功能需求

### REQ-B3-01 独立模型与兼容边界

- 输入：当前 Note、Batch 2 taxonomy、Alembic 011 真实状态。
- 处理：新增独立 DraftItem、QuestionDraft、Question、QuestionSource；与旧 Note 并存。
- 输出：新题目拥有稳定 ID，旧 Note 数据和旧页面行为不变。
- 失败：迁移前置版本、表名、约束或真实 schema 不符合预期时停止，不 stamp 或手改掩盖。
- 验收：012 正常升级；没有旧 Note 回填、删除、字段迁移或双写。

### REQ-B3-02 手工题目草稿

- 输入：题干、题型、科目、可选标题/选项/答案/解析/难度/知识点。
- 处理：一次事务创建 `draft_items(draft_type=question, source_type=manual)`、
  `question_drafts` 和知识点关联。
- 输出：状态为 `pending` 或因必填校验问题明确成为 `needs_fix` 的私有草稿。
- 失败：空题干、无效科目、跨科目知识点、非法题型/options 合同时返回稳定 400/404/409/422。
- 验收：管理员可手工创建并在草稿列表、详情看到完整数据；未登录返回 401。

### REQ-B3-03 草稿编辑、拒绝与版本控制

- 输入：草稿 ID、客户端已读版本、修改字段或拒绝动作。
- 处理：仅允许未转换草稿修改；每次修改递增 version；拒绝后状态为 `rejected`。
- 输出：更新后的类型化草稿与统一状态。
- 失败：版本不匹配返回 409；converted/rejected 草稿的非法修改返回 409；不存在返回 404。
- 验收：并发旧版本不能覆盖新修改；拒绝草稿不会进入题库。

### REQ-B3-04 幂等人工确认转换

- 输入：草稿 ID 与当前 version。
- 处理：事务内锁定草稿，重新验证字段、科目、知识点；创建一个 Question、
  一个 manual QuestionSource，复制正式知识点关联，并将 DraftItem 更新为 converted
  且记录 target_type/target_id。
- 输出：正式 Question 与转换映射。
- 失败：缺字段或无效关联返回 400；版本冲突返回 409；事务任一步失败全部回滚。
- 验收：重复转换返回同一个 Question，不会生成第二条；未确认草稿不出现在题库。

### REQ-B3-05 正式题库管理

- 输入：管理员筛选条件或题目更新字段。
- 处理：支持私有 Question 列表、详情、更新和归档；科目与知识点关联保持一致。
- 输出：可追溯 manual 来源的正式题目。
- 失败：跨科目知识点、重复/版本冲突或不存在返回稳定错误；删除采用归档，不物理删除。
- 验收：`/manage/questions` 和详情页可查询、编辑、归档；归档状态清晰。

### REQ-B3-06 管理页面状态

- 输入：真实 admin API 的 loading、empty、success、validation、conflict、network error。
- 处理：保留未提交表单；转换与归档需要明确确认；状态标签区分 pending、needs_fix、
  rejected、converted、active、archived。
- 输出：桌面与移动端均可完成主流程。
- 失败：错误显示可读信息，不伪造成功、不丢输入。
- 验收：真实浏览器完成创建、编辑、转换、题库查看/编辑/归档及冲突路径；无横向溢出。

### REQ-B3-07 权限、审计与回归

- 输入：未登录、临时管理员、公开页面和旧 Note 流程。
- 处理：全部 drafts/questions API 使用 `get_current_admin`；管理页面由既有 AuthGate 保护；
  转换/拒绝/归档至少形成可追溯状态与来源。
- 输出：私有数据不公开，旧公开读取和旧管理入口不变。
- 失败：任何未登录 2xx、公开页面回归或旧 Note 变更都阻塞验收。
- 验收：401、API 合同、DB 映射、公开页面、旧 `/manage` 零 diff、临时账号清理均有证据。

## 非功能需求

- 安全：Question/Draft 默认私有；后端鉴权是真实边界；不使用 AUTH_BYPASS 验收。
- 一致性：转换在一个数据库事务中完成，使用行锁、version 和唯一来源约束保证幂等。
- 兼容：不改变 Note schema、`/api/notes`、公开博客/笔记/错题或旧写作路由。
- 可维护：router thin；schema/service/model 分层；前端 DTO 显式且无 `any`。
- 可审计：保存 source_type=manual、草稿到 Question 的 target 映射和时间戳。
- 可恢复：012 不迁移旧数据；执行前记录 current/head，验证重复 upgrade 和现有数据保全。

## 明确不做

- 旧 Note/错题回填、双写、迁移或删除。
- AI、OCR、Capture Router、附件。
- 错题、复习、练习、做题结果。
- 批量创建/审核、复杂去重、搜索、公开题库。
- Question 直接创建入口、公开 Question API。

## 总体验收

管理员无需 AI 即可完成一条手工题目入库闭环；重复转换只得到一个正式题目；未确认或
被拒绝草稿不进入题库；权限、迁移、合同、浏览器与旧系统兼容证据完整。
