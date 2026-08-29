# Next Iteration Requirements

## REQ-PRA-NEXT-01：恢复可用的视觉核心指标

- 来源：验收报告 / RISK-PRA-001
- 问题描述：四个场景的 LCP 全部为 null，现有数据不能支持 LCP 预算或视觉就绪结论。
- 需求描述：先以有界诊断确定 LCP 缺失原因；若页面存在合格 LCP candidate，修正仅限测量 harness 并重采样。若 LCP 不适用，先审批替代指标与成功/失败合同，再生成新矩阵。
- 验收标准：每个场景至少 10 个有效样本具有已批准的视觉核心指标；缺失值仍保留为缺失，不得填 0；诊断与采样 raw 可重算。
- 优先级：P0
- 关联风险：RISK-PRA-001

## REQ-PRA-NEXT-02：分离采集 server-cold 与代表性环境矩阵

- 来源：验收报告 / RISK-PRA-002
- 问题描述：当前仅证明本地隔离、server-warm 条件，不能覆盖冷启动、CDN、移动网络或地理延迟。
- 需求描述：在单独授权的非生产或受控 staging 环境中冻结网络、缓存、数据量和主机合同；server-cold 与 server-warm 分开采集、分开聚合。
- 验收标准：每个获批场景都有明确温度定义、原始样本、失败保留和独立聚合；任何生产服务、数据或凭据使用均需新的显式授权。
- 优先级：P0
- 关联风险：RISK-PRA-002

## REQ-PRA-NEXT-03：建立权威 warm-preflight 证据链

- 来源：验收报告 / RISK-PRA-003
- 问题描述：PRA-05 旧 manifest 的 404 与后续修正证据分离，增加复核歧义。
- 需求描述：harness 在批次前生成一个权威 preflight manifest；每个样本引用其 run id 与内容 hash；非 200 preflight 必须停止批次并记录失败。
- 验收标准：manifest、raw 引用和健康检查状态一一对应，不需要从历史说明推断 server temperature。
- 优先级：P1
- 关联风险：RISK-PRA-003

## REQ-PRA-NEXT-04：在代表性证据完备后再作预算决策

- 来源：PRA-REQ-05 / RISK-PRA-001 / RISK-PRA-002
- 问题描述：当前 raw-only 聚合可重算，但不足以形成生产预算、SLA 或优化优先级。
- 需求描述：仅在 REQ-PRA-NEXT-01 与 REQ-PRA-NEXT-02 验收通过后，比较候选预算、定位主要延迟并形成需单独审批的优化任务。
- 验收标准：预算来源、环境、百分位算法、样本量、失败率和不确定性均可追溯；不得把本地最好值或旧目标标成已达成。
- 优先级：P0
- 关联风险：RISK-PRA-001、RISK-PRA-002
