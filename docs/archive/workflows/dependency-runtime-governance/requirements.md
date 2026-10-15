# 需求文档：Dependency Runtime Governance

## 背景

上一轮已将 Next.js、DOMPurIFY 和 Undici 的主要 high 风险清理并部署公网，但生产审计仍保留 Next 内置 PostCSS 构建链的 2 个 moderate 项。构建环境还存在工具链警告，Cloudflare compatibility date 仍为旧值，发布前缺少自动化阻断规则。

## 角色

- 发布执行者：需要知道当前依赖是否可安全构建和发布。
- 管理员：需要确保依赖升级不破坏管理、认证和内容编辑流程。
- 公共访客：需要确保安全治理不封闭公开内容路由。

## 功能需求

### REQ-DRG-01 PostCSS 残余风险治理

- 输入：`npm audit --omit=dev`、Next 依赖树、上游修复版本和构建结果。
- 处理：优先等待/采用官方上游修复；必要时验证受支持的 Next/OpenNext 组合；禁止不受支持的 override。
- 输出：PostCSS 风险清零，或形成明确的构建期可达性、缓解措施和接受期限。
- 失败处理：无法安全升级时保持已知可用版本，标记风险，不阻塞公开内容读取但阻止无证据的“已清理”结论。

### REQ-DRG-02 工具链可复现治理

- 输入：Node、npm、Wrangler、OpenNext、lockfile 和构建警告。
- 处理：定义支持的 Node LTS 范围和固定的安装/构建命令，区分运行时警告与开发工具警告。
- 输出：干净 worktree 中 `npm ci` 可复现，构建日志分类稳定。
- 失败处理：版本漂移或依赖安装不一致时停止发布并记录差异。

### REQ-DRG-03 Cloudflare Runtime 日期评估

- 输入：当前 compatibility date、Cloudflare flags 变化和 OpenNext preview 回归。
- 处理：单独比较保持旧日期与更新日期的行为差异。
- 输出：保持旧日期或更新日期的书面决策及证据。
- 失败处理：出现公开/私有路由回归时不更新生产配置。

### REQ-DRG-04 发布前安全门禁

- 输入：package manifest、lockfile、依赖树、audit 和 peer contract。
- 处理：在发布前执行生产 audit、全量 audit、peer 检查、测试、类型检查和 Cloudflare build。
- 输出：可读的 pass/block 结果，阻止 high、critical 或 invalid peer contract 进入发布流程。
- 失败处理：门禁失败时禁止部署，不自动修复或扩大升级范围。

## 非功能要求

- 安全：high/critical 生产风险不得无记录进入公网。
- 兼容：公开路由仍匿名可访问，管理入口和 backend authorization 不变。
- 可回滚：依赖、runtime 配置、门禁脚本分开提交。
- 可审计：记录版本、命令、输出、部署源和残余风险。
- 数据安全：不执行 migration、DDL、DML，不改变数据库数据。

## 范围外

- 后端 Python 依赖治理。
- 数据库 schema、API contract 和业务模型。
- AI/OCR/Capture/Search/Analytics/Practice/BKT。
- UI 重构、内容迁移和 Batch 8 功能。

## 验收标准

1. PostCSS 风险有清零或明确接受证据。
2. 干净 worktree 的 Node/npm/OpenNext/Wrangler 构建可复现。
3. compatibility date 有独立决策和 preview 回归证据。
4. 发布门禁能阻断 high/critical、invalid peer 和构建失败。
5. 公开/私有路由、权限、数据库 revision 和数据基线不变。
