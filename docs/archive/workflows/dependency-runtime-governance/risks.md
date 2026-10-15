# 剩余风险清单：Dependency Runtime Governance

| 风险编号 | 类型 | 风险描述 | 影响范围 | 严重程度 | 当前状态 | 是否进入本轮 |
|---|---|---|---|---|---|---|
| RISK-DRG-001 | 安全 | Next 内置 PostCSS `8.4.31` 仍有 audit moderate 项 | 构建链，当前未进入 `.open-next` Worker bundle | 中 | 已决策：等待上游安全版本 | 是 |
| RISK-DRG-002 | 维护 | Node `DEP0205` 和 deprecated transitive packages | 构建工具可维护性和未来升级成本 | 低/中 | 已分类 | 是 |
| RISK-DRG-003 | 部署 | compatibility date `2025-03-25` 较旧 | 未采用部分较新的 Workers runtime 行为 | 低/中 | 已评估：保持旧日期 | 是 |
| RISK-DRG-004 | 供应链 | 当前没有发布前 audit/peer/build 自动阻断 | 依赖风险可能随脏工作区或版本漂移重新进入部署 | 中 | 已缓解：`predeploy` lifecycle 接入阻断门禁 | 是 |
| RISK-DRG-005 | 基线 | clean worktree 直接运行 TypeScript 时缺少 Next 生成的 image type declaration | 门禁顺序错误会误阻断发布 | 中 | 已缓解：先 build 再 tsc | 否 |
| RISK-DRG-006 | 工具链 | Node 24 基线已声明但本机未安装，尚未完成 Node 24 build 证据 | 不能证明 Node 24 与当前 OpenNext bundle 完全兼容 | 中 | 部分处理，待环境补齐 | 是 |

所有风险必须在下一轮验收中转为已缓解、接受或继续进入后续需求，不能只留在对话中。
