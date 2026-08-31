# Markdown 特殊适配器安全启用

Status: `SA-01～04 HISTORICAL COMPLETE — Mermaid / Markmap / Chart = ENABLED_ISOLATED; G2 ISOLATED PASS; FIX-03～05 COMPLETE; F4 INPUT READY FOR SEPARATE APPROVAL; NO PRODUCTION MIGRATION OR F4`

## 目标

在隔离 Markdown PoC 中分别为 Mermaid、Markmap、Chart 建立项目自有的安全适配器，并让三条路径都达到 `ENABLED_ISOLATED`。只有三条路径的结构合同、真实浏览器主动观测和失败回退全部通过，G2 才能关闭，F3 才能开始。

本工作夹承接用户于 2026-08-16 对 D1 选择的方案 B。它不重做已完成的 M1～M6.9，也不授权生产 Markdown 消费者切换。

## 涉及范围

- `src/lib/markdown-poc/` 内的隔离适配器、测试夹具和浏览器表面；
- Mermaid 最终 SVG 白名单；
- Markmap 转换后 DOM/SVG、链接与交互边界；
- Chart JSON 配置白名单、Canvas/容器生命周期；
- G2 所需的可复现命令、主动观测和本地 artifacts。

## 明确不包含

- `src/lib/markdown-renderer.ts`、`src/hooks/use-markdown-render.tsx` 或生产消费者迁移；
- 路由、认证、API、DTO、数据库、持久化和视觉系统改造；
- F3、F4、Git 发布或部署；
- 真实私有内容、生产 API 或凭据。

## 当前入口

SA-01～04 已在获得批准后完成。当前仅执行已批准的 FIX-03 文档同步；它不重新开启适配器实现、生产迁移或 F4。

## 文件

- [设计](design.md)
- [需求](requirements.md)
- [任务清单](tasks.md)
- [审计](audit.md)
- [验证](validation.md)
- [交接](handoff-prompt.md)
