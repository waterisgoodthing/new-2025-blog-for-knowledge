# UI Inventory — UI 资产全量清单

**证据等级**：L1（已验证）  
**审计日期**：2026-10-15  
**Git HEAD**：`700f345`

---

## 总览

| 资产类型 | 数量 | 位置 | 状态 |
|----------|------|------|------|
| **页面（Routes）** | 53 | `src/app/` | ✅ 已盘点 |
| **组件** | 约 120+ | `src/components/` | ✅ 已盘点 |
| **UI V2 组件** | 15 | `src/components/ui-v2/` | ⚠️ 零接入 |
| **样式文件** | 4 | `src/styles/` + `src/components/ui-v2/` | ✅ 已盘点 |
| **API 客户端** | 20+ | `src/lib/api/` | ✅ 已盘点 |
| **SVG 图标** | 若干 | `src/svgs/` | ✅ 已识别 |

---

## 1. 页面清单（53 页）

**验证方法**：
```bash
find src/app -name "page.tsx" | wc -l
# 结果：53
```

### 按域分类

#### 公开内容页面（Public Content）

| 路由 | 文件 | 说明 |
|------|------|------|
| `/` | `src/app/(home)/page.tsx` | 首页 |
| `/blog` | `src/app/blog/page.tsx` | 博客列表 |
| `/blog/[slug]` | `src/app/blog/[slug]/page.tsx` | 博客详情 |
| `/notes` | `src/app/notes/page.tsx` | 笔记列表 |
| `/notes/[id]` | `src/app/notes/[id]/page.tsx` | 笔记详情 |
| `/mistakes` | `src/app/mistakes/page.tsx` | 错题列表 |
| `/mistakes/[id]` | `src/app/mistakes/[id]/page.tsx` | 错题详情 |

#### 互动页面（Interaction）

| 路由 | 文件 | 说明 |
|------|------|------|
| `/discover` | `src/app/discover/page.tsx` | 发现页 |
| `/guestbook` | `src/app/guestbook/page.tsx` | 留言板 |
| `/about` | `src/app/about/page.tsx` | 关于页 |

#### 管理页面（Admin）

| 路由 | 文件 | 说明 |
|------|------|------|
| `/manage` | `src/app/manage/page.tsx` | 管理面板（Tab 切换） |
| `/write` | `src/app/write/page.tsx` | 写作页 |
| `/dashboard` | `src/app/dashboard/page.tsx` | Dashboard（学习数据） |
| `/review` | `src/app/review/page.tsx` | Review（复习系统） |
| `/practice` | `src/app/practice/page.tsx` | Practice（练习） |

**完整清单**：见 `git ls-files 'src/app/**/page.tsx'`

---

## 2. 组件清单（约 120+）

### 2.1 UI V2 组件（15 个）

**位置**：`src/components/ui-v2/`  
**特征**：
- ✅ 完整 token 系统（`tokens.css`）
- ✅ TypeScript + 测试覆盖
- ❌ **路由接入率 = 0**（关键问题）

| 组件 | 文件 | 说明 | 测试 |
|------|------|------|------|
| **AppShell** | `AppShell.tsx` | 应用外壳（sidebar + main + mobile） | ✅ |
| **Badge** | `Badge.tsx` | 徽章（状态标签） | ✅ |
| **Button** | `Button.tsx` | 按钮 | ✅ |
| **Card** | `Card.tsx` | 卡片容器 | ✅ |
| **DomainBadges** | `DomainBadges.tsx` | 领域徽章组 | - |
| **ErrorState** | `ErrorState.tsx` | 错误状态 | ✅ |
| **PageHeader** | `PageHeader.tsx` | 页面头部 | - |
| **PageStateView** | `PageStateView.tsx` | 页面状态（loading/error/empty） | - |
| **Progress** | `Progress.tsx` | 进度条 | - |
| **SectionHeader** | `SectionHeader.tsx` | 区块标题 | - |
| **Skeleton** | `Skeleton.tsx` | 骨架屏 | - |
| **navigation.ts** | `navigation.ts` | Navigation 工具函数 | - |
| **index.ts** | `index.ts` | 导出入口 | - |
| **tokens.css** | `tokens.css` | Token 系统 | - |

**测试文件**：
- `AppShell.test.tsx`
- `components.test.tsx`

---

### 2.2 Legacy 组件（约 100+）

**位置**：`src/components/`（根目录）

#### Overlay 组件（关键）

| 组件 | 文件 | 说明 | 问题 |
|------|------|------|------|
| **Modal** | `dialog-modal.tsx` | 对话框模态 | 独立实现，无统一焦点管理 |
| **Drawer** | `drawer.tsx` | 抽屉 | 独立实现 |
| **ContextMenu** | `context-menu.tsx` | 右键菜单 | 独立实现，无 ARIA |

#### Navigation 组件

| 组件 | 文件 | 说明 | 问题 |
|------|------|------|------|
| **VerticalNav** | `vertical-nav.tsx` | 垂直导航（Desktop） | 不符合设计目标（应为 glass topbar） |
| **MobileNav** | `mobile-nav.tsx` | 底部导航（Mobile） | - |
| **NavCard** | `nav-card.tsx` | 导航卡片（首页） | - |

#### 表单组件

| 组件 | 文件 | 说明 |
|------|------|------|
| **Input** | `input.tsx` | 输入框 |
| **Textarea** | `textarea.tsx` | 多行输入 |
| **Button** | `button.tsx` | 按钮（Legacy 版本，与 UI V2 重复） |

#### 内容组件

