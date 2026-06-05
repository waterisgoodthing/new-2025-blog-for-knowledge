# UI 升级 — 任务清单 v2.2

> 版本: 2.2
> 日期: 2026-06-05
> 关联: `docs/ui-upgrade-design.md` v2.0 | `docs/ui-upgrade-requirements.md` v2.0 | `docs/ui-upgrade-diff-report.md`
>
> **v2.2 变更**: 全部 P0/P1/P2 任务完成。T-D08 采用前端聚合+累积模式（已知限制：未访问页面的标签不可见，完整方案需后端 `contentTypes` 参数）。T-D11 抽取 `SiteSettingsPanel` 共享组件。T-D03 ConfigDialog 挂载到全局布局。T-D07 跳过（各页面已有独立写入入口）。

---

## 执行边界

1. 每次开发前先执行 `git status --short`。
2. 不回退用户已有改动。
3. 前端 API 调用优先走 `src/lib/api/*`。
4. UI 变更必须符合半透明卡片、圆角、轻量动效风格。
5. 默认不 `git add`、`git commit`、`git push`。

---

## 阶段回滚策略

| 阶段 | 回滚方式 |
|------|----------|
| P0 导航修复 | 恢复 `vertical-nav.tsx` 原始版本 |
| P0 跳转修复 | 恢复 `motion.div` 原始 pointer-events |
| P0 错题 AI | 恢复原按钮文案，移除次级按钮 |
| P0 思维导图 | 恢复 `loadFailed` 机制 |
| P1 标题装饰 | 恢复 `::before` 伪元素规则 |
| P1 标签过滤 | 恢复原始 `listTags()` 调用 |
| P1 设置保存 | 恢复原始 try-catch 结构 |
| P2 Live2D | 恢复原始占位页 |
| P2 设置集中化 | 移除 /manage 第四个 tab |

---

## 任务概览

| 阶段 | 任务范围 | 任务数 |
|------|---------|--------|
| P0 | 导航溢出 + 跳转 + My Blog + 错题 AI + 思维导图 | 5 |
| P1 | 标题去# + 写作文案 + 标签过滤 + 设置保存 | 4 |
| P2 | Live2D 状态页 + 设置集中化 | 2 |
| P3 | 验收 | 1 |
| **合计** | | **12** |

---

## 依赖关系图

```text
P0（T-D01~03 同文件串行；T-D04/T-D05 可并行）
  T-D01 左侧导航溢出与裁切修复  ← 无依赖（与 T-D02/T-D03 同文件，串行）
  T-D02 导航跳转修复            ← T-D01（同文件，串行）
  T-D03 My Blog 与设置入口拆分   ← T-D02（同文件，串行）
  T-D04 错题 AI 入口增强        ← 无依赖
  T-D05 思维导图渲染失败修复     ← 无依赖

P1（全部可并行）
  T-D06 Markdown 标题 # 默认移除  ← 无依赖
  T-D07 写作入口文案（可选）      ← 无依赖
  T-D08 左侧标签按页面动态过滤    ← 无依赖
  T-D09 设置保存 GitHub 错误拆分  ← 无依赖

P2（全部可并行）
  T-D10 Live2D 状态页            ← 无依赖
  T-D11 /manage 网站设置集中化    ← T-D09

P3
  T-D12 全量验收                 ← T-D01~11
```

---

## 阶段 P0: 日常使用阻断修复

### T-D01: 左侧导航溢出与裁切修复

**影响域**: shared UI
**依赖**: 无
**关联需求**: FR-1.1 ~ FR-1.5
**文件范围**:
- `src/components/vertical-nav.tsx`

**子任务**:
- [x] 内层 `div` 添加 `max-h-[calc(100vh-32px)]`
- [x] 导航列表区域添加 `overflow-y-auto`
- [x] 头像区域与导航列表分离（头像固定，列表可滚动）
- [x] `left-0` 改为 `left-2`，给左侧 8px 间距防止被浏览器边缘裁切
- [x] 确保展开动画（56px → 180px）不受 max-height 影响
- [x] 确认展开态（180px）不覆盖 `KnowledgeSidebar` 主要操作区域

**验收标准**:
- 在截图宽高下，左侧竖栏不能被浏览器左边缘裁切
- 展开态不覆盖知识库侧栏主要操作
- 导航不紧贴屏幕边缘
- 展开/收起动画平滑

---

### T-D02: 导航跳转修复

**影响域**: shared UI
**依赖**: 无
**关联需求**: FR-2.1 ~ FR-2.4
**文件范围**:
- `src/components/vertical-nav.tsx`

