# 需求

- **SA-REQ-01 隔离。** 所有实现和测试只存在于 `src/lib/markdown-poc/` 及本工作夹，不连接生产 Markdown 消费者。
- **SA-REQ-02 现状先行。** 实施前重新核对当前依赖版本、license、advisory、peer/runtime、bundle 和 lockfile 状态；不得依赖历史版本印象。
- **SA-REQ-03 依赖审批。** 新增、升级、删除依赖、lockfile 变化或浏览器二进制下载必须单独获得明确批准。
- **SA-REQ-04 测试先行。** 每个适配器必须先增加能证明当前缺口的失败结构测试与浏览器测试，再写实现。
- **SA-REQ-05 独立结论。** Mermaid、Markmap、Chart 不得互相继承安全结论；每条都必须达到 `ENABLED_ISOLATED`。
- **SA-REQ-06 Mermaid。** 最终 SVG 必须经过 PoC 自有的元素、属性、命名空间、URL、id 和有限样式白名单；拒绝 `foreignObject`、事件和外部资源。
- **SA-REQ-07 Markmap。** 转换后的 DOM/SVG、链接、平移缩放、事件、导航和下载分别受控；默认禁止下载和非批准导航。
- **SA-REQ-08 Chart。** 只解析 JSON 数据及有限配置；禁止函数、HTML formatter、动态执行、外部请求和下载，并验证 Canvas/容器生命周期。
- **SA-REQ-09 精确回退。** 任意解析、渲染或净化失败必须局部退回精确解码的 inert 文本和结构化 warning，不得改写用户源文本。
- **SA-REQ-10 主动浏览器证据。** 每条路径都必须捕获并断言脚本、事件、错误、弹窗、网络、导航、下载、最终结构和重复渲染残留。
- **SA-REQ-11 可复现 artifacts。** 失败与最终通过证据必须保存在 `assets/`，记录运行时、浏览器、精确命令、计数和限制；不存在的 artifact 不得作为证据。
- **SA-REQ-12 G2 硬门。** 只有三类适配器全部 `ENABLED_ISOLATED`，共享 fallback 和完整验证矩阵通过，G2 才能 PASS。
- **SA-REQ-13 非迁移授权。** G2 PASS 仍不授权 M7、生产消费者切换、路由变更或部署。
