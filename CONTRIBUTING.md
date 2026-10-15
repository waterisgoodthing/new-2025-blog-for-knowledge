# 贡献指南

感谢你考虑参与这个项目。

## 开始之前

1. Fork 并 clone 仓库。
2. 按 `README.md` 中的说明分别启动前端和后端。
3. 从 `main` 创建自己的功能分支。

## 技术栈

- 前端：TypeScript、Next.js App Router、Tailwind CSS。
- 后端：Python、FastAPI、SQLAlchemy async、Pydantic、Alembic。
- 状态和数据请求：项目已有 Zustand 和 SWR，不要为小改动引入新的状态库。

## 架构边界

请优先参考邻近文件的写法，保持改动小而聚焦。

- `src/lib/api/`：类型化 API 客户端，不放 React 组件。
- `src/app/<route>/components/`：路由内专用 UI 组件。
- `src/components/`：多个路由共享的 UI 组件。
- `backend/app/models/`：SQLAlchemy 数据库模型。
- `backend/app/schemas/`：Pydantic 请求和响应契约。
- `backend/app/routers/`：HTTP 路由、依赖注入和状态码，保持薄层。
- `backend/app/services/`：业务逻辑。

## 提交前验证

根据改动范围选择验证方式：

- 前端 TypeScript 改动：运行 `npx tsc --noEmit`。
- 前端构建敏感改动：运行 `npm run build`。
- 后端改动：在 `backend/` 目录运行 `python -c "from main import app"`，并优先运行相关测试。
- 数据库模型改动：补充或更新 `backend/alembic/versions/` 下的迁移。

如果验证失败但原因是已有问题，请在 PR 中明确说明第一处相关失败和判断依据。

## 提交 PR

1. 确认改动只覆盖本次任务范围。
2. 不要提交 `.env`、私钥、令牌、数据库备份、生成缓存或个人敏感内容。
3. 在 PR 描述中说明改了什么、为什么改、如何验证。
4. 如果改动涉及前后端契约，请同时说明后端 schema 和前端 API 类型是否已同步。

## 报告问题

请通过 GitHub issue 提供复现步骤、期望行为、实际行为和相关截图或日志。安全漏洞不要公开发 issue，请按 `SECURITY.md` 私下报告。
