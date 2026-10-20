# Design

## A01 来源校验
- `schemas/mistake.py::MistakeAiConfirmRequest` 增 `user_error_reason: str | None = None`（新增可选字段，向后兼容旧客户端缺省为 None）。
- `admin_mistakes.py::confirm_ai_candidate.create_entity`：在既有 question id/version 校验后，用 `canonical_input_hash(question.id, question.version, payload.my_answer, payload.user_error_reason)` 重算并与 `context["input_hash"]` 比对；不等则 `AiRunConflict`。
- 前端 `mistake-draft-entry.tsx` confirm 时补发 `user_error_reason`（= 生成时所用 `mistakeReason.trim()`）；`lib/api/mistakes.ts` 类型同步。

## A02 最终快照
- `confirm_canonical_creation`：在绑定 target 的同时，把 `creation_context` 复制并写入 `confirmed_snapshot = {"payload_hash": new_hash, "payload": payload}`；重放路径不变（已有快照）。免迁移（复用现有 JSONB）。

## A03 共同锁
- `decide_ai_run`：入口以 `select(AiRun).where(id==run.id).with_for_update().execution_options(populate_existing=True)` 重新加锁读取，替换传入对象；使 decision 与 confirm 在同一行上串行；随后沿用现有 revision/状态校验（CAS）。

## 边界
- 不改 schema 结构、不迁移、不回填历史。
- 不改变 confirm 的幂等/版本冲突语义（仅新增输入校验与快照）。
- A01 为向后兼容的可选字段；不传 `user_error_reason` 的旧客户端会因 input_hash 不匹配被拒（安全优先，符合 B05 意图）。
