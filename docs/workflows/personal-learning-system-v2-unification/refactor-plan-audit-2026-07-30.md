# `docs/refactor-plan` 重新审查报告

日期：2026-07-30
状态：`REVIEWED / IMPLEMENTATION NOT AUTHORIZED`

## 审查范围

- `docs/refactor-plan/` 当前 11 个文件，包括两份 HTML 预览、原始提案、校正版和依赖基线。
- 当前前端路由、管理工作区、博客读写链路、认证启动保护和测试入口。
- 既有统一大方案及 I0–I12 的阶段、权限、迁移和最终收口门禁。

本报告只校正文档前提并提取任务组。未修改业务代码、数据库、schema、migration、配置、部署、Git 历史或现有未跟踪原型。

## 总结结论

`docs/refactor-plan/` 不能直接作为实施清单。可保留的目标是：

1. 减少重复入口。
2. 保持蓝白色系并统一视觉语言。
3. 改善管理工作区的创建、复习和最近内容入口。
4. 在删除任何兼容路由前建立调用方矩阵、浏览器证据和回滚条件。

不能直接继承的内容是：

- 新建第二套 `/workspace` 主线。
- 再次执行无来源基线的博客迁移。
- 删除当前 `write*` 路由或静态内容。
- 把编辑器统一、数据迁移、认证、存储、缓存、队列和部署一次性打包。
- 使用文档中的 `58/58`、`300/300`、工期和性能提升百分比作为当前事实。

因此，本轮仅提取一个新任务组：`R1 管理工作区入口与视觉收敛`。

## 事实校正矩阵

| 原方案或校正版主张 | 当前证据 | 结论 |
|---|---|---|
| 当前项目没有毛玻璃效果 | `src/app/manage/(workspace)/layout.tsx`、`manage-sidebar.tsx` 及多个公开组件已使用 `backdrop-blur-*`、半透明背景和玻璃边框 | `FALSE`；任务应统一现有玻璃语言，不是从零新增 |
| `/workspace` 是新的统一入口 | 已完成的 I4 将 `/manage` 冻结为登录入口、`/manage/dashboard` 冻结为 canonical workspace；管理 route-group layout 已有 `AuthGate` | `CONFLICT`；不得并行建立第二套 workspace authority |
| `src/app/workspace/page.tsx` 可作为实现基础 | 该文件当前未跟踪；它链接到尚不存在的 `/workspace/create`、`/workspace/capture`、`/workspace/review`，并读取 `ReviewStats` 中不存在的 `total_notes` | `PROTOTYPE / NOT VERIFIED`；不得视为可交付实现 |
| 博客需要迁移到数据库 | 列表由 `useBlogIndex -> listNotes(type=blog)` 读取，详情由 `getNote` 读取，写入由 `createNote/updateNote` 完成 | 主读写链已经在 PostgreSQL Note API；不能再假设“尚未迁移” |
| 静态博客仍是迁移源 | `public/blogs/index.json` 当前为空，`public/blogs/` 无内容子目录 | 当前无可迁移静态博客基线 |
| 需要删除 GitHub sync service/router | 当前 `backend/main.py` 没有 sync router，仓库也没有提案所列 `backend/app/services/github_sync.py` | 删除任务已失效 |
| 认证系统处于默认绕过 | `AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false`；生产双 true 已在应用启动时拒绝 | 默认并非绕过；运行时环境仍需验证，但不属于本任务 |
| 后端启动仍用 `Base.metadata.create_all` | 当前 `backend/main.py` 使用只读 revision readiness，期望 revision `025` | 校正版引用的是过期架构事实 |
| 可直接删除旧 `write*` 路由 | 路由仍存在，且创建/编辑能力分散；既有 I4 明确要求兼容与受保护边界 | `BLOCKED`；先完成调用方与能力矩阵，再另行批准退役 |
| 每阶段独立分支、PR 和多人 review | 项目治理默认单所有者 | 不设虚构审批角色；保留用户审批、证据、回滚和独立验证 |

## 文档内部冲突

### 视觉基线冲突

- `02-UI-DESIGN-SYSTEM-BLUE-WHITE.md` 要求强化蓝白毛玻璃。
- `03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md` 要求保留毛玻璃。
- `04-DESIGN-REFACTOR-PROPOSAL.md` 又要求去除毛玻璃并改为纯白浅灰。
- `00-CORRECTED-PHASED-PLAN.md` 将其解释为“当前没有毛玻璃，需要新增”，与源码不符。

本任务组选用仓库当前已实现的方向：蓝白、克制玻璃、密集但清晰的管理界面。不得全局批量替换样式。

### 产品入口冲突

原方案使用：

```text
/workspace
  /create
  /capture
  /review
```

当前已冻结并实现的是：

```text
/manage                  登录入口
/manage/dashboard        canonical workspace
/manage/capture          管理员采集
/manage/review           管理员复习
/manage/settings         管理员设置
```

新任务组只收敛现有 `/manage/**`，不创建平行主线。

### 数据与编辑器冲突

博客已使用 Note API，但博客、普通笔记、错题编辑器仍承载不同字段和流程。直接合并会同时触碰：

- 博客封面、图片占位符与发布字段。
- 笔记文件夹、版本、标签和公开状态。
- 错题的一等字段、图片证据、AI 分阶段分析和复习关系。

因此，“统一编辑器”不属于 R1。R1 只建立能力矩阵和统一入口编排；编辑器内核合并必须成为后续独立任务并重新审批。

## 风险与处置

| ID | 风险 | 状态 | R1 处置 |
|---|---|---|---|
| RFP-01 | 第二套 workspace 导致导航和权限表达分叉 | 高 | 保持 `/manage/dashboard` 为唯一 canonical workspace |
| RFP-02 | 全局样式替换破坏公开博客/笔记/错题读取体验 | 高 | 仅在管理工作区内建立和验证 token/primitives |
| RFP-03 | 删除路由破坏深链、书签和编辑能力 | 高 | R1 禁止删除；先产出引用和能力矩阵 |
| RFP-04 | 把已数据库化的博客再次迁移 | 高 | R1 禁止 migration 和数据写入 |
| RFP-05 | 把原型页面当成已完成实现 | 中 | 标记 `PROTOTYPE / NOT VERIFIED`，由用户另行决定保留或放弃 |
| RFP-06 | 使用陈旧测试数量作为门禁 | 中 | 以届时实际命令、实际通过数和首个失败为准 |
| RFP-07 | 视觉动效降低可访问性或移动端性能 | 中 | 覆盖 reduced-motion、focus、对比度、三尺寸和无横向溢出 |

## 提取结果

详见：

- [R1 设计](./r1-workspace-entry-visual-convergence-design.md)
- [R1 需求](./r1-workspace-entry-visual-convergence-requirements.md)
- [R1 任务清单](./r1-workspace-entry-visual-convergence-tasks.md)

R1 在用户明确批准任务清单前保持 `APPROVAL REQUIRED`。
