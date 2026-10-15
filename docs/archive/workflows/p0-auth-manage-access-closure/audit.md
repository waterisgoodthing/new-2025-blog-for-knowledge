# P0-AUTH 审计记录

状态：`P0-AUTH-01 COMPLETE / IMPLEMENTATION BASELINE`

## 当前结论

- `/manage` 的直接缺陷是只检查会话成功、不检查 `is_admin`。
- AuthGate 的严格入口需要防止共享缓存把旧管理员状态当作当前权限证明。
- 后端 `get_current_admin` 的 401/403 语义正确；当前枚举未发现明显未保护的管理写路由。
- 仍需统一契约测试防止未来新增写路由漏保护。
- 公开路由必须保持匿名可读。

## 2026-07-30 根因复现与基线

- `src/app/manage/page.tsx` 的初始检查与登录回调都在任意 `getMe()` 成功后设置 `authenticated=true`，未检查 `user.is_admin`。有效普通/降权 session 因此稳定复现为旧管理面板可见。
- `src/components/auth-gate.tsx` 依赖 `useAdminAuth()`；hook 的判断本身要求 `is_admin === true`，但使用共享 key、60 秒 dedupe，并关闭 focus/reconnect revalidation。严格页面入口不能把这份可能陈旧的展示缓存当作当前授权证明。
- FastAPI 当前注册的管理型 POST/PUT/PATCH/DELETE 已通过只读路由枚举；除登录/登出/注册、Passkey 认证入口和公开留言创建外，当前管理写路由均声明 `get_current_admin` 或更严格的 `get_passkey_admin`。
- 后端当前语义：无会话/无效会话为 401，非管理员 session 为 403。
- 公开页面基线仍为 `/blog`、`/notes`、`/mistakes` 无页面级 AuthGate。
- 工作树中未跟踪 `src/app/workspace/page.tsx` 仍由 R1 边界排除，P0-AUTH 不得修改或通过配置隐藏其类型错误。

## 最终安全与代码质量审查

- 直接根因在 `/manage` 最小修复，没有重构 legacy 页面。
- AuthGate strict 模式与普通公开展示缓存分离；没有让公开页面反复请求管理员接口。
- Hook 调用顺序保持稳定。
- 后端运行时代码无需修改；102 条管理写路由均已有 `get_current_admin` 或 `get_passkey_admin`。
- 公开页面未修改，三尺寸匿名浏览器验证通过。
- 未发现 P0-AUTH 新增死链、横向溢出或浏览器 error。
- scoped 类型、构建、完整前端和定向后端测试通过。
- 主工作区与默认数据库的范围外阻断已进入 risks，不以 scoped 成功掩盖。

历史结论：P0-AUTH 权限功能 `PASS`；当时工作区闭环因范围外构建和数据库基线保持 `PARTIAL`。

后续结论（2026-07-30）：单独批准的 CLEANUP 已删除原型、通过主工作区
test/tsc/build、三尺寸浏览器和隔离 revision 回放。P0-AUTH workspace gate
更新为 `PASS`；日常库仍为 024，不视为已迁移。
