# 修复设计与决策

以下为推荐实现合同，实施 R00 定版并通过相应专业门禁后执行；本文件不代表合同已在产品生效。

## F01：题型输入与传输

`review-queue.tsx` 的 `answer: string` 和选项 `answer: option.key` 是当前失效点。为 multiple_choice 使用独立集合状态，点击切换成员，按题目选项顺序去重序列化为现有后端支持的逗号串，例如 `A,C`；不为修 UI 引入 breaking API。单选保持互斥，判断与文本题继续现有路径。

输入变更后清除旧 evaluation/attempt 建议，避免确认上一次答案的评分；请求进行中禁止产生与返回结果错配的编辑/重复提交，关闭/切换题目清空状态。空集合不能提交，保留 aria-pressed、键盘可达和六档人工确认。正常 API 与客户端合同一起验证。

## F02：KP 继承、覆写和历史界限

默认推荐：Question KP 在自动创建 MistakeDraft 时做一次初始快照；draft 人工编辑成为确认时的权威；convert 原样复制该集合到 Mistake。Question 后续改 KP 不反向同步已确认错题。不同三类关系不合并。

区分未提供与显式空集合：未提供时才继承，明确清空 `[]` 应保持空，不能被默认继承悄悄填回。自动错答入口读取 QuestionKnowledgePoint 并传入；检查人工草稿与 Capture 入口是否已有明确集合，避免普遍改变其合同。校验学科/有效 KP、去重、同事务；失败不得留下半个 Attempt/draft/link。

重复转换不新增 Mistake/ReviewItem/link；竞争下只有一次转换成功或返回既有结果。以创建时读取的一致快照为边界；若并发题目改标签，记录/测试确定的锁或版本策略，不随机混合集合。无需预设新增表；如要求持久化来源版本，先给 schema 差异与 G2，不擅自扩大。

历史无 KP 的 Mistake 无法仅凭空集合判断是缺陷还是人工清空。第一轮只修未来写链并提供只读缺链候选清单（来源Attempt/Question、现有集合、冲突、数量）；不自动回填。未来回填必须单独定源、人工确认、dry-run、幂等 ledger、备份/回退，不能推定所有旧数据已修复。

## F03：冻结入口完整性

复用 `legacy_mistake_freeze.assert_not_legacy_mistake_write`，覆盖 suggestions 的 move_to_folder 与 add_tag，并搜索 Note 全部 mutation、批量、导入/关联入口及间接文件夹/标签操作。校验已有类型和请求目标类型，保护从/到 mistake 的转换。普通 Note 和 Blog、canonical Mistake 不误伤；旧内容只读保留。

建议批量操作先预检全部目标，任一命中 legacy mistake 就整体 410 + stable code，普通目标也不产生提前落库副作用。需同步批量客户端错误展示及现有部分成功合同；若会破坏外部依赖，在 R00 决定兼容方案并经 G1，不只在循环末尾加guard。认证仍先由真实 get_current_admin 处理；禁止绕过认证用于最终权限验收。

## F04：schema ownership

清点 026 ledger/approval/rollback/nonce/transition 对象、draft 六列、相关 constraints/functions/triggers，及033四索引（含partial predicate）与purpose CHECK/FK约束；以 migration 为当前 SQL-owned 定义来源。033索引优先在模型 metadata 准确表示。

SQL-owned 对象可用独立 metadata 表示，或按 schema/table/column/index 精确 allowlist 排除 autogenerate；采用后者必须同时用 catalog 检查类型、nullable、默认值、约束、索引谓词及 SQL-owned 定义。不能广泛忽略 reflected 对象、整个业务表或所有未知表。

验收为双门禁：ORM-managed 的 alembic check 无未解释差异；SQL-managed 与明确 manifest 一致。故意删改受保护列/索引的 scratch 反例必须被检测，才能证明不是屏蔽报警。禁止编辑已发布迁移以改变历史、执行 autogen 候选 drop 或为 check 通过删除对象。若仅metadata对齐，无新DDL；若发现真实schema变更，另出增量迁移，经 R04/G2 后再测试。

## F05：真实保存与 AI 来源

先逐 caller 建表：调用类型、是否注册 AiRun、是否落库、目标 owner、生成返回 DTO、真实保存入口、前端消费者、review/版本语义。Capture recognition/draft 继续链接 Capture，不重绑为下游实体；纯暂态预览不强制虚构实体。

当前 GatewayCallResult 未返回 run_id，_start_run_record 独立会话可能失败返回 None，AiRun 无现成 created_by/owner 字段。需要贯通网关→响应schema→typed client→候选状态→保存请求，并设计可核验的服务端来源/产物绑定；admin身份不等于任意run属于本次产物。追踪不可用时必须明确拒绝或恢复，不能静默保存无来源内容。如必须新增持久化绑定字段，先R04/G2。

不能把 `ai.py` 的 question-draft/confirm echo 直接当 canonical 保存：它当前没有 DB dependency，且 staged 流有旧域边界。R00/R05 应选一个当前真实 canonical 创建流程闭合生成→run_id→用户确认→保存；若没有合适入口，定义最小 canonical 保存合同并专项审阅，不恢复已冻结的 legacy 写，也不把所有调用重新标 transient 规避欠账。

客户端只能提交候选关联；服务端核验 run 存在、task/target类型兼容、状态允许、当前授权/来源归属与预期版本。实体创建、关联、确认审计在同一业务事务提交；若 gateway 使用独立session，需明确生成记录和确认事务的边界，失败不得产生“已接受但无实体”。同run同target重复幂等；不同target重绑拒绝；并发锁/CAS防抢占；缺失run显式错误，不忽略helper的False。已拒绝/未成功run不得保存关联。弃用的候选允许NULL并可解释，不为填target创建无意义业务实体。

保留原有已链接Capture、retry继承、review状态与版本；完成后读取 AiRun 和业务实体双向证据，而非只断言 helper 被调用。涉及 DTO 必须后端 schema、typed client、UI 一起更新。

## D06：OCR 两条明确出口

推荐无真实 provider 授权时走“自动 OCR 默认关闭，手工录入可用”的可交付方案。禁用必须同时在 UI、服务端识别/重试入口和状态提示生效；直连 API 不能绕开触发 provider；保留已有结果只读和手工编辑/转换，不假装是质量达标。

若选择真实评估：单独明确 provider、调用成本上限和10份可使用样本（清晰/模糊/旋转/公式等分层），先冻结样本hash与评分规则，保留字段级准确性、失败类别、耗时/成本。沿PR14原标准pipeline完成至少8/10（不是字段准确率80%；字段级质量阈值在R00冻结）；失败、超预算或关键字段不满足标准则进入禁用策略，不反复换样本凑分。未经授权本轮不调用。

## 回退原则

代码回退只针对修复自身的隔离diff，不 reset/checkout 用户脏文件。schema对齐先不改数据；不可逆026禁止承诺全链降级。033 live challenge 的 fail-closed 保护保留，不删除challenge换取绿灯。F02历史回填和生产迁移都不属于代码回退。AI事务失败应自然rollback，外部调用已发生不能声称撤销费用。任何严重回归停止当前任务，保留复现和局部变更供复核。
