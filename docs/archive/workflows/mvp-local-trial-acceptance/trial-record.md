# MVP 本地试运行记录

## 结论摘要

| 项目 | 记录 |
| --- | --- |
| 日期 | 2026-07-04 |
| 分支 / commit | `notes-workspace-ux-upgrade` / `97626d21cf2505a46a641ed5f14b5853ccd42914` |
| 前端 / 后端 | `http://localhost:2025` / `http://127.0.0.1:8000` |
| 数据库 | PostgreSQL `localhost/blog_db`，Alembic `014 (head)` |
| 管理员方式 | 既有 CLI 临时管理员 + password cookie session |
| AUTH_BYPASS | false / false |
| 总体结论 | conditional pass（有条件通过） |
| 核心链路 | pass |
| 唯一条件项 | LT-ISSUE-002 |
| 归档兼容项 | LT-ISSUE-001（localhost 非目标环境） |

## 公共对象

| 节点 | ID | 结果 |
| --- | --- | --- |
| subject | `135` | create 201，refresh 200 |
| Hash Table knowledge point | `21` | create 201 |
| Stack knowledge point | `22` | create 201 |
| Tree BFS knowledge point | `23` | create 201 |

## 样例一：two-sum

| 节点 | ID | 结果 |
| --- | --- | --- |
| question draft item | `ae937d09-2199-4ed1-bd19-fe5b80714385` | create 201 |
| question | `6d13b948-433e-491e-95dd-0f519503572a` | convert 200 |
| mistake draft item | `afc508eb-f6ae-4502-99e2-9cccc5636590` | create 201 |
| mistake | `1e2b95b7-9116-46ae-b6e6-952b9227460b` | convert 200 |
| review item | `fa7f772c-5d06-4219-81f4-88e705c8ce32` | submit 200 |
| review record | 1 条 | list 200 |
| 样例结论 | pass | 主链路完整 |

## 样例二：valid-parentheses

| 节点 | ID | 结果 |
| --- | --- | --- |
| question draft item | `11b78a85-bcc0-4fe2-9b0b-aab7bc31b289` | create 201 |
| question | `496998c5-be71-421a-80c6-017bcc5d6cd6` | convert 200 |
| mistake draft item | `1ae0f363-1f8a-4268-a781-c82167a0895b` | create 201 |
| mistake | `97a16659-937d-43c9-9718-3221373eb305` | convert 200 |
| review item | `32110a4c-a19e-49c1-a0ff-fa3487cfce77` | submit 200 |
| review record | 1 条 | list 200 |
| 样例结论 | pass | 主链路完整 |

## 样例三：tree-level-order

| 节点 | ID | 结果 |
| --- | --- | --- |
| question draft item | `4a46f835-289d-4450-bdd7-d96f01ed22b3` | create 201 |
| question | `92a5b851-adbe-4323-b177-6f151382c544` | convert 200 |
| mistake draft item | `d280141d-c42d-48d4-90b0-ae4c048fe234` | create 201 |
| mistake | `c78f227f-752a-40dd-a6f0-a3a9272dc643` | convert 200 |
| review item | `1587ea8a-14df-459e-8c58-20d8edb9da24` | submit 200 |
| review record | 1 条 | list 200 |
| 样例结论 | pass | 主链路完整 |

## 附件

| 节点 | ID / 结果 |
| --- | --- |
| source file | `assets/LT-20260704-review-note.txt`，无敏感信息 |
| attachment | `56eeb372-3db7-43c7-a570-8e72f02f31c8`，upload 201 |
| attachment link | `9367fef4-ea4a-46d0-9ce1-a6471981cf05`，link 201 |
| target | two-sum mistake `1e2b95b7-9116-46ae-b6e6-952b9227460b` |
| metadata / link refresh | 200 / 200，link count 1 |
| content read | 200，SHA-256 与源文件一致 |
| unauthenticated read | 401 |
| 附件结论 | pass |

## 数据库复核

| 对象 | `LT-20260704` 数量 |
| --- | --- |
| subjects | 1 |
| knowledge points | 3 |
| questions | 3 |
| mistakes | 3 |
| review records | 3 |
| attachments | 1 |
| attachment links | 1 |

## 公开边界

| 检查 | 结果 |
| --- | --- |
| `/blog`、`/notes`、`/mistakes` | 未登录页面可访问 |
| 公开页面管理员操作 | 可交互 DOM 未发现编辑、删除、AI、上传、复习提交入口 |
| 公开 blog/note/mistake API | 均为 200，`LT-20260704` 命中 0 |
| 私有附件未登录读取 | 401 |
| 管理 API 未登录 | 401 |

## 临时管理员清理

| 检查 | 结果 |
| --- | --- |
| 创建/轮换 | pass |
| 登录、`/api/auth/me`、管理 API | 200 |
| 临时凭据权限 | mode 600 |
| 禁用账号 | pass |
| 旧 cookie 会话 | 403 |
| 禁用后原密码登录 | 500，预期 401，`LT-ISSUE-002` |
| 凭据文件 / cookie jar 删除 | pass |

## 收口

- 核心 subject → question → mistake → review → attachment 主链路：**pass**。
- 私有与公开边界：**pass**。
- 临时管理员权限撤销：**pass**，但禁用后登录错误码不正确。
- 本次总体结论：**有条件通过**。
- MVP 主链路、附件链路和公开边界允许进入日常试用观察。
- 唯一条件项为 `LT-ISSUE-002`，后续进入 Auth Error Handling Cleanup。
- `LT-ISSUE-001` 不作为当前阻塞项，也不启动 localhost Passkey 专项。
