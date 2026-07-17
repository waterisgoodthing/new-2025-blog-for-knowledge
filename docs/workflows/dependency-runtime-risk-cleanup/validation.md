# 验证报告：Dependency And Runtime Risk Cleanup

## 当前结论

本地依赖清理、回归验证和公网部署均通过；仍有 2 个构建链 moderate 风险作为残余风险保留，任务组进入阶段性关闭。

## 修改文件

- `package.json`：Next.js 从 `16.0.10` 升级至 `16.2.10`。
- `package-lock.json`：同步 Next.js、React DOM 及符合 semver 范围的传递依赖解析结果。
- 本轮未修改 `wrangler.toml`、后端代码、数据库或 migration。

## 依赖验证

| 检查 | 结果 |
|---|---|
| `npm ls next @opennextjs/cloudflare` | 通过；Next `16.2.10` 满足 OpenNext peer contract |
| DOMPurify | `3.4.12` |
| Undici | `6.27.0`（Markmap/Cheerio 路径） |
| `npm audit --omit=dev` | 2 moderate、0 high、0 critical；剩余为 Next 内置 PostCSS 构建链 |
| `npm audit` | 3 moderate、0 high、0 critical；另含开发依赖 js-yaml |
| Next→PostCSS override | 已试验并撤销；会产生 invalid 依赖解析，不纳入提交 |

## 自动化验证

- `npm test`：8 个 test files，26 tests passed。
- `npx tsc --noEmit --pretty false`：通过。
- `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me npm run build:cf`：通过，生成 40 个 App Router routes。
- Backend targeted auth/compatibility tests：5 passed。
- `PYTHONPATH=. .venv/bin/alembic current`：`020 (head)`。

## 本地 preview 验证

- Public read：`/`、`/blog`、`/notes`、`/notes/1`、`/mistakes`：HTTP 200。
- Private/legacy：`/write-note` → `/manage/dashboard`，`/write-mistake` → `/manage/capture`，`/mistakes/review` → `/manage/review`，均为 HTTP 307。
- Public HTML：未发现已知 admin review/attachment/AI/Capture API、401 或 403 标记。

## 数据与部署边界

- 未执行 migration、DDL、DML 或数据修改。
- 已执行公网部署，详见下方公网部署证据。
- 当前工作区原有的其他未提交改动未纳入本任务验证范围。

## 公网部署证据

- 构建源：基于已推送提交 `57d7a55` 的干净 worktree，仅注入本轮依赖升级。
- Worker Version ID：`2b35849d-904b-4609-abda-86418e168aea`。
- `https://2025-blog-public.17527677392.workers.dev/`：HTTP 200。
- `https://2025-blog-public.17527677392.workers.dev/mistakes`：HTTP 200。
- `https://2025-blog-public.17527677392.workers.dev/notes`：HTTP 200。
- `https://blog.limengyang.me/`：HTTP 200。
- `https://blog.limengyang.me/mistakes`：HTTP 200。

## 未关闭风险

- Next 内置 `postcss@8.4.31` 的 2 个 moderate audit 项仍待上游/安全兼容方案。
- `compatibility_date = 2025-03-25` 已评估为当前非阻塞，保持不变。
- npm deprecated 和 Node `DEP0205` 已分类为工具链维护项。
