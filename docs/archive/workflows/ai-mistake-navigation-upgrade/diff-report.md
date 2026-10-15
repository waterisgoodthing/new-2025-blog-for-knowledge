# Diff Report: AI 错题导航升级 — P1

**版本**: v1.0  
**日期**: 2026-06-05  

本文档描述 P1 实现将产生的文件变更预测，供审批前参考。实际实现可能因上下文微调。

---

## 受影响的文件

| # | 文件 | 变更类型 | 行数变化（估计） |
|---|------|----------|------------------|
| 1 | `src/app/notes/components/knowledge-sidebar.tsx` | 修改 | ~10 行新增 |
| 2 | `src/app/mistakes/page.tsx` | 修改 | ~2 行变更 |
| 3 | `src/app/write-note/page.tsx` | 修改 | ~-160 行净删除 |
| 4 | `src/app/write-mistake/page.tsx` | 修改 | ~15 行变更 |
| 5 | `src/app/manage/page.tsx` | 修改 | ~25 行变更 |
| 6 | `src/components/nav-card.tsx` | 修改 | ~10 行变更 |

**总计**: 6 文件修改，0 文件新增，0 文件删除

---

## 逐文件变更详述

### 1. knowledge-sidebar.tsx

```diff
// Props type: 新增
+ mode?: 'knowledge' | 'mistake'

// Destructuring: 新增默认值
+ mode = 'knowledge',

// navItems: 改为条件逻辑
- const navItems = [
-   { id: 'all', label: '全部内容', ... },
-   { id: 'inbox', label: '收件箱', ... },
-   ...
- ]
+ const navItems = mode === 'mistake'
+   ? [{ id: 'all', label: '全部错题', icon: <AlertCircle size={16} /> }]
+   : [ /* 原知识库 navItems */ ]

// 移动端标题: 动态
- <span className='text-sm font-medium'>知识库</span>
+ <span className='text-sm font-medium'>{mode === 'mistake' ? '错题库' : '知识库'}</span>
```

### 2. mistakes/page.tsx

```diff
// 默认 activeFilter
- const [activeFilter, setActiveFilter] = useState('mistake')
+ const [activeFilter, setActiveFilter] = useState('all')

// KnowledgeSidebar 调用
  <KnowledgeSidebar
    ...
    tags={pageTags}
+   mode='mistake'
  />
```

### 3. write-note/page.tsx

```diff
// Imports: 删除
- import { listSubjects, type Subject } from '@/lib/api/meta'

// Imports: 新增
+ import Link from 'next/link'
+ import { ArrowLeft } from 'lucide-react'

// State: 删除
- const [uploadedImages, setUploadedImages] = useState<string[]>([])
- const [uploading, setUploading] = useState(false)
- const [subjects, setSubjects] = useState<Subject[]>([])

// Handlers: 删除
- const handleImageUpload = async (...) => { ... }
- const handleDragOver = (...) => { ... }
- const handleDrop = async (...) => { ... }
- const uploadFiles = async (...) => { ... }

// useEffect: 简化
- listSubjects().then(setSubjects)...
+ (仅 listCategories)

// Form type: 缩窄
- type: 'note' as 'note' | 'blog' | 'mistake',
+ type: 'note' as 'note' | 'blog',

// Form fields: 删除
- subject: '', difficulty: 'medium' as ..., question: '', my_answer: '',
- correct_answer: '', analysis: '', knowledge_points: '',

// getPreviewContent: 删除整个函数

// handleSave: 简化
- const content = form.type === 'mistake' ? [...].filter(Boolean).join('\n\n') : form.content
- ... (subject, difficulty, question, my_answer 等条件字段)
+ content: form.content, (直接使用)

// Tab bar: 删除错题
- (['note', 'blog', 'mistake'] as const).map(
+ (['note', 'blog'] as const).map(
- {{ note: '笔记', blog: '博客', mistake: '错题' }[t]}
+ {{ note: '笔记', blog: '博客' }[t]}

// 错题表单区段: 删除整个 {form.type === 'mistake' ? ...} 块
// (约90行: 图片上传区 + 难度/科目选择 + 5个文本区)

// Header: 新增返回按钮
- <motion.h1 ...>写笔记</motion.h1>
+ <div className='mb-6 flex items-center gap-4'>
+   <Link href='/notes' ...><ArrowLeft size={18} /></Link>
+   <motion.h1 ...>写笔记</motion.h1>
+ </div>

// 取消按钮: 改为固定 Link
- <button onClick={() => router.back()} ...>取消</button>
+ <Link href='/notes' ...>取消</Link>
```

### 4. write-mistake/page.tsx

```diff
// Imports: 新增
+ import Link from 'next/link'
+ import { ArrowLeft } from 'lucide-react'

// Header: 新增返回按钮
- <motion.h1 ...>添加错题</motion.h1>
+ <div className='mb-6 flex items-center gap-4'>
+   <Link href='/mistakes' ...><ArrowLeft size={18} /></Link>
+   <motion.h1 ...>添加错题</motion.h1>
+ </div>

// 取消按钮: 改为固定 Link
- <button onClick={() => router.back()} ...>取消</button>
+ <Link href='/mistakes' ...>取消</Link>
```

### 5. manage/page.tsx

```diff
// Imports
+ import { Suspense } from 'react'
+ import { useRouter, useSearchParams } from 'next/navigation'

// 组件拆分
- export default function ManagePage() {
-   const [activeTab, setActiveTab] = useState<TabType>('content')
+ export default function ManagePage() {
+   return (
+     <Suspense fallback={...}>
+       <ManagePageInner />
+     </Suspense>
+   )
+ }
+
+ function ManagePageInner() {
+   const router = useRouter()
+   const searchParams = useSearchParams()
+   const tab = searchParams.get('tab') || 'content'
+   const activeTab = validTabs.includes(tab) ? tab : 'content'
+   const setActiveTab = (t: TabType) => router.push(`/manage?tab=${t}`)
```

### 6. nav-card.tsx — 用户确认 B 方案，无代码变更

> T3-6 用户确认采用 B 方案（头像 + Home 图标 + 首页文字）。当前代码 `nav-card.tsx:150-158` 已为 B 方案，无需变更。

---

## 不变的文件

| 文件 | 说明 |
|------|------|
| `src/app/notes/page.tsx` | mode 默认 `'knowledge'`，无需修改 |
| `src/components/vertical-nav.tsx` | 无需修改 |
| 后端任何文件 | P1 纯前端变更 |
| `src/app/(home)/*` | 不涉及 |