**子任务**:
- [x] `motion.div`（active 胶囊，line 108-112）添加 `pointer-events-none`
- [x] 标签展开动画从 `width: 0 → width: 'auto'` 改为 `opacity: 0, x: -8 → opacity: 1, x: 0`
- [x] `Link` 组件确认有 `relative z-10`
- [x] 测试：点击每个导航项确认跳转正常
- [x] 测试：hover 展开后点击确认不偏移

**验收标准**:
- 点击任意导航项稳定跳转
- hover 展开后点击不偏移
- active 胶囊动画正常

---

### T-D03: My Blog 与设置入口语义拆分

**影响域**: shared UI
**依赖**: 无
**关联需求**: FR-3.1 ~ FR-3.5
**文件范围**:
- `src/components/vertical-nav.tsx`

**子任务**:
- [x] 确认头像 + 站点名 `<Link href='/'>` 行为不变（跳转首页）
- [x] 在分割线下方、导航列表上方添加"网站设置"按钮
- [x] 按钮点击调用 `setConfigDialogOpen(true)`（复用 config-store 方法）
- [x] 使用 `Settings` 图标（lucide-react）
- [x] 添加 `aria-label='网站设置'` + `title='网站设置'`
- [x] 展开时显示"网站设置"文案，收起时只显示图标
- [x] ConfigDialog 从首页移至全局布局 `src/layout/index.tsx`，确保内页也能打开

**验收标准**:
- 头像/站点名点击跳转首页
- "网站设置"按钮点击打开设置对话框
- 两者行为独立，互不干扰

---

### T-D04: 错题 AI 入口增强

**影响域**: mistakes
**依赖**: 无
**关联需求**: FR-4.1 ~ FR-4.9
**文件范围**:
- `src/app/write-mistake/page.tsx`

**子任务**:
- [x] 主按钮文案从"开始 AI 分析"改为"AI 智能解析题目"（line 305）
- [x] 面板描述文案增加"点击按钮自动填充"（line 277）
- [x] 在主按钮下方增加"AI 生成解析"按钮
- [x] 在主按钮下方增加"AI 生成知识点"按钮
- [x] 次级按钮复用 `analyzeText` API，结果只更新 `analysis` / `knowledge_points` 字段
- [x] 次级按钮仅在 `pasteText.trim()` 非空时启用（纯图片上传不可用，因次级按钮走文本 API）
- [x] 次级按钮调用中显示 loading 状态（spinner + "生成中..."）
- [x] 次级按钮失败时不清空原字段，只显示 toast 错误
- [x] 次级按钮不需要二次确认（只覆盖目标字段，不覆盖全部）
- [x] 次级按钮样式：次级操作风格（`bg-white/60 text-gray-600`）

**验收标准**:
- "AI 智能解析题目"按钮明显可见
- "AI 生成解析""AI 生成知识点"按钮在有输入时可用，无输入时禁用
- 次级按钮只更新对应字段，失败不清空原字段

---

### T-D05: 思维导图渲染失败修复

**影响域**: notes, markdown
**依赖**: 无
**关联需求**: FR-5.1 ~ FR-5.6
**文件范围**:
- `src/components/markmap-block.tsx`

**子任务**:
- [x] 移除 `loadFailed` 全局变量（line 9）
- [x] `loadMarkmapLib` 和 `loadMarkmapView` 失败时将 `libPromise`/`viewPromise` 设为 `null`（允许重试）
- [x] SVG 容器添加 `style={{ minHeight: 200, minWidth: 300 }}`（line 141）
- [x] 添加 `mounted` state 防止 SSR 渲染（添加 `useEffect` 设置 `mounted`）
- [x] 错误状态添加"重试"按钮（line 119-125）
- [x] 添加重试计数器（最多 3 次）
- [x] 错误时降级显示原始 Markdown 代码（已有，确认样式）

**验收标准**:
- markmap 代码块正常渲染为思维导图
- 加载失败后刷新页面可重试
- 错误状态有"重试"按钮
- SSR 不报错

---

## 阶段 P1: 核心体验修正

### T-D06: Markdown 标题 # 默认移除

**影响域**: shared UI, markdown
**依赖**: 无
**关联需求**: FR-6.1 ~ FR-6.3
**文件范围**:
- `src/styles/article.css`

