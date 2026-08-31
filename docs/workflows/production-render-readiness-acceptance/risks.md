# Residual Risks

## RISK-PRA-001

- 风险类型：性能与可观测性
- 风险描述：E0、L20、D1、M30 的全部有效样本都没有浏览器 LCP entry；当前聚合只能把 LCP 标记为 `not_available`，不能判断或预算首个主要内容绘制体验。
- 影响范围：PRA-REQ-04、PRA-REQ-05、F4 性能基线与预算决策。
- 严重程度：高
- 当前状态：未处理；空值被正确保留，未误写为 0。
- 建议措施：在不改变页面行为的前提下，先验证 PerformanceObserver 注册时机、页面是否存在合格 LCP candidate，以及 Chromium headless 条件；若 LCP 不适用于这些页面，需单独批准并冻结替代指标合同后重新采样。
- 是否进入下一轮需求：是。

## RISK-PRA-002

- 风险类型：性能与部署外推
- 风险描述：主聚合只有 browser-cold/server-warm 的本地隔离样本，没有 server-cold 主样本，也没有 CDN、移动网络、地理延迟或生产数据分布证据。
- 影响范围：冷启动、尾延迟、生产预算、SLA 与 production-readiness 结论。
- 严重程度：高
- 当前状态：部分处理；本地隔离矩阵可重算，但外推边界已明确限制。
- 建议措施：在另行批准的非生产或受控 staging 环境中采集分离的 server-cold 矩阵，并记录网络、主机、数据量和缓存状态；不得混入现有 warm aggregate。
- 是否进入下一轮需求：是。

## RISK-PRA-003

- 风险类型：证据可审计性
- 风险描述：PRA-05 的三个原始 scenario manifest 仍记录早期 warm probe `404`，而修正后的 health check 与有效 raw 证据被单列；样本本身只有 `server_temperature=warm` 标签，没有逐条 warm-probe 对象。
- 影响范围：第三方复核 server-warm 前置条件时需要跨文件解释，容易误读。
- 严重程度：中
- 当前状态：部分处理；历史 404 未删除，修正证据和说明已保留。
- 建议措施：下轮 harness 在开始批次前写入唯一权威 preflight manifest，并在每条 raw 中引用其 run id/hash；preflight 非 200 时不得启动批次。
- 是否进入下一轮需求：是。

## RISK-PRA-004

- 风险类型：样本有效性
- 风险描述：E0 保留 1 个因初版 DOM 计数规则错误而失败的样本，失败率为 `1/11`；该行属于 harness 分类失败，不代表页面功能失败。
- 影响范围：E0 failure-rate 解读。
- 严重程度：低
- 当前状态：已缓解；失败行、原因和修正规则均保留，未从聚合中静默删除。
- 建议措施：未来运行在批次前执行单条合同 smoke，并将 smoke 与主矩阵物理分离；当前历史行继续保留。
- 是否进入下一轮需求：否，明确归档为历史 harness 证据。
