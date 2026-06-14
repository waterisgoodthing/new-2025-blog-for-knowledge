# 2025 Blog

这是一个个人知识库与博客系统，前端使用 Next.js App Router，后端使用 FastAPI。项目当前面向个人内容管理、笔记写作、错题复盘、博客发布、公开内容展示和后台管理。

## 来源与致谢

本仓库是在原开源项目基础上改造而来，并继续保留原项目的 MIT License 许可声明。当前仓库内可核验的许可证信息显示原版权人为 `YYsuni`。

仓库中暂未记录可核验的原项目链接或上游仓库地址，因此本文档不虚构上游 URL。若后续确认原项目地址，应在本节补充链接和更完整的致谢说明。

## 项目结构

本项目有两条主要架构线：

- `src/`：Next.js App Router 前端，包括公开页面、管理页面、写作页面和前端 API 客户端。
- `backend/`：FastAPI 后端，负责笔记、错题、复习、认证、AI、音乐推荐和可管理内容。

## 本地开发

### 前端

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

前端默认使用项目脚本中的端口配置。

### 后端

进入后端目录并创建本地虚拟环境：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

复制环境变量模板：

```bash
cp .env.example .env
```

启动后端：

```bash
uvicorn main:app --reload
```

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

## 配置

后端配置放在 `backend/.env` 中。不要提交真实 `.env`、私钥、令牌、数据库凭据或其他敏感信息。可以参考 `backend/.env.example` 创建本地配置。

关键配置项：

- `DATABASE_URL`：PostgreSQL 连接字符串。
- `JWT_SECRET_KEY`：会话签名密钥，生产环境必须修改。
- `ALLOWED_ORIGINS`：允许访问后端的 CORS 来源列表。
- `AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL`：可选 AI 功能配置。

## GitHub 写入依赖

当前版本不需要 GitHub 仓库写权限即可运行或开发。历史上的 GitHub sync 写入链路已经从支持的产品流程中移除；内容编辑以 PostgreSQL 和后端 API 为准。

## 参与贡献

贡献前请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。安全问题请按 [SECURITY.md](./SECURITY.md) 中的方式私下报告。
