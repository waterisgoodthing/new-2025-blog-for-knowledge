# 审查方法

Lead 唯一文档写入者；A/B/C 并行独立只读，D 分批；Lead 抽样与高风险直接复核，统一分类裁决，独立文档复核后验收。不实施建议；不访问数据库或启动生产配置服务。

结合阶段：original_plan_mapping仅只读原需求/PR/B咨询；plan_integration_review只读UI/September与最终整合独立审阅。Lead直接核对Week4/修复第二阶段/CI合同/UI总账，再串行更新已有ROADMAP、STATUS和入口。

复审分工：docs_recheck_facts核当前事实与源码、original_plan_mapping核计划/状态、docs_recheck_governance核治理/清单；全部只读。治理终审因usage limit未完成，由original_plan_mapping接续独立终审；Lead裁决并串行写入，事实Worker复核措辞。

## 2026-10-11至12日：整体设计推导

保留模块化单体，优先统一KP写入/AI决定协议；展示站和工作台共享品牌、分别组织布局。可选视觉轨和N05不成为N06隐含前置，PR20–26保持原独立合同。
