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

---

## 2026-07-29 R2 验证

状态：`DEPENDENCY FIX APPLIED / LOCAL REGRESSION IN PROGRESS`

### 基线

- `next@16.2.10`
- `@opennextjs/cloudflare@1.20.1`
- `npm audit --omit=dev`: 10 high、0 critical

### 最小升级结果

- `next@16.2.12`
- `@opennextjs/cloudflare@1.20.2`
- `@opennextjs/aws@4.1.0`
- `markdown-it@14.3.0` → `linkify-it@5.0.2`
- overrides:
  - `@node-minify/core@10.5.0`
  - `@node-minify/terser@10.5.0`
  - `minimatch@10.2.6`
  - `brace-expansion@5.0.8`
  - `postcss@8.5.24`
  - `sharp@0.35.3`

### 当前依赖证据

- `npm ls next @opennextjs/cloudflare markdown-it linkify-it
  @node-minify/core @node-minify/terser glob minimatch brace-expansion sharp
  postcss`: PASS，无 invalid。
- `npm audit --omit=dev --audit-level=high`: PASS，0 high、0 critical。
- 未使用 `npm audit fix --force`。
- 未采用 OpenNext `0.2.1` 降级建议。
- npm install 在本机 Node 26 下提示项目要求 Node 24；完整发布仍以隔离门禁
  和仓库既有 runtime contract 为准。

### 本地回归

| 检查 | 结果 |
| --- | --- |
| `npm ci` | PASS；postinstall 兼容补丁自动执行 |
| 补丁 tracer test | PASS，1/1 |
| `npm ls ...` | PASS，无 invalid |
| `npm audit` | PASS，0 vulnerabilities |
| `npm audit --omit=dev` | PASS，0 vulnerabilities |
| `npm test` | PASS，21 files / 58 tests |
| `npx tsc --noEmit --pretty false` | PASS |
| Cloudflare build | PASS，Next 16.2.12 / OpenNext 1.20.2 / 40 routes |

既有非阻塞输出：

- Node 26 对项目 Node 24 engine contract 的 `EBADENGINE` 警告。
- `module.register()` 的 `DEP0205` 警告。
- AI Runs 测试既有 React `act(...)` 警告；测试均通过。
- Wrangler compatibility date 仍为已评估的 `2025-03-25`。

### 隔离后端测试根因与修复

第一次完整门禁使用未迁移测试库，68 个失败均为缺表；迁移测试库后收敛为
2 个失败。最终根因不是依赖升级：

- admin profile HTTP 测试 override 固定管理员，但空库没有对应 `users` 行，
  正常更新返回 404。
- attachment HTTP 测试把同一固定 ID 写入 `created_by`，空库外键失败并返回
  500。

两个测试现改为创建随机临时管理员并在结束后清理。单项验证 2/2 PASS；
不再依赖源库的真实管理员身份。

### Migration Authority 025

门禁在 frontend 58/58、backend 300/300 后暴露 fresh 024 metadata drift。
只读 source `blog_db` 仍为 024 且 `alembic check` PASS，证明模型事实已经存在
于 source，但 001→024 migration chain 未完整表达。

新增 `025_align_fresh_install_metadata.py`：

- 统一 admin session 与 daily song 的 unique index contract。
- 补齐 music candidate 模型索引。
- 对 12 个已有 server-default 语义的列回填 null 后收紧 NOT NULL。
- 对 source 已存在状态使用 `IF EXISTS` / `IF NOT EXISTS`，安全 no-op。
- readiness expected revision 更新为 025。

验证：

- fresh 024→025→check：PASS。
- fresh 025→024→025→check：PASS。
- source schema-only clone 024→025→check：PASS。
- live source 024 `alembic check`：PASS；未执行 live source upgrade。

### 完整发布门禁

最终候选提交 `0613f150adbf3f7d0636d0537188f83a6469a9fa` 在 detached
worktree 中使用两个 fresh 临时数据库执行 `npm run predeploy:check`：

- frontend：58/58 PASS。
- backend：300/300 PASS（2 个既有 AsyncMock RuntimeWarning）。
- TypeScript 与 40-route Cloudflare/OpenNext build：PASS。
- 测试库与目标库：Alembic `025 (head)`。
- `alembic check`：`No new upgrade operations detected`。
- production dependency audit：0 vulnerabilities。

结论：此前 10 high 的 fail-closed 阻断已解除，可以继续精确 Git 发布。
