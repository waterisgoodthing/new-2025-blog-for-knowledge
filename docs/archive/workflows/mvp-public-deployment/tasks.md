# 任务清单：MVP Rebuild 公网部署

> 状态：P0-01 至 P0-05 已完成，公网部署与验收通过。

> 审批记录：2026-07-04，用户回复“批准执行”。

## P0-01 确认部署身份与源

- [x] 确认 Cloudflare Wrangler 已登录且可访问 Worker。
- [x] 确认部署 commit 为 `1cb7c7a7`。
- [x] 记录部署前线上状态和可用 version 证据。
- 来源需求：REQ-DEPLOY-01、REQ-DEPLOY-02。
- 完成标准：身份、commit 和目标均明确。
- 验证方式：`wrangler whoami`、Git、Cloudflare 查询。
- 执行结果：Wrangler 4.53.0 使用环境 API Token 登录成功；部署目标为 `2025-blog-public`；部署前最新 version 为 `13ece371-366f-4f98-92af-2e8568f6624c`。

## P0-02 创建隔离部署 worktree

- [x] 从 `1cb7c7a7` 创建临时 detached worktree。
- [x] 确认 worktree 干净且不包含当前未提交文件。
- [x] 使用锁文件安装依赖。
- 来源需求：REQ-DEPLOY-01。
- 完成标准：部署源可复现且范围单一。
- 验证方式：`git rev-parse HEAD`、`git status --short`、`npm ci`。
- 执行结果：worktree `/tmp/mvp-public-deploy-1cb7c7a7`，HEAD 精确匹配且 status 为空；`npm ci` 安装 824 packages 成功。npm audit 报告 10 个现有依赖漏洞（1 low、3 moderate、6 high），本轮不自动升级依赖。

## P0-03 构建并部署 Cloudflare Worker

- [x] 运行 `npx tsc --noEmit`。
- [x] 运行 `npm run build:cf`。
- [x] 运行 `npx wrangler deploy --route 'blog.limengyang.me/*'`。
- [x] 记录 Worker version、route 和命令结果。
- 来源需求：REQ-DEPLOY-02。
- 完成标准：Wrangler 明确返回成功。
- 验证方式：命令输出与 Cloudflare version 信息。
- 执行结果：首次类型检查因隔离 worktree 缺少 ignored `next-env.d.ts` 停止；运行 `next typegen` 后通过。首次 Cloudflare build 因缺少 ignored `.env.production` 停止；仅注入既有公开值 `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me` 后构建和部署成功。上传 43 个新/修改静态资产；Worker version `2b7cc7f0-7355-465d-b1c5-0d9f8b572e49`，route `blog.limengyang.me/*`。

## P0-04 公网验收

- [x] 验证首页、blog、notes、mistakes、manage。
- [x] 验证公网 API health。
- [x] 验证未登录管理员 API 仍受保护。
- [x] 验证公开页面/API 不出现私有试跑样例。
- 来源需求：REQ-DEPLOY-03。
- 完成标准：核心页面无 5xx，安全边界保持。
- 验证方式：HTTP、浏览器、API 响应。
- 执行结果：首页、blog、notes、mistakes、manage 及 6 个新 manage workspace 路由均为 200；生产域名、workers.dev 与本地构建 BUILD_ID 均为 `Gr1GjHxT-VdNouOkV0yJY`；公网 API health 为 200/db ok；未登录 subjects/attachments API 均为 401；公开 blog/note/mistake API 对 `LT-20260704` 命中 0。浏览器确认 dashboard 未登录后回到 `/manage` 登录门，公开 mistakes 页面无管理操作，控制台无 error/warn。

## P0-05 记录与清理

- [x] 完成 `validation.md`。
- [x] 记录失败、残余风险和是否允许日常使用。
- [x] 删除临时 worktree。
- 来源需求：REQ-DEPLOY-01 至 REQ-DEPLOY-03。
- 完成标准：部署可追溯，临时目录已清理。
- 验证方式：文档交叉检查、`git worktree list`。
- 执行结果：部署证据写入 `validation.md`，剩余风险与下一轮需求已记录；临时 worktree 删除成功。结论为 pass，可进入公网日常使用观察。

## 审批门

必须由用户明确批准 P0-01 至 P0-05 后才能执行公网部署。
