# 需求文档：MVP Rebuild 公网部署

## 背景

MVP Rebuild 已提交并推送，commit 为 `1cb7c7a7`，本地真实私有样例验收结论为有条件通过。
当前工作树仍包含与本轮无关的未提交音乐、部署清理和后续规划文件，因此公网部署必须从干净
commit 构建，避免扩大上线范围。

## 用户角色

- 站点所有者：需要在公网日常访问新的管理工作区和公开内容页面。
- 公开访客：继续读取公开 blog、notes、mistakes，不应看到管理员操作或私有 MVP 数据。

## 功能需求

### REQ-DEPLOY-01 干净部署源

- 输入：commit `1cb7c7a7`。
- 处理：创建临时 detached worktree，只使用该 commit 的文件和锁文件安装/构建。
- 输出：可追溯到该 commit 的 Cloudflare Worker 部署。
- 失败处理：worktree 不干净或 commit 不匹配时停止。
- 验收标准：部署目录 `git status` 干净，HEAD 为 `1cb7c7a7`。

### REQ-DEPLOY-02 构建与部署

- 输入：commit 自带的 `package-lock.json`、`open-next.config.ts`、`wrangler.toml`。
- 处理：安装锁定依赖、类型检查、OpenNext Cloudflare 构建、Wrangler 部署既有 Worker/route。
- 输出：新的 Worker version。
- 失败处理：任一命令失败即停止，不改源代码掩盖失败。
- 验收标准：Cloudflare 返回部署成功和 version 标识。

### REQ-DEPLOY-03 公网验收

- 输入：`https://blog.limengyang.me`、`https://public-api.limengyang.me`。
- 处理：检查首页、公开页面、管理入口、API health、未登录管理边界和私有数据隔离。
- 输出：公网验收证据与结论。
- 失败处理：记录实际 HTTP/页面结果；不自动修改 DNS、Tunnel、Access 或业务代码。
- 验收标准：公开页面可访问，API health 正常，管理写接口未登录受保护。

## 非功能需求

- 可追溯：记录 commit、Worker version、构建命令和公网结果。
- 安全：不输出 Cloudflare token，不启用 AUTH_BYPASS，不公开私有试跑数据或附件。
- 可回退：保留部署前 Worker version 信息；本轮不主动回退，除非部署造成明确 P0 故障且用户批准。

## 非目标

- 后端部署或数据库迁移。
- Cloudflare Tunnel、DNS、Access、Passkey 配置修改。
- AI、OCR、BKT、完整练习、对象存储、云端附件迁移。
- 音乐资产或未提交部署清理变更。
