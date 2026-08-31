# 下一步行动建议

**更新日期**：2026-08-01
**范围**：I-Series 收口后的发布准备与后续工程改进
**架构线**：共享基础设施；不在本文中变更 `src/`、`backend/` 或生产配置
**当前结论**：`DO NOT DEPLOY CURRENT DIRTY WORKTREE`

本文件将技术审计与 I-Series 工作流中的已验证事实转化为后续行动。它不是部署授权，也不替代一次在准确提交上的发布审查。当前工作树含有未提交的工作流文档和证据，因此不能通过 clean-artifact 门禁。

## 已有证据与边界

| 事项 | 已记录结论 | 主要证据 |
|---|---|---|
| 数据库权威 | runtime authority 为 `blog_v2`，revision `025`；`blog_db` 为 legacy read-only | `docs/workflows/i-series-completion-plan/README.md` |
| 数据完整性与恢复 | E-06、F-01 与恢复验证已记录为 PASS | `docs/workflows/i-series-completion-plan/validation.md` |
| 发布资格 | 历史审查为技术候选资格；当前脏工作树不可发布 | `docs/workflows/i-series-completion-plan/f02-deployment-eligibility.md` |
| 前端门禁 | `npm run predeploy:frontend` 检查 clean tree、production audit、Vitest、Cloudflare build、TypeScript 与 diff hygiene | `scripts/predeploy-gates.mjs` |
| 后端门禁 | `npm run predeploy:backend` 要求隔离的测试/目标数据库 URL，并执行 pytest、Alembic current/heads/check | `scripts/predeploy-gates.mjs` |
| 自动化 | 已有 GitHub Actions CI，覆盖前端类型/构建和后端导入/测试 | `.github/workflows/ci.yml` |

不要从历史报告中的测试数字、备份日期或外部服务状态推导当前状态。任何实际发布都必须重新运行适用的检查并保存当次输出。

## P0：下一次发布前的必需项

### 1. 形成可审查的发布候选

1. 只读核对 `git status --short`，为每一处改动划定所有者和意图。
2. 经改动所有者确认后，将本次 I-Series 文档/证据与无关工作分开；不要为了清理工作树而丢弃、覆盖或自动 stash 用户改动。
3. 在一个内容明确、工作树干净的候选提交或独立工作区中运行发布门禁。
4. 记录候选 commit SHA、分支、检查时间和检查输出。

**验收**：候选工作树为空，且所有进入候选的文件均已被确认属于该发布。

### 2. 在精确候选上运行门禁

完整门禁要求两个不同的数据库连接串，不能将测试库指向部署目标：

```bash
PREDEPLOY_BACKEND_TEST_DATABASE_URL='postgresql+asyncpg://…/isolated_test_db' \
PREDEPLOY_BACKEND_DATABASE_URL='postgresql+asyncpg://…/release_target_db' \
npm run predeploy:check
```

该命令会先要求干净工作树，随后执行前端与后端门禁。应将真实输出归档到发布工作流目录；不要手工声称“通过”。

**验收**：`npm run predeploy:check` 以零退出码完成；前端依赖审计没有 high/critical 生产依赖漏洞；目标数据库 `current`、`heads` 与 `check` 均通过。

### 3. 处理或重新验证 AI Gateway 测试警告

历史审计报告记录了 `backend/tests/test_ai_gateway.py` 的两个 AsyncMock RuntimeWarning。当前测试文件已在其中一处使用同步 `MagicMock` 替代 `session.add`，但发布前仍应以 warnings-as-errors 重跑相关测试，确认是否还有警告：

```bash
cd backend
.venv/bin/python -m pytest tests/test_ai_gateway.py -W error::RuntimeWarning
```

若复现，修复应局限在测试双（`AsyncSession.add()` 是同步方法；`commit()` 才是异步方法），并重跑该文件和全量后端测试。此建议不授权修改业务行为或生产 AI 配置。

**验收**：目标测试零 RuntimeWarning，且后端门禁在隔离测试库上通过。

### 4. 创建并演练发布前恢复点

发布前备份必须由实际部署环境的运维负责人执行。备份范围至少包括：

- 发布目标数据库的逻辑备份；
- `UPLOAD_ROOT` 指向的附件内容；
- 备份时间、候选 commit SHA、Alembic revision、校验和和保留位置；
- 在隔离环境完成一次恢复与基础完整性验证。

