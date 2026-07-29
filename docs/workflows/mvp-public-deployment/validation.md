# MVP Rebuild 公网部署验证

## 当前状态

pass

## 部署信息

| 项目 | 结果 |
| --- | --- |
| commit | `1cb7c7a7` |
| Worker | `2025-blog-public` |
| route | `blog.limengyang.me/*` |
| 部署前 version | `13ece371-366f-4f98-92af-2e8568f6624c` |
| 部署后 version | `2b7cc7f0-7355-465d-b1c5-0d9f8b572e49` |
| BUILD_ID | `Gr1GjHxT-VdNouOkV0yJY` |
| 部署结论 | pass |

## 验证记录

### 部署源

- 临时 worktree：`/tmp/mvp-public-deploy-1cb7c7a7`
- detached HEAD：`1cb7c7a7611147f0b644c938e415464aad63fa6e`
- 创建后 `git status --short`：空
- `npm ci`：通过，安装 824 packages
- 当前主工作树的音乐、Batch 8、open-source closure 和部署删除未进入部署源

### 构建

1. 初次 `deploy:full` 在 `tsc` 阶段停止：clean worktree 缺少 ignored `next-env.d.ts`。
2. 运行 `npx next typegen` 后，`npx tsc --noEmit` 通过。
3. 初次 `build:cf` 在页面数据阶段停止：clean worktree 缺少 ignored `.env.production`。
4. 仅注入既有公开构建值
   `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me` 后重跑。
5. Next.js 生成 35/35 页面，OpenNext bundle 成功。

以上两次停止均发生在 Worker 上传前，没有产生半完成线上版本。

### Cloudflare

- Wrangler 登录：通过，使用环境 API Token。
- 上传：43 个新或修改静态资产，241 个资产复用。
- Worker：`2025-blog-public`
- Route：`blog.limengyang.me/*`
- workers.dev：`https://2025-blog-public.17527677392.workers.dev`
- 新 version：`2b7cc7f0-7355-465d-b1c5-0d9f8b572e49`
- Worker startup time：22 ms

### HTTP 与 API

| 检查 | 结果 |
| --- | --- |
| `/`、`/blog`、`/notes`、`/mistakes`、`/manage` | 200 |
| `/manage/dashboard`、subjects、questions、mistakes、review、attachments | 200 |
| 生产、workers.dev、本地 BUILD_ID | 三者一致 |
| `public-api.../api/health` | 200，status ok，db ok |
| 未登录 `/api/subjects` | 401 |
| 未登录 `/api/admin/attachments` | 401 |
| 公开 blog/note/mistake API 的 LT 样例命中 | 0 |

### 浏览器

- `/manage` 显示 Passkey/密码登录门。
- 未登录访问 `/manage/dashboard` 最终回到 `/manage`。
- `/mistakes` 保持公开，未显示编辑、删除、上传或复习提交操作。
- 检查期间没有浏览器 error/warn。

## 结论

commit `1cb7c7a7` 已成功部署公网。MVP Rebuild 的公开页面、管理路由入口、API
健康状态和未登录权限边界均通过部署后验证，可以进入公网日常使用观察。

本轮没有部署后端、运行生产数据库迁移或修改 Cloudflare Tunnel、DNS、Access、Passkey、
AI/OCR/BKT、完整练习、对象存储和定时任务配置。
