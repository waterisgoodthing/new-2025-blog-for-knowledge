# Requirements: AI 错题导航升级 — P1 UI 与路由体验实现

**版本**: v1.0  
**日期**: 2026-06-05  
**来源文档**: [ai-mistake-navigation-upgrade-plan.md](../../ai-mistake-navigation-upgrade-plan.md) §6 P1  
**触及域**: `mistakes`, `notes`, `write-mistake`, `write-note`, `manage`, shared navigation

## 1. 用户角色

| 角色 | 场景 |
|------|------|
| 内容作者 | 在 `/notes` 写笔记/博客，在 `/mistakes` 管理错题 |
| 错题学习者 | 在 `/write-mistake` 录入错题 + AI 分析，在 `/mistakes` 复习 |
| 管理员 | 在 `/manage` 管理内容、音乐、推荐、网站设置 |

## 2. 核心问题

1. **错题页侧栏语义错误**: `/mistakes` 复用 `KnowledgeSidebar`，显示"全部内容""收件箱""笔记""博客"，不符合错题场景
2. **双重入口**: `/write-mistake` 和 `/write-note`（错题 tab）都创建错题，维护两套表单
3. **写作页无返回按钮**: `/write-note`、`/write-mistake` 依赖 `router.back()` 或左上角 mini 主栏返回，不可预期
4. **管理页 tab 无 URL 状态**: `/manage` tab 切换不更新 URL，浏览器前进/后退无法切换 tab
5. **nav-card.tsx mini 主栏语义**: 用户已确认采用 B 方案，即"头像 + Home 图标 + 首页文字"，用于明确返回首页语义

## 3. 功能需求

### FR1: 错题专属侧栏

- **输入**: `/mistakes` 页面渲染时的组件 props
- **处理**: `KnowledgeSidebar` 根据 `mode='mistake'` 渲染错题语义 nav items（全部错题）而非知识库 nav items（全部内容/收件箱/笔记/博客/错题）
- **输出**: 侧栏仅显示错题相关筛选项，移动端标题显示"错题库"
- **失败处理**: `mode` prop 缺失时回退默认 `'knowledge'` 行为

### FR2: 唯一新增错题入口

- **输入**: 用户通过导航进入 `/write-note` 或 `/write-mistake`
- **处理**: `/write-note` 只提供「笔记」「博客」tab，不渲染错题表单。`/write-mistake` 是唯一新增错题页面
- **边界**: 已有错题的编辑暂继续复用 `/write-note/[slug]`（不在本轮范围）
- **输出**: 用户不会从两个页面创建同类型内容
- **失败处理**: 无

### FR3: 写作页返回按钮

- **输入**: 用户在 `/write-note` 或 `/write-mistake` 页面
- **处理**: 页面顶部显示 ArrowLeft 返回按钮 + 标题，底部"取消"按钮改为固定 Link（非 router.back）
- **输出**: `/write-note` → 返回 `/notes`，`/write-mistake` → 返回 `/mistakes`
- **失败处理**: Link 为静态路径，不涉及运行时失败

### FR4: 管理页 tab URL query

- **输入**: 用户点击 `/manage` 页面 tab 或直接访问 `/manage?tab=music`
- **处理**: `useSearchParams` 读取 `?tab=` 确定当前 tab，tab 切换时 `router.push('/manage?tab=xxx')` 更新 URL
- **输出**: 浏览器前进/后退可切换 tab，非法 tab 值回退到 `content`
- **失败处理**: 非法 tab 值 → 默认 `content`；Suspense fallback 处理加载态

### FR5: nav-card.tsx 写作页 mini 主栏优化（用户确认 B 方案）

- **输入**: 写作页 (`/write*`) 路由渲染时
- **背景**: 用户反馈纯头像语义不清、点击像没反应；早前曾被误操作改为"头像 + Home 图标 + 首页文字"
- **方案**: 用户确认采用 B 方案（头像 + Home 图标 + 首页文字），代码见 `nav-card.tsx:150-158`，无需变更
- **输出**: mini 主栏显示头像 + Home 图标 + "首页"文字，`aria-label='返回首页'`
- **失败处理**: 无（静态 UI 变更）

## 4. 非功能需求

| 类型 | 要求 |
|------|------|
| 兼容性 | 不影响 `/notes`、`/write`(旧)、`/bloggers`、`/share` 等现有路由 |
| 类型安全 | `tsc --noEmit` 零错误 |
| 构建 | `npm run build` 成功 |
| 性能 | 无额外数据请求，纯 UI 路由变更 |

## 5. 边界说明

**不在此轮范围**:
- 编辑已有内容时的返回行为（需要按路由细分，后续处理）
- `/notes` 是否允许筛选 `type=mistake`（保持现状）
- AI 配置中心（P2）
- 错误答案联合分析（P3）
- 全局导航 VerticalNav 高亮逻辑修改（当前 pathname.startsWith 已满足要求）

## 6. 验收标准

| 编号 | 验收项 | 验证方式 |
|------|--------|----------|
| AC1 | `/mistakes` 侧栏不显示"全部内容""收件箱""笔记""博客" | 手动访问 `/mistakes` |
| AC2 | `/write-note` 只有「笔记」「博客」两个 tab | 手动访问 `/write-note` |
| AC3 | `/write-mistake` 为唯一新增错题入口 | 手动访问 `/write-mistake` |
| AC4 | `/write-note` 顶部有返回按钮，点击跳转 `/notes` | 手动点击 |
| AC5 | `/write-mistake` 顶部有返回按钮，点击跳转 `/mistakes` | 手动点击 |
| AC6 | `/manage` tab 切换时 URL 变更为 `?tab=xxx` | 手动点击 tab，检查 URL |
| AC7 | `/manage` 浏览器后退可恢复上一个 tab | 手动点击两个 tab 后按 back |
| AC8 | 写作页 mini 主栏采用 B 方案（头像 + Home 图标 + 首页） | 手动访问 `/write-note` |
| AC9 | `tsc --noEmit` 零错误 | 命令行执行 |
| AC10 | `npm run build` 成功 | 命令行执行 |
