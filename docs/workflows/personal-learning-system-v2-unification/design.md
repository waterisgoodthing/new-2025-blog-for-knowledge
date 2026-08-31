# 统一大方案设计边界

## 1. 统一原则

1. PostgreSQL 是正式业务数据唯一事实来源；GitHub Markdown 只负责导出、版本归档、公开构建输入和恢复副本。
2. `src/` 公开内容线与 `backend/` 个人学习线保持清晰边界，不为同一业务维护两套独立主数据。
3. 知识节点只拥有身份、别名、标签和关系；复习、掌握度、项目、发布和 AI 审核状态归属各自领域。
4. AI/OCR/Capture 输出必须先进入草稿和人工确认闸门。
5. 公开读取、管理员操作、私有学习数据和系统治理必须有独立 API 与页面边界。
6. 迁移、切换、删除和生产部署均采用 fail-closed 门槛。

## 1.1 当前事实与目标契约的分离

- `/api/public/**` 与 `/api/admin/**` 是目标 API 分层，不表示当前所有路由已经迁移到这些前缀。
- 既有公开 `GET /api/notes` 与 `GET /api/notes/{slug}` 的可见性规则是 `status=published` 且 `hidden=false`；目标中的 `public + published + 未删除` 不能在未定义兼容映射前直接替换它。
- 新公开资源必须先定义发布关系和兼容读模型；旧公开路由只能在契约测试、流量观察和明确退役日期齐全后停止服务。
- 当前代码、数据库和浏览器验证是现状证据；目标文档中的实体名称不能反向证明实体已经存在或已经完成迁移。

## 2. 目标产品结构

主导航控制在七项以内：

```text
今日 | 采集 | 学习 | 复习 | 知识库 | 项目 | 发布
```

全局入口：搜索、快速记录、命令面板、个人设置。

管理工作区不进入日常学习主导航，包含：AI 治理、草稿审核、附件、任务、迁移台账、系统健康和审计。

## 3. 统一领域边界

```text
今日工作台：只编排各领域摘要，不拥有业务写入逻辑
采集：原始文本、图片、PDF、网页摘录和临时附件
知识库：笔记、知识节点、关系、标签、WikiLink、反向链接
学习：科目、章节、题目、练习和作答
错题：具体错误、错因、预防规则和关联题目
复习：复习项、复习事件、调度和历史
内容发布：博客、公开快照、旧链接兼容
项目：学习项目和软件项目资料
治理：AI、人审、任务、审计、备份、迁移
```

文件工作区是跨域组织和附件访问能力，不取代上述领域实体。`workspace_nodes` 如实施，必须通过稳定资源引用连接业务对象，不能把所有业务状态塞进文件节点。

### 文件工作区最小状态机

首版以“资源引用 + 附件记录 + 显示路径”为边界，不创建第二套内容主数据：

```text
temporary_upload -> verified -> active -> trashed -> restored
                      |            |
                      v            v
                   rejected      missing
```

- 临时对象只可由创建者和后台任务访问；校验失败进入 `rejected`，不得生成可访问 URL。
- `verified` 表示 MIME、大小、哈希和存储写入均已验证；只有它可原子转为 `active` 并建立业务引用。
- 移动或重命名只更新显示路径/父节点，不改变稳定资源 ID；冲突采用显式拒绝或用户确认，不能静默覆盖。
- `trashed` 保留原始资源、路径、操作者、时间和审计事件；恢复必须检测目标冲突；物理清理需独立保留期与审批任务。
- `missing` 表示存储对象不可读但引用仍保留，必须提供恢复/重试路径，不能悄悄删除数据库记录。
- 公开发布是独立关系，不是附件或节点的默认属性；撤销发布立即撤销公开读取，而不删除私有对象。

## 4. 目标交付顺序

