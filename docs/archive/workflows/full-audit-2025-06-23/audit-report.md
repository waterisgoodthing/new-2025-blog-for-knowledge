# 全量审查报告

> 审查日期：2026-06-23
> 审查方式：只读代码审查 + 配置审查 + 静态分析
> 审查范围：全仓库（见下）

---

## 0. 审查范围与限制

### 已审查目录

- `/` — 根配置文件（package.json, next.config.ts, tsconfig.json, .gitignore, .env.example, README.md, AGENTS.md）
- `/src/` — 所有前端代码（app/, components/, hooks/, lib/, config/, layout/, styles/, svgs/）
- `/backend/` — 所有后端代码（app/, tests/, alembic/, main.py, requirements.txt）
- `/public/` — 静态资源
- `/docs/` — 文档
- `/scripts/` — 脚本
- `/.github/` — CI 配置

### 未审查项目

- Cloudflare Workers 部署配置（wrangler.toml, open-next.config.ts）— 未深度审查
- NetEase API 集成细节（已标记为禁用）— 仅检查路由权限
- AI Provider 适配器链的详细实现 — 仅检查权限和路由

### 未运行成功的命令

- `npx tsc --noEmit` — 未运行（AGENTS.md 自述已知失败，JSON 空数组推断为 `never[]`）
- `npm run build` — 未运行
- `python -m pytest tests/ -v` — 未运行（需要 PostgreSQL）

### 需要人工确认的部分

1. `backend/.env` 中的 API Key 是否仍在生产环境使用
2. `public/images/pictures/` 下 2 个被 git 追踪的 PNG 文件是否包含个人信息
3. `public/mymusic/` 下 mp3 文件的版权授权状态
4. Cloudflare 部署的 CORS 和反向代理配置
5. 生产环境 `ALLOWED_ORIGINS` 实际值

---

## 1. 总体结论

### 项目成熟度判断

这是一个**中等成熟度**的个人项目。核心技术栈选择合理，架构分层清晰，但存在一些需要修复的安全缺陷和工程治理缺口。

**正面**：
- 前后端分离架构设计良好，分层清晰（Router → Service → Model）
- 认证体系完备（密码 + Passkey + Cookie Session）
- 内容系统覆盖全面（博客、笔记、错题、发现、留言）
- 已有审计日志、速率限制、输入校验等基础安全设施
- AGENTS.md 对 AI Agent 约束细致

**需要改进**：
- 3 个编辑路由缺少 AuthGate（P0 级）
- 多处 SEO 问题（ssr: false，无 metadata）
- Schema 输入校验不完整
- 测试覆盖严重不足

### 最大风险

1. **认证绕过**：3 个 `[slug]` 编辑页面未包裹 AuthGate，匿名用户可直接访问编辑器
2. **SSR 禁用**：所有详情页使用 `ssr: false`，搜索引擎无法抓取内容
3. **审计日志泄露**：明文密码痕迹可能进入审计日志的 before/after 快照
4. **版权风险**：17MB 受版权保护的 mp3 文件在 git 历史中

### 最值得优先修复的 5 项

1. 为 `write/[slug]`、`write-note/[slug]`、`write-mistake/[slug]` 添加 AuthGate
2. 为 `mistakes/review` 页面添加认证检查
3. 将博客/笔记/错题详情页改为 SSR 并添加 generateMetadata
4. 为后端 schema 添加 max_length 约束
5. 从 git 历史中清除 mp3 文件和可能的个人信息图片

---

## 2. P0 问题：立即修复

| 编号 | 问题 | 位置 | 影响 | 证据 | 修复建议 | 验证方法 |
|------|------|------|------|------|----------|----------|
| P0-01 | `write/[slug]/page.tsx` 未包裹 AuthGate，匿名可编辑博客 | `src/app/write/[slug]/page.tsx:1-44` | 任何人都可直接访问博客编辑器并可能保存修改 | 对比 `src/app/write/page.tsx:16` 使用了 AuthGate，但 `src/app/write/[slug]/page.tsx` 完全没有 | 包裹 `<AuthGate>` 组件 | 未登录访问 `/write/any-slug` 应重定向到 `/manage` |
| P0-02 | `write-note/[slug]/page.tsx` 未包裹 AuthGate，匿名可编辑笔记 | `src/app/write-note/[slug]/page.tsx:1-467` | 任何人都可直接访问笔记编辑器 | 对比 `src/app/write-note/page.tsx:27` 使用了 AuthGate | 包裹 `<AuthGate>` 组件 | 未登录访问 `/write-note/any-slug` 应重定向到 `/manage` |
| P0-03 | `write-mistake/[slug]/page.tsx` 未包裹 AuthGate，匿名可编辑错题 | `src/app/write-mistake/[slug]/page.tsx:1-21` | 任何人都可直接访问错题编辑器 | 对比 `src/app/write-mistake/page.tsx:8` 使用了 AuthGate | 包裹 `<AuthGate>` 组件 | 未登录访问 `/write-mistake/any-slug` 应重定向到 `/manage` |
| P0-04 | 错题复习页面无认证，可匿名提交复习 | `src/app/mistakes/review/page.tsx:37-43` | 未认证用户可加载复习队列并提交 SM-2 复习，修改错题状态 | `Promise.all(...)` 无 .catch()；`submitReview()` 无 auth 检查 | 添加后端 `get_current_admin` 依赖；前端添加 AuthGate | API: `POST /api/review/{slug}` 无 Cookie 应返回 401 |
| P0-05 | `GET /api/recommendations/today` 执行数据库写入 | `backend/app/routers/recommendations.py:17-18` | GET 请求不应有副作用；未认证用户可触发数据创建 | `get_or_create_today_recommendation(db)` 在 GET handler 中 | 拆分为 GET（只读）和 POST（创建）；或返回 null 若无推荐 | GET 不创建新记录；POST 需要 admin |
| P0-06 | `AUTH_BYPASS` + `AUTH_BYPASS_ALLOW` 同时启用时完全绕过认证 | `backend/app/routers/auth.py:62-66` | 如果生产环境误开启，所有管理接口无保护 | `_is_auth_bypass_active()` 返回 True 时任何请求被当作 admin | 生产环境启动时检查并拒绝启动（添加类似 JWT/CORS 的检查） | 设置两个环境变量为 true，启动应退出 |

