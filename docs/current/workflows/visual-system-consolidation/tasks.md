# Tasks

## Approval State

Status: `APPROVED FOR VSC-01 READ-ONLY BASELINE ONLY`

Approved in conversation on 2026-08-05 for read-only project-state inspection, content freeze, and current-versus-target difference analysis. This approval authorizes only VSC-01 evidence collection and workflow-document updates. It does not authorize tests that mutate fixtures, source implementation, CSS changes, dependency changes, route changes, or VSC-02 and later tasks.

After completing an individual approved item, update this file and mark that exact item complete before starting another item. Every later task requires separate approval.

## Dependencies

- Public administrator-state controls and public navigation cutover depend on the approved outcome of `public-session-state-optimization`; do not deepen anonymous `/api/auth/me` probing.
- Final public and administrator destination maps depend on the route ownership decision from `route-ownership-alignment`. Until resolved, preserve current routes and do not delete or redirect legacy routes.
- This task may add shared frontend presentation primitives and migrate approved consumers. It does not authorize backend contract, authentication, persistence, or deployment changes.

## Phase A - Evidence and Contract Freeze

### VSC-01 Current Consumer and Route Matrix

- [ ] 状态：执行中（仅只读基线）
- 任务名称：建立视觉、导航、Overlay 和右键消费者矩阵
- 优先级：P0
- 来源需求：VS-REQ-01 至 VS-REQ-06
- 涉及文件：本 workflow 文档、`src/layout/`、`src/components/`、`src/app/manage/`、公开内容路由
- 修改内容：盘点主题变量、层级、导航、面包屑、目录、Modal、Drawer、页面专用弹窗、Context Menu、加载态和空状态；记录每个消费者的公开/管理员职责
- 完成标准：所有当前消费者均有保留、迁移、延后或淘汰结论；不存在未分类的权限敏感入口
- 验证方式：源文件矩阵与路由交叉检查
- 风险说明：路由归属未决时保留当前链接，不提前切换

### VSC-02 Token and State Contract

- [ ] 状态：待执行
- 任务名称：冻结共享视觉 token、尺寸、层级和状态机
- 优先级：P0
- 来源需求：VS-REQ-01 至 VS-REQ-05
- 涉及文件：本 workflow 文档、现有主题变量和样式入口
- 修改内容：冻结 teal 品牌色职责、公开/管理表面、间距、边框、阴影、焦点、motion、z-index，以及顶部导航、Sidebar、Dropdown、Drawer 和锚点状态
- 完成标准：实现无需自行发明颜色、尺寸、关闭语义或层级；不引入整站米黄色改色
- 验证方式：设计、需求、技术规格和消费者矩阵交叉检查
- 风险说明：若 token 方案要求 Tailwind 重写或新 UI 框架，暂停并重新审批

## Phase B - Shared Overlay Foundation

### VSC-03 Overlay Accessibility Tests First

- [ ] 状态：待执行
- 任务名称：先建立 Modal、Drawer 和 Popover 行为测试
- 优先级：P0
- 来源需求：VS-REQ-05
- 涉及文件：`src/components/` 下目标测试
- 修改内容：覆盖 role/label、初始焦点、焦点约束、焦点恢复、Escape、遮罩、滚动锁定、背景隔离、减少动态效果和层级
- 完成标准：测试能在现有实现上暴露缺口，并在后续实现完成后稳定通过
- 验证方式：目标 Vitest
- 风险说明：不得通过删除可访问性断言来适配现有实现

### VSC-04 Harden DialogModal

- [ ] 状态：待执行
- 任务名称：加固共享 Modal 基础组件
- 优先级：P0
- 来源需求：VS-REQ-05
- 涉及文件：`src/components/dialog-modal.tsx`、相关测试和最小类型
- 修改内容：增加语义化 dialog、标题/描述绑定、焦点进入与恢复、需要时的焦点约束、稳定关闭策略、尺寸变体和 reduced-motion 行为
- 完成标准：现有 Modal 消费者保持可用；短表单、确认和沉浸预览均有明确变体
- 验证方式：VSC-03 测试、现有目标组件测试、TypeScript 检查
- 风险说明：不得在本项批量改造所有页面弹窗

### VSC-05 Harden Drawer and Add Anchored Popover

- [ ] 状态：待执行
- 任务名称：加固 Drawer 并建立锚定式 Popover
- 优先级：P0
- 来源需求：VS-REQ-05
- 涉及文件：`src/components/drawer.tsx`、新建或既有 Popover 所有者、相关测试
- 修改内容：统一左/右/底部方向、焦点与背景隔离、Header/Body/Footer、视口安全区、锚点定位、边缘翻转和关闭语义
- 完成标准：Drawer 与 Popover 职责不重叠；移动和桌面行为稳定；不新增大型依赖
- 验证方式：VSC-03 测试、定位测试、TypeScript 检查
- 风险说明：若原生定位无法满足且需要新增依赖，先记录体积与替代方案并重新审批

## Phase C - Context Actions Pilot

