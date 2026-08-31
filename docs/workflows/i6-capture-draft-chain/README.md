# I6 采集到草稿深化链路

## 目标

在已完成的 I0–I5 基础上，收敛 I6 的最小可验收纵向链路：管理员上传私有单文件，Capture 经单图识别后进入可编辑草稿，草稿经过确认、拒绝或修正后才能幂等转换为类型化草稿；任何自动化失败都不能产生可读的正式学习对象，并保留来源、版本和操作证据。

## 当前状态

`COMPLETE / PASS / I6-VERIFIED (2026-07-24)`。I6-01 至 I6-08 已执行并完成验证；未执行源库/生产迁移、部署、推送或真实 AI 成功调用。

## 影响架构线与边界

- Personal learning backend：attachments、capture、question/mistake drafts、管理员权限和事务边界。
- 管理工作区前端：`/manage/capture`、`/manage/drafts` 及其 API client。
- 不涉及：文件夹树、移动/重命名/回收站、批量 OCR、真实 AI provider 成功调用、多用户/RBAC、公开读取、源库迁移、权威切换、部署和推送。

## 现状事实摘要

- 已有 `/api/admin/attachments`、`/api/admin/captures`、`/api/admin/drafts`，路由声明管理员依赖。
- 已有 `CaptureItem` 状态：`uploaded → recognizing → recognized → drafting → ready → converted`，并有 `failed/archived` 分支。
- 已有 `capture_service` 的人工修正、识别失败零污染、草稿失败零污染、Capture 到 Mistake Draft 的幂等转换。
- 已有服务层测试和部分前端 Capture/Draft 测试，但 I6 尚未形成一组完整的 HTTP、权限、审计和真实浏览器闭环证据。

## 主文档

- [audit.md](./audit.md)
- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [risk-register.md](./risk-register.md)
- [next-requirements.md](./next-requirements.md)
