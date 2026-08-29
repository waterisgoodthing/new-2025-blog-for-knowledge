# 前端重构计划 - 2026-08-02

## 一、核心目标

### 1. 统一内容创建入口
**问题:** 错题有多个来源，写笔记和写错题操作无统一入口
**解决方案:** 建立统一的"创作中心"

```
旧设计（入口分散）:
- 首页 WriteButtons → /manage/dashboard
- 学习空间卡片 → /manage/dashboard、/manage/review 等
- 独立路由: /write、/write-note、/write-mistake

新设计（统一入口）:
首页 → 创作按钮 → 创作面板
                 ├─ 写文章 (blog)
                 ├─ 写笔记 (note)
                 ├─ 记错题 (mistake)
                 └─ 快速捕获 (quick capture)
```

### 2. 保留 UI 美感
**原有美感元素:**
- ✓ 卡片式磨砂玻璃效果 (`bg-card`, `backdrop-blur`)
- ✓ 圆角设计 (`rounded-[40px]`, squircle 支持)
- ✓ 柔和阴影 (`box-shadow`)
- ✓ 渐变色品牌系统 (`--color-brand`, `--color-brand-secondary`)
- ✓ 流畅的动画过渡 (motion/react)

**需要修复:**
- ⚠️ 学习空间卡片风格不统一 (圆角、阴影、色彩)
- ⚠️ 管理后台样式与主站脱节

### 3. 渐进式披露 (Progressive Disclosure)
**原则:** 默认简洁，按需展开

```
L1 (首页) → 核心导航 (博客/笔记/错题)
L2 (悬停) → 快速操作面板
L3 (点击) → 详细管理界面
```

### 4. 严格的功能入口控制
**权限分层:**
```typescript
// 公开访问 (游客可见)
- 首页、博客列表、笔记列表、错题列表、关于页

// 认证访问 (管理员可见)
- 创作面板 (统一入口)
- 管理后台 (/manage/*)
- 设置页面

// 路由守卫
- AuthGate 组件已存在 ✓
- 需要在路由级别强制执行
```

---

## 总任务分组（2026-08-09）

本方案后续工作收敛为两大类：

1. [前端技术基座与质量保障](./workflows/frontend-foundation-and-quality/README.md)：统一编排路由归属、Markdown 安全、编辑器能力、公开会话状态和生产渲染验收；
2. [视觉与交互系统统一](./workflows/visual-system-consolidation/README.md)：在技术基座稳定后推进视觉 Token、弹层、上下文操作和导航迁移。

第一大类采用阶段 Gate，不允许把五条技术线合并为一次不可审查的大修改。

---

## 二、重构阶段

### Phase 1: 统一创作入口 (优先级: 🔴 最高)

#### 1.1 创建统一的创作面板组件
**位置:** `src/components/creation-panel.tsx`

**设计:**
```tsx
<CreationPanel>
  <PanelTrigger /> {/* 替换现有 WriteButtons */}
  <PanelContent>
    <CreationOption type="blog" icon={Pen} label="写文章" />
    <CreationOption type="note" icon={BookOpen} label="写笔记" />
    <CreationOption type="mistake" icon={AlertCircle} label="记错题" />
    <CreationOption type="capture" icon={Zap} label="快速捕获" />
  </PanelContent>
</CreationPanel>
```

**交互模式:**
- 悬停触发器 → 面板展开
- 点击选项 → 导航到对应编辑器
- 保持原有磨砂玻璃 + 动画效果

#### 1.2 路由整合
```
保留路由 (向后兼容):
- /write → 重定向到创作面板
- /write-note → 重定向到创作面板
- /write-mistake → 重定向到创作面板

新路由 (统一规范):
- /manage/create?type=blog
- /manage/create?type=note
- /manage/create?type=mistake
- /manage/capture (快速捕获)
```

#### 1.3 废弃/重构的组件
- ❌ `write-buttons.tsx` → 替换为 `creation-panel-trigger.tsx`
- ❌ `learning-space-card.tsx` → 整合到侧边栏快捷操作
- ✓ 保留所有编辑器组件 (blog/note/mistake 编辑器)

---

### Phase 2: UI 一致性修复 (优先级: 🟡 高)

#### 2.1 设计系统标准化
**创建:** `src/styles/design-tokens.css`