### VSC-06 ContextAction Tests and Shared Model

- [ ] 状态：待执行
- 任务名称：先建立统一 ContextAction 模型与交互测试
- 优先级：P0
- 来源需求：VS-REQ-06
- 涉及文件：`src/components/context-menu.tsx`、共享 action 类型/工具、Action Sheet、相关测试
- 修改内容：覆盖右键、更多按钮、`Shift+F10`、Menu key、方向键、Home/End、Enter、Escape、定位翻转、焦点恢复、禁用、危险分组和移动端 Action Sheet
- 完成标准：桌面 Context Menu 与移动 Action Sheet 消费同一 action 定义；右键不是唯一入口
- 验证方式：目标 Vitest 和键盘交互测试
- 风险说明：不得全局覆盖浏览器原生 contextmenu

### VSC-07 Pilot Notes and Knowledge Context Actions

- [ ] 状态：待执行
- 任务名称：迁移笔记列表与知识侧栏右键操作
- 优先级：P1
- 来源需求：VS-REQ-06
- 涉及文件：`src/app/notes/page.tsx`、`src/app/notes/components/knowledge-sidebar.tsx`、共享 ContextAction 组件和测试
- 修改内容：迁移打开、编辑、复制链接、移动、重命名、删除等现有动作；补充可见更多按钮和移动 Action Sheet
- 完成标准：文本、输入、链接、代码和页面空白保留原生右键；匿名用户不出现管理员动作
- 验证方式：目标测试、匿名/管理员浏览器检查、后端权限失败检查
- 风险说明：不能把 API 请求移动进共享展示组件

### VSC-08 Pilot Administrator List Context Actions

- [ ] 状态：待执行
- 任务名称：在管理员内容列表验证多选右键
- 优先级：P1
- 来源需求：VS-REQ-06
- 涉及文件：VSC-01 确认的管理员内容列表、共享 ContextAction 组件和测试
- 修改内容：实现选中项保持、非选中项替换选择、批量数量、不可批量动作禁用、批量删除确认和移动端入口
- 完成标准：单选、多选、危险确认、会话过期和后端拒绝均有明确结果
- 验证方式：组件测试、键盘测试和真实浏览器检查
- 风险说明：若列表所有权仍处于旧 `/manage` 与工作区之间的决策中，只选择一个明确稳定的试点

## Phase D - Administrator Navigation

### VSC-09 Collapsible Manage Sidebar

- [ ] 状态：待执行
- 任务名称：实现管理员 Sidebar 点击折叠
- 优先级：P1
- 来源需求：VS-REQ-03
- 涉及文件：`src/app/manage/components/manage-sidebar.tsx`、工作区 layout、相关测试
- 修改内容：实现 `232px/64px` 稳定宽度、折叠按钮、本地显示偏好、图标 tooltip、分组标题隐藏和非颜色 active 指示
- 完成标准：折叠不依赖 hover；路由与权限不变；内容区域不抖动或重叠
- 验证方式：组件测试、桌面断点浏览器检查、TypeScript 检查
- 风险说明：不得修改管理员路由归属

### VSC-10 Breadcrumb Foundation and Manage Coverage

- [ ] 状态：待执行
- 任务名称：建立面包屑组件并覆盖嵌套管理员页面
- 优先级：P1
- 来源需求：VS-REQ-04
- 涉及文件：共享 breadcrumb 组件、管理员 topbar/header、VSC-01 确认的详情与编辑页
- 修改内容：实现最多三级、当前项不可点击、长标题截断、移动端返回上级与当前标题
- 完成标准：顶级列表不机械显示面包屑；页面标题和导航层级不重复冲突
- 验证方式：目标测试、键盘和响应式浏览器检查
- 风险说明：动态标题加载失败时必须有稳定回退

## Phase E - Public Navigation Cutover

### VSC-11 Public Desktop Top Navigation

- [ ] 状态：待执行
- 任务名称：实现公开桌面 Floating/Sticky 顶部导航和 Dropdown
- 优先级：P1
- 来源需求：VS-REQ-02
- 前置条件：PSS 会话状态任务已完成；路由归属矩阵已冻结
- 涉及文件：共享 public header/dropdown、`src/layout/index.tsx`、`src/components/vertical-nav.tsx`、相关测试
- 修改内容：实现 top/scrolled/menu-open 状态、滚动迟滞、内容/探索分组、hover intent、点击/键盘操作和管理员入口
- 完成标准：公开内容保持可访问；匿名无管理员 API 噪音；切换后不与 `VerticalNav` 同时出现
- 验证方式：组件测试、匿名/管理员浏览器网络检查、响应式截图、性能观察
- 风险说明：PSS 未完成时本项 BLOCKED，不复制临时 auth 探测逻辑

### VSC-12 Public Mobile Topbar and Drawer

