# Batch 7 本地试运行说明

## 目标

用于本地验证第一版 MVP 手工学习闭环。本文只覆盖本地运行，不覆盖云部署、对象存储、生产发布或
生产认证绕过。

## 前置条件

- Node.js 与 npm 可用。
- Python 3.12+ 可用。
- PostgreSQL 正在运行。
- 已从模板创建环境文件：
  - 根目录 `.env`
  - `backend/.env`
- 不提交真实 `.env`、密钥、令牌、数据库 dump 或真实上传内容。

## 快速检查

```bash
npm run check
```

该命令只检查前置条件，不应修改项目状态。

## 初始化

保守初始化：

```bash
npm run init
```

完整交互式设置：

```bash
npm run setup
```

如果手动初始化：

```bash
npm install

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd ..

cp .env.example .env
```

## 数据库迁移

确认 `backend/.env` 的 `DATABASE_URL` 指向本地 PostgreSQL 后执行：

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
alembic current
cd ..
```

## 管理员凭据

设置管理员密码：

```bash
cd backend
source .venv/bin/activate
python -m app.cli set-password
cd ..
```

可选注册 Passkey：

```bash
cd backend
source .venv/bin/activate
python -m app.cli register-passkey
cd ..
```

不要把 `AUTH_BYPASS=true` 与 `AUTH_BYPASS_ALLOW=true` 作为生产或验收通过方式。

## 启动

终端 1：后端。

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

默认后端地址：`http://localhost:8000`。

终端 2：前端。

```bash
npm run dev
```

默认前端地址：`http://localhost:2025`。

如果端口已占用，先确认占用进程是否是你预期中的本项目进程；不要随意杀掉不明进程。

## 核心链路试跑

### 1. 公开读取

- 打开 `/blog`。
- 打开 `/notes`。
- 打开 `/mistakes`。
- 未登录时不应看到编辑、删除、AI、上传或复习提交操作。

### 2. 管理登录

- 打开 `/manage`。
- 使用管理员密码或已注册 Passkey 登录。
- 未登录访问 `/manage/dashboard`、`/manage/drafts`、`/manage/review` 应进入登录入口。

### 3. 科目与知识点

- 打开 `/manage/subjects`。
- 创建科目。
- 进入科目详情，创建章节或知识点。
- 删除前应看到明确确认；有关联数据时后端应拒绝危险删除。

### 4. 题目草稿到题库

- 打开 `/manage/drafts`。
- 创建题目草稿。
- 单选/多选题至少填写两个选项。
- 进入草稿详情，保存或确认入库。
- 打开 `/manage/questions` 验证正式题目存在。

### 5. 错题与复习

- 打开 `/manage/mistakes`。
- 从 active 正式题目创建错题草稿。
- 确认入错题前应看到“会同时创建复习项”的确认。
- 打开 `/manage/review`，验证到期复习项显示与提交行为。

### 6. 附件

- 打开 `/manage/attachments`。
- 上传图片、PDF 或纯文本。
- 进入附件详情查看预览/元数据。
- 关联到 question draft、question 或 mistake。
- 标记删除前应看到确认。
- 页面应明确 OCR 第一版暂未启用，不应出现真实 OCR 操作。

### 7. Batch 6 占位

- 打开 `/manage/ai`、`/manage/jobs`、`/manage/settings`。
- 页面应说明“第一版暂未启用”。
- 不应发起模型、OCR、任务队列或设置保存请求。

## 验证命令

```bash
npx tsc --noEmit
npm run build
cd backend && source .venv/bin/activate && python -c "from main import app"
cd backend && source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

也可以运行项目封装命令：

```bash
npm run check:project
```

本地 pytest 需要 PostgreSQL 可用，且 `backend/.env` 指向正确数据库。

## 常见问题

### 前端提示 API 连接失败

- 确认后端已启动。
- 确认 `.env` 中 `NEXT_PUBLIC_API_URL=http://localhost:8000`。
- 确认后端 `ALLOWED_ORIGINS` 包含前端地址。

### 数据库迁移失败

- 确认 PostgreSQL 正在运行。
- 确认 `DATABASE_URL` 用户、密码、数据库名正确。
- 执行 `alembic current` 查看当前版本。

### 未登录访问管理页

这是预期行为。管理页应由 `AuthGate` 保护，真实写入仍由后端管理员鉴权保护。

### 公开页出现管理操作

这是阻塞问题。公开页不得展示编辑、删除、AI、上传或复习提交操作；应记录并修复。

### 端口 2025 或 8000 被占用

使用 `lsof -nP -iTCP:2025 -sTCP:LISTEN` 或 `lsof -nP -iTCP:8000 -sTCP:LISTEN` 查看进程。
确认安全后再停止对应服务。

## 不属于本地试运行的事项

- 云部署。
- 对象存储、R2、S3 或 CDN。
- 真实 AI/OCR 接入。
- BKT 或完整练习系统。
- 自动迁移或删除旧数据。