```css
/* 统一的设计 Token */
:root {
  /* 圆角系统 */
  --radius-sm: 12px;
  --radius-md: 20px;
  --radius-lg: 40px;
  --radius-card: 40px; /* 主卡片圆角 */
  
  /* 阴影系统 */
  --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 12px 32px rgba(0, 0, 0, 0.08);
  --shadow-card: 0 40px 50px -32px rgba(0, 0, 0, 0.05);
  
  /* 磨砂玻璃 */
  --glass-bg: rgba(255, 255, 255, 0.6);
  --glass-border: rgba(255, 255, 255, 0.4);
  --glass-blur: blur(12px);
}
```

#### 2.2 组件标准化检查清单
- [ ] 所有卡片使用 `.card` utility
- [ ] 所有按钮使用 `.brand-btn` 或 `.btn-rounded`
- [ ] 统一动画时长 (0.2s ~ 0.35s)
- [ ] 统一交互反馈 (whileHover, whileTap)

#### 2.3 修复学习空间卡片
**文件:** `src/app/(home)/learning-space-card.tsx`

```diff
- className='rounded-[26px] border border-white/55 bg-white/54'
+ className='card' {/* 使用统一的 card utility */}

- className='rounded-2xl px-2.5 py-2'
+ className='btn-rounded px-2.5 py-2' {/* 统一圆角 */}
```

---

### Phase 3: 导航系统优化 (优先级: 🟢 中)

#### 3.1 侧边导航增强
**文件:** `src/components/vertical-nav.tsx`

**新增快捷操作区:**
```tsx
<nav>
  {/* 现有导航项 */}
  <NavGroup label="公开内容" items={publicContentItems} />
  <NavGroup label="互动探索" items={interactionItems} />
  
  {/* 新增：管理员快捷操作 */}
  {isAdmin && (
    <>
      <div className='mx-2 border-t border-white/30' />
      <QuickActions>
        <QuickAction icon={Plus} label="创建内容" onClick={openCreationPanel} />
        <QuickAction icon={Settings} label="管理后台" href="/manage/dashboard" />
      </QuickActions>
    </>
  )}
</nav>
```

#### 3.2 移动端导航整合
**文件:** `src/components/mobile-nav.tsx`

- 保持现有底部导航条
- "更多" 面板中增加创作入口 (仅管理员可见)

---

### Phase 4: 权限系统强化 (优先级: 🟢 中)

#### 4.1 路由级别守卫
**创建:** `src/middleware.ts`

```typescript
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // 保护管理路由
  if (pathname.startsWith('/manage')) {
    const token = request.cookies.get('auth-token')
    if (!token) {
      return NextResponse.redirect(new URL('/', request.url))
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/manage/:path*', '/write:path*']
}
```

#### 4.2 组件级别守卫
- ✓ 已有 `<AuthGate>` 组件
- 需要在所有管理页面顶层使用

---

## 三、实施步骤

### Week 1: 核心重构
- [ ] Day 1-2: 创建统一创作面板组件
- [ ] Day 3-4: 路由整合 + 废弃旧入口
- [ ] Day 5: 测试 + Bug 修复

### Week 2: UI 修复
- [ ] Day 1-2: 设计 Token 标准化
- [ ] Day 3-4: 组件样式审计 + 修复
- [ ] Day 5: 视觉 QA

### Week 3: 导航优化
- [ ] Day 1-2: 侧边导航增强
- [ ] Day 3-4: 移动端适配
- [ ] Day 5: 交互测试

### Week 4: 权限加固 + 收尾
- [ ] Day 1-2: 路由守卫实现
- [ ] Day 3: 全链路测试
- [ ] Day 4-5: 文档 + 部署

---

## 四、技术细节

### 4.1 保留的核心依赖
```json
{
  "next": "16.2.12",
  "react": "19.2.1",
  "motion": "^12.23.24",
  "tailwindcss": "^4",
  "zustand": "^5.0.8"
}
```

### 4.2 组件架构
```
src/
├─ components/
│  ├─ creation-panel/          # 新增：统一创作面板
│  │  ├─ index.tsx
│  │  ├─ trigger.tsx
│  │  └─ option.tsx
│  ├─ vertical-nav.tsx         # 增强
│  └─ mobile-nav.tsx           # 增强
├─ app/
│  ├─ (home)/
│  │  ├─ write-buttons.tsx     # 删除
│  │  └─ learning-space-card.tsx # 重构
│  └─ manage/
│     └─ create/               # 新增：统一创作路由
│        └─ page.tsx
└─ styles/
   ├─ globals.css
   └─ design-tokens.css        # 新增
```

