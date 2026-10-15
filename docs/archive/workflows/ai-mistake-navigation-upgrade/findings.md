# Findings & Decisions

## Requirements
- /mistakes 侧栏改为错题专属语义（移除全部内容/收件箱/笔记/博客）
- /write-note 不再内部创建错题
- /write-mistake 保持唯一新增错题入口
- 写作页添加顶部返回按钮
- /manage tab 使用 URL query 参数
- 左侧全局导航已有 hover 展开（vertical-nav.tsx 已实现）

## Research Findings

### KnowledgeSidebar 当前状态
- `knowledge-sidebar.tsx:110-119`: navItems 包含 `全部内容/收件箱/笔记/博客/错题`
- 已有 `contentTypes` prop 用于过滤 type 项，但 `all`/`inbox` 无 type 字段仍显示
- `/mistakes/page.tsx:60-69` 已传入 `contentTypes={['mistake']}` 和 `tags={pageTags}`
- 当前 `/api/tags` 返回全量标签（不分类型），但 `/mistakes` 用 `pageTags`（from items）规避了此问题

### /write-note 错题能力
- `write-note/page.tsx:70,74`: `form.type` 类型包含 `'mistake'`
- `write-note/page.tsx:178-189`: tab 栏包含 `note/blog/mistake` 三个选项
- `write-note/page.tsx:223-314`: 当 `type==='mistake'` 时渲染完整错题表单
- `write-note/page.tsx:113-124,134-141`: 保存逻辑有专门的 `type==='mistake'` 分支
- AI 功能由 `write-note` 的 `AIAssistantPanel` 提供，与 `/write-mistake` 的 AI 分析面板不同

### 写作页返回按钮
- `write-mistake/page.tsx:511`: 底部「取消」按钮用 `router.back()`
- `write-note/page.tsx:438-442`: 底部「取消」按钮用 `router.back()`
- 无页面顶部返回按钮

### /manage tab 状态
- `manage/page.tsx:24-31`: tabs 定义为 `content/music/recommendation/settings`
- `manage/page.tsx:317`: 用 `useState<TabType>` 管理 activeTab，无 URL 同步
- 已有 `SiteSettingsPanel` 在 `settings` tab 下渲染（`manage/page.tsx:412-415`）

### vertical-nav 状态
- `vertical-nav.tsx:34-41`: activeIndex 通过 `pathname.startsWith(item.href)` 计算
- 已有 hover 展开 → 标签文字（`vertical-nav.tsx:43-44`）
- 已有「网站设置」独立入口（`vertical-nav.tsx:91-114`）
- 左侧已有 `left-2` margin + `max-h-[calc(100vh-32px)]` 防溢出

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| KnowledgeSidebar 添加 `mode` prop | 保持组件复用，避免新建 MistakesSidebar |
| /write-note 删除错题 tab（非跳转） | 更干净，消除维护负担 |
| 返回按钮用固定 Link（非 router.back） | 更可预期的导航行为 |
| /manage 用 router.replace 更新 query | 避免标签切换填满浏览器历史 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
- 原始计划: `docs/ai-mistake-navigation-upgrade-plan.md`
- 设计文档: `docs/ui-upgrade-design.md`
- AGENTS.md: 项目根目录
