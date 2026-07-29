# Residual Risks

## RISK-P10-001 Baseline contaminated by existing worktree artifacts

- 风险类型：审计 / Git。
- 风险描述：当前已有未跟踪评估文档，后续可能被误归入 Phase 1.0 实施 diff。
- 影响范围：发布范围、验收可信度。
- 严重程度：中。
- 当前状态：已控制；P0-01 已记录精确边界，文件仍未跟踪且未被删除。
- 建议措施：Phase 0 精确记录 worktree；后续按任务文件范围审查，不 reset 用户文件。
- 是否进入下一轮需求：否，当前阶段控制。

## RISK-P10-002 Dashboard 聚合造成 API 耦合或虚假统计

- 风险类型：架构 / 产品。
- 风险描述：前端直接拼接多个列表 API 可能产生不一致快照、部分失败和过度请求。
- 影响范围：Dashboard 可信度与性能。
- 严重程度：高。
- 当前状态：**RESOLVED in Gate A**；单一 admin-only summary API 提供一致计数、有限最近列表与 unknown/zero 边界。
- 建议措施：Gate A 先完成合同审计；unknown 与 zero 分离；禁止 mock。
- 是否进入下一轮需求：是。

## RISK-P10-003 Public mobile nav introduces auth noise

- 风险类型：权限 / 体验。
- 风险描述：为显示管理员入口而在公开首页阻塞式探测会话，可能产生加载延迟或 401/403 噪音。
- 影响范围：移动首页与匿名用户。
- 严重程度：高。
- 当前状态：**RESOLVED in Gate A**；公开导航先渲染，管理入口仅在管理员会话确认后追加，匿名浏览器只有预期 auth/me 401 且无 UI/console error。
- 建议措施：公开导航先渲染；管理员入口仅在已确认会话后追加。
- 是否进入下一轮需求：是。

## RISK-P10-004 Historical auth status conflicts

- 风险类型：安全 / 文档。
- 风险描述：LT-ISSUE-002 同时出现在旧“未处理”段落和新“已修复”记录中。
- 影响范围：v1.0 Auth 判断。
- 严重程度：中。
- 当前状态：Phase 0 已统一为“代码与专项测试已修复，真实账号矩阵未重跑”；旧文档仍保留历史措辞。
- 建议措施：Gate B 运行 auth matrix；不要把旧失败段落当成当前 open 状态。
- 是否进入下一轮需求：是。

## RISK-P10-005 Backup evidence is revision-stale

- 风险类型：数据 / 恢复。
- 风险描述：现有隔离恢复证据针对 revision 018，不能证明 revision 020 与当前附件可恢复。
- 影响范围：Production Ready 判断。
- 严重程度：高。
- 当前状态：已确认；现有恢复证据仍停留在 revision 018。
- 建议措施：Gate B 复用安全模式，生成当前 DB + Attachment 配对证据。
- 是否进入下一轮需求：是。

## RISK-P10-006 Authenticated management screenshots unavailable

- 风险类型：验收 / 体验。
- 风险描述：无真实管理员会话时无法验证 Dashboard 和管理主流程当前视觉状态。
- 影响范围：Phase 0 UI baseline 与 Gate A 验收。
- 严重程度：中。
- 当前状态：**RESOLVED in Gate A**；使用短生命周期真实 admin session 完成桌面/390px 视觉验收，未使用 AUTH_BYPASS，会话已精确删除并验证不存在。
- 建议措施：等待真实用户会话；不得使用 AUTH_BYPASS；缺失证据标 BLOCKED。
- 是否进入下一轮需求：否，作为 Gate blocker 管理。

## RISK-P10-007 Learning Analytics leaks into product-polish scope

- 风险类型：范围 / migration。
- 风险描述：Analytics Lite 可能顺手引入新表、migration 和新产品承诺。
- 影响范围：Phase 1.0A/B 可审查性。
- 严重程度：高。
- 当前状态：已缓解。
- 建议措施：Gate C 标记 DEFERRED / NOT AUTHORIZED，RC 后重新审批。
- 是否进入下一轮需求：是，进入 Gate C。

## RISK-P10-008 Alembic metadata drift at revision 020

- 风险类型：schema / migration。
- 风险描述：数据库与 migration 均为 `020 (head)`，但 `alembic check` 提议删除三个 knowledge-point indexes 并新增 sibling-name unique constraint。
- 影响范围：未来 migration 生成、taxonomy 写入约束、Production Ready 判断。
- 严重程度：高。
- 当前状态：**RESOLVED / Schema Authority Gate PASS**。SA-A lifecycle metadata/service alignment is complete; `current`/`heads` are `020 (head)`, `check` has no upgrade operations, taxonomy tests pass, and core counts are unchanged. No DDL/migration or recovery-boundary change occurred.
- 建议措施：RC 使用最终 revision `020` 重新执行全链路证据；任何未来 physical schema change 仍须独立授权和恢复证明。
- 是否进入下一轮需求：是。

