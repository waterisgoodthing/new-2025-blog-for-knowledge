# Tasks：Route Cutover Sprint

> 状态：**实施完成**。D-0=方案 B，P0-01~P0-10 全部完成并通过验证，P0-11 收口文档已完成。
> 关联：[requirements.md](./requirements.md) | [design.md](./design.md) | [checklist.md](./checklist.md)
> 规则：`[ ]` 待办 / `[x]` 完成；被阻塞或跳过项需注明原因。

## 前置决策（必须先确认）

- [x] **D-0** `/mistakes` 公开策略：**方案 B**（关闭公开错题入口）。用户已确认。

## P0-01 路由与 Link 引用扫描

目标：找出所有旧路由入口和新旧混杂入口。

扫描范围：`src/**`、`docs/**`。

重点命令（实施时执行）：

```bash
rg "write-note|write-mistake|mistakes/review|manage/capture|manage/mistakes" src docs
rg "href=.*write|router.push.*write|Link.*write" src
```

已知命中（初始清单，实施时复核）：

| 路由 / 引用 | 出现文件 | 入口类型 | 用户可见 | 应保留 | 处理策略 |
| --- | --- | --- | --- | --- | --- |
| `/write-note` | `src/app/manage/page.tsx` | 写作入口 | 是 | 否 | 改为 `/manage/dashboard` 或移除 |
| `/write-mistake` | `src/app/manage/page.tsx` | 写作入口 | 是 | 否 | 改为 `/manage/capture` |
| `/write-mistake` | `src/app/mistakes/page.tsx` | 写作入口 | 是 | 否 | 改为 `/manage/capture` 或隐藏 |
| `/mistakes/review` | `src/app/mistakes/page.tsx` | 复习入口 | 是 | 否 | 改为 `/manage/review` |
| `/write-mistake` | `src/app/mistakes/review/page.tsx` | 写作入口 | 是 | 否 | 改为 `/manage/capture` |
| `/write-mistake?ai_prefill=1` | `src/app/mistakes/components/weak-point-diagnosis.tsx` | AI 预填入口 | 是(管理员) | 否 | 改为 `/manage/capture` 流程 |
| `/write-note?ai_prefill=1` | `src/app/mistakes/components/weak-point-diagnosis.tsx` | AI 预填入口 | 是(管理员) | 否 | 改为 `/manage/drafts` 或移除 |
| `/mistakes/review` | `src/app/mistakes/components/weak-point-diagnosis.tsx` | 复习入口 | 是 | 否 | 改为 `/manage/review` |
| `/write-note` | `src/app/notes/page.tsx` | 写作入口 | 是(管理员) | 否 | 改为 `/manage/dashboard` 或移除 |
| `/write-mistake` | `src/app/notes/page.tsx` | 写作入口 | 是(管理员) | 否 | 改为 `/manage/capture` 或移除 |
| `/mistakes/review` | `src/app/notes/[id]/note-detail-content.tsx` | 复习入口 | 是 | 否 | 改为 `/manage/review` 或隐藏 |
| `/write-note` | `src/components/empty-state.tsx` | 空状态入口 | 是 | 否 | 改为 `/manage/dashboard` 或移除 |
| `/write`、`/write/[slug]` | 待扫描确认 | 写作入口 | 待确认 | 否 | 与 write-note 同类处理 |

完成标准：

- [x] 所有指向旧 `write-*` 的链接都有处理决策。
- [x] 所有指向 `/manage/capture` 的入口都明确属于新主线。
- [x] 不存在用户可见的重复"新建错题"入口。
- [x] 输出完整扫描表到 diff-report.md（扫描结果记入 P0-01 表与 validation.md）。

## P0-02 Legacy 路由下线策略

处理：`/write`、`/write/[slug]`、`/write-note`、`/write-note/[slug]`、`/write-mistake`、`/write-mistake/[slug]`、`/mistakes/review`。

推荐规则：

- `/write-mistake` → `/manage/capture`
- `/mistakes/review` → `/manage/review`
- `/write-note` → `/manage/dashboard` 或提示页
- `/write-note/[slug]` → 提示旧编辑已停用
- `/write-mistake/[slug]` → 提示旧错题编辑已停用，或重定向 `/manage/mistakes`
- `/write`、`/write/[slug]` → 与 write-note 同类

完成标准：

- [x] 旧写作入口不再作为主线入口。
- [x] 用户访问旧路由时得到明确结果（重定向或提示页），不 404、不无限加载。（8 条旧路由全部 307 重定向，见 validation.md）

## P0-03 `/write-mistake` → `/manage/capture` 策略

- [x] `/write-mistake` 重定向到 `/manage/capture`（`next.config.ts` redirects）。
- [x] `/write-mistake/[slug]` 重定向 `/manage/mistakes`。
- [x] 清理所有引用 `/write-mistake` 的链接（见 P0-01 表）。
- [x] 确认新错题录入统一走 `/manage/capture`。

## P0-04 `/mistakes/review` → `/manage/review` 策略