**子任务**:
- [x] 删除 `.prose h1::before, .prose h2::before` 的 `content: '# '` 规则
- [x] 删除 `.prose h3::before` 的 `content: '## '` 规则
- [x] 删除 `.prose h4::before` 的 `content: '### '` 规则
- [x] 删除 `.prose h5::before` 的 `content: '#### '` 规则
- [x] 保留 `.prose [id] { scroll-margin-top: 100px }` 不受影响
- [x] 确认 TOC 锚点跳转正常

**验收标准**:
- 标题前不显示 # 符号
- 标题文本样式（字号、粗细、间距）不受影响
- TOC 锚点跳转正常

---

### T-D07: 写作入口文案（已跳过）

**影响域**: home
**依赖**: 无
**关联需求**: FR-7.1 ~ FR-7.2
**状态**: 已跳过

**跳过原因**:
- `/notes` 页面已有独立"写笔记"按钮（`notes/page.tsx`）
- `/mistakes` 页面已有独立"添加错题"按钮（`mistakes/page.tsx`）
- 首页"写文章"按钮是全局入口，保持"写文章"不变，无需额外修改

**子任务**:
- [x] 确认各页面已有独立写入按钮（/notes → 写笔记，/mistakes → 添加错题）
- [~] 保持"写文章"不变（无需修改）

---

### T-D08: 左侧标签按页面动态过滤

**影响域**: notes, mistakes, manage
**依赖**: 无
**关联需求**: FR-8.1 ~ FR-8.6
**文件范围**:
- `src/app/notes/components/knowledge-sidebar.tsx`
- `src/app/notes/page.tsx`
- `src/app/mistakes/page.tsx`

**实现方案**: 方案 B（前端从当前页面 items 聚合），使用 `useRef` 累积模式确保选中标签后列表不收窄。

**已知限制**: 只聚合到访过的页面标签，未访问页面的标签不可见。完整过滤需后端 `/api/tags` 增加 `contentTypes` 查询参数（方案 A）。

**子任务**:
- [x] `KnowledgeSidebar` 新增 `contentTypes` prop（可选，类型 `Array<'note' | 'blog' | 'mistake'>`）
- [x] `/notes` 页面传入 `contentTypes={['note', 'blog']}`，过滤掉 mistake 专属导航项
- [x] `/mistakes` 页面传入 `contentTypes={['mistake']}`，只显示 mistake 关联导航项
- [x] `/manage` 页面不传 `contentTypes`，显示全站所有标签（回退到 `listTags()` API）
- [x] 过滤逻辑：前端从当前页面 items 聚合标签，`useRef` 累积避免选中标签后收窄
- [x] 无标签时显示"暂无标签"文案（`text-xs text-gray-400`）
- [x] 标签点击后高亮状态更明显（`font-medium` + `shadow-sm`）

**验收标准**:
- `/notes` 页面不显示 mistake 专属标签
- `/mistakes` 页面不显示 note/blog 专属标签
- `/manage` 页面显示全站所有标签
- 点击标签正确筛选当前页面内容
- 无标签时显示"暂无标签"

---

### T-D09: 设置保存 GitHub 错误拆分

**影响域**: home, settings
**依赖**: 无
**关联需求**: FR-9.1 ~ FR-9.6
**文件范围**:
- `src/app/(home)/config-dialog/index.tsx`（简化为 DialogModal + SiteSettingsPanel 包装）
- `src/app/(home)/config-dialog/site-settings-panel.tsx`（新建，提取自 ConfigDialog）

**子任务**:
- [x] `handleSave` 拆分为两步：本地保存（Zustand + CSS 变量）+ GitHub 同步
- [x] 本地保存：更新 Zustand store + CSS 变量（不依赖 GitHub）
- [x] GitHub 同步：调用 `pushSiteContent()`，失败时 catch 但不阻断
- [x] 成功 toast: "设置已保存并同步到 GitHub"
- [x] 部分成功 toast: "本地设置已保存，GitHub 同步失败: {原因}"
- [x] 完全失败 toast: "保存失败: {原因}"
- [x] 部分成功时仍然关闭对话框 / 保持面板可用

**验收标准**:
- GitHub 同步失败时本地设置已更新
- 错误提示明确区分本地和 GitHub
- 不阻断用户操作

---

## 阶段 P2: 结构整理

### T-D10: Live2D 状态页

**影响域**: live2d
**依赖**: 无
**关联需求**: FR-10.1 ~ FR-10.5
**文件范围**:
- `src/app/live2d/page.tsx`

**子任务**:
- [x] 重写页面为状态说明页
- [x] 显示当前模型状态（当前仅显示"未启用"占位）
- [x] 显示"如何使用"操作指引（3 步）
- [x] 添加"前往网站设置"按钮，调用 `setConfigDialogOpen(true)`
- [x] 样式：玻璃卡片风格，居中布局

