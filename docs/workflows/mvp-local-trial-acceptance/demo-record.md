# P0-15 现场演示记录

## 执行信息

| 项目 | 结果 |
| --- | --- |
| 执行日期 | 2026-07-16 |
| 模式 | 只读 |
| 数据写入 | 未执行 |
| 代码修复 | 未执行 |
| 部署 | 未执行 |
| 前端 | `http://localhost:2025` |
| 后端健康检查 | `http://127.0.0.1:8000/api/health` → 200，`db=ok` |
| 管理员登录 | 未执行，未输入密码/token |
| 总体结果 | blocked by `DEMO-ISSUE-001` |

## 演示结果

| 演示段 | 路径 | 结果 | 证据 |
| --- | --- | --- | --- |
| Public Read：首页 | `/` | pass | 首页正常渲染，公开导航存在，控制台无 warning/error |
| Public Read：Blog | `/blog` | pass | 公开文章列表正常，未见管理操作入口 |
| Public Read：Notes | `/notes` | pass | 页面正常渲染，未见管理操作入口 |
| Public Detail | `/blog/x` | pass | `夏夜追凉` 详情正常渲染，未见编辑/删除入口 |
| Public Read：Mistakes | `/mistakes` | blocked | 307 重定向到 `/manage/mistakes`，见 `DEMO-ISSUE-001` |
| Private Manage | `/manage` | pass | 未登录显示登录页，未泄露管理工作区内容 |
| Private Manage routes | `/manage/dashboard`、`/manage/mistakes`、`/manage/review`、`/manage/attachments`、`/manage/ai`、`/manage/capture` | pass | 未登录最终回到管理登录保护状态 |
| Legacy protected route | `/mistakes/review`、`/write-mistake/test` | pass | 未登录进入管理保护，不泄露私有内容 |
| Closure Evidence | docs/DB | partial | 已有 Batch 7 validation 与数据库证据可展示；未在浏览器中执行管理态对象浏览 |

## 控制台与网络观察

- 首页、Blog、Notes、Blog 详情和管理登录页未观察到控制台 warning/error。
- `/mistakes` 的阻塞来自 HTTP redirect，不是页面加载后的随机异常。
- 本次未提交表单、未点击写入按钮、未上传附件、未调用 AI/OCR/Capture。

## 数据安全

- 未创建、更新、删除任何对象。
- 未输入管理员密码、token 或私钥。
- 未改变数据库 revision、row counts 或附件内容。

## 结论

P0-15 已按只读范围执行，但不能宣称项目验收无条件通过。`DEMO-ISSUE-001` 阻塞匿名 `/mistakes` 公开读取验收；后续应单独审批兼容修复 workflow。本次不自动修复、不部署、不进入 Batch 8。

## P0-17 修复后再次演示

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 修复文件 | `next.config.ts` | 删除 `/mistakes` → `/manage/mistakes` 单条 redirect |
| 回归测试 | pass | 先红后绿；Batch 7 route contract 4 tests passed |
| Full frontend tests | pass | 8 files / 26 tests passed |
| TypeScript | pass | `npx tsc --noEmit --pretty false` exit 0 |
| Production build | pass | `npm run build` completed；关键 routes 存在 |
| `/mistakes` 匿名访问 | pass | URL 保持 `/mistakes`，页面展示公开错题列表 |
| `/mistakes/review` 未登录 | pass | 重定向到 `/manage` 登录保护 |
| `/manage` 未登录 | pass | 登录页展示，未泄露工作区内容 |
| `/blog`、`/notes` | pass | 页面正常加载，控制台无 warning/error |
| 数据库 | unchanged | 未新增、修改或删除数据；未执行 migration |
| 部署 | not run | 明确禁止部署 |

### P0-17 结论

`DEMO-ISSUE-001` 已修复并关闭。项目验收恢复为 **conditional pass**；`LT-ISSUE-002` 仍保留为独立认证错误处理条件项。未登录、未写入、未部署，且不自动进入下一 Batch。
