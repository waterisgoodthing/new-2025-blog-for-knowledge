# I11 下一步

1. I11 E-05、E-06 与 I11-04 已完成并归档，不再作为下一轮需求。
2. 日常 authority 保持 `blog_v2`；Legacy `blog_db` 与旧附件保持只读，除新的
   明确回切授权外不得解除只读或删除。
3. 新鲜备份保留在仓库外；后续任何部署或 schema 变更应重新建立 exact-commit
   恢复点，并复核 current/head/check、hash、关系和附件。
4. 两条既有 AI Gateway `AsyncMock` RuntimeWarning 可进入独立测试债务任务，
   不与迁移切换混合处理。
