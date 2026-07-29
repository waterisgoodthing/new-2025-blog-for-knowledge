# 2025 Blog

这是一个个人知识库与博客系统，前端使用 Next.js App Router，后端使用 FastAPI。项目当前面向个人内容管理、笔记写作、错题复盘、博客发布、公开内容展示和后台管理。

## 来源与致谢

本仓库是在原开源项目基础上改造而来，并继续保留原项目的 MIT License 许可声明。当前仓库内可核验的许可证信息显示原版权人为 `YYsuni`。

仓库中暂未记录可核验的原项目链接或上游仓库地址，因此本文档不虚构上游 URL。若后续确认原项目地址，应在本节补充链接和更完整的致谢说明。

## 项目结构

本项目有两条主要架构线：

- `src/`：Next.js App Router 前端，包括公开页面、管理页面、写作页面和前端 API 客户端。
- `backend/`：FastAPI 后端，负责笔记、错题、复习、认证、AI、音乐推荐和可管理内容。
- `scripts/`：项目工具脚本，包括 setup/check 命令和 SVG 生成。
- `docs/`：架构文档和工作流记录。
- `.github/`：CI 工作流、Issue 模板、PR 模板。

### 后端架构

| 层 | 路径 | 职责 |
|---|---|---|
| Router | `backend/app/routers/` | HTTP 路由、状态码、依赖注入 |
| Schema | `backend/app/schemas/` | Pydantic 请求/响应契约 |
| Service | `backend/app/services/` | 业务逻辑（SM-2 复习、AI 分析、内容存储等） |
| Model | `backend/app/models/` | SQLAlchemy 数据库模型 |
| Migration | `backend/alembic/versions/` | 数据库迁移 |

### 前端架构

| 层 | 路径 | 职责 |
|---|---|---|
| Route page | `src/app/<route>/page.tsx` | 页面组件 |
| Route components | `src/app/<route>/components/` | 路由专属 UI |
| Route services | `src/app/<route>/services/` | 路络专属数据操作 |
| Shared components | `src/components/` | 跨路由共享 UI |
| API clients | `src/lib/api/` | 类型化 API 客户端 |
| Shared utils | `src/lib/` | 通用工具函数 |

## 快速开始

### 一键检查

检查前置条件，不修改任何文件：

```bash
npm run check
```

### 一键初始化（推荐新手）

引导式设置：检查前置条件、创建环境文件、安装依赖、引导数据库迁移：

```bash
npm run init
```

### 一键完整设置

包含初始化所有内容，外加可选的 AI 配置和管理员凭据设置：

```bash
npm run setup
```

### 手动设置

如果你更喜欢手动操作：

#### 1. 前端

```bash
npm install
npm run dev
```

#### 2. 后端

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

> **提示**：当前后端依赖建议使用 Python 3.12 或 3.13。不要使用 Python 3.14 创建虚拟环境；当前 `pydantic-core` 依赖集可能会在 Python 3.14 下构建失败。macOS 推荐通过 Homebrew 安装：`brew install python@3.12`。

#### 3. 数据库

确保 PostgreSQL 正在运行，然后执行迁移：

```bash
cd backend
source .venv/bin/activate   # Windows: .venv\Scripts\activate
alembic upgrade head
```

#### 4. 管理员凭据

```bash
cd backend
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m app.cli set-password
```

可选：注册 Passkey 实现无密码登录：

```bash
python -m app.cli register-passkey
```

#### 5. 启动

```bash
# 终端 1：后端
cd backend && source .venv/bin/activate && uvicorn main:app --reload

# 终端 2：前端
npm run dev
```

前端默认运行在 `http://localhost:2025`，后端默认运行在 `http://localhost:8000`。

本地开发可以使用 `NEXT_PUBLIC_API_URL=http://localhost:8000`。生产构建不能使用 localhost API 地址；运行 `npm run build` 时必须把 `NEXT_PUBLIC_API_URL` 设置为真实的非 localhost API URL。

## 验证命令