```text
Phase 0 术语、权限、数据源与恢复门槛
Phase 1 学习 MVP 纵向闭环
Phase 2 首页、导航与动态资料产品化
Phase 3 采集、附件与单文件 OCR
Phase 4 知识库和文件工作区基础
Phase 5 草稿审核、AI 治理与搜索
Phase 6 统计、报告、设置和项目协同
Phase 7 迁移 dry-run、影子迁移与切换准备
Phase 8 权威切换、观察期与 Legacy 归档
```

上一阶段未通过验收，不进入下一阶段。Phase 7/8 在 Migration Gate 解除前不得执行写入或切换。

## 5. MVP 与长期愿景分离

### MVP 必须交付

- Subject / Knowledge Point / Question
- Question Draft / Mistake Draft
- Question → Mistake → Review 的手工闭环
- 私有附件基础上传、关联和读取
- 公开内容与管理员工作区权限边界
- 今日摘要的最小只读聚合
- 可恢复的错误、空态、加载态和权限态

### 长期愿景

- 高密度可配置首页
- 动态个人资料与品牌配置
- 文件夹树、预览、回收站、版本和导入导出
- Markdown、WikiLink、反向链接、属性和搜索
- Capture/OCR/AI 人审闭环
- 学习统计、报告、知识图谱和扩展能力
- 旧系统全量迁移与 Legacy 归档

## 6. 明确不自动继承的内容

- 不把新方案中的示例数量、日期或迁移状态当作真实事实。
- 不把“接近 Obsidian Level 2”直接当作一个实施任务；必须拆成可验收能力。
- 不新增多用户、共享空间或 RBAC，除非另行批准权限模型。
- 不将 `/files` 默认视为公开路由；文件和附件默认私有，公开资源必须显式发布。
- 不在 Migration Gate `BLOCKED` 时执行迁移、删除、切换或旧系统停写。
# I2-R 管理端认证加载阻塞修复设计

## 问题

隔离浏览器环境中，匿名访问管理页获得预期的后端 `401`，但 `AuthGate` 长期停在“验证中…”。这阻断了 I2 的真实浏览器学习闭环验证。

根因已确认：临时 `2026` 开发服务与既有 `2025` 开发服务同时使用本工作区的 `.next` 输出目录，造成客户端产物互相覆盖。既有 `2025` 服务在单独运行时可正常水合并显示登录表单，故该现象不是认证 hook、后端接口或 CORS 的代码缺陷。

## 窄范围

- 影响架构线：Frontend / original blog，领域为 `manage` 与共享认证体验。
- 不修改 `src/hooks/use-admin-auth.ts`、`src/components/auth-gate.tsx` 或任何业务源文件；改以独立 Git worktree 取得独立 `.next` 输出目录。
- 保持后端 `get_current_admin`、Cookie、`AUTH_BYPASS` 语义和公开页面的权限边界不变。
- 不修改数据库、迁移、API 契约、生产配置或其他业务页面。

## 设计约束

1. 独立输出目录中，正常匿名 `401` 必须在有限时间内稳定归结为 `isLoading=false`、`isAdmin=false`，并跳转/呈现既有 `/manage` 登录入口。
2. 管理员正常密码会话必须继续进入受保护工作区；前端修复不替代后端权限校验。
3. 网络失败必须显示可理解、可恢复的状态，不得无限显示“验证中…”。
4. 验证必须使用新的隔离恢复环境和真实浏览器；不得使用 `AUTH_BYPASS` 或现有学习数据。

## 非目标

- 不修改认证代码、重构整套认证机制或引入状态库。
- 不将公开内容页面加入 `AuthGate`。
- 不在此任务修复与认证无关的水合、构建或 UI 问题。

# I3 Attempt、错题转换与采集手工回退设计

## 领域模型与状态

`Attempt` 是一次管理员作答的不可变学习事件，必须稳定关联一个正式 `Question`。最小字段为：`id`、`question_id`、`submitted_answer`、`is_correct`、`submitted_at`、`created_by`、`mistake_draft_item_id`（可空且唯一）。不保存可由题目版本快照推导的正式答案副本；本增量不实现多用户 owner 迁移。

错误 Attempt 的受控流程：

```text
Question → Attempt(is_correct=false) → Mistake Draft(pending) → confirm → Mistake + Review Item
```

