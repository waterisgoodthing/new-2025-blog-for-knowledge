# 进程保活与公网连接稳定性任务清单

> 来源：`design-process-keepalive.md`。按批次顺序执行。

---

## 禁止事项（全局）

- 不修改 `.env`、后端代码、前端代码、数据库结构
- 不修改 `package.json`
- 不杀已有进程（除非 D3 切换阶段明确授权）
- 不修改 Cloudflare Access 配置（已由用户配置）

---

## D0：只读确认

> 本阶段只读，不执行任何写操作、构建、启动。

- [x] 确认域名：`blog.limengyang.me`（前端）+ `api.limengyang.me`（后端）
- [x] 确认 `NEXT_PUBLIC_API_URL`：`https://api.limengyang.me`
- [x] 确认 `package.json` 的 `build`/`start` 脚本
- [x] 确认后端 `main:app` 路径
- [x] 确认后端 `.env` 加载方式：pydantic-settings 自行读取，不依赖 shell 环境变量
- [x] 确认 cloudflared 已登录，named tunnel `blog-tunnel` 存在
- [x] 确认 credentials 文件存在
- [x] 确认 Cloudflare Access 已配置，无需修改

---

## D1：本地 launchd 演练

> 不切换公网。不停止旧 Kilo 进程。
> **使用临时演练端口**，避免与 Kilo 旧进程冲突：
> - 后端演练端口：`18000`
> - 前端演练端口：`12025`
> D3 正式切换时再使用正式端口 `8000` 和 `2025`。

### T-01 后端 launchd 演练部署

- [ ] 创建 `~/Library/LaunchAgents/com.blog.backend.plist`（端口 `18000`）
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.backend.plist`
- [ ] 验证：`curl http://127.0.0.1:18000/health` 返回正常
- [ ] 验证：`launchctl list | grep blog.backend` 有进程
- [ ] 验证：`tail /tmp/blog-backend.log` 无异常

涉及文件

| 文件 | 变更类型 |
|---|---|
| `~/Library/LaunchAgents/com.blog.backend.plist` | 新建 |

验收标准

- launchd 后端进程存在
- 演练端口 18000 健康检查通过
- 日志无异常
- 旧 Kilo 后端（端口 8000）不受影响

---

### T-02 前端生产构建验证 + launchd 演练部署

> D1 阶段仅验证生产构建能否成功，不使用最终 API URL。
> D3 正式切换前再用 `NEXT_PUBLIC_API_URL=https://api.limengyang.me` 重新 build。

- [ ] `NEXT_PUBLIC_API_URL=https://api.limengyang.me pnpm build`
- [ ] 验证构建成功（无报错）
- [ ] 创建 `~/Library/LaunchAgents/com.blog.frontend.plist`（端口 `12025`）
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.frontend.plist`
- [ ] 验证：`curl http://127.0.0.1:12025` 返回 HTML
- [ ] 验证：`launchctl list | grep blog.frontend` 有进程
- [ ] 验证：`tail /tmp/blog-frontend.log` 无异常

涉及文件

| 文件 | 变更类型 |
|---|---|
| `~/Library/LaunchAgents/com.blog.frontend.plist` | 新建 |

验收标准

- `pnpm build` 成功
- launchd 前端进程存在
- 演练端口 12025 返回 HTML
- 日志无异常
- 旧 Kilo 前端（端口 2025）不受影响

**回退**：如果 build 失败，不创建 frontend plist，继续使用 Kilo 管理的 dev server。

---

## D2：named tunnel 演练

> 不停止旧 Kilo 进程。

### T-03 配置 cloudflared ingress

- [ ] 创建 `~/.cloudflared/config.yml`

  ```yaml
  tunnel: e8ca3989-62b6-4324-bf71-447fd1774a25
  credentials-file: /Users/limengyang/.cloudflared/e8ca3989-62b6-4324-bf71-447fd1774a25.json

  ingress:
    - hostname: blog.limengyang.me
      service: http://localhost:2025
    - hostname: api.limengyang.me
      service: http://localhost:8000
    - service: http_status:404
  ```

