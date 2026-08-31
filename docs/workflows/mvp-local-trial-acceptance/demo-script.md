# MVP 第一阶段演示脚本

## 演示目标

在 10–15 分钟内证明：公开内容可读、管理入口受保护、核心学习闭环已完成真实本地验收、附件边界有效，并且当前结论是有条件通过而非无条件全量通过。

默认模式：只读演示，使用已经记录的本地验收对象；不新增数据、不修改数据、不调用 AI/OCR/Capture、不开云部署。

## 演示前检查

- [ ] 用户明确批准现场演示范围。
- [ ] 确认前端和后端地址：`http://localhost:2025`、`http://127.0.0.1:8000`。
- [ ] 确认是否需要管理员会话；不展示密码或 token。
- [ ] 确认数据库仍为 `020 (head)`；只读展示。
- [ ] 打开浏览器开发者工具的 Network/Console 面板，用于观察 401/403、外部调用和明显错误。
- [ ] 准备异常回退：服务不可用时展示已保存的 validation/trial-record 证据，不现场修复。

## 1. Public Read（约 2 分钟）

访问：`/`、`/blog`、`/notes`、`/mistakes`，再打开一个公开详情页。

讲解重点：

- 匿名用户可以读取公开内容。
- 页面不显示编辑、删除、AI、上传和复习提交入口。
- 错题公开页只展示允许公开的内容；管理操作入口需要管理员状态。

观察证据：页面正常渲染；Network 中不出现 admin review、admin attachment、AI 或 Capture 请求。

失败恢复：若出现 401/403 或管理请求噪音，停止现场深入操作，记录页面、请求和时间，不临时改代码。

## 2. Private Manage（约 2 分钟）

先访问 `/manage`，展示未登录访问保护；在已有授权会话下进入 `/manage/dashboard`、`/manage/questions`、`/manage/mistakes`、`/manage/review`、`/manage/attachments`。

讲解重点：

- 管理工作区由 AuthGate 保护。
- 后端 `get_current_admin` 是真实安全边界，前端隐藏按钮不是唯一保护。
- `/write-note*` 和 `/write-mistake*` 旧入口仍保留，当前主流程使用 `/manage/**`。

## 3. Core Learning Loop（约 5 分钟）

使用既有验收记录中的对象，不进行现场写入：

- Subject `135`。
- Knowledge points `21/22/23`。
- Questions：见 [trial-record.md](./trial-record.md)。
- Mistakes：见 [trial-record.md](./trial-record.md)。
- Review items/records：展示已完成的 review 状态。

演示顺序：

1. 从 subject/knowledge point 说明分类关系。
2. 展示 question 已由 draft 转为正式对象。
3. 展示 mistake 与 question 的追溯关系。
4. 展示 review item 和已写入的 review record。
5. 说明公开页面与私有管理数据的边界。

若必须现场操作：先暂停演示并获得额外批准；只能使用本地私有样例，操作后记录新增 ID 和数据库变化。

## 4. Attachment and Closure Evidence（约 3 分钟）

展示 attachment `56eeb372-3db7-43c7-a570-8e72f02f31c8` 与 link `9367fef4-ea4a-46d0-9ce1-a6471981cf05` 的既有验证记录。

讲解重点：

- 附件完成 upload → link → read。
- 附件为 private，未授权读取被拒绝。
- 数据库 revision 为 `020 (head)`，Batch 7 没有 migration 或数据迁移。
- 当前结论为 conditional pass，`LT-ISSUE-002` 仍是条件项。

## 收尾话术

“MVP 第一阶段核心链路已通过真实本地私有样例验证，公共读取和私有权限边界符合预期。当前结论是有条件通过，剩余认证错误处理问题单独记录，不在本次演示中修复。下一步可在验收确认后进入部署准备或重新规划下一阶段需求。”

## 演示后记录

- [ ] 记录实际访问页面和时间。
- [ ] 记录截图/录屏路径（如有）。
- [ ] 记录 Console/Network 是否有异常。
- [ ] 记录未完成项和条件项，不把演示结果写成全量生产验收。
- [ ] 不自动启动 Batch 8 或部署流程。
