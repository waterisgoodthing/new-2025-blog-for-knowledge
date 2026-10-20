# Tasks

- [x] T1 侦察 A01–A03 代码路径
- [x] T2 建立本工作流
- [x] T3 A01：schema 加 `user_error_reason` + router 重算/比对 input_hash + 前端补发
- [x] T4 A02：confirm 持久化 `confirmed_snapshot`（写入 `creation_context`）
- [x] T5 A03：新增 `get_ai_run_for_update`，`/decision` 改用它（与 confirm 共享行锁）
- [x] T6 测试：更新既有 confirm 体；新增 A01 不一致、A02 快照、A03 加锁刷新用例
- [x] T7 运行定向 + 全量测试（定向 30 passed；全量 950 passed）
- [x] T8 独立审查（另一 agent）→ PASS（见 validation.md）
- [x] T9 提交：`92ab227`（作为 B05 功能提交的一环；因目标文件整体为未提交 WIP，无法从 WIP 中单独剥离 A01–A03）
