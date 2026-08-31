# I3 计划：Attempt、错题转换与采集手工回退

## 目标

交付可由管理员完成的最小闭环：`Question → Attempt → Mistake Draft → Mistake → Review Item → Review Record`，并让已存在的 Capture 能在 AI/OCR 不可用时由人工输入继续转为草稿。

## 阶段

1. 设计与契约冻结（当前）：盘点、定义状态机、形成任务清单与批准门。
2. 数据与服务：Attempt 模型、迁移、schema、服务和管理员 API。
3. 转换：错误 Attempt 幂等创建 Mistake Draft，既有 Draft 确认继续创建 Mistake/Review Item。
4. UI：题目详情作答、错误反馈、错题草稿跳转；启用 Capture 手工优先输入和失败恢复。
5. 验证：测试、TypeScript、隔离恢复环境、匿名/管理员边界与真实浏览器闭环。

## 硬停止条件

- migration 未获得任务清单批准、未在隔离库验证，或与现有 revision `020` 不兼容。
- Attempt 或 Capture 可绕过 `get_current_admin` 写入。
- 自动化结果可直接成为正式 Question/Mistake，或人工回退无法继续。
- 任何步骤要求迁移切换、部署、生产库写入或旧系统停写。
