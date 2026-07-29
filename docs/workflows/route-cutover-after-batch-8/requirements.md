# 需求：Route Cutover Sprint

> 关联：[README.md](./README.md) | [design.md](./design.md) | [tasks.md](./tasks.md)
> 本轮范围：仅文档，不改代码。下述需求为后续实施阶段的目标态。

## 一、核心目标

1. 统一管理主线为 `/manage/*`，公开端只读化，Legacy 写作入口下线 / 重定向 / 提示。
2. 新错题唯一写入路径收敛到：`capture → mistake_draft → mistake → review`。
3. 不引入旧 `Note(type="mistake")` 到新 `mistakes` 的自动迁移。

## 二、最终路由策略

### 2.1 公开路由（保留，只读化）

保留：`/`、`/blog`、`/blog/[id]`、`/notes`、`/notes/[id]`、`/mistakes`（视第六节决策）。

公开路由**只允许**：阅读、浏览、基础筛选、公开内容展示。

公开路由**禁止**：编辑、删除、上传、AI/OCR 操作、复习提交、管理统计、管理员诊断、跳转旧 write-* 新建入口。

公开端原则：

- 公开页不承担写入职责。
- 公开页不加载 admin-only hooks。
- 公开页不请求 admin API。
- 公开页不展示私有 capture / question / mistake / attachment。

### 2.2 新管理路由（唯一主线）

URL 路径（route group `(workspace)` 不影响 URL）：

```
/manage/dashboard
/manage/subjects        (+ /manage/subjects/[id])
/manage/drafts          (+ /manage/drafts/[id])
/manage/questions       (+ /manage/questions/[id])
/manage/mistakes        (+ /manage/mistakes/[id])
/manage/review
/manage/attachments     (+ /manage/attachments/[id])
/manage/capture
/manage/ai
/manage/jobs
/manage/settings
/manage/knowledge-points/[id]   （知识点编辑，归属 subjects）
```

学习主链路：

```
/manage/capture → capture_item → mistake_draft → /manage/mistakes → mistake → /manage/review
```

题库链路：

```
/manage/drafts → /manage/questions → /manage/mistakes
```

附件链路：

```
/manage/attachments → attachment_links → question / mistake / capture
```

### 2.3 Legacy 写作路由（下线 / 重定向 / 提示）

需处理：`/write`、`/write/[slug]`、`/write-note`、`/write-note/[slug]`、`/write-mistake`、`/write-mistake/[slug]`、`/mistakes/review`。

推荐处理：

| 路由 | 最终处理 | 目标 |
| --- | --- | --- |
| `/write-note` | 重定向或提示页 | 不再作为新内容主入口 |
| `/write-note/[slug]` | 下线或提示旧编辑已停用 | 避免继续扩展旧 Note 编辑 |
| `/write-mistake` | 直接重定向到 `/manage/capture` | 新错题录入统一走图片采集 |
| `/write-mistake/[slug]` | 提示旧错题编辑已停用，或重定向 `/manage/mistakes` | 不再维护旧 Note 错题编辑 |
| `/mistakes/review` | 重定向到 `/manage/review` | 复习统一走新 review 系统 |
| `/write`、`/write/[slug]` | 纳入 P0-01 扫描确认后定策略 | 与 write-note 同类处理 |

> 用户已确认：旧路由下线导致的数据丢失 / 旧编辑能力丢失，不作为阻塞风险。

## 三、数据流统一策略

### 3.1 新错题唯一写入路径

图片错题：

```
/manage/capture → capture_items → mistake_drafts → mistakes → review_items
```

手工错题：

```
/manage/mistakes → mistake_drafts → mistakes → review_items
```

题目来源错题：

```
/manage/questions → mistake_drafts → mistakes → review_items
```

### 3.2 旧 Note(type="mistake") 冻结

- 可继续公开展示，是否展示由公开策略决定。
- 不再作为新错题入口。
- 不进入新复习系统。
- 不通过 `/write-mistake` 编辑。
- 不自动迁移到 `mistakes`。

## 四、权限策略（沿用 AGENTS.md 权限分层）

- 公开读取层：`/blog`、`/notes`、`/notes/[id]`、`/mistakes` 允许未登录访问；未登录只返回 `status === "published" && hidden === false`。
- 管理员编辑层：`/write-note`、`/write-note/[slug]`、`/write-mistake`、`/write-mistake/[slug]` 必须使用 `AuthGate`；本轮下线后改为重定向 / 提示页，仍不得暴露写入。
- 管理员学习与复习层：`/mistakes/review` 必须使用 `AuthGate`；下线后重定向到 `/manage/review`（同样受保护）。
- AI 操作层、图片上传层：必须受 `get_current_admin` 保护；公开页不得出现相关入口。
- 前端 `AuthGate` 不替代后端权限校验，后端 API 是真实安全边界。

## 五、用户界面统一策略

### 5.1 首页

- 未登录访客：保留博客 / 笔记 / 关于 / 留言等公开入口；隐藏待复习、待审核、上传资料、进入学习空间。
- 管理员：显示进入学习空间、待复习、待审核、上传资料 / 图片采集入口；建议放在头像菜单、小型 admin toolbar 或首页底部私人快捷区，不与公开导航同级展示。

### 5.2 旧 /manage

- 第一步：顶部增加醒目提示 + 新入口按钮（指向 `/manage/dashboard`）。
- 第二步：确认无依赖后，`/manage` 重定向到 `/manage/dashboard`（或旧面板移到 `/manage/legacy`）。

## 六、`/mistakes` 公开策略（决策项）

必须二选一：

- **方案 A**：继续公开展示 legacy 错题。只展示明确 public 的旧 `Note(type="mistake")`；不展示新 private mistakes、复习状态、AI/OCR 中间结果、附件私有链接、编辑入口。
- **方案 B（推荐）**：关闭公开错题入口。公开导航移除"错题"；`/mistakes` 显示私有说明或重定向 `/manage/mistakes`（未登录进入登录流程）。

> 默认推荐方案 B。最终以用户决策为准，决策结果写入 [tasks.md](./tasks.md) P0-05 与 [handoff.md](./handoff.md)。

## 七、前端渲染减负策略

- 公开页减少 admin 逻辑：不默认加载 admin actions、review stats、weak point diagnosis、upload / AI / edit 组件。
- 统一模式：`const enabled = isAdmin && shouldLoadAdminData; useSWR(enabled ? key : null, fetcher);`
- 更好方向：公开页只保留 PublicList / PublicDetail，管理动作迁移到 `/manage/*`。
- 降低 notes 大组件职责：仅做职责归位，不做大 UI 重写。

**禁止**：全量重写 Notes 系统、改数据库模型、改旧 Note 数据、引入新状态管理库、大规模 UI 改版。

## 八、验收要求

1. 旧 write-* 不再作为新建主入口。
2. `/write-mistake` 不再写旧 `Note(type="mistake")`。
3. 图片错题统一走 `/manage/capture`。
4. 错题管理统一走 `/manage/mistakes`。
5. 复习统一走 `/manage/review`。
6. 公开页没有写入入口。
7. 匿名公开页不请求 admin API（无 401/403 噪音）。
8. 新旧入口关系文案清楚。
9. 没有无限"验证中"。
10. 没有用户可见的无解释 404。
11. 所有路由变更有记录。

## 九、本轮不做

- 不修改 `src/`、`backend/` 代码
- 不新增 migration、不删数据库数据
- 不自动迁移旧 Note
- 不改 Batch 8 业务逻辑、不接 AI Gateway
- 不大规模重写 notes 系统、不做全站 UI 重构
