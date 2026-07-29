# Manage UI Consolidation Tasks

## 0. 执行状态与批准门

- 设计：Approved v1.1，2026-07-12（包含可爱风文案修订）
- 需求：已编制并随设计批准
- 实施批准：用户已批准本任务清单并要求执行；首轮实施完成后经代码审查发现 5 项 P1 和 1 项 P2 问题，进入修复轮。
- 首轮实施：A-01~A-03、B-01、B-02、C1-01、C1-02、C2-01~C2-03、D1-01、D2-01、D3-01、E-01 已完成（15 项勾选）；E-02 浏览器验收未通过（存在焦点约束缺失、键盘不可达、错误状态误显等问题）；E-03 因 E-02 未通过而标记为未完成。
- 修复轮：R-01~R-06 已完成；最终验收中追加的 R-07~R-09 也已完成并复验。
- 最终状态：E-02 已通过真实浏览器验收；E-03 已完成文档与证据收口。

执行规则：

- 获批后按任务编号执行；每完成一个任务，立即勾选该项并记录验证，不得在最后批量回填。
- C1 与 C2、D1 与 D2/D3 分别独立验收；不得用一次大改动合并通过。
- 任何需要新 API、新字段、新权限、新路由契约或新产品能力的发现必须停止并重新审批。
- 修复轮不扩大 API、数据库或后端范围。

## A. 导航与开发痕迹清理

### [x] A-01 桌面分组导航与父路由激活

任务编号：A-01  
任务名称：桌面分组导航与显式父路由匹配  
优先级：P0  
来源需求：REQ-NAV-001、REQ-NAV-002  
涉及文件：`src/app/manage/components/manage-sidebar.tsx`  
修改内容：建立三组、9 项导航数据；隐藏 Jobs/Settings；为一级页和详情页配置显式匹配规则。  
完成标准：桌面侧栏顺序正确；详情页只激活正确父项；AI Runs 激活 AI。  
验证方式：TypeScript 检查；逐个一级/详情 pathname 浏览器检查；检查 `aria-current`。  
风险说明：避免用 `/manage`宽泛前缀造成多项同时激活。

### [x] A-02 移动端导航抽屉

任务编号：A-02  
任务名称：将移动端横向导航替换为分组抽屉  
优先级：P0  
来源需求：REQ-NAV-003、NFR-003、NFR-004  
涉及文件：`src/app/manage/components/manage-sidebar.tsx`、`src/app/manage/components/manage-topbar.tsx`、必要的 manage-scoped 抽屉组件  
修改内容：顶栏增加菜单按钮和当前页上下文；抽屉复用三组导航；处理关闭、路由切换和焦点恢复。  
完成标准：移动端不再横向平铺入口；键盘和触控均可完成导航。  
验证方式：窄屏浏览器、键盘 Tab/Escape、打开后焦点、关闭后焦点、路由切换自动关闭。  
风险说明：不得让桌面与移动端维护两份不同导航配置。

### [x] A-03 开发期文案与旧入口清理

任务编号：A-03  
任务名称：移除开发痕迹并换成温柔可爱的界面文案  
优先级：P0  
来源需求：REQ-COPY-001、REQ-COPY-002、REQ-COMPAT-001  
涉及文件：`src/app/manage/components/manage-topbar.tsx`、`src/app/manage/(workspace)/**/page.tsx`、`src/app/manage/(workspace)/components/future-capability-page.tsx`引用点  
修改内容：移除 Batch/MVP/占位等日常文案；按 v1.1 词典替换导航、标题、按钮、状态、空态与反馈；移除顶栏“旧管理面板”；保留旧 `/manage`路由和能力。  
完成标准：批准的禁用词和技术词不直接出现在日常 UI；可见文案温柔可爱但不弱化错误、费用、安全和删除后果。  
验证方式：源码定向扫描 + 所有一级页面浏览器检查。  
风险说明：扫描结果需区分用户可见 UI 与历史 workflow 文档、代码注释。

## B. 管理端组件统一

