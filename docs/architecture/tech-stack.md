# 技术栈基线

> 核心判断：**技术栈不换，按新架构重新组织项目。**

相关文档：[功能域](./domains.md)、[数据模型](./data-model.md)、[路由](./routes.md)、[API](./api-design.md)、[权限](./permissions.md)、[前端结构](./frontend-structure.md)、[后端结构](./backend-structure.md)、[渲染系统](./rendering-system.md)、[图标系统](./icon-system.md)、[思维导图](./mindmap-system.md)。

## 1. 技术栈总览

现有 Next.js + FastAPI + PostgreSQL 主体足以承载个人知识管理与学习系统。本轮不以更换框架解决领域混合问题，而是用明确的公开端/管理端、功能域、API、数据模型和渲染边界重新组织现有能力。

| 层级 | 技术 | 目标职责 |
|---|---|---|
| Web | Next.js 16 App Router、React 19、TypeScript | 路由、页面组合、交互与类型契约 |
| 样式与状态 | Tailwind CSS 4、SWR、Zustand、Motion | 样式、服务端数据缓存、少量客户端状态与动效 |
| API | FastAPI 0.115、Python、Uvicorn | HTTP 契约、鉴权依赖与业务编排入口 |
| 数据 | SQLAlchemy 2 Async、asyncpg、Alembic、PostgreSQL | 异步持久化、事务、约束和版本化迁移 |
| 认证 | 脚本生成的管理通行密钥、服务端管理员会话 | 单管理员访问与管理操作保护 |
| 部署 | Cloudflare / OpenNext、`public-api.limengyang.me` | 前端边缘部署与独立后端服务 |

## 2. 前端技术栈

- **Next.js 16 App Router**：负责公开路由、`/manage/**` 管理路由、布局和服务端/客户端组件边界。
- **React 19**：负责组件组合和交互；业务能力进入 `features/`，路由不堆积业务逻辑。
- **TypeScript**：显式定义 public/admin DTO、渲染块和图标语义，避免依赖可变 JSON 推断。
- **Tailwind CSS 4**：提供设计 token 和布局样式，不把业务状态隐藏在样式类中。
- **SWR**：管理远端 API 数据、缓存和重新验证，不作为跨域客户端状态仓库。
- **Zustand**：仅保存确有跨组件需求的客户端状态，不复制 SWR 的服务端数据。
- **Motion**：用于有意义的状态过渡；不影响可访问性、内容阅读或 reduced-motion。

## 3. 后端技术栈

- **FastAPI 0.115 + Uvicorn**：提供 `/api/public/**` 和 `/api/admin/**`。
- **SQLAlchemy 2 Async + asyncpg**：表达目标实体、关系和异步事务；router 不直接堆积查询与业务规则。
- **Pydantic schema**：分别定义 public/admin 输入输出，不能依靠前端删掉敏感字段。
- **Service 层**：承载发布、复习、AI Run、附件和 Taxonomy 等业务规则。

## 4. 数据库与迁移

PostgreSQL 继续作为唯一业务事实来源，依靠外键、唯一约束、检查约束和索引保证一致性。Alembic 是 schema 演进的唯一正式入口；每次模型变化必须配套可升级、可回滚且经过验证的 migration。

本技术基线不执行 [迁移计划](./migration-plan.md) 的 Phase 0 数据盘点，也不批准建表、回填或切流量。

## 5. 认证与权限

- 当前目标沿用脚本生成的管理通行密钥方案，并建立可撤销、可过期的服务端管理员会话。
- 本轮不展开密码、Passkey、复杂角色或多用户认证设计；若未来调整，必须单独形成安全设计。
- `get_current_admin` 是 admin API 的真实安全边界。
- `AuthGate` 只负责管理页面体验、避免闪烁和无效请求，不能替代后端鉴权。
- public API 只返回已发布且公开的数据；AI、复习、上传和内容写入均属于 admin 能力。

完整规则见 [权限模型](./permissions.md)。

## 6. 渲染系统

目标方案是 `unified + remark + rehype` Markdown 管线，React 展示统一进入 `RichText`。Shiki 处理代码高亮，KaTeX 处理数学公式，`MermaidBlock` 处理流程图，`MindMapBlock + Markmap` 处理思维导图，`Lucide React + AppIcon` 提供语义图标。公开输出由 `rehype-sanitize + DOMPurify` 分层净化。详见 [渲染系统](./rendering-system.md)。

## 7. AI 服务

AI 是可选辅助服务，不是保存 Post、Note、Mistake 的前置条件。调用由 admin API 发起，形成可追踪 `ai_runs`，记录输入快照、模型、状态、输出、错误和重试关系。AI 输出是不可信输入：必须校验、净化并由管理员确认后才能进入业务字段。

首期不因 AI 引入独立微服务或队列平台；只有同步请求确有可靠性或延迟瓶颈且证据充分时，才另行评估异步基础设施。

## 8. 部署策略

- 前端继续通过 Cloudflare / OpenNext 部署。
- 后端继续部署至 `public-api.limengyang.me`。
- PostgreSQL 由后端访问，浏览器不直接连接数据库。
- 前后端跨域、Cookie、TLS 和缓存策略必须一起验证。
- Shiki、Mermaid、Markmap 等浏览器/构建依赖需控制服务端 bundle 边界，不能无意进入不适合的运行时。

## 9. 暂不引入的技术

本阶段不引入 GraphQL、tRPC、Prisma、MongoDB、微服务、Redis 任务队列、Celery、Kafka、Elasticsearch、向量数据库、多用户权限系统或复杂 RBAC。若未来引入，必须由已验证的容量、检索、异步或协作需求驱动，并形成独立架构决策。

## 10. 技术栈决策原则

1. 优先解决领域和契约边界，不用换框架掩盖结构问题。
2. 一个数据域只有一个权威来源，公开与管理只分契约，不复制事实。
3. 安全边界在后端；前端保护只改善体验。
4. 新依赖必须解决明确问题，评估 bundle、运行时、维护和安全成本。
5. 技术文档描述目标状态，不冒充现状实现或实施批准。
