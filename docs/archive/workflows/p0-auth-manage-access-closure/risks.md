# P0-AUTH 剩余风险

## RISK-P0-AUTH-01

- 风险类型：构建
- 风险描述：未跟踪 `/workspace` 原型的两个类型错误阻断主工作区 TypeScript 和生产构建。
- 影响范围：全仓健康声明、提交前总门禁。
- 严重程度：高
- 当前状态：已解决；CLEANUP 方案 A 已删除原型，主工作区 TypeScript/构建通过。
- 建议措施：已归档到 CLEANUP 验收证据。
- 是否进入下一轮需求：否。

## RISK-P0-AUTH-02

- 风险类型：测试环境
- 风险描述：源码期望 Alembic revision 025，本地默认数据库仍为 024；带应用 lifespan 的既有 `test_auth_error_handling` 因 readiness gate 失败，不能与本轮组合运行。
- 影响范围：依赖默认本地数据库启动的后端集成测试。
- 严重程度：中
- 当前状态：已缓解；025 隔离 clone 已完成 upgrade/rollback/readiness/权限测试，日常库按边界保持 024。
- 建议措施：日常库是否迁移仍需独立授权；不得把隔离 PASS 当作源库已升级。
- 是否进入下一轮需求：是。

## RISK-P0-AUTH-03

- 风险类型：测试质量
- 风险描述：既有 AI 测试有 React `act(...)` warning；AuthGate jsdom focus 模拟有 `TimeoutNaNWarning`；Node/Tailwind 有 `DEP0205`。
- 影响范围：测试输出可读性，不影响本轮断言或真实浏览器结果。
- 严重程度：低
- 当前状态：部分缓解；已确认真实浏览器无对应 error。
- 建议措施：独立测试质量清理，不与权限修复混合。
- 是否进入下一轮需求：是，P2。

## RISK-P0-AUTH-04

- 风险类型：性能/体验
- 风险描述：登录页头像触发 Next.js LCP `loading="eager"` 建议。
- 影响范围：登录页开发期性能提示。
- 严重程度：低
- 当前状态：未处理，不属于权限缺陷。
- 建议措施：独立页面性能微调并验证 LCP。
- 是否进入下一轮需求：否，可归档到性能 backlog。
