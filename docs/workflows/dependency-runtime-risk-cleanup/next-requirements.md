# 下一轮需求文档：Dependency And Runtime Risk Cleanup

本文件将当前审计结果转换为可执行的下一轮需求。执行前仍需用户批准 `tasks.md`。

| 新需求编号 | 来源 | 需求描述 | 验收标准 | 优先级 | 关联风险 |
|---|---|---|---|---|---|
| REQ-DRC-NEXT-01 | RISK-DRC-001/002 | 升级 Next.js 到 OpenNext 支持且覆盖安全公告的稳定版本 | peer contract 有效；Next 相关 audit high/medium 清除；测试、构建、路由回归通过 | P0 | RISK-DRC-001、002 |
| REQ-DRC-NEXT-02 | RISK-DRC-003/004/005 | 清理生产传递依赖并证明 bundle 可达性 | `npm audit --omit=dev` 清零或完成逐项风险接受；Markdown/Mermaid/Markmap 回归通过 | P0 | RISK-DRC-003、004、005 |
| REQ-DRC-NEXT-03 | RISK-DRC-006/008 | 分类处理开发依赖和构建警告 | 全量 audit 与生产 audit 差异可解释；非安全警告有明确状态 | P1 | RISK-DRC-006、008 |
| REQ-DRC-NEXT-04 | RISK-DRC-007 | 独立评估并决定 Cloudflare compatibility date | 保持旧日期或更新日期均有书面理由、preview 和公网回归证据 | P1 | RISK-DRC-007 |

## 下一轮方案演进顺序

1. **P0 安全依赖持续治理**：等待 Next 上游将内置 PostCSS 更新到安全版本；期间持续监测 `npm audit --omit=dev`，不得用 invalid override 掩盖结果。
2. **P1 构建工具链治理**：单独评估 Node LTS、Wrangler、baseline-browser-mapping 和 deprecated transitive packages，保持部署环境可复现。
3. **P1 Cloudflare runtime 更新评估**：若要更新 compatibility date，单独创建配置任务，先 preview，再做公开/私有路由回归。
4. **P2 依赖供应链自动化**：增加锁文件审计、peer contract 检查和部署前阻断规则，但不引入新的业务能力。

下一轮仍需重新形成 requirements/design/tasks，并在执行前获得批准；不得自动进入 Batch 8 或其他功能开发。