- [ ] `cloudflared tunnel ingress validate`
- [ ] `cloudflared tunnel ingress rule https://blog.limengyang.me`
- [ ] `cloudflared tunnel ingress rule https://api.limengyang.me`

涉及文件

| 文件 | 变更类型 |
|---|---|
| `~/.cloudflared/config.yml` | 新建 |

验收标准

- ingress validate 通过
- 两条路由规则匹配正确

---

### T-04 配置 DNS CNAME

- [ ] 在 Cloudflare DNS 中添加：
  - `blog.limengyang.me` CNAME → `e8ca3989-62b6-4324-bf71-447fd1774a25.cfargotunnel.com`
  - `api.limengyang.me` CNAME → `e8ca3989-62b6-4324-bf71-447fd1774a25.cfargotunnel.com`
- [ ] 验证：`dig blog.limyang.me CNAME`
- [ ] 验证：`dig api.limengyang.me CNAME`

验收标准

- 两条 CNAME 记录存在
- 指向 `<tunnel-uuid>.cfargotunnel.com`
- 不指向 trycloudflare.com 或 localhost

---

### T-05 前台运行 cloudflared 测试

- [ ] `cloudflared tunnel run blog-tunnel`（前台运行）
- [ ] 验证：`https://blog.limengyang.me` 可访问前端
- [ ] 验证：`https://api.limengyang.me/health` 可访问后端
- [ ] Ctrl+C 停止前台进程

验收标准

- **必须**使用 `https://blog.limengyang.me` 作为前端验收地址
- **必须**使用 `https://api.limengyang.me/health` 作为后端验收地址
- **不得**使用 trycloudflare.com 作为 named tunnel 验收依据
- 两个域名均可访问
- 后端健康检查通过

**回退**：如果 named tunnel 失败，不继续 D3，改用 quick tunnel + launchd。

---

## D3：正式切换

> 切换门槛：D1 + D2 全部验收通过。

### 切换门槛检查

- [ ] D1 launchd 后端健康检查通过（演练端口 18000）
- [ ] D1 launchd 前端本地访问通过（演练端口 12025）
- [ ] D2 named tunnel 前端域名访问通过（`https://blog.limengyang.me`）
- [ ] D2 named tunnel 后端 API 域名健康检查通过（`https://api.limengyang.me/health`）
- [ ] 前端公网页面 API 调用正常

### T-06 正式端口重新部署

> D1 演练使用了临时端口。D3 正式切换时，需要卸载演练 plist，用正式端口重新部署。

- [ ] 卸载演练 plist：
  - `launchctl unload ~/Library/LaunchAgents/com.blog.backend.plist`
  - `launchctl unload ~/Library/LaunchAgents/com.blog.frontend.plist`
- [ ] 重新创建 `com.blog.backend.plist`（端口 `8000`）
- [ ] 重新创建 `com.blog.frontend.plist`（端口 `2025`）
- [ ] `NEXT_PUBLIC_API_URL=https://api.limengyang.me pnpm build`（使用最终 API URL 重新构建）
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.backend.plist`
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.frontend.plist`
- [ ] 验证：`curl http://127.0.0.1:8000/health` 返回正常
- [ ] 验证：`curl http://127.0.0.1:2025` 返回 HTML

验收标准

- 正式端口 8000 和 2025 正常
- 使用最终 `NEXT_PUBLIC_API_URL` 构建
- 日志无异常

---

### T-07 cloudflared launchd 部署

- [ ] 创建 `~/Library/LaunchAgents/com.blog.tunnel.plist`
- [ ] `launchctl load ~/Library/LaunchAgents/com.blog.tunnel.plist`
- [ ] 验证：`launchctl list | grep blog.tunnel` 有进程
- [ ] 验证：`https://blog.limengyang.me` 可访问
- [ ] 验证：`https://api.limengyang.me/health` 可访问
- [ ] 验证：公网前端页面 API 调用正常