- Attempt 写入和“生成错题草稿”均为管理员 API；转换必须幂等，一个 Attempt 最多一个 Mistake Draft。
- 作答正确时只记录 Attempt，不创建 Mistake Draft。
- Draft 仍是人工闸门：不得从 Attempt 直接写正式 Mistake 或 Review Item。
- 现有 Mistake Draft 保持对 Question / QuestionDraft 的兼容；新增 `attempt_id` 采用“恰好一个来源”的扩展约束。

Capture 使用既有 `capture_items` 与 `CaptureConvert`：管理页恢复现有工作区，上传与 AI/OCR 可失败；只要管理员手工补齐题干、科目、错误信息等转换字段，就可继续转为 Mistake Draft。AI/OCR 不得成为上传、保存或转换的前提。

## 允许范围

- Backend：Attempt model/schema/service/router、Mistake Draft 来源扩展、Alembic migration、相关单测。
- Frontend：Attempt API、Question detail 作答 UI、Draft 跳转、启用 Capture 现有 UI 与手工回退状态。
- 仅管理员私有学习路径：`/manage/questions/[id]`、`/manage/drafts`、`/manage/mistakes`、`/manage/review`、`/manage/capture`。

## 不做

- 不做多用户/RBAC、BKT、自适应出题、公开 Attempt/Mistake、批量 OCR、真实 AI 成功调用、迁移切换、部署或旧系统停写。

# I4 学习首页状态与统一导航收口设计

## 目标与边界

I4 只将已存在的学习管理首页和导航提升为可解释、可恢复的产品入口，覆盖 C-04、C-05。它不创建新的学习主数据，不引入资料偏好、OCR、文件工作区、迁移或部署。

当前 `/manage/dashboard` 依赖一个受保护的 `/api/admin/dashboard/summary` 聚合。整体请求失败时已有 loading/error/retry，但摘要中“今日任务、最近活动、附件存储”尚不能独立表达未知或失败；服务层还把 service/database 固定返回 `ok`，不能作为运行时健康结论。I4 要将这些状态表达为面向管理员的安全 UI 状态，不把内部错误、路径或私有对象泄露给匿名用户。

## I4 closure-fix 决策（2026-07-22）

I4 收口采用三个独立查询区块：`learning`、`activity`、`storage` 各自拥有 ready/unavailable/unknown/empty 契约；任一区块 SQL 异常只影响该区块，并在降级前 rollback。Dashboard 路由的全局 SQL fallback 仍保留，用于依赖级异常时的安全响应。真实 `get_db` 生命周期测试负责证明 commit、rollback、close 与异常后的后续查询恢复。此决策只完善 I4 的可解释性与恢复边界，不扩展到 I5 的资料、偏好或响应式产品能力。

## 设计原则

1. 管理员可见的首页保持一个学习行动入口，但数据块可以分别呈现 loading、empty、unavailable 或 ready；不可用区块不能遮挡复习、题目或其他已可用入口。
2. `DashboardSummary` 只报告本次查询实际已验证的事实；无法确认的系统或存储状态必须是 `unknown`/`unavailable`，不得以绿色“正常”替代。
3. `/manage/**` 继续由既有 `AuthGate` 与后端 `get_current_admin` 双层保护；失效会话只显示既有登录/恢复体验，不渲染缓存中的私有摘要。
4. `navGroups` 是学习管理的唯一导航配置。状态必须与实际交付一致：Capture 已激活；AI、任务、搜索、分析仍为显式后续能力。
5. 旧入口只允许保留、重定向到规范入口，或以明确的受保护提示退役；不复制页面、不引入第二套菜单。

## 不做

- 不做欢迎语、品牌、时区、资料或首页偏好设置（I5）。
- 不更改 Question、Attempt、Mistake、Review、Attachment 的领域模型或迁移。
- 不将 `/manage` 中任何模块开放给匿名用户，不移除后端管理员依赖。
- 不新增 analytics、jobs、search、AI 的主数据或虚假统计。
