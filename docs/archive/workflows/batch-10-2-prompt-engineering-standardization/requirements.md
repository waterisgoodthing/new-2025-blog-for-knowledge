# Requirements：Batch 10.2 Prompt Engineering Standardization

> 状态：**已完成并关闭**
>
> 关联：[design.md](./design.md) · [tasks.md](./tasks.md)

## 1. 背景

Batch 10 建立了 `AiTaskType`、`PromptTemplate`、Prompt Registry 和 Validator；Batch 10.1 让 Registry 实际驱动消息构建和 Gateway 默认参数。当前仍存在以下工程问题：

1. Prompt 文本的章节结构和约束表达不一致。
2. `user_content_template` 的变量只存在于字符串中，Registry 没有显式变量合同。
3. 调用方自行格式化模板，缺失变量、额外变量和未解析占位符不能被统一发现。
4. `output_schema_name`、`json_mode` 与 Prompt 中的输出声明主要依靠人工同步。
5. `mistake_staged_service.py` 仍直接引用 vision system message，属于 Batch 10.1 记录的受控例外。
6. 当前测试主要验证注册数量与字段值，尚未形成全量 Prompt 静态规范门禁。

## 2. 用户角色

- 个人管理员：使用 AI 识别、分析和草稿能力，期望输出稳定且失败可解释。
- 开发维护者：修改 Prompt 时需要明确合同、版本规则和自动回归证据。

## 3. 功能需求

### R1：Prompt 结构标准

每个静态 Prompt 必须能明确表达以下语义；允许纯文本任务按适用性省略输出 schema：

- 角色（Role）
- 任务（Task）
- 输入边界（Input）
- 约束与禁止事项（Constraints）
- 输出合同（Output Contract）
- 不确定或失败时的行为（Failure / Uncertainty）

验收标准：

- 所有非动态、非用户自定义 Prompt 通过结构规范检查。
- 规范检查不依赖调用真实模型。

### R2：模板变量合同

`PromptTemplate` 必须显式声明 `input_variables`，并由统一渲染函数处理 `user_content_template`。

输入：任务类型和变量映射。

处理：

- 校验必需变量完整；
- 拒绝未声明变量；
- 渲染模板；
- 拒绝残留的未解析占位符。

输出：渲染后的 user content 字符串。

失败行为：抛出不含敏感输入正文的确定性 `ValueError`。

验收标准：

- `NETEASE_REASON` 等含占位符模板通过统一入口渲染。
- 缺失、额外、残留变量均有单元测试。

### R3：Prompt 与输出合同一致性

Registry 必须能够自动检查：

- `json_mode=True` 的静态任务声明 JSON 输出；
- `output_schema_name` 引用已知 schema 或受控手动解析任务；
- 纯文本任务不错误声明 JSON schema；
- task type、版本号和 Prompt 元数据完整。

验收标准：

- 全量 Registry 一致性测试通过。
- 受控例外使用集中白名单并说明原因，不散落在测试条件中。

### R4：版本与变更规则

- Prompt 版本使用统一格式 `v<正整数>`。
- 本批发生语义变化的 Prompt 必须升级版本；仅排版且不改变发送文本时可保留版本。
- 测试必须固定每个 task type 的当前版本，防止无意降级或漏升版本。
- `prompt_version` 继续由 Gateway 写入现有调用日志。

验收标准：

- 所有 Registry 版本格式合法。
- 语义修改与版本变更有一一对应记录。

### R5：消息构建收口

- text 与 vision 消息继续通过 Registry builder 构建。
- vision 专用 system prompt 必须成为 Registry 的显式元数据，不允许业务 service 直接 import Prompt 常量。
- 动态 Prompt 和用户自定义 Prompt 仍允许显式 override，但必须被标记为动态策略。

验收标准：

- 生产业务 service 不直接 import `ai_prompts`。
- 现有 text / vision 消息结构保持兼容。

### R6：静态检查入口

提供一个可由测试调用的 Prompt 规范检查函数，输出确定性的违规列表，至少覆盖：

- 空 Prompt；
- 版本格式；
- 变量合同；
- JSON / schema 元数据冲突；
- 未声明的受控例外。

验收标准：

- 合法 Registry 返回空违规列表。
- 人工构造的违规模板能得到稳定、可断言的错误码。

## 4. 非功能需求

### N1：安全

- 错误信息不得回显完整用户输入、图片内容、密钥或 token。
- Prompt 标准化不得改变管理员权限要求。
- 不得建议或依赖生产 `AUTH_BYPASS`。

### N2：兼容

- 现有 AI API 请求/响应合同不变。
- `AiTaskType` 现有字符串值不变。
- Gateway 公开方法的既有调用方式保持兼容。
- `ai_call_logs.prompt_version` 的记录路径保持有效。

### N3：可维护

- Registry 不 import 业务 service。
- Prompt 纯常量模块不 import 业务 service。
- 不增加大型依赖。

### N4：可验证

- 新增规范逻辑必须有确定性单元测试。
- 不调用外部 AI provider 作为本批通过条件。
- 后端全量测试、TypeScript 检查和 `git diff --check` 纳入验收。

## 5. 不做事项

- 不评估或宣称 Prompt 的真实模型准确率提升。
- 不建立 golden dataset、在线 A/B、评分平台或人工标注系统。
- 不新增 Prompt 数据库持久化。
- 不增加管理后台编辑、发布、回滚 Prompt 的能力。
- 不改造 stream 运行架构；stream task type 枚举化另行规划。
- 不修改业务实体写入和草稿审核边界。
