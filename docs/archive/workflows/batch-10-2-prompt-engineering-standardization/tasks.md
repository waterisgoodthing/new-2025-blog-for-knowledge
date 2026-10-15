# Tasks：Batch 10.2 Prompt Engineering Standardization

> 状态：**已批准并全部完成**
>
> 关联：[requirements.md](./requirements.md) · [design.md](./design.md)
>
> 执行规则：用户批准后按编号逐项执行；每完成一个任务，立即勾选该任务，再进入下一项。不得进入 Batch 11。

## P0-01 建立 Prompt 规范检查器

任务编号：P0-01
任务名称：Prompt Registry 静态规范检查
优先级：P0
来源需求：R1、R3、R4、R6
涉及文件：`backend/app/services/ai_prompt_standard.py`、对应测试文件
修改内容：定义 `PromptViolation`、稳定错误码和 `validate_prompt_registry()`；覆盖空 Prompt、版本、结构、变量、JSON/schema、动态策略检查。
完成标准：合法 Registry 无违规；人工构造的每类违规均能稳定检出。
验证方式：目标单元测试。
风险说明：规则过严会把合法动态 Prompt 误判；使用集中受控元数据而非散落测试跳过。

- [x] 完成 P0-01。新增确定性规范检查器与稳定排序错误码；`test_ai_prompt_standard.py` 2 passed。

## P0-02 扩展 PromptTemplate 元数据

任务编号：P0-02
任务名称：变量、vision 与动态 Prompt 合同
优先级：P0
来源需求：R2、R5
涉及文件：`backend/app/services/ai_prompt_registry.py`、`backend/tests/test_ai_prompt_registry.py`
修改内容：增加 `input_variables`、`vision_system_prompt`、`dynamic_prompt` 默认字段，并补齐全量 Registry 元数据。
完成标准：全部 task type 元数据完整；旧构造方式保持兼容。
验证方式：Registry 合同测试。
风险说明：字段依赖方向处理不当可能产生循环 import。

- [x] 完成 P0-02。新增 `input_variables`、`vision_system_prompt`、`dynamic_prompt` 安全默认值并补齐 Registry 元数据；相关测试 17 passed。

## P0-03 建立安全模板渲染入口

任务编号：P0-03
任务名称：统一 user content 模板渲染
优先级：P0
来源需求：R2
涉及文件：`backend/app/services/ai_prompt_registry.py` 或独立纯工具模块、对应测试
修改内容：实现 `render_user_content()`；校验缺失、额外和残留变量；错误不包含变量值。
完成标准：所有声明变量模板可成功渲染，三类失败路径均有测试。
验证方式：目标单元测试。
风险说明：现有模板中的 JSON 大括号不可被误识别为变量。

- [x] 完成 P0-03。新增 `render_user_content()`，覆盖成功、缺失变量、额外变量、无模板和敏感值不回显；相关测试 28 passed。

## P0-04 迁移现有模板调用方

任务编号：P0-04
任务名称：调用方统一使用变量渲染入口
优先级：P0
来源需求：R2、R5
涉及文件：当前直接格式化 `user_content_template` 的 AI service 及相关测试
修改内容：迁移 `NETEASE_REASON` 等模板调用；保留最终消息内容合同。
完成标准：生产 service 不再自行格式化 Registry 模板。
验证方式：目标 service 测试与 grep。
风险说明：文本空格或换行变化可能影响快照断言，需区分合同变化与无意义格式差异。

- [x] 完成 P0-04。`netease_service` 与 `capture_recognition` 已统一使用安全渲染入口；目标回归 25 passed，生产 service 无 Registry 模板自行 `.format()`。

## P0-05 收口 vision system prompt

任务编号：P0-05
任务名称：消除业务 service 的 Prompt 常量 import 例外
优先级：P0
来源需求：R5
涉及文件：`backend/app/services/ai_prompt_registry.py`、`backend/app/services/mistake_staged_service.py`、message builder 测试
修改内容：实现 vision prompt 选择顺序；将 question draft vision system prompt 纳入 Registry；移除业务 service 直接 import。
完成标准：生产业务 service 中 `from app.services.ai_prompts import` 为 0；text/vision 行为测试通过。
验证方式：目标测试与 grep。
风险说明：不得把 vision 专用短提示错误用于 text 路径。

