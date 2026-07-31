# R1 管理工作区视觉基线

日期：2026-07-30
状态：`FROZEN FOR R1`

## 当前事实

管理工作区已经具备蓝白玻璃语言：

- route-group shell：`bg-white/48`、`backdrop-blur-xl`、白色半透明边框。
- 桌面侧栏和移动抽屉复用相同 `navGroups`，并有一致的品牌 focus ring。
- `ManagePanel` / `ManageFormPanel` 已定义 light/heavy 两种表面层级。
- `FeatureState` 已覆盖 loading、empty、error、deferred。
- Dashboard 已区分 ready、empty、unavailable、unknown。

因此 R1 不新增全局玻璃 CSS，也不修改 `src/styles/globals.css`。

## 需要收敛的最小问题

1. Dashboard 缺少清晰、真实的四个日常快捷行动。
2. Dashboard 多个 section 仍直接拼写相似的边框/文本/链接反馈。
3. 快捷行动需要一致的 focus、hover、reduced-motion 和语义色表达。
4. 不同领域入口必须明确是“跳转到真实流程”，而不是假操作按钮。

## R1 最小改动集

允许修改：

- `src/app/manage/(workspace)/dashboard/dashboard-overview.tsx`
- `src/app/manage/(workspace)/dashboard/dashboard-overview.test.tsx`
- `src/app/manage/components/` 下一个轻量 action link 组件及其测试（只有出现真实复用时）
- 直接指向 canonical workspace 的少量站内入口及相关测试（如盘点发现偏差）

不修改：

- `src/styles/globals.css`
- 公开博客、笔记、错题页面的视觉结构
- `src/app/workspace/page.tsx`
- 后端 API、schema、migration、数据库
- 三类编辑器内部实现

## 视觉约束

- Surface：延续 `border-slate-200/70`、`bg-white/55` 或语义色轻背景。
- Radius：Dashboard 操作使用现有 `rounded-2xl`；不引入新的全局 radius token。
- Motion：只用颜色/边框/阴影的轻量过渡，并提供 `motion-reduce:transition-none`。
- Focus：所有 action 使用 `focus-visible:ring-2` 和品牌色 ring。
- Hover：不使用默认上移 4px，不造成布局或视觉跳动。
- Icon：Lucide 图标标记 `aria-hidden`，链接文字提供 accessible name。

## 验收

- 四个快捷行动在桌面和移动端均可见且不溢出。
- 所有行动指向存在且权限正确的路由。
- 不出现 `/workspace/*` 链接。
- loading/error/empty/unknown 语义不退化。
- reduced-motion、键盘 focus 和三尺寸浏览器检查通过。