## RISK-P10-009 Current local frontend chunks return HTTP 500

- 风险类型：runtime / UI acceptance。
- 风险描述：页面文档返回 200，但现有本地 Next.js 实例的 generated CSS/JS chunks 返回 500，公开和管理页面停留在空白或加载状态。
- 影响范围：Demo Ready、UI baseline、管理截图与本地日常使用。
- 严重程度：blocker。
- 当前状态：**RESOLVED on 2026-07-17 by Phase 0.5**。根因为 stale Next 16.0.10 runtime 与当前 16.2.10 build output 不一致；clean build/restart 后目标 documents、JS/CSS、hydration、console 与 critical assets 全部通过。
- 建议措施：保留既有 LaunchAgent 与 clean-build 运行基线；未来依赖或构建变更后重新执行同一 runtime smoke matrix。
- 是否进入下一轮需求：否；runtime blocker 已解除。

Phase 0.5 ownership: `REQ-P05-001` through `REQ-P05-005` and P05-01 through P05-05 all passed. Historical Phase 0 failure evidence remains valid as root-cause history, not current runtime state.

## RISK-P10-010 Implemented infrastructure is hidden by placeholder routes

- 风险类型：product surface / route ownership。
- 风险描述：CaptureWorkspace、AI Gateway、AI runs 等实现存在，但当前 `/manage/capture`、`/manage/ai`、`/manage/ai/runs` 页面仍渲染 Batch 6 placeholder。
- 影响范围：用户感知完整度、能力发现、未来误删或重复实现风险。
- 严重程度：高。
- 当前状态：**RESOLVED in Gate A**；Drafts 作为 active 能力接入真实列表与详情，Capture、AI/AI Runs、Search、Analytics、Jobs 明确 deferred 并保留路由。
- 建议措施：Gate A 逐路由决定 active/deferred，并以真实可验收能力为准收口展示。
- 是否进入下一轮需求：是。

## RISK-P10-011 Public recommendation GET has write side effects

- 风险类型：API 语义 / 数据副作用。
- 风险描述：本地浏览器读取首页时，既有 `GET /api/recommendations/today` 在当日数据缺失时触发真实 AI 生成，写入 recommendation、AI run 与 call log；一次页面验收产生 1 + 3 + 3 条记录。
- 影响范围：只读验收、成本、可重复测试、GET 幂等预期。
- 严重程度：中。
- 当前状态：**CODE RESOLVED / RELEASE VERIFICATION PENDING**。公开 today GET 已改为只读缺失安全响应；生成、删除、history 均为管理员路径，history 不再返回 raw context。定向合同测试 6/6 通过。
- 建议措施：完成获批的 pre-deploy matrix 与不接触生产的安全评审；部署目标验证仍需独立部署授权。
- 是否进入下一轮需求：是，完成发布前门禁。

## RISK-P10-012 Minimal Learning Feedback scope expansion

- 风险类型：产品范围 / 数据语义。
- 风险描述：已完成的确定性 Dashboard 下一步提示，可能被误扩展为掌握度、AI 建议、推荐、Analytics、BKT 或持久化反馈。
- 影响范围：公开/管理权限边界、数据语义、schema 与产品承诺。
- 严重程度：中。
- 当前状态：已控制；Gate C 仅使用既有 admin summary counts，无新 API/schema/persistence/AI，且四分支优先级已有测试。
- 建议措施：任何新增指标、字段、存储、公共入口、AI 或用户角色均需新 workflow、精确 tasks 和独立批准；若涉及 schema，先走 backup/isolated restore/migration Gate。
- 是否进入下一轮需求：是，作为后续产品扩展。

## RISK-P10-013 Production authentication bypass startup exposure

- 风险类型：安全 / 启动配置。
- 风险描述：生产环境曾允许 `AUTH_BYPASS` 与 `AUTH_BYPASS_ALLOW` 同时为真而继续启动，且 JWT/CORS 安全拒绝使用 `SystemExit`。
- 影响范围：管理员认证真实边界、服务启动失败语义与可观测性。
- 严重程度：高。
- 当前状态：**RESOLVED**。production lifespan 现在在 database readiness 前拒绝双 bypass，并对 JWT、CORS、bypass 三类不安全配置统一抛出 `RuntimeError`；定向 11/11 通过。
- 建议措施：部署前仍须在目标环境验证配置；不得将 diagnostics warning 视为替代启动硬阻断。
- 是否进入下一轮需求：否，代码闭环；生产部署验证另行授权。

