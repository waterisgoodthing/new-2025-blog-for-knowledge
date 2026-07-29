# Residual Risks

## RISK-STREAM-001：client disconnect 难以稳定测试

- 风险类型：验证 / 生命周期
- 风险描述：ASGI 单测、浏览器取消、反向代理断开触发的取消语义可能不同。
- 影响范围：中断终态与 `finally` 是否可靠执行。
- 严重程度：高
- 当前状态：已转入后置 backlog；不阻塞当前系统冻结。
- 建议措施：后续同时使用 generator 单测、ASGI 集成测试和受控浏览器断连验证。
- 是否进入下一轮需求：是

## RISK-STREAM-002：partial output 持久化可能扩大敏感数据面

- 风险类型：安全 / 数据
- 风险描述：chunk 可能包含题目原文、个人答案、图片衍生内容或 provider 原始文本。
- 影响范围：数据库、备份、管理详情与清理流程。
- 严重程度：高
- 当前状态：旧 stream endpoint 已降级为 compatibility-only；完整 partial artifact 策略转入后置 backlog。
- 建议措施：只保存 parser 成功后清理过的 final output。
- 是否进入下一轮需求：是

## RISK-STREAM-003：SSE generator 异常可能绕过普通 Gateway finalize

- 风险类型：数据完整性
- 风险描述：provider 调用完成后，repair、related notes、parse 或 yield 仍可异常；普通
  Gateway finalize 不能代表 generator 完整成功。
- 影响范围：Run 状态准确性。
- 严重程度：高
- 当前状态：正式链路已迁出伪流式 endpoint；真正 stream generator 审计转入后置 backlog。
- 建议措施：真正流式方案必须由外层编排器拥有唯一 Run，并在 `finally` 收口。
- 是否进入下一轮需求：是

## RISK-STREAM-004：parser 成功/失败与 stream succeeded 的语义可能不同

- 风险类型：合同一致性
- 风险描述：provider 成功、JSON repair 成功、domain parser 成功和 final event 成功
  是不同阶段。
- 影响范围：`status`、`validation_status` 与人工审查含义。
- 严重程度：高
- 当前状态：正式链路已使用非流式 Run；真正 stream 语义差异转入后置 backlog。
- 建议措施：只有 parser 与 final delivery 均完成才标记 succeeded；parser error 标记
  failed 且 validation failed。
- 是否进入下一轮需求：是

## RISK-STREAM-005：真实 provider 流式行为与 mock 行为可能不一致

- 风险类型：集成 / provider
- 风险描述：真实 provider 的 chunk 边界、超时、断流和错误格式可能与 mock 不同。
- 影响范围：异常分类、buffer/parser 和最终审计。
- 严重程度：中
- 当前状态：未验证；转入后置 backlog，不作为当前系统冻结阻塞。
- 建议措施：只有未来批准真正 provider stream 后，才执行无敏感数据的受控补证。
- 是否进入下一轮需求：是

## 总体状态

RISK-B11-003 已关闭，关闭方式是消除正式业务生成链路对伪流式 endpoint 的依赖。
上述五项是完整 provider token streaming 的后置风险，必须在独立实施批中逐项验证；
它们不自动进入 Batch 12，也不阻塞当前系统冻结。
