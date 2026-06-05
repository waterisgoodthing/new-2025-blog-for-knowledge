# Design: AI 错题导航升级 — P1 UI 与路由体验实现

**版本**: v1.0  
**日期**: 2026-06-05  
**来源**: [requirements.md](./requirements.md), [findings.md](./findings.md), [ai-mistake-navigation-upgrade-plan.md](../../ai-mistake-navigation-upgrade-plan.md)

## 1. 总体架构

P1 为前端路由与 UI 体验修正，不涉及后端变更。所有修改限定在 React/Next.js 层。

## 2. 页面/组件设计

### 2.1 KnowledgeSidebar — mode prop

**文件**: `src/app/notes/components/knowledge-sidebar.tsx`

| 决策 | 说明 |
|------|------|
| 新增 `mode` prop 而非新建组件 | 避免重复逻辑，保持文件夹/标签排序/拖拽等能力复用 |
| `mode='knowledge'`（默认）| 保持现有行为：全部内容/收件箱/笔记/博客/错题 |
| `mode='mistake'` | navItems 替换为错题语义：`[{ id: 'all', label: '全部错题' }]` |
| 移动端标题 | `mode='mistake'` 时显示"错题库" |
| 文件夹/标签区段 | 保留，适用于错题场景 |

**navItems 设计**:
```
mode='knowledge': [全部内容, 收件箱, 笔记, 博客, 错题] (filter by contentTypes)
mode='mistake':   [全部错题]
```

当前 API (`useNoteIndex`) 不支持按复习状态（待复习/今日到期/已掌握）筛选，故仅保留"全部错题"一项。后续 API 支持后再扩展。

### 2.2 /write-note — 移除错题 tab

**文件**: `src/app/write-note/page.tsx`

| 变更项 | 变更前 | 变更后 |
|--------|--------|--------|
| `form.type` 联合类型 | `'note' \| 'blog' \| 'mistake'` | `'note' \| 'blog'` |
| Tab 选项 | 笔记 / 博客 / 错题 | 笔记 / 博客 |
| 错题表单字段 | question, my_answer, correct_answer, analysis, knowledge_points, subject, difficulty | 删除 |
| 错题图片上传 | handleImageUpload, handleDragOver, handleDrop, uploadFiles, uploadedImages, uploading | 删除 |
| 错题预览 | getPreviewContent() | 删除 |
| 保存逻辑 | 条件分支组装 content + 错题字段 | 仅保存 content |
| 未使用导入 | listSubjects, Subject | 删除 |

**保存逻辑简化**:
```ts
// 变更前: 条件组装错题 markdown content
const content = form.type === 'mistake' ? [...] : form.content

// 变更后: 直接使用 content
const created = await createNote({ slug, title, content: form.content, type: form.type, ... })
```

### 2.3 写作页返回按钮

**文件**: `src/app/write-mistake/page.tsx`, `src/app/write-note/page.tsx`

| 决策 | 说明 |
|------|------|
| 固定 Link 替代 router.back() | 可预期的导航目标 |
| 顶部 ArrowLeft + 标题布局 | flex-row，按钮 36x36 圆角卡片 |
| 底部"取消"按钮 | 同步改为固定 Link |

**组件结构**:
```tsx
<div className='mb-6 flex items-center gap-4'>
  <Link href='/mistakes' aria-label='返回错题集'>  // 或 /notes
    <ArrowLeft size={18} />
  </Link>
  <h1>标题</h1>
</div>
```

### 2.4 /manage — tab URL query

**文件**: `src/app/manage/page.tsx`

| 决策 | 说明 |
|------|------|
| `useSearchParams` 读取 `?tab=` | Next.js App Router 标准方式 |
| `router.push` 更新 URL | 用户选择 push，支持完整浏览器历史 |
| Suspense 包装 | Next.js 要求 useSearchParams 在 Suspense 边界内 |
| 默认 tab | `content`（fallback on 非法值） |
| TabType 校验 | `['content','music','recommendation','settings'].includes(tabParam)` |

**组件拆分**:
```tsx
export default function ManagePage() {
  return (
    <Suspense fallback={...}>
      <ManagePageInner />
    </Suspense>
  )
}

function ManagePageInner() {
  const searchParams = useSearchParams()
  const tab = searchParams.get('tab') || 'content'
  const setTab = (t) => router.push(`/manage?tab=${t}`)
  // ... existing state (auth, user, checking)
}
```

### 2.5 nav-card.tsx — 用户确认 B 方案

**文件**: `src/components/nav-card.tsx`

**背景**: 用户反馈纯头像语义不清、点击像没反应；当前确认采用"头像 + Home 图标 + 首页文字"的 B 方案。顶部返回按钮解决页面内返回路径，mini 主栏负责清晰表达"返回首页"。

**决策**: 用户确认采用 B 方案（头像 + Home 图标 + 首页文字），代码见 `nav-card.tsx:150-158`，无需变更。

## 3. 权限设计

无需权限变更。所有变更页面均为公开访问页面。

## 4. 异常处理设计

| 场景 | 处理方式 |
|------|----------|
| KnowledgeSidebar mode prop 缺失 | 默认 `'knowledge'` 行为 |
| /manage tab 参数非法 | 回退 `'content'` |
| /manage useSearchParams 未就绪 | Suspense fallback: "加载中..." |
| 返回按钮目标路由 | 静态路径 `/notes`、`/mistakes`，不涉及运行时错误 |

## 5. 不修改的文件

| 文件 | 原因 |
|------|------|
| `src/app/notes/page.tsx` | mode 默认 `'knowledge'`，行为不变 |
| `src/components/vertical-nav.tsx` | 当前 pathname.startsWith 高亮逻辑已满足需求 |
| `src/app/notes/[id]/` | 详情页不在此轮范围 |
| 后端任何文件 | P1 为纯前端变更 |
