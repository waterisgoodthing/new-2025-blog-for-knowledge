# MVP 本地试运行验收

## 任务目标

承接 Batch 0–7 开发实现阶段后的本地试运行验收准备。Batch 0–7 开发阶段当前结论为：
**有条件通过，未发现 P0 阻塞项；继续开发已关闭**。

下一阶段只验证本地 MVP 手工学习链路：

```text
subject → knowledge point → question draft → question → mistake draft → mistake
→ review item → review record → attachment upload/link/read
```

## 触及领域

- 领域：review、mistakes、notes、manage、shared infrastructure
- 本 workflow 只产出本地试运行验收文档。
- 本 workflow 不修改业务代码、数据库迁移、脚本、公开内容或部署配置。

## 当前状态

- 状态：MVP Rebuild 本轮开发与试运行验收已结束；总体结论为 **有条件通过**，可以进入日常试用观察。
- 执行方式：由 Codex 在本地环境使用少量人工转述样例试跑并记录证据。
- 结论边界：3 条样例的核心写入、复习、附件链路和公开边界均已通过真实私有数据验证。唯一条件项为 `LT-ISSUE-002`；`LT-ISSUE-001` 属于非目标 localhost 环境兼容问题，不作为当前阻塞项。

## 阶段关闭决定

- 允许结束 MVP Rebuild 本轮开发与试运行验收。
- 下一状态：日常使用观察。
- 后续条件项：`LT-ISSUE-002` 进入独立的 **Auth Error Handling Cleanup**。
- 不启动 localhost Passkey 专项。
- 不进入 AI、OCR、BKT、完整练习、对象存储或云部署。

## 本次允许事项

- 人工选取少量 LeetCode 相关练习作为本地测试素材，建议 3–5 题。
- 题目内容采用题意转述或自己改写。
- 每条样例保留本地来源标注：

```yaml
source_type: manual
source_title: LeetCode 相关练习
source_note: 仅用于本地试运行，不公开展示
```

## 本次禁止事项

- 不得批量抓取 LeetCode。
- 不得写爬虫。
- 不得接 LeetCode API。
- 不得将 LeetCode 原题公开发布。
- 不得把 LeetCode 题目迁移到公开 `/blog`、`/notes`、`/mistakes`。
- 不得加入公开题库或公开附件。
- 不得绕过版权边界复制大规模题库内容。
- 不得进入 AI Gateway、OCR、BKT、完整练习、对象存储或云部署。
- 不得新增导入脚本、批量题库功能、数据迁移或自动修复。

## 主要文件

- [requirements.md](requirements.md)
- [design.md](design.md)
- [tasks.md](tasks.md)
- [checklist.md](checklist.md)
- [sample-data-plan.md](sample-data-plan.md)
- [trial-record.md](trial-record.md)
- [issues.md](issues.md)
- [validation.md](validation.md)
- [risks.md](risks.md)
- [next-requirements.md](next-requirements.md)
