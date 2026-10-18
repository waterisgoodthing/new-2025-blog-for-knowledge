# Version Baseline

**审计时间**：2026-10-15 15:30 CST  
**Git 信息**：
- **仓库**：`/Users/limengyang/2025-blog-public`
- **分支**：`refactor/baseline`
- **HEAD**：`700f345` — docs: reorganize into docs/current (latest) and docs/archive (historical)
- **工作区状态**：clean
- **远程同步**：与 `mine/refactor/baseline` 同步

---

## 关键依赖版本

### 前端框架

```json
"next": "16.3.8",
"react": "19.0.0",
"react-dom": "19.0.0"
```

### 构建与部署

```json
"@opennext/cloudflare": "1.20.11",
"wrangler": "4.151.0"
```

### UI 相关

```json
"tailwindcss": "4.0.12",
"motion": "11.20.0",
"lucide-react": "0.469.0",
"sonner": "1.7.3"
```

### 完整依赖快照

见 `package.json`（文档编写时版本）。

---

## 数据库版本

- **PostgreSQL**：运行中，数据库 `blog_v2`
- **Alembic 迁移版本**：`034`（最新）
- **备份位置**：`/var/folders/.../opencode/ds-backups/blog_v2_pre034_*.sql`

---

## 部署版本

### Cloudflare Workers

- **线上版本**：`28a835c5`（2026-10-15 部署）
- **域名**：`blog.limengyang.me`
- **状态**：200 OK

### 本地开发

- **前端**：`launchd :2025`
- **后端**：`launchd :8000`
- **隧道**：`cloudflared` (launchd)

---

## 测试基线

### 后端测试

```
958 passed / 0 failed
```

**注意**：测试通过依赖 scratch 库与 head 同步（非 `.env` 缺失）。

### 前端测试

```
531 passed
```

### TypeScript 检查

```
0 errors (npx tsc --noEmit)
```

---

## 文档版本

- **当前文档入口**：`docs/current/README.md`（47 份）
- **历史文档**：`docs/archive/`（1161 份）
- **路径映射**：`docs/archive/README.md`（旧→新）

---

## 环境约束

- **Node.js**：见 `.nvmrc` 或 CI 配置
- **包管理器**：npm
- **操作系统**：macOS（Darwin 27.2.0）

---

**更新说明**：本基线随 UI 重构任务推进而更新，每个 Phase 完成后记录新版本。
