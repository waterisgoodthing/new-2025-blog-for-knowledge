# Route Cutover Sprint：新旧路由束口与旧入口下线

> 阶段：**实施完成**（D-0=方案 B，P0-01~P0-11 全部完成并通过验证）
> 前置：Batch 8（图片错题采集 `/manage/capture`）已完成
> 触碰域：`blog`、`notes`、`mistakes`、`review`、`auth`、`home`、`manage`、共享前端基础设施

## 一、任务目标

把当前系统从「旧公开内容系统 + 旧 write-* 写作入口 + 新 /manage/* 学习系统 + Batch 8 图片采集」收束为：

- **公开端**：只读展示
- **管理端**：统一 `/manage/*` 主线
- **Legacy**：旧入口下线 / 重定向 / 提示

最终主线：

```
/manage/capture      图片错题采集
/manage/drafts       题目草稿
/manage/questions    正式题库
/manage/mistakes     错题草稿 / 正式错题
/manage/review       复习
/manage/attachments  附件
/manage/subjects     科目与知识点
```

## 二、当前路由现状（代码事实）

通过路由扫描确认（截至本任务建立时）：

### 公开路由（保留，只读化）
- `/`、`/blog`、`/blog/[id]`、`/notes`、`/notes/[id]`、`/mistakes`
- 其它公开页：`/about`、`/bloggers`、`/clock`、`/discover`、`/guestbook`、`/image-toolbox`、`/live2d`

### 新管理主线（route group `(workspace)`，URL = `/manage/<name>`）
- `/manage/dashboard`、`/manage/capture`、`/manage/subjects`（+ `[id]`）、`/manage/drafts`（+ `[id]`）、`/manage/questions`（+ `[id]`）、`/manage/mistakes`（+ `[id]`）、`/manage/review`、`/manage/attachments`（+ `[id]`）、`/manage/ai`、`/manage/jobs`、`/manage/settings`、`/manage/knowledge-points/[id]`

### Legacy 写作路由（待下线 / 重定向 / 提示）
- `/write`、`/write/[slug]`
- `/write-note`、`/write-note/[slug]`
- `/write-mistake`、`/write-mistake/[slug]`
- `/mistakes/review`
- 旧 `/manage`（`src/app/manage/page.tsx`，非 workspace）

### 旧入口引用点（已扫描命中）
- `src/app/manage/page.tsx` → `/write-note`、`/write-mistake`
- `src/app/mistakes/page.tsx` → `/mistakes/review`、`/write-mistake`
- `src/app/mistakes/review/page.tsx` → `/write-mistake`
- `src/app/mistakes/components/weak-point-diagnosis.tsx` → `/write-mistake?ai_prefill=1`、`/write-note?ai_prefill=1`、`/mistakes/review`
- `src/app/notes/page.tsx` → `/write-mistake`、`/write-note`
- `src/app/notes/[id]/note-detail-content.tsx` → `/mistakes/review`
- `src/components/empty-state.tsx` → `/write-note`

> 完整扫描结果见 [tasks.md](./tasks.md) P0-01 与执行阶段产出的 diff-report。

## 三、用户关键确认

- 旧路由下线导致的**数据丢失 / 旧编辑能力丢失，不作为阻塞风险**，但必须记录于 [risks.md](./risks.md)。
- 本轮**不做**旧 `Note(type="mistake")` 到新 `mistakes` 的自动迁移，也不保留复杂兼容层。
- `/mistakes` 是否继续公开属于本任务组的**明确决策项**（见 requirements.md 第六节与 tasks.md P0-05），需用户拍板，默认推荐方案 B（关闭公开错题入口）。

## 四、本轮边界（已遵守）

本轮实施严格遵守以下边界：

- ✅ 仅修改 `src/` 前端与 `next.config.ts`，未碰 `backend/`
- ✅ 未新增 migration、未删数据库数据
- ✅ 未自动迁移旧 Note
- ✅ 未改 Batch 8 业务逻辑、未接 AI Gateway
- ✅ 未大规模重写 notes 系统、未做全站 UI 重构

## 五、主线文件

| 文件 | 用途 |
| --- | --- |
| [requirements.md](./requirements.md) | 路由策略、数据流、权限、公开页策略、验收要求 |
| [design.md](./design.md) | 路由收束设计、页面减负、导航统一、渲染减负方案 |
| [tasks.md](./tasks.md) | P0-01 ~ P0-09 实施勾选项（待用户审批后执行） |
| [checklist.md](./checklist.md) | 验收清单 |
| [risks.md](./risks.md) | 旧数据 / 书签 / SEO / 编辑能力丢失风险 |
| [validation.md](./validation.md) | 验证方案与记录模板 |
| [handoff.md](./handoff.md) | 交接说明与后续建议 |

## 六、状态

- 文档准备：✅ 完成
- 代码实施：✅ 完成（P0-01~P0-11 全部完成）
- 验证：✅ 通过（tsc、build、HTTP 重定向、浏览器回归）
- 收口文档：✅ 完成（tasks.md 勾选、validation.md 记录、handoff.md 回填）

> 详见 [tasks.md](./tasks.md)、[validation.md](./validation.md)、[handoff.md](./handoff.md)。