| 检查 | 命令 | 说明 |
|---|---|---|
| 前置条件检查 | `npm run check` | 检查 Node.js、Python、PostgreSQL、Docker、端口、环境文件（不修改状态） |
| 项目验证 | `npm run check:project` | TypeScript 类型检查 + Next.js 构建 + 后端导入检查 + pytest（需 PostgreSQL 运行） |
| TypeScript 检查 | `npx tsc --noEmit` | 前端类型检查 |
| 前端构建 | `npm run build` | Next.js 生产构建 |
| 后端导入检查 | `cd backend && python -c "from main import app"` | 验证后端可导入 |
| 后端测试 | `cd backend && python -m pytest tests/ -v` | 运行后端测试 |
| 数据库迁移 | `cd backend && alembic upgrade head` | 执行待处理的迁移 |
| 迁移状态 | `cd backend && alembic current` | 查看当前迁移版本 |

## 配置

### 环境变量

- 根目录 `.env`：前端变量（`NEXT_PUBLIC_API_URL`、`NEXT_PUBLIC_IMAGE_BASE_URL`）。
- `backend/.env`：后端变量（数据库、JWT、AI、CORS 等）。

参考 `.env.example` 和 `backend/.env.example` 创建本地配置。不要提交真实 `.env`、私钥、令牌或其他敏感信息。

### 关键配置项

| 变量 | 文件 | 说明 |
|---|---|---|
| `DATABASE_URL` | `backend/.env` | PostgreSQL 连接字符串 |
| `JWT_SECRET_KEY` | `backend/.env` | 会话签名密钥，生产环境必须修改 |
| `ALLOWED_ORIGINS` | `backend/.env` | CORS 来源列表，使用逗号分隔，不是 JSON 数组 |
| `NEXT_PUBLIC_API_URL` | `.env` | 后端 API 地址；本地开发可用 localhost，生产构建必须使用非 localhost URL |

### AI 配置（可选）

AI 功能通过 `npm run setup` 交互式配置，或手动编辑 `backend/.env`：

| 用途 | 环境变量组 | 当前默认模型 |
|---|---|---|
| 通用助手 | `AI_*` | Qwen3.7 Plus |
| 文本生成与分析 | `DEEPSEEK_*` | DeepSeek V4 Pro |
| 图像识别 (OCR) | `DASHSCOPE_*` | Qwen3.7 Plus |
| 图像生成 | `DASHSCOPE_IMAGE_*` | 需配置 |

支持的预设提供商：DashScope/Qwen、DeepSeek、OpenAI、OpenRouter、Gemini、xAI、Claude/Anthropic、Moonshot/Kimi、Zhipu/GLM、SiliconFlow、Volcengine/Doubao、Ollama、LM Studio。

> **注意**：Claude/Anthropic 的原生 API 不兼容 OpenAI 格式，需要兼容网关或适配器。其他预设提供商通过 OpenAI 兼容端点接入。

### 管理员凭据

| 设置 | 说明 |
|---|---|
| `JWT_SECRET_KEY` | 由 `npm run setup` 自动生成，或手动设置 |
| `ENABLE_REGISTRATION` | `true`/`false`，控制是否开放注册 |
| `REGISTRATION_KEY` | 设置后注册需要此密钥 |
| `OPERATOR_REGISTRATION_KEY` | 操作员 Passkey 注册密钥 |

## 内容真源

当前所有活跃内容域都通过后端 API 管理，并存储在 PostgreSQL 中：

| 领域 | 存储 | API |
|---|---|---|
| notes, blog, mistakes | PostgreSQL | `/api/notes` |
| about | PostgreSQL | `/api/content/about` |
| share | PostgreSQL | `/api/content/shares` |
| projects | PostgreSQL | `/api/content/projects` |
| pictures | PostgreSQL | `/api/content/pictures` |
| snippets | PostgreSQL | `/api/content/snippets` |
| bloggers | PostgreSQL | `/api/content/bloggers` |
| site settings | PostgreSQL | `/api/content/site-settings` |

`src/app/*/list.json` 和 `src/config/` 下的静态 JSON 文件只作为首次初始化数据库时的默认种子数据。实际编辑和保存都通过后端 API 持久化。

## GitHub 写入依赖

当前版本不需要 GitHub 仓库写权限即可运行或开发。历史上的 GitHub sync 写入链路已经从支持的产品流程中移除；内容编辑以 PostgreSQL 和后端 API 为准。

## 参与贡献

贡献前请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。安全问题请按 [SECURITY.md](./SECURITY.md) 中的方式私下报告。

提交 Issue 和 PR 时，GitHub 会自动引导你使用对应的模板。
