# Batch 3 审查与剩余风险

## 结论

Batch 3 实现与验证通过，未发现阻塞本批用户验收的问题。当前状态必须停留在等待用户
确认，不得自动进入 Batch 4。

## 范围与架构

- 独立 `draft_items/question_drafts/questions/question_sources` 与旧 Note 并存。
- 没有回填、迁移、双写或修改 `Note(type="mistake")`。
- 正式 Question 只能由 Draft conversion 生成；没有直接 Question create API。
- Question/Draft 全部私有且全部 admin API 后端鉴权；没有 public Question API。
- 未实现错题、复习、练习、附件、AI、OCR、Capture Router、批审或复杂去重。
- workspace shell、首页与旧 `/manage/page.tsx` 未改。

## 一致性审查

- conversion 使用 DraftItem 行锁与 version；converted 请求优先返回既有 target。
- `(source_type, source_ref)` 唯一约束作为第二道幂等保护。
- Question、manual source、正式 knowledge links 与 converted target 在同一事务中落库。
- 实测重复 convert 后 Question=1、Source=1。
- rejected 草稿不能转换；Question 删除为 archived，不物理删除。
- 题型/options 的合并后验证错误已在 service 转换为 domain validation，而不是 500。

## 迁移审查

- 012 前确认目标表均不存在；没有历史漂移。
- 012 只创建 4 张新表、约束与索引，不触碰旧 Note 数据。
- `011 -> 012` 与重复 upgrade 均通过；current 为 `012 (head)`。
- 旧 Note 基线在执行与清理后均为 blog=1、mistake=5、note=7。

## 剩余风险

### RISK-B3-01 create_all 仍存在

- 类型：数据/部署
- 描述：应用 lifespan 的既有 `Base.metadata.create_all` 仍可能在未来制造 migration 漂移。
- 严重程度：中
- 状态：已缓解；本批 migration 对提前存在目标表会主动失败。
- 建议：后续独立基础设施任务移除生产 create_all，保持 Alembic-only。
- 下一轮需求：否，不应混入 Batch 4。

### RISK-B3-02 列表查询为小规模 N+1

- 类型：性能
- 描述：当前列表逐题加载来源与知识点；MVP 小数据可接受。
- 严重程度：低
- 状态：未处理。
- 建议：出现真实规模或延迟证据后批量预取。
- 下一轮需求：否，归档为按证据优化项。

### RISK-B3-03 公开 mistakes 的管理员请求噪音

- 类型：权限/体验
- 描述：既有公开 `/mistakes` 仍请求 review/weak-points admin API 并产生 403。
- 严重程度：中
- 状态：已知、未由本批修改；页面仍正常且 console error=0。
- 建议：按 AGENTS P1 权限任务单独修复。
- 下一轮需求：否，不属于 Batch 4 核心模型。

## 下一轮需求决定

Batch 4 只可在用户确认后依据其既有 spec 规划独立 Mistake/Review 兼容方案。上述风险均不
自动扩大 Batch 4；RISK-B3-01 与 RISK-B3-03 进入独立基础设施/权限待办，RISK-B3-02
在缺少性能证据时归档。
