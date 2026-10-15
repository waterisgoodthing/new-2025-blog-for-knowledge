# 设计文档：MVP Rebuild 公网部署

## 总体流程

```text
确认 commit 与 Cloudflare 身份
→ 创建临时 detached worktree
→ npm ci
→ npx tsc --noEmit
→ npm run build:cf
→ npx wrangler deploy --route 'blog.limengyang.me/*'
→ 验证公网前端与 API
→ 记录 Worker version
→ 删除临时 worktree
```

## 隔离设计

- 当前主工作树保持不变。
- 临时 worktree 从 `1cb7c7a7` 创建，不叠加任何未提交文件。
- 依赖按该 commit 的 `package-lock.json` 使用 `npm ci` 安装。
- 构建和部署只在临时 worktree 内执行。
- 完成或失败后移除临时 worktree。

## 部署目标

- Worker：`2025-blog-public`
- Route：`blog.limengyang.me/*`
- Workers dev URL：由 Wrangler 输出记录。
- 公网 API：只验证 `public-api.limengyang.me`，本轮不部署后端。

## 验收设计

- HTTP：`/`、`/blog`、`/notes`、`/mistakes`、`/manage`。
- API：`/api/health`。
- 未登录管理边界：至少一个管理员 API 返回 401/403。
- 页面：确认部署后的 manage workspace 路由存在。
- 私有边界：不在公开 API/页面搜索 `LT-20260704` 样例。

## 异常与停止条件

- Wrangler 未登录或无权限：停止。
- clean worktree HEAD 不匹配：停止。
- 类型检查或构建失败：停止。
- Worker 上传失败：停止并记录。
- 公网核心页面出现 5xx：记录为 P0，不自动改代码。
- 后端 API 不健康：记录为独立公网后端问题，不修改 Tunnel/DNS。
