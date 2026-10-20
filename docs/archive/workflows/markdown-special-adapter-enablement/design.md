# 设计

## 总体顺序

```text
SA-01 当前事实与合同冻结
  -> SA-02 共享失败测试与浏览器观测基线
  -> Mermaid-01..03
  -> Markmap-01..03
  -> Chart-01..03
  -> SA-03 跨适配器回退与残留检查
  -> SA-04 完整验证矩阵
  -> G2
```

三类适配器必须顺序执行，避免同时改变多个渲染边界。每条路径先写失败测试，再实现最小隔离适配器，最后完成结构与浏览器闭环。任何一条仍为 `DEFERRED_INERT`，整体 G2 都保持 `BLOCKED / NOT GO`。

## 共享安全边界

- 输入 Markdown、管理员内容和 AI 内容一律视为不可信。
- 第三方渲染结果不能直接成为可信 HTML/SVG/配置；必须经过 PoC 自有、有限且可测试的结构白名单。
- 允许列表之外的元素、属性、命名空间、URL、样式和配置必须局部失败为精确 inert 文本。
- 禁止使用旧生产渲染链作为 fallback。
- 安全相邻块、TOC、warnings 和 outcome 必须在局部失败后保留；全局失败进入 PoC 自有安全表面。

## 各适配器最小能力

### Mermaid

只启用经过白名单过滤的静态 SVG。拒绝 `foreignObject`、脚本、事件属性、未批准命名空间、危险 URL、外部资源、任意 style 和不稳定生成结构。

### Markmap

独立验证转换后的 DOM/SVG，不继承 Mermaid 结论。允许受控的本地平移/缩放；链接必须复用统一 URL 策略。下载、任意导航和外部资源默认禁用。

### Chart

只接受 JSON 数据及显式配置子集。禁止函数型 formatter、HTML formatter、动态代码、动态 import、外部请求和下载。Canvas/容器必须能重复渲染并完整销毁，不留下事件或实例残留。

## 浏览器主动观测

每条路径必须覆盖 SSR、hydration、安全到恶意更新和重复渲染，并主动断言：

- script sentinel；
- `pageerror`、console error、dialog；
- request、navigation、download；
- `click`、`error`、`load` 等相关事件；
- 最终 DOM/SVG/Canvas/容器结构；
- 卸载后的监听器、DOM、Canvas 和第三方实例残留。

## 暂停条件

- 需要新增、升级或删除依赖，修改 lockfile，或下载新的持久浏览器二进制；
- 需要放宽 URL、元素、属性、样式或配置白名单；
- 需要生产消费者、旧渲染器 fallback、真实数据、Git 或部署动作；
- 同一适配器连续三轮有新证据的修正后仍不能满足合同。

前三类情况必须请求新授权。最后一种情况必须如实标记该适配器 `BLOCKED`，并保持 G2 不通过。
