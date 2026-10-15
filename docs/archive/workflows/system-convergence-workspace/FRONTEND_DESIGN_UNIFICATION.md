# 前端设计统一补充

## 当前状态评估 ⚠️

### 已有的设计定义 ✅

**设计方向**（DESIGN_RATIONALE_REVIEW）：
- "个人学习手稿的编辑感"
- 公开页 vs 工作台的差异化布局
- 八维质量标准定义

**UI V2 组件系统**（已批准但未挂载）：
- 16 个组件完成（U1-U16）
- Final Gate GRANTED（2026-09-20）
- 450/450 测试通过

**设计 Token**：
- `ui-v2/tokens.css` 定义了完整 token 系统
- 品牌色、间距、圆角、动效时长等

### 存在的严重问题 ❌

**1. 两套设计系统并存**
- Legacy: `theme.css` (旧系统)
- UI V2: `ui-v2/tokens.css` (新系统)
- 业务页面不知道用哪套
- 部分值冲突

**2. 组件未集成到业务路由**
- UI V2 组件独立存在
- 真实业务路由仍用旧组件
- Today 统一任务流未闭合

**3. 视觉验收未完成**
- 页面加载阻断（管理后台只显示"加载中"）
- 八维标准未实测
- 对比度、响应式、可访问性未验证

**4. 设计细节未闭合**
- ARIA 标签缺失（2 处）
- 对比度不足（3 处）
- reduced-motion 覆盖不完整
- 快捷键与浏览器保留键冲突

---

## 补充需求：前端设计统一

### REQ-DESIGN-001: 设计系统统一 [P1]

**目标**：从两套系统收敛到一套

**策略 A: 渐进迁移到 UI V2（推荐）**

```typescript
// Phase 1: 创建兼容层
// src/styles/design-tokens.css
:root {
  /* 统一命名空间，渐进替换 */
  --ds-brand: var(--uiv2-brand, #35bfab);
  --ds-text-primary: var(--uiv2-text-primary, #24312f);
  --ds-surface: var(--uiv2-surface, #ffffff);
  
  /* Legacy 别名（标记为废弃） */
  --color-brand: var(--ds-brand); /* @deprecated 使用 --ds-brand */
  --color-primary: var(--ds-text-primary); /* @deprecated */
}

// Phase 2: 业务页面逐步迁移
// 先迁移 Dashboard → Review → Notes
// 每个页面迁移后验证视觉一致性

// Phase 3: 删除 Legacy
// 确认无引用后删除 theme.css
```

**策略 B: 原地统一（风险较高）**
- 修改 theme.css 为新值
- 全局替换所有引用
- 一次性验证所有页面

**验收标准**：
- AC-DESIGN-001-1: 仅一套 CSS 变量系统
- AC-DESIGN-001-2: 所有业务页面使用统一 token
- AC-DESIGN-001-3: 视觉回归测试通过
- AC-DESIGN-001-4: 文档说明设计系统使用

---

### REQ-DESIGN-002: UI V2 组件集成 [P1]

**目标**：将 UI V2 组件挂载到真实业务路由

**优先级路由**（按重要性）：
1. **Dashboard** - 最高频入口
2. **Review Queue** - 核心学习流程
3. **Notes** - 内容管理
4. **Today** - 统一任务入口（B-001 阻断）
5. 其他管理页面

**实施步骤**：
```typescript
// 1. 评估当前页面与 UI V2 组件的差异
// 示例：Dashboard

// 当前 (旧组件)
import DashboardContent from '@/components/dashboard-content'

// 迁移后 (UI V2)
import { DashboardLayout } from '@/components/ui-v2/dashboard'
import { WeakTopThree } from '@/features/ui-v2/dashboard/weak-top-three'

// 2. 数据适配
import { dashboardAdapter } from '@/adapters/ui-v2/dashboard'

// 3. 渐进替换
// Week 1: Dashboard 主框架
// Week 2: Review Queue
// Week 3: Notes + Today
```

