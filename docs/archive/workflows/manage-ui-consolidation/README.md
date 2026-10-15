# Manage UI Consolidation

## 任务目标

将 `/manage/**` 从按 Batch 展开的开发期页面集合，设计为长期使用的个人学习系统工作台。

## 涉及领域

- `manage`
- 前端管理端信息架构、导航、页面职责、组件与文案

## 当前状态

设计 v1.1、实施任务、修复轮和最终浏览器验收均已完成。首轮审查问题 R-01~R-06 已修复，最终验收又补强了完整背景隔离、锁文件版本一致性和抽屉完整视口覆盖（R-07~R-09）。

最终验证（2026-07-13）：18/18 回归测试通过；生产与测试 TypeScript 检查通过；`git diff --check`通过；生产构建成功并生成 37/37 页面；真实浏览器 E-02 通过。证据见 [validation.md](./validation.md)。

## 本轮边界

- 已完成管理端 UI 收束设计、实施、静态验证与真实浏览器验收。
- 未修改 `backend/`、API 契约、数据库或 migration。
- 未修改公开页面或公开数据边界。
- AUTH_BYPASS 生产双 true 拒绝（P2）不在本任务范围。

## 文档

- [design.md](./design.md)：信息架构、页面职责、组件与文案规范、实施拆分和风险
- [requirements.md](./requirements.md)：可验证的 UI、数据真实性、兼容性和安全要求
- [tasks.md](./tasks.md)：原始任务与 R-01~R-09 修复任务，均已执行
- [validation.md](./validation.md)：静态、构建与真实浏览器验收证据
- [handoff.md](./handoff.md)：设计结论、非目标、下一阶段范围和验收标准