### [x] B-01 建立轻量管理组件并在低风险页面试点

任务编号：B-01  
任务名称：建立 manage-scoped 表现层组件  
优先级：P1  
来源需求：REQ-COMP-001、REQ-COMP-002、REQ-STATE-001  
涉及文件：`src/app/manage/components/`，试点优先 `src/app/manage/(workspace)/subjects/**` 或 `attachments/**`  
修改内容：收束 PageHeader、Panel、EmptyState、StatusBadge、组合式 Table、FormPanel；状态 tone 由页面显式映射。  
完成标准：试点覆盖 loading、empty、error、列表与表单容器；组件不持有 API 或 DTO；不建立全包式 DataTable。  
验证方式：TypeScript 检查；组件调用审查；试点页面桌面/移动浏览器检查。  
风险说明：只抽取实际重复表现，拒绝为单页面场景扩张组件 API。

### [x] B-02 将其余内容管理页迁移到统一反馈规范

任务编号：B-02  
任务名称：逐页统一列表、状态和表单外壳  
优先级：P1  
来源需求：REQ-COMP-001、REQ-STATE-001、NFR-007  
涉及文件：`src/app/manage/(workspace)/questions/**`、`mistakes/**`、`drafts/**`、`review/**`及其 route-specific components  
修改内容：在不改变业务请求的前提下使用已验证的管理组件和状态规范。  
完成标准：各页 loading、empty、filtered-empty、error、busy、success 可区分；管理内容面板圆角与密度一致。  
验证方式：TypeScript 检查；逐页状态检查；长文本和 200% 缩放检查。  
风险说明：不得借组件迁移提前执行 C1/C2 的业务模块迁位。

## C1. 题目链职责归位

### [x] C1-01 将手工题目录入迁入采集

任务编号：C1-01  
任务名称：采集页增加现有手工题目录入方式  
优先级：P0  
来源需求：REQ-CAP-001  
涉及文件：`src/app/manage/(workspace)/capture/**`、`src/app/manage/(workspace)/drafts/components/draft-workspace.tsx`或拆出的现有表单组件  
修改内容：复用现有创建草稿 API 和字段，将手工录入作为采集方式展开；暂不改变提交契约和详情 URL。  
完成标准：手工录入可从采集完成原有创建流程，行为与迁移前一致。  
验证方式：创建一条手工题目草稿并进入既有详情；失败和无科目状态检查。  
风险说明：先复用逻辑再移除旧位置，避免迁移过程中丢失入口。

### [x] C1-02 收束题目审核与正式题库

任务编号：C1-02  
任务名称：待审核页移除创建表单，题库保持正式内容边界  
优先级：P0  
来源需求：REQ-DRAFT-001、REQ-QUESTION-001  
涉及文件：`src/app/manage/(workspace)/drafts/**`、`src/app/manage/(workspace)/questions/**`  
修改内容：从待审核页移除手工创建模块；保留题目草稿审核；题库只展示正式题目。  
完成标准：题目链形成“采集 -> 待审核 -> 题库”，原审核和详情操作可用。  
验证方式：手工创建、审核确认、题库出现正式题目的端到端浏览器检查。  
风险说明：不得在此任务聚合错题草稿，C2 单独执行。

## C2. 错题链职责归位

### [x] C2-01 将错题草稿创建迁入采集

任务编号：C2-01  
任务名称：采集页增加现有“从题库记录错题”方式  
优先级：P0  
来源需求：REQ-CAP-001、REQ-MISTAKE-001  
涉及文件：`src/app/manage/(workspace)/capture/**`、`src/app/manage/(workspace)/mistakes/components/mistake-workspace.tsx`或拆出的现有表单组件  
修改内容：复用现有题库选择和错题草稿创建动作，在采集入口展开；不改 API 和详情 URL。  
完成标准：可从采集选择正式题目并创建错题草稿。  
验证方式：选择题目、创建草稿、失败反馈、无 active 题目状态检查。  
风险说明：先保证新入口完整，再从错题页移除旧入口。

