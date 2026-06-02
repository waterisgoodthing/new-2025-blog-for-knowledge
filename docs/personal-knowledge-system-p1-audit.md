# 个人知识与博客系统 P1 验收记录

> 日期: 2026-06-02
> 关联文档: `docs/personal-knowledge-system-tasks.md`

## 本轮目标

推进 P1「错题 AI 输出 + 复习规划」：

1. 扩展错题 AI 输出结构。
2. 让错题创建页能承接更完整的解析内容。
3. 增加复习规划 API。
4. 在错题集首页展示今日、本周、薄弱点和科目归总。

## 影响域

- `mistakes`: 错题 AI 输出、错题创建页、错题集首页。
- `review`: 复习规划 API 和聚合服务。
- `AI`: 图片/文本分析 prompt 和响应 schema。

## 已完成

### 错题 AI 输出扩展

`backend/app/schemas/ai.py` 和 `src/lib/api/ai.ts` 已同步新增字段：

- `error_reason`
- `key_step`
- `similar_traps`
- `generalization`
- `review_advice`
- `variant_questions`

`backend/app/routers/ai.py` 已更新图片分析和文本分析 prompt，并增加数组字段容错解析：模型如果把列表输出成字符串，也会按逗号、顿号或换行拆成数组。

### 错题创建页集成

`src/app/write-mistake/page.tsx` 已将扩展字段合并进“分析与反思”文本域：

- 详细解析
- 错误原因
- 关键步骤
- 相似易错点
- 举一反三
- 复习建议
- 变式题

当前没有新增数据库一等字段，保存时仍使用现有 `analysis` 和 `content` 承载扩展解析。这是为了避免半截迁移；后续如果需要独立筛选/统计这些字段，应进入模型、schema、migration、API client、详情页和同步的完整变更链。

### 复习规划 API

新增 `backend/app/services/review_planner.py`，并在 `backend/app/routers/review.py` 增加：

- `GET /api/review/plan`

响应包含：

- `today_count`
- `overdue_count`
- `week_count`
- `next_review_date`
- `subject_summaries`
- `weaknesses`
- `recommendations`

前端同步新增 `src/lib/api/review.ts` 类型和 `getReviewPlan()`，并在 `src/hooks/use-note-index.ts` 增加 `useReviewPlan()`。

### 错题集规划卡片

`src/app/mistakes/page.tsx` 已新增：

- 今日复习规划卡片。
- 本周复习数量。
- 下次复习日期。
- 薄弱点归总。
- 科目统计 chip。
- 醒目的“开始复习”入口。

### 错题详情学习页

`src/app/notes/[id]/note-detail-content.tsx` 已将 `mistake` 类型从普通笔记详情分支升级为学习页布局：

- 返回入口显示为“返回错题集”。
- 原题和图片证据位于首屏主要区域。
- 我的答案、正确答案、错因与解析、知识点归总独立分区。
- 复习状态卡片展示复习次数、记忆系数、间隔和下次复习日期。
- 保留编辑、删除和“开始复习”入口。

当前仍复用 `/notes/{slug}` 路由，尚未新增 `/mistakes/{slug}`；但页面体验已经按错题学习页处理。

## 验收结果

### API

当前代码启动在 `http://127.0.0.1:8010` 后：

| 接口 | 结果 |
|---|---|
| `GET /api/review/plan` | 200 |
| `GET /api/review/stats` | 200 |

样例返回显示：

- 今日到期: 1
- 已逾期: 1
- 薄弱点: `CSMA/CD`、`以太网`、`最小帧长`、`争用期`
- 重点科目: `计算机`

### 浏览器

前端启动在 `http://localhost:3000`，API 指向 `http://localhost:8010`。

| 页面 | 状态 | 结果 |
|---|---:|---|
| `/mistakes` | 200 | 显示“今日复习规划”和“薄弱点归总” |
| `/notes/csma-cd` | 200 | 显示错题学习页结构 |

页面文本确认包含：

- 今天有 1 道错题到期。
- 本周重点回看 `CSMA/CD`。
- 当前最需要关注的科目是 `计算机`。
- “开始复习”入口仍然可见。

错题详情页确认包含：

- 返回错题集。
- 先看题目和自己的答案，再对照正确步骤复盘。
- 题目、正确答案、错因与解析、知识点归总。
- 复习状态和开始复习入口。

移动端 390px 验收无横向溢出。

无 4xx/5xx 请求。浏览器关闭时出现一次 dev server 连接关闭日志，不影响页面数据。

### 代码检查

| 命令 | 结果 |
|---|---|
| `git diff --check` | 通过 |
| `npx tsc --noEmit` | 通过 |
| `npm run build` | 通过 |
| 后端 import/start check | 通过 |
| planner 样本聚合检查 | 通过 |

## 剩余问题

1. 错题扩展字段目前不是数据库一等字段，无法单独筛选或统计 `error_reason`、`key_step` 等字段。
2. 图片上传 AI 分析和文本 AI 分析需要真实 AI key 或 mock 服务才能做完整端到端验收。
3. 错题详情仍复用 `/notes/{slug}` 路由，尚未新增 `/mistakes/{slug}` 独立路由。
4. 复习完成页尚未展示本次复习总结和下一步建议。

## 下一步

1. 新增或改造错题详情页，突出原题、图片、错因、关键步骤、变式题和复习状态。
2. 为 AI 分析增加 mock 验收路径，避免依赖真实 key 才能验证 UI。
3. 改造 `/mistakes/review` 完成页，显示掌握程度分布和下一步计划。
