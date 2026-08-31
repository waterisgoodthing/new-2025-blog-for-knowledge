# R1 入口、调用方与权限矩阵

日期：2026-07-30
状态：`FROZEN FOR R1`

## 规范入口

| 场景 | 当前入口 | 页面保护 | 后端边界 | R1 决策 |
|---|---|---|---|---|
| 管理员登录 | `/manage` | 会话检测与登录界面 | 认证 API | 保留 |
| 管理工作区 | `/manage/dashboard` | route-group `AuthGate` | 管理 API 使用 `get_current_admin` | 唯一 canonical workspace |
| 采集 | `/manage/capture` | route-group `AuthGate` | 管理员附件/Capture API | Dashboard 快捷入口 |
| 复习 | `/manage/review` | route-group `AuthGate` | 管理员 Review API | Dashboard 快捷入口 |
| 写笔记 | `/write-note` | 页面 `AuthGate` | Note 写 API | R1 兼容快捷入口 |
| 写博客 | `/write` | 页面 `AuthGate` | Note 写 API，`type=blog` | R1 兼容快捷入口 |
| 历史错题录入 | `/write-mistake` | 页面 `AuthGate` | Note/AI 管理写 API | 不作为首选；保留兼容 |

## 公开读取

| 页面 | 匿名访问 | 管理操作 | R1 约束 |
|---|---|---|---|
| `/blog` | 允许 | 登录后条件展示 | 不加 `AuthGate` |
| `/blog/[id]` | 允许已发布且未隐藏内容 | 登录后条件展示编辑入口 | 不加 `AuthGate` |
| `/notes` | 允许 | 登录后条件展示工作区入口 | 不请求私有管理数据 |
| `/notes/[id]` | 允许已发布且未隐藏内容 | 登录后条件展示编辑/复习入口 | 不加 `AuthGate` |
| `/mistakes` | 允许公开错题 | 登录后加载私有统计和操作 | 匿名不产生管理员 API 噪音 |

## 已核对调用方

| 调用方 | 当前目标 | R1 处理 |
|---|---|---|
| 桌面管理侧栏 | `/manage/dashboard` | 保持 |
| 移动管理导航 | `/manage/dashboard` | 保持 |
| 全站移动导航（管理员） | `/manage/dashboard` | 保持 |
| 首页学习空间卡片 | `/manage/dashboard` | 保持 |
| 首页写作按钮 | `/manage/dashboard` | 保持 canonical workspace 入口 |
| 笔记页工作区入口 | `/manage/dashboard` | 保持 |
| 博客/笔记详情编辑入口 | `/manage/dashboard` | 保持，由工作区编排后续动作 |
| 弱点诊断工作区入口 | `/manage/dashboard` | 保持 |
| 未跟踪 `/workspace` 原型 | 独立页面及不存在的 `/workspace/*` 子路由 | 排除 R1 实现，不提交、不覆盖、不删除 |

## 会话预期

| 状态 | `/manage/dashboard` | `/write-note` / `/write` | 公开页面 |
|---|---|---|---|
| 匿名 | 进入既有登录体验，不显示私有摘要 | 进入既有登录体验 | 正常公开读取 |
| 管理员 | 显示工作区和真实快捷行动 | 显示编辑器 | 正常读取并可显示管理入口 |
| 失效会话 | 回到登录体验，不泄漏摘要 | 回到登录体验 | 公开内容仍可读取，不显示私有操作 |

## 退役边界

R1 不删除任何 `write*` 路由。后续只有在能力等价、深链/书签、权限、浏览器和观察证据齐全并获得新批准后，才能建立独立退役任务。
