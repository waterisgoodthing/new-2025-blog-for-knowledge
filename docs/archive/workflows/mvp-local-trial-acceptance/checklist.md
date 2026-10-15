# 本地试运行 Checklist

## 0. 范围与样例

- [x] 只执行 MVP 本地试运行，不新增功能。
- [x] 问题只记录，不自动修复。
- [x] 未修改业务代码、迁移、脚本、依赖、配置或部署。
- [x] 使用 two-sum、valid-parentheses、tree-level-order 三条人工题意转述。
- [x] 未抓取、未调用 LeetCode API、未复制原题全文。
- [x] 样例来源标注为 manual，仅用于本地试运行。
- [x] 准备无敏感信息附件 `assets/LT-20260704-review-note.txt`。

## 1. 环境与权限

- [x] PostgreSQL 可用，`/api/health` 返回 db ok。
- [x] Alembic 为 `014 (head)`。
- [x] 后端 8000、前端 2025 可访问。
- [x] `AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false`。
- [x] 未登录 `/manage` 显示登录入口。
- [x] 未登录管理 API 返回 401。
- [x] 临时管理员密码登录、`/api/auth/me` 和管理 API 返回 200。
- [x] 临时密码仅存于 mode 600 的 `/tmp` 文件，未写入仓库或报告。
- [x] 试跑结束后临时管理员已禁用，凭据文件和 cookie jar 已删除。
- [x] 旧临时会话在禁用后返回 403。
- [ ] 禁用后密码登录应返回 401；实际返回 500，见 `LT-ISSUE-002`。

## 2. Subject 与 Knowledge Point

- [x] 创建 `LT-20260704 Algorithms`，subject ID `135`。
- [x] 创建 Hash Table、Stack、Tree BFS 三个知识点，ID `21/22/23`。
- [x] subject 和 knowledge point 刷新读取返回 200。
- [x] 三个知识点均关联 subject `135`。

## 3. Question Draft → Question

- [x] 三条样例均创建 question draft，HTTP 201。
- [x] 草稿均关联 subject 与对应 knowledge point。
- [x] 题意均为人工转述并在说明中保留本地来源边界。
- [x] 三个草稿 convert 均返回 200。
- [x] 正式 questions 均为 private 且可读取。
- [x] question ID 已记录于 `trial-record.md`。

## 4. Mistake Draft → Mistake

- [x] 三条 questions 均创建 mistake draft，HTTP 201。
- [x] 每条均记录我的错误答案、错误原因和知识点。
- [x] 三个 mistake draft convert 均返回 200。
- [x] 正式 mistakes 均为 private 且可追溯 question。
- [x] mistake ID 已记录于 `trial-record.md`。

## 5. Review Item → Review Record

- [x] 三个 mistake 均自动产生 review item。
- [x] review item 均指向对应 mistake。
- [x] 三个 review item 均提交一次评分，HTTP 200。
- [x] 每个 review item 均可读取 1 条 review record。
- [x] review item / record ID 已记录于 `trial-record.md`。

## 6. Attachment Upload → Link → Read

- [x] 上传 `LT-20260704-review-note.txt`，HTTP 201。
- [x] attachment visibility 为 private。
- [x] 将附件关联到 two-sum mistake，HTTP 201。
- [x] 刷新读取 attachment metadata 和 link 均为 200。
- [x] 下载附件内容为 200，SHA-256 与源文件一致。
- [x] 未登录读取附件内容返回 401。

## 7. 公开边界

- [x] `/blog`、`/notes`、`/mistakes` 页面未登录可访问。
- [x] 三页可交互 DOM 未出现编辑、删除、AI、上传或复习提交入口。
- [x] 公开 blog、note、mistake API 均未出现 `LT-20260704`。
- [x] 私有附件未登录读取返回 401。
- [x] 管理 API 未登录仍返回 401。

## 8. 收尾

- [x] 三条样例均有对象 ID 和状态证据。
- [x] 所有失败项均进入 `issues.md`。
- [x] 剩余风险已进入 `risks.md` 和 `next-requirements.md`。
- [x] 没有自动修复发现的问题。
- [x] 本地样例数据保留供用户复核。
- [x] 最终结论为“有条件通过”，唯一条件项为 `LT-ISSUE-002`。
- [x] `LT-ISSUE-001` 已归档为非目标 localhost 环境兼容问题。
- [x] 当前阶段结束并进入日常使用观察，不启动新增专项。
