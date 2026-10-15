# Validation：Batch 10.2 Prompt Engineering Standardization

> 状态：**通过**
>
> 日期：2026-07-05

## 验收范围

- Prompt Registry 静态规范检查。
- PromptTemplate 变量、vision 和动态 Prompt 元数据。
- 安全 user content 模板渲染。
- Registry 驱动的 text / vision 消息构建。
- Prompt 与现有 Validator schema 映射一致性。
- 业务 service/router 对 `ai_prompts` 直接 import 的收口。
- 后端测试、TypeScript 和 diff 基础回归。

未包含真实 provider 调用、数据库、migration、管理后台、A/B、热更新、
成本统计、多供应商路由或 Batch 11。

## 自动化验证

### 1. Batch 10.2 目标测试

```text
cd backend
.venv/bin/python -m pytest \
  tests/test_ai_prompt_standard.py \
  tests/test_ai_prompt_registry.py \
  tests/test_ai_message_builder.py \
  tests/test_ai_validator.py \
  tests/test_question_draft_service.py \
  tests/test_capture_service.py -q
```

结果：**72 passed in 2.43s**。

### 2. 后端全量测试

```text
cd backend
.venv/bin/python -m pytest tests/ -q
```

结果：**185 passed, 2 warnings in 3.45s**。

两个 warning 均来自 `test_ai_gateway.py` 中既有 AsyncMock `session.add`
未 await 的 RuntimeWarning。本批没有修改该 mock 或日志写入实现，不影响测试通过结论。

### 3. TypeScript

```text
npx tsc --noEmit
```

结果：**通过，无错误输出**。

### 4. Diff 检查

```text
git diff --check
```

结果：**通过，无空白错误**。

### 5. Prompt import 边界

```text
rg -n "from app\\.services\\.ai_prompts import" backend/app --glob '*.py'
```

结果：仅 `backend/app/services/ai_prompt_registry.py` 作为唯一 Registry
入口保留 import。业务 service 和 router 为 **0**。

### 6. 模板自行格式化

生产 service 中不存在 `user_content_template.format(...)`。含变量的
`NETEASE_REASON` 与无变量的 `CAPTURE_RECOGNITION` 均通过
`render_user_content()` 构造 user content。

## Prompt 版本变更记录

Batch 10.2 为所有静态运行时 Prompt 增加统一的 Role / Task / Input /
Constraints / Output Contract / Failure / Uncertainty 结构。该包装文本会实际发送给
provider，属于语义可见变化，因此：

- 所有 `dynamic_prompt=False` 的 PromptTemplate：`v1` → `v2`。
- `PROMPT_TEST`、`REPAIR_DETERMINISTIC`：继续为 `v1`，其 system prompt 由调用方动态提供，本批未改写动态正文。

本次标准化未新增输出字段、未扩展任务范围，也未执行真实 provider 效果评估。

## 合同与边界核对

- 外部 API response schema：未修改。
- 业务输出字段：未新增。
- 手动 parser：未替换；`ANALYZE_MISTAKE`、`ANALYZE_TEXT`、
  `KNOWLEDGE_SUMMARY`、`REPAIR_DETERMINISTIC` 集中列为受控手动处理任务。
- 纯文本通道：`PROMPT_TEST`、`DIAGRAM_FALLBACK`、`NETEASE_REASON`
  集中列为受控 passthrough。
- 数据库与 migration：未新增。
- Batch 11：未进入。
- 真实模型效果：**未验证，不作准确率或效果提升声明**。

## 工作区说明

开始本批前工作区已有大量未提交和未跟踪文件，包括 Batch 9、10、10.1
实现。本批保留这些用户改动，没有回退或覆盖无关文件。全量测试结果反映当前
组合工作区，Batch 10.2 的直接目标测试另行记录在上方。

## 当前结论

P0-01 至 P1-04 已完成，Batch 10.2 通过本地工程合同与自动化回归验收。
未进行真实 provider 端到端效果评估，因此不作准确率或效果提升声明。
剩余风险及归档决定见 [audit.md](./audit.md)。

## 收口小补丁：Prompt 变量错误码直接覆盖

> 状态：**DEFER-10.2-001 已关闭**

新增两个使用最小人工违规 `PromptTemplate` 的直接测试：

- `test_detects_undeclared_input_variable`
- `test_detects_missing_input_variable`

两项测试均直接断言错误码，并确认 violation message 不包含测试中设置的
敏感输入值。测试不依赖生产 Registry 偶然触发；现有
`ai_prompt_standard.py` 已能正确检出，因此未修改检查器实现。

### 最终验证

```text
cd backend && .venv/bin/python -m pytest tests/test_ai_prompt_standard.py -q
```

结果：**7 passed in 0.06s**。

```text
cd backend && .venv/bin/python -m pytest tests/ -ra
```

结果：**187 passed, 2 warnings in 6.05s**。两个 warning 仍为
`test_ai_gateway.py` 中既有 AsyncMock RuntimeWarning，与本补丁无关。

```text
npx tsc --noEmit
```

结果：**通过，无错误输出**。

```text
git diff --check
```

结果：**通过，无空白错误**。

本补丁未修改业务 service、Prompt 文本、API schema、数据库或 migration，
未进入 Batch 11，也未执行真实模型调用或 Prompt 效果评估。
