# R1 管理工作区入口与视觉收敛任务清单

状态：`R1-01 至 R1-10 EXECUTED / CLOSED / PASS BY P0-AUTH + CLEANUP`

> 用户必须明确批准 `R1-01` 至 `R1-10` 后才能开始实施。批准 R1 不授权数据库/schema/migration、编辑器内核统一、旧路由删除、认证重构、部署、推送、生产写入、影子迁移、authority switch 或 E/F 阶段工作。

- [x] R1-01 已建立当前入口、调用方和权限矩阵：公开入口、管理员入口、移动/桌面导航、深链、编辑入口及匿名/管理员/失效会话预期均已冻结，见 [入口权限矩阵](./r1-entry-permission-matrix.md)。
- [x] R1-02 已采用保守处置：未跟踪 `/workspace` 原型保持原样并排除 R1，不提交、不覆盖、不删除，也不建立第二套工作区或新增 `/workspace/*` 子路由。
- [x] R1-03 已冻结管理工作区视觉基线：复用现有 glass shell、`ManagePanel`、`FeatureState` 与 focus 语言；最小改动限定为 Dashboard 和必要的共享 action，不新增全局 CSS、不批量修改公开页面。见 [视觉基线](./r1-visual-baseline.md)。
- [x] R1-04 已按 TDD 增加真实快捷行动测试并取得 RED→GREEN；与 canonical workspace、公开路由无 `AuthGate`、私有入口 `AuthGate`、桌面/移动导航测试组合运行，5 个文件共 23 项通过。
- [x] R1-05 已复用现有管理 shell、section heading、语义色表面、品牌 focus ring 和 `FeatureState`，仅为 Dashboard 快捷行动增加一致卡片样式与 `motion-reduce:transition-none`；未修改全局 CSS 或公开页面。
- [x] R1-06 已在 `/manage/dashboard` 增加写笔记、写博客、图片采集、开始复习四个真实快捷行动；最近题目/复习与局部失败状态保持原实现，未新增占位成功态。
- [x] R1-07 已核对全部受版本控制的站内调用方：管理工作区入口统一为 `/manage/dashboard`，`/manage` 仅由 `AuthGate` 用作登录回退；没有受跟踪代码指向 `/workspace*`，公开读取边界保持不变。
- [x] R1-08 已建立 note/blog/mistake 创建与编辑能力矩阵，明确 Dashboard 主入口和后续 `R2 内容创建入口适配与编辑器能力去重` 建议；未合并编辑器、DTO、Store 或删除旧路由。见 [能力矩阵](./r1-content-editor-capability-matrix.md)。
- [x] R1-09 已完成定向/完整前端测试、TypeScript、生产构建和 390×844/1280×800/1440×900 真实浏览器验证；R1 隔离源状态通过 59 项测试、TypeScript 与 40/40 页面生产构建，三尺寸无横向溢出且四个快捷行动目标正确。当时主工作区原型与管理回退形成历史 `PARTIAL`，现已由 P0-AUTH + CLEANUP 关闭。
- [x] R1-10 已完成 diff/权限/可访问性/死链/代码质量复核，更新 `validation.md`、主任务清单、验收、风险和后续需求；未在 R1 内自动执行权限修复、路由退役、原型处置或编辑器统一。历史 `PARTIAL` 已由独立审批的后续 workflow 更新为 `PASS`。

## 顺序与硬门禁

```text
R1-01 → R1-02 → R1-03 → R1-04 → R1-05 → R1-06 → R1-07 → R1-08 → R1-09 → R1-10
```

- R1 执行阶段 R1-02 未获得处置选择，因此当时不得修改或删除原型；
  后续 CLEANUP 已取得独立批准。

- R1-04 测试未先建立：不得进入 R1-05。
- 任一权限或公开读取回归：立即停止。
- 任一数据/schema/backend contract 需求：退出 R1，另建并审批独立任务。
- R1-09 未全部通过：不得将 R1 标为 `PASS`。

## 后续收口

- P0-AUTH 已修复 `/manage` 与 strict AuthGate 的真实管理员判定。
- CLEANUP 已获单独批准并采用方案 A 删除 `/workspace` 原型。
- 主工作区测试、TypeScript、生产构建和三尺寸浏览器均通过。
- R1-09/R1-10 的历史 `PARTIAL` 已由后续 workflow 解除。

## 完成定义

R1 只有同时满足以下条件才可标记 `PASS`：

1. `/manage/dashboard` 是唯一管理工作区 authority。
2. Dashboard 所有主要行动指向真实、存在、权限正确的流程。
3. 公开博客、笔记和错题读取未被封闭。
4. 未执行数据迁移、schema 变更或旧路由删除。
5. 管理工作区视觉在三种尺寸下清晰、可访问且无新回归。
6. 自动化测试、TypeScript、生产构建和真实浏览器证据均已记录。