---

## 3. P1 问题：短期修复

| 编号 | 问题 | 位置 | 影响 | 证据 | 修复建议 | 验证方法 |
|------|------|------|------|------|----------|----------|
| P1-01 | 博客详情页 SSR 禁用，无法被搜索引擎索引 | `src/app/blog/[id]/page.tsx:5` | 所有博客文章对搜索引擎不可见 | `dynamic(() => import(...), { ssr: false })` | 移除 `ssr: false`，添加 `generateMetadata` 和 `generateStaticParams` | 查看页面源码应包含文章内容 |
| P1-02 | 笔记详情页 SSR 禁用 | `src/app/notes/[id]/page.tsx:5` | 所有笔记对搜索引擎不可见 | 同上 | 同上 | 同上 |
| P1-03 | 关于页 SSR 禁用 | `src/app/about/page.tsx:5` | 关于页不可索引 | 同上 | 同上 | 同上 |
| P1-04 | 无 robots.txt | 全项目 | 搜索引擎爬虫无引导 | `src/app/` 无 `robots.ts` | 添加 `src/app/robots.ts` | 访问 `/robots.txt` 返回有效内容 |
| P1-05 | sitemap 仅包含博客，不包含笔记/错题/发现 | `src/app/sitemap.ts` | 仅博客在 sitemap 中 | sitemap 只查询 `type=blog` | 扩展为包含笔记、错题、发现、关于等页面 | sitemap.xml 包含多类型 URL |
| P1-06 | Schema 缺少 max_length 约束（多处） | `backend/app/schemas/note.py`, `auth.py`, `content.py` | 可发送超长 payload 导致 DoS | `content: str`、`title: str` 等无 max_length | 为所有字符串字段添加 `Field(max_length=N)` | 发送超长请求应返回 422 |
| P1-07 | `ai_metadata: dict` 完全无约束 | `backend/app/schemas/note.py:48` | 可发送任意深度字典 | `NoteCreate.ai_metadata: dict \| None` 无任何 Field 约束 | 添加最大深度/大小限制或使用 constrained type | 发送超大嵌套 JSON 应返回 422 |
| P1-08 | `content_store.py` 无 schema 验证即存储 JSON | `backend/app/services/content_store.py:25,33-35` | 恶意或损坏的 JSON 文件直接入数据库 | `get_default_content` 不验证文件格式 | 对文件 JSON 和 DB 返回数据执行 Pydantic schema 验证 | 写入畸形 JSON 后读取应报错/降级 |
| P1-09 | 审计日志可能捕获明文密码 | `backend/app/services/audit_service.py` + `backend/app/models/audit.py:22-23` | 密码变更时 before/after 快照可能包含明文 | `set-password` handler 不调用 audit 但审计模型设计无自动脱敏 | 在审计记录前对敏感字段做脱敏处理 | 查看审计日志中不出现密码明文 |
| P1-10 | 速率限制器存在内存泄漏和并发问题 | `backend/app/utils/rate_limit.py:16,11-22` | 长时间运行内存增长；并发请求可绕过限制 | `self._store[key]` 清理后空列表未删除；无锁保护 | 清理后删除空列表 key；使用 asyncio.Lock 或 Redis | 压力测试验证内存不增长 |
| P1-11 | AI 模块使用全局速率限制而非按用户 | `backend/app/routers/ai.py:106-112` | 一个用户可耗尽所有 AI 配额 | `_check_rate_limit("global")` vs `ai_polish.py` 使用 `user.id` | 改为 `_check_rate_limit(str(user.id))` | 不同用户应分别计数 |

---

## 4. P2 问题：后续优化

| 编号 | 问题 | 位置 | 影响 | 证据 | 修复建议 | 验证方法 |
|------|------|------|------|------|----------|----------|
| P2-01 | 受版权保护的 mp3 文件在 git 历史中 | `public/mymusic/孙燕姿-天黑黑.mp3`, `孙燕姿-遇见.mp3` | 版权侵权风险 + 仓库膨胀 | git ls-files 确认已追踪；~17MB | git filter-branch 清除历史；添加 `public/mymusic/*.mp3` 到 .gitignore | git log 中不再出现 mp3 |
| P2-02 | 2 张用户图片在 gitignore 前已提交 | `public/images/pictures/03bd49...png`, `079a7a...png` | 可能泄露个人信息 | git ls-files 确认已追踪 | 评估内容后决定是否清除历史 | git log 确认 |
| P2-03 | `operator-passkey-register.html` 公开可访问 | `public/operator-passkey-register.html` | 攻击者可尝试猜测 Operator Key | 页面公开但需要 Header 中的 KEY 才可注册 | 考虑将此页面移出 public/ 或在反向代理层限制 IP | 匿名访问确认存在但功能需 KEY |
| P2-04 | `selection.json` 在 public/ 中暴露 | `public/mymusic/selection.json` | UI 状态文件无需公开 | 包含 `{"selected_file":"..."}` | 移入数据库或 localStorage | public/ 不再包含 selection.json |
| P2-05 | `config.py` 默认 ALLOWED_ORIGINS 包含生产域名 | `backend/app/config.py:11` | 本地开发时默认允许生产域名 | 硬编码了 `https://blog.limengyang.me` | 本地默认仅 localhost 域名 | 未设置环境变量时仅允许 localhost |
| P2-06 | `database.py` get_db 自动提交读操作 | `backend/app/database.py:16-23` | 读请求也提交事务，不必要 | `try: yield session; await session.commit()` | 仅对写请求提交；或将 commit 移入 service 层 | 代码审查确认 |
| P2-07 | 前端 slug 未 encodeURIComponent | `src/lib/api/notes.ts:131,142,149` | 含特殊字符的 slug 导致 404 | `${API_BASE}/api/notes/${slug}` 直接拼接 | 使用 `encodeURIComponent(slug)` | 创建含 `#` 的 slug 可正常访问 |
| P2-08 | `use-blog-index.ts` 中 `items.sort()` 原地修改 SWR 缓存 | `src/hooks/use-blog-index.ts:58` | 可能导致其他组件数据错乱 | `items.sort(...)` 而非 `[...items].sort(...)` | 使用浅拷贝排序 | 验证 SWR 缓存不被修改 |
| P2-09 | `images.ts` 允许 HTTP URL 通过导致混合内容 | `src/lib/api/images.ts:5` | HTTPS 页面加载 HTTP 图片被阻止 | `url.startsWith('http://')` 直接返回 | 升级为 HTTPS 或返回占位图 | 上传 HTTP 图片后前端不报 mixed content |
| P2-10 | 文件夹深度检查有 TOCTOU 竞态 | `backend/app/routers/folders.py:99-101` | 并发创建时可绕过深度限制 | check-then-create 之间无锁 | 使用 DB 级别约束或 SELECT FOR UPDATE | 并发创建测试 |
| P2-11 | `content_store.py` get_default_content 可能 KeyError 500 | `backend/app/services/content_store.py:43` | 未知 key 导致 500 | 字典直接取 key 而非 .get() | 使用 .get() 返回默认值或明确 404 | 请求不存在的内容 key 返回 404 而非 500 |
| P2-12 | `slug.py` 非拉丁输入产生空 slug | `backend/app/utils/slug.py:11-14` | 纯中文标题无法生成 slug | regex 去除所有非 ASCII | 添加拼音转换或 UUID fallback | 创建纯中文标题应生成有效 slug |

