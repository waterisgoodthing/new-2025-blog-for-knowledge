# Design：Route Cutover Sprint

> 关联：[requirements.md](./requirements.md) | [tasks.md](./tasks.md)
> 本文件描述路由收束的设计方案，不含代码改动。

## 一、设计目标

将多入口的混合路由体系收束为「公开只读 + 管理统一」的单主线结构，并在此过程中对公开页做轻量化减负，但不触发大规模重构。

## 二、路由收束设计

### 2.1 目标态路由矩阵

```
公开端（只读）
  /              首页（未登录：公开站；登录：+ 学习空间轻量入口）
  /blog          博客列表
  /blog/[id]     博客详情
  /notes         笔记列表
  /notes/[id]    笔记详情
  /mistakes      错题（方案 A 公开 / 方案 B 私有，见 requirements 第六节）

管理端（唯一主线，AuthGate）
  /manage/dashboard
  /manage/capture
  /manage/subjects       (+ [id])
  /manage/drafts         (+ [id])
  /manage/questions      (+ [id])
  /manage/mistakes       (+ [id])
  /manage/review
  /manage/attachments    (+ [id])
  /manage/ai
  /manage/jobs
  /manage/settings
  /manage/knowledge-points/[id]

Legacy（下线 / 重定向 / 提示）
  /write             提示或重定向
  /write/[slug]      提示旧编辑已停用
  /write-note        重定向 /manage/dashboard 或提示
  /write-note/[slug] 提示旧编辑已停用
  /write-mistake     重定向 /manage/capture
  /write-mistake/[slug] 提示或重定向 /manage/mistakes
  /mistakes/review   重定向 /manage/review
```

### 2.2 Legacy 路由处理机制

采用 Next.js App Router 原生机制，优先级：

1. **重定向**（`next.config.ts` redirects 或页面内 `redirect()`）：用于明确 1:1 映射。
   - `/write-mistake` → `/manage/capture`
   - `/mistakes/review` → `/manage/review`
   - `/write-note` → `/manage/dashboard`（或提示页）
2. **停用提示页**：用于编辑类路由（`[slug]`），说明旧编辑已停用并给出新入口链接，避免直接 404。
3. **不保留兼容写入层**：旧 `write-*` 页面不再向旧 `Note` 写入，重定向后由新 `/manage/*` 承担。

> 设计取舍：用提示页而非直接删除，是为了旧书签体验与 SEO（避免大量 404）；对无内容价值的纯入口用重定向。

### 2.3 旧 /manage 降级

- 第一步：`src/app/manage/page.tsx` 顶部加提示条 + 跳转 `/manage/dashboard` 按钮，保留历史内容维护能力。
- 第二步：确认无依赖后，`/manage` 重定向到 `/manage/dashboard`，旧面板可选移到 `/manage/legacy`。

## 三、新 /manage/* 导航统一设计

### 3.1 Sidebar 结构

```
Dashboard
Capture
Subjects
Drafts
Questions
Mistakes
Review
Attachments
AI
Jobs
Settings
```

### 3.2 Dashboard 内容

- 图片采集入口
- 待审核草稿
- 待复习项
- 最近附件

> 不做过重统计，保持轻量。

## 四、公开页只读化与渲染减负设计

### 4.1 受影响文件（重点）

- `src/app/notes/page.tsx`
- `src/app/notes/[id]/note-detail-content.tsx`
- `src/app/notes/[id]/page.tsx`
- `src/app/blog/page.tsx`
- `src/app/mistakes/page.tsx`
- `src/app/mistakes/components/weak-point-diagnosis.tsx`
- `src/hooks/**`
- `src/components/empty-state.tsx`

### 4.2 减负模式

统一 admin 数据加载开关：

```ts
const enabled = isAdmin && shouldLoadAdminData;
useSWR(enabled ? key : null, fetcher);
```

原则：

- 公开页只保留 `PublicList` / `PublicDetail`。
- 管理动作迁移到 `/manage/*` 或隐藏到 admin-only 区域。
- 移除公开页中的旧写作按钮（`/write-note`、`/write-mistake`）。
- 移除公开页中的管理快捷动作。

### 4.3 范围禁止项

- 不全量重写 Notes 系统。
- 不重做 Markdown 渲染器 / Sidebar / 主题系统。
- 不改数据库模型、不改旧 Note 数据。
- 不引入新状态管理库。

## 五、首页设计

### 5.1 未登录

- 保留博客 / 笔记 / 关于 / 留言等公开入口。
- 隐藏：待复习、待审核、上传资料、进入学习空间。

### 5.2 已登录管理员

- 显示进入学习空间、待复习、待审核、上传资料 / 图片采集入口。
- 入口位置：头像菜单 / 小型 admin toolbar / 首页底部私人快捷区，不与公开导航同级。

## 六、`/mistakes` 公开策略设计

- **方案 A（公开）**：`/mistakes` 仅展示旧公开 `Note(type="mistake")`；不加载新 private mistakes、复习状态、AI/OCR、附件私有链接、编辑入口。
- **方案 B（私有，推荐）**：公开导航移除"错题"；`/mistakes` 显示私有说明或重定向 `/manage/mistakes`；未登录进入登录流程。

> 设计上两方案都需保证：公开页不请求 admin API，不产生 401/403 噪音。

## 七、文案设计

- `/manage/capture`：「用于图片错题采集，生成私有错题草稿。」
- `/manage/mistakes`：「管理新私有错题。历史公开错题不在此处编辑。」
- 旧路由提示页：「旧写作入口已停用。新错题请使用图片采集或错题管理工作区。」

## 八、验证设计

- 路由回归：逐条访问 Legacy 与新主线路由，检查 404 / 无限加载 / 重定向 / 未登录与管理员行为。
- 公开页噪音：匿名访问公开页，确认无 admin API 请求、无 401/403。
- 类型与构建：`npx tsc --noEmit`、`npm run build`。
- 详见 [validation.md](./validation.md)。

## 九、不做的设计决策（明确记录）

- 不设计旧 `Note(type="mistake")` → 新 `mistakes` 迁移流程。
- 不设计 Batch 8 业务逻辑变更。
- 不设计 AI Gateway 接入。
- 不设计全站 UI 重构。
