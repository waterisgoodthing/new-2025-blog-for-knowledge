# MVP 本地试运行验收报告

## 最终结论

**有条件通过：核心主链路、附件链路和公开边界均已通过真实私有样例验证，可以进入日常试用观察。唯一条件项为 LT-ISSUE-002。**

本轮可以确认 MVP 的以下本地私有链路具备真实数据闭环：

```text
subject
→ knowledge point
→ question draft
→ question
→ mistake draft
→ mistake
→ review item
→ review record
→ attachment upload
→ attachment link
→ attachment read
```

## 范围与约束

- 使用 3 条少量 LeetCode 相关练习的人工题意转述。
- 样例只进入本地私有新模型，不进入公开 notes/blog/mistakes。
- 使用既有临时管理员 CLI，不修改认证或业务代码。
- 不使用 AUTH_BYPASS。
- 问题只写入 issues/risks/next requirements，不自动修复。

## 环境

| 项目 | 结果 |
| --- | --- |
| 日期 / 时区 | 2026-07-04 / Asia/Shanghai |
| 分支 / commit | `notes-workspace-ux-upgrade` / `97626d21cf2505a46a641ed5f14b5853ccd42914` |
| 前端 | localhost:2025，200 |
| 后端 | 127.0.0.1:8000，health 200，db ok |
| 数据库 | PostgreSQL localhost/blog_db |
| 迁移 | `014 (head)` |
| AUTH_BYPASS | false / false |

## 分项结果

| 验收项 | 结果 | 证据摘要 |
| --- | --- | --- |
| 环境健康 | pass | 前后端 200、db ok、迁移 head |
| 未登录管理保护 | pass | subjects/drafts/review/attachments 均 401 |
| 临时管理员登录 | pass | login、me、管理 API 均 200 |
| subject / knowledge point | pass | 1 个 subject、3 个知识点，刷新 200 |
| question draft / question | pass | 3 次 create 201、3 次 convert 200 |
| mistake draft / mistake | pass | 3 次 create 201、3 次 convert 200 |
| review item / record | pass | 3 次 submit 200、每项 1 条 record |
| attachment upload | pass | 201，private |
| attachment link | pass | 201，刷新 link count 1 |
| attachment read | pass | 200，SHA-256 一致 |
| attachment 未登录保护 | pass | 401 |
| 公开 API 无 LT 样例 | pass | blog/note/mistake 均 0 命中 |
| 公开页面无管理操作 | pass | 未登录 DOM 未发现编辑、删除、AI、上传或复习提交入口 |
| 临时管理员禁用 | pass | CLI 成功；旧会话 403 |
| 禁用后密码登录 | fail | 返回 500，预期 401；LT-ISSUE-002 |
| 临时凭据清理 | pass | mode 600；完成后文件与 cookie jar 删除 |

## 数据与对象

- subject：`135`
- knowledge points：`21/22/23`
- questions：3
- mistakes：3
- review records：3
- attachment：`56eeb372-3db7-43c7-a570-8e72f02f31c8`
- attachment link：`9367fef4-ea4a-46d0-9ce1-a6471981cf05`

完整对象 ID 见 `trial-record.md`。

## 已确认问题

### LT-ISSUE-001

本地 Passkey 的 RP/Origin 与 localhost 不匹配。由于后续不再以 localhost 作为主要访问环境，该项降级为非目标环境兼容问题，归档且不作为当前阻塞项；不启动 localhost Passkey 专项。

### LT-ISSUE-002

临时管理员禁用后，以原密码登录返回 500。账号权限已撤销，旧会话为 403，因此不阻塞本轮业务主链路，但认证失败处理不符合预期。

## 变更审计

本轮只产生：

- 本地数据库中的私有试跑样例。
- 本地上传目录中的私有测试附件。
- `docs/workflows/mvp-local-trial-acceptance/` 下的验收记录。

本轮没有修改业务代码、后端代码、迁移、脚本、导入器、依赖、配置或部署文件。

## 闭环判断

- 对“本地 MVP 主链路是否可运行”：**是，已用 3 条真实私有样例验证通过。**
- 对“MVP 主业务链路、附件链路和公开边界是否可用”：**是，真实私有样例验收通过。**
- 对“MVP Rebuild 本轮是否允许结束”：**是，有条件通过并进入日常使用观察。**
- 唯一条件项：**LT-ISSUE-002**，后续进入独立的 Auth Error Handling Cleanup。
- 明确不进入：localhost Passkey 专项、AI、OCR、BKT、完整练习、对象存储、云部署。

## P0-16/P0-17 公开错题兼容修复复验

- 根因：`next.config.ts` 的 `/mistakes` → `/manage/mistakes` redirect 覆盖了公开错题页。
- 修复：删除该单条 redirect；保留 `/mistakes/review` → `/manage/review` 私有重定向。
- 测试：修复前回归测试 1 failed；修复后 Batch 7 route contract 4 passed，full frontend 26 passed。
- 构建：TypeScript 通过，`npm run build` 通过。
- 浏览器：匿名 `/mistakes` 保持原 URL 并加载公开错题列表；`/mistakes/review` 仍进入 `/manage` 登录保护；`/blog`、`/notes` 正常。
- 数据：未执行数据库写入、migration、数据迁移或部署；counts 与 revision 未变化。
- 结论：`DEMO-ISSUE-001` fixed-in-separate-workflow；项目验收恢复为 conditional pass，剩余 `LT-ISSUE-002`。

## P0-18/P0-19 Auth Error Handling Cleanup

- 根因：临时管理员禁用时将 `password_hash` 设为 `disabled`；bcrypt 校验 malformed hash 抛 `ValueError`，导致登录接口 500。
- 修复文件：`backend/app/utils/auth.py`；`verify_password()` 将 `TypeError` / `ValueError` 转换为 `False`。
- 新增测试：`backend/tests/test_auth_error_handling.py`，覆盖 malformed/disabled hash 和 login 401 契约。
- 定向认证/权限回归：`17 passed`。
- 全量后端测试：`244 passed`，2 个既有 AI gateway RuntimeWarning，不影响本次修复。
- Import check：177 routes。
- 数据库：`020 (head)`；counts 保持 `notes=13`、`subjects=1`、`knowledge_points=3`、`questions=3`、`mistakes=3`、`review_items=3`、`review_records=4`、`attachments=1`、`attachment_links=1`。
- 未执行 migration、数据迁移、数据写入、AUTH_BYPASS 或部署。
- 结论：`LT-ISSUE-002` fixed-in-separate-workflow 并关闭；MVP 第一阶段验收结论更新为 **pass**。