---

## 5. 前端审查

### 5.1 路由与页面

**已注册的公开页面（28 个 page.tsx）**：

| 路由 | 页面 | 客户端/服务端 | AuthGate | SSR | Metadata |
|------|------|---------------|----------|-----|----------|
| `/` | 首页 | Client | ❌ | N/A | ❌ |
| `/blog` | 博客列表 | Client | ❌ 部分 | ❌ | ❌ |
| `/blog/[id]` | 博客详情 | Client | ❌ | ❌ (ssr:false) | ❌ |
| `/notes` | 笔记列表 | Client | ❌ 部分 | ❌ | ❌ |
| `/notes/[id]` | 笔记详情 | Client | ❌ | ❌ (ssr:false) | ❌ |
| `/mistakes` | 错题列表 | Client | ❌ | ❌ | ❌ |
| `/mistakes/review` | 错题复习 | Client | ❌ **缺失** | ❌ | ❌ |
| `/discover` | 发现 | Client | ❌ | ❌ | ❌ |
| `/about` | 关于 | Client | ❌ | ❌ (ssr:false) | ❌ |
| `/guestbook` | 留言板 | Client | ❌ | ❌ | ❌ |
| `/share` | 分享管理 | Client | ❌ 客户端重定向 | ❌ | ❌ |
| `/projects` | 项目 | Client | ❌ | ❌ | ❌ |
| `/pictures` | 图片 | Client | ❌ | ❌ | ❌ |
| `/snippets` | 代码片段 | Client | ❌ | ❌ | ❌ |
| `/bloggers` | 博主 | Client | ❌ | ❌ | ❌ |
| `/music` | 音乐 | Client | ❌ | ❌ | ❌ |
| `/manage` | 管理面板 | Client | ✅ (getMe) | ❌ | ❌ |
| `/write` | 写博客 | Client | ✅ AuthGate | ❌ | ❌ |
| `/write/[slug]` | 编辑博客 | Client | ❌ **缺失** | ❌ | ❌ |
| `/write-note` | 写笔记 | Client | ✅ AuthGate | ❌ | ❌ |
| `/write-note/[slug]` | 编辑笔记 | Client | ❌ **缺失** | ❌ | ❌ |
| `/write-mistake` | 写错题 | Client | ✅ AuthGate | ❌ | ❌ |
| `/write-mistake/[slug]` | 编辑错题 | Client | ❌ **缺失** | ❌ | ❌ |
| `/live2d` | Live2D | Client | ❌ | ❌ | ❌ |
| `/clock` | 时钟 | Client | ❌ | ❌ | ❌ |
| `/image-toolbox` | 图片工具箱 | Client | ❌ | ❌ | ❌ |
| `/svgs` | SVG | Client | ❌ | ❌ | ❌ |
| `/wuthering-waves` | 鸣潮 | Client | ❌ | ❌ | ❌ |

**问题汇总**：
- 4 个路由缺少 AuthGate（P0）：write/[slug], write-note/[slug], write-mistake/[slug], mistakes/review
- 3 个路由使用 ssr: false（P1）：blog/[id], notes/[id], about
- 所有页面均为 Client Component 且无 metadata（P1）
- 存在疑似临时/废弃/个人兴趣页面（P2）：live2d, clock, image-toolbox, svgs, wuthering-waves
- `mistakes/page.tsx` 的 "添加错题" 按钮对所有用户可见

### 5.2 组件结构

- `src/components/` — 共享组件，结构合理
- `src/app/<route>/components/` — 路由专属组件，符合 AGENTS.md 规范
- `auth-gate.tsx` — 使用 `useAdminAuth` + client-side redirect，仅客户端保护
- 存在 `AritcleCard` 拼写错误（`src/app/(home)/page.tsx:70`）

### 5.3 Hooks