## RISK-P10-014 Release gate omits backend/schema checks

- 风险类型：发布 / 验证。
- 风险描述：现有 `predeploy:check` 强制 clean worktree、依赖审计和前端构建，但不运行后端 pytest、Alembic authority checks 或 recommendation public/admin contract verification。
- 影响范围：部署前安全判断、API 语义与数据库 revision 一致性。
- 严重程度：高。
- 当前状态：**PARTIALLY MITIGATED / DEPLOYMENT BLOCKED**。获批实现已将 backend pytest 与 Alembic `current`/`heads`/`check` 纳入 fail-closed matrix，并要求隔离 test DB 与 target DB 显式且不同；本地完整回归和脚本语法通过。实际 predeploy 保持由 dirty-worktree 首门禁阻断，未读取 target DB、未执行 deploy。
- 建议措施：在得到生产访问与部署授权后，以已决定的 target 边界运行完整 fail-closed matrix；保持 clean-worktree gate，不以本地测试替代 target 验证。
- 是否进入下一轮需求：是。

## RISK-P10-015 Production registration and invocation-log policy

- 风险类型：生产安全 / 隐私。
- 风险描述：配置默认允许注册，生产启动未强制要求关闭或受 registration key 保护；Cloudflare template 使用全量 invocation sampling 与 persistent logs，但无明确生产隐私/保留决策。
- 影响范围：账号创建面、请求元数据保留、生产部署资格。
- 严重程度：高。
- 当前状态：**CODE/TEMPLATE RESOLVED / TARGET VERIFICATION PENDING**。用户已决定 production registration disabled 与 Workers Logs 1% head sampling/platform short retention；production lifespan 现在拒绝 `ENABLE_REGISTRATION=true`，template 采样为 `0.01`。未读取真实生产配置或日志，故未声明 deployed target 已符合。
- 建议措施：frontend 部署前在 clean isolated worktree 运行 frontend gate；backend 发布或 target DB 检查仍需独立授权，并用不泄露配置值的方式证明目标满足该策略。
- 是否进入下一轮需求：是。

## RISK-P10-016 Worker temporary-origin CORS boundary

- 风险类型：生产 runtime / integration。
- 风险描述：Cloudflare `workers.dev` 临时 Worker origin 不在后端 CORS allowlist，因而不能作为浏览器端的正式产品入口；若将其误作验收 URL，会产生 site-settings network failure。
- 影响范围：部署验收口径、临时 Worker URL 的可用性判断；不影响已验证的正式 frontend domain。
- 严重程度：低（已控制）。
- 当前状态：**CONTROLLED / FORMAL DOMAIN PASS**。只读 probes 证明 public API health 为 200；`Origin: https://blog.limengyang.me` 的 preflight/读取为 200 且允许跨域。fresh anonymous browser 在正式域名上取得 document/JS/CSS 200、hydration/navigation、0 console errors 和公开 API 读取成功。先前 failure artifact 保留为临时 origin 边界证据，不再表述为 API outage。
- 建议措施：发布和验收固定使用正式 frontend domain；不要扩大 CORS 以兼容临时 `workers.dev` URL，除非另有安全评审和明确批准。管理员、附件与 diagnostics 公网 smoke 仍需 secret-safe real-admin session。
- 是否进入下一轮需求：是。

## RISK-P10-017 Production password rotation targets the frontend origin

- 风险类型：auth / production integration。
- 风险描述：legacy security settings uses a direct relative `fetch('/api/auth/set-password')`, while the formal frontend origin does not proxy backend APIs. A real high-privilege Passkey session therefore cannot rotate its password through the UI.
- 影响范围：管理员凭证轮换、Personal Use Ready 与生产管理可用性。
- 严重程度：高。
- 当前状态：**ROOT CAUSE CONFIRMED / REPAIR AWAITING APPROVAL**。真实浏览器安全设置可见且 Passkey session 有效；source shows the relative fetch, and no console/UI error was retained after the failed submission. The configured API client is the working reference for public and protected routes. No password value is recorded.
- 建议措施：只修复该调用到 typed configured-base API wrapper，测试先行；在 approved frontend-only clean artifact 中重跑 gate/release，并由用户在正式浏览器自行输入密码后明确确认最终提交。
- 是否进入下一轮需求：是。
