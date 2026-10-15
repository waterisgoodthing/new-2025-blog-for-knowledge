# 设计文档：Dependency Runtime Governance

## 总体架构

```text
package.json + package-lock.json
          ↓
依赖树 / audit / peer contract
          ↓
Node LTS + npm ci 可复现环境
          ↓
test + tsc + Next build + OpenNext build
          ↓
Cloudflare preview
          ↓
public/private route + backend permission 回归
          ↓
发布阻断或批准部署
```

## 方案分层

### A. PostCSS 上游治理

- 先确认 Next 当前稳定版本是否已更新内部 PostCSS。
- 若官方组合可用，升级 Next/OpenNext 并验证完整构建。
- 若只有 override 可行，必须证明 npm 不报告 invalid、构建产物稳定、OpenNext 支持该组合；否则拒绝 override。
- 若短期无安全上游版本，将该风险标记为构建期残余，不声称生产 audit 清零。

### B. 工具链基线

- 记录并固定 Node LTS、npm、Wrangler、OpenNext 版本范围。
- 使用 `npm ci`，禁止依赖 `npm install` 产生未审查 lockfile 漂移。
- 将 `baseline-browser-mapping` 新鲜度、Node `DEP0205`、deprecated package 分为信息、维护、阻断三类。

### C. compatibility date

- 仅在独立提交中修改 `wrangler.toml`。
- 对比旧日期和新日期的 preview：公开首页、blog、notes、mistakes；管理路由；API 请求失败态。
- 任一权限或公开路由回归即停止更新。

### D. 发布门禁

门禁顺序：

1. `npm ci`
2. `npm audit --omit=dev`
3. `npm audit`
4. `npm ls next @opennextjs/cloudflare`
5. `npm test`
6. `npx tsc --noEmit --pretty false`
7. `npm run build:cf`
8. preview route/permission checks

只允许通过门禁的干净 commit 进入部署。

## 权限和数据设计

- Public Read Lane 保持匿名访问，不添加 AuthGate。
- Manage/Review/AI/Capture Lane 保持页面保护和后端 `get_current_admin`。
- 本任务不改变 API、数据库模型、migration 或数据过滤逻辑。

## 异常处理

- audit high/critical：阻断发布并生成风险报告。
- peer invalid：阻断发布，不用 override 隐藏。
- build/preview 失败：阻断发布，保留日志。
- Cloudflare 上传失败：不重复扩大变更，最多一次受控重试。

## 回滚

- 依赖升级失败：回滚依赖提交。
- compatibility date 失败：只回滚配置提交。
- 门禁脚本误报：修复门禁并重新验证，不跳过门禁部署。