| Hook | 问题 | 严重度 |
|------|------|--------|
| `use-blog-index.ts` | `items.sort()` 原地修改 SWR 缓存 | P2 |
| `use-admin-auth` + `use-blog-index` | 重复 admin 检查，不同 SWR key | 低 |
| `use-markdown-render.tsx` | html-react-parser 不做 HTML 净化 | 中 |
| `use-markdown-render.tsx` | 复杂正则可能有回溯风险 | 低 |
| `use-knowledge.ts` | `null as unknown as ContextPackResponse` 类型断言 | 低 |
| `use-center.ts` | 魔法数字 -24 偏移 | 低 |

### 5.4 Lib

- API client (`src/lib/api/client.ts`)：统一 fetch 封装，错误分类合理
- `config.ts`：生产环境 localhost 检测良好
- `images.ts`：HTTP URL 未升级为 HTTPS（混合内容风险）
- `content-routes.ts`：正确使用 encodeURIComponent
- `notes.ts`：slug 未 encodeURIComponent

### 5.5 UI

- 使用 Tailwind CSS + motion (Framer Motion)
- 移动端无明显断裂
- 空状态覆盖良好（EmptyState 组件 4 种变体）
- 管理端与公开端视觉层级有区分
- 全局自定义光标 `cursor: url(/images/cursor.svg)`

### 5.6 SEO 与可访问性

| 检查项 | 状态 |
|--------|------|
| 全局 metadata | ✅ root layout 有 title/description/OG/Twitter |
| 各页面独立 metadata | ❌ 所有页面使用全局默认 |
| 动态文章页 metadata | ❌ 无 generateMetadata |
| sitemap.xml | ✅ 存在但仅含博客 |
| robots.txt | ❌ 不存在 |
| 图片 alt | ✅ 多数有 |
| 表单 label | ✅ htmlFor 绑定正确 |
| 首屏 HTML 包含内容 | ❌ 全 Client Component，首屏为空 |
| 页面标题层级 | 未逐页检查 |

---

## 6. 后端审查

### 6.1 main.py

**正面**：
- 生产环境 JWT 默认密钥检测并退出 ✅
- 生产环境 CORS `*` 检测并退出 ✅
- 健康检查接口 `/api/health` ✅
- lifespan 管理数据库初始化和 keep-alive ✅
- 注册了所有 router ✅

**问题**：
- `Base.metadata.create_all` 在每次启动执行（非生产最佳实践，应使用 Alembic）— 中
- 无全局异常处理中间件 — 中
- 无请求日志中间件 — 低
- `public/images` 挂载为静态文件，但 backend 路径解析为 `parent.parent/public/images` — 低（路径可能不对）

### 6.2 Routers

**已审查 18 个 router 文件，关键发现**：