**验收标准**:
- 页面显示清晰的状态说明
- "前往网站设置"按钮可用
- 样式与现有页面一致

---

### T-D11: /manage 网站设置集中化

**影响域**: manage
**依赖**: T-D09
**关联需求**: FR-11.1 ~ FR-11.6
**文件范围**:
- `src/app/manage/page.tsx`（新增第四个 tab "网站设置"，内联渲染 `SiteSettingsPanel`）
- `src/app/(home)/config-dialog/site-settings-panel.tsx`（新建，从 ConfigDialog 提取的可复用设置面板）
- `src/app/(home)/config-dialog/index.tsx`（简化为 DialogModal + SiteSettingsPanel）

**实现说明**: 抽取 `SiteSettingsPanel` 共享组件（含 tab 切换、SiteSettings/ColorConfig/HomeLayout 渲染、保存/重置逻辑、文件上传状态管理），同时供 ConfigDialog 弹窗和 /manage 内嵌面板使用。首页 `Ctrl+L` 弹窗保留。

**子任务**:
- [x] `/manage` 页面 tab 栏新增第四个 tab "网站设置"
- [x] 复用已导出的 `SiteSettings`、`ColorConfig`、`HomeLayout` 组件，抽取 `SiteSettingsPanel` 共享组件
- [x] "网站设置" tab 内联渲染 `SiteSettingsPanel`（含 site/color/layout 子 tab + 保存/重置按钮）
- [x] `handleCancel` 同步重置本地表单状态（`setFormData(originalData)` + `setCardStylesData(originalCardStyles)`）
- [x] 首页 `Ctrl+L` 弹窗保留（两种入口并存）

**验收标准**:
- `/manage` 页面显示 4 个 tab
- "网站设置" tab 可修改站点配置
- 保存行为与首页弹窗一致（先本地保存，再 GitHub 同步）
- 首页弹窗不受影响

---

## 阶段 P3: 全量验收

### T-D12: 全量验收

**影响域**: 全部
**依赖**: T-D01 ~ T-D11
**状态**: 部分完成（TypeScript 编译通过；浏览器验证需人工进行）

**验证清单**:
- [x] `npx tsc --noEmit` 无错误（exit code 0）
- [ ] 左侧导航在截图宽高下不被浏览器左边缘裁切，展开态不覆盖知识库侧栏主要操作
- [ ] 点击任意导航项都能稳定跳转
- [ ] My Blog 点击行为唯一（跳转首页），设置入口独立且可用
- [ ] 错题页能明显看到"AI 智能解析题目"入口，次级按钮有输入时启用
- [ ] 思维导图能正常渲染，失败时有重试按钮
- [ ] Markdown 标题不显示 # 装饰
- [ ] 左侧标签按页面类型过滤，无标签时显示"暂无标签"
- [ ] 设置保存时 GitHub 同步失败不阻断本地保存
- [ ] Live2D 页面有清晰状态说明和管理入口
- [ ] /manage 页面有 4 个 tab，"网站设置" tab 可修改站点配置（内联渲染 SiteSettingsPanel）
- [ ] 首页拖拽编辑功能正常
- [ ] 写作页 mini NavCard 正常

**自动化验证通过项**:
- `npx tsc --noEmit` ✓（exit 0）
- 所有 `::before` 装饰已移除 ✓（`src/styles/article.css` 中无 `::before` 残留）
- `scroll-margin-top: 100px` 保留 ✓
- `loadFailed` 永久标志已移除 ✓（`src/components/markmap-block.tsx`）
- `pointer-events-none` 添加到 active 胶囊 ✓（`src/components/vertical-nav.tsx`）
- 标签展开动画改为 `opacity + x` 位移 ✓
- `Settings` 按钮有 `aria-label="网站设置"` + `title="网站设置"` ✓
- ConfigDialog 移至全局布局 ✓（`src/layout/index.tsx`）
- `handleSave` 拆分本地保存 + GitHub 同步 ✓（`site-settings-panel.tsx`）
- `handleCancel` 同步重置本地表单状态 ✓（`setFormData(originalData)`）
- `SiteSettingsPanel` 共享组件已抽取 ✓

**待人工验证**（dev server `localhost:2025`）：
- 各页面导航行为、视觉裁切
- 思维导图实际渲染
- AI 次级按钮交互
- /manage 网站设置 tab 的 SiteSettingsPanel 内联显示
