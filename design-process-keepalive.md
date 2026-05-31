# 进程保活与公网连接稳定性设计文档

> 来源：进程保活与公网连接稳定性需求文档。基于只读审查结果。

---

## 1. 现状确认

### 1.1 关键发现

| 项目 | 状态 | 来源 |
|---|---|---|
| 前端启动脚本 | `pnpm dev` → `next dev --turbopack -p 2025` | `package.json` |
| 前端生产脚本 | `pnpm build` → `next build`；`pnpm start` → `next start` | `package.json` |
| 后端启动命令 | `.venv/bin/python -m uvicorn main:app --reload --port 8000` | ps aux |
| API baseURL | `process.env.NEXT_PUBLIC_API_URL \|\| "http://localhost:8000"` | `src/lib/api/client.ts:1` |
| 后端 .env 加载方式 | pydantic-settings `env_file=".env"`，应用自行读取，不依赖 shell 环境变量 | `backend/app/config.py` |
| 后端保活配置 | `KEEP_ALIVE_ENABLED=true`，间隔 300s，URL `http://limengyang.me/api/health` | `backend/.env` |
| PostgreSQL | launchd 管理，KeepAlive=true，RunAtLoad=true | brew services |
| Redis | launchd 管理，KeepAlive=true，RunAtLoad=true | brew services |
| cloudflared 账号 | 已登录，named tunnel `blog-tunnel` 已存在 | `cloudflared tunnel list` |
| cloudflared 当前 | 使用 quick tunnel（未使用 named tunnel） | ps aux |
| Docker | 未使用 | docker ps 不存在 |
| pm2 | 未安装 | pm2 list 不存在 |
| nginx | 未使用 | 无进程 |

### 1.2 named tunnel 已存在

```
ID:   e8ca3989-62b6-4324-bf71-447fd1774a25
NAME: blog-tunnel
CREATED: 2026-05-28
credentials-file: /Users/limengyang/.cloudflared/e8ca3989-62b6-4324-bf71-447fd1774a25.json
```

可以跳过注册 Cloudflare 账号步骤，直接配置 ingress 规则。

### 1.3 后端 .env 加载方式确认

后端使用 `pydantic-settings`，配置如下：

```python
# backend/app/config.py
class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

这意味着后端自行读取 `backend/.env` 文件，**不依赖 shell 环境变量**。launchd plist 中不需要显式配置 `.env` 中的变量，只需确保 `WorkingDirectory` 指向 `backend/` 目录即可。

---

## 2. 设计方案

### 2.1 整体架构

```text
用户浏览器
→ Cloudflare Edge (固定域名)
→ cloudflared (named tunnel, launchd 管理)
→ 本机路由规则：
   blog.域名 → localhost:2025 (前端)
   api.域名  → localhost:8000 (后端)
→ 前端 Next.js (生产构建, launchd 管理)
→ 后端 uvicorn (无 reload, launchd 管理)
→ PostgreSQL (launchd, 已有)
→ Redis (launchd, 已有)
```

### 2.2 服务管理方式

| 服务 | 管理方式 | 启动命令 | 端口 | 自动重启 | 开机自启 |
|---|---|---|---|---|---|
| PostgreSQL | launchd (已有) | `postgres -D ...` | 5432 | 是 | 是 |
| Redis | launchd (已有) | `redis-server ...` | 6379 | 是 | 是 |
| 后端 uvicorn | launchd (新建) | `uvicorn main:app --host 127.0.0.1 --port 8000` | 8000 | 是 | 是 |
| 前端 Next.js | launchd (新建) | `next start -p 2025` | 2025 | 是 | 是 |
| cloudflared | launchd (新建) | `cloudflared tunnel run blog-tunnel` | - | 是 | 是 |

---

## 3. 详细设计

### 3.1 REQ-01：固化后端运行方式

**plist 文件**：`~/Library/LaunchAgents/com.blog.backend.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.blog.backend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/limengyang/2025-blog-public/backend/.venv/bin/uvicorn</string>
        <string>main:app</string>
        <string>--host</string>
        <string>127.0.0.1</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/limengyang/2025-blog-public/backend</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>/Users/limengyang/2025-blog-public/backend</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/blog-backend.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/blog-backend.log</string>
</dict>
</plist>
```

**环境变量说明**：
- 后端通过 `pydantic-settings` 自行读取 `backend/.env`，不依赖 shell profile
- plist 中只需设置 `PYTHONPATH`（确保 `import app` 可用）
- 不需要在 plist 中复制 `.env` 中的密钥

**关键变更**：
- 去掉 `--reload`
- 绑定 `127.0.0.1`（不暴露公网）
- KeepAlive=true（崩溃自动重启）
- RunAtLoad=true（开机自启）

**验收**：
- `curl http://127.0.0.1:8000/health` 返回正常
- `launchctl list | grep blog.backend` 有进程
- 日志在 `/tmp/blog-backend.log`

