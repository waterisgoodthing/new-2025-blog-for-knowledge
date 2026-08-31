# 前端结构规范

> 目标结构，待实现。现有路由在迁移期按兼容旧系统保留。

相关文档：[功能域](./domains.md)、[路由](./routes.md)、[API](./api-design.md)、[权限](./permissions.md)、[技术栈](./tech-stack.md)、[渲染系统](./rendering-system.md)。

## 1. 前端分层原则

前端按“路由组合、业务功能、跨域组件、基础能力、通用 Hook”分层。公开端与管理端可以复用无权限含义的展示组件，但不能共享错误的数据契约或让公开页面请求 admin API。

## 2. 目标目录结构

```text
src/
├── app/
│   ├── blog/
│   ├── notes/
│   ├── mistakes/
│   ├── manage/
│   ├── write-note/          # 旧路由，后续兼容或重定向
│   └── write-mistake/       # 旧路由，后续兼容或重定向
├── features/
│   ├── posts/
│   ├── notes/
│   ├── questions/
│   ├── practice/
│   ├── mistakes/
│   ├── review/
│   ├── ai/
│   ├── attachments/
│   └── taxonomy/
├── components/
│   ├── rich-text/
│   ├── icons/
│   └── ...
├── lib/
│   ├── api/
│   ├── rendering/
│   └── ...
└── hooks/
```

管理端目标功能还应覆盖 `subjects`、`taxonomy`、`capture`、`ocr`、`drafts`、`jobs`、`search`、`analytics`、`reports` 和 `settings`。页面只负责组合；数据访问统一经过 `src/lib/api/admin/*`，不得从公开页面探测 admin API 再依赖 401 降级。

公开首页与 `/manage/**` 使用不同信息密度：前者保持浅蓝绿色、青春感、低密度玻璃卡片与轻量入口；后者作为高密度学习工作台。完整原则见 [UI 重构方向](./ui-redesign.md)。

这是目标结构，不表示本轮创建这些代码目录。

## 3. app/ 路由层职责

`app/` 只放 route segment、layout、loading/error/not-found、页面壳和页面级组合。它负责读取路由参数、选择 public/admin 数据入口并组合功能模块，不承载可复用业务规则、直接拼装 HTTP 请求或复制渲染管线。

## 4. features/ 业务功能层职责

每个 feature 可包含域组件、业务 hooks、业务类型、表单状态、映射器和局部工具，但不得拥有跨域基础设施。

- `features/posts`：文章列表、详情、编辑和发布交互；不处理 Note/Mistake 字段。
- `features/notes`：知识笔记读取、编辑和关联；不承载错题答案或复习算法状态。
- `features/questions`：题库列表、题目详情、题目选择器和题目来源展示；不记录练习行为、错题复盘或复习队列。
- `features/practice`：练习记录列表、练习导入、练习详情、作答展示、练习报告和从练习生成错题草稿；不编辑正式错题、不实现复习算法或 AI 底层调用。
- `features/mistakes`：单题错题导入、错题列表、详情、编辑和错题草稿确认；不承载多题练习导入、完整练习记录、做对题目的保存或调度算法。
- `features/review`：队列、评分、记录和统计；只引用可复习实体，不复制其正文所有权。
- `features/ai`：AI Run 创建、状态、结果确认与重试；不直接决定内容发布或保存。
- `features/attachments`：上传、选择、关联和附件状态；不解释业务正文。
- `features/taxonomy`：标签、学科、知识点及关系选择；不保存内容实体。

跨 feature 编排应在明确的页面组合或应用服务边界完成，不通过相互深层 import 形成隐式耦合。

## 5. components/ 通用组件层职责

`components/` 放两个及以上业务域可复用且不拥有业务数据的组件，例如 `RichText`、`AppIcon`、对话框、表单原语和空状态。组件通过明确 props 工作，不直接选择业务 API，也不根据 URL 猜测权限。

## 6. lib/ 基础能力层职责

`lib/api/` 放 typed API client、DTO 和统一错误处理，明确拆分 public/admin 客户端。`lib/rendering/` 放 Markdown 管线、净化 schema、代码高亮和块识别。其他 `lib/` 模块只放框架无关或跨域基础工具，不放 React 页面组件。

数据流保持：`page/component -> feature hook 或 action -> src/lib/api/* -> backend API`。

## 7. hooks/ 通用 Hook 层职责

`hooks/` 只放跨功能域通用 Hook，例如媒体查询、会话读取或可访问性交互。只服务单一业务域的 Hook 留在对应 feature。Hook 不应绕过 API client、隐藏管理员写操作或建立第二份远端数据事实。

## 8. 管理端与公开端边界

- `/blog/**`、`/notes/**`、`/mistakes/**` 只消费 public API。
- `/manage/**` 在页面级使用 `AuthGate`，并只消费 admin API；Question 与 Practice 页面同样适用。
- public DTO 不含草稿、内部 AI、复习、审计或存储字段。
- 管理组件不能因被隐藏就假设后端无需鉴权。
- 公开与管理预览可共享 `RichText`，但必须显式传入不同 mode。

## 9. 旧路由兼容策略

目标映射为：

| 旧路由 | 目标路由 |
|---|---|
| `/write-note` | `/manage/notes/new` |
| `/write-note/[slug]` | `/manage/notes/[slug]/edit` |
| `/write-mistake` | `/manage/mistakes/new` |
| `/write-mistake/[slug]` | `/manage/mistakes/[slug]/edit` |
| `/manage/mistakes/import`（若存在） | `/manage/practice/import` |

迁移时先建立目标路由并验收，再以兼容重定向保留旧入口，观察旧流量后删除。**本轮只记录策略，不修改路由。**

## 10. 禁止事项

- 不在 `app/` 页面中堆积 API、领域规则或复杂渲染逻辑。
- 不让 feature 相互读取内部文件形成循环依赖。
- 不把只用一次的业务组件伪装成全局组件。
- 不在组件中直接请求已有 API wrapper 可覆盖的端点。
- 不让公开页面请求 admin API 后依靠 401/403 降级。
- 不用 `any` 或 JSON 推断掩盖 public/admin 契约差异。
