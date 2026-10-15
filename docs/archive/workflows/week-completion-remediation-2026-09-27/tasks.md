# 串行执行任务书

所有 R 项当前均为 NOT_AUTHORIZED（实施）；只完成方案编制。下表是计划角色，不表示已派发或通过门禁。规模 S/M/L 不是承诺工日。每项实施需独立 reviewer，主 Agent 最终 accept；高风险另由专业 gate reviewer/QA 提供证据，不能自审代替。

> 2026-09-27 更新：用户明确要求按 R00→R07 推进，R00–R07 的**本地实现与隔离验证**已执行（结果与证据见 [README「实施结果」](README.md) 与 [validation.md](validation.md)）。真实 provider 外发、历史/生产回填、生产迁移、commit/push/部署仍未授权。独立 reviewer 未在本环境派发，最终 accept 仅限本地修复候选，不构成发布 accept。

| 顺序 | 范围/候选文件 | 交付与退出条件 | 角色/门禁 | 规模 |
|---|---|---|---|---|
| R00 | 当前源码/测试/未提交差异与本方案 | 冻结快照与可恢复副本；题型/KP/批量冻结/AI真实创建入口合同定版；列schema需求及验收ID | 主Agent、Domain/Product/QA；G0，AI来源G3/G4 | M |
| R01 | review-queue.tsx、组件测试、E2E04；必要时attempts client | 集合输入、旧evaluation失效；V01通过；不改调度 | Frontend、独立QA/Contract reviewer | S/M |
| R02 | attempt_service、mistake_service、必要schemas、KP穿链测试 | 未来写链KP完整；显式空/覆盖/并发/回滚通过；历史只出只读候选清单 | Backend/Data、独立Domain/QA；G0/G4，模型变化加G2 | M |
| R03 | suggestions、freeze service、扫描发现的Note mutations及客户端 | 写入口清单、批量预检、稳定410；普通写/公开及兼容读不退化 | Backend、独立Security/QA；G3，破坏合同另G1 | M |
| R04 | registry、challenge model、alembic/env、SQL-owner manifest/检查测试 | 双drift gate、fresh/局部roundtrip、破坏反例可检测、无误删 | Database、独立Database gate/QA；G2，challenge回归G3 | M |
| R05 | gateway、ai_run_service、选定canonical生成/保存service/router/schema/client/UI、治理文档 | caller分类、run_id传播、来源绑定、真实保存事务/幂等/冲突回读；Capture链接保留 | AI/Backend/Frontend、独立Security/Domain/QA；G0/G3/G4，schema加G2，边界变化加G1 | M/L |
| R06 | Capture识别/重试/config/UI及评估方案 | 默认建议禁用自动OCR并验证手工路径；或另授权10真实样本达到原标准，再提启用决策 | AI/Product、独立QA；G0/G4，外发G3，生产开关另G5 | S/M |
| R07 | 不变量索引、全套回归、当前状态索引 | F01–05关闭、OCR出口明确、D12矩阵齐全；独立复核无未关闭高优先级问题；本地/外部状态分列 | 独立Technical reviewer/QA、所需专业gate；主Agentaccept | M |

R01–R07串行验收。R04是任何迁移前置，可因schema需要提前；R05依赖R00选定真实canonical路径，不恢复legacy写。R07使用最终同一快照。各步附命令、输出、diff/hash、失败→通过证据与剩余风险。D12测试随修复落地。

## 执行边界与停止条件

当前仅授权制定方案。未来可一次明确授权 `R00–R07 本地实现与隔离验证` 后串行推进，不为同范围Worker重复询问；真实provider外发、历史/生产回填、生产迁移、commit、push、部署仍需相应明确授权。

执行前做用户脏文件可恢复快照，不以新worktree的HEAD冒充本工作树；隔离副本包含批准范围内未提交源码，排除凭据/缓存。用户同期编辑重叠文件则暂停重叠部分，不覆盖。

停止条件：核心合同冲突、schema超出批准、未知owner、专业gate失败、严重回归、无法保证隔离库、外部成本/样本外发未授权。报告证据与独立可继续范围，不放宽guard。

第一阶段退出必须满足REQ-01–07。F02存量未回填/规模未知单列；九项skip如涉及当前关键验收必须补运行。远端CI、真实设备passkey、生产cookie/CORS、迁移/恢复是后续发布证据；须对应授权提交的同源工件、目标拓扑和G5。方案审阅通过不代表这些门禁通过。