**验收标准**：
- AC-DESIGN-002-1: Dashboard 使用 UI V2 组件
- AC-DESIGN-002-2: Review Queue 使用 UI V2 组件
- AC-DESIGN-002-3: Notes 使用 UI V2 组件
- AC-DESIGN-002-4: 视觉一致性验证通过
- AC-DESIGN-002-5: 交互行为保持不变

---

### REQ-DESIGN-003: 八维视觉质量验证 [P1]

**目标**：验证并修复八维标准中的问题

**八维检查清单**（来自 DESIGN_RATIONALE_REVIEW）：

**1. 排版**
- [ ] 四级语义层次清晰
- [ ] 中文正文 16-18px, 1.65-1.85 行高
- [ ] 英文与公式基线对齐
- [ ] 长短标题、中英混排测试

**2. 留白**
- [ ] 嵌套容器 padding 一致
- [ ] 基于固定尺度（4/8/12/16/24/32px）
- [ ] 390/768/1440 节奏稳定

**3. 视觉层级**
- [ ] 主要动作突出
- [ ] 导航不重复争夺注意
- [ ] 错误状态显眼

**4. 色彩**
- [ ] 语义 token 统一
- [ ] 对比度 ≥4.5:1 (正文)
- [ ] 对比度 ≥3:1 (大文本)
- [ ] 状态不只靠颜色区分

**5. 动效**
- [ ] 状态变化有解释
- [ ] 反馈 120-180ms
- [ ] 面板 180-260ms
- [ ] reduced-motion 支持

**6. 微交互**
- [ ] 提交中禁用防重
- [ ] 失败保留输入
- [ ] 成功可感知
- [ ] 焦点有去处

**7. 响应式**
- [ ] 390px 可用
- [ ] 768px 可用
- [ ] 1440px 可用
- [ ] 软键盘不遮挡
- [ ] 触控目标 ≥44px

**8. 原创性**
- [ ] 学习手稿编辑感
- [ ] 个人品牌一致
- [ ] 不照搬获奖站

**已知问题**（需要修复）：
1. Dashboard weak KP 对比度 3.2:1 → 需要 ≥4.5:1
2. Review 评分按钮缺失 aria-label
3. reduced-motion 覆盖不完整

**验证方法**：
```bash
# 对比度测试
npx @axe-core/cli http://localhost:3000/manage/dashboard \
  --tags wcag2aa,color-contrast \
  --save evidence/design/contrast-report.json

# 响应式测试
npx playwright test --project mobile
npx playwright test --project tablet
npx playwright test --project desktop

# 可访问性测试
npm run test:a11y
```

**验收标准**：
- AC-DESIGN-003-1: 对比度全部达标（≥4.5:1 正文）
- AC-DESIGN-003-2: ARIA 标签完整
- AC-DESIGN-003-3: 响应式 3 断点通过
- AC-DESIGN-003-4: reduced-motion 全覆盖
- AC-DESIGN-003-5: 触控目标 ≥44px

---

### REQ-DESIGN-004: 页面加载问题修复 [P0]

**目标**：修复管理后台"加载中"阻断

**当前问题**（来自设计评估）：
> 主页曾仅有 main 空区域；`/manage` 多次观察仍为"加载中"；
> `/notes` 也只取得加载状态

**可能原因**：
1. 认证状态未正确初始化
2. API 请求失败但未显示错误
3. SWR 配置问题
4. 路由权限检查阻塞
5. 前端构建与服务端不一致

**调查步骤**：
```typescript
// 1. 检查认证流程
// src/hooks/use-admin-auth.ts
console.log('Auth status:', authStatus)
console.log('Is loading:', isLoading)

// 2. 检查 API 调用
// 浏览器 Network 面板
// 是否有 401/403/500 错误？
// 是否有请求超时？

// 3. 检查 AuthGate
// src/components/auth-gate.tsx
// 是否正确处理加载状态？

// 4. 检查 SWR 配置
// src/lib/api/client.ts
// revalidateOnFocus? dedupingInterval?
```

