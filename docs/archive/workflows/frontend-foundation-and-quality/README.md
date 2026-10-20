# 前端技术基座与质量保障：F4 前总工作夹

## 目标

在不进行前端视觉改造、不进入 F4 生产渲染验收的前提下，把 F0～F3/G4 收敛为一个有依赖、有阶段门、有统一验收标准的总工作夹：

1. 路由归属；
2. Markdown 渲染安全 PoC；
3. 编辑器能力收敛；
4. 公开会话状态优化；
5. F4 的输入合同与进入条件，但不执行 F4。

本工作夹负责当前事实、顺序、依赖、跨域风险、用户决策点和 F4 前证据闭环。各子任务组保留自己的范围与验收 Gate；本轮只整理计划，不把历史授权解释为对修订后实现清单的自动批准。

## 触及领域

- 前端：routing、notes、blog、mistakes、manage、shared hooks、Markdown rendering；
- 后端：auth 的最小会话状态合同，仅在对应阶段前置 Gate 通过后涉及；
- 共享基础设施：类型检查、隔离测试和浏览器权限/安全证据；生产构建、合成数据和性能采样仅作为 F4 输入要求记录。

不涉及视觉系统迁移；视觉与交互统一仍由 `visual-system-consolidation` 独立负责。

## 当前状态

`F4 INPUT READY FOR SEPARATE APPROVAL — FIX-01～05 COMPLETE; G2/G3/G4 PASS; F4 NOT EXECUTED OR AUTHORIZED.`

F0/G0、F1/G1、G2、G3 与 G4 均已通过其限定范围。Markdown 特殊适配器的 Mermaid、Markmap、Chart 均为 `ENABLED_ISOLATED`，没有生产消费者迁移。F2B 已在当前 HttpOnly `admin_session` Cookie 合同内完成 optional display state；FIX-01 的当前 Chromium `5 passed (12.6s)` 补齐公开详情和真实共享移动导航证据，严格会话与后端权限边界不变。F3 形成 Option A 的独立、未获实施批准清单。原 F4 输入包是历史快照；本轮修复未完成前，F4 仍不可执行。

## 当前执行边界

- **本轮当前：**FIX-01～04 已完成；FIX-05 正在准备交付审计。三类特殊适配器隔离启用与 G2、F2B PSS-01～06/G3、F3 E1～E5/G4 仅作为已验证前置证据；F4 输入包将于 FIX-05 审计后重新判断。
- **本轮不包含：**F4 实施、视觉 Token/导航/弹层/Context Action 改造、统一创作面板实现、生产 Markdown 消费者切换、JWT/Bearer 迁移、路由删除/重定向、Git 发布、部署或真实数据。
- **批准任务清单后的第一条源代码线：**特殊适配器 SA-01 起步并关闭 G2；随后执行 F2B。F3 只有在三类适配器全部通过后才能开始。

## 必须由用户判断

1. **下一步（若要继续）：单独批准 F4/PRA 当前任务清单。** 该批准才可开始 instrumentation、隔离构建、合成数据和浏览器采样。
2. **未来编辑器实施：**Option A 已选，但 `editor-convergence/implementation-tasks.md` 仍须单独批准。
3. **实施中按需：依赖或范围扩张。** 任何新依赖、持久浏览器二进制或产品交互扩张仍须独立判断。

Cookie optional-session 的字段、SWR 缓存键、测试结构、失败语义和消费者迁移顺序属于技术执行项，不需要用户逐项判断；认证提供方迁移、路由切换、视觉方案和部署均在本轮范围外，不在本工作夹内暗中决定。

## 子任务组

- [路由归属](../route-ownership-alignment/README.md)
- [Markdown 安全 PoC](../markdown-rendering-security-poc/README.md)
- [Markdown 特殊适配器安全启用](../markdown-special-adapter-enablement/README.md)
- [编辑器能力收敛](../editor-convergence/README.md)
- [公开会话状态优化](../public-session-state-optimization/README.md)
- [生产渲染就绪验收（仅作为 F4 输入）](../production-render-readiness-acceptance/README.md)

## 总任务组文档

- [设计](design.md)
- [需求](requirements.md)
- [任务清单](tasks.md)
- [现状审计](audit.md)
- [验证记录](validation.md)
- [F4 输入包模板](f4-input-package.md)
- [新对话交接 Prompt](handoff-prompt.md)

## 审批规则

- 历史 F0～F4 授权只适用于当时清单；本轮重组后的 F4 前总清单必须重新获得明确批准。
- 阶段 Gate 仍是强制技术和产品检查点；上一 Gate 未通过时不得继续依赖它的任务。
- Gate 中已有明确、可逆且不扩大范围的决策，由执行对话采用证据支持的最小风险方案并记录；若缺失信息会显著改变产品结果，仍须停止并询问用户。
- 对任务清单的批准不授权 F4、生产部署、推送、提交、真实数据/凭据使用、视觉系统迁移或超出清单的范围扩张。