| 组件 | 文件 | 说明 |
|------|------|------|
| **ArticleContent** | `article-content.tsx` | 文章渲染 |
| **MarkdownRenderer** | `markdown-renderer.tsx` | Markdown 渲染 |
| **CodeBlock** | `code-block.tsx` | 代码块 |
| **ChartBlock** | `chart-block.tsx` | 图表 |
| **MarkMapBlock** | `markmap-block.tsx` | 思维导图 |
| **DiagramViewer** | `diagram-viewer.tsx` | 图示查看器 |

#### 功能组件

| 组件 | 文件 | 说明 |
|------|------|------|
| **MusicCard** | `music-card.tsx` | 音乐播放器 |
| **ScrollTopButton** | `scroll-top-button.tsx` | 返回顶部 |
| **SiteSettingsLoader** | `site-settings-loader.tsx` | 站点配置加载器 |
| **AuthGate** | `auth-gate.tsx` | 鉴权门控 |

**完整清单**：`ls -1 src/components/*.tsx`（约 100+ 文件）

---

## 3. 样式文件清单（4 个）

**验证方法**：
```bash
find src -name "*.css" | grep -v node_modules
```

| 文件 | 位置 | 说明 | Token 数量 |
|------|------|------|------------|
| **globals.css** | `src/styles/globals.css` | 全局样式入口 | - |
| **theme.css** | `src/styles/theme.css` | Tailwind token 定义 | 10 个 |
| **article.css** | `src/styles/article.css` | 文章排版样式 | - |
| **tokens.css** | `src/components/ui-v2/tokens.css` | UI V2 token 系统 | 约 40+ |

**依赖关系**：
```css
/* globals.css */
@import 'tailwindcss';
@import 'katex/dist/katex.min.css';
@import './theme.css';
@import './article.css';
@import '../components/ui-v2/tokens.css';
```

---

## 4. API 客户端清单（20+）

**位置**：`src/lib/api/`

| 客户端 | 文件 | 说明 |
|--------|------|------|
| **governance** | `governance.ts` | 治理 API |
| **meta** | `meta.ts` | 元数据 |
| **knowledge** | `knowledge.ts` | 知识点 |
| **admin-profile** | `admin-profile.ts` | 管理员配置 |
| **folders** | `folders.ts` | 文件夹 |
| **search** | `search.ts` | 搜索 |
| **images** | `images.ts` | 图片 |
| **drafts** | `drafts.ts` | 草稿 |
| **attempts** | `attempts.ts` | 练习记录 |
| **taxonomy** | `taxonomy.ts` | 分类法 |
| **captures** | `captures.ts` | 快照 |
| **content** | `content.ts` | 内容 |
| **dashboard** | `dashboard.ts` | Dashboard 数据 |
| **music** | `music.ts` | 音乐 |
| **attachments** | `attachments.ts` | 附件 |
| **music-manage** | `music-manage.ts` | 音乐管理 |
| **review** | `review.ts` | 复习 |
| **notes** | `notes.ts` | 笔记 |
| **guest-messages** | `guest-messages.ts` | 留言 |
| **practice** | `practice.ts` | 练习 |

**完整清单**：`ls -1 src/lib/api/*.ts`

---

## 5. SVG 图标清单

**位置**：`src/svgs/`

包括：
- `scroll-outline.svg` / `scroll-filled.svg`（博客图标）
- `projects-outline.svg` / `projects-filled.svg`（项目图标）
- `about-outline.svg` / `about-filled.svg`（关于图标）
- 其他自定义图标

**外部图标库**：
- `lucide-react`（主要使用）

---

## 6. 组件使用热力图（Top 10）

**[需验证 L3]** — 需运行时统计

预期高频组件（基于代码扫描推断）：
1. `Button` (Legacy)
2. `Card` (Legacy)
3. `Input`
4. `Drawer`
5. `Modal`
6. `VerticalNav`
7. `MobileNav`
8. `ArticleContent`
9. `MarkdownRenderer`
10. `CodeBlock`

---

## 7. 重复实现识别

### 高风险重复

| 功能 | 实现 1 | 实现 2 | 问题 |
|------|--------|--------|------|
| **Button** | `src/components/button.tsx` | `src/components/ui-v2/Button.tsx` | 两套按钮，维护成本高 |
| **Card** | `src/components/card.tsx` | `src/components/ui-v2/Card.tsx` | 样式不一致 |

### 中风险重复

| 功能 | 实现数量 | 说明 |
|------|----------|------|
| **Overlay** | 3（Modal/Drawer/ContextMenu） | 无统一系统 |
| **Loading State** | 多处独立实现 | 应统一为 Skeleton 或 Spinner |

---

## 8. 依赖关系图（简化版）

```
page.tsx (53 个)
    ├── Legacy Components (100+)
    │   ├── VerticalNav
    │   ├── MobileNav
    │   ├── Drawer
    │   ├── Modal
    │   └── ...
    ├── API Clients (20+)
    │   ├── dashboard.ts
    │   ├── review.ts
    │   └── ...
    └── Styles
        ├── theme.css (Tailwind tokens)
        ├── globals.css
        └── [未使用] ui-v2/tokens.css
```

**关键发现**：
- ❌ UI V2 组件与页面**零连接**
- ⚠️ Token 系统分裂（theme.css vs ui-v2/tokens.css）
- ⚠️ 组件职责重叠（Legacy Button vs UI V2 Button）

---

## 9. 下一步

1. **阅读** `token-systems.md`（3 套 Token 对比）
2. **阅读** `dependency-graph.md`（完整依赖关系）
3. **阅读** `technical-debt.md`（技术债务清单）

---

**更新日志**：
- 2026-10-15：初始版本（基于 HEAD 700f345）
