# MVP Rebuild 公网部署

## 目标

将已推送的 MVP Rebuild commit `1cb7c7a7` 部署到现有 Cloudflare Workers 前端，
并验证 `https://blog.limengyang.me` 与现有公网 API 的关键访问边界。

## 领域

- shared infrastructure
- manage
- notes
- mistakes
- review
- attachments

## 当前状态

- commit `1cb7c7a7` 已部署到公网。
- Worker version：`2b7cc7f0-7355-465d-b1c5-0d9f8b572e49`。
- 部署后 HTTP、BUILD_ID、API health、未登录权限和公开数据边界验收通过。
- 状态：**pass，可进入公网日常使用观察**。

## 主要文件

- [requirements.md](requirements.md)
- [design.md](design.md)
- [tasks.md](tasks.md)
- [validation.md](validation.md)
- [risks.md](risks.md)
- [next-requirements.md](next-requirements.md)

## 边界

- 只部署 commit `1cb7c7a7`。
- 不从当前脏工作树直接构建。
- 不包含音乐资产、Batch 8、open-source closure 或未提交的部署配置删除。
- 不修改后端数据、Cloudflare Tunnel、DNS、Access、Passkey、AI/OCR/BKT、
  完整练习、对象存储或定时任务配置。