- [x] `/mistakes/review` 重定向到 `/manage/review`。
- [x] 清理 `mistakes/page.tsx`、`weak-point-diagnosis.tsx`、`note-detail-content.tsx` 中对 `/mistakes/review` 的引用。
- [x] 复习统一走 `/manage/review`。

## P0-05 `/mistakes` 公开策略确认与实施（依赖 D-0）

> 依赖前置决策 D-0。未确认前跳过本项。

- [x] 记录用户决策（方案 B）于 [handoff.md](./handoff.md)。
- [x] 方案 B 已实施：公开导航移除"错题"（nav-card.tsx）；`/mistakes` 重定向 `/manage/mistakes`（next.config.ts）；未登录经 AuthGate 跳转 `/manage` 登录页。
- [ ] ~方案 A 不适用（用户选择方案 B）~

## P0-06 公开页只读化与首页管理入口清理

处理页面：`/`、`/blog`、`/notes`、`/mistakes`。

- [x] 首页未登录隐藏"待复习 / 待审核 / 上传资料 / 进入学习空间"（LearningSpaceCard `if (!isAdmin) return null`）。
- [x] 首页管理员入口置于学习空间卡片，未登录不渲染，不与公开导航同级。
- [x] 公开页移除旧写作按钮（`/write-note`、`/write-mistake`）。
- [x] 公开页移除管理快捷动作（write-buttons 统一指向 `/manage/dashboard`）。
- [x] 公开页 admin-only SWR `enabled=false`（匿名不请求 admin 数据 API；useAdminAuth 仅一次 session check）。

## P0-07 新 `/manage/*` 主线导航统一

- [x] Sidebar 含：Dashboard、Capture、Subjects、Drafts、Questions、Mistakes、Review、Attachments、AI、Jobs、Settings。（manage-sidebar.tsx 既有结构，无需改动）
- [x] Dashboard 体现：图片采集入口、待审核草稿、待复习项、最近附件（轻量，不过重统计）。
- [x] 旧 `/manage`（`src/app/manage/page.tsx`）顶部加提示条 + 跳转 `/manage/dashboard` 按钮。
- [x] 用户从 `/manage/dashboard` 能找到所有新主线入口，不需访问 `write-*`。

## P0-08 notes / blog / mistakes 渲染减负

> 仅做职责归位，不做大 UI 重写。

- [x] 公开 `notes` 页移除旧写作入口与管理动作（getCreateAction 指向 /manage/*，编辑/删除/移动入口 `isAdmin` 条件渲染）。
- [x] 公开页 admin 数据加载统一开关：`useAdminAuth` + `isAdmin` 条件渲染。
- [x] 隐藏 / dynamic import 公开页中的管理组件（SuggestionCard、WeeklySummaryCard `isAdmin &&` 条件渲染）。
- [x] 匿名访问公开页不请求 admin API、无 401/403 噪音（浏览器验证 0 个 401/403）。
- [x] 公开页首屏 DOM 更轻（管理员组件未登录时不渲染）。

禁止：重写全部 notes 系统、改数据库模型、改旧 Note 数据、引入新状态管理库、大规模 UI 改版。

## P0-09 文案统一

- [x] `/manage/capture` 增加文案：「用于图片错题采集，生成私有错题草稿。」
- [x] `/manage/mistakes` 增加文案：「管理新私有错题。历史公开错题不在此处编辑。」
- [x] 旧路由提示页文案：旧路由统一重定向（无独立提示页），重定向目标页含主线文案。

## P0-10 路由回归与浏览器验证

必须验证路由：

```
/write-note
/write-note/[slug]
/write-mistake
/write-mistake/[slug]
/mistakes/review
/manage/capture
/manage/mistakes
/manage/review
/
/blog
/notes
/mistakes
```

- [x] 检查是否 404 / 无限加载 / 错误暴露 / 重定向正确 / 未登录行为正确 / 管理员行为正确。（见 validation.md 验证记录）
- [x] 匿名公开页无 admin API 请求、无 401/403。（浏览器验证 0 个 401/403）
- [x] 记录到 [validation.md](./validation.md)。

## P0-11 收口文档与 handoff

- [x] 记录被下线 / 重定向 / 保留路由清单。（见 handoff.md 第三节）
- [x] 记录公开页策略与旧数据风险。（见 handoff.md 第五、六节）
- [x] 记录用户确认不以旧数据丢失作为阻塞。（见 handoff.md 第五节）
- [x] 记录剩余风险与后续建议到 [handoff.md](./handoff.md)。

## 推荐执行顺序

1. P0-01 Link scan
2. D-0 决定 `/mistakes` 是否公开
3. P0-03 处理 `/write-mistake`
4. P0-04 处理 `/mistakes/review`
5. P0-02 处理 `/write-note`、`/write`
6. P0-06 清理首页公开管理入口
7. P0-07 统一 Sidebar / dashboard 新主线
8. P0-08 减少公开页 admin hook
9. P0-09 文案统一
10. P0-10 浏览器回归
11. P0-11 收口文档

> 不要一开始就大面积重构 notes 组件。