- [x] 完成 P0-05。vision builder 采用 override → Registry vision prompt → text prompt 的优先级；业务 service/router 对 `ai_prompts` 直接 import 已清零，仅 Registry 保留；目标测试 37 passed，导入检查通过。

## P1-01 标准化 Prompt 文本结构

任务编号：P1-01
任务名称：静态 Prompt 结构与失败语义统一
优先级：P1
来源需求：R1、R4
涉及文件：`backend/app/services/ai_prompts.py`、Registry 版本断言、相关输出测试
修改内容：按设计补齐 Role / Task / Input / Constraints / Output / Failure 语义，消除同一 Prompt 内冲突要求；保持现有业务字段合同。
完成标准：全量静态 Prompt 通过规范检查；发生语义变化的条目已升级版本并记录。
验证方式：规范测试、版本映射测试、现有 parser/validator 测试。
风险说明：这是本批语义风险最高项；不得顺手优化任务范围或新增输出字段。

- [x] 完成 P1-01。所有静态运行时 Prompt 增加统一六段结构且不新增业务字段/任务范围；因发送文本实际变化，静态 Prompt 统一由 `v1` 升级为 `v2`，动态 Prompt 保持 `v1`；目标回归 52 passed。

## P1-02 Prompt / Validator 合同对齐

任务编号：P1-02
任务名称：输出 schema 与 JSON 元数据一致性
优先级：P1
来源需求：R3
涉及文件：Prompt 规范模块、schema catalog 或 validator 只读映射、相关测试
修改内容：建立 schema 名称对照；集中记录手动 parse 与纯文本例外。
完成标准：Registry 全量一致性检查通过，不存在散落的测试跳过逻辑。
验证方式：目标单元测试。
风险说明：不得改变现有 API response schema 或把手动 parser 悄然替换掉。

- [x] 完成 P1-02。规范检查器已只读对照现有 `SCHEMA_MAP`；手动 parser 与纯文本任务集中列入受控元数据，不改变既有 parser/validator 路径；相关测试 39 passed。

## P1-03 全量回归与验证记录

任务编号：P1-03
任务名称：Batch 10.2 验收
优先级：P1
来源需求：N1、N2、N3、N4
涉及文件：`validation.md`
修改内容：执行目标测试、后端全量测试、TypeScript 检查、diff 检查和 grep；记录命令、结果、失败与影响。
完成标准：新增测试通过；若有预存在失败，给出可复现隔离证据；不得把真实模型效果写成已验证。
验证方式：

```text
cd backend && .venv/bin/python -m pytest <targeted tests>
cd backend && .venv/bin/python -m pytest tests/
npx tsc --noEmit
git diff --check
rg "from app\\.services\\.ai_prompts import" backend/app
```

风险说明：全量测试结果可能受当前脏工作区其他未提交改动影响，必须如实区分。

- [x] 完成 P1-03。目标测试 72 passed；后端全量 185 passed、2 个既有 AsyncMock warning；`npx tsc --noEmit`、`git diff --check` 通过；业务 service/router 对 `ai_prompts` 直接 import 为 0。

## P1-04 文档收口

任务编号：P1-04
任务名称：工作流收口与剩余风险记录
优先级：P1
来源需求：工作流规则
涉及文件：本目录 `README.md`、`tasks.md`、`validation.md`，必要时新增 `audit.md` / `handoff-prompt.md`
修改内容：更新状态、逐项完成记录、验收结论、偏差和下一轮建议。
完成标准：所有完成声明都有验证证据；未解决问题明确标为 blocked/deferred/risk。
验证方式：文档交叉链接和状态核对。
风险说明：不得用“阶段性完成”冒充完整关闭。

- [x] 完成 P1-04。README、design、validation 与 audit 已完成交叉收口；剩余风险均有归属或明确归档决定，未进入 Batch 11。

## 推荐执行顺序

```text
P0-01 -> P0-02 -> P0-03 -> P0-04 -> P0-05
      -> P1-01 -> P1-02 -> P1-03 -> P1-04
```

P1-01 涉及 Prompt 语义文本，必须在 P0 合同和检查器落地后执行。
