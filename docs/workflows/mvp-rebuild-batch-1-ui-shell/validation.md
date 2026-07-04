# Batch 1 验证记录

## 验证环境

- 日期：2026-07-02
- 本地开发地址：`http://localhost:2025`
- 桌面视口：1280×720
- 移动视口：390×844
- 登录状态：未登录

## TDD 路由基线

实现前：

```text
/manage                  200
/manage/dashboard        404
/manage/drafts           404
/manage/questions        404
/manage/mistakes         404
/manage/attachments      404
/manage/subjects         404
/manage/review           404
```

实现后：

```text
/manage/dashboard        200
/manage/drafts           200
/manage/questions        200
/manage/mistakes         200
/manage/attachments      200
/manage/subjects         200
/manage/review           200
```

结果：新路由从 RED 的 404 转为 GREEN 的 200。

## TypeScript

命令：

```text
npx tsc --noEmit --pretty false
```

结果：退出码 0，无输出，**TypeScript 通过**。

按用户要求明确记录：

- 第一条失败信息：无。
- 是否涉及本批新增文件：不适用。
- 本批新增文件是否存在新的 TypeScript 错误：否。
- 补充验证：生产构建、HTTP 路由、静态边界、桌面/移动浏览器、权限与公开回归。

## 生产构建

命令：

```text
npm run build
```

结果：通过。Next.js 成功编译、执行 TypeScript、生成 32 个静态页面；新增
`/manage/attachments`、`/manage/dashboard`、`/manage/drafts`、
`/manage/mistakes`、`/manage/questions`、`/manage/review`、
`/manage/subjects` 均出现在路由清单。

非阻塞警告：

- `baseline-browser-mapping` 数据超过两个月。
- Node 报告 `module.register()` 弃用。

本批未按警告更新依赖。

## 首页浏览器验收

### 桌面 1280×720

- LearningSpaceCard 位于主卡上方。
- 与左侧导航、主卡、写文章、时钟、日历无可见重叠。
- 只显示待复习、待审核、进入学习空间、上传资料。
- 数量显示 `—`，不伪造业务数据。
- DOM 中四个入口 href 均正确。

结果：通过。

### 移动 390×844

- LearningSpaceCard 进入原卡片流末尾。
- 无横向溢出或截断。
- 四个入口全部可见。

结果：通过。

## 权限与公开回归

### 未登录管理保护

访问 `/manage/dashboard` 后，浏览器跳转至 `/manage`，显示原密码与 Passkey 登录页。
未出现重定向循环，未展示工作区内容。

结果：通过。

### 公开页面

| 路由 | 最终 URL | 登录表单 | 结果 |
| --- | --- | --- | --- |
| `/blog` | `/blog` | 无 | 公开内容可见 |
| `/notes` | `/notes` | 无 | 公开内容可见 |
| `/mistakes` | `/mistakes` | 无 | 公开内容可见 |

浏览器 error 日志：0 条。

结果：通过。

### 已登录管理工作区

状态：**通过**。

经用户授权，使用仓库既有 `create-temp-admin` CLI 轮换本地临时管理员；未使用
AUTH_BYPASS。

验证结果：

- `/manage` 登录后仍显示原管理面板，旧业务逻辑可用。
- `/manage/dashboard` 正确显示 Sidebar、Topbar、PageHeader 和四个静态导航项。
- drafts、questions、mistakes、attachments、subjects、review 六个页面标题正确。
- 六个占位页均显示“后续批次启用”。
- 六个占位页工作区内真实动作按钮数量均为 0。
- 浏览器 error 日志为 0。

视觉修复：

1. 桌面 1280×720 首次验收发现全局竖导航压住新 Sidebar；只调整新 workspace
   layout 左侧安全间距后通过。
2. 移动 390×844 首次验收发现横向导航撑宽主体；只限制新 Sidebar、nav 与内容容器
   的宽度和 overflow 后通过。

清理：

- 临时会话已注销。
- `temp-admin` 已通过既有 CLI 禁用。
- 一次性密码临时文件已删除。

## 静态硬约束

- `src/app/manage/page.tsx`：零 diff。
- `src/config/`：零本批 diff。
- `src/styles/`：零本批 diff。
- 新管理页面与占位组件：无 `<button>`、`onClick`。
- 新首页和管理文件：无 `@/lib/api` 或 `fetch()`。
- `git diff --check`：通过。

## 最终结论

**验证与用户验收均通过。** 实现、TypeScript、生产构建、首页响应式、登录与
未登录管理边界、全部占位页和公开回归均通过。用户已于 2026-07-02 确认 Batch 1
通过。

## 剩余风险与下一轮决定

- Batch 1 没有阻塞性剩余风险。
- 旧 `/manage` 与新工作区共存是已批准的兼容决定，不进入修复需求。
- 首页卡片不进入旧拖拽配置是本批硬约束，不进入下一轮需求。
- Batch 2 需求来源使用既有 `batch-2-subject-taxonomy/spec.md`，不把 Batch 1 的
  非问题转换为额外范围。
