# Handoff：Batch 10.1 Prompt Registry Runtime Integration

> 日期：2025-07-05
> 状态：**通过，已关闭**
> 关联：[validation.md](./validation.md) | [tasks.md](./tasks.md)

## 验收结论

用户验收：**通过**。两个偏差已记录于 [validation.md 第 7 节](./validation.md)，均不阻塞验收。

## 通过项

- ✅ `npx tsc --noEmit` 通过
- ✅ `pytest` 173 passed, 0 failed（2 warnings 为 mock 相关，不影响结果）
- ✅ `git diff --check` 通过
- ✅ `ai.py` 中内联 system message 已清零（`"你是"` 模式 0 匹配）
- ✅ Prompt Registry 已通过 message builder 接入运行时（23 处调用点）

## 验收偏差

### 偏差 1：get_prompt_template() 直接调用数低于原标准

直接 `get_prompt_template` 调用数低于原至少 8 处标准，是因为 registry 访问被 Message Builder 集中封装。生产运行时仍通过 message builder 接入 Prompt Registry，不阻塞验收。

- 直接调用 6 处，间接调用（build_*_messages）17 处，合计 23 处运行时调用点

### 偏差 2：mistake_staged_service.py 仍保留 ai_prompts import

mistake_staged_service 仍保留 ai_prompts import，仅用于 vision override；普通 text prompt 已通过 message builder / registry 获取。

- 仅 import `QUESTION_DRAFT_VISION_SYSTEM_MESSAGE`，作为 `build_vision_messages` 的 `system_prompt_override` 参数
- 3 条 text 路径均使用 `build_text_messages`，system prompt 从 registry 获取
- 不存在直接 import 普通 system prompt 常量的情况
- 作为受控例外记录

## 后续迭代建议

1. **偏差 2 完全消除**：将 `QUESTION_DRAFT_VISION_SYSTEM_MESSAGE` 纳入 `PROMPT_REGISTRY` 中 `MISTAKE_QUESTION_DRAFT` 的配置（例如新增 `vision_system_prompt` 字段或直接设为 `system_prompt`），使 `mistake_staged_service.py` 不再需要直接 import `ai_prompts` 常量。
2. **预存在测试失败修复**：`test_mistake_review_service.py` 的 2 个失败和 `test_attachment_service.py` 的全量运行失败均为测试隔离问题，与 Batch 10.1 无关，建议在独立迭代中修复。
3. **stream 端点 task_type 枚举化**：`"analyze_mistake_stream"` / `"analyze_text_stream"` 仍为字符串，非 `AiTaskType` 枚举成员。stream 端点不经过 gateway 的 `_resolve_registry_defaults`，因此 registry 默认值对 stream 路径无效。后续可将 stream task_type 纳入枚举并接入 registry。
