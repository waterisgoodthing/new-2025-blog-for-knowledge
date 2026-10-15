# 个人知识与博客系统 P0 验收记录

> 日期: 2026-06-02
> 关联文档: `docs/personal-knowledge-system-requirements.md`、`docs/personal-knowledge-system-tasks.md`

## 本轮目标

验证 P0 中已经明确的结构修复项：

1. taxonomy 后端路由是否注册。
2. 博客、笔记、错题的详情/编辑/删除落点是否按类型分流。
3. 写笔记页的分类和学科请求是否能命中后端。
4. 主要页面是否能正常打开，且没有明显 4xx/5xx 或控制台错误。

## 影响域

- `shared infrastructure`: 后端 router 注册、统一内容跳转 helper。
- `blog`: 博客发布、更新、删除后的落点。
- `notes`: 笔记创建、更新、详情、删除后的落点。
- `mistakes`: 错题创建和列表进入详情的临时落点。
- `manage`: 管理面板查看和编辑链接按内容类型分流。

## 已完成修复

### 后端 taxonomy 路由

`backend/main.py` 已注册：

- `subjects.router`
- `categories.router`

当前代码启动在 `http://127.0.0.1:8010` 后验证：

| 接口 | 结果 |
|---|---|
| `GET /api/categories` | `200`, 返回 `[]` |
| `GET /api/subjects` | `200`, 返回 `[]` |

说明：`localhost:8000` 上仍有旧后端进程时，这两个接口会返回 `404`。这属于环境进程未重启导致的误报，不是当前代码缺少 router。

### 内容跳转 helper

新增 `src/lib/content-routes.ts`，统一三类内容的落点规则：

| 内容类型 | 详情入口 | 编辑入口 | 列表入口 |
|---|---|---|---|
| `blog` | `/blog/{slug}` | `/write/{slug}` | `/blog` |
| `note` | `/notes/{slug}` | `/write-note/{slug}` | `/notes` |
| `mistake` | `/notes/{slug}` | `/write-note/{slug}` | `/mistakes` |

错题详情目前继续复用笔记详情页，这是临时策略；如果后续要突出题目、答案、解析和复习计划，应在 P1 或 P0 延伸任务中新增 `/mistakes/{slug}`。

### 页面落点修复

已接入统一跳转规则的位置：

- `src/app/manage/page.tsx`
- `src/app/notes/[id]/note-detail-content.tsx`
- `src/app/write-note/page.tsx`
- `src/app/write-note/[slug]/page.tsx`
- `src/app/write-mistake/page.tsx`
- `src/app/write/hooks/use-publish.ts`

当前行为：

| 操作 | 落点 |
|---|---|
| 新建普通笔记 | `/notes/{slug}` |
| 编辑普通笔记 | `/notes/{slug}` |
| 新建错题 | `/notes/{slug}` |
| 删除错题/笔记详情 | 按类型回到 `/mistakes` 或 `/notes` |
| 新建/更新博客 | `/blog/{slug}` |
| 删除博客 | `/blog` |
| 管理面板查看博客 | `/blog/{slug}` |
| 管理面板编辑博客 | `/write/{slug}` |
| 管理面板查看笔记/错题 | `/notes/{slug}` |
| 管理面板编辑笔记/错题 | `/write-note/{slug}` |

### 模板可见化入口

`src/app/write-note/components/note-templates.tsx` 已改造为可见模板面板：

| 模板 | 用途 |
|---|---|
| 课堂笔记 | 整理课堂概念、例题、疑问和课后复盘 |
| 错题解析 | 拆解题目、错误原因、正确思路和复习建议 |
| 读书笔记 | 记录书籍观点、摘录、自己的理解和可迁移结论 |
| 项目复盘 | 复盘目标、决策、结果、风险和下一步动作 |

`/` 指令继续保留为高级快捷方式，但用户不需要输入 `/` 就能插入常用模板。

### 按钮可理解性

已补充高频按钮的 accessible name：

- 写作工具栏图标按钮。
- 模板入口按钮。
- 错题图片删除按钮。
- 标签删除按钮。

模板入口保留“模板”文字，不再只是图标。

## 可视化验收

本轮使用当前代码启动：

- 后端: `http://127.0.0.1:8010`
- 前端: `http://localhost:3000`
- 前端环境: `NEXT_PUBLIC_API_URL=http://localhost:8010`

浏览器检查结果：

| 页面 | HTTP 状态 | 控制台错误 | 4xx/5xx 请求 | 观察 |
|---|---:|---|---|---|
| `/` | 200 | 无 | 无 | 首页正常展示推荐、日历、导航 |
| `/blog` | 200 | 无 | 无 | 当前无文章，展示空状态 |
| `/notes` | 200 | 无 | 无 | 笔记、博客、错题筛选与列表正常 |
| `/mistakes` | 200 | 无 | 无 | 错题统计、开始复习、添加错题入口正常 |
| `/manage` | 200 | 无 | 无 | 未登录状态展示管理面板登录表单 |
| `/write-note` | 200 | 无 | 无 | 模板、分类、发布、取消入口正常 |

模板面板专项检查：

| 项目 | 结果 |
|---|---|
| 模板按钮 accessible name | `打开笔记模板面板` |
| 模板菜单 role/name | `menu` / `笔记模板` |
| 模板项数量 | 4 |
| 模板项内容 | 课堂笔记、错题解析、读书笔记、项目复盘均显示名称和用途说明 |
| 写笔记页控制台错误 | 无 |
| 写笔记页 4xx/5xx 请求 | 无 |
| 移动端 390px 模板面板 | 可打开，弹层已限制在视口内 |

链接抽样结果：

- `/notes` 的普通笔记进入 `/notes/{slug}`。
- `/mistakes` 的错题进入 `/notes/{slug}`，符合当前临时复用策略。
- `/mistakes` 的复习入口进入 `/mistakes/review`。
- `/mistakes` 的添加入口进入 `/write-mistake`。
- `/write-note` 提供返回首页入口。

## 代码验证

| 命令 | 结果 |
|---|---|
| `git diff --check` | 通过 |
| `npx tsc --noEmit` | 通过 |
| `npm run build` | 通过 |
| 后端 import/start check | 通过 |

构建期间仍有两个非阻塞提示：

- `baseline-browser-mapping` 数据较旧。
- Node.js 输出 `DEP0205` deprecation warning。

这两个提示不影响本轮 P0 验收。

## 剩余问题

1. 错题详情仍复用 `/notes/{slug}`，无法突出错题专属结构。建议在 P1 错题 AI 与复习规划阶段决定是否新增 `/mistakes/{slug}`。
2. 管理面板需要登录才能验证已登录后的真实列表链接；本轮已从源码和未登录页面验证分流逻辑，但未执行登录态端到端操作。
3. 当前工作树存在多处本轮之前已经脏的文件，本轮结论只覆盖上述 P0 跳转、taxonomy 和文档改动。
4. `localhost:8000` 如果继续运行旧后端，会导致写笔记页分类/学科接口 404；开发验收时需要重启后端或显式指向当前代码启动的后端端口。
5. 危险操作的统一红色弱背景和批量删除影响文案仍未完全覆盖，建议在管理面板登录态验收时一并补齐。

## 下一步建议

优先进入 P1：

1. 扩展错题 AI 输出结构，让解析、知识点、易错原因和训练建议更完整。
2. 设计清晰的复习规划卡片，包括今日、未来 7 天、薄弱知识点和复习节奏。
3. 决定错题详情页是否从 `/notes/{slug}` 独立为 `/mistakes/{slug}`。
