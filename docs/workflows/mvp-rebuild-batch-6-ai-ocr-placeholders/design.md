# 设计文档：Batch 6 AI / OCR 占位与依赖隔离

## 1. 架构决定

采用“前端静态占位 + 主流程依赖审计”的方式：

```text
/manage/ai        → 静态 AI 控制台占位
/manage/jobs      → 静态任务观察占位
/manage/settings  → 静态设置占位
/manage/attachments/[id] → OCR 未启用状态卡片
```

本批不创建真实 AI/OCR/Job 后端合同，不新增表，不复用旧真实 AI 入口作为新 MVP 能力。已有历史
AI 代码只作为既有系统存在，Batch 6 不扩大它的访问面。

## 2. 页面设计

### `/manage/ai`

展示三块静态结构：

- 模型配置占位：说明未来会管理模型、能力、成本、延迟和可用性。
- Prompt 模板占位：说明未来会有版本化 prompt，但第一版暂未启用。
- 调用记录占位：说明未来会展示 run ID、状态、错误和审计信息；当前不显示虚构记录。

所有操作按钮使用禁用态或纯说明，不发请求。

### `/manage/jobs`

展示未来任务队列结构：

- 队列状态占位。
- 任务类型占位：OCR、Capture、AI、附件处理。
- 重试与错误观察占位。

不得创建 job API、轮询或 mock 成功状态。

### `/manage/settings`

展示设置分类占位：

- AI
- OCR
- Upload
- Jobs
- Privacy

只说明未来设置归属，不提供真实保存按钮或假保存 toast。

### `/manage/attachments/[id]`

在附件详情页添加 OCR 状态区域：

- 标题清楚显示“OCR 第一版暂未启用”。
- 说明当前附件可作为未来 OCR 输入，但不会自动识别。
- 不显示“开始 OCR”按钮，不请求 OCR API。

## 3. 导航

在 `ManageSidebar` 增加 AI、任务、设置入口。若 dashboard 需要展示 Batch 6 入口，只显示“占位 /
暂未启用”，不显示虚构数据。

## 4. 依赖审计

对以下范围做静态检查：

- `src/app/manage/(workspace)/(drafts|questions|mistakes|review|attachments)`
- `src/lib/api`
- `backend/app/routers`

目标：

- 确认 Batch 3-5 主流程未新增 AI/OCR 请求依赖。
- 确认 Batch 6 页面没有调用 `src/lib/api/ai*`、OCR、capture 或 jobs API。
- 确认没有新增 AI/OCR migration/model/router/service。

## 5. 权限与安全

- Batch 6 页面必须在 `/manage/(workspace)` 下，继承 AuthGate。
- 公开页面不得新增 AI/OCR 操作入口。
- 未登录用户不得看到或触发 AI/OCR 管理操作。
- 不依赖 `AUTH_BYPASS` 作为权限验收。

## 6. 验证策略

- TypeScript：`npx tsc --noEmit`。
- Build：`npm run build`。
- 静态搜索：检查无新增 AI/OCR/job 后端合同、无新迁移、无前端真实调用。
- 浏览器：访问 `/manage/ai`、`/manage/jobs`、`/manage/settings`、附件详情页，确认占位文案清晰且 console/network 无异常。

## 7. 暂缓

真实模型调用、OCR、Capture Router、多模型路由、Prompt 保存、调用记录持久化、任务队列、worker、
轮询、重试、成本统计、AI 设置保存。
