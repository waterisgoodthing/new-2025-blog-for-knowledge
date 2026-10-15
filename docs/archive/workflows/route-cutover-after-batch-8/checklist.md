# Checklist：Route Cutover Sprint 验收清单

> 关联：[tasks.md](./tasks.md) | [validation.md](./validation.md)
> 用法：实施阶段逐项核对，通过后打勾并记录到 [validation.md](./validation.md)。

## 一、前置决策

- [ ] D-0 `/mistakes` 公开策略已确认（方案 A / 方案 B）。

## 二、路由收束

- [ ] 旧 `write-*` 不再作为新建主入口。
- [ ] `/write-mistake` 重定向到 `/manage/capture`。
- [ ] `/mistakes/review` 重定向到 `/manage/review`。
- [ ] `/write-note` 重定向或停用提示。
- [ ] `/write`、`/write/[slug]` 已纳入处理。
- [ ] 旧路由无用户可见的无解释 404。
- [ ] 旧路由无无限"验证中"。

## 三、新主线导航

- [ ] Sidebar 含 Dashboard / Capture / Subjects / Drafts / Questions / Mistakes / Review / Attachments / AI / Jobs / Settings。
- [ ] `/manage/dashboard` 能找到所有新主线入口。
- [ ] 旧 `/manage` 顶部有提示条 + 跳转 `/manage/dashboard` 按钮。

## 四、公开页只读化

- [ ] 公开页无写入入口（编辑 / 删除 / 上传 / AI / 复习提交）。
- [ ] 首页未登录隐藏待复习 / 待审核 / 上传资料 / 进入学习空间。
- [ ] 首页管理员入口不与公开导航同级。
- [ ] `/mistakes` 策略按 D-0 执行。

## 五、渲染减负

- [ ] 匿名访问公开页不请求 admin API。
- [ ] 匿名公开页控制台无 401/403 噪音。
- [ ] 公开页 admin-only SWR `enabled=false`。
- [ ] 未做 notes 全量重写 / 数据库模型改动 / 新状态库。

## 六、数据流

- [ ] `/write-mistake` 不再写旧 `Note(type="mistake")`。
- [ ] 图片错题统一走 `/manage/capture`。
- [ ] 错题管理统一走 `/manage/mistakes`。
- [ ] 复习统一走 `/manage/review`。
- [ ] 旧 `Note(type="mistake")` 未被自动迁移。

## 七、文案

- [ ] `/manage/capture` 文案到位。
- [ ] `/manage/mistakes` 文案到位。
- [ ] 旧路由提示页文案到位。

## 八、回归验证

- [ ] Legacy 路由逐条访问通过。
- [ ] 新主线路由逐条访问通过。
- [ ] 公开路由未登录行为正确。
- [ ] 管理路由管理员行为正确。

## 九、构建与类型

- [ ] `npx tsc --noEmit` 通过（或仅剩既有已知问题，已记录）。
- [ ] `npm run build` 通过（或仅剩既有已知问题，已记录）。

## 十、收口

- [ ] 被下线 / 重定向 / 保留路由清单已记录。
- [ ] 风险已记录于 [risks.md](./risks.md)。
- [ ] handoff 已写入 [handoff.md](./handoff.md)。
- [ ] `git diff --check` 无空白错误。
- [ ] `git diff --name-only` 改动范围符合预期。
