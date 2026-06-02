# 个人笔记本与博客系统闭环与安全修复设计文档 (Revised Edition)

> **历史参考文档**。当前设计文档见 `docs/roadmap-design.md`。本文档 P0/P1 修复项已基本完成。

基于《博客及笔记系统全链路可用性与安全审计报告》的审查结论，结合最新的“无需考虑内容越权保护”及“重构安全架构与底线”的指令，本文档重写了全部修复与改进技术方案。本方案聚焦于系统闭环与基础安全，剔除 premature 级别功能扩展，并重新编排优先级。

---

## P0：阻断与安全底线修复

### 2.1 博客删除的数据库同步连动清理

#### 1. 问题描述
当前通过前台 `/write/[slug]` (编辑模式) 删除博客文章时，前端逻辑仅删除了 GitHub 仓库下的静态文件及更新静态索引（`public/blogs/{slug}` 和 `index.json`），但并未向 FastAPI 后端发送删除请求。这导致该博客对应的 `Note` 数据仍残留在 PostgreSQL 数据库中，前台虽无法通过静态渲染显示，但管理后台与后端 API 检索中出现“幽灵博客”。

#### 2. 影响范围
- 前端删除服务：[delete-blog.ts](file:///Users/limengyang/2025-blog-public/src/app/write/services/delete-blog.ts)
- 数据库状态：PostgreSQL 中的 `notes` 表

#### 3. 修改文件
- `src/app/write/services/delete-blog.ts`

#### 4. 设计方案
- 引入后端 API 的 `deleteNote` 请求。
- 在 `deleteBlog` 逻辑中，当 GitHub 上的文件删除并成功更新 Ref 分支后，立即调用 `deleteNote(slug)` 接口。
- **补偿与救济设计**：如果 GitHub 删除成功，但数据库删除（因网络或数据库故障）失败，系统不可直接吞掉异常。必须捕获此错误并使用 Toast 醒目提示用户：“GitHub 静态文件已成功删除，但后端数据库记录清理失败！这会导致管理后台依然存在该条目。补救措施：请前往管理面板（/manage）找到该条目并点击‘删除’进行手动清理。”，并将错误向上抛出。

#### 5. 最小实现路径
1. 导入 `deleteNote` 客户端 API。
2. 在 `updateRef` 执行成功后，包裹在 `try...catch` 中调用 `deleteNote(slug)`。
3. 若 catch 到异常，调用 `toast.error(..., { duration: 10000 })` 并抛出错误。

#### 6. 回滚方案
- 移除 `deleteNote(slug)` 调用并恢复 [delete-blog.ts](file:///Users/limengyang/2025-blog-public/src/app/write/services/delete-blog.ts) 到前一版本。

#### 7. 验收标准
- 发布一篇新博客，在编辑页点击“删除”。
- 检查 GitHub Commit 记录，静态文件已被删除。
- 检索 PostgreSQL 数据库 `SELECT * FROM notes WHERE slug = 'xxx'`，返回结果为空。
- 模拟数据库故障（如让 deleteNote 返回 500 状态），触发删除时前端弹窗大红字告警并详细提示补救。

#### 8. 必须补充的测试用例
- **成功删除流**：GitHub 删除成功 -> DB 删除成功 -> 流程顺畅结束。
- **补偿失败流**：GitHub 删除成功 -> DB 删除返回 500 -> 触发 10 秒以上持久化补偿 Toast 提示。

---

### 2.2 笔记表单元数据（分类与科目）自动加载

#### 1. 问题描述
新建笔记页面 `/write-note` 加载时，并没有对可选的分类与科目数据进行初始化加载。导致分类下拉菜单仅有硬编码的“无分类”，科目输入框没有任何 autocomplete 候选词。

#### 2. 影响范围
- 前端页面：[write-note/page.tsx](file:///Users/limengyang/2025-blog-public/src/app/write-note/page.tsx)
- 用户新增笔记的输入体验与数据规范化。

#### 3. 修改文件
- `src/app/write-note/page.tsx`

#### 4. 设计方案
- 引入 React 的 `useEffect` 钩子以及 API 客户端 `listCategories` 和 `listSubjects`。
- 在页面挂载阶段，通过 `Promise.all` 并发拉取后端已有的分类和科目，成功后将结果设置到 `categories` 和 `subjects` 的 useState 中。

#### 5. 最小实现路径
1. 导入 `useEffect`。
2. 添加 `useEffect` 挂载函数，并发请求，并加错误 catch 日志输出防止挂起。
3. 渲染分类的 `select` 和科目的 `datalist`。

#### 6. 回滚方案
- 移除 `useEffect` 逻辑，数据状态恢复为空。

#### 7. 验收标准
- 打开 `/write-note` 页面。
- 确认分类下拉框中已呈现后端返回的所有有效分类。
- 确认科目输入框有正确的联想下拉。

#### 8. 必须补充的测试用例
- **首屏并发加载用例**：页面挂载时调用 API 次数等于 2。
- **异常捕获用例**：若后端接口加载失败，控制台输出 `Failed to load categories/subjects`，但不阻断页面正常输入。

---

### 2.3 跨域配置（CORS）与 Credential 冲突修复

#### 1. 问题描述
在后端 `backend/main.py` 中，`CORSMiddleware` 配置了 `allow_origins=["*"]` 和 `allow_credentials=True`。根据 W3C 规范与现代浏览器安全机制，当 `allow_credentials=True` 时，允许的 Origin 绝不能为通配符 `*`，否则浏览器会拦截跨域凭证请求（如携带 Authorization Bearer 头部的 API 请求），导致无法跨域登录和操作。

#### 2. 影响范围
- 后端中间件与全局跨域策略。
- 前域与后域之间的网络请求通信。

#### 3. 修改文件
- `backend/app/config.py`
- `backend/main.py`

#### 4. 设计方案
- 生产环境禁止使用 `*`。
- 从环境变量 `ALLOWED_ORIGINS` 动态读取跨域可信域名列表。
- 后端 `Settings` 增加 `ALLOWED_ORIGINS: str` 字段，默认值为 `"http://localhost:2025,http://localhost:3000,http://127.0.0.1:2025,http://127.0.0.1:3000"`。
- 在 `main.py` 启动解析该字段，将其按逗号分割成字符串列表传递给 `allow_origins`。
- 生产校验：若 `settings.ENV == "production"` 且 `ALLOWED_ORIGINS` 包含通配符 `*` 或为空，则抛出异常，强制阻断服务启动。

#### 5. 最小实现路径
1. 修改 `config.py` 增加 `ALLOWED_ORIGINS` 配置。
2. 修改 `main.py` 处理 `split(',')` 提取 origins。
3. 在 `lifespan` 阶段增加生产环境下 `*` 检测，若检测到 `*` 则调用 `sys.exit("CORS settings invalid")`。

#### 6. 回滚方案
- 恢复 `allow_origins=["*"]` 并将 `allow_credentials` 改为 `False`（若不携带 Token 认证）或直接恢复原代码。

#### 7. 验收标准
- 环境变量 `ALLOWED_ORIGINS="http://localhost:2025"`，使用该源进行 API 请求，响应头正确包含 `Access-Control-Allow-Origin: http://localhost:2025` 且 `Access-Control-Allow-Credentials: true`。
- 生产模式下（`ENV=production`），将 `ALLOWED_ORIGINS` 设为 `*`，应用直接崩溃报错无法启动。

#### 8. 必须补充的测试用例
- **有效可信源测试**：提供合法的可信源，确保跨域请求凭证正常通过。
- **非法源测试**：非可信源发起请求，浏览器拦截。
- **生产拦截测试**：验证 `*` 安全阻断机制是否生效。

---

### 2.4 Hidden 笔记匿名泄露修复

#### 1. 问题描述
当前后端 `GET /api/notes/{slug}` 和列表接口 `GET /api/notes` 没有根据用户身份严格区分 hidden 数据和 draft 状态的查看。任何匿名用户都可以通过直接拼装 slug 请求详情接口拿到 Hidden 笔记的全部正文，造成敏感信息泄露。

#### 2. 影响范围
- 后端笔记路由：`backend/app/routers/notes.py`
- 前台公开页面与管理面板的数据可见性。

#### 3. 修改文件
- `backend/app/routers/notes.py`

#### 4. 设计方案
- 引入可选的认证用户依赖 `get_optional_user`。
- 在 `list_notes` 和 `get_note` 中根据 `current_user` 的角色制定三层访问规则：
  - **匿名用户（未登录）**：
    - `list_notes` 仅返回 `hidden == False` 且 `status == "published"` 的数据。
    - `get_note` 查到 `hidden == True` 或 `status == "draft"` 的内容时，直接抛出 `404 Not Found`（防止泄露 slug 存在）。
  - **已登录普通用户（is_admin == False）**：
    - 与匿名用户规则完全相同（防止注册普通用户绕过隐私）。
    - `list_notes` 强制过滤 `hidden == False`，`get_note` 访问 hidden 时报 `404`。
  - **管理员（is_admin == True）**：
    - 完全放行。可查询/获取 `hidden == True/False` 和 status 为任意值的文章。

#### 5. 最小实现路径
1. 在 `notes.py` 内部或 `auth.py` 实现 `get_optional_user`，该依赖获取 Header 中 token 但若无 token 不抛 401 而是返回 `None`。
2. 在 `list_notes` 中根据 `is_admin` 状态判定，非管理员一律覆盖 `hidden = False` 和 `status = "published"` 查询条件。
3. 在 `get_note` 中做对应判断，非管理员且是隐私/草稿内容时返回 404。

#### 6. 回滚方案
- 移除 `get_optional_user` 校验，退回到直接无校验返回。

#### 7. 验收标准
- 匿名浏览器访问 `/api/notes/hidden-slug` -> 返回 404。
- 普通用户（`is_admin == False`）携带 Token 访问 `/api/notes/hidden-slug` -> 返回 404。
- 管理员（`is_admin == True`）携带 Token 访问 `/api/notes/hidden-slug` -> 返回 200 及正文。

#### 8. 必须补充的测试用例
- **匿名权限拦截测试**：验证 404。
- **普通用户权限拦截测试**：验证 404。
- **管理员权限放开测试**：验证 200。

---

### 2.5 生产环境 JWT_SECRET_KEY 默认值阻断

#### 1. 问题描述
`backend/app/config.py` 中 `JWT_SECRET_KEY` 的默认值为硬编码的 `"your-secret-key-change-this"`。若在生产环境部署时没有覆盖此密钥，攻击者可轻易签发合法的 JWT Token 获取系统的所有管理员控制权。

#### 2. 影响范围
- 后端系统安全与鉴权中心。
- 生产环境启动流程。

#### 3. 修改文件
- `backend/app/config.py`
- `backend/main.py`

#### 4. 设计方案
- 增加 `ENV` 配置项，区分 `development` 与 `production`。
- 在 `main.py` 的 lifespan 启动初始化函数中进行安全审计断言：
  - 如果检测到 `settings.ENV == "production"` 且 `settings.JWT_SECRET_KEY` 仍为默认值 `"your-secret-key-change-this"`，则向终端输出显眼的红色高危警告信息，并立即执行 `sys.exit("CRITICAL SECURITY ERROR: JWT_SECRET_KEY is insecure.")` 强行终止服务启动。

#### 5. 最小实现路径
1. 在 `config.py` 中为 `Settings` 类添加 `ENV: str = "development"`。
2. 在 `main.py` 的 lifespan 启动钩子中编写该安全校验，使用 `sys.exit` 阻断。

#### 6. 回滚方案
- 注释掉启动校验中的 `sys.exit()` 调用。

#### 7. 验收标准
- 设置环境变量 `ENV=production` 且不设置 `JWT_SECRET_KEY`。
- 启动后端 `uvicorn main:app`。
- 观察服务直接打印异常安全警示并退出启动，端口未开放。

#### 8. 必须补充的测试用例
- **生产环境默认密钥校验用例**：生产环境 + 默认密钥 -> 启动失败。
- **生产环境自定义密钥校验用例**：生产环境 + 自定义安全密钥 -> 启动成功。

---

### 2.6 限制公开注册接口

#### 1. 问题描述
由于该笔记本为**单用户/个人**系统，`/api/auth/register` 接口对公网完全暴露。任何未授权访客均可在生产环境下注册账号，绕过管理员独占限制，写入并更改数据库内容。

#### 2. 影响范围
- 后端用户模块：`backend/app/routers/auth.py`

#### 3. 修改文件
- `backend/app/config.py`
- `backend/app/schemas/auth.py`
- `backend/app/routers/auth.py`

#### 4. 设计方案
- 在 `Settings` 中引入：
  - `ENABLE_REGISTRATION: bool = True`（生产环境下默认为 `False`）
  - `REGISTRATION_KEY: str = ""`
- 在 `RegisterRequest` Schema 中添加：
  - `registration_key: str | None = None`
- 在 `/register` 路由中逻辑处理：
  1. 如果 `settings.ENABLE_REGISTRATION` 为 `False`，直接抛出 `403 Forbidden`。
  2. 如果提供了非空 `settings.REGISTRATION_KEY`，校验请求 payload 中的 `registration_key` 或请求头 `X-Registration-Key` 是否与后端配置相符，不匹配则抛出 `403 Forbidden`。
  3. 生产安全默认：当 `settings.ENV == "production"` 时，如果未明确提供安全非空的 `REGISTRATION_KEY`，则一律强制关闭注册功能（`ENABLE_REGISTRATION` 被覆盖强置为 `False`）。

#### 5. 最小实现路径
1. 更新 `config.py` 添加相关属性。
2. 更新 `schemas/auth.py` 添加 `registration_key` 字段。
3. 修改 `auth.py` 路由函数，在最前端插入注册开关和 Key 校验条件。

#### 6. 回滚方案
- 将 `ENABLE_REGISTRATION` 重新设定为 `True`，且不设置 `REGISTRATION_KEY`。

#### 7. 验收标准
- 当注册关闭时，向 `/api/auth/register` 发起请求，返回 `403 Forbidden`。
- 当注册开启且设置了 Key 时，若不带 Key 或 Key 错误，返回 `403 Forbidden`；提供正确 Key 时注册成功并返回 201。

#### 8. 必须补充 of 测试用例
- **生产关闭用例**：ENV=production -> 未设置 key 无法注册。
- **密钥匹配用例**：设置了 registration_key，使用错误 key 注册失败，使用正确 key 注册成功。

---

## P1：系统安全与可靠性增强

### 3.1 所有写入/变更接口的管理员与 Owner 校验

#### 1. 问题描述
当前后端除了部分普通认证外，并未区分管理员权限。在 `notes`、`tags`、`subjects`、`categories`、`music` 和 `recommendations` 等模块的增删改接口中，仅仅依赖 `get_current_user` 校验是否登录，缺少管理员（Owner）特权验证。这使得非管理员账号（只要是成功通过 auth 接口注册的账号）能够越权增删改系统核心内容。

#### 2. 影响范围
- 所有包含写操作 (POST / PUT / DELETE) 的后端路由文件。
- 用户权限模型：`backend/app/models/note.py` (User 增加 is_admin 字段)

#### 3. 修改文件
- `backend/app/models/note.py`
- `backend/app/schemas/auth.py`
- `backend/app/routers/auth.py` (提供 `get_current_admin` 依赖)
- `backend/app/routers/` 下的 `notes.py`, `tags.py`, `subjects.py`, `categories.py`, `music.py`, `recommendations.py`

#### 4. 设计方案
- **模型扩展**：
  - `User` 模型中增加字段：`is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")`。
  - 需要在数据库新增 Alembic 迁移脚本 `003_add_user_admin_field.py`。
- **校验逻辑**：
  - 编写 `get_current_admin` 依赖函数：
    ```python
    async def get_current_admin(user: User = Depends(get_current_user)) -> User:
        if not getattr(user, "is_admin", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
        return user
    ```
  - 将上述模块中所有写接口中的 `Depends(get_current_user)` 替换为 `Depends(get_current_admin)`。

#### 5. 最小实现路径
1. 生成并执行 Alembic 迁移，给 `users` 表添加 `is_admin` 字段。
2. 在 `auth.py` 中封装 `get_current_admin` 依赖。
3. 搜索全局的变更路由，把写操作参数从 `_user=Depends(get_current_user)` 替换为 `_admin=Depends(get_current_admin)`。

#### 6. 回滚方案
- 将依赖退回 `get_current_user`，并删除或保留 `is_admin` 数据库字段。

#### 7. 验收标准
- 注册一个普通用户并登录获取 token。
- 尝试调用 `POST /api/notes` 新建文章，后端返回 `403 Forbidden`。
- 登录管理员（`is_admin = True`）账号，调用 `POST /api/notes` 新建文章，成功返回 201。

#### 8. 必须补充的测试用例
- **普通用户越权拦截测试**：验证 403 响应。
- **管理员正常写入测试**：验证 201/200 响应。

---

### 3.2 博客发布、编辑与删除的 DB/GitHub 双写一致性策略

#### 1. 问题描述
当前博客系统的编辑和删除是双链路运作：前端直接提交给 GitHub，后端同步记录在 PostgreSQL 中。这种弱连动极易因一侧失败发生数据不一致（如数据库存在但 GitHub 提交被驳回，或 GitHub 删除了静态文件但数据库中依然保留条目）。

#### 2. 影响范围
- 博客的新增/编辑页面及提交链路：`/write`，`/write/[slug]`
- 博客删除流程。

#### 3. 修改文件
- `src/app/write/services/push-blog.ts`
- `src/app/write/services/delete-blog.ts`

#### 4. 设计方案
- **双写优先逻辑**：
  - 在新建/更新博客时，前端先执行数据库写入操作（`POST /api/notes` 或 `PUT /api/notes/{slug}`）。
  - 若数据库写操作失败（例如 slug 重复、网络异常等），中断后续逻辑，直接向用户抛出异常，此时 GitHub 没有任何文件变更（事务安全）。
  - 若数据库写入成功，前端再触发 GitHub API 写入静态文件。
  - **一致性补偿回滚**：如果 GitHub 文件写入失败，则必须立即调用 `DELETE /api/notes/{slug}` 将刚才写入后端数据库的临时记录删除（补偿性回滚），并警告用户“发布失败，GitHub 提交异常，后端记录已自动撤销”。
  - **删除流程补偿**（承接自 P0-2.1）：如果删除 GitHub 静态文件成功后，后端 `deleteNote` 调用超时或异常，则向用户展示持久化的 Toast，提供明确的手动补救说明，并在管理页面后台提供一键校对与同步按钮。

#### 5. 最小实现路径
1. 梳理 `use-publish` hook 里的执行流，串行化 DB 保存与 GitHub push。
2. 在 GitHub push 的 `catch` 块中加入 `deleteNote(slug)` 补偿接口调用。

#### 6. 回滚方案
- 退回原独立的并行/单向写入逻辑。

#### 7. 验收标准
- 发布文章时，故意断开网络或模拟 GitHub API 返回 500。
- 检查 GitHub 仓库没有提交。
- 检查数据库中没有刚才输入的错误博客记录。

#### 8. 必须补充的测试用例
- **GitHub 写入失败补偿测试**：验证 DB 撤销调用。
- **全链路成功测试**：确保成功流一切正常。

---

### 3.3 GitHub 密钥 localStorage 长期存储的安全迁移方案

#### 1. 问题描述
GitHub App 的私钥（PEM 文件内容）不应长期保留在浏览器的 `sessionStorage`/`localStorage` 中（即使使用 AES 进行加密，由于前端必须硬编码解密密钥 `ENCRYPT_KEY`，该防护极易被 XSS 等方式攻破，导致严重的供应链安全隐患）。

#### 2. 影响范围
- 前端密钥管理机制与认证获取模块：[src/lib/auth.ts](file:///Users/limengyang/2025-blog-public/src/lib/auth.ts)

#### 3. 修改文件
- `src/lib/auth.ts`
- `src/hooks/use-auth.ts`
- 后端：新增中转 GitHub 写入服务 `backend/app/routers/sync.py` 

#### 4. 设计方案
- **向后端中转的安全架构迁移**：
  - 核心思想：客户端不直接交互 GitHub，不持有 PEM 私钥，私钥与 GitHub App Token 的获取与计算收归至 FastAPI 后端环境。
  - 将原前端 `github-client.ts` 中的文件合并、分支更新、文件树构建的逻辑，整体重构迁移至后端 Python 的 GitHub 服务中。
  - 后端提供安全的中转接口：例如 `POST /api/sync/publish-blog`，需要校验 `get_current_admin` 身份。
  - 前端只需将文章的 JSON Payload 投递给后端中转接口，后端利用从本地安全 `.env` 读取的私钥在服务器端自动向 GitHub 发起 commit 动作。
- **平滑迁移实施路径**：
  - **第一步**：保留前端本地 Private Key 的临时缓存功能，作为旧链路的向后兼容，同时在后端实现完整的 GitHub 代理提交路由。
  - **第二步**：当检测到后端配置了 `GITHUB_TOKEN` 或 `GITHUB_PRIVATE_KEY` 环境变量时，前端优先走后端代理中转接口，停止让用户输入私钥。
  - **第三步**：在元数据配置中弃用 `isCachePem` 开关，彻底废弃 `sessionStorage` 的 GITHUB_PEM_CACHE_KEY，移除客户端加密解密（AES）工具模块。

#### 5. 最小实现路径
1. 后端新增代理写入与删除接口。
2. 前端 `push-blog` 替换为优先调用后端代理接口，若失败且无后端配置，才回退到前端私钥提交。

#### 6. 回滚方案
- 重新回退到完全基于客户端 JWT 签发的旧 GitHub App API 交互方案。

#### 7. 验收标准
- 退出登录并清除浏览器缓存，打开管理面板。
- 确认不再弹出“需要输入私钥”的强制限制。
- 成功发布博客后，检查 GitHub 对应提交是由后台环境通过服务器完成。

#### 8. 必须补充的测试用例
- **后端代理上传用例**：普通发布流程流经后端安全代理。
- **无状态验证用例**：清除前端缓存，仍然可以成功发布及同步。

---

### 3.4 错题图片证据的数据库去 base64 化与外部存储持久化

#### 1. 问题描述
AI 分析错题时，前端通过 base64 临时投递图片数据以生成 OCR 和解析。若直接将图片的 base64 数据长期以明文/正文方式存入 PostgreSQL 数据库的 `images` 字段，会导致数据库体积急剧膨胀，带来严峻的性能降级隐患。

#### 2. 影响范围
- 错题库写入与呈现：`/write-mistake` 和 `/notes/[id]`
- 后端 Note 表结构。

#### 3. 修改文件
- `backend/app/models/note.py`
- `backend/app/schemas/note.py`
- `src/app/write-mistake/page.tsx`
- `src/app/notes/[id]/page.tsx`

#### 4. 设计方案
- **数据解耦与引用持久化**：
  - 数据库的 `images` 字段仅允许存储外链图片的元数据（格式如：`[{"url": "https://...", "filename": "xxx.png"}]`），杜绝直接保存 base64 字符串。
  - 方案 A（过渡方案）：前端将图片上传至 GitHub 仓库指定目录下（`public/images/mistakes/`），拿到 GitHub 的相对/绝对 URL 后，将 URL 写进数据库。
  - 方案 B（正式方案）：后端提供专门的图片上传接口 `POST /api/media/upload`，后端将其存储到安全的目标存储服务中（如 Cloudflare R2 / AWS S3），返回存储 URL 后写入数据库。
  - 本设计方案在前端上传时，使用统一的 API client 接口逻辑，对图片进行分步处理：上传文件 -> 获得 URL -> 随 note 模型创建保存 URL 列表。

#### 5. 最小实现路径
1. 限制数据库字段存储规范为 JSON 数组（带 `url` 与 `filename` 键）。
2. 在错题上传时，前端必须先上传图片到托管服务，将拿到的静态 URL 替换 base64，然后随 note 数据写入数据库。

#### 6. 回滚方案
- 在无外部存储时，作为临时兜底，限制存入数据库 base64 的体积（例如必须裁剪至 100KB 以下），但仍必须在外链方案就绪后迁移。

#### 7. 验收标准
- 打开错题录入页面，拖入图片文件。
- 保存错题后，查看数据库 `notes` 表中的 `images` 内容，确认为合法的 URL 地址，未见大段 Base64 杂乱文本。
- 详情页能通过外链成功解析并渲染图片。

#### 8. 必须补充的测试用例
- **图片预上传测试**：测试上传文件，成功拿回外链 URL。
- **引用入库测试**：确认入库 JSON 中只有 `url` 项，没有任何 `base64` 信息。

---

### 3.5 博客详情与管理面板的动态跳转路由修复

#### 1. 问题描述
在笔记详情页 `/notes/[id]` 和管理后台管理面板 `/manage` 的表格中，所有类型的条目的“编辑”按钮均被硬编码重定向至 `/write-note/[slug]`。这导致用户在编辑 `blog` 类型的条目时，会被误引导进入普通笔记编辑器，编辑保存只会更新数据库，无法触发 GitHub 同步流程，造成双端数据割裂。

#### 2. 影响范围
- 笔记详情页面：`src/app/notes/[id]/page.tsx`
- 内容管理列表：`src/app/manage/page.tsx`

#### 3. 修改文件
- `src/app/notes/[id]/page.tsx`
- `src/app/manage/page.tsx`

#### 4. 设计方案
- 在两个页面渲染“编辑”链接的地方，增加基于条目 `type` 的动态判断逻辑：
  - 如果条目 `type === 'blog'`，编辑 URL 路径为 `/write/${item.slug}`。
  - 否则（`type === 'note'` 或 `type === 'mistake'`），编辑 URL 路径为 `/write-note/${item.slug}`。

#### 5. 最小实现路径
- 直接修改两个文件中编辑按钮/链接的 `href` 表达式，插入三元条件分支。

#### 6. 回滚方案
- 还原为硬编码形式。

#### 7. 验收标准
- 进入 `/manage` 页面。
- 点击一篇博客的“编辑”，验证页面成功进入 `/write/[slug]`。
- 点击一篇普通笔记的“编辑”，验证页面成功进入 `/write-note/[slug]`。

#### 8. 必须补充的测试用例
- **博客路由跳转校验**：验证 blog 类型返回 `/write/` 开头的地址。
- **笔记路由跳转校验**：验证 note 类型返回 `/write-note/` 开头的地址。

---

### 3.6 前端弹窗警告的原生 alert() 统一替换为 Toast 提示

#### 1. 问题描述
系统内多个功能模块的交互异常提示采用浏览器的原生 `alert()`，阻断线程且视觉风格简陋，而博客发布流程却使用精美的 Toast。用户交互体验不一致。

#### 2. 影响范围
- 涉及页面：`/notes`, `/write-note`, `/write-mistake`, `/mistakes/review`, `/manage` 等。

#### 3. 修改文件
- `src/app/manage/music-tab.tsx`
- `src/app/manage/recommendation-tab.tsx`
- 其他使用原生 `alert` 的页面（若有）

#### 4. 设计方案
- 引入统一的 `toast` (来自 `sonner` 库)。
- 将捕获到异常时的 `alert(...)` 语句全部改造为 `toast.error(...)`、`toast.warning(...)` 或 `toast.success(...)`。
- 保留 `window.confirm(...)` 用于关键删除操作的二次确认。

#### 5. 最小实现路径
- 逐个文件扫描 `alert(`，将其替换为 `toast` 相应样式。

#### 6. 回滚方案
- 还原为原生 `alert()`。

#### 7. 验收标准
- 故意制造一个异常（例如更新音乐排序失败）。
- 确认不再弹出系统的灰色阻塞弹窗，而是优雅地在屏幕边缘弹出 Toast。

#### 8. 必须补充的测试用例
- **Toast 无阻断呈现用例**：确保在抛出异常时，Toast 可以被渲染而无需阻断 JavaScript 主线程执行。

---

## P2：产品交互与体验优化

### 4.1 笔记编辑器增加 Markdown 双栏预览

#### 1. 问题描述
`/write-note` 页面仅有单一的 textarea 文本域，输入 Markdown 语法时排版不直观。

#### 2. 影响范围
- 前端页面：`/write-note/page.tsx` 和 `/write-note/[slug]/page.tsx`

#### 3. 修改文件
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`
- 新增 `src/app/write-note/hooks/use-note-editor-tab.ts`
- 新增 `src/app/write-note/components/note-preview-content.tsx`

#### 4. 设计方案
- 提供“编辑/预览”双模式卡片切换机制。
- 引入 `useMarkdownRender` 动态解析 Markdown 内容。

#### 5. 最小实现路径
- 引入 tab state，默认为 'edit'；若切换到 'preview'，渲染 Markdown。

#### 6. 回滚方案
- 移除切换 tab，直接全屏渲染 textarea。

#### 7. 验收标准
- 点击“预览”标签，正确展示标题和被解析渲染后的 HTML。

#### 8. 必须补充的测试用例
- **Markdown 渲染测试**：验证 LaTeX / 代码块的高亮渲染是否工作。

---

### 4.2 图片 URL 插入工具栏

#### 1. 问题描述
笔记编辑时，用户若想添加网络图片，必须手动拼装复杂的 Markdown 语法 `![]()`。

#### 2. 影响范围
- 前端页面：`/write-note` 编辑输入组件

#### 3. 修改文件
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`

#### 4. 设计方案
- 在编辑器上方新增小型工具快捷条。
- 提供“图片”按钮，点击后弹出提示框让用户输入 URL，自动在光标所在位置插入 `![]({url})`。

#### 5. 最小实现路径
- 获取 textarea ref，读取 `selectionStart` 与 `selectionEnd` 字段进行字符插入并重置光标。

#### 6. 回滚方案
- 移除快捷工具条。

#### 7. 验收标准
- 点击“图片”按钮，输入外链，Markdown 文本框自动在指定光标处出现外链图片的 Markdown 语法。

#### 8. 必须补充的测试用例
- **光标聚焦插入测试**：验证在段落中间点击插入，能正确包裹和还原光标。

---

### 4.3 笔记表单支持封面图字段输入

#### 1. 问题描述
后端 `Note` 表虽然支持 `cover` 字段，但在写笔记页面中无封面图设置入口。

#### 2. 影响范围
- 前端写入页面：`/write-note`

#### 3. 修改文件
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`

#### 4. 设计方案
- 表单新增“封面图 URL”文本框。
- 输入 URL 后提供小型的图片预览卡片以便用户确认外观。

#### 5. 最小实现路径
- 在 state 中新增 `cover` 项，与 input 进行双向绑定，并在其后增加 `img` 预览标签。

#### 6. 回滚方案
- 隐藏封面图输入框。

#### 7. 验收标准
- 填入封面 URL 并在保存后，能在详情页中查看到此封面。

#### 8. 必须补充的测试用例
- **双向数据绑定测试**：确认提交的 payload 携带合法的 `cover` 属性。

---

### 4.4 科目输入框 datalist 候选自动建议

#### 1. 问题描述
输入错题科目时，用户必须全字输入，极易造成同一学科输入命名不统一的问题（如“数学”与“高等数学”）。

#### 2. 影响范围
- 新建/编辑笔记和错题页面。

#### 3. 修改文件
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`
- `src/app/write-mistake/page.tsx`

#### 4. 设计方案
- 结合 HTML5 `<datalist>` 元素，将文本 input 与加载出的 `subjects` 集合绑定，提供既可以自由输入、又可以在下拉选项中直接选择的模式。

#### 5. 最小实现路径
- 渲染 `<input list="subject-options" />` 并挂载 `<datalist id="subject-options">`。

#### 6. 回滚方案
- 撤销 datalist 绑定，恢复为纯文本 input。

#### 7. 验收标准
- 点击“科目”输入框，自动滑出已有的科目列表（如数学、英语等）。

#### 8. 必须补充的测试用例
- **选项匹配测试**：确保输入关联字时，下拉联想自动缩小候选范围。

---

### 4.5 错题无用冗余路由目录清理

#### 1. 问题描述
前端包含一些无用且未开发完毕的空目录路由，导致包体积冗余和代码结构混乱。

#### 2. 影响范围
- 前端路由结构。

#### 3. 修改文件
- 删除目录：`src/app/mistakes/[id]/`
- 删除目录：`src/app/write-mistake/[slug]/`
- 修改文件：`src/app/notes/[id]/page.tsx`

#### 4. 设计方案
- 直接彻底移除上述空目录。
- 详情页中的“返回列表”按钮，基于 type 属性动态将 href 定向至 `/mistakes` 或 `/notes`。

#### 5. 最小实现路径
- 执行物理删除命令并修改跳转条件。

#### 6. 回滚方案
- 重新从 git 恢复删除的目录。

#### 7. 验收标准
- 错题详情页面的“返回”能回到错题列表 `/mistakes`，且本地不再有这两处空文件夹。

#### 8. 必须补充的测试用例
- **编译依赖检查**：删除无用目录后，前端仍能通过 `npm run build`。

---

### 4.6 首页音乐卡片无源曲目播放置灰兜底与 toast

#### 1. 问题描述
当数据库为空或曲目未提供 `preview_url` 时，首页音乐卡片的播放/暂停按钮点击无任何响应，影响用户体验。

#### 2. 影响范围
- 首页音乐卡片：[music-card.tsx](file:///Users/limengyang/2025-blog-public/src/components/music-card.tsx)

#### 3. 修改文件
- `src/components/music-card.tsx`

#### 4. 设计方案
- 在 `togglePlayPause` 逻辑中，当 `currentTrack.preview_url` 为空时，拦截播放动作，执行 `toast.warning('当前曲目没有可播放的音频预览')`。
- 将播放按钮置灰（`opacity-40`），增加 `cursor-not-allowed` 指针。

#### 5. 最小实现路径
- 修改 `togglePlayPause` 条件并应用 clsx 逻辑。

#### 6. 回滚方案
- 移除 toast 并解除按钮置灰。

#### 7. 验收标准
- 点击 `Close To You` 的播放键，屏幕弹出警告 Toast，按钮为半透明状态。

#### 8. 必须补充 of 测试用例
- **无源限制检测**：验证 preview_url 为 null 时 `isPlaying` 保持 False。

---

### 4.7 笔记草稿保存与回收站

#### 1. 问题描述
用户在录入长篇文章时，如果直接退出会导致内容全盘丢失，急需草稿箱和删除安全机制。

#### 2. 影响范围
- 后端 Note 模型扩展，前端状态保存。

#### 3. 修改文件
- `backend/app/routers/notes.py`
- `src/app/manage/page.tsx`
- `src/lib/api/notes.ts`

#### 4. 设计方案
- **草稿**：充分复用已核验的 `status` 字段。保存时可选将 `status` 设为 `'draft'`。
- **回收站（软删除）**：在后端 Note 表中增加 `deleted_at` 字段，默认列表过滤掉已软删除的条目，在管理页增加“回收站”选项卡用于彻底删除或恢复。

#### 5. 最小实现路径
- 新增 `deleted_at` 字段迁移，并在 API 层修改查询语句，支持 `with_deleted` 参数。

#### 6. 回滚方案
- 回滚数据库字段，不提供软删除状态。

#### 7. 验收标准
- 设为草稿的内容匿名无法读取，可在回收站执行恢复。

#### 8. 必须补充的测试用例
- **草稿隐藏测试**：确保草稿无法被公开接口列表渲染。
