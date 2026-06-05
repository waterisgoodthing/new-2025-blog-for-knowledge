# Tasks: AI 错题导航升级 — P1 UI 与路由体验实现

**版本**: v1.1  
**日期**: 2026-06-05  
**状态**: 全部完成（含 T3-6 用户确认 B 方案）  
**来源**: [requirements.md](./requirements.md), [design.md](./design.md)

---

## Phase 2: KnowledgeSidebar 错题专属模式

- [x] **T2-1**: 为 `KnowledgeSidebar` 添加 `mode` prop（类型 `'knowledge' | 'mistake'`，默认 `'knowledge'`）
  - 文件: `src/app/notes/components/knowledge-sidebar.tsx`
  - 完成标准: Props 类型定义含 `mode?`，解构 `mode = 'knowledge'`

- [x] **T2-2**: `mode='mistake'` 时 navItems 显示错题语义（`全部错题`），替换知识库 navItems
  - 文件: `src/app/notes/components/knowledge-sidebar.tsx`
  - 完成标准: `mode='mistake'` 时侧栏不出现"全部内容""收件箱""笔记""博客"

- [x] **T2-3**: `mode='mistake'` 时移动端侧栏标题显示"错题库"
  - 文件: `src/app/notes/components/knowledge-sidebar.tsx`
  - 完成标准: 移动端打开侧栏时标题为"错题库"

- [x] **T2-4**: `/mistakes/page.tsx` 传入 `mode='mistake'`，默认 `activeFilter` 改为 `'all'`
  - 文件: `src/app/mistakes/page.tsx`
  - 完成标准: 侧栏高亮"全部错题"，数据查询不受影响

---

## Phase 3: /write-note 移除错题类型 + nav-card.tsx B 方案确认

- [x] **T3-1**: `/write-note` 删除 `'mistake'` tab，`form.type` 改为 `'note' | 'blog'`
  - 文件: `src/app/write-note/page.tsx`
  - 完成标准: Tab 栏只有「笔记」「博客」两个按钮

- [x] **T3-2**: 移除错题专属表单字段和对应 state
  - 文件: `src/app/write-note/page.tsx`
  - 涉及: question, my_answer, correct_answer, analysis, knowledge_points, subject, difficulty, uploadedImages, uploading, subjects
  - 完成标准: form state 不含错题字段，tsc 无类型错误

- [x] **T3-3**: 移除错题专属 handlers（handleImageUpload, handleDragOver, handleDrop, uploadFiles）和 getPreviewContent
  - 文件: `src/app/write-note/page.tsx`
  - 完成标准: 无未使用函数/变量警告

- [x] **T3-4**: 简化 handleSave，移除错题条件分支
  - 文件: `src/app/write-note/page.tsx`
  - 完成标准: handleSave 直接使用 `form.content`，不组装错题 markdown

- [x] **T3-5**: 移除未使用导入（listSubjects, Subject）
  - 文件: `src/app/write-note/page.tsx`
  - 完成标准: import 列表仅含使用中的符号

- [x] **T3-6**: nav-card.tsx 采用 B 方案（头像+Home图标+首页）
  - 文件: `src/components/nav-card.tsx`
  - 决策: 用户确认采用 B 方案，当前代码 `nav-card.tsx:150-158` 已为 B 方案，无需变更
  - 完成标准: mini 主栏显示头像+Home图标+首页文字，`aria-label='返回首页'`

---

## Phase 4: 写作页返回按钮

- [x] **T4-1**: `/write-mistake` 顶部添加返回按钮，链接到 `/mistakes`
  - 文件: `src/app/write-mistake/page.tsx`
  - 涉及: 导入 ArrowLeft + Link，header 布局调整
  - 完成标准: 点击返回按钮跳转 `/mistakes`

- [x] **T4-2**: `/write-note` 顶部添加返回按钮，链接到 `/notes`
  - 文件: `src/app/write-note/page.tsx`
  - 涉及: 导入 ArrowLeft + Link，header 布局调整
  - 完成标准: 点击返回按钮跳转 `/notes`

- [x] **T4-3**: 两个写作页底部"取消"按钮改为固定 Link（替代 router.back()）
  - 文件: `src/app/write-mistake/page.tsx`, `src/app/write-note/page.tsx`
  - 完成标准: 取消按钮为 `<Link href='/mistakes'>` 或 `<Link href='/notes'>`

---

## Phase 5: /manage tab URL query

- [x] **T5-1**: 导入 `useRouter`, `useSearchParams`, `Suspense`
  - 文件: `src/app/manage/page.tsx`
  - 完成标准: 新导入无类型错误

- [x] **T5-2**: ManagePage 拆分为 Suspense 包装器 + ManagePageInner（使用 useSearchParams）
  - 文件: `src/app/manage/page.tsx`
  - 完成标准: `?tab=` 参数驱动 activeTab，非法值 fallback `content`

- [x] **T5-3**: tab 切换时 `router.push('/manage?tab=xxx')` 更新 URL
  - 文件: `src/app/manage/page.tsx`
  - 完成标准: 点击 tab 后 URL 变更，浏览器后退可恢复上一个 tab

---

## Phase 6: 验证

- [x] **T6-1**: `npx tsc --noEmit` 类型检查零错误
- [x] **T6-2**: `npm run build` 构建成功
- [x] **T6-3**: 手动逐页检查导航语义
  - `/mistakes` — 侧栏无知识库词汇
  - `/write-note` — 无错题 tab，返回按钮可用
  - `/write-mistake` — 返回按钮可用
  - `/manage` — tab URL query 生效
- [x] **T6-4**: 生成/更新 `validation.md`，记录逐项验证结果（不在 progress.md 里写验证）

---

## 执行前置项（实现前必须完成）

- [x] **PRE-1**: 确认 `progress.md` 状态已修正为真实状态
- [x] **PRE-2**: ☑️ 本 tasks.md 已获用户口头或书面审批

---

## 注意事项（实现时遵守）

- [x] **NOTE-1**: 删除 `/write-note` 错题字段时，确认 `uploadImage` import 仍保留 —— `useNoteEditor` 的 `onImageUpload` 回调依赖它进行普通笔记编辑器内图片粘贴，不可误删

---

## 关键决策

| 决策 | 结论 |
|------|------|
| Nav-card.tsx 处理 | B 方案：头像+Home图标+首页（用户确认） |
| /write-note 错题 tab | 直接删除 |
| /manage tab URL | router.push（用户选择） |
| 返回按钮 | 固定 Link，非 router.back |

---

> 所有 task 已完成，验证通过。
