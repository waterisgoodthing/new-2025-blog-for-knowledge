# Requirements

## 已核实缺口
- **A01 来源校验**：`routers/admin_mistakes.py` 生成 `creation_context.input_hash`（含 question id/version、my_answer、user_error_reason），但 confirm 时只校验 question id+version（`create_entity`），**不比对 input_hash**。生成输入在确认前被改动不会被拒绝。
- **A02 最终快照**：`ai_creation_service.confirm_canonical_creation` 只存 `confirmed_payload_hash`，**未持久化最终确认载荷**，无法重建"人工确认了什么"。
- **A03 共同锁**：`ai_run_service.decide_ai_run` 基于 router 传入的**未加锁**对象做内存 revision 检查后 flush；与 confirm 的 `with_for_update` 不共享原子协议 → 并发 confirm/decision 可竞争。

## 需求
1. confirm 必须校验"确认输入"与生成输入一致（重算 `input_hash` 比对），不一致拒绝（409）。
2. confirm 必须原子持久化"最终确认快照"（可重建），无需 schema 迁移。
3. 通用 decision 必须与 confirm 共享同一行锁协议（`SELECT … FOR UPDATE` + revision CAS）。

## 验收
- 输入不一致 → 409；一致 → 200。
- 确认后 `run.creation_context["confirmed_snapshot"]` 含 payload 与 hash。
- decision 对已变更/已决 run 走数据库最新状态（不因传入对象陈旧而误判）。
- 现有 AI 测试不回退。