### 4.3 状态管理
```typescript
// 新增：创作面板状态
import { create } from 'zustand'

type CreationType = 'blog' | 'note' | 'mistake' | 'capture'

interface CreationPanelStore {
  isOpen: boolean
  selectedType: CreationType | null
  open: (type?: CreationType) => void
  close: () => void
}

export const useCreationPanel = create<CreationPanelStore>((set) => ({
  isOpen: false,
  selectedType: null,
  open: (type) => set({ isOpen: true, selectedType: type }),
  close: () => set({ isOpen: false, selectedType: null })
}))
```

### 4.4 公开页面会话状态分层（2026-08-04 探测补充）

2026-08-03 的真实浏览器探测确认：匿名访问 `/notes` 时，页面会通过共享 `useAdminAuth` 调用严格身份接口 `GET /api/auth/me`。后端按设计返回 401，前端捕获后降级为非管理员，因此没有越权或公开内容中断，但会产生额外请求和认证失败日志。

技术方案采用两层会话合同：

1. 公开页面使用独立的“可选会话状态”接口，只返回最小布尔状态；匿名访问返回 200，不返回管理员资料；
2. `AuthGate`、`/manage` 和所有受保护操作继续使用严格 `GET /api/auth/me` 与后端权限依赖，401/403 语义保持不变；
3. 前端公共会话状态使用共享缓存，避免多个公开组件重复探测；
4. 任何写入、AI、上传或复习接口均不得依赖公开会话状态作为安全边界。

详细任务组：[public-session-state-optimization](./workflows/public-session-state-optimization/README.md)。

### 4.5 渲染就绪可观测性（2026-08-04 探测补充）

当前探测只能用 API `responseEnd` 加真实 DOM 空态断言作为内容就绪代理。后续在列表、详情和管理页定义稳定的 `loading / ready / empty / error` DOM 状态或 Performance Mark，使浏览器验收可以直接测量用户可见内容完成时间。

详细任务组：[production-render-readiness-acceptance](./workflows/production-render-readiness-acceptance/README.md)。

---

## 五、成功指标

### 用户体验
- ✅ 从首页到创作只需 2 次点击
- ✅ 所有创作功能统一在一个面板
- ✅ 移动端和桌面端体验一致

### 性能
- ⏳ 首页 LCP < 2.5s：原计划目标，尚缺当前生产构建证据。
- ⏳ 创作面板打开延迟 < 200ms：原计划目标，尚未验证。
- ⏳ 路由切换延迟 < 100ms：原计划目标，尚未验证。
- ✅ 本地空数据探测基线：匿名 `/notes` 内容就绪代理中位数 284.9ms、最大 362.8ms。
- ✅ 本地空数据探测基线：管理员提交登录至 `/manage` 内容就绪代理中位数 201.0ms、最大 334.5ms。

以上两项实测值仅代表浏览器无缓存、服务已启动、空隔离数据库和开发模式，不能作为生产 SLA。

### 维护性
- ✅ 设计 Token 统一管理
- ✅ 组件复用率 > 80%
- ✅ 代码规范统一

---

## 六、风险评估

### 高风险
- 🔴 路由重定向可能影响现有书签/分享链接
  - **缓解:** 保留旧路由并重定向

### 中风险
- 🟡 UI 改动可能影响用户习惯
  - **缓解:** 渐进式发布，保留旧入口 1 个月
- 🟡 当前渲染时效仅覆盖空数据开发环境，无法代表生产构建、真实内容量或移动网络
  - **缓解:** 独立执行生产渲染就绪验收任务，不以当前数值作为发布门槛

### 低风险
- 🟢 组件重构可能引入 Bug
  - **缓解:** 充分的单元测试 + E2E 测试
- 🟢 公开页面无条件探测严格管理员身份接口，匿名访问产生预期 401 噪音
  - **缓解:** 引入最小可选会话状态合同；严格身份和写入权限保持不变

---

## 七、后续优化方向

1. **内容管理中台化**
   - 统一的内容列表视图
   - 批量操作 (删除、移动、标签)

2. **AI 辅助创作**
   - 智能标签推荐
   - 错题相似度检测
   - 笔记大纲生成

3. **协作功能**
   - 评论系统
   - 分享预览

---

## 八、参考资源

### 设计参考
- Notion - 统一创作入口
- Obsidian - 快捷操作面板
- Linear - 渐进式披露

### 技术参考
- [Next.js App Router 最佳实践](https://nextjs.org/docs)
- [Motion 动画库文档](https://motion.dev/)
- [Radix UI Primitives](https://www.radix-ui.com/)