- [ ] 状态：待执行
- 任务名称：实现公开移动端 Sticky 顶栏、Hamburger 和 Drawer
- 优先级：P1
- 来源需求：VS-REQ-02
- 前置条件：VSC-11 导航模型稳定
- 涉及文件：共享 mobile header/drawer、`src/components/mobile-nav.tsx`、`src/layout/index.tsx`、相关测试
- 修改内容：实现安全区、分组导航、焦点约束、背景隔离、路由切换关闭和认证后管理员入口
- 完成标准：切换后不再同时显示旧底部导航；Drawer 与内容、Toast、滚动按钮不重叠
- 验证方式：组件测试、移动视口浏览器检查、触摸目标和键盘检查
- 风险说明：不得用长按或隐藏手势作为主导航入口

### VSC-13 Public Breadcrumb and Anchor Navigation

- [ ] 状态：待执行
- 任务名称：覆盖公开详情面包屑与滚动高亮目录
- 优先级：P1
- 来源需求：VS-REQ-04
- 涉及文件：博客/笔记详情、`src/components/blog-toc.tsx`、共享 breadcrumb 和移动目录 Drawer
- 修改内容：H2/H3 单一 active section、顶部偏移、hash replace、reduced motion、桌面 sticky 目录和移动底部目录
- 完成标准：滚动高亮稳定；锚点不被顶栏遮挡；历史记录不被滚动污染
- 验证方式：IntersectionObserver 测试、真实长文浏览器检查、移动/桌面截图
- 风险说明：Markdown heading id 不稳定时先修复 ID 合同，不用文本匹配临时绕过

## Phase F - Overlay Consumer Migration

### VSC-14 Migrate Approved Drawer Consumers

- [ ] 状态：待执行
- 任务名称：迁移长配置、筛选和辅助面板到 Drawer
- 优先级：P1
- 来源需求：VS-REQ-05
- 涉及文件：VSC-01 确认的消费者，优先首页配置与既有弱点诊断验证
- 修改内容：将长配置从 oversized Modal 调整为右 Drawer；校验弱点诊断等既有 Drawer 对新合同的兼容
- 完成标准：长内容具备固定 Header、滚动 Body 和按需 Footer；关闭不丢失未确认数据
- 验证方式：目标测试和桌面/移动浏览器检查
- 风险说明：每次只迁移一个消费者并立即更新本任务状态与验证记录

### VSC-15 Migrate Approved Modal and Popover Consumers

- [ ] 状态：待执行
- 任务名称：迁移短表单、确认、预览和快捷选择
- 优先级：P2
- 来源需求：VS-REQ-05
- 涉及文件：VSC-01 选定的 page-specific dialogs、Dropdown、账户/筛选菜单
- 修改内容：短表单使用标准 Modal，危险动作使用确认 Modal，沉浸预览使用 viewer 变体，快捷选择使用 Popover
- 完成标准：不存在本批次消费者自定义冲突的遮罩、层级、焦点和关闭语义
- 验证方式：逐消费者测试和浏览器检查
- 风险说明：不进行全仓机械替换；未验证消费者保留原实现

## Phase G - State Quality and Final Acceptance

### VSC-16 Loading and Empty State Alignment

- [ ] 状态：待执行
- 任务名称：统一本次触达页面的加载与空状态
- 优先级：P2
- 来源需求：VS-REQ-07
- 涉及文件：本次迁移触达的列表、导航和面板
- 修改内容：保持导航几何稳定、增加代表性内容 skeleton、为可操作空状态提供一个相关下一步
- 完成标准：无管理员控件闪现、无导航位移、无空白等待页、无卡片嵌套
- 验证方式：组件状态测试、慢网络浏览器检查和布局截图
- 风险说明：不扩展到未触达页面的全站视觉清扫

### VSC-17 Full Validation and Documentation Closure

- [ ] 状态：待执行
- 任务名称：执行完整视觉、交互、权限和构建验收
- 优先级：P0
- 来源需求：全部
- 涉及文件：`tasks.md`、`validation.md`、`assets/` 和所有实际修改文件
- 修改内容：完成桌面/平板/移动、匿名/管理员、键盘、右键、Action Sheet、reduced motion、滚动、层级、焦点、TypeScript、测试、构建和 bundle 对比
- 完成标准：所有通过、失败、阻断、回滚和残余风险均有证据；临时进程和测试数据已清理
- 验证方式：目标 Vitest、`npx tsc --noEmit`、`npm run build`、真实浏览器和工作树复核
- 风险说明：若存在未关闭的 P0/P1 可访问性、公开权限或导航重叠问题，不得标记 COMPLETE

## Stop Conditions

- A change requires route deletion, authentication weakening, backend contract changes, a new UI framework, or a broad CSS rewrite.
- Public reading would become gated or anonymous pages would request protected actions.
- A new navigation is added without an approved cutover and rollback plan for the existing navigation.
- Context actions would replace browser-native text, input, link, code, or image behavior without an explicit product reason.
- Public navigation work would proceed while `public-session-state-optimization` is incomplete.
- Implementation findings expand beyond the approved consumers or require unrelated route/editor/Markdown refactors.
