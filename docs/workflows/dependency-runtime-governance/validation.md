# 验证报告：Dependency Runtime Governance

## 结论

本轮本地治理、发布门禁和公网部署完成。PostCSS 仍是已记录的构建期上游风险，Node 24 实测证据尚未补齐。

## 任务结果

| 任务 | 结果 | 证据 |
|---|---|---|
| P0-01 PostCSS 上游决策 | Pass with residual | Next `16.2.10` 仍解析 PostCSS `8.4.31`；invalid override 未采用 |
| P0-02 隔离回归 | Pass | 两次 `npm ci` lockfile SHA 一致；audit 0 high/0 critical；peer 通过；clean test 4/4；Cloudflare build 通过 |
| P1-03 工具链基线 | Partial pass | `.nvmrc=24`、engines Node `24.x`/npm `>=11 <12`；本机未安装 Node 24 |
| P1-04 compatibility date | Pass | 候选 `2026-07-15` preview 路由 200/307；生产日期保持 `2025-03-25` |
| P2-05 发布门禁 | Pass | dirty worktree 阻断；clean worktree audit、peer、test、build、tsc 全通过；门禁失败不会继续 deploy |
| P0-06 交付 | Pass | 公网 Worker Version ID=`303a8af2-e2e2-4949-9af3-22c86eee40f6`；workers.dev 与 `blog.limengyang.me` 的 `/`、`/mistakes`、`/notes` 关键路由返回 200 |

## 门禁修复

根因：`next-env.d.ts` 由 Next build 生成且不在 clean source 中；门禁先执行裸 TypeScript 会误报 PNG 模块缺失。另发现部署命令链未自动接入门禁，已补充 npm `predeploy` lifecycle。

修复：`scripts/predeploy-audit.mjs` 调整为：

```text
clean worktree → audit → peer → test → Cloudflare build → TypeScript
```

验证：clean worktree 的 `npm run predeploy:check` 通过；直接执行 `npm run deploy` 先完成门禁，再完成 Cloudflare build/deploy。

## 数据与部署

- 未执行 migration、DDL、DML；Alembic/数据库数据未修改；公网 Worker 已部署，版本为 `303a8af2-e2e2-4949-9af3-22c86eee40f6`。

## 残余风险

- RISK-DRG-001：Next 内置 PostCSS，等待上游安全版本。
- RISK-DRG-006：Node 24 未安装，缺少实际 Node 24 build 证据。

## 公网冒烟

- `https://2025-blog-public.17527677392.workers.dev/`：200
- `https://2025-blog-public.17527677392.workers.dev/mistakes`：200
- `https://2025-blog-public.17527677392.workers.dev/notes`：200
- `https://blog.limengyang.me/`：200
- `https://blog.limengyang.me/mistakes`：200

## 关闭声明

Batch 7 / 本轮依赖运行时治理已完成并接受。不得自动开始下一 Batch；后续工作必须重新设计、建立任务清单并获得批准。
