# 设计文档：Dependency And Runtime Risk Cleanup

## 总体策略

本任务组采用“依赖树确认 → 最小升级 → 隔离构建 → 页面/API 回归 → 公网发布”的单向门禁。依赖安全升级和 Cloudflare compatibility date 分为两个可独立回滚的变更组。

```text
审计基线
  ├─ Next/OpenNext 契约与 Next 安全升级
  ├─ 生产传递依赖可达性与升级
  ├─ 开发依赖风险分类
  └─ Cloudflare compatibility date 单独决策
          ↓
隔离 worktree 构建/测试
          ↓
公开/私有路由与后端权限回归
          ↓
审批后公网部署
          ↓
部署后冒烟与风险关闭
```

## 依赖变更设计

### Next.js 与 OpenNext

- 当前 `next@16.0.10` 与 OpenNext peer 范围不匹配，优先升级到经 audit 和 OpenNext 支持的稳定版本。
- 同步更新 lockfile，不直接手工编辑 lockfile。
- React、React DOM、OpenNext、Wrangler 的版本关系必须通过 `npm ls` 和构建验证。
- 不使用 `npm audit fix --force`，不接受自动引入 major 版本或无关依赖重写。

### 传递依赖

- `dompurify`：由 Mermaid 引入，检查 Mermaid 运行时和生成 SVG 的行为；升级后验证公开 Markdown/图表渲染。
- `undici`：由 Markmap/Cheerio 引入，确认是否进入 Worker/server bundle 或仅为客户端/构建依赖；根据证据决定升级父依赖或记录剩余风险。
- `postcss`：优先随 Next.js 版本升级处理，验证 Tailwind 和生产 CSS 输出。
- `js-yaml`：开发链路依赖，单独记录，不因开发期 audit 项修改生产运行时。

## 路由和权限回归设计

### Public Read Lane

验证匿名访问：`/`、`/blog`、`/notes`、`/notes/[id]`、`/mistakes`。确认不出现 401/403，不请求 admin review/attachment/AI/Capture API。

### Private Manage Lane

验证 `/manage/**`、`/manage/review`、`/manage/attachments`、`/manage/ai`、`/manage/capture` 仍有页面级保护，后端 mutation 继续依赖真实权限检查。

### Legacy redirects

验证 `/write-note`、`/write-note/[slug]`、`/write-mistake`、`/write-mistake/[slug]` 和 `/mistakes/review` 的现有 redirect/notice 行为不变。

## Cloudflare compatibility date 设计

- 不与 Next.js 升级同一提交强绑定。
- 先在隔离 worktree 使用当前日期配置构建并执行 preview/冒烟。
- 只有发现明确收益且回归通过，才创建独立配置提交。
- 若无足够证据，保持 `2025-03-25`，把警告标为“非阻塞、待维护”。

## 失败与回滚

- 安全升级后 build 失败：停止，不部署，保留失败日志。
- 公共页面 4xx/5xx 或私有页面泄露：停止，回到已知公网版本。
- Cloudflare runtime 行为变化：只回滚 compatibility date 提交，不回滚无关依赖。
- audit 仍有 high：不得标记“清理完成”，转入剩余风险和决策报告。

## 数据边界

本设计不触碰 `backend/alembic/`、数据库 schema、业务数据、附件存储或后端权限实现。
# 2026-07-29 R2 设计增量

## 目标

恢复 `npm run predeploy:check` 的 fail-closed 通过状态，并继续既定 Git 推送
与公网部署流程。

## 依赖策略

1. 将 Next 从 `16.2.10` 升级到当前稳定补丁 `16.2.12`，处理 Next、
   内置 PostCSS 与 Sharp 公告。
2. 将 OpenNext Cloudflare 从解析版本 `1.20.1` 升级到当前稳定补丁
   `1.20.2`，采用其新版 Glob 路径。
3. 让 Markdown-it 解析到 `14.3.0` / `linkify-it>=5.0.2`。
4. 若 OpenNext AWS 仍解析受影响的 `@node-minify/core@8.0.6`，只允许
   精确 override 到当前安全主线，并以 `npm ls`、前端测试、TypeScript、
   Cloudflare build 和隔离完整门禁共同证明兼容。
5. 不以移动生产依赖到 devDependencies、忽略 audit、降低 audit 等级或
   `npm audit fix --force` 绕过门禁。

## 回退与停止条件

- 依赖树 invalid、测试/类型/build 失败：撤销本轮候选依赖变更并重新诊断。
- audit 仍有 high/critical：不推送、不部署。
- OpenNext override 导致构建行为漂移：不保留 override，等待上游修复或采用
  经验证的替代部署工具版本。
- 不修改 backend 业务代码、schema、migration、源数据库或生产数据。

## 隔离门禁发现的测试依赖

完整门禁在空白且已迁移的测试库中发现两个 HTTP 测试依赖固定生产管理员
UUID。修复范围仅限测试：每个用例创建随机临时管理员、完成 API 行为后按
外键顺序清理。不得通过向测试库复制生产管理员或改松外键来让测试通过。

## 024 Fresh-Install Metadata Drift

只读对比证明 live source 024 与 SQLAlchemy metadata 一致，但从 001→024
新建的数据库缺少同一组索引与 NOT NULL 约束。新增 025 只用于把 migration
authority 补齐到已存在的模型/source 事实：

- 对 source 已存在的索引、约束和 NOT NULL 状态必须幂等 no-op。
- 对 fresh 024 创建模型要求的索引，替换旧 unique constraint 命名，并补齐
  NOT NULL。
- nullable 收紧前以既有 server-default 语义回填 null，不能静默删除行。
- upgrade/downgrade 均在隔离数据库验证；本轮不迁移 live source。