---

### 3.2 REQ-02：固化前端运行方式

**plist 文件**：`~/Library/LaunchAgents/com.blog.frontend.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.blog.frontend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/node</string>
        <string>/Users/limengyang/2025-blog-public/node_modules/.bin/next</string>
        <string>start</string>
        <string>-p</string>
        <string>2025</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/limengyang/2025-blog-public</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/blog-frontend.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/blog-frontend.log</string>
</dict>
</plist>
```

**关键变更**：
- 从 `pnpm dev` 改为 `next start -p 2025`
- 需要先 `pnpm build`
- KeepAlive=true

**注意**：`next start` 的端口通过命令行 `-p 2025` 传入，因为 `package.json` 的 `start` 脚本未指定端口。

**验收**：
- `curl http://127.0.0.1:2025` 返回 HTML
- `launchctl list | grep blog.frontend` 有进程
- 日志在 `/tmp/blog-frontend.log`

---

### 3.3 REQ-03：固化 cloudflared 运行方式

**已有的 named tunnel**：

```
ID:   e8ca3989-62b6-4324-bf71-447fd1774a25
NAME: blog-tunnel
```

**第一步：配置 ingress 规则**

创建 `~/.cloudflared/config.yml`：

```yaml
tunnel: e8ca3989-62b6-4324-bf71-447fd1774a25
credentials-file: /Users/limengyang/.cloudflared/e8ca3989-62b6-4324-bf71-447fd1774a25.json

ingress:
  - hostname: blog.域名
    service: http://localhost:2025
  - hostname: api.域名
    service: http://localhost:8000
  - service: http_status:404
```

域名需要用户确认（见第 5 节）。

**第二步：配置 DNS**

在 Cloudflare DNS 中添加 CNAME 记录：
- `blog.域名` → `e8ca3989-62b6-4324-bf71-447fd1774a25.cfargotunnel.com`
- `api.域名` → `e8ca3989-62b6-4324-bf71-447fd1774a25.cfargotunnel.com`

CNAME 目标必须是 `<tunnel-uuid>.cfargotunnel.com`：
- 不要指向 `trycloudflare.com` 临时域名
- 不要指向 `localhost`

**DNS 验收**：

```bash
dig blog.域名 CNAME
dig api.域名 CNAME
```

**第三步：ingress 验证（前台运行，不加载 launchd）**

```bash
# 验证配置语法
cloudflared tunnel ingress validate

# 验证路由规则
cloudflared tunnel ingress rule https://blog.域名
cloudflared tunnel ingress rule https://api.域名

# 前台运行测试（Ctrl+C 可停止）
cloudflared tunnel run blog-tunnel
```

确认 `blog.域名` 和 `api.域名` 都可访问后，再交给 launchd。

**第四步：plist 文件**

`~/Library/LaunchAgents/com.blog.tunnel.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.blog.tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
        <string>blog-tunnel</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/blog-tunnel.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/blog-tunnel.log</string>
</dict>
</plist>
```

**验收**：
- `launchctl list | grep blog.tunnel` 有进程
- 固定域名可访问前端和后端
- 重启后域名不变

---

### 3.4 REQ-04：确认前端 API 地址

**当前状态**：

```typescript
// src/lib/api/client.ts:1
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
```

**问题**：公网用户访问前端时，如果没有设置 `NEXT_PUBLIC_API_URL`，浏览器会尝试连接用户自己电脑的 `localhost:8000`，API 调用全部失败。

**强制规则**：

1. `pnpm build` **前**必须确认 `NEXT_PUBLIC_API_URL` 已设置为后端公网地址
2. 构建**后**浏览器 Network 面板中不得出现 `http://localhost:8000`
3. 如果 API 域名变化，**必须重新** `pnpm build`
4. 仅修改 `.env` 后不重新 build，对已构建前端**无效**

**构建命令**：

```bash
NEXT_PUBLIC_API_URL=https://api.域名 pnpm build
```

**推荐**：双域名方案（`blog.域名` + `api.域名`），通过 cloudflared ingress 按 hostname 路由。

---

### 3.5 REQ-05：后端 worker 策略

**当前**：单 worker（默认）。

**建议**：
- 短期保持单 worker，先确保保活稳定
- 后续评估 `--workers 2`
- 检查项：是否有全局状态、内存缓存、定时任务副作用

**已知风险**：
- `KEEP_ALIVE_ENABLED=true` 会启动定时任务，多 worker 会重复执行
- 如果启用多 worker，需先将 keep_alive 改为仅在主进程执行

