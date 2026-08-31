# I12 下一步

1. I10、I11 和 I12/F-01～F-03 已完成并归档，不再作为下一轮需求。
2. 任何未来应用部署必须先形成审查过的 clean exact commit，并在该 commit 上
   重跑 `predeploy:check`；当前 dirty worktree 不得部署。
3. 部署若晚于本次恢复点，应重新生成 DB/附件备份并做隔离恢复；保持
   `AUTH_BYPASS=false`、非通配 CORS、注册策略和 rollback owner。
4. 真实外部 AI/OCR provider、测试 warning hygiene、Cloudflare
   compatibility date 和 off-machine backup 属于后续独立任务，不改变本次终态。
