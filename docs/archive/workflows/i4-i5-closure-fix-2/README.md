# I4-I5 closure-fix-2

## 目标

收口 I4 Dashboard 与 I5 首页偏好之间的最后一组契约缺口：Dashboard 按 `section_order` 排序并应用 `hidden_sections`，前后端共同保证至少保留一个学习行动区块，统一 `empty` 与系统健康状态的语义，并补齐后端局部失败/事务生命周期与偏好刷新生效测试，重新采集隐藏/排序实际生效的浏览器证据。

## 影响架构线与边界

- Frontend / original blog：不涉及。
- Personal learning backend：Dashboard、管理员 profile/preferences API、定向测试。
- 管理工作区前端：`/manage/dashboard`、`/manage/settings`、Dashboard API 类型与测试。
- 不涉及：新模型、迁移、源库写入、生产部署、真实 AI 调用、公开读取页面权限调整。

## 当前状态

`COMPLETE / PASS / FINAL-FIX-VERIFIED (2026-07-24)`。实现与最终收口证据已完成；详细的事件循环隔离、独立故障矩阵、022 目标和浏览器限制见 [i4-i5-closure-final-fix](../i4-i5-closure-final-fix/README.md)。当前工作树中的其他 I4/I5 修改保留，未回滚。

## 文件

- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [audit.md](./audit.md)