涉及文件

| 文件 | 变更类型 |
|---|---|
| `~/Library/LaunchAgents/com.blog.tunnel.plist` | 新建 |

验收标准

- launchd tunnel 进程存在
- 两个公网域名可访问
- 前端 API 调用正常

---

### T-08 停止旧 Kilo 进程

- [ ] 确认 T-06、T-07 全部验收通过
- [ ] **旧进程确认清单**（人工确认）：
  - `pgrep -af "next dev"` — 确认旧前端进程 PID
  - `pgrep -af "uvicorn.*--reload"` — 确认旧后端进程 PID
  - `pgrep -af "cloudflared tunnel --url"` — 确认旧 quick tunnel 进程 PID
- [ ] 停止 Kilo background_process（前端、后端、cloudflared quick tunnel）
- [ ] 验证：停止后公网仍可访问
- [ ] 验证：`launchctl list | grep blog` 显示三个服务

验收标准

- 旧进程确认清单已人工核对
- Kilo 旧进程已停止
- 公网访问不受影响
- 三个 launchd 服务正常运行

**回退**：如果停止旧进程后公网异常，按以下顺序恢复：

```bash
# 第一步：恢复本地前端进程（因为 launchd 前端可能也已失败）
pnpm dev &

# 第二步：恢复本地后端进程
cd backend && .venv/bin/python -m uvicorn main:app --reload --port 8000 &

# 第三步：恢复 quick tunnel
cloudflared tunnel --url http://localhost:2025 &
cloudflared tunnel --url http://localhost:8000 &

# 第四步：卸载失败的 launchd 服务
launchctl unload ~/Library/LaunchAgents/com.blog.tunnel.plist
launchctl unload ~/Library/LaunchAgents/com.blog.frontend.plist
launchctl unload ~/Library/LaunchAgents/com.blog.backend.plist
```

---

## D4：运维增强

### T-09 健康检查脚本

- [ ] 创建 `~/bin/blog-health-check.sh`

  ```bash
  #!/bin/bash
  echo "=== launchd 服务 ==="
  launchctl list | grep blog
  echo ""
  echo "=== 端口监听 ==="
  lsof -i :2025 -P -n | grep LISTEN
  lsof -i :8000 -P -n | grep LISTEN
  echo ""
  echo "=== 后端健康 ==="
  curl -s http://127.0.0.1:8000/health
  echo ""
  echo "=== 前端状态 ==="
  curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:2025
  echo ""
  echo "=== 日志尾部 ==="
  echo "--- backend ---"
  tail -3 /tmp/blog-backend.log
  echo "--- frontend ---"
  tail -3 /tmp/blog-frontend.log
  echo "--- tunnel ---"
  tail -3 /tmp/blog-tunnel.log
  ```

- [ ] `chmod +x ~/bin/blog-health-check.sh`

验收标准

- 运行脚本可一键查看所有服务状态

---

### T-10 日志轮转方案评估

> 本轮不直接实施日志轮转，仅评估方案。

日志文件路径：
- `/tmp/blog-backend.log`
- `/tmp/blog-frontend.log`
- `/tmp/blog-tunnel.log`

候选方案：

| 方案 | 说明 | 优点 | 缺点 |
|---|---|---|---|
| A. newsyslog | macOS 内置日志轮转工具，配置 `/etc/newsyslog.conf` | 系统原生，自动轮转 | 需要 sudo 权限 |
| B. crontab | 定时执行截断脚本 | 简单，无需 sudo | 需要手动维护脚本 |
| C. LaunchAgent | 新建 plist 定期执行清理 | 与现有架构一致 | 增加一个 launchd 服务 |
| D. 手动截断 | `tail -1000 file > file.tmp && mv file.tmp file` | 最简单 | 不自动执行，需人工操作 |

- [ ] 评估候选方案
- [ ] 选择推荐方案（不实施）

验收标准

- 已记录推荐方案和理由
