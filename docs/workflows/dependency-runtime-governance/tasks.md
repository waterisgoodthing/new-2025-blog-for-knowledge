# 任务清单：Dependency Runtime Governance

## 审批状态

当前状态：`PUBLIC DEPLOYED / BATCH COMPLETE`。本轮本地实现、门禁验证与公网部署均已完成。

## 任务

- [x] **P0-01 PostCSS 上游版本与可达性决策**
  - 来源需求：REQ-DRG-01
  - 涉及文件：`package.json`、`package-lock.json`、Next/OpenNext 依赖树
  - 修改内容：确认官方修复路径；必要时制定最小支持版本方案。
  - 完成标准：清零或形成有期限、可验证的风险接受决策；无 invalid override。
  - 验证方式：npm audit、npm ls、bundle/构建检查、官方版本说明。
  - 风险说明：需要等待上游，不能用不受支持版本冒险。
  - 执行结果：当前最新稳定 Next `16.2.10` 仍依赖 PostCSS `8.4.31`；OpenNext peer contract 有效；`.open-next` bundle 未发现 PostCSS 引用；invalid override 方案不采用。该风险转为构建期上游跟踪。

- [x] **P0-02 依赖升级隔离回归**
  - 来源需求：REQ-DRG-01、REQ-DRG-02
  - 涉及文件：仅依赖 manifest/lockfile，具体以 P0-01 决策为准
  - 修改内容：执行批准的最小升级。
  - 完成标准：`npm ci`、audit、peer、测试、类型检查和 Cloudflare build 通过。
  - 验证方式：干净 worktree 全链路验证。
  - 风险说明：Next/OpenNext/RSC/Markdown/Mermaid/Markmap 可能有兼容变化；首次直接执行 TypeScript 时受 Next 生成型声明影响，已由 P2-05 修复执行顺序。
  - 执行结果：两次 `npm ci` 后 lockfile SHA256 均为 `7ce3d32b6f24c6b0218938261ce3108624987a0f01c3d9e8cf9fe536cc0281f1`；peer contract 通过；生产 audit 0 high/0 critical、2 moderate；Vitest 4/4；Cloudflare build 通过；按修复后的门禁顺序 TypeScript 通过。

- [x] **P1-03 Node/npm/Wrangler 工具链基线**
  - 来源需求：REQ-DRG-02
  - 涉及文件：`package.json`、lockfile、部署文档或 CI 配置（如批准）
  - 修改内容：定义支持的 Node LTS 和可复现安装命令，分类工具链警告。
  - 完成标准：干净环境可重复安装和构建；警告均有状态。
  - 验证方式：隔离 worktree 两次 `npm ci`/build 对比。
  - 风险说明：工具链版本调整可能影响 OpenNext bundle；本机未安装 Node 24，Node 24 实际 build 待后续环境补齐。
  - 执行结果：新增 `.nvmrc`=`24`，`package.json engines` 固定 Node `24.x`、npm `>=11 <12`；当前环境 Node 26/npm 11.12.1，未执行系统级 Node 安装。

- [x] **P1-04 Cloudflare compatibility date 对比实验**
  - 来源需求：REQ-DRG-03
  - 涉及文件：临时 preview 配置；正式 `wrangler.toml` 仅在决策后修改
  - 修改内容：对比当前日期与候选新日期。
  - 完成标准：形成 keep/update 决策；公开/私有路由和权限回归通过。
  - 验证方式：Cloudflare preview、HTTP 冒烟、backend permission checks。
  - 风险说明：runtime 行为变化可能影响生产 Worker；本次决定保持生产日期，不修改 `wrangler.toml`。
  - 执行结果：候选 `2026-07-15` local preview 启动成功；`/`、`/blog`、`/notes`、`/mistakes` 返回 200；`/write-note`、`/write-mistake`、`/mistakes/review` 返回 307。候选 `2026-07-17` 超出本地 workerd 支持上限，未采用。

- [x] **P2-05 发布前审计门禁**
  - 来源需求：REQ-DRG-04
  - 涉及文件：现有 scripts/CI 配置（具体待设计确认）
  - 修改内容：增加只读审计和阻断规则，不自动升级依赖。
  - 完成标准：high/critical、invalid peer、测试/build 失败时返回非零并阻止部署。
  - 验证方式：用正常、故意失败和无关脏工作区样例测试。
  - 风险说明：门禁误报会影响发布效率，必须提供清晰错误信息；本次已修复生成型 Next 类型声明的执行顺序。
  - 执行结果：新增 `scripts/predeploy-audit.mjs`、`npm run predeploy:check` 和 `predeploy` lifecycle；dirty worktree 阻断通过；clean worktree audit、peer contract、test、Cloudflare build、TypeScript 全部通过。npm audit 输出解析已增强，high/critical 仍阻断。

- [x] **P0-06 下一轮验收与交付** `PUBLIC DEPLOYED`
  - 来源需求：所有验收标准
  - 涉及文件：`validation.md`、`risks.md`、`next-requirements.md`
  - 修改内容：记录执行证据、残余风险和下一轮需求。
  - 完成标准：所有未解决项进入风险清单；完成批准范围内的公网部署；不自动进入 Batch 8。
  - 验证方式：命令输出、路由/权限、数据库 revision、部署记录。
  - 风险说明：Node 24 尚未在本机安装，缺少 Node 24 实测证据；PostCSS moderate 项等待上游修复。
  - 执行结果：P0-01、P0-02、P1-03、P1-04、P2-05 已记录；clean worktree 完整门禁通过；Worker Version ID=`303a8af2-e2e2-4949-9af3-22c86eee40f6`；workers.dev 与自定义域名关键公共路由均返回 200。

## 审批门

仅在用户明确批准本 `tasks.md` 后开始 P0-01；每个任务完成后立即更新本文件。
