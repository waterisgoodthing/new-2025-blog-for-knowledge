# 任务清单：Dependency And Runtime Risk Cleanup

## 审批状态

当前状态：`PHASED COMPLETE`。依赖清理、本地回归和已批准公网部署完成；PostCSS 构建链残余风险进入下一轮持续治理。

## 任务

- [x] **P0-01 当前风险基线审计**
  - 来源需求：REQ-DRC-01 至 REQ-DRC-05
  - 涉及文件：`package.json`、`package-lock.json`、`wrangler.toml`、源代码依赖使用点
  - 结果：确认 Next `16.0.10`、OpenNext peer invalid、生产 audit 4 项、全量 audit 5 项及三类构建警告。
  - 验证：`npm audit`、`npm audit --omit=dev`、`npm ls`、代码使用点审查。

- [x] **P0-02 Next.js 安全升级与 OpenNext 契约修复**
  - 来源需求：REQ-DRC-01
  - 涉及文件：`package.json`、`package-lock.json`
  - 修改内容：升级到通过 OpenNext peer contract 且覆盖当前 Next 安全公告的稳定版本。
  - 完成标准：`npm ls` 无 invalid peer；Next 相关 high/medium audit 项消失；无强制 major 升级。
  - 验证方式：`npm ci`、`npm ls`、`npm audit --omit=dev`、`npm test`、`npx tsc --noEmit --pretty false`、`npm run build:cf`。
  - 风险说明：Next 运行时、RSC、路由和构建输出可能发生兼容变化；本次构建、测试和公网冒烟通过。
  - 执行结果：升级至 `next@16.2.10`；`npm ls` peer contract 有效；`npm test` 26/26；TypeScript check 通过；`npm run build:cf` 通过。生产 audit 从 2 high/2 moderate 降为 1 high/3 moderate。

- [x] **P0-03 生产传递依赖风险清理**
  - 来源需求：REQ-DRC-02
  - 涉及文件：依赖直接父包及 lockfile，具体路径由 P0-01/P0-02 结果决定
  - 修改内容：优先升级 Mermaid/Markmap/Cheerio 等父依赖；必要时使用最小、可解释的 override。
  - 完成标准：生产 audit 归零，或每项剩余风险有可达性和审批记录。
  - 验证方式：bundle 检查、Mermaid/Markmap/Markdown 页面回归、`npm audit --omit=dev`。
  - 风险说明：传递依赖升级可能改变图表、SVG、Markdown 渲染；本次回归通过。Next 内置 PostCSS `8.4.31` 仍产生 2 个 moderate 构建链审计项，受控 override 验证无效，已转入残余风险，不强行修改。
  - 执行结果：DOMPurify `3.4.12`、Undici `6.27.0`；生产 audit 从 4 项降为 2 项，high 从 2 降为 0；`npm test` 26/26；TypeScript check 通过；`npm run build:cf` 通过。

- [x] **P1-04 开发依赖与构建警告分类处理**
  - 来源需求：REQ-DRC-03、REQ-DRC-05
  - 涉及文件：必要时为开发依赖 manifest/lockfile；不修改业务代码
  - 修改内容：处理或明确接受 `js-yaml`、baseline browser mapping、Node `DEP0205` 和 npm deprecated warnings。
  - 完成标准：每项警告有“已清理 / 非阻塞已接受 / 另立任务”结论。
  - 验证方式：干净 `npm ci`、构建日志对比、`npm audit` 与 `npm audit --omit=dev` 对比。
  - 风险说明：不得把构建期提示误判为公网运行时漏洞，也不得隐藏真实 audit 项。
  - 执行结果：`baseline-browser-mapping@2.10.33` 为当前解析版本，提示属于数据新鲜度；Node `DEP0205` 属于 Node 26 工具链弃用；`js-yaml` 仅开发依赖；全量 audit 3 moderate、生产 audit 2 moderate，均已分类并保留在风险清单。

- [x] **P1-05 Cloudflare compatibility date 独立评估**
  - 来源需求：REQ-DRC-04
  - 涉及文件：`wrangler.toml`（仅在批准后）
  - 修改内容：评估是否从 `2025-03-25` 更新；若更新必须独立提交。
  - 完成标准：明确保持旧日期或更新日期的决策，并有 preview/公网回归证据。
  - 验证方式：Cloudflare preview、公开路由冒烟、管理入口保护检查。
  - 风险说明：runtime 行为变化可能影响 OpenNext Worker；本次决定保持现值，不引入该变量。
  - 执行结果：保留 `compatibility_date = "2025-03-25"`。当前警告非阻塞；如后续需要采用新 Workers runtime 行为，另立配置维护任务并单独 preview/回归。

- [x] **P0-06 隔离回归与公网发布**
  - 来源需求：所有验收标准
  - 涉及文件：无额外业务文件；使用干净 commit worktree
  - 修改内容：仅部署通过验证的依赖/运行时提交。
  - 完成标准：测试、类型检查、生产构建、公开/私有路由、后端权限和公网冒烟全部通过。
  - 验证方式：记录命令输出、HTTP 状态、关键页面和部署版本。
  - 风险说明：数据库 revision 和数据基线必须不变；PostCSS 构建链残余风险仍在风险清单中。
  - 执行结果：本地 Cloudflare preview 通过；公开路由 `/`、`/blog`、`/notes`、`/notes/1`、`/mistakes` 返回 200；私有/legacy 入口 `/write-note`、`/write-mistake`、`/mistakes/review` 返回预期 307；后端 auth/compatibility tests 5/5；Alembic `020 (head)`；公网部署成功，Worker Version ID `2b35849d-904b-4609-abda-86418e168aea`，主站与 workers.dev 冒烟均返回 200。

## 明确禁止

- 不执行 `npm audit fix --force`。
- 不创建 migration，不执行 Alembic、DDL、DML。
- 不修改后端权限模型，不启用 `AUTH_BYPASS`。
- 不自动进入下一 Batch。