### [x] C2-02 在待审核页聚合两类草稿

任务编号：C2-02  
任务名称：建立单列表审核中心  
优先级：P0  
来源需求：REQ-DRAFT-001、REQ-STATE-001  
涉及文件：`src/app/manage/(workspace)/drafts/**`、必要的现有错题草稿 client 调用  
修改内容：单列表展示题目/错题草稿；加入全部/题目/错题筛选；统一摘要、来源、状态、时间和审核入口。  
完成标准：两类草稿可从同一审核中心到达各自既有详情；一类失败不被显示为空。  
验证方式：三种筛选、两类详情跳转、空态、局部错误、移动端列表检查。  
风险说明：复用现有 API，禁止为聚合列表新增后端接口。

### [x] C2-03 将错题页收束为正式错题管理

任务编号：C2-03  
任务名称：移除错题页的创建与待审核模块  
优先级：P0  
来源需求：REQ-MISTAKE-001、REQ-COMPAT-001  
涉及文件：`src/app/manage/(workspace)/mistakes/**`  
修改内容：只保留正式错题列表、筛选和详情入口；删除页面内重复的创建和待审核 UI。  
完成标准：错题页只代表正式内容，采集和待审核已分别承接原入口。  
验证方式：正式错题列表/详情、采集创建、审核详情三处回归。  
风险说明：旧公开 Note 错题与私有 Mistake 的数据边界不得改变。

## D. 总览与 AI 长期布局

### [x] D1-01 收束 Dashboard

任务编号：D1-01  
任务名称：将 Batch 入口索引改为真实工作总览  
优先级：P1  
来源需求：REQ-DASH-001、REQ-COPY-001  
涉及文件：`src/app/manage/(workspace)/dashboard/page.tsx`及必要的现有前端 API 调用  
修改内容：展示可靠待处理事项与常用入口；移除 Jobs/Settings/占位状态；无可靠数量时省略徽章。  
完成标准：无新增统计接口、无全量列表计数、失败不显示为零且不阻断入口。  
验证方式：网络成功/失败/无数据状态；请求数量审查；桌面/移动浏览器检查。  
风险说明：控制首屏请求并避免重复拉取现有列表。

### [x] D2-01 重排 AI 治理首页

任务编号：D2-01  
任务名称：按易懂层级重排 AI 小助手页面  
优先级：P1  
来源需求：REQ-AI-001、REQ-AI-002、REQ-COPY-002  
涉及文件：`src/app/manage/(workspace)/ai/page.tsx`及 manage-scoped 表现组件  
修改内容：按处理记录、模型连接、使用与花费、调用记录组织；保留现有只读数据和调用统计；隐藏不必要技术词。  
完成标准：无新增写操作或主动探针；“还没有费用记录，不代表 0”表达明确；敏感字段不渲染。  
验证方式：现有数据/空数据/区块失败、长 Provider 名称和长错误摘要检查；敏感词定向审查。  
风险说明：不得把 Provider 运行状态误写为真实在线探针结果。

### [x] D3-01 收束 AI Run 二级导航

任务编号：D3-01  
任务名称：统一 AI 处理记录页面归属和返回路径  
优先级：P1  
来源需求：REQ-NAV-002、REQ-AI-001  
涉及文件：`src/app/manage/(workspace)/ai/runs/page.tsx`、`src/app/manage/components/manage-sidebar.tsx`  
修改内容：移除 Batch 和 Run Audit 等可见技术文案；使用“处理记录”和“回到 AI 小助手”；保证侧栏激活 AI 小助手。  
完成标准：Run 审计仍独立可用，人工接受/拒绝/重试能力不变。  
验证方式：列表、详情、人工流转、返回 AI、父级激活检查。  
风险说明：不得将业务 Run 与技术调用日志混为同一状态模型。

## E. 验证与收口

### [x] E-01 静态与构建验证

