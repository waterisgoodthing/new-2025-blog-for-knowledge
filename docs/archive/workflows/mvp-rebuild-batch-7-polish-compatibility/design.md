# 设计文档：Batch 7 体验收口、旧路由兼容、数据质量

## 1. 架构决定

Batch 7 采用“审计优先、小范围修复、证据收口”的方式：

```text
旧入口审计
  → 公开读取边界审计
  → 管理端状态 / 校验 / 确认小修
  → 链接与数据质量只读检查
  → 本地试运行说明
  → audit / validation / handoff
```

本批不引入新后端域、不新增表、不改变数据主模型，不把旧公开站重构为新系统。

## 2. 页面与路由设计

### 旧写作入口

候选路由：

- `/write-mistake`
- `/write-mistake/[slug]`
- `/write-note`
- `/write-note/[slug]`

设计原则：

- `/write-note` 保持可用，不强行破坏原博客/笔记流程。
- `/write-mistake` 可在任务获批后采用轻量迁移提示或跳转到管理工作区，但必须先审计当前实现。
- 动态编辑旧路由是否处理，必须按具体文件和风险在 tasks 中列明。
- 不创建复杂兼容层，不删除旧内容。

### 公开读取页面

候选路由：

- `/mistakes`
- `/notes`
- `/notes/[slug]`
- `/blog`
- `/blog/[slug]`

设计原则：

- 不加 `AuthGate`。
- 不展示编辑、删除、AI、上传、复习提交等管理操作。
- 不让管理员 API 的 401/403 变成公开页大面积错误。
- 如发现公开页调用管理员接口，优先改为登录态条件加载或优雅降级，但实现需等 tasks 获批。

### 管理端体验状态

候选页面：

- `/manage/dashboard`
- `/manage/drafts`
- `/manage/drafts/[id]`
- `/manage/questions`
- `/manage/questions/[id]`
- `/manage/mistakes`
- `/manage/mistakes/[id]`
- `/manage/review`
- `/manage/attachments`
- `/manage/attachments/[id]`
- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/ai`
- `/manage/jobs`
- `/manage/settings`

设计原则：

- 管理页面继续继承 `/manage/(workspace)` 的 `AuthGate`。
- empty/loading/error state 使用现有页面和组件风格，小修不抽象成新 framework。
- 对危险操作使用明确确认文案；不把“隐藏按钮”当作权限边界。

## 3. API 与数据设计

Batch 7 原则上不新增 API、不新增 migration、不新增 model。

允许的 API 相关工作仅限：

- 审计现有 frontend API client 是否与页面状态匹配。
- 修复小范围错误呈现或参数校验，但必须在 tasks 中列明。
- 验证公开页只使用 public API、管理页只使用 admin API。

数据质量检查只读进行，候选范围：

- subjects / chapters / knowledge_points
- question_drafts / questions
- mistake_drafts / mistakes
- review_items / review_records
- attachments / attachment_links
- legacy notes with `type = mistake`

检查目标：

- 必填字段空值或明显空白。
- 外键/关联缺失。
- 状态枚举异常。
- published/hidden 与公开读取边界是否一致。
- 附件记录是否泄露本地路径或存在孤儿关联。

任何自动修复、迁移、删除或合并都不属于本批默认实现。

## 4. 权限设计

- 公开页保持公开读取，不使用 `AuthGate`。
- 管理页保持页面级 `AuthGate`，后端写入/上传/复习等接口继续依赖管理员鉴权。
- 不依赖 `AUTH_BYPASS` 作为权限验收。
- 旧入口兼容不得绕过后端权限校验。

## 5. 异常与状态设计

状态收口采用四类最小状态：

- empty：无数据时解释原因和下一步。
- loading：加载中不闪现错误或空成功。
- error：显示可读错误，保留重试或返回路径。
- confirm：删除、归档、拒绝、解除关联等危险操作必须明确说明对象和后果。

## 6. 本地试运行设计

本地试运行说明应覆盖：

1. 安装依赖。
2. 配置 `.env.example` 与后端 `.env.example` 的必要项。
3. 数据库迁移。
4. 启动 FastAPI 与 Next.js。
5. 管理员登录或本地管理员初始化。
6. 试跑核心链路：
   - 科目 / 知识点
   - 草稿 → 题库
   - 错题 → 复习记录
   - 附件上传 / 关联
   - 公开读取页
7. 常见失败：API 连接失败、端口占用、未登录、数据库未迁移。

说明文档不得建议生产启用认证绕过，不包含云部署步骤。

## 7. 验证策略

实现获批后按触达范围选择：

- 静态搜索：公开/管理 API 边界、旧入口、死链、禁止能力关键字。
- TypeScript：`npx tsc --noEmit`。
- Build：`npm run build`。
- Backend：定向 pytest 或 FastAPI import/start check。
- Browser：匿名公开页、未登录管理页、登录态管理主链路。
- 数据质量：只读 SQL/API 检查并记录样本，不写入。

## 8. 暂缓与禁止

暂缓真实 AI/OCR、BKT、完整练习、对象存储、云部署、复杂迁移、公开站重做、复杂兼容层。

若审计中发现必须通过上述能力才能解决的问题，应记录为剩余风险或下一轮需求，不在 Batch 7
直接实现。
