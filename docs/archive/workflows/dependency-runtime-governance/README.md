# Dependency Runtime Governance

## 目标

承接上一轮依赖清理后的残余风险，建立可持续的依赖安全、构建工具链和 Cloudflare runtime 治理方案。

## 来源

上一轮任务组：[dependency-runtime-risk-cleanup](../dependency-runtime-risk-cleanup/README.md)

已知残余：

- Next 内置 `postcss@8.4.31` 仍产生 2 个 moderate audit 项。
- Node `DEP0205`、baseline browser mapping 和 deprecated transitive packages 需要工具链治理。
- `compatibility_date = 2025-03-25` 尚未更新。
- 当前没有部署前自动化 audit/peer contract 阻断。

## 影响架构线

- 主要：`src/` Next.js 前端与 Cloudflare OpenNext 部署链路。
- 辅助：package manager lockfile、CI/本地发布检查。
- 不涉及：FastAPI 业务线、数据库、数据模型和现有内容数据。

## 当前状态

本轮本地治理、发布门禁与公网部署已完成。Node 24 实测证据保留为后续环境任务。

## 文件

- [requirements.md](requirements.md)
- [design.md](design.md)
- [tasks.md](tasks.md)
- [risks.md](risks.md)
- [next-requirements.md](next-requirements.md)

## 硬边界

- 不使用 `npm audit fix --force`。
- 不以 invalid override 掩盖 audit 或 peer contract。
- 不更新 compatibility date，除非独立任务验证通过。
- 不新增业务能力，不进入 Batch 8，不修改数据库或部署后端。