---

### 3.6 REQ-07：日志路径

| 服务 | 日志路径 | 查看命令 |
|---|---|---|
| 后端 | `/tmp/blog-backend.log` | `tail -f /tmp/blog-backend.log` |
| 前端 | `/tmp/blog-frontend.log` | `tail -f /tmp/blog-frontend.log` |
| cloudflared | `/tmp/blog-tunnel.log` | `tail -f /tmp/blog-tunnel.log` |
| PostgreSQL | `/opt/homebrew/var/log/postgresql@16.log` | `tail -f /opt/homebrew/var/log/postgresql@16.log` |
| Redis | `/opt/homebrew/var/log/redis.log` | `tail -f /opt/homebrew/var/log/redis.log` |

日志轮转：macOS launchd 日志文件会持续增长。长期运行建议配置 newsyslog 或定期清理。

---

### 3.7 REQ-08：服务状态检查命令

```bash
# 检查 launchd 服务状态
launchctl list | grep blog

# 检查端口监听
lsof -i :2025 -P -n | grep LISTEN
lsof -i :8000 -P -n | grep LISTEN

# 健康检查
curl -s http://127.0.0.1:8000/health
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:2025

# 查看日志
tail -n 80 /tmp/blog-backend.log
tail -n 80 /tmp/blog-frontend.log
tail -n 80 /tmp/blog-tunnel.log
```

---

## 4. 实施批次

### 执行阶段边界

| 阶段 | 允许执行 | 不允许执行 |
|---|---|---|
| D0 只读确认 | 只读命令 | 任何写操作、构建、启动 |
| D1 本地演练 | launchctl load、pnpm build、pnpm start | 停止旧进程、修改 DNS |
| D2 named tunnel 演练 | cloudflared 配置、前台运行测试 | 停止旧进程 |
| D3 正式切换 | launchctl load tunnel、停止旧 Kilo 进程 | - |
| D4 运维增强 | 日志轮转、健康检查脚本 | - |

---

### D0：只读确认

只读阶段**不得执行** `pnpm build`、`pnpm start`、`launchctl load`、`cloudflared tunnel run`。

- [ ] 确认域名选择（需用户决策）
- [ ] 确认 `NEXT_PUBLIC_API_URL` 值（需先确定域名）
- [ ] 确认 `package.json` 的 `build`/`start` 脚本（已确认）
- [ ] 确认后端 `main:app` 路径（已确认）
- [ ] 确认后端 `.env` 加载方式（已确认：pydantic-settings 自行读取）
- [ ] 确认 cloudflared 已登录且 named tunnel 存在（已确认）
- [ ] 确认 credentials 文件存在（已确认）
- [ ] 确认 `next start` 阶段所需环境变量（已确认：无额外运行时环境变量需求）

---

### D1：本地 launchd 演练

**目标**：验证 launchd 管理的服务在本地可正常运行。**不切换公网，不停止旧 Kilo 进程。**

- [ ] 创建 `com.blog.backend.plist`
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.backend.plist`
- [ ] 验证：`curl http://127.0.0.1:8000/health` 返回正常
- [ ] 确认 `NEXT_PUBLIC_API_URL` 已设置
- [ ] `pnpm build`（构建时注入 `NEXT_PUBLIC_API_URL`）
- [ ] 创建 `com.blog.frontend.plist`
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.frontend.plist`
- [ ] 验证：`curl http://127.0.0.1:2025` 返回 HTML
- [ ] 验证：`launchctl list | grep blog` 显示两个服务
- [ ] 验证：`tail /tmp/blog-backend.log` 和 `/tmp/blog-frontend.log` 无异常
- [ ] **不停止旧 Kilo 进程**
- [ ] **不切换公网 tunnel**

**回退**：如果 launchd 服务失败，`launchctl unload` 卸载 plist，继续使用 Kilo 管理。

---

### D2：named tunnel 演练

**目标**：验证 named tunnel 配置正确，域名可访问。**不停止旧 Kilo 进程。**

- [ ] 确认域名（需用户决策）
- [ ] 创建 `~/.cloudflared/config.yml`
- [ ] `cloudflared tunnel ingress validate`（验证配置语法）
- [ ] `cloudflared tunnel ingress rule https://blog.域名`（验证路由规则）
- [ ] `cloudflared tunnel ingress rule https://api.域名`（验证路由规则）
- [ ] 配置 Cloudflare DNS CNAME 记录
- [ ] 验证 DNS：`dig blog.域名 CNAME` 和 `dig api.域名 CNAME`
- [ ] 前台运行测试：`cloudflared tunnel run blog-tunnel`
- [ ] 验证：`blog.域名` 可访问前端
- [ ] 验证：`api.域名` 可访问后端 `/health`
- [ ] 停止前台 cloudflared（Ctrl+C）
- [ ] **不停止旧 Kilo 进程**

