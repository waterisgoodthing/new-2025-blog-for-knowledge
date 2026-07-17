# ADR-003：Today 是统一入口与 Dashboard Orchestrator

- 状态：Accepted
- 日期：2026-07-13
- 范围：Home、Review、Capture、Learning、Mistake、Project、AI

## 决策

`/today` 是登录后的统一入口，`TodayOrchestrator` 只并行调用各领域的摘要 provider，组合行动项、处理超时和局部失败，不拥有任何领域事实和写入逻辑。

## 原因

用户需要一个明确的每日入口，但不能让入口服务吞并 Review、Capture、Project、AI 等领域的业务规则。

## 后果

每个领域必须提供稳定的 summary contract。Today 页面需要接受部分区块失败；新增领域不能直接向 Today 塞入业务逻辑，只能提供摘要 provider。

