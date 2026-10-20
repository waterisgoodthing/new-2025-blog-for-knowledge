# 剩余风险清单：Dependency And Runtime Risk Cleanup

| 风险编号 | 类型 | 描述 | 影响 | 严重度 | 状态 | 是否进入本轮 |
|---|---|---|---|---|---|---|
| RISK-DRC-001 | 安全 | Next `16.0.10` 命中 App Router/Server Components 安全公告 | 公网 Worker 可能受 DoS 或相关 Next 漏洞影响 | 高 | 已缓解：升级至 `16.2.10` | 是 |
| RISK-DRC-002 | 兼容 | `next@16.0.10` 不满足 OpenNext `1.20.1` peer 范围 | 后续构建/运行兼容性不受支持 | 高 | 已缓解：peer contract 有效 | 是 |
| RISK-DRC-003 | 安全 | DOMPurify `3.4.7` 经 Mermaid 引入 | 恶意图表/HTML 输入场景存在条件性 XSS/配置污染风险 | 中 | 已缓解：升级至 `3.4.12` | 是 |
| RISK-DRC-004 | 安全 | Undici `6.26.0` 经 Markmap/Cheerio 引入 | 是否进入生产 bundle 尚未完全确认 | 高 | 已缓解：升级至 `6.27.0` | 是 |
| RISK-DRC-005 | 安全 | PostCSS `8.4.31` 为 Next 内部依赖 | 主要为构建链风险，audit 仍保留 2 个 moderate 项 | 中 | 部分处理：无可靠 override，待上游版本 | 是 |
| RISK-DRC-006 | 安全 | js-yaml `4.1.1` 仅开发依赖 | 当前不确认影响公网运行时 | 中 | 已分类并接受为开发链风险 | 是 |
| RISK-DRC-007 | 部署 | Cloudflare compatibility date 为 `2025-03-25` | 未采用较新的 Workers runtime 行为 | 低/中 | 已评估：当前保持并接受 | 是 |
| RISK-DRC-008 | 工具链 | baseline browser mapping、Node DEP0205、npm deprecated warnings | 影响维护性和构建噪音，不构成当前运行故障 | 低 | 已确认非阻塞并归档 | 否 |

## 决策规则

- 未验证 bundle 可达性前，不将 RISK-DRC-004 标记为无影响。
- 未完成 Next 升级和路由回归前，不关闭 RISK-DRC-001/002。
- 若升级需要 schema、migration 或数据修改，立即停止并生成单独决策报告。
