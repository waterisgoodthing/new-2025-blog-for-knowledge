# Design：Batch 10.2 Prompt Engineering Standardization

> 状态：**已完成并关闭**
>
> 关联：[requirements.md](./requirements.md) · [tasks.md](./tasks.md)

## 1. 设计原则

本批采用“元数据合同 + 统一渲染 + 静态检查”的最小方案，不引入数据库 Prompt 平台。

数据流保持为：

```text
业务 service
  -> render_user_content / build_text_messages / build_vision_messages
  -> PROMPT_REGISTRY
  -> AI Gateway
  -> Output Validator
  -> 现有草稿或响应适配层
```

## 2. PromptTemplate 扩展

在现有 dataclass 上增加最小元数据：

```python
@dataclass(frozen=True)
class PromptTemplate:
    task_type: AiTaskType
    version: str
    system_prompt: str
    output_schema_name: str | None
    json_mode: bool
    preferred_provider: str | None
    max_tokens: int
    description: str
    user_content_template: str | None = None
    input_variables: tuple[str, ...] = ()
    vision_system_prompt: str | None = None
    dynamic_prompt: bool = False
```

字段规则：

- `input_variables`：仅声明 `user_content_template` 使用的命名变量。
- `vision_system_prompt`：同一 task 的 vision 路径需要独立 system prompt 时使用。
- `dynamic_prompt`：标记 `PROMPT_TEST`、`REPAIR_DETERMINISTIC` 等必须由调用方提供 system prompt 的任务。

不在本批增加 `prompt_id`、数据库主键、发布时间或审批人字段。

## 3. 统一模板渲染

新增：

```python
def render_user_content(
    task_type: AiTaskType,
    variables: Mapping[str, object],
) -> str:
    ...
```

处理顺序：

1. 获取 Registry 模板。
2. 确认存在 `user_content_template`。
3. 比较声明变量与调用变量。
4. 使用受控命名变量渲染。
5. 检查是否仍有未解析占位符。
6. 返回字符串。

错误只报告 task type 与变量名，不包含变量值。

本批不实现 Jinja2；继续使用标准库能力，避免为简单模板引入依赖。

## 4. Message Builder

`build_text_messages` 保持既有签名和行为。

`build_vision_messages` 的 system prompt 选择顺序调整为：

```text
显式 system_prompt_override
  > PromptTemplate.vision_system_prompt
  > PromptTemplate.system_prompt
```

由此将 `QUESTION_DRAFT_VISION_SYSTEM_MESSAGE` 纳入 Registry，消除 `mistake_staged_service.py` 对 Prompt 常量的直接 import。

动态任务仍允许 override；静态任务不禁止 override，以保持兼容，但规范检查会要求动态任务显式标记。

## 5. Prompt 结构标准

静态 Prompt 使用统一标题语义，推荐顺序：

```text
[Role]
[Task]
[Input]
[Constraints]
[Output Contract]
[Failure / Uncertainty]
```

中文正文可以使用对应中文标题。规范检查以明确标记或 Registry 元数据为准，不用脆弱的自然语言猜测判断 Prompt 质量。

实现采用 `ai_prompts.standardize_prompt()` 统一包装 Registry 中的静态
`system_prompt` 与 `vision_system_prompt`。原始任务正文仍由
`ai_prompts.py` 的既有常量提供，Registry 暴露给运行时的是标准化后的版本。

为避免一次性重写全部 Prompt 引发不可控语义漂移，本批只做：

- 补齐缺失的结构标记；
- 合并重复或冲突的输出要求；
- 明确“不编造”“信息不足”“只返回 JSON/纯文本”等失败语义；
- 保留原有任务目标与字段合同。

凡发送给模型的文本发生语义变化，对应 Prompt 版本升级为下一版本。

最终版本策略：

- 静态 Prompt：`v2`。
- `PROMPT_TEST`、`REPAIR_DETERMINISTIC` 动态 Prompt：`v1`。

## 6. 静态规范检查

在 AI service 层新增轻量检查模块，例如：

```text
backend/app/services/ai_prompt_standard.py
```

核心接口：

```python
@dataclass(frozen=True)
class PromptViolation:
    task_type: AiTaskType
    code: str
    message: str

def validate_prompt_registry(
    registry: Mapping[AiTaskType, PromptTemplate],
) -> list[PromptViolation]:
    ...
```

首批错误码：

- `empty_prompt`
- `invalid_version`
- `missing_input_variable`
- `undeclared_input_variable`
- `json_contract_mismatch`
- `schema_contract_mismatch`
- `dynamic_prompt_mismatch`
- `missing_structure_section`

违规结果按 `task_type.value`、`code` 排序，保证测试输出稳定。

## 7. 输出 schema 对照

检查器使用集中 schema 名称集合或来自 validator 的只读映射进行核对。依赖方向必须保持：

```text
ai_prompt_standard -> registry metadata / schema catalog
business services  -> registry builders
registry           -X-> business services
```

若直接 import validator 会产生循环依赖，则把 schema catalog 移到独立纯元数据模块；不得用延迟 import 掩盖循环依赖。

## 8. 权限与数据边界

本批不修改 router 权限。现有 AI 操作继续由 `get_current_admin` 保护。

Prompt 输出仍进入 validator 和既有草稿/响应适配层，不直接写 `Note`、错题正式实体或复习数据。

## 9. 兼容与回滚

兼容策略：

- 保留现有 Registry 查询与 builder 函数。
- 新字段全部提供默认值。
- API schema 和 HTTP 语义不变。

回滚策略：

- 代码回滚不需要数据库 downgrade。
- 若单个 Prompt 规范化产生行为回归，可恢复该 task 的旧文本和版本映射，不影响其他 task。

## 10. 验证设计

验证分四层：

1. 单元测试：变量渲染、vision prompt 选择顺序、违规错误码。
2. Registry 合同测试：全 task 覆盖、版本、结构、schema / JSON 一致性。
3. 回归测试：现有 AI、capture、mistake、diagram 测试。
4. 仓库检查：后端全量 pytest、`npx tsc --noEmit`、`git diff --check`、生产代码 import grep。

真实模型效果不在本批验收结论中；没有数据集证据时不得声称准确率提升。