| Router | 公开读 | 公开写 | 管理写 | 问题 |
|--------|--------|--------|--------|------|
| `auth.py` | passkey/status, auth-options, reg-options | login, login-passkey, register | set-password (passkey), operator/* | register 在 production 且无 REGISTRATION_KEY 时拒绝开放 ✅ |
| `notes.py` | list, get | ❌ | CRUD + batch-delete + upload-image + promote | batch-delete 无审计日志 ⚠️ |
| `content.py` | about, shares, projects, pictures, bloggers, snippets, site-settings | ❌ | PUT/DELETE (admin/passkey) | site-settings PUT 需要 passkey ✅ |
| `review.py` | ❌ | ❌ | queue, submit, stats, plan | 仅 admin ✅ |
| `guest_messages.py` | list | create | moderate, bans | 有速率限制和 ban 机制 ✅ |
| `recommendations.py` | today, history | ❌ | delete today | **GET today 会写数据库** 🚨 P0-05 |
| `music.py` | playlist | ❌ | CRUD items | ✅ |
| `music_manage.py` | public songs, history | ❌ | config, sync, rules | config PUT 用 passkey 不一致 |
| `ai.py` | ❌ | ❌ | 全 admin | 全局速率限制（非按用户）⚠️ |
| `ai_polish.py` | ❌ | ❌ | polish (admin) | 按用户速率限制 ✅ |
| `folders.py` | list | ❌ | CRUD + move | TOCTOU 深度竞态 ⚠️ |
| `tags.py` | list | ❌ | CRUD + merge | 使用 raw SQL 操作 note_tags ⚠️ |
| `subjects.py` | list | ❌ | create, delete | 删除不检查引用 ⚠️ |
| `categories.py` | list | ❌ | CRUD | 同上 ⚠️ |
| `knowledge.py` | ❌ | ❌ | context-pack, weak-points | ✅ |
| `suggestions.py` | ❌ | ❌ | suggestions, weekly-summary | ✅ |
| `audit.py` | ❌ | ❌ | list | ✅ |

### 6.3 Services

| Service | 问题 |
|---------|------|
| `content_store.py` | 无 JSON schema 验证；KeyError 500 |
| `passkey_service.py` | 内存存储 challenge（多进程问题）；replace_credential 删除所有旧凭证 |
| `audit_service.py` | 可能记录敏感信息 |
| `sm2.py` | 标准 SM-2 算法实现，未见问题 |
| `rate_limit.py` | 内存泄漏 + 并发不安全 |
| `slug.py` | 非拉丁输入空 slug；无最大长度检查 |
| `keep_alive.py` | 定时 HTTP 请求 self-health-check，可能造成无限循环 |

### 6.4 Models

- 11 个数据库模型，结构清晰 ✅
- `Note` 使用单表多类型设计（type 字段区分 note/blog/mistake）✅
- 有 created_at / updated_at ✅
- 有关键索引（slug, status, next_review, search_vector）✅
- 软删除策略：`GuestMessage.status` 字段，`Note.hidden` 字段；管理员可硬删除
- `folder_id` 使用 `ondelete="SET NULL"` ✅

### 6.5 Schemas

- 请求和响应模型分离 ✅
- 但大量字段缺少 max_length 约束 🚨
- `ai_metadata: dict` 和 `attestation: dict` 完全无约束 🚨
- `cardStyles: dict[str, Any]` 使用 Any 🚨
- `NoteOut` 暴露 `password_hash` 字段？已确认只有 User 模型有 password_hash 且 UserOut schema 不包含 ✅

### 6.6 Utils

- `auth.py`：bcrypt 密码哈希 ✅, SHA256 session token ✅, secrets.token_urlsafe ✅
- `rate_limit.py`：内存泄漏 + 并发问题 🚨
- `slug.py`：空 slug + 无长度检查 🚨

### 6.7 Tests

**已有测试（5 文件，约 33 个测试）**：
- AI 确定性修复（1 个）
- AI provider 模型配置（3 个）
- 本地音乐源选择（5 个）
- 错题分阶段工作流 schema（约 20 个）
- 临时 admin 引导（3 个）

**缺失测试**：
- ❌ 认证测试（401/403 验证）
- ❌ API CRUD 集成测试
- ❌ 权限测试
- ❌ 速率限制测试
- ❌ 上传测试
- ❌ XSS/注入测试
- ❌ 审计日志测试
- ❌ 会话管理测试

---

## 7. 认证与权限审查

### 7.1 登录

| 检查项 | 状态 | 位置 |
|--------|------|------|
| 密码登录路径 | `/api/auth/login` | `auth.py:162` |
| 失败不泄露账号存在性 | ✅ 统一返回 "Invalid credentials" | `auth.py:171` |
| 频率限制 | ❌ 登录接口无速率限制 | |
| 暴力破解防护 | ❌ 无 | |
| 登录失败日志 | ⚠️ 仅在成功时记录 audit | `auth.py:189-200` |
| bcrypt 哈希 | ✅ | `utils/auth.py:11-12` |
| Passkey 登录 | ✅ | `auth.py:213-284` |

### 7.2 Passkey / WebAuthn

| 检查项 | 状态 | 位置 |
|--------|------|------|
| RP ID 配置 | ✅ `WEBAUTHN_RP_ID=blog.limengyang.me` (生产) | `backend/.env` |
| Origin 配置 | ✅ `WEBAUTHN_ORIGIN=https://blog.limengyang.me` (生产) | `backend/.env` |
| Operator 注册需 KEY | ✅ Header `X-Operator-Registration-Key` | `auth.py:299-311` |
| 注册页面公开 | ⚠️ `public/operator-passkey-register.html` 可公开访问 | 需要 KEY 才能注册 |
| Challenge 存储 | ⚠️ 内存字典（多 worker 问题） | `passkey_service.py:14-16` |
| userVerification | ✅ required | `passkey_service.py:73` |

### 7.3 会话

| 检查项 | 状态 | 位置 |
|--------|------|------|
| Cookie HttpOnly | ✅ | `auth.py:51` |
| Cookie Secure | ✅ 条件（HTTPS 时 True） | `auth.py:52` |
| SameSite | ✅ Lax | `auth.py:39` |
| Cookie Path | `/api` | `auth.py:38` |
| 退出清理 Cookie | ✅ delete_cookie | `auth.py:59` |
| 退出撤销 session | ✅ `sess.revoked = True` | `auth.py:416` |
| Session 过期 | ✅ Passkey 7 天，Password 3 天 | `utils/auth.py:7-8` |
| localStorage 存 token | ❌ 未发现（使用 Cookie） | |
| auth_level 区分 | ✅ passkey vs password | `auth.py:181,255` |

### 7.4 访问控制

| 检查项 | 状态 |
|--------|------|
| 管理页面后端鉴权 | ✅ get_current_admin / get_passkey_admin |
| 写接口后端强制鉴权 | ✅ 大部分（review 除外） |
| 匿名访问管理 API | ✅ 返回 401/403 |
| 前管理端双重保护 | ⚠️ AuthGate 仅客户端，3 个页面缺失 |
| IDOR 风险 | ⚠️ 未逐接口检查 |
| 修改他人数据 | ⚠️ 仅有 admin 判断，无资源所有者检查 |

### 7.5 认证与权限风险矩阵

| 风险 | 严重度 | 利用条件 | 影响 |
|------|--------|----------|------|
| AUTH_BYPASS 误开启 | P0 | 两个环境变量设为 true | 完全绕过认证 |
| [slug] 编辑器无 AuthGate | P0 | 知道 URL 路径 | 匿名编辑/查看内容 |
| 复习提交无认证 | P0 | 知道 API 路径 | 篡改 SM-2 状态 |
| 登录无限速 | P1 | 网络可达 | 密码爆破 |
| Challenge 内存存储 | P2 | 多 worker 部署 | Passkey 注册/登录偶尔失败 |
| Cookie Path /api | 信息 | 非 /api 路径不发送 | Cookie 不泄露到静态资源 |

---

## 8. 内容系统审查

### 8.1 数据流

```
┌──────────────────────────────────────────────────┐
│                   Frontend                        │
│  page.tsx → hook/component → src/lib/api/*.ts    │
│       │                                              │
│       ▼                                              │
│  fetch(API_BASE/api/...) credentials:'include'     │
└──────────────────┬───────────────────────────────┘
                   │ HTTP (Cloudflare Tunnel)
┌──────────────────▼───────────────────────────────┐
│                Backend FastAPI                     │
│  routers/*.py → get_current_admin/get_optional_user │
│       │                                              │
│       ▼                                              │
│  services/*.py → models/*.py → PostgreSQL          │
│       │                                              │
│       ▼                                              │
│  schemas/*.py → JSON Response                      │
└──────────────────────────────────────────────────┘
```

### 8.2 博客

- 数据源：PostgreSQL（`notes` 表 type='blog'）✅
- 列表 API：`GET /api/notes?type=blog` ✅
- 详情 API：`GET /api/notes/{slug}` ✅
- Markdown 渲染：client-side `use-markdown-render`（html-react-parser 不净化 HTML）⚠️
- 草稿/发布状态：`Note.status` 字段（draft/published）✅
- 摘要/封面/标签/时间：✅
- 前台隐藏：`Note.hidden` 字段，非 admin 不可见 ✅

### 8.3 笔记

- 与博客共享 Note 模型，type='note' 区分 ✅
- 分类/标签/搜索：✅
- 文件夹组织：✅
- Markdown 支持：✅
- 空状态：✅

### 8.4 错题

- SM-2 间隔重复参数（ef, interval, repetitions, next_review, last_reviewed）：✅
- 题目/答案/解析/来源/标签：✅
- 科目/难度筛选：✅
- 隐私风险：错题包含个人学习内容，但需要认证才可写入 ✅；但复习页面公开 ❌（P0-04）
- 上传图片：`images` 字段 + `upload-image` API，存储于 `public/images/pictures/` ✅

### 8.5 发现

- 分享/博主/项目/图片：通过 `content_store` 管理 ✅
- 空状态：✅
- 外链安全：`rel="noopener noreferrer"` ✅
- 图片无 onError 处理 ⚠️

### 8.6 留言

| 检查项 | 状态 |
|--------|------|
| 输入长度限制 | ✅ maxLength=2000（前端），max_length=2000（schema） |
| XSS 防护 | ⚠️ 存储为纯文本 ✅，但渲染时无额外 HTML 编码 |
| Spam 防护 | ✅ 速率限制（5 条/60 秒）+ 24 小时 ban |
| 频率限制 | ✅ |
| 审核机制 | ✅ 管理员可隐藏/恢复 |
| 匿名可见 | ✅ 无需登录 |
| 访客隐私 | ⚠️ IP + User-Agent 存储 |

---

## 9. public 暴露面审查

### 9.1 可公开文件 ✅

| 路径 | 说明 |
|------|------|
| `public/favicon.png` | 网站图标 |
| `public/manifest.json` | PWA manifest |
| `public/images/avatar.png` | 头像 |
| `public/images/cursor.svg` | 自定义光标 |
| `public/images/christmas/*.webp` | 圣诞雪花装饰 |
| `public/images/hats/*.webp` | 帽子装饰 |
| `public/blogs/index.json` | 空占位符 |
| `public/blogs/categories.json` | 空占位符 |

### 9.2 可疑文件 ⚠️

| 路径 | 风险 | 建议 |
|------|------|------|
| `public/images/pictures/03bd49...png` | 可能包含个人信息，git 已追踪 | 审查内容后决定 |
| `public/images/pictures/079a7a...png` | 同上 | 同上 |
| `public/mymusic/selection.json` | UI 状态，无需公开 | 移入数据库或 localStorage |

### 9.3 应迁移/保护文件 🚨

| 路径 | 风险 | 建议 |
|------|------|------|
| `public/operator-passkey-register.html` | 攻击面 | 考虑 IP 白名单或移出 public/ |
| `public/mymusic/孙燕姿-天黑黑.mp3` | 版权侵权 | 清除 git 历史 + gitignore |
| `public/mymusic/孙燕姿-遇见.mp3` | 版权侵权 | 清除 git 历史 + gitignore |

### 9.4 已保护文件 ✅

- `/public/images/pictures/` — gitignore 生效 ✅
- 无 .env / .sql / .pem / .key 文件 ✅

### 9.5 风险等级

| 等级 | 文件数 | 说明 |
|------|--------|------|
| 🚨 高风险 | 3 | mp3 版权文件 + 可能的个人信息图片 |
| ⚠️ 中风险 | 3 | selection.json + 2 张 tracked PNG |
| ✅ 低风险 | 其余 | 正常静态资源 |

---

## 10. 文档与工程治理审查

### 10.1 README.md

**覆盖度**：

| 检查项 | 状态 |
|--------|------|
| 项目定位 | ✅ 个人知识库与博客系统 |
| 本地启动 | ✅ 详细步骤（前端+后端+数据库） |
| 环境变量 | ✅ 关键变量表格 |
| 数据库迁移 | ✅ alembic upgrade head |
| 部署 | ✅ Cloudflare Workers runbook |
| 测试 | ✅ 验证命令表格 |
| 贡献指南 | ✅ 引用 CONTRIBUTING.md 和 SECURITY.md |
| AI 配置 | ✅ 多种 Provider 说明 |

**评分：85/100**。缺少：常见问题排查、开发环境 vs 生产环境差异说明。

### 10.2 AGENTS.md

**覆盖度**：

| 检查项 | 状态 |
|--------|------|
| 修改边界 | ✅ 前后端分层规则 |
| 先读 docs | ✅ Required First Steps |
| 运行测试 | ✅ Validation Rules |
| 禁止提交密钥 | ✅ "Never commit real .env, private keys, tokens..." |
| 输出格式 | ✅ Task Workspace 结构 |
| 冲突指令 | ❌ 未发现冲突 |

**评分：90/100**。是高质量的 Agent 约束文件。

### 10.3 docs/

| 目录/文件 | 状态 | 问题 |
|-----------|------|------|
| `docs/acceptance/` | 空 | 无验收文档 |
| `docs/design/` | 空 | 设计文档分散在根 docs/ 下 |
| `docs/requirements/` | 空 | 需求文档分散 |
| `docs/risks/` | 空 | 无风险登记册 |
| `docs/tasks/` | 空 | 任务管理分散 |
| `docs/workflows/` | 21 个任务文件夹 | 结构良好 ✅ |
| 根 docs/ 下的 .md 文件 | 多个设计/需求/审计文档 | 应移入对应子目录 |

### 10.4 scripts/

| 文件 | 说明 | 问题 |
|------|------|------|
| `scripts/setup.mjs` | 一键检查/初始化/设置 | 功能完整 ✅ |
| `scripts/check-project.mjs` | 项目验证 | ✅ |
| `scripts/gen-svgs-index.js` | SVG 索引生成 | 用途明确 ✅ |
| `scripts/start-frontend.sh` | 前端启动 | 简单脚本 ✅ |

### 10.5 .github/

| 检查项 | 状态 |
|--------|------|
| 前端 lint/build | ✅ `npx tsc --noEmit` + `npm run build` |
| 后端 test | ✅ `python -m pytest tests/` |
| 类型检查 | ✅ |
| 依赖审计 | ❌ 缺少 `npm audit` / `pip audit` |
| PR 模板 | ✅ |
| Issue 模板 | ✅ bug_report.yml + feature_request.yml |

### 10.6 Agent 配置 (.agents/, .kilo/)

存在 `.agents/`、`.kilo/`、`.playwright-mcp/` 目录，用于 Agent 和 Playwright 自动化。未深度审查。

---

## 11. 测试与 CI 审查

### 11.1 已有测试

| 测试文件 | 数量 | 覆盖 |
|----------|------|------|
| `test_ai_deterministic_repair.py` | 1 | 确定性修复函数 |
| `test_ai_provider_models.py` | 3 | Provider 配置 |
| `test_local_music_source.py` | 5 | 本地音乐源 |
| `test_mistake_staged_workflow.py` | ~20 | 错题分阶段 schema |
| `test_temp_admin_bootstrap.py` | 3 | CLI admin 引导 |
| **合计** | **~33** | |

### 11.2 建议新增测试

按优先级排列：

1. **认证测试**（P0）
   - `POST /api/auth/login` 正确密码返回 200 + Set-Cookie
   - `POST /api/auth/login` 错误密码返回 401，不泄露用户存在性
   - `GET /api/auth/me` 无 Cookie 返回 401
   - `GET /api/auth/me` 有效 Cookie 返回用户信息
   - `POST /api/auth/logout` 后 me 返回 401

2. **权限测试**（P0）
   - 匿名 GET `/api/notes?type=blog` 仅返回 published 非 hidden
   - 匿名 POST/PUT/DELETE 任何 `/api/notes/*` 返回 401
   - 匿名 POST `/api/review/{slug}` 返回 401
   - 非 admin 用户访问管理 API 返回 403
   - Password 级别 session 访问 passkey-only 端点返回 403

3. **CRUD 测试**（P1）
   - 创建/读取/更新/删除笔记完整流程
   - 创建笔记 slug 冲突处理
   - 批量删除
   - 文件夹移动

4. **留言测试**（P1）
   - 创建留言（匿名）
   - XSS payload `<script>alert(1)</script>` 不应执行
   - 速率限制后返回 429
   - Ban 后返回 403
   - 管理审核（隐藏/恢复）

5. **上传测试**（P2）
   - 上传合法图片返回 URL
   - 上传非图片文件返回 400
   - 上传超大文件返回 413

---

## 12. 环境变量与部署审查

### 12.1 环境变量风险

| 变量 | 位置 | 风险 |
|------|------|------|
| `DASHSCOPE_API_KEY` | `backend/.env` | 发现疑似密钥，位置：`backend/.env:13` |
| `DEEPSEEK_API_KEY` | `backend/.env` | 发现疑似密钥，位置：`backend/.env:14` |
| `OPERATOR_REGISTRATION_KEY` | `backend/.env` | 发现疑似密钥，位置：`backend/.env:17` |
| `JWT_SECRET_KEY` | `backend/.env` | 已脱敏显示，确认非默认值 |
| `DATABASE_URL` | `backend/.env` | 已脱敏显示 |

**git 追踪状态**：以上文件未被 git 追踪（`.gitignore` 中 `.env*` 规则生效）。

### 12.2 环境变量清单

| 变量 | .env.example 中存在 | 默认值 | 说明 |
|------|---------------------|--------|------|
| `NEXT_PUBLIC_API_URL` | ✅ | `http://localhost:8000` | ✅ |
| `NEXT_PUBLIC_IMAGE_BASE_URL` | ✅ | 无 | 缺少说明 |
| `NEXT_PUBLIC_SITE_URL` | ✅ | 无 | RSS 使用 |
| `SITE_URL` | ✅ | VERCEL_URL fallback | sitemap 使用 |
| `ENV` | ✅ | development | ✅ |
| `DATABASE_URL` | ✅ | 本地 | ✅ |
| `JWT_SECRET_KEY` | ✅ | 默认（生产检测） | ✅ |
| `ALLOWED_ORIGINS` | ✅ | 本地域名 | ✅ |
| `AUTH_BYPASS` | ✅ | false | ✅ |
| `AUTH_BYPASS_ALLOW` | ✅ | false | ✅ |
| `WEBAUTHN_RP_ID` | ✅ | localhost | ✅ |
| `WEBAUTHN_ORIGIN` | ✅ | localhost | ✅ |
| `OPERATOR_REGISTRATION_KEY` | ✅ | 空 | 空时禁用 ✅ |
| `ENABLE_REGISTRATION` | ✅ | true | ⚠️ 生产应默认 false |
| `REGISTRATION_KEY` | ✅ | 空 | ✅ |

### 12.3 CORS

- 本地默认：`localhost:2025, localhost:3000, 127.0.0.1:2025, 127.0.0.1:3000` ✅
- `config.py` 默认值硬编码了生产域名 `https://blog.limengyang.me` — ⚠️ 应仅本地
- 生产检测：拒绝 `*` ✅
- allow_methods=["*"], allow_headers=["*"] — ⚠️ 可以收紧

### 12.4 部署

- 前端：Cloudflare Workers + OpenNext
- 后端：独立 FastAPI 服务，通过 `public-api.limengyang.me`
- 反向代理：Cloudflare Tunnel
- 备份策略：未提及

---

## 13. 修复路线图

### 第 1 天必须修复（P0）

1. 为 4 个缺失 AuthGate 的路由添加认证（P0-01, P0-02, P0-03, P0-04）
2. 修复 `GET /api/recommendations/today` 副作用（P0-05）
3. 添加 AUTH_BYPASS 生产环境启动检查（P0-06）
4. 确认 `backend/.env` 中的 API Key 轮换（如有泄露风险）

### 第 1 周建议修复（P1）

1. 3 个详情页启用 SSR + generateMetadata（P1-01 至 P1-03）
2. 添加 robots.ts（P1-04）
3. 扩展 sitemap.ts（P1-05）
4. Schema 添加 max_length 约束（P1-06 至 P1-08）
5. 审计日志脱敏（P1-09）
6. 速率限制器修复（P1-10 至 P1-11）

### 第 1 个月优化（P2）

1. 清除 git 历史中的 mp3 文件（P2-01）
2. 审查并处理 2 张 tracked PNG（P2-02）
3. 移动 operator-passkey-register.html（P2-03）
4. 前端/后端代码质量改进（P2-04 至 P2-12）
5. 补充测试（认证、权限、CRUD、留言、上传）
6. 移动 docs/ 根目录文档到子目录
7. CI 添加依赖审计
8. 编写备份策略文档

---

## 14. 给下一轮 Codex 修复的 Prompt

```
请按以下优先级修复 2025-blog-public 项目的安全和架构问题。

## P0 修复（立即，按顺序）

1. 为以下 4 个文件包裹 AuthGate 组件：
   - src/app/write/[slug]/page.tsx
   - src/app/write-note/[slug]/page.tsx
   - src/app/write-mistake/[slug]/page.tsx
   - src/app/mistakes/review/page.tsx
   参考 src/app/write/page.tsx 的使用方式。对于 review 页面，同时在后端 router review.py 的 submit_review 端点添加 get_current_admin 依赖。

2. 修复 backend/app/routers/recommendations.py 中 GET /today 端点：
   将 get_or_create_today_recommendation 调用拆分为：GET 仅返回已有推荐或 null；新建推荐移至 POST 端点（需 admin 权限）。

3. 在 backend/main.py 的 lifespan 中添加 AUTH_BYPASS 生产环境检查：
   如果 ENV=production 且 AUTH_BYPASS=true 且 AUTH_BYPASS_ALLOW=true，则应 sys.exit 拒绝启动（类似已有的 JWT/CORS 检查）。

## P1 修复（按顺序）

4. 为以下文件移除 ssr: false 并添加 generateMetadata：
   - src/app/blog/[id]/page.tsx
   - src/app/notes/[id]/page.tsx
   - src/app/about/page.tsx

5. 创建 src/app/robots.ts 输出 robots.txt。

6. 扩展 src/app/sitemap.ts：加入笔记、错题、发现、关于等页面的 URL。

7. 为以下 Pydantic schema 字段添加 max_length 约束（使用 Field）：
   - backend/app/schemas/note.py: NoteCreate.content, title, summary, cover, category, subject, question, my_answer, correct_answer, analysis, knowledge_points
   - backend/app/schemas/auth.py: LoginRequest.username, password; RegisterRequest.password; SetPasswordRequest.password
   - backend/app/schemas/content.py: 所有 str 字段

8. 为 NoteCreate.ai_metadata 添加 dict 约束或替换为更严格的类型。

9. 为 content_store.py 的 get_default_content 添加 schema 验证。

10. 在 audit_service.py 中添加敏感字段脱敏（password 等）。

11. 修复 backend/app/utils/rate_limit.py：清理后删除空列表 key；考虑 asyncio.Lock。

12. 将 backend/app/routers/ai.py 的速率限制改为按用户：
    将 `_check_rate_limit("global")` 改为 `_check_rate_limit(str(user.id))`。

## 约束

- 不要修改 backend/.env 中的值
- 不要删除 public/ 下任何文件（除非明确授权）
- 每个修复后运行相关测试或验证命令
- 修复 P0 项后再开始 P1 项
- 遇到冲突或不确定时停止并询问
```

---

## 附录 A：审查工具与命令

以下为审查过程中使用/引用的命令：

```bash
# 检查 git 追踪状态
git ls-files backend/.env .env .env.production .env.development

# TypeScript 类型检查
npx tsc --noEmit

# 前端构建
npm run build

# 后端导入检查
cd backend && python -c "from main import app"

# 后端测试
cd backend && python -m pytest tests/ -v

# Alembic 状态
cd backend && alembic current
```

---

## 附录 B：文件引用索引

| 序号 | 文件路径 | 主要问题 |
|------|----------|----------|
| 1 | `src/app/write/[slug]/page.tsx` | P0-01 无 AuthGate |
| 2 | `src/app/write-note/[slug]/page.tsx` | P0-02 无 AuthGate |
| 3 | `src/app/write-mistake/[slug]/page.tsx` | P0-03 无 AuthGate |
| 4 | `src/app/mistakes/review/page.tsx` | P0-04 无认证 |
| 5 | `backend/app/routers/recommendations.py:17-18` | P0-05 GET 写入 |
| 6 | `backend/app/routers/auth.py:62-66` | P0-06 AUTH_BYPASS |
| 7 | `src/app/blog/[id]/page.tsx:5` | P1-01 ssr:false |
| 8 | `src/app/notes/[id]/page.tsx:5` | P1-02 ssr:false |
| 9 | `src/app/about/page.tsx:5` | P1-03 ssr:false |
| 10 | `backend/app/schemas/note.py:28,48` | P1-06/07 无 max_length |
| 11 | `backend/app/services/content_store.py:25` | P1-08 无验证 |
| 12 | `backend/app/utils/rate_limit.py:16` | P1-10 内存泄漏 |
| 13 | `backend/app/routers/ai.py:106-112` | P1-11 全局速率限制 |
| 14 | `public/mymusic/孙燕姿-天黑黑.mp3` | P2-01 版权 |
| 15 | `public/operator-passkey-register.html` | P2-03 暴露面 |
| 16 | `backend/app/config.py:11` | P2-05 默认值含生产域名 |

---

> **审查结束**。本报告包含 6 个 P0 问题、11 个 P1 问题、12 个 P2 问题。建议按第 13 节路线图顺序修复。修复后运行附录 A 中的验证命令。
