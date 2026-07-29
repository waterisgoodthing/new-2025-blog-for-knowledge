# 下一轮需求文档：Dependency Runtime Governance

本文件暂不预设新的业务功能。只有在本轮验收后，才根据实际残余风险生成下一轮需求。

## 生成规则

- PostCSS 仍未清零：转为上游跟踪或安全接受期限需求。
- compatibility date 更新后出现回归：转为 runtime 兼容修复需求。
- 门禁误报：转为门禁可用性修复需求。
- 已证明非阻塞的构建提示：归档，不继续扩大范围。

执行前必须重新创建或更新 requirements/design/tasks，并获得审批。

## 本轮新增阻断需求

- `REQ-DRG-NEXT-01`：已转化为门禁顺序要求：先完成 Next/Cloudflare build 生成 image type declaration，再执行独立 TypeScript check。
- `REQ-DRG-NEXT-02`：在 Node 24.x 环境完成一次真实 `npm ci`、测试、TypeScript 和 Cloudflare build，补齐当前本机缺失的 Node 24 证据。