任务编号：E-01  
任务名称：执行前端静态检查与构建验证  
优先级：P0  
来源需求：NFR-002、NFR-008  
涉及文件：本 workflow `validation.md`（实施阶段创建或更新）  
修改内容：运行 `npx tsc --noEmit`、`git diff --check`；对构建敏感变更运行 `npm run build`。  
完成标准：检查通过，或明确记录第一个与本任务无关的既有失败。  
验证方式：保存命令、结果、时间和失败边界。  
风险说明：不得依赖 `ignoreBuildErrors`替代 TypeScript 健康证明。

### [x] E-02 浏览器与可访问性验收

任务编号：E-02  
任务名称：验证管理端全链路、响应式和公开边界  
优先级：P0  
来源需求：REQ-NAV-003、REQ-STATE-001、REQ-PUBLIC-001、REQ-COMPAT-001、NFR-003、NFR-004  
涉及文件：本 workflow `validation.md`与 `assets/`中的必要证据  
修改内容：检查桌面/移动导航、核心页面状态、长文本、200% 缩放、键盘焦点、旧链接和公开首页边界。  
完成标准：无遮挡、溢出、失焦、布局跳动；公开页不出现管理数据；旧链接仍可访问。  
验证方式：真实浏览器逐项验收并保存必要截图。  
风险说明：必须覆盖失败态和窄屏，不只验收理想数据桌面截图。

首轮状态（2026-07-12）：**未通过**。代码审查发现以下问题：AI 页面暴露原始 Provider 错误正文；切换采集方式清空未保存内容；移动抽屉无焦点约束；审核中心把请求失败显示为空列表；AI 处理记录行不可键盘操作。修复轮 R-01~R-05 解决上述问题后重新验收。

最终状态（2026-07-13）：**通过**。真实浏览器复验覆盖 390px 移动视口、抽屉完整视口覆盖和焦点循环、AI 错误脱敏、采集状态保留、审核局部失败、AI 记录键盘打开、11 个管理路由、公开首页请求边界及等效 200% 布局。

### [x] E-03 文档收口

任务编号：E-03  
任务名称：回填实施证据、剩余风险与交接状态  
优先级：P0  
来源需求：全部批准需求  
涉及文件：`README.md`、`tasks.md`、`validation.md`、`handoff.md`，必要时 `audit.md`、`diff-report.md`  
修改内容：逐项记录完成状态和证据；未验证或失败项进入风险，不虚报闭环。  
完成标准：任务、验证、风险和交接结论一致。  
验证方式：文档交叉核对与 `git diff --check`。  
风险说明：未完成项不得因阶段结束被批量勾选。

## 推荐执行顺序

```text
A-01 -> A-02 -> A-03
  -> B-01 -> B-02
  -> C1-01 -> C1-02
  -> C2-01 -> C2-02 -> C2-03
  -> D1-01
  -> D2-01 -> D3-01
  -> E-01 -> E-02 -> E-03
```

## F. 修复轮（审查反馈）

### [x] R-01 AI 页面错误脱敏

任务编号：R-01  
来源审查项：P1-01  
涉及文件：`src/app/manage/(workspace)/ai/page.tsx`  
修改内容：不直接显示 `log.error` 原文；仅展示安全分类或脱敏后的简短说明；不在 `title` 属性暴露完整错误正文；不展示 API Key、Token、Prompt、Input Summary、Replay Input 等敏感信息。  
完成标准：浏览器中看不到真实服务商错误链和敏感字段。  
验证方式：源码审查 + 浏览器检查失败调用记录。

### [x] R-02 采集模式状态保留

任务编号：R-02  
来源审查项：P1-02  
涉及文件：`src/app/manage/(workspace)/capture/components/capture-content.tsx`  
修改内容：使用 lazy mount + keep-alive 模式保留三个采集模式各自的未提交状态；切换模式不静默丢失输入。  
完成标准：填写题干后切换到上传图片再切回，内容仍在。  
验证方式：浏览器手动复现 + 回归测试。

### [x] R-03 移动抽屉焦点约束

