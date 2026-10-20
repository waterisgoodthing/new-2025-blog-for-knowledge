# P0-AUTH Diff 报告

状态：`COMPLETE`

## 业务代码

- `src/app/manage/page.tsx`
  - 初始会话与登录回调均要求 `is_admin === true`。
  - 非管理员或鉴权失败会清理 user/authenticated 页面状态。
- `src/hooks/use-admin-auth.ts`
  - 新增可选 `strict` 模式。
  - strict 使用独立 SWR key，并启用 focus/reconnect revalidation 与短 dedupe。
- `src/components/auth-gate.tsx`
  - 页面级 gate 使用 strict 管理员核验。

## 测试

- `src/app/manage/manage-auth.test.tsx`
  - 非管理员初始会话、非管理员密码登录回调、管理员正常状态。
- `src/components/auth-gate.test.tsx`
  - 新受保护入口重新核验、页面保持挂载时 focus 后降权收口。
- `backend/tests/test_manage_write_permissions.py`
  - 全部管理写路由依赖契约。
  - Note create/update/delete 的匿名、失效和非管理员运行时权限。

## 未修改

- backend 运行时代码、API contract、数据库、schema、migration。
- AUTH_BYPASS、JWT、Passkey。
- `/workspace` 原型。
- 公开 blog/note/mistake 页面。
- 部署或远端仓库。
