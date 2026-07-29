# 需求与验收

## 功能需求

- REQ-CF2-01：Dashboard 按 `section_order` 渲染，且 `hidden_sections` 中的区块不进入 DOM。
- REQ-CF2-02：`today`/`activity` 至少保留一个可见；前端编辑、后端 API 都拒绝同时隐藏两者。
- REQ-CF2-03：偏好保存成功后，重新 GET profile 并刷新 Dashboard 仍保持顺序和隐藏状态。
- REQ-CF2-04：empty 代表健康但无数据；系统健康字段必须映射为 `ok`，局部失败才映射为 `unavailable`/`unknown`。
- REQ-CF2-05：后端测试必须验证局部失败、正常 commit、empty、rollback/close 和偏好刷新生效。
- REQ-CF2-06：浏览器证据必须证明隐藏和排序已在实际 Dashboard 页面生效，而非只证明设置控件存在。

## 退出条件

1. 前后端支持集合和学习行动保护规则均有定向测试。
2. Dashboard 的实际 DOM 顺序与偏好一致，隐藏区块不显示；至少一个学习行动区块始终存在。
3. 全空数据返回 section `empty` 且对应 system 健康为 `ok`。
4. learning/activity 局部失败分别保留其他可用区块，并正确报告系统健康。
5. 正常请求有 commit，异常路径有 rollback 和 session close，异常后后续查询可继续。
6. 文档中的测试数量、浏览器尺寸和截图链接与实际执行结果一致。

## 明确不包含

不新增数据库 schema，不改变公开页面，不修改认证绕过语义，不部署、不推送、不操作生产或源数据库。