**回退**：如果 named tunnel 配置失败，继续使用 quick tunnel。

---

### D3：正式切换

**目标**：将所有服务切换到 launchd + named tunnel，停止旧 Kilo 进程。

**切换门槛**：只有同时满足以下全部条件，才允许停止旧 Kilo 进程：

1. D1 launchd 后端健康检查通过
2. D1 launchd 前端本地访问通过
3. D2 named tunnel 前端域名访问通过
4. D2 named tunnel 后端 API 域名健康检查通过
5. 前端公网页面调用 API 正常（浏览器 Network 面板无 localhost:8000 请求）

**执行步骤**：

- [ ] 确认切换门槛全部满足
- [ ] 创建 `com.blog.tunnel.plist`
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.tunnel.plist`
- [ ] 验证：`launchctl list | grep blog.tunnel` 有进程
- [ ] 验证：公网 `blog.域名` 可访问
- [ ] 验证：公网 `api.域名/health` 可访问
- [ ] 验证：公网前端页面 API 调用正常
- [ ] 停止旧 Kilo background_process
- [ ] 验证：停止后公网仍可访问

**回退**：如果 launchd 服务异常：

```bash
# 卸载 launchd 服务
launchctl unload ~/Library/LaunchAgents/com.blog.tunnel.plist
launchctl unload ~/Library/LaunchAgents/com.blog.frontend.plist
launchctl unload ~/Library/LaunchAgents/com.blog.backend.plist

# 恢复 Kilo background_process（手动启动）
# 或使用 quick tunnel
cloudflared tunnel --url http://localhost:2025
cloudflared tunnel --url http://localhost:8000
```

---

### D4：运维增强

- [ ] 日志轮转配置
- [ ] 健康检查脚本
- [ ] 可选：监控告警
- [ ] 可选：数据库定期备份

---

## 5. 待确认决策

| 编号 | 决策点 | 影响 | 候选方案 |
|---|---|---|---|
| D-1 | 域名选择 | cloudflared ingress、DNS、NEXT_PUBLIC_API_URL | A. 使用已有域名 `limengyang.me` 的子域名 / B. 注册新域名 / C. 继续用 quick tunnel（URL 会变） |
| D-2 | 是否立即切换到 named tunnel | 域名固定性、配置复杂度 | A. 立即切换（推荐） / B. 短期继续 quick tunnel，后续再切 |
| D-3 | 前端是否立即改为生产构建 | 需要 `pnpm build`，可能暴露构建问题 | A. 立即切换（推荐） / B. 短期继续 dev server |
| D-4 | 是否需要 Cloudflare Access | 访问控制 | A. 公开访问 / B. 限制特定邮箱/IP |
| D-5 | NEXT_PUBLIC_API_URL 设置时机 | 构建时 bake | 必须在 `pnpm build` 前确定后端公网 URL |

---

## 6. 风险与回退

| 风险 | 影响 | 回退方案 |
|---|---|---|
| `pnpm build` 失败 | 前端无法切换到生产模式 | 继续使用 dev server + launchd 管理 |
| named tunnel ingress 配置错误 | 域名无法访问 | 回退到 quick tunnel |
| launchd plist 路径错误 | 服务无法启动 | `launchctl unload` 卸载，检查日志，修正路径 |
| NEXT_PUBLIC_API_URL 设置错误 | API 调用失败 | 重新 `NEXT_PUBLIC_API_URL=<正确URL> pnpm build` |
| 后端多 worker 定时任务重复 | keep_alive 重复执行 | 保持单 worker |
| DNS CNAME 配置错误 | 域名无法解析 | 检查 CNAME 目标是否为 `<uuid>.cfargotunnel.com` |
| 停止旧进程后新服务异常 | 公网中断 | 立即恢复 Kilo background_process 或 quick tunnel |

---

## 7. 不建议的做法

- 不建议在 D0 只读阶段执行 `pnpm build`、`pnpm start`、`launchctl load`
- 不建议在 named tunnel、NEXT_PUBLIC_API_URL、前端生产构建未确认前停止旧 Kilo 进程
- 不建议长期用 `pnpm dev` 对公网服务
- 不建议直接在普通终端运行 cloudflared（关闭终端即断开）
- 不建议使用 `nohup` 作为长期生产方案
- 不建议使用 quick tunnel 长期服务（无 SLA、URL 不固定）
- 不建议 uvicorn 使用 `--reload` 生产运行
- 不建议未配置 `NEXT_PUBLIC_API_URL` 就开放公网访问
- 不建议把 PostgreSQL/Redis 端口暴露公网