**修复验收标准**：
- AC-DESIGN-004-1: `/manage` 正常显示 Dashboard
- AC-DESIGN-004-2: `/manage/notes` 正常显示笔记列表
- AC-DESIGN-004-3: 加载失败时显示明确错误
- AC-DESIGN-004-4: 录屏证据（从登录到正常使用）

---

## 集成到工作空间

### Phase 3 增强（前端体验与交互）

**原 Phase 3 内容**：
- REQ-P3-001: Capture 状态隔离
- REQ-P3-002: Notes 分页
- REQ-P3-003: 三条关键流程
- REQ-P3-004: 八维视觉质量

**新增内容**：
- REQ-P3-005: 设计系统统一（REQ-DESIGN-001）
- REQ-P3-006: UI V2 组件集成（REQ-DESIGN-002）
- REQ-P3-007: 八维质量修复（REQ-DESIGN-003 增强）
- REQ-P3-000: 页面加载修复（REQ-DESIGN-004，前置到 Phase 3 开始）

**执行顺序**：
```
P3-000: 修复页面加载阻断（优先）
   ↓
P3-001-002: 交互修复（Capture、Notes）
   ↓
P3-005: 设计系统统一
   ↓
P3-006: UI V2 组件集成（渐进）
   ↓
P3-003: 三条流程验证
   ↓
P3-007: 八维质量验证
```

### Phase 5 增加前端独立验证

**前端独立验证增加检查项**：
```yaml
design_consistency:
  single_design_system: PASS/FAIL
  ui_v2_integration: PASS/FAIL
  eight_dimensions: PASS/FAIL
  page_loading: PASS/FAIL
  evidence:
    - evidence/p5-integration/design-consistency.json
    - evidence/p5-integration/screenshots/
```

---

## 设计迭代停止条件

来自 DESIGN_RATIONALE_REVIEW：

> "没有明显可提升之处"的操作定义：在上述页面、状态、尺寸和约束内，
> 无未解决的高/中影响缺陷；低影响项已处理或明确记录成本取舍；
> 关键流程、响应式与可访问性检查通过；独立复审无阻断。

**具体停止条件**：
- 所有 P0 设计问题修复
- 八维标准检查通过
- 对比度、响应式、可访问性达标
- 三条关键流程视觉一致
- 独立前端审查者 APPROVE

**不要求**：
- 视觉绝对最优
- 全站无任何改进空间
- 保证获奖

---

## 快速行动建议

### 选项 A: 先修复加载阻断（推荐）⭐

**紧急修复**（Phase 3 前置）：
1. 调查 `/manage` 加载阻断根因
2. 修复认证/API/路由问题
3. 验证页面正常显示
4. 录屏证据

**预计时间**: 2-4 小时  
**收益**: 解除视觉验证的前置阻断

### 选项 B: 设计系统统一优先

Phase 3 按原计划执行，但增加设计统一任务。

**预计时间**: Phase 3 延长 2-3 天  
**收益**: 建立统一的设计语言

### 选项 C: 延后到专门的视觉迭代轨

Phase 3 仅做交互修复，视觉统一作为独立项目。

**风险**: 视觉不一致持续存在

---

## 总结

**前端设计风格状态**: 🟡 **部分定义，未统一，未验证**

- ✅ 设计方向已定义
- ✅ UI V2 组件已完成（但未挂载）
- ❌ 两套设计系统并存（冲突）
- ❌ 页面加载阻断（无法验证视觉）
- ❌ 八维标准未实测
- ❌ 对比度、可访问性有缺陷

**建议优先级**: **P0（页面加载）+ P1（设计统一）**

**需要纳入工作空间**: ✅ 已补充到本文档

---

你希望我：
1. ✅ **立即调查页面加载阻断**（2-4小时，解除验证阻塞）
2. 📋 **纳入 Phase 3 系统性修复**
3. ⏰ **延后到专门的视觉迭代项目**
4. ❓ **先看更多细节再决定**
