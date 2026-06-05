# Task Plan: AI 错题导航升级 — P1 UI 与路由体验实现

## Goal
修正 `/mistakes` 错题页侧栏语义、`/write-note` 双入口问题、写作页返回按钮、全局导航高亮、`/manage` tab URL query，使日常使用导航体验一致且可预期。

## Current Phase
全部完成（含 T3-6 用户确认 B 方案、复审修正）

## Phases

### Phase 1: Requirements & Discovery
- [x] 读取原始计划文档 `docs/ai-mistake-navigation-upgrade-plan.md`
- [x] 读取 AGENTS.md 规则，确认触及域
- [x] 建立任务工作区 `docs/workflows/ai-mistake-navigation-upgrade/`
- [x] 读取所有待修改文件当前状态
- [x] 确认 `nav-card.tsx` 处理方案 → 用户确认 B 方案（头像+Home图标+首页），代码已满足
- [x] 确认 `/write-note` 错题 tab 处理方案 → 直接删除
- [x] 确认 `/manage` tab URL query 设计 → router.push
- **Status:** completed

### Phase 2: 实现 — KnowledgeSidebar 错题专属模式
- [x] 为 KnowledgeSidebar 添加 `mode` prop（`'knowledge'` | `'mistake'`）
- [x] `mode='mistake'` 时 navItems 使用错题语义（全部错题）
- [x] 移动端标题显示"错题库"
- [x] `/mistakes/page.tsx` 传入 `mode='mistake'`，`activeFilter` 默认 `'all'`
- [x] 确认 `/notes` 和 `/manage` 不受影响（默认 `mode='knowledge'`）
- **Status:** completed

### Phase 3: 实现 — /write-note 移除错题类型
- [x] `/write-note/page.tsx` 移除 `'mistake'` tab 选项
- [x] 简化 `form.type` 类型为 `'note' | 'blog'`
- [x] 移除错题专属表单字段（question, my_answer, correct_answer, analysis, knowledge_points, subject, difficulty）
- [x] 移除错题预览逻辑（getPreviewContent）
- [x] 移除错题保存逻辑（content 拼接 + 额外字段）
- [x] 移除未使用导入（listSubjects, Subject）
- [x] 保留 `uploadImage` import（useNoteEditor 的 onImageUpload 回调依赖）
- [x] nav-card.tsx 采用 B 方案（头像+Home图标+首页），用户确认，代码已满足
- **Status:** completed

### Phase 4: 实现 — 写作页返回按钮
- [x] `/write-mistake/page.tsx` 顶部添加返回按钮 → `/mistakes`
- [x] `/write-note/page.tsx` 顶部添加返回按钮 → `/notes`
- [x] 返回按钮替换 `router.back()` 的「取消」按钮为固定 Link
- [x] 编辑已有内容模式不在此轮处理
- **Status:** completed

### Phase 5: 实现 — /manage tab URL query
- [x] `/manage/page.tsx` 从 `useSearchParams` 读取 `?tab=`
- [x] tab 切换时用 `router.push` 更新 URL query
- [x] 浏览器前进/后退正确切换 tab
- [x] 默认 tab 为 `content`
- [x] 非法 tab 值回退到 `content`（含 useEffect fallback）
- **Status:** completed

### Phase 6: 验证
- [x] `npx tsc --noEmit` 类型检查通过
- [x] `npm run build` 构建成功
- [x] 逐页手动检查导航语义（代码审查确认）
- [x] `validation.md` 已生成
- **Status:** completed

### 复审修正 (2026-06-05 18:10)
- [x] manage/page.tsx useEffect fallback：非法 tab 值回退到 `'content'`
- [x] tasks.md T3-6 标注当前代码已为 B 方案
- [x] progress.md / task_plan.md 同步至最新状态

## Key Questions
1. `/write-note` 的"错题"tab 是直接删除还是点击跳转 `/write-mistake`？→ 直接删除 ✓
2. `nav-card.tsx` mini 主栏方案？→ 用户确认 B 方案（头像+Home图标+首页）✓
3. `/notes` 是否还允许筛选 `type=mistake` 内容？→ 保持现状

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| KnowledgeSidebar 用 `mode` prop 而非新建组件 | 避免重复，保持维护性；`mode='mistake'` 替换 navItems |
| /write-note 直接删除错题类型 | 计划文档推荐 `/write-mistake` 为唯一入口 |
| /manage tab 使用 `router.push` 非 `replace` | 用户选择，支持浏览器前进/后退完整历史 |
| /manage useEffect fallback 到 'content' | 复审修正：确保非法 tab 值和空 tab 值都回退 |
| nav-card.tsx 采用 B 方案 | 用户确认，头像+Home图标+首页提供清晰语义 |
| 返回按钮使用固定 Link 非 router.back | 更可预期的导航行为 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| manage useEffect 非法 tab 不回退 | 1 | 复审修正：fallback 到 'content' |

## Notes
- 触及域: `mistakes`, `notes`, `write-mistake`, `write-note`, `manage`, shared navigation
- 关键文件: `knowledge-sidebar.tsx`, `mistakes/page.tsx`, `write-note/page.tsx`, `write-mistake/page.tsx`, `manage/page.tsx`, `nav-card.tsx`
- T3-6 nav-card.tsx 用户确认 B 方案，代码已满足
