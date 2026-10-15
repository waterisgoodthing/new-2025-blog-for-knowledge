# I6 设计

## 1. 纵向链路

```text
管理员登录
  → 私有 Attachment 上传并验证
  → CaptureItem(uploaded)
  → 单图识别
     ├─ recognized → 草稿生成 → ready
     └─ failed     → 安全错误 / 重试 / 人工修正
  → 类型化 DraftItem
     ├─ 编辑并递增 version
     ├─ reject → rejected（终止）
     └─ confirm → 幂等转换 → 正式 Question/Mistake
```

Capture 只承载过程状态和候选输出；DraftItem 是人工闸门；正式 Question/Mistake/ReviewItem 仍由既有领域服务负责。

## 2. 后端边界

- `routers/attachments.py`、`routers/captures.py`、`routers/drafts.py` 只负责身份依赖、请求 DTO、状态码和薄编排。
- `attachment_service` 负责私有文件验证、存储键、内容读取和清理。
- `capture_service` 负责 Capture 状态转换、失败隔离和 Capture → Draft 的幂等协调。
- `capture_recognition` 与 `capture_ai_draft` 继续作为窄 adapter；测试用 fake，不将 provider 配置传播到路由。
- `draft_service` 负责类型化草稿的版本、字段校验、拒绝和正式转换。

## 3. API 验证矩阵

| 方法 | 路径 | 权限 | 关注点 |
|---|---|---|---|
| POST | `/api/admin/attachments` | admin | 流式私有上传、非法文件、清理 |
| POST | `/api/admin/captures` | admin | 只接受 active image attachment |
| POST | `/api/admin/captures/{id}/recognize` | admin | 状态、失败码、无正式对象污染 |
| POST | `/api/admin/captures/{id}/draft` | admin | fake 成功、空输入、provider/schema 失败 |
| PATCH | `/api/admin/captures/{id}` | admin | 人工覆盖和 failed → ready |
| GET/PUT | `/api/admin/drafts/{id}` | admin | 版本校验、字段与来源保留 |
| POST | `/api/admin/drafts/{id}/reject` | admin | rejected 后不可转换 |
| POST | `/api/admin/drafts/{id}/convert` | admin | 人工确认、幂等目标和重复请求 |

匿名/失效会话对上述私有路径统一保持 401；公开读取链不受影响。

## 4. 数据与审计

优先复用现有字段：Attachment 的 `storage_key/status/visibility/checksum`，Capture 的 `source_attachment_id/status/last_stage/attempt_count/error_*`，DraftItem 的 `source_type/source_id/status/version/validation_errors/target_*`，以及 `created_by/created_at/updated_at`。执行前必须用 022 目标确认这些字段和约束真实存在。

若验收发现某项审计证据无法由现有字段重建，先增加一个最小需求和迁移任务，再停止等待额外批准；不得在实现中顺手引入通用 audit 大表。

## 5. 异常与事务

- 文件写入未完成或校验失败：不创建 active Attachment；临时文件可清理。
- 识别/草稿 adapter 失败：只更新 Capture 的安全失败字段；不创建正式对象。
- 转换失败：事务回滚；Capture 不得标记 converted。
- 重复转换：锁定目标草稿并返回已有 target；版本不匹配返回 409。
- 所有 dependency 测试在同一事件循环完成资源释放，避免 I4/I5 已修复的 asyncpg 跨 loop 回归。

## 6. 页面与浏览器验收

`/manage/capture` 保留现有图片、手工录入和错题入口，补齐真实状态文本、失败重试、人工修正和转换后回到草稿审核的连续路径。`/manage/drafts/[id]` 需要显示来源、版本、状态、修正、拒绝和确认动作；所有图标按钮有可访问名称，移动端不禁用缩放。