任务编号：R-03  
来源审查项：P1-03  
涉及文件：`src/app/manage/components/manage-mobile-nav.tsx`  
修改内容：打开后焦点进入抽屉；Tab/Shift+Tab 只在抽屉内循环；背景内容使用 `inert` 隔离；Escape、遮罩和关闭按钮关闭后焦点返回菜单按钮；路由切换后抽屉关闭。  
完成标准：Tab 不越过最后一个导航项进入背景。  
验证方式：键盘 Tab/Shift+Tab/Escape 测试。

### [x] R-04 审核中心局部失败显示

任务编号：R-04  
来源审查项：P1-04  
涉及文件：`src/app/manage/(workspace)/drafts/components/draft-workspace.tsx`  
修改内容：任一数据源失败显示对应局部错误；不把失败解释为零条数据；已成功加载的另一类内容仍可展示；提供明确重试方式。  
完成标准：题目草稿请求失败 + 错题草稿返回空数组时，"全部"筛选显示错误提示而非空列表。  
验证方式：模拟请求失败 + 回归测试。

### [x] R-05 AI 处理记录键盘可操作

任务编号：R-05  
来源审查项：P1-05  
涉及文件：`src/app/manage/(workspace)/ai/components/ai-runs-panel.tsx`  
修改内容：表格行可键盘聚焦并使用 Enter/Space 打开详情；保留表格语义和清晰焦点样式。  
完成标准：键盘用户可 Tab 到行并按 Enter 打开详情。  
验证方式：键盘 Tab + Enter/Space 测试。

### [x] R-06 Dashboard 文案与 rounded-xl 修正

任务编号：R-06  
来源审查项：P2-01、文档问题 6  
涉及文件：`src/app/manage/(workspace)/dashboard/page.tsx`、`src/app/manage/components/manage-mobile-nav.tsx`、`src/app/manage/components/manage-topbar.tsx`  
修改内容：Dashboard 替换 `待审核`→`待确认`、`待复习`→`温习`、`科目与知识点`→`学科角`、`附件`→`资料袋`；扫描 workspace 内其他用户可见文案确保与 v1.1 词典一致；修复新 manage 组件中的 `rounded-xl`。  
完成标准：Dashboard 文案与 v1.1 词典一致；新组件无 `rounded-xl`。  
验证方式：源码扫描 + 浏览器检查。

### [x] R-07 移动抽屉完整背景隔离

任务编号：R-07  
来源审查项：E-02 最终复验  
涉及文件：`src/app/manage/components/manage-mobile-nav.tsx`、对应回归测试  
修改内容：抽屉打开时沿 DOM 祖先链隔离各层非抽屉分支，覆盖工作区内容及站点级移动导航；关闭或卸载时只恢复本组件添加的 `inert`。  
完成标准：抽屉外的工作区、站点级底部导航和其他可聚焦背景均不可访问；焦点循环与恢复行为保持不变。  
验证方式：跨层 DOM 回归测试 + 真实移动浏览器辅助功能树与键盘检查。

### [x] R-08 依赖锁文件精确版本同步

任务编号：R-08  
来源审查项：E-01 最终复验  
涉及文件：`package-lock.json`  
修改内容：将锁文件根依赖中的 `react-dom` 同步为与 `package.json` 一致的精确 `19.2.1`。  
完成标准：清单与锁文件不再出现根依赖版本范围漂移，安装元数据校验通过。  
验证方式：源码检查 + `npm install --package-lock-only --ignore-scripts --dry-run`。

### [x] R-09 移动抽屉完整视口覆盖

任务编号：R-09  
来源审查项：E-02 截图复验  
涉及文件：`src/app/manage/components/manage-mobile-nav.tsx`、对应回归测试  
修改内容：将抽屉覆盖层挂载到 `document.body`，避免工作区玻璃容器形成固定定位上下文后裁短覆盖层。  
完成标准：抽屉和遮罩覆盖完整移动视口，站点级底部导航不再露出；R-07 的背景隔离、焦点循环和焦点恢复保持通过。  
验证方式：Portal 回归测试 + 390px 真实浏览器截图与键盘复验。