仓库默认配置显示附件根目录由 `UPLOAD_ROOT` 控制，不能假定草稿路径或把本地路径写入公开文档。备份产物也不得提交到仓库。

**验收**：备份可读取、校验和匹配、隔离恢复成功，并记录恢复结果和负责人。

### 5. 生产配置与最小烟雾验证

在真实启用前确认以下前提，而不是以本地默认值替代生产设置：

- `ENV=production`，JWT 密钥非默认值，`ALLOWED_ORIGINS` 不包含 `*`；
- `AUTH_BYPASS` 和 `AUTH_BYPASS_ALLOW` 不得同时为 `true`；
- 管理员写入、AI、上传与复习 API 保持后端管理员鉴权；公开读取仍仅返回已发布、未隐藏数据；
- 真实健康端点为 `GET /api/health`；如需数据库 revision、外部依赖或延迟诊断，应在独立任务中设计受保护的详细健康检查；
- 回滚目标、触发条件和负责人已经明确。

**验收**：在生产或等价预发布环境，以匿名和管理员两种会话完成必要的公开读取、管理员登录和健康检查；未授权请求不会产生错误暴露或重复 401/403 噪音。

## P1：发布后优先改进

| 改进 | 当前基础 | 建议完成标准 |
|---|---|---|
| CI 强化 | 已有 `.github/workflows/ci.yml` | 将实际门禁中可在 CI 安全执行的检查纳入 CI，并为数据库迁移使用隔离服务；不要把部署凭据置入普通 CI。 |
| 外部服务集成验证 | adapter 覆盖已有，真实 provider 状态未作为发布证据 | 新增 opt-in integration marker，只有显式注入短期凭据时运行；限制费用、请求数和日志中的敏感数据。 |
| 可观测性 | 已有 `/api/health` 与 provider health snapshot | 先定义可观测性目标、访问边界和告警负责人；避免在公共响应中泄露数据库、路径或 provider 错误详情。 |
| 发布 runbook | I-Series 含恢复与资格证据 | 把候选、备份、门禁、烟雾验证、回滚和事后记录固化为一个由负责人签核的步骤清单。 |

这些均为独立工程任务。涉及新依赖、外部平台、生产密钥、监控服务或部署工作流时，应先建立相应工作流任务并取得明确批准。

## P2：长期质量工作

1. **覆盖率度量**：先基线测量再设置按关键域划分的目标，避免仅用全局百分比驱动低价值测试。
2. **OpenAPI 文档**：核对现有 FastAPI OpenAPI 输出和认证模型后，再决定是否公开 Swagger；管理端接口不应因文档化而对匿名用户开放。
3. **性能基准**：围绕真实 API 边界和代表性数据量建立基准，记录数据库、并发和环境假设，避免直接调用 router 函数作为 HTTP 性能结论。
4. **依赖维护**：定期运行生产依赖审计，并为 Next/OpenNext、FastAPI、SQLAlchemy/Alembic 保持可回滚的升级窗口。

## 明确不在本任务中执行

- 不创建 commit、tag、分支、stash、push 或 pull request。
- 不启动部署、不改 Cloudflare、tunnel、DNS 或生产环境变量。
- 不执行数据库迁移、不修改 production 数据、不创建数据库备份。
- 不调用带费用或敏感凭据的 AI/OCR 服务。

这些动作必须由后续获得明确授权的发布或运维任务完成。

## 发布决策清单

- [ ] 候选提交与变更范围已由所有者确认。
- [ ] 候选工作树干净。
- [ ] `npm run predeploy:check` 在所需隔离数据库配置下通过。
- [ ] AI Gateway warnings-as-errors 检查已通过，或有经批准的例外记录。
- [ ] 新鲜备份、校验和与隔离恢复演练已完成。
- [ ] 生产安全配置和权限矩阵已复核。
- [ ] 健康检查、公开读取与管理员流程烟雾验证已通过。
- [ ] 回滚负责人、触发条件和目标版本已记录。

只有全部项目完成且获得单独部署授权后，才能将候选标记为可发布。

## 关联资料

- `CODEX-TECHNICAL-AUDIT-REPORT-20260801.md`：历史技术审计输入。
- `docs/workflows/i-series-completion-plan/`：I-Series 的设计、需求、任务、风险和验证记录。
- `docs/workflows/i-series-completion-plan/f02-deployment-eligibility.md`：部署资格审查。
- `scripts/predeploy-gates.mjs`：当前门禁的可执行定义。

**文档状态**：已完成；建议项待未来获得相应授权后逐项执行。
