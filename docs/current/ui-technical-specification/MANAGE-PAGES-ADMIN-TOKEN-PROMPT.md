# Manage 页面 Admin Token 接入 Prompt

## 背景

Phase 4 已完成 5 个 manage 页面（questions/mistakes/notes/drafts/review）的 admin token 接入，使用 `Uiv2PageHeader` + admin token 变量。剩余 10 个页面仍使用旧的 legacy token（`var(--color-brand)`、`text-slate-900`、硬编码颜色）或没有统一的视觉风格，需要迁移到 admin token 系统。

## 目标

将以下 10 个 manage 页面迁移到 admin token：

1. `/manage/(workspace)/dashboard` — 学习概览
2. `/manage/(workspace)/capture` — 快速捕获
3. `/manage/(workspace)/search` — 全局搜索
4. `/manage/(workspace)/subjects` — 学科管理
5. `/manage/(workspace)/knowledge-points` — 知识点
6. `/manage/(workspace)/ai` — AI 运行记录
7. `/manage/(workspace)/jobs` — 后台任务
8. `/manage/(workspace)/practice` — 练习记录
9. `/manage/(workspace)/attachments` — 附件管理
10. `/manage/(workspace)/analytics` — 数据分析

## 要求

### 1. 页面头部统一使用 `Uiv2PageHeader`

已完成页面的模式：

```tsx
import { Uiv2PageHeader } from '@/components/ui-v2'

export default function Page() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader
        eyebrow='内容管理'
        title='题目'
        subtitle='管理可复用题目、答案、解析与知识点关联。'
      />
      {/* 页面内容 */}
    </div>
  )
}
```

所有页面头部（eyebrow/title/description）改为 `Uiv2PageHeader`，移除旧的手写标题结构。

### 2. Admin token 变量替换规则

| 旧写法 | 新写法 | 用途 |
|---|---|---|
| `var(--color-brand)` | `var(--admin-accent)` | 强调色、按钮、badge |
| `text-slate-900` | `text-admin-primary` | 主要文本 |
| `text-slate-600`/`text-slate-500` | `text-admin-secondary` | 次要文本 |
| `bg-white`/`bg-slate-50` | `bg-admin-surface` | 卡片背景 |
| `border-slate-200` | `border-admin-border` | 边框 |
| 硬编码颜色（`#...`） | 根据语义选择 admin token | 任何非中性色 |

### 3. 保持现有布局和功能

**零功能改动**：只替换 token，不改变布局、交互、数据流、组件结构。

已有的 `ManagePageHeader` 组件如果语义和 `Uiv2PageHeader` 一致，可以替换；如果有特殊逻辑（操作按钮、tabs、自定义布局），保留其结构但内部用 admin token。

### 4. 特殊情况

- **dashboard** 页面：可能有多个数据卡片，每个卡片的背景、文本、边框都要用 admin token
- **search** 页面：已是 `'use client'`，可能有搜索框、结果列表，保持交互不变
- **analytics** 页面：可能有图表，图表库的颜色配置不在此次范围（除非是包裹容器的背景/文本）
- **attachments/[id]** 详情页：如果存在，也要一起迁移

### 5. 验证要求

迁移完成后：

1. `npx tsc --noEmit` — 0 errors
2. `npx vitest run` — 通过（baseline 679 passed）
3. `npm run build` — 成功
4. `git diff --check` — clean
5. 验收 grep：`grep -r "var(--color-brand)\|text-slate-9\|bg-slate-5\|border-slate-2" src/app/manage/\(workspace\)/{dashboard,capture,search,subjects,knowledge-points,ai,jobs,practice,attachments,analytics}` — **0 结果**（允许保留 `text-slate-700` 等非主色调的中性灰）

浏览器实测（可选，如果环境支持）：打开 `/manage/dashboard`、`/manage/subjects` 等页面，确认：
- 页面头部使用 `Uiv2PageHeader`，eyebrow 是 admin-accent
- 卡片/列表项的文本是 admin-primary/secondary
- 按钮/badge 是 admin-accent
- 无明显视觉断层

## 交付

完成后报告：

- **Conclusion**: PASS / PARTIAL / FAIL
- **Changes**: 迁移的 10 个页面清单 + 组件侧改动（如果有）
- **Verification**: tsc/vitest/build/验收 grep 结果
- **Browser evidence**（可选）: 截图或实测记录
- **Deviations**: 任何保留旧 token 的地方及原因
- **Remaining**: 未处理的遗留项（如果有）

提交前确认所有改动已验证，未 commit。
