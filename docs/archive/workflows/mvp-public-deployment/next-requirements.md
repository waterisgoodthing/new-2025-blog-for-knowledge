# 下一轮需求

## REQ-NEXT-DEPLOY-01 Clean checkout 部署入口

- 来源：DEPLOY-RISK-002。
- 需求：部署入口应先执行 Next 类型生成，并明确校验生产 API URL，再进行类型检查和 OpenNext 构建。
- 验收：clean worktree 中单条受支持命令可完成构建，不依赖另一个工作树的 ignored 文件。
- 优先级：P1。

## REQ-NEXT-DEPLOY-02 依赖漏洞审计

- 来源：DEPLOY-RISK-001。
- 需求：审查 npm audit 的 10 个依赖问题，区分生产可达风险与开发依赖，并制定最小兼容升级。
- 验收：每项漏洞有包路径、可达性、处置或接受记录；不得直接运行破坏性 `npm audit fix --force`。
- 优先级：P1。

## REQ-NEXT-DEPLOY-03 登录后公网管理链路观察

- 来源：DEPLOY-RISK-003。
- 需求：在日常使用中验证登录后的 subjects、questions、mistakes、review、attachments 公网链路。
- 验收：至少完成一轮只读管理页面检查；任何后端 404/合同漂移单独建 issue。
- 优先级：P1。
