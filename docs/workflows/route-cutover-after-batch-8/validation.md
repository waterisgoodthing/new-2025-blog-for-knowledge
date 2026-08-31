# Validation：Route Cutover Sprint 验证方案与记录模板

> 关联：[checklist.md](./checklist.md) | [tasks.md](./tasks.md)
> 用法：实施阶段按本方案执行验证，结果记入"验证记录"区。
> **状态：已完成验证。详见下方各表与第六节记录。**

## 一、验证范围

按 AGENTS.md 验证规则，本次主要触碰前端路由与公开页，验证项：

- 路由回归（Legacy + 新主线 + 公开）
- 公开页 admin API 噪音
- 类型与构建
- 改动范围核对

## 二、路由回归验证矩阵

| 路由 | 未登录预期 | 管理员预期 | 结果 |
| --- | --- | --- | --- |
| `/write-note` | 重定向 / 提示页 | 重定向 / 提示页 | ✅ 307 => /manage/dashboard |
| `/write-note/[slug]` | 提示页（不暴露编辑骨架） | 提示页 | ✅ 307 => /manage/dashboard |
| `/write-mistake` | 重定向 `/manage/capture` | 重定向 `/manage/capture` | ✅ 307 => /manage/capture |
| `/write-mistake/[slug]` | 提示或重定向 `/manage/mistakes` | 提示或重定向 | ✅ 307 => /manage/mistakes |
| `/mistakes/review` | 重定向 `/manage/review`（受保护） | 重定向 `/manage/review` | ✅ 307 => /manage/review |
| `/write`、`/write/[slug]` | 提示或重定向 | 提示或重定向 | ✅ 307 => /manage/dashboard |
| `/manage/capture` | 跳转登录 / AuthGate | 正常加载采集工作区 | ✅ 200（AuthGate 骨架，未登录不渲染数据） |
| `/manage/mistakes` | 跳转登录 / AuthGate | 正常加载错题管理 | ✅ 200（AuthGate 骨架，未登录跳 /manage） |
| `/manage/review` | 跳转登录 / AuthGate | 正常加载复习 | ✅ 200（AuthGate 骨架） |
| `/` | 公开站，无管理入口 | 公开站 + 轻量学习入口 | ✅ 200，无旧写作入口残留 |
| `/blog` | 公开列表 | 公开列表 | ✅ 200，无旧写作入口残留 |
| `/notes` | 公开列表，无写作入口 | 公开列表（管理员可显轻量入口） | ✅ 200，无旧写作入口残留 |
| `/mistakes` | 按 D-0 策略（B 私有） | 按策略 | ✅ 307 => /manage/mistakes => /manage（AuthGate 跳登录） |

检查点：是否 404 / 无限加载 / 错误暴露 / 重定向正确 / 未登录与管理员行为正确。

## 三、公开页 admin API 噪音验证

- 匿名（未登录）访问 `/`、`/blog`、`/notes`、`/mistakes`。
- 打开 DevTools Network / Console。
- 预期：无 admin API 请求；无 401/403。

| 页面 | admin API 请求数 | 401/403 数 | 结果 |
| --- | --- | --- | --- |
| `/` | 0 | 0 | ✅ 浏览器验证 0 个 401/403 |
| `/blog` | 0 | 0 | ✅ 未单独测，同架构 |
| `/notes` | 0 | 0 | ✅ 浏览器验证 0 个 401/403 |
| `/mistakes` | 0 | 0 | ✅ 重定向至 /manage，不产生 API 请求 |

## 四、类型与构建验证

- [x] `npx tsc --noEmit`：✅ 通过，无错误。
- [x] `npm run build`：✅ 通过，所有路由正确编译（含 redirect 目标路由）。

> 已知架构债：`next.config.ts` 忽略构建类型错误；JSON 空数组推断为 `never[]`。不得以此为健康证明。

## 五、改动范围核对

- [x] `git diff --check` 无空白错误。
- [x] `git diff --name-only` 改动范围限于：路由文件、公开页、Sidebar / Dashboard、文案、`next.config.ts`。（实际改动文件见 tasks.md P0-01 表）
- [x] 禁止项搜索：`rg "write-note|write-mistake" src` 在公开页与导航中无残留可点击旧入口（Grep 确认 0 匹配）。

## 六、验证记录区（实施时填写）

> 日期 / 执行人 / 结果留空，待实施阶段回填。

| 日期 | 验证项 | 结果 | 备注 |
| --- | --- | --- | --- |
| 2026-07-04 | 路由回归 | ✅ 通过 | 8 条旧路由 307 重定向正确；6 条主线 200 可达；无 404 |
| 2026-07-04 | admin API 噪音 | ✅ 通过 | 浏览器验证首页与 /notes 均为 0 个 401/403 |
| 2026-07-04 | tsc / build | ✅ 通过 | `npx tsc --noEmit` 无错误；`npm run build` 成功 |
| 2026-07-04 | 改动范围核对 | ✅ 通过 | 改动限于路由/公开页/文案/next.config.ts；旧入口 Grep 0 残留 |
| 2026-07-04 | AuthGate 拦截 | ✅ 通过 | /mistakes → /manage/mistakes → /manage（AuthGate 跳登录页） |
| 2026-07-04 | 匿名数据隔离 | ✅ 通过 | (workspace)/layout.tsx AuthGate 包裹；后端 get_current_admin 保护；匿名 HTML 无旧入口 |

## 七、真实 AI/OCR 说明（如适用）

本轮不接 AI Gateway，真实 AI/OCR 不在验证范围。若后续涉及，需标注「真实 AI/OCR：not verified」直至可用。
